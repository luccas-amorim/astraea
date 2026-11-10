"""Builds the static site from static/data/ and the templates in site/.

    python scripts/build_site.py                 says what it would write (simulation)
    python scripts/build_site.py --execute       writes _site/
    python scripts/build_site.py --execute --out <dir> --base-url https://.../astraea/

Phase 1 has one screen, the home page, in every active locale (`/en/`, `/pt-br/`), plus
a short page at the root that takes the reader to the browser's language. The page is
rendered here, at build time, from `static/data/quality.json` and
`static/data/situations.json`: it shows the counters and the situations without
JavaScript, and the deploy rebuilds it whenever the data change.

The output also carries a copy of `static/data/` (the open data the page links to), the
stylesheet and `CITATION.cff`. Interface texts live in `site/i18n/<locale>.json`; dates
follow the `formats` of `static/data/i18n/<locale>.json`, through the same function the
derived labels use.

Simulation by default; `--execute` writes; nothing is ever deleted: a file found in the
output that this script does not generate is only reported. Only the standard library.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from transform import format_date, show  # noqa: E402

DEFAULT_OUT = "_site"
DATA_FILES = ("countries.json", "situations.json", "quality.json")


def route(locale: str) -> str:
    """The path prefix of a locale: `pt-BR` -> `pt-br` (docs/04, "As telas")."""
    return locale.lower()


# ------------------------------------------------------------------ inputs


@dataclass
class Inputs:
    quality: dict
    situations: list[dict]
    formats: dict[str, dict]  # locale -> formats of static/data/i18n/<locale>.json
    texts: dict[str, dict]  # locale -> site/i18n/<locale>.json
    citation: dict
    templates: dict[str, Template]
    data_dir: Path
    site_dir: Path
    citation_file: Path


def _json(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"{show(path)}: not found")
    return json.loads(path.read_text(encoding="utf-8"))


def read_citation(path: Path) -> dict:
    """The few keys of CITATION.cff the page cites. Not a YAML parser: the file is ours.

    Reads top-level `key: value` lines and the `family-names`/`given-names` of each
    author; skips comments and folded blocks.
    """
    result: dict = {"authors": []}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        if m := re.fullmatch(r"\s*-?\s*(family-names|given-names):\s*(.+)", line):
            if line.lstrip().startswith("-") or not result["authors"]:
                result["authors"].append({})
            result["authors"][-1][m.group(1)] = m.group(2).strip().strip('"')
        elif m := re.fullmatch(r"([A-Za-z][\w-]*):\s*(.*)", line):
            value = m.group(2).strip()
            if value and not value.startswith((">", "|")):
                result[m.group(1)] = value.strip('"')
    return result


def load(data_dir: Path, site_dir: Path, citation_file: Path) -> Inputs:
    texts = {path.stem: _json(path) for path in sorted((site_dir / "i18n").glob("*.json"))}
    if not texts:
        raise FileNotFoundError(f"{show(site_dir / 'i18n')}: no interface texts")
    formats = {}
    for locale in texts:
        labels = _json(data_dir / "i18n" / f"{locale}.json")
        formats[locale] = labels["formats"]
    templates = {
        name: Template((site_dir / "templates" / f"{name}.html").read_text(encoding="utf-8"))
        for name in ("home", "root")
    }
    return Inputs(
        quality=_json(data_dir / "quality.json"),
        situations=_json(data_dir / "situations.json"),
        formats=formats,
        texts=texts,
        citation=read_citation(citation_file),
        templates=templates,
        data_dir=data_dir,
        site_dir=site_dir,
        citation_file=citation_file,
    )


def default_base_url(citation: dict) -> str:
    """https://github.com/<owner>/<repo> -> https://<owner>.github.io/<repo>/."""
    m = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+?)/?", citation.get("repository-code", ""))
    if not m:
        return "/"
    return f"https://{m.group(1).lower()}.github.io/{m.group(2)}/"


# ------------------------------------------------------------------ rendering


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def localized(value: dict, locale: str, texts: dict[str, dict]) -> str:
    """The version for the locale; else the English one, marked with its language."""
    if locale in value:
        return esc(value[locale])
    fallback = "en" if "en" in value else next(iter(value))
    language = texts[locale]["languages"].get(fallback, fallback)
    note = texts[locale]["only_in"].format(language=language)
    original = f'<span lang="{esc(fallback)}">{esc(value[fallback])}</span>'
    return f'{original} <span class="lang">({esc(note)})</span>'


