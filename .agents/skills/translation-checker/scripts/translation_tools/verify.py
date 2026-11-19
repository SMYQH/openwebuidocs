"""Deterministic checks and explicit quality signals, never a semantic pass claim."""

from __future__ import annotations

from bisect import bisect_right
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from fnmatch import fnmatchcase
from http import HTTPStatus
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import urlsplit

from .document import (ACRONYM, ATTRIBUTE, CJK, FENCE_TITLE, IDENTIFIER, KEYWORD_FIELDS, LAYOUT_FIELDS, TEXT_FIELDS, URL,
                       WORDS, Document, digest, inline_protected, inline_structure, literal_fence_title,
                       opaque_signature, prose)


SKILL_DIR = Path(__file__).resolve().parents[2]
ROOT = SKILL_DIR.parents[2]
DEFAULT_CONFIG = SKILL_DIR / "translation_config.json"
SUFFIXES = {".md", ".mdx"}
REVIEW_DIMENSIONS = ("completeness", "accuracy", "fluency", "terminology")
CORRUPT_CHARACTER = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\ufffd]")


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) - {"terms", "source_term_aliases", "untranslated_min_words", "length_ratio_warning", "exceptions", "non_compliant_link_patterns"}:
        raise ValueError("Invalid verifier configuration keys")
    if not isinstance(config.get("terms"), list) or not all(isinstance(t, str) and t for t in config["terms"]):
        raise ValueError("Configuration terms must be nonempty strings")
    aliases = config.get("source_term_aliases", {})
    if not isinstance(aliases, dict) or any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", alias)
                                           or not IDENTIFIER.fullmatch(alias) or alias in config["terms"]
                                           or term not in config["terms"] for alias, term in aliases.items()):
        raise ValueError("Source term aliases must map bare term misspellings to configured terms")
    if not isinstance(config.get("untranslated_min_words"), int) or config["untranslated_min_words"] < 1:
        raise ValueError("untranslated_min_words must be a positive integer")
    if not isinstance(config.get("length_ratio_warning"), (int, float)) or not 0 < config["length_ratio_warning"] < 1:
        raise ValueError("length_ratio_warning must be between 0 and 1")
    if not isinstance(config.get("non_compliant_link_patterns", []), list) or not all(
            isinstance(p, str) and p.strip() for p in config.get("non_compliant_link_patterns", [])):
        raise ValueError("non_compliant_link_patterns must be an array of nonempty strings")
    if not isinstance(config.get("exceptions"), list):
        raise ValueError("exceptions must be an array")
    fingerprints = set()
    for exception in config["exceptions"]:
        if (not isinstance(exception, dict) or set(exception) != {"fingerprint", "reason"}
                or not isinstance(exception["fingerprint"], str) or not re.fullmatch(r"[0-9a-f]{64}", exception["fingerprint"])
                or not isinstance(exception["reason"], str) or not exception["reason"].strip()):
            raise ValueError("Each exception needs an exact fingerprint and a nonempty reason")
        if exception["fingerprint"] in fingerprints:
            raise ValueError("Duplicate exact exception fingerprint")
        fingerprints.add(exception["fingerprint"])
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
class SectionDrift:
    anchor: str
    source_line: int | None
    target_line: int | None
    token: str
    source_count: int
    target_count: int


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
    section_drift: list[SectionDrift] | None = None


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


def normalized_markers(doc: Document) -> Counter:
    """Ignore marker spelling and padding when parsed block structure matches."""
    counts = count_literals(doc, "marker").copy()
    # Only an actual list item can use a different raw number. The start of
    # each ordered list is already part of the parsed structure.
    for span in doc.literal_spans:
        if span.kind == "marker" and doc.line(span.start) in doc.ordered_item_rows:
            marker, changes = re.subn(r"[0-9]+[.)](?=[ \t]+$)", "1.", span.value)
            if changes:
                counts[span.value] -= 1
                counts[marker] += 1
    result = Counter()
    for raw, count in (+counts).items():
        marker = re.sub(r"[ \t]+", " ", raw.strip())
        prefix, match = re.match(r"((?:>[ \t]*)*)(.*)", marker).groups()
        if match in {"-", "+", "*"}:
            match = "-"
        elif re.fullmatch(r"[0-9]+\)", match):
            match = match[:-1] + "."
        result[">" * prefix.count(">") + match] += count
    return result


def canonical_term(value: str, terms: set[str]) -> str:
    """Normalize a terminology surface form.

    The same name may be written in another case or with a regular plural
    suffix ("WebSocket"/"WebSockets", "markdown"/"Markdown"). Both spellings
    denote the same product, protocol or interface, so they compare equal.
    """
    lowered = value.lower()
    if lowered in terms:
        return lowered
    for suffix in ("s", "es", "ies"):
        if not lowered.endswith(suffix):
            continue
        stem = lowered[: -len(suffix)]
        candidate = stem + "y" if suffix == "ies" else stem
        if candidate in terms:
            return candidate
    return lowered


def canonical_terms(counts: Counter, terms: set[str]) -> Counter:
    result = Counter()
    for value, count in counts.items():
        result[canonical_term(value, terms)] += count
    return result


def literal_section_drift(source: Document, target: Document, kind: str, values: set[str],
                          terms: set[str]) -> list[SectionDrift]:
    """Locate file-level findings without applying cross-section allowances."""
    def group(doc):
        headings = [(1, "<preamble>"), *((line, anchor) for _, line, _, anchor in doc.headings)]
        lines = [line for line, _ in headings]
        groups = {anchor: (line, Counter()) for line, anchor in headings}

        def count(span, offset):
            if span.kind != kind:
                return
            token = canonical_term(span.value, terms) if kind == "term" else span.value
            if token in values:
                index = bisect_right(lines, doc.line(offset)) - 1
                groups[headings[index][1]][1][token] += 1

        for span in doc.literal_spans:
            count(span, span.start)
        for segment in doc.segments:
            if segment.kind != "prose":
                for span in inline_protected(segment.text, doc.terms):
                    count(span, segment.start)
        return groups

    left, right = group(source), group(target)
    result = []
    for anchor in dict.fromkeys((*left, *right)):
        source_line, a = left.get(anchor, (None, Counter()))
        target_line, b = right.get(anchor, (None, Counter()))
        for token in sorted(a.keys() | b.keys()):
            if a[token] != b[token]:
                result.append(SectionDrift(anchor, source_line, target_line, token, a[token], b[token]))
    return result


