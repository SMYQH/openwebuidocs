"""Lossless prose extraction. Markdown/MDX is data, never executable code.

markdown-it supplies CommonMark block ranges; the scanner adds conservative MDX
protection. Unknown expressions are protected rather than sent for translation.
"""

from __future__ import annotations

from dataclasses import dataclass
from bisect import bisect_right
import hashlib
import html
import json
import re
import unicodedata

from markdown_it import MarkdownIt
import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


PARSER = MarkdownIt("commonmark").enable("table").disable("html_block")
# Metadata fields whose values are prose and must be translated.
TEXT_FIELDS = {"title", "sidebar_label", "description", "label"}
# Search-term lists. Translations may localize them, but keyword lists are
# not prose: keeping them in the upstream language is a deliberate choice,
# so they never trigger untranslated-prose or unchanged-prose findings.
KEYWORD_FIELDS = {"keywords"}
# Ordering and layout directives may be adjusted for the translated site.
LAYOUT_FIELDS = {"sidebar_position", "position", "collapsible", "collapsed", "hidden", "link", "custom", "className"}
ATTRIBUTE = re.compile(r'''\b(alt|title|label|placeholder|aria-label)\s*=\s*("[^"\n]*"|'[^'\n]*')''')
FENCE_TITLE = re.compile(r'''(?<!\S)title=("[^"\n]*"|'[^'\n]*')''')
PLACEHOLDER = re.compile(r"⟦P\d+⟧")
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002fa1f]")
WORDS = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")
IDENTIFIER = re.compile(
    r"(?a:(?<!\w)(?:[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+|"
    r"[a-zA-Z]\w*_[a-zA-Z0-9_]+|[a-z]+(?:[A-Z][a-zA-Z0-9]*)+|"
    r"--[a-z][\w-]*)(?!\w))"
    # A prose slash between words is not a bare filesystem path.
    r"|(?<![\w/])(?a:(?:/|\./|\.\./)[\w./{}:<>-]+)"
)
URL = re.compile(r"(?:https?://|mailto:)[^\s<>\]\)\"']+")
EXPLICIT_ID = re.compile(r"\\?\{#([^}]+)\}\s*$")


def digest(text: str | bytes) -> str:
    return hashlib.sha256(text.encode("utf-8") if isinstance(text, str) else text).hexdigest()


def literal_fence_title(value: str) -> bool:
    """A title consisting of a filename or path is a literal, not prose."""
    return bool(re.fullmatch(r"(?:[A-Za-z]:)?[\w.@~\\/-]*[\\/][\w.@~\\/-]+|[\w.@~-]+\.[A-Za-z0-9]{1,10}", value))


@dataclass(frozen=True)
class Protected:
    start: int
    end: int
    kind: str
    value: str


@dataclass
class Segment:
    start: int
    end: int
    text: str
    kind: str = "prose"


def term_pattern(terms: list[str]) -> re.Pattern:
    # Chinese has no word spaces. Bound only Latin letters/digits/underscores.
    choices = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True) if t)
    return re.compile(r"(?<![A-Za-z0-9_])(?:" + (choices or r"(?!)") + r")(?![A-Za-z0-9_])")


def balanced_end(text: str, start: int, opening: str, closing: str) -> int | None:
    """Balanced JSX expression/link destination, respecting quoted JS strings."""
    depth, quote, escaped = 0, None, False
    for i in range(start, len(text)):
        c = text[i]
        if escaped:
            escaped = False
        elif c == "\\":
            escaped = True
        elif quote:
            if c == quote:
                quote = None
        elif c in "\"'`" and opening == "{":
            quote = c
        elif c == opening:
            depth += 1
        elif c == closing:
            depth -= 1
            if depth == 0:
                return i + 1
    return None