def situation_item(situation: dict, locale: str, texts: dict[str, dict]) -> str:
    t = texts[locale]
    name = localized(situation["name"], locale, texts)
    status = situation.get("highest_status")
    if status is None:
        detail = f'<span class="none">{esc(t["status_none"])}</span>'
    else:
        label = localized(status["label"], locale, texts)
        detail = f'<a href="{esc(status["url"])}">{label}</a>'
        if status.get("checked_by") != "human":
            detail += f' <span class="draft">{esc(t["status_draft"])}</span>'
    return f'      <li id="{esc(situation["id"])}"><span class="name">{name}</span> {detail}</li>'


def citation_text(citation: dict, locale: str, inputs: Inputs) -> str:
    t = inputs.texts[locale]
    authors = "; ".join(
        ", ".join(p for p in (a.get("family-names"), a.get("given-names")) if p)
        for a in citation["authors"]
    )
    released = citation.get("date-released")
    return esc(
        t["cite_pattern"].format(
            authors=authors,
            title=citation.get("title", "Astraea"),
            type=t["cite_type"],
            date=format_date(released, inputs.formats[locale]) if released else "",
            url=citation.get("repository-code", ""),
        )
    )


def alternates(locales: list[str], base_url: str) -> str:
    links = [
        f'<link rel="alternate" hreflang="{esc(loc)}" href="{esc(base_url)}{route(loc)}/">'
        for loc in locales
    ]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{esc(base_url)}">')
    return "\n".join(links)


def language_links(current: str, texts: dict[str, dict]) -> str:
    parts = []
    for locale, t in texts.items():
        name = esc(t["language_name"])
        if locale == current:
            parts.append(f'<span aria-current="page" lang="{locale}">{name}</span>')
        else:
            parts.append(
                f'<a href="../{route(locale)}/" hreflang="{locale}" lang="{locale}">{name}</a>'
            )
    return " ".join(parts)


def home(locale: str, inputs: Inputs, base_url: str) -> str:
    t = inputs.texts[locale]
    q = inputs.quality
    countries = q["countries"]
    drafts = q["drafts"]
    as_of = q.get("as_of")
    files = [*DATA_FILES, *(f"i18n/{loc}.json" for loc in inputs.texts)]
    data_files = "\n".join(
        f'      <li><a href="../static/data/{esc(name)}">{esc(t["data_files"].get(name, name))}</a>'
        f" <code>{esc(name)}</code></li>"
        for name in files
    )
    return inputs.templates["home"].substitute(
        lang=esc(locale),
        site_name=esc(t["site_name"]),
        tagline=esc(t["tagline"]),
        skip_to_content=esc(t["skip_to_content"]),
        language_switch=esc(t["language_switch"]),
        language_links=language_links(locale, inputs.texts),
        alternates=alternates(list(inputs.texts), base_url),
        about_title=esc(t["about_title"]),
        about="\n    ".join(f"<p>{esc(p)}</p>" for p in t["about"]),
        countries_title=esc(t["countries_title"]),
        countries_total=countries["total"],
        countries_checked=countries["complete"],
        countries_counter=esc(
            t["countries_counter"].format(total=countries["total"], checked=countries["complete"])
        ),
        countries_note=esc(t["countries_note"]),
        situations_title=esc(t["situations_title"]),
        situations_intro=esc(t["situations_intro"]),
        situations="\n".join(situation_item(s, locale, inputs.texts) for s in inputs.situations),
        drafts_title=esc(t["drafts_title"]),
        drafts_fields=drafts["fields"],
        drafts_records=drafts["records"],
        drafts_counter=esc(
            t["drafts_counter"].format(fields=drafts["fields"], records=drafts["records"])
        ),
        drafts_note=esc(t["drafts_note"]),
        quality_link=esc(t["quality_link"]),
        cite_title=esc(t["cite_title"]),
        cite_intro=esc(t["cite_intro"]),
        citation=citation_text(inputs.citation, locale, inputs),
        cite_file=esc(t["cite_file"]),
        data_title=esc(t["data_title"]),
        data_intro=esc(t["data_intro"]),
        data_files=data_files,
        as_of=esc(t["as_of"].format(date=format_date(as_of, inputs.formats[locale])))
        if as_of
        else "",
        footer_licence=esc(t["footer_licence"]),
        footer_code=esc(t["footer_code"]),
        repository=esc(inputs.citation.get("repository-code", "")),
    )


