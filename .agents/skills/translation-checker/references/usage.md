# Translation verification and updates

Use the [checker skill](../SKILL.md) for audit commands and finding triage.
Use the [semantic review skill](../../translation-semantic-review/SKILL.md)
for the full bilingual review procedure and approval criteria.

Python 3.10 or later. Run commands from the repository root:

```sh
python -m pip install -r .agents/skills/translation-checker/requirements.txt
python -m unittest discover -s .agents/skills/translation-checker/scripts -p "test_*.py"
python .agents/skills/translation-checker/scripts/translation_check.py --strict --summary-only --report .agents/skills/translation-checker/.reports/audit.json
```

All verification and translation-update Python code lives under
`.agents/skills/translation-checker/scripts/`. Reports and task bundles belong in
the ignored `.agents/skills/translation-checker/.reports/` directory. Checks read
the current English source; they contain no expected translations, bilingual
answer tables, or snapshots of Chinese wording. Behavior tests use generated CJK
characters. Only terminology and other literal exclusions are stored verbatim.

## What the checks establish

Hard failures cover missing documents/categories, changed code (including
comments), code fence metadata, inline literals, identifiers, terminology, link
destinations, MDX code/props, metadata keys, heading levels/order/anchors,
duplicate anchors, malformed fences/admonitions, and replacement characters.
Unexpected ASCII control characters also fail. In table cells, an escaped pipe
preserves the rendered code value; an unescaped pipe inside code splits the cell
and fails the target check.
The literal Markdown marker `{#}` may gain a backslash to render correctly in
a heading; the check still fails if the marker disappears or MDX code changes.
Localizable metadata values and quoted `alt`, `title`, `label`, `placeholder`,
and `aria-label` attributes are prose; other attributes and expressions are code.
Code strings and comments must match verbatim. Only a code fence's `title`
value is localizable; its language, line highlights and other directives remain
protected. JSON-LD permits changes to `name`, `text`, `description`, `headline`
and `abstract` prose while retaining types, contexts, URLs and surrounding code.
Literal-only lines are checked even when they contain no translatable prose.
Indented JSX children remain prose, and backticked HTML examples cannot hide
subsequent paragraphs. Backticks around preserved identifiers or product names
do not count as missing literals. Only surplus code spans containing exactly the
identifier can satisfy bare identifier counts; existing source code spans are
still required separately. Fully quoted headings inside upstream
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
The `literal-inline-code-substitution` warning identifies a section that
omits a repeated code identifier and introduces a new one. Check both values
in the affected section; finding the original identifier elsewhere does not
validate a setting or example.
A URL only has to survive somewhere in the target, as a bare URL, a link
destination, or inline code. JSON-LD payloads are compared by structure, so
translated FAQ text is allowed while a changed FAQ count is not. Keyword lists
and layout directives such as `sidebar_position` are not prose and not
structure, so they never fail a file.

Two literal classes are not failures. A code span that holds an interface
label (`Settings`, `Admin Panel`, `Image Generation Engine`) may be translated,
because the translated site shows a translated interface; that is reported as a
note. Protected terms are checked in each matched section, including in bold
text, headings, and inline code. Mention-count changes remain warnings for
review. A link to a host listed in `non_compliant_link_patterns` may be
dropped, because project policy removes Discord, Reddit and similar community
links from the Chinese site; keeping one is reported as `non-compliant-link`,
and a code span that exists only in the removed sentence disappears with it.
The layout check allows a contact-directory row to disappear when its only
cells are the matching host name and its policy-listed link. It still compares
the rest of that table and other links, code, and Markdown.

Compound menu paths qualify as UI labels only when every occurrence is in a
UI action. A default row may move the English `empty string` gloss outside the
code span; the empty-string literal must remain in that setting's default row.
An identifier may lose a stray terminal period only when its clean spelling
already occurs upstream and the target has enough exact occurrences. The
`source_term_aliases` map corrects known bare terminology typos; it does not
allow changes inside code, commands, or configuration keys.