def inline_protected(text: str, terms: list[str]) -> list[Protected]:
    """Return non-overlapping ranges, preserving exact literal spelling."""
    ranges: list[Protected] = []
    occupied = bytearray(len(text))

    def add(start: int, end: int, kind: str) -> None:
        if end > start and not any(occupied[start:end]):
            ranges.append(Protected(start, end, kind, text[start:end]))
            occupied[start:end] = b"\1" * (end - start)

    # Code spans allow arbitrary backtick run lengths and multiline contents.
    i = 0
    while i < len(text):
        if text[i] == "`" and (i == 0 or text[i - 1] != "\\"):
            run = re.match(r"`+", text[i:])[0]
            remainder = text[i + len(run):]
            paragraph_end = re.search(r"\n[ \t]*\n", remainder)
            if paragraph_end:
                remainder = remainder[:paragraph_end.start()]
            match = re.search(r"(?<!`)" + re.escape(run) + r"(?!`)", remainder)
            if match:
                end = i + len(run) + match.end()
                add(i, end, "inline_code")
                i = end
                continue
            add(i, i + len(run), "symbol")
            i += len(run)
            continue
        i += 1
    for pattern, kind in [
        (r"<!--.*?-->", "comment"),
        (r"\\?\{#[^}\n]+\}", "anchor"),
        (r"(?<![\\$])\$\$.*?(?<!\\)\$\$(?!\$)|(?<![\\$])\$(?![\s$])(?:\\.|[^\\\n$])*(?<![\s\\])\$(?![\d$])", "math"),
    ]:
        for m in re.finditer(pattern, text, re.S):
            add(m.start(), m.end(), kind)
    i = 0
    while i < len(text):
        if occupied[i]:
            i += 1
            continue
        if text[i] == "<":
            # Include JSX braces inside tags; '>' inside quoted props is not a close.
            if re.match(r"</?[A-Za-z]|<>|</>", text[i:]):
                j, quote = i + 1, None
                while j < len(text):
                    c = text[j]
                    if quote:
                        if c == quote and text[j - 1] != "\\":
                            quote = None
                    elif c in "\"'":
                        quote = c
                    elif c == "{":
                        end = balanced_end(text, j, "{", "}")
                        if end is None:
                            break
                        j = end - 1
                    elif c == ">":
                        add(i, j + 1, "jsx")
                        i = j
                        break
                    j += 1
        elif text[i] == "{" and (i == 0 or text[i - 1] != "\\"):
            end = balanced_end(text, i, "{", "}")
            if end:
                add(i, end, "expression")
                i = end - 1
        elif text.startswith("](", i):
            end = balanced_end(text, i + 1, "(", ")")
            if end:
                add(i + 1, end, "destination")
        i += 1
    for pattern, kind in [
        (r"\[\^[^\]\n]+\]|!?\[[^\]\n]+\]\[\]", "reference"),
        (r"!?\[[^\]\n]*\](\[[^\]\n]*\])", "reference"),
        (r"(?m)^\s{0,3}(\[[^\]\n]+\]:\s*\S+)", "reference"),
        (URL.pattern, "url"),
        (r"&(?:[A-Za-z][A-Za-z0-9]+|#\d+|#x[0-9a-fA-F]+);", "entity"),
        (r"\\[!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~]", "escape"),
        (r"(?m)^(?:[ \t]*>[ \t]*)*[ \t]*(?:#{1,6}(?:\s+|$)|[-+*]\s+|\d+[.)]\s+|:{3,}[a-zA-Z]*|[-=]{3,}\s*$)", "marker"),
        (r"\[[ xX]\](?=\s)|(?m:(?<=\s)#{1,6}\s*$)", "marker"),
        (IDENTIFIER.pattern, "identifier"),
        (term_pattern(terms).pattern, "term"),
        (r"(?a:(?<!\w)\d+(?:[.,:/-]\d+)*(?:%|[a-zA-Z]+)?(?!\w))", "number"),
        (r"(?m)^(?:[ \t]*>[ \t]*)+|!?(?=\[)\[|\*+|_+|~{2,}|[\]|]", "symbol"),
    ]:
        for m in re.finditer(pattern, text):
            start, end = m.span(1) if m.lastindex else m.span()
            if kind == "identifier" and text[start:end].startswith(("/", "./", "../")):
                # A sentence-ending period is prose, not part of a bare path.
                while end > start and text[end - 1] == "." and text[end - 2:end] != "/.":
                    end -= 1
            add(start, end, kind)
    return sorted(ranges, key=lambda p: p.start)


def mask(text: str, terms: list[str]) -> tuple[str, list[Protected]]:
    spans = inline_protected(text, terms)
    for i, span in reversed(list(enumerate(spans))):
        text = text[:span.start] + f"⟦P{i}⟧" + text[span.end:]
    return text, spans


