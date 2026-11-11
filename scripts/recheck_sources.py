"""The Cartógrafo: rechecks, every month, the penal-law databases that were down.

The probe of 2026-11-06 found no open database of penal codes alive (docs/02-fontes.md,
1.2), so penal_code and domestic_genocide come from the human load. The Cartógrafo only
asks, once a month, whether Legislationline, SHERLOC, the Law Library of Congress and
WorldLII answer again, and reopens the source in data/sources.json (`state: active`) when
one does (docs/04-arquitetura.md, "Os robôs"). It reads no content: one page per source,
through the engine's client, with the Astraea User-Agent and robots.txt obeyed. It runs
inside the monthly reading of the countries (scripts/countries_monthly.py), whose pull
request is the review.

    python scripts/recheck_sources.py              asks each source over the network and
                                                   says what it would change
    python scripts/recheck_sources.py --execute    the same, and writes sources.json
    --only ID[,ID]                                 ask only these sources
    --responses FILE --read-on YYYY-MM-DD          answer from the recorded responses in
                                                   FILE instead of the network (the tests)
    --data DIR                                     another source directory

What "answers" means, for each source, is in PROBES: HTTP 2xx on the page that matters,
on the same host (a redirect to another site is not the source), with the mark that
proves it is that page, and not a challenge page (Cloudflare and the like are never
circumvented: AGENTS.md, rule 7). What it changes:

- a `suspended` source that answers, and whose suspension was about answering, becomes
  `active`, with `robots_checked_on` the day of the reading and a `reason` that says so;
  the sha256 of the response is printed (it goes to CHANGELOG.md);
- SHERLOC is asked but never reopened: it was suspended for its content (tested searches
  for genocide returned no law), which one page cannot settle; the report says whether it
  answered, and a person decides;
- a source a person discarded is left alone, and an active one is never suspended by the
  robot: the report says when it stopped answering.

When the robots.txt of a source disallows AI agents by name, the report and the new
reason say so: a session that is a language model does not read that portal, even though
the Astraea client may (AGENTS.md, "Carga humana").

Simulation by default; --execute writes. Nothing is deleted.

Exit codes: 0 fine (a source that does not answer is a result, not a failure); 1 a source
of PROBES is missing from sources.json, or the file of responses is unreadable (nothing
written); 2 usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from transform import dumps, is_full_date, show  # noqa: E402

from astraea.engine.http import Client, FetchError, Request, Response  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RATE_LIMIT = 6  # per minute, when the source declares none


@dataclass(frozen=True)
class Probe:
    source: str  # id in data/sources.json
    url: str  # the page that has to answer
    what: str  # English: it goes into the reason
    mark: str  # text the page must carry ("" for none); for json, a top-level key
    json: bool = False
    reopens: bool = True


PROBES = (
    Probe(
        "legislationline",
        "https://www.legislationline.org/documents/section/criminal-codes",
        "the criminal codes collection",
        "riminal",
    ),
    Probe(
        "sherloc",
        "https://sherloc.unodc.org/cld/en/v3/sherloc/legdb/",
        "the Database of Legislation",
        "Genocide",
        reopens=False,
    ),
    Probe(
        "loc-glm",
        "https://www.loc.gov/collections/global-legal-monitor/?fo=json",
        "the JSON API of the Global Legal Monitor collection",
        "results",
        json=True,
    ),
    Probe("worldlii", "http://www.worldlii.org/", "the home page", "WorldLII"),
)

# A page served with 200 that is a challenge or a block, not the source.
CHALLENGES = (
    "just a moment...",
    "cf-chl",
    "challenge-platform",
    "attention required! | cloudflare",
    "sorry, you have been blocked",
    "request rejected",
    "enable javascript and cookies to continue",
)

# User agents of AI systems that a robots.txt may name; a session that is a model does
# not read a portal that disallows any of them (AGENTS.md).
AI_AGENTS = (
    "ClaudeBot",
    "Claude-User",
    "Claude-Web",
    "anthropic-ai",
    "GPTBot",
    "ChatGPT-User",
    "OAI-SearchBot",
    "CCBot",
    "Google-Extended",
    "PerplexityBot",
    "MistralAI-User",
)


@dataclass
class Answer:
    answers: bool
    detail: str  # English, one line
    status: int | None = None
    sha256: str = ""
    size: int = 0
    ai_agents: tuple[str, ...] = ()


# ------------------------------------------------------------------ asking


def recorded_transport(path: Path):
    """A transport that answers from a JSON file {"responses": {url: {...}}}.

    Each response has `status`, and may have `url` (where it ended, after redirects),
    `headers` and `body` (text). A URL that is not in the file fails as a connection that
    did not answer (the Client retries it, then gives up).
    """
    recorded = json.loads(path.read_text(encoding="utf-8"))["responses"]

    def transport(req: Request, timeout: float) -> Response:
        r = recorded.get(req.url)
        if r is None:
            raise OSError(f"no answer from {req.url} (recorded)")
        return Response(
            r["status"],
            r.get("url", req.url),
            r.get("body", "").encode("utf-8"),
            {k.lower(): v for k, v in r.get("headers", {}).items()},
        )

    return transport


def _host(url: str) -> str:
    return urllib.parse.urlsplit(url).hostname or ""


def ask(probe: Probe, client: Client) -> Answer:
    """One request to the page of the probe; what came back, said in one line."""
    try:
        response = client.request(probe.url)
    except FetchError as error:
        # the message, without the excerpt of the page the client appends to an HTTP error
        answer = Answer(False, re.sub(r"(-> HTTP \d+):.*", r"\1", str(error), flags=re.S))
    else:
        answer = judge(probe, response)
    # Only the agents named apart from everyone else: a robots.txt that closes the page to
    # all (or that answers 401/403, read as "disallow everything") names nobody.
    rules = client.robots(probe.url)
    if rules is not None and rules.can_fetch(client.headers["User-Agent"], probe.url):
        answer.ai_agents = tuple(a for a in AI_AGENTS if not rules.can_fetch(a, probe.url))
    return answer


def judge(probe: Probe, response: Response) -> Answer:
    body = response.body
    sha = hashlib.sha256(body).hexdigest()
    seen = dict(status=response.status, sha256=sha, size=len(body))
    if _host(response.url) != _host(probe.url):
        return Answer(False, f"redirected to {_host(response.url)} ({response.url})", **seen)
    text = body.decode("utf-8", errors="replace")
    lowered = text.lower()
    challenge = next((c for c in CHALLENGES if c in lowered), None)
    if challenge:
        detail = f"HTTP {response.status}, but a challenge page ({challenge!r})"
        return Answer(False, detail, **seen)
    if probe.json:
        try:
            parsed = json.loads(text)
        except ValueError:
            return Answer(False, f"HTTP {response.status}, but not JSON", **seen)
        if not isinstance(parsed, dict) or probe.mark not in parsed:
            return Answer(False, f"HTTP {response.status}, JSON without {probe.mark!r}", **seen)
    elif probe.mark and probe.mark not in text:
        return Answer(False, f"HTTP {response.status}, without the mark {probe.mark!r}", **seen)
    return Answer(True, f"HTTP {response.status}, {len(body)} bytes", **seen)


# ------------------------------------------------------------------ deciding


def reopen_reason(probe: Probe, answer: Answer, read_on: str) -> str:
    reason = (
        f"Reopened by the Cartógrafo (monthly recheck) on {read_on}: {probe.what} "
        f"({probe.url}) answered HTTP {answer.status} on the same host; only that page was "
        "asked, no content was read, and the monthly pull request is the review."
    )
    if answer.ai_agents:
        reason += (
            f" Its robots.txt disallows AI agents by name ({', '.join(answer.ai_agents)}): "
            "a session that is a language model does not read it."
        )
    return reason


def plan(
    sources: list[dict], answers: dict[str, Answer], read_on: str
) -> tuple[list[dict], list[str]]:
    """The new sources.json and one report line per probe (kinds as the other loads)."""
    by_id = {s["id"]: s for s in sources}
    new = [dict(s) for s in sources]
    new_by_id = {s["id"]: s for s in new}
    report: list[str] = []
    for probe in PROBES:
        if probe.source not in answers:
            continue
        answer = answers[probe.source]
        old = by_id[probe.source]
        state = old.get("state")
        said = "answers" if answer.answers else "does not answer"
        line = f"{probe.source} ({state}): {probe.url}: {said}: {answer.detail}"
        if answer.ai_agents:
            line += f"; robots.txt disallows AI agents by name: {', '.join(answer.ai_agents)}"
        if state == "discarded":
            report.append(f"left alone: {line}; discarded by a person")
        elif state == "active":
            note = "" if answer.answers else "; the robot does not suspend it, a person decides"
            report.append(f"kept: {line}{note}")
        elif answer.answers and probe.reopens:
            entry = new_by_id[probe.source]
            entry["state"] = "active"
            entry["robots_checked_on"] = read_on
            entry["reason"] = reopen_reason(probe, answer, read_on)
            report.append(
                f"changed: {probe.source}.state: 'suspended' -> 'active': {probe.url}: "
                f"{answer.size} bytes, sha256 {answer.sha256}"
            )
            if answer.ai_agents:
                report.append(
                    f"  robots.txt disallows AI agents by name: {', '.join(answer.ai_agents)}"
                )
        elif answer.answers:
            report.append(
                f"kept: {line}; not reopened by the robot: it was suspended for its content, "
                "which one page does not settle"
            )
        else:
            report.append(f"kept: {line}")
    return new, report


# ------------------------------------------------------------------ command line


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--execute", action="store_true", help="write (default: simulation)")
    parser.add_argument("--only", help="comma-separated ids of the sources to ask")
    parser.add_argument("--responses", help="answer from this JSON file, not the network")
    parser.add_argument("--read-on", help="date of the reading, YYYY-MM-DD (with --responses)")
    parser.add_argument("--data", help="source directory (default: data/)")
    args = parser.parse_args(argv)

    if args.responses and not args.read_on:
        print("--responses needs --read-on: the date the responses were recorded", file=sys.stderr)
        return 2
    read_on = args.read_on or date.today().isoformat()
    if not is_full_date(read_on):
        print(f"--read-on {read_on!r} is not a date YYYY-MM-DD", file=sys.stderr)
        return 2
    known = [p.source for p in PROBES]
    only = [i.strip() for i in args.only.split(",")] if args.only else known
    unknown = [i for i in only if i not in known]
    if unknown:
        print(f"--only: not a source the Cartógrafo asks: {', '.join(unknown)}", file=sys.stderr)
        return 2

    data = Path(args.data) if args.data else ROOT / "data"
    path = data / "sources.json"
    sources = json.loads(path.read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in sources}
    missing = [i for i in only if i not in by_id]
    if missing:
        print(f"FAIL not in {show(path)}: {', '.join(missing)}")
        print("nothing was written")
        return 1
    try:
        transport = recorded_transport(Path(args.responses)) if args.responses else None
    except (OSError, ValueError, KeyError) as error:
        print(f"FAIL the recorded responses: {error}")
        print("nothing was written")
        return 1

    answers: dict[str, Answer] = {}
    for probe in PROBES:
        if probe.source not in only:
            continue
        rate = by_id[probe.source].get("rate_limit_per_minute") or RATE_LIMIT
        options = {"attempts": 3, "timeout": 30.0}
        if transport is not None:
            options.update(transport=transport, sleep=lambda seconds: None)
        answers[probe.source] = ask(probe, Client(rate, **options))

    new, report = plan(sources, answers, read_on)
    for line in report:
        print(line)
    reopened = sum(1 for line in report if line.startswith("changed:"))
    print(f"{len(answers)} sources asked, {reopened} reopened")
    text = dumps(new)
    if path.read_text(encoding="utf-8") == text:
        print(f"up to date: {show(path)}")
    elif args.execute:
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote: {show(path)} ({reopened} sources)")
    else:
        print(f"would write: {show(path)} ({reopened} sources)")
        print("simulation: nothing was written; add --execute to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
