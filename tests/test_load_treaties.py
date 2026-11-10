"""The Tabelião's load (scripts/load_treaties.py) and the treaty blocks in data/.

The load is pure (`plan`): tables in, records out. The fixtures parse as the files
downloaded on 2026-11-10; the load tests run on the records as those fixtures read them
(`countries`), not on the repository, which the monthly reading (countries.yml) may have
moved on since. The real-data tests check that the repository agrees with the fixtures
except in the blocks read later or checked by a person, that every block is stamped or
empty with a reason, and that the counts read from the fixtures agree with the Status
block.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

import load_treaties as lt  # noqa: E402
import vocabularies as voc  # noqa: E402

from astraea.sources.listing import parse_untc_treaty  # noqa: E402

READ_ON = "2026-11-10"
BLOCKS = ("genocide_convention", "rome_statute")
FIXTURES = ROOT / "tests" / "fixtures" / "untc"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tables():
    return {t.block: parse_untc_treaty((FIXTURES / t.file).read_bytes()) for t in lt.TREATIES}


@pytest.fixture(scope="module")
def repository():
    return load("countries.json")


@pytest.fixture(scope="module")
def countries(repository, tables, names):
    """The records as the fixtures read them: the repository with both blocks read again."""
    return lt.plan(bare(repository), tables, names, READ_ON)[0]


@pytest.fixture(scope="module")
def names():
    return load("untc-names.json")


def bare(countries):
    """The records without the two treaty blocks, as before the first load."""
    out = copy.deepcopy(countries)
    for c in out:
        c.pop("genocide_convention", None)
        c.pop("rome_statute", None)
    return out


def by_id(records):
    return {c["id"]: c for c in records}


def later(block) -> bool:
    """A block a later reading or a person wrote: it may differ from the fixtures."""
    return isinstance(block, dict) and (
        block.get("checked_by") == "human" or (block.get("read_on") or "") > READ_ON
    )


# ------------------------------------------------------------------ the load


def test_the_fixtures_read_twice_change_nothing(tables, countries, names):
    new, report = lt.plan(countries, tables, names, READ_ON)
    assert report == []
    assert new == countries
    first, report = lt.plan(bare(countries), tables, names, READ_ON)
    assert first == countries
    assert len(report) == 2 * 197


def test_the_repository_agrees_with_the_fixtures_but_for_later_readings(repository, countries):
    assert [c["id"] for c in repository] == [c["id"] for c in countries]
    for old, new in zip(repository, countries, strict=True):
        assert {k: v for k, v in old.items() if k not in BLOCKS} == {
            k: v for k, v in new.items() if k not in BLOCKS
        }, old["id"]
        for name in BLOCKS:
            if old[name] != new[name]:
                assert later(old[name]), (old["id"], name)


def test_a_name_without_a_map_stops_the_load(tables, countries, names):
    shrunk = {**names, "names": [n for n in names["names"] if n["untc"] != "Viet Nam"]}
    with pytest.raises(lt.LoadError, match="'Viet Nam' is not a name of countries.json"):
        lt.plan(countries, tables, shrunk, READ_ON)


def test_the_map_cannot_point_outside_the_197(tables, countries, names):
    broken = copy.deepcopy(names)
    broken["names"][0]["id"] = "ZZZ"
    with pytest.raises(lt.LoadError, match="not a record"):
        lt.plan(countries, tables, broken, READ_ON)
    broken = copy.deepcopy(names)
    entry = next(n for n in broken["names"] if n["id"] is None)
    del entry["reason"]
    with pytest.raises(lt.LoadError, match="without a reason"):
        lt.plan(countries, tables, broken, READ_ON)


def test_a_block_checked_by_a_person_is_left_alone(tables, countries, names):
    records = copy.deepcopy(countries)
    brazil = by_id(records)["BRA"]
    brazil["rome_statute"] = {**brazil["rome_statute"], "objections": "yes", "checked_by": "human"}
    new, report = lt.plan(records, tables, names, READ_ON)
    assert report == ["left alone (checked by a person): BRA.rome_statute"]
    assert by_id(new)["BRA"]["rome_statute"]["objections"] == "yes"


def test_same_values_keep_the_old_reading_date(tables, countries, names):
    new, report = lt.plan(countries, tables, names, "2026-12-01")
    assert report == [] and new == countries


def test_a_change_is_reported_field_by_field(tables, countries, names):
    records = copy.deepcopy(countries)
    by_id(records)["HUN"]["rome_statute"]["participation"] = "withdrawn"
    new, report = lt.plan(records, tables, names, "2026-12-01")
    assert report == ["changed: HUN.rome_statute: participation: 'withdrawn' -> 'party'"]
    assert by_id(new)["HUN"]["rome_statute"]["read_on"] == "2026-12-01"


def test_simulation_writes_nothing(tmp_path, capsys, countries):
    data = tmp_path / "data"
    data.mkdir()
    (data / "untc-names.json").write_bytes((DATA / "untc-names.json").read_bytes())
    (data / "countries.json").write_text(lt.dumps(bare(countries)), encoding="utf-8", newline="\n")
    before = (data / "countries.json").read_bytes()
    args = ["--xml-dir", str(FIXTURES), "--read-on", READ_ON, "--data", str(data)]
    assert lt.main(args) == 0
    assert (data / "countries.json").read_bytes() == before
    assert "would write" in capsys.readouterr().out
    assert lt.main([*args, "--execute"]) == 0
    assert (data / "countries.json").read_text(encoding="utf-8") == lt.dumps(countries)
    assert lt.main(["--xml-dir", str(FIXTURES), "--data", str(data)]) == 2  # no --read-on


def test_a_failed_reading_writes_nothing(tmp_path, capsys):
    data = tmp_path / "data"
    data.mkdir()
    for name in ("countries.json", "untc-names.json"):
        (data / name).write_bytes((DATA / name).read_bytes())
    xml = tmp_path / "xml"
    xml.mkdir()
    (xml / "IV-1.en.xml").write_bytes((FIXTURES / "IV-1.en.xml").read_bytes()[:5000])
    (xml / "XVIII-10.en.xml").write_bytes((FIXTURES / "XVIII-10.en.xml").read_bytes())
    args = ["--xml-dir", str(xml), "--read-on", READ_ON, "--data", str(data), "--execute"]
    assert lt.main(args) == 1
    assert "nothing was written" in capsys.readouterr().out
    assert (data / "countries.json").read_bytes() == (DATA / "countries.json").read_bytes()


# ------------------------------------------------------------------ the real data


def test_every_record_has_both_blocks_stamped_or_empty_with_a_reason(repository):
    """In the repository as it is: a later reading moves read_on; a person may stamp."""
    for c in repository:
        for name in BLOCKS:
            block = c[name]
            if "participation" not in block:
                assert set(block) == {"reason"} and block["reason"], (c["id"], name)
                continue
            assert all(block.get(k) for k in voc.STAMP_FIELDS), (c["id"], name)
            assert block["read_on"] >= READ_ON, (c["id"], name)
            if block["checked_by"] == "human":
                continue  # a person's block: its own source and url (rule 3)
            assert {k: block[k] for k in voc.STAMP_FIELDS} == {
                "url": block["url"],
                "source": "untc",
                "read_on": block["read_on"],
                "confidence": "A",
                "checked_by": "robot",
            }, (c["id"], name)
            assert block["url"].startswith(lt.BASE), (c["id"], name)


def test_the_counts_agree_with_the_status_block(countries, tables):
    def count(name, value):
        return sum(1 for c in countries if c[name].get("participation") == value)

    assert tables["genocide_convention"].meta["parties"] == 154
    assert count("genocide_convention", "party") == 154
    # 125 parties to the Rome Statute: 124 among the 197, plus the Cook Islands
    assert tables["rome_statute"].meta["parties"] == 125
    assert count("rome_statute", "party") == 124
    assert count("rome_statute", "withdrawn") == 2
    signed = sum(1 for c in countries if c["genocide_convention"].get("signature"))
    assert signed == tables["genocide_convention"].meta["signatories"] == 41


def test_the_four_records_outside_the_member_list(countries):
    records = by_id(countries)
    for ident in ("TWN", "XKX"):
        assert set(records[ident]["genocide_convention"]) == {"reason"}
        assert set(records[ident]["rome_statute"]) == {"reason"}
    assert records["PSE"]["genocide_convention"]["bound_since"] == "2014-04-02"
    assert records["PSE"]["rome_statute"]["bound_since"] == "2015-01-02"
    assert records["PSE"]["rome_statute"]["consent_type"] == "accession"
    assert records["VAT"]["genocide_convention"]["participation"] == "none"
    assert records["VAT"]["rome_statute"]["participation"] == "none"


def test_known_values(countries):
    records = by_id(countries)
    brazil = records["BRA"]
    assert brazil["genocide_convention"]["signature"] == "1948-12-11"
    assert brazil["genocide_convention"]["bound_since"] == "1952-04-15"
    assert brazil["rome_statute"]["bound_since"] == "2002-06-20"
    assert records["USA"]["genocide_convention"]["reservations_article_ix"] == "yes"
    assert records["USA"]["rome_statute"]["participation"] == "signatory"
    assert records["CHN"]["genocide_convention"]["reservations_article_ix"] == "yes"
    assert records["MMR"]["genocide_convention"]["reservations"] == "yes"
    assert records["MMR"]["genocide_convention"]["reservations_article_ix"] == "no"
    assert records["BDI"]["rome_statute"]["participation"] == "withdrawn"
    assert records["BDI"]["rome_statute"]["withdrawal"] == "2017-10-27"
    assert records["PHL"]["rome_statute"]["withdrawal"] == "2019-03-17"
    assert records["NER"]["rome_statute"]["participation"] == "party"
    assert records["NER"]["rome_statute"]["withdrawal"] == "2027-06-18"
    assert records["HUN"]["rome_statute"]["withdrawal"] is None  # rescinded on 2026-05-29
    assert records["NLD"]["rome_statute"]["consent_type"] == "acceptance"
    assert records["DOM"]["genocide_convention"]["participation"] == "signatory"


def test_the_name_map(names, countries):
    ids = {c["id"] for c in countries}
    english = {c["name"]["en"] for c in countries}
    assert names["source"] == "unsd-m49"
    seen = set()
    for entry in names["names"]:
        assert entry["untc"] not in seen and entry["untc"] not in english, entry
        seen.add(entry["untc"])
        assert entry["m49"], entry
        assert entry["id"] in ids or (entry["id"] is None and entry["reason"]), entry
    assert {e["id"] for e in names["absent"]} == {"TWN", "XKX"}
    outside = [e["untc"] for e in names["names"] if e["id"] is None]
    assert outside == ["Cook Islands"]
    assert any(e["untc"] == "State of Palestine" and e["id"] == "PSE" for e in names["names"])


def test_every_map_entry_is_used(tables, names):
    used = {r.key for t in tables.values() for r in t.rows}
    assert {e["untc"] for e in names["names"]} <= used
