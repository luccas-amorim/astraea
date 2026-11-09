from datetime import date

import pytest

from astraea import sources
from astraea.engine.contract import Reference, Source
from astraea.sources.rss import Rss, read_feed

FEED = "https://jornal.exemplo.br/feed"


def _rss(network, **cfg):
    return sources.build({"type": "rss", "id": "rss:paper", "url": FEED, **cfg}, network)


def test_adapters_fulfil_the_contract():
    for cls in sources.TYPES.values():
        for name in ("list", "fetch", "sentinel", "from_config"):
            assert callable(getattr(cls, name))
        assert isinstance(cls.respects_robots, bool)
    assert isinstance(Rss("x", FEED, client=None), Source)
    assert set(sources.TYPES) == {"rss", "gdelt", "curated_list"}


def test_unknown_type_is_refused():
    with pytest.raises(ValueError, match="unknown"):
        sources.build({"type": "gopher", "id": "x"})


def test_rss_and_atom(fixtures):
    refs = list(read_feed((fixtures / "rss" / "feed.xml").read_bytes(), "rss:j"))
    assert [r.source_id for r in refs] == [
        "jornal-1001",
        "jornal-1002",
        "jornal-1003",
        "jornal-0900",
    ]
    assert refs[0].published_at == date(2026, 10, 2)
    atom = list(read_feed((fixtures / "rss" / "atom.xml").read_bytes(), "rss:r"))
    assert len(atom) == 1  # the entry without a link is ignored
    assert atom[0].url == "https://repositorio.exemplo.br/handle/123/456"
    assert atom[0].published_at == date(2026, 9, 30)


def test_rss_lists_from_the_date(network, fixtures):
    network.answer(FEED, fixtures / "rss" / "feed.xml")
    refs = list(_rss(network).list(date(2026, 9, 1)))
    assert "jornal-0900" not in [r.source_id for r in refs]
    assert len(refs) == 3


def test_rss_fetches_the_page_and_not_the_summary(network, fixtures):
    url = "https://jornal.exemplo.br/2026/10/carandiru-34-anos"
    network.answer(url, fixtures / "rss" / "article-carandiru.html")
    source = _rss(network)
    ref = Reference("rss:paper", "jornal-1001", url, "Massacre do Carandiru: 34 anos depois")
    doc = source.fetch(ref)
    assert "Pavilhão 9" in doc.text
    assert "Resumo curto" not in doc.text
    assert doc.highlights["headline"] == ref.title
    assert doc.highlights["standfirst"].startswith("Familiares")
    assert len(doc.text_hash) == 64
    assert source.sentinel(doc)


def test_rss_sentinel_rejects_an_error_page_served_with_200(network, fixtures):
    url = "https://jornal.exemplo.br/2026/10/sumiu"
    network.answer(url, fixtures / "rss" / "error-200.html")
    source = _rss(network, min_chars=50)
    doc = source.fetch(Reference("rss:paper", "jornal-1003", url))
    assert not source.sentinel(doc)


def test_rss_sentinel_rejects_short_text(network, fixtures):
    url = "https://jornal.exemplo.br/2026/10/sumiu"
    network.answer(url, "<p>Carandiru</p>")
    source = _rss(network)
    assert not source.sentinel(source.fetch(Reference("rss:paper", "x", url)))
