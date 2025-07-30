# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Make sure that the "grab and pack `uv` up" example works."""

from __future__ import annotations

import os
import pathlib
import shutil
import tempfile
import typing
from unittest import mock

import pytest
from run_isolated import util as ri_util

from grab_bin_dist import defs
from grab_bin_dist import rdocker
from grab_bin_dist import util
from grab_bin_dist.sample import pack_uv


if typing.TYPE_CHECKING:
    from typing import Final


TEST_CONTAINER: Final = os.environ.get("TEST_CONTAINER")
"""The name of the container to run the test in, if explicitly specified."""

UV_PATH: Final = shutil.which("uv")
"""The path to `uv` on the host, if any."""


def do_test_pack_up_uv() -> None:
    """Start a Docker container, install ourselves in there, fetch the `uv` tool."""
    test_container: Final = os.environ["TEST_CONTAINER"]
    cfg: Final = defs.Config(
        additional_packages=["curl", "git", "xz-utils"],
        log=ri_util.build_logger(name="test-grab-bin-dist", quiet=False, verbose=True),
        utf8_env=util.get_utf8_env(),
    )

    latest_version: Final = pack_uv.host_get_uv_version(cfg)
    print(f"Got latest `uv` version {latest_version}")

    with tempfile.TemporaryDirectory(prefix="test-grab-uv.") as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)
        print(f"Using {tempd} as a work directory")

        assert not sorted(tempd.iterdir())

        with rdocker.Container.bootstrap(
            cfg,
            test_container,
            python3=os.environ.get("TEST_PYTHON3"),
            workdir=tempd,
        ) as cont:
            cont.run_python(
                "grab_bin_dist.sample.pack_uv",
                [],
                env={"PYTHONPATH": str(cont.int_path / "tests")},
            )

        uv_path: Final = util.find_single_file(
            tempd,
            lambda path: path.name.startswith("uv-") and path.name.endswith(".tar.xz"),
            lambda other: pytest.fail(repr(other)),
        )
        print(f"Whee, got {uv_path} in the work directory")
        meta: Final = util.extract_meta(cfg, uv_path)
        assert len(meta.packages) == 1
        assert meta.packages[0].name == "uv"
        assert meta.packages[0].version == latest_version

        save_dir_str: Final = os.environ.get("TEST_SAVE_DIR")
        if save_dir_str is not None:
            save_dir: Final = pathlib.Path(save_dir_str)
            print(f"Moving {uv_path} over to {save_dir}")
            shutil.move(uv_path, save_dir / uv_path.name)


@pytest.mark.skipif(TEST_CONTAINER is None, reason="No test container specified")
def test_pack_up_uv_without_uv() -> None:
    """Test fetching `uv` with no `uv` on the host system."""
    with mock.patch("shutil.which", return_value=None):
        do_test_pack_up_uv()


@pytest.mark.skipif(TEST_CONTAINER is None, reason="No test container specified")
@pytest.mark.skipif(UV_PATH is None, reason="No `uv` on the host system")
def test_pack_up_uv_with_uv() -> None:
    """Test fetching `uv` with `uv` on the host system."""
    do_test_pack_up_uv()
