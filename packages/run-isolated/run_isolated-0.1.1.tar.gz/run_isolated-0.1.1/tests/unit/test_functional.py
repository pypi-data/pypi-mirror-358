# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Make sure that `run_isolated` can run commands in a Docker container."""

from __future__ import annotations

import contextlib
import dataclasses
import functools
import json
import os
import subprocess  # noqa: S404
import time
import typing

import pytest

from run_isolated import rdocker
from run_isolated import util


if typing.TYPE_CHECKING:
    import logging
    from collections.abc import Callable, Iterator
    from typing import Any, Final


ENV_DOCKER_IMG: Final = "TEST_RUN_ISOLATED_DOCKER_IMAGE"
"""The name of the environment variable to pass the Docker image name in."""

DOCKER_IMG: Final = os.environ.get(ENV_DOCKER_IMG)
"""The Docker image to use."""

SKIP_DOCKER_FLAG: Final = DOCKER_IMG is None
"""Whether to skip the Docker container tests."""

SKIP_DOCKER_REASON: Final = f"No {ENV_DOCKER_IMG} in the environment"
"""The reason to supply for skipping the Docker container tests."""


@dataclasses.dataclass(frozen=True)
class Nonce:
    """Initialize tracking data about a set of containers created by a single test run."""

    test_tag: str
    """The tag of the test, usually the test function name."""

    log: logging.Logger
    """The logger to send diagnostic messages to."""

    def log_info(self, fmt: str, args: dict[str, Any] | None = None) -> None:
        """Log an info-level message."""
        if args is None:
            args = {}
        self.log.info("[%(test_tag)s] " + fmt, args | {"test_tag": self.test_tag})  # noqa: G003

    def log_exception(self, fmt: str, args: dict[str, Any] | None = None) -> None:
        """Log an info-level message."""
        if args is None:
            args = {}
        self.log.exception(  # noqa: LOG004  # this method is invoked in exception handlers
            "[%(test_tag)s] " + fmt,  # noqa: G003
            args | {"test_tag": self.test_tag},
        )


@functools.lru_cache
def get_utf8_env() -> dict[str, str]:
    """Prepare a UTF-8-capable environment for running child processes."""
    current: Final = dict(os.environ)
    return current | {"LC_ALL": "C.UTF-8", "LANGUAGE": ""}


def init_test_nonce(test_tag: str) -> Nonce:
    """Construct a `Nonce` object to test with."""
    nonce: Final = Nonce(
        test_tag=f"ri-test-{test_tag}-{os.getpid()}",
        log=util.build_logger(name="test-run-isolated", verbose=True),
    )
    nonce.log_info("Starting a test")
    return nonce


def cleanup_test_containers(nonce: Nonce) -> None:
    """Clean up all the containers created by this test."""
    nonce.log_info("Cleaning up after a test")
    utf8_env: Final = get_utf8_env()
    prefix: Final = f"{nonce.test_tag}-"

    def list_and_run(*, remove: bool) -> None:
        """List Docker containers for this test, stop or remove them."""
        # Find all running Docker containers and stop them
        nonce.log_info(
            "Looking for containers to %(action)s",
            {"action": "remove" if remove else "stop"},
        )
        opts_ps: Final = ["-a"] if remove else []
        try:
            jlines_ps: Final = subprocess.check_output(  # noqa: S603
                ["docker", "ps", "--format=json", *opts_ps],  # noqa: S607
                encoding="UTF-8",
                env=utf8_env,
            ).splitlines()
        except (OSError, subprocess.CalledProcessError):
            nonce.log_exception("Could not run `docker ps`")
            return
        except ValueError:
            nonce.log_exception("Could not process the output of `docker ps` as valid UTF-8")
            return

        containers: Final[list[str]] = []
        for jline in jlines_ps:
            try:
                cdata = json.loads(jline)
            except ValueError:
                nonce.log_exception(
                    "A `docker ps` line is not valid JSON: %(jline)r",
                    {"jline": jline},
                )
                continue

            try:
                cid = cdata["ID"]
                cname = cdata["Names"]
            except KeyError:
                nonce.log_exception(
                    "A `docker ps` line with missing fields: %(jline)r",
                    {"jline": jline},
                )
                continue

            if not cname.startswith(prefix):
                continue

            nonce.log_info("- found container %(cid)s (%(cname)s)", {"cid": cid, "cname": cname})
            containers.append(cid)

        nonce.log_info("Found %(count)d container(s)", {"count": len(containers)})
        for cid in containers:
            nonce.log_info(
                "%(action)s container %(cid)s",
                {"action": "Removing" if remove else "Stopping", "cid": cid},
            )
            try:
                subprocess.check_call(  # noqa: S603
                    ["docker", "rm" if remove else "stop", "--", cid],  # noqa: S607
                    env=utf8_env,
                )
            except (OSError, subprocess.CalledProcessError):
                nonce.log_exception(
                    "Could not %(action)s container %(cid)s",
                    {
                        "action": "remove" if remove else "stop",
                        "cid": cid,
                    },
                )
                continue

            nonce.log_info("Done with container %(cid)s", {"cid": cid})

    time.sleep(1)
    list_and_run(remove=False)
    time.sleep(1)
    list_and_run(remove=True)


