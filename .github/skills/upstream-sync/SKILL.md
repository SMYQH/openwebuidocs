---
name: upstream-sync
description: "Sync and translate upstream English docs (en-us) to simplified Chinese (zh-cn). Use when: upstream sync, sync upstream, en-us update, submodule update, translation sync, pull open-webui/docs, update STATUS.md coverage, detect new en-us commits."
argument-hint: "[optional: detect only | full sync | specific files]"
user-invocable: true
---

# Upstream Sync Workflow (en-us → zh-cn)

Sync updates from the official English documentation submodule `en-us/` (`open-webui/docs`) and translate them into `zh-cn/` maintained in this repository.

## When to Use

- User requests "sync upstream", "pull en-us updates", or "translate latest docs"
- Check whether the `en-us` submodule is behind `origin/main`
- After upstream adds or modifies docs, the Chinese version and `STATUS.md` need updating

## Prerequisites

- Workspace root is `open-webui-docs` (contains `en-us/`, `zh-cn/`, `AGENTS.MD`, `STATUS.md`)
- The translation principles and site differences in the root `AGENTS.MD` have been reviewed
- On Windows, prefer PowerShell; `git -C` must be available

## Translation Principles (must follow during execution)

**Do NOT translate**: code blocks, commands, environment variable names, config keys, error messages, product/brand names

**DO translate**: body text, headings, UI interaction descriptions, step-by-step instructions

Other conventions:

- The Chinese version removes non-compliant external links (Discord, Reddit, X, etc.)
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

- **No output**: `en-us/` is already up to date → inform user and stop
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

1. Compare `en-us/docs/` with `zh-cn/docs/` file by file; process all P0 items
2. Adhere to the "Translation Principles" above
3. When upstream adds new MDX `<Tabs>`, ensure the corresponding `tab-*/` directories are added to `zh-cn`
4. When upstream adds/modifies image paths, copy them to the same path under `zh-cn/static/`
5. Process P1 (`_category_.json`) and necessary P2/P3 items
6. Renames/moves/deletions: perform equivalent operations in `zh-cn` (e.g. upstream `features/foo.md` → `ecosystem/foo.md`)

For large-scale changes:

- Translate in batches by directory (`features/`, `ecosystem/`, `reference/`, etc.)
- For very long files like `reference/env-configuration.mdx`: translate only descriptive text, **never** modify environment variable names or code examples

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
- [ ] All P0 docs have been translated into `zh-cn/docs/`
- [ ] P1 `_category_.json` files are aligned
- [ ] Necessary static/src assets have been synced
- [ ] Renames/deletions have equivalent handling in zh-cn
- [ ] Translation commit and metadata commit are separated
- [ ] `STATUS.md` counts and coverage have been updated
- [ ] `AGENTS.MD` snapshot hash/timestamp has been updated (if applicable)

## FAQ

| Situation | Handling |
| --------- | -------- |
| No new upstream commits | Stop immediately; do not modify any files |
| Config/CI changes only (all P4) | Still update submodule pointer; may have no translation commit, or commit only `en-us` pointer + STATUS |
| zh-cn intentionally retains local differences | Follow `AGENTS.MD` section 3; do not overwrite with en-us |
| Conflicting or uncertain product terminology | Keep the en-us term; confirm with user before changing |

## Related Files

- Project conventions: repo root [`AGENTS.MD`](../../../AGENTS.MD)
- Translation status: [`STATUS.md`](../../../STATUS.md)
- English source: `en-us/docs/`
- Chinese target: `zh-cn/docs/`
