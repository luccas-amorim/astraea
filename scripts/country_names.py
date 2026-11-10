"""The map from the names a source writes to the ids of data/countries.json.

Each source has its own map file in data/ (`untc-names.json`, `cornell-names.json`),
kept by hand and checked against the UN Statistics Division M49 table: a name that is,
letter for letter, the English name of a record needs no line; any other name needs one,
with the id it stands for, or `id: null` and a `reason` when it is deliberately outside
the 197 (a territory, an entity outside D1). A name that is in neither stops the load
before anything is written: it is never guessed.

Why one file per source (docs/03-modelo-de-dados.md, "Nomes"): the same spelling can
mean different things in two sources, and an alias accepted for one would be silently
accepted for the other. Each line was checked for the source it names; the code that
reads the files is this one.
"""

from __future__ import annotations

from collections.abc import Iterable


class NameMapError(RuntimeError):
    """The map or the names read do not allow a safe load: nothing is written."""


def name_map(
    countries: list[dict], names_file: dict, key: str, file: str
) -> tuple[dict[str, str | None], dict[str, str], dict[str, dict]]:
    """name -> id (None: deliberately outside the 197); id -> reason for the records
    listed as `absent`; name -> the map line itself (for checks a source adds).

    `key` is the field that holds the source's spelling in each line ("untc",
    "cornell"); `file` is the name used in the messages."""
    ids = {c["id"] for c in countries}
    mapping: dict[str, str | None] = {c["name"]["en"]: c["id"] for c in countries}
    lines: dict[str, dict] = {}
    problems: list[str] = []
    for entry in names_file.get("names", []):
        name, ident = entry.get(key), entry.get("id")
        if not name or name in mapping:
            problems.append(f"{file}: {name!r} is empty, repeated or already a name")
            continue
        if ident is None and not entry.get("reason"):
            problems.append(f"{file}: {name!r} maps to nothing without a reason")
        if ident is not None and ident not in ids:
            problems.append(f"{file}: {name!r} maps to {ident!r}, not a record")
        mapping[name] = ident
        lines[name] = entry
    absent: dict[str, str] = {}
    for entry in names_file.get("absent", []):
        ident, reason = entry.get("id"), entry.get("reason")
        if ident not in ids or not reason:
            problems.append(f"{file}: absent {ident!r} is not a record or has no reason")
            continue
        absent[ident] = reason
    if problems:
        raise NameMapError("\n".join(problems))
    return mapping, absent, lines


def unknown_names(names: Iterable[str], mapping: dict[str, str | None], label: str, file: str):
    """The message for every name without a map, or None when all are known."""
    unknown = [name for name in names if name not in mapping]
    if not unknown:
        return None
    return "\n".join(
        f"{label}: {name!r} is not a name of countries.json nor of "
        f"{file}; check it in the M49 table and add it by hand"
        for name in unknown
    )
