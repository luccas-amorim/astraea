"""Makes the UNTC test fixtures from the XML files the engine downloaded.

    python scripts/trim_untc_fixtures.py --xml-dir DIR             says what it would write
    python scripts/trim_untc_fixtures.py --xml-dir DIR --execute   writes tests/fixtures/untc/

The fixture keeps the file byte for byte except the prose of the depositary: every
paragraph of the declarations, reservations, objections, notifications and end notes is
replaced by a short marker that names the articles the paragraph refers to. The
participants table, the Status block, the dates and the table of withdrawals stay as they
came. The repository does not carry third-party text (AGENTS.md, rule 2), and the UN terms
do not allow redistributing it; the facts of the table are what the tests need.

Before writing, the script parses the original and the fixture and stops if the two
tables differ in anything: the fixture must say to the adapter exactly what the original
says. The sha256 of the original goes to CHANGELOG.md. Simulation by default; never
deletes.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from pathlib import Path

from astraea.sources.listing import articles, clean, parse_untc_treaty

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "fixtures" / "untc"
FILES = ("IV-1.en.xml", "XVIII-10.en.xml")
SECTIONS = (
    b"Declarations",
    b"DeclarationsUnderArticle",
    b"Objections",
    b"Notifications",
    b"EndNotes",
)
_TEXT = re.compile(rb"(<text(?: type=\"(?P<type>[a-z]+)\")?>)(?P<body>.*?)(</text>)", re.S)
_RIGHT = re.compile(rb"^&lt;right&gt;[^&]*&lt;/right&gt;$")  # a date line: kept


def marker(body: bytes, in_withdrawals: bool) -> bytes:
    text = clean(html.unescape(body.decode("latin-1")))
    if not text.strip(" .…") or _RIGHT.match(body.strip()):
        return body
    found = articles([text])
    words = "[text of the depositary omitted in this fixture"
    if in_withdrawals:
        words += "; notifications of withdrawal"
    if found:
        words += f"; refers to article{'s' if len(found) > 1 else ''} {', '.join(found)}"
    return (words + "]").encode("ascii")


def _trim_section(section: bytes) -> bytes:
    def note(m: re.Match) -> bytes:
        chunk = m.group(0)
        withdrawals = b"<table>" in chunk and b"withdraw" in chunk.lower()
        return _TEXT.sub(
            lambda t: (
                t.group(1)
                + (
                    t.group("body")
                    if t.group("type") == b"title"
                    else marker(t.group("body"), withdrawals)
                )
                + t.group(4)
            ),
            chunk,
        )

    # one unit per entry, so the withdrawals note is recognised as a whole
    return re.sub(
        rb"<(Note|Declaration|Objection|Notification)>.*?</\1>", note, section, flags=re.S
    )


def trim(raw: bytes) -> bytes:
    out = re.sub(
        rb"(<TreatyNote><Text>).*?(</Text></TreatyNote>)",
        lambda m: m.group(1) + b"[text of the depositary omitted in this fixture]" + m.group(2),
        raw,
        flags=re.S,
    )
    for name in SECTIONS:
        out = re.sub(
            rb"<" + name + rb">.*?</" + name + rb">",
            lambda m: _trim_section(m.group(0)),
            out,
            flags=re.S,
        )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--xml-dir", required=True, help="where the downloaded files are")
    parser.add_argument("--execute", action="store_true", help="write (default: simulation)")
    args = parser.parse_args(argv)
    for name in FILES:
        raw = (Path(args.xml_dir) / name).read_bytes()
        fixture = trim(raw)
        if parse_untc_treaty(raw) != parse_untc_treaty(fixture):
            print(f"FAIL {name}: the fixture does not parse as the original; nothing written")
            return 1
        target = OUT / name
        print(
            f"{name}: original {len(raw)} bytes, sha256 {hashlib.sha256(raw).hexdigest()}; "
            f"fixture {len(fixture)} bytes, sha256 {hashlib.sha256(fixture).hexdigest()}"
        )
        if target.exists() and target.read_bytes() == fixture:
            print(f"up to date: {target.relative_to(ROOT).as_posix()}")
        elif args.execute:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(fixture)
            print(f"wrote: {target.relative_to(ROOT).as_posix()}")
        else:
            print(f"would write: {target.relative_to(ROOT).as_posix()}")
    if not args.execute:
        print("simulation: nothing was written; add --execute to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
