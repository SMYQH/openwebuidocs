---
name: translation-checker
description: Run the repository's translation checker and DeepL CLI. Use for preservation audits, review artifacts, exact exceptions, offline tests, and requested DeepL translations or bilingual review evidence.
---

# Python Translation Checker

Run from the repository root. Follow [first-run setup](references/usage.md#first-run-setup) on a new machine. Initialize the pinned `en-us` submodule and run `uv sync --locked` to install the local commands in `.venv`. Audits are read-only for docs and need no provider key. Save reports to ignored `.agents/skills/translation-checker/.reports/`. See [usage](references/usage.md) for individual rules and [semantic review](../translation-semantic-review/SKILL.md) for bilingual judgment.

## Use DeepL

When the user requests DeepL, run `uv run --locked deepl-cli` with `translate`, `usage`, or `review`. Use `DEEPL_AUTH_KEY` from the environment or root `.env` for live requests. For a corpus review, start with `review --plan` and `usage` and follow the [CLI examples](references/usage.md#deepl-cli). Review artifacts contain evidence for the bilingual reviewer. They carry no semantic approval.

If the remaining quota cannot cover any pending text, keep the checkpoint and continue with the [full bilingual review](../translation-semantic-review/SKILL.md). Use saved replies as evidence and compare uncovered passages directly against the source.

## Run an Audit

```sh
uv run --locked translation-check --strict --summary-only --report .agents/skills/translation-checker/.reports/audit.json
uv run --locked translation-check --strict --files alternatives --report .agents/skills/translation-checker/.reports/scoped-audit.json
uv run --locked python -m unittest discover -s .agents/skills/translation-checker/scripts -p "test_*.py"
```

`--files` accepts paths, directory prefixes, or globs relative to `en-us/docs/`. Forward slashes and Windows backslashes both work. Omit it for full scope. Run offline unit tests after checker or configuration changes. Use `--summary-only` for large scopes; JSON still contains each finding.

Use both exit status and report: `0` means the requested checks passed; `1` means errors, warnings under `--strict`, or submitted semantic results that did not pass; `2` means invalid input or an operational failure. Without `--review-results`, a successful audit does not certify meaning.

## Triage Findings

The audit checks counterpart coverage, code and literal preservation, Markdown/MDX structure, headings and anchors, links, and metadata. Language and omission heuristics flag places to read; they cannot establish completeness or accuracy.

- Read the file, line, rule, severity, message, and any `section_drift` entries. Compare the matched English and Chinese sections. Counts are leads, not proof, and local counts can differ from totals after policy exclusions.
- For `setting-type` or `setting-default`, compare type, value, and unit within the same setting. If upstream pages disagree, check the application revision that corresponds to the docs and record it in `STATUS.md`.
- For `literal-inline-code-substitution`, compare identifiers in the affected section; an occurrence elsewhere does not prove preservation. Preserve literal diagnostic headings in troubleshooting sections. For an upstream fence repair, compare every code body and any inline sample moved into a block; do not exempt surrounding prose.
- Fix confirmed translation defects only when authorized. Fix confirmed checker defects in this skill's `scripts/` with narrow, source-derived rules and generated regression fixtures. Update this skill and its usage reference when behavior or commands change. Never hard-code translations, answer tables, or expected Chinese snapshots in the tooling; only terminology and other literal exclusions may be stored verbatim.
- Exact exception fingerprints bind both files with line endings normalized to LF, plus the path, finding line, rule, and message. Content edits to either file invalidate its exceptions. Keep the audit report from before the edit as a baseline, run a fresh audit, and re-bind the surviving exceptions:
```sh
uv run --locked restamp-exceptions --baseline .agents/skills/translation-checker/.reports/audit-before.json --current .agents/skills/translation-checker/.reports/audit.json
```
  The tool keeps the reason of every finding that still exists, drops exceptions whose finding disappeared, and prints the findings that need manual review. Review those findings yourself before adding an exception; the tool never invents a reason.
- Use an exact exception in `.agents/skills/translation-checker/translation_config.json` only for a verified intentional difference or reviewed upstream defect. Record the current finding's `fingerprint` and a specific `reason`. Either document changing expires it. Retest exceptions after rule changes and remove stale entries. Never loosen checks or exempt whole directories to clear warnings.

## Review Artifacts

```sh
uv run --locked translation-check --files alternatives --review-bundle .agents/skills/translation-checker/.reports/review.json
uv run --locked translation-check --strict --files alternatives --review-results .agents/skills/translation-checker/.reports/review-results.json --report .agents/skills/translation-checker/.reports/reviewed-audit.json
uv run --locked translation-check --strict --files alternatives --review-results .agents/skills/translation-checker/.reports/review-results.json --reuse-review .agents/skills/translation-checker/.reports/review-results.json --review-bundle .agents/skills/translation-checker/.reports/pending.json --report .agents/skills/translation-checker/.reports/checkpoint-audit.json
```

Use the same scope when exporting and validating. The last command validates current results and exports pending pairs in one audit. It requires a results file for the current snapshot, including entries for unread pairs. A valid partial result still exits nonzero.

If files changed, export a fresh bundle with `--reuse-review` but without submitting stale results. Only finding-free passes with matching source, target, and config digests are reused. When only exact exceptions change, preserve the previous config before editing and pass it with `--reuse-review-config` plus `--reuse-review`. The report re-audits the current config; other config changes require a fresh review.

Report errors, warnings, notes, and exact exceptions separately from semantic passes and pending pairs. After changing translated site content, require the production build and its link, anchor, and route checks per [upstream-sync](../upstream-sync/SKILL.md).
