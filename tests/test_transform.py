"""scripts/transform.py: the eleven checks of docs/03-modelo-de-dados.md, the two modes
and the derived files.

Each check is tested against a small data directory built in tmp_path, valid as it is
born; a test breaks one thing and says which check must catch it. The last tests run the
validator over the real data/ of the repository.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

import transform  # noqa: E402
import vocabularies  # noqa: E402

STAMP = {
    "url": "https://official.example/law",
    "source": "official",
    "read_on": "2026-11-01",
    "confidence": "A",
    "checked_by": "human",
}
SURFACE = {"level": "surface", "trigger": None, "since": None, "where": None}


def source(ident: str, state: str) -> dict:
    return {
        "id": ident,
        "name": f"Source {ident}",
        "url": f"https://{ident}.example",
        "function": 1,
        "confidence": "A",
        "license": "open",
        "terms_url": None,
        "robots_checked_on": "2026-11-01",
        "api": "no",
        "rate_limit_per_minute": None,
        "languages": ["en"],
        "sentinel": None,
        "state_media": False,
        "no_text_by_policy": False,
        "state": state,
        "reason": "Test source.",
    }


def status(code: str = "allegation", **changes) -> dict:
    base = {
        "code": code,
        "by": "A State",
        "date": "1990-05-01",
        "url": "https://official.example/act",
        "confidence": "A",
        "checked_by": "human",
    }
    return {**base, **changes}


def write(root: Path, name: str, content) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def read(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


def edit(root: Path, name: str, change) -> None:
    content = read(root, name)
    write(root, name, change(content) or content)


@pytest.fixture
def data(tmp_path) -> Path:
    """A data directory that passes --strict: two countries, one situation, two sources."""
    root = tmp_path / "data"
    shutil.copytree(DATA / "i18n", root / "i18n")
    write(
        root,
        "countries.json",
        [
            {
                "id": "AAA",
                "name": {"en": "Aland", "pt-BR": "Alanda"},
                "un_status": "member",
                "un_member_since": "1945-10-24",
                "situations": ["sample-1990"],
            },
            {
                "id": "BBB",
                "name": {"en": "Beland", "pt-BR": "Belanda"},
                "un_status": "observer",
                "un_member_since": None,
                "situations": [],
            },
        ],
    )
    write(
        root,
        "situations.json",
        [
            {
                "id": "sample-1990",
                "name": {"en": "Sample (1990)", "pt-BR": "Exemplo (1990)"},
                "countries": [{"id": "AAA", "role": "territory"}],
                "period": {"start": "1990", "end": None, "approximate": True},
                "statuses": [status()],
                "terms": [{"lang": "en", "forms": ["Sample"], "exclusions": []}],
                "promotion": dict(SURFACE),
            }
        ],
    )
    write(root, "sources.json", [source("official", "active"), source("parked", "suspended")])
    write(root, "retired-ids.json", [])
    write(
        root,
        "verification.json",
        [
            {
                "entity": "countries",
                "records": ["AAA", "BBB"],
                "fields": ["name", "un_status", "un_member_since"],
                **STAMP,
                "result": "confirmed",
                "method": "Read by hand.",
            }
        ],
    )
    return root


def problems(root: Path) -> list[transform.Problem]:
    return transform.validate(transform.load(root))


def checks(root: Path) -> set[int]:
    return {p.check for p in problems(root)}


def country(root: Path, **fields) -> None:
    """Adds or replaces fields of the first country."""
    edit(root, "countries.json", lambda countries: countries[0].update(fields))


def situation(root: Path, **fields) -> None:
    edit(root, "situations.json", lambda situations: situations[0].update(fields))


def run(root: Path, *options: str) -> int:
    return transform.main([*options, "--data", str(root)])


def test_the_sample_data_passes_strict(data):
    assert problems(data) == []
    assert run(data, "--strict") == 0


# ------------------------------------------------------------------ check 1


@pytest.mark.parametrize("ident", ["aaa", "AAAA", "A1A", None])
def test_check_1_id_outside_the_pattern(data, ident):
    country(data, id=ident)
    assert 1 in checks(data)


def test_check_1_situation_id_is_an_ascii_slug(data):
    situation(data, id="Sample_1990")
    assert 1 in checks(data)


def test_check_1_repeated_id(data):
    edit(data, "countries.json", lambda countries: countries.append(dict(countries[1])))
    assert [p.message for p in problems(data) if p.check == 1] == ["repeated id"]


@pytest.mark.parametrize("retired", ["BBB", {"entity": "countries", "id": "BBB"}])
def test_check_1_retired_id_never_comes_back(data, retired):
    write(data, "retired-ids.json", [retired])
    found = [p for p in problems(data) if p.check == 1]
    assert [p.where for p in found] == ["countries[BBB]"]


def test_check_1_retired_id_of_another_entity_is_free(data):
    write(data, "retired-ids.json", [{"entity": "situations", "id": "BBB"}])
    assert problems(data) == []


# ------------------------------------------------------------------ check 2


def test_check_2_value_outside_the_vocabulary(data):
    country(data, un_status="republic")
    found = [p for p in problems(data) if p.check == 2]
    assert [p.where for p in found] == ["countries[AAA].un_status"]


def test_check_2_reaches_nested_fields_and_lists(data):
    situation(
        data,
        countries=[{"id": "AAA", "role": "victim"}],
        statuses=[status("massacre")],
        terms=[{"lang": "xx", "forms": ["Sample"], "exclusions": []}],
    )
    wheres = {p.where for p in problems(data) if p.check == 2}
    assert wheres == {
        "situations[sample-1990].countries.role",
        "situations[sample-1990].statuses.code",
        "situations[sample-1990].terms.lang",
    }


def test_check_2_author_is_human_or_a_named_model(data):
    text = {"en": {"text": "Ours.", "author": "robot"}}
    situation(data, description=text)
    assert 2 in checks(data)
    text["en"]["author"] = "model:claude-haiku-5-5"
    situation(data, description=text)
    assert problems(data) == []


# ------------------------------------------------------------------ check 3

# The block of the Brazil example of docs/03: what is expected, not yet read by anyone.
UNSTAMPED_BLOCK = {
    "signature": "1948-12-11",
    "bound_since": "1952-04-15",
    "consent_type": "ratification",
    "reservations": "no",
    "reservations_note": None,
    "url": "https://official.example/treaty",
    "source": "official",
    "read_on": None,
    "confidence": "A",
    "checked_by": None,
}


def test_check_3_strict_refuses_a_record_without_stamp_and_draft_accepts_it(data, capsys):
    country(data, genocide_convention=UNSTAMPED_BLOCK)
    found = problems(data)
    assert [(p.check, p.where) for p in found] == [(3, "countries[AAA].genocide_convention")]
    assert "read_on, checked_by" in found[0].message

    assert run(data, "--strict") == 1
    assert "FAIL check 3" in capsys.readouterr().out
    assert run(data, "--draft") == 0
    assert "1 fields in draft" in capsys.readouterr().out


def test_check_3_a_stamped_block_passes(data):
    country(data, genocide_convention={**UNSTAMPED_BLOCK, **STAMP})
    assert problems(data) == []


def test_treaty_dates_are_always_full_dates(data):
    rome = {"participation": "party", "signature": "2000-02-07", "bound_since": "2002-06", **STAMP}
    country(data, rome_statute=rome)
    found = [p for p in problems(data) if p.check == transform.STRUCTURE]
    assert [p.where for p in found] == ["countries[AAA].rome_statute.bound_since"]
    country(data, rome_statute={**rome, "bound_since": "2002-06-20", "withdrawal": "2027-06-18"})
    assert problems(data) == []


def test_participation_is_a_closed_vocabulary(data):
    country(data, genocide_convention={"participation": "observer", **STAMP})
    assert [p.check for p in problems(data)] == [2]


def test_check_3_a_block_that_asserts_nothing_needs_no_stamp(data):
    country(data, penal_code={"exists": None, "reason": "not read yet"})
    assert problems(data) == []


def test_check_3_scalar_fields_are_stamped_by_a_verification_line(data):
    edit(data, "verification.json", lambda lines: lines[0].update(records=["AAA"]))
    wheres = [p.where for p in problems(data) if p.check == 3]
    # un_member_since of BBB is null: nothing is asserted, nothing to stamp
    assert wheres == ["countries[BBB].name", "countries[BBB].un_status"]


@pytest.mark.parametrize("change", [{"checked_by": None}, {"result": "unconfirmed"}])
def test_check_3_a_line_that_did_not_confirm_stamps_nothing(data, change):
    edit(data, "verification.json", lambda lines: lines[0].update(change))
    wheres = {p.where for p in problems(data) if p.check == 3}
    assert "countries[AAA].un_status" in wheres


def test_check_3_status_without_checked_by(data):
    situation(data, statuses=[status(checked_by=None)])
    assert [(p.check, p.where) for p in problems(data)] == [
        (3, "situations[sample-1990].statuses[0]")
    ]
    assert run(data, "--strict") == 1
    assert run(data, "--draft") == 0


# ------------------------------------------------------------------ check 4


@pytest.mark.parametrize(("name", "excerpt"), [("nowhere", "not in"), ("parked", "suspended")])
def test_check_4_source_must_exist_and_be_active(data, name, excerpt):
    country(data, genocide_convention={**UNSTAMPED_BLOCK, **STAMP, "source": name})
    found = [p for p in problems(data) if p.check == 4]
    assert len(found) == 1 and excerpt in found[0].message


def test_check_4_also_for_the_verification_trail(data):
    edit(data, "verification.json", lambda lines: lines[0].update(source="parked"))
    assert [p.where for p in problems(data) if p.check == 4] == ["verification[0]"]


# ------------------------------------------------------------------ check 5


@pytest.mark.parametrize("missing", ["by", "date", "url", "confidence"])
def test_check_5_status_without_body_date_address_or_confidence(data, missing):
    situation(data, statuses=[status(**{missing: None})])
    assert 5 in checks(data)
    assert run(data, "--draft") == 1  # --draft does not relax it


def test_check_5_merits_decision_without_outcome(data):
    situation(data, statuses=[status("merits_decision")])
    assert [p.message for p in problems(data) if p.check == 5] == [
        "merits_decision without outcome"
    ]
    situation(data, statuses=[status("merits_decision", outcome="partial")])
    assert problems(data) == []


def test_check_5_date_may_be_partial_but_must_be_a_date(data):
    situation(data, statuses=[status(date="2005-06")])
    assert problems(data) == []
    situation(data, statuses=[status(date="June 2005")])
    assert 5 in checks(data)
    situation(data, statuses=[status(date="2005-13")])
    assert 5 in checks(data)


# ------------------------------------------------------------------ check 6


@pytest.mark.parametrize("code", vocabularies.HUMAN_ONLY_STATUSES)
def test_check_6_court_statuses_are_recorded_by_a_person(data, code, capsys):
    extra = {"outcome": "recognized"} if code == "merits_decision" else {}
    situation(data, statuses=[status(code, checked_by="robot", **extra)])
    assert [p.check for p in problems(data)] == [6]
    assert run(data, "--strict") == 1
    assert run(data, "--draft") == 0
    capsys.readouterr()


def test_check_6_does_not_reach_the_statuses_a_robot_may_record(data):
    situation(data, statuses=[status("investigation", checked_by="robot")])
    assert problems(data) == []


# ------------------------------------------------------------------ check 7


def test_check_7_country_points_to_a_situation_that_does_not_exist(data):
    country(data, situations=["sample-1990", "ghost"])
    found = [p for p in problems(data) if p.check == 7]
    assert len(found) == 1 and "'ghost' does not exist" in found[0].message


def test_check_7_country_in_a_situation_without_role(data):
    situation(data, countries=[{"id": "AAA"}])
    found = [p for p in problems(data) if p.check == 7]
    assert len(found) == 1 and "has no role" in found[0].message


def test_check_7_situation_points_to_a_country_that_does_not_exist(data):
    situation(data, countries=[{"id": "AAA", "role": "territory"}, {"id": "ZZZ", "role": "forum"}])
    found = [p for p in problems(data) if p.check == 7]
    assert len(found) == 1 and "'ZZZ' does not exist" in found[0].message


def test_check_7_the_link_is_kept_on_both_sides(data):
    country(data, situations=[])
    assert [p.where for p in problems(data) if p.check == 7] == ["countries[AAA].situations"]

    country(data, situations=["sample-1990"])
    edit(data, "countries.json", lambda countries: countries[1].update(situations=["sample-1990"]))
    assert [p.where for p in problems(data) if p.check == 7] == ["countries[BBB].situations"]


# ------------------------------------------------------------------ check 8


def test_check_8_a_description_has_at_most_600_characters(data):
    situation(data, description={"en": {"text": "a" * 600, "author": "human"}})
    assert problems(data) == []
    situation(data, description={"en": {"text": "a" * 601, "author": "human"}})
    assert [p.check for p in problems(data)] == [8]


def test_check_8_does_not_limit_a_note(data):
    note = {"en": {"text": "a" * 900, "author": "human"}}
    country(data, genocide_convention={**UNSTAMPED_BLOCK, **STAMP, "note": note})
    assert problems(data) == []


# ------------------------------------------------------------------ check 9


def test_check_9_text_of_ours_without_author(data):
    situation(data, description={"en": {"text": "Ours."}})
    assert [p.check for p in problems(data)] == [9]


def test_check_9_locale_outside_data_i18n(data):
    situation(data, description={"fr": {"text": "Le nôtre.", "author": "human"}})
    assert [p.check for p in problems(data)] == [9]
    situation(data, description=None, name={"en": "Sample", "fr": "Exemple"})
    assert [p.check for p in problems(data)] == [9]


def test_check_9_reaches_the_note_inside_a_block(data):
    note = {"pt-BR": {"text": "Nota."}}
    country(data, genocide_convention={**UNSTAMPED_BLOCK, **STAMP, "note": note})
    assert [(p.check, p.where) for p in problems(data)] == [
        (9, "countries[AAA].genocide_convention.note.pt-BR")
    ]


# ------------------------------------------------------------------ check 10


def test_check_10_penalty_in_years_without_the_years(data):
    country(data, max_penalty={"type": "years", "years": None, **STAMP})
    assert [p.check for p in problems(data)] == [10]
    country(data, max_penalty={"type": "years", "years": 40, **STAMP})
    assert problems(data) == []


def test_check_10_retentionist_with_a_lower_maximum_needs_a_note(data):
    country(
        data,
        max_penalty={"type": "life", "years": None, **STAMP},
        death_penalty={"status": "retentionist", **STAMP},
    )
    assert [(p.check, p.where) for p in problems(data)] == [(10, "countries[AAA].death_penalty")]

    note = {"en": {"text": "Death only in wartime.", "author": "human"}}
    country(data, death_penalty={"status": "retentionist", "note": note, **STAMP})
    assert problems(data) == []


def test_check_10_waits_for_the_maximum_penalty_to_be_loaded(data):
    country(data, death_penalty={"status": "retentionist", **STAMP})
    assert problems(data) == []


# ------------------------------------------------------------------ check 11


def test_check_11_refuses_a_value_without_label_in_pt_br(data, capsys):
    def drop(labels):
        del labels["values"]["un_status.observer"]

    edit(data, "i18n/pt-BR.json", drop)
    found = problems(data)
    assert {p.check for p in found} == {11}
    assert {p.where for p in found} == {"i18n/pt-BR.json", "countries[BBB].un_status"}
    assert all("un_status.observer" in p.message for p in found)
    assert run(data, "--draft") == 1  # --draft does not relax it
    capsys.readouterr()


def test_check_11_refuses_a_field_without_label(data):
    country(data, capital="Alandia")
    found = problems(data)
    assert [(p.check, p.where) for p in found] == [(11, "countries[AAA].capital")]
    assert "raw key" in found[0].message


def test_check_11_refuses_an_empty_label(data):
    edit(data, "i18n/en.json", lambda labels: labels["fields"].update(period=" "))
    assert [(p.check, p.where) for p in problems(data)] == [(11, "i18n/en.json")]


def test_a_labelled_field_of_another_entity_is_still_refused(data):
    country(data, court="icj")
    assert [(p.check, p.where) for p in problems(data)] == [(0, "countries[AAA].court")]


# ------------------------------------------------------------------ modes and files


def test_draft_relaxes_only_checks_3_and_6(data):
    assert transform.RELAXED_IN_DRAFT == (3, 6)
    for check in transform.CHECKS:
        assert transform.Problem(check, "x", "y").relaxable == (check in (3, 6))


def test_missing_files_fail_instead_of_passing_empty(tmp_path, capsys):
    (tmp_path / "data").mkdir()
    assert run(tmp_path / "data", "--draft") == 1
    assert "countries.json: file not found" in capsys.readouterr().out
    assert run(tmp_path / "nowhere") == 2


def test_simulation_writes_nothing_and_execute_writes(data, capsys):
    output = data.parent / "static" / "data"
    assert run(data) == 0
    assert not output.exists()
    assert "simulation" in capsys.readouterr().out

    assert run(data, "--execute") == 0
    assert sorted(p.relative_to(output).as_posix() for p in output.rglob("*.json")) == [
        "countries.json",
        "i18n/en.json",
        "i18n/pt-BR.json",
        "quality.json",
        "situations.json",
    ]
    assert b"\r" not in (output / "countries.json").read_bytes()
    assert read(output, "i18n/en.json") == read(data, "i18n/en.json")


def test_nothing_is_written_when_the_data_fails(data, capsys):
    country(data, un_status="republic")
    assert run(data, "--execute") == 1
    assert not (data.parent / "static").exists()
    capsys.readouterr()


def test_execute_never_deletes(data, capsys):
    output = data.parent / "static" / "data"
    output.mkdir(parents=True)
    (output / "old.json").write_text("{}", encoding="utf-8")
    assert run(data, "--execute") == 0
    assert (output / "old.json").exists()
    assert "left alone" in capsys.readouterr().out


def test_check_says_when_the_derived_files_are_out_of_date(data, capsys):
    assert run(data, "--check") == 1  # nothing generated yet
    assert run(data, "--execute") == 0
    assert run(data, "--check") == 0
    country(data, name={"en": "Aland Islands", "pt-BR": "Alanda"})
    assert run(data, "--check") == 1
    assert "out of date (changed)" in capsys.readouterr().out


def test_the_same_files_in_both_modes(data):
    out = data.parent / "static" / "data"
    assert run(data, "--strict", "--execute") == 0
    strict = {p.name: p.read_bytes() for p in out.rglob("*.json")}
    assert run(data, "--draft", "--execute") == 0
    assert {p.name: p.read_bytes() for p in out.rglob("*.json")} == strict


# ------------------------------------------------------------------ derived content


def derived(root: Path) -> dict:
    ds = transform.load(root)
    return transform.derive(ds, transform.validate(ds))


def test_country_gets_provenance_completeness_and_date(data):
    country(data, genocide_convention=UNSTAMPED_BLOCK)
    aaa, bbb = derived(data)["countries.json"]
    assert aaa["provenance"]["un_status"] == STAMP
    assert aaa["completeness"]["fields"]["un_status"] == "stamped"
    assert aaa["completeness"]["fields"]["genocide_convention"] == "draft"
    assert aaa["completeness"]["fields"]["penal_code"] == "empty"
    assert (aaa["completeness"]["stamped"], aaa["completeness"]["draft"]) == (1, 1)
    assert aaa["completeness"]["empty"] == 5
    assert aaa["updated_at"] == bbb["updated_at"] == "2026-11-01"


def test_highest_status_is_the_highest_rank_at_its_first_date(data):
    situation(
        data,
        statuses=[
            status("allegation", date="1990-05-01"),
            status("provisional_measures", by="A Court", date="1993-09-13"),
            status("provisional_measures", by="A Court", date="1993-04-08"),
            status("closed", by="Another Court", date="2001-01-01"),
        ],
    )
    top = derived(data)["situations.json"][0]["highest_status"]
    assert (top["code"], top["date"]) == ("provisional_measures", "1993-04-08")
    assert top["label"] == {
        "en": "provisional measures — A Court, 8 Apr 1993",
        "pt-BR": "medidas provisórias — A Court, 08/04/1993",
    }


def test_closed_shows_only_when_there_is_nothing_else(data):
    situation(data, statuses=[status("closed", date="2025-05-05")])
    assert derived(data)["situations.json"][0]["highest_status"]["code"] == "closed"
    situation(data, statuses=[status("closed", date="2025-05-05"), status("allegation")])
    assert derived(data)["situations.json"][0]["highest_status"]["code"] == "allegation"


def test_the_label_carries_the_outcome_and_the_precision_of_the_date(data):
    situation(data, statuses=[status("merits_decision", outcome="partial", date="2007-02")])
    label = derived(data)["situations.json"][0]["highest_status"]["label"]
    assert label == {
        "en": "decision on the merits (partial) — A State, Feb 2007",
        "pt-BR": "decisão de mérito (parcial) — A State, 02/2007",
    }
    formats = read(data, "i18n/en.json")["formats"]
    assert transform.format_date("2005", formats) == "2005"


def test_situation_without_status_has_no_label(data):
    situation(data, statuses=[])
    record = derived(data)["situations.json"][0]
    assert record["highest_status"] is None
    assert derived(data)["quality.json"]["situations"]["without_status"] == ["sample-1990"]


def test_no_label_says_genocide_by_itself():
    """AGENTS.md, rule 1: the status label always names what was done and by whom."""
    for locale in vocabularies.LOCALES:
        values = read(DATA, f"i18n/{locale}.json")["values"]
        for code in vocabularies.STATUS_ORDER:
            assert "genoc" not in values[f"statuses.code.{code}"].lower()


def test_quality_counts_the_drafts(data):
    country(data, genocide_convention=UNSTAMPED_BLOCK)
    situation(data, statuses=[status("provisional_measures", checked_by=None)])
    report = derived(data)["quality.json"]
    assert report["drafts"]["fields"] == 2
    assert report["drafts"]["records"] == 2
    assert report["drafts"]["by_check"] == {"3": 2, "6": 1}
    assert report["countries"]["fields"]["genocide_convention"] == {
        "stamped": 0,
        "draft": 1,
        "empty": 1,
    }
    assert report["situations"]["statuses"] == {"total": 1, "stamped": 0, "draft": 1}
    # territory of a situation a court already acts on, without domestic law checked
    assert report["countries"]["priority"] == ["AAA"]
    assert report["as_of"] == "2026-11-01"
    assert report["sources"]["by_state"] == {"active": 1, "suspended": 1}


def test_quality_says_which_robots_checks_expired(data):
    def age(sources):
        sources[1]["robots_checked_on"] = "2026-01-01"

    edit(data, "sources.json", age)
    assert derived(data)["quality.json"]["sources"]["robots_expired"] == ["parked"]


# ------------------------------------------------------------------ the lexicon in the data


def test_a_stale_lexicon_is_refused(data):
    shutil.copytree(DATA / "lexicon" / "fixed", data / "lexicon" / "fixed")
    found = problems(data)
    assert {p.where for p in found} == {
        f"lexicon/{lang}.json" for lang in vocabularies.LEXICON_LANGUAGES
    }
    assert all("is missing" in p.message for p in found)

    import build_lexicon

    assert build_lexicon.main(["--data", str(data), "--execute"]) == 0
    assert problems(data) == []
    situation(data, terms=[{"lang": "en", "forms": ["Sample", "Specimen"], "exclusions": []}])
    assert [(p.where, "out of date" in p.message) for p in problems(data)] == [
        ("lexicon/en.json", True)
    ]


# ------------------------------------------------------------------ the real data


def test_the_real_data_passes_draft_and_strict_stops_only_at_the_expected_drafts():
    found = problems(DATA)
    assert found, "when every draft is stamped, this test and --draft in the battery can go"
    for problem in found:
        assert problem.check in transform.RELAXED_IN_DRAFT, str(problem)
        unstamped_status = problem.where.startswith("situations[") and ".statuses[" in problem.where
        observer_or_non_member = problem.where in {
            f"countries[{c}].un_status" for c in ("PSE", "VAT", "XKX", "TWN")
        }
        # A penal law block of the human load (phase 2, session 4) read and prepared, with
        # url, source, read_on and confidence, waiting only for the owner's checked_by.
        waiting_for_the_owner = (
            problem.check == 3
            and re.fullmatch(
                r"countries\[[A-Z]{3}\]\.(penal_code|domestic_genocide|max_penalty)", problem.where
            )
            and problem.message == "asserted without stamp: missing checked_by"
        )
        assert unstamped_status or observer_or_non_member or waiting_for_the_owner, str(problem)


def test_the_committed_static_data_is_up_to_date(capsys):
    assert transform.main(["--draft", "--check"]) == 0, capsys.readouterr().out
    capsys.readouterr()


def test_the_ten_situations_of_d6_and_their_links():
    situations = read(DATA, "situations.json")
    assert len(situations) == 10
    countries = {c["id"]: c for c in read(DATA, "countries.json")}
    for s in situations:
        assert set(s["name"]) == set(vocabularies.LOCALES)
        assert {t["lang"] for t in s["terms"]} == set(vocabularies.LEXICON_LANGUAGES)
        assert s["promotion"]["level"] == "surface"
        assert "description" not in s  # our texts wait for D4
        for status_ in s["statuses"]:
            assert status_["checked_by"] is None  # only a person stamps a status (rule 3)
        for c in s["countries"]:
            assert s["id"] in countries[c["id"]]["situations"]
