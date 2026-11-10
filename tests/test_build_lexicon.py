"""scripts/build_lexicon.py and the lexicons it generates in data/lexicon/."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

from astraea import cli
from astraea.engine import lexicon
from astraea.engine.text import fold

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

import build_lexicon  # noqa: E402
import vocabularies  # noqa: E402

LANGUAGES = vocabularies.LEXICON_LANGUAGES


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def data(tmp_path) -> Path:
    """A copy of the two sources of the lexicon, without the generated files."""
    root = tmp_path / "data"
    shutil.copytree(DATA / "lexicon" / "fixed", root / "lexicon" / "fixed")
    shutil.copy(DATA / "situations.json", root / "situations.json")
    return root


def keys_found(lang: str, text: str) -> tuple[set[str], set[str], bool]:
    matcher = lexicon.Matcher(lexicon.load(DATA / "lexicon" / f"{lang}.json"))
    folded = fold(text)
    valid, cancelled = matcher.occurrences(folded)
    return {o.key for o in valid}, {o.key for o in cancelled}, bool(matcher.context(folded))


# ------------------------------------------------------------------ the generated files


def test_the_generated_lexicons_are_up_to_date():
    for lang, built in build_lexicon.build(DATA).items():
        path = build_lexicon.generated_path(DATA, lang)
        assert path.read_text(encoding="utf-8") == build_lexicon.dumps(built), (
            f"{path.name} is out of date: run python scripts/build_lexicon.py --execute"
        )


def test_one_valid_lexicon_per_language_of_d5(capsys):
    generated = sorted(p.stem for p in (DATA / "lexicon").glob("*.json"))
    assert generated == sorted(LANGUAGES)
    assert cli.main(["validate-lexicon", str(DATA / "lexicon" / "*.json")]) == 0
    assert capsys.readouterr().out.count(": valid,") == len(LANGUAGES)


@pytest.mark.parametrize("lang", LANGUAGES)
def test_fixed_terms_plus_one_term_per_situation(lang):
    fixed = read(build_lexicon.fixed_path(DATA, lang))
    generated = read(build_lexicon.generated_path(DATA, lang))
    situations = [s["id"] for s in read(DATA / "situations.json")]

    keys = [t["key"] for t in generated["terms"]]
    assert keys == [t["key"] for t in fixed["terms"]] + situations
    assert generated["context"] == fixed["context"]
    assert generated["id"] == f"astraea-{lang}"
    assert generated["version"].startswith(f"{lang}-{fixed['version']}-")
    assert "Do not edit" in generated["description"]
    for term in generated["terms"]:
        expected = ["situation"] if term["key"] in situations else None
        assert expected is None or term["categories"] == expected
        assert set(term["categories"]) <= set(vocabularies.VOCABULARIES["categories"])


def test_the_fixed_terms_have_the_same_keys_in_every_language():
    keys = {
        lang: [t["key"] for t in read(build_lexicon.fixed_path(DATA, lang))["terms"]]
        for lang in LANGUAGES
    }
    assert all(keys[lang] == keys["en"] for lang in LANGUAGES)
    assert "genocide" in keys["en"]


def test_the_arabic_lexicon_says_it_is_a_draft():
    assert read(build_lexicon.fixed_path(DATA, "ar"))["description"].startswith("DRAFT")
    assert "DRAFT" in read(build_lexicon.generated_path(DATA, "ar"))["description"]


# ------------------------------------------------------------------ what the terms catch


def test_english_court_order_on_a_situation():
    keys, _, context = keys_found(
        "en",
        "The ICJ indicated provisional measures in South Africa v. Israel, "
        "under the Genocide Convention.",
    )
    assert {"icj", "provisional-measures", "gaza-2023", "genocide-convention"} <= keys
    assert context


def test_english_noise_stays_out():
    keys, cancelled, _ = keys_found(
        "en", "Critics spoke of cultural genocide. The ICC rankings put India first."
    )
    assert keys == set() and cancelled == {"genocide"}


def test_a_country_name_alone_does_not_tie_the_news_to_the_situation():
    assert keys_found("en", "Fighting continues in Ukraine, a court heard.")[0] == set()
    keys, _, _ = keys_found("en", "Kyiv says Russia is committing genocide in Ukraine.")
    assert keys == {"genocide", "ukraine-2022"}


def test_portuguese_everyday_words_stay_out():
    keys, _, _ = keys_found(
        "pt",
        "O governo editou medidas provisórias sobre o orçamento. O tigre fugiu do "
        "zoológico. A CPI ouviu o ministro. Enchentes na província de Gaza, em Moçambique.",
    )
    assert keys == set()


def test_portuguese_court_order():
    keys, _, context = keys_found(
        "pt", "A CIJ determinou medidas provisórias no caso de genocídio em Gaza."
    )
    assert keys == {"icj", "provisional-measures", "genocide", "gaza-2023"}
    assert context  # the court itself is a legal marker


def test_french_and_spanish():
    keys, _, context = keys_found(
        "fr", "La CIJ a indiqué des mesures conservatoires; le génocide des Tutsi au Rwanda."
    )
    assert keys == {"icj", "provisional-measures", "genocide", "rwanda-1994"} and context
    keys, _, context = keys_found(
        "es", "La fiscalía de la Corte Penal Internacional investiga el genocidio de los rohinyás."
    )
    assert keys == {"icc", "genocide", "rohingya-myanmar"} and context


def test_arabic_matches_with_attached_particles():
    keys, _, context = keys_found(
        "ar",
        "أمرت محكمة العدل الدولية بتدابير تحفظية في قضية الإبادة الجماعية بغزة، "
        "وذكرت الروهينغا والإيزيديين.",
    )
    assert keys == {
        "icj",
        "provisional-measures",
        "genocide",
        "gaza-2023",
        "rohingya-myanmar",
        "yazidis-sinjar",
    }
    assert context


def test_rhetorical_use_stays_without_context():
    keys, _, context = keys_found("ar", "وصف ما يجري بأنه حرب إبادة")
    assert keys == {"genocide"} and not context
    keys, _, context = keys_found(
        "en", "Fans called the referee's decision a genocide of football."
    )
    assert keys == {"genocide"} and not context


# ------------------------------------------------------------------ the script


def test_simulation_writes_nothing_and_execute_writes(data, capsys):
    assert build_lexicon.main(["--data", str(data)]) == 0
    assert "simulation" in capsys.readouterr().out
    assert list((data / "lexicon").glob("*.json")) == []

    assert build_lexicon.main(["--data", str(data), "--execute"]) == 0
    written = sorted(p.stem for p in (data / "lexicon").glob("*.json"))
    assert written == sorted(LANGUAGES)
    assert b"\r" not in (data / "lexicon" / "en.json").read_bytes()
    # the real files are what the script writes from the real sources
    for lang in LANGUAGES:
        assert (data / "lexicon" / f"{lang}.json").read_bytes() == (
            DATA / "lexicon" / f"{lang}.json"
        ).read_bytes()

    assert build_lexicon.main(["--data", str(data), "--execute"]) == 0
    assert capsys.readouterr().out.count("up to date") == len(LANGUAGES)


def test_the_version_changes_with_any_term(data):
    before = build_lexicon.build(data)["en"]["version"]
    situations = read(data / "situations.json")
    situations[0]["terms"][0]["forms"].append("Arakan Rohingya")
    (data / "situations.json").write_text(json.dumps(situations), encoding="utf-8")
    after = build_lexicon.build(data)
    assert after["en"]["version"] != before
    assert after["en"]["version"].rsplit("-", 1)[0] == before.rsplit("-", 1)[0]


def change_fixed(data: Path, lang: str, change) -> None:
    path = build_lexicon.fixed_path(data, lang)
    fixed = read(path)
    change(fixed)
    path.write_text(json.dumps(fixed, ensure_ascii=False), encoding="utf-8")


@pytest.mark.parametrize(
    ("change", "excerpt"),
    [
        (lambda f: f["terms"][0].update(categories=["rumour"]), "category 'rumour'"),
        (lambda f: f["terms"][0].update(categories=["situation"]), "category 'situation'"),
        (lambda f: f["terms"][0].update(categories=[]), "at least one category"),
        (lambda f: f["terms"][0]["forms"].append("GÉNOCIDE"), "repeats"),
        (lambda f: f.update(version="november"), "YYYY-MM-DD"),
        (lambda f: f.pop("context"), "context.requires_any"),
        (lambda f: f["terms"][0].update(key="gaza-2023"), "repeated (gaza-2023)"),
        (lambda f: f["terms"][0].update(regex="."), "unknown field"),
    ],
)
def test_an_invalid_source_stops_the_build(data, capsys, change, excerpt):
    change_fixed(data, "fr", change)
    with pytest.raises(build_lexicon.BuildError) as error:
        build_lexicon.build(data)
    assert any(excerpt in p for p in error.value.problems), error.value.problems
    assert build_lexicon.main(["--data", str(data), "--execute"]) == 1
    assert list((data / "lexicon").glob("*.json")) == []
    capsys.readouterr()


def test_a_language_without_fixed_terms_stops_the_build(data):
    build_lexicon.fixed_path(data, "ar").unlink()
    with pytest.raises(build_lexicon.BuildError) as error:
        build_lexicon.build(data)
    assert "file not found" in error.value.problems[0]
