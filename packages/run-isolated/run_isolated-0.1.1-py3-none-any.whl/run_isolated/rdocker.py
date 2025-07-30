# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Run commands in Docker containers."""

from __future__ import annotations

import contextlib
import dataclasses
import itertools
import re
import subprocess  # noqa: S404
import sys
import typing

import pshlex

from . import defs


if typing.TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator
    from typing import Final, Self


_RE_CID: Final = re.compile(r"^ [0-9a-f]+ $", re.X)
"""Match a Docker container id as returned by `docker start`."""

_CONTAINER_UNINIT: Final = "(not started)"
"""Marker string for an uninitialized container."""


@dataclasses.dataclass
class DockerError(Exception):
    """An error that occurred while handling the Docker container."""

    def __str__(self) -> str:
        """Provide a human-readable error description."""
        raise NotImplementedError


@dataclasses.dataclass
class CommandError(DockerError):
    """An error related to running a command."""

    cmd: list[pathlib.Path | str]
    """The command we tried to run."""

    @property
    def cmdstr(self) -> str:
        """Join the words of the command."""
        return pshlex.join(self.cmd)

    def __str__(self) -> str:
        """Provide a human-readable error description."""
        return f"Could not run the `{self.cmdstr}` command: {self!r}"


@dataclasses.dataclass
class CommandRunError(CommandError):
    """An error that occurred while trying to run a command."""

    err: OSError
    """The error that occurred."""

    def __str__(self) -> str:
        """Provide a human-readable error description."""
        return f"Could not run the `{self.cmdstr}` command: {self.err}"


@dataclasses.dataclass
class CommandFailError(CommandError):
    """A command that we tried to run failed."""

    err: subprocess.CalledProcessError
    """The error that occurred."""

    def __str__(self) -> str:
        """Provide a human-readable error description."""
        return (
            f"The `{self.cmdstr}` command exited with code {self.err.returncode}; "
            f"output: {self.err.stdout!r}; error output: {self.err.stderr!r}"
        )


@dataclasses.dataclass
class CommandDecodeOutputError(CommandError):
    """A command that we tried to run failed."""

    err: ValueError
    """The error that occurred."""

    def __str__(self) -> str:
        """Provide a human-readable error description."""
        return f"Could not parse the output of the `{self.cmdstr}` command: {self.err}"


@dataclasses.dataclass(frozen=True)
class Config(defs.Config):
    """Runtime configuration for the `run-i-docker` tool."""

    uid: int
    """The account user ID to use within the container."""

    gid: int
    """The account group ID to use within the container."""


@dataclasses.dataclass(frozen=True)
class ContainerVolume:
    """A single directory to be mounted within the container."""

    external: pathlib.Path
    """The full path to the directory on the host."""

    internal: pathlib.Path
    """The path within the container that the directory will be mounted on."""

    readonly: bool
    """Mount the directory read-only."""


@dataclasses.dataclass(frozen=True)
class Container:
    """A representation of a Docker container."""

    cid: str
    """The ID string of the container."""

    @classmethod
    def uninitialized(cls) -> Self:
        """Return an uninitialized container object, not to be used."""
        return cls(cid=_CONTAINER_UNINIT)

    @classmethod
    @contextlib.contextmanager
    def start_container(
        cls,
        cfg: Config,
        container: str,
        *,
        name: str | None = None,
        volumes: list[ContainerVolume] | None = None,
        workdir: pathlib.Path | None = None,
    ) -> Iterator[Self]:
        """Start a Docker container, stop it when done, record it in a `Config` object."""

        def output_lines(cmd: list[pathlib.Path | str]) -> list[str]:
            """Run a command, decode its output as UTF-8 lines."""
            try:
                return subprocess.check_output(cmd, encoding="UTF-8").splitlines()  # noqa: S603
            except OSError as err:
                raise CommandRunError(cmd, err) from err
            except subprocess.CalledProcessError as err:
                raise CommandFailError(cmd, err) from err
            except ValueError as err:
                raise CommandDecodeOutputError(cmd, err) from err

        def start() -> str:
            """Start the container, validate the `docker start` output."""
            cfg.log.debug(
                "Starting a Docker container using the '%(container)s' image",
                {"container": container},
            )
            vol_cmd: Final = list(
                itertools.chain(
                    *(
                        [
                            "--volume",
                            f"{vol.external}:{vol.internal}:{'ro' if vol.readonly else 'rw'}",
                        ]
                        for vol in (volumes or [])
                    ),
                ),
            )
            workdir_cmd: Final[list[pathlib.Path | str]] = (
                ["--workdir", workdir] if workdir is not None else []
            )
            name_cmd: Final = ["--name", name] if name is not None else []
            lines_start: Final = output_lines(
                [
                    "docker",
                    "run",
                    "--detach",
                    "--init",
                    "--pull",
                    "never",
                    "--rm",
                    "--user",
                    f"{cfg.uid}:{cfg.gid}",
                    *vol_cmd,
                    *workdir_cmd,
                    *name_cmd,
                    "--",
                    container,
                    "sleep",
                    "7200",
                ],
            )
            if len(lines_start) != 1 or not _RE_CID.match(lines_start[0]):
                sys.exit(f"Unexpected output from `docker start`: {lines_start!r}")
            return lines_start[0]

        def stop() -> None:
            """Stop the container, validate the `docker stop` output."""
            cfg.log.debug("Stopping the '%(cid)s' Docker container", {"cid": cid})
            lines_stop: Final = output_lines(["docker", "stop", "--", cid])
            expected: Final = [cid]
            if lines_stop != expected:
                sys.exit(
                    f"Unexpected output from `docker stop`: "
                    f"expected {expected!r}, got {lines_stop!r}",
                )

        cid: Final = start()
        cfg.log.debug("Got a Docker container with ID '%(cid)s'", {"cid": cid})

        try:
            yield cls(cid=cid)
        finally:
            stop()

    def run_command(
        self,
        cmd: list[pathlib.Path | str],
        ugid: str | None = None,
        workdir: pathlib.Path | None = None,
    ) -> None:
        """Run a command in the container, check for errors."""
        ugid_cmd: Final = ["--user", ugid] if ugid is not None else []
        workdir_cmd: Final[list[pathlib.Path | str]] = (
            ["--workdir", workdir] if workdir is not None else []
        )
        try:
            subprocess.check_call(  # noqa: S603
                ["docker", "exec", *ugid_cmd, *workdir_cmd, "--", self.cid, *cmd],  # noqa: S607
            )
        except OSError as err:
            raise CommandRunError(cmd, err) from err
        except subprocess.CalledProcessError as err:
            raise CommandFailError(cmd, err) from err
        except ValueError as err:
            raise CommandDecodeOutputError(cmd, err) from err

    def run_command_output(
        self,
        cmd: list[pathlib.Path | str],
        ugid: str | None = None,
        workdir: pathlib.Path | None = None,
    ) -> str:
        """Run a command in the container, check for errors."""
        ugid_cmd: Final = ["--user", ugid] if ugid is not None else []
        workdir_cmd: Final[list[pathlib.Path | str]] = (
            ["--workdir", workdir] if workdir is not None else []
        )
        cmd_exec: Final = ["docker", "exec", *ugid_cmd, *workdir_cmd, "--", self.cid, *cmd]
        try:
            return subprocess.check_output(cmd_exec, encoding="UTF-8")  # noqa: S603
        except OSError as err:
            raise CommandRunError(cmd_exec, err) from err
        except subprocess.CalledProcessError as err:
            raise CommandFailError(cmd_exec, err) from err
        except ValueError as err:
            raise CommandDecodeOutputError(cmd_exec, err) from err
