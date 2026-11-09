import json
from pathlib import Path

import pytest

from astraea.engine import lexicon
from astraea.engine.text import fold

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "tests" / "fixtures" / "lexicon-example.json"


def _match(lex, text):
    valid, cancelled = lexicon.Matcher(lex).occurrences(fold(text))
    return [o.key for o in valid], [o.key for o in cancelled]


def test_repository_example_is_valid():
    lex = lexicon.load(EXAMPLE)
    assert lex.terms[0].key == "cp-art-121"
    assert "recurso" in lex.context


def test_schema_and_validator_agree():
    """The fields the validator accepts are exactly those of the published schema."""
    schema = json.loads((ROOT / "schemas" / "lexicon.schema.json").read_text(encoding="utf-8"))
    term = schema["properties"]["terms"]["items"]
    context = schema["properties"]["context"]
    assert set(schema["properties"]) == lexicon._ROOT_KEYS
    assert set(term["properties"]) == lexicon._TERM_KEYS
    assert set(context["properties"]) == lexicon._CONTEXT_KEYS
    assert set(schema["required"]) == {"id", "version", "terms"}
    assert set(term["required"]) == {"key", "forms"}


@pytest.mark.parametrize(
    ("data", "excerpt"),
    [
        ({"version": "1", "terms": [{"key": "a", "forms": ["a"]}]}, "id"),
        ({"id": "x", "version": "1", "terms": []}, "terms"),
        ({"id": "x", "version": "1", "terms": [{"key": "a", "forms": []}]}, "forms"),
        (
            {"id": "x", "version": "1", "terms": [{"key": "a", "forms": ["a"], "weight": 0}]},
            "weight",
        ),
        (
            {
                "id": "x",
                "version": "1",
                "terms": [{"key": "a", "forms": ["a"]}, {"key": "a", "forms": ["b"]}],
            },
            "repeated",
        ),
        (
            {"id": "x", "version": "1", "terms": [{"key": "a", "forms": ["a"], "regex": "."}]},
            "unknown",
        ),
        (
            {"id": "x", "version": "1", "terms": [{"key": "a", "forms": ["a"]}], "context": {}},
            "requires_any",
        ),
    ],
)
def test_invalid_ones_are_refused_with_a_reason(data, excerpt):
    problems = lexicon.validate(data)
    assert problems
    assert any(excerpt in p for p in problems)
    with pytest.raises(lexicon.LexiconError):
        lexicon.from_data(data)


def test_matches_ignoring_accent_and_case_by_whole_word():
    lex = lexicon.from_data(
        {"id": "x", "version": "1", "terms": [{"key": "h", "forms": ["homicídio"]}]}
    )
    assert _match(lex, "HOMICIDIO qualificado")[0] == ["h"]
    assert _match(lex, "Homicídio")[0] == ["h"]
    assert _match(lex, "pré-homicídiorama")[0] == []


def test_space_in_the_form_tolerates_line_break():
    lex = lexicon.from_data(
        {"id": "x", "version": "1", "terms": [{"key": "a", "forms": ["art. 121 do CP"]}]}
    )
    assert _match(lex, "nos termos do art.\n121  do CP")[0] == ["a"]


def test_exclusion_cancels_only_the_occurrence_it_contains():
    lex = lexicon.load(EXAMPLE)
    valid, cancelled = _match(lex, "Trata-se de homicídio culposo na direção de veículo.")
    assert valid == [] and cancelled == ["cp-art-121"]
    valid, cancelled = _match(
        lex, "Homicídio culposo na direção; depois, homicídio doloso, art. 121 do Código Penal."
    )
    assert valid == ["cp-art-121", "cp-art-121"] and cancelled == ["cp-art-121"]


def test_longest_form_wins_at_the_same_position():
    matcher = lexicon.Matcher(lexicon.load(EXAMPLE))
    text = fold("conforme o art. 121 do Código Penal")
    (oc,), _ = matcher.occurrences(text)
    assert text[oc.start : oc.end] == "art. 121 do codigo penal"


def test_context_absent_from_the_lexicon_requires_nothing():
    lex = lexicon.from_data({"id": "x", "version": "1", "terms": [{"key": "a", "forms": ["a"]}]})
    assert lexicon.Matcher(lex).context("anything") is True


@pytest.mark.parametrize(
    ("text", "valid", "cancelled"),
    [
        ("nos termos do art. 121, § 2º, inc. IV, do Código Penal.", 1, 0),
        ("art. 121, caput, do CP", 1, 0),
        ("art. 121 do Código Penal Militar", 0, 1),  # the exclusion also uses an ellipsis
        ("art. 1210 do CP", 0, 0),  # word boundary at both ends of the gap
        ("art. 121, § 2º, do CPM", 0, 0),
        ("art. 121; e o Código Penal", 0, 0),  # a semicolon closes the gap
        ("art. 121 " + "x" * 70 + " do Código Penal", 0, 0),  # gap longer than 60
    ],
)
def test_ellipsis_as_case_law_cites(text, valid, cancelled):
    lex = lexicon.from_data(
        {
            "id": "x",
            "version": "1",
            "terms": [
                {
                    "key": "cp-art-121",
                    "forms": ["art. 121 … Código Penal", "art. 121 … CP"],
                    "exclusions": ["art. 121 … Código Penal Militar"],
                }
            ],
        }
    )
    v, c = _match(lex, text)
    assert (len(v), len(c)) == (valid, cancelled)
