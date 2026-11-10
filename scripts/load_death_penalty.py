"""Loads death_penalty into data/countries.json from the Cornell Center lists.

Reads the four lists of the Cornell Center on the Death Penalty Worldwide (the database
API behind the world map of dpw.lawschool.cornell.edu, one list per category) through the
`listing` adapter (astraea/sources/listing.py, format `cornell_dpw_status`), maps each
name to one of the 197 records (data/cornell-names.json), and writes the block with the
full stamp, confidence B and `checked_by: robot` (docs/03-modelo-de-dados.md, Entidade 1,
"Como a pena de morte é preenchida").

    python scripts/load_death_penalty.py              reads the four lists from the
                                                      network; says what it would change
    python scripts/load_death_penalty.py --execute    the same, and writes countries.json
    python scripts/load_death_penalty.py --json-dir DIR --read-on 2026-11-10
                                                      reads the four JSON files saved in
                                                      DIR (tests/fixtures/cornell/ names)

Simulation by default; --execute writes. It never deletes a record or a field: only the
death_penalty block is written. A block a person checked (`checked_by: human`, the
Amnesty annex) is left alone (AGENTS.md, rule 3), and the report says when Cornell reads
otherwise. A block whose values did not change is kept with its old `read_on`. A stamped
block of a country that is no longer in any list is kept, and the report says so: the
robot does not empty what it once read. A name that is not in data/cornell-names.json
nor the English name of a record stops the load before anything is written.

No `note` is written: the hypothesis of a death penalty for war or exceptional crimes is
a text of ours, and a text of ours needs an author (D4, pending).

The sha256 of each response is printed: it goes to CHANGELOG.md.

Exit codes: 0 fine; 1 the reading or the map failed (nothing written); 2 usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import country_names  # noqa: E402
import vocabularies as voc  # noqa: E402
from load_treaties import ordered  # noqa: E402
from transform import dumps, is_full_date, show  # noqa: E402

from astraea.engine.http import Client, FetchError  # noqa: E402
from astraea.sources.listing import (  # noqa: E402
    CORNELL_CATEGORIES,
    PARTED_FORMATS,
    Listing,
    Table,
    TableError,
    parse_cornell_dpw_status,
)

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://cornell-dpw.herokuapp.com/api/countries/by-law-status/1"
FORMAT = "cornell_dpw_status"
SOURCE = "cornell-dpw"
CONFIDENCE = "B"
RATE_LIMIT = 10  # per minute; neither host declares a Crawl-delay
NAMES_FILE = "cornell-names.json"
BLOCK = "death_penalty"
STAMP_ORDER = ("url", "source", "read_on", "confidence", "checked_by")

# The file of each list in --json-dir (and in tests/fixtures/cornell/).
FILES: dict[str, str] = {
    "Abolitionist": "abolitionist.json",
    "Abolitionist For Ordinary Crimes": "abolitionist-for-ordinary-crimes.json",
    "Abolitionist de facto": "abolitionist-de-facto.json",
    "Retentionist": "retentionist.json",
}
# Cornell category -> death_penalty.status (Amnesty's classification, docs/03), or None
# when the two definitions do not coincide and the record stays empty with a reason.
# The correspondence and why is in docs/03-modelo-de-dados.md.
STATUS: dict[str, str | None] = {
    "Abolitionist": "abolitionist_all_crimes",
    "Abolitionist For Ordinary Crimes": "abolitionist_ordinary_crimes",
    "Abolitionist de facto": None,
    "Retentionist": "retentionist",
}
UNMAPPED_REASON: dict[str, str] = {
    "Abolitionist de facto": (
        "Cornell lists it as abolitionist de facto (no execution in at least ten years); "
        "Amnesty's abolitionist in practice also asks for a policy or established practice "
        "of not executing, so the two do not coincide. Waits for the Amnesty annex, "
        "loaded by hand."
    ),
}
NOT_LISTED = (
    "Not in any of the four lists of the Cornell Center on the Death Penalty Worldwide "
    "at the reading that created this block. Waits for the Amnesty annex, loaded by hand."
)

assert set(FILES) == set(STATUS) == set(CORNELL_CATEGORIES)
assert all(STATUS[c] is not None or c in UNMAPPED_REASON for c in STATUS)


class LoadError(RuntimeError):
    """The map or the data do not allow a safe load: nothing is written."""


def category_urls() -> dict[str, str]:
    return PARTED_FORMATS[FORMAT].urls(BASE)


# ------------------------------------------------------------------ the names


def match(table: Table, names_file: dict, countries: list[dict]) -> dict[str, dict]:
    """id -> cells of the row. A name without a map, a map line whose ISO code the list no
    longer gives, or two names for one record stop everything."""
    try:
        mapping, _, lines = country_names.name_map(countries, names_file, "cornell", NAMES_FILE)
    except country_names.NameMapError as error:
        raise LoadError(str(error)) from error
    problem = country_names.unknown_names(
        (row.key for row in table.rows), mapping, "cornell", "data/" + NAMES_FILE
    )
    if problem:
        raise LoadError(problem)
    rows: dict[str, dict] = {}
    for row in table.rows:
        line = lines.get(row.key)
        if line is not None and line.get("iso2") != row.cells["iso_code"]:
            raise LoadError(
                f"cornell: {row.key!r} now comes with isoCode {row.cells['iso_code']!r}, "
                f"and {NAMES_FILE} was checked with {line.get('iso2')!r}; check it in the "
                "M49 table again"
            )
        ident = mapping[row.key]
        if ident is None:
            continue
        if ident in rows:
            raise LoadError(f"cornell: two names map to {ident}")
        rows[ident] = dict(row.cells) | {"name": row.key}
    return rows


# ------------------------------------------------------------------ the block


def block_for(cells: dict | None, urls: dict[str, str], read_on: str) -> dict:
    if cells is None:
        return {"reason": NOT_LISTED}
    category = cells["category"]
    status = STATUS[category]
    if status is None:
        return {"reason": UNMAPPED_REASON[category]}
    if status not in voc.VOCABULARIES[f"{BLOCK}.status"]:
        raise LoadError(f"{status!r} is not one of {list(voc.VOCABULARIES[BLOCK + '.status'])}")
    return {
        "status": status,
        "url": urls[category],
        "source": SOURCE,
        "read_on": read_on,
        "confidence": CONFIDENCE,
        "checked_by": "robot",
    }


def _values(block: dict | None) -> dict:
    return {k: v for k, v in (block or {}).items() if k != "read_on"}


def _asserted(block: dict | None) -> bool:
    return isinstance(block, dict) and block.get("status") is not None


def plan(
    countries: list[dict], table: Table, names_file: dict, read_on: str
) -> tuple[list[dict], list[str]]:
    """The new countries.json and the lines of the report. Pure: no file, no network."""
    rows = match(table, names_file, countries)
    urls = category_urls()
    report: list[str] = []
    out: list[dict] = []
    for country in countries:
        ident = country["id"]
        record = dict(country)
        old = country.get(BLOCK)
        cells = rows.get(ident)
        new = block_for(cells, urls, read_on)
        if isinstance(old, dict) and old.get("checked_by") == "human":
            line = f"left alone (checked by a person): {ident}.{BLOCK}"
            if new.get("status") != old.get("status"):
                said = cells["category"] if cells else "not listed"
                line += f"; Cornell reads {said!r}, the block says {old.get('status')!r}"
            report.append(line)
        elif _values(old) == _values(new):
            pass  # same values: keep the old block and its read_on
        elif cells is None and _asserted(old):
            report.append(
                f"kept (no longer in the Cornell lists): {ident}.{BLOCK} = "
                f"{old['status']!r}, read on {old.get('read_on')}"
            )
        else:
            record[BLOCK] = new
            shown = new.get("status") or "empty"
            if old is None:
                report.append(f"new: {ident}.{BLOCK} = {shown}")
            else:
                changes = [
                    f"{k}: {old.get(k)!r} -> {new.get(k)!r}"
                    for k in dict.fromkeys([*old, *new])
                    if k != "read_on" and old.get(k) != new.get(k)
                ]
                report.append(f"changed: {ident}.{BLOCK}: " + "; ".join(changes))
        out.append(ordered(record))
    return out, report


def summary(countries: list[dict]) -> str:
    count: dict[str, int] = {}
    for c in countries:
        block = c.get(BLOCK) or {}
        key = block.get("status") or "empty"
        count[key] = count.get(key, 0) + 1
    return f"{BLOCK}: " + ", ".join(f"{n} {k}" for k, n in sorted(count.items()))


# ------------------------------------------------------------------ reading


def read_table(json_dir: Path | None) -> tuple[Table, list[str]]:
    if json_dir:
        bodies = {c: (json_dir / FILES[c]).read_bytes() for c in CORNELL_CATEGORIES}
        table = parse_cornell_dpw_status(bodies)
        urls = category_urls()
    else:
        client = Client(RATE_LIMIT, respects_robots=True)
        listing = Listing("listing:cornell-dpw", BASE, FORMAT, client, RATE_LIMIT)
        table, responses = listing.read()
        urls = listing.urls()
        bodies = {c: r.body for c, r in zip(CORNELL_CATEGORIES, responses, strict=True)}
    lines = [
        f"{c}: {urls[c]}: {len(raw)} bytes, sha256 {hashlib.sha256(raw).hexdigest()}"
        for c, raw in bodies.items()
    ]
    lines.append(table.sentinel)
    return table, lines


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--execute", action="store_true", help="write (default: simulation)")
    parser.add_argument("--json-dir", help="read the four JSON files from here, not the network")
    parser.add_argument("--read-on", help="date of the reading, YYYY-MM-DD (with --json-dir)")
    parser.add_argument("--data", help="source directory (default: data/)")
    args = parser.parse_args(argv)

    data = Path(args.data) if args.data else ROOT / "data"
    json_dir = Path(args.json_dir) if args.json_dir else None
    if json_dir and not args.read_on:
        print("--json-dir needs --read-on: the date the files were downloaded", file=sys.stderr)
        return 2
    read_on = args.read_on or date.today().isoformat()
    if not is_full_date(read_on):
        print(f"--read-on {read_on!r} is not a date YYYY-MM-DD", file=sys.stderr)
        return 2

    path = data / "countries.json"
    countries = json.loads(path.read_text(encoding="utf-8"))
    names_file = json.loads((data / NAMES_FILE).read_text(encoding="utf-8"))
    try:
        table, lines = read_table(json_dir)
        new, report = plan(countries, table, names_file, read_on)
    except (TableError, FetchError, LoadError, OSError) as error:
        print(f"FAIL {error}")
        print("nothing was written")
        return 1

    for line in [*lines, *report, summary(new)]:
        print(line)
    text = dumps(new)
    changed = sum(1 for line in report if line.startswith(("new:", "changed:")))
    if path.read_text(encoding="utf-8") == text:
        print(f"up to date: {show(path)}")
    elif args.execute:
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote: {show(path)} ({changed} blocks)")
    else:
        print(f"would write: {show(path)} ({changed} blocks)")
        print("simulation: nothing was written; add --execute to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
