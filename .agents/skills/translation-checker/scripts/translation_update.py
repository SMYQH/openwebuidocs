#!/usr/bin/env python3
"""Prepare autonomous AI tasks or DeepL translations, then validate/apply."""

import argparse
import json
from pathlib import Path
import sys

from translation_tools.artifacts import check_artifacts, save_bundle
from translation_tools.update import DeepL, apply_bundle, pending_segments, prepare, reuse_completed, translation_plan, validate_task
from translation_tools.verify import DEFAULT_CONFIG, ROOT, load_config


def main(argv=None):
    parser = argparse.ArgumentParser(prog="translation-update", description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "en-us/docs")
    parser.add_argument("--target", type=Path, default=ROOT / "zh-cn/docs")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--files", nargs="+", default=[], help="Source-relative paths, directories, or globs")
    parser.add_argument("--mode", choices=["autonomous", "deepl"], default="autonomous")
    parser.add_argument("--bundle", type=Path, help="Prepared task/output JSON (required unless --apply)")
    parser.add_argument("--apply", type=Path, help="Validate a completed task bundle")
    parser.add_argument("--write", action="store_true", help="Write validated translations; default is validation only")
    parser.add_argument("--review-results", type=Path, help="Validate completed full-pair review of the exact candidate bytes")
    parser.add_argument("--resume", action="store_true", help="Resume an existing DeepL bundle without repeating completed requests")
    parser.add_argument("--reuse", type=Path, help="Copy exact unchanged segments from an earlier DeepL checkpoint into a new task")
    parser.add_argument("--retry-rejected", action="store_true", help="With --resume, retry only rejected legacy XML or use fixed order after XML v2")
    parser.add_argument("--plan", action="store_true", help="Show local file/segment/character counts without API calls or writes")
    parser.add_argument("--report", type=Path, help="Write candidate pairs and detailed verifier findings, including on validation failure")
    args = parser.parse_args(argv)
    if args.apply and (args.bundle or args.mode != "autonomous" or args.files or args.resume or args.plan):
        parser.error("--apply cannot be combined with --bundle, --mode deepl, --files, --resume, or --plan")
    if not args.bundle and not args.apply and not args.plan:
        parser.error("--bundle is required when preparing translations")
    if args.resume and (args.mode != "deepl" or not args.bundle or args.files):
        parser.error("--resume requires --mode deepl and --bundle, without --files")
    if args.reuse and (args.mode != "deepl" or args.resume or args.apply):
        parser.error("--reuse requires a new DeepL task")
    if args.retry_rejected and (not args.resume or args.plan):
        parser.error("--retry-rejected requires a DeepL resume without --plan")
    if args.write and (not args.apply or not args.review_results):
        parser.error("--write requires --apply and --review-results")
    if args.review_results and not args.apply:
        parser.error("--review-results requires --apply")
    if args.report and (args.plan or not args.apply and args.mode != "deepl"):
        parser.error("--report requires DeepL or --apply, without --plan")
    if args.mode == "deepl" and not args.files and not args.resume:
        parser.error("DeepL preparation requires explicit --files to bound paid requests")
    report = {"schema_version": 1, "purpose": "translation-candidate-report", "files": [],
              "semantic_review": "required", "validation": "incomplete"}
    report_safe, exit_code = False, 0
    try:
        check_artifacts((args.bundle, args.report),
                        (args.apply, args.reuse, args.review_results, args.config, DEFAULT_CONFIG, ROOT / ".env", ROOT / ".env.example"),
                        (args.source, args.target, ROOT / "en-us", ROOT / "zh-cn", ROOT / ".git"))
        report_safe = True
        config = load_config(args.config)
        if args.apply:
            bundle = json.loads(args.apply.read_text(encoding="utf-8"))
        else:
            if args.resume:
                bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
                if not isinstance(bundle, dict) or bundle.get("provider") != "deepl":
                    raise ValueError("--resume requires a DeepL checkpoint")
            else:
                if args.bundle and args.bundle.exists() and not args.plan:
                    raise ValueError("Bundle already exists; use --resume for DeepL or choose another path")
                bundle = prepare(args.source, args.target, config, args.files)
            documents = validate_task(bundle, args.source, args.target, config) if args.mode == "deepl" else None
            if args.reuse:
                reuse_completed(bundle, json.loads(args.reuse.read_bytes()), documents, config)
            if args.plan:
                print(json.dumps(translation_plan(bundle, documents)))
                return 0
            if args.mode == "autonomous":
                save_bundle(args.bundle, bundle)
                print(f"Prepared {len(bundle['files'])} file(s). Fill translation fields, then run --apply.")
                return 0
            bundle["provider"] = "deepl"
            save_bundle(args.bundle, bundle)
            if pending_segments(bundle):
                DeepL().fill(bundle, checkpoint=lambda value: save_bundle(args.bundle, value),
                             documents=documents, retry_rejected=args.retry_rejected)
        if args.retry_rejected and (pending := pending_segments(bundle)):
            print(f"Checkpoint updated. {len(pending)} segments still pending; run --resume to continue.")
        else:
            reviews = json.loads(args.review_results.read_bytes()) if args.review_results else None
            if args.review_results and not isinstance(reviews, dict):
                raise ValueError("Not a supported semantic review result")
            outputs = apply_bundle(bundle, args.source, args.target, config, args.write, report, review_results=reviews)
            review_status = "Semantic review passed." if reviews is not None else "Semantic review required before writing."
            print(f"{'Wrote' if args.write else 'Validated'} {len(outputs)} file(s). {review_status} Production build required after writing.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Translation update failed: {error}", file=sys.stderr)
        report.update(validation="blocked", error=str(error))
        exit_code = 2
    if args.report and report_safe:
        try:
            save_bundle(args.report, report)
        except OSError as error:
            print(f"Could not write candidate report: {error}", file=sys.stderr)
            exit_code = 2
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
