"""JSONL: the boundary with the consumer. Every line carries the whole provenance."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from astraea import __version__
from astraea.engine.run import TRIAGED, Run


def _line(run: Run, data: dict) -> str:
    data = {**data, "lexicon": {"id": run.lexicon_id, "version": run.lexicon_version}}
    return json.dumps(data, ensure_ascii=False)


def _write(path: Path, lines: list[str]) -> None:
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")


def counts(run: Run) -> dict:
    by_status = Counter(line.status for line in run.lines)
    by_reason = Counter(line.result.reason for line in run.lines if line.result is not None)
    return {
        "status": dict(sorted(by_status.items())),
        "reason": dict(sorted(by_reason.items())),
    }


def write(run: Run, folder: Path) -> None:
    everything = [line.as_dict() for line in run.lines]
    _write(folder / "items.jsonl", [_line(run, d) for d in everything])
    for name, level in (("accepted.jsonl", 3), ("needs-review.jsonl", 2)):
        chosen = [d for d in everything if d["status"] == TRIAGED and d["level"] == level]
        _write(folder / name, [_line(run, d) for d in chosen])
    meta = {
        "id": run.id,
        "mode": run.mode,
        "engine": __version__,
        "lexicon": {"id": run.lexicon_id, "version": run.lexicon_version},
        "start": run.start,
        "end": run.end,
        "since": run.since,
        "source_failures": run.source_failures,
        "incomplete": run.incomplete,
        "needs_reading": run.needs_reading,
        "counts": counts(run),
        "exit_code": run.exit_code,
    }
    (folder / "run.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
