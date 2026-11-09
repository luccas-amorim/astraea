"""The data files of phase 1: countries (D1), sources (docs/02) and the i18n labels.

These checks come before scripts/transform.py; when the validator exists, it takes them
over and this file keeps only what is specific to the initial load.
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

import vocabularies  # noqa: E402


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


# D1 (docs/07-decisoes-pendentes.md): the 193 UN Member States, read from
# https://www.un.org/en/about-us/member-states on 2026-11-09, as ISO 3166-1 alpha-3.
MEMBERS = frozenset(
    """
    AFG ALB DZA AND AGO ATG ARG ARM AUS AUT AZE BHS BHR BGD BRB BLR BEL BLZ BEN BTN BOL BIH
    BWA BRA BRN BGR BFA BDI CPV KHM CMR CAN CAF TCD CHL CHN COL COM COG CRI CIV HRV CUB CYP
    CZE PRK COD DNK DJI DMA DOM ECU EGY SLV GNQ ERI EST SWZ ETH FJI FIN FRA GAB GMB GEO DEU
    GHA GRC GRD GTM GIN GNB GUY HTI HND HUN ISL IND IDN IRN IRQ IRL ISR ITA JAM JPN JOR KAZ
    KEN KIR KWT KGZ LAO LVA LBN LSO LBR LBY LIE LTU LUX MDG MWI MYS MDV MLI MLT MHL MRT MUS
    MEX FSM MCO MNG MNE MAR MOZ MMR NAM NRU NPL NLD NZL NIC NER NGA MKD NOR OMN PAK PLW PAN
    PNG PRY PER PHL POL PRT QAT KOR MDA ROU RUS RWA KNA LCA VCT WSM SMR STP SAU SEN SRB SYC
    SLE SGP SVK SVN SLB SOM ZAF SSD ESP LKA SDN SUR SWE CHE SYR TJK THA TLS TGO TON TTO TUN
    TUR TKM TUV UGA UKR ARE GBR TZA USA URY UZB VUT VEN VNM YEM ZMB ZWE
    """.split()
)
OBSERVERS = frozenset({"PSE", "VAT"})
NON_MEMBERS = frozenset({"XKX", "TWN"})
COUNTRY_KEYS = {"id", "name", "un_status", "un_member_since"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@pytest.fixture(scope="module")
def countries() -> list[dict]:
    return load("countries.json")


@pytest.fixture(scope="module")
def sources() -> list[dict]:
    return load("sources.json")


@pytest.fixture(scope="module", params=vocabularies.LOCALES)
def labels(request) -> dict:
    return load(f"i18n/{request.param}.json")


def test_the_d1_universe_has_197_distinct_alpha3_ids(countries):
    ids = [c["id"] for c in countries]
    assert len(MEMBERS) == 193
    assert len(ids) == 197
    assert len(set(ids)) == 197, "repeated id"
    assert all(re.fullmatch(r"[A-Z]{3}", i) for i in ids)
    assert set(ids) == MEMBERS | OBSERVERS | NON_MEMBERS
    assert ids == sorted(ids)


def test_un_status_and_admission_date_follow_d1(countries):
    for c in countries:
        if c["id"] in MEMBERS:
            assert c["un_status"] == "member", c["id"]
            assert DATE.match(c["un_member_since"]), c["id"]
            assert "1945-10-24" <= c["un_member_since"] <= "2026-11-09", c["id"]
        else:
            expected = "observer" if c["id"] in OBSERVERS else "non_member"
            assert c["un_status"] == expected, c["id"]
            assert c["un_member_since"] is None, c["id"]


def test_countries_carry_only_the_fields_of_this_session(countries):
    # No penal law or treaty field before phase 2: absent, not null.
    for c in countries:
        assert set(c) == COUNTRY_KEYS, c["id"]
        assert set(c["name"]) == set(vocabularies.LOCALES), c["id"]
        assert all(isinstance(n, str) and n.strip() == n and n for n in c["name"].values())


def test_no_retired_id_is_in_use(countries, sources):
    retired = load("retired-ids.json")
    assert isinstance(retired, list)
    in_use = {c["id"] for c in countries} | {s["id"] for s in sources}
    assert not in_use & {r["id"] if isinstance(r, dict) else r for r in retired}


def test_sources_are_unique_and_inside_the_vocabularies(sources):
    ids = [s["id"] for s in sources]
    assert len(ids) == len(set(ids))
    fields = set(vocabularies.SOURCE_FIELDS) | {
        "id",
        "name",
        "url",
        "confidence",
        "languages",
        "reason",
    }
    for s in sources:
        assert set(s) == fields, s["id"]
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s["id"]), s["id"]
        assert s["url"].startswith(("http://", "https://")), s["id"]
        for field in ("function", "confidence", "api", "state"):
            assert str(s[field]) in vocabularies.VOCABULARIES[field], (s["id"], field)
        assert s["reason"], s["id"]
        assert s["robots_checked_on"] in (None, "2026-11-06", "2026-11-09"), s["id"]
        assert s["languages"] is None or all(re.fullmatch(r"[a-z]{2}", x) for x in s["languages"])
        assert isinstance(s["state_media"], bool) and isinstance(s["no_text_by_policy"], bool)


def test_every_field_and_value_has_a_label(labels):
    assert set(labels["fields"]) == set(vocabularies.FIELDS)
    assert set(labels["values"]) == set(vocabularies.value_keys())
    assert all(isinstance(t, str) and t for t in labels["fields"].values())
    assert all(isinstance(t, str) and t for t in labels["values"].values())


def test_the_two_locales_label_the_same_keys():
    en, pt = (load(f"i18n/{loc}.json") for loc in vocabularies.LOCALES)
    assert en["locale"] == "en" and pt["locale"] == "pt-BR"
    assert set(en["fields"]) == set(pt["fields"])
    assert set(en["values"]) == set(pt["values"])


def test_the_data_uses_only_labelled_keys_and_values(countries, sources, labels):
    for c in countries:
        assert set(c) <= set(labels["fields"])
        assert f"un_status.{c['un_status']}" in labels["values"]
    for s in sources:
        assert set(s) <= set(labels["fields"])
        for field in ("function", "confidence", "api", "state"):
            assert f"{field}.{s[field]}" in labels["values"]