def unmask(text: str, spans: list[Protected], *, move_terms: bool = False) -> str:
    expected = [f"⟦P{i}⟧" for i in range(len(spans))]
    actual = PLACEHOLDER.findall(text)
    valid_order = actual == expected
    if move_terms and not valid_order and sorted(actual) == sorted(expected):
        # DeepL can move terms within a run of terms and inline code. All other
        # placeholders stay in their slots, and code spans stay in source order.
        kinds = {key: span.kind for key, span in zip(expected, spans)}
        fixed = [i for i, span in enumerate(spans) if span.kind not in {"term", "inline_code"}]
        edges = [-1, *fixed, len(spans)]
        valid_order = (
            all(actual[i] == expected[i] for i in fixed)
            and all(sorted(actual[a + 1:b]) == sorted(expected[a + 1:b]) for a, b in zip(edges, edges[1:]))
            and [key for key in actual if kinds[key] == "inline_code"]
            == [key for key in expected if kinds[key] == "inline_code"]
        )
    remaining = PLACEHOLDER.sub("", text)
    if not valid_order or "⟦" in remaining or "⟧" in remaining:
        raise ValueError("Translation changed, duplicated, reordered, or removed protected placeholders")
    return PLACEHOLDER.sub(lambda m: spans[int(m[0][2:-1])].value, text)


def prose(text: str, terms: list[str]) -> str:
    masked, _ = mask(text, terms)
    return PLACEHOLDER.sub(" ", masked)


