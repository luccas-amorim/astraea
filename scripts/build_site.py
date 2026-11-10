"""Builds the static site from static/data/ and the templates in site/.

    python scripts/build_site.py                 says what it would write (simulation)
    python scripts/build_site.py --execute       writes _site/
    python scripts/build_site.py --execute --out <dir> --base-url https://.../astraea/

Pages, in every active locale (`/en/…`, `/pt-br/…`, the same path after the prefix):

- the home page (`/en/`);
- the countries screen (`/en/countries/`): completeness per field and the table of the
  197, with filters on the Genocide Convention, the Rome Statute and the death penalty;
- one record per country (`/en/countries/BRA/`), with the provenance of every field
  (source, url, date read, confidence, who checked it) and the reason of every empty one;

plus a short page at the root that takes the reader to the browser's language. Every page
is rendered here, at build time, from the derived data (`static/data/`): nothing needs
JavaScript. The filters of the table are plain CSS: a group of radio buttons per field,
siblings of the table, and a rule that hides the rows that do not match the button
checked; without CSS the table shows the 197.

The output also carries a copy of `static/data/` (the open data the pages link to), the
stylesheet and `CITATION.cff`. Interface texts live in `site/i18n/<locale>.json`; field
and value labels and the date formats come from `static/data/i18n/<locale>.json`, through
the same function the derived labels use. Our texts and the `reason` of an empty field
are shown in the version that exists, marked with its language when it is not the page's.

Simulation by default; `--execute` writes; nothing is ever deleted: a file found in the
output that this script does not generate is only reported. Only the standard library.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import vocabularies as voc  # noqa: E402
from transform import COMPLETENESS_FIELDS, asserts, format_date, show  # noqa: E402

DEFAULT_OUT = "_site"
DATA_FILES = ("countries.json", "situations.json", "quality.json")
TEMPLATES = ("layout", "home", "countries", "country", "root")
DATA_LANGUAGE = "en"  # the language of the data itself: `reason`, `by` (D8)
# The filters of the countries table: block, the field read, the short key of the attribute.
FILTERS = (
    ("genocide_convention", "participation", "gc"),
    ("rome_statute", "participation", "rs"),
    ("death_penalty", "status", "dp"),
)
STATES = ("stamped", "draft", "empty")
_DATE = re.compile(r"\d{4}(-\d{2}(-\d{2})?)?")


def route(locale: str) -> str:
    """The path prefix of a locale: `pt-BR` -> `pt-br` (docs/04, "As telas")."""
    return locale.lower()


# ------------------------------------------------------------------ inputs


@dataclass
class Inputs:
    quality: dict
    situations: list[dict]
    countries: list[dict]
    labels: dict[str, dict]  # locale -> static/data/i18n/<locale>.json
    texts: dict[str, dict]  # locale -> site/i18n/<locale>.json
    citation: dict
    templates: dict[str, Template]
    data_dir: Path
    site_dir: Path
    citation_file: Path

    @property
    def formats(self) -> dict[str, dict]:
        return {locale: labels["formats"] for locale, labels in self.labels.items()}


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
    labels = {locale: _json(data_dir / "i18n" / f"{locale}.json") for locale in texts}
    templates = {
        name: Template((site_dir / "templates" / f"{name}.html").read_text(encoding="utf-8"))
        for name in TEMPLATES
    }
    return Inputs(
        quality=_json(data_dir / "quality.json"),
        situations=_json(data_dir / "situations.json"),
        countries=_json(data_dir / "countries.json"),
        labels=labels,
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


# ------------------------------------------------------------------ small pieces


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def marked(text: str, language: str, locale: str, texts: dict[str, dict]) -> str:
    """A text in its own language; outside a page of that language, marked as such."""
    if locale.split("-")[0] == language.split("-")[0]:
        return esc(text)
    name = texts[locale]["languages"].get(language, language)
    note = texts[locale]["only_in"].format(language=name)
    return (
        f'<span lang="{esc(language)}">{esc(text)}</span> <span class="lang">({esc(note)})</span>'
    )


def localized(value: dict, locale: str, texts: dict[str, dict]) -> str:
    """The version for the locale; else the English one, marked with its language."""
    if locale in value:
        return esc(value[locale])
    fallback = "en" if "en" in value else next(iter(value))
    return marked(value[fallback], fallback, locale, texts)


def our_text(value: dict, locale: str, texts: dict[str, dict]) -> str:
    """A localized text of ours ({locale: {text, author}}): the text, its language marked."""
    return localized({k: v["text"] for k, v in value.items()}, locale, texts)


def field_label(key: str, inputs: Inputs, locale: str) -> str:
    """The label of a field: by its path, else by its loose name (docs/03, "Chave")."""
    fields = inputs.labels[locale]["fields"]
    return fields.get(key) or fields[key.rsplit(".", 1)[-1]]


def value_label(key: str, value, inputs: Inputs, locale: str) -> str | None:
    return inputs.labels[locale]["values"].get(f"{key}.{value}")


def sort_key(text: str) -> str:
    """Alphabetical order that ignores accents: Áustria next to Austrália."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold()