Warnings cover untranslated English after exclusions, verbatim copied prose,
number drift, Markdown/list/table differences, and unusually short sections.
An empty section is an error. Section checks continue when heading counts differ.
For settings with an upstream `Type` and a backticked numeric `Default`,
`setting-type` checks a literal type in the opening type row.
`setting-default` checks numeric and boolean defaults in their own rows.
A value elsewhere cannot satisfy either check. Reordered fields, unit conversions,
and upstream inaccuracies require review rather than automatic replacement.
English month/year, month/day/year, and day/month/year dates compare by calendar value with
their Chinese counterparts. Two coordinated days sharing a month and year
compare as two complete dates; neither day may disappear or change.
A standalone English month needs date context; a
suffix of another word cannot be its preposition. Explicit AM/PM clock notation compares by hour and
minute. Coordinated deadlines in the same sentence may share a unit when the
second deadline omits it. The values and any explicit units still have to match.
Day labels such as `on day 8` and `第 8 天` compare by ordinal, not
as durations or counts per day. Missing or changed components still warn.
Prose durations after a slash retain their units, as in a rate per 30-day
period. URL and filesystem path literals remain protected.
Localized multipliers, pixel counts, percentile ranks, and explicit numeric
ranges compare by value and unit. Range separators and thousands grouping may
differ. Duration and token ranges preserve both endpoints, the unit, and
whether the upper bound is open. Pixel counts may use a million-pixel scale,
and a year duration may use the Chinese suffix for excess years. An explicit
Chinese calendar span (`年间`) with two four-digit years can match a bare range
without being treated as a duration. Changed endpoints and code spans still
report differences. List marker spelling and padding compare equal
only when the parsed block structure matches. CVE and
GHSA identifiers are protected literals, not untranslated title text.
English terminology alone never triggers untranslated-prose warnings.
The same exclusions apply to fence titles. Keyword lists do not contribute to
copied-section warnings. Dollar prices are not inline math, and sentence-ending
periods are not part of bare filesystem paths; backticked paths remain exact.
Bare Windows drive-letter paths are protected as whole identifiers, including
any product names or numbers in their directory names.
Admonition types may differ at the same position; a different number of
admonitions is a failure. An upstream parse defect is reported as a warning:
the translation must not inherit broken upstream structure, so block-level
comparisons for that file become review signals. Code differences become review
signals only when unclosed upstream fences, or malformed inline fences with a
changed block count, make the code comparison unreliable. A standalone source
code span moved to a new fenced block must retain its exact body. An unrelated
upstream admonition defect never relaxes code preservation.

Use `--files` for paths, directory prefixes, or globs relative to `docs/`:

```sh
python .agents/skills/translation-checker/scripts/translation_check.py --files alternatives reference/https/haproxy.md --report .agents/skills/translation-checker/.reports/selected.json
```