def section_terms(doc: Document, terms: set[str]) -> dict[str, Counter]:
    """Collect the terminology each section of a document uses."""
    offsets = [(0, "<preamble>"), *((line, anchor) for _, line, _, anchor in doc.headings)]
    groups = {anchor: Counter() for _, anchor in offsets}
    index = 0
    for span in doc.literal_spans:
        if span.kind == "inline_code":
            # A name wrapped in a code span keeps its spelling, so the section
            # still introduces the term.
            values = [inner.value for inner in inline_protected(span.value.strip("`"), terms)
                      if inner.kind == "term"]
        elif span.kind == "term":
            values = [span.value]
        else:
            continue
        line = doc.line(span.start)
        while index + 1 < len(offsets) and offsets[index + 1][0] <= line:
            index += 1
        for value in values:
            groups[offsets[index][1]][canonical_term(value, terms)] += 1
    return groups


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


INLINE_SLUG = re.compile(r"`[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)+`")


def inline_code_substitutions(source: Document, target: Document, added: list[str],
                              shifted: dict[str, tuple[int, int]]) -> list[SectionDrift]:
    """Spot a new identifier where a repeated source identifier disappeared."""
    new = {value for value in added if INLINE_SLUG.fullmatch(value)}
    reduced = {value for value, (a, b) in shifted.items() if a > b and INLINE_SLUG.fullmatch(value)}
    if not new or not reduced:
        return []
    drift = [entry for entry in literal_section_drift(source, target, "inline_code", new | reduced, set())
             if entry.source_line is not None and entry.target_line is not None]
    replacements = {entry.anchor for entry in drift if entry.token in new and entry.target_count}
    omissions = {entry.anchor for entry in drift if entry.token in reduced and not entry.target_count}
    return [entry for entry in drift if entry.anchor in replacements & omissions
            and (entry.token in new or not entry.target_count)]


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


CONTACT_ROW = re.compile(
    r"[ \t]*\|[ \t]*(?P<bold>\*\*)?(?P<label>[A-Za-z0-9-]+)(?(bold)\*\*)[ \t]*\|"
    r"[ \t]*\[(?P<link_text>[^][|\r\n]+)\]\((?P<url>https?://[A-Za-z0-9.-]+/[^][|()\s]*)\)[ \t]*\|[ \t]*"
)


def without_policy_contact_rows(doc: Document, patterns: list[str]) -> Document:
    """Project the source layout without directory rows that only advertise a removed host."""
    if not patterns or not doc.table_data_rows:
        return doc
    lines = doc.text.split("\n")
    excluded = set()
    for row in doc.table_data_rows:
        match = CONTACT_ROW.fullmatch(lines[row - 1].removesuffix("\r"))
        if not match or not non_compliant(match["url"], patterns):
            continue
        link = urlsplit(match["url"])
        host = link.hostname
        if not host or match["label"].lower() != host.removeprefix("www.").split(".")[0]:
            continue
        path = link.path.strip("/")
        if match["link_text"].strip("/") in {match["url"].rstrip("/"), host + link.path.rstrip("/"), path}:
            excluded.add(row)
    if not excluded:
        return doc
    return Document("\n".join(line for row, line in enumerate(lines, 1) if row not in excluded),
                    doc.suffix, doc.terms)


def policy_link_symbols(doc: Document, patterns: list[str]) -> Counter:
    """Count only the outer brackets of policy-listed inline links and images."""
    symbols = {s.start: s for s in doc.literal_spans if s.kind == "symbol" and s.value in {"[", "![", "]"}}
    excluded = Counter()
    for span in doc.literal_spans:
        if span.kind != "destination" or not non_compliant(strip_destination(span.value), patterns):
            continue
        close = span.start - 1
        if close not in symbols:
            continue
        start = doc.text.rfind("[", doc.text.rfind("\n", 0, close) + 1, close)
        if start < 0 or "]" in doc.text[start + 1:close]:
            continue
        if start - 1 in symbols and symbols[start - 1].value == "![":
            start -= 1
        if start not in symbols:
            continue
        structure = inline_structure(doc.text[start:span.end])
        if structure == ["image"] or structure[:1] == ["link_open"] and structure[-1:] == ["link_close"]:
            excluded.update((symbols[start].value, symbols[close].value))
    return excluded


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


def contextual_ui_labels(doc: Document) -> set[str]:
    """Recognize menu paths and compound controls only in UI action prose."""
    labels = set()
    non_labels = set()
    for span in doc.literal_spans:
        if span.kind != "inline_code" or not (" > " in span.value or "/" in span.value):
            continue
        value = span.value.strip("`")
        parts = re.split(r" > |/", value)
        start = doc.text.rfind("\n", 0, span.start) + 1
        prefix = doc.text[start:span.start]
        if (all(ui_label(part) and part[0].isupper() for part in parts)
                and re.search(r"\b(?:navigate to|go to|open|click|select|choose)\s+(?:the\s+)?$", prefix, re.I)):
            labels.add(span.value)
        else:
            non_labels.add(span.value)
    return labels - non_labels


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


def repaired_inline_fences(missing: Counter, source_code: list[str], target_code: list[str]) -> Counter:
    """Count source spans moved into standalone blocks with the exact same body."""
    code = Counter(value.removesuffix("\n") for value in target_code) - Counter(
        value.removesuffix("\n") for value in source_code)
    repairs = Counter()
    for value in missing:
        match = re.fullmatch(r"(`{3,})([^`\n]+)\1", value)
        if match and code[match[2]]:
            repairs[value] = min(missing[value], code[match[2]])
            code[match[2]] -= repairs[value]
    return repairs


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


EMPTY_STRING_GLOSS = re.compile(r'`(\(""\)|\(\x27\x27\)|""|\x27\x27) (?:empty string|\(empty string\))`')
PUNCTUATED_IDENTIFIER = re.compile(r"`([A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+)\.`")


def normalize_inline_defaults(counts: Counter, fields: dict, keys) -> Counter:
    """Exclude the English gloss, but preserve the quoted empty value."""
    result = counts.copy()
    for key in keys:
        _, rows = fields.get(key, (0, []))
        match = EMPTY_STRING_GLOSS.match(rows[1][2]) if len(rows) == 2 else None
        if match and result[match[0]]:
            result[match[0]] -= 1
            result[f"`{match[1]}`"] += 1
    return +result


def normalize_identifier_punctuation(source: Counter, target: Counter) -> Counter:
    """Accept a moved period only when the exact clean name also occurs upstream."""
    result = source.copy()
    for literal, count in source.items():
        match = PUNCTUATED_IDENTIFIER.fullmatch(literal)
        if match:
            clean = f"`{match[1]}`"
            if source[clean] and not target[literal] and target[clean] >= source[clean] + count:
                del result[literal]
                result[clean] += count
    return result


MONTHS = {name: month for month, name in enumerate(
    "january february march april may june july august september october november december".split(), 1)}
