"""The death penalty load (scripts/load_death_penalty.py) and the death_penalty blocks.

The load is pure (`plan`): the table in, records out. The four fixtures are the API
responses of 2026-11-10 byte for byte; the load tests run on the records as those fixtures
read them (`countries`), not on the repository, which the monthly reading (countries.yml)
or the Amnesty annex may have moved on since. The real-data tests check that the
repository agrees with the fixtures except in the blocks read later or checked by a
person, that every block is stamped or empty with a reason, and that the counts read from
the fixtures agree with the lists.
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

import load_death_penalty as ld  # noqa: E402
import vocabularies as voc  # noqa: E402

from astraea.sources.listing import CORNELL_CATEGORIES, parse_cornell_dpw_status  # noqa: E402

READ_ON = "2026-11-10"
FIXTURES = ROOT / "tests" / "fixtures" / "cornell"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def parts(**replace: bytes) -> dict[str, bytes]:
    out = {c: (FIXTURES / ld.FILES[c]).read_bytes() for c in CORNELL_CATEGORIES}
    return out | replace


@pytest.fixture(scope="module")
def table():
    return parse_cornell_dpw_status(parts())


@pytest.fixture(scope="module")
def repository():
    return load("countries.json")


@pytest.fixture(scope="module")
def countries(repository, table, names):
    """The records as the fixtures read them: the repository with the block read again."""
    return ld.plan(bare(repository), table, names, READ_ON)[0]


@pytest.fixture(scope="module")
def names():
    return load("cornell-names.json")


def bare(countries):
    out = copy.deepcopy(countries)
    for c in out:
        c.pop("death_penalty", None)
    return out


def by_id(records):
    return {c["id"]: c for c in records}


def later(block) -> bool:
    """A block a later reading or a person wrote: it may differ from the fixtures. A later
    reading that moves a country to "de facto" empties its block, with no date: a reason
    block may differ too."""
    return isinstance(block, dict) and (
        block.get("checked_by") == "human"
        or (block.get("read_on") or "") > READ_ON
        or set(block) == {"reason"}
    )


# ------------------------------------------------------------------ the load


def test_the_repository_agrees_with_the_fixtures_but_for_later_readings(repository, countries):
    assert [c["id"] for c in repository] == [c["id"] for c in countries]
    for old, new in zip(repository, countries, strict=True):
        assert {k: v for k, v in old.items() if k != ld.BLOCK} == {
            k: v for k, v in new.items() if k != ld.BLOCK
        }, old["id"]
        if old[ld.BLOCK] != new[ld.BLOCK]:
            assert later(old[ld.BLOCK]), old["id"]


def test_the_fixtures_read_twice_change_nothing(table, countries, names):
    new, report = ld.plan(countries, table, names, READ_ON)
    assert report == [] and new == countries
    first, report = ld.plan(bare(countries), table, names, READ_ON)
    assert first == countries
    assert len(report) == 197 and all(line.startswith("new: ") for line in report)


def test_a_name_without_a_map_stops_the_load(table, countries, names):
    shrunk = {**names, "names": [n for n in names["names"] if n["cornell"] != "East Timor"]}
    with pytest.raises(ld.LoadError, match="'East Timor' is not a name of countries.json"):
        ld.plan(countries, table, shrunk, READ_ON)


def test_a_name_whose_iso_code_changed_stops_the_load(countries, names):
    moved = json.loads(parts()["Abolitionist"])
    next(i for i in moved if i["displayName"] == "Macedonia")["isoCode"] = "MC"
    changed = parse_cornell_dpw_status(parts(Abolitionist=json.dumps(moved).encode()))
    with pytest.raises(ld.LoadError, match="'Macedonia' now comes with isoCode 'MC'"):
        ld.plan(countries, changed, names, READ_ON)


def test_the_map_cannot_point_outside_the_197(table, countries, names):
    broken = copy.deepcopy(names)
    broken["names"][0]["id"] = "ZZZ"
    with pytest.raises(ld.LoadError, match="not a record"):
        ld.plan(countries, table, broken, READ_ON)
    broken = copy.deepcopy(names)
    del next(n for n in broken["names"] if n["id"] is None)["reason"]
    with pytest.raises(ld.LoadError, match="without a reason"):
        ld.plan(countries, table, broken, READ_ON)


def test_a_block_checked_by_a_person_is_left_alone(table, countries, names):
    records = copy.deepcopy(countries)
    amnesty = {
        "status": "abolitionist_in_practice",
        "url": "https://www.amnesty.org/en/documents/act50/0000/2026/en/",
        "source": "amnesty",
        "read_on": "2026-11-11",
        "confidence": "B",
        "checked_by": "human",
    }
    by_id(records)["JAM"]["death_penalty"] = dict(amnesty)
    by_id(records)["BRA"]["death_penalty"] = amnesty | {"status": "abolitionist_ordinary_crimes"}
    new, report = ld.plan(records, table, names, READ_ON)
    assert report == [
        "left alone (checked by a person): BRA.death_penalty",
        "left alone (checked by a person): JAM.death_penalty; Cornell reads "
        "'Abolitionist de facto', the block says 'abolitionist_in_practice'",
    ]
    assert by_id(new)["JAM"]["death_penalty"] == amnesty


def test_a_stamped_block_no_longer_listed_is_kept(countries, names):
    shrunk = json.loads(parts()["Retentionist"])
    shrunk = [i for i in shrunk if i["displayName"] != "Japan"]
    table = parse_cornell_dpw_status(parts(Retentionist=json.dumps(shrunk).encode()))
    new, report = ld.plan(countries, table, names, "2026-12-01")
    assert report == [
        "kept (no longer in the Cornell lists): JPN.death_penalty = 'retentionist', "
        "read on 2026-11-10"
    ]
    assert new == countries


def test_same_values_keep_the_old_reading_date(table, countries, names):
    new, report = ld.plan(countries, table, names, "2026-12-01")
    assert report == [] and new == countries


def test_a_change_is_reported_field_by_field(countries, names):
    lists = {c: json.loads(b) for c, b in parts().items()}
    japan = next(i for i in lists["Retentionist"] if i["displayName"] == "Japan")
    lists["Retentionist"].remove(japan)
    lists["Abolitionist"].append(japan)
    table = parse_cornell_dpw_status({c: json.dumps(v).encode() for c, v in lists.items()})
    new, report = ld.plan(countries, table, names, "2026-12-01")
    assert report == [
        "changed: JPN.death_penalty: status: 'retentionist' -> 'abolitionist_all_crimes'; "
        f"url: {ld.category_urls()['Retentionist']!r} -> {ld.category_urls()['Abolitionist']!r}"
    ]
    assert by_id(new)["JPN"]["death_penalty"]["read_on"] == "2026-12-01"


def _data_dir(tmp_path, countries):
    data = tmp_path / "data"
    data.mkdir()
    (data / "cornell-names.json").write_bytes((DATA / "cornell-names.json").read_bytes())
    (data / "countries.json").write_text(ld.dumps(countries), encoding="utf-8", newline="\n")
    return data


def test_simulation_writes_nothing(tmp_path, capsys, countries):
    data = _data_dir(tmp_path, bare(countries))
    before = (data / "countries.json").read_bytes()
    args = ["--json-dir", str(FIXTURES), "--read-on", READ_ON, "--data", str(data)]
    assert ld.main(args) == 0
    assert (data / "countries.json").read_bytes() == before
    out = capsys.readouterr().out
    assert "would write: " in out and "(197 blocks)" in out
    assert "sha256 844e476e8ecb78a9b1597417b38fd9f23bed58c53a6edbfa31b0fb16ce738018" in out
    assert ld.main([*args, "--execute"]) == 0
    assert (data / "countries.json").read_text(encoding="utf-8") == ld.dumps(countries)
    assert ld.main(args) == 0
    assert "up to date" in capsys.readouterr().out
    assert ld.main(["--json-dir", str(FIXTURES), "--data", str(data)]) == 2  # no --read-on


def test_a_failed_reading_writes_nothing(tmp_path, capsys):
    data = _data_dir(tmp_path, bare(load("countries.json")))
    before = (data / "countries.json").read_bytes()
    lists = tmp_path / "lists"
    lists.mkdir()
    for c in CORNELL_CATEGORIES:
        (lists / ld.FILES[c]).write_bytes((FIXTURES / ld.FILES[c]).read_bytes())
    (lists / ld.FILES["Retentionist"]).write_bytes(b"<html>Application error</html>")
    args = ["--json-dir", str(lists), "--read-on", READ_ON, "--data", str(data), "--execute"]
    assert ld.main(args) == 1
    assert "nothing was written" in capsys.readouterr().out
    assert (data / "countries.json").read_bytes() == before


# ------------------------------------------------------------------ the correspondence


def test_only_the_categories_that_coincide_are_recorded():
    assert ld.STATUS == {
        "Abolitionist": "abolitionist_all_crimes",
        "Abolitionist For Ordinary Crimes": "abolitionist_ordinary_crimes",
        "Abolitionist de facto": None,
        "Retentionist": "retentionist",
    }
    recorded = {s for s in ld.STATUS.values() if s}
    assert recorded <= set(voc.VOCABULARIES["death_penalty.status"])
    # abolitionist_in_practice is Amnesty's, loaded by hand; the robot never writes it
    assert "abolitionist_in_practice" not in recorded


# ------------------------------------------------------------------ the real data


def test_every_record_has_the_block_stamped_or_empty_with_a_reason(repository):
    """In the repository as it is: a later reading moves read_on; the Amnesty annex is a
    person's block, with its own source (docs/03, "Como a pessoa carrega o anexo")."""
    urls = set(ld.category_urls().values())
    for c in repository:
        block = c["death_penalty"]
        if "status" not in block:
            assert set(block) == {"reason"} and block["reason"], c["id"]
            continue
        assert block["read_on"] >= READ_ON, c["id"]
        if block["checked_by"] == "human":
            assert all(block.get(k) for k in voc.STAMP_FIELDS), c["id"]
            continue
        assert block == {
            "status": block["status"],
            "url": block["url"],
            "source": "cornell-dpw",
            "read_on": block["read_on"],
            "confidence": "B",
            "checked_by": "robot",
        }, c["id"]
        assert block["url"] in urls, c["id"]
        assert "note" not in block  # a text of ours needs an author (D4)


