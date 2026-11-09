"""CSV catalogue (one document per line), observations and completion of older files."""

import csv
import json
from datetime import date

from astraea import cli, sources
from astraea.engine import config
from astraea.engine import run as runs
from astraea.engine.contract import Reference
from astraea.engine.outputs import catalog, observations
from astraea.engine.triage import Result
from astraea.engine.url import identity
from tests.support import _run


def _lines(path):
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _empty_run(run_id="20261005T000000Z"):
    return runs.Run(run_id, "lex", "v1", "run", "x")


def test_catalog_only_with_what_passed(cfg, paper_network, tmp_path):
    c, r = _run(cfg, paper_network)
    path = tmp_path / "catalog.csv"
    assert catalog.update(r, path, stratum_of=lambda s: "press") == 1
    (line,) = _lines(path)
    assert tuple(line) == catalog.COLUMNS
    assert line["url"] == "https://jornal.exemplo.br/2026/10/carandiru-34-anos"
    assert line["id"] == identity(line["url"]) == catalog.id_from_url(line["url"])
    assert line["domain"] == "jornal.exemplo.br"
    assert line["stratum"] == "press"
    assert line["title"].startswith("Massacre do Carandiru: 34 anos depois")
    assert line["published_at"] == "2026-10-02"
    assert line["level"] == "3"
    assert line["keys"].split(";")[0] == "massacre-do-carandiru"
    assert "evento" in line["categories"].split(";")
    assert line["first_run"] == r.id
    assert line["lexicon_version"] == "2026-10-04"
    assert line["snapshot"] == "" and line["captured_at"] == ""


def test_catalog_is_cumulative_and_keeps_the_first_record(cfg, paper_network, tmp_path):
    _, r = _run(cfg, paper_network)
    path = tmp_path / "catalog.csv"
    catalog.update(r, path)
    before = path.read_text(encoding="utf-8")
    r.lines[0].result.keys = ["other-key"]
    assert catalog.update(r, path) == 0
    assert path.read_text(encoding="utf-8") == before


def test_same_article_archived_and_live_is_one_line(tmp_path):
    r = _empty_run()
    live = Reference(
        "gdelt:c", "a", "https://www.jornal.br/2016/carandiru.shtml?utm_source=t", "Título"
    )
    archived = Reference(
        "wayback:j", "http://jornal.br/2016/carandiru.shtml",
        "https://web.archive.org/web/20160927090000id_/http://jornal.br/2016/carandiru.shtml",
        data={"snapshot": "https://web.archive.org/web/20160927090000id_/http://jornal.br/2016/carandiru.shtml"},
    )  # fmt: skip
    for ref in (live, archived):
        r.lines.append(runs.Line(ref, runs.TRIAGED, Result(3, "accepted", ["k"], ["evento"]),
                                 text_hash="h", snapshot=runs._snapshot(ref)))  # fmt: skip
    path = tmp_path / "catalog.csv"
    assert catalog.update(r, path) == 1
    (line,) = _lines(path)
    assert line["url"] == "https://www.jornal.br/2016/carandiru.shtml?utm_source=t"  # the first
    assert line["snapshot"] == ""  # the live one did not bring it; complete_snapshots resolves

    n = catalog.complete_snapshots(
        path,
        lambda url: ("20160927090000", f"https://web.archive.org/web/20160927090000id_/{url}"),
    )
    assert n == 1
    (line,) = _lines(path)
    assert line["captured_at"] == "20160927090000" and "id_/" in line["snapshot"]
    assert catalog.complete_snapshots(path, lambda url: None) == 0


def test_wayback_snapshot_goes_to_the_catalog(tmp_path):
    r = _empty_run()
    snap = "https://web.archive.org/web/19990301120000id_/http://www1.j.br/fsp/carandiru.htm"
    ref = Reference(
        "wayback:j", "http://www1.j.br/fsp/carandiru.htm", snap, data={"snapshot": snap}
    )
    r.lines.append(runs.Line(ref, runs.TRIAGED, Result(3, "accepted"), snapshot=snap))
    catalog.update(r, tmp_path / "c.csv")
    (line,) = _lines(tmp_path / "c.csv")
    assert line["url"] == "http://www1.j.br/fsp/carandiru.htm"
    assert line["snapshot"] == snap and line["captured_at"] == "19990301120000"