DATE_MONTH = "(?P<month>" + "|".join(MONTHS) + ")"
DATE_DAY = r"(?P<day_token>(?P<day>[0-9]{1,2})(?:st|nd|rd|th)?)"
DATE_YEAR = r"(?P<year>[1-9][0-9]{3})(?![0-9])"
ENGLISH_DAY_FIRST_DATE = re.compile(
    rf"\b(?:(?P<first_token>(?P<first_day>[0-9]{{1,2}})(?:st|nd|rd|th)?)[ \t]+and[ \t]+)?"
    rf"{DATE_DAY}[ \t]+{DATE_MONTH}[ \t]+{DATE_YEAR}", re.I)
ENGLISH_DATE = re.compile(rf"\b{DATE_MONTH}[ \t]+(?:{DATE_DAY},[ \t]+)?{DATE_YEAR}", re.I)
CHINESE_DATE = re.compile(r"(?<![0-9])(?P<year>[1-9][0-9]{3})[ \t]*\u5e74[ \t]*"
                          r"(?P<month>[0-9]{1,2})[ \t]*\u6708"
                          r"(?:[ \t]*(?:(?P<first_token>(?P<first_day>[0-9]{1,2}))[ \t]*\u65e5?"
                          r"[ \t]*[\u548c\u4e0e\u53ca\u3001][ \t]*)?(?P<day>[0-9]{1,2})[ \t]*\u65e5)?")
ENGLISH_CLOCK = re.compile(r"(?<![A-Za-z0-9_.,:/+-])(?P<clock>(?P<hour>[0-9]{1,2})(?::(?P<minute>[0-9]{2}))?)"
                           r"[ \t]*(?P<period>am|pm)(?![A-Za-z0-9_])", re.I)
CHINESE_CLOCK = re.compile(r"(?P<period>\u4e0a\u5348|\u65e9\u4e0a|\u4e0b\u5348|\u51cc\u6668|\u5348\u591c|\u6df1\u591c|\u665a\u4e0a)[ \t]*(?P<hour>[0-9]{1,2})[ \t]*\u70b9"
                           r"(?:[ \t]*(?P<minute>[0-9]{1,2})[ \t]*\u5206)?")
CHINESE_COLON_CLOCK = re.compile(r"(?P<period>\u4e0a\u5348|\u65e9\u4e0a|\u4e0b\u5348|\u51cc\u6668|\u5348\u591c|\u6df1\u591c|\u665a\u4e0a)[ \t]*"
                                 r"(?P<clock>(?P<hour>[0-9]{1,2})[ \t]*:[ \t]*(?P<minute>[0-9]{2}))(?![0-9])")
DECIMAL = r"[0-9]+(?:\.[0-9]+)?"
DURATION_UNITS = {
    "milliseconds": "ms", "millisecond": "ms", "ms": "ms", "\u6beb\u79d2": "ms",
    "seconds": "s", "second": "s", "s": "s", "\u79d2": "s",
    "minutes": "min", "minute": "min", "min": "min", "\u5206\u949f": "min",
    "hours": "h", "hour": "h", "h": "h", "\u5c0f\u65f6": "h",
    "days": "d", "day": "d", "d": "d", "\u5929": "d",
    "weeks": "w", "week": "w", "w": "w", "\u5468": "w",
    "months": "mo", "month": "mo", "mo": "mo", "\u4e2a\u6708": "mo",
    "years": "y", "year": "y", "y": "y", "\u5e74": "y",
}
DURATION_UNIT = "(?:" + "|".join(sorted(DURATION_UNITS, key=len, reverse=True)) + ")"
# A unit may follow a plain space, a non-breaking space or an HTML entity.
SEPARATOR = r"(?:[ \t\u00a0]|&nbsp;|&#160;|&amp;nbsp;)+"
# A slash can delimit a rate in prose. Path and URL spans are not numbers.
DURATION = re.compile(rf"(?<![A-Za-z0-9_.,:+\u2212-])(?P<value>{DECIMAL})"
                      rf"(?:{SEPARATOR}|-)(?P<unit>{DURATION_UNIT})(?![A-Za-z0-9_])", re.I)
COORDINATED_DEADLINES = re.compile(
    rf"\bwithin[ \t]+(?P<first>{DECIMAL})[ \t]+"
    r"(?P<unit>milliseconds?|seconds?|minutes?|hours?|days?|weeks?|months?|years?)"
    rf",[ \t]+and[ \t]+[^.!?;:\r\n]{{1,80}}?[ \t]+within[ \t]+(?P<second>{DECIMAL})"
    r"(?=[ \t]*(?:[!?;]|\.(?![0-9])|$))", re.I | re.M,
)
OPEN_DURATION = re.compile(rf"(?<![A-Za-z0-9_.,:/+\u2212-])(?P<value>{DECIMAL})"
                           rf"\+[ \t]*(?P<unit>{DURATION_UNIT})(?![A-Za-z0-9_])", re.I)
CHINESE_OPEN_DURATION = re.compile(
    rf"(?<![A-Za-z0-9_.,:/+\u2212-])(?P<value>{DECIMAL})[ \t]*(?P<unit>{DURATION_UNIT})"
    r"[ \t]*(?:\u4ee5\u4e0a|(?:\u751a\u81f3|\u6216)\u66f4[\u4e45\u957f])"
)
# A Chinese duration unit may follow its number without a separating space.
CHINESE_DURATION = re.compile(rf"(?<![A-Za-z0-9_.,:+\u2212-])(?P<value>{DECIMAL})"
                              rf"(?P<unit>\u79d2|\u6beb\u79d2|\u5206\u949f|\u5c0f\u65f6|\u5929|\u5468)(?![A-Za-z0-9_])")
CHINESE_EXTRA_YEARS = re.compile(rf"(?<![A-Za-z0-9_.,:/+\u2212-])(?P<value>{DECIMAL})"
                                r"[ \t]*\u4f59[ \t]*(?P<unit>\u5e74)")
# Recognize sequence labels in headings, parentheses, lists, or after a
# time preposition. "Each day 7 items arrive" is not a sequence label.
ENGLISH_DAY_ORDINAL = re.compile(
    r"(?:^[ \t]*(?:#{1,6}[ \t]+)?|(?<=[(,])[ \t]*|\b(?:on|by|from|until|before|after)[ \t]+)"
    r"day[ \t]+(?P<value>[0-9]+)(?![A-Za-z0-9_:/+\-]|[.,][0-9])", re.I | re.M)
CHINESE_DAY_ORDINAL = re.compile(r"\u7b2c[ \t]*(?P<value>[0-9]+)[ \t]*\u5929")
MULTIPLIER = re.compile(rf"(?<![A-Za-z0-9_.-])(?P<value>{DECIMAL})"
                        r"(?:x(?![A-Za-z0-9_])|[ \t]*(?:\u00d7(?![ \t]*[0-9])|\u500d))")
