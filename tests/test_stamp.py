"""The stamp script (scripts/stamp.py): checked_by human, only where the person says.

Runs on a copy of a small countries.json in a temporary folder; the repository data is
never written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import stamp  # noqa: E402

PLANALTO = "https://www.planalto.gov.br/ccivil_03/leis/l2889.htm"


def prepared(**values) -> dict:
    return {
        **values,
        "url": PLANALTO,
        "source": "planalto",
        "read_on": "2026-11-10",
        "confidence": "A",
        "checked_by": None,
    }


def records() -> list[dict]:
    return [
        {
            "id": "BRA",
            "name": {"en": "Brazil", "pt-BR": "Brasil"},
            "penal_code": prepared(exists="yes", title="Código Penal", enacted_year=1940),
            "domestic_genocide": prepared(status="criminalized", provision="art. 1º", year=1956),
            "max_penalty": prepared(type="years", years=40, applies_to_genocide="yes"),
            "death_penalty": {
                "status": "abolitionist_ordinary_crimes",
                "url": "https://cornell-dpw.herokuapp.com/api/x",
                "source": "cornell-dpw",
                "read_on": "2026-11-10",
                "confidence": "B",
                "checked_by": "robot",
            },
        },
        {
            "id": "MMR",
            "name": {"en": "Myanmar", "pt-BR": "Mianmar"},
            "penal_code": {"reason": "Not read on 2026-11-10."},
            "domestic_genocide": {**prepared(status="no"), "url": None},
            "max_penalty": {**prepared(type="death"), "checked_by": "human"},
        },
    ]


@pytest.fixture
def data(tmp_path) -> Path:
    folder = tmp_path / "data"
    folder.mkdir()
    (folder / "countries.json").write_text(
        json.dumps(records(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return folder


def read(data: Path) -> list[dict]:
    return json.loads((data / "countries.json").read_text(encoding="utf-8"))


def run(data: Path, *args: str) -> int:
    return stamp.main(["--data", str(data), *args])


def test_without_field_it_lists_the_ready_blocks_and_writes_nothing(data, capsys):
    before = (data / "countries.json").read_bytes()
    assert run(data) == 0
    out = capsys.readouterr().out
    assert "3 blocks ready to be stamped" in out
    for name in ("BRA.penal_code", "BRA.domestic_genocide", "BRA.max_penalty"):
        assert f"  {name}\n" in out
    # Empty with a reason, missing url, stamped by a person or by the robot: not ready.
    assert "MMR." not in out and "death_penalty" not in out
    assert (data / "countries.json").read_bytes() == before


def test_simulation_says_what_it_would_stamp_and_writes_nothing(data, capsys):
    before = (data / "countries.json").read_bytes()
    args = ("--field", "BRA.penal_code", "--by", "A Person", "--read-on", "2026-11-12")
    assert run(data, *args) == 0
    out = capsys.readouterr().out
    assert "-> checked_by: human, read_on: 2026-11-12" in out
    assert "would stamp: 1 blocks" in out and "simulation: nothing was written" in out
    assert (data / "countries.json").read_bytes() == before


def test_execute_stamps_only_the_named_block_and_changes_no_value(data, capsys):
    args = ("--field", "BRA.max_penalty", "--by", "A Person", "--read-on", "2026-11-12")
    assert run(data, *args, "--execute") == 0
    out = capsys.readouterr().out
    after, before = read(data), records()
    block = after[0]["max_penalty"]
    assert block["checked_by"] == "human" and block["read_on"] == "2026-11-12"
    assert {k: v for k, v in block.items() if k not in ("checked_by", "read_on")} == {
        k: v for k, v in before[0]["max_penalty"].items() if k not in ("checked_by", "read_on")
    }
    # Everything else is as it was, the other prepared blocks included.
    after[0]["max_penalty"] = before[0]["max_penalty"]
    assert after == before
    # The name goes in the commit message, never in the data.
    assert "A Person" not in (data / "countries.json").read_text(encoding="utf-8")
    assert 'git commit -m "Carimba BRA.max_penalty (conferido por A Person em 2026-11-12)"' in out


def test_a_country_alone_stamps_every_ready_block_of_it(data):
    assert run(data, "--field", "BRA", "--by", "A Person", "--execute") == 0
    after = read(data)[0]
    for name in ("penal_code", "domestic_genocide", "max_penalty"):
        assert after[name]["checked_by"] == "human", name
    assert after["death_penalty"]["checked_by"] == "robot"


@pytest.mark.parametrize(
    ("field", "why"),
    [
        ("XXX.penal_code", "'XXX' is not a record"),
        ("BRA.situations", "'situations' is not a block"),
        ("MMR.penal_code", "asserts nothing"),
        ("MMR.domestic_genocide", "lacks url"),
        ("MMR.max_penalty", "already checked by human"),
        ("BRA.death_penalty", "already checked by robot"),
        ("MMR", "no block of MMR is ready"),
    ],
)
def test_a_block_that_is_not_ready_is_refused(data, capsys, field, why):
    before = (data / "countries.json").read_bytes()
    assert run(data, "--field", field, "--by", "A Person", "--execute") == 1
    out = capsys.readouterr().out
    assert why in out and "nothing was written" in out
    assert (data / "countries.json").read_bytes() == before


def test_one_refused_block_stops_the_others(data):
    before = (data / "countries.json").read_bytes()
    args = ("--field", "BRA.penal_code", "--field", "MMR.penal_code", "--by", "A Person")
    assert run(data, *args, "--execute") == 1
    assert (data / "countries.json").read_bytes() == before


def test_to_stamp_needs_a_name_and_a_date(data, capsys):
    assert run(data, "--field", "BRA.penal_code", "--execute") == 2
    assert "--by" in capsys.readouterr().err
    assert run(data, "--field", "BRA.penal_code", "--by", " ", "--execute") == 2
    assert run(data, "--field", "BRA.penal_code", "--by", "A Person", "--read-on", "10/11") == 2
    assert read(data) == records()


def test_the_real_data_lists_without_writing(capsys):
    path = ROOT / "data" / "countries.json"
    before = path.read_bytes()
    assert stamp.main([]) == 0
    assert "blocks ready to be stamped" in capsys.readouterr().out
    assert path.read_bytes() == before


def test_stamping_brazil_in_a_copy_of_the_real_data_clears_it_in_strict(tmp_path):
    import shutil

    import transform

    data = tmp_path / "data"
    shutil.copytree(ROOT / "data", data)
    before = [p for p in transform.validate(transform.load(data)) if "[BRA]" in p.where]
    assert {p.where for p in before} == {
        f"countries[BRA].{b}" for b in ("penal_code", "domestic_genocide", "max_penalty")
    }
    assert run(data, "--field", "BRA", "--by", "A Person", "--execute") == 0
    assert [p for p in transform.validate(transform.load(data)) if "[BRA]" in p.where] == []