def country_name(country: dict, locale: str) -> str:
    return country["name"].get(locale) or country["name"]["en"]


def up(path: str) -> str:
    """From a page at /<locale>/<path> back to the root of the site."""
    return "../" * (1 + path.count("/"))


def alternates(locales: list[str], base_url: str, path: str = "") -> str:
    links = [
        f'<link rel="alternate" hreflang="{esc(loc)}" href="{esc(base_url)}{route(loc)}/{path}">'
        for loc in locales
    ]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{esc(base_url)}">')
    return "\n".join(links)


def language_links(current: str, texts: dict[str, dict], path: str = "") -> str:
    parts = []
    for locale, t in texts.items():
        name = esc(t["language_name"])
        if locale == current:
            parts.append(f'<span aria-current="page" lang="{locale}">{name}</span>')
        else:
            href = f"{up(path)}{route(locale)}/{path}"
            parts.append(f'<a href="{href}" hreflang="{locale}" lang="{locale}">{name}</a>')
    return " ".join(parts)


def page(
    locale: str,
    inputs: Inputs,
    base_url: str,
    path: str,
    *,
    title: str,
    description: str,
    content: str,
    head_extra: str = "",
    wide: bool = False,
) -> str:
    """The layout around the content of a page at /<locale>/<path>."""
    t = inputs.texts[locale]
    in_countries = path.startswith("countries/")
    return inputs.templates["layout"].substitute(
        lang=esc(locale),
        title=esc(title),
        description=esc(description),
        alternates=alternates(list(inputs.texts), base_url, path),
        up=up(path),
        route=route(locale),
        head_extra=head_extra,
        skip_to_content=esc(t["skip_to_content"]),
        site_name=esc(t["site_name"]),
        sections_label=esc(t["sections_label"]),
        nav_countries=esc(t["nav_countries"]),
        countries_current=(
            ' aria-current="page"'
            if path == "countries/"
            else ' class="current"'
            if in_countries
            else ""
        ),
        language_switch=esc(t["language_switch"]),
        language_links=language_links(locale, inputs.texts, path),
        main_class="wrap wide" if wide else "wrap",
        content=content,
        footer_licence=esc(t["footer_licence"]),
        footer_code=esc(t["footer_code"]),
        repository=esc(inputs.citation.get("repository-code", "")),
    )


# ------------------------------------------------------------------ home page


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
    content = inputs.templates["home"].substitute(
        up=up(""),
        site_name=esc(t["site_name"]),
        tagline=esc(t["tagline"]),
        about_title=esc(t["about_title"]),
        about="\n    ".join(f"<p>{esc(p)}</p>" for p in t["about"]),
        countries_title=esc(t["countries_title"]),
        countries_total=countries["total"],
        countries_checked=countries["complete"],
        countries_counter=esc(
            t["countries_counter"].format(total=countries["total"], checked=countries["complete"])
        ),
        countries_note=esc(t["countries_note"]),
        countries_link=esc(t["countries_link"].format(total=countries["total"])),
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
    )
    return page(
        locale,
        inputs,
        base_url,
        "",
        title=f"{t['site_name']} — {t['tagline']}",
        description=t["tagline"],
        content=content,
    )


