"""The URL as identity: the same normalization for the catalogue, observations and estimate.

Two URLs that differ only in scheme, `www.`, trailing slash, default port, tracking
parameters or the Wayback prefix point to the same document and need the same `id`. In
Alétheia, the catalogue once used the raw URL and the estimate the normalized one: the
same article seen by GDELT (live) and by the Wayback (archived) became two rows.
"""

from __future__ import annotations

import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlsplit

_WAYBACK = re.compile(r"^https?://web\.archive\.org/web/\d+[a-z_]*/(.+)$")
_TRACKING = re.compile(r"^(utm_|fbclid$|gclid$|mc_|ref$|amp$|igshid$|_ga$)")


def normalize(url: str) -> str:
    """`host/path?query`, without scheme, `www.`, default port, trailing slash or tracking."""
    url = url.strip()
    if m := _WAYBACK.match(url):
        url = m.group(1)
    if "://" not in url:
        url = f"http://{url}"
    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.")
    host = re.sub(r":(80|443)$", "", host)
    path = parts.path.rstrip("/") or "/"
    query = urlencode(
        sorted((k, v) for k, v in parse_qsl(parts.query) if not _TRACKING.match(k.lower()))
    )
    return f"{host}{path}" + (f"?{query}" if query else "")


def identity(url: str) -> str:
    """16 hex of the sha256 of the normalized URL: stable across runs and channels."""
    return hashlib.sha256(normalize(url).encode("utf-8")).hexdigest()[:16]


def domain(url: str) -> str:
    return normalize(url).split("/", 1)[0]


def original_from_wayback(url: str) -> str:
    """The origin URL behind a Wayback address; the URL itself if it is not one."""
    m = _WAYBACK.match(url.strip())
    return m.group(1) if m else url
