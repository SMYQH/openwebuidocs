# Translation verification and updates

Python 3.10 or later. Run commands from the repository root:

```sh
python -m pip install -r test/requirements.txt
python -m unittest discover -s test -p "test_*.py"
python test/translation_check.py --strict --summary-only --report test/.reports/audit.json
```

All verification and translation-update Python code lives under `test/`. Reports
and task bundles belong in the ignored `test/.reports/` directory. Checks read
the current English source; they contain no expected translations, bilingual
answer tables, or snapshots of Chinese wording. Behavior tests use generated CJK
characters. Only terminology and other literal exclusions are stored verbatim.

## What the checks establish

Hard failures cover missing documents/categories, changed code (including
comments), code fence metadata, inline literals, identifiers, terminology, link
destinations, MDX code/props, metadata keys, heading levels/order/anchors,
duplicate anchors, malformed fences/admonitions, and replacement characters.
Localizable metadata values and quoted `alt`, `title`, `label`, `placeholder`,
and `aria-label` attributes are prose; other attributes and expressions are code.
Code strings and comments must match verbatim. Only a code fence's `title`
value is localizable; its language, line highlights and other directives remain
protected. JSON-LD permits changes to `name`, `text`, `description`, `headline`
and `abstract` prose while retaining types, contexts, URLs and surrounding code.
Literal-only lines are checked even when they contain no translatable prose.
Indented JSX children remain prose, and backticked HTML examples cannot hide
subsequent paragraphs. Backticks around preserved identifiers or product names
do not count as missing literals. Fully quoted headings inside upstream
troubleshooting/error sections are literal diagnostics: both providers preserve
them, language checks exclude them, and changed messages fail preservation.
Other quoted headings still require translation.
Both update providers receive prose fence titles as segments. Titles consisting
of filenames or paths remain literal, along with code bodies and other directives.

A literal that upstream uses and the translation never uses is a failure. A
literal the translation adds, or mentions a different number of times, is a
review signal instead: translations legitimately repeat a term a different
number of times. Link destinations are compared after resolving them, so
relative and absolute forms, `.md`/`.mdx` suffixes, and links that upstream
points at the English site while the translation points at its own pages
compare equal.
A URL only has to survive somewhere in the target, as a bare URL, a link
destination, or inline code. JSON-LD payloads are compared by structure, so
translated FAQ text is allowed while a changed FAQ count is not. Keyword lists
and layout directives such as `sidebar_position` are not prose and not
structure, so they never fail a file.

Two literal classes are not failures. A code span that holds an interface
label (`Settings`, `Admin Panel`, `Image Generation Engine`) may be translated,
because the translated site shows a translated interface; that is reported as a
review signal. A link to a host listed in `non_compliant_link_patterns` may be
dropped, because project policy removes Discord, Reddit and similar community
links from the Chinese site; keeping one is reported as `non-compliant-link`,
and a code span that exists only in the removed sentence disappears with it.

Warnings cover untranslated English after exclusions, verbatim copied prose,
number drift, Markdown/list/table differences, and unusually short sections.
An empty section is an error. Section checks continue when heading counts differ.
English terminology alone never triggers untranslated-prose warnings.
The same exclusions apply to fence titles. Keyword lists do not contribute to
copied-section warnings. Dollar prices are not inline math, and sentence-ending
periods are not part of bare filesystem paths; backticked paths remain exact.
Admonition types may differ at the same position; a different number of
admonitions is a failure. An upstream parse defect is reported as a warning:
the translation must not inherit broken upstream structure, so block-level
comparisons for that file become review signals. Code differences become review
signals only when unclosed upstream fences, or malformed inline fences with a
changed block count, make the code comparison unreliable. An unrelated upstream
admonition defect never relaxes code preservation.

Use `--files` for paths, directory prefixes, or globs relative to `docs/`:

```sh
python test/translation_check.py --files alternatives reference/https/haproxy.md --report test/.reports/selected.json
```

Exit codes: `0` means selected deterministic checks passed; `1` means findings
(`--strict` includes warnings); `2` means invalid input or an operational failure.
An empty selection fails. JSON records contain file, line, rule, severity,
message, and an exact exception fingerprint. File coverage includes category
JSON; it measures counterpart existence, never semantic completeness.

`translation_config.json` defines English terminology/exclusions, heuristic
thresholds, and `non_compliant_link_patterns` (URL globs the translation may
drop). Add project-specific terms there; do not add expected translations.
Intentional localization differences need an `exceptions` entry containing an
issue's `fingerprint` and a specific `reason`. Fingerprints bind both documents,
the path, rule, line, and finding. Editing either document expires the exception.
Do not blanket-exempt a directory or hide a stale upstream parse error.

## Semantic quality review without configuration

Static checks cannot prove accuracy, fluency, correct negation, or that a Chinese
body belongs under the right heading. Export full pairs of installed documents:

```sh
python test/translation_check.py --files alternatives --review-bundle test/.reports/review.json
```

The agent reads every pair and section in full. It reviews completeness,
accuracy, fluency, and terminology; markup and protected literals are excluded
from language judgments. It copies `result_format` into a separate result file,
sets `reviewed_all_sections` only after full comparison, and records each finding
with `line`, `source_evidence`, and `message`. Status values are `pass`, `fail`,
or `needs-review`. Never mark an unread file passed.