def root_page(inputs: Inputs, base_url: str) -> str:
    locales = list(inputs.texts)
    pt = next((loc for loc in locales if loc.startswith("pt")), locales[0])
    links = "\n".join(
        f'    <li><a href="{route(loc)}/" hreflang="{loc}" lang="{loc}">'
        f"{esc(inputs.texts[loc]['root_link'])}</a></li>"
        for loc in locales
    )
    return inputs.templates["root"].substitute(
        site_name=esc(inputs.texts[locales[0]]["site_name"]),
        alternates=alternates(locales, base_url),
        route_pt=f"{route(pt)}/",
        route_en=f"{route('en' if 'en' in locales else locales[0])}/",
        links=links,
    )


def build(inputs: Inputs, base_url: str) -> dict[str, bytes]:
    """Relative path in the output -> content. Pages, stylesheet, data and citation."""
    files: dict[str, bytes] = {"index.html": root_page(inputs, base_url).encode("utf-8")}
    for locale in inputs.texts:
        files[f"{route(locale)}/index.html"] = home(locale, inputs, base_url).encode("utf-8")
    for path in sorted((inputs.site_dir / "assets").rglob("*")):
        if path.is_file():
            files[f"assets/{path.relative_to(inputs.site_dir / 'assets').as_posix()}"] = (
                path.read_bytes()
            )
    for path in sorted(inputs.data_dir.rglob("*")):
        if path.is_file():
            files[f"static/data/{path.relative_to(inputs.data_dir).as_posix()}"] = path.read_bytes()
    files["CITATION.cff"] = inputs.citation_file.read_bytes()
    return files


# ------------------------------------------------------------------ command line


def _state(path: Path, content: bytes) -> str:
    if not path.exists():
        return "new"
    return "unchanged" if path.read_bytes() == content else "changed"


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # a console in cp1252 must not break the report
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--execute", action="store_true", help="write (default: simulation)")
    parser.add_argument("--out", help=f"output directory (default: {DEFAULT_OUT}/)")
    parser.add_argument("--data", help="derived data directory (default: static/data/)")
    parser.add_argument("--site", help="templates and interface texts (default: site/)")
    parser.add_argument(
        "--base-url",
        help="public address of the site, for the hreflang links "
        "(default: the GitHub Pages address of repository-code in CITATION.cff)",
    )
    args = parser.parse_args(argv)

    data_dir = Path(args.data) if args.data else ROOT / "static" / "data"
    site_dir = Path(args.site) if args.site else ROOT / "site"
    out = Path(args.out) if args.out else ROOT / DEFAULT_OUT
    try:
        inputs = load(data_dir, site_dir, ROOT / "CITATION.cff")
    except (OSError, ValueError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        print("is static/data/ generated? python scripts/transform.py --draft --execute")
        return 2
    base_url = args.base_url or default_base_url(inputs.citation)
    if not base_url.endswith("/"):
        base_url += "/"
    try:
        files = {out / name: content for name, content in build(inputs, base_url).items()}
    except (KeyError, ValueError) as error:
        print(f"error: missing interface text or data field: {error}", file=sys.stderr)
        return 2

    if out.is_dir():
        for path in sorted(p for p in out.rglob("*") if p.is_file() and p not in files):
            print(f"left alone (not generated by this script, never deleted): {show(path)}")
    for path, content in files.items():
        state = _state(path, content)
        if state == "unchanged":
            print(f"up to date: {show(path)}")
        elif args.execute:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            print(f"wrote ({state}): {show(path)}")
        else:
            print(f"would write ({state}): {show(path)}")
    pages = ", ".join(f"/{route(loc)}/" for loc in inputs.texts)
    print(f"site: {len(files)} files, home page in {pages}; base URL {base_url}")
    if not args.execute:
        print("simulation: nothing was written; add --execute to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
