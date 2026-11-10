"""Validates data/ and generates static/data/ (docs/03-modelo-de-dados.md).

data/ is the source, edited by people and robots; static/data/ is derived, written only
by this script and never edited. The eleven checks of "O que o validador reprova" are
here, numbered as in the document; the closed vocabularies and the field keys come from
scripts/vocabularies.py.

    python scripts/transform.py --strict            validates; says what it would write
    python scripts/transform.py --draft             the same, relaxing checks 3 and 6
    python scripts/transform.py --draft --execute   writes static/data/; never deletes
    python scripts/transform.py --draft --check     compares with what is in static/data/

--strict is the default. --draft is for the initial load: a field without its stamp and
a court status not yet confirmed by a person are counted as drafts in quality.json
instead of failing. The derived files are the same in both modes.

Exit codes: 0 fine; 1 the data does not pass, or static/data/ is out of date (--check);
2 usage or file error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_lexicon  # noqa: E402
import vocabularies as voc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

STRUCTURE = 0  # a malformed file or record: not one of the eleven, but nothing passes with it
CHECKS = {
    STRUCTURE: "structure",
    1: "id",
    2: "closed vocabulary",
    3: "stamp",
    4: "source",
    5: "status",
    6: "status recorded by a person",
    7: "links between countries and situations",
    8: "text limit",
    9: "localized text",
    10: "penalties",
    11: "labels",
}
RELAXED_IN_DRAFT = (3, 6)

ID_PATTERNS = {
    "countries": re.compile(r"[A-Z]{3}"),
    "situations": re.compile(r"[a-z0-9]+(-[a-z0-9]+)*"),
    "sources": re.compile(r"[a-z0-9]+(-[a-z0-9]+)*"),
}
# Entities whose `name` is a name per locale; in the others it is a plain string.
NAMED_PER_LOCALE = ("countries", "situations")
# What the completeness of a country counts: the questions of function 1.
COMPLETENESS_FIELDS = ("un_status", *voc.COUNTRY_BLOCKS)
ROBOTS_VALIDITY_DAYS = 180

_FULL_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_PARTIAL_DATE = re.compile(r"\d{4}(-\d{2}(-\d{2})?)?")
_DATE_TOKEN = re.compile(r"YYYY|MMM|MM|DD|D")
_FIELDS = frozenset(voc.FIELDS)
_SHARED = frozenset(voc.SHARED_FIELDS)
_NOT_ASSERTED = frozenset((*voc.STAMP_FIELDS, "note", "reason"))


@dataclass(frozen=True)
class Problem:
    check: int
    where: str
    message: str

    @property
    def relaxable(self) -> bool:
        return self.check in RELAXED_IN_DRAFT

    def __str__(self) -> str:
        return f"check {self.check} ({CHECKS[self.check]}): {self.where}: {self.message}"


@dataclass
class Dataset:
    root: Path
    countries: list = field(default_factory=list)
    situations: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    retired: list = field(default_factory=list)
    verification: list = field(default_factory=list)
    labels: dict[str, dict] = field(default_factory=dict)  # locale -> data/i18n/<locale>.json
    problems: list[Problem] = field(default_factory=list)  # found while reading the files


# ------------------------------------------------------------------ reading


def _read_list(ds: Dataset, name: str, *, required: bool = True) -> list:
    path = ds.root / name
    if not path.exists():
        if required:
            ds.problems.append(Problem(STRUCTURE, name, "file not found"))
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        ds.problems.append(Problem(STRUCTURE, name, f"invalid JSON: {error}"))
        return []
    if not isinstance(data, list):
        ds.problems.append(Problem(STRUCTURE, name, "the root must be a list"))
        return []
    return data


def load(root: str | Path) -> Dataset:
    ds = Dataset(Path(root))
    ds.countries = _read_list(ds, "countries.json")
    ds.situations = _read_list(ds, "situations.json")
    ds.sources = _read_list(ds, "sources.json")
    ds.retired = _read_list(ds, "retired-ids.json")
    ds.verification = _read_list(ds, "verification.json", required=False)
    for path in sorted((ds.root / "i18n").glob("*.json")):
        name = f"i18n/{path.name}"
        try:
            labels = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            ds.problems.append(Problem(STRUCTURE, name, f"invalid JSON: {error}"))
            continue
        if not isinstance(labels, dict):
            ds.problems.append(Problem(STRUCTURE, name, "the root must be an object"))
            continue
        ds.labels[path.stem] = labels
    return ds


# ------------------------------------------------------------------ small helpers


def field_key(path: tuple[str, ...]) -> str:
    """The label key of a field: its path, or the bare name when the field is shared."""
    full = ".".join(path)
    if full in _FIELDS:
        return full
    for i in range(1, len(path)):
        tail = ".".join(path[i:])
        if tail in _SHARED:
            return tail
    return full


def vocabulary_value(key: str, value) -> str:
    """How a value is written in the vocabulary: 1 -> "1", "model:<id>" -> "model"."""
    if key == "author" and isinstance(value, str) and value.startswith("model:") and value[6:]:
        return "model"
    return str(value)


def is_full_date(value) -> bool:
    if not isinstance(value, str) or not _FULL_DATE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_partial_date(value) -> bool:
    """YYYY, YYYY-MM or YYYY-MM-DD: a source that says "June 2005" is recorded as 2005-06."""
    if not isinstance(value, str) or not _PARTIAL_DATE.fullmatch(value):
        return False
    return is_full_date((value + "-01-01")[:10])


def format_date(value: str, formats: dict) -> str:
    """A (partial) date in the pattern of the locale: tokens YYYY, MMM, MM, DD and D."""
    parts = value.split("-")
    pattern = formats[("year", "month", "date")[len(parts) - 1]]
    year, month, day = (parts + ["01", "01"])[:3]
    tokens = {
        "YYYY": year,
        "MMM": formats["months_short"][int(month) - 1],
        "MM": month,
        "DD": day,
        "D": str(int(day)),
    }
    return _DATE_TOKEN.sub(lambda m: tokens[m.group()], pattern)


def asserts(block: dict) -> bool:
    """A block asserts something when it has a value besides the stamp and the notes."""
    return any(v is not None for k, v in block.items() if k not in _NOT_ASSERTED)


def missing_stamp(block: dict) -> list[str]:
    return [f for f in voc.STAMP_FIELDS if block.get(f) in (None, "")]


def _records(items: list) -> list[dict]:
    return [r for r in items if isinstance(r, dict) and isinstance(r.get("id"), str)]


def highest_status(statuses: list[dict]) -> dict | None:
    """The highest status reached, at the date it was first reached."""
    known = [s for s in statuses if s.get("code") in voc.STATUS_ORDER]
    if not known:
        return None
    top = max(voc.STATUS_ORDER.index(s["code"]) for s in known)
    return min(
        (s for s in known if voc.STATUS_ORDER.index(s["code"]) == top),
        key=lambda s: str(s.get("date")),
    )


# ------------------------------------------------------------------ validation


class Validator:
    def __init__(self, ds: Dataset) -> None:
        self.ds = ds
        self.problems: list[Problem] = list(ds.problems)
        self.locales = tuple(ds.labels)
        self.ids = {
            "countries": {r["id"] for r in _records(ds.countries)},
            "situations": {r["id"] for r in _records(ds.situations)},
            "sources": {r["id"] for r in _records(ds.sources)},
        }
        self.source_state = {r["id"]: r.get("state") for r in _records(ds.sources)}
        self.stamps = self._index_stamps()

    def add(self, check: int, where: str, message: str) -> None:
        problem = Problem(check, where, message)
        if problem not in self.problems:
            self.problems.append(problem)

    def run(self) -> list[Problem]:
        self.check_labels()
        self.check_retired()
        for entity in ("countries", "situations", "sources"):
            self.check_ids(entity, getattr(self.ds, entity))
            for record in _records(getattr(self.ds, entity)):
                self.walk(entity, f"{entity}[{record['id']}]", record, ())
        self.check_verification()
        for country in _records(self.ds.countries):
            self.check_country(country)
        for situation in _records(self.ds.situations):
            self.check_situation(situation)
        self.check_links()
        self.check_lexicon()
        return self.problems

    # -- check 11 (and the shape of data/i18n/)

    def check_labels(self) -> None:
        if set(self.locales) != set(voc.LOCALES):
            self.add(
                STRUCTURE,
                "i18n/",
                f"the label files are for {sorted(self.locales)}, "
                f"but the active locales are {sorted(voc.LOCALES)}",
            )
        for locale, labels in self.ds.labels.items():
            where = f"i18n/{locale}.json"
            if labels.get("locale") != locale:
                self.add(STRUCTURE, where, f'"locale" must be {locale!r}')
            for section, keys in (("fields", voc.FIELDS), ("values", voc.value_keys())):
                given = labels.get(section)
                given = given if isinstance(given, dict) else {}
                for key in keys:
                    if not isinstance(given.get(key), str) or not given[key].strip():
                        kind = "field" if section == "fields" else "value"
                        self.add(11, where, f"no label for the {kind} {key}")
            formats = labels.get("formats")
            if not isinstance(formats, dict) or not all(
                isinstance(formats.get(k), str) for k in ("date", "month", "year")
            ):
                self.add(STRUCTURE, where, '"formats" needs the patterns date, month and year')
            elif not (
                isinstance(formats.get("months_short"), list)
                and len(formats["months_short"]) == 12
                and all(isinstance(m, str) and m for m in formats["months_short"])
            ):
                self.add(STRUCTURE, where, '"formats.months_short" needs the twelve months')

    def _labelled(self, where: str, key: str, value: str) -> None:
        for locale, labels in self.ds.labels.items():
            if not (labels.get("values") or {}).get(f"{key}.{value}"):
                self.add(11, where, f"the value {key}.{value} has no label in {locale}")

    # -- check 1

    def check_retired(self) -> None:
        self.retired: set[tuple[str | None, str]] = set()
        for i, entry in enumerate(self.ds.retired):
            if isinstance(entry, str) and entry:
                self.retired.add((None, entry))
            elif isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry["id"]:
                self.retired.add((entry.get("entity"), entry["id"]))
            else:
                self.add(STRUCTURE, f"retired-ids[{i}]", 'must be an id or an object with "id"')

    def check_ids(self, entity: str, items: list) -> None:
        seen: set[str] = set()
        for i, record in enumerate(items):
            where = f"{entity}[{i}]"
            if not isinstance(record, dict):
                self.add(STRUCTURE, where, "must be an object")
                continue
            ident = record.get("id")
            if not isinstance(ident, str) or not ID_PATTERNS[entity].fullmatch(ident):
                self.add(1, where, f"id {ident!r} is outside the pattern of {entity}")
                continue
            where = f"{entity}[{ident}]"
            if ident in seen:
                self.add(1, where, "repeated id")
            seen.add(ident)
            if (entity, ident) in self.retired or (None, ident) in self.retired:
                self.add(1, where, "id is in retired-ids.json and never comes back")

    # -- checks 2, 8, 9 and 11, field by field

    def walk(self, entity: str, where: str, value, path: tuple[str, ...]) -> None:
        if isinstance(value, list):
            for item in value:
                self.walk(entity, where, item, path)
            return
        if not isinstance(value, dict):
            self._leaf(where, path, value)
            return
        for name, child in value.items():
            child_path = (*path, name)
            key = field_key(child_path)
            at = f"{where}.{'.'.join(child_path)}"
            self._field(entity, at, key)
            if child is None:
                continue
            if key in voc.LOCALIZED_TEXT_FIELDS:
                self._localized_text(at, key, child)
            elif key == "name" and entity in NAMED_PER_LOCALE:
                self._name(at, child)
            else:
                self.walk(entity, where, child, child_path)

    def _field(self, entity: str, at: str, key: str) -> None:
        if key not in _FIELDS:
            self.add(11, at, f"the field {key} has no label: the screen would show the raw key")
        elif key not in _SHARED and key not in voc.ENTITY_FIELDS[entity]:
            self.add(STRUCTURE, at, f"the field {key} does not belong to {entity}")

    def _leaf(self, where: str, path: tuple[str, ...], value) -> None:
        key = field_key(path)
        if value is None or key not in voc.VOCABULARIES:
            return
        at = f"{where}.{'.'.join(path)}"
        written = vocabulary_value(key, value)
        if isinstance(value, bool) or written not in voc.VOCABULARIES[key]:
            self.add(2, at, f"{value!r} is not one of {list(voc.VOCABULARIES[key])}")
        else:
            self._labelled(at, key, written)

    def _localized_text(self, at: str, key: str, value) -> None:
        if not isinstance(value, dict):
            self.add(STRUCTURE, at, 'must be a localized text: {"<locale>": {"text", "author"}}')
            return
        for locale, version in value.items():
            here = f"{at}.{locale}"
            if locale not in self.locales:
                self.add(9, here, f"the locale {locale} is not in data/i18n/")
            if not isinstance(version, dict) or not isinstance(version.get("text"), str):
                self.add(STRUCTURE, here, 'a version needs "text" and "author"')
                continue
            author = version.get("author")
            if author in (None, ""):
                self.add(9, here, "text of ours without author")
            elif vocabulary_value("author", author) not in voc.VOCABULARIES["author"]:
                self.add(2, f"{here}.author", f'{author!r} is not "human" nor "model:<id>"')
            if key in voc.LIMITED_TEXT_FIELDS and len(version["text"]) > voc.TEXT_LIMIT:
                self.add(
                    8,
                    here,
                    f"{len(version['text'])} characters; the limit is {voc.TEXT_LIMIT} "
                    "(a summary, not a copy)",
                )

    def _name(self, at: str, value) -> None:
        if not isinstance(value, dict):
            self.add(STRUCTURE, at, 'must be a name per locale: {"en": ..., "pt-BR": ...}')
            return
        for locale, name in value.items():
            if locale not in self.locales:
                self.add(9, f"{at}.{locale}", f"the locale {locale} is not in data/i18n/")
            if not isinstance(name, str) or not name.strip():
                self.add(STRUCTURE, f"{at}.{locale}", "must be a non-empty string")
        if "en" not in value:
            self.add(STRUCTURE, at, "the name in English is required")

    # -- checks 3 and 4: the stamp

    def _index_stamps(self) -> dict[tuple[str, str, str], dict]:
        """(entity, id, field) -> the line of verification.json that stamps it."""
        index: dict[tuple[str, str, str], dict] = {}
        for line in self.ds.verification:
            if not isinstance(line, dict) or missing_stamp(line):
                continue
            if line.get("result") not in voc.STAMPING_RESULTS:
                continue
            records, fields = line.get("records"), line.get("fields")
            if not isinstance(records, list) or not isinstance(fields, list):
                continue
            for ident in records:
                for name in fields:
                    key = (line.get("entity"), ident, name)
                    if key not in index or str(line["read_on"]) > str(index[key]["read_on"]):
                        index[key] = line
        return index

    def _source(self, where: str, source) -> None:
        if source is None:
            return
        if source not in self.source_state:
            self.add(4, where, f"the source {source!r} is not in sources.json")
        elif self.source_state[source] != "active":
            self.add(4, where, f"the source {source!r} is {self.source_state[source]}, not active")

    def _read_on(self, where: str, value) -> None:
        if value is not None and not is_full_date(value):
            self.add(STRUCTURE, f"{where}.read_on", f"{value!r} is not a date YYYY-MM-DD")

    def check_verification(self) -> None:
        for i, line in enumerate(self.ds.verification):
            where = f"verification[{i}]"
            if not isinstance(line, dict):
                self.add(STRUCTURE, where, "must be an object")
                continue
            self.walk("verification", where, line, ())
            entity = line.get("entity")
            records, fields = line.get("records"), line.get("fields")
            if not isinstance(records, list) or not records:
                self.add(STRUCTURE, where, '"records" must be a list of ids')
            elif entity in self.ids:
                for ident in records:
                    if ident not in self.ids[entity]:
                        self.add(STRUCTURE, where, f"{ident!r} is not a record of {entity}")
            if not isinstance(fields, list) or not fields:
                self.add(STRUCTURE, where, '"fields" must be a list of field keys')
            else:
                for name in fields:
                    if name not in _FIELDS:
                        self.add(STRUCTURE, where, f"{name!r} is not a field of the model")
            if line.get("result") is None:
                self.add(STRUCTURE, where, '"result" is required')
            if missing := missing_stamp(line):
                self.add(3, where, f"line without stamp: missing {', '.join(missing)}")
            self._source(where, line.get("source"))
            self._read_on(where, line.get("read_on"))

    # -- checks 3, 4, 7 and 10: one country

    def check_country(self, country: dict) -> None:
        ident = country["id"]
        where = f"countries[{ident}]"
        for name in voc.COUNTRY_STAMPED_SCALARS:
            if country.get(name) is not None and ("countries", ident, name) not in self.stamps:
                self.add(
                    3,
                    f"{where}.{name}",
                    "asserted without stamp: no line of verification.json covers it",
                )
        for name in voc.COUNTRY_BLOCKS:
            block = country.get(name)
            if block is None:
                continue
            at = f"{where}.{name}"
            if not isinstance(block, dict):
                self.add(STRUCTURE, at, "must be an object")
                continue
            if asserts(block) and (missing := missing_stamp(block)):
                self.add(3, at, f"asserted without stamp: missing {', '.join(missing)}")
            self._source(at, block.get("source"))
            self._read_on(at, block.get("read_on"))
        self._penalties(where, country)
        situations = country.get("situations", [])
        if not isinstance(situations, list):
            self.add(STRUCTURE, f"{where}.situations", "must be a list of situation ids")
            return
        for situation in situations:
            if situation not in self.ids["situations"]:
                self.add(7, f"{where}.situations", f"the situation {situation!r} does not exist")

    def _penalties(self, where: str, country: dict) -> None:
        penalty, death = country.get("max_penalty"), country.get("death_penalty")
        penalty = penalty if isinstance(penalty, dict) else {}
        death = death if isinstance(death, dict) else {}
        years = penalty.get("years")
        if penalty.get("type") == "years" and (
            isinstance(years, bool) or not isinstance(years, int)
        ):
            self.add(10, f"{where}.max_penalty", 'type "years" without the number of years')
        if (
            death.get("status") == "retentionist"
            and penalty.get("type") in ("years", "life")
            and not (death.get("note") or penalty.get("note"))
        ):
            self.add(
                10,
                f"{where}.death_penalty",
                "retentionist, but the maximum penalty is not death: a note must say why",
            )

    # -- checks 3, 5, 6 and 7: one situation

    def check_situation(self, situation: dict) -> None:
        where = f"situations[{situation['id']}]"
        for name in ("name", "countries", "period", "statuses", "terms", "promotion"):
            if name not in situation:
                self.add(STRUCTURE, where, f'"{name}" is required')

        countries = situation.get("countries", [])
        if not isinstance(countries, list):
            self.add(STRUCTURE, f"{where}.countries", "must be a list of {id, role}")
            countries = []
        for entry in countries:
            if not isinstance(entry, dict):
                self.add(STRUCTURE, f"{where}.countries", "must be a list of {id, role}")
                continue
            if entry.get("id") not in self.ids["countries"]:
                self.add(7, f"{where}.countries", f"the country {entry.get('id')!r} does not exist")
            if not entry.get("role"):
                self.add(7, f"{where}.countries", f"the country {entry.get('id')!r} has no role")

        self._period(f"{where}.period", situation.get("period"))

        statuses = situation.get("statuses", [])
        if not isinstance(statuses, list):
            self.add(STRUCTURE, f"{where}.statuses", "must be a list")
            statuses = []
        for i, status in enumerate(statuses):
            self._status(f"{where}.statuses[{i}]", status)

        self._terms(f"{where}.terms", situation.get("terms", []))

        promotion = situation.get("promotion")
        if promotion is not None and (
            not isinstance(promotion, dict) or promotion.get("level") is None
        ):
            self.add(STRUCTURE, f"{where}.promotion", 'must be an object with "level"')

    def _period(self, at: str, period) -> None:
        if period is None:
            return
        if not isinstance(period, dict):
            self.add(STRUCTURE, at, "must be an object {start, end, approximate}")
            return
        start, end = period.get("start"), period.get("end")
        if not is_partial_date(start):
            self.add(STRUCTURE, at, f"start {start!r} is not a date (YYYY, YYYY-MM or YYYY-MM-DD)")
        if end is not None and not is_partial_date(end):
            self.add(STRUCTURE, at, f"end {end!r} is not a date (YYYY, YYYY-MM or YYYY-MM-DD)")
        elif end is not None and is_partial_date(start) and end < start[: len(end)]:
            self.add(STRUCTURE, at, "the end comes before the start")
        if not isinstance(period.get("approximate"), bool):
            self.add(STRUCTURE, at, '"approximate" must be true or false')

    def _status(self, at: str, status) -> None:
        if not isinstance(status, dict) or not status.get("code"):
            self.add(STRUCTURE, at, 'must be an object with "code"')
            return
        for name in ("by", "date", "url", "confidence"):
            if status.get(name) in (None, ""):
                self.add(5, at, f"status without {name}: a status says who, when and where it is")
        if status.get("date") not in (None, "") and not is_partial_date(status["date"]):
            self.add(5, at, f"date {status['date']!r} is not a date")
        url = status.get("url")
        if url not in (None, "") and not str(url).startswith(("http://", "https://")):
            self.add(5, at, f"url {url!r} is not an address")
        if status["code"] == "merits_decision" and not status.get("outcome"):
            self.add(5, at, "merits_decision without outcome")
        if status.get("checked_by") is None:
            self.add(3, at, "asserted without stamp: missing checked_by")
        if status["code"] in voc.HUMAN_ONLY_STATUSES and status.get("checked_by") != "human":
            self.add(
                6,
                at,
                f"{status['code']} with checked_by {status.get('checked_by')!r}: "
                "only a person records it",
            )

    def _terms(self, at: str, terms) -> None:
        if not isinstance(terms, list):
            self.add(STRUCTURE, at, "must be a list of {lang, forms, exclusions}")
            return
        seen: set[str] = set()
        for entry in terms:
            if not isinstance(entry, dict):
                self.add(STRUCTURE, at, "must be a list of {lang, forms, exclusions}")
                continue
            lang = entry.get("lang")
            if lang not in voc.LEXICON_LANGUAGES:
                self.add(2, f"{at}.lang", f"{lang!r} is not one of {list(voc.LEXICON_LANGUAGES)}")
            if lang in seen:
                self.add(STRUCTURE, at, f"the language {lang!r} appears twice")
            seen.add(lang)
            forms, exclusions = entry.get("forms"), entry.get("exclusions", [])
            if not (
                isinstance(forms, list)
                and forms
                and all(isinstance(f, str) and f.strip() for f in forms)
            ):
                self.add(STRUCTURE, f"{at}[{lang}].forms", "needs at least one non-empty form")
            if not (
                isinstance(exclusions, list)
                and all(isinstance(e, str) and e.strip() for e in exclusions)
            ):
                self.add(STRUCTURE, f"{at}[{lang}].exclusions", "must be a list of strings")

    # -- check 7, both ways

    def check_links(self) -> None:
        listed: dict[str, set[str]] = {}
        for situation in _records(self.ds.situations):
            countries = situation.get("countries")
            for entry in countries if isinstance(countries, list) else []:
                if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                    listed.setdefault(entry["id"], set()).add(situation["id"])
        for country in _records(self.ds.countries):
            given = country.get("situations", [])
            given = {s for s in given if isinstance(s, str)} if isinstance(given, list) else set()
            where = f"countries[{country['id']}].situations"
            for situation in sorted(listed.get(country["id"], set()) - given):
                self.add(7, where, f"{situation!r} lists this country, but is missing here")
            for situation in sorted(
                (given & self.ids["situations"]) - listed.get(country["id"], set())
            ):
                self.add(7, where, f"{situation!r} is here, but does not list this country")

    # -- the lexicon: valid sources, generated files up to date

    def check_lexicon(self) -> None:
        if not (self.ds.root / "lexicon").exists():
            return
        try:
            lexicons = build_lexicon.build(self.ds.root)
        except build_lexicon.BuildError as error:
            for problem in error.problems:
                self.add(2 if "category" in problem else STRUCTURE, "lexicon", problem)
            return
        for lang, lexicon in lexicons.items():
            path = build_lexicon.generated_path(self.ds.root, lang)
            state = build_lexicon.state(path, build_lexicon.dumps(lexicon))
            if state != "unchanged":
                what = "is missing" if state == "new" else "is out of date"
                self.add(
                    STRUCTURE,
                    f"lexicon/{lang}.json",
                    f"{what}: run python scripts/build_lexicon.py --execute",
                )


def validate(ds: Dataset) -> list[Problem]:
    return Validator(ds).run()


# ------------------------------------------------------------------ derived files


def _block_state(block) -> str:
    if not isinstance(block, dict) or not asserts(block):
        return "empty"
    return "draft" if missing_stamp(block) else "stamped"


def derive_country(country: dict, stamps: dict) -> dict:
    ident = country["id"]
    provenance = {}
    for name in voc.COUNTRY_STAMPED_SCALARS:
        if line := stamps.get(("countries", ident, name)):
            provenance[name] = {f: line[f] for f in voc.STAMP_FIELDS}
    states = {}
    for name in COMPLETENESS_FIELDS:
        if name in voc.COUNTRY_BLOCKS:
            states[name] = _block_state(country.get(name))
        elif country.get(name) is None:
            states[name] = "empty"
        else:
            states[name] = "stamped" if name in provenance else "draft"
    read = [p["read_on"] for p in provenance.values()]
    read += [
        country[b]["read_on"]
        for b in voc.COUNTRY_BLOCKS
        if isinstance(country.get(b), dict) and country[b].get("read_on")
    ]
    return {
        **country,
        "provenance": provenance,
        "completeness": {
            **{
                s: sum(1 for v in states.values() if v == s)
                for s in voc.VOCABULARIES["completeness"]
            },
            "fields": states,
        },
        "updated_at": max(read, default=None),
    }


def status_label(status: dict, labels: dict) -> str:
    """ "provisional measures — International Court of Justice, 26 Jan 2024": never without
    the body that produced the status (docs/03, taxonomy, rule 2)."""
    values = labels["values"]
    text = values[f"statuses.code.{status['code']}"]
    if outcome := status.get("outcome"):
        text += f" ({values['statuses.outcome.' + outcome]})"
    return f"{text} — {status['by']}, {format_date(status['date'], labels['formats'])}"


def derive_situation(situation: dict, stamps: dict, labels: dict[str, dict]) -> dict:
    top = highest_status(situation["statuses"])
    if top is not None:
        top = {**top, "label": {loc: status_label(top, labels[loc]) for loc in labels}}
    read = [
        line["read_on"]
        for (entity, ident, _), line in stamps.items()
        if entity == "situations" and ident == situation["id"]
    ]
    return {**situation, "highest_status": top, "updated_at": max(read, default=None)}


def _as_of(ds: Dataset) -> str | None:
    """The most recent reading recorded in the data: the report's "today", so that the
    same data always gives the same report."""
    dates = [s.get("robots_checked_on") for s in _records(ds.sources)]
    dates += [line.get("read_on") for line in ds.verification if isinstance(line, dict)]
    for country in _records(ds.countries):
        dates += [
            country[b].get("read_on")
            for b in voc.COUNTRY_BLOCKS
            if isinstance(country.get(b), dict)
        ]
    return max((d for d in dates if is_full_date(d)), default=None)


def _record_of(where: str) -> str:
    return where[: where.index("]") + 1] if "]" in where else where


def quality(ds: Dataset, problems: list[Problem], countries: list, situations: list) -> dict:
    as_of = _as_of(ds)
    drafts = [p for p in problems if p.relaxable]
    locales = list(ds.labels)

    rank = voc.STATUS_ORDER.index
    watched: set[str] = set()  # territory or respondent where a body already investigates
    for s in situations:
        top = s["highest_status"]
        if top and rank(top["code"]) >= rank("investigation"):
            watched |= {c["id"] for c in s["countries"] if c["role"] in ("territory", "respondent")}

    statuses = [st for s in situations for st in s["statuses"]]
    by_highest: dict[str, int] = {}
    for s in situations:
        code = s["highest_status"]["code"] if s["highest_status"] else "none"
        by_highest[code] = by_highest.get(code, 0) + 1

    sources = _records(ds.sources)
    by_state: dict[str, int] = {}
    for s in sources:
        by_state[str(s.get("state"))] = by_state.get(str(s.get("state")), 0) + 1
    expired = []
    if as_of:
        for s in sources:
            checked = s.get("robots_checked_on")
            if is_full_date(checked):
                age = date.fromisoformat(as_of) - date.fromisoformat(checked)
                if age.days > ROBOTS_VALIDITY_DAYS:
                    expired.append(s["id"])

    lexicon = {}
    for lang in voc.LEXICON_LANGUAGES:
        path = build_lexicon.generated_path(ds.root, lang)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            lexicon[lang] = {
                "version": data["version"],
                "terms": len(data["terms"]),
                "forms": sum(len(t["forms"]) for t in data["terms"]),
            }

    def without_name(records: list) -> dict:
        return {loc: [r["id"] for r in records if not r["name"].get(loc)] for loc in locales}

    return {
        "as_of": as_of,
        "drafts": {
            "fields": len({p.where for p in drafts}),
            "records": len({_record_of(p.where) for p in drafts}),
            "by_check": {
                str(c): sum(1 for p in drafts if p.check == c)
                for c in RELAXED_IN_DRAFT
                if any(p.check == c for p in drafts)
            },
            "items": [{"check": p.check, "where": p.where, "message": p.message} for p in drafts],
        },
        "countries": {
            "total": len(countries),
            "complete": sum(
                1 for c in countries if c["completeness"]["stamped"] == len(COMPLETENESS_FIELDS)
            ),
            "fields": {
                name: {
                    state: sum(1 for c in countries if c["completeness"]["fields"][name] == state)
                    for state in voc.VOCABULARIES["completeness"]
                }
                for name in COMPLETENESS_FIELDS
            },
            "names_missing": without_name(countries),
            "priority": sorted(
                c["id"]
                for c in countries
                if c["id"] in watched
                and c["completeness"]["fields"]["domestic_genocide"] != "stamped"
            ),
        },
        "situations": {
            "total": len(situations),
            "by_highest_status": by_highest,
            "without_status": [s["id"] for s in situations if not s["statuses"]],
            "statuses": {
                "total": len(statuses),
                "stamped": sum(1 for st in statuses if st.get("checked_by")),
                "draft": sum(1 for st in statuses if not st.get("checked_by")),
            },
            "names_missing": without_name(situations),
            "terms_missing": {
                lang: [s["id"] for s in situations if lang not in {t["lang"] for t in s["terms"]}]
                for lang in voc.LEXICON_LANGUAGES
            },
            "texts_missing": {
                "description": {
                    loc: sum(1 for s in situations if loc not in (s.get("description") or {}))
                    for loc in locales
                }
            },
        },
        "sources": {
            "total": len(sources),
            "by_state": by_state,
            "robots_unchecked": [s["id"] for s in sources if not s.get("robots_checked_on")],
            "robots_expired": expired,
        },
        "lexicon": lexicon,
    }


def derive(ds: Dataset, problems: list[Problem]) -> dict[str, object]:
    """{path inside static/data/: content}. Only for data that passed the checks that
    --draft does not relax."""
    stamps = Validator(ds).stamps
    countries = [derive_country(c, stamps) for c in ds.countries]
    situations = [derive_situation(s, stamps, ds.labels) for s in ds.situations]
    files: dict[str, object] = {"countries.json": countries, "situations.json": situations}
    for locale, labels in ds.labels.items():
        files[f"i18n/{locale}.json"] = labels
    files["quality.json"] = quality(ds, problems, countries, situations)
    return files


# ------------------------------------------------------------------ command line


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def show(path: Path) -> str:
    try:
        return Path(os.path.relpath(path)).as_posix()
    except ValueError:  # another drive, on Windows
        return path.as_posix()


def _state(path: Path, text: str) -> str:
    if not path.exists():
        return "new"
    return "unchanged" if path.read_text(encoding="utf-8") == text else "changed"


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # a console in cp1252 must not break the report
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true", help="every check (the default)")
    mode.add_argument("--draft", action="store_true", help="initial load: relaxes checks 3 and 6")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--execute", action="store_true", help="write (default: simulation)")
    action.add_argument("--check", action="store_true", help="fail if the output is out of date")
    parser.add_argument("--data", help="source directory (default: data/)")
    parser.add_argument("--output", help="derived directory (default: static/data/)")
    args = parser.parse_args(argv)

    data = Path(args.data) if args.data else ROOT / "data"
    output = Path(args.output) if args.output else data.parent / "static" / "data"
    if not data.is_dir():
        print(f"{show(data)}: directory not found", file=sys.stderr)
        return 2

    ds = load(data)
    problems = validate(ds)
    drafts = [p for p in problems if p.relaxable]
    hard = [p for p in problems if not p.relaxable]
    mode_name = "draft" if args.draft else "strict"

    for problem in hard:
        print(f"FAIL {problem}")
    for problem in drafts:
        print(f"{'draft' if args.draft else 'FAIL'} {problem}")
    if drafts:
        fields = len({p.where for p in drafts})
        records = len({_record_of(p.where) for p in drafts})
        print(f"{fields} fields in draft, in {records} records (checks 3 and 6)")
    if hard or (drafts and not args.draft):
        if not hard:
            print(
                "strict: only drafts stand in the way. That is expected during the initial "
                "load; --draft accepts and counts them in quality.json."
            )
        print(f"{mode_name}: FAILED, {len(hard) + (0 if args.draft else len(drafts))} findings")
        return 1
    print(
        f"{mode_name}: passed. {len(ds.countries)} countries, {len(ds.situations)} situations, "
        f"{len(ds.sources)} sources, {len({p.where for p in drafts})} fields in draft"
    )

    files = {output / name: dumps(content) for name, content in derive(ds, problems).items()}
    states = {path: _state(path, text) for path, text in files.items()}
    if output.is_dir():
        for path in sorted(p for p in output.rglob("*") if p.is_file() and p not in files):
            print(f"left alone (not generated by this script, never deleted): {show(path)}")

    if args.check:
        stale = [path for path, state in states.items() if state != "unchanged"]
        for path in stale:
            print(f"out of date ({states[path]}): {show(path)}")
        if stale:
            print("run python scripts/transform.py --draft --execute (or --strict --execute)")
            return 1
        print(f"{show(output)} is up to date")
        return 0

    for path, text in files.items():
        if states[path] == "unchanged":
            print(f"up to date: {show(path)}")
        elif args.execute:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote ({states[path]}): {show(path)}")
        else:
            print(f"would write ({states[path]}): {show(path)}")
    if not args.execute:
        print("simulation: nothing was written; add --execute to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
