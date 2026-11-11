"""The monthly reading of the countries (.github/workflows/countries.yml) and its report.

Runs the two loads (scripts/load_treaties.py and scripts/load_death_penalty.py) and the
Cartógrafo (scripts/recheck_sources.py, which asks whether the penal-law databases that
were down answer again), then, if data/countries.json or data/sources.json changed,
scripts/transform.py --draft --execute and a CHANGELOG.md entry with the sha256 of each
response (docs/03, "Confiança por registro": a robot
stamp needs the hash registered in the CHANGELOG). It never opens the pull request
itself: it says what the pull request (or the issue) must contain, and the workflow
opens it with `gh`.

    python scripts/countries_monthly.py
        runs the three readings in simulation (reads the sources over the network) and
        prints the pull request or the issue the monthly run would open; writes nothing
    python scripts/countries_monthly.py --execute --report-dir DIR
        runs the three readings with --execute and, when countries.json or sources.json
        changed, the transform
        and the CHANGELOG entry; writes into DIR the texts the workflow uses:
        pr-title.txt, pr-body.md and commit-message.txt (when a pull request is due),
        issue-title.txt and issue-body.md (when a load or the transform failed)
    --xml-dir DIR --json-dir DIR --responses FILE --read-on YYYY-MM-DD
        read the saved files instead of the network (the test fixtures)
    --data DIR --changelog FILE
        other source directory and changelog (tests)

The readings are independent: one that fails opens an issue and writes nothing, and the
others still give their pull request. The Cartógrafo alone does not: when both loads fail,
there is a pull request only if it reopened a source (a source that does not answer is
its usual result, not a failure). A month without news gives a pull request with an
empty commit (data/ and static/data/ unchanged), whose body carries the sha256 of the
responses; a month with news adds the changed blocks, the derived data and the CHANGELOG
entry. When the transform fails, nothing is proposed: an issue only.

Simulation by default; --execute writes; nothing is ever deleted. When GITHUB_OUTPUT is
set (inside Actions) it also writes `pr`, `issue` and `changed` (yes/no) there.

Exit codes: 0 the run went through (its outcome is in the report, even when a load
failed); 2 usage error.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import sys
import traceback
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import load_death_penalty  # noqa: E402
import load_treaties  # noqa: E402
import recheck_sources  # noqa: E402
import transform  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BRANCH = "robot/countries"
BODY_LIMIT = 60_000  # GitHub refuses a pull request or issue body above 65,536 characters
KINDS = ("new", "changed", "kept", "left alone")


@dataclass
class Load:
    key: str  # short id, English
    title: str  # Portuguese: the PR, the issue and the CHANGELOG are in Portuguese
    source: str
    names_file: str
    code: int = 0
    output: str = ""
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def failed(self) -> bool:
        return self.code != 0

    def lines(self) -> list[str]:
        return self.output.rstrip("\n").splitlines()


def _call(main, argv: list[str]) -> tuple[int, str]:
    """Runs a script's main() and returns its exit code and what it printed."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            code = main(argv)
        except Exception:  # an unexpected error is a failure to report, not a crash
            traceback.print_exc(file=buffer)
            code = 1
    return code, buffer.getvalue()


def count(output: str) -> dict[str, int]:
    lines = output.splitlines()
    return {kind: sum(1 for line in lines if line.startswith(kind)) for kind in KINDS}


def run_url() -> str:
    server, repo, run = (
        os.environ.get(k) for k in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID")
    )
    return f"{server}/{repo}/actions/runs/{run}" if server and repo and run else ""


# ------------------------------------------------------------------ what a failure means

NAME = re.compile(
    r"is not a name of countries\.json|now comes with isoCode|not a record|two names map to"
)
# The messages of astraea/engine/http.py: HTTP error, retries exhausted, robots, country.
NETWORK = re.compile(r"-> HTTP \d|failed after \d+ attempts|robots\.txt does not allow|refuses")
HINTS = {
    "name": (
        "**Nome sem mapa.** A fonte trouxe um nome de país que não está em `countries.json` "
        "nem no arquivo de nomes (`data/{names_file}`), ou mudou o código de um nome já "
        "conferido. Confira o nome na tabela M49 da ONU "
        "(https://unstats.un.org/unsd/methodology/m49/overview/), acrescente ou corrija a "
        "linha em `data/{names_file}` e rode o *workflow* de novo."
    ),
    "network": (
        "**Leitura.** A fonte não respondeu, ou respondeu com erro (HTTP 403, 404, 5xx, "
        "tempo esgotado, `robots.txt` que passou a vedar). Rode o *workflow* de novo outro "
        "dia. Se for bloqueio (403, desafio de navegador, bloqueio por país, `robots.txt`), "
        "ele **não se contorna** (regra 7 do `AGENTS.md`): fica registrado aqui e vai para a "
        "próxima sessão."
    ),
    "cartographer": (
        "**Cartógrafo.** A releitura das fontes da lei penal parou antes de perguntar a "
        "todas: uma fonte que ele conhece sumiu de `data/sources.json`, ou houve um erro "
        "inesperado (a saída abaixo diz qual). Fonte que não responde **não** é falha: é o "
        "resultado de quase todo mês. Se alguém tirou a fonte de `sources.json`, a próxima "
        "sessão decide se o Cartógrafo deixa de perguntar por ela."
    ),
    "sentinel": (
        "**Sentinela.** A fonte respondeu, mas não com a tabela que o robô conhece: arquivo "
        "incompleto, contagem que não fecha, página de erro ou de manutenção, formato novo. "
        "Abra a página da fonte no navegador e veja se ela mudou. Se mudou de forma, o "
        "adaptador precisa de uma sessão; se era instabilidade, rode o *workflow* de novo "
        "outro dia."
    ),
}