PERCENT_RANGE = re.compile(rf"(?<![A-Za-z0-9_.-])(?P<low>{DECIMAL}%?)[ \t]*"
                           rf"(?:\bto\b|[-\u2013\u2014\u81f3\u5230])[ \t]*(?P<high>{DECIMAL}%)")
RANGE_BOUND = rf"(?:[0-9]{{1,3}}(?:,[0-9]{{3}})+(?:\.[0-9]+)?|{DECIMAL})"
RANGE_SEPARATOR = r"-|[ \t]+-[ \t]+|[ \t]*(?:\bto\b|\bthrough\b|\buntil\b|[\u2013\u2014\u81f3\u5230])[ \t]*"
TOKEN_UNIT = r"(?:\u4e2a[ \t]*)?tokens?"
NUMERIC_RANGE = re.compile(rf"(?<![A-Za-z0-9_.,:/+\u2212-])(?P<low>{RANGE_BOUND})"
                           rf"(?P<separator>{RANGE_SEPARATOR})"
                           rf"(?P<high>{RANGE_BOUND})(?![A-Za-z0-9_:/+-]|[.,][0-9])", re.I)
QUANTITY_RANGE = re.compile(
    rf"(?<![A-Za-z0-9_.,:/+\u2212-])(?P<low>{RANGE_BOUND})(?:{RANGE_SEPARATOR})(?P<high>{RANGE_BOUND})"
    rf"(?P<plus>\+)?[ \t]*(?:(?P<more_before>\u591a)(?={TOKEN_UNIT}))?"
    rf"(?P<unit>{DURATION_UNIT}|{TOKEN_UNIT}|x|\u500d|\u00d7)(?![A-Za-z0-9_])"
    # Chinese comparatives can express the same open bound as "+".
    r"(?:[ \t]*(?:\u751a\u81f3|\u6216)\u66f4(?:(?P<longer>[\u4e45\u957f])|(?P<more_after>\u591a)))?", re.I
)
SCALE_EXPONENTS = {"thousand": 3, "million": 6, "billion": 9, "trillion": 12,
                   "\u4e07": 4, "\u767e\u4e07": 6, "\u5343\u4e07": 7, "\u4ebf": 8}
SCALED_QUANTITY = re.compile(rf"(?<![A-Za-z0-9_.:+-])(?P<value>{DECIMAL})[ \t]*"
                             r"(?P<unit>(?:thousand|million|billion|trillion)(?![A-Za-z])|[\u4e07\u4ebf])", re.I)
PIXELS = re.compile(rf"(?<![A-Za-z0-9_.,:/+\u2212-])(?P<value>{RANGE_BOUND})[ \t]*"
                    r"(?:(?:(?P<english_scale>mega|million[ \t]+))?pixels?(?![A-Za-z])|px(?![A-Za-z])"
                    r"|(?P<chinese_scale>\u767e\u4e07|\u5343\u4e07|\u4e07|\u4ebf)?[ \t]*\u50cf\u7d20)", re.I)
ENGLISH_PERCENTILE = re.compile(rf"(?<![A-Za-z0-9_.,:/+\u2212-])"
                                rf"(?P<rank>{DECIMAL})(?P<ordinal>st|nd|rd|th)[ \t-]+percentile\b", re.I)
CHINESE_PERCENTILE = re.compile(rf"\u7b2c[ \t]*(?P<rank>{DECIMAL})[ \t]*(?:\u4e2a)?\u767e\u5206\u4f4d")
GROUPED_INTEGER = re.compile(r"[0-9]{1,3}(?:,[0-9]{3})+")
# A month name is capitalized; the modal "may" and the verb "march" are not.
ENGLISH_MONTH = re.compile(r"(?<![A-Za-z0-9_])(?P<month>" + "|".join(name.capitalize() for name in MONTHS) + r")(?![A-Za-z0-9_])")
# A month name only names a month next to a day, a year or a date preposition.
MONTH_CONTEXT = re.compile(r"(?:\d|\b(?:in|on|at|by|until|since|from|through|during|of|before|after))[ \t]+$")
MONTH_NAMES = "|".join(name.capitalize() for name in MONTHS)
ENGLISH_MONTH_RANGE = re.compile(rf"(?P<first>{MONTH_NAMES})[ \t]+(?:to|-|\u2013|through)[ \t]+"
                                 rf"(?P<second>{MONTH_NAMES})[ \t]+(?P<year>[1-9][0-9]{{3}})")
CHINESE_MONTH_RANGE = re.compile(r"(?P<year>[1-9][0-9]{3})[ \t]*\u5e74[ \t]*(?P<first>[0-9]{1,2})[ \t]*\u6708"
                                 r"[ \t]*(?:\u81f3|\u5230|-|\u2013)[ \t]*(?P<second>[0-9]{1,2})[ \t]*\u6708")
CHINESE_MONTH = re.compile(r"(?<![0-9])(?P<value>[0-9]{1,2})[ \t]*\u6708(?![0-9])")
REPEATED_COUNT = re.compile(r"(?<![0-9])(?P<first>[0-9]+)(?P<middle>[ \t]+of[ \t]+(?:the[ \t]+)?)(?P<second>[0-9]+)(?![0-9])")
SLASH_LIST = re.compile(r"[0-9]+(?:/[0-9]+){2,}")
ENGLISH_NUMBER_WORDS = {
    "zero": 0,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}
NUMBER_WORD = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(ENGLISH_NUMBER_WORDS) + r")(?![A-Za-z0-9_])", re.I)


def scaled_value(value: str, scale: int) -> str:
    sign, digits, exponent = Decimal(value.replace(",", "")).as_tuple()
    expanded = format(Decimal((sign, digits, exponent + scale)), "f")
    return expanded.rstrip("0").rstrip(".") if "." in expanded else expanded


PLURAL_COUNT = re.compile(r"(?:\bas\b|,)\s*$")
HTTP_STATUS_CODES = {str(status.value) for status in HTTPStatus}
HTTP_STATUS_ALTERNATIVE = re.compile(r"\b(?:empty (?:results|responses)|HTTP errors?)[ \t]+(?:or|and)[ \t]+$", re.I)
CHANGE_CUE = re.compile(
    r"(?:change[ds]?|upgrad\w*|updat\w*|increas\w*|decreas\w*|dropp?\w*|rais\w*|lower\w*|migrat\w*"
    r"|switch\w*|bump\w*|reduc\w*)\s+(?:from\s+)?$"
    r"|\u6539\u4e3a|\u53d8\u66f4\u4e3a|\u5347\u7ea7\u4e3a|\u8c03\u6574\u4e3a|\u9012\u589e\u4e3a|\u9012\u51cf\u4e3a",
    re.I)


