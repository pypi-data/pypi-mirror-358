# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Unit tests for the `grab_bin_dist.fetch` routines."""

from __future__ import annotations

import errno
import pathlib
import random
import socket
import subprocess  # noqa: S404
import sys
import tempfile
import time
import typing

import pytest
import requests
from requests import codes as req_codes
from run_isolated import util as ri_util

from grab_bin_dist import defs
from grab_bin_dist import fetch
from grab_bin_dist import util


if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Final


PORT_FIRST: Final = 6502
"""The first port number to try to bind a listening socket to."""

PORT_LAST: Final = 8086
"""The last port number to try to bind a listening socket to."""

PORT_INCR_MIN: Final = 5
"""The minimum value to add to a port number when looking for available ones."""

PORT_INCR_MAX: Final = 10
"""The maximum value to add to a port number when looking for available ones."""

BIN_FILENAME: Final = "whee.bin"
"""The name of the binary file."""

BIN_CONTENTS: Final = b"\x03\x8e\x1c\xdf"
"""Not the contents of a text file."""

TEXT_FILENAME: Final = "whee.txt"
"""The name of the text file."""

TEXT_CONTENTS: Final = "This is a test.\nThis is only a test.\nOr is it?\n"
"""The contents of a text file."""


def find_listening_address(hosts: Iterable[tuple[int, str]]) -> tuple[int, str, int]:
    """Find an address that we can bind a socket to."""
    for family, host in hosts:
        port = PORT_FIRST
        while port <= PORT_LAST:
            sock = socket.socket(family, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError as err:
                if err.errno == errno.EADDRNOTAVAIL:
                    break

                if err.errno != errno.EADDRINUSE:
                    raise
            else:
                return family, host, port

            port += random.randint(PORT_INCR_MIN, PORT_INCR_MAX)  # noqa: S311

    pytest.fail("Could not find an available host/port to listen on")


def test_fetch_url() -> None:  # noqa: PLR0915  # maybe we should break this one down
    """Test the `fetch_url_to_file` function."""
    cfg: Final = defs.Config(
        additional_packages=[],
        log=ri_util.build_logger(name="test-fetch-url", quiet=False, verbose=True),
        utf8_env=util.get_utf8_env(),
    )
    with tempfile.TemporaryDirectory(prefix="test-fetch-url.") as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)

        family, addr, port = find_listening_address(
            ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")),
        )
        cfg.log.info("Listening on %(addr)s:%(port)d", {"addr": addr, "port": port})

        datadir: Final = tempd / "data"
        datadir.mkdir(mode=0o755)

        outdir: Final = tempd / "out"
        outdir.mkdir(mode=0o755)

        with subprocess.Popen(  # noqa: S603
            [sys.executable, "-m", "http.server", "--bind", addr, "--", str(port)],
            cwd=datadir,
        ) as srv_proc:
            try:
                cfg.log.info("Started an HTTP server at pid %(pid)d", {"pid": srv_proc.pid})
                cfg.log.info("Waiting for a little while for the HTTP server to start...")
                time.sleep(0.5)

                base_addr: Final = addr if family == socket.AF_INET else f"[{addr}]"
                base: Final = f"http://{base_addr}:{port}"

                def expect_err(
                    func: Callable[[defs.Config, str, pathlib.Path], None],
                    filename: str,
                    expected: int | type[Exception],
                ) -> None:
                    """Send a request, expect an error, expect no file to be there."""
                    cfg.log.info(
                        "Expecting a %(expected)s error for %(base)s/%(bin)s",
                        {
                            "expected": str(expected)
                            if isinstance(expected, int)
                            else expected.__name__,
                            "base": base,
                            "bin": filename,
                        },
                    )
                    if isinstance(expected, int):
                        with pytest.raises(requests.HTTPError) as req_err:
                            func(cfg, f"{base}/{filename}", outdir / filename)
                        cfg.log.info("Got exception: %(err)r", {"err": req_err})
                        assert req_err.value.response.status_code == expected
                    else:
                        with pytest.raises(expected) as err:
                            func(cfg, f"{base}/{filename}", outdir / filename)
                        cfg.log.info("Got exception: %(err)r", {"err": err})

                    assert not list(outdir.iterdir())

                def expect_ok(filename: str, contents: bytes) -> None:
                    """Send a request, expect an error, expect no file to be there."""
                    cfg.log.info(
                        "Expecting success for %(base)s/%(bin)s",
                        {"base": base, "bin": filename},
                    )
                    fetch.fetch_url_to_file(cfg, f"{base}/{filename}", outdir / filename)
                    outname: Final = outdir / filename
                    assert sorted(outdir.iterdir()) == [outname]
                    assert outname.read_bytes() == contents
                    outname.unlink()

                def expect_text_ok(filename: str, contents: str) -> None:
                    """Send a request, expect an error, expect no file to be there."""
                    cfg.log.info(
                        "Expecting success for %(base)s/%(bin)s",
                        {"base": base, "bin": filename},
                    )
                    fetch.fetch_url_text_to_file(cfg, f"{base}/{filename}", outdir / filename)
                    outname: Final = outdir / filename
                    assert sorted(outdir.iterdir()) == [outname]
                    assert outname.read_text(encoding="UTF-8") == contents
                    outname.unlink()

                expect_err(fetch.fetch_url_to_file, BIN_FILENAME, req_codes.NOT_FOUND)
                (datadir / BIN_FILENAME).write_bytes(BIN_CONTENTS)
                expect_ok(BIN_FILENAME, BIN_CONTENTS)

                expect_err(fetch.fetch_url_to_file, TEXT_FILENAME, req_codes.NOT_FOUND)
                (datadir / TEXT_FILENAME).write_text(TEXT_CONTENTS, encoding="UTF-8")
                expect_ok(TEXT_FILENAME, TEXT_CONTENTS.encode("UTF-8"))

                (datadir / TEXT_FILENAME).unlink()

                expect_err(fetch.fetch_url_text_to_file, BIN_FILENAME, UnicodeDecodeError)

                expect_err(fetch.fetch_url_text_to_file, TEXT_FILENAME, req_codes.NOT_FOUND)
                (datadir / TEXT_FILENAME).write_text(TEXT_CONTENTS, encoding="UTF-8")
                expect_text_ok(TEXT_FILENAME, TEXT_CONTENTS)
            finally:
                if srv_proc.poll() is None:
                    cfg.log.info(
                        "Sending a kill signal to the HTTP server at pid %(pid)d",
                        {"pid": srv_proc.pid},
                    )
                    srv_proc.kill()

                cfg.log.info(
                    "Making sure the HTTP server at pid %(pid)d has stopped",
                    {"pid": srv_proc.pid},
                )
                srv_proc.wait()
