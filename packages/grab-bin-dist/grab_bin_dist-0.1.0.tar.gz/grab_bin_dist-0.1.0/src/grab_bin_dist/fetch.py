# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Fetch data from variuos locations."""

from __future__ import annotations

import typing

import requests

from . import util


if typing.TYPE_CHECKING:
    import pathlib
    from typing import IO, Final

    from . import defs


def fetch_url(cfg: defs.Config, url: str, output: IO[bytes]) -> None:
    """Fetch a file, write the contents to the supplied output stream."""
    cfg.log.debug("Fetching %(url)s", {"url": url})
    resp: Final = requests.get(url, stream=True, timeout=1800)
    cfg.log.debug("Got a response: %(resp)r", {"resp": resp})
    resp.raise_for_status()
    for chunk in resp.iter_content(chunk_size=8192):
        output.write(chunk)


def fetch_url_to_file(cfg: defs.Config, url: str, path: pathlib.Path) -> None:
    """Fetch a file from the specified URL."""
    with util.tempfile_moved_if_okay(path) as tempf, tempf.open(mode="wb") as outf:
        cfg.log.debug("Fetching %(url)s into %(path)s", {"url": url, "path": path})
        fetch_url(cfg, url, output=outf)


def fetch_url_text(cfg: defs.Config, url: str, output: IO[str]) -> None:
    """Fetch a UTF-8 text file, write the UTF-8 contents to the supplied output stream."""
    cfg.log.debug("Fetching text %(url)s", {"url": url})
    resp: Final = requests.get(url, stream=True, timeout=1800)
    cfg.log.debug("Got a response: %(resp)r", {"resp": resp})
    resp.raise_for_status()
    contents: Final = resp.content
    if len(contents) <= 200:  # noqa: PLR2004
        cfg.log.debug(
            "Got %(count)d bytes of contents: %(contents)r",
            {"count": len(contents), "contents": contents},
        )
    else:
        cfg.log.debug("Got %(count)d bytes of text", {"count": len(contents)})
    output.write(contents.decode("UTF-8"))


def fetch_url_text_to_file(cfg: defs.Config, url: str, path: pathlib.Path) -> None:
    """Fetch a UTF-8 text file from the specified URL."""
    with util.tempfile_moved_if_okay(path) as tempf, tempf.open(mode="w", encoding="UTF-8") as outf:
        cfg.log.debug("Fetching text %(url)s into %(path)s", {"url": url, "path": path})
        fetch_url_text(cfg, url, output=outf)