def canonical_number_token(token: str, before: str = "") -> str:
    """Return the canonical form of a numeric token.

    A unit suffix becomes a field of its own so the comparison can tell
    "10 s" from a plain "10". A trailing "s" names seconds ("37s") unless
    the number counts things ("as 403s"), and a scaled suffix ("1M") becomes
    its expanded value.
    """
    if token.endswith("%"):
        return f"{token[:-1]} %"
    for suffix, unit in (("ms", "ms"), ("px", "px")):
        if token.endswith(suffix) and token[:-len(suffix)].replace(",", "").isdigit():
            return f"{token[:-len(suffix)]} {unit}"
    for suffix, scale in (("KB", 3), ("MB", 6), ("GB", 9), ("TB", 12),
                          ("K", 3), ("M", 6), ("G", 9), ("T", 12)):
        if token.endswith(suffix):
            head = token[:-len(suffix)]
            if head.replace(",", "").isdigit():
                return scaled_value(head, scale)
    if token.endswith("s") and token[:-1].replace(",", "").isdigit():
        if PLURAL_COUNT.search(before) or (token[:-1] in HTTP_STATUS_CODES and HTTP_STATUS_ALTERNATIVE.search(before)):
            return token[:-1]
        return f"{token[:-1]} s"
    return token


def duration_suffix(unit: str) -> str:
    return DURATION_UNITS.get(unit.lower(), unit.lower())


def change_cue(text: str, match: re.Match) -> bool:
    """True when a range actually states a change of value.

    "Change from 0.6 to 0.9" names two values, not an interval, so the
    translation must keep both values instead of turning them into a range.
    """
    before = text[max(0, match.start() - 48):match.start()]
    after = text[match.end():match.end() + 12]
    return bool(CHANGE_CUE.search(before) or CHANGE_CUE.search(after))


def numeric_values(doc: Document) -> Counter:
    """Compare localized values without reinterpreting code or IDs."""
    result = Counter()
    numbers = {(s.start, s.end): s.value for s in doc.literal_spans if s.kind == "number"}

    def context(start: int) -> str:
        return doc.text[max(0, start - 40):start]

    for (start, _), token in numbers.items():
        result[canonical_number_token(token, context(start))] += 1

    def replace(parts, value: str, *additional_values: str) -> None:
        if all(part in numbers for part in parts):
            for part in parts:
                result[canonical_number_token(numbers.pop(part), context(part[0]))] -= 1
            result.update((value, *additional_values))

    dates = []
    for pattern in (ENGLISH_DAY_FIRST_DATE, ENGLISH_DATE, CHINESE_DATE):
        for match in pattern.finditer(doc.text):
            year = int(match["year"])
            month = int(match["month"]) if pattern is CHINESE_DATE else MONTHS[match["month"].lower()]
            first_day = match.groupdict().get("first_day")
            try:
                normalized = date(year, month, int(match["day"] or 1)).isoformat()
                additional_values = (date(year, month, int(first_day)).isoformat(),) if first_day else ()
            except ValueError:
                continue
            fields = ["year"]
            if pattern is CHINESE_DATE:
                fields.append("month")
            if match["day"]:
                fields.append("day" if pattern is CHINESE_DATE else "day_token")
            if first_day:
                fields.append("first_token")
            replace([match.span(field) for field in fields],
                    normalized if match["day"] else normalized[:7], *additional_values)
            dates.append(match.span())
    for pattern in (ENGLISH_CLOCK, CHINESE_CLOCK, CHINESE_COLON_CLOCK):
        for match in pattern.finditer(doc.text):
            hour, minute = int(match["hour"]), int(match["minute"] or 0)
            if not 1 <= hour <= 12 or minute >= 60:
                continue
            pm = match["period"].lower() in {"pm", "\u4e0b\u5348", "\u665a\u4e0a"}
            if pattern is ENGLISH_CLOCK:
                parts = [match.span()] if match.span() in numbers else [match.span("clock")]
            elif pattern is CHINESE_COLON_CLOCK and match.span("clock") in numbers:
                parts = [match.span("clock")]
            else:
                parts = [match.span("hour")] + ([match.span("minute")] if match["minute"] else [])
            replace(parts, f"{hour % 12 + 12 * pm:02}:{minute:02} clock")
    for pattern in (ENGLISH_DAY_ORDINAL, CHINESE_DAY_ORDINAL):
        for match in pattern.finditer(doc.text):
            replace([match.span("value")], f"{int(match['value'])} day ordinal")
    # A joined range may be one protected token or two. Consume the whole
    # quantity before standalone units so both spellings produce the same key.
    for match in QUANTITY_RANGE.finditer(doc.text):
        unit = match["unit"].lower()
        duration = unit in DURATION_UNITS
        tokens = unit.endswith(("token", "tokens"))
        if (unit == "\u5e74" and not (match["plus"] or match["longer"])
                and all(re.fullmatch(DATE_YEAR, match[name]) for name in ("low", "high"))
                and doc.text.startswith("\u95f4", match.end("unit"))):
            # The explicit calendar suffix leaves both years to NUMERIC_RANGE.
            continue
        if unit == "\u00d7" and re.match(r"[ \t]*[0-9]", doc.text[match.end("unit"):]):
            continue
        start, end = match.start(), match.end("high")
        starts = match.start("high")
        unit_end = match.end("unit")
        parts = next((parts for parts in (
            [(start, unit_end)], [(start, end)],
            [match.span("low"), (starts, unit_end)], [match.span("low"), (starts, end)],
        ) if all(part in numbers for part in parts)), None)
        if parts is None:
            continue
        low, high = (match[name].replace(",", "") for name in ("low", "high"))
        suffix = duration_suffix(unit) if duration else "tokens" if tokens else "x"
        open_bound = match["plus"] or (duration and match["longer"]) or (tokens and (match["more_before"] or match["more_after"]))
        bound = "+" if open_bound else ""
        replace(parts, f"{low}-{high}{bound} {suffix}")
    # The second deadline in a coordinated clause can omit the first one's unit.
    for match in COORDINATED_DEADLINES.finditer(doc.text):
        if match.span("first") in numbers:
            replace([match.span("second")], f"{match['second']} {duration_suffix(match['unit'])}")
    for pattern in (OPEN_DURATION, CHINESE_OPEN_DURATION):
        for match in pattern.finditer(doc.text):
            part = (match.start("value"), match.end("unit"))
            if part not in numbers:
                part = match.span("value")
            replace([part], f"{match['value']}+ {duration_suffix(match['unit'])}")
    for pattern in (DURATION, CHINESE_DURATION, CHINESE_EXTRA_YEARS):
        for match in pattern.finditer(doc.text):
            if match["unit"] in {"\u5e74", "year", "years"} and len(match["value"]) == 4:
                # "2014-2016 \u5e74" names a year range, not a duration.
                continue
            part = match.span() if match.span() in numbers else match.span("value")
            replace([part], f"{match['value']} {duration_suffix(match['unit'].lower())}")
    for match in MULTIPLIER.finditer(doc.text):
        part = match.span() if match[0].endswith("x") else match.span("value")
        replace([part], f"{match['value']} x")
    for match in PERCENT_RANGE.finditer(doc.text):
        parts = [match.span()] if match.span() in numbers else [match.span("low"), match.span("high")]
        replace(parts, match["low"].removesuffix("%") + "-" + match["high"])
    for match in NUMERIC_RANGE.finditer(doc.text):
        low, high = (match[name].replace(",", "") for name in ("low", "high"))
        # "To" can describe an upgrade or change, not an interval.
        if match["separator"].strip().lower() in {"to", "\u5230"}:
            if Decimal(low) >= Decimal(high):
                continue
            if change_cue(doc.text, match):
                continue
        parts = [match.span()] if match.span() in numbers else [match.span("low"), match.span("high")]
        replace(parts, low + "-" + high)
    for match in PIXELS.finditer(doc.text):
        scale = 6 if match["english_scale"] else SCALE_EXPONENTS.get(match["chinese_scale"], 0)
        replace([match.span("value")], scaled_value(match["value"], scale) + " px")
    for pattern in (ENGLISH_PERCENTILE, CHINESE_PERCENTILE):
        for match in pattern.finditer(doc.text):
            rank = match["rank"]
            parts = [(match.start("rank"), match.end("ordinal"))] if pattern is ENGLISH_PERCENTILE else [match.span("rank")]
            replace(parts, f"{scaled_value(rank, 0)} percentile")
    for match in SCALED_QUANTITY.finditer(doc.text):
        if match.span("value") in numbers:
            replace([match.span("value")], scaled_value(match["value"], SCALE_EXPONENTS[match["unit"].lower()]))
    for span, value in list(numbers.items()):
        if GROUPED_INTEGER.fullmatch(value):
            replace([span], value.replace(",", ""))
    # A month range names two months of one year.
    for match in ENGLISH_MONTH_RANGE.finditer(doc.text):
        result[f"{match['year']}-{MONTHS[match['first'].lower()]:02d}"] += 1
    for match in CHINESE_MONTH_RANGE.finditer(doc.text):
        if match.span("second") in numbers:
            replace([match.span("second")], f"{match['year']}-{int(match['second']):02d}")
    # A calendar month without a day keeps its name in prose.
    for match in ENGLISH_MONTH.finditer(doc.text):
        if any(match.start() < end and start < match.end() for start, end in dates):
            continue
        before = doc.text[max(0, match.start() - 16):match.start()]
        after = doc.text[match.end():match.end() + 8]
        if not (after[:1].isdigit() or MONTH_CONTEXT.search(before)):
            continue
        result[f"{MONTHS[match['month'].lower()]} month"] += 1
    for match in CHINESE_MONTH.finditer(doc.text):
        if match.span("value") in numbers:
            replace([match.span("value")], f"{int(match['value'])} month")
    # "9 of the 9 records" states one quantity twice.
    for match in REPEATED_COUNT.finditer(doc.text):
        if match["first"] != match["second"]:
            continue
        parts = [match.span("first"), match.span("second")]
        if not all(part in numbers for part in parts):
            continue
        result[canonical_number_token(numbers[match.span("second")])] -= 1
        numbers.pop(match.span("second"))
    for value, count in count_literals(doc, "version").items():
        result[value[1:]] += count
    for value, count in list(result.items()):
        if SLASH_LIST.fullmatch(value):
            del result[value]
            for part in value.split("/"):
                result[part] += count
    return +result


