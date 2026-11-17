# Translation verification and updates

Python 3.10 or later. Run commands from the repository root:

```sh
python -m pip install -r test/requirements.txt
python -m unittest discover -s test -p "test_*.py"
python test/translation_check.py --strict --report test/.reports/audit.json
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
Admonition types may differ at the same position; a different number of
admonitions is a failure. An upstream parse defect is reported as a warning:
the translation must not inherit broken upstream structure, so block-level
comparisons for that file become review signals.

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
body belongs under the right heading. Export full pairs for the current AI agent:

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

## Autonomous AI translation (default, no key)

Only prepare/apply translations when the user requests translation work.

```sh
python test/translation_update.py --files path/to/page.mdx --bundle test/.reports/task.json
```

The current agent translates `source` prose segments and fills only their
`translation` fields. Full source/current target context is included. Protected
terms, code, URLs, numbers, and Markdown symbols become ordered `⟦Pn⟧`
placeholders. Keep each placeholder exactly once, in order. No model endpoint,
model key, or additional provider configuration is needed.

```sh
python test/translation_update.py --apply test/.reports/task.json
python test/translation_update.py --apply test/.reports/task.json --write
```

The first command validates only. The second writes only after validating the
entire batch. Changes to source, target, configuration, segment identity, or
protected content reject the task. Writes preserve target newline style/BOM,
use atomic replacement per file, and roll back earlier writes on a later I/O
failure. This is not a crash-proof multi-file filesystem transaction.

Updates reconstruct selected documents from upstream prose segments. They do
not merge arbitrary Chinese-only blocks or preserve unrelated local edits.
Use small explicit selections and review the resulting diff. Malformed upstream
syntax stops automated translation; fix/review syntax before generating a task.
Upstream-derived explicit heading IDs are added automatically, including dedup
suffixes and escaping for indented MDX headings.

## DeepL translation (optional key only)

Copy `.env.example` to `.env` and set:

```dotenv
DEEPL_AUTH_KEY=your-key
```

No other setting is required. An environment variable of the same name takes
precedence. The key suffix selects Free or Pro automatically. `.env` is ignored
by Git and never executed as shell code. Autonomous verification/translation
does not load the key.

```sh
python test/translation_update.py --mode deepl --files path/to/page.mdx --bundle test/.reports/deepl.json
python test/translation_update.py --apply test/.reports/deepl.json --write
```

DeepL mode sends prose only. XML `keep` tags protect placeholders. Requests batch
at most 50 texts and stay below 120,000 encoded bytes, with a 45-second timeout
and at most three attempts for transient HTTP failures. Redirects are rejected;
errors never print keys or API response bodies. Returned XML, placeholder order,
and result counts must validate. No live API requests run in behavior tests.

Both modes share the same apply checks. Follow updates with a strict audit,
semantic review, diff review, and `npm --prefix zh-cn run build`. Python's
CommonMark parser and conservative MDX scanner do not replace Docusaurus's MDX
compiler or its broken-link/anchor checks. Do not weaken build validation.
