"""The run report in two sizes.

The full one has one line per item, discarded ones included, with the reason: three
seconds of reading per line, and the filter's decision stays auditable. The summary has
only what calls for action, and it is what becomes an issue body.
"""

from __future__ import annotations

from pathlib import Path

from astraea.engine.outputs.jsonl import counts
from astraea.engine.run import FAILED, ROBOTS, SENTINEL, TRIAGED, Line, Run


def _cell(text: str | None) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def _title(line: Line) -> str:
    title = _cell(line.title) or line.ref.source_id
    return f"[{title[:120]}]({line.ref.url})"


def _header(run: Run) -> list[str]:
    c = counts(run)
    parts = [f"{k}: {v}" for k, v in {**c["status"], **c["reason"]}.items()]
    lines = [
        f"# Astraea: run {run.id} ({run.mode})",
        "",
        f"Lexicon `{run.lexicon_id}` version `{run.lexicon_version}`. "
        f"Start {run.start}, end {run.end}.",
        "",
        f"Counts: {', '.join(parts) or 'no items'}.",
    ]
    if run.since:
        windows = ", ".join(f"`{s}` since {d}" for s, d in run.since.items())
        lines += ["", f"Windows: {windows}."]
    return lines


def _section(title: str, lines: list[Line], with_excerpt: bool) -> list[str]:
    if not lines:
        return []
    out = ["", f"## {title} ({len(lines)})", ""]
    for line in lines:
        r = line.result
        detail = ""
        if r is not None:
            keys = ", ".join(f"`{k}`" for k in r.keys)
            detail = f" level {r.level}, `{r.reason}`" + (f", {keys}" if keys else "")
        elif line.error:
            detail = f" {_cell(line.error)[:200]}"
        copy = f" · [copy]({line.snapshot})" if line.snapshot else ""
        out.append(f"- {_title(line)} ({line.ref.source}){detail}{copy}")
        if with_excerpt and r is not None and r.excerpt:
            out.append(f"  > {_cell(r.excerpt)} *({r.where})*")
    return out


def _groups(run: Run) -> dict[str, list[Line]]:
    triaged = [line for line in run.lines if line.status == TRIAGED]
    return {
        "accepted": [line for line in triaged if line.level == 3],
        "review": [line for line in triaged if line.level == 2],
        "level1": [line for line in triaged if line.level == 1],
        "level0": [line for line in triaged if line.level == 0],
        "failures": [line for line in run.lines if line.status in (FAILED, SENTINEL)],
        "robots": [line for line in run.lines if line.status == ROBOTS],
    }


def _source_failures(run: Run) -> list[str]:
    out: list[str] = []
    if run.source_failures:
        out += ["", f"## Sources that failed ({len(run.source_failures)})", ""]
        out += [f"- `{s}`: {_cell(e)[:300]}" for s, e in run.source_failures.items()]
        if run.needs_reading:
            out += [
                "",
                "There are items that need reading in this run, besides the failures above.",
            ]
    if run.incomplete:
        out += ["", f"## Listings that continue in the next run ({len(run.incomplete)})", ""]
        out += [f"- `{s}`: {_cell(e)[:300]}" for s, e in run.incomplete.items()]
    return out


def summary(run: Run) -> str:
    g = _groups(run)
    body = _header(run) + _source_failures(run)
    body += _section("Needs review", g["review"], with_excerpt=True)
    body += _section("Accepted", g["accepted"], with_excerpt=True)
    body += _section("Capture or integrity failures", g["failures"], with_excerpt=False)
    if not (g["review"] or g["accepted"] or g["failures"] or run.source_failures):
        body += ["", "Nothing needs reading in this run."]
    return "\n".join(body) + "\n"


def full(run: Run) -> str:
    g = _groups(run)
    body = _header(run) + _source_failures(run)
    body += _section("Needs review", g["review"], with_excerpt=True)
    body += _section("Accepted", g["accepted"], with_excerpt=True)
    body += _section("Capture or integrity failures", g["failures"], with_excerpt=False)
    body += _section("Blocked by robots.txt", g["robots"], with_excerpt=False)
    body += _section("Discarded at level 1", g["level1"], with_excerpt=True)
    body += _section("Discarded at level 0", g["level0"], with_excerpt=False)
    return "\n".join(body) + "\n"


def write(run: Run, folder: Path) -> None:
    (folder / "report-summary.md").write_text(summary(run), encoding="utf-8")
    (folder / "report-full.md").write_text(full(run), encoding="utf-8")