Exit codes: `0` means selected deterministic checks passed; `1` means findings
(`--strict` includes warnings); `2` means invalid input or an operational failure.
An empty selection fails. JSON records contain file, line, rule, severity,
message, and an exact exception fingerprint. File coverage includes category
JSON; it measures counterpart existence, never semantic completeness.
File-wide terminology recount and Markdown symbol warnings include
`section_drift` in JSON. Each entry gives an anchor, the heading line on each
side, and local token counts. These are review leads: document-wide allowances
such as policy-link removal can make local counts differ from the reported
total. Locations do not affect findings or exception fingerprints.

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
python .agents/skills/translation-checker/scripts/translation_check.py --files alternatives --review-bundle .agents/skills/translation-checker/.reports/review.json
```

The agent reads every pair and section in full. It reviews completeness,
accuracy, fluency, and terminology; markup and protected literals are excluded
from language judgments. It copies `result_format` into a separate result file,
sets `reviewed_all_sections` only after full comparison, and records each finding
with `line`, `source_evidence`, and `message`. Status values are `pass`, `fail`,
or `needs-review`. Never mark an unread file passed.

```sh
python .agents/skills/translation-checker/scripts/translation_check.py --strict --files alternatives --review-results .agents/skills/translation-checker/.reports/review-results.json --report .agents/skills/translation-checker/.reports/reviewed-audit.json
```

Results require every selected source file exactly once, valid statuses, and
matching source/target hashes. Incomplete, stale, or failed reviews cannot pass.
This validates review coverage and provenance, not the reviewer's truthfulness.
Without submitted results, reports always say semantic review is required.

On later runs, add `--reuse-review .agents/skills/translation-checker/.reports/review-results.json` to the
`--review-bundle` command. Only completed, finding-free reviews with the same
source, target, and verifier configuration hashes carry forward. The export
still audits all selected files; only files needing review include full text.
Keep carried-forward entries in `result_format`. Review changed pairs in full,
not just the changed lines.

Use `--review-results`, `--review-bundle`, and `--reuse-review` together to
validate current results and export the next pending pairs in one audit. Pass
the same results file to both input options. A partial result still exits
nonzero, and its report lists the pending paths.

When only exact exceptions change, pass the old configuration using
`--reuse-review-config` with `--reuse-review`. The old config must match the
review digest. The exported result binds to the new config, and deterministic
checks run again. A changed document or any other config change prevents reuse
through this option.

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
python .agents/skills/translation-checker/scripts/translation_update.py --files path/to/page.mdx --bundle .agents/skills/translation-checker/.reports/task.json
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
python .agents/skills/translation-checker/scripts/translation_update.py --mode deepl --plan --files path/to/page.mdx
python .agents/skills/translation-checker/scripts/translation_update.py --mode deepl --files path/to/page.mdx --bundle .agents/skills/translation-checker/.reports/task.json --report .agents/skills/translation-checker/.reports/candidate.json
```

The plan reports distinct unrequested texts and their prose character count,
not billed characters. DeepL receives masked prose, not code or whole documents.
Exact duplicate segments on the same page share a request. For a new revision,
add `--reuse .agents/skills/translation-checker/.reports/earlier-task.json` to both commands. Only exact
same-page, same-kind segments with a single validated translation and matching
verifier configuration are reused. This is local reuse, not a paid DeepL
translation memory. Reuse does not replace full candidate review.

```sh
python .agents/skills/translation-checker/scripts/translation_update.py --mode deepl --resume --plan --bundle .agents/skills/translation-checker/.reports/task.json
python .agents/skills/translation-checker/scripts/translation_update.py --mode deepl --resume --bundle .agents/skills/translation-checker/.reports/task.json --report .agents/skills/translation-checker/.reports/candidate.json
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
python .agents/skills/translation-checker/scripts/translation_update.py --apply .agents/skills/translation-checker/.reports/task.json --report .agents/skills/translation-checker/.reports/candidate.json
```

The report includes full source, current target, candidate, and file/line
findings. Review every pair in full, including frontmatter, headings, lists,
tables, and accessible text. Copy `result_format` into a separate completed
review file as described above. It binds source, candidate bytes, and verifier
configuration. Review warnings; fix false positives in tooling when confirmed.
Do not mark unresolved omissions, meaning changes, or lost local content passed.

```sh
python .agents/skills/translation-checker/scripts/translation_update.py --apply .agents/skills/translation-checker/.reports/task.json --review-results .agents/skills/translation-checker/.reports/candidate-review.json --write
python .agents/skills/translation-checker/scripts/translation_check.py --strict --files path/to/page.mdx --review-results .agents/skills/translation-checker/.reports/candidate-review.json --report .agents/skills/translation-checker/.reports/reviewed-audit.json
npm --prefix zh-cn run build
```

The tool revalidates the entire batch and completed review before writing.
It preserves target newline style/BOM, replaces files atomically, and attempts
to roll back earlier files if a later write fails. Updates reconstruct selected
documents, not a merge with Chinese-only text. If local edits must remain, stage
a reviewed manual merge separately and audit that result. Malformed upstream
syntax stops automated translation. Docusaurus remains the final link, anchor,
route, and MDX build gate.
