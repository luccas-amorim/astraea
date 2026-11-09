"""Constants and shortcuts shared by the run tests."""

from datetime import date

from astraea import sources
from astraea.engine import config, lexicon
from astraea.engine import run as runs

FEED = "https://jornal.exemplo.br/feed"
BASE = "https://jornal.exemplo.br/2026/10"


def _run(path, network, **kw):
    c = config.load(path)
    matcher = lexicon.Matcher(lexicon.load(c.lexicon))
    instances = [sources.build(s, network) for s in c.sources]
    return c, runs.run(c, instances, matcher, today=date(2026, 10, 4), **kw)