class Document:
    def __init__(self, text: str, suffix: str, terms: list[str]):
        self.text, self.suffix, self.terms = text, suffix, list(terms)
        self._line_offsets = [0] + [m.end() for m in re.finditer("\n", text)]
        self.segments: list[Segment] = []
        self.code: list[tuple[int, str]] = []
        self.hidden_headings: list[tuple[int, int, str, str]] = []
        self.opaque_code: list[str] = []
        self.fences: list[tuple[str, str]] = []
        self.errors: list[tuple[int, str]] = []
        self.metadata = None
        self.headings: list[tuple[int, int, str, str]] = []
        self.error_messages: dict[str, str] = {}
        self.structure: list[tuple[str, int]] = []
        self.admonitions: list[str] = []
        self.body_start = 0
        self._parse()

    def line(self, offset: int) -> int:
        return bisect_right(self._line_offsets, offset)

    def _hidden_headings(self, lines: list[str], offset: int) -> None:
        """Record headings that an unclosed code fence swallows.

        Upstream sometimes leaves a fence open, so a real section heading is
        rendered as code. The translation restores the heading; the verifier
        must compare it instead of reporting a heading-count difference.
        """
        for index, line in enumerate(lines):
            match = re.match(r"^[ \t]*(#{1,6})\s+(.+?)\s*$", line)
            if not match or match.group(2).startswith("#"):
                continue
            title = re.sub(r"\s+#+\s*$", "", match.group(2))
            explicit = EXPLICIT_ID.search(title)
            base = explicit[1].replace("\\_", "_") if explicit else slug(title)
            self.hidden_headings.append((len(match.group(1)), self.line(offset + index), title, base))

    def _yaml_segments(self, node, offset: int, path: tuple = ()) -> None:
        if isinstance(node, MappingNode):
            for key, value in node.value:
                self._yaml_segments(value, offset, path + (key.value,))
        elif isinstance(node, SequenceNode):
            for value in node.value:
                self._yaml_segments(value, offset, path)
        elif isinstance(node, ScalarNode) and node.tag.endswith(":str") and path and (path[-1] in TEXT_FIELDS or path[-1] in KEYWORD_FIELDS):
            kind = "keyword" if path[-1] in KEYWORD_FIELDS else "yaml"
            self.segments.append(Segment(offset + node.start_mark.index, offset + node.end_mark.index, node.value, kind))

    def _parse(self) -> None:
        if PLACEHOLDER.search(self.text):
            self.errors.append((1, "Reserved translation placeholder appears in source"))
        if self.suffix == ".json":
            try:
                self.metadata = json.loads(self.text)
                if not isinstance(self.metadata, dict):
                    raise ValueError("Category must be an object")
            except ValueError as error:
                self.errors.append((1, f"Invalid category JSON: {error}"))
                return
            # Category label only; keys/order/paths/options remain literal.
            for m in re.finditer(r'"(label|description)"\s*:\s*("(?:[^"\\]|\\.)*")', self.text):
                self.segments.append(Segment(m.start(2), m.end(2), json.loads(m[2]), "json"))
            return
        front = re.match(r"\A(?:\ufeff)?---[^\S\n]*\n(.*?)\n(?:---|\.\.\.)[^\S\n]*(?:\n|$)", self.text, re.S)
        if front:
            try:
                self.metadata = yaml.safe_load(front[1]) or {}
                if not isinstance(self.metadata, dict):
                    self.errors.append((1, "YAML frontmatter must be a mapping"))
                self._yaml_segments(yaml.compose(front[1]), front.start(1))
            except yaml.YAMLError:
                self.errors.append((1, "Invalid YAML frontmatter"))
            self.body_start = front.end()
        elif self.text.lstrip("\ufeff").startswith("---\n"):
            self.errors.append((1, "Unclosed YAML frontmatter"))
            return
        body = self.text[self.body_start:]
        offsets = [self.body_start]
        for line in body.splitlines(keepends=True):
            offsets.append(offsets[-1] + len(line))
        blocked = bytearray(len(self.text))

        def protect(start: int, end: int) -> None:
            blocked[start:end] = b"\1" * (end - start)

        protect(0, self.body_start)
        # MDX permits fenced blocks indented inside JSX containers. CommonMark
        # alone treats those as indented text and can mistake code comments for
        # headings. Scan fence boundaries first, without interpreting code.
        body_lines = body.splitlines(keepends=True)
        opened = None
        for index, line in enumerate(body_lines):
            candidate = re.match(r"^[ \t]*(?:>\s*)*(?:(?:[-+*]|\d+[.)])\s+)?(`{3,}|~{3,})([^\r\n]*)", line)
            if opened:
                begin, marker, info = opened
                if candidate and candidate[1][0] == marker[0] and len(candidate[1]) >= len(marker) and not candidate[2].strip():
                    protect(offsets[begin], offsets[index + 1])
                    self.code.append((self.line(offsets[begin]), "".join(body_lines[begin + 1:index])))
                    self.fences.append((marker, info))
                    self._hidden_headings(body_lines[begin + 1:index], offsets[begin + 1])
                    opened = None
            elif candidate and not (candidate[1][0] == "`" and "`" in candidate[2]):
                opened = (index, candidate[1], candidate[2].strip())
                for title in FENCE_TITLE.finditer(candidate[2]):
                    if literal_fence_title(title[1][1:-1]):
                        continue
                    start = offsets[index] + candidate.start(2) + title.start(1)
                    self.segments.append(Segment(start, start + len(title[1]), title[1][1:-1], "fence-title"))
        if opened:
            begin, marker, info = opened
            protect(offsets[begin], len(self.text))
            self.code.append((self.line(offsets[begin]), "".join(body_lines[begin + 1:])))
            self.fences.append((marker, info))
            self.errors.append((self.line(offsets[begin]), "Unclosed fenced code block"))
        parse_body = "".join("\n" if c == "\n" else " " if blocked[self.body_start + i] else c for i, c in enumerate(body))
        tokens = PARSER.parse(parse_body)
        body_spans = inline_protected(parse_body, self.terms)
        jsx_tags = [span for span in body_spans if span.kind == "jsx"]
        jsx_cursor, jsx_stack = 0, []
        void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
        for token in tokens:
            if token.type == "code_block" and token.map:
                start, end = (offsets[n] for n in token.map)
                # Indentation inside JSX children is prose/layout, not a
                # CommonMark indented code block. Fences remain protected above.
                while jsx_cursor < len(jsx_tags) and self.body_start + jsx_tags[jsx_cursor].start < start:
                    span = jsx_tags[jsx_cursor]
                    jsx_cursor += 1
                    if blocked[self.body_start + span.start]:
                        continue
                    tag = re.match(r"<(\/?)([\w.-]*)", span.value)
                    if tag[1]:
                        if tag[2] in jsx_stack:
                            del jsx_stack[len(jsx_stack) - 1 - jsx_stack[::-1].index(tag[2]):]
                    elif not span.value.rstrip().endswith("/>") and tag[2].lower() not in void_tags:
                        jsx_stack.append(tag[2])
                if jsx_stack:
                    continue
                protect(start, end)
                self.code.append((self.line(start), token.content))
            if token.type in {"bullet_list_open", "ordered_list_open", "list_item_open", "tr_open", "th_open", "td_open", "blockquote_open", "hr"}:
                self.structure.append((token.type, token.level))
        opaque_body = list(parse_body)
        for span in body_spans:
            if span.kind in {"inline_code", "comment"}:
                opaque_body[span.start:span.end] = ["\n" if c == "\n" else " " for c in span.value]
        opaque_body = "".join(opaque_body)
        for pattern in [r"(?ms)^\s*(?:import|export)\s+.*?(?:;[ \t]*(?:\n|$)|\n\s*\n|\Z)", r"(?is)<(script|style|pre|code)\b[^>]*>.*?</\1\s*>"]:
            for m in re.finditer(pattern, opaque_body):
                first = self.body_start + m.start() + len(m[0]) - len(m[0].lstrip())
                if first < len(blocked) and blocked[first]:
                    continue
                protect(self.body_start + m.start(), self.body_start + m.end())
                self.opaque_code.append(self.text[self.body_start + m.start():self.body_start + m.end()])
        # Inline ranges may cross lines (JSX props, code spans, expressions).
        # Scan only unblocked runs: braces/backticks in code must never eat prose.
        ranges: list[Protected] = []
        cursor = self.body_start
        while cursor < len(self.text):
            if blocked[cursor]:
                cursor += 1
                continue
            end = cursor
            while end < len(self.text) and not blocked[end]:
                end += 1
            for span in inline_protected(self.text[cursor:end], self.terms):
                if span.kind == "jsx":
                    for attribute in ATTRIBUTE.finditer(span.value):
                        begin = cursor + span.start + attribute.start(2)
                        finish = cursor + span.start + attribute.end(2)
                        self.segments.append(Segment(begin, finish, html.unescape(attribute[2][1:-1]), "attribute"))
                    protect(cursor + span.start, cursor + span.end)
                if span.kind in {"inline_code", "jsx", "expression", "comment", "math"} and "\n" in span.value:
                    protect(cursor + span.start, cursor + span.end)
                ranges.append(Protected(cursor + span.start, cursor + span.end, span.kind, span.value))
            cursor = end
        self.literal_spans = ranges
        # Heading scanning also works inside JSX containers ignored by CommonMark.
        seen: dict[str, int] = {}
        admonition_stack: list[int] = []
        setext = {}
        for token in tokens:
            if token.type == "heading_open" and token.map:
                begin, finish = token.map
                raw_lines = body.splitlines()
                if finish - begin == 2 and re.fullmatch(r"\s*(?:=+|-+)\s*", raw_lines[finish - 1]):
                    setext[begin] = int(token.tag[1])
        for index, line in enumerate(body.splitlines(keepends=True)):
            start = offsets[index]
            first = start + len(line) - len(line.lstrip())
            if first < start + len(line) and blocked[first]:
                continue
            admonition = re.match(r"^\s*(?:>\s*)*(?:(?:[-+*]|\d+[.)])\s+)?(:{3,})([A-Za-z][\w-]*)?(?=\s|\[|$)", line)
            if admonition:
                if admonition[2]:
                    self.admonitions.append(admonition[2])
                    admonition_stack.append(self.line(start))
                elif admonition_stack:
                    admonition_stack.pop()
                else:
                    self.errors.append((self.line(start), "Orphan admonition closing marker"))
            h = re.match(r"^[ \t]*(?:>\s*)*(#{1,6})\s+(.+?)\s*$", line)
            if h or index in setext:
                level = len(h[1]) if h else setext[index]
                title = re.sub(r"\s+#+\s*$", "", h[2]) if h else line.strip()
                explicit = EXPLICIT_ID.search(title)
                base = explicit[1].replace("\\_", "_") if explicit else slug(title)
                anchor = base
                if not explicit:
                    n = seen.get(base, 0)
                    while anchor in seen:
                        n += 1
                        anchor = f"{base}-{n}"
                    seen[base] = n
                seen[anchor] = seen.get(anchor, 0)
                self.headings.append((level, self.line(start), title, anchor))
            # Preserve leading/trailing whitespace and line endings outside segments.
            left, right = len(line) - len(line.lstrip()), len(line.rstrip())
            if right <= left:
                continue
            # Split around cross-line protected regions, preserving all original bytes.
            pos = start + left
            limit = start + right
            while pos < limit:
                if blocked[pos]:
                    pos += 1
                    continue
                end = pos
                while end < limit and not blocked[end]:
                    end += 1
                value = self.text[pos:end]
                clean = prose(value, self.terms)
                if WORDS.search(clean) or CJK.search(clean):
                    self.segments.append(Segment(pos, end, value))
                pos = end
        # A fully quoted heading inside an explicit troubleshooting/error
        # section denotes a literal diagnostic, rather than a display label.
        # Derive the spelling from the source instead of storing log messages.
        parents = []
        for level, _, title, anchor in self.headings:
            while parents and parents[-1][0] >= level:
                parents.pop()
            title = EXPLICIT_ID.sub("", title).strip()
            quoted = re.fullmatch(r'"([^"\n]+)"|“([^”\n]+)”', title)
            if quoted and any(re.search(r"\b(?:troubleshooting|errors?|exceptions?)\b", parent, re.I)
                              for _, parent in parents):
                self.error_messages[anchor] = quoted[1] or quoted[2]
            parents.append((level, title))
        self.terms.extend(self.error_messages.values())
        self.segments = [s for s in self.segments if s.kind != "prose"
                         or WORDS.search(prose(s.text, self.terms)) or CJK.search(prose(s.text, self.terms))]
        self.segments.sort(key=lambda s: s.start)
        self.code.sort(key=lambda pair: pair[0])
        for line in admonition_stack:
            self.errors.append((line, "Unclosed admonition"))

    def render_segment(self, segment: Segment, value: str, *, move_terms: bool = False) -> str:
        if not isinstance(value, str) or not value.strip() or segment.kind == "prose" and ("\n" in value or "\r" in value):
            raise ValueError("Translation must be nonempty and preserve prose line boundaries")
        _, spans = mask(segment.text, self.terms)
        restored = unmask(value, spans, move_terms=move_terms)
        if segment.kind in {"yaml", "keyword", "json", "fence-title"}:
            return json.dumps(restored, ensure_ascii=False)
        if segment.kind == "attribute":
            return '"' + html.escape(restored, quote=True) + '"'
        # Preserve every source marker, including symbols absent from placeholders.
        if markup_signature(segment.text, self.terms) != markup_signature(restored, self.terms):
            raise ValueError("Translation changed Markdown syntax")
        if move_terms and inline_structure(segment.text) != inline_structure(restored):
            raise ValueError("Translation changed rendered inline Markdown")
        return restored

    def render(self, translations: list[str], *, move_terms: bool = False) -> str:
        if len(translations) != len(self.segments):
            raise ValueError("Translation segment count differs")
        result = self.text
        for index in range(len(self.segments) - 1, -1, -1):
            segment = self.segments[index]
            try:
                restored = self.render_segment(segment, translations[index], move_terms=move_terms)
            except ValueError as error:
                raise ValueError(f"segment {index}: {error}") from None
            result = result[:segment.start] + restored + result[segment.end:]
        if self.suffix != ".json":
            # Chinese heading text needs the upstream fragment, never a new slug.
            rendered = Document(result, self.suffix, self.terms)
            if len(rendered.headings) != len(self.headings):
                raise ValueError("Translation changed heading structure")
            lines = result.splitlines(keepends=True)
            for original, translated in zip(self.headings, rendered.headings):
                if not EXPLICIT_ID.search(translated[2]):
                    index = translated[1] - 1
                    line = lines[index]
                    ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
                    indent = len(line) - len(line.lstrip())
                    prefix = "\\" if self.suffix == ".mdx" and indent else ""
                    anchor = original[3].replace("_", "\\_")
                    lines[index] = line.rstrip("\r\n ") + " " + prefix + "{#" + anchor + "}" + ending
            result = "".join(lines)
        return result


