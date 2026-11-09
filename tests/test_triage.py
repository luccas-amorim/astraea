from datetime import UTC, datetime

import pytest

from astraea.engine import lexicon
from astraea.engine.capture import build_document
from astraea.engine.contract import Reference
from astraea.engine.triage import cut_excerpt, triage

REF = Reference(source="test", source_id="1", url="https://exemplo.br/1")


@pytest.fixture
def matcher(fixtures):
    return lexicon.Matcher(lexicon.load(fixtures / "lexicon-carandiru.json"))


def _doc(text, **highlights):
    return build_document(REF, text, highlights=highlights, now=datetime(2026, 10, 4, tzinfo=UTC))


def test_level_0_no_term(matcher):
    r = triage(_doc("A prefeitura anunciou obras de drenagem."), matcher)
    assert (r.level, r.reason, r.excerpt) == (0, "no_term", None)


def test_level_0_only_excluded_comes_with_excerpt(matcher):
    r = triage(_doc("Sessão de cinema: Carandiru, o filme, com debate."), matcher)
    assert (r.level, r.reason) == (0, "only_excluded")
    assert "o filme" in r.excerpt


def test_level_1_term_without_context(matcher):
    r = triage(_doc("O bairro do Carandiru ganhou uma feira de artesanato."), matcher)
    assert (r.level, r.reason, r.keys) == (1, "no_context", ["massacre-do-carandiru"])
    assert "Carandiru" in r.excerpt


def test_level_2_term_and_context_outside_the_highlight(matcher):
    doc = _doc(
        "Seminário discute segurança pública. "
        "Entre os casos, o Carandiru, onde presos foram mortos.",
        headline="Seminário discute segurança pública",
    )
    r = triage(doc, matcher)
    assert (r.level, r.reason, r.where) == (2, "needs_review", "text")


def test_level_3_term_in_the_highlight(matcher):
    doc = _doc(
        "Em 1992 a Polícia Militar invadiu o Pavilhão 9 da Casa de Detenção. Houve indulto.",
        headline="Massacre do Carandiru: 34 anos",
    )
    r = triage(doc, matcher)
    assert (r.level, r.reason, r.where) == (3, "accepted", "headline")
    assert r.keys == ["casa-de-detencao", "indulto"]
    assert r.categories == ["lugar", "desdobramento-juridico"]
    assert r.score == 1.5
    assert r.excerpt == "Massacre do Carandiru: 34 anos"


def test_excerpt_marks_what_it_cut():
    text = "a" * 500 + "TARGET" + "b" * 500
    excerpt = cut_excerpt(text, 500, 506, radius=10)
    assert excerpt == "…" + "a" * 10 + "TARGET" + "b" * 10 + "…"


def test_triage_is_deterministic(matcher):
    doc = _doc("Carandiru, 1992: presos mortos.", headline="Carandiru")
    assert triage(doc, matcher) == triage(doc, matcher)
