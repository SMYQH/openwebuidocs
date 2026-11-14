# TODO — Outstanding Work

> Last updated: 2026-11-14, after the third deep translation audit against upstream `en-us` `36b7e50e`.
> This file lists work that is **not** finished. Everything not listed here was verified as complete
> (see the verification table at the bottom).

---

## 1. Upstream sync — NOT DONE (highest priority)

The `en-us` submodule is pinned at **`36b7e50e`**, but upstream `open-webui/docs` `main` has already moved to
**`49fea2bd`**. The pending upstream range is `36b7e50e..49fea2bd` — **16 files changed, +111 / -48 lines**:

| Upstream file | Change |
| --- | --- |
| `reference/api-endpoints.md` | +4 — note that the API endpoints are no longer documented upstream |
| `reference/env-configuration.mdx` | ±8 — corrected `WHISPER_COMPUTE_TYPE` / `BYPASS_PYDUB_PREPROCESSING` defaults, OpenAI speech-model shutdown dates, new STT model default |
| `reference/monitoring/otel.md` | +9 — the user gauges exported by the OpenTelemetry metrics |
| `troubleshooting/rag.mdx` | ±8 |
| plus | Google PSE end date moved to 2027-01-01, two dead GitHub links fixed, admin model-settings menu renamed, API-endpoint wording reworked |

**Action**: run the `/upstream-sync` skill (`.github/skills/upstream-sync/SKILL.md`), which re-syncs
`zh-cn/src/`, `zh-cn/scripts/`, `zh-cn/package.json` and the localized `zh-cn/docusaurus.config.ts` from the
submodule while preserving the Chinese site configuration, then translate the changed pages and re-run the
verification suite below.

**Note**: the audit scripts in `.tmpwork/deepaudit/` are written against the `36b7e50e` snapshot; re-run them
after the sync and expect a fresh round of findings.

---

## 2. Review items left open by the third audit

These are **not** known defects. Each was sampled and judged to be a benign structural difference, but the
sampling was not exhaustive.

### 2.1 Section-level prose-unit differences — 51 sections flagged, 6 with a difference of >= 3

The detector compares the number of prose units (paragraphs, list items, table rows) per section between the
English and Chinese page. A difference of 2 is usually the Chinese version merging two English paragraphs;
larger differences are worth a second look.

Remaining sections with a difference of >= 3 (6 in total):

| Section | EN / ZH units | Status |
| --- | --- | --- |
| `reference/env-configuration.mdx` — `DATABASE_URL` | 12 / 8 | sampled: the Chinese version folds several upstream paragraphs into one |
| `reference/env-configuration.mdx` — `REDIS_SOCKET_CONNECT_TIMEOUT` | 11 / 8 | sampled: same pattern |
| `reference/env-configuration.mdx` — `REDIS_HEALTH_CHECK_INTERVAL` | 10 / 7 | not yet sampled |
| `security/security-policy.mdx` — "Reporting Guidelines" | 41 / 17 | see §2.3 |
| `troubleshooting/rag.mdx` — "10. CUDA Out of Memory During Embedding" | 10 / 6 | sampled: the numbered list items are merged into one paragraph; all six items and the code block are present |
| `troubleshooting/sso.mdx` — "Correct Microsoft Variables:" | 12 / 7 | sampled: the `:::info` / `:::tip` / `:::warning` blocks are merged into their parent paragraphs; all content is present |

**Action**: open the section list printed by `python .tmpwork/deepaudit/secunits.py` and confirm each remaining
difference is a deliberate merge rather than a dropped paragraph.

### 2.2 `features/extensibility/plugin/tools/development.mdx` — `<details>` structure differs from upstream

Upstream nests two large code examples inside `<details><summary>Safe Message Streaming (Legacy Mode)</summary>`
and `<details><summary>Dynamic Content Replacement (Legacy Mode)</summary>`. The Chinese page keeps three
`<details>` wrappers (including "模式安全的消息工具") but places the code blocks **outside** them. The content is
complete and the anchors resolve, but the collapsible structure is not identical to upstream.

**Action**: either re-nest the code blocks (indentation-sensitive, inside JSX) or accept the difference
deliberately and record it in `STATUS.md` under "Intentional Differences".

### 2.3 `security/security-policy.mdx` — "Reporting Guidelines" readability

Upstream renders the 13 reporting rules as separate numbered items with nested `:::note` blocks. The Chinese
version merges each rule and its note into one long paragraph. All 13 rules and all notes are present, but the
Chinese page is noticeably harder to scan than the English one.

**Action**: split the merged paragraphs back into a numbered list with the nested admonitions.

### 2.4 `reference/env-configuration.mdx` — field wording not line-for-line with upstream

The `- 类型：` / `- 默认值：` / `- 描述：` labels are translated and correct, but the value wording is not always
word-for-word aligned with the upstream English (for example the `DATABASE_URL` and `REDIS_*` entries were
paraphrased rather than translated literally). This is acceptable Chinese prose, but it means the file cannot
be diffed mechanically against upstream.

**Action**: optional — do a literal pass over the entries whose English changed in the pending upstream sync.

---

## 3. Known, intentional differences — no action needed

- **46 code blocks** where the Chinese version translates the comments, user-facing strings or mermaid labels
  inside the block. The identifiers themselves are byte-identical to upstream.
- **14 headings** whose `{#id}` sits inside a JSX block without the `\{#id}` escape documented in `AGENTS.MD`.
  The production build resolves every one of them, so they are currently harmless.
- **`intro.mdx`**: the upstream Discord badge is intentionally removed (project policy: the Chinese site drops
  Discord / Reddit / X links).
- **`_imgs.py` reports 1 "missing" image** that is in fact an API URL (`/api/v1/files/abc123/content`), not an image.

---

## 4. Housekeeping

- **`AGENTS.MD` snapshot header** — the `Git Commit Hash` / `Commit` timestamp line at the top of `AGENTS.MD`
  must be refreshed to point at the commit that carries this change set. It is updated by the follow-up commit
  that accompanies this file.
- **`STATUS.md`** — the "Content completeness" metrics and the 2026-11-14 audit section were updated in this
  change set; refresh them again after the upstream sync in section 1.

---

## 5. Verification suite to re-run after any change

```bash
cd zh-cn && npm run build        # must pass with 0 broken links / anchors / markdown links / duplicate routes

python .tmpwork/deepaudit/_realmiss_run.py   # content gaps per section          -> expect 0
python .tmpwork/deepaudit/critspan.py         # verbatim inline code spans       -> expect 0
python .tmpwork/deepaudit/codeblocks5.py      # code-block parity                -> expect 1441 identical
python .tmpwork/deepaudit/verify_code.py      # code-block placement             -> expect 0 violations
python .tmpwork/deepaudit/cbdrops.py          # identifiers lost in code blocks  -> expect 0
python .tmpwork/deepaudit/secunits.py         # prose-unit parity (review list)  -> informational
python .tmpwork/deepaudit/secalign.py         # section misalignment            -> expect 0
python .tmpwork/deepaudit/admtitles.py        # untranslated admonition titles  -> expect 0 (product names excluded)
python .tmpwork/deepaudit/todo3.py            # TODO markers EN vs ZH            -> expect 14 / 14
python .tmpwork/deepaudit/_cjklinks.py        # CJK-literal anchors              -> expect 0
python .tmpwork/deepaudit/_moji.py            # U+FFFD replacement chars         -> expect 0
node    .tmpwork/deepaudit/idparity.cjs       # heading / explicit-ID parity     -> expect 0 mismatches
```

Current status of the suite on `en-us` `36b7e50e`: **all green** (see the table in `STATUS.md`).
