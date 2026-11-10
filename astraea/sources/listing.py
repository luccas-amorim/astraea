"""Listing: a table that changes slowly, read whole, one reference per row.

The origin publishes one document that is the whole table (the status of a treaty, a
list of cases). `list` reads it once, checks that it is whole, and returns one reference
per row; the reference id is the row key plus a digest of the row, so a row that did not
change is not read again (the source state already saw it) and **a row that changed
comes back as new**. That is the whole idea, inherited from Argos: the table is cheap to
read, and the diff between two readings is what matters.

`since` is not used: a table has no dates of its own. The state does the filtering.

The parsing of each origin is a **format**: a function from the raw bytes to a `Table`,
which fails (`TableError`) when the table is not whole. Formats are registered in
`FORMATS`. The first one is `untc_treaty`, the per-treaty XML of the United Nations
Treaty Collection (`docs/02-fontes.md`, 1.1), read by the Tabelião.

Some origins publish the table in **parts**, one document per value of a query
parameter (the Cornell death penalty lists, one per category). Those formats are in
`PARTED_FORMATS`: the listing makes one request per part and the format reads them
together, so the table is still whole or refused as a whole.

Configuration:
    {"type": "listing", "id": "listing:untc-iv-1", "format": "untc_treaty",
     "url": "https://treaties.un.org/doc/Publication/MTDSG/Volume%20I/Chapter%20IV/IV-1.en.xml",
     "rate_limit_per_minute": 30}
    {"type": "listing", "id": "listing:cornell-dpw", "format": "cornell_dpw_status",
     "url": "https://cornell-dpw.herokuapp.com/api/countries/by-law-status/1",
     "rate_limit_per_minute": 10}
"""

from __future__ import annotations

import codecs
import hashlib
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from astraea.engine.capture import build_document
from astraea.engine.contract import Document, Reference
from astraea.engine.http import Client, Response, Transport, urllib_transport


class TableError(ValueError):
    """The table read is not whole, or has something the format does not know.

    Never guessed around: an unknown action code, a date in another shape or a count
    that does not add up stop the reading, and the previous data stay as they were.
    """