def test_completes_a_file_with_missing_columns(tmp_path):
    path = tmp_path / "catalog.csv"
    path.write_text(
        "id,url,keys\n"
        "abcd,https://web.archive.org/web/2016id_/http://www.j.br/x,massacre-do-carandiru\n",
        encoding="utf-8",
    )
    assert catalog.update(_empty_run(), path) == 0
    (line,) = _lines(path)
    assert tuple(line) == catalog.COLUMNS
    assert line["url"] == "http://www.j.br/x" and line["id"] == identity("http://www.j.br/x")
    assert line["domain"] == "j.br" and line["keys"] == "massacre-do-carandiru"


def test_min_level(cfg, paper_network, tmp_path):
    _, r = _run(cfg, paper_network)
    assert catalog.update(r, tmp_path / "a.csv", min_level=0) == 2
    assert catalog.update(r, tmp_path / "b.csv", min_level=3) == 1


def test_observations_one_line_per_sighting(cfg, paper_network, tmp_path):
    _, r = _run(cfg, paper_network)
    path = tmp_path / "observations.csv"
    assert observations.append(r, path) == 1  # level >= 2 only
    assert observations.append(r, path) == 1  # appends again: it is a sighting, not a document
    lines = _lines(path)
    assert len(lines) == 2 and tuple(lines[0]) == observations.COLUMNS
    assert lines[0]["channel"] == "rss" and lines[0]["source"] == "rss:paper"
    assert lines[0]["id"] == identity(lines[0]["url"])
    assert lines[0]["run"] == r.id and lines[0]["level"] == "3"
    assert lines[0]["published_at"] == "2026-10-02" and len(lines[0]["text_hash"]) == 64


def test_without_store_text_nothing_goes_to_the_corpus(cfg, paper_network):
    data = json.loads(cfg.read_text(encoding="utf-8"))
    data["store_text"] = False
    cfg.write_text(json.dumps(data))
    c, r = _run(cfg, paper_network)
    assert not c.corpus.exists()
    assert [line.level for line in r.lines if line.level is not None] == [3, 0]
    assert all(line.corpus is None for line in r.lines)


def test_cli_updates_catalog_and_observations(cfg, monkeypatch, paper_network, capsys):
    data = json.loads(cfg.read_text(encoding="utf-8"))
    data["catalog"] = {"file": "catalog.csv"}
    data["observations"] = {"file": "observations.csv"}
    data["sources"][0]["stratum"] = "press"
    cfg.write_text(json.dumps(data))
    build = sources.build
    monkeypatch.setattr(sources, "build", lambda s: build(s, paper_network))
    assert cli.main(["run", "--config", str(cfg)]) == 3
    c = config.load(cfg)
    assert len(_lines(c.catalog_csv)) == 1
    assert _lines(c.catalog_csv)[0]["stratum"] == "press"
    assert len(_lines(c.observations_csv)) == 1
    out = capsys.readouterr().out
    assert "catalog: 1 new documents" in out and "observations: 1 sightings" in out
    assert cli.main(["validate-config", str(cfg)]) == 0


def test_date_import_used():
    assert date(2026, 10, 5).isoformat() == "2026-10-05"


def test_title_comes_from_the_headline_when_the_reference_only_has_the_url():
    ref = Reference(
        "wayback:j",
        "http://j.br/x",
        "https://web.archive.org/web/1id_/http://j.br/x",
        "http://j.br/x",
    )
    line = runs.Line(
        ref, runs.TRIAGED, Result(3, "accepted"), headline="Carandiru, dez anos depois"
    )
    assert line.title == "Carandiru, dez anos depois"
    assert line.as_dict()["title"] == "Carandiru, dez anos depois"
    feed_ref = Reference("rss:j", "a", "https://j.br/a", "Manchete do feed")
    with_title = runs.Line(feed_ref, runs.TRIAGED, Result(3, "accepted"), headline="Outra")
    assert with_title.title == "Manchete do feed"
    assert runs.Line(Reference("x", "a", "https://j.br/a"), runs.TRIAGED).title is None


def test_same_text_under_two_urls_is_one_document(tmp_path):
    r = _empty_run()
    for url in ("https://j.br/materia/", "https://j.br/materia/embed/"):
        r.lines.append(runs.Line(Reference("wayback:j", url, url), runs.TRIAGED,
                                 Result(3, "accepted"), text_hash="SAME"))  # fmt: skip
    assert catalog.update(r, tmp_path / "c.csv") == 1
    r2 = _empty_run("20261006T000000Z")
    r2.lines.append(runs.Line(Reference("gdelt:c", "z", "https://outro.br/z"), runs.TRIAGED,
                              Result(3, "accepted"), text_hash="SAME"))  # fmt: skip
    assert catalog.update(r2, tmp_path / "c.csv") == 0
