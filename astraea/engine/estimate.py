"""How much is missing: an estimate of the total from the overlap between channels.

It is the capture-recapture technique, the same used to count fish in a lake. If channel A
finds `n1` documents, B finds `n2` and `m` are in both, the estimated total is
~ `n1 · n2 / m`. Here the Chapman form is used, which does not blow up when `m` is small,
and, for three channels or more, the Chao estimator, which uses how many documents were
seen by a single channel (`f1`) and by exactly two (`f2`) and is a **floor** robust to
heterogeneity (a popular page is easier to find than an obscure one).

Rules the code enforces:

- **A channel is the prefix of the source id** (`rss:bbc` and `rss:dw` are the same
  channel, `rss`). Treated as separate channels, sources of one kind that barely overlap
  would make almost every document "seen by a single channel" and blow the estimate up.
- **Only channels of the same stratum are compared.** Each source declares `"stratum"` in
  the configuration, and the report comes out per stratum.
- **The unit is the document**, not the URL: the `id` is that of the normalized URL and,
  when two URLs serve the same text (equal `text_hash`), they count once.
- **Window**: GDELT only keeps ~90 days. A pair with a short-window channel is only
  comparable when `--since` restricts both to the same window; otherwise, the report
  shows the pair marked as **not comparable** instead of a meaningless number.

The caveats go in the report because they are part of the number: the channels are not
independent (all favour what is popular), and positive dependence pushes the estimate
**below** the real value. Read it as a floor. The accumulation curve (how many new
documents each run brought) says whether the search is saturating, which no estimator
says on its own.

Input: `observations.csv` (one line per sighting: document, channel, source, run, level).
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from itertools import combinations
from pathlib import Path

from astraea.engine.url import normalize as normalize_url  # noqa: F401  (re-exported)

# Channels whose listing only reaches a short window; comparison without `--since` is void.
SHORT_WINDOW = {"gdelt"}


@dataclass
class Pair:
    a: str
    b: str
    n1: int
    n2: int
    m: int
    comparable: bool = True

    @property
    def chapman(self) -> float:
        return (self.n1 + 1) * (self.n2 + 1) / (self.m + 1) - 1

    @property
    def interval(self) -> tuple[float, float]:
        n1, n2, m = self.n1, self.n2, self.m
        var = (n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m) / ((m + 1) ** 2 * (m + 2))
        sd = math.sqrt(var)
        return max(self.n1 + self.n2 - self.m, self.chapman - 1.96 * sd), self.chapman + 1.96 * sd


@dataclass
class Estimate:
    by_channel: dict[str, set[str]]
    curve: list[tuple[str, int, int]] = field(default_factory=list)  # run, new, total
    aligned: bool = False  # True when `since` restricted every channel to the same window

    @property
    def observed(self) -> set[str]:
        return set().union(*self.by_channel.values()) if self.by_channel else set()

    @property
    def frequencies(self) -> Counter:
        """How many documents were seen by exactly k channels."""
        count = Counter(u for urls in self.by_channel.values() for u in urls)
        return Counter(count.values())

    @property
    def comparable_channels(self) -> list[str]:
        return [c for c in sorted(self.by_channel) if self.aligned or c not in SHORT_WINDOW]

    @property
    def chao(self) -> float | None:
        channels = self.comparable_channels
        if len(channels) < 2:
            return None
        count = Counter(u for c in channels for u in self.by_channel[c])
        s = len(count)
        f = Counter(count.values())
        f1, f2 = f.get(1, 0), f.get(2, 0)
        return s + (f1 * f1 / (2 * f2) if f2 else f1 * (f1 - 1) / 2)

    @property
    def pairs(self) -> list[Pair]:
        return [
            Pair(a, b, len(self.by_channel[a]), len(self.by_channel[b]),
                 len(self.by_channel[a] & self.by_channel[b]),
                 comparable=self.aligned or not ({a, b} & SHORT_WINDOW))
            for a, b in combinations(sorted(self.by_channel), 2)
        ]  # fmt: skip


def channel(source: str) -> str:
    return source.split(":", 1)[0]


def compute(
    observations: Path,
    min_level: int = 2,
    stratum_of: Callable[[str], str] = lambda source: "general",
    since: date | None = None,
) -> dict[str, Estimate]:
    """One estimate per stratum, from `observations.csv`. `stratum_of` gets the source id."""
    by_stratum: dict[str, Estimate] = {}
    observations = Path(observations)
    if not observations.exists():
        return by_stratum
    with observations.open(encoding="utf-8", newline="") as file:
        lines = list(csv.DictReader(file))
    # Document = text hash when there is one; otherwise, the id of the normalized URL.
    unit = {line["id"]: (line.get("text_hash") or line["id"]) for line in lines}
    by_run: dict[str, list[dict]] = {}
    for line in lines:
        by_run.setdefault(line["run"], []).append(line)
    accumulated: dict[str, set[str]] = {}
    for run in sorted(by_run):
        before = {e: len(v) for e, v in accumulated.items()}
        for line in by_run[run]:
            try:
                level = int(line.get("level") or 0)
            except ValueError:
                level = 0
            if level < min_level:
                continue
            published = line.get("published_at") or ""
            if since and (not published or date.fromisoformat(published) < since):
                continue
            stratum = stratum_of(line["source"])
            est = by_stratum.setdefault(stratum, Estimate({}, aligned=since is not None))
            doc = unit[line["id"]]
            est.by_channel.setdefault(channel(line["source"]), set()).add(doc)
            accumulated.setdefault(stratum, set()).add(doc)
        for stratum, docs in accumulated.items():
            new = len(docs) - before.get(stratum, 0)
            if new or stratum in by_stratum:
                by_stratum[stratum].curve.append((run, new, len(docs)))
    return by_stratum


def report(strata: dict[str, Estimate], since: date | None = None) -> str:
    lines = ["# Coverage estimate", ""]
    if since:
        lines += [f"Only items published or captured from {since.isoformat()} on.", ""]
    if not strata:
        return "\n".join([*lines, "No run with triaged items yet."]) + "\n"
    for name, est in sorted(strata.items()):
        lines += _stratum(name, est)
    lines += [
        "",
        "## How to read",
        "",
        "The channels are not independent, and the dependence pulls the estimate down: the "
        "numbers above are a floor. Real saturation is the curve flattening with new channels "
        "coming in, not just with the same channels repeating. A pair marked as not "
        "comparable joins a short-window channel (GDELT, ~90 days) with a long-window one "
        "without `--since`: the number would come out huge and say nothing.",
    ]
    return "\n".join(lines) + "\n"


def _stratum(name: str, est: Estimate) -> list[str]:
    total = len(est.observed)
    lines = [f"## Stratum `{name}`", "", f"Distinct documents observed: **{total}**.", ""]

    lines += ["| Channel | Documents | Only in this channel |", "|---|---|---|"]
    count = Counter(u for urls in est.by_channel.values() for u in urls)
    for ch, urls in sorted(est.by_channel.items()):
        exclusive = sum(1 for u in urls if count[u] == 1)
        mark = "" if ch in est.comparable_channels else " (short window; outside the floor)"
        lines.append(f"| `{ch}`{mark} | {len(urls)} | {exclusive} |")

    if est.chao is not None:
        comparable = est.comparable_channels
        count_c = Counter(u for c in comparable for u in est.by_channel[c])
        f = Counter(count_c.values())
        observed_c = len(count_c)
        lines += [
            "",
            "**Estimated total**",
            "",
            f"- **Chao (floor, {len(comparable)} comparable channels):** {est.chao:,.0f} "
            f"(seen by a single channel: {f.get(1, 0)}; by exactly two: {f.get(2, 0)}).",
            f"- **Coverage:** at most {observed_c / est.chao:.0%} (observed ÷ floor)."
            if est.chao
            else "",
            "",
            "| Pair | n1 | n2 | in common | Chapman | 95% CI |",
            "|---|---|---|---|---|---|",
        ]
        for p in est.pairs:
            if not p.comparable:
                lines.append(
                    f"| `{p.a}` × `{p.b}` | {p.n1} | {p.n2} | {p.m} | not comparable | "
                    "use `--since` |"
                )
                continue
            low, high = p.interval
            lines.append(
                f"| `{p.a}` × `{p.b}` | {p.n1} | {p.n2} | {p.m} | {p.chapman:,.0f} | "
                f"{low:,.0f} to {high:,.0f} |"
            )
        lines += [
            "",
            "A pair with nothing in common gives a huge and unstable estimate: it does not say "
            "the total is huge, it says the two channels look at different places.",
        ]
    else:
        lines += [
            "",
            "With a single comparable channel there is no estimate: at least two are needed "
            "(a short-window channel only counts with `--since`).",
        ]

    lines += ["", "**Accumulation curve**", "", "| Run | New | Total |", "|---|---|---|"]
    lines += [f"| {r} | {new} | {acc} |" for r, new, acc in est.curve]
    return [*lines, ""]
