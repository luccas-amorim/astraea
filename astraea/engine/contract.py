"""The contract every source adapter fulfils.

Three functions and a block of metadata. The engine does not know what a court or a
newspaper is: it knows how to list, fetch and ask whether what it fetched is intact.
Everything specific to the origin stays inside the adapter, with a fixture and a test
that run without network.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class Reference:
    """What `list` returns: enough to decide whether to fetch, nothing more."""

    source: str  # adapter id, e.g. "rss:un-news-en"
    source_id: str  # stable identifier inside the origin
    url: str
    title: str | None = None
    published_at: date | None = None
    # What the listing already brought and the adapter wants to reuse in `fetch`
    # (e.g. the whole record of an API). Not part of equality.
    data: Mapping[str, Any] | None = field(default=None, compare=False, hash=False)


@dataclass
class Document:
    """What `fetch` returns: the whole item, with provenance."""

    ref: Reference
    text: str  # normalized UTF-8, no markup
    captured_at: datetime
    text_hash: str  # sha256 of the normalized text
    raw: bytes | None = None  # raw HTML/JSON, when there is one
    headers: dict[str, str] = field(default_factory=dict)
    # Passages the source itself marks as strong: summary, operative part, headline,
    # subjects. A term found here is what takes triage to level 3.
    # Every highlight must also be in `text`: triage counts terms in the text.
    highlights: dict[str, str] = field(default_factory=dict)
    # Set when the text is not the page's by policy: `"no_text_by_policy"` means only the
    # listing's title and description were read (astraea.engine.policy). Triage caps it.
    policy: str | None = None


@runtime_checkable
class Source(Protocol):
    """An adapter. Instances are configured by the consumer (keys, queries)."""

    id: str
    rate_limit_per_minute: int  # declared by the adapter; the engine obeys
    respects_robots: bool  # True, except for a source that publishes its own API
    # Optional: `margin_days: int`, how far to go back before the last run. A source
    # that publishes late declares its own; without it, the configuration margin applies.
    # Optional: `uses_progress: bool`, see `list`.
    # Optional: `effective_since: date`, the window the source actually queried when it
    # is shorter than the one asked for (GDELT keeps only ~90 days); goes to the report.
    # Optional: `incomplete_listing: str`, set when the listing stopped on purpose and
    # continues in the next run.

    def list(self, since: date) -> Iterable[Reference]:
        """Enumerates what the source published from `since` on.

        May paginate internally. Does not fetch text. Must be idempotent: calling twice
        with the same date returns the same references.

        A long-scan adapter declares `uses_progress = True` and receives a second
        argument, `progress: dict`, which the engine keeps in the source state between
        runs. The adapter notes there what it has finished (slices, cursors) and, in the
        next run, continues where it stopped. If the listing is interrupted by an error,
        what was noted before the error is preserved.
        """

    def fetch(self, ref: Reference) -> Document:
        """Fetches the whole item and normalizes the encoding here, once.

        Never decides on the summary: if the origin only gives the summary in the
        listing, this is where the full item is fetched.
        """

    def sentinel(self, doc: Document) -> bool:
        """Says whether the document is intact.

        Error pages served with HTTP 200, truncated text, "no results" and captchas are
        rejected here, before triage. Failing is cheap; accepting bad text contaminates
        the run silently.
        """
