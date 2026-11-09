"""Observations: one line per sighting (document × channel × source × run).

It is the capture-recapture matrix. The catalogue says **what** exists; the observations
say **who saw what, when**, and `estimate` draws from them the overlap between channels
and the accumulation curve. Append only; never rewrite. Documents below `min_level`
(default 2) are left out: what the lexicon neither accepted nor left in doubt is not
"seen".

| Column         | Content                                                 |
|----------------|---------------------------------------------------------|
| `id`           | the same id as the catalogue (normalized URL)           |
| `channel`      | prefix of the source id (`gdelt`, `rss`, ...)           |
| `source`       | source id                                               |
| `run`          | run id                                                  |
| `level`        | triage level in this sighting                           |
| `published_at` | declared or capture date, to align windows              |
| `text_hash`    | to count one document served under two URLs as one      |
| `url`          | the origin address                                      |
"""

from __future__ import annotations

import csv
from pathlib import Path

from astraea.engine.estimate import channel
from astraea.engine.run import TRIAGED, Run
from astraea.engine.url import identity, original_from_wayback

COLUMNS = ("id", "channel", "source", "run", "level", "published_at", "text_hash", "url")


def append(run: Run, path: Path, min_level: int = 2) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    written = 0
    with path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        if new:
            writer.writeheader()
        for item in run.lines:
            if item.status != TRIAGED or (item.level or 0) < min_level:
                continue
            url = original_from_wayback(item.ref.url)
            writer.writerow(
                {
                    "id": identity(url),
                    "channel": channel(item.ref.source),
                    "source": item.ref.source,
                    "run": run.id,
                    "level": item.level,
                    "published_at": item.ref.published_at.isoformat()
                    if item.ref.published_at
                    else "",
                    "text_hash": item.text_hash or "",
                    "url": url,
                }
            )
            written += 1
    return written