def test_the_counts_agree_with_the_lists(countries, table):
    def count(key):
        return sum(1 for c in countries if c["death_penalty"].get("status") == key)

    assert table.meta["counts"] == {
        "Abolitionist": 95,
        "Abolitionist For Ordinary Crimes": 6,
        "Abolitionist de facto": 45,
        "Retentionist": 35,
    }
    # six of the 95 abolitionist names are outside the 197 (five territories and
    # Northern Cyprus)
    assert count("abolitionist_all_crimes") == 89
    assert count("abolitionist_ordinary_crimes") == 6
    assert count("retentionist") == 35
    reasons = [c["death_penalty"]["reason"] for c in countries if "reason" in c["death_penalty"]]
    assert len(reasons) == 67
    assert reasons.count(ld.UNMAPPED_REASON["Abolitionist de facto"]) == 45
    assert reasons.count(ld.NOT_LISTED) == 22


def test_known_values(countries):
    records = by_id(countries)
    assert records["BRA"]["death_penalty"]["status"] == "abolitionist_ordinary_crimes"
    assert records["USA"]["death_penalty"]["status"] == "retentionist"
    assert records["DEU"]["death_penalty"]["status"] == "abolitionist_all_crimes"
    assert records["XKX"]["death_penalty"]["status"] == "abolitionist_all_crimes"
    assert records["TWN"]["death_penalty"]["status"] == "retentionist"
    assert records["PSE"]["death_penalty"]["status"] == "retentionist"
    assert records["TLS"]["death_penalty"]["status"] == "abolitionist_all_crimes"  # East Timor
    assert records["JAM"]["death_penalty"] == {
        "reason": ld.UNMAPPED_REASON["Abolitionist de facto"]
    }
    for ident in ("AND", "VAT", "GTM", "COG", "SUR"):
        assert records[ident]["death_penalty"] == {"reason": ld.NOT_LISTED}, ident


