#!/usr/bin/env python3
"""Verify translation integrity; optionally export a full AI review bundle."""

import argparse
import json
from pathlib import Path
import sys

from translation_tools.artifacts import check_artifacts, save_bundle
from translation_tools.verify import DEFAULT_CONFIG, ROOT, load_config, review_bundle, verify


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "en-us/docs")
    parser.add_argument("--target", type=Path, default=ROOT / "zh-cn/docs")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--files", nargs="+", default=[], help="Relative paths, directory prefixes, or globs")
    parser.add_argument("--report", type=Path, help="Write machine-readable JSON")
    parser.add_argument("--review-bundle", type=Path, help="Export complete source/target pairs for autonomous AI quality review")
    parser.add_argument("--review-results", type=Path, help="Validate completed AI review coverage and source/target hashes")
    parser.add_argument("--reuse-review", type=Path, help="With --review-bundle, reuse passed reviews for unchanged source and target files")
    parser.add_argument("--summary-only", action="store_true", help="Do not print individual findings; include them in --report")
    parser.add_argument("--strict", action="store_true", help="Treat heuristic warnings as failures too")
    args = parser.parse_args(argv)
    if args.reuse_review and not args.review_bundle:
        parser.error("--reuse-review requires --review-bundle")
    try:
        check_artifacts((args.report, args.review_bundle),
                        (args.review_results, args.reuse_review, args.config, DEFAULT_CONFIG, ROOT / ".env", ROOT / ".env.example"),
                        (args.source, args.target, ROOT / "en-us", ROOT / "zh-cn", ROOT / ".git"))
        config = load_config(args.config)
        reviews = json.loads(args.review_results.read_bytes()) if args.review_results else None
        if args.review_results and not isinstance(reviews, dict):
            raise ValueError("Not a supported semantic review result")
        if args.review_bundle:
            previous = json.loads(args.reuse_review.read_bytes()) if args.reuse_review else None
            bundle = review_bundle(args.source, args.target, config, args.files, previous=previous, review_results=reviews)
            report = bundle["deterministic_report"]
        else:
            report = verify(args.source, args.target, config, args.files, review_results=reviews)
        if args.report:
            save_bundle(args.report, report)
        if args.review_bundle:
            save_bundle(args.review_bundle, bundle)
            print(f"Full pairs for review: {len(bundle['files'])}; unchanged passed reviews reused: {len(bundle['reused_files'])}.")
        if not args.summary_only:
            for issue in report["issues"]:
                if not issue["suppressed"]:
                    print(f"{issue['path']}:{issue['line']}: {issue['severity']} [{issue['code']}] {issue['message']}")
        summary = report["summary"]
        semantic = report["quality"]["semantic_review"]
        print(f"{summary['matched_files']}/{summary['source_files']} files; {summary['errors']} errors; {summary['warnings']} warnings; {summary['suppressed']} exceptions. Semantic review: {semantic}.")
        return int(bool(summary["errors"] or args.strict and summary["warnings"] or args.review_results and semantic != "passed"))
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
