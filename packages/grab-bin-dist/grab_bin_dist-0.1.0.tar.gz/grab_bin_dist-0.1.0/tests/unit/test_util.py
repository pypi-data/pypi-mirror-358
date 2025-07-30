# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Unit tests for the `grab_bin_dist.util` routines."""

from __future__ import annotations

import dataclasses
import os
import pathlib
import shutil
import subprocess  # noqa: S404
import tempfile
import typing
from unittest import mock

import pytest
import tomli_w
from run_isolated import util as ri_util

from grab_bin_dist import defs
from grab_bin_dist import util


if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Final, Never


TEST_DATA_TOP: Final = pathlib.Path(__file__).parent.parent / "data"
"""The `tests/data/` subdirectory of the source tree."""


@dataclasses.dataclass
class TempFileMovedError(Exception):
    """The error we raise in the tempfile moved test."""

    tempfile: pathlib.Path
    """The temporary file that was created for us."""


@pytest.mark.parametrize(
    ("v_input", "v_expected"),
    [
        ({"HOME": "/home/stuff"}, {"HOME": "/home/stuff", "LC_ALL": "C.UTF-8"}),
        ({"HOME": "/home/stuff", "LC_ALL": "C"}, {"HOME": "/home/stuff", "LC_ALL": "C.UTF-8"}),
        (
            {"HOME": "/home/stuff", "LANGUAGE": "en", "LC_ALL": "C"},
            {"HOME": "/home/stuff", "LC_ALL": "C.UTF-8"},
        ),
        ({"HOME": "/home/stuff", "LANGUAGE": "en"}, {"HOME": "/home/stuff", "LC_ALL": "C.UTF-8"}),
    ],
)
def test_get_utf8_env(*, v_input: dict[str, str], v_expected: dict[str, str]) -> None:
    """Test the `get_utf8_env()` function."""
    with mock.patch.object(os, "environ", new=v_input):
        assert util.get_utf8_env.__wrapped__() == v_expected


def test_extract_meta() -> None:
    """Test the `extract_meta()` function."""
    cfg: Final = defs.Config(
        additional_packages=[],
        log=ri_util.build_logger(name="test-util", quiet=False, verbose=True),
        utf8_env=util.get_utf8_env(),
    )

    raw: Final = {
        "format": {"version": {"major": 0, "minor": 1}},
        "grab": {
            "packages": [
                {
                    "name": "something",
                    "version": "0.1",
                    "mach": "x86_64",
                    "system": "Linux",
                    "subdir": "x86_64",
                },
                {
                    "name": "nothing",
                    "version": "42.616",
                    "mach": "arm64",
                    "system": "Darwin",
                    "subdir": "thing/arm/64",
                },
            ],
        },
    }
    with tempfile.TemporaryDirectory(prefix="test-extract-meta.") as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)
        topdir: Final = tempd / "top"
        subdir: Final = topdir / "something" / "else"
        subdir.mkdir(mode=0o755, parents=True)
        with (subdir / defs.META_FILENAME).open(mode="wb") as outf:
            tomli_w.dump(raw, outf)

        arch: Final = tempd / "top-or-something.tar.bz2"
        subprocess.check_call(  # noqa: S603
            ["tar", "caf", arch.name, "--", topdir.name],  # noqa: S607
            cwd=tempd,
        )
        shutil.rmtree(topdir)

        assert sorted(tempd.iterdir()) == [arch]

        assert util.extract_meta(cfg, arch) == defs.Meta(
            packages=[
                defs.MetaPackage("something", "0.1", "x86_64", "Linux", pathlib.Path("x86_64")),
                defs.MetaPackage(
                    "nothing",
                    "42.616",
                    "arm64",
                    "Darwin",
                    pathlib.Path("thing/arm/64"),
                ),
            ],
        )