def number_words(doc: Document) -> Counter:
    """Count the numbers that prose spells out in English.

    A spelled-out number is an optional spelling: the translation may keep
    the word or write the digits, so it never fails the comparison on its own.
    """
    result = Counter()
    for segment in doc.segments:
        if segment.kind != "prose":
            continue
        spans = inline_protected(segment.text, doc.terms)
        previous = 0
        gaps = []
        for span in spans:
            gaps.append(segment.text[previous:span.start])
            previous = span.end
        gaps.append(segment.text[previous:])
        for gap in gaps:
            for match in NUMBER_WORD.finditer(gap):
                result[str(ENGLISH_NUMBER_WORDS[match.group(0).lower()])] += 1
    return result


def split_numeric(key: str) -> tuple[str, str]:
    value, _, unit = key.partition(" ")
    return value, unit


def numeral_difference(source: Counter, target: Counter, words: Counter) -> tuple[Counter, Counter, list]:
    """Compare numerals by value and unit.

    Digits correspond one to one. A number spelled out in English may
    become digits in the translation. A unit must agree with the source:
    dropping it or naming another one states a different quantity.
    """
    src_pairs: Counter = Counter()
    tgt_pairs: Counter = Counter()
    for key, count in source.items():
        value, unit = split_numeric(key)
        src_pairs[(value, unit)] += count
    for key, count in target.items():
        value, unit = split_numeric(key)
        tgt_pairs[(value, unit)] += count
    common = src_pairs & tgt_pairs
    src_pairs -= common
    tgt_pairs -= common
    # An English number word may stand in for digits in the translation.
    for (value, unit), count in list(tgt_pairs.items()):
        while count > 0 and words.get(value, 0) > 0:
            count -= 1
            words[value] -= 1
        if count:
            tgt_pairs[(value, unit)] = count
        else:
            del tgt_pairs[(value, unit)]
    src = Counter()
    tgt = Counter()
    src_units: dict[str, set[str]] = {}
    tgt_units: dict[str, set[str]] = {}
    for (value, unit), count in src_pairs.items():
        src[value] += count
        src_units.setdefault(value, set()).add(unit)
    for (value, unit), count in tgt_pairs.items():
        tgt[value] += count
        tgt_units.setdefault(value, set()).add(unit)
    conflicts = []
    for value in sorted(set(src_units) | set(tgt_units)):
        if value not in src_units or value not in tgt_units:
            # One side does not state the value at all: that is a dropped or
            # added number, not a unit conflict.
            continue
        left = src_units[value]
        right = tgt_units[value]
        if left == right:
            continue
        conflicts.append((value, sorted(left), sorted(right)))
        # The value itself matched; only its unit differs.
        src.pop(value, None)
        tgt.pop(value, None)
    return +src, +tgt, conflicts