def test_the_source_is_active_and_its_confidence_agrees(countries):
    source = next(s for s in load("sources.json") if s["id"] == ld.SOURCE)
    assert source["state"] == "active" and source["robots_checked_on"] >= READ_ON
    assert source["confidence"] == ld.CONFIDENCE


def test_the_name_map(names, countries, table):
    ids = {c["id"] for c in countries}
    english = {c["name"]["en"] for c in countries}
    assert names["source"] == "unsd-m49"
    seen = set()
    for entry in names["names"]:
        assert entry["cornell"] not in seen and entry["cornell"] not in english, entry
        seen.add(entry["cornell"])
        assert entry["id"] in ids or (entry["id"] is None and entry["reason"]), entry
        if entry["id"] is not None:
            assert entry["m49"] and entry["iso2"], entry
        assert table.row(entry["cornell"]).cells["iso_code"] == entry["iso2"], entry
    outside = sorted(e["cornell"] for e in names["names"] if e["id"] is None)
    assert outside == [
        "Falkland Islands (Malvinas)",
        "French Southern and Antartic Lands",
        "Greenland",
        "New Caledonia",
        "Northern Cyprus",
        "Puerto rico",
    ]


def test_the_untc_and_cornell_maps_stay_apart():
    untc = load("untc-names.json")
    cornell = load("cornell-names.json")
    assert all("cornell" not in e for e in untc["names"])
    assert all("untc" not in e for e in cornell["names"])
