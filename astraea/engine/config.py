"""The run configuration: which lexicon, which sources, where to write.

    {
      "lexicon": "data/lexicon/en.json",
      "registry": "data/sources.json",
      "directory": ".",
      "since": "2026-11-01",
      "margin_days": 7,
      "store_text": false,
      "catalog": {"file": "catalog.csv", "min_level": 3},
      "observations": {"file": "observations.csv", "min_level": 2},
      "archive": {"resolve": true, "rate_limit_per_minute": 15},
      "sources": [{"type": "rss", "id": "rss:un-news-en",
                   "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
                   "stratum": "press"}]
    }

Relative paths are resolved from the configuration file. `state/`, `corpus/`, `runs/`, the
catalogue and the observations live in `directory`.

`registry` is `data/sources.json`: the run reads from it the domains with
`no_text_by_policy`, whose pages are never fetched (astraea.engine.policy). It is required
by `validate()` and by `astraea run`.

`stratum` is required for the estimate to make sense: capture-recapture only compares
channels that look at the same population. `validate()` refuses a stratum outside the list.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

STRATA = ("press", "historical-press", "academic", "legal", "memory", "general")


@dataclass(frozen=True)
class Config:
    lexicon: Path
    directory: Path
    sources: tuple[dict, ...]
    since: date | None = None
    # How far to go back before the last run: a source that publishes late or with a
    # backdated date does not escape. The state prevents re-reading what was already seen.
    margin_days: int = 2
    # False: the full text is read, triaged and discarded; nothing goes to `corpus/`.
    store_text: bool = True
    # {"file": "catalog.csv", "min_level": 3}: the cumulative CSV catalogue.
    catalog: dict | None = None
    # {"file": "observations.csv", "min_level": 2}: the document × channel × run matrix.
    observations: dict | None = None
    # {"resolve": true, "rate_limit_per_minute": 15}: look up in the Wayback the reference
    # copy of items that came from other channels.
    archive: dict | None = None
    # data/sources.json: where the text-and-data-mining opt-outs are read from.
    registry: Path | None = None

    @property
    def catalog_csv(self) -> Path | None:
        if not self.catalog:
            return None
        return self.directory / self.catalog.get("file", "catalog.csv")

    @property
    def catalog_level(self) -> int:
        return int((self.catalog or {}).get("min_level", 3))

    @property
    def observations_csv(self) -> Path | None:
        if self.observations is None:
            return None
        return self.directory / self.observations.get("file", "observations.csv")

    @property
    def observations_level(self) -> int:
        return int((self.observations or {}).get("min_level", 2))

    @property
    def resolve_archive(self) -> bool:
        return bool((self.archive or {}).get("resolve", False))

    @property
    def state(self) -> Path:
        return self.directory / "state"

    @property
    def corpus(self) -> Path:
        return self.directory / "corpus"

    @property
    def runs(self) -> Path:
        return self.directory / "runs"

    def stratum_of(self, source: str) -> str:
        for s in self.sources:
            if s.get("id") == source:
                return s.get("stratum", "general")
        return "general"


def validate(data: dict) -> list[str]:
    """Problems of form and of method; empty when the configuration is sound."""
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["the root must be an object"]
    if not data.get("lexicon"):
        problems.append("lexicon: required")
    if not data.get("registry"):
        problems.append(
            "registry: required: the path to data/sources.json, where the domains with "
            "no_text_by_policy are listed (docs/02-fontes.md, 2.2)"
        )
    sources = data.get("sources") or []
    if not sources:
        problems.append("sources: no source configured")
    ids = [s.get("id") for s in sources]
    if len(set(ids)) != len(ids):
        problems.append("sources: repeated ids")
    for s in sources:
        where = f"sources[{s.get('id') or '?'}]"
        if not s.get("id"):
            problems.append(f"{where}: no id")
        if not s.get("type"):
            problems.append(f"{where}: no type")
        stratum = s.get("stratum")
        if stratum is None:
            problems.append(f"{where}: no stratum (one of {', '.join(STRATA)})")
        elif stratum not in STRATA:
            problems.append(f"{where}: unknown stratum {stratum!r}")
        if ":" in (s.get("id") or "") and s["id"].split(":", 1)[0] != s.get("type"):
            problems.append(
                f"{where}: the id prefix ({s['id'].split(':', 1)[0]}) must be the type "
                f"({s.get('type')}): it is what the estimate groups channels by"
            )
    for key in ("catalog", "observations"):
        block = data.get(key)
        if block is not None:
            level = block.get("min_level", 3 if key == "catalog" else 2)
            if not isinstance(level, int) or not 0 <= level <= 3:
                problems.append(f"{key}.min_level: integer from 0 to 3")
    cat = (data.get("catalog") or {}).get("min_level", 3)
    obs = (data.get("observations") or {}).get("min_level", 2)
    if isinstance(cat, int) and isinstance(obs, int) and obs > cat:
        problems.append("observations.min_level cannot be greater than catalog.min_level")
    if data.get("since"):
        try:
            date.fromisoformat(data["since"])
        except ValueError:
            problems.append("since: use YYYY-MM-DD")
    return problems


def load(path: str | Path) -> Config:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    base = path.parent
    sources = data.get("sources") or []
    if not sources:
        raise ValueError(f"{path}: no source configured")
    ids = [s.get("id") for s in sources]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{path}: repeated source ids")
    return Config(
        lexicon=(base / data["lexicon"]).resolve(),
        directory=(base / data.get("directory", "data")).resolve(),
        sources=tuple(sources),
        since=date.fromisoformat(data["since"]) if data.get("since") else None,
        margin_days=int(data.get("margin_days", 2)),
        store_text=bool(data.get("store_text", True)),
        catalog=data.get("catalog"),
        observations=data.get("observations"),
        archive=data.get("archive"),
        registry=(base / data["registry"]).resolve() if data.get("registry") else None,
    )
