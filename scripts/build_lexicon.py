"""Builds data/lexicon/<lang>.json, one lexicon per language (docs/03-modelo-de-dados.md).

A lexicon is made of two lists, both data and both edited by hand:

- the fixed terms of the language, in data/lexicon/fixed/<lang>.json, which is itself a
  lexicon in the format of schemas/lexicon.schema.json (terms and legal context);
- the terms of each situation, in data/situations.json (`terms`, per language). They
  enter with the id of the situation as key and the category "situation".

The result is generated: never edit data/lexicon/<lang>.json. Its version is
"<lang>-<date of the fixed terms>-<digest of the content>", so any change of term gives
a new version without anyone having to remember to bump it.

    python scripts/build_lexicon.py             simulation: says what it would write
    python scripts/build_lexicon.py --execute   writes; never deletes anything

Exit codes: 0 fine; 1 a source is invalid; 2 usage or file error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vocabularies  # noqa: E402

from astraea.engine import lexicon as engine_lexicon  # noqa: E402
from astraea.engine.text import fold  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITUATION_CATEGORY = "situation"
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class BuildError(ValueError):
    def __init__(self, problems: list[str]) -> None:
        super().__init__("cannot build the lexicon:\n  - " + "\n  - ".join(problems))
        self.problems = problems


def fixed_path(data: Path, lang: str) -> Path:
    return data / "lexicon" / "fixed" / f"{lang}.json"


def generated_path(data: Path, lang: str) -> Path:
    return data / "lexicon" / f"{lang}.json"


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def _read(path: Path, problems: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        problems.append(f"{path.as_posix()}: file not found")
    except json.JSONDecodeError as error:
        problems.append(f"{path.as_posix()}: invalid JSON: {error}")
    return None


def _repeated_forms(term: dict) -> list[str]:
    """Forms that are the same once case and accents are ignored."""
    seen: dict[str, str] = {}
    repeated = []
    for form in term.get("forms") or []:
        if not isinstance(form, str):
            continue
        key = " ".join(fold(form).split())
        if key in seen:
            repeated.append(f"{form!r} repeats {seen[key]!r}")
        seen.setdefault(key, form)
    return repeated


def check_fixed(lang: str, fixed, where: str) -> list[str]:
    """Problems of one file of fixed terms; empty when it can be used."""
    problems = [f"{where}: {p}" for p in engine_lexicon.validate(fixed)]
    if problems:
        return problems
    if fixed["id"] != f"astraea-fixed-{lang}":
        problems.append(f"{where}: id must be astraea-fixed-{lang}")
    if not _DATE.match(fixed["version"]):
        problems.append(f"{where}: version must be the date of the last edit, YYYY-MM-DD")
    if "context" not in fixed:
        problems.append(f"{where}: context.requires_any is required (the legal markers)")
    allowed = set(vocabularies.VOCABULARIES["categories"]) - {SITUATION_CATEGORY}
    for term in fixed["terms"]:
        at = f"{where}: terms[{term['key']}]"
        categories = term.get("categories") or []
        if not categories:
            problems.append(f"{at}: needs at least one category")
        for category in categories:
            if category not in allowed:
                problems.append(f"{at}: category {category!r} is not one of {sorted(allowed)}")
        problems += [f"{at}: form {r}" for r in _repeated_forms(term)]
    return problems


def situation_terms(situations: list, lang: str, problems: list[str]) -> list[dict]:
    terms = []
    for situation in situations:
        if not isinstance(situation, dict):
            continue
        for entry in situation.get("terms") or []:
            if not isinstance(entry, dict) or entry.get("lang") != lang:
                continue
            term = {"key": situation.get("id"), "forms": entry.get("forms") or []}
            if entry.get("exclusions"):
                term["exclusions"] = entry["exclusions"]
            term["categories"] = [SITUATION_CATEGORY]
            term["weight"] = 1.0
            at = f"situations[{situation.get('id')}].terms[{lang}]"
            problems += [f"{at}: form {r}" for r in _repeated_forms(term)]
            terms.append(term)
    return terms


def build_one(lang: str, fixed: dict, situations: list, problems: list[str]) -> dict:
    terms = [*fixed["terms"], *situation_terms(situations, lang, problems)]
    content = {"terms": terms, "context": fixed["context"]}
    digest = hashlib.sha256(
        json.dumps(content, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:8]
    description = (
        f"Generated by scripts/build_lexicon.py from data/lexicon/fixed/{lang}.json and "
        "data/situations.json. Do not edit: change the sources and run the script again."
    )
    if fixed.get("description"):
        description += f" Fixed terms: {fixed['description']}"
    lexicon = {
        "id": f"astraea-{lang}",
        "version": f"{lang}-{fixed['version']}-{digest}",
        "description": description,
        **content,
    }
    problems += [f"lexicon/{lang}.json: {p}" for p in engine_lexicon.validate(lexicon)]
    return lexicon


def build(data: Path) -> dict[str, dict]:
    """{lang: lexicon} for every language of LEXICON_LANGUAGES, or BuildError."""
    problems: list[str] = []
    situations = _read(data / "situations.json", problems)
    if situations is not None and not isinstance(situations, list):
        problems.append("situations.json: the root must be a list")
        situations = None
    result: dict[str, dict] = {}
    for lang in vocabularies.LEXICON_LANGUAGES:
        path = fixed_path(data, lang)
        fixed = _read(path, problems)
        if fixed is None:
            continue
        found = check_fixed(lang, fixed, f"lexicon/fixed/{lang}.json")
        problems += found
        if found or situations is None:
            continue
        result[lang] = build_one(lang, fixed, situations, problems)
    if problems:
        raise BuildError(problems)
    return result


def show(path: Path) -> str:
    try:
        return Path(os.path.relpath(path)).as_posix()
    except ValueError:  # another drive, on Windows
        return path.as_posix()


def state(path: Path, text: str) -> str:
    if not path.exists():
        return "new"
    return "unchanged" if path.read_text(encoding="utf-8") == text else "changed"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data", default=str(ROOT / "data"), help="data directory")
    parser.add_argument(
        "--execute", action="store_true", help="write the files (default: simulation)"
    )
    args = parser.parse_args(argv)
    data = Path(args.data)
    try:
        lexicons = build(data)
    except BuildError as error:
        print(error, file=sys.stderr)
        return 1
    for lang, lexicon in lexicons.items():
        path = generated_path(data, lang)
        text = dumps(lexicon)
        forms = sum(len(t["forms"]) for t in lexicon["terms"])
        what = state(path, text)
        if args.execute and what != "unchanged":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        verb = "wrote" if args.execute and what != "unchanged" else "would write"
        if what == "unchanged":
            verb = "up to date"
        print(
            f"{verb}: {show(path)} ({what}; {lexicon['version']}, "
            f"{len(lexicon['terms'])} terms, {forms} forms)"
        )
    if not args.execute:
        print("simulation: nothing was written; run again with --execute to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