QUOTE_MARKER = re.compile(r"^[ \t]*(?:>[ \t]*)+")


def quote_content(line: str) -> str:
    """Strip the Markdown quote markers from a line and normalize its spacing."""
    return re.sub(r"\s+", " ", QUOTE_MARKER.sub("", line)).strip()


def quoted_lines(text: str) -> list[str]:
    return [line for line in text.split("\n") if QUOTE_MARKER.match(line)]


def compare(path: str, source: Document, target: Document, config: dict) -> list[Issue]:
    issues: list[Issue] = []

    def add(code: str, message: str, line: int = 1, severity: str = "error",
            *, section_drift: list[SectionDrift] | None = None) -> None:
        issues.append(Issue(path, line, severity, code, message, section_drift=section_drift))

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
    patterns = config.get("non_compliant_link_patterns", [])
    layout_source = without_policy_contact_rows(source, patterns)
    if layout_source.structure != target.structure:
        add("markdown-structure", "Lists, table cells, blockquotes, or thematic breaks differ", severity="warning")
    source_fields = setting_fields(source)
    target_fields = setting_fields(target) if source_fields else {}
    for key, (_, rows) in source_fields.items():
        if not rows or rows[0][1] != "Type" or key not in target_fields:
            continue
        type_token = re.fullmatch(r"`([A-Za-z][A-Za-z0-9_]*)`", rows[0][2])
        if not type_token:
            continue
        line, local = target_fields[key]
        if not local or local[0][2] != type_token[0]:
            add("setting-type", f"Check {key}: expected type {type_token[0]} in its own field",
                local[0][0] if local else line, "warning")
    default_keys = [key for key, (_, rows) in source_fields.items() if [r[1] for r in rows] == ["Type", "Default"]]
    for key in default_keys:
        if key not in target_fields:
            continue
        source_rows = source_fields[key][1]
        value = source_rows[1][2]
        number = re.match(r"`([-+]?\d+(?:\.\d+)?)`(?:\s|$)", value)
        empty_string = EMPTY_STRING_GLOSS.match(value)
        line, local = target_fields[key]
        localized = local[1][2] if len(local) == 2 else ""
        field_line = local[1][0] if len(local) == 2 else line
        if empty_string and not localized.startswith((f"`{empty_string[1]}`", empty_string[0])):
            add("setting-default", f"Check {key}: preserve the empty-string value in its own field", field_line)
        if source_rows[0][2] == "`bool`" and value.lower() in ("`true`", "`false`"):
            boolean = re.match(r"(`(?:true|false)`|true|false)(?=\s|$|[（(])", localized, re.IGNORECASE)
            if not boolean or boolean[1].strip("`").lower() != value.strip("`").lower():
                add("setting-default", f"Check {key}: expected boolean default {value} in its own field",
                    field_line, "warning")
        if number:
            # Labels are translated. Use the source field order as a review signal,
            # not a failure: a translation can legitimately reorder or convert units.
            first_number = re.search(r"(?<![\w.+-])[-+]?\d+(?:\.\d+)?(?![\w.])", localized, re.ASCII)
            if not first_number or first_number[0] != number[1]:
                add("setting-default", f"Check {key}: expected numeric default {number[1]} in its own field",
                    field_line, "warning")
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
    for kind in ["marker", "symbol"]:
        a, b = count_literals(layout_source, kind), count_literals(target, kind)
        if kind == "symbol" and patterns and a != b:
            a, b = a - policy_link_symbols(layout_source, patterns), b - policy_link_symbols(target, patterns)
        if kind == "marker" and a != b and layout_source.structure == target.structure:
            a, b = normalized_markers(layout_source), normalized_markers(target)
        if a != b:
            drift = None
            if kind == "symbol":
                drift = literal_section_drift(source, target, kind, (a - b).keys() | (b - a).keys(), set())
            add("markdown-" + kind, difference(a, b), severity="warning", section_drift=drift)
    source_inline = count_literals(source, "inline_code")
    target_inline = count_literals(target, "inline_code")
    terms = {t.lower() for t in config["terms"]}
    display = {t.lower(): t for t in config["terms"]}
    aliases = {alias: term for alias, term in config.get("source_term_aliases", {}).items()
               if term in count_literals(target, "term") and alias not in count_literals(target, "identifier")}
    promoted_terms = set()
    promoted_identifiers = Counter()
    for value in target_inline:
        content = value.strip("`")
        for span in inline_protected(content, target.terms):
            if span.kind == "term":
                promoted_terms.add(canonical_term(span.value, terms))
            if span.kind == "identifier" and span.value == content:
                # Only surplus, whole-identifier spans can replace bare mentions.
                promoted_identifiers[content] += target_inline[value] - source_inline[value]
    for kind in ["inline_code", "identifier", "term", "destination", "reference", "jsx", "expression", "hash_placeholder", "math", "comment"]:
        a, b = count_literals(source, kind), count_literals(target, kind)
        if kind == "term":
            a, b = canonical_terms(a, terms), canonical_terms(b, terms)
        if kind in {"identifier", "term"}:
            b = b.copy()
            # Adding backticks around a preserved identifier or product name
            # changes its token kind, not its spelling or meaning.
            if kind == "identifier":
                for value, count in (a - b).items():
                    credit = min(count, promoted_identifiers[value])
                    if credit > 0:
                        b[value] += credit
            else:
                for value in (a.keys() & promoted_terms) - b.keys():
                    b[value] = 1
            if aliases:
                a = a.copy()
                for alias, term in aliases.items():
                    if kind == "identifier":
                        a.pop(alias, None)
                    else:
                        count = count_literals(source, "identifier")[alias]
                        if count:
                            a[term.lower()] += count
        if kind == "destination":
            a, b = canonical_destinations(a, path), canonical_destinations(b, path)
            a = policy_removed_destinations(a, patterns)
            kept = sorted({strip_destination(v) for v in b if non_compliant(strip_destination(v), patterns)})
            if kept:
                add("non-compliant-link", "Target keeps external links that project policy removes: " + ", ".join(kept[:5]))
            # An existing bare URL can become a link. The Markdown symbol check
            # still reports markup drift, and excess or changed destinations
            # must remain visible.
            bare_links = Counter()
            target_bare = Counter()
            for doc, counts in ((source, bare_links), (target, target_bare)):
                for value, count in count_literals(doc, "url").items():
                    url = canonical_url(value)
                    if not non_compliant(url, patterns):
                        counts[f"({url})"] += count
            converted = canonical_destinations(bare_links, path) - canonical_destinations(target_bare, path)
            b = b - ((b - a) & converted)
        if kind == "inline_code" and patterns:
            dropped = policy_removed_inline_codes(source.text, patterns)
            a = Counter({v: n for v, n in a.items() if v.strip("`") not in dropped})
        code = "literal-" + kind.replace("_", "-")
        if kind == "inline_code":
            # A code span that upstream wrote with a fence marker is broken
            # markup when used as a block. Accept the move only if the target
            # block contains the exact original sample.
            a = a - repaired_inline_fences(a - b, src_code, dst_code)
            a = normalize_inline_defaults(a, source_fields, default_keys)
            b = normalize_inline_defaults(b, target_fields, default_keys)
            a = normalize_identifier_punctuation(a, b)
        missing, added, shifted = literal_difference(a, b)
        if kind == "inline_code":
            # A translated interface label is expected, not a dropped literal.
            contextual = contextual_ui_labels(source) if missing else set()
            relaxed = {v for v in missing if (v in contextual or ui_label(v.strip("`"))) and v.strip("`") not in config["terms"]}
            hard = [v for v in missing if v not in relaxed]
            if hard:
                add(code, "Missing: " + brief_literals(hard, a))
            if relaxed:
                # Project policy allows an interface label to be translated: the
                # Chinese site shows a Chinese interface. Report it as a note so
                # the finding stays visible without failing an approved file.
                add("ui-label-translated",
                    "Translated interface label: " + brief_literals(sorted(relaxed), a),
                    severity="info")
            drift = inline_code_substitutions(source, target, added, shifted)
            if drift:
                add("literal-inline-code-substitution",
                    "A section dropped a repeated inline code identifier and added a new one.",
                    severity="warning", section_drift=drift)
        elif kind == "term":
            if missing:
                add(code, "Missing: " + brief_literals(missing, a))
            # A dropped name fails. A name the target uses more often, or a
            # name only the target uses, is a review signal: the translation
            # may repeat a mention or introduce one.
            if added or shifted:
                parts = []
                if added:
                    parts.append("Added: " + brief_literals(added, b))
                if shifted:
                    parts.append("Recount: " + ", ".join(f"{v!r} {a[v]}->{b[v]}" for v in sorted(shifted)[:5]))
                drift = literal_section_drift(source, target, kind, set(added) | shifted.keys(), terms)
                add(code, "; ".join(parts), severity="warning", section_drift=drift)
        elif missing:
            add(code, "Missing: " + brief_literals(missing, a))
        elif added or shifted:
            parts = []
            if added:
                parts.append("Added: " + brief_literals(added, b))
            if shifted:
                parts.append("Count differs: " + ", ".join(f"{v[:100]!r} {a[v]}->{b[v]}" for v in sorted(shifted)[:5]))
            add(code, "; ".join(parts), severity="warning")
    # Terminology must survive inside the section that introduces it: a
    # translation may repeat or merge a mention, but a section that drops the
    # name itself translated the term away.
    source_sections_terms = section_terms(source, terms)
    target_sections_terms = section_terms(target, terms)
    section_lines = {anchor: line for _, line, _, anchor in target.headings}
    for anchor, counts in source_sections_terms.items():
        local = target_sections_terms.get(anchor)
        if local is None:
            continue
        omitted = sorted(set(counts) - set(local))
        if not omitted:
            continue
        names = ", ".join(repr(display.get(name, name)) for name in omitted[:5])
        add("literal-term", f"Section {anchor!r} omits terminology: {names}",
            section_lines.get(anchor, 1), "warning")
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
    a, b = numeric_values(source), numeric_values(target)
    missing, added, conflicts = numeral_difference(a, b, number_words(source))
    if missing or added or conflicts:
        parts = []
        if missing:
            parts.append("Missing: " + brief_literals(list(missing), missing))
        if added:
            parts.append("Added: " + brief_literals(list(added), added))
        for value, left, right in conflicts:
            parts.append(f"Unit differs for {value!r}: "
                         f"{[u or '(none)' for u in left]} vs {[u or '(none)' for u in right]}")
        add("numbers", "; ".join(parts), severity="warning")
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
    heading_lines = {line for _, line, _, _ in target.headings}
    # Upstream quotes evidence verbatim: a CNA notice, a scanner finding or a
    # generated summary that upstream prints in English stays in the source
    # language on purpose. Reproduce such a quote byte for byte and the page
    # loses no meaning; quote something upstream does not quote and the rule
    # does not apply.
    source_quotes = {quote_content(line).lower() for line in quoted_lines(source.text)}
    source_quote_blob = re.sub(r"\s+", " ", " ".join(prose(quote_content(line), language_terms)
                                               for line in quoted_lines(source.text)).lower())
    for segment, value in zip(target.segments, target_prose):
        if segment.kind in {"keyword", "fence-title"}:
            # Search-term lists may stay in the upstream language on purpose.
            # Fence titles already have their own language check.
            continue
        words = WORDS.findall(value)
        if not words or CJK.search(value):
            continue
        line = target.line(segment.start)
        if segment.kind in {"yaml", "json", "attribute"}:
            add("untranslated-metadata", "Localizable metadata or accessibility text remains English after exclusions", line, "warning")
        elif line not in heading_lines:
            raw = target.text[segment.start:segment.end]
            quoted = [l for l in raw.split("\n") if l.strip()]
            if quoted and all(QUOTE_MARKER.match(l) and quote_content(l).lower() in source_quotes
                              for l in quoted):
                continue
            if len(words) >= config["untranslated_min_words"]:
                add("untranslated-prose", "English prose remains after excluding terminology, code, and markup", line, "warning")
            elif len(words) >= 3 and re.sub(r"\s+", " ", value).strip().lower() in normalized_source:
                add("unchanged-prose", "Prose matches upstream verbatim", line, "warning")
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
                if re.sub(r"\s+", " ", sentence).strip().lower() in source_quote_blob:
                    continue
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
                    "errors": counts["error"], "warnings": counts["warning"], "notes": counts["info"],
                    "suppressed": sum(i.suppressed for i in issues)},
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
                  *, previous=None, previous_config: dict | None = None, review_results=None) -> dict:
    earlier = {}
    review_entries = result_entries(previous) if previous is not None else {}
    bound_config = config
    if previous_config is not None:
        if previous is None or previous.get("config_sha256") != digest(json.dumps(previous_config, sort_keys=True)):
            raise ValueError("Previous config does not match the reused review")
        # Exceptions affect deterministic severity, not the meaning of the
        # reviewed bytes. The new bundle still runs the full current audit.
        if dict(previous_config, exceptions=[]) != dict(config, exceptions=[]):
            raise ValueError("Cannot reuse review after a non-exception configuration change")
        bound_config = previous_config
    if previous is not None and previous.get("config_sha256") == digest(json.dumps(bound_config, sort_keys=True)):
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
