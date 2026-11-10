"""Robot policy in code (docs/06-roteiro.md, phase 1, item 5): the Crawl-delay of each
host and the domains that reserve text and data mining (`no_text_by_policy`)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from astraea import cli
from astraea.engine import lexicon, policy
from astraea.engine import run as runs
from astraea.engine.contract import Reference
from astraea.engine.http import Client
from astraea.engine.triage import triage
from tests.support import FEED, _run
from tests.test_http import Clock

ROOT = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------ Crawl-delay


def _client(network, clock, limit=60, **kw):
    return Client(limit, transport=network, sleep=clock.sleep, clock=clock, **kw)


def test_crawl_delay_is_kept_between_requests_to_the_host(network):
    network.answer("https://a.br/robots.txt", "User-agent: *\nCrawl-delay: 10\n")
    network.answer("https://a.br/x", "ok")
    clock = Clock()
    client = _client(network, clock)
    client.request("https://a.br/x")
    client.request("https://a.br/x")
    # robots.txt at 0 s, the first page at 10 s, the second at 20 s.
    assert clock.pauses == [10.0, 10.0]
    assert client.crawl_delay("https://a.br/y") == 10.0


def test_crawl_delay_is_per_host(network):
    network.answer("https://a.br/robots.txt", "User-agent: *\nCrawl-delay: 10\n")
    network.answer("https://a.br/x", "ok")
    network.answer("https://b.br/x", "ok")
    clock = Clock()
    client = _client(network, clock, limit=600)  # 0.1 s between any two requests
    client.request("https://a.br/x")
    clock.pauses.clear()
    client.request("https://b.br/x")  # b has no robots.txt: only the source's limit
    client.request("https://b.br/x")
    assert all(p <= 0.1 + 1e-9 for p in clock.pauses)
    assert client.crawl_delay("https://b.br/x") == 0.0


def test_the_larger_of_limit_and_crawl_delay_wins(network):
    network.answer("https://a.br/robots.txt", "User-agent: *\nCrawl-delay: 10\n")
    network.answer("https://a.br/x", "ok")
    clock = Clock()
    client = _client(network, clock, limit=2)  # 30 s between requests
    client.request("https://a.br/x")
    client.request("https://a.br/x")
    assert clock.now == pytest.approx(60.0)  # 30 s each, the crawl delay fits inside


def test_no_robots_no_crawl_delay(network):
    network.answer("https://a.br/x", "ok")
    clock = Clock()
    client = _client(network, clock, respects_robots=False)
    client.request("https://a.br/x")
    client.request("https://a.br/x")
    assert clock.pauses == [1.0]


# ------------------------------------------------------------------ no_text_by_policy


def test_hosts_and_subdomains():
    p = policy.Policy(frozenset({"elpais.com"}))
    assert p.no_text("https://elpais.com/internacional/x.html")
    assert p.no_text("https://www.elpais.com/x")
    assert p.no_text("https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada")
    assert not p.no_text("https://notelpais.com/x")
    assert not p.no_text("https://news.un.org/en/story/1")


def test_registry_reads_the_flag_from_sources_json(tmp_path):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps([
            {"url": "https://www.aljazeera.com", "no_text_by_policy": True},
            {"url": "https://news.un.org", "no_text_by_policy": False},
            {"url": None, "no_text_by_policy": True},
        ]),
        encoding="utf-8",
    )  # fmt: skip
    assert policy.Policy.from_registry(path).no_text_domains == {"aljazeera.com"}


def test_every_opt_out_of_docs_02_is_flagged_in_sources_json():
    """docs/02-fontes.md, 2.2: El País, EFE, Al Jazeera (clause 6) and Amnesty."""
    sources = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
    flagged = {s["id"] for s in sources if s["no_text_by_policy"]}
    assert {"el-pais", "efe", "al-jazeera", "amnesty-news"} <= flagged
    domains = policy.Policy.from_registry(ROOT / "data/sources.json").no_text_domains
    assert {"elpais.com", "efe.com", "aljazeera.com", "amnesty.org"} <= domains


def test_metadata_document_keeps_only_title_and_description():
    ref = Reference(
        "rss:x", "1", "https://reservado.exemplo/a", "Massacre do Carandiru: 34 anos",
        data={"description": "<p>Os <b>presos</b> do Pavilhão 9</p>"},
    )  # fmt: skip
    doc = policy.metadata_document(ref)
    assert doc.policy == policy.NO_TEXT
    assert doc.raw is None
    assert "Os presos do Pavilhão 9" in doc.text and "<b>" not in doc.text
    assert doc.highlights["headline"] == "Massacre do Carandiru: 34 anos"


def test_triage_caps_at_level_2_and_keeps_levels_0_and_1(fixtures):
    matcher = lexicon.Matcher(lexicon.load(fixtures / "lexicon-carandiru.json"))
    accepted = Reference("rss:x", "1", "https://r.exemplo/a", "Massacre do Carandiru")
    result = triage(policy.metadata_document(accepted), matcher)
    assert (result.level, result.reason) == (2, policy.NO_TEXT)
    nothing = Reference("rss:x", "2", "https://r.exemplo/b", "Obras de drenagem")
    assert triage(policy.metadata_document(nothing), matcher).reason == "no_term"


RESERVED_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item>
    <title>Massacre do Carandiru: 34 anos depois</title>
    <link>https://www.reservado.exemplo/2026/10/carandiru</link>
    <guid>reservado-1</guid>
    <pubDate>Fri, 02 Oct 2026 09:00:00 -0300</pubDate>
    <description>Presos e policiais, julgamento sem fim.</description>
  </item>
</channel></rss>"""


def test_run_never_fetches_a_reserved_page(cfg, network):
    network.answer(FEED, RESERVED_FEED)
    _, r = _run(cfg, network)
    assert "https://www.reservado.exemplo/2026/10/carandiru" not in network.urls()
    assert not any("reservado.exemplo" in url for url in network.urls())
    (line,) = r.lines
    assert line.status == runs.TRIAGED
    assert (line.level, line.result.reason) == (2, policy.NO_TEXT)
    assert line.title == "Massacre do Carandiru: 34 anos depois"
    assert r.exit_code == runs.NEEDS_READING


def test_cli_run_refuses_a_configuration_without_registry(cfg, capsys):
    data = json.loads(cfg.read_text(encoding="utf-8"))
    del data["registry"]
    cfg.write_text(json.dumps(data), encoding="utf-8")
    assert cli.main(["run", "--config", str(cfg)]) == runs.ERROR
    assert "registry" in capsys.readouterr().err
