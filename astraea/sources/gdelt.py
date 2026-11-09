"""GDELT DOC 2.0: news from the whole world, full-text search, in dozens of languages.

API: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

The window is **rolling, of about three months**: GDELT serves surveillance (what is out
now), not a sweep of the past. A `since` earlier than that is cut to the limit, and the
report states the window used. (The source survey of 06/11/2026 found the API answering
for 2019; lifting this cut is phase 4 work, see `docs/06-roteiro.md`.)

Each query returns at most 250 articles. The adapter asks **one day at a time**; if a day
comes back full, it asks again in four six-hour bands, so as not to lose what went over
the cap. The text comes from the outlet's page, with its `robots.txt` respected.

Configuration:
    {"type": "gdelt", "id": "gdelt:genocide-en", "query": "genocide sourcelang:english",
     "rate_limit_per_minute": 12, "min_chars": 400}
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import date, datetime, timedelta

from astraea.engine.contract import Document, Reference
from astraea.engine.http import Client, Transport, urllib_transport
from astraea.sources.rss import html_document, page_is_intact

URL = "https://api.gdeltproject.org/api/v2/doc/doc"
CAP = 250
WINDOW_DAYS = 90


def _moment(day: date, hour: int = 0) -> str:
    return datetime(day.year, day.month, day.day, hour).strftime("%Y%m%d%H%M%S")


def _date(seen: str | None) -> date | None:
    try:
        return datetime.strptime((seen or "")[:8], "%Y%m%d").date()
    except ValueError:
        return None


class Gdelt:
    respects_robots = True  # applies to the outlets' pages

    def __init__(
        self,
        id: str,
        query: str,
        client: Client,
        rate_limit_per_minute: int = 12,
        min_chars: int = 400,
        today: Callable[[], date] = date.today,
    ) -> None:
        self.id = id
        self.query = query
        self.client = client
        self.rate_limit_per_minute = rate_limit_per_minute
        self.min_chars = min_chars
        self.today = today
        self.effective_since: date | None = None

    @classmethod
    def from_config(cls, cfg: dict, transport: Transport = urllib_transport) -> Gdelt:
        limit = int(cfg.get("rate_limit_per_minute", 12))
        client = Client(limit, respects_robots=cls.respects_robots, transport=transport)
        return cls(cfg["id"], cfg["query"], client, limit, int(cfg.get("min_chars", 400)))

    def _query(self, start: str, end: str) -> list[dict]:
        params = {
            "query": self.query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": CAP,
            "sort": "datedesc",
            "startdatetime": start,
            "enddatetime": end,
        }
        return self.client.request(URL, params=params).json().get("articles") or []

    def list(self, since: date) -> Iterator[Reference]:
        today = self.today()
        day = max(since, today - timedelta(days=WINDOW_DAYS))
        self.effective_since = day
        while day <= today:
            articles = self._query(_moment(day), _moment(day + timedelta(days=1)))
            if len(articles) >= CAP:
                articles = []
                for hour in (0, 6, 12, 18):
                    start = _moment(day, hour)
                    following = day + timedelta(days=1)
                    end = _moment(following) if hour == 18 else _moment(day, hour + 6)
                    articles += self._query(start, end)
            for article in articles:
                if article.get("url"):
                    yield Reference(
                        source=self.id,
                        source_id=article["url"],
                        url=article["url"],
                        title=article.get("title"),
                        published_at=_date(article.get("seendate")),
                        data={k: article.get(k) for k in ("domain", "language", "sourcecountry")},
                    )
            day += timedelta(days=1)

    def fetch(self, ref: Reference) -> Document:
        return html_document(ref, self.client.request(ref.url), ref.title)

    def sentinel(self, doc: Document) -> bool:
        return page_is_intact(doc, self.min_chars)
