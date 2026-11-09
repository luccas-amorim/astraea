from astraea.engine.text import Page, decode, fold, normalize


def test_cp1252_declared_as_latin1(fixtures):
    text, encoding = decode((fixtures / "rss" / "article-carandiru.html").read_bytes())
    assert encoding == "cp1252"
    assert "Detenção de\nSão Paulo" in text


def test_http_header_beats_the_meta():
    raw = '<meta charset="cp1252"><p>ação</p>'.encode()
    text, encoding = decode(raw, "text/html; charset=utf-8")
    assert encoding == "utf-8"
    assert "ação" in text


def test_utf16_with_bom_and_stray_byte():
    raw = "﻿Lei penal".encode("utf-16-le") + b" "
    raw = b"\xff\xfe" + raw[2:]
    text, encoding = decode(raw)
    assert encoding == "utf-16"
    assert text.strip("﻿") == "Lei penal"


def test_without_declaration_tries_utf8_and_falls_back_to_cp1252():
    assert decode("ação".encode())[1] == "utf-8"
    assert decode("ação".encode("cp1252"))[1] == "cp1252"


def test_page_ignores_script_nav_and_footer(fixtures):
    html, _ = decode((fixtures / "rss" / "article-carandiru.html").read_bytes())
    page = Page(html)
    assert "Pavilhão 9" in page.text
    assert "publicidade" not in page.text
    assert "Especial Carandiru" not in page.text
    assert "o filme" not in page.text
    assert page.headline.startswith("Massacre do Carandiru")
    assert page.meta["description"].startswith("Familiares")


def test_fold_keeps_the_length():
    original = "AÇÃO Penal — São Paulo, ÍNDIO, ﬁm, İstanbul"
    folded = fold(original)
    assert len(folded) == len(original)
    assert folded.startswith("acao penal — sao paulo, indio")


def test_normalize_collapses_spaces_and_lines():
    assert normalize("a\xa0 b\r\n\n\n\n c  ") == "a b\n\nc"
