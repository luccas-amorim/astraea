"""Command line.

    astraea run --config config/news.json
    astraea run --config ... --source rss:un-news-en --since 2026-11-01
    astraea retriage --config ...
    astraea estimate --config ... [--since YYYY-MM-DD]
    astraea validate-lexicon data/lexicon/en.json
    astraea validate-lexicon data/lexicon/*.json
    astraea validate-config config/news.json

Exit codes: 0 nothing to read; 2 execution error or source down; 3 there are items that
need review. `run.json` carries `needs_reading` even when the code is 2: one does not hide
the other.
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import sys
from datetime import date
from pathlib import Path

from astraea import __version__, sources
from astraea.engine import archive, config, estimate, lexicon, outputs
from astraea.engine import run as runs
from astraea.engine.outputs import catalog, observations


def _instances(cfg: config.Config, config_path: str, chosen: list[str] | None):
    selected = [s for s in cfg.sources if not chosen or s["id"] in chosen]
    if chosen and len(selected) != len(set(chosen)):
        raise ValueError(f"unknown source among {chosen}")
    base = str(Path(config_path).resolve().parent)
    return [sources.build({"_config_dir": base, **s}) for s in selected]


def _run(args: argparse.Namespace) -> int:
    cfg = config.load(args.config)
    matcher = lexicon.Matcher(lexicon.load(cfg.lexicon))
    try:
        instances = _instances(cfg, args.config, args.source)
    except ValueError as error:
        print(error, file=sys.stderr)
        return runs.ERROR
    since = date.fromisoformat(args.since) if args.since else None
    result = runs.run(cfg, instances, matcher, since=since, use_state=not args.no_state)
    folder = outputs.write(result, cfg.runs)
    print(f"{len(result.lines)} items; outputs in {folder}")
    _catalogue(cfg, result)
    if result.source_failures and result.needs_reading:
        print("there are items that need reading, besides failed source(s)", file=sys.stderr)
    return result.exit_code


def _catalogue(cfg: config.Config, result: runs.Run) -> None:
    if cfg.catalog_csv is not None:
        new = catalog.update(result, cfg.catalog_csv, cfg.catalog_level, cfg.stratum_of)
        print(f"catalog: {new} new documents in {cfg.catalog_csv}")
    if cfg.observations_csv is not None:
        n = observations.append(result, cfg.observations_csv, cfg.observations_level)
        print(f"observations: {n} sightings in {cfg.observations_csv}")
    if cfg.catalog_csv is not None and cfg.resolve_archive:
        limit = int((cfg.archive or {}).get("rate_limit_per_minute", 15))
        n = catalog.complete_snapshots(
            cfg.catalog_csv, archive.Archive(rate_limit_per_minute=limit).resolve
        )
        print(f"archive: {n} reference copies resolved in the Wayback")


def _retriage(args: argparse.Namespace) -> int:
    cfg = config.load(args.config)
    matcher = lexicon.Matcher(lexicon.load(cfg.lexicon))
    result = runs.retriage(cfg, matcher, args.source)
    folder = outputs.write(result, cfg.runs)
    print(f"{len(result.lines)} items re-triaged; outputs in {folder}")
    _catalogue(cfg, result)
    return result.exit_code


def _estimate(args: argparse.Namespace) -> int:
    cfg = config.load(args.config)
    if cfg.observations_csv is None:
        print('configure "observations" in the configuration to estimate', file=sys.stderr)
        return runs.ERROR
    since = date.fromisoformat(args.since) if args.since else None
    by_stratum = estimate.compute(cfg.observations_csv, args.min_level, cfg.stratum_of, since)
    text = estimate.report(by_stratum, since)
    target = cfg.directory / (args.output or "estimate.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    for name, est in sorted(by_stratum.items()):
        floor = f"{est.chao:,.0f}" if est.chao is not None else "no estimate (a single channel)"
        print(f"{name}: {len(est.observed)} documents observed; estimated floor: {floor}")
    print(f"report in {target}")
    return runs.NOTHING


def _expand(patterns: list[str]) -> list[str]:
    """The files named, with `*` expanded here: PowerShell hands the pattern over as it is."""
    files: list[str] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern)) if glob.has_magic(pattern) else []
        files += matches or [pattern]
    return files


def _validate_lexicon(args: argparse.Namespace) -> int:
    code = runs.NOTHING
    for file in _expand(args.file):
        try:
            lex = lexicon.load(file)
        except lexicon.LexiconError as error:
            print(f"{file}: {error}", file=sys.stderr)
            code = runs.ERROR
            continue
        forms = sum(len(t.forms) for t in lex.terms)
        print(f"{lex.id} {lex.version}: valid, {len(lex.terms)} terms, {forms} forms")
    return code


def _validate_config(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    problems = config.validate(data)
    for s in data.get("sources") or []:
        try:
            sources.build({"_config_dir": str(Path(args.file).parent), **s})
        except (ValueError, KeyError) as error:
            problems.append(f"sources[{s.get('id') or '?'}]: {error}")
    if problems:
        print("invalid configuration:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return runs.ERROR
    print(f"{args.file}: valid, {len(data.get('sources', []))} sources")
    return runs.NOTHING


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="astraea", description=__doc__.split("\n")[0])
    parser.add_argument("--version", action="version", version=f"astraea {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("run", help="one run: list, fetch, triage, record")
    p.add_argument("--config", required=True)
    p.add_argument("--since", help="YYYY-MM-DD; ignores the date kept in the state")
    p.add_argument("--no-state", action="store_true", help="re-reads everything, writes no state")
    p.add_argument("--source", action="append", help="only this source (repeatable)")
    p.set_defaults(func=_run)

    p = sub.add_parser("retriage", help="applies the current lexicon to the stored corpus, offline")
    p.add_argument("--config", required=True)
    p.add_argument("--source")
    p.set_defaults(func=_retriage)

    p = sub.add_parser("estimate", help="how much is missing: capture-recapture across channels")
    p.add_argument("--config", required=True)
    p.add_argument("--min-level", type=int, default=2)
    p.add_argument("--since", help="YYYY-MM-DD: only items from this date on")
    p.add_argument("--output", help="report name inside the directory (default estimate.md)")
    p.set_defaults(func=_estimate)

    p = sub.add_parser("validate-lexicon", help="checks the format of one or more lexicons")
    p.add_argument("file", nargs="+", help="a file, several, or a pattern such as dir/*.json")
    p.set_defaults(func=_validate_lexicon)

    p = sub.add_parser("validate-config", help="checks the configuration: sources, strata, levels")
    p.add_argument("file")
    p.set_defaults(func=_validate_config)

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        return args.func(args)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return runs.ERROR