# ------------------------------------------------------------------ countries table


def filter_value(country: dict, block: str, key: str) -> str:
    """The value a filter reads: the field of the block, or `empty`."""
    value = (country.get(block) or {}).get(key)
    return value if value is not None else "empty"


def filter_values(block: str, key: str) -> tuple[str, ...]:
    return (*voc.VOCABULARIES[f"{block}.{key}"], "empty")


def filter_style() -> str:
    """The CSS that filters the table, one rule per radio button: no JavaScript.

    A checked button hides the rows whose attribute is another value; the three groups
    add up, so the table keeps the rows that match all three. The other rules mark the
    label of the checked button and of the focused one (the buttons themselves are
    visually hidden, still reachable by keyboard).
    """
    rules = []
    for block, key, short in FILTERS:
        for value in ("all", *filter_values(block, key)):
            ident = f"f-{short}-{value}"
            label = f'.filters label[for="{ident}"]'
            if value != "all":
                rules.append(
                    f'#{ident}:checked ~ .table-wrap tbody tr:not([data-{short}="{value}"])'
                    " { display: none; }"
                )
            rules.append(
                f"#{ident}:checked ~ {label} {{ font-weight: 600; border-color: var(--accent); }}"
            )
            rules.append(
                f"#{ident}:focus-visible ~ {label} {{ outline: 2px solid var(--accent); "
                "outline-offset: 2px; }"
            )
    return "<style>\n" + "\n".join(rules) + "\n</style>"


def filter_inputs() -> str:
    out = []
    for block, key, short in FILTERS:
        for value in ("all", *filter_values(block, key)):
            checked = " checked" if value == "all" else ""
            out.append(
                f'    <input class="filter" type="radio" name="{short}" id="f-{short}-{value}"'
                f' value="{value}"{checked}>'
            )
    return "\n".join(out)


def filter_groups(locale: str, inputs: Inputs) -> str:
    t = inputs.texts[locale]
    groups = []
    for block, key, short in FILTERS:
        counts: dict[str, int] = {}
        for c in inputs.countries:
            value = filter_value(c, block, key)
            counts[value] = counts.get(value, 0) + 1
        options = [(f"f-{short}-all", f"{t['filter_all']} ({len(inputs.countries)})")]
        for value in filter_values(block, key):
            name = (
                t["no_data"]
                if value == "empty"
                else value_label(f"{block}.{key}", value, inputs, locale)
            )
            options.append((f"f-{short}-{value}", f"{name} ({counts.get(value, 0)})"))
        labels = " ".join(f'<label for="{ident}">{esc(text)}</label>' for ident, text in options)
        groups.append(
            f'      <div class="group" role="group" aria-labelledby="g-{short}">'
            f'<p class="legend" id="g-{short}">{esc(field_label(block, inputs, locale))}</p> '
            f"{labels}</div>"
        )
    return "\n".join(groups)


def table_row(country: dict, locale: str, inputs: Inputs) -> str:
    t = inputs.texts[locale]
    ident = country["id"]
    attrs = " ".join(
        f'data-{short}="{esc(filter_value(country, block, key))}"' for block, key, short in FILTERS
    )
    cells = [
        f'<th scope="row"><a href="{esc(ident)}/">{esc(country_name(country, locale))}</a>'
        f' <span class="code">{esc(ident)}</span></th>',
        f"<td>{esc(value_label('un_status', country['un_status'], inputs, locale))}</td>",
    ]
    for block, key, _ in FILTERS:
        value = (country.get(block) or {}).get(key)
        if value is None:
            cells.append(f'<td class="empty">{esc(t["no_data"])}</td>')
        else:
            label = value_label(f"{block}.{key}", value, inputs, locale)
            cells.append(f"<td>{esc(label)}</td>")
    stamped, total = country["completeness"]["stamped"], len(COMPLETENESS_FIELDS)
    title = t["completeness_cell"].format(stamped=stamped, total=total)
    cells.append(f'<td class="done" title="{esc(title)}">{stamped}/{total}</td>')
    return f'        <tr id="{esc(ident)}" {attrs}>' + "".join(cells) + "</tr>"


