"""Tabelião: loads genocide_convention and rome_statute into data/countries.json.

Reads the per-treaty XML of the UN Treaty Collection (chapters IV-1 and XVIII-10) through
the `listing` adapter (astraea/sources/listing.py), maps each participant name to one of
the 197 records (data/untc-names.json), and writes the two blocks with the full stamp and
`checked_by: robot` (docs/03-modelo-de-dados.md, Entidade 1).

    python scripts/load_treaties.py                   reads the two XML files from the
                                                      UNTC; says what it would change
    python scripts/load_treaties.py --execute         the same, and writes countries.json
    python scripts/load_treaties.py --xml-dir DIR --read-on 2026-11-10
                                                      reads IV-1.en.xml and XVIII-10.en.xml
                                                      saved in DIR instead of the network

Simulation by default; --execute writes. It never deletes a record or a field: only the
two treaty blocks are written. A block a person checked (`checked_by: human`) is left
alone (AGENTS.md, rule 3). A block whose values did not change is kept as it is, with its
old `read_on`, so a monthly reading without news gives an empty diff. A participant name
that is not in data/untc-names.json nor the English name of a record stops the load
before anything is written: it is never guessed.

The sha256 of each response is printed: it goes to CHANGELOG.md, which is what makes the
reading count as `robot` (docs/03, "Confiança por registro").

Exit codes: 0 fine; 1 the reading or the map failed (nothing written); 2 usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import country_names  # noqa: E402
import vocabularies as voc  # noqa: E402
from transform import dumps, is_full_date, show  # noqa: E402

from astraea.engine.http import Client, FetchError  # noqa: E402
from astraea.sources.listing import Listing, Table, TableError, parse_untc_treaty  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://treaties.un.org/doc/Publication/MTDSG/"
SOURCE = "untc"
CONFIDENCE = "A"
NAMES_FILE = "untc-names.json"


@dataclass(frozen=True)
class Treaty:
    block: str  # the field of countries.json
    chapter: str  # MTDSG number
    file: str  # the name of the XML file
    path: str  # path under BASE


TREATIES = (
    Treaty("genocide_convention", "IV-1", "IV-1.en.xml", "Volume%20I/Chapter%20IV/IV-1.en.xml"),
    Treaty(
        "rome_statute",
        "XVIII-10",
        "XVIII-10.en.xml",
        "Volume%20II/Chapter%20XVIII/XVIII-10.en.xml",
    ),
)
# The order of the keys of a country record (docs/03, Entidade 1).
RECORD_ORDER = (
    "id",
    "name",
    "un_status",
    "un_member_since",
    "penal_code",
    "domestic_genocide",
    "genocide_convention",
    "rome_statute",
    "max_penalty",
    "death_penalty",
    "situations",
    "promotion",
    "valid_until",
    "validity_note",
)
STAMP_ORDER = ("url", "source", "read_on", "confidence", "checked_by")


class LoadError(RuntimeError):
    """The map or the data do not allow a safe load: nothing is written."""


# ------------------------------------------------------------------ the name map


def name_map(countries: list[dict], names_file: dict) -> tuple[dict[str, str | None], dict]:
    """UNTC name -> id (None: deliberately outside the 197), and id -> reason for the
    records that stay empty. The English names of countries.json match letter for letter;
    the rest comes from data/untc-names.json (scripts/country_names.py)."""
    try:
        mapping, absent, _ = country_names.name_map(countries, names_file, "untc", NAMES_FILE)
    except country_names.NameMapError as error:
        raise LoadError(str(error)) from error
    return mapping, absent


def match(table: Table, mapping: dict[str, str | None], chapter: str) -> dict[str, dict]:
    """id -> cells of the row. A name without a map stops everything."""
    rows: dict[str, dict] = {}
    problem = country_names.unknown_names(
        (row.key for row in table.rows), mapping, chapter, "data/" + NAMES_FILE
    )
    if problem:
        raise LoadError(problem)
    for row in table.rows:
        ident = mapping[row.key]
        if ident is None:
            continue
        if ident in rows:
            raise LoadError(f"{chapter}: two rows map to {ident}")
        rows[ident] = dict(row.cells)
    return rows


# ------------------------------------------------------------------ the blocks


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def _participation(cells: dict | None) -> str:
    if cells is None:
        return "none"
    if cells["struck_out"]:
        return "withdrawn"
    if cells["bound_since"]:
        return "party"
    return "signatory" if cells["signature"] else "none"


def genocide_block(cells: dict | None) -> dict:
    participation = _participation(cells)
    if participation == "withdrawn":
        raise LoadError("IV-1: a struck-out row in the Genocide Convention (no withdrawal clause)")
    block: dict = {"participation": participation}
    if cells is None:
        block |= {
            "signature": None,
            "bound_since": None,
            "consent_type": None,
            "reservations": None,
            "reservations_article_ix": None,
            "objections": None,
        }
        return block
    return block | {
        "signature": cells["signature"],
        "bound_since": cells["bound_since"],
        "consent_type": cells["consent_type"],
        "reservations": _yes(cells["declarations"]),
        "reservations_article_ix": _yes("IX" in cells["articles"]),
        "objections": _yes(cells["objections"]),
    }


def rome_block(cells: dict | None) -> dict:
    block: dict = {"participation": _participation(cells)}
    if cells is None:
        return block | {
            "signature": None,
            "bound_since": None,
            "consent_type": None,
            "withdrawal": None,
            "withdrawal_notified": None,
            "objections": None,
        }
    rescinded = cells["withdrawal_rescinded"]
    return block | {
        "signature": cells["signature"],
        "bound_since": cells["bound_since"],
        "consent_type": cells["consent_type"],
        "withdrawal": None if rescinded else cells["withdrawal_effect"],
        "withdrawal_notified": None if rescinded else cells["withdrawal_notified"],
        "objections": _yes(cells["objections"]),
    }


BUILDERS = {"genocide_convention": genocide_block, "rome_statute": rome_block}


def stamped(block: dict, url: str, read_on: str) -> dict:
    return block | {
        "url": url,
        "source": SOURCE,
        "read_on": read_on,
        "confidence": CONFIDENCE,
        "checked_by": "robot",
    }


def check_block(name: str, ident: str, block: dict) -> None:
    """The closed vocabularies and the full dates, before anything is written."""
    for key, value in block.items():
        vocabulary = voc.VOCABULARIES.get(f"{name}.{key}")
        if value is not None and vocabulary is not None and value not in vocabulary:
            raise LoadError(f"{ident}.{name}.{key}: {value!r} is not one of {list(vocabulary)}")
    for key in voc.TREATY_DATE_FIELDS[name]:
        if block.get(key) is not None and not is_full_date(block[key]):
            raise LoadError(f"{ident}.{name}.{key}: {block[key]!r} is not a full date")


def _values(block: dict | None) -> dict:
    """What a block says, without when it was read."""
    return {k: v for k, v in (block or {}).items() if k != "read_on"}


def ordered(record: dict) -> dict:
    known = [k for k in RECORD_ORDER if k in record]
    return {k: record[k] for k in known + [k for k in record if k not in RECORD_ORDER]}


def plan(
    countries: list[dict],
    tables: dict[str, Table],
    names_file: dict,
    read_on: str,
) -> tuple[list[dict], list[str]]:
    """The new countries.json and the lines of the report. Pure: no file, no network."""
    mapping, absent = name_map(countries, names_file)
    rows = {t.block: match(tables[t.block], mapping, t.chapter) for t in TREATIES}
    report: list[str] = []
    out: list[dict] = []
    for country in countries:
        ident = country["id"]
        record = dict(country)
        for treaty in TREATIES:
            old = country.get(treaty.block)
            cells = rows[treaty.block].get(ident)
            if ident in absent:
                if cells is not None:
                    raise LoadError(f"{treaty.chapter}: {ident} is in the table and in 'absent'")
                new = {"reason": absent[ident]}
            else:
                new = BUILDERS[treaty.block](cells)
                check_block(treaty.block, ident, new)
                new = stamped(new, BASE + treaty.path, read_on)
            if isinstance(old, dict) and old.get("checked_by") == "human":
                report.append(f"left alone (checked by a person): {ident}.{treaty.block}")
                continue
            if _values(old) == _values(new):
                continue  # same values: keep the old block and its read_on
            record[treaty.block] = new
            if old is None:
                report.append(f"new: {ident}.{treaty.block} = {new.get('participation', 'empty')}")
            else:
                changes = [
                    f"{k}: {old.get(k)!r} -> {new.get(k)!r}"
                    for k in dict.fromkeys([*old, *new])
                    if k != "read_on" and old.get(k) != new.get(k)
                ]
                report.append(f"changed: {ident}.{treaty.block}: " + "; ".join(changes))
        out.append(ordered(record))
    return out, report


def summary(countries: list[dict]) -> list[str]:
    lines = []
    for treaty in TREATIES:
        count: dict[str, int] = {}
        for c in countries:
            block = c.get(treaty.block) or {}
            key = block.get("participation", "empty")
            count[key] = count.get(key, 0) + 1
        lines.append(
            f"{treaty.chapter} ({treaty.block}): "
            + ", ".join(f"{n} {k}" for k, n in sorted(count.items()))
        )
    return lines


# ------------------------------------------------------------------ reading


def read_tables(xml_dir: Path | None) -> tuple[dict[str, Table], list[str]]:
    tables: dict[str, Table] = {}
    lines: list[str] = []
    client = None if xml_dir else Client(30, respects_robots=True)
    for treaty in TREATIES:
        if xml_dir:
            raw = (xml_dir / treaty.file).read_bytes()
            table = parse_untc_treaty(raw)
        else:
            listing = Listing(f"listing:untc-{treaty.chapter.lower()}", BASE + treaty.path,
                              "untc_treaty", client)  # fmt: skip
            table, (response,) = listing.read()
            raw = response.body
        tables[treaty.block] = table
        lines.append(
            f"{treaty.chapter}: {len(raw)} bytes, sha256 {hashlib.sha256(raw).hexdigest()}; "
            f"{table.sentinel}"
        )
    return tables, lines


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--execute", action="store_true", help="write (default: simulation)")
    parser.add_argument("--xml-dir", help="read the two XML files from here, not the network")
    parser.add_argument("--read-on", help="date of the reading, YYYY-MM-DD (with --xml-dir)")
    parser.add_argument("--data", help="source directory (default: data/)")
    args = parser.parse_args(argv)

    data = Path(args.data) if args.data else ROOT / "data"
    xml_dir = Path(args.xml_dir) if args.xml_dir else None
    if xml_dir and not args.read_on:
        print("--xml-dir needs --read-on: the date the files were downloaded", file=sys.stderr)
        return 2
    read_on = args.read_on or date.today().isoformat()
    if not is_full_date(read_on):
        print(f"--read-on {read_on!r} is not a date YYYY-MM-DD", file=sys.stderr)
        return 2

    path = data / "countries.json"
    countries = json.loads(path.read_text(encoding="utf-8"))
    names_file = json.loads((data / "untc-names.json").read_text(encoding="utf-8"))
    try:
        tables, lines = read_tables(xml_dir)
        new, report = plan(countries, tables, names_file, read_on)
    except (TableError, FetchError, LoadError, OSError) as error:
        print(f"FAIL {error}")
        print("nothing was written")
        return 1

    for line in lines + report + summary(new):
        print(line)
    text = dumps(new)
    if path.read_text(encoding="utf-8") == text:
        print(f"up to date: {show(path)}")
    elif args.execute:
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote: {show(path)} ({len(report)} blocks)")
    else:
        print(f"would write: {show(path)} ({len(report)} blocks)")
        print("simulation: nothing was written; add --execute to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
