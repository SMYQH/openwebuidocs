"""Re-bind exact exceptions to their findings after translation edits.

An exception is bound to a fingerprint that mixes the file path, the upstream
and target hashes, the finding line, the finding code and the finding text.
Any edit to a translated file therefore invalidates the exceptions that
belonged to it, even when the underlying finding is unchanged.

This tool matches the findings of a current audit against the findings of a
baseline audit. When a finding still exists with the same path, code and
normalized message, and the baseline finding carried an exception reason, the
exception is re-stamped with the current fingerprint and keeps its reason.
Findings that no longer exist drop their exception. Findings without a
baseline counterpart stay visible for manual review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_DIR / "translation_config.json"


def normalize(message: str) -> str:
    """Compare finding text without its counts and line-specific numbers."""
    text = " ".join(message.split())
    for token in ("×", "x"):
        parts = text.split(token)
        text = token.join(part if i % 2 == 0 else "#" for i, part in enumerate(parts))
    return "".join(ch if not ch.isdigit() else "#" for ch in text)


def collect(report: dict) -> list[dict]:
    return [issue for issue in report.get("issues", []) if issue.get("code")]


def restamp(baseline: dict, current: dict, config: dict) -> tuple[list[dict], list[dict]]:
    """Return the updated exception list and the findings that need review."""
    reasons = {entry["fingerprint"]: entry["reason"] for entry in config["exceptions"]}
    baseline_by_key: dict[tuple[str, str, str], list[dict]] = {}
    for issue in collect(baseline):
        key = (issue["path"], issue["code"], normalize(issue["message"]))
        baseline_by_key.setdefault(key, []).append(issue)

    current_suppressed = {issue["fingerprint"] for issue in collect(current) if issue.get("suppressed")}
    kept = [entry for entry in config["exceptions"] if entry["fingerprint"] in current_suppressed]

    added: list[dict] = []
    review: list[dict] = []
    for issue in collect(current):
        if issue.get("suppressed"):
            continue
        key = (issue["path"], issue["code"], normalize(issue["message"]))
        reason = None
        for candidate in baseline_by_key.get(key, []):
            if candidate.get("suppressed") and candidate["fingerprint"] in reasons:
                reason = reasons[candidate["fingerprint"]]
                break
        if reason is None:
            if issue.get("severity") in {"error", "warning"}:
                review.append(issue)
            continue
        added.append({"fingerprint": issue["fingerprint"], "reason": reason})

    return kept + added, review


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--baseline", required=True, type=Path, help="audit report taken before the edits")
    parser.add_argument("--current", required=True, type=Path, help="audit report taken after the edits")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    current = json.loads(args.current.read_text(encoding="utf-8"))
    config = json.loads(args.config.read_text(encoding="utf-8"))

    updated, review = restamp(baseline, current, config)
    before = {entry["fingerprint"] for entry in config["exceptions"]}
    after = {entry["fingerprint"] for entry in updated}
    restamped = len(after - before)
    print(f"exceptions before {len(config['exceptions'])}, after {len(updated)}, "
          f"kept {len(after & before)}, restamped {restamped}, dropped {len(before - after)}")
    for issue in review:
        print(f"REVIEW {issue['path']}: {issue['code']}: {issue['message']}")
    if args.dry_run:
        print("dry run: config not written")
        return 0
    config["exceptions"] = updated
    args.config.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
