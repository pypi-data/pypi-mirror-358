# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Helper functions for use within the container."""

from __future__ import annotations

import dataclasses
import functools
import os
import pathlib
import subprocess  # noqa: S404
import typing

import tomli_w
from run_isolated import util as ri_util

from . import defs
from . import util


if typing.TYPE_CHECKING:
    import logging
    from typing import Final


@dataclasses.dataclass
class WorkerError(defs.GrabError):
    """An error that occurred while examining or handling the worker container."""


@dataclasses.dataclass
class UnsupportedInterfaceVersionError(WorkerError):
    """The environment variables specified an unsupported `grab-bin-dist` interface version."""

    ver_major: int
    """The interface major version number."""

    ver_minor: int
    """The interface minor version number."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return (
            f"Unsupported `grab-bin-dist` environment interface version: "
            f"{self.ver_major}.{self.ver_minor}"
        )


@dataclasses.dataclass(frozen=True)
class Config(defs.Config):
    """The configuration settings gleaned from the environment."""

    int_path: pathlib.Path
    """The path to the source tree mounted within the container."""

    orig_uid: int
    """The original user ID of the program running on the host."""

    orig_gid: int
    """The original group ID of the program running on the host."""

    venv_path: pathlib.Path
    """The path to the virtual environment bootstrapped within the container."""

    workdir: pathlib.Path
    """The path to the work directory mounted within the container."""


@functools.lru_cache
def get_grab_iface_version(*, log: logging.Logger) -> tuple[tuple[int, int], dict[str, str]] | None:
    """Validate the interface version variables, return the UTF-8-capable environment, too."""
    utf8_env: Final = util.get_utf8_env()

    iface_maj_str: Final = utf8_env.get("GRAB_BIN_IFACE_VER_MAJOR")
    if iface_maj_str is None:
        return None
    try:
        iface_maj: Final = int(iface_maj_str)
    except ValueError as err:
        log.warning(
            "GRAB_BIN_IFACE_VER_MAJOR is not an integer: %(major)r: %(err)s",
            {"major": iface_maj_str, "err": err},
        )
        return None

    iface_min_str: Final = utf8_env.get("GRAB_BIN_IFACE_VER_MINOR")
    if iface_min_str is None:
        log.warning("GRAB_BIN_IFACE_VER_MAJOR defined, but no GRAB_BIN_IFACE_VER_MINOR")
        return None
    try:
        iface_min: Final = int(iface_min_str)
    except ValueError as err:
        log.warning(
            "GRAB_BIN_IFACE_VER_MINOR is not an integer: %(major)r: %(err)s",
            {"major": iface_min_str, "err": err},
        )
        return None

    if iface_maj != 0 or iface_min < 1:
        raise UnsupportedInterfaceVersionError(iface_maj, iface_min)

    return (iface_maj, iface_min), utf8_env


def is_in_container(*, log: logging.Logger) -> bool:
    """Check whether the interface version variables are set."""
    return get_grab_iface_version(log=log) is not None


def build_config(
    *,
    name: str,
    log: logging.Logger | None = None,
    verbose: bool = False,
    quiet: bool = False,
) -> Config:
    """Deduce stuff from environment variables and stuff."""
    if log is None:
        log = ri_util.build_logger(name=name, verbose=verbose, quiet=quiet)
    iface_ver: Final = get_grab_iface_version(log=log)
    if iface_ver is None:
        raise RuntimeError
    utf8_env = iface_ver[1]

    return Config(
        additional_packages=[],
        log=log,
        utf8_env=utf8_env,
        int_path=pathlib.Path(utf8_env["GRAB_BIN_DIST_SRC"]),
        orig_uid=int(utf8_env["GRAB_BIN_ORIG_UID"]),
        orig_gid=int(utf8_env["GRAB_BIN_ORIG_GID"]),
        venv_path=pathlib.Path(utf8_env["GRAB_BIN_DIST_VENV"]),
        workdir=pathlib.Path(utf8_env["GRAB_BIN_DIST_WORKDIR"]),
    )


def setuid_if_needed(cfg: Config) -> None:
    """Change to the non-root account's user and group ID if needed."""
    if os.getgid() != cfg.orig_gid:
        cfg.log.debug("Changing our group ID to %(gid)s", {"gid": cfg.orig_gid})
        os.setgid(cfg.orig_gid)

    if os.getuid() != cfg.orig_uid:
        cfg.log.debug("Changing our user ID to %(uid)s", {"uid": cfg.orig_uid})
        os.setuid(cfg.orig_uid)


def install_file(  # noqa: PLR0913  # we need all of the arguments
    cfg: Config,
    src: pathlib.Path,
    dst: pathlib.Path,
    *,
    owner: str | int | None = None,
    group: str | int | None = None,
    mode: str | int | None = None,
) -> None:
    """Use `install(8)` to install a file."""
    cfg.log.info("%(src)s -> %(dst)s", {"src": src, "dst": dst})
    mode_opts: Final = (
        [] if mode is None else ["-m", mode if isinstance(mode, str) else f"0{mode:03o}"]
    )
    subprocess.check_call(  # noqa: S603
        [  # noqa: S607
            "install",
            *(["-o", str(owner)] if owner is not None else []),
            *(["-g", str(group)] if group is not None else []),
            *mode_opts,
            "--",
            src,
            dst,
        ],
    )


def store_meta(
    cfg: Config,
    destdir: pathlib.Path,
    *,
    packages: list[defs.MetaPackage],
) -> pathlib.Path:
    """Store the metadata about packages grabbed."""
    # Let's try to do it without mashumaro first...
    meta_raw: Final = {
        "format": {"version": {"major": 0, "minor": 1}},
        "grab": {
            "packages": [
                {
                    "name": pkg.name,
                    "version": pkg.version,
                    "mach": pkg.mach,
                    "system": pkg.system,
                    "subdir": str(pkg.subdir),
                }
                for pkg in packages
            ],
        },
    }

    path_meta: Final = destdir / defs.META_FILENAME
    cfg.log.debug(
        "Dumping metadata abount %(count)d packages into %(path)s",
        {"count": len(packages), "path": path_meta},
    )
    with path_meta.open(mode="wb") as outf_meta:
        tomli_w.dump(meta_raw, outf_meta)
    return path_meta
