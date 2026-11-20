"""Prepare and checkpoint DeepL evidence for review of installed translations."""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from itertools import zip_longest
from pathlib import Path
from typing import Any

from .artifacts import save_bundle
from .document import CJK, JSON_LD, WORDS, Document, digest, inline_protected
from .update import DeepL
from .verify import audit_text, files, require_docs_directory, selected

SectionKey = tuple[str, str, int]
Section = tuple[int, str]
PROSE_FIELDS = {"name", "text", "description", "headline", "abstract"}
RETAINED_LITERALS = {"identifier", "inline_code", "number", "version", "escape", "entity"}
MAX_PART_CHARACTERS = 10_000


def visible_text(text: str) -> str:
    pieces = []
    start = 0
    for span in inline_protected(text, []):
        pieces.append(text[start:span.start])
        if span.kind == "inline_code":
            pieces.append(span.value.strip("`"))
        elif span.kind in RETAINED_LITERALS:
            pieces.append(html.unescape(span.value.lstrip("\\") if span.kind == "escape" else span.value))
        elif span.kind not in {"symbol", "marker"} or span.value == "|":
            pieces.append(" ")
        start = span.end
    pieces.append(text[start:])
    return " ".join("".join(pieces).split())


def json_ld_prose(value: Any, field: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from json_ld_prose(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from json_ld_prose(child, field)
    elif isinstance(value, str) and field in PROSE_FIELDS:
        yield visible_text(value)


def sections(doc: Document) -> dict[SectionKey, Section]:
    groups: dict[SectionKey, list[str]] = defaultdict(list)
    first_lines: dict[SectionKey, int] = {}
    preamble: SectionKey = ("preamble", "", 1)
    metadata: SectionKey = ("metadata", "", 1)
    current = preamble
    indexes: Counter[str] = Counter()
    headings = iter(doc.headings)
    heading = next(headings, None)
    for segment in doc.segments:
        line = doc.line(segment.start)
        while heading is not None and heading[1] <= line:
            _, heading_line, _, anchor = heading
            indexes[anchor] += 1
            current = ("heading", anchor, indexes[anchor])
            first_lines[current] = heading_line
            heading = next(headings, None)
        if segment.kind == "keyword":
            continue
        text = visible_text(segment.text)
        if text:
            key = metadata if segment.kind in {"json", "yaml"} else current
            groups[key].append(text)
            first_lines.setdefault(key, line)
    for index, block in enumerate(doc.opaque_code, 1):
        if match := JSON_LD.search(block):
            try:
                payload = json.loads(match["payload"])
            except ValueError:
                continue  # The full pair still shows unparsed structured data.
            key = ("json-ld", "", index)
            groups[key].extend(json_ld_prose(payload))
            first_lines[key] = doc.line(doc.text.index(block) + match.start())
    return {key: (first_lines[key], "\n".join(lines)) for key, lines in groups.items() if any(lines)}


def split_text(text: str):
    while len(text) > MAX_PART_CHARACTERS:
        end = text.rfind("\n", 0, MAX_PART_CHARACTERS + 1)
        if end < MAX_PART_CHARACTERS // 2:
            end = MAX_PART_CHARACTERS
        yield text[:end]
        text = text[end:].lstrip()
    if text:
        yield text


def prepare(source_root: Path, target_root: Path, config: dict, patterns: list[str]) -> dict:
    require_docs_directory(source_root)
    require_docs_directory(target_root)
    source, target = files(source_root), files(target_root)
    pairs = []
    for path in sorted(source.keys() | target.keys()):
        if not selected(path, patterns):
            continue
        origin = source[path].read_bytes() if path in source else None
        local = target[path].read_bytes() if path in target else None
        suffix = Path(path).suffix.lower()
        en = Document(audit_text(origin), suffix, config["terms"]) if origin is not None else None
        zh = Document(audit_text(local), suffix, config["terms"]) if local is not None else None
        left, right = sections(en) if en else {}, sections(zh) if zh else {}
        entries = []
        for key in dict.fromkeys([*left, *right]):
            en_line, en_text = left.get(key, (None, ""))
            zh_line, zh_text = right.get(key, (None, ""))
            entries.append({"kind": key[0], "anchor": key[1], "occurrence": key[2], "source_line": en_line,
                            "target_line": zh_line, "source": en_text, "target": zh_text})
        pairs.append({"path": path, "source_sha256": digest(origin) if origin is not None else None,
                      "target_sha256": digest(local) if local is not None else None,
                      "source_parse_issues": en.errors if en else [], "target_parse_issues": zh.errors if zh else [],
                      "sections": entries})
    if not pairs:
        raise ValueError("No documentation files matched")
    snapshot = digest(json.dumps([pairs, config], ensure_ascii=False, sort_keys=True))
    return {"schema_version": 1, "purpose": "deepl-backtranslation-review", "snapshot_sha256": snapshot,
            "files": pairs, "translations": {}}


def request_texts(report: dict) -> dict[str, str]:
    per_file = [[part for section in pair["sections"] for part in split_text(section["target"]) if CJK.search(part)]
                for pair in report["files"]]
    return {digest(text): text for parts in zip_longest(*per_file) for text in parts if text is not None}


def restore(report: dict, previous: dict, texts: dict[str, str]) -> None:
    if (not isinstance(previous, dict) or previous.get("purpose") != report["purpose"]
            or previous.get("schema_version") != report["schema_version"]
            or previous.get("snapshot_sha256") != report["snapshot_sha256"]):
        raise ValueError("DeepL review checkpoint does not match the current scope or snapshot")
    cached = previous.get("translations")
    if (not isinstance(cached, dict) or not cached.keys() <= texts.keys()
            or not all(isinstance(value, str) and value.strip() for value in cached.values())):
        raise ValueError("DeepL review checkpoint contains invalid translations")
    report["translations"] = cached


def pending_texts(report: dict, texts: dict[str, str]) -> dict[str, str]:
    return {key: text for key, text in texts.items() if key not in report["translations"]}


def within_budget(pending: dict[str, str], characters: int) -> dict[str, str]:
    chosen = {}
    for key, text in pending.items():
        if len(text) <= characters:
            chosen[key] = text
            characters -= len(text)
    return chosen


def batches(items: dict[str, str]):
    batch, size = [], 0
    for key, text in items.items():
        encoded_size = len(json.dumps(text, ensure_ascii=False).encode("utf-8")) + 2
        if batch and (len(batch) == 50 or size + encoded_size > 119_000):
            yield batch
            batch, size = [], 0
        batch.append((key, text))
        size += encoded_size
    if batch:
        yield batch


def collect(report: dict, pending: dict[str, str], client: DeepL, output: Path) -> None:
    save_bundle(output, report)
    for batch in batches(pending):
        translated = client.translate([text for _, text in batch], source_lang="ZH", target_lang="EN-US")
        report["translations"].update({key: value for (key, _), value in zip(batch, translated, strict=True)})
        save_bundle(output, report)


def add_comparisons(report: dict) -> None:
    for pair in report["files"]:
        for section in pair["sections"]:
            parts = [report["translations"].get(digest(text)) if CJK.search(text) else text
                     for text in split_text(section["target"])]
            if any(part is None for part in parts):
                section["backtranslation"] = None
                section["word_overlap_percent"] = None
                continue
            english = "\n".join(parts)
            section["backtranslation"] = english
            source_words = Counter(WORDS.findall(section["source"].lower()))
            back_words = Counter(WORDS.findall(english.lower()))
            total = sum(source_words.values()) + sum(back_words.values())
            section["word_overlap_percent"] = round(200 * sum((source_words & back_words).values()) / total) if total else None
