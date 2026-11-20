---
name: translation-semantic-review
description: Review complete English and Simplified Chinese Open WebUI documentation pairs for meaning, completeness, fluency, and terminology. Use for bilingual quality reviews or reviewing a translation candidate before writing it.
---

# Translation Semantic Review

Start at the repository root. Use the current `en-us/docs/` source and `zh-cn/docs/` target, including category JSON. Read the translation conventions in [AGENTS.MD](../../../AGENTS.MD). Review is read-only unless the user also requests fixes. The default review is offline. A clear checker report, matching headings, or full file coverage does not establish semantic quality.

## 1. Capture the Exact Pair

- **Installed docs:** Export a full review bundle using the [translation checker skill](../translation-checker/SKILL.md#review-artifacts). Use explicit file or directory scope; omit `--files` for the entire corpus. Keep bundles and results under `.agents/skills/translation-checker/.reports/`.
- **Translation candidate:** Review the report from `python .agents/skills/translation-checker/scripts/translation_update.py --apply .agents/skills/translation-checker/.reports/task.json --report .agents/skills/translation-checker/.reports/candidate.json` without `--write`. Resolve blocking checker findings before approval. Compare the complete source with the candidate. Also diff the candidate against the installed target to catch lost Chinese-only content and policy changes. A review of the installed file does not approve different candidate bytes.
- Use `files` as the reading queue and `result_format` as the result template. Keep the approved entries in the template for paths listed in `reused_files`. Split large scopes into manageable batches without dropping unchecked sections or changing review criteria.

When the user requests DeepL, use the checker's [DeepL CLI](../translation-checker/references/usage.md#deepl-cli) to collect English back-translations of installed Chinese prose. Compare suspected drift against both originals. Check source-only and target-only sections and parse issues directly. If quota runs out, continue reading the original pairs. Report incomplete DeepL evidence and any unread pairs separately from confirmed findings.

## 2. Read Both Versions in Full

Read frontmatter prose, category labels and descriptions, headings and bodies, lists, tables, localizable fence titles, and accessible text. Align sections by upstream anchors and subject. When counts differ, identify missing, duplicated, moved, or misaligned sections instead of assuming positional alignment.

| Dimension | Compare |
| --- | --- |
| `completeness` | Missing or unsupported content, headings detached from their bodies, and lost local-only content. Account for intentional differences allowed by project policy. |
| `accuracy` | Facts, negation, conditions, scope, step order, UI actions, numbers, units, and defaults in the setting they belong to. Report unclear or inconsistent upstream claims separately. |
| `fluency` | Natural, readable Chinese that retains the instruction's meaning and emphasis. Do not flag acceptable rewording as an error. |
| `terminology` | Consistent, context-appropriate terms and Chinese-English spacing. Distinguish explicit URIs, named APIs/protocols, base URLs, and shared API addresses per AGENTS.MD. |

Exclude protected product names, identifiers, commands, diagnostic text, code, and Markdown symbols from language judgments. Review the surrounding prose for meaning. Use the checker for exact preservation and structural checks; examine relevant findings against the pair.

## 3. Record Findings and Disposition

Copy `result_format` into a separate JSON result file. Keep each selected path once and leave the source, target, and config digests as generated. For each issue, record the 1-based target `line`, a short `source_evidence` excerpt, and a `message` identifying the meaning change and the correction. For missing content, point to where it belongs.

Set `reviewed_all_sections: true` only after reading the full pair. Mark each dimension `pass`, `fail`, or `needs-review`. Any unresolved finding, unread section, or missing counterpart prevents a semantic pass. Do not infer passes from tool output or bulk-fill review results.

If fixes are authorized, preserve code, anchors, and intentional local content. After any source or target edit, export a fresh pair and re-review it in full. Do not patch digests to make an old result validate.

## 4. Validate and Deliver

For installed docs, use the [checker skill](../translation-checker/SKILL.md#review-artifacts) to validate the completed results against the exact scope. A partial review can still produce a pending bundle; it cannot pass the release gate. For a candidate, hand its result back to [upstream-sync](../upstream-sync/SKILL.md#41-verify-completeness-and-quality-before-committing) for the apply, installed audit, and production build.

Report passed pairs out of the selected total, unresolved findings with source evidence, and pending paths or their artifact. Report checker diagnostics separately. Neither a validated result file nor a build proves that an unread translation is complete.