def countries_page(locale: str, inputs: Inputs, base_url: str) -> str:
    t = inputs.texts[locale]
    q = inputs.quality["countries"]
    path = "countries/"
    rows = sorted(inputs.countries, key=lambda c: sort_key(country_name(c, locale)))
    state_headers = "".join(
        f'<th scope="col">{esc(value_label("completeness", s, inputs, locale))}</th>'
        for s in STATES
    )
    completeness_rows = "\n".join(
        f'        <tr data-field="{esc(name)}"><th scope="row">'
        f"{esc(field_label(name, inputs, locale))}</th>"
        + "".join(f'<td data-state="{s}">{q["fields"][name][s]}</td>' for s in STATES)
        + "</tr>"
        for name in COMPLETENESS_FIELDS
    )
    headers = [t["column_country"], field_label("un_status", inputs, locale)]
    headers += [field_label(block, inputs, locale) for block, _, _ in FILTERS]
    headers.append(field_label("completeness", inputs, locale))
    content = inputs.templates["countries"].substitute(
        up=up(path),
        heading=esc(t["countries_page_title"]),
        intro=esc(t["countries_page_intro"].format(total=q["total"])),
        no_verdict=esc(t["no_verdict"]),
        completeness_title=esc(t["completeness_title"]),
        completeness_intro=esc(t["completeness_intro"]),
        column_field=esc(t["column_field"]),
        state_headers=state_headers,
        completeness_rows=completeness_rows,
        countries_total=q["total"],
        countries_complete=q["complete"],
        complete_counter=esc(
            t["complete_counter"].format(complete=q["complete"], total=q["total"])
        ),
        table_title=esc(t["table_title"]),
        filters_intro=esc(t["filters_intro"]),
        filter_inputs=filter_inputs(),
        filter_groups=filter_groups(locale, inputs),
        table_caption=esc(t["table_caption"].format(total=q["total"])),
        column_headers="".join(f'<th scope="col">{esc(h)}</th>' for h in headers),
        rows="\n".join(table_row(c, locale, inputs) for c in rows),
        shown=esc(t["shown"]),
        data_note=esc(t["data_note"]),
    )
    return page(
        locale,
        inputs,
        base_url,
        path,
        title=f"{t['countries_page_title']} — {t['site_name']}",
        description=t["countries_page_intro"].format(total=q["total"]),
        content=content,
        head_extra=filter_style(),
        wide=True,
    )


# ------------------------------------------------------------------ country record


def show_value(block: str, key: str, value, record: dict, inputs: Inputs, locale: str) -> str:
    """A value of a block as the reader sees it: label, date, link or the text as is."""
    t = inputs.texts[locale]
    if value is None:
        return f'<span class="none">{esc(t["value_none"])}</span>'
    if isinstance(value, bool) or not isinstance(value, str):
        return esc(value)
    label = value_label(f"{block}.{key}", value, inputs, locale)
    if label is not None:
        return esc(label)
    if _DATE.fullmatch(value):
        return esc(format_date(value, inputs.formats[locale]))
    if value.startswith(("https://", "http://")):
        return f'<a href="{esc(value)}">{esc(value)}</a>'
    if key == "title" and record.get("language"):  # a title in its original language
        return f'<span lang="{esc(record["language"])}">{esc(value)}</span>'
    return esc(value)