def kind(load: Load) -> str:
    """What failed: the name map, the network, the table itself (sentinel or format), or
    the Cartógrafo."""
    if load.key == "sources":
        return "cartographer"
    if NAME.search(load.output):
        return "name"
    if NETWORK.search(load.output):
        return "network"
    return "sentinel"


def hint(load: Load) -> str:
    return HINTS[kind(load)].format(names_file=load.names_file)


# ------------------------------------------------------------------ texts


def _block(lines: list[str]) -> str:
    return "```text\n" + "\n".join(lines) + "\n```"


def _tally(load: Load) -> str:
    c = load.counts
    return f"{c['new']} new, {c['changed']} changed, {c['kept']} kept, {c['left alone']} left alone"


def pr_title(read_on: str, changed: bool) -> str:
    title = f"Leitura mensal dos países, {read_on}"
    return title if changed else f"{title}: sem novidade"


def pr_body(read_on: str, loads: list[Load], changed: bool, transform_out: str) -> str:
    url = run_url()
    parts = [
        f"Leitura mensal de {read_on} pelo `countries.yml`"
        + (f" ([execução]({url}))" if url else "")
        + ". As duas cargas e o Cartógrafo leram as fontes pelo cliente HTTP do motor, "
        "com o `User-Agent` do Astraea e o `robots.txt` obedecido.",
        "",
    ]
    if changed:
        ok = [ld for ld in loads if not ld.failed]
        blocks = sum(ld.counts["new"] + ld.counts["changed"] for ld in ok if ld.key != "sources")
        reopened = sum(ld.counts["changed"] for ld in ok if ld.key == "sources")
        what = "bloco novo ou mudado" if blocks == 1 else "blocos novos ou mudados"
        news = f"{blocks} {what}"
        if reopened:
            news += " e 1 fonte reaberta" if reopened == 1 else f" e {reopened} fontes reabertas"
        parts += [
            f"**Há novidade: {news}.** O PR traz o que mudou em `data/countries.json` e "
            "`data/sources.json`, o derivado (`static/data/`, gerado por `transform.py "
            "--draft --execute`) e a entrada do `CHANGELOG.md` com os sha256.",
        ]
    else:
        parts += [
            "**Sem novidade: diff vazio.** `data/` e `static/data/` não mudaram; o commit é "
            "vazio e só guarda, na mensagem, os sha256 das respostas lidas.",
        ]
    for load in loads:
        parts += ["", f"### {load.title} (`{load.source}`)", ""]
        if load.failed:
            parts += [
                "**A carga falhou e nada dela foi gravado**: a issue aberta nesta mesma "
                "execução diz o que houve. Este PR traz só a outra carga.",
                "",
            ]
        else:
            parts += [_tally(load), ""]
        parts += [_block(load.lines())]
    if changed and transform_out:
        last = [line for line in transform_out.splitlines() if line.startswith("draft:")]
        if last:
            parts += ["", "### Validação", "", _block(last)]
    parts += ["", "### O que fazer", ""]
    if changed:
        parts += [
            "1. Abra a aba **Files changed** e leia as mudanças de `data/countries.json` e "
            "de `data/sources.json`: cada uma corresponde a uma linha `new:` ou `changed:` "
            "acima. Uma fonte reaberta pelo Cartógrafo (`state` de `suspended` para "
            "`active`) só quer dizer que a página respondeu; se o `reason` disser que o "
            "`robots.txt` veda agentes de IA, nenhuma sessão que seja modelo a lê.",
            "2. Se quiser, confira a mudança na página da fonte (o `url` do bloco).",
            "3. Espere a CI ficar verde e clique em **Merge pull request**.",
        ]
    else:
        parts += [
            "Nada a conferir. **Merge pull request** guarda a leitura no histórico (e mantém "
            "o repositório ativo, o que impede o GitHub de desligar o agendamento); fechar o "
            "PR sem merge também serve.",
        ]
    parts += [
        "",
        "Se o PR acusar conflito (*This branch has conflicts*), feche-o e rode de novo em "
        "**Actions → Countries → Run workflow**: o robô relê as fontes a partir da `main`.",
    ]
    return _limit("\n".join(parts) + "\n")