def test_tempfile_moved_if_okay() -> None:
    """Test the `tempfile_moved_if_okay()` function."""
    with tempfile.TemporaryDirectory(prefix="test-tempfile-moved.") as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)

        assert not list(tempd.iterdir())

        tempf_name: str | None = None

        def check_tempf(tempf: pathlib.Path, *, check_name: bool) -> None:
            """Run a couple of checks."""
            assert tempf.is_file()
            assert sorted(tempd.iterdir()) == [tempf]

            if check_name:
                assert tempf.name.startswith("tempfile.")
                assert tempf.name.endswith(".whee")

            nonlocal tempf_name
            tempf_name = tempf.name

        def check_tempf_raise(tempf: pathlib.Path, *, check_name: bool) -> None:
            """Run a couple of checks, then raise an exception."""
            check_tempf(tempf, check_name=check_name)
            raise TempFileMovedError(tempfile=tempf)

        def check_tempf_ok(tempf: pathlib.Path, *, check_name: bool) -> None:
            """Run a couple of checks, write something to the tempfile."""
            check_tempf(tempf, check_name=check_name)
            tempf.write_text("hello\n", encoding="UTF-8")

        with (
            pytest.raises(TempFileMovedError) as temp_err,
            util.tempfile_moved_if_okay(
                tempd / "nosuch.file",
                prefix="tempfile.",
                suffix=".whee",
            ) as tempf,
        ):
            check_tempf_raise(tempf, check_name=True)

        assert not list(tempd.iterdir())
        assert isinstance(tempf_name, str)
        assert temp_err.value.tempfile == tempd / tempf_name

        tempf_name = None
        dst: Final = tempd / "whee.txt"
        with util.tempfile_moved_if_okay(dst) as tempf:
            check_tempf_ok(tempf, check_name=False)

        assert sorted(tempd.iterdir()) == [dst]
        assert dst.is_file()
        assert dst.read_text(encoding="UTF-8") == "hello\n"
        assert isinstance(tempf_name, str)
        assert tempf_name != dst.name


def _setup_dir(path: pathlib.Path, callbacks: list[Callable[[pathlib.Path], None]]) -> None:
    """Create a directory at that path, then invoke the callbacks to create stuff within."""
    path.mkdir(mode=0o755)
    for cb in callbacks:
        cb(path)


def _setup_file(path: pathlib.Path) -> None:
    """Create a regular file at that path."""
    path.write_text("This is a file, believe it or not.\n", encoding="UTF-8")


def _setup_symlink(path: pathlib.Path) -> None:
    """Create a symbolic link at that path."""
    path.symlink_to("/bin/sh")


@pytest.mark.parametrize(
    ("setup", "expect_success"),
    [
        (lambda path: _setup_dir(path, []), True),
        (lambda path: _setup_dir(path, [lambda path: _setup_file(path / "whee.txt")]), True),
        (
            lambda path: _setup_dir(
                path,
                [
                    lambda path: _setup_file(path / "whoo.bin"),
                    lambda path: _setup_symlink(path / "whee.link"),
                ],
            ),
            True,
        ),
        (
            lambda path: _setup_dir(
                path,
                [
                    lambda path: _setup_dir(
                        path / "subdir",
                        [lambda path: _setup_symlink(path / "whaa.link")],
                    ),
                ],
            ),
            True,
        ),
        (_setup_file, False),
        (_setup_symlink, False),
    ],
)
def test_prepare_workdir(*, setup: Callable[[pathlib.Path], None], expect_success: bool) -> None:
    """Test the `prepare_workdir()` function."""
    cfg: Final = defs.Config(
        additional_packages=[],
        log=ri_util.build_logger(name="test-util", quiet=False, verbose=True),
        utf8_env=util.get_utf8_env(),
    )

    with tempfile.TemporaryDirectory(prefix="test-grab-prepare-workdir.") as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)
        workdir: Final = tempd / "whee-work"
        setup(workdir)

        if expect_success:
            util.prepare_workdir(cfg, workdir)
        else:
            with pytest.raises(util.ExpectedDirectoryError) as err:
                util.prepare_workdir(cfg, workdir)

            assert err.value.path == workdir


