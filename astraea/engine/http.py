"""Polite HTTP client: identifies the project, obeys the source limit and robots.txt.

The limit is what the adapter declares (`rate_limit_per_minute`), not a number the engine
negotiates. The transport is injectable: tests swap the network for recorded fixtures.

Two safety rules this module enforces on its own:

- **No error message or log line carries a secret.** Every URL goes through `redact()`
  before becoming text: `api_key=`, `token=` and the like come out as `<redacted>`. The
  run report is committed to a public repository; a failure after the retries would
  otherwise take the whole key into the git history.
- **The `Crawl-delay` of each host is honoured.** The per-minute limit is the source's;
  the `Crawl-delay` that a host's robots.txt declares for `User-agent: *` (or for
  Astraea) is the host's, and it is kept between two requests to that host, robots.txt
  included. The larger of the two wins. (Divergence from Alétheia, whose client read
  robots.txt only for `Disallow`: docs/02-fontes.md, 2.2, asks for 10 s on un.org.)
- **Transient failures are retried, including a truncated response.** `IncompleteRead`,
  `RemoteDisconnected` and `BadStatusLine` inherit from `http.client.HTTPException`, not
  from `OSError`; without this `except`, a connection closed by the server would become a
  "source failure" with no retry (it is what brought down Alétheia's first run).
"""

from __future__ import annotations

import http.client
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections.abc import Callable
from dataclasses import dataclass, field

from astraea import __version__

log = logging.getLogger(__name__)

USER_AGENT = f"Astraea/{__version__} (academic research; +https://github.com/luccas-amorim/astraea)"
RETRYABLE = {408, 425, 429, 500, 502, 503, 504}

_SECRETS = re.compile(
    r"((?:api[_-]?key|apikey|key|token|access[_-]?token|secret|password|senha|mailto)=)([^&#\s]+)",
    re.I,
)


def redact(text: str) -> str:
    """Replaces the value of sensitive parameters with `<redacted>`. Idempotent."""
    return _SECRETS.sub(r"\1<redacted>", text)


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    body: bytes | None = None
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Response:
    status: int
    url: str
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)

    def json(self):
        return json.loads(self.body.decode("utf-8"))


Transport = Callable[[Request, float], Response]


class FetchError(RuntimeError):
    """Network or HTTP failure after the retries are exhausted."""


class BlockedByRobots(FetchError):
    """The origin's robots.txt does not allow the path. Not a failure: it is policy."""


class BlockedByCountry(FetchError):
    """The origin refuses connections from the country the run comes from.

    Retrying or changing headers does not help: the run has to come from an address the
    origin accepts. Circumventing the block is not done (AGENTS.md, rule 7).
    """


# Signatures of a geographic block in the body of a 403.
_COUNTRY_MARKS = (
    b"block access from your country",
    b"not available in your country",
    b"geo-restricted",
)

# Transport exceptions that deserve a retry: network, DNS, timeout and a response
# truncated or closed by the server (the last ones are not OSError).
TRANSIENT = (OSError, urllib.error.URLError, http.client.HTTPException)


