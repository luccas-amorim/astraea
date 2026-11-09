from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from astraea.engine.http import Request, Response
from tests.support import BASE, FEED

FIXTURES = Path(__file__).parent / "fixtures"


class Network:
    """Fake transport: answers by exact URL (without query) from fixtures."""

    def __init__(self) -> None:
        self.routes: dict[str, list[Response]] = {}
        self.requests: list[Request] = []

    def answer(
        self,
        url: str,
        body: bytes | str | Path,
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        if isinstance(body, Path):
            body = body.read_bytes()
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.routes.setdefault(url, []).append(Response(status, url, body, headers or {}))

    def __call__(self, req: Request, timeout: float) -> Response:
        self.requests.append(req)
        url = req.url.split("?")[0]
        if url not in self.routes:
            return Response(404, req.url, b"not found", {})
        queue = self.routes[url]
        return queue.pop(0) if len(queue) > 1 else queue[0]

    def urls(self) -> list[str]:
        return [r.url for r in self.requests]


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    """The per-minute limit is tested in test_http with a fake clock; here, nothing sleeps."""
    monkeypatch.setattr("astraea.engine.http.time.sleep", lambda seconds: None)


@pytest.fixture
def network() -> Network:
    return Network()


@pytest.fixture
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture
def cfg(tmp_path, fixtures):
    """Minimal configuration: one RSS feed and the sample lexicon."""
    shutil.copy(fixtures / "lexicon-carandiru.json", tmp_path / "lexicon.json")
    data = {
        "lexicon": "lexicon.json",
        "directory": "data",
        "since": "2026-09-01",
        "sources": [{"type": "rss", "id": "rss:paper", "url": FEED, "min_chars": 200}],
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def paper_network(network, fixtures):
    network.answer(FEED, fixtures / "rss" / "feed.xml")
    network.answer(f"{BASE}/carandiru-34-anos", fixtures / "rss" / "article-carandiru.html")
    network.answer(f"{BASE}/drenagem", fixtures / "rss" / "article-other.html")
    network.answer(f"{BASE}/sumiu", fixtures / "rss" / "error-200.html")
    return network