@dataclasses.dataclass
class UnexpectedPathsError(Exception):
    """Unexpected files or directories were found in the test directories."""

    names: list[str]
    """The names of the unexpected files or directories."""


def exc_on_unexpected_paths(paths: list[pathlib.Path]) -> UnexpectedPathsError:
    """Raise an exception."""
    return UnexpectedPathsError([path.name for path in paths])


def raise_on_unexpected_paths(paths: list[pathlib.Path]) -> Never:
    """Raise an exception."""
    raise exc_on_unexpected_paths(paths)


@pytest.mark.parametrize(
    ("subdir", "pred", "expected"),
    [
        (".", lambda _: True, UnexpectedPathsError([])),
        ("empty", lambda _: True, UnexpectedPathsError([])),
        ("single-text-file", lambda _: True, "test.txt"),
        ("single-text-file", lambda path: path.name.endswith(".dat"), UnexpectedPathsError([])),
        ("two-text-files", lambda _: True, UnexpectedPathsError(["first.txt", "second.txt"])),
        (
            "two-text-files",
            lambda path: path.name.endswith(".txt"),
            UnexpectedPathsError(["first.txt", "second.txt"]),
        ),
        ("two-text-files", lambda path: path.name.endswith(".dat"), UnexpectedPathsError([])),
        ("two-text-files", lambda path: path.name.startswith("first"), "first.txt"),
        ("two-text-files", lambda path: path.name.startswith("second"), "second.txt"),
        (
            "more-files",
            lambda _: True,
            UnexpectedPathsError(["empty.dat", "first.txt", "second.txt"]),
        ),
        ("more-files", lambda path: path.name.endswith(".dat"), "empty.dat"),
        (
            "more-files",
            lambda path: path.name.endswith(".txt"),
            UnexpectedPathsError(["first.txt", "second.txt"]),
        ),
    ],
)
def test_find_single_file(
    *,
    subdir: str,
    pred: Callable[[pathlib.Path], bool],
    expected: str | UnexpectedPathsError,
) -> None:
    """Make sure `find_single_file()` works."""
    path: Final = TEST_DATA_TOP / "find" / subdir
    if isinstance(expected, UnexpectedPathsError):
        with pytest.raises(UnexpectedPathsError) as exc_info_raise:
            pytest.fail(repr(util.find_single_file(path, pred, raise_on_unexpected_paths)))

        assert exc_info_raise.value == expected

        with pytest.raises(UnexpectedPathsError) as exc_info_exc:
            pytest.fail(repr(util.find_single_file(path, pred, exc_on_unexpected_paths)))

        assert exc_info_exc.value == expected
        return

    assert util.find_single_file(path, pred, raise_on_unexpected_paths).name == expected


@pytest.mark.parametrize(
    ("pred", "expected"),
    [
        (
            lambda _: True,
            UnexpectedPathsError(["empty", "more-files", "single-text-file", "two-text-files"]),
        ),
        (lambda _: False, UnexpectedPathsError([])),
        (
            lambda path: "text" in path.name,
            UnexpectedPathsError(["single-text-file", "two-text-files"]),
        ),
        (lambda path: "more" in path.name, "more-files"),
    ],
)
def test_find_single_dir(
    *,
    pred: Callable[[pathlib.Path], bool],
    expected: str | UnexpectedPathsError,
) -> None:
    """Make sure `find_single_dir()` works."""
    path: Final = TEST_DATA_TOP / "find"
    if isinstance(expected, UnexpectedPathsError):
        with pytest.raises(UnexpectedPathsError) as exc_info_raise:
            pytest.fail(repr(util.find_single_dir(path, pred, raise_on_unexpected_paths)))

        assert exc_info_raise.value == expected

        with pytest.raises(UnexpectedPathsError) as exc_info_exc:
            pytest.fail(repr(util.find_single_dir(path, pred, exc_on_unexpected_paths)))

        assert exc_info_exc.value == expected
        return

    assert util.find_single_dir(path, pred, raise_on_unexpected_paths).name == expected
