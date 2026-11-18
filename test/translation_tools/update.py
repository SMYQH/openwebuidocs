"""Two providers share one lossless extraction and validated apply path.

Autonomous mode exports a task for the current agent; it does not call another
model or require a model key. DeepL uses its text API, never an LLM gateway.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict

from .artifacts import atomic_write
from .document import CJK, Document, PLACEHOLDER, digest, mask, prose, WORDS
from .verify import ROOT, SUFFIXES, audit_text, compare, files, review_template, selected, validate_review_snapshot


def read_bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def text_bytes(raw: bytes) -> str:
    # A lossless read: Path.read_text() would normalize Windows newlines.
    return raw.decode("utf-8-sig")


def contained(root: Path, relative: str) -> Path:
    if (not isinstance(relative, str) or any(part in {"", ".", ".."} for part in relative.split("/"))
            or "\\" in relative or ":" in relative):
        raise ValueError("Bundle path escapes documentation directory")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Bundle path escapes documentation directory")
    if Path(relative).suffix.lower() not in SUFFIXES and Path(relative).name != "_category_.json":
        raise ValueError("Bundle path is not a documentation file")
    return path


def prepare(source_root: Path, target_root: Path, config: dict, patterns: list[str]) -> dict:
    if source_root.resolve() == target_root.resolve():
        raise ValueError("Source and target must be different directories")
    entries = []
    for path, source_path in files(source_root).items():
        if not selected(path, patterns):
            continue
        raw = source_path.read_bytes()
        target_raw = read_bytes(contained(target_root, path))
        doc = Document(text_bytes(raw), source_path.suffix, config["terms"])
        if doc.errors:
            raise ValueError(f"{path}: source parse errors; repair/review upstream syntax before translation")
        entries.append({"path": path, "source_sha256": digest(raw),
                        "source": text_bytes(raw),
                        "target_sha256": digest(target_raw) if target_raw is not None else None,
                        "current_target": text_bytes(target_raw) if target_raw is not None else None,
                        "segments": [{"id": i, "source": mask(s.text, doc.terms)[0], "translation": None}
                                     for i, s in enumerate(doc.segments)]})
    if not entries:
        raise ValueError("No source files matched")
    return {"schema_version": 1, "purpose": "translation-update", "config_sha256": digest(json.dumps(config, sort_keys=True)),
            "instructions": "Translate every segment from English into Simplified Chinese. Fill only translation fields. Preserve each ⟦Pn⟧ placeholder exactly, in order, once. Do not translate terminology, code, identifiers, URLs or Markdown symbols. Preserve facts, negation, numbers, meaning and section alignment. Do not invent or omit prose. Use current_target as context, not an expected answer. No API configuration is required in autonomous mode. Return this JSON bundle for validated apply.",
            "files": entries}


def task_documents(bundle: dict, source_root: Path, target_root: Path, config: dict):
    """Load the real input bytes and verify task identities before requests or writes."""
    if source_root.resolve() == target_root.resolve():
        raise ValueError("Source and target must be different directories")
    if not isinstance(bundle, dict) or bundle.get("schema_version") != 1 or bundle.get("purpose") != "translation-update":
        raise ValueError("Not a supported translation-update bundle")
    if bundle.get("config_sha256") != digest(json.dumps(config, sort_keys=True)):
        raise ValueError("Configuration changed; regenerate bundle")
    entries = bundle.get("files")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Bundle contains no files")
    seen = set()
    for entry in entries:
        path = entry["path"]
        src, dst_path = contained(source_root, path), contained(target_root, path)
        if dst_path in seen or dst_path.is_relative_to(source_root.resolve()):
            raise ValueError(f"{path}: duplicate target or target overlaps source")
        seen.add(dst_path)
        dst = read_bytes(dst_path)
        raw = src.read_bytes()
        if digest(raw) != entry["source_sha256"] or (digest(dst) if dst is not None else None) != entry["target_sha256"]:
            raise ValueError(f"{path}: source or target changed; regenerate bundle")
        doc = Document(text_bytes(raw), src.suffix, config["terms"])
        if doc.errors or len(entry["segments"]) != len(doc.segments):
            raise ValueError(f"{path}: source parse or segment count changed")
        for index, (segment, original) in enumerate(zip(entry["segments"], doc.segments)):
            if segment["id"] != index or segment["source"] != mask(original.text, doc.terms)[0]:
                raise ValueError(f"{path}: segment {index} identity changed")
        yield entry, doc, src, dst_path, raw, dst


def validate_task(bundle: dict, source_root: Path, target_root: Path, config: dict) -> dict[str, Document]:
    documents = {}
    for entry, doc, *_ in task_documents(bundle, source_root, target_root, config):
        documents[entry["path"]] = doc
        for segment, original in zip(entry["segments"], doc.segments):
            if segment["translation"] is not None:
                try:
                    doc.render_segment(original, segment["translation"], move_terms=bundle.get("provider") == "deepl")
                except ValueError as error:
                    raise ValueError(f"{entry['path']}: segment {segment['id']}: {error}") from None
    return documents


def reuse_completed(bundle: dict, previous: dict, documents: dict[str, Document], config: dict) -> None:
    """Use only exact same-page source segments from a compatible DeepL checkpoint."""
    if (not isinstance(previous, dict) or previous.get("schema_version") != 1
            or previous.get("purpose") != "translation-update" or previous.get("provider") != "deepl"
            or previous.get("config_sha256") != bundle["config_sha256"]):
        raise ValueError("Reuse requires a DeepL checkpoint with the same configuration")
    seen = set()
    memory = {}
    for entry in previous["files"]:
        path = entry["path"]
        if path not in documents:
            continue
        if path in seen:
            raise ValueError(f"{path}: duplicate file in reuse checkpoint")
        seen.add(path)
        source = entry["source"].encode("utf-8")
        if entry["source_sha256"] not in {digest(source), digest(b"\xef\xbb\xbf" + source)}:
            raise ValueError(f"{path}: source hash mismatch in reuse checkpoint")
        doc = Document(entry["source"], documents[path].suffix, config["terms"])
        if doc.errors or len(doc.segments) != len(entry["segments"]):
            raise ValueError(f"{path}: incompatible extraction in reuse checkpoint")
        for index, (original, segment) in enumerate(zip(doc.segments, entry["segments"])):
            if segment["id"] != index or mask(original.text, doc.terms)[0] != segment["source"]:
                raise ValueError(f"{path}: segment {index} identity mismatch in reuse checkpoint")
            value = segment["translation"]
            if not isinstance(value, str):
                continue
            try:
                DeepL.checked_text(value, segment["source"], doc, index)
            except ValueError:
                continue
            memory.setdefault((path, original.kind, original.text, segment["source"]), set()).add(value)
    for entry in bundle["files"]:
        path = entry["path"]
        doc = documents[path]
        for segment, original in zip(entry["segments"], doc.segments):
            matches = memory.get((path, original.kind, original.text, segment["source"]), set())
            if len(matches) == 1 and segment["translation"] is None:
                value, = matches
                # A matching string can inherit different diagnostic exclusions.
                try:
                    segment["translation"] = DeepL.checked_text(value, segment["source"], doc, segment["id"])
                except ValueError:
                    continue
                segment["reused"] = True


def pending_segments(bundle: dict) -> list[tuple[str, dict]]:
    return [(entry["path"], s) for entry in bundle["files"] for s in entry["segments"] if s["translation"] is None]


def request_groups(items, documents):
    groups = {}
    for path, segment in items:
        if documents is None:
            key = path, segment["id"]
        else:
            original = documents[path].segments[segment["id"]]
            key = path, original.kind, original.text, segment["source"]
        groups.setdefault(key, []).append((path, segment))
    return list(groups.values())


def translation_plan(bundle: dict, documents=None) -> dict:
    pending = pending_segments(bundle)
    unrequested = [(p, s) for p, s in pending if "deepl_response" not in s and WORDS.search(prose_text(s["source"]))]
    groups = request_groups(unrequested, documents)
    return {"files": len(bundle["files"]), "segments": sum(len(e["segments"]) for e in bundle["files"]),
            "pending_segments": len(pending), "cached_pending_segments": sum("deepl_response" in s for _, s in pending),
            "reused_segments": sum(s.get("reused", False) for e in bundle["files"] for s in e["segments"]),
            "deduplicated_segments": len(unrequested) - len(groups),
            "unrequested_texts": len(groups),
            "unrequested_prose_characters": sum(len(prose_text(group[0][1]["source"])) for group in groups)}


def prose_text(masked: str) -> str:
    return PLACEHOLDER.sub("", masked)


def apply_bundle(bundle: dict, source_root: Path, target_root: Path, config: dict, write: bool = False,
                 report: dict | None = None, *, review_results: dict | None = None) -> list[tuple[str, str]]:
    pending, failures = [], []
    identities = {}
    if report is not None:
        report.update({"schema_version": 1, "purpose": "translation-candidate-report", "files": [],
                       "semantic_review": "required", "validation": "incomplete"})
    for entry, doc, src_path, dst_path, src_raw, dst_raw in task_documents(bundle, source_root, target_root, config):
        path = entry["path"]
        values = []
        for index, (segment, original) in enumerate(zip(entry["segments"], doc.segments)):
            value = segment["translation"]
            if not isinstance(value, str):
                raise ValueError(f"{path}: segment {index} has no translation")
            # A copied English answer must not silently complete an AI task.
            clean = prose(original.text, doc.terms)
            if len(WORDS.findall(clean)) >= 3 and value == segment["source"]:
                raise ValueError(f"{path}: segment {index} still contains unchanged English prose")
            values.append(value)
        try:
            translated = doc.render(values, move_terms=bundle.get("provider") == "deepl")
        except ValueError as error:
            raise ValueError(f"{path}: {error}") from None
        # Keep a pre-existing target's BOM and newline style; new files use source style.
        style = dst_raw if dst_raw is not None else src_raw
        translated = translated.replace("\r\n", "\n")
        if b"\r\n" in style:
            translated = translated.replace("\n", "\r\n")
        raw = (b"\xef\xbb\xbf" if style.startswith(b"\xef\xbb\xbf") else b"") + translated.encode("utf-8")
        source_hash, candidate_hash = digest(src_raw), digest(raw)
        identities[path] = (source_hash, candidate_hash)
        audit_source = Document(audit_text(src_raw), src_path.suffix, config["terms"]) if "\r" in doc.text else doc
        candidate = Document(audit_text(raw), src_path.suffix, config["terms"])
        issues = compare(path, audit_source, candidate, config)
        blocking = [issue for issue in issues
                    if issue.severity == "error" or issue.code.startswith("untranslated-")
                    or issue.code in {"unchanged-prose", "copied-sentence", "markdown-structure", "markdown-marker", "markdown-symbol"}]
        if blocking:
            failures.append(f"{path}: " + ", ".join(f"{i.code} (line {i.line})" for i in blocking))
        if report is not None:
            report["files"].append({"path": path, "source_sha256": source_hash,
                                    "target_sha256": digest(dst_raw) if dst_raw is not None else None,
                                    "source": text_bytes(src_raw), "current_target": text_bytes(dst_raw) if dst_raw is not None else None,
                                    "candidate": translated, "candidate_sha256": candidate_hash, "issues": [asdict(i) for i in issues]})
        pending.append((path, dst_path, raw, translated, dst_raw, src_path, src_raw))
    if report is not None:
        report["validation"] = "blocked" if failures else "passed"
        report["blocking_files"] = len(failures)
    if failures:
        raise ValueError("Generated documents failed validation: " + "; ".join(failures))
    if report is not None:
        report["result_format"] = review_template(identities, config)
    if review_results is not None:
        quality = validate_review_snapshot(review_results, identities, config=config, require_config=True)
        if report is not None:
            report.update(quality=quality, semantic_review=quality["semantic_review"])
        if quality["semantic_review"] != "passed":
            raise ValueError("Semantic review incomplete or unresolved: " + ", ".join(quality["pending_files"]))
    # Validate the entire batch before touching any target. Recheck immediately
    # before writes; roll back completed writes if a later write fails.
    if write:
        for _, dst, _, _, old, src, original in pending:
            if read_bytes(dst) != old or src.read_bytes() != original:
                raise ValueError("Source or target changed during validation")
        completed = []
        try:
            for _, dst, raw, _, old, _, _ in pending:
                atomic_write(dst, raw)
                completed.append((dst, old))
        except OSError:
            for dst, old in reversed(completed):
                if old is None:
                    dst.unlink(missing_ok=True)
                else:
                    atomic_write(dst, old)
            raise
    return [(path, translated) for path, _, _, translated, _, _, _ in pending]


def load_deepl_key(env_file: Path = ROOT / ".env") -> str:
    key = os.environ.get("DEEPL_AUTH_KEY", "").strip()
    if not key and env_file.exists():
        # Deliberately never execute .env, interpolate variables, or print values.
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            match = re.match(r"\s*(?:export\s+)?DEEPL_AUTH_KEY\s*=\s*(.*?)\s*$", line)
            if match:
                value = match[1]
                key = value[1:-1] if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'" else value.split(" #", 1)[0].strip()
    if not key or key == "your-key" or any(c.isspace() for c in key):
        raise ValueError("Set DEEPL_AUTH_KEY in ./.env for DeepL mode")
    return key


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class DeepL:
    def __init__(self, key: str | None = None, opener=None, sleep=time.sleep):
        self.key, self.sleep = key, sleep
        self.opener = opener or urllib.request.build_opener(NoRedirect())

    @property
    def endpoint(self) -> str:
        return "https://api-free.deepl.com/v2/translate" if (self.key or "").endswith(":fx") else "https://api.deepl.com/v2/translate"

    def request(self, texts: list[str], *, context: str | None = None) -> list[str]:
        params = {"text": texts, "source_lang": "EN", "target_lang": "ZH-HANS", "preserve_formatting": True}
        if context is None:
            params.update(tag_handling="xml", tag_handling_version="v2", ignore_tags=["keep"],
                          outline_detection=False, non_splitting_tags=["keep"])
        else:
            params["context"] = context
        payload = json.dumps(params, ensure_ascii=False).encode("utf-8")
        if not texts or len(texts) > 50 or len(payload) > 120_000:
            raise ValueError("DeepL request exceeds safe batch limits")
        if self.key is None:
            self.key = load_deepl_key()
        for attempt in range(3):
            request = urllib.request.Request(self.endpoint, data=payload, headers={"Authorization": "DeepL-Auth-Key " + self.key, "Content-Type": "application/json"}, method="POST")
            try:
                with self.opener.open(request, timeout=45) as response:
                    result = json.loads(response.read())
                translations = result.get("translations", [])
                if len(translations) != len(texts) or not all(isinstance(v.get("text"), str) for v in translations):
                    raise ValueError("DeepL returned an invalid translation count or payload")
                return [v["text"] for v in translations]
            except urllib.error.HTTPError as error:
                error.close()
                if error.code in {429, 500, 502, 503, 504} and attempt < 2:
                    self.sleep(2 ** attempt)
                    continue
                # No response bodies, request objects, or credentials in logs.
                raise ValueError(f"DeepL request failed (HTTP {error.code})") from None
            except (urllib.error.URLError, TimeoutError, OSError):
                raise ValueError("DeepL connection failed") from None
            except (json.JSONDecodeError, AttributeError, TypeError):
                raise ValueError("DeepL returned malformed JSON") from None
        raise ValueError("DeepL retry limit reached")

    @staticmethod
    def xml_encode(value: str) -> str:
        root = ET.Element("text")
        pos, previous = 0, None
        for match in re.finditer(rf"{PLACEHOLDER.pattern}(?:[ \t]*{PLACEHOLDER.pattern})*", value):
            if previous is None:
                root.text = value[pos:match.start()]
            else:
                previous.tail = value[pos:match.start()]
            previous = ET.SubElement(root, "keep", {"id": PLACEHOLDER.match(match[0])[0][2:-1]})
            previous.text = match[0]
            pos = match.end()
        if previous is None:
            root.text = value
        else:
            previous.tail = value[pos:]
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def xml_text(value: str, original: str) -> str:
        if not isinstance(value, str) or "<!" in value or "<?" in value:
            raise ValueError("DeepL returned invalid XML content")
        try:
            root = ET.fromstring(value)
        except ET.ParseError:
            raise ValueError("DeepL returned malformed XML") from None
        if root.tag != "text" or root.attrib:
            raise ValueError("DeepL changed protected XML structure")
        allowed = {p[2:-1] for p in PLACEHOLDER.findall(original)}
        for child in root:
            if child.tag != "keep" or set(child.attrib) != {"id"} or child.attrib["id"] not in allowed or len(child):
                raise ValueError("DeepL changed protected XML structure")
            allowed.remove(child.attrib["id"])
        # v2 can merge wrappers or move prose inside them. The marker stream,
        # not the disposable XML envelope, is what the renderer must preserve.
        return "".join(root.itertext())

    @classmethod
    def xml_decode(cls, value: str, original: str) -> str:
        return cls.checked_text(cls.xml_text(value, original), original)

    @staticmethod
    def checked_text(value: str, original: str, doc: Document | None = None, index: int = 0) -> str:
        clean = PLACEHOLDER.sub("", value)
        if WORDS.search(PLACEHOLDER.sub("", original)) and not (WORDS.search(clean) or CJK.search(clean)):
            raise ValueError("DeepL dropped the segment prose")
        if doc is None:
            if PLACEHOLDER.findall(value) != PLACEHOLDER.findall(original) or "⟦" in clean or "⟧" in clean:
                raise ValueError("DeepL changed protected placeholders")
            return value
        segment = doc.segments[index]
        # Restore whitespace at Markdown boundaries. Use the masked source so
        # whitespace already inside a list-marker token is not added twice.
        _, spans = mask(segment.text, doc.terms)
        for token, span in zip(PLACEHOLDER.finditer(original), spans):
            if span.kind not in {"marker", "symbol", "destination"}:
                continue
            marker = re.escape(token[0])
            left = re.search(r"[ \t]*$", original[:token.start()])[0]
            right = re.match(r"[ \t]*", original[token.end():])[0]
            value = re.sub(rf"[ \t]*(?={marker})", lambda _: left, value, count=1)
            value = re.sub(rf"(?<={marker})[ \t]*", lambda _: right, value, count=1)
        doc.render_segment(segment, value, move_terms=True)
        return value

    @staticmethod
    def retry_parts(original: str) -> tuple[list[str], list[int]]:
        parts = re.split(f"({PLACEHOLDER.pattern})", original)
        slots = [i for i in range(0, len(parts), 2) if WORDS.search(parts[i])]
        return parts, slots

    def request_retry(self, original: str) -> list[str]:
        parts, slots = self.retry_parts(original)
        context = " ".join(PLACEHOLDER.sub(" ", original).split())
        return self.request([parts[i].strip() for i in slots], context=context)

    @classmethod
    def retry_text(cls, original: str, fragments: list[str]) -> str:
        parts, slots = cls.retry_parts(original)
        if not isinstance(fragments, list) or len(fragments) != len(slots):
            raise ValueError("DeepL returned an invalid prose fragment count")
        for i, value in zip(slots, fragments):
            if (not isinstance(value, str) or not (WORDS.search(value) or CJK.search(value))
                    or "⟦" in value or "⟧" in value):
                raise ValueError("DeepL returned an invalid prose fragment")
            part = parts[i]
            parts[i] = part[:len(part) - len(part.lstrip())] + value.strip() + part[len(part.rstrip()):]
        return "".join(parts)

    def fill(self, bundle: dict, checkpoint=None, *, documents=None, retry_rejected=False) -> None:
        pending = pending_segments(bundle)
        batch, batch_size = [], 0
        rejected, unrequested = [], []

        def save():
            if checkpoint:
                checkpoint(bundle)

        def decode(path, segment):
            try:
                original = segment["source"]
                value = (self.retry_text(original, segment["deepl_retry"]) if "deepl_retry" in segment
                         else self.xml_text(segment["deepl_response"], original))
                doc = documents[path] if documents is not None else None
                segment["translation"] = self.checked_text(value, original, doc, segment["id"])
            except ValueError as error:
                segment["provider_error"] = str(error)
                return False
            segment.pop("provider_error", None)
            return True

        def fail(items):
            details = "; ".join(f"{path}: segment {s['id']}: {s['provider_error']}" for path, s in items)
            retry_hint = " (--resume --retry-rejected available)" if any("deepl_retry" not in s for _, s in items) else ""
            raise ValueError(f"Saved DeepL output needs review{retry_hint}: {details}")

        def send():
            if not batch:
                return
            try:
                results = self.request([xml for _, xml in batch])
            except ValueError as error:
                path, segment = batch[0][0][0]
                raise ValueError(f"{path}: batch starting at segment {segment['id']}: {error}") from None
            # Save paid responses before parsing them. A malformed response must
            # remain inspectable without paying for the same request again.
            for (group, _), result in zip(batch, results):
                for _, segment in group:
                    segment["deepl_response"] = result
                    segment["deepl_tag_version"] = "v2"
            save()
            errors = [(path, s) for group, _ in batch for path, s in group if not decode(path, s)]
            save()
            if errors:
                fail(errors)

        for path, segment in pending:
            if "deepl_response" in segment:
                # Reuse an interrupted batch. Invalid cached XML needs review;
                # never silently resend it or switch translation providers.
                if not decode(path, segment):
                    rejected.append((path, segment))
            elif not WORDS.search(prose_text(segment["source"])):
                segment["translation"] = segment["source"]
            else:
                unrequested.append((path, segment))
        save()
        if rejected and not retry_rejected:
            fail(rejected)
        if retry_rejected:
            errors, unrequested, retries = [], [], []
            for path, segment in rejected:
                if "deepl_retry" in segment:
                    errors.append((path, segment))
                    continue
                if segment.get("deepl_tag_version") != "v2":
                    unrequested.append((path, segment))
                    continue
                retries.append((path, segment))
            for group in request_groups(retries, documents):
                path, segment = group[0]
                try:
                    fragments = self.request_retry(segment["source"])
                except ValueError as error:
                    raise ValueError(f"{path}: segment {segment['id']}: {error}") from None
                for _, member in group:
                    member["deepl_retry"] = fragments
                save()
                errors.extend((p, s) for p, s in group if not decode(p, s))
                save()
            if errors:
                fail(errors)

        for group in request_groups(unrequested, documents):
            path, segment = group[0]
            xml = self.xml_encode(segment["source"])
            size = len(json.dumps(xml, ensure_ascii=False).encode("utf-8")) + 2
            if size > 119_000:
                raise ValueError(f"{path}: segment {segment['id']} exceeds DeepL request size")
            if batch and (len(batch) == 50 or batch_size + size > 119_000):
                send()
                batch, batch_size = [], 0
            batch.append((group, xml))
            batch_size += size
        send()
