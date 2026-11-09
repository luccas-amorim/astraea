"""A run: for each source, list, fetch what is new, check, triage, record.

A failure of one source does not bring down the others, but it is not silent: the run
ends with code 2 and the source appears in the summary. An item that failed capture or
the sentinel is not marked as seen: it stays pending in the state and is retried in every
following run, even after leaving the date window.

A listing that fails midway **does not lose what it already listed**: the references read
until the error are fetched and triaged, the progress noted by the adapter is written, and
only the date of the last run does not advance. That is what keeps a long scan from
starting over from zero.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from astraea.engine import state
from astraea.engine.capture import Corpus
from astraea.engine.config import Config
from astraea.engine.contract import Document, Reference, Source
from astraea.engine.http import BlockedByRobots, redact
from astraea.engine.lexicon import Matcher
from astraea.engine.triage import Result, triage

log = logging.getLogger(__name__)

# Status of each report line.
TRIAGED = "triaged"
SENTINEL = "sentinel_rejected"
FAILED = "fetch_failed"
ROBOTS = "blocked_by_robots"

NOTHING, ERROR, NEEDS_READING = 0, 2, 3


@dataclass
class Line:
    ref: Reference
    status: str
    result: Result | None = None
    text_hash: str | None = None
    captured_at: str | None = None
    corpus: str | None = None
    error: str | None = None
    # Reference copy in the Wayback (`.../web/<ts>id_/<url>`), when known.
    snapshot: str | None = None
    # Headline read from the page, when the listing only brought the URL.
    headline: str | None = None

    @property
    def title(self) -> str | None:
        """The best title available: the source's, unless it is just the URL; else the headline."""
        ref = self.ref.title
        if ref and ref.strip() and ref.strip() != self.ref.url and not _looks_like_url(ref):
            return ref.strip()
        return (self.headline or ref or "").strip() or None

    @property
    def level(self) -> int | None:
        return self.result.level if self.result else None

    def as_dict(self) -> dict:
        ref = self.ref
        return {
            "source": ref.source,
            "source_id": ref.source_id,
            "url": ref.url,
            "title": self.title,
            "published_at": ref.published_at.isoformat() if ref.published_at else None,
            "captured_at": self.captured_at,
            "text_hash": self.text_hash,
            "status": self.status,
            **(self.result.as_dict() if self.result else {"level": None}),
            "corpus": self.corpus,
            "snapshot": self.snapshot,
            "error": self.error,
        }


@dataclass
class Run:
    id: str
    lexicon_id: str
    lexicon_version: str
    mode: str  # "run" or "retriage"
    start: str
    end: str | None = None
    lines: list[Line] = field(default_factory=list)
    source_failures: dict[str, str] = field(default_factory=dict)
    # Sources whose listing stopped on purpose (slice limit per run) and continues in the
    # next one. Not a failure: it is the date of the last run that does not advance.
    incomplete: dict[str, str] = field(default_factory=dict)
    since: dict[str, str] = field(default_factory=dict)

    @property
    def needs_reading(self) -> bool:
        return any((line.level or 0) >= 2 for line in self.lines)

    @property
    def exit_code(self) -> int:
        """2 if some source failed (the report also says whether reading is pending)."""
        if self.source_failures:
            return ERROR
        if self.needs_reading:
            return NEEDS_READING
        return NOTHING


def new_run(matcher: Matcher, mode: str, now: datetime | None = None) -> Run:
    now = (now or datetime.now(UTC)).replace(microsecond=0)
    lex = matcher.lexicon
    return Run(
        id=now.strftime("%Y%m%dT%H%M%SZ"),
        lexicon_id=lex.id,
        lexicon_version=lex.version,
        mode=mode,
        start=now.isoformat(),
    )


def _snapshot(ref: Reference) -> str | None:
    return (ref.data or {}).get("snapshot") if ref.data else None


def _looks_like_url(text: str) -> bool:
    return bool(re.match(r"^(https?://|www\.)\S+$", text.strip()))


def triaged_line(doc: Document, matcher: Matcher, path: str | None) -> Line:
    return Line(
        ref=doc.ref,
        status=TRIAGED,
        result=triage(doc, matcher),
        text_hash=doc.text_hash,
        captured_at=doc.captured_at.isoformat(),
        corpus=path,
        snapshot=_snapshot(doc.ref),
        headline=doc.highlights.get("headline") or doc.highlights.get("title"),
    )


