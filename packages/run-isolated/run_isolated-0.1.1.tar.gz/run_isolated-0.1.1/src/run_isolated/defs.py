# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Common definitions for the run-isolated library."""

from __future__ import annotations

import dataclasses
import typing


if typing.TYPE_CHECKING:
    import logging
    from typing import Final


VERSION: Final = "0.1.1"
"""The run-isolated library version, semver-like."""


FEATURES: Final = {
    "run-isolated": VERSION,
}
"""The list of features supported by the run-isolated library."""


@dataclasses.dataclass(frozen=True)
class Config:
    """Runtime configuration for the run-isolated library."""

    log: logging.Logger
    """The logger to send diagnostic, informational, and error messages to."""
