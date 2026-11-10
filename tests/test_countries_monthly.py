"""The monthly reading of the countries: scripts/countries_monthly.py and countries.yml.

The script runs offline here, on a copy of data/ and of CHANGELOG.md in tmp_path, reading
the fixtures of the two loads (the files of 2026-11-10). What cannot run without a push
(the cron, `gh`, the token) is checked in the text of the workflow: the schedule, the
limits, the permissions, that it never pushes to main, and that every `run` is valid
shell.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import countries_monthly as cm  # noqa: E402

UNTC = ROOT / "tests" / "fixtures" / "untc"
CORNELL = ROOT / "tests" / "fixtures" / "cornell"
WORKFLOW = ROOT / ".github" / "workflows" / "countries.yml"
READ_ON = "2026-12-01"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A copy of data/ and of CHANGELOG.md, and the folders the run reads and writes."""
    for key in ("GITHUB_OUTPUT", "GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"):
        monkeypatch.delenv(key, raising=False)
    shutil.copytree(ROOT / "data", tmp_path / "data")
    shutil.copytree(ROOT / "static" / "data", tmp_path / "static" / "data")
    shutil.copy(ROOT / "CHANGELOG.md", tmp_path / "CHANGELOG.md")
    shutil.copytree(UNTC, tmp_path / "untc")
    shutil.copytree(CORNELL, tmp_path / "cornell")
    return tmp_path


def run(repo: Path, *extra: str) -> int:
    return cm.main(
        [
            "--data", str(repo / "data"),
            "--changelog", str(repo / "CHANGELOG.md"),
            "--xml-dir", str(repo / "untc"),
            "--json-dir", str(repo / "cornell"),
            "--read-on", READ_ON,
            *extra,
        ]
    )  # fmt: skip


def execute(repo: Path) -> int:
    return run(repo, "--execute", "--report-dir", str(repo / "report"))


def report(repo: Path) -> dict[str, str]:
    folder = repo / "report"
    if not folder.is_dir():
        return {}
    return {p.name: p.read_text(encoding="utf-8") for p in folder.iterdir()}


def move_japan(repo: Path) -> None:
    """Cornell moves Japan from the retentionist list to the abolitionist one."""
    folder = repo / "cornell"
    kept = json.loads((folder / "retentionist.json").read_text(encoding="utf-8"))
    japan = next(i for i in kept if i["displayName"] == "Japan")
    kept.remove(japan)
    moved = json.loads((folder / "abolitionist.json").read_text(encoding="utf-8")) + [japan]
    (folder / "retentionist.json").write_text(json.dumps(kept), encoding="utf-8")
    (folder / "abolitionist.json").write_text(json.dumps(moved), encoding="utf-8")


# ------------------------------------------------------------------ the script


def test_a_month_without_news_gives_a_pull_request_with_an_empty_diff(repo, monkeypatch):
    monkeypatch.setenv("GITHUB_OUTPUT", str(repo / "github-output"))
    before = {p: (repo / p).read_bytes() for p in ("data/countries.json", "CHANGELOG.md")}
    assert execute(repo) == 0
    for path, content in before.items():
        assert (repo / path).read_bytes() == content, path
    texts = report(repo)
    assert set(texts) == {"pr-title.txt", "pr-body.md", "commit-message.txt"}
    assert texts["pr-title.txt"] == f"Leitura mensal dos países, {READ_ON}: sem novidade\n"
    body = texts["pr-body.md"]
    assert "Sem novidade: diff vazio" in body
    assert "0 new, 0 changed, 0 kept, 0 left alone" in body
    # the sha256 of every response read: two XML files and four lists
    shas = re.findall(r"sha256 ([0-9a-f]{64})", body)
    assert len(shas) == 6
    assert "cf92b55e7d874a6f885fa99c44c2a132b601bf0e80929dac4dba34cd8fef7501" in shas
    assert "844e476e8ecb78a9b1597417b38fd9f23bed58c53a6edbfa31b0fb16ce738018" in shas
    assert len(re.findall(r"sha256 [0-9a-f]{64}", texts["commit-message.txt"])) == 6
    assert texts["commit-message.txt"].startswith(f"Leitura mensal de {READ_ON}: ")
    outputs = (repo / "github-output").read_text(encoding="utf-8")
    assert outputs.splitlines() == ["pr=yes", "issue=no", "changed=no"]


