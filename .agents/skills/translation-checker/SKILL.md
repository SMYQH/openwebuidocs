---
name: translation-checker
description: Run and troubleshoot the repository's Python translation checker. Use for coverage and preservation audits, strict checks, JSON diagnostics, exact exceptions, review-bundle commands, and offline checker tests.
---

# Python Translation Checker

Run from the repository root. Use Python 3.10+ and install `.agents/skills/translation-checker/requirements.txt` if needed. The checker is read-only for docs and needs no provider key. Save reports to ignored `.agents/skills/translation-checker/.reports/`. See [usage](references/usage.md) for individual rules and [semantic review](../translation-semantic-review/SKILL.md) for bilingual judgment.

## Run an Audit

```powershell
python -m pip install -r .agents/skills/translation-checker/requirements.txt
python .agents/skills/translation-checker/scripts/translation_check.py --strict --summary-only --report .agents/skills/translation-checker/.reports/audit.json
python .agents/skills/translation-checker/scripts/translation_check.py --strict --files alternatives --report .agents/skills/translation-checker/.reports/scoped-audit.json
python -m unittest discover -s .agents/skills/translation-checker/scripts -p "test_*.py"
```

`--files` accepts paths, directory prefixes, or globs relative to `en-us/docs/`. Omit it for full scope. Run offline unit tests after checker or configuration changes. Use `--summary-only` for large scopes; JSON still contains each finding.

Use both exit status and report: `0` means the requested checks passed; `1` means errors, warnings under `--strict`, or submitted semantic results that did not pass; `2` means invalid input or an operational failure. Without `--review-results`, a successful audit does not certify meaning.

## Triage Findings

The audit checks counterpart coverage, code and literal preservation, Markdown/MDX structure, headings and anchors, links, and metadata. Language and omission heuristics flag places to read; they cannot establish completeness or accuracy.

- Read the file, line, rule, severity, message, and any `section_drift` entries. Compare the matched English and Chinese sections. Counts are leads, not proof, and local counts can differ from totals after policy exclusions.
- For `setting-type` or `setting-default`, compare type, value, and unit within the same setting. If upstream pages disagree, check the application revision that corresponds to the docs and record it in `STATUS.md`.
- For `literal-inline-code-substitution`, compare identifiers in the affected section; an occurrence elsewhere does not prove preservation. Preserve literal diagnostic headings in troubleshooting sections. For an upstream fence repair, compare every code body and any inline sample moved into a block; do not exempt surrounding prose.
- Fix confirmed translation defects only when authorized. Fix confirmed checker defects in this skill's `scripts/` with narrow, source-derived rules and generated regression fixtures. Update this skill and its usage reference when behavior or commands change. Never hard-code translations, answer tables, or expected Chinese snapshots in the tooling; only terminology and other literal exclusions may be stored verbatim.
- Editing a translated file invalidates the exact exceptions that belonged to it, because a fingerprint mixes the file path, both file hashes, the finding line, the rule and the finding text. After such an edit, keep the audit report from before the edit as a baseline, run a fresh audit, and re-bind the surviving exceptions:
```powershell
python .agents/skills/translation-checker/scripts/restamp_exceptions.py --baseline .agents/skills/translation-checker/.reports/audit-before.json --current .agents/skills/translation-checker/.reports/audit.json
```
  The tool keeps the reason of every finding that still exists, drops exceptions whose finding disappeared, and prints the findings that need manual review. Review those findings yourself before adding an exception; the tool never invents a reason.
- Use an exact exception in `.agents/skills/translation-checker/translation_config.json` only for a verified intentional difference or reviewed upstream defect. Record the current finding's `fingerprint` and a specific `reason`. Either document changing expires it. Retest exceptions after rule changes and remove stale entries. Never loosen checks or exempt whole directories to clear warnings.

## Review Artifacts

```powershell
python .agents/skills/translation-checker/scripts/translation_check.py --files alternatives --review-bundle .agents/skills/translation-checker/.reports/review.json
python .agents/skills/translation-checker/scripts/translation_check.py --strict --files alternatives --review-results .agents/skills/translation-checker/.reports/review-results.json --report .agents/skills/translation-checker/.reports/reviewed-audit.json
python .agents/skills/translation-checker/scripts/translation_check.py --strict --files alternatives --review-results .agents/skills/translation-checker/.reports/review-results.json --reuse-review .agents/skills/translation-checker/.reports/review-results.json --review-bundle .agents/skills/translation-checker/.reports/pending.json --report .agents/skills/translation-checker/.reports/checkpoint-audit.json
```

Use the same scope when exporting and validating. The last command validates current results and exports pending pairs in one audit. It requires a results file for the current snapshot, including entries for unread pairs. A valid partial result still exits nonzero.

If files changed, export a fresh bundle with `--reuse-review` but without submitting stale results. Only finding-free passes with matching source, target, and config digests are reused. When only exact exceptions change, preserve the previous config before editing and pass it with `--reuse-review-config` plus `--reuse-review`. The report re-audits the current config; other config changes require a fresh review.

Report errors, warnings, notes, and exact exceptions separately from semantic passes and pending pairs. After changing translated site content, require the production build and its link, anchor, and route checks per [upstream-sync](../upstream-sync/SKILL.md).
