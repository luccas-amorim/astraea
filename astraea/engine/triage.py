"""Triage in levels. Deterministic: the same inputs always give the same result.

| Level | Means                                                    | Reason          |
|-------|----------------------------------------------------------|-----------------|
| 0     | no lexicon form in the text                              | no_term         |
| 0     | only occurrences cancelled by an exclusion               | only_excluded   |
| 1     | term present, required context absent                    | no_context      |
| 2     | term and context, but the term is not in a highlight     | needs_review    |
| 3     | term and context, and the term is in a source highlight  | accepted        |
| 2     | level 2 or 3, but the page was not read by policy        | no_text_by_policy |

The last line is new in Astraea: on a domain that reserves text and data mining only the
listing's title and description are read (astraea.engine.policy), and an item that would
be accepted on so little goes to a person instead. Levels 0 and 1 keep their reason.

The cut does not delete: every level goes to the full report, with the reason and the
excerpt that decided it. A false positive is acceptable; a false negative is not.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from astraea.engine.contract import Document
from astraea.engine.lexicon import Matcher
from astraea.engine.policy import MAX_LEVEL, NO_TEXT
from astraea.engine.text import fold

EXCERPT_RADIUS = 160


@dataclass
class Result:
    level: int
    reason: str
    keys: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    score: float = 0.0
    excerpt: str | None = None
    where: str | None = None  # "text" or the name of the highlight where it was found

    def as_dict(self) -> dict:
        return {
            "level": self.level,
            "reason": self.reason,
            "keys": self.keys,
            "categories": self.categories,
            "score": self.score,
            "excerpt": self.excerpt,
            "where": self.where,
        }


def cut_excerpt(text: str, start: int, end: int, radius: int = EXCERPT_RADIUS) -> str:
    a, b = max(0, start - radius), min(len(text), end + radius)
    excerpt = " ".join(text[a:b].split())
    return f"{'…' if a > 0 else ''}{excerpt}{'…' if b < len(text) else ''}"


def triage(doc: Document, matcher: Matcher) -> Result:
    result = _triage(doc, matcher)
    if doc.policy == NO_TEXT and result.level >= MAX_LEVEL:
        result.level, result.reason = MAX_LEVEL, NO_TEXT
    return result


def _triage(doc: Document, matcher: Matcher) -> Result:
    text = doc.text
    folded = fold(text)
    valid, cancelled = matcher.occurrences(folded)

    if not valid:
        if cancelled:
            oc = cancelled[0]
            return Result(
                0, "only_excluded", excerpt=cut_excerpt(text, oc.start, oc.end), where="text"
            )
        return Result(0, "no_term")

    keys = list(dict.fromkeys(o.key for o in valid))
    terms = [matcher.term(k) for k in keys]
    categories = list(dict.fromkeys(c for t in terms for c in t.categories))
    score = round(sum(t.weight for t in terms), 4)
    first = valid[0]
    base = Result(1, "", keys, categories, score)

    marker = matcher.context(folded)
    if not marker:
        base.reason = "no_context"
        base.excerpt, base.where = cut_excerpt(text, first.start, first.end), "text"
        return base

    for name, highlight in doc.highlights.items():
        in_highlight, _ = matcher.occurrences(fold(highlight))
        if in_highlight:
            oc = in_highlight[0]
            base.level, base.reason = 3, "accepted"
            base.excerpt, base.where = cut_excerpt(highlight, oc.start, oc.end), name
            return base

    base.level, base.reason = 2, "needs_review"
    base.excerpt, base.where = cut_excerpt(text, first.start, first.end), "text"
    return base
