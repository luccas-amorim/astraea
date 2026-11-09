"""Outputs of a run. All written to `<runs>/<run id>-<mode>/`.

| File                  | Content                                                          |
|-----------------------|------------------------------------------------------------------|
| `items.jsonl`         | one line per item, every level and status (canonical)            |
| `accepted.jsonl`      | level 3 only, with provenance: what the consumer imports         |
| `needs-review.jsonl`  | level 2 only: what needs human reading                           |
| `report-full.md`      | one line per item, accepted and discarded, with the reason       |
| `report-summary.md`   | what calls for action: accepted, needs review, failures          |
| `run.json`            | metadata: lexicon, engine version, dates, counts                 |
"""

from __future__ import annotations

from pathlib import Path

from astraea.engine.outputs import jsonl, report
from astraea.engine.run import Run


def write(run: Run, root: Path) -> Path:
    folder = Path(root) / f"{run.id}-{run.mode}"
    folder.mkdir(parents=True, exist_ok=True)
    jsonl.write(run, folder)
    report.write(run, folder)
    return folder
