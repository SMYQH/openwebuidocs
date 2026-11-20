"""Offline checks for the DeepL CLI and its review checkpoint."""

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, patch

from deepl_cli import main
from test_translation_suite import Fixture, Response, generated_cjk
from translation_tools.update import DeepL


class DeepLCliTests(Fixture):
    def setUp(self):
        super().setUp()
        self.opener = Mock()
        self.client = DeepL("synthetic:fx", opener=self.opener)
        self.report = self.root / "review.json"

    def invoke(self, *args, status=0):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("deepl_cli.DeepL", return_value=self.client), redirect_stdout(stdout), redirect_stderr(stderr):
            result = main(list(args))
        self.assertEqual(result, status, stdout.getvalue() + stderr.getvalue())
        return stdout.getvalue(), stderr.getvalue()

    def review(self, *args, status=0):
        return self.invoke("review", "--source", str(self.source), "--target", str(self.target),
                           "--report", str(self.report), *args, status=status)

    def test_translate_utf8_stdin_with_auto_detection(self):
        source = generated_cjk(7)
        self.opener.open.return_value = Response({"translations": [{"text": "English output"}]})
        stdin = io.TextIOWrapper(io.BytesIO(source.encode("utf-8")))
        with patch("sys.stdin", stdin):
            output, _ = self.invoke("translate", "--to", "en-us", "-")
        self.assertEqual(output.strip(), "English output")
        request = self.opener.open.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["target_lang"], "EN-US")
        self.assertEqual(payload["text"], [source])
        self.assertNotIn("source_lang", payload)
        self.assertNotIn("tag_handling", payload)

    def test_translate_utf8_file_preserves_line_endings_and_strips_bom(self):
        source = generated_cjk(7) + "\r\n" + generated_cjk(8)
        path = self.put(self.root, "source text.txt", "\ufeff" + source)
        self.opener.open.return_value = Response({"translations": [{"text": "English output"}]})

        output, _ = self.invoke("translate", "--to", "EN-US", "--input-file", str(path))

        self.assertEqual(output.strip(), "English output")
        payload = json.loads(self.opener.open.call_args.args[0].data)
        self.assertEqual(payload["text"], [source])

    def test_usage_returns_only_quota_counters(self):
        counters = {"character_count": 4, "character_limit": 20}
        self.opener.open.return_value = Response(dict(counters, unrelated="synthetic-response-data"))
        output, _ = self.invoke("usage")
        self.assertEqual(json.loads(output), counters)
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url, "https://api-free.deepl.com/v2/usage")

    def test_review_plan_makes_no_requests_or_writes(self):
        self.put(self.source, "guide/a.md", "Source prose.\n")
        self.put(self.target, "guide/a.md", generated_cjk(6))
        self.put(self.source, "b.md", "Outside the selected directory.\n")
        self.put(self.target, "b.md", generated_cjk(7))
        output, _ = self.review("--plan", "--files", r".\guide\a.md")
        self.assertIn("1 pending texts (6 characters)", output)
        self.opener.open.assert_not_called()
        self.assertFalse(self.report.exists())

    def test_budgeted_review_resumes_whole_sections_without_resending(self):
        source = "# Source\n\nRead the guide.\n"
        first = generated_cjk(6)
        second = generated_cjk(7)
        self.put(self.source, "a.md", source)
        self.put(self.source, "b.md", source)
        a = self.put(self.target, "a.md", f"# {first} {{#source}}\n\n```sh\nsecret_code\n```\n")
        self.put(self.target, "b.md", f"# {second} {{#source}}\n")
        usage = Response({"character_count": 0, "character_limit": 20})
        translation = Response({"translations": [{"text": "Source"}]})
        self.opener.open.side_effect = [usage, translation, usage, translation]

        self.review("--partial", "--max-characters", "6")
        snapshot = json.loads(self.report.read_bytes())
        self.assertEqual(len(snapshot["translations"]), 1)
        self.assertIsNone(snapshot["files"][1]["sections"][0]["backtranslation"])
        self.review("--resume")
        messages = [json.loads(call.args[0].data) for call in self.opener.open.call_args_list if call.args[0].data]
        self.assertEqual([message["text"] for message in messages], [[first], [second]])
        self.assertEqual(messages[0]["source_lang"], "ZH")
        self.assertEqual(messages[0]["target_lang"], "EN-US")
        self.assertIn("#source", a.read_text(encoding="utf-8"))
        self.assertEqual(len(json.loads(self.report.read_bytes())["translations"]), 2)

        self.put(self.target, "b.md", f"# {generated_cjk(8)} {{#source}}\n")
        _, error = self.review("--resume", "--plan", status=2)
        self.assertIn("does not match the current scope or snapshot", error)
        self.assertEqual(self.opener.open.call_count, 4)