def commit_message(read_on: str, loads: list[Load], changed: bool) -> str:
    head = (
        f"Lê tratados, pena de morte e fontes da lei penal (leitura mensal de {read_on})"
        if changed
        else f"Leitura mensal de {read_on}: tratados, pena de morte e fontes sem novidade"
    )
    lines = [head, ""]
    for load in loads:
        if load.failed:
            lines.append(f"{load.title}: a carga falhou; nada gravado (ver a issue).")
            continue
        lines.append(f"{load.title}: {_tally(load)}.")
        lines += [line for line in load.lines() if "sha256" in line]
    url = run_url()
    if url:
        lines += ["", f"Execução: {url}"]
    return "\n".join(lines) + "\n"


def issue_title(read_on: str, failed: list[Load], transform_failed: bool) -> str:
    what = [ld.title.lower() for ld in failed]
    if transform_failed:
        what.append("validação")
    return f"Leitura mensal dos países falhou ({read_on}): " + ", ".join(what)


def issue_body(read_on: str, failed: list[Load], transform_out: str | None) -> str:
    url = run_url()
    parts = [
        f"A leitura mensal de {read_on} pelo `countries.yml`"
        + (f" ([execução]({url}))" if url else "")
        + " não pôde ser proposta como PR no que vai abaixo. **Nada disso foi gravado na "
        "`main`.**",
    ]
    for load in failed:
        parts += ["", f"### {load.title} (`{load.source}`)", "", hint(load), "", "Saída:", ""]
        parts += [_block(load.lines())]
    if transform_out is not None:
        parts += [
            "",
            "### Validação (`transform.py --draft`)",
            "",
            "As cargas leram as fontes, mas os dados novos não passam no validador: o PR "
            "não foi aberto, para não propor dado que a CI reprovaria. As linhas `FAIL` "
            "dizem a trava e o registro.",
            "",
            _block(transform_out.rstrip("\n").splitlines()),
        ]
    parts += [
        "",
        "### Depois de resolver",
        "",
        "Rode de novo em **Actions → Countries → Run workflow**. Quando o PR vier, ou se "
        "não houver o que corrigir, feche esta issue: no commit da correção, escreva "
        "`Closes #<número desta issue>` na mensagem, ou clique em **Close issue** com um "
        "comentário dizendo por quê.",
    ]
    return _limit("\n".join(parts) + "\n")


def _limit(text: str) -> str:
    if len(text) <= BODY_LIMIT:
        return text
    cut = "\n\n(corte: o texto passava do limite do GitHub; a saída inteira está no log)\n```\n"
    return text[: BODY_LIMIT - len(cut)] + cut


def changelog_entry(read_on: str, loads: list[Load]) -> str:
    url = run_url()
    parts = [
        f"## {read_on} — Leitura mensal dos países (robô, `countries.yml`)",
        "",
        "Leitura automática, não sessão: `load_treaties.py --execute`, "
        "`load_death_penalty.py --execute`, `recheck_sources.py --execute` (o Cartógrafo) e "
        "`transform.py --draft --execute`, pelo cliente "
        "HTTP do motor, com o `User-Agent` do Astraea e o `robots.txt` obedecido"
        + (f" ([execução]({url}))" if url else "")
        + ". As linhas `new:` e `changed:` são o dado que mudou; os sha256 são das respostas "
        'lidas, e é o registro deles aqui que vale como carimbo `robot` (`03`, "Confiança '
        'por registro").',
    ]
    for load in loads:
        parts += ["", f"**{load.title} (`{load.source}`).**"]
        if load.failed:
            parts[-1] += " A carga falhou e nada dela foi gravado; uma issue foi aberta."
            continue
        parts += ["", _block(load.lines())]
    return "\n".join(parts) + "\n\n"


def insert_entry(changelog: str, entry: str) -> str:
    """The entry goes above the first `## ` heading: the newest entry first."""
    at = changelog.find("\n## ")
    if at < 0:
        return changelog.rstrip("\n") + "\n\n" + entry
    return changelog[: at + 1] + entry + changelog[at + 1 :]


# ------------------------------------------------------------------ command line


