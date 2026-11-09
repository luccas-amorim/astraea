"""Channels: gdelt and curated_list; and the reference archive in the Wayback."""

import json
from datetime import date
from urllib.parse import parse_qs, urlsplit

from astraea import sources
from astraea.engine import archive
from astraea.sources import gdelt


def _query(url):
    return parse_qs(urlsplit(url).query)


def test_archive_resolves_exact_url(network):
    network.answer(
        archive.CDX,
        json.dumps([["timestamp", "original"], ["20200101000000", "http://x.br/a"]]),
    )
    ts, url = archive.Archive(transport=network).resolve("https://www.x.br/a?utm_source=z")
    assert ts == "20200101000000"
    assert url == f"{archive.ARCHIVE}/20200101000000id_/http://x.br/a"
    q = _query(network.requests[-1].url)
    assert q["matchType"] == ["exact"] and q["limit"] == ["-1"]

    network.routes[archive.CDX] = []
    network.answer(archive.CDX, "[]")
    assert archive.Archive(transport=network).resolve("https://x.br/never") is None


# --- gdelt -------------------------------------------------------------------------


def test_gdelt_one_day_at_a_time_within_the_window(network, fixtures):
    network.answer(gdelt.URL, fixtures / "gdelt" / "day.json")
    cfg = {"type": "gdelt", "id": "gdelt:carandiru", "query": "carandiru"}
    source = sources.build(cfg, network)
    source.today = lambda: date(2026, 10, 4)
    refs = list(source.list(date(2020, 1, 1)))  # earlier than the window: cut

    queries = [_query(r.url) for r in network.requests if r.url.startswith(gdelt.URL)]
    assert len(queries) == 91  # 90-day window, plus today
    assert queries[0]["startdatetime"] == ["20260706000000"]
    assert queries[0]["enddatetime"] == ["20260707000000"]
    assert source.effective_since == date(2026, 7, 6)  # goes to the run report
    assert {r.source_id for r in refs} == {
        "https://noticias.exemplo.com/2026/10/02/carandiru-34-anos",
        "https://news.example.org/brazil-prison-massacre",
    }
    assert refs[0].published_at == date(2026, 10, 2)


def test_gdelt_full_day_is_split_in_six_hours(network):
    full = {
        "articles": [
            {"url": f"https://x.br/{i}", "seendate": "20261002T000000Z"} for i in range(250)
        ]
    }
    network.answer(gdelt.URL, json.dumps(full))
    network.answer(gdelt.URL, json.dumps({"articles": []}))
    cfg = {"type": "gdelt", "id": "gdelt:x", "query": "x"}
    source = sources.build(cfg, network)
    source.today = lambda: date(2026, 10, 2)
    list(source.list(date(2026, 10, 2)))
    api = [r for r in network.requests if r.url.startswith(gdelt.URL)]
    bands = [_query(r.url)["startdatetime"][0] for r in api][1:]
    assert bands == ["20261002000000", "20261002060000", "20261002120000", "20261002180000"]


# --- curated_list ------------------------------------------------------------------


def test_curated_list_reads_csv_relative_to_the_config(network, tmp_path, fixtures):
    (tmp_path / "lists").mkdir()
    (tmp_path / "lists" / "archive.csv").write_text(
        "url,title,published_at\n"
        "https://memoria.bn.br/doc/1,Jornal do Brasil 3/10/1992,1992-10-03\n"
        "https://memoria.bn.br/doc/2,,bad-date\n"
        ",no url,\n",
        encoding="utf-8",
    )
    cfg = {"type": "curated_list", "id": "curated_list:archive", "file": "lists/archive.csv",
           "_config_dir": str(tmp_path)}  # fmt: skip
    source = sources.build(cfg, network)
    refs = list(source.list(date(1990, 1, 1)))
    assert [r.url for r in refs] == ["https://memoria.bn.br/doc/1", "https://memoria.bn.br/doc/2"]
    assert refs[0].published_at == date(1992, 10, 3) and refs[1].published_at is None
    assert refs[0].title == "Jornal do Brasil 3/10/1992"
    network.answer("https://memoria.bn.br/doc/1", fixtures / "html" / "archived-page.html")
    assert source.sentinel(source.fetch(refs[0]))
