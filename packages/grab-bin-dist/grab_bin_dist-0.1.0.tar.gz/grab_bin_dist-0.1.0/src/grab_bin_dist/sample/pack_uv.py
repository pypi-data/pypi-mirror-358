# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Sample script to pack the `uv` tool up."""

from __future__ import annotations

import pathlib
import platform
import pprint
import re
import subprocess  # noqa: S404
import typing
from urllib import parse as u_parse

import requests

from grab_bin_dist import defs
from grab_bin_dist import fetch
from grab_bin_dist import worker


if typing.TYPE_CHECKING:
    from typing import Final


RE_SEMVER: Final = re.compile(r"^ (?: 0 | [1-9][0-9]* ) (?: \. (?: 0 | [1-9][0-9]* ) )* $", re.X)
"""Check whether a string is a semantic version one."""

UV_URL: Final = "https://pypi.org/pypi/uv/json"
"""The PyPI information about the `uv` Python module."""

UV_INSTALL_URL: Final = "https://astral.sh/uv/install.sh"
"""The URL of the `uv` installation script."""


def host_get_uv_version(cfg: defs.Config) -> str:
    """Determine the current `uv` version without spawning a container."""

    def version_path(path: pathlib.Path) -> str | None:
        """Try to parse a version string out of this path."""
        ver_p: Final = path.parent.name
        return (
            ver_p
            if (
                "installer" in path.name
                and path.parent.parent.name == "download"
                and path.parent.parent.parent.name == "releases"
                and RE_SEMVER.match(ver_p)
            )
            else None
        )

    def follow_redirects(url: str) -> pathlib.Path:
        """Follow the successive redirects, return the path of the final location."""
        while True:
            cfg.log.info("- examining %(url)s", {"url": url})
            path = pathlib.Path(u_parse.urlsplit(url).path)
            if version_path(path) is not None:
                cfg.log.info("  - got it!")
                return path

            cfg.log.info("  - not a version path, sending a HEAD request")
            resp = requests.head(url, timeout=10)
            cfg.log.debug("  - got %(resp)r", {"resp": resp})
            if not resp.is_redirect:
                cfg.log.info("  - not a redirect!")
                return pathlib.Path(u_parse.urlsplit(url).path)

            url = resp.headers["location"]
            cfg.log.info("  - redirected to %(url)s", {"url": url})

    cfg.log.info("About to determine the latest `uv` version")
    path: Final = follow_redirects(UV_INSTALL_URL)
    version: Final = version_path(path)
    if version is None:
        raise RuntimeError(repr(path))
    cfg.log.info("Seems like the latest version of `uv` is %(ver)s", {"ver": version})
    return version


def find_uv_bin(
    cfg: worker.Config,
    path_bin: pathlib.Path,
) -> tuple[pathlib.Path, pathlib.Path, str]:
    """Get the path to the `uv` binary and its version string."""
    cfg.log.debug("Looking for uv in %(bin)s", {"bin": path_bin})
    path_uv_bin: Final = path_bin / "uv"
    if not path_uv_bin.is_file():
        raise RuntimeError(repr(path_uv_bin))

    cfg.log.debug("Looking for uvx in %(bin)s", {"bin": path_bin})
    path_uvx_bin: Final = path_bin / "uvx"
    if not path_uvx_bin.is_file():
        raise RuntimeError(repr(path_uvx_bin))

    cfg.log.debug("Checking the version of %(uv)s", {"uv": path_uv_bin})
    match [
        line.split()
        for line in subprocess.check_output(  # noqa: S603
            [path_uv_bin, "--version"],
            encoding="UTF-8",
            env=cfg.utf8_env,
        ).splitlines()
    ]:
        case [["uv", vers]]:
            return path_uv_bin, path_uvx_bin, vers

        case other_lines:
            raise RuntimeError(pprint.pformat(other_lines))


def main() -> None:
    """Grab `uv`, pack it up."""
    cfg: Final = worker.build_config(name="grab-bin-pack-uv", verbose=True, quiet=False)
    worker.setuid_if_needed(cfg)

    path_install: Final = cfg.workdir / "install.sh"
    fetch.fetch_url_text_to_file(cfg, UV_INSTALL_URL, path_install)

    path_bin: Final = cfg.workdir / "bin"
    path_bin.mkdir(mode=0o700)
    subprocess.check_call(  # noqa: S603
        [  # noqa: S607
            "env",
            f"XDG_BIN_HOME={path_bin}",
            "UV_DISABLE_UPDATE=1",
            "sh",
            path_install,
            "--no-modify-path",
        ],
    )

    mach: Final = platform.machine()
    system: Final = platform.system()

    (path_uv_bin, path_uvx_bin, vers_uv_bin) = find_uv_bin(cfg, path_bin)
    basename: Final = f"uv-{vers_uv_bin}"
    destdir: Final = cfg.workdir / basename
    cfg.log.debug("Preparing %(destdir)s", {"destdir": destdir})
    path_dst_bin: Final = destdir / system / mach / "usr" / "bin"
    path_dst_bin.mkdir(mode=0o755, parents=True)
    worker.install_file(cfg, path_uv_bin, path_dst_bin / "uv", mode=0o755)
    worker.install_file(cfg, path_uvx_bin, path_dst_bin / "uvx", mode=0o755)

    worker.store_meta(
        cfg,
        destdir,
        packages=[
            defs.MetaPackage(
                name="uv",
                version=vers_uv_bin,
                mach=mach,
                system=system,
                subdir=pathlib.Path(system) / mach,
            ),
        ],
    )

    tarball: Final = cfg.workdir / f"{basename}.tar.xz"
    cfg.log.debug("Packing %(destdir)s into %(tarball)s", {"destdir": destdir, "tarball": tarball})
    subprocess.check_call(  # noqa: S603
        ["tar", "caf", tarball, "--", destdir.name],  # noqa: S607,
        cwd=destdir.parent,
    )

    cfg.log.debug("Got %(stat)r", {"stat": tarball.stat()})


if __name__ == "__main__":
    main()