def test_a_month_with_news_carries_the_data_the_derived_and_the_changelog(repo, monkeypatch):
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/astraea")
    monkeypatch.setenv("GITHUB_RUN_ID", "42")
    move_japan(repo)
    assert execute(repo) == 0
    countries = json.loads((repo / "data/countries.json").read_text(encoding="utf-8"))
    japan = next(c for c in countries if c["id"] == "JPN")["death_penalty"]
    assert japan["status"] == "abolitionist_all_crimes" and japan["read_on"] == READ_ON
    derived = json.loads((repo / "static/data/countries.json").read_text(encoding="utf-8"))
    assert next(c for c in derived if c["id"] == "JPN")["death_penalty"] == japan

    texts = report(repo)
    assert texts["pr-title.txt"] == f"Leitura mensal dos países, {READ_ON}\n"
    body = texts["pr-body.md"]
    assert "Há novidade: 1 bloco novo ou mudado." in body
    assert "changed: JPN.death_penalty: status: 'retentionist' -> 'abolitionist_all_crimes'" in body
    assert "0 new, 1 changed, 0 kept, 0 left alone" in body
    assert "https://github.com/owner/astraea/actions/runs/42" in body
    assert "draft: passed." in body  # the validation line

    changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    entry = changelog.index(f"## {READ_ON} — Leitura mensal dos países (robô, `countries.yml`)")
    assert entry < changelog.index("## 2026-11-10")  # the newest entry first
    assert changelog.index("changed: JPN.death_penalty") > entry
    assert "\r\n" not in changelog
    assert "pr=" not in changelog


def test_a_name_without_a_map_opens_an_issue_and_the_other_load_its_pull_request(repo):
    names = json.loads((repo / "data/cornell-names.json").read_text(encoding="utf-8"))
    names["names"] = [n for n in names["names"] if n["cornell"] != "East Timor"]
    (repo / "data/cornell-names.json").write_text(json.dumps(names), encoding="utf-8")
    before = (repo / "data/countries.json").read_bytes()
    assert execute(repo) == 0
    assert (repo / "data/countries.json").read_bytes() == before
    texts = report(repo)
    assert texts["issue-title.txt"] == (
        f"Leitura mensal dos países falhou ({READ_ON}): pena de morte\n"
    )
    issue = texts["issue-body.md"]
    assert "**Nome sem mapa.**" in issue and "`data/cornell-names.json`" in issue
    assert "'East Timor' is not a name of countries.json" in issue
    assert "Closes #" in issue
    # the treaties still read well: their pull request, saying the other load failed
    assert texts["pr-title.txt"].endswith("sem novidade\n")
    assert "A carga falhou e nada dela foi gravado" in texts["pr-body.md"]
    assert "Pena de morte: a carga falhou" in texts["commit-message.txt"]


def test_a_sentinel_failure_in_both_loads_opens_an_issue_and_no_pull_request(repo):
    xml = repo / "untc" / "IV-1.en.xml"
    xml.write_bytes(xml.read_bytes()[:5000])
    (repo / "cornell" / "retentionist.json").write_bytes(b"<html>Application error</html>")
    assert execute(repo) == 0
    texts = report(repo)
    assert set(texts) == {"issue-title.txt", "issue-body.md"}
    assert texts["issue-title.txt"].endswith("tratados, pena de morte\n")
    assert texts["issue-body.md"].count("**Sentinela.**") == 2


def test_data_the_validator_refuses_opens_an_issue_and_no_pull_request(repo):
    move_japan(repo)
    situations = json.loads((repo / "data/situations.json").read_text(encoding="utf-8"))
    situations[0]["statuses"][0]["code"] = "genocide_found"  # outside the vocabulary
    (repo / "data/situations.json").write_text(
        json.dumps(situations, ensure_ascii=False), encoding="utf-8"
    )
    changelog = (repo / "CHANGELOG.md").read_bytes()
    assert execute(repo) == 0
    texts = report(repo)
    assert set(texts) == {"issue-title.txt", "issue-body.md"}
    assert texts["issue-title.txt"].endswith(": validação\n")
    assert "### Validação (`transform.py --draft`)" in texts["issue-body.md"]
    assert "FAIL check 2" in texts["issue-body.md"]
    assert (repo / "CHANGELOG.md").read_bytes() == changelog  # nothing proposed


def test_simulation_writes_nothing(repo, capsys):
    move_japan(repo)
    before = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    assert run(repo, "--report-dir", str(repo / "report")) == 0
    after = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    assert after == before
    printed = capsys.readouterr().out
    assert f"--- pr-title.txt\nLeitura mensal dos países, {READ_ON}\n" in printed
    assert "would write: " in printed and "simulation: nothing was written" in printed


def test_usage_errors(repo):
    assert cm.main(["--xml-dir", str(repo / "untc")]) == 2  # no --read-on
    assert cm.main(["--read-on", "2026-12"]) == 2
    assert cm.main(["--data", str(repo / "nothing"), "--read-on", READ_ON]) == 2


