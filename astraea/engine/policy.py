"""Text-and-data-mining opt-outs: the domains whose pages the robot does not fetch.

Some outlets reserve text and data mining expressly (El País and EFE under art. 67.3 of
the Spanish RDL 24/2021, Al Jazeera in clause 6 of its terms, Amnesty International in
its terms). Astraea honours that (docs/02-fontes.md, 2.2): on those domains the page is
never fetched; the item is triaged by the title and the description that the listing
already brought, and its level is capped at 2 with the reason `no_text_by_policy`, so a
person reads it before anything is recorded as accepted.

The list is not kept in code: it is every source of `data/sources.json` with
`no_text_by_policy: true`, by the host of its `url`. A host covers its subdomains
(`elpais.com` covers `feeds.elpais.com`); `www.` is ignored.

New in Astraea: Alétheia fetched every page.
"""

from __future__ import annotations

import json
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

from astraea.engine.capture import build_document
from astraea.engine.contract import Document, Reference
from astraea.engine.text import html_to_text

NO_TEXT = "no_text_by_policy"
MAX_LEVEL = 2


def host(url: str) -> str:
    name = (urllib.parse.urlsplit(url).hostname or "").lower().rstrip(".")
    return name[4:] if name.startswith("www.") else name


@dataclass(frozen=True)
class Policy:
    no_text_domains: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_registry(cls, path: str | Path) -> Policy:
        """Reads `data/sources.json`: the hosts of the sources with `no_text_by_policy`."""
        sources = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(sources, list):
            raise ValueError(f"{path}: expected a list of sources")
        domains = {
            host(s["url"])
            for s in sources
            if isinstance(s, dict) and s.get("no_text_by_policy") is True and s.get("url")
        }
        return cls(frozenset(d for d in domains if d))

    def no_text(self, url: str) -> bool:
        name = host(url)
        return any(name == d or name.endswith(f".{d}") for d in self.no_text_domains)


def metadata_document(ref: Reference) -> Document:
    """The item as the listing gave it: title and description, never the page.

    The description may come with markup (RSS often carries HTML); only its text stays.
    """
    title = (ref.title or "").strip()
    description = html_to_text(str((ref.data or {}).get("description") or "")).strip()
    text = "\n\n".join(part for part in (title, description) if part)
    doc = build_document(ref, text, highlights={"headline": title, "standfirst": description})
    doc.policy = NO_TEXT
    return doc