def markup_signature(text: str, terms: list[str]) -> list[str]:
    return [p.value for p in inline_protected(text, terms) if p.kind != "term"]


def inline_structure(text: str) -> list[str]:
    return [token.type for token in PARSER.parseInline(text)[0].children or [] if token.type != "text"]


JSON_LD = re.compile(r"<script\b[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>\s*\{JSON\.stringify\((?P<payload>.*?)\)\}\s*</script>", re.S)


def opaque_signature(block: str) -> str:
    """Structural signature of an MDX import/export or script/style block.

    JSON-LD payloads carry translated prose, so only their structure is
    compared. Everything else must match byte for byte.
    """
    match = JSON_LD.search(block)
    if not match:
        return block
    try:
        payload = json.loads(match.group("payload"))
    except ValueError:
        return block

    def shape(value, field=None):
        if isinstance(value, dict):
            return {k: shape(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [shape(v, field) for v in value]
        if isinstance(value, str):
            return "<prose>" if field in {"name", "text", "description", "headline", "abstract"} else value
        return value

    signature = json.dumps(shape(payload), ensure_ascii=False, sort_keys=True)
    return block[:match.start("payload")] + signature + block[match.end("payload"):]


def slug(text: str) -> str:
    text = EXPLICIT_ID.sub("", text)
    def content(tokens):
        return "".join(content(t.children) if t.children else t.content if t.type in {"text", "code_inline", "image"} else " " if t.type == "softbreak" else "" for t in tokens)
    text = content(PARSER.parseInline(text)).lower()
    return "".join(c for c in text if c in "-_ " or unicodedata.category(c)[0] in "LNM").replace(" ", "-")
