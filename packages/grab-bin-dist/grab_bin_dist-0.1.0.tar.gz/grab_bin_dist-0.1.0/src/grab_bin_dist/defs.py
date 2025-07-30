# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Common definitions for the grab-bin-dist library."""

from __future__ import annotations

import dataclasses
import typing


if typing.TYPE_CHECKING:
    import logging
    import pathlib
    from typing import Final


VERSION: Final = "0.1.0"
"""The grab-bin-dist library version, semver-like."""


FEATURES: Final = {
    "grab-bin-dist": VERSION,
}
"""The list of features supported by the grab-bin-dist library."""

META_FILENAME = "grab-bin-dist.toml"
"""The name of the metadata file to store into an archive directory."""


@dataclasses.dataclass
class GrabError(Exception):
    """An error that occurred at some point during the processing."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        raise NotImplementedError(repr(self))


@dataclasses.dataclass(frozen=True)
class Config:
    """Runtime configuration for the grab-bin-dist library."""

    additional_packages: list[str]
    """Any additional OS packages to install within the container, if needed."""

    log: logging.Logger
    """The logger to send diagnostic, informational, and error messages to."""

    utf8_env: dict[str, str]
    """The environment to run UTF-8-capable programs in."""


@dataclasses.dataclass(frozen=True)
class MetaPackage:
    """Metadata about a single grabbed package."""

    name: str
    """The package name."""

    version: str
    """The package version."""

    mach: str
    """The machine type of the grabbed package."""

    system: str
    """The OS type of the grabbed package."""

    subdir: pathlib.Path
    """The relative subdirectory path of the grabbed package within the archive."""


@dataclasses.dataclass(frozen=True)
class Meta:
    """Metadata about packages grabbed."""

    packages: list[MetaPackage]
    """The packages grabbed."""