@dataclass(frozen=True)
class Row:
    key: str  # stable inside the table: the participant, the case
    cells: Mapping[str, Any]

    def digest(self) -> str:
        """Changes when any cell changes: what makes a changed row be read again."""
        blob = json.dumps(dict(self.cells), sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Table:
    rows: tuple[Row, ...]
    sentinel: str  # what proved the table whole, in words, for the run report
    meta: Mapping[str, Any] = field(default_factory=dict)

    def row(self, key: str) -> Row | None:
        return next((r for r in self.rows if r.key == key), None)


Format = Callable[[bytes], Table]


@dataclass(frozen=True)
class PartedFormat:
    """A table published in parts: one document per value of `parameter`."""

    parse: Callable[[Mapping[str, bytes]], Table]
    parameter: str
    values: tuple[str, ...]

    def urls(self, base: str) -> dict[str, str]:
        """value -> URL, with the value percent-encoded as the origin's own page does
        (`%20`, not `+`)."""
        sep = "&" if "?" in base else "?"
        return {
            v: f"{base}{sep}{self.parameter}={urllib.parse.quote(v, safe='')}" for v in self.values
        }


class Listing:
    respects_robots = True

    def __init__(
        self,
        id: str,
        url: str,
        format: str,
        client: Client,
        rate_limit_per_minute: int = 30,
    ) -> None:
        if format not in FORMATS and format not in PARTED_FORMATS:
            known = sorted([*FORMATS, *PARTED_FORMATS])
            raise ValueError(f"unknown listing format: {format!r} (known: {known})")
        self.id = id
        self.url = url
        self.format = format
        self.client = client
        self.rate_limit_per_minute = rate_limit_per_minute

    @classmethod
    def from_config(cls, cfg: dict, transport: Transport = urllib_transport) -> Listing:
        limit = int(cfg.get("rate_limit_per_minute", 30))
        client = Client(limit, respects_robots=True, transport=transport)
        return cls(cfg["id"], cfg["url"], cfg["format"], client, limit)

    def urls(self) -> dict[str, str]:
        """part -> URL; a single-document format has one part, named ""."""
        parted = PARTED_FORMATS.get(self.format)
        return parted.urls(self.url) if parted else {"": self.url}

    def read(self) -> tuple[Table, tuple[Response, ...]]:
        """One request per part (one, for most formats); the table, and the responses it
        came from, in the order of the parts (for their hashes)."""
        responses = {part: self.client.request(url) for part, url in self.urls().items()}
        parted = PARTED_FORMATS.get(self.format)
        if parted:
            table = parted.parse({part: r.body for part, r in responses.items()})
        else:
            table = FORMATS[self.format](responses[""].body)
        return table, tuple(responses.values())

    def list(self, since: date) -> Iterator[Reference]:
        table, _ = self.read()
        for row in table.rows:
            yield Reference(
                source=self.id,
                source_id=f"{row.key}#{row.digest()}",
                url=f"{self.url}#{urllib.parse.quote(row.key)}",
                title=row.key,
                data={"cells": dict(row.cells), "sentinel": table.sentinel},
            )

    def fetch(self, ref: Reference) -> Document:
        """No second request: the row came whole with the table."""
        cells = dict((ref.data or {}).get("cells") or {})
        lines = [ref.title or ""] + [f"{k}: {v}" for k, v in sorted(cells.items())]
        raw = json.dumps(cells, sort_keys=True, ensure_ascii=False, default=str)
        return build_document(ref, "\n".join(lines), raw=raw.encode("utf-8"))

    def sentinel(self, doc: Document) -> bool:
        data = doc.ref.data or {}
        return bool(data.get("sentinel")) and bool(doc.ref.title) and "cells" in data


# ------------------------------------------------------------------ decoding and cleaning

_XML_ENCODING = re.compile(rb"""^\s*<\?xml[^>]*\bencoding\s*=\s*["']([A-Za-z0-9._-]+)["']""")
_XML_DECLARATION = re.compile(r"^\s*<\?xml[^>]*\?>")
_SUPERSCRIPT = re.compile(r"<superscript>.*?</superscript>", re.S)
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


def decode_xml(raw: bytes) -> str:
    """The text of an XML file by its own declaration, never by the HTTP header.

    The UNTC serves the XML as `text/html` without charset, and declares ISO-8859-1. As
    in the engine (`astraea.engine.text`), a declared ISO-8859-1 is read as cp1252, which
    is what such files carry in practice (Word quotes); a byte cp1252 does not define
    falls back to Latin-1, so no byte is lost.
    """
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8")
    m = _XML_ENCODING.match(raw)
    declared = m.group(1).decode("ascii").lower() if m else "utf-8"
    if declared in {"iso-8859-1", "latin-1", "latin1", "us-ascii", "windows-1252", "cp1252"}:
        return raw.decode("cp1252", errors=_LATIN1_FALLBACK)
    try:
        return raw.decode(declared)
    except (LookupError, UnicodeDecodeError) as error:
        raise TableError(f"cannot decode the XML as {declared}: {error}") from error


def _latin1(error: UnicodeDecodeError) -> tuple[str, int]:
    return error.object[error.start : error.end].decode("latin-1"), error.end


_LATIN1_FALLBACK = "astraea-latin1-fallback"
codecs.register_error(_LATIN1_FALLBACK, _latin1)


def parse_xml(raw: bytes) -> ET.Element:
    text = _XML_DECLARATION.sub("", decode_xml(raw), count=1)
    try:
        return ET.fromstring(text)
    except ET.ParseError as error:
        raise TableError(f"not well-formed XML: {error}") from error


def clean(text: str | None) -> str:
    """Visible text: footnote superscripts out, inline markup out, spaces collapsed.

    The UNTC writes the footnote marks as escaped markup inside the text
    (`Argentina&lt;superscript&gt;3&lt;/superscript&gt;`); the parser unescapes them, and
    here they go.
    """
    if not text:
        return ""
    text = _SUPERSCRIPT.sub("", text)
    text = _TAG.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def _texts(node: ET.Element | None, tag: str = "text") -> list[str]:
    if node is None:
        return []
    return [clean("".join(t.itertext())) for t in node.iter(tag)]


# ------------------------------------------------------------------ format: UNTC treaty XML

_MONTHS = {
    m: i
    for i, m in enumerate(
        ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"),
        start=1,
    )
}
# "22 Mar 1956 a", "[13 Jan 1999 ]", "17 March 2018"
_UNTC_DATE = re.compile(r"(\[)?\s*(\d{1,2}) ([A-Za-z]{3})[A-Za-z]* (\d{4})\s*([A-Za-z]*)\s*(\])?")
_ACTION = re.compile(r"([A-Za-z]+)\s*\(([A-Za-z]+)\)")
# "article IX", "articles VIII and IX", "Ad article IX", "article 87 (1)"
_ARTICLES = re.compile(
    r"\b[Aa]rticles?\s+((?:[IVXLC]+|\d+)(?:\s*(?:,|and|&)\s*(?:[IVXLC]+|\d+))*)\b"
)
_ACTION_NAMES = {
    "ratification": "ratification",
    "accession": "accession",
    "succession": "succession",
    "acceptance": "acceptance",
    "approval": "approval",
}


def untc_date(text: str) -> tuple[str, str, bool]:
    """(ISO date, action code, struck out). Struck out is the UNTC's square brackets: a
    signature or a binding that a withdrawal took away."""
    m = _UNTC_DATE.fullmatch(_SPACE.sub(" ", text).strip())
    if not m or m.group(3).lower() not in _MONTHS:
        raise TableError(f"date in an unknown shape: {text!r}")
    opened, day, month, year, code, closed = m.groups()
    if bool(opened) != bool(closed):
        raise TableError(f"unbalanced brackets: {text!r}")
    try:
        value = date(int(year), _MONTHS[month.lower()], int(day)).isoformat()
    except ValueError as error:
        raise TableError(f"not a date: {text!r}") from error
    return value, code, bool(opened)


def _actions(header: str) -> dict[str, str]:
    """The action codes the table itself declares in the header of its third column:
    "Accession(a), Succession(d), Ratification" -> {"a": accession, "d": succession,
    "": ratification}. The bare word at the end is the action without a code."""
    codes: dict[str, str] = {}
    for word, code in _ACTION.findall(header):
        if word.lower() not in _ACTION_NAMES:
            raise TableError(f"unknown action in the header: {word!r}")
        codes[code] = _ACTION_NAMES[word.lower()]
    bare = _ACTION.sub("", header).strip(" ,")
    if bare.lower() not in _ACTION_NAMES:
        raise TableError(f"the header does not name the action without a code: {header!r}")
    codes[""] = _ACTION_NAMES[bare.lower()]
    return codes


def articles(texts: list[str]) -> list[str]:
    """Articles that the texts refer to, as written ("IX", "87"), in order of first use."""
    found: list[str] = []
    for text in texts:
        for group in _ARTICLES.findall(text):
            for item in re.split(r"\s*(?:,|and|&)\s*", group):
                if item and item not in found:
                    found.append(item)
    return found


def _substantive(texts: list[str]) -> list[str]:
    """What is left of a declaration once the empty and the elided ("...") are out."""
    return [t for t in texts if t.strip(" .…")]


def _withdrawals(root: ET.Element, names: set[str]) -> dict[str, dict]:
    """The withdrawals note of the Rome Statute (art. 127): a table inside an end note.

    Each line: participant (with "*" when the withdrawal was later rescinded), date of
    notification, date of effect or "(Withdrawn)", depositary notification.
    """
    out: dict[str, dict] = {}
    for note in root.iter("Note"):
        heading = " ".join(_texts(note))
        table = note.find("table")
        if table is None or "withdraw" not in heading.lower():
            continue
        lines = [
            [clean("".join(c.itertext())) for c in row.iter("col")] for row in table.iter("row")
        ]
        if not lines or not lines[0] or not lines[0][0].lower().startswith("participant"):
            raise TableError("withdrawals note without its header line")
        for line in lines[1:]:
            if len(line) < 3:
                raise TableError(f"withdrawals note: short line {line!r}")
            name = line[0].rstrip(" *").strip()
            if name not in names:
                raise TableError(f"withdrawals note names {name!r}, who is not in the table")
            notified, _, _ = untc_date(line[1])
            rescinded = line[2].strip("() ").lower() == "withdrawn"
            effect = None if rescinded else untc_date(line[2])[0]
            out[name] = {
                "notified": notified,
                "effect": effect,
                "rescinded": rescinded,
                "notification": line[3] if len(line) > 3 else None,
            }
    return out


def parse_untc_treaty(raw: bytes) -> Table:
    """The per-treaty XML of the UNTC: participants, declarations, objections, withdrawals.

    The sentinel is the `Status` block of the header (the number of signatories and of
    parties the depositary declares), checked against the rows: the table is whole only
    when the rows count the same. The HTML page shows a "STATUS AS AT" line, but it is the
    time the page was generated, not a date of the data; the XML has no such line.
    """
    root = parse_xml(raw)
    status = root.find("./Treaty/Header/ExternalData/Status")
    if status is None:
        raise TableError("no Status block: not a treaty status file, or truncated")
    try:
        signatories = int(clean(status.findtext("Signatories")))
        parties = int(clean(status.findtext("Parties")))
    except ValueError as error:
        raise TableError("the Status block has no counts") from error
    title = clean(root.findtext("./Treaty/Header/ExternalData/Titlesect"))

    head = root.find("./Treaty/Participants/Table/TGroup/Thead/Row")
    body = root.find("./Treaty/Participants/Table/TGroup/Tbody/Rows")
    if head is None or body is None:
        raise TableError("no participants table")
    header = [clean("".join(e.itertext())) for e in head.findall("Entry")]
    if len(header) != 3 or header[0] != "Participant" or header[1] != "Signature":
        raise TableError(f"participants table with unknown columns: {header!r}")
    codes = _actions(header[2])

    rows: dict[str, dict[str, Any]] = {}
    for tr in body.findall("Row"):
        entries = ["".join(e.itertext()) for e in tr.findall("Entry")]
        if len(entries) != 3:
            raise TableError(f"row with {len(entries)} cells: {entries!r}")
        name = clean(entries[0])
        if not name or name in rows:
            raise TableError(f"empty or repeated participant: {name!r}")
        cells: dict[str, Any] = {
            "signature": None,
            "bound_since": None,
            "consent_type": None,
            "struck_out": False,
        }
        if clean(entries[1]):
            cells["signature"], code, struck = untc_date(entries[1])
            if code:
                raise TableError(f"{name}: action code in the signature column: {entries[1]!r}")
            cells["struck_out"] = struck
        if clean(entries[2]):
            cells["bound_since"], code, struck = untc_date(entries[2])
            if code not in codes:
                raise TableError(f"{name}: action code {code!r} not in the header {header[2]!r}")
            cells["consent_type"] = codes[code]
            cells["struck_out"] = cells["struck_out"] or struck
        rows[name] = cells

    names = set(rows)
    declarations: dict[str, list[str]] = {}
    for node in root.findall("./Treaty/Declarations/Declaration"):
        name = clean(node.findtext("Participant"))
        if name not in names:
            raise TableError(f"declaration by {name!r}, who is not in the table")
        paragraphs = [clean("".join(t.itertext())) for t in node.findall("text")]
        kept = [
            p
            for t, p in zip(node.findall("text"), paragraphs, strict=True)
            if t.get("type") != "title"
        ]
        declarations.setdefault(name, []).extend(_substantive(kept))
    objectors: set[str] = set()
    for node in root.findall("./Treaty/Objections/Objection"):
        name = clean(node.findtext("Participant"))
        if name not in names:
            raise TableError(f"objection by {name!r}, who is not in the table")
        objectors.add(name)
    withdrawals = _withdrawals(root, names)

    for name, cells in rows.items():
        texts = declarations.get(name, [])
        cells["declarations"] = bool(texts)
        cells["articles"] = articles(texts)
        cells["objections"] = name in objectors
        w = withdrawals.get(name)
        cells["withdrawal_notified"] = w["notified"] if w else None
        cells["withdrawal_effect"] = w["effect"] if w else None
        cells["withdrawal_rescinded"] = bool(w and w["rescinded"])
        if cells["struck_out"] and not (w and w["effect"]):
            raise TableError(f"{name}: struck out, but the withdrawals note does not say so")

    bound = sum(1 for c in rows.values() if c["bound_since"] and not c["struck_out"])
    signed = sum(1 for c in rows.values() if c["signature"] and not c["struck_out"])
    if bound != parties or signed != signatories:
        raise TableError(
            f"the Status block says {signatories} signatories and {parties} parties; "
            f"the rows count {signed} and {bound}"
        )
    return Table(
        rows=tuple(Row(name, cells) for name, cells in rows.items()),
        sentinel=f"Status: {signatories} signatories, {parties} parties; the rows agree",
        meta={"title": title, "signatories": signatories, "parties": parties},
    )


# ------------------------------------------------------------------ format: Cornell lists

# The four values of `lawStatus` that the legend of the world map on
# dpw.lawschool.cornell.edu sends to the database API, as the page writes them.
CORNELL_CATEGORIES: tuple[str, ...] = (
    "Abolitionist",
    "Abolitionist For Ordinary Crimes",
    "Abolitionist de facto",
    "Retentionist",
)
_CORNELL_KEYS = frozenset({"displayName", "isoCode"})
_ISO2 = re.compile(r"[A-Z]{2}")


def _cornell_list(category: str, raw: bytes) -> list[tuple[str, str | None]]:
    try:
        items = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise TableError(f"{category}: not a JSON document ({error})") from error
    if not isinstance(items, list):
        raise TableError(f"{category}: not a JSON list")
    if not items:
        raise TableError(f"{category}: an empty list")
    out = []
    for item in items:
        if not isinstance(item, dict) or set(item) != _CORNELL_KEYS:
            raise TableError(f"{category}: an item of unknown shape: {item!r}")
        name, iso = item["displayName"], item["isoCode"]
        if not isinstance(name, str) or not name.strip():
            raise TableError(f"{category}: an item without a name: {item!r}")
        if iso is not None and not (isinstance(iso, str) and _ISO2.fullmatch(iso)):
            raise TableError(f"{category}: {name!r} with an isoCode of unknown shape: {iso!r}")
        out.append((_SPACE.sub(" ", name).strip(), iso))
    return out


def parse_cornell_dpw_status(parts: Mapping[str, bytes]) -> Table:
    """The four lists of the Cornell Center on the Death Penalty Worldwide.

    The legend of the world map on dpw.lawschool.cornell.edu asks the database API, once
    per category, for the countries in it (`/api/countries/by-law-status/1?lawStatus=…`,
    1 being English): a JSON list of `{displayName, isoCode}`, the code being ISO 3166-1
    alpha-2 or null. The table is the four lists together.

    The page gives no count per category, so the sentinel is the shape itself: the four
    lists came, each a non-empty JSON list of objects with exactly those two keys, and no
    name is in two of them (nor twice in one). Anything else stops the reading.
    """
    if set(parts) != set(CORNELL_CATEGORIES):
        missing = sorted(set(CORNELL_CATEGORIES) - set(parts))
        unknown = sorted(set(parts) - set(CORNELL_CATEGORIES))
        raise TableError(f"the four lists did not come: missing {missing}, unknown {unknown}")
    rows: dict[str, dict[str, Any]] = {}
    counts: dict[str, int] = {}
    for category in CORNELL_CATEGORIES:
        items = _cornell_list(category, parts[category])
        for name, iso in items:
            if name in rows:
                where = rows[name]["category"]
                raise TableError(f"{name!r} is in {where!r} and again in {category!r}")
            rows[name] = {"category": category, "iso_code": iso}
        counts[category] = len(items)
    listed = ", ".join(f"{n} {c}" for c, n in counts.items())
    return Table(
        rows=tuple(Row(name, cells) for name, cells in rows.items()),
        sentinel=f"4 lists ({listed}); each one whole, no name in two",
        meta={"counts": counts},
    )


FORMATS: dict[str, Format] = {"untc_treaty": parse_untc_treaty}
PARTED_FORMATS: dict[str, PartedFormat] = {
    "cornell_dpw_status": PartedFormat(parse_cornell_dpw_status, "lawStatus", CORNELL_CATEGORIES),
}
