"""A run end to end, without network: feed, pages, sentinel, triage, state and outputs."""

import json
from datetime import date

import pytest

from astraea import cli
from astraea.engine import config, lexicon, outputs, state
from astraea.engine import run as runs
from astraea.engine.capture import Corpus
from astraea.engine.contract import Reference
from astraea.engine.http import Response
from astraea.sources.rss import html_document
from tests.support import BASE, FEED, _run


def test_complete_run(cfg, paper_network):
    c, r = _run(cfg, paper_network)
    by_id = {line.ref.source_id: line for line in r.lines}

    assert set(by_id) == {"jornal-1001", "jornal-1002", "jornal-1003"}  # 0900 is earlier
    assert by_id["jornal-1001"].level == 3
    assert by_id["jornal-1001"].result.where == "headline"
    assert by_id["jornal-1002"].result.reason == "no_term"
    assert by_id["jornal-1003"].status == runs.SENTINEL
    assert r.exit_code == runs.NEEDS_READING
    assert r.needs_reading
    assert r.since == {"rss:paper": "2026-09-01"}

    # Corpus: only the intact one has a canonical name; the rejected one stays as .part.
    folder = c.corpus / "rss_paper"
    assert len(list(folder.glob("*.json"))) == 2
    assert len(list(folder.glob("*.json.part"))) == 1

    # State: the rejected one is not marked as seen, so it is retried.
    memory = state.read(c.state, "rss:paper")
    assert memory.last_run == date(2026, 10, 4)
    assert set(memory.seen) == {"jornal-1001", "jornal-1002"}
    assert memory.progress == {}


