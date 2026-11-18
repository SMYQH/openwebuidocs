"""Two providers share one lossless extraction and validated apply path.

Autonomous mode exports a task for the current agent; it does not call another
model or require a model key. DeepL uses its text API, never an LLM gateway.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from .document import Document, PLACEHOLDER, digest, mask, prose, WORDS
from .verify import ROOT, compare, files, selected


def read_bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def text_bytes(raw: bytes) -> str:
    # A lossless read: Path.read_text() would normalize Windows newlines.
    return raw.decode("utf-8-sig")


def contained(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not relative or "\\" in relative or Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError("Bundle path escapes documentation directory")
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


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".translation-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def apply_bundle(bundle: dict, source_root: Path, target_root: Path, config: dict, write: bool = False) -> list[tuple[str, str]]:
    if source_root.resolve() == target_root.resolve():
        raise ValueError("Source and target must be different directories")
    if bundle.get("schema_version") != 1 or bundle.get("purpose") != "translation-update":
        raise ValueError("Not a supported translation-update bundle")
    if bundle.get("config_sha256") != digest(json.dumps(config, sort_keys=True)):
        raise ValueError("Configuration changed; regenerate bundle")
    if not isinstance(bundle.get("files"), list) or not bundle["files"]:
        raise ValueError("Bundle contains no files")
    pending = []
    seen = set()
    for entry in bundle["files"]:
        path = entry["path"]
        if path in seen:
            raise ValueError("Duplicate bundle path")
        seen.add(path)
        src_path, dst_path = contained(source_root, path), contained(target_root, path)
        src_raw, dst_raw = src_path.read_bytes(), read_bytes(dst_path)
        if digest(src_raw) != entry["source_sha256"] or (digest(dst_raw) if dst_raw is not None else None) != entry["target_sha256"]:
            raise ValueError(f"{path}: source or target changed; regenerate bundle")
        doc = Document(text_bytes(src_raw), src_path.suffix, config["terms"])
        if doc.errors:
            raise ValueError(f"{path}: source has parse errors")
        segments = entry["segments"]
        if len(segments) != len(doc.segments):
            raise ValueError(f"{path}: segment count changed")
        values = []
        for index, (segment, original) in enumerate(zip(segments, doc.segments)):
            if segment["id"] != index or segment["source"] != mask(original.text, doc.terms)[0]:
                raise ValueError(f"{path}: segment identity changed")
            value = segment["translation"]
            if not isinstance(value, str):
                raise ValueError(f"{path}: segment {index} has no translation")
            # A copied English answer must not silently complete an AI task.
            clean = prose(original.text, doc.terms)
            if len(WORDS.findall(clean)) >= 3 and value == segment["source"]:
                raise ValueError(f"{path}: segment {index} still contains unchanged English prose")
            values.append(value)
        translated = doc.render(values)
        candidate = Document(translated, src_path.suffix, config["terms"])
        blocking = [issue for issue in compare(path, doc, candidate, config)
                    if issue.severity == "error" or issue.code.startswith("untranslated-") or issue.code in {"unchanged-prose", "copied-sentence"}]
        if blocking:
            raise ValueError(f"{path}: generated document failed validation: " + ", ".join(sorted({i.code for i in blocking})))
        # Keep a pre-existing target's BOM and newline style; new files use source style.
        style = dst_raw if dst_raw is not None else src_raw
        translated = translated.replace("\r\n", "\n")
        if b"\r\n" in style:
            translated = translated.replace("\n", "\r\n")
        raw = (b"\xef\xbb\xbf" if style.startswith(b"\xef\xbb\xbf") else b"") + translated.encode("utf-8")
        pending.append((path, dst_path, raw, translated, dst_raw, src_path, src_raw))
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
    if not key or any(c.isspace() for c in key):
        raise ValueError("Set DEEPL_AUTH_KEY in ./.env for DeepL mode")
    return key


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class DeepL:
    def __init__(self, key: str, opener=None, sleep=time.sleep):
        self.key, self.sleep = key, sleep
        self.endpoint = "https://api-free.deepl.com/v2/translate" if key.endswith(":fx") else "https://api.deepl.com/v2/translate"
        self.opener = opener or urllib.request.build_opener(NoRedirect())

    def request(self, texts: list[str]) -> list[str]:
        payload = json.dumps({"text": texts, "source_lang": "EN", "target_lang": "ZH-HANS", "tag_handling": "xml", "ignore_tags": ["keep"], "preserve_formatting": True}, ensure_ascii=False).encode("utf-8")
        if not texts or len(texts) > 50 or len(payload) > 120_000:
            raise ValueError("DeepL request exceeds safe batch limits")
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
                raise ValueError("DeepL connection failed; no files were written") from None
            except (json.JSONDecodeError, AttributeError, TypeError):
                raise ValueError("DeepL returned malformed JSON") from None
        raise ValueError("DeepL retry limit reached")

    @staticmethod
    def xml_encode(value: str) -> str:
        root = ET.Element("text")
        pos, previous = 0, None
        for match in PLACEHOLDER.finditer(value):
            if previous is None:
                root.text = value[pos:match.start()]
            else:
                previous.tail = value[pos:match.start()]
            previous = ET.SubElement(root, "keep", {"id": match[0][2:-1]})
            previous.text = match[0]
            pos = match.end()
        if previous is None:
            root.text = value
        else:
            previous.tail = value[pos:]
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def xml_decode(value: str, original: str) -> str:
        if "<!" in value:
            raise ValueError("DeepL returned an XML declaration or entity")
        try:
            root = ET.fromstring(value)
        except ET.ParseError:
            raise ValueError("DeepL returned malformed XML") from None
        expected = PLACEHOLDER.findall(original)
        if root.tag != "text" or root.attrib or len(root) != len(expected):
            raise ValueError("DeepL changed protected XML structure")
        for child, placeholder in zip(root, expected):
            if child.tag != "keep" or child.attrib != {"id": placeholder[2:-1]} or child.text != placeholder or len(child):
                raise ValueError("DeepL changed a protected placeholder")
        result = "".join(root.itertext())
        if PLACEHOLDER.findall(result) != expected:
            raise ValueError("DeepL changed protected placeholder order")
        return result

    def fill(self, bundle: dict) -> None:
        pending = [s for entry in bundle["files"] for s in entry["segments"]]
        batch, batch_size = [], 0

        def send():
            if not batch:
                return
            xml = [self.xml_encode(s["source"]) for s in batch]
            results = self.request(xml)
            for segment, result in zip(batch, results):
                segment["translation"] = self.xml_decode(result, segment["source"])

        for segment in pending:
            size = len(json.dumps(self.xml_encode(segment["source"]), ensure_ascii=False).encode("utf-8")) + 2
            if size > 119_000:
                raise ValueError("A prose segment exceeds DeepL request size; split the source paragraph first")
            if batch and (len(batch) == 50 or batch_size + size > 119_000):
                send()
                batch, batch_size = [], 0
            batch.append(segment)
            batch_size += size
        send()
