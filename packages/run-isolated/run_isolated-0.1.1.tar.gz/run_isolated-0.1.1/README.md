<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# run-isolated - run commands in an isolated environment, e.g. a Docker container

\[[Home][ringlet-home] | [GitLab][gitlab] | [PyPI][pypi] | [ReadTheDocs][readthedocs]\]

## Overview

The `run-isolated` library allows programs to invoke some actions in
an isolated, clean environment, with read-only or read/write access to
existing filesystem directories.

Currently the only isolated environment supported is a Docker container.

## Examples

Start a container with commands run as a non-root account by default,
run a command as root, grab another command's output:

``` python
PATH_SRC: Final = pathlib.Path("/opt/src")
PATH_WORK: Final = pathlib.Path("/opt/work")

with rdocker.Container.start_container(
    run_isolated.Config(
        log=util.build_logger(name="ri-example", verbose=True),
        uid=1000,
        gid=1000,
    ),
    "debian:bookworm",
    volumes=[
        rdocker.ContainerVolume(
            external=pathlib.Path.cwd(),
            internal=PATH_SRC,
            readonly=True,
        ),
        rdocker.ContainerVolume(
            external=pathlib.Path.cwd() / "work",
            internal=PATH_WORK,
            readonly=False,
        ),
    ],
) as cont:
    cont.run_command(["apt-get", "update"], ugid="0:0", cwd=pathlib.Path("/"))

    lines = cont.run_command_output(
        ["find", ".", "-mindepth", "1", "-maxdepth", "1", "-type", "f"],
    ).splitlines()

    cont.run_command(
        [
            "env",
            f"PYTHONPATH={PATH_SRC / 'src'}",
            "python3",
            "-B",
            "-u",
            "-m",
            "ri_example.worker",
            "-o",
            PATH_WORK,
        ],
    )
```

## Contact

The `run-isolated` library was written by [Peter Pentchev][roam].
It is developed in [a GitLab repository][gitlab].
This documentation is hosted at [Ringlet][ringlet-home] with a copy at [ReadTheDocs][readthedocs].

[roam]: mailto:roam@ringlet.net "Peter Pentchev"
[gitlab]: https://gitlab.com/ppentchev/run-isolated "The run-isolated GitLab repository"
[pypi]: https://pypi.org/project/run-isolated/ "The run-isolated Python Package Index page"
[readthedocs]: https://run-isolated.readthedocs.io/ "The run-isolated ReadTheDocs page"
[ringlet-home]: https://devel.ringlet.net/sysutils/run-isolated/ "The Ringlet run-isolated homepage"
