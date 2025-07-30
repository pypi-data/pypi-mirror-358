# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Helper functions for the grab_bin_dist library."""

from __future__ import annotations

import contextlib
import dataclasses
import functools
import os
import pathlib
import shutil
import subprocess  # noqa: S404
import tempfile
import tomllib
import typing

from . import defs


if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from typing import Final


@dataclasses.dataclass
class UtilError(defs.GrabError):
    """An error that occurred while doing something."""


@dataclasses.dataclass
class ExpectedDirectoryError(UtilError):
    """Expected the working directory to be a, well, directory."""

    path: pathlib.Path
    """The path to the supposed working directory."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Expected the working directory {self.path} to be a directory"


@dataclasses.dataclass
class MetaFilesError(UtilError):
    """An archive did not contain the expected single meta file."""

    path: pathlib.Path
    """The path to the archive that we tried to examine."""


@dataclasses.dataclass
class NoMetaFilesError(MetaFilesError):
    """The archive did not contain any meta files at all."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"No {defs.META_FILENAME} in {self.path}"


@dataclasses.dataclass
class ExtraMetaFilesError(MetaFilesError):
    """The archive did not contain any meta files at all."""

    meta_files: list[str]
    """The meta files found in the archive."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"More than one {defs.META_FILENAME} in {self.path}: {self.meta_files}"


@dataclasses.dataclass
class UnsupportedMetaFormatError(MetaFilesError):
    """The meta file in the archive specifies an unsupported format version."""

    ver_major: int
    """The format major version number."""

    ver_minor: int
    """The format minor version number."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Unsupported meta format version in {self.path}: {self.ver_major}.{self.ver_minor}"


@functools.lru_cache
def get_utf8_env() -> dict[str, str]:
    """Use a naive, yet mostly working way to simulate the `utf8-locale` functionality."""
    res: Final = dict(os.environ)
    res["LC_ALL"] = "C.UTF-8"
    with contextlib.suppress(KeyError):
        res.pop("LANGUAGE")
    return res


def extract_meta(cfg: defs.Config, path: pathlib.Path) -> defs.Meta:
    """Extract the `grab-bin-dist` metadata stored into an archive."""
    cfg.log.debug("Looking for grab-bin-dist metadata in the %(path)s archive", {"path": path})
    list_files: Final = subprocess.check_output(  # noqa: S603
        ["tar", "taf", path],  # noqa: S607
        encoding="UTF-8",
        env=cfg.utf8_env,
    ).splitlines()
    match [line for line in list_files if line.endswith(str(defs.META_FILENAME))]:
        case []:
            raise NoMetaFilesError(path)

        case [single_file]:
            meta_rel_path: Final = single_file

        case other_files:
            raise ExtraMetaFilesError(path, other_files)

    cfg.log.debug("Trying to extract %(meta)s from %(path)s", {"meta": meta_rel_path, "path": path})
    meta_contents: Final = subprocess.check_output(  # noqa: S603
        ["tar", "xOaf", path, "--", meta_rel_path],  # noqa: S607
        encoding="UTF-8",
        env=cfg.utf8_env,
    )
    cfg.log.debug("Parsing %(count)d characters of metadata", {"count": len(meta_contents)})
    meta_raw: Final = tomllib.loads(meta_contents)

    # Let's try to do this without mashumaro for now...
    fver_maj: Final = meta_raw["format"]["version"]["major"]
    fver_min: Final = meta_raw["format"]["version"]["minor"]
    if (
        not isinstance(fver_maj, int)
        or fver_maj != 0
        or not isinstance(fver_min, int)
        or fver_min < 1
    ):
        raise UnsupportedMetaFormatError(path, fver_maj, fver_min)

    meta: Final = defs.Meta(
        packages=[
            defs.MetaPackage(
                name=pkg["name"],
                version=pkg["version"],
                mach=pkg["mach"],
                system=pkg["system"],
                subdir=pathlib.Path(pkg["subdir"]),
            )
            for pkg in meta_raw["grab"]["packages"]
        ],
    )
    cfg.log.debug("Got metadata about %(count)d packages", {"count": len(meta.packages)})
    return meta


@contextlib.contextmanager
def tempfile_moved_if_okay(
    path: pathlib.Path,
    *,
    prefix: str | None = None,
    suffix: str | None = None,
) -> Iterator[pathlib.Path]:
    """Create a temporary file, yield its name, rename it to the specified path on success.

    Remove the temporary file if any exceptions are raised.
    """
    with tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, dir=path.parent) as tempf_obj:
        tempf: Final = pathlib.Path(tempf_obj.name)
        yield tempf

        tempf.rename(path)

        if hasattr(tempf_obj, "delete"):
            tempf_obj.delete = False
        if hasattr(tempf_obj, "_closer") and hasattr(tempf_obj._closer, "delete"):  # noqa: SLF001
            tempf_obj._closer.delete = False  # noqa: SLF001


def prepare_workdir(cfg: defs.Config, workdir: pathlib.Path) -> None:
    """Clean the work directory up if it exists."""
    if not workdir.exists():
        cfg.log.debug("Creating the %(path)s work directory", {"path": workdir})
        workdir.mkdir(mode=0o755)
    if not workdir.is_dir():
        raise ExpectedDirectoryError(workdir)

    work_items: Final = sorted(workdir.iterdir())
    if work_items:
        cfg.log.info("Cleaning up the %(path)s work directory", {"path": workdir})
        for path in work_items:
            if path.is_symlink() or not path.is_dir():
                path.unlink()
            else:
                shutil.rmtree(path)


def find_single_path(
    path: pathlib.Path,
    pred: Callable[[pathlib.Path], bool],
    err_handler: Callable[[list[pathlib.Path]], Exception],
) -> pathlib.Path:
    """Find a single object in the `path` directory that matches the supplied predicate.

    If there are no matches or more than one match, invoke the error handler.
    """
    match [found_path for found_path in path.iterdir() if pred(found_path)]:
        case [single]:
            found_path: Final = single

        case other_paths:
            raise err_handler(sorted(other_paths))

    return found_path


def find_single_dir(
    path: pathlib.Path,
    pred: Callable[[pathlib.Path], bool],
    err_handler: Callable[[list[pathlib.Path]], Exception],
) -> pathlib.Path:
    """Use `find_single_path()` to find a single directory that matches the supplied predicate."""
    return find_single_path(
        path,
        lambda found_path: found_path.is_dir() and pred(found_path),
        err_handler,
    )


def find_single_file(
    path: pathlib.Path,
    pred: Callable[[pathlib.Path], bool],
    err_handler: Callable[[list[pathlib.Path]], Exception],
) -> pathlib.Path:
    """Use `find_single_path()` to find a single file that matches the supplied predicate."""
    return find_single_path(
        path,
        lambda found_path: found_path.is_file() and pred(found_path),
        err_handler,
    )
