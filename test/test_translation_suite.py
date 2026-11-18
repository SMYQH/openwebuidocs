"""Behavior tests use generated CJK text, never expected/baked-in translations.

English strings are synthetic source fixtures. Terminology is the only language
content asserted verbatim. No dictionary or bilingual reference answers exist.
"""

from __future__ import annotations

from copy import deepcopy
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from translation_tools.document import Document, PLACEHOLDER, digest, mask, prose, unmask
from translation_tools.update import DeepL, apply_bundle, load_deepl_key, prepare
from translation_tools.verify import compare, load_config, review_bundle, validate_review, verify
from translation_check import main as check_main


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

    def test_ordered_list_and_checkbox_markers_are_indivisible(self):
        for source, literal in [("1. Source prose", "1. "), ("- [x] Source prose", "[x]"), ("Source prose[^literal]", "[^literal]"), ("Source [reference][]", "[reference][]")]:
            _, spans = mask(source, self.terms)
            self.assertIn(literal, [s.value for s in spans])

    def test_multibacktick_inline_code(self):
        value = "Run ``literal ` command`` safely."
        _, spans = mask(value, self.terms)
        self.assertIn("``literal ` command``", [s.value for s in spans])

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

    def test_sentence_punctuation_is_not_part_of_bare_paths(self):
        source = "Read /photos. Inspect /archive/data.csv.\n"
        target = generated_cjk(8) + " /photos /archive/data.csv\n"
        self.assertNotIn("literal-identifier", self.codes(source, target))
        self.assertIn("literal-identifier", self.codes(source, target.replace("/photos", "/changed")))
        spans = mask("Read /photos/.", self.terms)[1]
        self.assertIn("/photos/.", [span.value for span in spans])

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

    def test_code_structure_must_stay_identical(self):
        source = "```python\n# literal comment\nrun()\n```\n"
        # Comments and example strings stay verbatim, like executable code.
        self.assertIn("code-changed", self.codes(source, source.replace("literal comment", "different comment")))
        # Commands and identifiers are literal: a failure.
        self.assertIn("code-changed", self.codes(source, source.replace("run()", "other()")))

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

    def test_dropped_literal_is_still_a_failure(self):
        source = "Use `OPENAI_TOKEN` for the source task.\n"
        target = (generated_cjk(9) + '。\n')
        found = [i for i in self.issues(source, target) if i.code == "literal-inline-code"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "error")

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

    def test_document_suffix_is_stripped_completely(self):
        source = "See [policy](/security/security-policy.md) for details.\n"
        target = "See [policy](/security/security-policy) for details.\n"
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("literal-destination", codes)

    def test_interface_label_may_be_translated(self):
        source = "Open the `Settings` panel and check `Admin Panel`.\n"
        target = (generated_cjk(2) + ' `' + generated_cjk(2) + '` ' + generated_cjk(5) + ' `' + generated_cjk(4) + '`。\n')
        found = [i for i in self.issues(source, target) if i.code == "literal-inline-code"]
        self.assertTrue(found)
        self.assertTrue(all(i.severity == "warning" for i in found))

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

    def test_policy_removed_link_may_be_dropped(self):
        source = "- [Community](https://discord.gg/abcdef) for support.\n"
        target = ('- ' + generated_cjk(7) + '。\n')
        codes = {i.code for i in self.issues(source, target)}
        self.assertNotIn("literal-destination", codes)

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
            self.assertLessEqual(len(payload["text"]), 50)
            self.assertLess(len(request.data), 128 * 1024)
            return Response({"translations": [{"text": t} for t in payload["text"]]})
        opener.open.side_effect = respond
        bundle = {"files": [{"segments": [{"source": "source ⟦P0⟧", "translation": None} for _ in range(121)]}]}
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


if __name__ == "__main__":
    unittest.main()
