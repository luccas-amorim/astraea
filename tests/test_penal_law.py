"""The penal law blocks of the human load: penal_code, domestic_genocide, max_penalty.

Phase 2, session 4 (2026-11-10): the 24 countries the owner approved for the human load,
Brazil first. A session reads the source and prepares the block with url, source,
read_on and confidence; `checked_by` stays empty until the owner stamps it
(scripts/stamp.py), so these tests accept a block prepared or stamped by a person, and a
later `read_on`. The robot never writes these blocks (docs/02, 1.2; AGENTS.md, rule 4).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
import transform  # noqa: E402
import vocabularies as voc  # noqa: E402

BLOCKS = ("penal_code", "domestic_genocide", "max_penalty")
# The list approved by the owner on 2026-11-10, in the order of the load: Brazil; the
# priority of quality.json; the other countries linked to a situation; and the forum or
# jurisdiction countries without a link (docs/06, phase 2, item 4).
HUMAN_LOAD = (
    "BRA",
    *("MMR", "PSE", "ISR", "UKR", "RUS", "SDN", "BIH", "SRB"),
    *("GMB", "ZAF", "ETH", "CHN", "IRQ", "RWA", "KHM"),
    *("DEU", "FRA", "BEL", "NLD", "ARG", "BGD", "TZA", "SYR"),
)
FIRST_READ = "2026-11-10"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def countries() -> dict[str, dict]:
    return {c["id"]: c for c in load("countries.json")}


@pytest.fixture(scope="module")
def sources() -> dict[str, dict]:
    return {s["id"]: s for s in load("sources.json")}


def loaded(countries):
    for ident, record in countries.items():
        for name in BLOCKS:
            if name in record:
                yield ident, name, record[name]


def test_the_list_has_24_countries_with_brazil_first(countries):
    assert len(HUMAN_LOAD) == len(set(HUMAN_LOAD)) == 24
    assert HUMAN_LOAD[0] == "BRA"
    assert set(HUMAN_LOAD) <= set(countries)


def test_the_blocks_exist_only_where_the_human_load_reached(countries):
    reached = {ident for ident, _, _ in loaded(countries)}
    assert reached <= set(HUMAN_LOAD)
    for ident in HUMAN_LOAD:
        # Every country of the list has at least the two blocks of the law, read or empty.
        assert {"penal_code", "domestic_genocide"} <= set(countries[ident]), ident


def test_each_block_is_prepared_stamped_by_a_person_or_empty_with_a_reason(countries):
    for ident, name, block in loaded(countries):
        where = f"{ident}.{name}"
        if "reason" in block:
            assert set(block) == {"reason"}, where
            assert block["reason"].strip(), where
            continue
        assert transform.asserts(block), where
        for field in ("url", "source", "read_on", "confidence"):
            assert block.get(field), (where, field)
        assert transform.is_full_date(block["read_on"]) and block["read_on"] >= FIRST_READ, where
        # Prepared (waiting for the owner) or stamped by a person; never by the robot.
        assert block["checked_by"] in (None, "human"), where


def test_the_source_is_active_of_function_1_and_gives_the_confidence(countries, sources):
    for ident, name, block in loaded(countries):
        if "reason" in block:
            continue
        source = sources[block["source"]]
        assert source["state"] == "active" and source["function"] == 1, (ident, name)
        assert block["confidence"] == source["confidence"], (ident, name)
        assert source["robots_checked_on"], (ident, name)


def test_values_are_in_the_vocabularies_and_years_only_with_years(countries):
    for ident, name, block in loaded(countries):
        for key, value in block.items():
            vocabulary = voc.VOCABULARIES.get(f"{name}.{key}")
            if vocabulary and value is not None:
                assert value in vocabulary, (ident, name, key)
        if name == "max_penalty" and "type" in block:
            if block["type"] == "years":
                assert isinstance(block["years"], int) and block["years"] > 0, ident
            else:
                assert block.get("years") is None, ident
        if name == "penal_code" and block.get("official_url"):
            assert block["official_url"].startswith(("https://", "http://")), ident
            assert re.fullmatch(r"[a-z]{2}", block["language"]), ident


def test_a_note_is_written_only_by_a_person(countries):
    """D4 is pending: a text of ours is the owner's, with author human."""
    for ident, name, block in loaded(countries):
        for version in (block.get("note") or {}).values():
            assert version["author"] == "human", (ident, name)


def test_a_retentionist_with_a_lesser_maximum_has_a_note(countries):
    """Check 10, on the real data: the validator reprobates it; this says where."""
    for ident, record in countries.items():
        penalty, death = record.get("max_penalty") or {}, record.get("death_penalty") or {}
        if death.get("status") == "retentionist" and penalty.get("type") in ("years", "life"):
            assert penalty.get("note") or death.get("note"), ident


def test_brazil_has_the_three_blocks_read_at_the_planalto(countries):
    brazil = countries["BRA"]
    code, genocide, penalty = (brazil[b] for b in BLOCKS)
    assert {code["source"], genocide["source"], penalty["source"]} == {"planalto"}
    assert code["exists"] == "yes" and code["enacted_year"] == 1940
    assert code["title"].startswith("Código Penal (Decreto-Lei nº 2.848")
    assert code["official_url"] == (
        "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm"
    )
    assert code["alternative_url"] == "https://atlaspen.com.br/data/crimes.json"
    assert genocide["status"] == "criminalized"
    assert genocide["instrument"].startswith("Lei nº 2.889")
    assert (genocide["provision"], genocide["year"]) == ("art. 1º", 1956)
    assert genocide["follows_convention_definition"] == "yes"
    assert genocide["url"] == "https://www.planalto.gov.br/ccivil_03/leis/l2889.htm"
    assert (penalty["type"], penalty["years"], penalty["applies_to_genocide"]) == (
        "years",
        40,
        "yes",
    )


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site") / "site"
    assert build_site.main(["--out", str(out), "--execute"]) == 0
    return out


def section(html: str, ident: str) -> str:
    pattern = rf'<section[^>]*(?: id| aria-labelledby)="{ident}".*?</section>'
    return re.search(pattern, html, re.S).group()


@pytest.mark.parametrize("locale", ("en", "pt-BR"))
def test_the_record_of_brazil_shows_the_three_blocks_with_their_source(site, countries, locale):
    path = site / build_site.route(locale) / "countries" / "BRA" / "index.html"
    html = path.read_text(encoding="utf-8")
    for name in BLOCKS:
        part = section(html, name)
        block = countries["BRA"][name]
        state = "stamped" if block["checked_by"] == "human" else "draft"
        assert f'data-state="{state}"' in part, name
        assert f'<a href="{build_site.esc(block["url"])}">' in part, name
        assert "<code>planalto</code>" in part, name
    assert "Decreto-Lei nº 2.848" in section(html, "penal_code")
    assert "Lei nº 2.889" in section(html, "domestic_genocide")
    assert "<dd>40</dd>" in section(html, "max_penalty")
