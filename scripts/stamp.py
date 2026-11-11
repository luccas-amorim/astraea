"""Stamps, as checked by a person, the country blocks that are ready for it.

A block is ready when it asserts something and carries `url`, `source`, `read_on` and
`confidence`, with `checked_by` still empty: it was read and prepared (by a session of
the human load, or by hand) and waits for the person who confers it at the source
(AGENTS.md, rule 3). This script never changes a value: it only writes
`checked_by: "human"` and the date of the person's reading in `read_on`, in the blocks the
person names.

    python scripts/stamp.py                      lists the blocks ready to be stamped
    python scripts/stamp.py --field BRA.penal_code --by "Name"
                                                 says what it would stamp (simulation)
    python scripts/stamp.py --field BRA.penal_code --field BRA.max_penalty --by "Name" --execute
                                                 stamps those two blocks
    python scripts/stamp.py --field BRA --by "Name" --execute
                                                 stamps every ready block of Brazil

`--by` is required to stamp, and the name goes in the commit message the script prints,
not in the data: the person's name stays out of countries.json (AGENTS.md, rule 8), and
the git author already records who committed. `--read-on` (default: today) is the day
the person read the source.

Simulation by default; --execute writes data/countries.json and nothing else. It refuses
a block that does not exist, asserts nothing, lacks part of the stamp, or is already
checked by a person or by the robot; when one named block is refused, nothing is written.

Exit codes: 0 fine; 1 a named block was refused (nothing written); 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vocabularies as voc  # noqa: E402
from transform import asserts, dumps, is_full_date, show  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# The stamp minus checked_by: what a prepared block must already have.
PREPARED = tuple(f for f in voc.STAMP_FIELDS if f != "checked_by")


class StampError(ValueError):
    """A named block cannot be stamped; the message says why."""


def ready(block) -> bool:
    return (
        isinstance(block, dict)
        and asserts(block)
        and block.get("checked_by") in (None, "")
        and all(block.get(f) not in (None, "") for f in PREPARED)
    )


def ready_blocks(countries: list[dict]) -> list[tuple[str, str]]:
    """(id, block) of every block ready to be stamped, in file order."""
    return [(c["id"], name) for c in countries for name in voc.COUNTRY_BLOCKS if ready(c.get(name))]


def resolve(countries: list[dict], fields: list[str]) -> list[tuple[str, str]]:
    """Turns "BRA.penal_code" and "BRA" into (id, block) pairs, or raises StampError."""
    by_id = {c["id"]: c for c in countries}
    chosen: list[tuple[str, str]] = []
    for field in fields:
        ident, _, name = field.partition(".")
        if ident not in by_id:
            raise StampError(f"{field}: {ident!r} is not a record of countries.json")
        record = by_id[ident]
        if not name:
            pairs = [(ident, b) for b in voc.COUNTRY_BLOCKS if ready(record.get(b))]
            if not pairs:
                raise StampError(f"{field}: no block of {ident} is ready to be stamped")
        elif name not in voc.COUNTRY_BLOCKS:
            raise StampError(f"{field}: {name!r} is not a block ({', '.join(voc.COUNTRY_BLOCKS)})")
        else:
            block = record.get(name)
            if not isinstance(block, dict):
                raise StampError(f"{field}: the block does not exist yet")
            if block.get("checked_by") not in (None, ""):
                raise StampError(f"{field}: already checked by {block['checked_by']}")
            if not asserts(block):
                raise StampError(f"{field}: the block asserts nothing (empty, with a reason)")
            if missing := [f for f in PREPARED if block.get(f) in (None, "")]:
                raise StampError(f"{field}: the block lacks {', '.join(missing)}; prepare it first")
            pairs = [(ident, name)]
        chosen += [p for p in pairs if p not in chosen]
    return chosen


def stamp(countries: list[dict], chosen: list[tuple[str, str]], read_on: str) -> list[dict]:
    """A copy of the records with the chosen blocks stamped. Values are not touched."""
    new = json.loads(json.dumps(countries))
    by_id = {c["id"]: c for c in new}
    for ident, name in chosen:
        block = by_id[ident][name]
        block["read_on"] = read_on
        block["checked_by"] = "human"
    return new


def describe(record: dict, name: str) -> list[str]:
    block = record[name]
    values = {
        k: v for k, v in block.items() if k not in voc.STAMP_FIELDS and k not in ("note", "reason")
    }
    lines = [f"  {record['id']}.{name}"]
    for key, value in values.items():
        lines.append(f"      {key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append(f"      read at: {block['url']}")
    lines.append(
        f"      source {block['source']}, read on {block['read_on']}, "
        f"confidence {block['confidence']}"
    )
    return lines


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--field",
        action="append",
        default=[],
        help='a block ("BRA.penal_code") or every ready block of a country ("BRA"); repeatable',
    )
    parser.add_argument("--by", help="the name of the person who checked (goes in the commit)")
    parser.add_argument("--read-on", help="the day the person read the source (default: today)")
    parser.add_argument("--execute", action="store_true", help="write (default: simulation)")
    parser.add_argument("--data", help="source directory (default: data/)")
    args = parser.parse_args(argv)

    data = Path(args.data) if args.data else ROOT / "data"
    path = data / "countries.json"
    countries = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in countries}

    if not args.field:
        pairs = ready_blocks(countries)
        print(
            f"{len(pairs)} blocks ready to be stamped "
            "(checked_by empty, the rest of the stamp in place):"
        )
        for ident, name in pairs:
            for line in describe(by_id[ident], name):
                print(line)
        if pairs:
            print('to stamp: python scripts/stamp.py --field ID.block --by "Your Name" --execute')
        return 0

    if not args.by or not args.by.strip():
        print('--by "Your Name" is required to stamp', file=sys.stderr)
        return 2
    read_on = args.read_on or date.today().isoformat()
    if not is_full_date(read_on):
        print(f"--read-on {read_on!r} is not a date YYYY-MM-DD", file=sys.stderr)
        return 2
    try:
        chosen = resolve(countries, args.field)
    except StampError as error:
        print(f"FAIL {error}")
        print("nothing was written")
        return 1

    for ident, name in chosen:
        for line in describe(by_id[ident], name):
            print(line)
        print(f"      -> checked_by: human, read_on: {read_on}")
    names = ", ".join(f"{i}.{n}" for i, n in chosen)
    if not args.execute:
        print(f"would stamp: {len(chosen)} blocks in {show(path)}")
        print("simulation: nothing was written; add --execute to write")
        return 0
    path.write_text(dumps(stamp(countries, chosen, read_on)), encoding="utf-8", newline="\n")
    print(f"stamped: {len(chosen)} blocks in {show(path)}")
    print("next, to regenerate the derived data and commit:")
    print("  python scripts/transform.py --draft --execute")
    print("  git add data/countries.json static/data")
    print(f'  git commit -m "Carimba {names} (conferido por {args.by.strip()} em {read_on})"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
