"""RSS 2.0 and Atom, generic. Serves any outlet, court, blog or repository that publishes a feed.

The feed is only for listing. The text always comes from the item's page: a feed summary
is a summary, and triage never decides on the summary.

Configuration:
    {"type": "rss", "id": "rss:un-news-en", "url": "https://.../rss.xml",
     "rate_limit_per_minute": 20, "min_chars": 400}
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterator
from datetime import date, datetime
from email.utils import parsedate_to_datetime

from astraea.engine.capture import build_document
from astraea.engine.contract import Document, Reference
from astraea.engine.http import Client, Response, Transport, urllib_transport
from astraea.engine.text import Page, decode

_ATOM = "{http://www.w3.org/2005/Atom}"

# Error page served with HTTP 200. Looked for only at the start of a short text: an error
# page is short and says what it is right away. A long article whose headline says "access
# denied" must not be rejected for it: a false negative costs more than a false positive.
ERROR_PAGE_LIMIT = 2500
ERROR_MARKS = (
    "página não encontrada",
    "pagina nao encontrada",
    "page not found",
    "404 not found",
    "acesso negado",
    "access denied",
    "verifique se você é humano",
    "are you a robot",
    "captcha",
    "just a moment",
)


def _date(text: str | None) -> date | None:
    if not text:
        return None
    text = text.strip()
    try:
        return parsedate_to_datetime(text).date()  # RSS: RFC 822
    except (TypeError, ValueError, IndexError):
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()  # Atom: RFC 3339
    except ValueError:
        return None


def _text(node: ET.Element | None) -> str | None:
    return node.text.strip() if node is not None and node.text and node.text.strip() else None


def _description(text: str | None) -> dict | None:
    """Kept for the domains whose page is not fetched by policy (astraea.engine.policy).

    Triage never decides on it otherwise: the text comes from the page.
    """
    return {"description": text} if text else None


def read_feed(content: bytes, source: str) -> Iterator[Reference]:
    root = ET.fromstring(content)
    for item in root.iter("item"):  # RSS 2.0
        link = _text(item.find("link"))
        if not link:
            continue
        yield Reference(
            source=source,
            source_id=_text(item.find("guid")) or link,
            url=link,
            title=_text(item.find("title")),
            published_at=_date(_text(item.find("pubDate"))),
            data=_description(_text(item.find("description"))),
        )
    for entry in root.iter(f"{_ATOM}entry"):
        links = entry.findall(f"{_ATOM}link")
        alternate = [n for n in links if n.get("rel", "alternate") == "alternate"]
        link = (alternate or links or [None])[0]
        url = link.get("href") if link is not None else None
        if not url:
            continue
        published = _text(entry.find(f"{_ATOM}published")) or _text(entry.find(f"{_ATOM}updated"))
        yield Reference(
            source=source,
            source_id=_text(entry.find(f"{_ATOM}id")) or url,
            url=url,
            title=_text(entry.find(f"{_ATOM}title")),
            published_at=_date(published),
            data=_description(_text(entry.find(f"{_ATOM}summary"))),
        )


class Rss:
    respects_robots = True

    def __init__(
        self,
        id: str,
        url: str,
        client: Client,
        rate_limit_per_minute: int = 20,
        min_chars: int = 400,
    ) -> None:
        self.id = id
        self.url = url
        self.client = client
        self.rate_limit_per_minute = rate_limit_per_minute
        self.min_chars = min_chars

    @classmethod
    def from_config(cls, cfg: dict, transport: Transport = urllib_transport) -> Rss:
        limit = int(cfg.get("rate_limit_per_minute", 20))
        client = Client(limit, respects_robots=cls.respects_robots, transport=transport)
        return cls(cfg["id"], cfg["url"], client, limit, int(cfg.get("min_chars", 400)))

    def list(self, since: date) -> Iterator[Reference]:
        response = self.client.request(self.url)
        for ref in read_feed(response.body, self.id):
            # An item without a date goes in: losing an item is worse than re-reading one.
            if ref.published_at is None or ref.published_at >= since:
                yield ref

    def fetch(self, ref: Reference) -> Document:
        return html_document(ref, self.client.request(ref.url), ref.title)

    def sentinel(self, doc: Document) -> bool:
        return page_is_intact(doc, self.min_chars)


def html_document(ref: Reference, response: Response, headline: str | None = None) -> Document:
    """An HTML page as a Document: visible text, with headline and standfirst as highlights.

    Shared by every adapter that fetches an outlet's page (rss, gdelt, curated_list).
    """
    html, _ = decode(response.body, response.headers.get("content-type"))
    page = Page(html)
    headline = headline or page.headline or ""
    text = page.text
    if headline and headline not in text:
        text = f"{text}\n\n{headline}"
    highlights = {"headline": headline}
    if description := page.meta.get("og:description") or page.meta.get("description"):
        highlights["standfirst"] = description
        if description not in text:
            text = f"{text}\n\n{description}"
    return build_document(
        ref,
        text,
        raw=response.body,
        headers={
            k: v for k, v in response.headers.items() if k in ("content-type", "last-modified")
        },
        highlights=highlights,
    )


def page_is_intact(doc: Document, min_chars: int, marks=ERROR_MARKS) -> bool:
    """Text long enough and, if short, without the look of an error page."""
    if len(doc.text) < min_chars:
        return False
    if len(doc.text) >= ERROR_PAGE_LIMIT:
        return True
    head = doc.text[:300].lower()
    return not any(mark in head for mark in marks)
