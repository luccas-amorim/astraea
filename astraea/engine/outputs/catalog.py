"""The catalogue: one line per document, cumulative, in a versioned CSV.

| Column            | Content                                                               |
|-------------------|-----------------------------------------------------------------------|
| `id`              | 16 hex of the sha256 of the normalized URL: stable across runs        |
| `url`             | the origin address (without the Wayback prefix)                       |
| `domain`          | host, without `www.`                                                  |
| `stratum`         | that of the source that brought it first                              |
| `title`           | headline or title, as the source gave it                              |
| `published_at`    | date declared by the source; empty if unknown                         |
| `captured_at`     | timestamp of the Wayback capture used as reference                    |
| `snapshot`        | `https://web.archive.org/web/<ts>id_/<url>`, when there is one        |
| `text_hash`       | sha256 of the normalized text                                         |
| `level`           | 2 or 3 the first time                                                 |
| `keys`            | lexicon keys that matched, separated by `;`                           |
| `categories`      | lexicon facets, separated by `;`                                      |
| `first_run`       | id of the run in which it entered                                     |
| `lexicon_version` | version of the lexicon that decided                                   |

The file grows across runs and **never rewrites a line**: a document that comes back in
a later run, or through another channel, keeps the record of its first time. Two addresses
serving the same text (equal `text_hash`: `/amp/`, `/embed/`, republication) are one
document. The only exception is `snapshot`: when empty and later resolved, it is filled in
(see `complete_snapshots`). The catalogue describes documents, not people: the title is
the only text field and it comes from the source; there is no column of names.

Reading fills in any missing column, so a file written by an older version is completed
on the next write.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

from astraea.engine.run import TRIAGED, Run
from astraea.engine.url import domain, identity, original_from_wayback

COLUMNS = (
    "id",
    "url",
    "domain",
    "stratum",
    "title",
    "published_at",
    "captured_at",
    "snapshot",
    "text_hash",
    "level",
    "keys",
    "categories",
    "first_run",
    "lexicon_version",
)


def id_from_url(url: str) -> str:
    return identity(url)


def read(path: Path) -> list[dict[str, str]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as file:
        lines = list(csv.DictReader(file))
    out = []
    for line in lines:
        complete = {c: (line.get(c) or "") for c in COLUMNS}
        complete["url"] = original_from_wayback(complete["url"])
        complete["id"] = identity(complete["url"]) if complete["url"] else complete["id"]
        complete["domain"] = complete["domain"] or (
            domain(complete["url"]) if complete["url"] else ""
        )
        out.append(complete)
    return out


def _write(path: Path, lines: list[dict[str, str]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".csv.part")
    with temporary.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(lines)
    os.replace(temporary, path)


def _timestamp(snapshot: str | None) -> str:
    if not snapshot:
        return ""
    parts = snapshot.split("/web/", 1)
    return (
        parts[1].split("/", 1)[0].rstrip("abcdefghijklmnopqrstuvwxyz_") if len(parts) == 2 else ""
    )


def update(
    run: Run,
    path: Path,
    min_level: int = 3,
    stratum_of=lambda source: "general",
) -> int:
    """Appends the run's new documents with level >= `min_level`. Returns how many."""
    path = Path(path)
    lines = read(path)
    known = {line["id"] for line in lines}
    # The same text served under two URLs (`/amp/`, `/embed/`, republication) is one document.
    texts = {line["text_hash"] for line in lines if line.get("text_hash")}
    new = 0
    for item in run.lines:
        if item.status != TRIAGED or (item.level or 0) < min_level:
            continue
        url = original_from_wayback(item.ref.url)
        ident = identity(url)
        if ident in known or (item.text_hash and item.text_hash in texts):
            continue
        known.add(ident)
        if item.text_hash:
            texts.add(item.text_hash)
        r = item.result
        lines.append(
            {
                "id": ident,
                "url": url,
                "domain": domain(url),
                "stratum": stratum_of(item.ref.source),
                "title": (item.title or "").replace("\n", " ").strip(),
                "published_at": item.ref.published_at.isoformat() if item.ref.published_at else "",
                "captured_at": _timestamp(item.snapshot),
                "snapshot": item.snapshot or "",
                "text_hash": item.text_hash or "",
                "level": str(item.level or ""),
                "keys": ";".join(r.keys) if r else "",
                "categories": ";".join(r.categories) if r else "",
                "first_run": run.id,
                "lexicon_version": run.lexicon_version,
            }
        )
        new += 1
    if new or not path.exists() or _needs_migration(path):
        _write(path, lines)
    return new


def _needs_migration(path: Path) -> bool:
    with Path(path).open(encoding="utf-8", newline="") as file:
        header = next(csv.reader(file), [])
    return tuple(header) != COLUMNS


def complete_snapshots(path: Path, resolve) -> int:
    """Fills empty `snapshot`/`captured_at` using `resolve(url) -> (ts, url) | None`."""
    lines = read(path)
    filled = 0
    for line in lines:
        if line["snapshot"] or not line["url"]:
            continue
        found = resolve(line["url"])
        if found is None:
            continue
        line["captured_at"], line["snapshot"] = found
        filled += 1
    if filled:
        _write(path, lines)
    return filled
