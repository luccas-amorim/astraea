"""Decoding, text extraction from HTML and the folding used to match terms.

Decoding wrongly does not break: it corrupts silently and imitates old text (the lesson
from AtlasPen, with a government portal serving undeclared cp1252 and UTF-16 with a BOM).
That is why detection lives here, once, and the rest of the engine only sees normalized
UTF-8 text.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from html.parser import HTMLParser

_META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?\s*([A-Za-z0-9_\-]+)""", re.I)
_CT_CHARSET = re.compile(r"charset\s*=\s*\"?([A-Za-z0-9_\-]+)", re.I)


def decode(raw: bytes, content_type: str | None = None) -> tuple[str, str]:
    """(text, encoding). Order: BOM, HTTP header, meta charset, UTF-8, cp1252."""
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", errors="replace"), "utf-8-sig"
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        # An odd trailing byte in UTF-16 is edge garbage (seen in the wild), not content.
        body = raw[:-1] if len(raw) % 2 else raw
        return body.decode("utf-16", errors="replace"), "utf-16"

    candidates: list[str] = []
    if content_type and (m := _CT_CHARSET.search(content_type)):
        candidates.append(m.group(1))
    if m := _META_CHARSET.search(raw[:4096]):
        candidates.append(m.group(1).decode("ascii", errors="ignore"))
    candidates += ["utf-8", "cp1252"]

    for name in candidates:
        try:
            return raw.decode(_canonical(name)), _canonical(name)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("cp1252", errors="replace"), "cp1252"


def _canonical(name: str) -> str:
    name = name.strip().lower()
    # Declared iso-8859-1 is almost always cp1252 in practice (Word quotes and dashes).
    return "cp1252" if name in {"iso-8859-1", "latin-1", "latin1", "us-ascii"} else name


_IGNORE = {"script", "style", "noscript", "template", "svg", "nav", "footer", "aside", "form"}
_BLOCK = {
    "p", "div", "br", "li", "ul", "ol", "tr", "table", "section", "article", "header",
    "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "dd", "dt", "figcaption",
}  # fmt: skip


class _Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title: list[str] = []
        self.h1: list[str] = []
        self.meta: dict[str, str] = {}
        self._ignoring = 0
        self._inside: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _IGNORE:
            self._ignoring += 1
        if tag == "meta":
            a = {k.lower(): (v or "") for k, v in attrs}
            key = (a.get("property") or a.get("name") or "").lower()
            if key and "content" in a:
                self.meta.setdefault(key, a["content"])
        if tag in _BLOCK:
            self.parts.append("\n")
        self._inside.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "meta":
            self.handle_starttag(tag, attrs)
            self._inside.pop()
        elif tag in _BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _IGNORE and self._ignoring:
            self._ignoring -= 1
        if tag in _BLOCK:
            self.parts.append("\n")
        if tag in self._inside:
            while self._inside and self._inside.pop() != tag:
                pass

    def handle_data(self, data: str) -> None:
        if "title" in self._inside:
            self.title.append(data)
            return
        if self._ignoring:
            return
        if "h1" in self._inside:
            self.h1.append(data)
        self.parts.append(data)


class Page:
    """Visible text of an HTML page, plus what it declares about itself."""

    def __init__(self, html: str) -> None:
        extractor = _Extractor()
        extractor.feed(html)
        extractor.close()
        self.text = normalize("".join(extractor.parts))
        self.title = normalize(" ".join(extractor.title)) or None
        self.h1 = normalize(" ".join(extractor.h1)) or None
        self.meta = extractor.meta

    @property
    def headline(self) -> str | None:
        return self.meta.get("og:title") or self.h1 or self.title


def html_to_text(html: str) -> str:
    return Page(html).text


def normalize(text: str) -> str:
    """NFC, spaces collapsed per line, at most one blank line in a row."""
    text = unicodedata.normalize("NFC", text).replace("\xa0", " ").replace("\r", "")
    lines = [re.sub(r"[ \t\f\v]+", " ", line).strip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def fold(text: str) -> str:
    """Lowercase without accents, with ONE output character per input character.

    The 1:1 correspondence is what allows finding the term in the folded text and cutting
    the excerpt from the original text at the same indices.
    """
    out = []
    for c in text:
        base = "".join(x for x in unicodedata.normalize("NFD", c) if not unicodedata.combining(x))
        base = base.lower()
        out.append(base[0] if base else c)
    return "".join(out)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