def _outputs(**values: bool) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={'yes' if value else 'no'}\n")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--execute", action="store_true", help="write (default: simulation)")
    parser.add_argument("--report-dir", help="where to write the texts of the PR and the issue")
    parser.add_argument("--xml-dir", help="read the UNTC files from here (with --read-on)")
    parser.add_argument("--json-dir", help="read the Cornell files from here (with --read-on)")
    parser.add_argument("--responses", help="the Cartógrafo's recorded responses (--read-on)")
    parser.add_argument("--read-on", help="date of the reading, YYYY-MM-DD")
    parser.add_argument("--data", help="source directory (default: data/)")
    parser.add_argument("--changelog", help="changelog file (default: CHANGELOG.md)")
    args = parser.parse_args(argv)

    if (args.xml_dir or args.json_dir or args.responses) and not args.read_on:
        print("--xml-dir, --json-dir and --responses need --read-on", file=sys.stderr)
        return 2
    read_on = args.read_on or date.today().isoformat()
    if not transform.is_full_date(read_on):
        print(f"--read-on {read_on!r} is not a date YYYY-MM-DD", file=sys.stderr)
        return 2
    data = Path(args.data) if args.data else ROOT / "data"
    changelog = Path(args.changelog) if args.changelog else ROOT / "CHANGELOG.md"
    countries = data / "countries.json"
    sources = data / "sources.json"
    if not countries.is_file():
        print(f"{transform.show(countries)}: not found", file=sys.stderr)
        return 2

    common = ["--data", str(data), *(["--execute"] if args.execute else [])]
    if args.read_on:
        common += ["--read-on", args.read_on]
    loads = [
        Load("treaties", "Tratados", "untc", load_treaties.NAMES_FILE),
        Load("death_penalty", "Pena de morte", "cornell-dpw", load_death_penalty.NAMES_FILE),
        Load("sources", "Fontes da lei penal (Cartógrafo)", "sources.json", ""),
    ]
    extra = {
        "treaties": ["--xml-dir", args.xml_dir] if args.xml_dir else [],
        "death_penalty": ["--json-dir", args.json_dir] if args.json_dir else [],
        "sources": ["--responses", args.responses] if args.responses else [],
    }
    mains = {
        "treaties": load_treaties.main,
        "death_penalty": load_death_penalty.main,
        "sources": recheck_sources.main,
    }

    def written() -> tuple[bytes, bytes]:
        return countries.read_bytes(), sources.read_bytes()

    before = written()
    for load in loads:
        load.code, load.output = _call(mains[load.key], [*common, *extra[load.key]])
        load.counts = count(load.output)
        print(f"--- {load.key} (exit {load.code})")
        print(load.output, end="")
    if args.execute:
        changed = written() != before
    else:
        changed = any("would write:" in ld.output for ld in loads if not ld.failed)

    transform_out = ""
    transform_failed = False
    if changed and args.execute:
        code, transform_out = _call(transform.main, ["--draft", "--execute", "--data", str(data)])
        print(f"--- transform (exit {code})")
        print(transform_out, end="")
        transform_failed = code != 0
    elif changed:
        print("--- transform: not run in simulation (it would validate the data as it is)")

    failed = [ld for ld in loads if ld.failed]
    # The Cartógrafo alone gives no pull request: one of the two loads has to have read,
    # or a source has to have been reopened.
    loads_read = any(not ld.failed for ld in loads if ld.key != "sources")
    pr_due = not transform_failed and (loads_read or changed)
    issue_due = bool(failed) or transform_failed
    texts: dict[str, str] = {}
    if pr_due:
        texts["pr-title.txt"] = pr_title(read_on, changed) + "\n"
        texts["pr-body.md"] = pr_body(read_on, loads, changed, transform_out)
        texts["commit-message.txt"] = commit_message(read_on, loads, changed)
    if issue_due:
        texts["issue-title.txt"] = issue_title(read_on, failed, transform_failed) + "\n"
        texts["issue-body.md"] = issue_body(
            read_on, failed, transform_out if transform_failed else None
        )

    if changed and pr_due:
        entry = changelog_entry(read_on, loads)
        if args.execute:
            text = changelog.read_text(encoding="utf-8")
            changelog.write_text(insert_entry(text, entry), encoding="utf-8", newline="\n")
            print(f"wrote: {transform.show(changelog)} (entry of {read_on})")
        else:
            print(f"would write: {transform.show(changelog)} (entry of {read_on})")

    yes = {True: "yes", False: "no"}
    outcome = f"pull request {yes[pr_due]}, issue {yes[issue_due]}, data changed {yes[changed]}"
    print(f"--- outcome: {outcome}")
    if args.report_dir and args.execute:
        out = Path(args.report_dir)
        out.mkdir(parents=True, exist_ok=True)
        for name, text in texts.items():
            (out / name).write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote: {transform.show(out / name)}")
    else:
        for name, text in texts.items():
            print(f"--- {name}")
            print(text, end="")
        if not args.execute:
            print("simulation: nothing was written; add --execute to write")
    _outputs(pr=pr_due, issue=issue_due, changed=changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
