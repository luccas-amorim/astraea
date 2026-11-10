import json

import pytest

from astraea.engine import config


def _base(**extra):
    return {
        "lexicon": "lexicon.json",
        "registry": "sources.json",
        "sources": [{"type": "rss", "id": "rss:x", "url": "https://x/feed", "stratum": "press"}],
        **extra,
    }


def test_sound_config():
    assert config.validate(_base()) == []


def test_stratum_is_required_and_known():
    data = _base()
    del data["sources"][0]["stratum"]
    assert any("no stratum" in p for p in config.validate(data))
    data["sources"][0]["stratum"] = "newspapers"
    assert any("unknown stratum" in p for p in config.validate(data))


def test_id_prefix_is_the_type():
    data = _base()
    data["sources"][0]["id"] = "paper:x"
    assert any("id prefix" in p for p in config.validate(data))


def test_coherent_levels():
    data = _base(catalog={"min_level": 2}, observations={"min_level": 3})
    assert any("observations.min_level" in p for p in config.validate(data))
    data = _base(catalog={"min_level": 7})
    assert any("integer from 0 to 3" in p for p in config.validate(data))


def test_since_and_repeated_ids():
    data = _base(since="05/10/2026")
    assert any("YYYY-MM-DD" in p for p in config.validate(data))
    data = _base()
    data["sources"].append(dict(data["sources"][0]))
    assert any("repeated ids" in p for p in config.validate(data))


def test_load_and_properties(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(_base(
        directory=".", catalog={"file": "catalog.csv"}, observations={}, archive={"resolve": True}
    )))  # fmt: skip
    c = config.load(path)
    assert c.catalog_csv == tmp_path.resolve() / "catalog.csv" and c.catalog_level == 3
    assert c.observations_csv == tmp_path.resolve() / "observations.csv"
    assert c.observations_level == 2
    assert c.resolve_archive is True
    assert c.stratum_of("rss:x") == "press" and c.stratum_of("nothing") == "general"
    with pytest.raises(ValueError, match="no source"):
        path.write_text(json.dumps({"lexicon": "l", "sources": []}))
        config.load(path)
