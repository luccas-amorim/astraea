"""What has already been seen, per source. It is the only memory between runs.

`<root>/<source>.json` keeps the date of the last completed run, the text hash of every id
already captured, the **pending** items (references whose capture failed or that the
sentinel rejected) and the listing **progress**: what the adapter has already covered in
a long scan (slices, cursors).

A pending item is retried in every run, even outside the date window; without that, an
item that failed once would leave the window and never be read again, silently. Progress
is what makes an interrupted listing continue where it stopped instead of starting over.
Deleting the file amounts to reading everything again.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from astraea.engine.capture import safe_name
from astraea.engine.contract import Reference

# `data` of a pending reference above this size is not kept: it may contain the item's
# text (names of people), and the adapter must be able to fetch again from the URL alone.
PENDING_DATA_LIMIT = 4000


@dataclass
class State:
    source: str
    last_run: date | None = None
    seen: dict[str, str] = field(default_factory=dict)  # source_id -> text_hash
    pending: dict[str, dict] = field(default_factory=dict)  # source_id -> reference
    progress: dict = field(default_factory=dict)  # the adapter's; opaque to the engine

    def was_seen(self, source_id: str) -> bool:
        return source_id in self.seen

    def add_pending(self, ref: Reference, reason: str) -> None:
        previous = self.pending.get(ref.source_id, {})
        data = asdict(ref)
        data["published_at"] = ref.published_at.isoformat() if ref.published_at else None
        extras = dict(ref.data) if ref.data is not None else None
        if extras is not None:
            size = len(json.dumps(extras, ensure_ascii=False))
            if size > PENDING_DATA_LIMIT:
                extras = None
        data["data"] = extras
        self.pending[ref.source_id] = {
            "ref": data,
            "reason": reason,
            "attempts": previous.get("attempts", 0) + 1,
        }

    def resolve(self, source_id: str, text_hash: str) -> None:
        self.pending.pop(source_id, None)
        self.seen[source_id] = text_hash

    def pending_references(self) -> list[Reference]:
        refs = []
        for item in self.pending.values():
            data = dict(item["ref"])
            if data.get("published_at"):
                data["published_at"] = date.fromisoformat(data["published_at"])
            refs.append(Reference(**data))
        return refs


def path(root: Path, source: str) -> Path:
    return Path(root) / f"{safe_name(source)}.json"


def read(root: Path, source: str) -> State:
    file = path(root, source)
    if not file.exists():
        return State(source)
    data = json.loads(file.read_text(encoding="utf-8"))
    last = data.get("last_run")
    return State(
        source,
        date.fromisoformat(last) if last else None,
        data.get("seen", {}),
        data.get("pending", {}),
        data.get("progress", {}),
    )


def write(root: Path, state: State) -> None:
    file = path(root, state.source)
    file.parent.mkdir(parents=True, exist_ok=True)
    temporary = file.with_suffix(".json.part")
    data = {
        "source": state.source,
        "last_run": state.last_run.isoformat() if state.last_run else None,
        "seen": dict(sorted(state.seen.items())),
        "pending": dict(sorted(state.pending.items())),
        "progress": state.progress,
    }
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(temporary, file)
