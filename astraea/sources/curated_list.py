"""Curated list: URLs a person gathered by hand, in a versioned CSV.

Serves what no robot reaches by policy or for lack of an API: a court site behind a
challenge page whose acts a person found by browsing (the Inter-American Court, in
`docs/02-fontes.md`), documents found in manual consultation. The CSV has the header
`url,title,published_at` (the last two optional). The listing returns everything; the
source state prevents re-reading what was already seen.

Configuration:
    {"type": "curated_list", "id": "curated_list:iacthr", "file": "lists/iacthr.csv",
     "rate_limit_per_minute": 10, "stratum": "legal"}

`file` is relative to the configuration file.
"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from datetime import date
from pathlib import Path

from astraea.engine.contract import Document, Reference
from astraea.engine.http import Client, Transport, urllib_transport
from astraea.engine.url import normalize
from astraea.sources.rss import html_document, page_is_intact


class CuratedList:
    respects_robots = True

    def __init__(
        self,
        id: str,
        file: Path,
        client: Client,
        rate_limit_per_minute: int = 10,
        min_chars: int = 400,
    ) -> None:
        self.id = id
        self.file = Path(file)
        self.client = client
        self.rate_limit_per_minute = rate_limit_per_minute
        self.min_chars = min_chars

    @classmethod
    def from_config(cls, cfg: dict, transport: Transport = urllib_transport) -> CuratedList:
        limit = int(cfg.get("rate_limit_per_minute", 10))
        base = Path(cfg.get("_config_dir", "."))
        client = Client(limit, respects_robots=True, transport=transport)
        return cls(cfg["id"], base / cfg["file"], client, limit, int(cfg.get("min_chars", 400)))

    def list(self, since: date) -> Iterator[Reference]:
        with self.file.open(encoding="utf-8", newline="") as f:
            for line in csv.DictReader(f):
                url = (line.get("url") or "").strip()
                if not url:
                    continue
                published = (line.get("published_at") or "").strip()
                try:
                    day = date.fromisoformat(published) if published else None
                except ValueError:
                    day = None
                yield Reference(
                    source=self.id,
                    source_id=normalize(url),
                    url=url,
                    title=(line.get("title") or "").strip() or None,
                    published_at=day,
                    data={"via": self.file.name},
                )

    def fetch(self, ref: Reference) -> Document:
        return html_document(ref, self.client.request(ref.url), ref.title)

    def sentinel(self, doc: Document) -> bool:
        return page_is_intact(doc, self.min_chars)
