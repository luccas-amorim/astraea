"""The Cartógrafo: scripts/recheck_sources.py, offline, on recorded responses.

The responses are the synthetic fixture of tests/fixtures/cartographer/ (the four sources
as 2026-11-11 saw them: none reopenable); each test changes the copy it needs. The
sources.json the tests read is the repository's with the four entries put back to
`suspended`, so that a source the monthly pull request reopened later does not break
them ("teste não fixa o valor do dia", AGENTS.md).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import recheck_sources as rs  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "cartographer" / "responses.json"
READ_ON = "2026-12-01"
FOUR = ("legislationline", "sherloc", "loc-glm", "worldlii")


@pytest.fixture
def repo(tmp_path):
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    for s in sources:
        if s["id"] in FOUR:
            s["state"] = "suspended"
            s["reason"] = f"Suspended for the test ({s['id']})."
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "sources.json").write_text(rs.dumps(sources), encoding="utf-8")
    (tmp_path / "responses.json").write_bytes(FIXTURE.read_bytes())
    return tmp_path


def run(repo: Path, *extra: str) -> int:
    return rs.main(
        [
            "--data", str(repo / "data"),
            "--responses", str(repo / "responses.json"),
            "--read-on", READ_ON,
            *extra,
        ]
    )  # fmt: skip


def answer(repo: Path, url: str, status: int, body: str, final: str | None = None) -> None:
    """Records (or replaces) the response the transport gives for one URL."""
    path = repo / "responses.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["responses"][url] = {"status": status, "body": body, **({"url": final} if final else {})}
    path.write_text(json.dumps(data), encoding="utf-8")


def sources(repo: Path) -> dict[str, dict]:
    path = repo / "data" / "sources.json"
    return {s["id"]: s for s in json.loads(path.read_text(encoding="utf-8"))}


LL = "https://www.legislationline.org/documents/section/criminal-codes"
LL_PAGE = "<html><title>Criminal codes | Legislationline</title><body>Criminal codes</body></html>"


# ------------------------------------------------------------------ nothing came back


def test_a_month_like_today_changes_nothing(repo, capsys):
    before = (repo / "data" / "sources.json").read_bytes()
    assert run(repo, "--execute") == 0
    assert (repo / "data" / "sources.json").read_bytes() == before
    out = capsys.readouterr().out
    assert "4 sources asked, 0 reopened" in out and "up to date: " in out
    lines = [line for line in out.splitlines() if line.startswith("kept: ")]
    assert len(lines) == 4
    assert "legislationline (suspended)" in lines[0] and "-> HTTP 404" in lines[0]
    assert "<html" not in out  # the page the client appends to an HTTP error is cut
    assert "robots.txt does not allow" in lines[2]  # loc.gov answers its robots.txt with 403
    # the AI agents the robots.txt names apart, and only those: never for a 403 robots.txt
    assert lines[3].endswith("disallows AI agents by name: ClaudeBot, anthropic-ai, GPTBot")
    assert "AI agents" not in lines[2]
    assert "sha256" not in out  # only a reopened source needs the hash in the CHANGELOG


def test_sherloc_answers_but_is_never_reopened_by_the_robot(repo, capsys):
    assert run(repo, "--execute", "--only", "sherloc") == 0
    assert sources(repo)["sherloc"]["state"] == "suspended"
    out = capsys.readouterr().out
    assert "sherloc (suspended): " in out and ": answers: HTTP 200" in out
    assert "suspended for its content" in out


# ------------------------------------------------------------------ a source came back


def test_a_source_that_answers_again_is_reopened_with_execute(repo, capsys):
    answer(repo, LL, 200, LL_PAGE)
    before = sources(repo)
    assert run(repo, "--execute") == 0
    after = sources(repo)
    ll = after["legislationline"]
    assert ll["state"] == "active" and ll["robots_checked_on"] == READ_ON
    assert ll["reason"].startswith(f"Reopened by the Cartógrafo (monthly recheck) on {READ_ON}")
    assert LL in ll["reason"] and "AI agents" not in ll["reason"]
    # nothing else moved: every other entry, and every other key of this one
    assert {k: v for k, v in after.items() if k != "legislationline"} == {
        k: v for k, v in before.items() if k != "legislationline"
    }
    changed = {k for k in ll if ll[k] != before["legislationline"].get(k)}
    assert changed == {"state", "robots_checked_on", "reason"}
    out = capsys.readouterr().out
    assert f"changed: legislationline.state: 'suspended' -> 'active': {LL}: " in out
    assert f"{len(LL_PAGE)} bytes, sha256 " in out
    assert "wrote: " in out and "(1 sources)" in out


def test_the_simulation_writes_nothing(repo, capsys):
    answer(repo, LL, 200, LL_PAGE)
    before = (repo / "data" / "sources.json").read_bytes()
    assert run(repo) == 0
    assert (repo / "data" / "sources.json").read_bytes() == before
    out = capsys.readouterr().out
    assert "would write: " in out and "simulation: nothing was written" in out


def test_a_reopened_source_whose_robots_names_ai_agents_says_so(repo, capsys):
    answer(repo, "http://www.worldlii.org/", 200, "<html><title>WorldLII</title></html>")
    assert run(repo, "--execute") == 0
    reason = sources(repo)["worldlii"]["reason"]
    assert "disallows AI agents by name (ClaudeBot, anthropic-ai, GPTBot)" in reason
    assert "a session that is a language model does not read it" in reason
    assert "  robots.txt disallows AI agents by name: " in capsys.readouterr().out


@pytest.mark.parametrize(
    ("status", "body", "final", "why"),
    [
        (200, "<html>Criminal codes</html>", "https://odihr.osce.org/x/", "redirected to"),
        (200, "<html><title>Just a moment...</title>Criminal</html>", None, "challenge page"),
        (200, "<html>Legal opinions and comments</html>", None, "without the mark"),
        (503, "<html>Criminal codes</html>", None, "failed after 3 attempts: HTTP 503"),
    ],
)
def test_what_does_not_count_as_answering(repo, capsys, status, body, final, why):
    answer(repo, LL, status, body, final)
    assert run(repo, "--execute", "--only", "legislationline") == 0
    assert sources(repo)["legislationline"]["state"] == "suspended"
    out = capsys.readouterr().out
    assert "does not answer: " in out and why in out


def test_the_json_api_needs_its_key(repo, capsys):
    loc = "https://www.loc.gov/collections/global-legal-monitor/?fo=json"
    answer(repo, "https://www.loc.gov/robots.txt", 404, "")
    answer(repo, loc, 200, '{"error": "nothing"}')
    assert run(repo, "--execute", "--only", "loc-glm") == 0
    assert sources(repo)["loc-glm"]["state"] == "suspended"
    assert "JSON without 'results'" in capsys.readouterr().out
    answer(repo, loc, 200, '{"results": [], "pagination": {}}')
    assert run(repo, "--execute", "--only", "loc-glm") == 0
    loc_glm = sources(repo)["loc-glm"]
    assert loc_glm["state"] == "active" and loc_glm["robots_checked_on"] == READ_ON


# ------------------------------------------------------------------ what a person decided


def test_discarded_and_active_sources_are_left_to_a_person(repo, capsys):
    path = repo / "data" / "sources.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for s in data:
        if s["id"] == "legislationline":
            s["state"] = "discarded"
        if s["id"] == "worldlii":
            s["state"] = "active"
    path.write_text(rs.dumps(data), encoding="utf-8")
    answer(repo, LL, 200, LL_PAGE)
    before = path.read_bytes()
    assert run(repo, "--execute") == 0
    assert path.read_bytes() == before
    out = capsys.readouterr().out
    assert "left alone: legislationline (discarded): " in out and "discarded by a person" in out
    assert "kept: worldlii (active): " in out and "the robot does not suspend it" in out


# ------------------------------------------------------------------ errors


def test_a_probe_missing_from_sources_json_writes_nothing(repo, capsys):
    path = repo / "data" / "sources.json"
    data = [s for s in json.loads(path.read_text(encoding="utf-8")) if s["id"] != "sherloc"]
    path.write_text(rs.dumps(data), encoding="utf-8")
    before = path.read_bytes()
    assert run(repo, "--execute") == 1
    assert path.read_bytes() == before
    assert "FAIL not in " in capsys.readouterr().out


def test_usage_errors(repo):
    assert rs.main(["--responses", str(repo / "responses.json")]) == 2  # no --read-on
    assert rs.main(["--read-on", "2026-12"]) == 2
    assert run(repo, "--only", "wikipedia") == 2


def test_every_probe_is_a_source_of_function_1_in_the_repository():
    """The probes name entries of data/sources.json; their state is not fixed here (the
    monthly pull request may have reopened one), only that they exist."""
    data = {s["id"]: s for s in json.loads((ROOT / "data/sources.json").read_text("utf-8"))}
    for probe in rs.PROBES:
        assert data[probe.source]["function"] == 1
        assert data[probe.source]["state"] in ("active", "suspended", "discarded")
    assert [p.source for p in rs.PROBES] == list(FOUR)
