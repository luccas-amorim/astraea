"""Capture: builds the Document with provenance and writes the full text to the corpus.

The file is first written as `.part` and only promoted to its final name when the
source's sentinel approves. A file at the canonical path means "intact", by construction:
whoever scans the corpus does not need to read metadata to know it can be trusted. A
rejected `.part` stays in the directory for diagnosis and does not match `*.json`.

Astraea runs with `store_text: false` (AGENTS.md, rule 2: never third-party full text):
the text is read, triaged and discarded, and nothing is written here.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path

from astraea.engine.contract import Document, Reference, Source
from astraea.engine.text import normalize, sha256


def build_document(
    ref: Reference,
    text: str,
    *,
    raw: bytes | None = None,
    headers: dict[str, str] | None = None,
    highlights: dict[str, str] | None = None,
    now: datetime | None = None,
) -> Document:
    """The only place that computes the hash and the capture date. Adapters call this."""
    text = normalize(text)
    return Document(
        ref=ref,
        text=text,
        captured_at=(now or datetime.now(UTC)).replace(microsecond=0),
        text_hash=sha256(text),
        raw=raw,
        headers=dict(headers or {}),
        highlights={k: normalize(v) for k, v in (highlights or {}).items() if v and v.strip()},
    )


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_") or "_"


def document_to_dict(doc: Document) -> dict:
    ref = asdict(doc.ref)
    ref.pop("data", None)
    if isinstance(doc.ref.published_at, date):
        ref["published_at"] = doc.ref.published_at.isoformat()
    return {
        "ref": ref,
        "text": doc.text,
        "captured_at": doc.captured_at.isoformat(),
        "text_hash": doc.text_hash,
        "headers": doc.headers,
        "highlights": doc.highlights,
    }


def document_from_dict(data: dict) -> Document:
    ref = dict(data["ref"])
    if ref.get("published_at"):
        ref["published_at"] = date.fromisoformat(ref["published_at"])
    return Document(
        ref=Reference(**ref),
        text=data["text"],
        captured_at=datetime.fromisoformat(data["captured_at"]),
        text_hash=data["text_hash"],
        headers=data.get("headers", {}),
        highlights=data.get("highlights", {}),
    )


class Corpus:
    """`<root>/<source>/<hash>.json`: one file per distinct text within the source.

    The same text arriving under another id of the same source (republication) lands in
    the same file, and the stored reference becomes that of the latest capture. The report
    and the run JSONL keep both.

    With `store=False` nothing is written: the sentinel checks the document in memory,
    triage reads the text and it is discarded. It is the choice of whoever wants only the
    catalogue (URL and identifiers), at the price of not being able to re-triage without
    fetching again.
    """

    def __init__(self, root: Path, store: bool = True) -> None:
        self.root = Path(root)
        self.store = store

    def relative(self, path: Path | None) -> str | None:
        """The path as it goes to the output: relative to the data directory, portable."""
        if path is None:
            return None
        return Path(path).relative_to(self.root.parent).as_posix()

    def path(self, doc: Document) -> Path:
        return self.root / safe_name(doc.ref.source) / f"{doc.text_hash}.json"

    def write(self, doc: Document, source: Source) -> tuple[bool, Path | None]:
        """(intact, path). Writes `.part`, asks the sentinel, promotes if it passes."""
        if not self.store:
            return source.sentinel(doc), None
        final = self.path(doc)
        final.parent.mkdir(parents=True, exist_ok=True)
        partial = final.with_suffix(".json.part")
        partial.write_text(
            json.dumps(document_to_dict(doc), ensure_ascii=False, indent=1), encoding="utf-8"
        )
        if not source.sentinel(doc):
            return False, partial
        os.replace(partial, final)
        return True, final

    def documents(self, source: str | None = None) -> Iterator[tuple[Document, Path]]:
        folders = [self.root / safe_name(source)] if source else sorted(self.root.glob("*"))
        for folder in folders:
            for file in sorted(folder.glob("*.json")):
                yield document_from_dict(json.loads(file.read_text(encoding="utf-8"))), file