@pytest.mark.parametrize(
    ("output", "kind"),
    [
        ("FAIL cornell: 'Fooland' is not a name of countries.json nor of …", "name"),
        ("FAIL cornell: 'Macedonia' now comes with isoCode 'MC', and …", "name"),
        ("FAIL GET https://treaties.un.org/x.xml -> HTTP 403: Forbidden", "network"),
        ("FAIL GET https://x/ failed after 3 attempts: timed out", "network"),
        ("FAIL robots.txt does not allow https://x/", "network"),
        ("FAIL the Status block says 41 signatories and 154 parties; the rows …", "sentinel"),
        ("FAIL Retentionist: an empty list", "sentinel"),
    ],
)
def test_what_a_failure_means(output, kind):
    assert cm.kind(cm.Load("x", "X", "src", "names.json", 1, output)) == kind


def test_the_entry_goes_above_the_newest_one():
    text = "# Changelog\n\nIntro.\n\n## 2026-11-10 — old\n\nbody\n"
    new = cm.insert_entry(text, "## 2026-12-01 — new\n\nmore\n\n")
    head, newest, older = new.split("\n## ")
    assert head == "# Changelog\n\nIntro.\n"
    assert newest == "2026-12-01 — new\n\nmore\n"
    assert older == "2026-11-10 — old\n\nbody\n"


def test_a_body_too_long_is_cut_below_the_github_limit():
    assert len(cm._limit("x" * 100_000)) <= cm.BODY_LIMIT
    assert cm._limit("short") == "short"


# ------------------------------------------------------------------ the workflow


@pytest.fixture(scope="module")
def workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def run_blocks(text: str) -> list[str]:
    """The shell of every `run: |` block (and of the one-line `run:`), dedented."""
    blocks, lines = [], text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"(\s*)(?:- )?run: (.*)$", line)
        if not m:
            continue
        if m.group(2).strip() != "|":
            blocks.append(m.group(2))
            continue
        indent, body = None, []
        for nxt in lines[i + 1 :]:
            if nxt.strip() and indent is None:
                indent = len(nxt) - len(nxt.lstrip())
            if nxt.strip() and len(nxt) - len(nxt.lstrip()) < (indent or 0):
                break
            body.append(nxt[indent or 0 :])
        blocks.append("\n".join(body))
    return blocks


def test_schedule_limits_and_concurrency(workflow):
    assert 'cron: "0 5 1 * *"' in workflow  # day 1, 05:00 UTC (docs/04)
    assert "workflow_dispatch:" in workflow
    assert "timeout-minutes: 60" in workflow
    assert re.search(r"concurrency:\n  group: countries\n  cancel-in-progress: false", workflow)


def test_minimal_permissions(workflow):
    block = re.search(r"\npermissions:\n((?:  .+\n)+)", workflow).group(1)
    assert sorted(block.split()) == sorted(
        ["contents:", "write", "pull-requests:", "write", "issues:", "write"]
    )


def test_the_same_action_versions_as_the_ci(workflow):
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    used = set(re.findall(r"uses: (\S+)", workflow))
    assert used == {"actions/checkout@v7", "actions/setup-python@v7"}
    assert used <= set(re.findall(r"uses: (\S+)", ci))


def test_it_never_commits_to_main(workflow):
    pushes = re.findall(r"git push.*", workflow)
    assert pushes == ["git push --force origin robot/countries"]
    assert cm.BRANCH == "robot/countries"
    assert "gh pr create --base main --head robot/countries" in workflow
    assert "git switch -C robot/countries" in workflow
    assert "git merge" not in workflow and "gh pr merge" not in workflow


def test_it_reads_with_execute_and_proposes_only_after_the_battery(workflow):
    assert 'python scripts/countries_monthly.py --execute --report-dir "$REPORT"' in workflow
    battery = workflow.index("name: Battery")
    assert workflow.index("python -m pytest") > battery
    assert workflow.index("name: Open or update the pull request") > battery
    assert "if: failure() || steps.read.outputs.issue == 'yes'" in workflow
    assert "secrets.COUNTRIES_PR_TOKEN || github.token" in workflow


@pytest.mark.skipif(shutil.which("bash") is None, reason="no bash to check the syntax")
def test_every_run_block_is_valid_shell(workflow):
    blocks = run_blocks(workflow)
    assert len(blocks) >= 5
    for block in blocks:
        script = re.sub(r"\$\{\{.*?\}\}", "x", block)
        result = subprocess.run(
            ["bash", "-n"], input=script, capture_output=True, text=True, encoding="utf-8"
        )
        assert result.returncode == 0, (block, result.stderr)
