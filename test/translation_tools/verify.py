"""Deterministic checks and explicit quality signals, never a semantic pass claim."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from fnmatch import fnmatchcase
import json
from pathlib import Path
import re

from .document import ATTRIBUTE, CJK, WORDS, Document, digest, inline_protected, prose


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "test/translation_config.json"
SUFFIXES = {".md", ".mdx"}


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) - {"terms", "untranslated_min_words", "length_ratio_warning", "exceptions"}:
        raise ValueError("Invalid verifier configuration keys")
    if not isinstance(config.get("terms"), list) or not all(isinstance(t, str) and t for t in config["terms"]):
        raise ValueError("Configuration terms must be nonempty strings")
    if not isinstance(config.get("untranslated_min_words"), int) or config["untranslated_min_words"] < 1:
        raise ValueError("untranslated_min_words must be a positive integer")
    if not isinstance(config.get("length_ratio_warning"), (int, float)) or not 0 < config["length_ratio_warning"] < 1:
        raise ValueError("length_ratio_warning must be between 0 and 1")
    if not isinstance(config.get("exceptions"), list):
        raise ValueError("exceptions must be an array")
    for exception in config["exceptions"]:
        if set(exception) != {"fingerprint", "reason"} or not re.fullmatch(r"[0-9a-f]{64}", exception["fingerprint"]) or not exception["reason"].strip():
            raise ValueError("Each exception needs an exact fingerprint and a nonempty reason")
    return config


def files(root: Path) -> dict[str, Path]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and (path.suffix.lower() in SUFFIXES or path.name == "_category_.json"):
            if not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("Documentation symlink escapes selected root")
            result[path.relative_to(root).as_posix()] = path
    return result


def selected(path: str, patterns: list[str]) -> bool:
    return not patterns or any(fnmatchcase(path, p) or path.startswith(p.rstrip("/") + "/") for p in patterns)


@dataclass
class Issue:
    path: str
    line: int
    severity: str
    code: str
    message: str
    fingerprint: str = ""
    suppressed: bool = False
    reason: str = ""


def metadata_literals(value):
    if isinstance(value, dict):
        return {k: metadata_literals(v) for k, v in value.items() if k not in {"title", "sidebar_label", "description", "keywords", "label"}}
    if isinstance(value, list):
        return [metadata_literals(v) for v in value]
    return value


def count_literals(doc: Document, kind: str) -> Counter:
    if not hasattr(doc, "_literal_counts"):
        doc._literal_counts = {}
        # Tokenize each segment once, not once per check kind.
        for segment in doc.segments:
            for span in inline_protected(segment.text, doc.terms):
                doc._literal_counts.setdefault(span.kind, Counter())[span.value] += 1
    # Include structural MDX expressions/tags excluded from multiline segments.
    if kind in {"jsx", "expression", "comment", "math"}:
        return Counter(ATTRIBUTE.sub(lambda m: m[1] + '="<prose>"', p.value) if kind == "jsx" else p.value
                       for p in getattr(doc, "literal_spans", []) if p.kind == kind)
    return doc._literal_counts.get(kind, Counter())


def difference(a: Counter, b: Counter) -> str:
    missing, added = a - b, b - a
    def brief(values):
        return ", ".join(f"{v[:100]!r} ×{n}" for v, n in list(values.items())[:5]) or "none"
    return f"Missing: {brief(missing)}; added: {brief(added)}"


def compare(path: str, source: Document, target: Document, config: dict) -> list[Issue]:
    issues: list[Issue] = []

    def add(code: str, message: str, line: int = 1, severity: str = "error") -> None:
        issues.append(Issue(path, line, severity, code, message))

    for line, error in source.errors:
        add("source-parse", error, line)
    for line, error in target.errors:
        add("target-parse", error, line)
    if metadata_literals(source.metadata) != metadata_literals(target.metadata):
        add("metadata-literal", "Non-translatable metadata keys or values changed")
    # Localizable fields may change values, but must not silently disappear.
    if isinstance(source.metadata, dict) and isinstance(target.metadata, dict):
        if set(source.metadata) != set(target.metadata):
            add("metadata-fields", "Metadata field set differs from upstream")
    src_code, dst_code = [v for _, v in source.code], [v for _, v in target.code]
    if src_code != dst_code:
        add("code-changed", "Code block content/order differs from upstream; comments are literal too")
    if source.opaque_code != target.opaque_code:
        add("opaque-code-changed", "MDX imports/exports or script/style content changed")
    if source.fences != target.fences:
        add("fence-structure", "Code fence delimiters or language metadata changed")
    src_head, dst_head = [(v[0], v[3]) for v in source.headings], [(v[0], v[3]) for v in target.headings]
    if src_head != dst_head:
        add("heading-structure", f"Heading levels/order/anchors differ (source {len(src_head)}, target {len(dst_head)}). "
            + difference(Counter(src_head), Counter(dst_head)))
    anchors = [v[3] for v in target.headings]
    if len(anchors) != len(set(anchors)):
        add("duplicate-anchor", "Target has duplicate explicit heading anchors")
    if source.structure != target.structure:
        add("markdown-structure", "Lists, table cells, blockquotes, or thematic breaks differ", severity="warning")
    if source.admonitions != target.admonitions:
        add("admonition-structure", "Admonition types/order differ")
    for kind in ["marker", "symbol"]:
        a, b = count_literals(source, kind), count_literals(target, kind)
        if a != b:
            add("markdown-" + kind, difference(a, b), severity="warning")
    for kind in ["inline_code", "identifier", "term", "destination", "url", "reference", "jsx", "expression", "math", "comment"]:
        a, b = count_literals(source, kind), count_literals(target, kind)
        if a != b:
            add("literal-" + kind.replace("_", "-"), difference(a, b))
    a, b = count_literals(source, "number"), count_literals(target, "number")
    if a != b:
        add("numbers", difference(a, b), severity="warning")
    for doc, code in [(source, "source-corruption"), (target, "target-corruption")]:
        if "\ufffd" in doc.text:
            add(code, "Unicode replacement character U+FFFD found", doc.line(doc.text.index("\ufffd")))
    source_prose = [prose(s.text, source.terms) for s in source.segments]
    normalized_source = {re.sub(r"\s+", " ", p).strip().lower() for p in source_prose}
    for segment in target.segments:
        value = prose(segment.text, target.terms)
        words = WORDS.findall(value)
        normalized = re.sub(r"\s+", " ", value).strip().lower()
        if len(words) >= config["untranslated_min_words"] and not CJK.search(value):
            add("untranslated-prose", "English prose remains after excluding terminology, code, and markup", target.line(segment.start), "warning")
        elif len(words) >= 3 and normalized in normalized_source and not CJK.search(value):
            add("unchanged-prose", "Prose matches upstream verbatim", target.line(segment.start), "warning")
        if words and not CJK.search(value) and segment.kind in {"yaml", "json", "attribute"}:
            add("untranslated-metadata", "Localizable metadata or accessibility text remains English after exclusions", target.line(segment.start), "warning")
    for _, line, title, _ in target.headings:
        value = prose(title, target.terms)
        if WORDS.search(value) and not CJK.search(value):
            add("untranslated-heading", "Heading remains English after terminology/code exclusions", line, "warning")
    # Compare every matched section even when heading counts differ. Alignment
    # follows anchors, not heading position, so one omission cannot shift all checks.
    def sections(doc):
        result = {}
        heading_offsets = [(line, anchor) for _, line, _, anchor in doc.headings]
        for i, (line, anchor) in enumerate([(0, "<preamble>")] + heading_offsets):
            end = heading_offsets[i][0] if i < len(heading_offsets) else doc.text.count("\n") + 2
            content = " ".join(prose(s.text, doc.terms) for s in doc.segments if line < doc.line(s.start) < end)
            result[anchor] = (line, content)
        return result
    src_sections, dst_sections = sections(source), sections(target)
    for anchor, (line, src) in src_sections.items():
        if anchor not in dst_sections:
            continue
        dst_line, dst = dst_sections[anchor]
        source_size = len(WORDS.findall(src))
        target_size = len(CJK.findall(dst)) + len(WORDS.findall(dst))
        if source_size >= 12 and target_size == 0:
            add("empty-section", f"Section {anchor!r} has no translated prose", dst_line or 1)
        elif source_size >= 30 and target_size / source_size < config["length_ratio_warning"]:
            add("short-section", f"Section {anchor!r} is unusually short; review possible omissions", dst_line or 1, "warning")
        # Same-language sentence copy can hide inside an otherwise Chinese paragraph.
        for sentence in re.split(r"(?<=[.!?])\s+", src):
            if len(WORDS.findall(sentence)) >= 8 and sentence.strip() in dst:
                add("copied-sentence", f"Untranslated upstream sentence in section {anchor!r}", dst_line or 1, "warning")
                break
    return issues


def verify(source_root: Path, target_root: Path, config: dict, patterns: list[str] | None = None) -> dict:
    if not source_root.is_dir() or not target_root.is_dir():
        raise ValueError("Source and target documentation directories must exist")
    src, dst = files(source_root), files(target_root)
    paths = sorted(p for p in src.keys() | dst.keys() if selected(p, patterns or []))
    if not paths:
        raise ValueError("No documentation files matched; refusing an empty verification")
    issues: list[Issue] = []
    matched = 0
    for path in paths:
        a = src[path].read_text(encoding="utf-8-sig") if path in src else ""
        b = dst[path].read_text(encoding="utf-8-sig") if path in dst else ""
        source_hash = digest(src[path].read_bytes()) if path in src else None
        target_hash = digest(dst[path].read_bytes()) if path in dst else None
        if path not in dst:
            current = [Issue(path, 1, "error", "missing-file", "Missing target file")]
        elif path not in src:
            current = [Issue(path, 1, "warning", "extra-file", "Target file has no upstream counterpart")]
        else:
            matched += 1
            current = compare(path, Document(a, src[path].suffix, config["terms"]), Document(b, dst[path].suffix, config["terms"]), config)
        for issue in current:
            issue.fingerprint = digest(json.dumps([path, source_hash, target_hash,
                                                  issue.line, issue.code, issue.message], ensure_ascii=False))
            exception = next((e for e in config["exceptions"] if e["fingerprint"] == issue.fingerprint), None)
            if exception:
                issue.suppressed, issue.reason = True, exception["reason"]
        issues.extend(current)
    counts = Counter(i.severity for i in issues if not i.suppressed)
    source_count = sum(p in src for p in paths)
    return {
        "schema_version": 1,
        "summary": {"source_files": source_count, "target_files": sum(p in dst for p in paths), "matched_files": matched,
                    "file_coverage_percent": round(100 * matched / source_count, 2) if source_count else 0,
                    "errors": counts["error"], "warnings": counts["warning"], "suppressed": sum(i.suppressed for i in issues)},
        "quality": {"semantic_review": "required", "note": "File coverage and deterministic checks do not prove semantic completeness or translation accuracy."},
        "issues": [asdict(i) for i in issues],
    }


def review_bundle(source_root: Path, target_root: Path, config: dict, patterns: list[str]) -> dict:
    report = verify(source_root, target_root, config, patterns)
    entries = []
    src, dst = files(source_root), files(target_root)
    for path in sorted(src):
        if not selected(path, patterns):
            continue
        a, b = src[path].read_text(encoding="utf-8-sig"), dst[path].read_text(encoding="utf-8-sig") if path in dst else None
        entries.append({"path": path, "source_sha256": digest(src[path].read_bytes()), "target_sha256": digest(dst[path].read_bytes()) if path in dst else None,
                        "source": a, "target": b, "issues": [i for i in report["issues"] if i["path"] == path]})
    return {"schema_version": 1, "purpose": "semantic-review",
            "instructions": "Read every source and target section, including frontmatter and category labels. Check omissions, additions, wrong facts, negation, numbers, section/body alignment, fluency, and terminology. Do not flag protected product names, code, or Markdown symbols as untranslated. Report path, target line, source evidence, severity, and correction. Mark each file reviewed only after full comparison. Do not change translations during review.",
            "protected_terms": config["terms"], "files": entries, "deterministic_report": report,
            "result_format": {"schema_version": 1, "purpose": "semantic-review-results", "files": [
                {"path": e["path"], "source_sha256": e["source_sha256"], "target_sha256": e["target_sha256"],
                 "reviewed_all_sections": False, "completeness": "needs-review", "accuracy": "needs-review",
                 "fluency": "needs-review", "terminology": "needs-review", "findings": []} for e in entries]}}


def validate_review(results: dict, source_root: Path, target_root: Path, patterns: list[str]) -> dict:
    """Validate review coverage/provenance, not the reviewer's truthfulness."""
    if results.get("schema_version") != 1 or results.get("purpose") != "semantic-review-results":
        raise ValueError("Not a supported semantic review result")
    src, dst = files(source_root), files(target_root)
    expected = {p for p in src if selected(p, patterns)}
    if not expected or not isinstance(results.get("files"), list):
        raise ValueError("Review has no selected files")
    seen, findings, pending = set(), [], []
    for entry in results["files"]:
        path = entry["path"]
        if path in seen or path not in expected or path not in dst:
            raise ValueError("Review file set is duplicate, unexpected, or missing target")
        seen.add(path)
        if entry["source_sha256"] != digest(src[path].read_bytes()) or entry["target_sha256"] != digest(dst[path].read_bytes()):
            raise ValueError(f"{path}: stale semantic review; source or target changed")
        if type(entry.get("reviewed_all_sections")) is not bool:
            raise ValueError("reviewed_all_sections must be a boolean")
        statuses = [entry.get(key) for key in ["completeness", "accuracy", "fluency", "terminology"]]
        if any(status not in {"pass", "fail", "needs-review"} for status in statuses):
            raise ValueError("Review statuses must be pass, fail, or needs-review")
        if not isinstance(entry.get("findings"), list):
            raise ValueError("Review findings must be an array")
        for finding in entry["findings"]:
            if not isinstance(finding.get("line"), int) or finding["line"] < 1 or not all(isinstance(finding.get(k), str) and finding[k].strip() for k in ["source_evidence", "message"]):
                raise ValueError("Review findings need a target line, source_evidence, and message")
            findings.append({"path": path, **finding})
        if not entry["reviewed_all_sections"] or any(s != "pass" for s in statuses) or entry["findings"]:
            pending.append(path)
    if seen != expected:
        raise ValueError("Semantic review omitted selected source files")
    return {"semantic_review": "passed" if not pending else "needs-review", "reviewed_files": len(seen), "pending_files": pending, "findings": findings}
