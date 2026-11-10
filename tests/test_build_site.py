"""scripts/build_site.py: the home page, the countries screen and the country records.

Covers both locales, the counters, a situation without status, simulation × --execute,
the filters of the table without JavaScript, the provenance of every field, the reason
of an empty one, and rule 1 on the screen (the word only as the name of the crime or of
the convention, never as a label of a country or of a situation).

Most tests build a small static/data/ in tmp_path with two made-up countries and the real
labels, interface texts and templates; the last ones run over the real static/data/ of
the repository.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
import vocabularies as voc  # noqa: E402

LOCALES = ("en", "pt-BR")
FIELDS = ("un_status", *voc.COUNTRY_BLOCKS)


def write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def stamp(source: str, url: str, read_on: str | None, confidence: str, checked_by) -> dict:
    return {
        "url": url,
        "source": source,
        "read_on": read_on,
        "confidence": confidence,
        "checked_by": checked_by,
    }


UNTC = "https://treaties.un.org/doc/IV-1.en.xml"
ATLANTIS = {
    "id": "AAA",
    "name": {"en": "Atlantis", "pt-BR": "Atlântida"},
    "un_status": "member",
    "un_member_since": "1945-10-24",
    "penal_code": {
        "exists": "yes",
        "title": "Código Penal de Atlântida",
        "enacted_year": 1940,
        "language": "pt",
        "note": {"pt-BR": {"text": "Nota só em português.", "author": "human"}},
        **stamp("planalto", "https://law.example/code", "2026-10-26", "A", "human"),
    },
    "genocide_convention": {
        "participation": "party",
        "signature": "1948-12-11",
        "bound_since": "1952-04-15",
        "consent_type": "ratification",
        **stamp("untc", UNTC, "2026-11-10", "A", "robot"),
    },
    "rome_statute": {
        "participation": "signatory",
        "signature": "2000-02-07",
        **stamp("untc", "https://treaties.un.org/doc/XVIII-10.en.xml", None, "A", None),
    },
    "death_penalty": {
        "status": "retentionist",
        **stamp("cornell-dpw", "https://dpw.example/Retentionist", "2026-11-10", "B", "robot"),
    },
    "situations": ["with-status"],
    "provenance": {
        "name": stamp("cldr", "https://cldr.example", "2026-11-09", "B", "robot"),
        "un_status": stamp("un-member-states", "https://un.example", "2026-11-09", "A", "robot"),
        "un_member_since": stamp(
            "un-member-states", "https://un.example", "2026-11-09", "A", "robot"
        ),
    },
    "completeness": {
        "stamped": 4,
        "draft": 1,
        "empty": 2,
        "fields": {
            "un_status": "stamped",
            "penal_code": "stamped",
            "domestic_genocide": "empty",
            "genocide_convention": "stamped",
            "rome_statute": "draft",
            "max_penalty": "empty",
            "death_penalty": "stamped",
        },
    },
    "updated_at": "2026-11-10",
}
REASON = "No entry of its own in the depositary tables. Left empty."
BORDURIA = {
    "id": "BBB",
    "name": {"en": "Borduria"},
    "un_status": "non_member",
    "un_member_since": None,
    "genocide_convention": {"reason": REASON},
    "rome_statute": {"reason": REASON},
    "death_penalty": {"reason": "Not in any list."},
    "situations": [],
    "provenance": {
        "name": stamp("cldr", "https://cldr.example", "2026-11-09", "B", "robot"),
        "un_status": stamp(
            "un-non-member-states", "https://un.example/n", "2026-11-10", "B", "robot"
        ),
    },
    "completeness": {
        "stamped": 1,
        "draft": 0,
        "empty": 6,
        "fields": {"un_status": "stamped", **{b: "empty" for b in voc.COUNTRY_BLOCKS}},
    },
    "updated_at": "2026-11-10",
}


@pytest.fixture
def data(tmp_path) -> Path:
    """A static/data/ with two situations and two countries, and the real labels."""
    folder = tmp_path / "static" / "data"
    write(
        folder / "quality.json",
        {
            "as_of": "2026-11-09",
            "drafts": {"fields": 13, "records": 9, "items": []},
            "countries": {
                "total": 197,
                "complete": 0,
                "fields": {
                    f: {"stamped": i, "draft": 1, "empty": 196 - i} for i, f in enumerate(FIELDS)
                },
            },
        },
    )
    write(
        folder / "situations.json",
        [
            {
                "id": "with-status",
                "name": {"en": "Somewhere (2020–)", "pt-BR": "Algures (2020–)"},
                "countries": [{"id": "AAA", "role": "territory"}],
                "highest_status": {
                    "code": "provisional_measures",
                    "url": "https://court.example/case/1",
                    "checked_by": None,
                    "label": {
                        "en": "provisional measures — Court, 23 Jan 2020",
                        "pt-BR": "medidas provisórias — Court, 23/01/2020",
                    },
                },
            },
            {
                "id": "without-status",
                "name": {"en": "Elsewhere (1994)"},
                "countries": [],
                "highest_status": None,
            },
        ],
    )
    write(folder / "countries.json", [BORDURIA, ATLANTIS])
    (folder / "i18n").mkdir()
    for locale in LOCALES:
        name = f"{locale}.json"
        shutil.copy(ROOT / "static" / "data" / "i18n" / name, folder / "i18n" / name)
    return folder


def run(data: Path, out: Path, *extra: str) -> int:
    return build_site.main(["--data", str(data), "--out", str(out), *extra])


def page(out: Path, locale: str, path: str = "") -> str:
    return (out / build_site.route(locale) / path / "index.html").read_text(encoding="utf-8")


@pytest.fixture
def site(data, tmp_path) -> Path:
    out = tmp_path / "site"
    assert run(data, out, "--execute") == 0
    return out


def section(html: str, ident: str) -> str:
    """A section by its id, or by the heading that labels it."""
    pattern = rf'<section[^>]*(?: id| aria-labelledby)="{ident}".*?</section>'
    return re.search(pattern, html, re.S).group()


# ------------------------------------------------------------------ the build


def test_routes_follow_the_locale():
    assert build_site.route("en") == "en"
    assert build_site.route("pt-BR") == "pt-br"


def test_simulation_writes_nothing(data, tmp_path, capsys):
    out = tmp_path / "site"
    assert run(data, out) == 0
    assert not out.exists()
    printed = capsys.readouterr().out
    assert "would write (new):" in printed and "en/index.html" in printed
    assert "en/countries/AAA/index.html" in printed
    assert "simulation: nothing was written" in printed


def test_execute_writes_every_page_in_both_languages(site):
    for name in (
        "index.html",
        "en/index.html",
        "pt-br/index.html",
        "en/countries/index.html",
        "pt-br/countries/index.html",
        "en/countries/AAA/index.html",
        "pt-br/countries/BBB/index.html",
        "assets/style.css",
        "static/data/quality.json",
        "static/data/i18n/pt-BR.json",
        "CITATION.cff",
    ):
        assert (site / name).is_file(), name
    root = (site / "index.html").read_text(encoding="utf-8")
    assert 'href="en/"' in root and 'href="pt-br/"' in root


def test_second_execute_is_up_to_date_and_never_deletes(data, site, capsys):
    stray = site / "old.html"
    stray.write_text("kept", encoding="utf-8")
    capsys.readouterr()
    assert run(data, site, "--execute") == 0
    printed = capsys.readouterr().out
    assert "wrote" not in printed
    assert "up to date:" in printed
    assert "left alone (not generated by this script, never deleted)" in printed
    assert stray.read_text(encoding="utf-8") == "kept"


def test_missing_derived_data_is_an_error(tmp_path, capsys):
    assert run(tmp_path / "nothing", tmp_path / "site") == 2
    assert "transform.py" in capsys.readouterr().out


def test_default_base_url_is_the_pages_address():
    citation = {"repository-code": "https://github.com/Owner/repo"}
    assert build_site.default_base_url(citation) == "https://owner.github.io/repo/"


def test_interface_texts_have_the_same_keys_in_every_locale():
    texts = {loc: json.loads((ROOT / "site/i18n" / f"{loc}.json").read_text(encoding="utf-8"))
             for loc in LOCALES}  # fmt: skip
    assert set(texts["en"]) == set(texts["pt-BR"])
    assert set(texts["en"]["data_files"]) == set(texts["pt-BR"]["data_files"])


# ------------------------------------------------------------------ home page


def test_counter_in_both_languages(site):
    assert "197 countries, 0 checked" in page(site, "en")
    assert "197 países, 0 conferidos" in page(site, "pt-BR")
    assert "13 fields in draft, in 9 records" in page(site, "en")
    assert "13 campos em rascunho, em 9 registros" in page(site, "pt-BR")


def test_the_home_page_leads_to_the_countries(site):
    assert '<a href="countries/">The 197 countries, field by field</a>' in page(site, "en")
    assert '<a href="countries/">Os 197 países, campo a campo</a>' in page(site, "pt-BR")


def test_situations_with_and_without_status(site):
    en, pt = page(site, "en"), page(site, "pt-BR")
    assert "provisional measures — Court, 23 Jan 2020" in en
    assert "medidas provisórias — Court, 23/01/2020" in pt
    assert 'href="https://court.example/case/1"' in en
    assert "draft: not yet checked by a person" in en
    item = re.search(r'<li id="without-status">.*?</li>', pt).group()
    assert "sem status registrado" in item
    # The name has no pt-BR version: the English one appears, marked with its language.
    assert "Elsewhere (1994)" in item and "disponível só em inglês" in item
    assert "no status recorded" in re.search(r'<li id="without-status">.*?</li>', en).group()


def test_dates_follow_the_locale_formats(site):
    assert "Data as of 9 Nov 2026." in page(site, "en")
    assert "Dados de 09/11/2026." in page(site, "pt-BR")


def test_language_switch_and_hreflang(data, tmp_path):
    out = tmp_path / "site"
    run(data, out, "--execute", "--base-url", "https://example.org/astraea")
    en = page(out, "en")
    assert '<html lang="en">' in en and '<html lang="pt-BR">' in page(out, "pt-BR")
    assert 'href="../pt-br/"' in en
    assert '<link rel="alternate" hreflang="pt-BR" href="https://example.org/astraea/pt-br/">' in en
    assert 'hreflang="x-default" href="https://example.org/astraea/"' in en
    record = page(out, "en", "countries/AAA")
    assert 'href="../../../pt-br/countries/AAA/"' in record
    assert 'hreflang="pt-BR" href="https://example.org/astraea/pt-br/countries/AAA/"' in record
    assert 'href="../../../assets/style.css"' in record


def test_citation_comes_from_citation_cff(site):
    en = page(site, "en")
    assert "Amorim, Luccas de." in en and "[dataset]" in en
    assert "https://github.com/luccas-amorim/astraea" in en


# ------------------------------------------------------------------ the countries screen


def rows(html: str) -> list[str]:
    body = re.search(r'<table class="countries">.*?<tbody>(.*?)</tbody>', html, re.S).group(1)
    return re.findall(r"<tr [^>]*>.*?</tr>", body)


def test_the_table_lists_every_country_in_the_order_of_the_locale(site):
    en, pt = page(site, "en", "countries"), page(site, "pt-BR", "countries")
    assert [re.search(r'id="(\w+)"', r).group(1) for r in rows(en)] == ["AAA", "BBB"]
    # Atlântida sorts as Atlantida, before Borduria; the name links to the record
    assert '<a href="AAA/">Atlântida</a>' in rows(pt)[0]
    assert "Borduria" in rows(pt)[1]


def test_each_row_carries_what_the_filters_read(site):
    atlantis, borduria = rows(page(site, "en", "countries"))
    assert 'data-gc="party" data-rs="signatory" data-dp="retentionist"' in atlantis
    assert 'data-gc="empty" data-rs="empty" data-dp="empty"' in borduria
    assert "<td>party</td><td>signatory, not bound</td><td>retentionist</td>" in atlantis
    assert borduria.count('<td class="empty">no data</td>') == 3
    assert '<td class="done" title="4 of 7 fields stamped">4/7</td>' in atlantis


def test_the_filters_work_without_javascript(site):
    for locale in LOCALES:
        html = page(site, locale, "countries")
        assert "<script" not in html
        listing = re.search(r'<section class="list".*?</section>', html, re.S).group()
        # The radio buttons come before the labels and the table, as their siblings:
        # the CSS rules `#f-…:checked ~ .table-wrap tr` need exactly that.
        inputs = re.findall(
            r'<input class="filter" type="radio" name="(\w+)" id="([\w-]+)"', listing
        )
        assert listing.index("<input") < listing.index('<div class="filters">')
        assert listing.index('<div class="filters">') < listing.index('<div class="table-wrap">')
        for block, key, short in build_site.FILTERS:
            values = [*voc.VOCABULARIES[f"{block}.{key}"], "empty"]
            assert [i for n, i in inputs if n == short] == [
                f"f-{short}-{v}" for v in ("all", *values)
            ]
            assert f'id="f-{short}-all" value="all" checked>' in listing
            for value in values:
                rule = (
                    f"#f-{short}-{value}:checked ~ .table-wrap tbody "
                    f'tr:not([data-{short}="{value}"]) {{ display: none; }}'
                )
                assert rule in html, rule
                assert f'<label for="f-{short}-{value}">' in listing


def test_the_filter_labels_count_the_countries(site):
    en = page(site, "en", "countries")
    assert '<label for="f-gc-all">all (2)</label>' in en
    assert '<label for="f-gc-party">party (1)</label>' in en
    assert '<label for="f-gc-empty">no data (1)</label>' in en
    assert '<label for="f-dp-abolitionist_in_practice">abolitionist in practice (0)</label>' in en
    pt = page(site, "pt-BR", "countries")
    assert '<label for="f-rs-signatory">signatário, não vinculado (1)</label>' in pt
    assert '<label for="f-dp-all">todos (2)</label>' in pt


def test_completeness_by_field_comes_from_the_quality_report(site):
    html = page(site, "pt-BR", "countries")
    table = re.search(r'<table class="completeness">.*?</table>', html, re.S).group()
    for i, name in enumerate(FIELDS):
        row = re.search(rf'<tr data-field="{name}">.*?</tr>', table).group()
        assert (
            f'<td data-state="stamped">{i}</td><td data-state="draft">1</td>'
            f'<td data-state="empty">{196 - i}</td>'
        ) in row
    assert "Pena de morte" in table and "carimbado: fonte, data e quem conferiu" in table
    assert "0 de 197 países com todos os campos carimbados" in html


# ------------------------------------------------------------------ the country record


def test_the_record_shows_the_provenance_of_every_field(site):
    html = page(site, "en", "countries/AAA")
    convention = section(html, "genocide_convention")
    assert 'data-state="stamped"' in convention
    assert "<dd>party</dd>" in convention and "<dd>11 Dec 1948</dd>" in convention
    for item in (
        f'<dd><a href="{UNTC}">{UNTC}</a></dd>',
        "<dd><code>untc</code></dd>",
        "<dd>10 Nov 2026</dd>",
        "<dd>A — official or intergovernmental</dd>",
        "<dd>robot</dd>",
    ):
        assert item in convention, item
    assert "<dd>person</dd>" in section(html, "penal_code")  # checked_by: human
    identity = section(html, "identity")
    assert identity.count('<dl class="provenance"') == 3  # name, UN status, member since
    assert "Member State" in identity and "24 Oct 1945" in identity
    pt = page(site, "pt-BR", "countries/AAA")
    assert "<dd>10/11/2026</dd>" in section(pt, "genocide_convention")
    assert "<dd>robô</dd>" in section(pt, "genocide_convention")


def test_a_field_in_draft_says_what_is_missing(site):
    statute = section(page(site, "en", "countries/AAA"), "rome_statute")
    assert 'data-state="draft"' in statute and "draft, without full stamp" in statute
    for key in ("read_on", "checked_by"):
        item = re.search(rf'<div data-stamp="{key}">.*?</div>', statute).group()
        assert "missing: not yet stamped" in item
    assert "signatory, not bound" in statute


def test_an_empty_field_shows_its_reason_marked_in_portuguese(site):
    en = section(page(site, "en", "countries/BBB"), "genocide_convention")
    assert f"Left empty. The reason recorded:</strong> {REASON}</p>" in en
    pt = section(page(site, "pt-BR", "countries/BBB"), "genocide_convention")
    assert f'<span lang="en">{REASON}</span>' in pt
    assert "(disponível só em inglês)" in pt
    assert "Deixado vazio. O motivo registrado:" in pt
    assert "provenance" not in pt  # nothing asserted, nothing stamped


def test_a_block_not_loaded_says_so(site):
    html = page(site, "en", "countries/BBB")
    for block in ("penal_code", "domestic_genocide", "max_penalty"):
        assert "Not loaded yet." in section(html, block), block
    assert "Ainda não carregado." in section(page(site, "pt-BR", "countries/BBB"), "max_penalty")


def test_our_text_and_a_title_keep_their_language(site):
    en = section(page(site, "en", "countries/AAA"), "penal_code")
    assert '<span lang="pt">Código Penal de Atlântida</span>' in en
    assert '<span lang="pt-BR">Nota só em português.</span>' in en
    assert "available only in Portuguese" in en
    pt = section(page(site, "pt-BR", "countries/AAA"), "penal_code")
    assert "Nota só em português." in pt and "disponível só" not in pt


def test_the_record_lists_the_situations_of_the_country(site):
    html = section(page(site, "en", "countries/AAA"), "situations")
    assert '<a class="name" href="../../../en/#with-status">Somewhere (2020–)</a>' in html
    assert "Role: territory" in html
    assert "provisional measures — Court, 23 Jan 2020" in html
    assert "draft: not yet checked by a person" in html
    other = section(page(site, "pt-BR", "countries/BBB"), "situations")
    assert "Este país não aparece em nenhuma das situações acompanhadas." in other


def test_the_record_counts_its_fields(site):
    assert "4 of 7 fields stamped, 1 in draft, 2 empty" in page(site, "en", "countries/AAA")
    assert "1 de 7 campos carimbados, 0 em rascunho, 6 vazios" in page(
        site, "pt-BR", "countries/BBB"
    )


# ------------------------------------------------------------------ rule 1 on the screen

WORD = re.compile(r"genoc[ií]d", re.I)
# Interface text may name the crime, never use the word as a label.
ALLOWED = {
    "en": ("crime of genocide",),
    "pt-BR": ("crime de genocídio",),
}
ROBOTS = ("Tabelião", "Cartógrafo", "Sentenciador", "Vigia", "Escrivão", "Recenseador",
          "Arquivista", "Auditor")  # fmt: skip


def allowed(locale: str) -> list[str]:
    """The phrases the word may appear in: the name of the crime in our texts, and the
    labels of the fields about the crime or the convention ("Genocide Convention (1948)",
    "Genocide in domestic law"): names of a crime and of a treaty, not a qualification."""
    labels = json.loads((ROOT / "static/data/i18n" / f"{locale}.json").read_text(encoding="utf-8"))
    phrases = [v for v in labels["fields"].values() if WORD.search(v)]
    # both names of the crime: the citation title, from CITATION.cff, is in Portuguese on
    # both pages
    crime = [p for names in ALLOWED.values() for p in names]
    return sorted({*crime, *phrases}, key=len, reverse=True)


def visible(html: str) -> str:
    """What the reader reads: the text and the title of the page, without tags,
    attributes or the style. Keys and ids in attributes are the data contract, in English
    (D8): `domestic_genocide` is a key, not a label."""
    html = re.sub(r"<style>.*?</style>", " ", html, flags=re.S)
    read = re.findall(r'(?:content|title|aria-label)="([^"]*)"', html)  # read aloud or shown
    text = re.sub(r"<[^>]+>", " ", html)
    return build_site.html.unescape(" ".join([text, *read]))


def without_allowed(html: str, locale: str) -> str:
    rest = visible(html).lower()
    for phrase in allowed(locale):
        rest = rest.replace(phrase.lower(), "")
    return rest


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


@pytest.mark.parametrize("locale", LOCALES)
def test_interface_texts_never_label_a_situation_or_country_with_the_word(locale):
    texts = json.loads((ROOT / "site/i18n" / f"{locale}.json").read_text(encoding="utf-8"))
    for text in strings(texts):
        rest = text.lower()
        for phrase in ALLOWED[locale]:
            rest = rest.replace(phrase, "")
        assert not WORD.search(rest), f"{locale}: {text!r}"


# ------------------------------------------------------------------ the real data


@pytest.fixture(scope="module")
def real(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("real") / "site"
    assert build_site.main(["--out", str(out), "--execute"]) == 0
    return out


@pytest.fixture(scope="module")
def derived() -> list[dict]:
    return json.loads((ROOT / "static/data/countries.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("locale", LOCALES)
def test_the_real_page_lists_situations_without_the_word(real, locale):
    html = page(real, locale)
    situations = re.search(r'<ul class="situations">.*?</ul>', html, re.S).group()
    assert situations.count("<li ") == 10
    assert not WORD.search(situations)
    counters = re.findall(r'<p class="counter".*?</p>', html)
    assert counters and not any(WORD.search(c) for c in counters)


def test_the_real_page_has_the_counter(real):
    quality = json.loads((ROOT / "static/data/quality.json").read_text(encoding="utf-8"))
    total, complete = quality["countries"]["total"], quality["countries"]["complete"]
    assert f"{total} countries, {complete} checked" in page(real, "en")
    assert f"{total} países, {complete} conferidos" in page(real, "pt-BR")


@pytest.mark.parametrize("locale", LOCALES)
def test_every_country_has_its_row_and_its_record(real, derived, locale):
    assert len(derived) == 197
    html = page(real, locale, "countries")
    assert sorted(re.search(r'id="(\w+)"', r).group(1) for r in rows(html)) == sorted(
        c["id"] for c in derived
    )
    records = {
        p.name for p in (real / build_site.route(locale) / "countries").iterdir() if p.is_dir()
    }
    assert records == {c["id"] for c in derived}


@pytest.mark.parametrize("locale", LOCALES)
def test_the_real_filter_counts_agree_with_the_data(real, derived, locale):
    html = page(real, locale, "countries")
    for block, key, short in build_site.FILTERS:
        for value in (*voc.VOCABULARIES[f"{block}.{key}"], "empty"):
            expected = sum(1 for c in derived if build_site.filter_value(c, block, key) == value)
            label = re.search(rf'<label for="f-{short}-{value}">[^<]*\((\d+)\)</label>', html)
            assert int(label.group(1)) == expected, (short, value)
            assert sum(f'data-{short}="{value}"' in r for r in rows(html)) == expected


def test_the_real_completeness_agrees_with_the_quality_report(real):
    quality = json.loads((ROOT / "static/data/quality.json").read_text(encoding="utf-8"))
    table = re.search(
        r'<table class="completeness">.*?</table>', page(real, "en", "countries"), re.S
    ).group()
    for name, counts in quality["countries"]["fields"].items():
        row = re.search(rf'<tr data-field="{name}">.*?</tr>', table).group()
        for state, n in counts.items():
            assert f'<td data-state="{state}">{n}</td>' in row, (name, state)


@pytest.mark.parametrize("locale", LOCALES)
def test_every_real_record_shows_each_stamp_and_each_reason(real, derived, locale):
    for country in derived:
        html = page(real, locale, f"countries/{country['id']}")
        for block in voc.COUNTRY_BLOCKS:
            record = country.get(block)
            part = section(html, block)
            if record is None:
                assert 'data-state="empty"' in part, (country["id"], block)
            elif "reason" in record:
                assert build_site.esc(record["reason"]) in part, (country["id"], block)
                if locale != "en":
                    assert '<span lang="en">' in part
            else:
                assert f'<a href="{build_site.esc(record["url"])}">' in part, (country["id"], block)
                assert f"<code>{record['source']}</code>" in part


def test_the_record_of_brazil(real):
    html = page(real, "pt-BR", "countries/BRA")
    assert "<h1>Brasil</h1>" in html
    assert "<dd>parte</dd>" in section(html, "genocide_convention")
    assert "<dd>15/04/1952</dd>" in section(html, "genocide_convention")
    assert "abolicionista só para crimes comuns" in section(html, "death_penalty")
    assert "<dd><code>cornell-dpw</code></dd>" in section(html, "death_penalty")


@pytest.mark.parametrize("locale", LOCALES)
def test_the_word_appears_only_as_the_name_of_the_crime_or_of_the_convention(real, locale):
    folder = real / build_site.route(locale)
    pages = sorted(folder.rglob("index.html"))
    assert len(pages) == 1 + 1 + 197
    for path in pages:
        rest = without_allowed(path.read_text(encoding="utf-8"), locale)
        found = WORD.search(rest)
        assert not found, (path, found and rest[max(0, found.start() - 80) : found.end() + 40])


@pytest.mark.parametrize("locale", LOCALES)
def test_no_robot_name_on_any_page(real, locale):
    """D15: the robot names are not decided; no page shows one."""
    for path in (real / build_site.route(locale)).rglob("index.html"):
        html = path.read_text(encoding="utf-8")
        assert not [name for name in ROBOTS if name in html], path
