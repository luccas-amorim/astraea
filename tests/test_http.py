import http.client

import pytest

from astraea.engine.http import (
    USER_AGENT,
    BlockedByCountry,
    BlockedByRobots,
    Client,
    FetchError,
    Request,
    Response,
    redact,
)


class Clock:
    def __init__(self):
        self.now = 0.0
        self.pauses = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.pauses.append(seconds)
        self.now += seconds


def _client(network, clock=None, **kw):
    clock = clock or Clock()
    return Client(kw.pop("limit", 60), transport=network, sleep=clock.sleep, clock=clock, **kw)


def test_identifies_the_project_and_reads_robots_once_per_origin(network):
    network.answer("https://a.br/x", "ok")
    network.answer("https://a.br/y", "ok")
    client = _client(network)
    client.request("https://a.br/x")
    client.request("https://a.br/y")
    assert network.urls() == ["https://a.br/robots.txt", "https://a.br/x", "https://a.br/y"]
    assert all(r.headers["User-Agent"] == USER_AGENT for r in network.requests)
    assert USER_AGENT.startswith("Astraea/")


def test_obeys_the_per_minute_limit(network):
    network.answer("https://a.br/x", "ok")
    clock = Clock()
    client = _client(network, clock, limit=30, respects_robots=False)
    for _ in range(3):
        client.request("https://a.br/x")
    assert clock.pauses == [2.0, 2.0]


def test_robots_that_disallows_blocks_without_requesting(network):
    network.answer("https://a.br/robots.txt", "User-agent: *\nDisallow: /private/\n")
    client = _client(network)
    with pytest.raises(BlockedByRobots):
        client.request("https://a.br/private/doc")
    assert "https://a.br/private/doc" not in network.urls()


def test_robots_403_disallows_everything(network):
    network.answer("https://a.br/robots.txt", "", status=403)
    with pytest.raises(BlockedByRobots):
        _client(network).request("https://a.br/x")


def test_retries_on_503_and_gives_up_on_404(network):
    network.answer("https://a.br/x", "down", status=503)
    network.answer("https://a.br/x", "ok")
    clock = Clock()
    response = _client(network, clock, respects_robots=False).request("https://a.br/x")
    assert response.body == b"ok"
    assert 2.0 in clock.pauses
    with pytest.raises(FetchError, match="HTTP 404"):
        _client(network, respects_robots=False).request("https://a.br/nothing")


def test_exhausts_attempts_without_sleeping_after_the_last(network):
    network.answer("https://a.br/x", "down", status=502)
    clock = Clock()
    with pytest.raises(FetchError, match="after 2 attempts"):
        _client(network, clock, respects_robots=False, attempts=2).request("https://a.br/x")
    # A single pause, between the first and second attempts; none after giving up.
    assert clock.pauses == [2.0]


def test_truncated_response_is_retried():
    """IncompleteRead inherits from HTTPException, not OSError: it must be caught."""
    calls = []

    def transport(req: Request, timeout: float) -> Response:
        calls.append(req.url)
        if len(calls) == 1:
            raise http.client.IncompleteRead(b"x" * 10)
        if len(calls) == 2:
            raise http.client.RemoteDisconnected("closed")
        return Response(200, req.url, b"ok", {})

    clock = Clock()
    client = Client(60, respects_robots=False, transport=transport, sleep=clock.sleep, clock=clock)
    assert client.request("https://a.br/x").body == b"ok"
    assert len(calls) == 3


def test_redacts_secrets_in_errors_and_in_the_url():
    assert redact("https://api.br/w?search=x&api_key=SECRET&per-page=2") == (
        "https://api.br/w?search=x&api_key=<redacted>&per-page=2"
    )
    assert redact("token=abc&mailto=me@example.org") == "token=<redacted>&mailto=<redacted>"
    assert redact("no secret") == "no secret"


def test_error_after_the_attempts_does_not_carry_the_key(network):
    network.answer("https://api.br/w", "limit", status=429)
    with pytest.raises(FetchError) as error:
        _client(network, respects_robots=False, attempts=1).request(
            "https://api.br/w", params={"api_key": "SECRET-KEY", "q": "x"}
        )
    assert "SECRET-KEY" not in str(error.value)
    assert "api_key=<redacted>" in str(error.value)


def test_http_error_does_not_carry_the_key(network):
    network.answer("https://api.br/w", "forbidden", status=403)
    with pytest.raises(FetchError) as error:
        _client(network, respects_robots=False).request("https://api.br/w?api_key=SECRET-KEY")
    assert "SECRET-KEY" not in str(error.value)


def test_json_body_and_parameters(network):
    network.answer("https://api.br/search", '{"ok": true}')
    client = _client(network, respects_robots=False)
    response = client.request(
        "https://api.br/search", method="POST", params={"q": "ação"}, json_body={"a": 1}
    )
    assert response.json() == {"ok": True}
    req = network.requests[-1]
    assert req.url == "https://api.br/search?q=a%C3%A7%C3%A3o"
    assert req.body == b'{"a": 1}'
    assert req.headers["Content-Type"] == "application/json"


def test_country_block_has_its_own_error(network):
    body = (
        "<TITLE>ERROR: The request could not be satisfied</TITLE> The Amazon CloudFront "
        "distribution is configured to block access from your country."
    )
    network.answer("https://api.br/x", body, status=403)
    with pytest.raises(BlockedByCountry, match="blocks access from this country"):
        _client(network, respects_robots=False).request("https://api.br/x")