@contextlib.contextmanager
def ctx_nonce(name: str) -> Iterator[Nonce]:
    """Construct a `Nonce` object, clean up afterwards."""
    nonce: Nonce | None = None
    try:
        nonce = init_test_nonce(name)
        yield nonce
    finally:
        if nonce is not None:
            cleanup_test_containers(nonce)


def with_docker_container(
    *,
    test_tag: str | None = None,
) -> Callable[[Callable[[Nonce, rdocker.Container], None]], Callable[[], None]]:
    """Provide a test nonce and a Docker container to the decorated function."""

    def wrap(func: Callable[[Nonce, rdocker.Container], None]) -> Callable[[], None]:
        """Wrap the decorated function."""

        def inner() -> None:
            """Create the container, run the test."""
            print(flush=True)  # noqa: T201  # for cleaner pytest output

            nonlocal test_tag
            if test_tag is None:
                test_tag = func.__name__.removeprefix("test_").replace("_", "-")

            with ctx_nonce(test_tag) as nonce:
                assert DOCKER_IMG is not None

                cfg: Final = rdocker.Config(log=nonce.log, uid=999, gid=999)

                nonce.log_info("test-setup: Starting a container")
                with rdocker.Container.start_container(
                    cfg,
                    DOCKER_IMG,
                    name=f"{nonce.test_tag}-1",
                ) as cont:
                    nonce.log_info("test-setup: Started container %(cid)s", {"cid": cont.cid})

                    func(nonce, cont)

                    nonce.log_info(
                        "test-teardown: Automatically stopping the %(cid)s container",
                        {"cid": cont.cid},
                    )

                nonce.log_info("test-teardown: Stopped the test container... hopefully")

        return inner

    return wrap


@pytest.mark.skipif(SKIP_DOCKER_FLAG, reason=SKIP_DOCKER_REASON)
@with_docker_container()
def test_create_destroy(nonce: Nonce, container: rdocker.Container) -> None:
    """Create a container and destroy it immediately."""
    nonce.log_info("Doing nothing with the %(cid)s container", {"cid": container.cid})


@pytest.mark.skipif(SKIP_DOCKER_FLAG, reason=SKIP_DOCKER_REASON)
@with_docker_container()
def test_run_command(nonce: Nonce, cont: rdocker.Container) -> None:
    """Create a container and destroy it immediately."""
    nonce.log_info("test: running `test -f /etc/os-release`")
    cont.run_command(["test", "-f", "/etc/os-release"])

    nonce.log_info("test: running `test -f /etc/os-release` via the shell")
    cont.run_command(["sh", "-ec", "test -f /etc/os-release"])

    nonce.log_info("test: running `! test -f /nonexistent` via the shell")
    cont.run_command(["sh", "-ec", "! test -f /nonexistent"])


@pytest.mark.skipif(SKIP_DOCKER_FLAG, reason=SKIP_DOCKER_REASON)
@with_docker_container()
def test_run_command_output(nonce: Nonce, cont: rdocker.Container) -> None:
    """Create a container and destroy it immediately."""
    assert DOCKER_IMG is not None
    needle: Final = DOCKER_IMG.split(":")[1]
    nonce.log_info("test: will look for %(needle)r in /etc/os-release", {"needle": needle})

    nonce.log_info("test: Grabbing the version variables from /etc/os-release")
    lines: Final = cont.run_command_output(
        ["sed", "-nre", "/^VERSION/ { s/^[^=]+=//; p; }", "--", "/etc/os-release"],
    ).splitlines()
    nonce.log_info("test: Got output lines: %(lines)r", {"lines": lines})

    found: Final = [line for line in (line.strip('"') for line in lines) if needle in line]
    nonce.log_info("test: Found %(found)r", {"found": found})
    assert found
