---
name: upstream-sync
description: "Sync upstream English docs (en-us) to Simplified Chinese (zh-cn), verify translations, or maintain translation tooling. Use for en-us submodule updates, translation sync, coverage audits, and offline acceptance tests."
---

# Upstream Sync Workflow (en-us → zh-cn)

Sync updates from the official English documentation submodule `en-us/` (`open-webui/docs`) and translate them into `zh-cn/` maintained in this repository.

## When to Use

- User requests "sync upstream", "pull en-us updates", or "translate latest docs"
- Check whether the `en-us` submodule is behind `origin/main`
- After upstream adds or modifies docs, the Chinese version and `STATUS.md` need updating
- For verification or tooling only, go directly to [verification](#41-verify-completeness-and-quality-before-committing). Do not fetch, pull, translate, or send provider requests unless separately requested.

## Prerequisites

- Workspace root is `openwebuidocs` (contains `en-us/`, `zh-cn/`, `AGENTS.MD`, `STATUS.md`)
- The translation principles and site differences in the root `AGENTS.MD` have been reviewed
- On Windows, prefer PowerShell; `git -C` must be available
- Python 3.10+ with `python -m pip install -r test/requirements.txt`
- Read [`test/README.md`](../../../test/README.md) for verifier rules, review result schemas, and provider commands

## Translation Principles (must follow during execution)

**Do NOT translate**: code blocks, commands, environment variable names, config keys, error messages, product/brand names

**DO translate**: body text, headings, UI interaction descriptions, step-by-step instructions

Other conventions:

- The Chinese version removes non-compliant external links (Discord, Reddit, X, etc.). The hosts are listed in `non_compliant_link_patterns` in `test/translation_config.json`; the verifier allows the link to be absent and reports `non-compliant-link` when a translation keeps one
- An interface label that upstream marks with a code span (`Settings`, `Admin Panel`, `Image Generation Engine`) may be translated, because the Chinese site shows a Chinese interface. Identifiers, commands, paths, values and product names stay verbatim inside code spans
- Translate prose in code fence `title="..."` values; filename/path titles stay literal
- Preserve code comments and string values byte for byte. Preserve fence directives other than the title value. JSON-LD prose may be localized, but its types, contexts, URLs and surrounding code stay unchanged
- `tab-*/` content is included via MDX `<Tabs>` and does not appear in the sidebar
- Static assets (images, etc.) are copied from `en-us/static/` to `zh-cn/static/` at the same relative path
- For site config differences see `AGENTS.MD` section 3; do not blindly overwrite `zh-cn` localized configuration

---

## Procedure

### 1. Detect Upstream Changes

```powershell
git -C en-us fetch origin main
git -C en-us log HEAD..origin/main --oneline
```

- **No output**: `en-us/` is already up to date. Stop for detection-only requests; run requested verification or backlog work when explicitly requested.
- **Has output**: record the commit list and proceed to step 2

Optional: stop here for detection-only mode (no pull).

### 2. Pull and Analyze Changes

Record the submodule commit before updating (for diff and STATUS):

```powershell
$before = git -C en-us rev-parse HEAD
git -C en-us pull origin main
$after = git -C en-us rev-parse HEAD
git -C en-us diff --name-only $before $after
```

> Avoid relying on `HEAD@{1}` (reflog is unreliable in some environments). Always use `$before` / `$after` for diffing.

### 3. Classify Changed Files by Priority

| Priority | Change Type | Handling Strategy |
| -------- | ----------- | ----------------- |
| P0 | New/modified `.md`/`.mdx` files under `docs/` | **Must translate** |
| P1 | Modified `_category_.json` (labels, ordering) | Update the `zh-cn` counterpart |
| P2 | Modified `docusaurus.config.ts` / `sidebars.ts` | Evaluate whether to sync; refer to `AGENTS.MD` "Chinese/English site differences" |
| P3 | Modified `src/` (components/themes), `static/` (static assets) | Must sync; images etc. copied directly to `zh-cn/static/` |
| P4 | `.github/`, `scripts/`, config files | Usually no need to sync (build & CI are independent) |

Briefly report to the user: list of P0–P3 files and the planned handling.

### 4. Execute Translation & Sync

When the user requests verification/tooling only, do not translate or apply translation tasks. Verification never requires a provider key. Never encode expected Chinese wording, bilingual answer tables, or translated-answer snapshots into `test/`; only terminology and other literal exclusions may be stored verbatim. Behavior fixtures use generated text rather than translations.

Choose the translation mode from the user's request. Default to **autonomous**; the current AI translates without API configuration. **DeepL** requires only `DEEPL_AUTH_KEY` in root `.env` (see `.env.example`); do not ask for an endpoint or model setting. Never display or commit the key. Do not silently switch providers after a failure.

When the user assigns translation to sub-agents, delegate translation edits directly. The parent handles tooling, integration, and validation; it must not translate on their behalf. Respect the user's concurrency limit; run one translation agent at a time when requested. A provider/capacity failure must be reported, never hidden by certifying unfinished review.

Prepare small, explicit file batches. Paths are relative to `en-us/docs/`.
Keep task and review artifacts in ignored `test/.reports/`.

```powershell
# Autonomous: fill only translation fields in this task JSON, preserving placeholders.
python test/translation_update.py --files path/to/page.mdx --bundle test/.reports/task.json

# DeepL: estimate locally, then send only authorized text.
python test/translation_update.py --mode deepl --plan --files path/to/page.mdx
python test/translation_update.py --mode deepl --files path/to/page.mdx --bundle test/.reports/task.json --report test/.reports/candidate.json

# Either provider: export full source/current target/candidate for review without writing docs.
python test/translation_update.py --apply test/.reports/task.json --report test/.reports/candidate.json
```

Use `--resume --bundle` for an interrupted DeepL task. Review rejected replies before a bounded `--resume --retry-rejected`; do not loop on a failed retry. Use `--reuse` with an earlier compatible checkpoint for a new revision. Only exact same-page segments are reusable. See [`test/README.md`](../../../test/README.md#deepl-optional-key-only) for commands and limits.

Task bundles bind source/target bytes, configuration, and segment identities. Autonomous translations must preserve ordered `⟦Pn⟧` placeholders. Both providers protect terminology, code, identifiers, link destinations, numbers, and Markdown symbols. Automated updates reconstruct documents; compare the complete candidate to upstream and the existing target before applying. Do not overwrite Chinese-only content or local policy edits. Malformed upstream syntax stops generation; report or repair the defect rather than bypassing protection.

1. Compare `en-us/docs/` with `zh-cn/docs/` file by file; process all P0 items
2. Adhere to the "Translation Principles" above
3. When upstream adds new MDX `<Tabs>`, ensure the corresponding `tab-*/` directories are added to `zh-cn`
4. When upstream adds/modifies image paths, copy them to the same path under `zh-cn/static/`
5. Process P1 (`_category_.json`) and necessary P2/P3 items
6. Renames/moves/deletions: perform equivalent operations in `zh-cn` (e.g. upstream `features/foo.md` → `ecosystem/foo.md`)

For large-scale changes:

- Translate in batches by directory (`features/`, `ecosystem/`, `reference/`, etc.)
- For very long files like `reference/env-configuration.mdx`: translate only descriptive text, **never** modify environment variable names or code examples

#### 4.1 Verify completeness and quality before committing

All translation verification scripts live under root `test/`. Run offline behavior tests after changing them. Audit the requested scope; for existing target files, export review pairs with `--review-bundle`:

```powershell
python -m unittest discover -s test -p "test_*.py"
python test/translation_check.py --strict --summary-only --report test/.reports/audit.json
python test/translation_check.py --files path/to/page.mdx --review-bundle test/.reports/review.json
```

Fully quoted headings inside upstream troubleshooting/error sections are source-derived literal diagnostics. Preserve those messages, including when translating with either provider; other quoted headings remain prose.

For `setting-default` findings, compare the same setting's default and unit in both languages. If upstream pages disagree, check the application revision corresponding to the docs before changing the translation. Record that revision in `STATUS.md`.

The deterministic audit checks file/category coverage, code/literal preservation, heading structure/anchors, Markdown structure, metadata, terminology, untranslated prose, and omission signals. It compares matched sections even when heading counts differ. A dropped literal fails; an added or re-counted literal, a translated interface label and a repaired upstream fence are review signals. File coverage and matching headings **do not establish semantic completeness**. Do not invent a quality score or claim a semantic pass from static checks. Treat findings as leads, not proof: read the pair before changing a translation, and improve the checker when a finding turns out to be a tool defect.

Read every English/Chinese pair in the candidate report or review bundle in full. Assess omissions/additions, facts, negation, numbers, fluency, terminology, and heading/body alignment. Exclude protected terms, code, and markup from language judgments. Complete `result_format` in a separate result file, including source evidence for every finding. For later installed-document audits, `--reuse-review` can carry forward only completed reviews with matching file and configuration hashes.

The update CLI requires a passed review of the exact candidate before writing. Use the same result file to verify the installed bytes, then build:

```powershell
python test/translation_update.py --apply test/.reports/task.json --review-results test/.reports/review-results.json --write
python test/translation_check.py --strict --files path/to/page.mdx --review-results test/.reports/review-results.json --report test/.reports/reviewed-audit.json
npm --prefix zh-cn run build
```

Resolve findings within the authorized scope. Intentional localization differences need a specific reason and exact issue fingerprint in `test/translation_config.json`; source/target changes expire that exception. Never blanket-suppress a directory, hard-code a preferred translation, weaken anchor/link checks, or silently call an incomplete review passed. Keep unresolved pre-existing findings separate from newly introduced defects. A production build with zero broken links, anchors, Markdown links, and duplicate routes remains required after translation changes.

### 5. Commit Translation Changes (excluding metadata files)

```powershell
git add zh-cn/ en-us/
git commit -m @"
sync: sync upstream en-us doc updates to zh-cn

Upstream commit: <en-us latest commit hash>
"@
```

- `<en-us latest commit hash>` uses `$after` from step 2 (full or short hash, consistent with historical commit style)
- **Do NOT** include `AGENTS.MD` / `STATUS.md` in this commit

### 6. Update AGENTS.MD and STATUS.md

#### 6.1 AGENTS.MD

Update the snapshot line near the top of the file (~line 5) with the main repo commit and timestamp:

```markdown
> Current doc snapshot `Git Commit Hash`: `<main repo latest commit hash>`, `Commit` timestamp: `<ISO 8601 timestamp>`
```

Example retrieval:

```powershell
git rev-parse HEAD
Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
```

If this sync also involves:

| Change | Update AGENTS.MD |
| ------ | ---------------- |
| New/removed doc directories | Section 5 "Document Domain Overview" |
| New/modified `_category_.json` label semantics | Section 5 translation notes |
| Site config changes | Section 3 "Chinese/English site differences" |
| This Skill's procedure changes | Section 9 pointer note + this file |

#### 6.2 STATUS.md

Sync the following data:

- `en-us` submodule latest commit hash (`$after`)
- Source file count / translated file count / `_category_.json` count / coverage rate
- Append a sync summary for this run (new files, major rewrites, renames, deletions, static assets)

Counting commands (PowerShell):

```powershell
(Get-ChildItem -Path en-us/docs -Recurse -Include *.md,*.mdx -File).Count
(Get-ChildItem -Path zh-cn/docs -Recurse -Include *.md,*.mdx -File).Count
(Get-ChildItem -Path en-us/docs -Recurse -Filter _category_.json -File).Count
(Get-ChildItem -Path zh-cn/docs -Recurse -Filter _category_.json -File).Count
```

Coverage = translated file count / source file count × 100

### 7. Commit Metadata and Push

```powershell
git add AGENTS.MD STATUS.md
git commit -m "chore: update AGENTS.MD and STATUS.md to latest sync state"
git push
```

Only execute `git push` when the user explicitly requests it. If the user does not request a push, stop after the two local commits and report.

---

## Completion Checklist

- [ ] `en-us` is updated to `origin/main`
- [ ] All requested P0 docs have been translated into `zh-cn/docs/` using the selected provider (skip for verification/tooling-only requests)
- [ ] P1 `_category_.json` files are aligned
- [ ] Necessary static/src assets have been synced
- [ ] Renames/deletions have equivalent handling in zh-cn
- [ ] Translation commit and metadata commit are separated
- [ ] `STATUS.md` counts and coverage have been updated
- [ ] `AGENTS.MD` snapshot hash/timestamp has been updated (if applicable)
- [ ] Python checks and complete semantic review cover the requested scope; unresolved findings are reported honestly
- [ ] Production build passes with zero broken-link/anchor/duplicate-route diagnostics after translation changes

## FAQ

| Situation | Handling |
| --------- | -------- |
| No new upstream commits | Stop for detection only; still perform explicitly requested verification/backlog work |
| DeepL key absent | Explain that only `DEEPL_AUTH_KEY` in `.env` is needed; autonomous mode needs no key |
| Config/CI changes only (all P4) | Still update submodule pointer; may have no translation commit, or commit only `en-us` pointer + STATUS |
| zh-cn intentionally retains local differences | Follow `AGENTS.MD` section 3; do not overwrite with en-us |
| Conflicting or uncertain product terminology | Keep the en-us term; confirm with user before changing |

## Related Files

- Project conventions: repo root [`AGENTS.MD`](../../../AGENTS.MD)
- Translation status: [`STATUS.md`](../../../STATUS.md)
- English source: `en-us/docs/`
- Chinese target: `zh-cn/docs/`
