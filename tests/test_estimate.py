import csv
import json
from datetime import date

import pytest

from astraea import cli
from astraea.engine import estimate
from astraea.engine.estimate import Pair, normalize_url
from astraea.engine.outputs.observations import COLUMNS
from astraea.engine.url import identity


def test_normalize_url_is_re_exported():
    assert normalize_url("https://www.Jornal.br/a/b/") == "jornal.br/a/b"


def test_chapman_with_known_numbers():
    # n1 = 100, n2 = 80, 40 in common: Lincoln-Petersen would give 200; Chapman, 199.4.
    pair = Pair("a", "b", 100, 80, 40)
    assert pair.chapman == pytest.approx(101 * 81 / 41 - 1)
    low, high = pair.interval
    assert 140 <= low < pair.chapman < high


def _observations(path, sightings):
    """sightings: (source, url, level, run[, published_at[, hash]])."""
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        for obs in sightings:
            source, url, level, run = obs[:4]
            published = obs[4] if len(obs) > 4 else ""
            text_hash = obs[5] if len(obs) > 5 else ""
            writer.writerow({
                "id": identity(url), "channel": estimate.channel(source), "source": source,
                "run": run, "level": level, "published_at": published,
                "text_hash": text_hash, "url": url,
            })  # fmt: skip


def test_compute_channels_chao_curve_and_dedupe_by_hash(tmp_path):
    obs = tmp_path / "observations.csv"
    r1, r2 = "20261001T000000Z", "20261008T000000Z"
    _observations(obs, [
        ("wayback:j", "http://j.br/1", 3, r1),
        ("wayback:k", "http://k.br/2", 2, r1),
        ("wayback:j", "http://j.br/noise", 1, r1),             # level 1 stays out
        ("topic:c", "https://www.j.br/1", 3, r2),              # same normalized URL
        ("topic:c", "https://k.br/9", 2, r2, "", "HASH-A"),
        ("rss:paper", "https://k.br/9-amp", 3, r2, "", "HASH-A"),  # another URL, same text
        ("openalex:c", "https://doi.org/10.1/x", 3, r2),
        ("crossref:c", "https://doi.org/10.1/x", 3, r2),
    ])  # fmt: skip

    strata = {"openalex:c": "academic", "crossref:c": "academic"}
    by_stratum = estimate.compute(obs, stratum_of=lambda s: strata.get(s, "press"))
    press, academic = by_stratum["press"], by_stratum["academic"]

    # Two Wayback domains are a single channel; k.br/9 and k.br/9-amp are one document.
    assert set(press.by_channel) == {"wayback", "topic", "rss"}
    assert len(press.observed) == 3
    assert press.frequencies == {2: 2, 1: 1}
    assert press.chao == 3 + 1 * 1 / (2 * 2)
    assert press.curve == [(r1, 2, 2), (r2, 1, 3)]
    assert academic.chao == 1  # two channels, everything in common: floor equals observed

    text = estimate.report(by_stratum)
    assert "## Stratum `press`" in text and "## Stratum `academic`" in text
    assert "`topic` × `wayback` | 2 | 2 | 1 |" in text


def test_gdelt_only_enters_the_floor_with_since(tmp_path):
    obs = tmp_path / "observations.csv"
    r = "20261001T000000Z"
    _observations(obs, [
        ("wayback:j", "http://j.br/old", 3, r, "2002-10-02"),
        ("wayback:j", "http://j.br/new", 3, r, "2026-09-30"),
        ("gdelt:c", "http://j.br/new", 3, r, "2026-09-30"),
    ])  # fmt: skip
    (without,) = estimate.compute(obs).values()
    assert without.chao is None  # wayback + gdelt unaligned: a single comparable channel
    assert "not comparable" in estimate.report({"general": without})

    (with_since,) = estimate.compute(obs, since=date(2026, 7, 1)).values()
    assert with_since.observed == {identity("http://j.br/new")}
    assert with_since.aligned and with_since.chao == 1


def test_a_single_channel_does_not_estimate(tmp_path):
    obs = tmp_path / "observations.csv"
    _observations(obs, [("rss:a", "https://x.br/1", 3, "20261001T000000Z")])
    by_stratum = estimate.compute(obs)
    assert by_stratum["general"].chao is None
    assert "at least two" in estimate.report(by_stratum)


def test_without_observations_empty_report(tmp_path):
    assert estimate.compute(tmp_path / "does-not-exist.csv") == {}
    assert "No run" in estimate.report({})


def test_cli_estimate_requires_observations_and_writes_the_report(cfg, capsys):
    assert cli.main(["estimate", "--config", str(cfg)]) == 2
    data = json.loads(cfg.read_text(encoding="utf-8"))
    data["observations"] = {"file": "observations.csv"}
    cfg.write_text(json.dumps(data))
    assert cli.main(["estimate", "--config", str(cfg)]) == 0
    assert "report in" in capsys.readouterr().out
    assert (cfg.parent / "data" / "estimate.md").exists()
