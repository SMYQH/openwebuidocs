"""Deterministic checks and explicit quality signals, never a semantic pass claim."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from fnmatch import fnmatchcase
import json
from pathlib import Path
import posixpath
import re

from .document import (ATTRIBUTE, CJK, FENCE_TITLE, KEYWORD_FIELDS, LAYOUT_FIELDS, TEXT_FIELDS, URL, WORDS,
                     Document, digest, inline_protected, literal_fence_title, opaque_signature, prose)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "test/translation_config.json"
SUFFIXES = {".md", ".mdx"}
REVIEW_DIMENSIONS = ("completeness", "accuracy", "fluency", "terminology")
CORRUPT_CHARACTER = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\ufffd]")


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) - {"terms", "untranslated_min_words", "length_ratio_warning", "exceptions", "non_compliant_link_patterns"}:
        raise ValueError("Invalid verifier configuration keys")
    if not isinstance(config.get("terms"), list) or not all(isinstance(t, str) and t for t in config["terms"]):
        raise ValueError("Configuration terms must be nonempty strings")
    if not isinstance(config.get("untranslated_min_words"), int) or config["untranslated_min_words"] < 1:
        raise ValueError("untranslated_min_words must be a positive integer")
    if not isinstance(config.get("length_ratio_warning"), (int, float)) or not 0 < config["length_ratio_warning"] < 1:
        raise ValueError("length_ratio_warning must be between 0 and 1")
    if not isinstance(config.get("non_compliant_link_patterns", []), list) or not all(
            isinstance(p, str) and p.strip() for p in config.get("non_compliant_link_patterns", [])):
        raise ValueError("non_compliant_link_patterns must be an array of nonempty strings")
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
    """Metadata that must match upstream exactly.

    Prose fields, keyword lists and layout directives are excluded: prose is
    translated, keyword lists are optional search terms, and sidebar ordering
    is a local layout decision.
    """
    skip = TEXT_FIELDS | KEYWORD_FIELDS | LAYOUT_FIELDS
    if isinstance(value, dict):
        return {k: metadata_literals(v) for k, v in value.items() if k not in skip}
    if isinstance(value, list):
        return [metadata_literals(v) for v in value]
    return value


def count_literals(doc: Document, kind: str) -> Counter:
    if not hasattr(doc, "_literal_counts"):
        doc._literal_counts = {}
        # Reuse body tokens, including lines that contain literals but no prose.
        for span in getattr(doc, "literal_spans", []):
            value = span.value
            # The table parser consumes the pipe escape before parsing code spans.
            if span.kind == "inline_code" and r"\|" in value and doc.line(span.start) in doc.table_rows:
                value = value.replace(r"\|", "|")
            if span.kind == "hash_placeholder":
                value = value.removeprefix("\\")
            doc._literal_counts.setdefault(span.kind, Counter())[value] += 1
        # Metadata and localizable attributes sit outside the body token stream.
        for segment in doc.segments:
            if segment.kind == "prose":
                continue
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


def literal_difference(a: Counter, b: Counter) -> tuple[list[str], list[str], dict[str, tuple[int, int]]]:
    """Split literal drift into dropped, added and re-counted literals.

    A literal that upstream uses and the target never uses is a preservation
    failure. A target-only literal or a changed occurrence count is a review
    signal, not a failure: translations legitimately mention a term a
    different number of times.
    """
    missing = sorted(set(a) - set(b))
    added = sorted(set(b) - set(a))
    shifted = {v: (a[v], b[v]) for v in set(a) & set(b) if a[v] != b[v]}
    return missing, added, shifted


def brief_literals(values: list[str], counts: Counter | None = None) -> str:
    if not values:
        return "none"
    out = []
    for value in values[:5]:
        count = counts[value] if counts is not None else 1
        out.append(f"{value[:100]!r} ×{count}")
    return ", ".join(out)


UPSTREAM_SITE = ("https://docs.openwebui.com", "http://docs.openwebui.com")
DOCUMENT_SUFFIX = (".md", ".mdx")


def canonical_destination(value: str, base: str) -> str:
    """Resolve a link destination so equivalent forms compare equal.

    Markdown destinations are captured with their parentheses, so the wrapper
    is removed first. Absolute paths, relative paths, ``.md`` suffixes and
    links that upstream points at the English site while the translation
    points at its own pages all resolve to the same canonical form.
    """
    stripped = value.strip()
    wrapped = stripped.startswith("(") and stripped.endswith(")")
    if wrapped:
        stripped = stripped[1:-1].strip()
    if not stripped or stripped.startswith("#") or stripped.startswith("mailto:"):
        return value
    for prefix in UPSTREAM_SITE:
        if stripped.startswith(prefix + "/"):
            stripped = stripped[len(prefix):]
            break
    else:
        if "://" in stripped:
            return value
    target, sep, anchor = stripped.partition("#")
    for suffix in sorted(DOCUMENT_SUFFIX, key=len, reverse=True):
        if target.endswith(suffix):
            target = target[: -len(suffix)]
            break
    if target.startswith("/"):
        canonical = posixpath.normpath(target)
    else:
        canonical = posixpath.normpath(posixpath.join(base, target))
    result = canonical + (sep + anchor if sep else "")
    return "(" + result + ")" if wrapped else result


def canonical_url(value: str) -> str:
    """Normalize a URL literal for comparison.

    Trailing sentence punctuation is not part of the URL, and links to the
    upstream English site are localized to the translated site's own pages.
    """
    value = value.rstrip(".,;:!?")
    for prefix in UPSTREAM_SITE:
        if value.startswith(prefix + "/"):
            return value[len(prefix):]
    return value


def strip_destination(value: str) -> str:
    """Markdown destinations are captured with their parentheses."""
    value = value.strip()
    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1].strip()
    return value


def non_compliant(url: str, patterns: list[str]) -> bool:
    """True when a link is one the project policy removes from the translation."""
    return any(fnmatchcase(url, pattern) for pattern in patterns)


def policy_removed_destinations(counter: Counter, patterns: list[str]) -> Counter:
    """Source destinations the translation is allowed to drop."""
    result = Counter()
    for value, count in counter.items():
        if non_compliant(strip_destination(value), patterns):
            continue
        result[value] += count
    return result


def policy_removed_inline_codes(text: str, patterns: list[str]) -> set[str]:
    """Code spans that exist only in a paragraph carrying a removed link.

    Removing the non-compliant link removes the sentence around it, so the
    code spans inside that sentence disappear with it. A code span that also
    occurs outside such a paragraph stays required.
    """
    inside, outside = Counter(), Counter()
    for block in re.split(r"\n[ \t]*\n", text):
        linked = any(non_compliant(url, patterns) for url in URL.findall(block))
        for code in set(re.findall(r"`([^`\n]+)`", block)):
            (inside if linked else outside)[code] += 1
    return {code for code in inside if not outside[code]}


def ui_label(value: str) -> bool:
    """True when a code span holds a UI label that the translation may rename.

    Upstream marks interface labels with code spans. The translated site shows
    a Chinese interface, so the label itself is translated. Identifiers,
    commands, paths, values and product names keep their literal spelling.
    """
    base = value.strip().split(" (", 1)[0]
    if not re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", base):
        return False
    words = base.split(" ")
    return (any(re.fullmatch(r"[A-Z][a-z]+", w) for w in words)
            and all(re.fullmatch(r"[A-Z][A-Za-z]*", w) or re.fullmatch(r"[a-z]+", w) for w in words))


FENCE_MARKER = re.compile(r"```|~~~")


def fence_metadata(info: str) -> str:
    """Exclude only the localizable title value; retain every other directive."""
    return FENCE_TITLE.sub(lambda m: m[0] if literal_fence_title(m[1][1:-1]) else 'title="<prose>"', info.strip())


def fence_titles(doc: Document) -> list[str]:
    """Titles carried by code fences. They are prose, not fence metadata."""
    return [title[1][1:-1] for _, info in doc.fences for title in FENCE_TITLE.finditer(info)
            if not literal_fence_title(title[1][1:-1])]


def malformed_fence_markup(doc: Document) -> bool:
    """True when upstream wrote a fence marker inside a code span."""
    return any(FENCE_MARKER.search(value) for value in count_literals(doc, "inline_code"))


def canonical_destinations(counter: Counter, path: str) -> Counter:
    base = posixpath.dirname("/" + path)
    result = Counter()
    for value, count in counter.items():
        result[canonical_destination(value, base)] += count
    return result


def setting_fields(doc: Document):
    """Return the opening field rows of sections headed by a literal setting name."""
    lines = doc.text.splitlines()
    fields = {}
    for index, (_, line, title, _) in enumerate(doc.headings):
        key = re.fullmatch(r"`([A-Z][A-Z0-9_]+)`(?:\s+\\?\{#[^}]+\})?", title)
        if not key:
            continue
        end = doc.headings[index + 1][1] - 1 if index + 1 < len(doc.headings) else len(lines)
        rows = []
        for offset in range(line, end):
            text = lines[offset].strip()
            if not text:
                continue
            field = re.fullmatch(r"[-*] ([^:`：]+?)\s*[:：]\s*(.*)", text)
            if not field:
                break
            rows.append((offset + 1, field[1], field[2]))
            if len(rows) == 2:
                break
        fields[key[1]] = (line, rows)
    return fields


def compare(path: str, source: Document, target: Document, config: dict) -> list[Issue]:
    issues: list[Issue] = []

    def add(code: str, message: str, line: int = 1, severity: str = "error") -> None:
        issues.append(Issue(path, line, severity, code, message))

    for line, error in source.errors:
        # Upstream defects stay visible, but the translation must not inherit them.
        add("source-parse", f"Upstream defect: {error}", line, severity="warning")
    for line, error in target.errors:
        add("target-parse", error, line)
    if metadata_literals(source.metadata) != metadata_literals(target.metadata):
        add("metadata-literal", "Non-translatable metadata keys or values changed")
    # Localizable fields may change values, but must not silently disappear.
    if isinstance(source.metadata, dict) and isinstance(target.metadata, dict):
        if set(source.metadata) != set(target.metadata):
            add("metadata-fields", "Metadata field set differs from upstream")
    # An upstream parse defect makes block-level comparison unreliable: the
    # translation must not inherit broken upstream structure, so those findings
    # stay visible but do not fail the file.
    source_broken = bool(source.errors)
    structural = "warning" if source_broken else "error"
    src_code, dst_code = [v for _, v in source.code], [v for _, v in target.code]
    if src_code != dst_code:
        unreliable_fences = any("Unclosed fenced code block" in error for _, error in source.errors)
        unreliable_fences |= malformed_fence_markup(source) and len(src_code) != len(dst_code)
        add("code-changed", "Code block content/order differs from upstream; comments and string values are literal too"
            + ("; upstream fence defects require direct review" if unreliable_fences else ""),
            severity="warning" if unreliable_fences else "error")
    if [opaque_signature(v) for v in source.opaque_code] != [opaque_signature(v) for v in target.opaque_code]:
        add("opaque-code-changed", "MDX imports/exports or script/style structure changed")
    if [(d, fence_metadata(i)) for d, i in source.fences] != [(d, fence_metadata(i)) for d, i in target.fences]:
        # Upstream that writes a fence marker inside a code span has broken
        # markup; a translation that repairs it must not inherit the defect.
        severity = "warning" if malformed_fence_markup(source) else structural
        add("fence-structure", "Code fence delimiters or language metadata changed", severity=severity)
    for title in fence_titles(target):
        clean = prose(title, target.terms)
        if len(WORDS.findall(clean)) >= 4 and not CJK.search(clean):
            add("untranslated-prose", "Code fence title remains English after exclusions", severity="warning")
    src_head, dst_head = [(v[0], v[3]) for v in source.headings], [(v[0], v[3]) for v in target.headings]
    if src_head != dst_head:
        # A target heading that upstream renders as code (a section heading a
        # broken fence swallows) is a restoration, not a structural difference.
        hidden = Counter((v[0], v[3]) for v in source.hidden_headings)
        extra = Counter(dst_head) - Counter(src_head)
        if extra and not (extra - hidden):
            add("heading-structure", "Target restores a section heading that upstream renders as code", severity="warning")
        else:
            add("heading-structure", f"Heading levels/order/anchors differ (source {len(src_head)}, target {len(dst_head)}). "
                + difference(Counter(src_head), Counter(dst_head)), severity=structural)
    anchors = [v[3] for v in target.headings]
    if len(anchors) != len(set(anchors)):
        add("duplicate-anchor", "Target has duplicate explicit heading anchors")
    if source.structure != target.structure:
        add("markdown-structure", "Lists, table cells, blockquotes, or thematic breaks differ", severity="warning")
    source_fields = setting_fields(source)
    if source_fields:
        target_fields = setting_fields(target)
        for key, (_, rows) in source_fields.items():
            if key not in target_fields or [r[1] for r in rows] != ["Type", "Default"]:
                continue
            number = re.match(r"`([-+]?\d+(?:\.\d+)?)`(?:\s|$)", rows[1][2])
            if not number:
                continue
            line, local = target_fields[key]
            # Labels are translated. Use the source field order as a review signal,
            # not a failure: a translation can legitimately reorder or convert units.
            value = local[1][2] if len(local) == 2 else ""
            first_number = re.search(r"(?<![\w.+-])[-+]?\d+(?:\.\d+)?(?![\w.])", value, re.ASCII)
            if not first_number or first_number[0] != number[1]:
                add("setting-default", f"Check {key}: expected numeric default {number[1]} in its own field",
                    local[1][0] if len(local) == 2 else line, "warning")
    for span in target.literal_spans:
        if span.kind == "inline_code" and re.search(r"(?<!\\)\|", span.value):
            line = target.line(span.start)
            if line in target.table_rows:
                add("table-code-pipe", "An unescaped pipe splits inline code across table cells", line)
    if source.admonitions != target.admonitions:
        if len(source.admonitions) != len(target.admonitions):
            add("admonition-structure", f"Admonition count differs (source {len(source.admonitions)}, "
                f"target {len(target.admonitions)})", severity=structural)
        else:
            changed = [f"{i + 1}:{a}->{b}" for i, (a, b) in enumerate(zip(source.admonitions, target.admonitions)) if a != b]
            add("admonition-structure", "Admonition types differ at " + ", ".join(changed[:5]), severity="warning")
    patterns = config.get("non_compliant_link_patterns", [])
    for kind in ["marker", "symbol"]:
        a, b = count_literals(source, kind), count_literals(target, kind)
        if a != b:
            add("markdown-" + kind, difference(a, b), severity="warning")
    for kind in ["inline_code", "identifier", "term", "destination", "reference", "jsx", "expression", "hash_placeholder", "math", "comment"]:
        a, b = count_literals(source, kind), count_literals(target, kind)
        if kind in {"identifier", "term"}:
            b = b.copy()
            # Adding backticks around a preserved identifier or product name
            # changes its token kind, not its spelling or meaning.
            for value in count_literals(target, "inline_code"):
                for span in inline_protected(value.strip("`"), target.terms):
                    if span.kind == kind and span.value in a and span.value not in b:
                        b[span.value] = 1
        if kind == "destination":
            a, b = canonical_destinations(a, path), canonical_destinations(b, path)
            a = policy_removed_destinations(a, patterns)
            kept = sorted({strip_destination(v) for v in b if non_compliant(strip_destination(v), patterns)})
            if kept:
                add("non-compliant-link", "Target keeps external links that project policy removes: " + ", ".join(kept[:5]))
        if kind == "inline_code" and patterns:
            dropped = policy_removed_inline_codes(source.text, patterns)
            a = Counter({v: n for v, n in a.items() if v.strip("`") not in dropped})
        missing, added, shifted = literal_difference(a, b)
        code = "literal-" + kind.replace("_", "-")
        if kind == "inline_code":
            # A code span that upstream wrote with a fence marker is broken
            # markup; the translation repairs it as a real code block.
            a = Counter({v: n for v, n in a.items() if not FENCE_MARKER.search(v)})
            missing, added, shifted = literal_difference(a, b)
            # A translated interface label is expected, not a dropped literal.
            relaxed = {v for v in missing if ui_label(v.strip("`")) and v.strip("`") not in config["terms"]}
            hard = [v for v in missing if v not in relaxed]
            if hard:
                add(code, "Missing: " + brief_literals(hard, a))
            if relaxed:
                add(code, "Missing: " + brief_literals(sorted(relaxed), a) + " (interface label, may be translated)",
                    severity="warning")
        elif missing:
            add(code, "Missing: " + brief_literals(missing, a))
        elif added or shifted:
            parts = []
            if added:
                parts.append("Added: " + brief_literals(added, b))
            if shifted:
                parts.append("Count differs: " + ", ".join(f"{v[:100]!r} {a[v]}->{b[v]}" for v in sorted(shifted)[:5]))
            add(code, "; ".join(parts), severity="warning")
    source_urls = Counter({canonical_url(v): n for v, n in count_literals(source, "url").items()
                           if not non_compliant(canonical_url(v), patterns)})
    target_urls = Counter({canonical_url(v): n for v, n in count_literals(target, "url").items()})
    # A URL may survive as a link destination or inline code instead of a bare
    # URL, so the target surface is the union of all literal forms.
    surface = set(target_urls)
    for value in count_literals(target, "inline_code"):
        surface.add(canonical_url(value.strip("`")))
    for value in count_literals(target, "destination"):
        surface.add(canonical_url(value.strip("()")))
    lost = sorted(set(source_urls) - surface)
    if lost:
        add("literal-url", "Missing: " + brief_literals(lost, source_urls))
    else:
        extra = sorted(set(target_urls) - set(source_urls))
        if extra:
            add("literal-url", "Added: " + brief_literals(extra, target_urls), severity="warning")
    a, b = count_literals(source, "number"), count_literals(target, "number")
    if a != b:
        add("numbers", difference(a, b), severity="warning")
    for doc, code in [(source, "source-corruption"), (target, "target-corruption")]:
        if match := CORRUPT_CHARACTER.search(doc.text):
            add(code, f"Unexpected character U+{ord(match[0]):04X} found", doc.line(match.start()))
    language_terms = config["terms"] + list(source.error_messages.values())
    target_headings = {anchor: (line, title) for _, line, title, anchor in target.headings}
    for anchor, message in source.error_messages.items():
        line, title = target_headings.get(anchor, (1, ""))
        if message not in title:
            add("literal-error-message", "Quoted diagnostic heading changed: " + repr(message), line)
    source_prose = [prose(s.text, language_terms) for s in source.segments]
    normalized_source = {re.sub(r"\s+", " ", p).strip().lower() for p in source_prose}
    target_prose = [prose(s.text, language_terms) for s in target.segments]
    for segment, value in zip(target.segments, target_prose):
        words = WORDS.findall(value)
        normalized = re.sub(r"\s+", " ", value).strip().lower()
        if segment.kind == "keyword":
            # Search-term lists may stay in the upstream language on purpose.
            continue
        if len(words) >= config["untranslated_min_words"] and not CJK.search(value):
            add("untranslated-prose", "English prose remains after excluding terminology, code, and markup", target.line(segment.start), "warning")
        elif len(words) >= 3 and normalized in normalized_source and not CJK.search(value):
            add("unchanged-prose", "Prose matches upstream verbatim", target.line(segment.start), "warning")
        if words and not CJK.search(value) and segment.kind in {"yaml", "json", "attribute"}:
            add("untranslated-metadata", "Localizable metadata or accessibility text remains English after exclusions", target.line(segment.start), "warning")
    for _, line, title, _ in target.headings:
        value = prose(title, language_terms)
        if WORDS.search(value) and not CJK.search(value):
            add("untranslated-heading", "Heading remains English after terminology/code exclusions", line, "warning")
    # Compare every matched section even when heading counts differ. Alignment
    # follows anchors, not heading position, so one omission cannot shift all checks.
    def sections(doc, values):
        offsets = [(0, "<preamble>"), *((line, anchor) for _, line, _, anchor in doc.headings)]
        groups = [[] for _ in offsets]
        index = 0
        for segment, value in zip(doc.segments, values):
            line = doc.line(segment.start)
            while index + 1 < len(offsets) and offsets[index + 1][0] <= line:
                index += 1
            if segment.kind != "keyword" and line > offsets[index][0]:
                groups[index].append(value)
        return {anchor: (line, " ".join(group)) for (line, anchor), group in zip(offsets, groups)}
    src_sections, dst_sections = sections(source, source_prose), sections(target, target_prose)
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


def verify(source_root: Path, target_root: Path, config: dict, patterns: list[str] | None = None,
           *, review_entries: list[dict] | None = None, review_results: dict | None = None) -> dict:
    if not source_root.is_dir() or not target_root.is_dir():
        raise ValueError("Source and target documentation directories must exist")
    src, dst = files(source_root), files(target_root)
    paths = sorted(p for p in src.keys() | dst.keys() if selected(p, patterns or []))
    if not paths:
        raise ValueError("No documentation files matched; refusing an empty verification")
    issues: list[Issue] = []
    audited_pairs = {}
    exceptions = {entry["fingerprint"]: entry["reason"] for entry in config["exceptions"]}
    matched = 0
    for path in paths:
        a = src[path].read_bytes() if path in src else None
        b = dst[path].read_bytes() if path in dst else None
        source_hash = digest(a) if a is not None else None
        target_hash = digest(b) if b is not None else None
        if review_results is not None and a is not None:
            audited_pairs[path] = source_hash, target_hash
        source_text = audit_text(a) if a is not None else None
        target_text = audit_text(b) if b is not None else None
        if path not in dst:
            current = [Issue(path, 1, "error", "missing-file", "Missing target file")]
        elif path not in src:
            current = [Issue(path, 1, "warning", "extra-file", "Target file has no upstream counterpart")]
        else:
            matched += 1
            current = compare(path, Document(source_text, src[path].suffix, config["terms"]),
                              Document(target_text, dst[path].suffix, config["terms"]), config)
        for issue in current:
            issue.fingerprint = digest(json.dumps([path, source_hash, target_hash,
                                                  issue.line, issue.code, issue.message], ensure_ascii=False))
            if issue.fingerprint in exceptions:
                issue.suppressed, issue.reason = True, exceptions[issue.fingerprint]
        issues.extend(current)
        if review_entries is not None and a is not None:
            review_entries.append({"path": path, "source_sha256": source_hash, "target_sha256": target_hash,
                                   "source": source_text, "target": target_text, "issues": [asdict(i) for i in current]})
    counts = Counter(i.severity for i in issues if not i.suppressed)
    source_count = sum(p in src for p in paths)
    quality = {"semantic_review": "required", "note": "File coverage and deterministic checks do not prove semantic completeness or translation accuracy."}
    if review_results is not None:
        quality = validate_review_snapshot(review_results, audited_pairs, config=config)
    return {
        "schema_version": 1,
        "summary": {"source_files": source_count, "target_files": sum(p in dst for p in paths), "matched_files": matched,
                    "file_coverage_percent": round(100 * matched / source_count, 2) if source_count else 0,
                    "errors": counts["error"], "warnings": counts["warning"], "suppressed": sum(i.suppressed for i in issues)},
        "quality": quality,
        "issues": [asdict(i) for i in issues],
    }


def audit_text(raw: bytes) -> str:
    # Line ending style does not constitute a code difference in an audit.
    return raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def review_template(files, config: dict) -> dict:
    return {"schema_version": 1, "purpose": "semantic-review-results",
            "config_sha256": digest(json.dumps(config, sort_keys=True)),
            "files": [{"path": path, "source_sha256": hashes[0], "target_sha256": hashes[1],
                       "reviewed_all_sections": False, **dict.fromkeys(REVIEW_DIMENSIONS, "needs-review"),
                       "findings": []} for path, hashes in files.items()]}


def review_bundle(source_root: Path, target_root: Path, config: dict, patterns: list[str],
                  *, previous=None, review_results=None) -> dict:
    earlier = {}
    if previous is not None:
        config_hash = digest(json.dumps(config, sort_keys=True))
        review_entries = result_entries(previous)
        if previous.get("config_sha256") == config_hash:
            earlier = review_entries
    entries: list[dict] = []
    report = verify(source_root, target_root, config, patterns, review_entries=entries, review_results=review_results)
    identities = {e["path"]: (e["source_sha256"], e["target_sha256"]) for e in entries}
    template = review_template(identities, config)
    pending, reused = [], []
    for index, entry in enumerate(entries):
        prior = earlier.get(entry["path"])
        if (prior and entry["target_sha256"] is not None
                and (prior["source_sha256"], prior["target_sha256"]) == identities[entry["path"]]
                and review_passed(prior)):
            template["files"][index] = prior
            reused.append(entry["path"])
        else:
            pending.append(entry)
    return {"schema_version": 1, "purpose": "semantic-review",
            "instructions": "Read every source and target section in files, including frontmatter and category labels. Check omissions, additions, wrong facts, negation, numbers, section/body alignment, fluency, and terminology. Do not flag protected product names, code, or Markdown symbols as untranslated. Report target line, source evidence, severity, and correction. Mark each file reviewed only after full comparison. Preserve reused results in result_format. Do not change translations during review.",
            "protected_terms": config["terms"], "files": pending, "reused_files": reused, "deterministic_report": report,
            "result_format": template}


def result_entries(results: dict) -> dict[str, dict]:
    if (not isinstance(results, dict) or results.get("schema_version") != 1
            or results.get("purpose") != "semantic-review-results" or not isinstance(results.get("files"), list)):
        raise ValueError("Not a supported semantic review result")
    entries = {}
    for entry in results["files"]:
        path = entry["path"]
        if not isinstance(path, str) or path in entries:
            raise ValueError("Review paths must be unique strings")
        if type(entry.get("reviewed_all_sections")) is not bool:
            raise ValueError("reviewed_all_sections must be a boolean")
        for field in ("source_sha256", "target_sha256"):
            value = entry[field]
            if field == "target_sha256" and value is None:
                continue
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError(f"{path}: invalid {field}")
        if any(entry.get(k) not in ("pass", "fail", "needs-review") for k in REVIEW_DIMENSIONS):
            raise ValueError("Review statuses must be pass, fail, or needs-review")
        if not isinstance(entry.get("findings"), list):
            raise ValueError("Review findings must be an array")
        for finding in entry["findings"]:
            if (not isinstance(finding, dict) or type(finding.get("line")) is not int or finding["line"] < 1
                    or not all(isinstance(finding.get(k), str) and finding[k].strip() for k in ("source_evidence", "message"))):
                raise ValueError("Review findings need a target line, source_evidence, and message")
        entries[path] = entry
    return entries


def review_passed(entry: dict) -> bool:
    return entry["reviewed_all_sections"] and all(entry[k] == "pass" for k in REVIEW_DIMENSIONS) and not entry["findings"]


def validate_review(results: dict, source_root: Path, target_root: Path, patterns: list[str], *, config=None) -> dict:
    """Validate review coverage/provenance, not the reviewer's truthfulness."""
    src, dst = files(source_root), files(target_root)
    expected = {p: (digest(src[p].read_bytes()), digest(dst[p].read_bytes()) if p in dst else None)
                for p in src if selected(p, patterns)}
    return validate_review_snapshot(results, expected, config=config)


def validate_review_snapshot(results: dict, expected: dict, *, config=None) -> dict:
    entries = result_entries(results)
    if config is not None:
        if results.get("config_sha256") != digest(json.dumps(config, sort_keys=True)):
            raise ValueError("Stale semantic review; configuration changed or unbound")
    if not expected or entries.keys() != expected.keys() or any(target is None for _, target in expected.values()):
        raise ValueError("Review must cover every selected source file with an existing target")
    findings, pending = [], []
    for path, entry in entries.items():
        if (entry["source_sha256"], entry["target_sha256"]) != expected[path]:
            raise ValueError(f"{path}: stale semantic review; source or target changed")
        findings.extend(dict(finding, path=path) for finding in entry["findings"])
        if not review_passed(entry):
            pending.append(path)
    return {"semantic_review": "passed" if not pending else "needs-review",
            "reviewed_files": sum(e["reviewed_all_sections"] for e in entries.values()),
            "pending_files": pending, "findings": findings}
