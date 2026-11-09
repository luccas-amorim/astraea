"""The lexicon as data: load, validate and match against text.

No term lives in code. The format is in `schemas/lexicon.schema.json`; the validation
below applies the same rules without depending on a JSON Schema library, and the test
`test_schema_and_validator_agree` keeps the two from diverging silently.

Matching is by whole word, ignoring case and accents, and tolerates a line break or a
double space where the form has one space ("art.  121" matches "art. 121"). An occurrence
that falls inside an exclusion of the same term does not count.

An ellipsis (`…`, a single character) in a form stands for up to 60 arbitrary characters,
without crossing a semicolon or a line break (a period does cross, because of "para.").
So "art. 121 … Código Penal" matches "art. 121, § 2º, IV, do Código Penal", which is how
case law cites. Exclusions accept the same: "art. 121 … Código Penal Militar" cancels the
occurrence that is really from the Military Penal Code.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from astraea.engine.text import fold


class LexiconError(ValueError):
    def __init__(self, problems: list[str]) -> None:
        super().__init__("invalid lexicon:\n  - " + "\n  - ".join(problems))
        self.problems = problems


@dataclass(frozen=True)
class Term:
    key: str
    forms: tuple[str, ...]
    exclusions: tuple[str, ...] = ()
    weight: float = 1.0
    categories: tuple[str, ...] = ()
    note: str | None = None


@dataclass(frozen=True)
class Lexicon:
    id: str
    version: str
    terms: tuple[Term, ...]
    context: tuple[str, ...] = ()  # one of these in the text is enough
    description: str | None = None


@dataclass(frozen=True)
class Occurrence:
    key: str
    start: int
    end: int


_ROOT_KEYS = {"id", "version", "description", "terms", "context"}
_TERM_KEYS = {"key", "forms", "exclusions", "weight", "categories", "note"}
_CONTEXT_KEYS = {"requires_any", "note"}


def _text_list(value, where: str, problems: list[str], minimum: int = 0) -> None:
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        problems.append(f"{where}: must be a list of non-empty strings")
    elif len(value) < minimum:
        problems.append(f"{where}: needs at least {minimum} item")


def validate(data) -> list[str]:
    """List of problems; empty when the lexicon is valid."""
    if not isinstance(data, dict):
        return ["the root must be an object"]
    problems: list[str] = []
    for key in sorted(set(data) - _ROOT_KEYS):
        problems.append(f"unknown field at the root: {key}")
    for key in ("id", "version"):
        if not isinstance(data.get(key), str) or not data.get(key, "").strip():
            problems.append(f"{key}: required, non-empty string")
    if "description" in data and not isinstance(data["description"], str):
        problems.append("description: must be a string")

    terms = data.get("terms")
    if not isinstance(terms, list) or not terms:
        problems.append("terms: required, a list with at least one term")
        terms = []
    seen: set[str] = set()
    for i, term in enumerate(terms):
        where = f"terms[{i}]"
        if not isinstance(term, dict):
            problems.append(f"{where}: must be an object")
            continue
        for key in sorted(set(term) - _TERM_KEYS):
            problems.append(f"{where}: unknown field: {key}")
        key = term.get("key")
        if not isinstance(key, str) or not key.strip():
            problems.append(f"{where}.key: required, non-empty string")
        elif key in seen:
            problems.append(f"{where}.key: repeated ({key})")
        else:
            seen.add(key)
            where = f"terms[{key}]"
        _text_list(term.get("forms"), f"{where}.forms", problems, minimum=1)
        for optional in ("exclusions", "categories"):
            if optional in term:
                _text_list(term[optional], f"{where}.{optional}", problems)
        weight = term.get("weight", 1.0)
        if isinstance(weight, bool) or not isinstance(weight, int | float) or weight <= 0:
            problems.append(f"{where}.weight: must be a positive number")
        if "note" in term and not isinstance(term["note"], str):
            problems.append(f"{where}.note: must be a string")

    context = data.get("context")
    if context is not None:
        if not isinstance(context, dict):
            problems.append("context: must be an object")
        else:
            for key in sorted(set(context) - _CONTEXT_KEYS):
                problems.append(f"context: unknown field: {key}")
            _text_list(context.get("requires_any"), "context.requires_any", problems, 1)
    return problems


def from_data(data: dict) -> Lexicon:
    problems = validate(data)
    if problems:
        raise LexiconError(problems)
    terms = tuple(
        Term(
            key=t["key"],
            forms=tuple(t["forms"]),
            exclusions=tuple(t.get("exclusions", ())),
            weight=float(t.get("weight", 1.0)),
            categories=tuple(t.get("categories", ())),
            note=t.get("note"),
        )
        for t in data["terms"]
    )
    context = tuple((data.get("context") or {}).get("requires_any", ()))
    return Lexicon(data["id"], data["version"], terms, context, data.get("description"))


def load(path: str | Path) -> Lexicon:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise LexiconError([f"invalid JSON: {error}"]) from error
    return from_data(data)


# "…" in a form: up to this much of anything between the parts. It is what lets
# "art. 121 … Código Penal" match "art. 121, § 2º, IV, do Código Penal".
ELLIPSIS = "…"
ELLIPSIS_WINDOW = 60


def _chunk(part: str) -> str:
    return r"\s+".join(map(re.escape, part.split()))


def _form(form: str) -> str:
    parts = [p.strip() for p in fold(form.strip()).split(ELLIPSIS)]
    # Each part closes and opens on a word boundary: "art. 121 … CP" does not match "art. 1210".
    gap = rf"(?!\w)[^;\n]{{0,{ELLIPSIS_WINDOW}}}?(?<!\w)"
    return gap.join(_chunk(p) for p in parts if p)


def _pattern(forms: tuple[str, ...]) -> re.Pattern[str] | None:
    if not forms:
        return None
    # Longest first: "art. 121 do Código Penal" beats "art. 121" at the same position.
    parts = sorted({f.strip() for f in forms}, key=len, reverse=True)
    alternatives = "|".join(_form(p) for p in parts)
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)")


class Matcher:
    """The compiled lexicon. Works on already folded text (see `text.fold`)."""

    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        self._terms = [(t, _pattern(t.forms), _pattern(t.exclusions)) for t in lexicon.terms]
        self._context = _pattern(lexicon.context)

    def occurrences(self, folded: str) -> tuple[list[Occurrence], list[Occurrence]]:
        """(valid occurrences, occurrences cancelled by an exclusion)."""
        valid: list[Occurrence] = []
        cancelled: list[Occurrence] = []
        for term, pattern, exclusion in self._terms:
            spans = [m.span() for m in exclusion.finditer(folded)] if exclusion else []
            for m in pattern.finditer(folded):
                oc = Occurrence(term.key, m.start(), m.end())
                inside = any(a <= oc.start and oc.end <= b for a, b in spans)
                (cancelled if inside else valid).append(oc)
        valid.sort(key=lambda o: o.start)
        return valid, cancelled

    def context(self, folded: str) -> re.Match[str] | None | bool:
        """The first context marker, or True when the lexicon requires no context."""
        if self._context is None:
            return True
        return self._context.search(folded)

    def term(self, key: str) -> Term:
        return next(t for t in self.lexicon.terms if t.key == key)
