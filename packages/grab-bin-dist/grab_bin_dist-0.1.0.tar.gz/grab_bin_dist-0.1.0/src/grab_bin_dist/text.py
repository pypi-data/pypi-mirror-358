# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Parse and generate text data."""

from __future__ import annotations

import dataclasses
import re
import typing
from html import parser as html_parser

from . import defs


if typing.TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator
    from typing import Final

    from . import worker


RE_HAS_PATTERNS: Final = re.compile(r"@ [A-Za-z0-9_]+ @", re.X)
"""Find any replacement patterns left unreplaced."""


@dataclasses.dataclass
class UnsubstitutedError(defs.GrabError):
    """Some patterns in a template were not substituted."""

    contents: str
    """The text contents after substituting the supplied variables."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Some patterns were not substituted: {self.contents!r}"


class HRefHtmlParser(html_parser.HTMLParser):
    """Look for `<a href="...">...</a> tags in the HTML source."""

    _href_links: list[str]

    def __init__(self, *, convert_charrefs: bool = True) -> None:
        """Construct a `HRefHtmlParser` object."""
        super().__init__(convert_charrefs=convert_charrefs)
        self._href_links = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Look for `<a href="...">` start tags."""
        if tag != "a":
            return

        hrefs: Final = [value for name, value in attrs if name == "href" and value is not None]
        if not hrefs:
            return

        # Only store the final `href` attribute
        self._href_links.append(hrefs[-1])

    @property
    def href_links(self) -> Iterator[str]:
        """Return an iterator over the parsed links."""
        return iter(self._href_links)


def extract_html_links(contents: str, regex: re.Pattern[str]) -> list[tuple[str, dict[str, str]]]:
    """Extract link targets that match a particular pattern.

    Returns a tuple containing the link URL and the `.groupdict()` of the successful match.
    """
    parser: Final = HRefHtmlParser()
    parser.feed(contents)
    return [
        (full, rel.groupdict())
        for full, rel in ((full, regex.match(full)) for full in parser.href_links)
        if rel is not None
    ]


def substitute_in_files(
    cfg: worker.Config,
    srcdir: pathlib.Path,
    dstdir: pathlib.Path,
    replace: dict[str, str],
) -> None:
    """Substitute strings in files."""
    dstdir.mkdir(mode=0o755)
    cfg.log.info(
        "Replacing strings in files from %(src)s to %(dst)s",
        {"src": srcdir, "dst": dstdir},
    )

    def do_replace(contents: str) -> str:
        """Replace the placeholders in a single file's contents."""
        for pattern, repl in replace.items():
            contents = contents.replace(pattern, repl)

        if RE_HAS_PATTERNS.match(contents):
            raise UnsubstitutedError(contents)

        return contents

    for src in (path for path in srcdir.iterdir() if path.is_file() and path.name.endswith(".in")):
        dst = dstdir / src.with_suffix("").name
        cfg.log.info("- %(src)s -> %(dst)s", {"src": src, "dst": dst})
        dst.write_text(do_replace(src.read_text(encoding="UTF-8")), encoding="UTF-8")
