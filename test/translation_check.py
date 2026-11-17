#!/usr/bin/env python3
"""Verify translation integrity; optionally export a full AI review bundle."""

import argparse
import json
from pathlib import Path
import sys

from translation_tools.verify import DEFAULT_CONFIG, ROOT, load_config, review_bundle, validate_review, verify


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "en-us/docs")
    parser.add_argument("--target", type=Path, default=ROOT / "zh-cn/docs")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--files", nargs="+", default=[], help="Relative paths, directory prefixes, or globs")
    parser.add_argument("--report", type=Path, help="Write machine-readable JSON")
    parser.add_argument("--review-bundle", type=Path, help="Export complete source/target pairs for autonomous AI quality review")
    parser.add_argument("--review-results", type=Path, help="Validate completed AI review coverage and source/target hashes")
    parser.add_argument("--strict", action="store_true", help="Treat heuristic warnings as failures too")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        report = verify(args.source, args.target, config, args.files)
        if args.review_results:
            report["quality"] = validate_review(json.loads(args.review_results.read_text(encoding="utf-8")), args.source, args.target, args.files)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.review_bundle:
            args.review_bundle.parent.mkdir(parents=True, exist_ok=True)
            args.review_bundle.write_text(json.dumps(review_bundle(args.source, args.target, config, args.files), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
