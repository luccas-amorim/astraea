"""The Wayback Machine as reference archive, by exact URL.

Discovering is one thing (any channel does it); having a stable, dated copy of each
document is another. For a document that came from GDELT or from a feed, this module asks
the CDX whether the Wayback has an intact capture of the URL and returns the address in
`id_` mode (archived content without the Wayback toolbar). The exact-URL query answers in
under a second; the whole-domain query is the one that times out.

`SavePageNow` (asking the Wayback to archive a live URL that has no copy yet) is left to a
research decision: it needs a key and has its own quota. The extension point is
`request_capture()`.
"""

from __future__ import annotations

from urllib.parse import urlencode

from astraea.engine.http import Client, FetchError, Transport, urllib_transport
from astraea.engine.url import original_from_wayback

CDX = "https://web.archive.org/cdx/search/cdx"
ARCHIVE = "https://web.archive.org/web"


def snapshot(timestamp: str, original: str) -> str:
    return f"{ARCHIVE}/{timestamp}id_/{original}"


class Archive:
    """Resolves URLs to the most recent intact capture in the Wayback."""

    def __init__(
        self,
        client: Client | None = None,
        *,
        rate_limit_per_minute: int = 15,
        transport: Transport = urllib_transport,
    ) -> None:
        self.client = client or Client(
            rate_limit_per_minute, respects_robots=False, transport=transport, timeout=60
        )

    def resolve(self, url: str) -> tuple[str, str] | None:
        """(timestamp, snapshot url) of the most recent 200 capture, or None."""
        original = original_from_wayback(url)
        params = [
            ("url", original),
            ("matchType", "exact"),
            ("filter", "statuscode:200"),
            ("output", "json"),
            ("fl", "timestamp,original"),
            ("limit", "-1"),  # the last capture
        ]
        try:
            lines = self.client.request(f"{CDX}?{urlencode(params)}").json() or []
        except FetchError:
            return None
        body = [line for line in lines[1:] if line]
        if not body:
            return None
        timestamp, found = body[-1][0], body[-1][1]
        return timestamp, snapshot(timestamp, found)

    def request_capture(self, url: str) -> None:  # pragma: no cover - extension point
        """Ask for archiving (SavePageNow). Not implemented: a research decision."""
        raise NotImplementedError("SavePageNow needs a key and its own policy")
