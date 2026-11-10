"""Discovery channels. One per origin, all fulfilling `astraea.engine.contract.Source`.

| type           | what it reaches                                | usual stratum |
|----------------|------------------------------------------------|---------------|
| `gdelt`        | news by text, last ~90 days                    | press         |
| `rss`          | the feed of an outlet, court or repository     | press, legal  |
| `curated_list` | CSV curated by hand (archives without an API)  | any           |
| `listing`      | a table that changes slowly, one row per item  | function 1, 3 |

`listing` is new in Astraea (phase 2 of `docs/06-roteiro.md`): its first format is the
per-treaty XML of the UN Treaty Collection, read by the Tabelião.
"""

from __future__ import annotations

from astraea.engine.contract import Source
from astraea.engine.http import Transport, urllib_transport
from astraea.sources.curated_list import CuratedList
from astraea.sources.gdelt import Gdelt
from astraea.sources.listing import Listing
from astraea.sources.rss import Rss

TYPES = {
    "rss": Rss,
    "gdelt": Gdelt,
    "curated_list": CuratedList,
    "listing": Listing,
}


def build(cfg: dict, transport: Transport = urllib_transport) -> Source:
    kind = cfg.get("type")
    if kind not in TYPES:
        raise ValueError(f"unknown source type: {kind!r} (known: {sorted(TYPES)})")
    if not cfg.get("id"):
        raise ValueError(f"{kind} source without id")
    return TYPES[kind].from_config(cfg, transport)