def urllib_transport(req: Request, timeout: float) -> Response:
    request = urllib.request.Request(req.url, data=req.body, headers=req.headers, method=req.method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as r:
            return Response(
                r.status, r.geturl(), r.read(), {k.lower(): v for k, v in r.headers.items()}
            )
    except urllib.error.HTTPError as error:
        headers = {k.lower(): v for k, v in (error.headers or {}).items()}
        return Response(error.code, req.url, error.read() or b"", headers)


class Client:
    def __init__(
        self,
        rate_limit_per_minute: int,
        *,
        respects_robots: bool = True,
        transport: Transport = urllib_transport,
        headers: dict[str, str] | None = None,
        attempts: int = 4,
        timeout: float = 60.0,
        sleep: Callable[[float], None] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if rate_limit_per_minute <= 0:
            raise ValueError("rate_limit_per_minute must be positive")
        self.interval = 60.0 / rate_limit_per_minute
        self.respects_robots = respects_robots
        self.transport = transport
        self.headers = {"User-Agent": USER_AGENT, **(headers or {})}
        self.attempts = attempts
        self.timeout = timeout
        # Resolved at call time, not at definition, so tests can swap the clock.
        self._sleep = sleep or (lambda seconds: time.sleep(seconds))
        self._clock = clock or (lambda: time.monotonic())
        self._last: float | None = None
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self._host_last: dict[str, float] = {}  # origin -> time of the last request

    def _wait(self) -> None:
        if self._last is not None:
            delay = self.interval - (self._clock() - self._last)
            if delay > 0:
                self._sleep(delay)
        self._last = self._clock()

    @staticmethod
    def _origin(url: str) -> str:
        parts = urllib.parse.urlsplit(url)
        return f"{parts.scheme}://{parts.netloc}"

    def crawl_delay(self, url: str) -> float:
        """Seconds the host asks between requests (robots.txt), 0 when it asks nothing."""
        rules = self._robots.get(self._origin(url))
        if rules is None:
            return 0.0
        delay = rules.crawl_delay(self.headers["User-Agent"])
        return float(delay) if delay else 0.0

    def _wait_host(self, url: str) -> None:
        origin = self._origin(url)
        delay = self.crawl_delay(url)
        last = self._host_last.get(origin)
        if delay and last is not None:
            remaining = delay - (self._clock() - last)
            if remaining > 0:
                self._sleep(remaining)
        self._host_last[origin] = self._clock()

    def _allowed(self, url: str) -> bool:
        origin = self._origin(url)
        if origin not in self._robots:
            # A network failure here rises as FetchError and is not cached: the next
            # request to the same origin tries to read robots.txt again.
            self._robots[origin] = self._read_robots(origin)
        rules = self._robots[origin]
        return rules is None or rules.can_fetch(self.headers["User-Agent"], url)

    def _read_robots(self, origin: str) -> urllib.robotparser.RobotFileParser | None:
        """None when there is no robots.txt (404 and the like): by convention, all allowed.

        401 and 403 are read as "disallow everything". This is more conservative than
        RFC 9309 (which treats 4xx as no restriction) and it is deliberate: an origin that
        hides its robots.txt does not get the benefit of the doubt.
        """
        response = self._send(Request("GET", f"{origin}/robots.txt", headers=dict(self.headers)))
        self._host_last[origin] = self._clock()
        rules = urllib.robotparser.RobotFileParser()
        if response.status in (401, 403):
            rules.disallow_all = True
            return rules
        if response.status >= 400:
            return None
        rules.parse(response.body.decode("utf-8", errors="replace").splitlines())
        return rules

    def _send(self, req: Request) -> Response:
        last: str = ""
        for attempt in range(self.attempts):
            self._wait()
            try:
                response = self.transport(req, self.timeout)
            except TRANSIENT as error:
                last = f"{type(error).__name__}: {redact(str(error))}"
            else:
                if response.status not in RETRYABLE:
                    return response
                last = f"HTTP {response.status}"
            if attempt + 1 < self.attempts:
                pause = min(60.0, 2.0 ** (attempt + 1))
                log.warning(
                    "%s %s failed (%s); retrying in %ss",
                    req.method, redact(req.url), last, pause,
                )  # fmt: skip
                self._sleep(pause)
        raise FetchError(
            f"{req.method} {redact(req.url)} failed after {self.attempts} attempts: {last}"
        )

    def request(
        self,
        url: str,
        *,
        method: str = "GET",
        params: dict | list[tuple[str, str]] | None = None,
        json_body: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        """Makes the request and returns the 2xx response. Any other status is FetchError."""
        if params:
            url = f"{url}{'&' if '?' in url else '?'}{urllib.parse.urlencode(params)}"
        if self.respects_robots and not self._allowed(url):
            raise BlockedByRobots(f"robots.txt does not allow {redact(url)}")
        all_headers = {**self.headers, **(headers or {})}
        body = None
        if json_body is not None:
            body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
            all_headers.setdefault("Content-Type", "application/json")
        if self.respects_robots:
            self._wait_host(url)
        response = self._send(Request(method, url, body, all_headers))
        if self.respects_robots:  # counted from the end of the request, retries included
            self._host_last[self._origin(url)] = self._clock()
        if response.status == 403 and any(m in response.body for m in _COUNTRY_MARKS):
            raise BlockedByCountry(
                f"{method} {redact(url)}: the origin blocks access from this country; "
                "run from an address it accepts"
            )
        if not 200 <= response.status < 300:
            excerpt = response.body[:300].decode("utf-8", errors="replace")
            raise FetchError(f"{method} {redact(url)} -> HTTP {response.status}: {excerpt}")
        return response