def provenance(stamp: dict, inputs: Inputs, locale: str) -> str:
    """The stamp of a field, item by item; a missing item says so."""
    t = inputs.texts[locale]
    items = []
    for key in voc.STAMP_FIELDS:
        value = stamp.get(key)
        if value in (None, ""):
            shown = f'<span class="draft">{esc(t["stamp_missing"])}</span>'
        elif key == "url":
            shown = f'<a href="{esc(value)}">{esc(value)}</a>'
        elif key == "source":
            shown = f"<code>{esc(value)}</code>"
        elif key == "read_on":
            shown = esc(format_date(value, inputs.formats[locale]))
        else:
            shown = esc(value_label(key, value, inputs, locale) or value)
        items.append(
            f'<div data-stamp="{key}"><dt>{esc(field_label(key, inputs, locale))}</dt>'
            f"<dd>{shown}</dd></div>"
        )
    return (
        f'      <dl class="provenance" aria-label="{esc(t["provenance_title"])}">'
        + "".join(items)
        + "</dl>"
    )


def state_badge(state: str, inputs: Inputs, locale: str) -> str:
    label = value_label("completeness", state, inputs, locale)
    return f'<span class="state {state}">{esc(label)}</span>'


def block_section(country: dict, block: str, inputs: Inputs, locale: str) -> str:
    t = inputs.texts[locale]
    record = country.get(block)
    state = country["completeness"]["fields"][block]
    heading = esc(field_label(block, inputs, locale))
    out = [
        f'  <section class="block" id="{block}" data-state="{state}" aria-labelledby="h-{block}">',
        f'    <h2 id="h-{block}">{heading} {state_badge(state, inputs, locale)}</h2>',
    ]
    if record is None:
        out.append(f'    <p class="none">{esc(t["not_loaded"])}</p>')
    elif "reason" in record and not asserts(record):
        reason = marked(record["reason"], DATA_LANGUAGE, locale, inputs.texts)
        out.append(f'    <p class="reason"><strong>{esc(t["empty_reason"])}</strong> {reason}</p>')
    else:
        rows = []
        for key, value in record.items():
            if key in (*voc.STAMP_FIELDS, "note", "reason", "language"):
                continue
            rows.append(
                f'<div data-field="{block}.{key}">'
                f"<dt>{esc(field_label(f'{block}.{key}', inputs, locale))}</dt>"
                f"<dd>{show_value(block, key, value, record, inputs, locale)}</dd></div>"
            )
        out.append('      <dl class="fields">' + "".join(rows) + "</dl>")
        if record.get("note"):
            out.append(
                f'    <p class="note-text"><strong>{esc(field_label("note", inputs, locale))}:'
                f"</strong> {our_text(record['note'], locale, inputs.texts)}</p>"
            )
        out.append(f'    <h3 class="sub">{esc(t["provenance_title"])}</h3>')
        out.append(provenance(record, inputs, locale))
    out.append("  </section>")
    return "\n".join(out)


def identity(country: dict, inputs: Inputs, locale: str) -> str:
    """The stamped scalars (name, UN status, UN member since), each with its stamp."""
    t = inputs.texts[locale]
    stamps = country.get("provenance", {})
    out = []
    for key in voc.COUNTRY_STAMPED_SCALARS:
        value = country.get(key)
        if key == "name":
            shown = esc(country_name(country, locale))
        elif value is None:
            shown = f'<span class="none">{esc(t["value_none"])}</span>'
        elif (label := value_label(key, value, inputs, locale)) is not None:
            shown = esc(label)
        else:
            shown = esc(
                format_date(value, inputs.formats[locale]) if _DATE.fullmatch(value) else value
            )
        out.append(
            f'    <div class="scalar" id="{key}" data-field="{key}">'
            f'<p class="scalar-value"><strong>{esc(field_label(key, inputs, locale))}:</strong>'
            f" {shown}</p>"
        )
        if key in stamps:
            out.append(provenance(stamps[key], inputs, locale))
        elif value is not None:
            out.append(f'      <p class="draft">{esc(t["stamp_missing"])}</p>')
        out.append("    </div>")
    return "\n".join(out)


