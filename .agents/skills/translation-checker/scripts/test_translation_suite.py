"""Behavior tests use generated CJK text, never expected/baked-in translations.

English strings are synthetic source fixtures. Terminology is the only language
content asserted verbatim. No dictionary or bilingual reference answers exist.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error
import xml.etree.ElementTree as ET

from translation_tools.artifacts import save_bundle
from translation_tools.document import Document, PLACEHOLDER, digest, mask, prose, unmask
from translation_tools.update import DeepL, apply_bundle, load_deepl_key, prepare, reuse_completed, translation_plan, validate_task
from translation_tools.verify import REVIEW_DIMENSIONS, compare, load_config, review_bundle, validate_review, verify
from translation_check import main as check_main
from translation_update import main as update_main


def generated_cjk(length: int) -> str:
    """Generate script characters without storing translated answers."""
    return "".join(chr(0x4E00 + index) for index in range(length))


def generated_text(value: str) -> str:
    """Replace prose words with generated script characters; not a translation."""
    parts = re.split(r"(⟦P\d+⟧)", value)
    return "".join(part if PLACEHOLDER.fullmatch(part) else re.sub(r"[A-Za-z]+", lambda m: chr(0x4E00 + len(m[0])) * len(m[0]), part) for part in parts)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.terms = self.config["terms"]
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source, self.target = self.root / "en", self.root / "zh"
        self.source.mkdir()
        self.target.mkdir()

    def put(self, root, path, text):
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(text.encode("utf-8"))
        return file

    def translate(self, text, suffix=".mdx"):
        doc = Document(text, suffix, self.terms)
        self.assertFalse(doc.errors)
        return doc.render([generated_text(mask(s.text, self.terms)[0]) for s in doc.segments])

    def codes(self, source, target, suffix=".mdx"):
        return {i.code for i in compare("fixture" + suffix, Document(source, suffix, self.terms), Document(target, suffix, self.terms), self.config)}

    def fill(self, bundle):
        for entry in bundle["files"]:
            for segment in entry["segments"]:
                segment["translation"] = generated_text(segment["source"])
        return bundle


class ExtractionTests(Fixture):
    def test_mask_roundtrip_all_literals(self):
        source = "## Use **Open WebUI** with `POST /api/v1/chats` and OPENAI_API_KEY at [site](https://example.test/a_(b)) {#use-api}"
        masked, spans = mask(source, self.terms)
        self.assertEqual(unmask(masked, spans), source)
        for literal in ["Open WebUI", "POST /api/v1/chats", "OPENAI_API_KEY", "https://example.test"]:
            self.assertNotIn(literal, masked)
        self.assertNotIn("**", masked)

    def test_terms_not_part_of_other_words(self):
        value = "OpenAI OpenAIish API API_KEY"
        masked, _ = mask(value, self.terms)
        self.assertIn("OpenAIish", masked)
        self.assertNotIn("API_KEY", masked)

    def test_windows_product_name_excludes_common_noun(self):
        _, spans = mask("Windows and WINDOWS: Context Windows and context windows.", ["Windows"])
        self.assertEqual([(s.kind, s.value) for s in spans],
                         [("term", "Windows"), ("term", "WINDOWS")])

    def test_acronym_plural_is_a_single_verbatim_placeholder(self):
        source = "APIs, APIson, and `APIs`.\n"
        masked, spans = mask(source, self.terms)
        self.assertIn("APIson", masked)
        self.assertEqual([s.value for s in spans], ["APIs", "`APIs`"])
        self.assertEqual(unmask(masked, spans), source)

    def test_prefixed_release_version_is_protected_as_one_literal(self):
        version = "v12.3.45-rc.2+build.7"
        source = f"Upgrade to {version}."
        masked, spans = mask(source, self.terms)
        self.assertEqual([(s.kind, s.value) for s in spans], [("version", version)])
        self.assertEqual(unmask(masked, spans), source)

    def test_ordered_list_and_checkbox_markers_are_indivisible(self):
        for source, literal in [("1. Source prose", "1. "), ("- [x] Source prose", "[x]"), ("Source prose[^literal]", "[^literal]"), ("Source [reference][]", "[reference][]")]:
            _, spans = mask(source, self.terms)
            self.assertIn(literal, [s.value for s in spans])

    def test_multibacktick_inline_code(self):
        value = "Run ``literal ` command`` safely."
        _, spans = mask(value, self.terms)
        self.assertIn("``literal ` command``", [s.value for s in spans])

    def test_sparse_inline_candidates_keep_exact_protected_offsets(self):
        prefix = generated_cjk(48)
        source = prefix + r" \`escaped ``literal <Tag />`` <Box value={{x: '>'}}> [label](#entry) \{#} {value} </Box>"
        masked, spans = mask(source, [])
        self.assertEqual(unmask(masked, spans), source)
        self.assertTrue(masked.startswith(prefix))
        self.assertEqual(
            [(span.kind, span.value) for span in spans if span.kind not in {"symbol", "escape"}],
            [("inline_code", "``literal <Tag />``"), ("jsx", "<Box value={{x: '>'}}>"),
             ("destination", "(#entry)"), ("hash_placeholder", r"\{#}"),
             ("expression", "{value}"), ("jsx", "</Box>")],
        )
        for span in spans:
            self.assertEqual(source[span.start:span.end], span.value)

    def test_nested_fence_and_indented_code_preserved(self):
        source = "# Example\n\n````md\n```python\nprint('literal')\n```\n````\n\n    untouched_command()\n\nA source paragraph with enough words.\n"
        target = self.translate(source)
        self.assertNotIn("code-changed", self.codes(source, target))
        self.assertIn("print('literal')", target)
        self.assertIn("untouched_command()", target)

    def test_fence_titles_are_available_to_both_translation_providers(self):
        source = '```sh title="Start this source service safely" {1} showLineNumbers\necho "literal string"\n```\n'
        self.put(self.source, "a.md", source)
        bundle = self.fill(prepare(self.source, self.target, self.config, []))
        self.assertTrue(bundle["files"][0]["segments"])
        target = apply_bundle(bundle, self.source, self.target, self.config)[0][1]
        self.assertNotIn("Start this source service safely", target)
        self.assertIn('{1} showLineNumbers\necho "literal string"\n', target)
        self.assertNotIn("fence-structure", self.codes(source, target, ".md"))

    def test_filename_fence_titles_remain_literal(self):
        for title in ["tailscale/serve.json", "docker-compose.override.yml", "etc/project/config/service.conf"]:
            with self.subTest(title=title):
                source = '```json title="' + title + '"\n{}\n```\n'
                target = self.translate(source)
                self.assertIn(title, target)
                issues = compare("fixture.mdx", Document(source, ".mdx", self.terms),
                                 Document(target, ".mdx", self.terms), self.config)
                self.assertEqual(issues, [])
                self.assertIn("fence-structure", self.codes(source, target.replace(title, "other.json")))

    def test_multiline_mdx_expressions_and_esm_preserved(self):
        source = "import Thing from 'module';\n\n<Thing\n  options={{ label: 'Do not translate code', number: 2 }}\n>\n## Source heading\n\nVisible source text.\n</Thing>\n"
        target = self.translate(source)
        self.assertIn("import Thing from 'module';", target)
        self.assertIn("options={{ label: 'Do not translate code', number: 2 }}", target)
        self.assertNotIn("literal-jsx", self.codes(source, target))

    def test_indented_jsx_children_are_prose_and_attributes_not_code(self):
        source = '<Tabs>\n  <TabItem value="example" label="Source label">\n    <div>\n    Source text inside the tab.\n    </div>\n  </TabItem>\n</Tabs>\n'
        doc = Document(source, ".mdx", self.terms)
        self.assertEqual(doc.code, [])
        target = self.translate(source)
        self.assertNotIn("Source text inside the tab.", target)
        self.assertNotIn('label="Source label"', target)
        self.assertNotIn("code-changed", self.codes(source, target))

    def test_inline_html_examples_do_not_swallow_following_prose(self):
        source = 'Use `<script>` tags when needed.\n\nSource prose after the example.\n\n```html\n<script>run()</script>\n```\n'
        doc = Document(source, ".mdx", self.terms)
        self.assertEqual(doc.opaque_code, [])
        target = self.translate(source)
        self.assertNotIn("Source prose after the example.", target)
        self.assertNotIn("opaque-code-changed", self.codes(source, target))

    def test_blank_lines_before_import_are_not_mdx_code(self):
        statement = "import Thing from 'module';\n"
        source = "\n \n" + statement
        self.assertEqual(Document(source, ".mdx", self.terms).opaque_code, [statement])
        self.assertNotIn("opaque-code-changed", self.codes(source, statement))
        self.assertIn("opaque-code-changed", self.codes(source, statement.replace("module", "other")))

    def test_quoted_diagnostics_remain_literal_for_both_providers(self):
        message = "Source subsystem reports an unavailable dependency"
        source = '## Troubleshooting\n\n### "' + message + '"\n\nSource recovery instructions.\n'
        self.put(self.source, "a.md", source)
        bundle = self.fill(prepare(self.source, self.target, self.config, []))
        self.assertNotIn(message, " ".join(s["source"] for s in bundle["files"][0]["segments"]))
        target = apply_bundle(bundle, self.source, self.target, self.config)[0][1]
        self.assertIn(message, target)
        self.assertNotIn("untranslated-heading", self.codes(source, target, ".md"))

    def test_quoted_labels_outside_diagnostic_sections_still_translate(self):
        source = '## Troubleshooting\n\nSource recovery text.\n\n## Source overview\n\n### "Source heading label"\n\nSource body.\n'
        doc = Document(source, ".md", self.terms)
        self.assertEqual(doc.error_messages, {})
        self.assertNotIn("Source heading label", self.translate(source, ".md"))

    def test_status_diagnostic_heading_remains_literal(self):
        message = "499: 'SampleType' failed to resolve 'sample_property'"
        source = f"## Common Issues\n\n### 2. {message}\n\nExplain the recovery step.\n"
        target = self.translate(source, ".md")
        self.assertIn(message, target)
        self.assertNotIn("untranslated-heading", self.codes(source, target, ".md"))
        self.assertIn("literal-error-message", self.codes(source, target.replace("SampleType", "ChangedType"), ".md"))
        overview = source.replace("Common Issues", "Remote Requests")
        self.assertEqual(Document(overview, ".md", self.terms).error_messages, {})
        ordinary_heading = source.replace(message, "499: Requests that fail")
        self.assertEqual(Document(ordinary_heading, ".md", self.terms).error_messages, {})

    def test_attributes_translate_without_changing_jsx_code(self):
        source = '<Thing alt="Source description" path="/literal" title="Source title">Visible prose</Thing>\n'
        target = self.translate(source)
        self.assertIn('path="/literal"', target)
        self.assertNotIn("Source description", target)
        self.assertFalse(self.codes(source, target))

    def test_frontmatter_values_only(self):
        source = '---\ntitle: "Source heading"\nsidebar_position: 7\nslug: /literal\nkeywords: ["Source phrase", "OpenAI"]\n---\n\n# Source heading\n'
        target = self.translate(source)
        self.assertIn("sidebar_position: 7", target)
        self.assertIn("slug: /literal", target)
        self.assertNotIn("Source phrase", target)
        self.assertNotIn("metadata-literal", self.codes(source, target))

    def test_category_json_localizable_fields_only(self):
        source = json.dumps({"label": "Source category", "position": 2, "link": {"type": "doc", "id": "literal/path"}})
        target = self.translate(source, ".json")
        self.assertEqual(json.loads(target)["link"], json.loads(source)["link"])
        self.assertFalse(self.codes(source, target, ".json"))

    def test_comments_math_and_template_placeholders_protected(self):
        source = "Text <!-- literal comment --> with $x_1 + y$ and {{CONTEXT}}.\n"
        target = self.translate(source)
        for value in ["<!-- literal comment -->", "$x_1 + y$", "{{CONTEXT}}"]:
            self.assertIn(value, target)

    def test_currency_does_not_mask_prose_between_prices_as_math(self):
        source = "Pay $12 per 1,000 requests, billed every 30 days or at $100.\n"
        masked, spans = mask(source, self.terms)
        self.assertNotIn("math", {span.kind for span in spans})
        self.assertIn("requests", masked)
        target = generated_cjk(30) + " 12 / 1,000 / 30 / 100.\n"
        self.assertNotIn("literal-math", self.codes(source, target))

    def test_math_delimiters_respect_escapes_and_whitespace(self):
        for source in [r"Use \$cash and \$money.", "$ spaced prose $", "$5 and $10"]:
            with self.subTest(source=source):
                self.assertNotIn("math", {span.kind for span in mask(source, self.terms)[1]})
        for source in ["Use $x + y$ here.", "Use $$x + y$$ here."]:
            with self.subTest(source=source):
                self.assertIn("math", {span.kind for span in mask(source, self.terms)[1]})

    def test_bare_windows_paths_are_protected_before_terminology(self):
        root = r"C:\OpenAI"
        file = root + r"\7-day\settings.json"
        source = f"Inspect {file}. Backup root: {root}.\n"
        target = f"{generated_cjk(5)} {file} {root}\n"
        tick = chr(96)
        spans = mask(source, self.terms)[1]
        self.assertEqual([(span.kind, span.value) for span in spans], [
            ("identifier", file), ("identifier", root),
        ])
        for good in (target, target.replace(file, f"{tick}{file}{tick}")):
            findings = self.codes(source, good)
            self.assertNotIn("literal-term", findings)
            self.assertNotIn("literal-identifier", findings)
        self.assertIn("literal-identifier", self.codes(source, target.replace("settings.json", "other.json")))
        self.assertNotIn("numbers", self.codes(source, target.replace("7-day", "8-day")))

    def test_sentence_punctuation_is_not_part_of_bare_paths(self):
        source = "Read /photos. Inspect /archive/data.csv.\n"
        target = generated_cjk(8) + " /photos /archive/data.csv\n"
        self.assertNotIn("literal-identifier", self.codes(source, target))
        self.assertIn("literal-identifier", self.codes(source, target.replace("/photos", "/changed")))
        spans = mask("Read /photos/.", self.terms)[1]
        self.assertIn("/photos/.", [span.value for span in spans])

    def test_prose_slashes_do_not_hide_terms_or_adjacent_paths(self):
        cjk = generated_cjk(3)
        source = "Source API and /archive/config with API_KEY and --source.\n"
        target = f"{cjk}/API/{cjk} /archive/config{cjk}API_KEY{cjk}--source{cjk}.\n"
        spans = mask(target, self.terms)[1]
        self.assertEqual([s.value for s in spans if s.kind == "identifier"], ["/archive/config", "API_KEY", "--source"])
        self.assertIn(("term", "API"), [(s.kind, s.value) for s in spans])
        self.assertFalse({"literal-identifier", "literal-term"} & self.codes(source, target))
        self.assertIn("literal-identifier", self.codes(source, target.replace("/archive/config", "")))

    def test_html_code_is_never_prose(self):
        source = '<code>source_command --literal</code>\n\n<pre>Literal source code\n</pre>\n\nVisible source prose.\n'
        target = self.translate(source)
        self.assertIn('<code>source_command --literal</code>', target)
        self.assertIn('<pre>Literal source code\n</pre>', target)

    def test_duplicate_heading_slugs(self):
        source = "## Source title\n\nFirst body.\n\n## Source title\n\nSecond body.\n"
        target = self.translate(source)
        self.assertIn("{#source-title}", target)
        self.assertIn("{#source-title-1}", target)
        self.assertNotIn("heading-structure", self.codes(source, target))

    def test_indented_mdx_heading_id_escaped(self):
        source = "<TabItem>\n  ## Source title\n\n  Source prose.\n</TabItem>\n"
        target = self.translate(source)
        self.assertIn(r"\{#source-title}", target)

    def test_placeholder_change_duplicate_or_reorder_rejected(self):
        source, spans = mask("Use `literal_a` with `literal_b`.", self.terms)
        for bad in [source.replace("⟦P0⟧", ""), source + "⟦P0⟧", source.replace("⟦P0⟧", "⟦P99⟧"), source.replace("⟦P0⟧", "⟦P1⟧", 1)]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                unmask(bad, spans)

    def test_new_markdown_syntax_rejected(self):
        doc = Document("Plain source prose.", ".md", self.terms)
        with self.assertRaises(ValueError):
            doc.render(["**" + generated_text(doc.segments[0].text) + "**"])

    def test_unclosed_fence_reported(self):
        doc = Document("# Header\n\n```python\nprint('x')\n", ".md", self.terms)
        self.assertTrue(any("Unclosed fenced" in message for _, message in doc.errors))

    def test_unbalanced_admonitions_reported(self):
        for source in [":::tip Title\nBody text.\n", "::: \n"]:
            self.assertTrue(Document(source, ".mdx", self.terms).errors)

    def test_empty_code_delimiters_do_not_swallow_later_headings(self):
        source = "Default: ``\n\n## Source heading\n\nUse `literal` here.\n"
        doc = Document(source, ".mdx", self.terms)
        self.assertEqual(len(doc.headings), 1)
        self.assertEqual(doc.headings[0][3], "source-heading")

    def test_four_space_mdx_fence_never_becomes_heading_or_prose(self):
        source = '<Tabs>\n  <TabItem value="literal">\n    ```python\n    # Not a heading\n    import literal_module\n    ```\n  </TabItem>\n</Tabs>\n\n## Real heading\n'
        doc = Document(source, ".mdx", self.terms)
        self.assertEqual([h[3] for h in doc.headings], ["real-heading"])
        self.assertNotIn("Not a heading", " ".join(s.text for s in doc.segments))
        self.assertFalse(doc.opaque_code)

    def test_import_inside_fence_cannot_swallow_following_heading(self):
        source = "```python\nimport literal_module\n```\n### Real heading\n\nSource prose.\n"
        doc = Document(source, ".mdx", self.terms)
        self.assertEqual(doc.headings[0][3], "real-heading")

    def test_code_like_heading_text_is_slugged_as_text(self):
        source = "## Source `<small>`\n"
        self.assertEqual(Document(source, ".md", self.terms).headings[0][3], "source-small")

    def test_setext_headings_keep_upstream_anchor(self):
        source = "Source heading\n==============\n\nSource body.\n"
        target = self.translate(source, ".md")
        self.assertIn("{#source-heading}", target)
        self.assertNotIn("heading-structure", self.codes(source, target, ".md"))

    def test_admonitions_inside_lists_and_bracket_titles(self):
        for source in ["- :::info Source title\n  Source prose.\n  :::\n", ":::tip[Source title]\nSource prose.\n:::\n"]:
            self.assertFalse(Document(source, ".mdx", self.terms).errors)


class VerificationTests(Fixture):
    def test_setting_default_cannot_be_satisfied_by_another_setting_or_body(self):
        def section(key, value, label):
            return f"#### `{key}`\n\n- Type: `int`\n- {label}: {value}\n- Description: `10000`.\n\n"

        a = section("SETTING_A", "`10000` (milliseconds)", "Default")
        b = section("SETTING_B", "`10000`", "Default")
        label = generated_cjk(3)
        self.assertNotIn("setting-default", self.codes(a + b, section("SETTING_A", "`10000`", label) + b))
        for wrong in ["None", "`100000`", "`-10000`", "`10000.5`", "`30` (formerly `10000`)"]:
            with self.subTest(wrong=wrong):
                self.assertIn("setting-default", self.codes(a + b, section("SETTING_A", wrong, label) + b))
        self.assertIn("setting-default", self.codes(a + b, "#### `SETTING_A`\n\n" + b))

    def test_setting_type_is_checked_in_its_own_row(self):
        label = generated_cjk(3)
        source = "#### `SETTING_A`\n\n- Type: `bool`\n- Default: `False`\n"
        local = source.replace("Type", label).replace("Default", generated_cjk(4))
        self.assertNotIn("setting-type", self.codes(source, local))
        for wrong in ["`str`", "`str` (formerly `bool`)"]:
            with self.subTest(wrong=wrong):
                self.assertIn("setting-type", self.codes(source, local.replace("`bool`", wrong)))
        self.assertIn("setting-type", self.codes(source, "#### `SETTING_A`\n\n- Default: `False`\n"))

    def test_setting_boolean_default_cannot_be_satisfied_by_body(self):
        label = generated_cjk(3)
        source = "#### `SETTING_A`\n\n- Type: `bool`\n- Default: `False`\n- Description: `True` or `False`.\n"
        local = source.replace("Default: `False`", f"{label}：`false`")
        self.assertNotIn("setting-default", self.codes(source, local))
        self.assertIn("setting-default", self.codes(source, local.replace("`false`", "`True`")))

    def test_escaped_hash_placeholder_is_literal_not_mdx_code(self):
        source = "## Settings.{#} {#stable-heading}\n\nText {node.value}.\n"
        escaped = source.replace(".{#}", r".\{#}")
        self.assertNotIn("literal-expression", self.codes(source, escaped))
        self.assertNotIn("literal-hash-placeholder", self.codes(source, escaped))
        self.assertIn("literal-hash-placeholder", self.codes(source, escaped.replace(r"\{#}", "")))
        self.assertIn("literal-expression", self.codes(source, escaped.replace("{node.value}", "{other.value}")))
        masked, spans = mask(escaped, self.terms)
        self.assertIn(r"\{#}", [span.value for span in spans])
        self.assertEqual(unmask(masked, spans), escaped)

    def test_missing_and_extra_files_and_category_coverage(self):
        self.put(self.source, "missing.md", "Source prose.")
        self.put(self.target, "extra.md", "Extra source prose.")
        self.put(self.source, "_category_.json", '{"label":"OpenAI"}')
        self.put(self.target, "_category_.json", '{"label":"OpenAI"}')
        report = verify(self.source, self.target, self.config)
        self.assertEqual(report["summary"]["file_coverage_percent"], 50)
        self.assertEqual({i["code"] for i in report["issues"]}, {"missing-file", "extra-file"})

    def test_empty_filter_fails(self):
        with self.assertRaises(ValueError):
            verify(self.source, self.target, self.config, ["missing/*"])

    def test_terms_code_symbols_not_untranslated(self):
        source = "# OpenAI {#openai}\n\nOpenAI API Docker Python Kubernetes Redis\n\n`these are many English words in literal code`\n"
        self.assertNotIn("untranslated-prose", self.codes(source, source))

    def test_english_prose_detected(self):
        source = "This source paragraph contains enough English words to require a translated counterpart.\n"
        self.assertIn("untranslated-prose", self.codes(source, source))

    def test_short_headings_and_metadata_are_checked_without_answers(self):
        source = '---\ntitle: Source\n---\n\n## Source\n'
        codes = self.codes(source, source)
        self.assertTrue({"untranslated-heading", "untranslated-metadata"}.issubset(codes))

    def test_protected_term_drop_detected(self):
        source = "Use OpenAI for source work.\n"
        target = self.translate(source).replace("OpenAI", "")
        self.assertIn("literal-term", self.codes(source, target))

    def test_file_wide_term_and_symbol_warnings_locate_section_drift(self):
        text = generated_cjk(8)
        source = "## Alpha {#alpha}\n\n**OpenAI**.\n\n## Beta {#beta}\n\nOpenAI.\n"
        target = f"\n## {text} {{#alpha}}\n\nOpenAI {text} OpenAI.\n\n## {text} {{#beta}}\n\nOpenAI.\n"
        self.put(self.source, "fixture.mdx", source)
        self.put(self.target, "fixture.mdx", target)
        report = verify(self.source, self.target, self.config)
        warnings = {row["code"]: row for row in report["issues"] if row["severity"] == "warning"}
        for code, token, counts in (("literal-term", "openai", (1, 2)), ("markdown-symbol", "**", (2, 0))):
            with self.subTest(code=code):
                row = warnings[code]
                self.assertEqual(row["line"], 1)
                self.assertEqual(row["section_drift"], [{
                    "anchor": "alpha", "source_line": 1, "target_line": 2, "token": token,
                    "source_count": counts[0], "target_count": counts[1],
                }])

    def test_literal_only_lines_are_checked_without_surrounding_prose(self):
        for source, target, code in [
            ("`LITERAL_TOKEN`\n", "`CHANGED_TOKEN`\n", "literal-inline-code"),
            ("LITERAL_TOKEN\n", generated_cjk(4) + "\n", "literal-identifier"),
            ("OpenAI\n", generated_cjk(4) + "\n", "literal-term"),
            ("https://example.test/source\n", "https://other.test/target\n", "literal-url"),
        ]:
            with self.subTest(code=code):
                found = [i for i in self.issues(source, target) if i.code == code]
                self.assertTrue(found)
                self.assertEqual(found[0].severity, "error")

    def test_backticks_do_not_hide_preserved_identifiers_or_product_names(self):
        source = "Set LITERAL_KEY with OpenAI for this source task.\n"
        target = generated_cjk(8) + " `LITERAL_KEY` `OpenAI`.\n"
        self.assertNotIn("literal-identifier", self.codes(source, target))
        self.assertNotIn("literal-term", self.codes(source, target))
        self.assertIn("literal-identifier", self.codes(source, target.replace("LITERAL_KEY", "CHANGED_KEY")))
        self.assertIn("literal-term", self.codes(source, target.replace("OpenAI", "OtherVendor")))

    def test_repeated_bare_identifiers_may_gain_backticks_without_losing_mentions(self):
        source = "Use SETTING_KEY and `SETTING_KEY`. Check SETTING_KEY. Reuse SETTING_KEY.\n"
        local = generated_cjk(8)
        good = f"{local} SETTING_KEY {local} `SETTING_KEY` {local} `SETTING_KEY` {local} `SETTING_KEY`.\n"
        self.assertNotIn("literal-identifier", self.codes(source, good))
        self.assertIn("literal-identifier", self.codes(source, good.replace(" `SETTING_KEY`", "", 1)))
        self.assertIn("literal-identifier", self.codes(source, good.replace(" `SETTING_KEY`", " `echo SETTING_KEY`", 1)))
        missing = f"{local} `SETTING_KEY`.\n"
        findings = {i.code: i.severity for i in self.issues(source, missing)}
        self.assertEqual(findings.get("literal-identifier"), "error")
        self.assertNotIn("literal-inline-code", findings)

    def test_code_structure_must_stay_identical(self):
        source = "```python\n# literal comment\nrun()\n```\n"
        # Comments and example strings stay verbatim, like executable code.
        self.assertIn("code-changed", self.codes(source, source.replace("literal comment", "different comment")))
        # Commands and identifiers are literal: a failure.
        self.assertIn("code-changed", self.codes(source, source.replace("run()", "other()")))

    def test_table_pipe_escape_preserves_rendered_code_only_in_table_rows(self):
        source = "| Column | Detail |\n| --- | --- |\n| Token | `left|right` |\n"
        escaped = source.replace("left|right", r"left\|right")
        self.assertNotIn("literal-inline-code", self.codes(source, escaped))
        self.assertNotIn("table-code-pipe", self.codes(source, escaped))
        self.assertIn("table-code-pipe", self.codes(escaped, source))
        self.assertIn("literal-inline-code", self.codes(source, escaped.replace("right", "changed")))
        self.assertIn("literal-inline-code", self.codes("`left|right`\n", "`left\\|right`\n"))

    def test_control_character_reports_its_line_and_codepoint(self):
        source = "Line one.\n\tLine two.\n"
        findings = self.issues(source, source.replace("Line two", "\x08Line two"))
        corrupt = [issue for issue in findings if issue.code == "target-corruption"]
        self.assertEqual([(issue.line, issue.severity) for issue in corrupt], [(2, "error")])
        self.assertIn("U+0008", corrupt[0].message)
        self.assertNotIn("target-corruption", self.codes(source, source))

    def test_code_string_values_are_hard_preservation_failures(self):
        source = '```sh\nexport API_URL="https://example.test/v1"\n```\n'
        changed = source.replace("example.test", "other.test")
        found = [i for i in self.issues(source, changed) if i.code == "code-changed"]
        self.assertEqual([i.severity for i in found], ["error"])

    def test_source_derived_diagnostic_headings_must_survive_verbatim(self):
        message = "Source subsystem reports an unavailable dependency"
        source = '## Troubleshooting\n\n### "' + message + '"\n\nSource recovery instructions.\n'
        target = self.translate(source, ".md")
        self.assertNotIn("untranslated-prose", self.codes(source, target, ".md"))
        found = [i for i in compare("fixture.md", Document(source, ".md", self.terms),
                                   Document(target.replace(message, generated_cjk(8)), ".md", self.terms), self.config)
                 if i.code == "literal-error-message"]
        self.assertEqual([i.severity for i in found], ["error"])

    def test_fence_directives_are_preserved_apart_from_title(self):
        source = '```python title="Example source" {1,3} showLineNumbers\nrun()\n```\n'
        for changed in [source.replace("{1,3}", "{2}"), source.replace(" showLineNumbers", ""),
                        source.replace(' title="Example source"', "")]:
            with self.subTest(changed=changed):
                self.assertIn("fence-structure", self.codes(source, changed))

    def test_json_ld_preserves_types_urls_and_surrounding_code(self):
        payload = '{"@context":"https://schema.org","@type":"FAQPage","url":"https://example.test","name":"Source name"}'
        source = '<script type="application/ld+json">{JSON.stringify(' + payload + ')}</script>\n'
        for old, new in [("FAQPage", "Article"), ("schema.org", "other.test"),
                         ("https://example.test", "https://changed.test"),
                         ("application/ld+json", "application/json")]:
            with self.subTest(field=old):
                self.assertIn("opaque-code-changed", self.codes(source, source.replace(old, new)))

    def test_heading_count_difference_does_not_skip_section_checks(self):
        source = "# First\n\n" + "source word " * 20 + "\n\n## Second\n\nAnother source paragraph.\n"
        target = "# " + generated_text("First") + " {#first}\n\n"
        codes = self.codes(source, target)
        self.assertIn("heading-structure", codes)
        self.assertIn("empty-section", codes)

    def test_wrong_anchor_and_duplicate_anchor_detected(self):
        source = "# First\n\n## Second\n"
        target = self.translate(source).replace("{#second}", "{#first}")
        self.assertTrue({"heading-structure", "duplicate-anchor"}.issubset(self.codes(source, target)))

    def test_number_drift_is_review_warning(self):
        source = "Wait 30 seconds for source service.\n"
        self.assertIn("numbers", self.codes(source, self.translate(source).replace("30", "300")))

    def test_release_versions_compare_all_components(self):
        for original, equivalent, changed in [
            ("12.3.45", "v12.3.45", "v12.3.46"),
            ("v12.3.45-rc.2+build.7", "v12.3.45-rc.2+build.7", "v12.3.45-rc.3+build.7"),
        ]:
            with self.subTest(original=original):
                source = f"Upgrade to {original}.\n"
                self.assertNotIn("numbers", self.codes(source, f"{generated_cjk(2)}{equivalent}\n"))
                self.assertIn("numbers", self.codes(source, f"{generated_cjk(2)}{changed}\n"))
                self.assertIn("literal-inline-code", self.codes(f"`{original}`\n", f"`{changed}`\n"))

    def test_localized_duration_preserves_value_and_unit(self):
        for original, equivalent in [("37s", "37 \u79d2"), ("37 seconds", "37 \u79d2"),
                                     ("37-second", "37\u79d2"),
                                     ("37ms", "37 \u6beb\u79d2"), ("3.5 milliseconds", "3.5 \u6beb\u79d2"),
                                     ("over 45 years", "45 \u4f59\u5e74")]:
            with self.subTest(original=original):
                source = f"Wait {original}.\n"
                self.assertNotIn("numbers", self.codes(source, f"{generated_cjk(2)} {equivalent}\n"))
                self.assertIn("numbers", self.codes(source, f"{generated_cjk(2)} 50\u79d2\n"))
                self.assertIn("literal-inline-code", self.codes(f"`{original}`\n", f"`{equivalent}`\n"))
        self.assertIn("numbers", self.codes("Wait 37ms.\n", "37\u79d2\n"))
        self.assertIn("numbers", self.codes("Wait 37ms.\n", "37\n"))

    def test_coordinated_deadlines_inherit_only_omitted_unit(self):
        source = "Finish within 27 minutes, and each stage within 14.\n"
        prose = generated_cjk(3)
        same = f"{prose} 27 \u5206\u949f\uff0c{prose} 14 \u5206\u949f\u3002\n"
        self.assertNotIn("numbers", self.codes(source, same))
        self.assertIn("numbers", self.codes(source, same.replace("14", "15")))
        self.assertIn("numbers", self.codes(source, same.replace("14 \u5206\u949f", "14 \u79d2")))
        self.assertIn("numbers", self.codes(source, same.replace("14 \u5206\u949f", "14")))
        explicit_count = source.replace("within 14.", "within 14 steps.")
        self.assertIn("numbers", self.codes(explicit_count, same))

    def test_dates_compare_values_instead_of_word_order(self):
        for english, local, changed in [
            ("May 2044", "2044\u5e745\u6708", "2044\u5e746\u6708"),
            ("May 9, 2044", "2044 \u5e74 5 \u6708 9 \u65e5", "2044 \u5e74 5 \u6708 8 \u65e5"),
            ("9th May 2044", "2044\u5e745\u67089\u65e5", "2044\u5e745\u67088\u65e5"),
            ("May 9th, 2044", "2044\u5e745\u67089\u65e5", "2044\u5e745\u67088\u65e5"),
        ]:
            with self.subTest(date=english):
                source = "Published " + english + ".\n"
                self.assertNotIn("numbers", self.codes(source, generated_cjk(2) + local + "\n"))
                self.assertIn("numbers", self.codes(source, generated_cjk(2) + changed + "\n"))
                self.assertIn("literal-inline-code", self.codes(f"`{english}`\n", f"`{local}`\n"))

    def test_dropped_date_component_is_reported(self):
        self.assertIn("numbers", self.codes("May 2044\n", "2044\n"))
        self.assertIn("numbers", self.codes("May 9, 2044\n", "2044\u5e745\u6708\n"))
        self.assertIn("numbers", self.codes("9th May 2044\n", "2044\u5e745\u6708\n"))

    def test_coordinated_dates_keep_both_days_in_the_shared_month(self):
        english = "7th and 9th May 2044"
        prose = generated_cjk(3)
        for local in ("2044\u5e745\u67087\u65e5\u548c9\u65e5",
                      "2044 \u5e74 5 \u6708 7 \u3001 9 \u65e5",
                      "2044\u5e745\u67087\u65e5\u548c2044\u5e745\u67089\u65e5"):
            with self.subTest(local=local):
                self.assertNotIn("numbers", self.codes(f"Published {english}.\n", f"{prose}{local}\n"))
        for local in ("2044\u5e745\u67086\u65e5\u548c9\u65e5",
                      "2044\u5e746\u67087\u65e5\u548c9\u65e5",
                      "2044\u5e745\u67089\u65e5"):
            with self.subTest(local=local):
                self.assertIn("numbers", self.codes(f"Published {english}.\n", f"{prose}{local}\n"))

    def test_month_prepositions_match_whole_words(self):
        prose = generated_cjk(8)
        for text in ("Synchronization May Stall", "The Plugin May Fail", "The Format May Change"):
            with self.subTest(text=text):
                self.assertNotIn("numbers", self.codes(f"## {text}\n", f"## {prose}\n"))
        self.assertNotIn("numbers", self.codes("Available in May.\n", f"{prose} 5\u6708\n"))
        self.assertIn("numbers", self.codes("Available in May.\n", f"{prose} 6\u6708\n"))
        self.assertIn("numbers", self.codes("Available in May.\n", f"{prose}\n"))

    def test_explicit_clock_notation_preserves_period_and_minute(self):
        for original, local, changed in [
            ("3pm", "\u4e0b\u5348 3 \u70b9", "\u4e0a\u5348 3 \u70b9"),
            ("9AM", "\u65e9\u4e0a 9 \u70b9", "\u4e0b\u5348 9 \u70b9"),
            ("12:15 AM", "\u4e0a\u534812\u70b915\u5206", "\u4e0a\u534812\u70b916\u5206"),
            ("12 PM", "\u4e0b\u5348 12 \u70b9", "\u4e0b\u5348 1 \u70b9"),
            ("4:35 AM", "\u51cc\u6668 4:35", "\u51cc\u6668 4:36"),
            ("8:25 PM", "\u665a\u4e0a 8:25", "\u65e9\u4e0a 8:25"),
        ]:
            with self.subTest(original=original):
                self.assertNotIn("numbers", self.codes(f"Starts at {original}.\n", local))
                self.assertIn("numbers", self.codes(f"Starts at {original}.\n", changed))
                self.assertIn("literal-inline-code", self.codes(f"`{original}`\n", f"`{local}`\n"))
        self.assertIn("numbers", self.codes("3pm\n", "3\u70b9\n"))

    def test_localized_numeric_units_keep_values_and_code_distinct(self):
        prefix = generated_cjk(4)
        for upstream, localized, changed in [
            ("5x", "5 \u500d", "50 \u500d"),
            ("5x", "5\u00d7", "5"),
            ("30 to 40%", "30-40%", "30-41%"),
            ("30% to 40%", "30\u81f340%", "31\u81f340%"),
            ("3.5 to 4.5%", "3.5\u20134.5%", "3.5\u20134.5"),
            ("10-15", "10\u201315", "10\u201316"),
            ("30 to 60", "30\u201360", "30\u201361"),
            ("5,000 to 12,000", "5000-12000", "5000-12200"),
            ("5,000-12,000", "5000\u81f312000", "5000\u81f312200"),
        ]:
            with self.subTest(upstream=upstream, localized=localized):
                self.assertNotIn("numbers", self.codes(f"Observed {upstream}.\n", f"{prefix} {localized}\n"))
                self.assertIn("numbers", self.codes(f"Observed {upstream}.\n", f"{prefix} {changed}\n"))
                self.assertIn("literal-inline-code", self.codes(f"`{upstream}`\n", f"`{localized}`\n"))

    def test_duration_after_slash_keeps_its_value_and_unit(self):
        source = "Allow 12 items/7-day period.\n"
        target = f"{generated_cjk(4)} 12, 7\u5929\n"
        self.assertNotIn("numbers", self.codes(source, target))
        for changed in (target.replace("7", "8"), target.replace("\u5929", "\u5468"), target.replace("\u5929", "")):
            self.assertIn("numbers", self.codes(source, changed))

        for literal in ("/var/archive/7-day", "https://example.com/7-day"):
            original = f"Open {literal}.\n"
            changed = f"{generated_cjk(4)} {literal.replace('7-day', '8-day')}\n"
            codes = self.codes(original, changed)
            self.assertNotIn("numbers", codes)
            self.assertTrue(any(code.startswith("literal-") for code in codes), codes)

    def test_range_requires_two_bounds_and_an_explicit_separator(self):
        source = "Choose 10 to 15 items.\n"
        for value in ("10, 15", "10 -15", "10\u201315.1", "10 to 15%", "10 to 15.0.0"):
            with self.subTest(value=value):
                self.assertIn("numbers", self.codes(source, f"{generated_cjk(2)} {value}\n"))

    def test_spelled_out_zero_matches_one_digit_occurrence(self):
        source = "The counter starts at zero."
        target = f"{generated_cjk(4)} 0"
        self.assertNotIn("numbers", self.codes(source, target))
        self.assertIn("numbers", self.codes(source, target.replace("0", "1")))
        self.assertIn("numbers", self.codes(source, f"{target}, 0"))
        self.assertIn("literal-inline-code", self.codes("Use `zero`.", target))

    def test_calendar_year_span_is_not_a_duration(self):
        start, end = 1983, 1995
        source = f"~{start}-{end}"
        target = f"{start}\u81f3{end}\u5e74\u95f4"
        self.assertNotIn("numbers", self.codes(source, target))
        self.assertIn("numbers", self.codes(source, target.replace(str(end), str(end + 1))))
        self.assertIn("numbers", self.codes(f"{start}-{end} years", target))
        self.assertIn("literal-inline-code", self.codes(f"`{source}`", f"`{target}`"))

    def test_day_ordinals_are_not_durations_or_daily_counts(self):
        day = 8
        target = f"\u7b2c {day} \u5929"
        self.assertNotIn("numbers", self.codes(f"On day {day}.", target))
        self.assertIn("numbers", self.codes(f"On day {day}.", target.replace("8", "9")))
        self.assertIn("numbers", self.codes(f"Wait {day} days.", target))
        self.assertIn("numbers", self.codes(f"Each day {day} items arrive.", target))
        self.assertIn("literal-inline-code", self.codes(f"`Day {day}`", f"`{target}`"))

    def test_quantity_ranges_preserve_units_endpoints_and_open_bounds(self):
        tick = chr(96)
        for original, local, changes in [
            ("7-12x", "7\u201312 \u500d", ("8\u201312 \u500d", "7\u201313 \u500d", "7\u201312", "7\u201312 \u79d2")),
            ("8-16ms", "8\u81f316 \u6beb\u79d2", ("8\u81f316 \u79d2", "8 16 \u6beb\u79d2")),
            ("6-14+ seconds", "6\u201314 \u79d2\u6216\u66f4\u4e45",
             ("6\u201314 \u79d2", "6\u201315+ \u79d2", "6\u201314+ \u6beb\u79d2")),
            ("9\u201318x", "9-18 \u500d", ("9-18 \u00d7 2", "9-18+ \u500d")),
        ]:
            with self.subTest(original=original):
                self.assertNotIn("numbers", self.codes(original, local))
                self.assertIn("literal-inline-code", self.codes(f"{tick}{original}{tick}", f"{tick}{local}{tick}"))
                for changed in changes:
                    self.assertIn("numbers", self.codes(original, changed))

    def test_change_in_value_or_version_is_not_an_interval(self):
        for low, high in [("64", "16"), ("0.6", "0.9")]:
            with self.subTest(low=low, high=high):
                self.assertIn("numbers", self.codes(f"Change from {low} to {high}.\n", f"{low}\u2013{high}\n"))
                self.assertNotIn("numbers", self.codes(f"Change from {low} to {high}.\n", f"{low} {generated_cjk(2)} {high}\n"))

    def test_standalone_open_duration_preserves_bound_and_unit(self):
        source = "12+ minutes"
        for equivalent in ("12 \u5206\u949f\u6216\u66f4\u4e45", "12\u5206\u949f\u4ee5\u4e0a"):
            self.assertNotIn("numbers", self.codes(source, equivalent))
            self.assertIn("literal-inline-code", self.codes(f"`{source}`", f"`{equivalent}`"))
        for changed in ("12 \u5206\u949f", "13+ minutes", "12+ seconds", "12"):
            self.assertIn("numbers", self.codes(source, changed))

    def test_token_ranges_preserve_counts_units_and_open_end(self):
        source = "Usually 2,500-3,500+ tokens."
        for value in ("2500-3500\u591a\u4e2a token", "2,500\u81f33,500 \u4e2a token\u6216\u66f4\u591a"):
            self.assertNotIn("numbers", self.codes(source, value))
        for value in ("2500-3500 \u4e2a token", "2500-3600+ tokens", "2500-3500+ words"):
            self.assertIn("numbers", self.codes(source, value))

    def test_multiplication_is_not_a_multiplier_suffix(self):
        self.assertIn("numbers", self.codes("2x 3\n", "2 \u00d7 3\n"))

    def test_explicit_magnitudes_and_thousands_grouping_compare_exactly(self):
        for original, local, changed in [
            ("10 million", "1000 \u4e07", "100 \u4e07"),
            ("1.25 billion", "12.5 \u4ebf", "12.6 \u4ebf"),
            ("5,000", "5000", "500"),
            ("2 million", "2,000,000", "2,000,001"),
        ]:
            with self.subTest(original=original):
                self.assertNotIn("numbers", self.codes(f"Count: {original}.\n", generated_cjk(4) + f" {local}\n"))
                self.assertIn("numbers", self.codes(f"Count: {original}.\n", generated_cjk(4) + f" {changed}\n"))
                self.assertIn("literal-inline-code", self.codes(f"`{original}`\n", f"`{local}`\n"))

    def test_image_counts_compare_values_and_require_pixel_units(self):
        for original, equivalent, wrong in [
            ("13.5 megapixels", "1350 \u4e07\u50cf\u7d20", "1351 \u4e07\u50cf\u7d20"),
            ("17 million pixels", "1700 \u4e07\u50cf\u7d20", "1700 \u4e07"),
            ("7,525 pixels", "7525 \u50cf\u7d20", "7525"),
            ("2 pixels", "2 \u50cf\u7d20", "2 \u4e07\u50cf\u7d20"),
        ]:
            with self.subTest(original=original):
                self.assertNotIn("numbers", self.codes(original, generated_cjk(2) + equivalent))
                self.assertIn("numbers", self.codes(original, generated_cjk(2) + wrong))
                self.assertIn("literal-inline-code", self.codes(f"`{original}`", f"`{equivalent}`"))

    def test_percentile_is_not_a_percentage_or_plain_number(self):
        source = "At the 91.3rd percentile."
        local = "\u7b2c 91.3 \u767e\u5206\u4f4d"
        self.assertNotIn("numbers", self.codes(source, local))
        for changed in (local.replace("91.3", "90.3"), "91.3%", "91.3"):
            self.assertIn("numbers", self.codes(source, changed))
        self.assertIn("literal-inline-code", self.codes("`91.3rd percentile`", f"`{local}`"))

    def test_plural_http_status_is_not_a_duration(self):
        source = "The client receives empty responses or 502s."
        target = f"{generated_cjk(8)} 502"
        self.assertNotIn("numbers", self.codes(source, target))
        self.assertIn("numbers", self.codes(source, target.replace("502", "503")))
        self.assertIn("numbers", self.codes("It times out in 502s.", target))
        self.assertIn("numbers", self.codes("Run requests in batches for 502s.", target))

    def test_advisory_ids_in_titles_are_literals_not_english(self):
        for advisory in ("CVE-2099-12345", "GHSA-abcd-1234-wxyz"):
            with self.subTest(advisory=advisory):
                source = f'---\ntitle: "{advisory}"\n---\n\n# {advisory}\n'
                self.assertFalse({"untranslated-heading", "untranslated-metadata"} & self.codes(source, source))
                self.assertIn("literal-identifier", self.codes(source, source.replace(advisory, generated_cjk(4))))
                self.assertEqual([s.value for s in mask(advisory, self.terms)[1]], [advisory])
                label = f"# {advisory} disclosure notice\n"
                self.assertIn("untranslated-heading", self.codes(label, label))

    def test_equivalent_list_marker_padding_and_spelling(self):
        source = "-   First item\n-   Second item\n\n1.  One item\n2.  Two items\n\n--- \n"
        target = self.translate(source).replace("-   ", "* ").replace("1.  ", "1) ").replace("2.  ", "2) ").replace("--- \n", "---\n")
        self.assertFalse({"markdown-marker", "markdown-structure"} & self.codes(source, target))
        self.assertIn("markdown-marker", self.codes(source, target.replace("1) ", "3) ")))
        self.assertIn("markdown-structure", self.codes(source, target.replace("* ", "", 1)))

    def test_ordered_list_normalizes_later_numbers_without_changing_start(self):
        source = "3. First step\n8. Second step\n1. Third step\n"
        target = self.translate(source).replace("8. ", "4. ").replace("1. ", "5. ")
        self.assertFalse({"markdown-marker", "markdown-structure"} & self.codes(source, target))
        self.assertIn("markdown-structure", self.codes(source, target.replace("3. ", "1. ")))
        self.assertIn("markdown-marker", self.codes(source, "3. " + generated_cjk(5) + "\n"))

    def test_exception_expires_when_either_document_changes(self):
        source = "Source prose with enough words to trigger English review.\n"
        self.put(self.source, "a.md", source)
        target_path = self.put(self.target, "a.md", source)
        report = verify(self.source, self.target, self.config)
        fingerprints = [i["fingerprint"] for i in report["issues"]]
        self.config["exceptions"] = [{"fingerprint": p, "reason": "Synthetic test exception"} for p in fingerprints]
        self.assertEqual(verify(self.source, self.target, self.config)["summary"]["warnings"], 0)
        target_path.write_text(source + "\n", encoding="utf-8")
        self.assertGreater(verify(self.source, self.target, self.config)["summary"]["warnings"], 0)

    def test_review_bundle_has_complete_pairs_and_hashes(self):
        source = "# Source heading\n\nSource body.\n"
        self.put(self.source, "a.md", source)
        self.put(self.target, "a.md", self.translate(source))
        bundle = review_bundle(self.source, self.target, self.config, [])
        self.assertEqual(bundle["files"][0]["source"], source)
        self.assertEqual(bundle["files"][0]["source_sha256"], digest(source))
        self.assertEqual(bundle["deterministic_report"]["quality"]["semantic_review"], "required")

    def test_cli_strict_exit_code(self):
        source = "Source prose with enough words to trigger English review.\n"
        self.put(self.source, "a.md", source)
        self.put(self.target, "a.md", source)
        args = ["--source", str(self.source), "--target", str(self.target)]
        with patch("sys.stdout", new=io.StringIO()):
            self.assertEqual(check_main(args), 0)
            self.assertEqual(check_main(args + ["--strict"]), 1)

    def test_missing_pinned_source_explains_submodule_setup(self):
        missing_source = self.root / "en-us/docs"
        error = io.StringIO()
        with patch("translation_tools.verify.ROOT", self.root), redirect_stderr(error):
            self.assertEqual(check_main(["--source", str(missing_source), "--target", str(self.target)]), 2)
        self.assertIn("git submodule update --init -- en-us", error.getvalue())

    def test_imports_scripts_and_fence_metadata_are_literal(self):
        for source, target, code in [
            ("import Source from 'module';\n", "import Changed from 'module';\n", "opaque-code-changed"),
            ('<script>{"literal": 3}</script>\n', '<script>{"literal": 4}</script>\n', "opaque-code-changed"),
            ("```python\nrun()\n```\n", "```javascript\nrun()\n```\n", "fence-structure"),
        ]:
            self.assertIn(code, self.codes(source, target))

    def issues(self, source, target, path="fixture.mdx", suffix=".mdx"):
        return compare(path, Document(source, suffix, self.terms), Document(target, suffix, self.terms), self.config)

    def test_keyword_lists_in_source_language_are_not_prose_findings(self):
        source = '---\ntitle: "Source"\nkeywords: ["OpenAI API reference", "second keyword phrase here"]\n---\n\nThis paragraph has several english words that differ from the translation.\n'
        target = source.replace('title: "Source"', ('title: "' + generated_cjk(2) + '"')).replace(
            "This paragraph has several english words that differ from the translation.",
            (generated_cjk(18) + '。'))
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("untranslated-metadata", codes)
        self.assertNotIn("unchanged-prose", codes)

    def test_keyword_lists_do_not_trigger_copied_section_prose(self):
        source = '---\nkeywords: ["One two three four five six seven eight nine."]\n---\n\nSource body.\n'
        target = source.replace("Source body.", generated_cjk(4) + ".")
        self.assertNotIn("copied-sentence", self.codes(source, target))

    def test_literal_recount_is_a_review_signal_not_a_failure(self):
        source = "Use OpenAI once for the source task.\n"
        target = (generated_cjk(2) + ' OpenAI ' + generated_cjk(5) + '，' + generated_cjk(6) + ' OpenAI ' + generated_cjk(4) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "literal-term"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "warning")

    def test_singular_and_plural_acronyms_preserve_prose_term_not_code_spelling(self):
        target = generated_cjk(6)
        self.assertNotIn("literal-term", self.codes("These APIs work.\n", f"{target} API\n"))
        self.assertIn("literal-term", self.codes("These APIs work.\n", target))
        self.assertIn("literal-inline-code", self.codes("Use `APIs`.\n", f"{target} `API`\n"))

    def test_dropped_literal_is_still_a_failure(self):
        source = "Use `OPENAI_TOKEN` for the source task.\n"
        target = (generated_cjk(9) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "literal-inline-code"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "error")

    def test_inline_code_substitution_detected_even_if_original_id_survives_elsewhere(self):
        current, stale = "example-engine-2026", "earlier-engine-release"
        title = generated_cjk(4)
        prose = generated_cjk(10)
        source = (f"Use `{current}` in the setup screen.\n\n"
                  f"## Retry\n\nSelect `{current}` manually when the request fails.\n")
        target = f"{prose} `{current}`\n\n## {title} {{#retry}}\n\n{prose} `{stale}`\n"
        code = "literal-inline-code-substitution"
        found = [i for i in self.issues(source, target) if i.code == code]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].severity, "warning")
        self.assertEqual({d.anchor for d in found[0].section_drift}, {"retry"})
        self.assertEqual({d.token for d in found[0].section_drift}, {f"`{current}`", f"`{stale}`"})
        self.assertNotIn(code, self.codes(source, target + f"\n{prose} `{current}`\n"))
        other_section = target.replace(f"`{stale}`", "") + f"\n## {title} {{#elsewhere}}\n\n`{stale}`\n"
        self.assertNotIn(code, self.codes(source, other_section))

    def test_relative_and_absolute_destinations_compare_equal(self):
        source = "See [guide](/guide) for details.\n"
        target = "See [guide](../guide) for details.\n"
        codes = {i.code for i in self.issues(source, target, path="features/page.mdx")}
        self.assertNotIn("literal-destination", codes)

    def test_upstream_self_link_localized_to_local_path(self):
        source = "See [guide](https://docs.openwebui.com/guide) for details.\n"
        target = "See [guide](/guide) for details.\n"
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("literal-destination", codes)
        self.assertNotIn("literal-url", codes)

    def test_url_surviving_as_inline_code_is_not_missing(self):
        source = "Use https://example.com/path in the source text.\n"
        target = (generated_cjk(6) + ' `https://example.com/path`。\n')
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("literal-url", codes)

    def test_bare_url_can_become_one_link_without_allowing_new_destinations(self):
        url = "https://example.test/guide"
        source = f"See {url}.\n"
        link = f"[{generated_cjk(3)}]({url})"
        self.assertNotIn("literal-destination", self.codes(source, link))
        self.assertIn("markdown-symbol", self.codes(source, link))
        self.assertIn("literal-destination", self.codes(source, link + " " + link))
        self.assertIn("literal-destination", self.codes(source, source + link))
        self.assertIn("literal-destination", self.codes(source, link.replace("/guide", "/other")))
        self.assertIn("literal-url", self.codes(source, link.replace("/guide", "/other")))

    def test_document_suffix_is_stripped_completely(self):
        source = "See [policy](/security/security-policy.md) for details.\n"
        target = "See [policy](/security/security-policy) for details.\n"
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("literal-destination", codes)

    def test_interface_label_may_be_translated(self):
        source = "Open the `Settings` panel and check `Admin Panel`.\n"
        target = (generated_cjk(2) + ' `' + generated_cjk(2) + '` ' + generated_cjk(5) + ' `' + generated_cjk(4) + '`。\n')
        found = [i for i in self.issues(source, target) if i.code == "ui-label-translated"]
        self.assertTrue(found)
        self.assertTrue(all(i.severity == "info" for i in found))
        self.assertNotIn("literal-inline-code", self.codes(source, target))

    def test_compound_labels_are_only_relaxed_in_ui_actions(self):
        for label in ("Settings > Documents", "Clear Cache/Storage"):
            with self.subTest(label=label):
                target = generated_cjk(12) + "\n"
                ui = f"Click `{label}` in the panel.\n"
                literal = f"The literal value is `{label}`.\n"
                for source, severity in [(ui, "info"), (literal, "error"), (ui + literal, "error")]:
                    findings = [i.severity for i in self.issues(source, target)
                                if i.code in {"literal-inline-code", "ui-label-translated"}]
                    self.assertEqual(findings, [severity])

    def test_empty_default_gloss_can_move_but_value_cannot(self):
        source = '#### `EXAMPLE_KEY`\n\n- Type: `str`\n- Default: `("") empty string`\n'
        local = self.translate(source).replace('`("") empty string`', '`("")` ' + generated_cjk(4))
        self.assertFalse({"literal-inline-code", "setting-default"} & self.codes(source, local))
        changed = local.replace('`("")`', '`("value")`') + '\nAnother value: `("")`.\n'
        self.assertIn("setting-default", self.codes(source, changed))
        self.assertIn("literal-inline-code", self.codes('Run `("") empty string`.\n', 'Run `("")`.\n'))

    def test_inline_identifier_period_requires_source_spelling_and_target_count(self):
        clean = "`sample_engine`"
        punctuated = "`sample_engine.`"
        prefix = generated_cjk(4)
        source = f"Use {clean} for this service. Select {punctuated} Next select the mode.\n"
        target = f"{prefix} {clean} {prefix} {clean}.\n"
        self.assertNotIn("literal-inline-code", self.codes(source, target))
        self.assertIn("literal-inline-code", self.codes(source, f"{prefix} {clean}.\n"))
        self.assertIn("literal-inline-code", self.codes(f"Select {punctuated}\n", target))
        self.assertIn("literal-inline-code", self.codes(source, target.replace(clean, "`other_engine`")))

    def test_source_term_alias_does_not_change_inline_code_or_keys(self):
        self.config["source_term_aliases"] = {"oepnAI": "OpenAI"}
        prefix = generated_cjk(4)
        self.assertNotIn("literal-identifier", self.codes("Use oepnAI.\n", f"{prefix} OpenAI.\n"))
        self.assertIn("literal-identifier", self.codes("Use oepnAI.\n", prefix))
        self.assertIn("literal-inline-code", self.codes("Use `oepnAI`.\n", f"{prefix} `OpenAI`.\n"))
        self.assertIn("literal-identifier", self.codes("Use oepnAI_KEY.\n", f"{prefix} OpenAI.\n"))

    def test_english_headings_and_metadata_have_single_language_findings_each(self):
        prose_text = "Some English words that still need translation"
        source = f'---\ntitle: "{prose_text}"\n---\n\n## {prose_text}\n'
        findings = [i.code for i in self.issues(source, source) if i.code.startswith(("untranslated", "unchanged"))]
        self.assertCountEqual(findings, ["untranslated-heading", "untranslated-metadata"])

    def test_identifier_code_span_still_required(self):
        source = "Set `OPENAI_TOKEN` for the source task.\n"
        target = (generated_cjk(9) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "literal-inline-code"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "error")

    def test_fence_title_may_be_translated(self):
        source = '```bash title="Start the Docker Compose Project Here"\necho start\n```\n\nProse about the command.\n'
        target = ('```bash title="' + generated_cjk(2) + ' Docker Compose ' + generated_cjk(2) + '"\necho start\n```\n\n' + generated_cjk(8) + '。\n')
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("fence-structure", codes)

    def test_fence_language_must_match(self):
        source = '```bash\necho start\n```\n\nProse about the command.\n'
        target = ('```python\necho start\n```\n\n' + generated_cjk(8) + '。\n')
        codes = {i.code for i in self.issues(source, target)}
        self.assertIn("fence-structure", codes)

    def test_untranslated_fence_title_is_a_warning(self):
        source = '```bash title="Start the Docker Compose Project Here"\necho start\n```\n\nProse about the command.\n'
        target = ('```bash title="Start the Docker Compose Project Here"\necho start\n```\n\n' + generated_cjk(8) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "untranslated-prose"]
        self.assertTrue(found)
        self.assertTrue(all(i.severity == "warning" for i in found))

    def test_fence_title_excludes_terminology_from_language_check(self):
        source = '```bash title="Open WebUI Docker OpenAI Python"\nrun\n```\n'
        found = [i for i in self.issues(source, source) if i.code == "untranslated-prose"]
        self.assertEqual(found, [])

    def test_repaired_upstream_fence_is_a_warning(self):
        source = "Run ```sudo dnf install haproxy``` to install it.\n\nProse about the installation.\n"
        target = ('```bash\nsudo dnf install haproxy\n```\n\n' + generated_cjk(7) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "fence-structure"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "warning")
        self.assertNotIn("literal-inline-code", {i.code for i in self.issues(source, target)})
        code = [i for i in self.issues(source, target) if i.code == "code-changed"]
        self.assertEqual([i.severity for i in code], ["warning"])

    def test_unrelated_source_defect_does_not_relax_code_preservation(self):
        source = "```sh\nsource_command\n```\n\n:::\n"
        target = source.replace("source_command", "changed_command").replace("\n:::\n", "\n")
        found = [i for i in self.issues(source, target) if i.code == "code-changed"]
        self.assertEqual([i.severity for i in found], ["error"])

    def test_fence_repair_requires_a_new_block_with_the_exact_inline_sample(self):
        source = "Run ```source_command --flag```.\n\n```sh\nold_block\n```\n"
        target = "```sh\nsource_command --changed\n```\n\n```sh\nold_block\n```\n"
        for candidate in (target, target.split("\n\n")[1]):
            found = [i for i in self.issues(source, candidate) if i.code == "literal-inline-code"]
            self.assertEqual([i.severity for i in found], ["error"])
        self.assertNotIn("literal-inline-code", self.codes(source, target.replace("--changed", "--flag")))
        same_block = source.replace("old_block", "source_command --flag")
        self.assertIn("literal-inline-code", self.codes(same_block, same_block.split("\n\n")[1]))

    def test_backticks_cannot_join_adjacent_list_items(self):
        source = "- Remove ````alpha` prefix\n- Remove ```` suffix\n"
        target = f"- {generated_cjk(3)} ````alpha`\n- {generated_cjk(4)} ````\n"
        self.assertNotIn("literal-inline-code", self.codes(source, target))
        source = "- `value\n  continued`\n- Another item\n"
        self.assertIn("literal-inline-code", self.codes(source, source.replace("continued", "changed")))

    def test_policy_removed_link_may_be_dropped(self):
        source = "- [Community](https://discord.gg/abcdef) for support.\n"
        target = ('- ' + generated_cjk(7) + '。\n')
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("literal-destination", codes)
        self.assertNotIn("markdown-symbol", codes)

    def test_policy_contact_row_can_be_removed_without_hiding_other_table_changes(self):
        header = "| Channel | Link |\n| --- | --- |\n"
        excluded = "| **Discord** | [discord.gg/test](https://discord.gg/test) |\n"
        required = "| **Guide** | [Guide](https://example.test/) |\n"
        localized = f"| **{generated_cjk(3)}** | [{generated_cjk(3)}](https://example.test/) |\n"
        source = header + excluded + required
        self.assertFalse({"markdown-structure", "markdown-symbol", "literal-destination"} &
                         self.codes(source, header + localized))
        self.assertIn("markdown-structure", self.codes(source, header))
        self.assertIn("literal-destination", self.codes(source, header))
        self.assertIn("markdown-symbol", self.codes(source, header + localized.replace("**", "")))
        for ineligible in (
            excluded.replace("**Discord**", "**Required setup**"),
            excluded.replace("[discord.gg/test]", "[Read the setup guide]"),
            excluded.rstrip() + " required action |\n",
        ):
            self.assertIn("markdown-structure", self.codes(header + ineligible + required, header + localized))

    def test_policy_links_do_not_exempt_other_symbol_or_destination_changes(self):
        link = "[Community](https://discord.gg/abcdef)"
        ordinary = "[Guide](https://example.test/)"
        text = generated_cjk(8)
        self.assertIn("markdown-symbol", self.codes(f"{link} **Example prose** and {ordinary}\n", f"{text} {ordinary}\n"))
        self.assertIn("literal-destination", self.codes(f"{link} alongside {ordinary}\n", text))
        self.assertIn("markdown-symbol", self.codes(r"\[Unlinked](https://discord.gg/abcdef)" + "\n", text))

    def test_policy_removed_link_still_reported_when_target_keeps_it(self):
        source = "- [Community](https://discord.gg/abcdef) for support.\n"
        target = ('- [' + generated_cjk(2) + '](https://discord.gg/abcdef) ' + generated_cjk(4) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "non-compliant-link"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "error")

    def test_code_span_in_removed_paragraph_may_disappear(self):
        source = "- [Community](https://discord.gg/abcdef) channel `#support`.\n"
        target = ('- ' + generated_cjk(7) + '。\n')
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("literal-inline-code", codes)

    def test_code_span_outside_removed_paragraph_still_required(self):
        source = "- [Community](https://discord.gg/abcdef) channel `#support`.\n\nAlso `#support`.\n"
        target = ('- ' + generated_cjk(7) + '。\n\n' + generated_cjk(6) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "literal-inline-code"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "error")

    def test_json_ld_prose_may_be_translated_but_structure_may_not_change(self):
        payload = '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Source question","acceptedAnswer":{"@type":"Answer","text":"Source answer text."}}]}'
        script = '<script type="application/ld+json">{JSON.stringify(' + payload + ')}</script>\n'
        translated = script.replace("Source question", "translated question").replace("Source answer text.", "translated answer text.")
        self.assertNotIn("opaque-code-changed", {i.code for i in self.issues(script, translated)})
        shortened = translated.replace('{"@type":"Question","name":"translated question","acceptedAnswer":{"@type":"Answer","text":"translated answer text."}}', "")
        self.assertIn("opaque-code-changed", {i.code for i in self.issues(script, shortened)})

    def test_upstream_parse_defect_is_reported_as_warning(self):
        source = "Body text.\n\n:::\n"
        target = (generated_cjk(4) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "source-parse"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "warning")

    def test_source_defect_downgrades_structural_findings(self):
        source = "# Source\n\n:::\n"
        target = ('# ' + generated_cjk(2) + '\n')
        found = [i for i in self.issues(source, target) if i.code == "heading-structure"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "warning")

    def test_section_heading_swallowed_by_upstream_fence_is_restored(self):
        source = "```bash\nrun()\n\n## Section Title\n\nBody.\n\n```\n"
        target = ('```bash\nrun()\n```\n\n## ' + generated_cjk(4) + ' {#section-title}\n\n' + generated_cjk(2) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "heading-structure"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "warning")

    def test_layout_metadata_may_differ(self):
        source = '---\nsidebar_position: 10\ntitle: "Source"\n---\n\nBody prose for the source.\n'
        target = ('---\nsidebar_position: 3\ntitle: "' + generated_cjk(2) + '"\n---\n\n' + generated_cjk(4) + '。\n')
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("metadata-literal", codes)

    def test_admonition_types_may_differ_but_their_count_may_not(self):
        source = "Body.\n\n:::tip\n\nTip body.\n\n:::\n"
        target = (generated_cjk(2) + '。\n\n:::info\n\n' + generated_cjk(4) + '。\n\n:::\n')
        found = [i for i in self.issues(source, target) if i.code == "admonition-structure"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "warning")
        longer = source + "\n:::danger\n\nMore.\n\n:::\n"
        found = [i for i in self.issues(longer, target) if i.code == "admonition-structure"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "error")

    def review_result(self):
        source = "# Source heading\n\nSource body.\n"
        self.put(self.source, "a.md", source)
        self.put(self.target, "a.md", self.translate(source))
        return review_bundle(self.source, self.target, self.config, [])["result_format"]

    def test_semantic_review_requires_all_dimensions_and_full_read(self):
        results = self.review_result()
        self.assertEqual(validate_review(results, self.source, self.target, [])["semantic_review"], "needs-review")
        entry = results["files"][0]
        for key in ["completeness", "accuracy", "fluency", "terminology"]:
            entry[key] = "pass"
        self.assertEqual(validate_review(results, self.source, self.target, [])["semantic_review"], "needs-review")
        entry["reviewed_all_sections"] = True
        self.assertEqual(validate_review(results, self.source, self.target, [])["semantic_review"], "passed")

    def test_installed_audit_rejects_review_without_config_digest(self):
        results = self.review_result()
        del results["config_sha256"]
        with self.assertRaisesRegex(ValueError, "unbound"):
            verify(self.source, self.target, self.config, review_results=results)

    def test_exception_only_change_reuses_reviews_but_reaudits_current_findings(self):
        source = "# Source heading\n\nSource body.\n"
        self.put(self.source, "a.md", source)
        self.put(self.target, "a.md", self.translate(source))
        self.put(self.source, "b.md", source)
        self.put(self.target, "b.md", self.translate(source))
        self.put(self.source, "c.md", source)
        self.put(self.target, "c.md", self.translate(source))
        self.put(self.source, "d.md", source + "Visit https://example.org/guide.\n")
        self.put(self.target, "d.md", self.translate(source))
        found = verify(self.source, self.target, self.config, ["d.md"])
        fingerprint = next(i["fingerprint"] for i in found["issues"] if i["code"] == "literal-url")
        previous_config = dict(self.config, exceptions=[{"fingerprint": fingerprint, "reason": "Synthetic waiver"}])
        previous = review_bundle(self.source, self.target, previous_config, [])["result_format"]
        for row in previous["files"][:2]:
            row.update(reviewed_all_sections=True, **dict.fromkeys(REVIEW_DIMENSIONS, "pass"))
        self.put(self.target, "b.md", self.translate(source) + "\n")

        unbound = review_bundle(self.source, self.target, self.config, [], previous=previous)
        self.assertEqual(unbound["reused_files"], [])
        current = review_bundle(self.source, self.target, self.config, [],
                                previous=previous, previous_config=previous_config)
        self.assertEqual(current["reused_files"], ["a.md"])
        self.assertEqual([row["path"] for row in current["files"]], ["b.md", "c.md", "d.md"])
        self.assertNotEqual(current["result_format"]["config_sha256"], previous["config_sha256"])
        self.assertTrue(any(i["fingerprint"] == fingerprint and not i["suppressed"]
                            for i in current["deterministic_report"]["issues"]))
        with self.assertRaisesRegex(ValueError, "does not match"):
            review_bundle(self.source, self.target, self.config, [],
                          previous=previous, previous_config=self.config)
        changed_policy = dict(self.config, terms=self.config["terms"] + ["Sample Product"])
        with self.assertRaisesRegex(ValueError, "non-exception"):
            review_bundle(self.source, self.target, changed_policy, [],
                          previous=previous, previous_config=previous_config)

    def test_semantic_review_rejects_stale_missing_duplicate_and_bad_status(self):
        initial = self.review_result()
        for change in ["stale", "missing", "duplicate", "status"]:
            results = deepcopy(initial)
            if change == "stale":
                results["files"][0]["source_sha256"] = "0" * 64
            elif change == "missing":
                results["files"] = []
            elif change == "duplicate":
                results["files"] *= 2
            else:
                results["files"][0]["accuracy"] = "unknown"
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_review(results, self.source, self.target, [])

    def test_semantic_findings_block_pass(self):
        results = self.review_result()
        entry = results["files"][0]
        entry["reviewed_all_sections"] = True
        for key in ["completeness", "accuracy", "fluency", "terminology"]:
            entry[key] = "pass"
        entry["findings"] = [{"line": 3, "source_evidence": "Source body.", "message": "Synthetic review finding"}]
        self.assertEqual(validate_review(results, self.source, self.target, [])["semantic_review"], "needs-review")


class QuoteEvidenceTests(Fixture):
    """Upstream quotes reproduced verbatim are evidence, not untranslated prose."""

    def test_verbatim_upstream_quote_is_not_reported_as_untranslated(self):
        quote = "> The scanner reports a denial of service condition on the upstream host.\n"
        source = "## Findings\n\n" + quote
        target = "## \u7ed3\u8bba\n\n" + quote
        codes = self.codes(source, target)
        self.assertNotIn("untranslated-prose", codes)
        self.assertNotIn("copied-sentence", codes)

    def test_english_prose_outside_an_upstream_quote_is_still_reported(self):
        source = "## Findings\n\nThe scanner reports a denial of service condition on the host.\n"
        target = "## \u7ed3\u8bba\n\nThe scanner reports a denial of service condition on the host.\n"
        codes = self.codes(source, target)
        self.assertIn("untranslated-prose", codes)

    def test_quote_that_upstream_does_not_quote_is_still_reported(self):
        quoted = "> The scanner reports a denial of service condition on the upstream host.\n"
        source = "## Findings\n\nThe scanner reports a denial of service condition on the host.\n"
        target = "## \u7ed3\u8bba\n\n" + quoted
        codes = self.codes(source, target)
        self.assertIn("untranslated-prose", codes)


class UpdateTests(Fixture):
    def test_autonomous_prepare_no_config_or_network(self):
        self.put(self.source, "a.md", "# Source heading\n\nSource body paragraph.\n")
        with patch("urllib.request.build_opener", side_effect=AssertionError("Network forbidden")), patch.dict("os.environ", {}, clear=True):
            bundle = self.fill(prepare(self.source, self.target, self.config, []))
            apply_bundle(bundle, self.source, self.target, self.config, write=True)
        self.assertTrue((self.target / "a.md").exists())

    def test_default_apply_does_not_write(self):
        self.put(self.source, "a.md", "Source body paragraph.\n")
        bundle = self.fill(prepare(self.source, self.target, self.config, []))
        apply_bundle(bundle, self.source, self.target, self.config)
        self.assertFalse((self.target / "a.md").exists())

    def test_stale_target_source_or_config_rejected(self):
        src = self.put(self.source, "a.md", "Source body paragraph.\n")
        dst = self.put(self.target, "a.md", "Previous target bytes.\n")
        for change in ["target", "source", "config"]:
            with self.subTest(change=change):
                bundle = self.fill(prepare(self.source, self.target, self.config, []))
                config = deepcopy(self.config)
                if change == "target":
                    dst.write_text("Edited bytes " + change, encoding="utf-8")
                elif change == "source":
                    src.write_text("Edited bytes " + change, encoding="utf-8")
                else:
                    config["terms"].append("ExtraTerm")
                with self.assertRaises(ValueError):
                    apply_bundle(bundle, self.source, self.target, config, True)

    def test_invalid_batch_writes_nothing(self):
        for name in ["a.md", "b.md"]:
            self.put(self.source, name, "Source body paragraph with `literal`.\n")
        bundle = self.fill(prepare(self.source, self.target, self.config, []))
        bundle["files"][1]["segments"][0]["translation"] = ""
        with self.assertRaises(ValueError):
            apply_bundle(bundle, self.source, self.target, self.config, True)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_unchanged_english_not_complete(self):
        self.put(self.source, "a.md", "Source body paragraph.\n")
        bundle = prepare(self.source, self.target, self.config, [])
        for s in bundle["files"][0]["segments"]:
            s["translation"] = s["source"]
        with self.assertRaises(ValueError):
            apply_bundle(bundle, self.source, self.target, self.config, True)

    def test_preserve_crlf_and_bom(self):
        self.put(self.source, "a.md", "Source body paragraph.\n")
        dst = self.put(self.target, "a.md", "\ufeffPrevious target.\r\n")
        bundle = self.fill(prepare(self.source, self.target, self.config, []))
        apply_bundle(bundle, self.source, self.target, self.config, True)
        raw = dst.read_bytes()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
        self.assertTrue(raw.endswith(b"\r\n"))

    def test_path_traversal_rejected(self):
        self.put(self.source, "a.md", "Source body paragraph.\n")
        for path in ["../outside.md", "nested/../../outside.md", "C:/outside.md", "a\\b.md"]:
            bundle = prepare(self.source, self.target, self.config, [])
            bundle["files"][0]["path"] = path
            with self.subTest(path=path), self.assertRaises(ValueError):
                apply_bundle(bundle, self.source, self.target, self.config, True)

    def test_source_target_same_directory_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.source, self.source, self.config, [])

    def test_failed_second_write_rolls_back_first(self):
        from translation_tools.update import atomic_write
        for name in ["a.md", "b.md"]:
            self.put(self.source, name, "Source body paragraph.\n")
            self.put(self.target, name, "Previous bytes.\n")
        bundle = self.fill(prepare(self.source, self.target, self.config, []))
        calls = 0
        def failing_write(path, raw):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("Synthetic write failure")
            atomic_write(path, raw)
        with patch("translation_tools.update.atomic_write", side_effect=failing_write), self.assertRaises(OSError):
            apply_bundle(bundle, self.source, self.target, self.config, True)
        for path in self.target.iterdir():
            self.assertEqual(path.read_bytes(), b"Previous bytes.\n")


class Response:
    def __init__(self, value):
        self.value = value
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return json.dumps(self.value).encode("utf-8")


class DeepLTests(Fixture):
    def test_mock_provider_output_uses_shared_validated_apply_path(self):
        import xml.etree.ElementTree as ET
        from unittest.mock import Mock
        self.put(self.source, "a.md", "# Source heading\n\nUse OpenAI with `literal_command` for source work.\n")
        bundle = prepare(self.source, self.target, self.config, [])
        opener = Mock()
        def respond(request, timeout):
            payload = json.loads(request.data)
            self.assertNotIn("OpenAI", json.dumps(payload["text"]))
            self.assertNotIn("literal_command", json.dumps(payload["text"]))
            outputs = []
            for value in payload["text"]:
                root = ET.fromstring(value)
                root.text = generated_text(root.text or "")
                for keep in root:
                    keep.tail = generated_text(keep.tail or "")
                outputs.append({"text": ET.tostring(root, encoding="unicode")})
            return Response({"translations": outputs})
        opener.open.side_effect = respond
        DeepL("synthetic:fx", opener=opener).fill(bundle)
        apply_bundle(bundle, self.source, self.target, self.config, True)
        self.assertIn("OpenAI", (self.target / "a.md").read_text(encoding="utf-8"))

    def test_only_env_key_needed_and_not_executed(self):
        path = self.put(self.root, ".env", '# Test key\nDEEPL_AUTH_KEY="synthetic:fx"\nOTHER=$(never_execute)\n')
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(load_deepl_key(path), "synthetic:fx")
        self.assertIn("api-free.deepl.com", DeepL("synthetic:fx").endpoint)
        self.assertIn("api.deepl.com", DeepL("synthetic").endpoint)

    def test_missing_key_error_contains_no_secret(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(ValueError):
            load_deepl_key(self.root / "absent")

    def test_example_key_is_rejected_before_request(self):
        path = self.put(self.root, ".env", "DEEPL_AUTH_KEY=your-key\n")
        opener = Mock()
        with (patch.dict("os.environ", {}, clear=True),
              patch("translation_tools.update.load_deepl_key", side_effect=lambda: load_deepl_key(path)),
              self.assertRaisesRegex(ValueError, "Set DEEPL_AUTH_KEY")):
            DeepL(opener=opener).request(["<text>Source</text>"])
        opener.open.assert_not_called()

    def test_xml_escape_and_protected_placeholder_roundtrip(self):
        source = "Source & prose < text ⟦P0⟧ and ⟦P1⟧."
        self.assertEqual(DeepL.xml_decode(DeepL.xml_encode(source), source), source)

    def test_xml_tampering_rejected(self):
        source = "Source ⟦P0⟧."
        original = DeepL.xml_encode(source)
        for bad in [original.replace("P0", "P9"), original.replace('id="0"', 'id="9"'), original.replace("keep", "other"), "<!DOCTYPE text>" + original, "not XML"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                DeepL.xml_decode(bad, source)

    def test_api_batches_and_xml_mode(self):
        from unittest.mock import Mock
        opener = Mock()
        def respond(request, timeout):
            payload = json.loads(request.data)
            self.assertEqual(payload["target_lang"], "ZH-HANS")
            self.assertEqual(payload["ignore_tags"], ["keep"])
            self.assertEqual(payload["tag_handling_version"], "v2")
            self.assertLessEqual(len(payload["text"]), 50)
            self.assertLess(len(request.data), 128 * 1024)
            return Response({"translations": [{"text": t} for t in payload["text"]]})
        opener.open.side_effect = respond
        bundle = {"files": [{"path": "a.md", "segments": [{"id": i, "source": "source ⟦P0⟧", "translation": None}
                                                          for i in range(121)]}]}
        DeepL("synthetic:fx", opener=opener).fill(bundle)
        self.assertEqual(opener.open.call_count, 3)
        self.assertTrue(all(s["translation"] is not None for s in bundle["files"][0]["segments"]))

    def test_auth_error_never_includes_key_or_response_body(self):
        from unittest.mock import Mock
        opener = Mock()
        opener.open.side_effect = urllib.error.HTTPError("https://example.test", 403, "synthetic-secret", {}, io.BytesIO(b"synthetic-secret"))
        with self.assertRaisesRegex(ValueError, r"HTTP 403") as error:
            DeepL("synthetic-secret", opener=opener).request(["<text>source</text>"])
        self.assertNotIn("synthetic-secret", str(error.exception))
        self.assertEqual(opener.open.call_count, 1)

    def test_retry_is_bounded(self):
        from unittest.mock import Mock
        opener, sleep = Mock(), Mock()
        opener.open.side_effect = urllib.error.HTTPError("https://example.test", 429, "limit", {}, None)
        with self.assertRaises(ValueError):
            DeepL("synthetic", opener=opener, sleep=sleep).request(["<text>source</text>"])
        self.assertEqual(opener.open.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_invalid_api_response_rejected(self):
        from unittest.mock import Mock
        for payload in [{"translations": []}, {"translations": [{"text": 42}]}]:
            opener = Mock()
            opener.open.return_value = Response(payload)
            with self.assertRaises(ValueError):
                DeepL("synthetic", opener=opener).request(["<text>source</text>"])

    def test_wrapper_merge_keeps_prose_and_tokens_but_rejects_missing_and_duplicate_tokens(self):
        original = "Source ⟦P0⟧⟦P1⟧ and ⟦P2⟧."
        response = f'<text>{generated_cjk(3)}<keep id="0">⟦P0⟧⟦P1⟧{generated_cjk(2)}⟦P2⟧</keep>.</text>'
        self.assertEqual(PLACEHOLDER.findall(DeepL.xml_decode(response, original)), PLACEHOLDER.findall(original))
        for bad in (response.replace("⟦P2⟧", ""), response.replace("⟦P2⟧", "⟦P2⟧⟦P2⟧"),
                    "<text>⟦P0⟧⟦P1⟧⟦P2⟧.</text>", "<text><other /></text>"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                DeepL.xml_decode(bad, original)

    def test_term_motion_never_moves_markup_or_reorders_inline_code(self):
        raw = "- **Source text** with Open WebUI and `source_key` plus `other_key`."
        source, spans = mask(raw, self.terms)
        by_value = {span.value: token for span, token in zip(spans, PLACEHOLDER.findall(source))}
        translated = generated_text(source)

        def swap(left, right):
            return translated.replace(by_value[left], "\0").replace(by_value[right], by_value[left]).replace("\0", by_value[right])

        reordered = swap("Open WebUI", "`source_key`")
        with self.assertRaises(ValueError):
            unmask(reordered, spans)
        self.assertIn("Open WebUI", unmask(reordered, spans, move_terms=True))
        for invalid in (swap("`source_key`", "`other_key`"), swap("Open WebUI", "- ")):
            with self.assertRaises(ValueError):
                unmask(invalid, spans, move_terms=True)

    def test_linkage_and_emphasis_survive_provider_spacing_and_adjacent_cjk(self):
        raw = "1. **Source label:** Use --source with port 8188 at [source](https://example.test)."
        doc = Document(raw, ".md", self.terms)
        source, _ = mask(raw, self.terms)
        value = generated_text(source).replace("⟦P0⟧", "⟦P0⟧ ").replace("⟦P1⟧", "⟦P1⟧ ")
        value = value.replace("⟦P3⟧", "⟦P3⟧ ").replace("⟦P4⟧", "⟦P4⟧ ").replace("⟦P6⟧⟦P7⟧", "⟦P6⟧ ⟦P7⟧")
        checked = DeepL.checked_text(value, source, doc)
        rendered = doc.render_segment(doc.segments[0], checked, move_terms=True)
        self.assertTrue(rendered.startswith("1. **"))
        self.assertIn("](https://example.test)", rendered)
        self.assertIn("--source", rendered)
        self.assertIn("8188", rendered)


class WorkflowTests(Fixture):
    def invoke(self, main, args, status=0):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = main(["--source", str(self.source), "--target", str(self.target), *map(str, args)])
        self.assertEqual(result, status, stdout.getvalue() + stderr.getvalue())
        return stdout.getvalue(), stderr.getvalue()

    def mark_reviewed(self, result):
        # Simulate review status, not expected Chinese phrasing.
        for entry in result["files"]:
            entry.update(reviewed_all_sections=True, **dict.fromkeys(REVIEW_DIMENSIONS, "pass"))
        return result

    def mock_deepl(self):
        opener = Mock()
        def respond(request, timeout):
            payload = json.loads(request.data)
            if payload.get("tag_handling") != "xml":
                values = [generated_text(t) for t in payload["text"]]
            else:
                values = []
                for text in payload["text"]:
                    root = ET.fromstring(text)
                    root.text = generated_text(root.text or "")
                    for keep in root:
                        keep.tail = generated_text(keep.tail or "")
                    values.append(ET.tostring(root, encoding="unicode"))
            return Response({"translations": [{"text": value} for value in values]})
        opener.open.side_effect = respond
        return opener

    def test_plan_translate_review_apply_and_reuse_after_source_edit(self):
        paragraph = "Use Open WebUI with `literal_code` in the current setup."
        source = "# Source heading\n\n" + (paragraph + "\n\n") * 2
        path = self.put(self.source, "a.md", source)
        bundle, report = self.root / "task.json", self.root / "report.json"
        mode = ["--mode", "deepl", "--files", "a.md"]
        with patch("translation_tools.update.load_deepl_key", side_effect=AssertionError("No key in plan")):
            counts = json.loads(self.invoke(update_main, mode + ["--plan", "--bundle", bundle])[0])
        self.assertFalse(bundle.exists())
        self.assertEqual((counts["pending_segments"], counts["unrequested_texts"], counts["deduplicated_segments"]), (3, 2, 1))
        opener = self.mock_deepl()
        with patch("translation_tools.update.load_deepl_key", return_value="synthetic:fx"), patch("urllib.request.build_opener", return_value=opener):
            self.invoke(update_main, mode + ["--bundle", bundle, "--report", report])
        self.assertEqual(len(json.loads(opener.open.call_args.args[0].data)["text"]), 2)
        candidate = json.loads(report.read_bytes())
        self.assertEqual(candidate["validation"], "passed")
        self.assertEqual(candidate["semantic_review"], "required")
        self.assertFalse((self.target / "a.md").exists())
        reviews = self.root / "reviews.json"
        save_bundle(reviews, self.mark_reviewed(candidate["result_format"]))
        self.invoke(update_main, ["--apply", bundle, "--review-results", reviews, "--write"])
        old_target = (self.target / "a.md").read_bytes()
        self.assertEqual(digest(old_target), candidate["files"][0]["candidate_sha256"])
        self.invoke(check_main, ["--strict", "--files", "a.md", "--review-results", reviews])
        path.write_bytes(source.replace("literal_code", "different_code", 1).encode("utf-8"))
        with patch("translation_tools.update.load_deepl_key", side_effect=AssertionError("No key in plan")):
            counts = json.loads(self.invoke(update_main, mode + ["--plan", "--reuse", bundle])[0])
        self.assertEqual((counts["reused_segments"], counts["unrequested_texts"]), (2, 1))
        opener.reset_mock()
        with patch("translation_tools.update.load_deepl_key", return_value="synthetic:fx"), patch("urllib.request.build_opener", return_value=opener):
            self.invoke(update_main, mode + ["--reuse", bundle, "--bundle", self.root / "next.json"])
        self.assertEqual(len(json.loads(opener.open.call_args.args[0].data)["text"]), 1)
        self.assertEqual((self.target / "a.md").read_bytes(), old_target)

    def test_reuse_does_not_pick_between_conflicting_saved_translations(self):
        self.put(self.source, "a.md", "Source body paragraph.\n\nSource body paragraph.\n")
        previous = self.fill(prepare(self.source, self.target, self.config, []))
        previous["provider"] = "deepl"
        previous["files"][0]["segments"][1]["translation"] = generated_cjk(20)
        fresh = prepare(self.source, self.target, self.config, [])
        docs = validate_task(fresh, self.source, self.target, self.config)
        reuse_completed(fresh, previous, docs, self.config)
        self.assertEqual(translation_plan(fresh, docs)["reused_segments"], 0)

    def test_interrupted_batch_replays_paid_response_without_key_or_request(self):
        self.put(self.source, "a.md", "Source body paragraph.\n")
        task = prepare(self.source, self.target, self.config, [])
        task["provider"] = "deepl"
        docs = validate_task(task, self.source, self.target, self.config)
        bundle = self.root / "task.json"

        def interrupted(value):
            save_bundle(bundle, value)
            if "deepl_response" in value["files"][0]["segments"][0]:
                raise InterruptedError("Interrupted after response save")

        with self.assertRaises(InterruptedError):
            DeepL("synthetic", opener=self.mock_deepl()).fill(task, checkpoint=interrupted, documents=docs)
        pending = json.loads(bundle.read_bytes())["files"][0]["segments"][0]
        self.assertIsNone(pending["translation"])
        self.assertIn("deepl_response", pending)
        with patch("translation_tools.update.load_deepl_key", side_effect=AssertionError("No new requests")):
            self.invoke(update_main, ["--mode", "deepl", "--resume", "--bundle", bundle])
        self.assertIsNotNone(json.loads(bundle.read_bytes())["files"][0]["segments"][0]["translation"])
        self.assertFalse((self.target / "a.md").exists())

    def test_stale_or_tampered_resume_is_rejected_before_network(self):
        path = self.put(self.source, "a.md", "Source body paragraph.\n")
        task = prepare(self.source, self.target, self.config, [])
        task["provider"] = "deepl"
        bundle = self.root / "task.json"
        args = ["--mode", "deepl", "--resume", "--bundle", bundle]
        broken = deepcopy(task)
        broken["files"][0]["segments"][0]["source"] += " Changed."
        save_bundle(bundle, broken)
        with patch("translation_tools.update.load_deepl_key", side_effect=AssertionError("Stale task must not call DeepL")):
            self.assertIn("segment 0 identity changed", self.invoke(update_main, args, 2)[1])
            save_bundle(bundle, task)
            path.write_bytes(b"Source body changed.\n")
            self.assertIn("source or target changed", self.invoke(update_main, args, 2)[1])

    def test_rejected_retry_never_sends_untouched_or_already_retried_segments(self):
        self.put(self.source, "a.md", "Source with `literal_code` here.\n\nUntouched source prose.\n")
        task = prepare(self.source, self.target, self.config, [])
        task["provider"] = "deepl"
        a, b = task["files"][0]["segments"]
        a.update(deepl_response="<text></text>", deepl_tag_version="v2")
        bundle = self.root / "task.json"
        save_bundle(bundle, task)
        args = ["--mode", "deepl", "--resume", "--bundle", bundle]
        with patch("translation_tools.update.load_deepl_key", side_effect=AssertionError("Explicit retry required")):
            self.assertIn("a.md: segment 0", self.invoke(update_main, args, 2)[1])
        opener = Mock()
        opener.open.return_value = Response({"translations": [{"text": ""}, {"text": ""}]})
        with patch("translation_tools.update.load_deepl_key", return_value="synthetic"), patch("urllib.request.build_opener", return_value=opener):
            self.invoke(update_main, args + ["--retry-rejected"], 2)
        payload = json.loads(opener.open.call_args.args[0].data)
        self.assertNotIn("tag_handling", payload)
        self.assertEqual(payload["text"], ["Source with", "here."])
        self.assertNotIn(b["source"], str(payload))
        a, b = json.loads(bundle.read_bytes())["files"][0]["segments"]
        self.assertIn("deepl_retry", a)
        self.assertNotIn("deepl_response", b)
        with patch("translation_tools.update.load_deepl_key", side_effect=AssertionError("Retry already paid")):
            self.invoke(update_main, args + ["--retry-rejected"], 2)

    def test_artifact_collisions_preserve_bundle_docs_and_inputs(self):
        source = self.put(self.source, "a.md", "Source body paragraph.\n")
        bundle = self.root / "task.json"
        save_bundle(bundle, self.fill(prepare(self.source, self.target, self.config, [])))
        before = bundle.read_bytes()
        for command, args in [
            (update_main, ["--apply", bundle, "--report", bundle]),
            (update_main, ["--mode", "deepl", "--files", "a.md", "--bundle", self.root / "new.json", "--report", self.root / "new.json"]),
            (update_main, ["--apply", bundle, "--report", source]),
            (check_main, ["--report", self.target / "report.json"]),
            (check_main, ["--report", bundle, "--review-results", bundle]),
            (check_main, ["--report", bundle, "--review-bundle", bundle]),
        ]:
            with self.subTest(command=command, args=args):
                self.invoke(command, args, 2)
        self.assertEqual(before, bundle.read_bytes())
        self.assertEqual(source.read_bytes(), b"Source body paragraph.\n")
        self.assertFalse(any(self.target.iterdir()))

    def test_blocked_candidate_report_and_report_failure_leave_target_unchanged(self):
        self.put(self.source, "a.md", "Source prose [linked](https://discord.gg/synthetic).\n")
        bundle, report = self.root / "task.json", self.root / "report.json"
        save_bundle(bundle, self.fill(prepare(self.source, self.target, self.config, [])))
        args = ["--apply", bundle, "--report", report]
        self.assertIn("a.md: non-compliant-link", self.invoke(update_main, args, 2)[1])
        summary = json.loads(report.read_bytes())
        self.assertEqual(summary["validation"], "blocked")
        self.assertIn("non-compliant-link", {i["code"] for i in summary["files"][0]["issues"]})
        with patch("translation_update.save_bundle", side_effect=OSError("Synthetic report write failure")):
            errors = self.invoke(update_main, args, 2)[1]
        self.assertIn("non-compliant-link", errors)
        self.assertIn("Synthetic report write failure", errors)
        self.assertFalse(any(self.target.iterdir()))

    def test_apply_requires_review_of_exact_candidate_and_preserves_existing_target(self):
        self.put(self.source, "a.md", "# Source heading\r\n\r\nSource body prose.\r\n")
        target = self.put(self.target, "a.md", "\ufeffPrevious target.\r\n")
        before = target.read_bytes()
        bundle, review, report = (self.root / name for name in ("task.json", "review.json", "report.json"))
        task = self.fill(prepare(self.source, self.target, self.config, []))
        save_bundle(bundle, task)
        self.invoke(update_main, ["--apply", bundle, "--report", report])
        results = json.loads(report.read_bytes())["result_format"]
        args = ["--apply", bundle, "--review-results", review, "--write"]
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            update_main(["--apply", str(bundle), "--write"])
        save_bundle(review, results)
        self.assertIn("Semantic review incomplete", self.invoke(update_main, args, 2)[1])
        review.write_bytes(b"null\n")
        self.invoke(update_main, args, 2)
        save_bundle(review, self.mark_reviewed(results))
        changed = deepcopy(task)
        changed["files"][0]["segments"][-1]["translation"] += generated_cjk(2)
        save_bundle(bundle, changed)
        self.assertIn("stale semantic review", self.invoke(update_main, args, 2)[1])
        self.assertEqual(target.read_bytes(), before)
        save_bundle(bundle, task)
        self.invoke(update_main, args)
        self.assertTrue(target.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertIn(b"\r\n", target.read_bytes())
        self.invoke(check_main, ["--strict", "--review-results", review])

    def test_review_reuse_exports_full_changed_pairs_and_requires_complete_results(self):
        text = "# Source heading\n\nSource body paragraph.\n"
        for path in ["a.md", "b.md", "c.md"]:
            self.put(self.source, path, text)
            self.put(self.target, path, self.translate(text))
        previous = review_bundle(self.source, self.target, self.config, [])
        results = previous["result_format"]
        for entry in results["files"][:2]:
            entry.update(reviewed_all_sections=True, completeness="pass", accuracy="pass", fluency="pass", terminology="pass")
        prior, review = self.root / "results.json", self.root / "review.json"
        save_bundle(prior, results)
        self.put(self.target, "b.md", self.translate(text) + "\n")
        self.invoke(check_main, ["--summary-only", "--review-bundle", review, "--reuse-review", prior])
        bundle = json.loads(review.read_bytes())
        self.assertEqual(bundle["reused_files"], ["a.md"])
        self.assertEqual([(e["path"], e["source"]) for e in bundle["files"]], [("b.md", text), ("c.md", text)])
        self.assertEqual(bundle["files"][0]["target"], self.translate(text) + "\n")
        quality = validate_review(bundle["result_format"], self.source, self.target, [], config=self.config)
        self.assertEqual((quality["reviewed_files"], quality["pending_files"]), (1, ["b.md", "c.md"]))
        config = deepcopy(self.config)
        config["terms"].append("ExtraTerm")
        self.assertEqual(review_bundle(self.source, self.target, config, [], previous=results)["reused_files"], [])

    def test_cli_audit_and_review_use_the_same_snapshot(self):
        text = "Source body paragraph.\n"
        self.put(self.source, "a.md", text)
        target = self.put(self.target, "a.md", self.translate(text))
        results = self.mark_reviewed(review_bundle(self.source, self.target, self.config, [])["result_format"])
        review = self.root / "results.json"
        save_bundle(review, results)

        audited = target.read_bytes() + b"\n"
        target.write_bytes(audited)
        original_read = Path.read_bytes

        def read_then_restore(path):
            data = original_read(path)
            if path == target:
                target.write_bytes(self.translate(text).encode("utf-8"))
            return data

        with patch.object(type(target), "read_bytes", read_then_restore):
            out, err = self.invoke(check_main, ["--summary-only", "--review-results", review], 2)
        self.assertNotIn("Semantic review: passed", out)
        self.assertIn("stale semantic review", err)


class ExceptionRestamp(unittest.TestCase):
    """The restamp tool re-binds exceptions to findings after edits."""

    def report(self, issues):
        return {"schema_version": 1, "issues": issues}

    def issue(self, path, code, message, fingerprint, suppressed=False):
        return {"path": path, "line": 1, "severity": "warning", "code": code,
                "message": message, "fingerprint": fingerprint, "suppressed": suppressed,
                "reason": "", "section_drift": None}

    def test_existing_finding_keeps_reason_and_new_fingerprint(self):
        from restamp_exceptions import restamp
        config = {"exceptions": [{"fingerprint": "a" * 64, "reason": "reviewed difference"}]}
        baseline = self.report([self.issue("a.md", "markdown-symbol", "added: '[' x1", "a" * 64, True)])
        current = self.report([self.issue("a.md", "markdown-symbol", "added: '[' x2", "b" * 64)])
        updated, review = restamp(baseline, current, config)
        self.assertEqual([entry["fingerprint"] for entry in updated], ["b" * 64])
        self.assertEqual(updated[0]["reason"], "reviewed difference")
        self.assertEqual(review, [])

    def test_disappeared_finding_drops_its_exception(self):
        from restamp_exceptions import restamp
        config = {"exceptions": [{"fingerprint": "a" * 64, "reason": "reviewed difference"}]}
        baseline = self.report([self.issue("a.md", "markdown-symbol", "added: '[' x1", "a" * 64, True)])
        current = self.report([])
        updated, review = restamp(baseline, current, config)
        self.assertEqual(updated, [])
        self.assertEqual(review, [])

    def test_new_finding_without_baseline_needs_review(self):
        from restamp_exceptions import restamp
        config = {"exceptions": []}
        baseline = self.report([])
        current = self.report([self.issue("a.md", "literal-term", "Recount: 'x' 1->2", "c" * 64)])
        updated, review = restamp(baseline, current, config)
        self.assertEqual(updated, [])
        self.assertEqual([issue["code"] for issue in review], ["literal-term"])

    def test_normalize_ignores_counts_but_keeps_rule_text(self):
        from restamp_exceptions import normalize
        self.assertEqual(normalize("added: '[' x1"), normalize("added: '[' x2"))
        self.assertNotEqual(normalize("added: '[' x1"), normalize("missing: '[' x1"))


if __name__ == "__main__":
    unittest.main()
