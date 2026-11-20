#!/usr/bin/env python3
"""Translate text, check quota, or collect DeepL review evidence for installed docs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from translation_tools import backtranslation
from translation_tools.artifacts import check_artifacts, save_bundle
from translation_tools.update import DeepL
from translation_tools.verify import DEFAULT_CONFIG, ROOT, load_config


def review(args: argparse.Namespace, client: DeepL) -> None:
    check_artifacts((args.report,), (args.config, DEFAULT_CONFIG, ROOT / ".env", ROOT / ".env.example"),
                    (args.source, args.target, ROOT / "en-us", ROOT / "zh-cn", ROOT / ".git"))
    if args.report and args.report.exists() and not args.resume and not args.plan:
        raise ValueError("Review report already exists. Use --resume or choose a new path")
    report = backtranslation.prepare(args.source, args.target, load_config(args.config), args.files)
    texts = backtranslation.request_texts(report)
    if args.resume:
        backtranslation.restore(report, json.loads(args.report.read_bytes()), texts)
    pending = backtranslation.pending_texts(report, texts)
    characters = sum(map(len, pending.values()))
    print(f"{len(report['files'])} files. {len(texts) - len(pending)} cached texts. "
          f"{len(pending)} pending texts ({characters:,} characters).", flush=True)
    if args.plan:
        if args.partial and args.max_characters is not None:
            batch = backtranslation.within_budget(pending, args.max_characters)
            print(f"Within budget: {len(batch)} texts ({sum(map(len, batch.values())):,} characters).")
        return
    if args.max_characters is not None and characters > args.max_characters and not args.partial:
        raise ValueError(f"Review exceeds --max-characters ({args.max_characters:,})")
    if pending:
        usage = client.usage()
        available = usage["character_limit"] - usage["character_count"]
        if "api_key_character_limit" in usage and "api_key_character_count" in usage:
            available = min(available, usage["api_key_character_limit"] - usage["api_key_character_count"])
        if characters > available and not args.partial:
            raise ValueError(f"Review needs {characters:,} characters. DeepL has {max(available, 0):,} available")
        if args.partial:
            limit = min(available, args.max_characters) if args.max_characters is not None else available
            pending = backtranslation.within_budget(pending, limit)
            print(f"Sending {len(pending)} texts ({sum(map(len, pending.values())):,} characters).", flush=True)
        backtranslation.collect(report, pending, client, args.report)
    backtranslation.add_comparisons(report)
    save_bundle(args.report, report)
    remaining = len(texts) - len(report["translations"])
    print(f"Saved DeepL review evidence to {args.report}. {remaining} texts pending.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    translate = commands.add_parser("translate", help="Translate text or UTF-8 stdin")
    translate.add_argument("text", nargs="?", help="Text to translate, or - for stdin")
    translate.add_argument("--from", dest="source_lang", type=str.upper, help="Source language (default: detect)")
    translate.add_argument("--to", dest="target_lang", type=str.upper, default="ZH-HANS",
                           help="Target language (default: ZH-HANS)")
    commands.add_parser("usage", help="Show DeepL character usage and limits as JSON")
    audit = commands.add_parser("review", help="Back-translate Chinese prose for bilingual review")
    audit.add_argument("--source", type=Path, default=ROOT / "en-us/docs")
    audit.add_argument("--target", type=Path, default=ROOT / "zh-cn/docs")
    audit.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    audit.add_argument("--files", nargs="+", default=[], help="Relative paths, directory prefixes, or globs")
    audit.add_argument("--report", type=Path, help="Checkpoint and final JSON report")
    audit.add_argument("--plan", action="store_true", help="Estimate pending characters without contacting DeepL")
    audit.add_argument("--resume", action="store_true", help="Reuse replies in --report for the same snapshot")
    audit.add_argument("--max-characters", type=int, help="Maximum pending characters to send on this run")
    audit.add_argument("--partial", action="store_true", help="Collect as much evidence as the budget allows")
    args = parser.parse_args(argv)
    if args.command == "review" and (args.resume or not args.plan) and args.report is None:
        parser.error("review requires --report unless using --plan without --resume")
    if args.command == "review" and args.max_characters is not None and args.max_characters < 0:
        parser.error("--max-characters must be nonnegative")
    try:
        client = DeepL()
        if args.command == "review":
            review(args, client)
        elif args.command == "usage":
            print(json.dumps(client.usage(), indent=2))
        else:
            text = args.text
            if text is None or text == "-":
                if sys.stdin.isatty() and text is None:
                    parser.error("provide text or pipe UTF-8 input")
                text = sys.stdin.buffer.read().decode("utf-8-sig")
            if not text.strip():
                raise ValueError("Provide nonempty text to translate")
            print(client.translate([text], source_lang=args.source_lang, target_lang=args.target_lang)[0])
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"DeepL CLI failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
