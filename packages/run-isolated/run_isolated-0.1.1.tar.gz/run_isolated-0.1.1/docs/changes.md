<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Changelog

All notable changes to the run-isolated project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-06-27

### Additions

- Build infrastructure:
    - declare Python 3.14 as a supported version
    - keep the `uv.lock` file under version control
- Testing infrastructure:
    - add `uvoxen` configuration for running linters and unit tests

### Other changes

- Build infrastructure:
    - switch to PEP 735 dependency groups
    - use `mkdocstrings` 0.29.x with no changes
    - drop the `click` dependency, we do not have any command-line tools
    - switch from `[format.version]` to `mediaType` in the `publync` configuration
- Testing infrastructure:
    - drop the `unit-tests-pytest-7` test environment and rename
      the `unit-tests-pytest-8` one to `unit-tests`
    - use `ruff` 0.12.1, `reuse` 5.x, and `packaging` 25.x with no changes

## [0.1.0] - 2025-01-26

### Started

- First public release.

[Unreleased]: https://gitlab.com/ppentchev/run-isolated/-/compare/release%2F0.1.1...main
[0.1.1]: https://gitlab.com/ppentchev/run-isolated/-/compare/release%2F0.1.0...release%2F0.1.1
[0.1.0]: https://gitlab.com/ppentchev/run-isolated/-/tags/release%2F0.1.0