def _list(source: Source, since: date, memory: state.State) -> Iterable[Reference]:
    if getattr(source, "uses_progress", False):
        return source.list(since, memory.progress)  # type: ignore[call-arg]
    return source.list(since)


def process_source(
    source: Source,
    matcher: Matcher,
    corpus: Corpus,
    memory: state.State,
    since: date,
    run: Run,
) -> None:
    run.since[source.id] = since.isoformat()
    references: list[Reference] = []
    try:
        for ref in _list(source, since, memory):
            references.append(ref)
    # Boundary with the adapter: any error of its own (a malformed feed is a SyntaxError)
    # is a failure of this source, never of the whole run. What was listed goes ahead.
    except Exception as error:  # noqa: BLE001
        message = redact(f"{type(error).__name__}: {error}")
        log.error("%s: listing failed: %s", source.id, message)
        run.source_failures[source.id] = f"listing: {message}"
    if reason := getattr(source, "incomplete_listing", None):
        run.incomplete[source.id] = str(reason)
    effective = getattr(source, "effective_since", None)
    if isinstance(effective, date) and effective != since:
        run.since[source.id] = f"{since.isoformat()} (effective {effective.isoformat()})"

    unique: dict[str, Reference] = {}
    for ref in [*references, *memory.pending_references()]:
        unique.setdefault(ref.source_id, ref)  # the one listed now beats the stored one
    new = [r for r in unique.values() if not memory.was_seen(r.source_id)]
    log.info(
        "%s: %d listed, %d pending, %d to fetch since %s",
        source.id, len(references), len(memory.pending), len(new), since,
    )  # fmt: skip
    for ref in new:
        try:
            doc = source.fetch(ref)
        except BlockedByRobots as error:
            run.lines.append(Line(ref, ROBOTS, error=redact(str(error))))
            # Policy, not failure: marking as seen avoids knocking on the same door every run.
            memory.resolve(ref.source_id, "")
            continue
        except Exception as error:  # noqa: BLE001 (same boundary)
            run.lines.append(Line(ref, FAILED, error=redact(f"{type(error).__name__}: {error}")))
            memory.add_pending(ref, FAILED)
            continue
        try:
            intact, path = corpus.write(doc, source)
        except Exception as error:  # noqa: BLE001 (the sentinel is adapter code)
            run.lines.append(Line(ref, FAILED, error=redact(f"sentinel: {error}")))
            memory.add_pending(ref, FAILED)
            continue
        if not intact:
            run.lines.append(
                Line(
                    ref,
                    SENTINEL,
                    text_hash=doc.text_hash,
                    corpus=corpus.relative(path),
                    snapshot=_snapshot(ref),
                )
            )
            memory.add_pending(ref, SENTINEL)
            continue
        run.lines.append(triaged_line(doc, matcher, corpus.relative(path)))
        memory.resolve(ref.source_id, doc.text_hash)


def run(
    config: Config,
    sources: Iterable[Source],
    matcher: Matcher,
    *,
    since: date | None = None,
    use_state: bool = True,
    today: date | None = None,
    now: datetime | None = None,
) -> Run:
    today = today or (now.date() if now else date.today())
    result = new_run(matcher, "run", now)
    corpus = Corpus(config.corpus, store=config.store_text)
    for source in sources:
        memory = state.read(config.state, source.id) if use_state else state.State(source.id)
        start = since
        if start is None and memory.last_run:
            # The source may declare its own margin (one that publishes late).
            margin = getattr(source, "margin_days", config.margin_days)
            start = memory.last_run - timedelta(days=margin)
        if start is None:
            start = config.since or today - timedelta(days=7)
        process_source(source, matcher, corpus, memory, start, result)
        if use_state:
            # Seen, pending and progress are always written; the date only advances when
            # the listing finished entirely, so the next window covers what was missing.
            if source.id not in result.source_failures and source.id not in result.incomplete:
                memory.last_run = today
            state.write(config.state, memory)
    result.end = (now or datetime.now(UTC)).replace(microsecond=0).isoformat()
    return result


def retriage(config: Config, matcher: Matcher, source: str | None = None) -> Run:
    """Applies the current lexicon to the stored corpus, offline. For when the lexicon changes."""
    result = new_run(matcher, "retriage")
    corpus = Corpus(config.corpus)
    for doc, path in corpus.documents(source):
        result.lines.append(triaged_line(doc, matcher, corpus.relative(path)))
    result.end = datetime.now(UTC).replace(microsecond=0).isoformat()
    return result