def test_outputs(cfg, paper_network):
    c, r = _run(cfg, paper_network)
    folder = outputs.write(r, c.runs)
    accepted = [
        json.loads(x) for x in (folder / "accepted.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(accepted) == 1
    item = accepted[0]
    assert item["url"] == f"{BASE}/carandiru-34-anos"
    assert item["lexicon"] == {"id": "carandiru-sample", "version": "2026-10-04"}
    assert item["keys"][0] == "massacre-do-carandiru"
    assert "evento" in item["categories"]
    assert item["text_hash"] and item["captured_at"]
    assert item["snapshot"] is None
    assert item["corpus"] == f"corpus/rss_paper/{item['text_hash']}.json"
    assert (c.directory / item["corpus"]).exists()
    assert (folder / "needs-review.jsonl").read_text(encoding="utf-8") == ""
    assert len((folder / "items.jsonl").read_text(encoding="utf-8").splitlines()) == 3

    full = (folder / "report-full.md").read_text(encoding="utf-8")
    summary = (folder / "report-summary.md").read_text(encoding="utf-8")
    assert full.startswith("# Astraea: run")
    assert "Discarded at level 0" in full and "drenagem" in full
    assert "drenagem" not in summary
    assert "Capture or integrity failures (1)" in summary
    meta = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    assert meta["counts"]["status"] == {"sentinel_rejected": 1, "triaged": 2}
    assert meta["exit_code"] == 3 and meta["needs_reading"] is True
    assert meta["incomplete"] == {}


def test_second_run_does_not_refetch_what_it_saw(cfg, paper_network):
    _run(cfg, paper_network)
    paper_network.requests.clear()
    _, r = _run(cfg, paper_network)
    fetched = [u for u in paper_network.urls() if u.startswith(BASE)]
    # The window now starts on 02/10 and the rejected item is from 01/10: it only comes back
    # because it is pending.
    assert r.since == {"rss:paper": "2026-10-02"}  # last run minus the margin
    assert fetched == [f"{BASE}/sumiu"]


def test_pending_is_resolved_when_the_page_comes_back(cfg, paper_network, fixtures):
    c, _ = _run(cfg, paper_network)
    memory = state.read(c.state, "rss:paper")
    assert memory.pending["jornal-1003"]["reason"] == runs.SENTINEL
    assert memory.pending["jornal-1003"]["attempts"] == 1

    paper_network.routes[f"{BASE}/sumiu"] = []
    paper_network.answer(f"{BASE}/sumiu", fixtures / "rss" / "article-carandiru.html")
    _, r = _run(cfg, paper_network)
    assert [line.level for line in r.lines] == [3]
    memory = state.read(c.state, "rss:paper")
    assert memory.pending == {}
    assert "jornal-1003" in memory.seen


def test_pending_does_not_keep_large_data(cfg):
    memory = state.State("x")
    large = Reference("x", "1", "https://a.br/1", data={"text": "palavra " * 2000})
    small = Reference(
        "x", "2", "https://a.br/2", data={"snapshot": "https://web.archive.org/web/1id_/a"}
    )
    memory.add_pending(large, runs.FAILED)
    memory.add_pending(small, runs.FAILED)
    assert memory.pending["1"]["ref"]["data"] is None
    assert memory.pending["2"]["ref"]["data"]["snapshot"].startswith("https://web.archive.org")


def test_without_state_rereads_everything_and_writes_nothing(cfg, paper_network):
    c, _ = _run(cfg, paper_network, use_state=False)
    assert not state.path(c.state, "rss:paper").exists()


def test_source_down_gives_code_2_and_does_not_advance_the_date(cfg, network):
    c, r = _run(cfg, network)  # no route for the feed: 404
    assert r.exit_code == runs.ERROR
    assert "rss:paper" in r.source_failures
    # The state is written (seen, pending, progress), but the date does not advance.
    memory = state.read(c.state, "rss:paper")
    assert memory.last_run is None


class _SourceThatFailsMidway:
    """Lists one reference, notes progress, and then the network goes down."""

    id = "fake:midway"
    rate_limit_per_minute = 60
    respects_robots = False
    uses_progress = True

    def __init__(self, html: bytes) -> None:
        self.html = html

    def list(self, since, progress):
        progress["done"] = ["a|2024"]
        snapshot = "https://web.archive.org/web/20261001id_/https://fake.br/one"
        yield Reference(
            self.id, "one", "https://fake.br/one", "Carandiru: 34 anos", date(2026, 10, 1),
            {"snapshot": snapshot},
        )  # fmt: skip
        raise ConnectionError("dropped with api_key=SECRET in the URL")

    def fetch(self, ref):
        return html_document(ref, Response(200, ref.url, self.html, {}), ref.title)

    def sentinel(self, doc):
        return True


def test_listing_that_fails_midway_uses_what_it_listed_and_writes_progress(cfg, fixtures):
    c = config.load(cfg)
    matcher = lexicon.Matcher(lexicon.load(c.lexicon))
    source = _SourceThatFailsMidway((fixtures / "rss" / "article-carandiru.html").read_bytes())
    r = runs.run(c, [source], matcher, today=date(2026, 10, 4))

    assert r.exit_code == runs.ERROR
    assert "SECRET" not in r.source_failures["fake:midway"]
    assert "api_key=<redacted>" in r.source_failures["fake:midway"]
    assert [line.level for line in r.lines] == [3]  # the listed reference was triaged
    assert r.lines[0].snapshot.startswith("https://web.archive.org/web/20261001id_/")
    assert r.needs_reading

    memory = state.read(c.state, "fake:midway")
    assert memory.progress == {"done": ["a|2024"]}
    assert "one" in memory.seen
    assert memory.last_run is None  # the next window covers the period again


class _IncompleteSource(_SourceThatFailsMidway):
    id = "fake:incomplete"
    incomplete_listing = "3 slice(s) left for the next run"

    def list(self, since, progress):
        yield Reference(
            self.id, "one", "https://fake.br/one", "Carandiru: 34 anos", date(2026, 10, 1)
        )


def test_incomplete_listing_is_not_a_failure_but_does_not_advance_the_date(cfg, fixtures):
    c = config.load(cfg)
    matcher = lexicon.Matcher(lexicon.load(c.lexicon))
    source = _IncompleteSource((fixtures / "rss" / "article-carandiru.html").read_bytes())
    r = runs.run(c, [source], matcher, today=date(2026, 10, 4))
    assert r.source_failures == {}
    assert r.incomplete == {"fake:incomplete": "3 slice(s) left for the next run"}
    assert r.exit_code == runs.NEEDS_READING
    assert state.read(c.state, "fake:incomplete").last_run is None
    folder = outputs.write(r, c.runs)
    assert "continue in the next run (1)" in (folder / "report-summary.md").read_text(
        encoding="utf-8"
    )


def test_retriage_applies_a_new_lexicon_without_network(cfg, paper_network, tmp_path):
    c, _ = _run(cfg, paper_network)
    new = json.loads((tmp_path / "lexicon.json").read_text(encoding="utf-8"))
    new["version"] = "2026-10-05"
    new["terms"].append({"key": "drenagem", "forms": ["drenagem"]})
    new["context"]["requires_any"].append("prefeitura")
    (tmp_path / "lexicon.json").write_text(json.dumps(new))

    r = runs.retriage(c, lexicon.Matcher(lexicon.load(c.lexicon)))
    assert r.lexicon_version == "2026-10-05"
    levels = sorted(line.level for line in r.lines)
    assert levels == [3, 3]


def test_cli_validate_and_run_without_source(cfg, capsys, fixtures):
    assert cli.main(["validate-lexicon", str(fixtures / "lexicon-carandiru.json")]) == 0
    assert "valid" in capsys.readouterr().out
    assert cli.main(["run", "--config", str(cfg), "--source", "rss:other"]) == runs.ERROR


def test_malformed_feed_brings_down_only_the_source(cfg, network):
    network.answer(FEED, "<rss><channel><item>unclosed")
    _, r = _run(cfg, network)
    assert r.exit_code == runs.ERROR
    assert r.source_failures["rss:paper"].startswith("listing: ParseError")


def test_corpus_relative():
    corpus = Corpus("/data/corpus", store=False)
    assert corpus.relative(None) is None


@pytest.mark.parametrize(
    "data", [{}, {"catalog": {"min_level": 1}, "observations": {"min_level": 2}}]
)
def test_cli_validate_config_refuses(tmp_path, data, capsys):
    base = {
        "lexicon": "lexicon.json",
        "sources": [{"type": "rss", "id": "rss:x", "url": "https://x/feed"}],
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps({**base, **data}))
    assert cli.main(["validate-config", str(path)]) == runs.ERROR
    assert "stratum" in capsys.readouterr().err