def country_situations(country: dict, inputs: Inputs, locale: str, path: str) -> str:
    """The situations the country is linked to, each pointing to the home page list."""
    t = inputs.texts[locale]
    linked = [s for s in inputs.situations if any(c["id"] == country["id"] for c in s["countries"])]
    if not linked:
        return f'    <p class="none">{esc(t["no_situations"])}</p>'
    items = []
    for s in linked:
        role = next(c["role"] for c in s["countries"] if c["id"] == country["id"])
        role_label = esc(value_label("countries.role", role, inputs, locale))
        status = s.get("highest_status")
        if status is None:
            detail = f'<span class="none">{esc(t["status_none"])}</span>'
        else:
            label = localized(status["label"], locale, inputs.texts)
            detail = f'<a href="{esc(status["url"])}">{label}</a>'
            if status.get("checked_by") != "human":
                detail += f' <span class="draft">{esc(t["status_draft"])}</span>'
        home_anchor = f"{up(path)}{route(locale)}/#{esc(s['id'])}"
        name = localized(s["name"], locale, inputs.texts)
        role_name = esc(field_label("countries.role", inputs, locale))
        items.append(
            f'      <li id="s-{esc(s["id"])}"><a class="name" href="{home_anchor}">{name}</a>'
            f' <span class="role">{role_name}: {role_label}</span> {detail}</li>'
        )
    return (
        f'    <p class="note">{esc(t["situations_of_country"])}</p>\n'
        '    <ul class="situations">\n' + "\n".join(items) + "\n    </ul>"
    )


def country_page(country: dict, locale: str, inputs: Inputs, base_url: str) -> str:
    t = inputs.texts[locale]
    path = f"countries/{country['id']}/"
    done = country["completeness"]
    name = country_name(country, locale)
    updated = country.get("updated_at")
    content = inputs.templates["country"].substitute(
        up=up(path),
        id=esc(country["id"]),
        back_to_list=esc(t["back_to_list"]),
        name=esc(name),
        no_verdict=esc(t["no_verdict"]),
        stamped=done["stamped"],
        draft=done["draft"],
        empty=done["empty"],
        completeness_line=esc(
            t["completeness_line"].format(
                stamped=done["stamped"],
                draft=done["draft"],
                empty=done["empty"],
                total=len(COMPLETENESS_FIELDS),
            )
        ),
        identity_title=esc(t["identity_title"]),
        identity=identity(country, inputs, locale),
        blocks="\n\n".join(block_section(country, b, inputs, locale) for b in voc.COUNTRY_BLOCKS),
        situations_title=esc(t["situations_title"]),
        situations=country_situations(country, inputs, locale, path),
        record_note=esc(t["record_note"]),
        updated=esc(t["updated"].format(date=format_date(updated, inputs.formats[locale])))
        if updated
        else "",
    )
    return page(
        locale,
        inputs,
        base_url,
        path,
        title=f"{name} — {t['countries_page_title']} — {t['site_name']}",
        description=t["country_description"].format(name=name),
        content=content,
    )


# ------------------------------------------------------------------ the root and the build


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
        prefix = route(locale)
        files[f"{prefix}/index.html"] = home(locale, inputs, base_url).encode("utf-8")
        files[f"{prefix}/countries/index.html"] = countries_page(locale, inputs, base_url).encode(
            "utf-8"
        )
        for country in inputs.countries:
            files[f"{prefix}/countries/{country['id']}/index.html"] = country_page(
                country, locale, inputs, base_url
            ).encode("utf-8")
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
    unchanged = 0
    for path, content in files.items():
        state = _state(path, content)
        if state == "unchanged":
            unchanged += 1
        elif args.execute:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            print(f"wrote ({state}): {show(path)}")
        else:
            print(f"would write ({state}): {show(path)}")
    if unchanged:
        print(f"up to date: {unchanged} files in {show(out)}")
    pages = ", ".join(f"/{route(loc)}/" for loc in inputs.texts)
    print(
        f"site: {len(files)} files; in {pages}: the home page, countries/ and "
        f"{len(inputs.countries)} country records; base URL {base_url}"
    )
    if not args.execute:
        print("simulation: nothing was written; add --execute to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
