# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Bootstrap ourselves into a new Docker container."""

from __future__ import annotations

import configparser
import contextlib
import dataclasses
import enum
import itertools
import os
import pathlib
import shlex
import shutil
import subprocess  # noqa: S404
import sys
import typing

import pshlex
from run_isolated import rdocker as ri_rdocker

from . import defs


if typing.TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Final, Self


@dataclasses.dataclass
class DockerError(defs.GrabError):
    """An error that occurred while processing a Docker container."""


@dataclasses.dataclass
class SlugArgumentError(DockerError):
    """An invalid path slug was supplied to `bootstrap_container()`."""

    value: str
    """The invalid value of the `slug` argument."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return (
            f"Invalid value {self.value!r} for the `slug` argument: "
            f"must be a single relative path component"
        )


@dataclasses.dataclass
class QueryOSReleaseError(DockerError):
    """Could not examine the contents of the `/etc/os-release` file within the container."""

    err: ri_rdocker.CommandError
    """The error that occurred."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Could not query /etc/os-release within the container: {self.err}"


@dataclasses.dataclass
class ParseOSReleaseError(DockerError):
    """Could not parse the contents of the `/etc/os-release` file within the container."""

    err: str
    """The error that occurred."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Could not parse /etc/os-release within the container: {self.err}"


class LinuxFamily(enum.StrEnum):
    """The type of the Linux distribution that we guessed."""

    DEB = "deb"
    """A Debian derivative."""

    RPM = "rpm"
    """A Fedora derivative."""


@dataclasses.dataclass(frozen=True)
class LinuxDistribution:
    """The Linux distribution that is running within the container."""

    name: str
    """The name of the Linux distribution."""

    version: str | None
    """The version ID of the Linux distribution, if present."""

    codename: str | None
    """The codename of the Linux distribution, if present."""

    family: LinuxFamily
    """The type of Linux distribution, if we can guess it."""

    @property
    def version_or_codename(self) -> str:
        """Return whichever of the version Id or the codename is defined."""
        if self.version is not None:
            return self.version

        if self.codename is not None:
            return self.codename

        raise RuntimeError(repr(self))


def parse_os_release(ri_cont: ri_rdocker.Container) -> LinuxDistribution:
    """Parse the contents of the /etc/os-release file within the container."""
    try:
        os_rel_contents: Final = ri_cont.run_command_output(["cat", "/etc/os-release"])
    except ri_rdocker.CommandError as err:
        raise QueryOSReleaseError(err) from err

    cfgp: Final = configparser.ConfigParser(interpolation=None)
    # Sigh...
    try:
        cfgp.read_string(f"[os-release]\n{os_rel_contents}\n")
    except ValueError as err:
        raise ParseOSReleaseError(str(err)) from err
    match cfgp.sections():
        case ["os-release"]:
            pass

        case other:
            raise ParseOSReleaseError(f"weird sections: {other!r}")  # noqa: EM102,TRY003

    def parse_value(name: str, value: str) -> tuple[str, str]:
        """Unquote a single value."""
        match shlex.split(value):
            case [single]:
                return (name, single)

            case _:
                raise ParseOSReleaseError(f"unexpected {name} value: {value!r}")  # noqa: EM102,TRY003

    os_rel_vars: Final = dict(itertools.starmap(parse_value, cfgp["os-release"].items()))
    os_id: Final = os_rel_vars["id"]
    os_id_like: Final = os_rel_vars.get("id_like")
    return LinuxDistribution(
        name=os_id,
        version=os_rel_vars.get("version_id"),
        codename=os_rel_vars.get("version_codename"),
        family=LinuxFamily.DEB if os_id == "debian" or os_id_like == "debian" else LinuxFamily.RPM,
    )


def find_uv(cfg: defs.Config) -> pathlib.Path | None:
    """Try to find a suitable `uv` executable to bind-mount into the container."""
    cfg.log.debug("Looking for a `uv` executable")
    uv_direct: Final = shutil.which("uv")
    if uv_direct is None:
        cfg.log.debug("- no `uv` in the search path at all")
        return None

    cfg.log.debug("- found at `%(uv)s`", {"uv": uv_direct})
    try:
        uv_real: Final = pathlib.Path(uv_direct).resolve()
    except OSError as err:
        cfg.log.warning(
            "- could not resolve `%(uv)s` to an absolute path: %(err)s",
            {"uv": uv_direct, "err": err},
        )
    cfg.log.debug("- resolved to `%(uv)s`", {"uv": uv_real})

    try:
        lines: Final = subprocess.check_output(  # noqa: S603
            [uv_real, "--version"],
            encoding="UTF-8",
            env=cfg.utf8_env,
        ).splitlines()
    except (OSError, subprocess.CalledProcessError) as err:
        cfg.log.warning(
            "- could not run `%(uv)s --version`: %(err)s",
            {"uv": uv_real, "err": err},
        )
    match [line.split() for line in lines]:
        case [["uv", version]] if version and "0" <= version[0] <= "9":
            cfg.log.debug("- got %(uv)s version %(version)s", {"uv": uv_real, "version": version})
            return uv_real

        case _:
            cfg.log.debug(
                "- unexpected `%(uv)s --version` output: %(lines)r",
                {"uv": uv_real, "lines": lines},
            )
            return None


@dataclasses.dataclass(frozen=True)
class Container:
    """Wrap a `run-isolated` container, provide our own helpers."""

    cfg: defs.Config
    """The runtime configuration, including the logger."""

    cont: ri_rdocker.Container
    """The `run-isolated` Docker container."""

    int_path: pathlib.Path
    """The path to the source tree mounted within the container."""

    int_workdir: pathlib.Path
    """The path to the working directory mounted within the container."""

    linux_distribution: LinuxDistribution
    """The name of the Linux distribution installed within the container."""

    venv_path: pathlib.Path
    """The path to the virtual environment bootstrapped within the container."""

    workdir: pathlib.Path
    """The path to the working directory on the host."""

    @classmethod
    @contextlib.contextmanager
    def bootstrap(
        cls,
        cfg: defs.Config,
        container: str,
        *,
        python3: str | None = None,
        slug: str = "grab-bin-dist",
        workdir: pathlib.Path,
    ) -> Iterator[Self]:
        """Start a `run-isolated` container, install ourselves within it."""
        slug_path: Final = pathlib.Path(slug)
        if slug_path.is_absolute() or len(slug_path.parts) != 1 or not slug_path.parts[0]:
            raise SlugArgumentError(slug)
        int_path: Final = pathlib.Path("/opt/grab") / slug

        uv_path: Final = find_uv(cfg)
        int_path_uv: Final = pathlib.Path("/opt/grab-tools/uv")

        int_workdir: Final = pathlib.Path("/opt/grab-tools-work")

        venv_path: Final = pathlib.Path("/tmp/grab-venv")  # noqa: S108  # in a container

        if python3 is None:
            python3 = "python3"

        ri_cfg: Final = ri_rdocker.Config(log=cfg.log, uid=0, gid=0)
        cfg.log.debug("Starting a %(container)s container", {"container": container})
        with ri_rdocker.Container.start_container(
            ri_cfg,
            container,
            volumes=[
                ri_rdocker.ContainerVolume(
                    external=pathlib.Path.cwd(),
                    internal=int_path,
                    readonly=True,
                ),
                ri_rdocker.ContainerVolume(external=workdir, internal=int_workdir, readonly=False),
                *(
                    []
                    if uv_path is None
                    else [
                        ri_rdocker.ContainerVolume(
                            external=uv_path,
                            internal=int_path_uv,
                            readonly=True,
                        ),
                    ]
                ),
            ],
        ) as ri_cont:
            linux_distribution: Final = parse_os_release(ri_cont)
            cont: Final = cls(
                cfg=cfg,
                cont=ri_cont,
                int_path=int_path,
                int_workdir=int_workdir,
                linux_distribution=linux_distribution,
                venv_path=venv_path,
                workdir=workdir,
            )

            pkgs: Final[list[str | pathlib.Path]] = [
                *cfg.additional_packages,
                *([] if uv_path is not None else [python3, f"{python3}-venv"]),
            ]
            cont.update_pkg_db()
            cont.install_os_packages(pkgs)

            cfg.log.debug("Initializing a Python virtual environment")
            if uv_path is None:
                ri_cont.run_command(
                    [python3, "-m", "venv", "--upgrade-deps", "--", venv_path],
                )
            else:
                ri_cont.run_command(
                    [
                        int_path_uv,
                        "venv",
                        "-p",
                        f"{sys.version_info[0]}.{sys.version_info[1]}",
                        "--",
                        venv_path,
                    ],
                )

            cfg.log.debug("Bootstrapping ourselves into the Python virtual environment")
            if uv_path is None:
                ri_cont.run_command(
                    [venv_path / "bin" / "python3", "-m", "pip", "install", "--", int_path],
                )
            else:
                uv_cmd = "; ".join(
                    [
                        "set -e",
                        pshlex.join([".", venv_path / "bin" / "activate"]),
                        pshlex.join([int_path_uv, "pip", "install", "--", int_path]),
                    ],
                )
                ri_cont.run_command(["sh", "-c", uv_cmd])

            yield cont

    def update_pkg_db(self) -> None:
        """Update the container's OS package database in an OS-specific way."""
        self.cfg.log.debug(
            "Updating the package database within the %(cid)s container",
            {"cid": self.cont.cid},
        )
        self.cont.run_command(["apt-get", "update"])

    def install_os_packages(self, pkgs: list[str | pathlib.Path]) -> None:
        """Install OS packages within the container in an OS-specific way."""
        match self.linux_distribution.family:
            case LinuxFamily.DEB:
                self.cfg.log.debug(
                    "Installing packages within the %(cid)s container: %(pkgs)s",
                    {"cid": self.cont.cid, "pkgs": pshlex.join(pkgs)},
                )
                cmd: Final[list[pathlib.Path | str]] = [
                    "env",
                    "DEBIAN_FRONTEND=noninteractive",
                    "apt-get",
                    "-y",
                    "install",
                    *pkgs,
                ]
                self.cont.run_command(cmd)

            case LinuxFamily.RPM:
                raise NotImplementedError

    def run_python(
        self,
        python_module: str,
        python_argv: list[str],
        *,
        env: dict[str, str] | None = None,
        is_module: bool = True,
    ) -> None:
        """Invoke a Python module or function within the container."""
        env_vars: Final = {
            "GRAB_BIN_IFACE_VER_MAJOR": "0",
            "GRAB_BIN_IFACE_VER_MINOR": "1",
            "GRAB_BIN_DIST_VENV": str(self.venv_path),
            "GRAB_BIN_DIST_SRC": str(self.int_path),
            "GRAB_BIN_DIST_WORKDIR": str(self.int_workdir),
            "GRAB_BIN_ORIG_UID": str(os.getuid()),
            "GRAB_BIN_ORIG_GID": str(os.getgid()),
            **(env or {}),
        }
        cmd: Final[list[pathlib.Path | str]] = [
            "env",
            *(shlex.quote(f"{name}={value}") for name, value in env_vars.items()),
            self.venv_path / "bin" / "python3",
            "-m" if is_module else "--",
            python_module,
            *python_argv,
        ]
        self.cfg.log.debug(
            "Invoking `%(cmd)s` within the %(cid)s container",
            {"cmd": pshlex.join(cmd), "cid": self.cont.cid},
        )
        self.cont.run_command(cmd)