```sh
python test/translation_check.py --strict --files alternatives --review-results test/.reports/review-results.json --report test/.reports/reviewed-audit.json
```

Results require every selected source file exactly once, valid statuses, and
matching source/target hashes. Incomplete, stale, or failed reviews cannot pass.
This validates review coverage and provenance, not the reviewer's truthfulness.
Without submitted results, reports always say semantic review is required.

On later runs, add `--reuse-review test/.reports/review-results.json` to the
`--review-bundle` command. Only completed, finding-free reviews with the same
source, target, and verifier configuration hashes carry forward. The export
still audits all selected files; only files needing review include full text.
Keep carried-forward entries in `result_format`. Review changed pairs in full,
not just the changed lines.

## Translation workflow

1. Select explicit paths relative to `en-us/docs/`. Use `--plan` for a local
   estimate before sending text to a provider.
2. Generate a task with one provider. Validate and export a candidate report.
3. Review the complete source and candidate, and diff against the current
   target. Resolve meaning changes, missing content, and local-only changes.
4. Apply with the completed review, then run a strict audit and the site build.

Only prepare/apply translations when the user requests translation work.

### Autonomous AI (default, no key)

```sh
python test/translation_update.py --files path/to/page.mdx --bundle test/.reports/task.json
```

The assigned AI translates `source` prose segments and fills only their
`translation` fields. When the user delegates translation, sub-agents make the
translation edits and the parent handles tooling and validation. Respect any
user limit on agent concurrency. Full source/current target context is included.
Protected terms, code, URLs, numbers, and Markdown symbols become ordered `⟦Pn⟧`
placeholders. Keep each placeholder exactly once, in order. No model endpoint,
model key, or additional provider configuration is needed.

### DeepL (optional key only)

Copy `.env.example` to `.env` and set:

```dotenv
DEEPL_AUTH_KEY=your-key
```

Replace the placeholder with a real key. An environment variable of the same
name takes precedence. The key suffix selects Free or Pro automatically.
`.env` is ignored by Git and never executed as shell code. Autonomous
verification/translation does not load the key.

```sh
python test/translation_update.py --mode deepl --plan --files path/to/page.mdx
python test/translation_update.py --mode deepl --files path/to/page.mdx --bundle test/.reports/task.json --report test/.reports/candidate.json
```

The plan reports distinct unrequested texts and their prose character count,
not billed characters. DeepL receives masked prose, not code or whole documents.
Exact duplicate segments on the same page share a request. For a new revision,
add `--reuse test/.reports/earlier-task.json` to both commands. Only exact
same-page, same-kind segments with a single validated translation and matching
verifier configuration are reused. This is local reuse, not a paid DeepL
translation memory. Reuse does not replace full candidate review.

```sh
python test/translation_update.py --mode deepl --resume --plan --bundle test/.reports/task.json
python test/translation_update.py --mode deepl --resume --bundle test/.reports/task.json --report test/.reports/candidate.json
```

Responses are saved atomically before decoding. Resume uses cached responses
before making requests and stops if the input snapshots no longer match. If
DeepL returned invalid output, `--resume --retry-rejected` retries only the
rejected segments: legacy XML upgrades to v2; rejected v2 replies retry prose
fragments with placeholders anchored locally. Review those fragments carefully
for fluency and meaning. A saved rejected fragment retry is not sent again.
Inspect unresolved segments instead of looping or switching providers.

DeepL groups adjacent placeholders in XML v2. It may move a term past an intact
inline code span, but may not reorder code spans or cross other protected
markers. Missing or duplicated tokens, invalid XML, and broken rendered Markdown
reject the output. Requests use at most 50 texts, at most 120,000 encoded bytes,
and a 45-second timeout. Redirects are rejected; transient HTTP retries are
bounded. No live API requests run in behavior tests.

### Shared review and apply

```sh
python test/translation_update.py --apply test/.reports/task.json --report test/.reports/candidate.json
```

The report includes full source, current target, candidate, and file/line
findings. Review every pair in full, including frontmatter, headings, lists,
tables, and accessible text. Copy `result_format` into a separate completed
review file as described above. It binds source, candidate bytes, and verifier
configuration. Review warnings; fix false positives in tooling when confirmed.
Do not mark unresolved omissions, meaning changes, or lost local content passed.

```sh
python test/translation_update.py --apply test/.reports/task.json --review-results test/.reports/candidate-review.json --write
python test/translation_check.py --strict --files path/to/page.mdx --review-results test/.reports/candidate-review.json --report test/.reports/reviewed-audit.json
npm --prefix zh-cn run build
```

The tool revalidates the entire batch and completed review before writing.
It preserves target newline style/BOM, replaces files atomically, and attempts
to roll back earlier files if a later write fails. Updates reconstruct selected
documents, not a merge with Chinese-only text. If local edits must remain, stage
a reviewed manual merge separately and audit that result. Malformed upstream
syntax stops automated translation. Docusaurus remains the final link, anchor,
route, and MDX build gate.
