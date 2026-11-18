# Chinese Documentation Translation Status

## en-us Source Version

- **Repo**: `en-us` (submodule)
- **Git commit**: `3072f18c3dce6b0078f8edd2447367263560f0f7`
- **Branch**: `main`
- **Snapshot date**: 2026-11-17

## Translation Progress Overview

| Metric | Value |
| --- | --- |
| en-us source files (.md/.mdx) | 398 |
| zh-cn files (.md/.mdx) | 398 |
| en-us `_category_.json` | 43 |
| zh-cn `_category_.json` | 43 |
| File coverage | **100%** (all 398 en-us documents have corresponding zh-cn translations) |
| Content completeness | **Not certified**. File/heading coverage cannot establish semantic completeness; full source/target review is required. |
| Verbatim code blocks | Current audit reports hard code-preservation differences in **28 pages**, including comments and strings. Broken upstream fence boundaries require direct review rather than copying malformed structure. |
| Upstream inline code spans preserved | Current source-derived audit reports preservation findings; the previous **100%** claim is not a current certification. |
| Explicit heading IDs matching upstream | No heading-structure findings in the current Python scan; upstream syntax defects still require review. |
| Untranslated English prose | Current audit reports heuristic language warnings after literal/terminology exclusions; semantic review is pending. |
| Production build | 2026-11-18: **passes** with zero broken links, anchors, Markdown links, or duplicate routes after the current translation repair pass. Local sitemap synchronization is skipped without `DOMAIN`, as designed. |

### 2026-11-18 Translation repairs and focused verifier improvements

- Updated 89 Chinese documents across authentication/access, enterprise, chat/audio/search, extensibility, getting started, reference, and troubleshooting. Repairs restore upstream code comments, string values and literals; align stale navigation and instructions; and remove obsolete or duplicated content. The upstream submodule remains at `3072f18`; both trees still contain 398 documents and 43 categories.
- OpenAPI server guides restore model-reliability guidance and array-query support, and follow current integration, MCP and OAuth instructions. SSO troubleshooting distinguishes signup controls and logout scope. Manual database migration restores the revision-history explanation and matching-version requirement for offline migration. A quoted Mistral diagnostic was restored verbatim from upstream.
- Preservation checks now reject changed code comments/strings, preserve all fence directives except prose titles, protect JSON-LD technical values, and check literal-only lines. Both translation providers receive prose fence titles; filename/path titles remain literal. Source-derived quoted diagnostics inside troubleshooting/error sections stay verbatim. No translations or bilingual answer tables are hard-coded in tests; fixtures use generated CJK characters.
- Fixed demonstrated parser false positives involving dollar prices, bare-path sentence punctuation, keyword lists, backticked identifiers/product names, indented JSX children, and inline HTML examples. Broken upstream fence boundaries produce visible review signals when code comparison is unreliable; unrelated upstream parse defects never relax code preservation. No fingerprint exceptions were added.
- Validation: **99 behavior tests passed**. Full audit: **441/441 counterparts, 79 errors, 1195 warnings, 0 exceptions**. The 89 edited documents have **0 errors and 289 heuristic warnings**. The full strict audit still fails; remaining findings need triage and cannot be treated as a semantic certification. Production build passes with zero broken-link, anchor, Markdown-link, or duplicate-route diagnostics.
- Hash-bound full-pair semantic review passes for **20 edited authentication/enterprise pages**. The other **69 edited pages remain pending full semantic review** after translation agents encountered service-capacity errors. Subsequent retries ran sequentially as requested and also failed; no unfinished review was marked passed. Local audit and review artifacts are under ignored `test/.reports/`. No live DeepL requests were made.
- Updated `upstream-sync` and tooling documentation for the preservation rules and user-directed delegation/concurrency limits. The parent performs tooling, integration and verification when translation edits are assigned to sub-agents.

### 2026-11-17 Alternatives re-translation and verification refinements

**Document changes**

- `alternatives/` (13 pages) - the pages had still mirrored the May 2026 upstream text. `anythingllm`, `chatgpt` and `claude` were re-translated against the current upstream structure (new "At a Glance" tables, rewritten comparison sections, revised "When to Use Each" text), and the remaining pages were updated for the August 2026 upstream revision (last-updated date, 13 vector databases / 8 extraction engines, Gemini 3.5 Pro). Every page now keeps a 1:1 block and heading structure with its English source.
- `reference/https/haproxy.md` - the upstream base-configuration fence is never closed, so the "WebSocket and HTTP/2 Compatibility" section and its prose rendered inside one code block. The Chinese page closes the fence at the end of the base configuration, restores the section as a real heading with the upstream-derived ID `{#websocket-and-http2-compatibility}`, and turns the two malformed ` ```sudo ... ``` ` inline spans into proper shell blocks.
- `features/extensibility/plugin/tools/index.mdx` - removed a leftover block (numbered items, a duplicated link and an orphan `:::`) that no longer exists upstream, and removed a misplaced duplicate of the "Why use these?" paragraph that belongs to the Native Mode section. The "Model Quality Matters" warning still recommended superseded models; it now follows upstream, links to "Model Requirements & Caveats" and keeps the `GPU` literal.
- `features/administration/webhooks.md` - the "How it Works" section was an outdated condensed paragraph. It now follows upstream, including the `API` literal and the `(/features/channels#muting-a-channel)` link.
- `tutorials/integrations/redis.md` - the page still carried the pre-August-2026 upstream structure. The "Overview", "When is Redis Required?", "Prerequisites", "Basic Configuration" and "Optional Configuration" sections now follow the current upstream; stale warning and danger blocks, an orphaned paragraph, a moved code block and a stale troubleshooting block were removed; the missing per-room-channel paragraph and the `#persistence` link were restored.
- `reference/env-configuration.mdx`, `reference/tab-nginx/NginxProxyManager.md` - closed two admonitions that upstream closes and removed one orphan closing marker each; the DuckDNS token example now uses a proper shell block.
- `features/administration/banners.md`, `features/administration/webhooks.md` - removed UTF-8 byte order marks from the frontmatter.
- Terminology: `开放终端` was replaced by `Open Terminal` in 13 files (36 occurrences). Upstream treats it as a feature name, the Chinese page title is already "Open Terminal", and the side bar label is now `💻 Open Terminal`.
- Six pages had lost the upstream `<ThemedImage>` banner (`features/authentication-access/index.mdx`, `features/calendar/index.md`, `features/chat-conversations/data-controls/index.mdx`, `features/chat-conversations/direct-connections.mdx`, `features/notes/index.md`, `features/workspace/knowledge.mdx`). The imports and the banner block were restored with translated alt text; the banner SVG files already exist under `zh-cn/static/images/banners/`.
- Nine CVE disposition pages had lost the `<span className="badge badge--success cve-rejected">` badge and the emphasis on the REJECTED sentence; both were restored. Ten pages were missing the `---` separator before "What the CVE Claims"; it was restored with the blank lines that the Markdown rules require.
- `troubleshooting/manual-database-migration.md` - nine code fence titles were still English; they are now translated like the rest of the file.
- The last two Discord links were removed to follow the project policy; both now point at GitHub Discussions (`getting-started/quick-start/index.mdx`, `tutorials/integrations/redis.md`).

**Tooling changes**

- Literal comparison now separates dropped literals (failure) from added or re-counted literals (review signal); the previous count-based rule reported every re-counted term as a failure.
- Link destinations are compared after resolution: relative and absolute forms, `.md` and `.mdx` suffixes and links that upstream points at the English site while the translation points at its own pages compare equal. A URL only has to survive as a bare URL, a link destination or inline code.
- JSON-LD payloads are compared by structure, so translated FAQ text no longer fails the opaque-code check while a changed FAQ count still does.
- Keyword lists and layout directives (`sidebar_position`, `position`, `collapsible`, `collapsed`) are no longer treated as prose or as structure.
- Upstream parse defects are reported as warnings and downgrade block-level comparisons for that file, so a translation never has to inherit broken upstream structure. Admonition types may differ at the same position; a different admonition count still fails.
- Document suffixes are stripped completely when a destination is resolved. The previous code removed two characters instead of the matched suffix, which produced 40 false "missing destination" errors.
- Fence metadata is compared by language only, so a translated `title="..."` no longer counts as changed fence metadata; an English fence title is reported as a warning. Upstream that writes a fence marker inside a code span is a warning rather than a failure, so a translation may repair the markup.
- An interface label that upstream marks with a code span (`Settings`, `Admin Panel`, `Image Generation Engine`) may be translated, because the Chinese site shows a Chinese interface; that is a review signal. Identifiers, commands, paths, values and product names stay verbatim inside code spans.
- `non_compliant_link_patterns` in `test/translation_config.json` lists the community links the project policy removes. A listed link may be absent from the translation, a translation that keeps one is reported as `non-compliant-link`, and a code span that exists only in the removed sentence disappears with it.
- Validation: **81 behavior tests passed** on Python 3.14. Strict working-tree audit covered **441/441** files, reporting **182 errors, 1422 warnings, 0 exceptions** (down from 646 errors / 1365 warnings when the tooling landed and 272 errors after the first repair pass). The remaining findings are historical drift outside this pass and need triage, not blanket suppression. The strict audit still returns failure and semantic review remains **required**.

### 2026-11-17 Translation verification tooling

- Added the Python suite under `test/`, including source-derived completeness/preservation checks, quality warnings, full-pair AI review bundles, and validation of hash-bound semantic review results.
- Translation expectations are never hard-coded. Behavior tests use generated CJK text; only terminology and other literal exclusions are stored verbatim.
- Added autonomous AI translation tasks requiring no configuration, plus optional DeepL mode requiring only `DEEPL_AUTH_KEY` in root `.env`. Both use protected placeholders and the same guarded apply path. No live translation requests were made.
- Updated `.codex/skills/upstream-sync/SKILL.md` and fixed `AGENTS.MD` pointers for the user's `.github/` to `.codex/` skill/agent move.
- Validation: **58 behavior tests passed** on Python 3.14. CI tests Python 3.10 and 3.14. Strict working-tree audit covered **441/441** files (398 documents and 43 categories), reporting **646 errors, 1365 warnings, 0 exceptions**. These include historical differences and possible intentional localization; they require triage, not blanket suppression. Reproduce with `python test/translation_check.py --strict --report test/.reports/full-audit.json`.
- The strict audit returns failure and semantic review remains **required**. No translation edits were made or included in the tooling task; earlier uncommitted document edits remain separate. All prior audit narrative below describes historical runs, not a new semantic certification.


### 2026-11-17 Sync (en-us `36b7e50` -> `3072f18`)

Upstream range: 274 files changed, 1035 insertions(+), 4082 deletions(-).

**Removals**

- `ecosystem/computer/` — upstream dropped the entire Computer (cptr) section: 63 pages plus 9 `_category_.json` files. The Chinese tree was deleted to match, together with `getting-started/quick-start/connect-an-agent/cptr.mdx`.
- Page count moved 461 -> 398 and `_category_.json` count 52 -> 43 on both sides; coverage stays at 100%.

**Additions**

- `reference/tether-client-protocol.md` — new reference page for the native-client sign-in and the Tether handshake flow; translated.
- `static/images/tether-connect.png` — copied from `en-us/static/`.

**Major rewrites**

- `ecosystem/tether.md` — upstream rewrote the page as a product page (workspace, Spotlight screen capture, folder sandbox). The Chinese page was rewritten to the same structure and heading order.
- `features/workspace/knowledge.mdx` — new "提出第一个文档问题" walkthrough, a new "附加知识与笔记" section, a Key Features table (13 vector databases, always-use-full-text, file browser with preview), the Retrieval Modes overview, the Full Context paragraph, the reworked agentic-tools table and the scoped-access note.
- `features/open-terminal/coding-agents.md` — upstream added a "Supported Agents" table (13 agents with their interface and executable) and an "Add Another ACP Agent" section. Both were translated, and a duplicated Chinese block left by an earlier edit was removed.
- `features/chat-conversations/audio/speech-to-text/openai-stt-integration.md` — `whisper-1` now retires on 2027-02-26, a `:::caution` block lists the retiring models, `AUDIO_STT_MODEL` defaults to empty, and the troubleshooting list gained a step for OpenAI-compatible services.

**Admin-path normalization (upstream-wide)**

Upstream moved "Settings > Admin > X" to "Settings > X (admin section)" across roughly 120 pages. The Chinese pages were updated to the same wording, with the marker rendered as `（管理员区域）`. Headings that upstream re-titled also had their explicit IDs re-derived (`features/open-terminal/setup/connecting.md` now uses `{#2-go-to-settings--integrations-admin-section}`).

**Other content**

- `reference/monitoring/otel.md` — three new user gauges (`webui.users.total`, `webui.users.active`, `webui.users.active.today`) with the 3-minute window and the UTC-midnight semantics.
- `features/chat-conversations/web-search/providers/google-pse.md` — the Custom Search JSON API end date (2027-01-01) and the `google_pse` engine warning.
- `security/vendor-dispositions/cve-2024-7999.mdx` and `cve-2024-9840.mdx` — the CNA's published rejection text, and the note that the behaviour belongs to `python-multipart`.
- `security/accepted-risks/agentic-application-risks.mdx` — the capability bullet now describes creating versus using a Tool; the Security Policy reference was renumbered to Rule 9. Upstream deleted the old Rule 5, so rules 6-13 became 5-12 across the 24 affected Chinese pages.
- `reference/database-schema.md` — the `auth_session` rows now point at `/reference/tether-client-protocol` instead of the removed `/ecosystem/tether` anchor.
- `src/css/custom.css` — the monospace font-stack re-wrap was re-synced from upstream.
- `features/chat-conversations/data-controls/files.md`, `features/chat-conversations/prompt-caching.md`, `features/workspace/knowledge.mdx`, `troubleshooting/rag.mdx`, `features/notes/index.md`, `features/chat-conversations/chat-features/conversation-organization.md`, `features/chat-conversations/rag/index.md`, `features/extensibility/plugin/tools/index.mdx`, `features/extensibility/plugin/functions/filter.mdx` — the "collections" concept was replaced by "knowledge bases" throughout the Chinese text, with links to `/features/workspace/knowledge`.

**Verification**

- Production build passes: 0 broken links, 0 broken anchors, 0 broken markdown links, 0 duplicate routes.
- Explicit heading IDs re-derived from the upstream English slugs and checked against `github-slugger`: 0 mismatches, 0 Chinese headings without an ID.
### 2026-11-17 Fourth deep audit (en-us `3072f18`) — sync-omission repair and full repo re-check

A second full pass over all 398 pages after the `36b7e50 -> 3072f18` sync. Two defect classes were found and fixed: omissions introduced by the sync itself, and pre-existing drift that the earlier audits had missed.

**Sync-introduced omissions (fixed)**

- `features/chat-conversations/audio/text-to-speech/openai-tts-integration.md` — the upstream `:::caution` block (tts-1 / tts-1-hd / gpt-4o-mini-tts retire on 2027-01-06, switch to the OpenAI Realtime engine) was missing.
- `security/security-policy.mdx` — the Ground Truth block was inverted, the "other urgent issues" paragraph was missing, the tools/functions/pipelines section was stale, and the closing paragraph contradicted upstream (password change plus "sign out of all devices").
- `security/vendor-dispositions/cve-2024-7036.mdx` — one missing upstream sentence and one stale rule bullet.
- `security/vendor-dispositions/cve-2025-29446.mdx` and `cve-2025-63391.mdx` — missing rule bullets (1/6/8/12 and 1/3/7).
- 10 further CVE pages — "NVD mirrors that state" replaced the older "propagates to NVD and downstream sources" phrasing.
- `reference/env-configuration.mdx` — the `WHISPER_COMPUTE_TYPE` default and description now match upstream.
- `troubleshooting/performance.md` — the Redis table had a header but no rows; four upstream rows and the WebSocket Pub/Sub buffer paragraph were added.
- `getting-started/advanced-topics/hardening.md` — missing quick-reference row (`ENABLE_MFA=true`).
- `features/chat-conversations/chat-features/code-execution/index.md` — the Pyodide persistence cell no longer claims unconditional refresh persistence.
- `features/chat-conversations/image-generation-and-editing/usage.md` — the stale Image Edit requirement was replaced by the upstream toggle/edit-engine text.
- `features/chat-conversations/rag/index.md` — "GPT-4 Turbo 128k" became "GPT-5.6, 1M token context window"; a duplicated "并，" was removed.

**Explicit heading IDs re-derived from the upstream English slugs**

- `enterprise/index.mdx` (7 IDs), `enterprise/deployment/index.md` (3 IDs), `security/index.mdx`, `security/accepted-risks/index.mdx` (`known--accepted-risks`), `chatterbox-tts-api-integration.md`, `openai-edge-tts-integration.md`.
- `reference/api-flow.md` — the whole "API Reference" block was untranslated English without explicit IDs. It is now translated and uses `{#api-reference}`, `{#dto-structures}`, `{#chat-dto-complete-structure}`, `{#chatcompletionsrequest-dto}`, `{#chatcompletionmessage-dto}`, `{#history-dto}`, `{#message-dto-complete-structure}`.

**Verbatim inline code spans restored**

- `reference/env-configuration.mdx`, `features/chat-conversations/rag/index.md`, `features/extensibility/plugin/development/events.mdx`, `under-the-hood.mdx`, `tools/development.mdx`, `tools/index.mdx`, `features/extensibility/mcp.mdx`, `features/workspace/skills.md`, `features/chat-conversations/chat-features/chatshare.md`, `index.mdx`, `features/administration/banners.md`, `tutorials/integrations/dev-tools/jupyter.md`, `tutorials/maintenance/s3-storage.md`, `getting-started/advanced-topics/scaling.md`.
- UI menu labels inside code spans (`设置`, `音频`, `Admin Panel`) stay translated by design; only technical literals were restored.

**Pre-existing drift found by the re-check (fixed)**

- `features/chat-conversations/memory.mdx` and `features/chat-conversations/web-search/agentic-search.mdx` — stale model-tier lists and a reversed recommendation (upstream asks for a minimum tier, the Chinese text asked for a frontier model).
- `features/workspace/models.md` — stale base-model names.
- `features/chat-conversations/rag/document-extraction/index.md` — the sentence listing the four engines that have no page of their own was missing.
- `features/extensibility/plugin/tools/development.mdx` — the paragraph about the four rewritten import prefixes (`from utils`, `from apps`, `from main`, `from config`) was missing, and the pip note still claimed the UI freezes during installation.
- `features/extensibility/plugin/development/events.mdx` — the "Return Value Persistence" section was stale: the Pipes text still described `ENABLE_REALTIME_CHAT_SAVE`, and the Actions table lacked the `{"messages": [...]}` row and the correct persistence values.
- `getting-started/quick-start/connect-an-agent/hermes-agent.mdx` — "connection test passes but no models load" was replaced by upstream's current explanation.
- `getting-started/quick-start/tab-kubernetes/Helm.md` — the paragraph about the chart's default Ollama/Pipelines/Redis deployments and the 2 GiB PVC was missing.
- `troubleshooting/rag.mdx` and `faq.mdx` — the Ollama VRAM-based context-window defaults (4096 / 32768 / 262144) were missing or stale.
- `reference/https/haproxy.md`, `reference/tab-nginx/NginxProxyManager.md`, `reference/database-schema.md` — untranslated English blocks.

**Markdown structure repairs**

- `getting-started/advanced-topics/hardening.md` and `tutorials/maintenance/database.mdx` — a missing blank line turned a thematic break into an accidental setext H2.
- `troubleshooting/web-search.mdx` — same defect class.

**Audit tooling**

Ten independent detectors were run over all 398 pages: exact Docusaurus heading-ID comparison (MDX parse + github-slugger + parseMarkdownHeadingId), rendered-anchor comparison against `build/**/index.html`, upstream-added-line code-span diff, numeric-literal diff, inline code-span literal drift, table-row token diff, CVE rule-number parity, accidental setext-heading scan, untranslated-prose scan and a per-file prose-block parity diff.

**Verification**

- Heading audit: 0 issues across 398 files.
- Rendered-anchor audit: 368 pages, 14 findings, all symmetric (upstream and Chinese agree).
- `npm run build`: SUCCESS — 376 pages, 0 broken links, 0 broken anchors, 0 broken markdown links, 0 duplicate routes.

### 2026-11-14 Third deep audit (en-us `36b7e50`) — content-gap sweep, verbatim-span fidelity, heading/content realignment

Third full pass over the same upstream snapshot `36b7e50`, aimed at the defect classes the token-level detectors could not see. Four independent detectors were run over all 461 page pairs; every finding below was fixed and re-verified.

**Content gaps (227 → 0)**

A section-by-section token-coverage detector found **227 sections across ~60 files** where the Chinese text was missing upstream content entirely. All were rewritten. Highlights:

- `features/chat-conversations/chat-features/reasoning-models.mdx` — sections 0/3/9/10/12/14/17/21/23/24/26/27/28/33/35/36 rewritten.
- `features/index.mdx` — the entire `<Banner>` component and all ten `<Banner slug=.../>` usages were absent; added.
- `features/chat-conversations/chat-features/code-execution/python.md` — `openpyxl` / `python-pptx` / `python-docx` rows and `ENABLE_PYODIDE_FILE_PERSISTENCE` added.
- `security/vendor-dispositions/*` — the Timeline tables were rebuilt from upstream (missing "Still open", 2026-08-08 and 2026-08-14 rows); nine files carried a Chinese-only `### 披露途径` section that upstream does not have (removed).
- `troubleshooting/connection-error.mdx` (code blocks were outside their list items; Milvus TLS paragraph added), `troubleshooting/manual-database-migration.md` (two `<Tabs>` blocks were empty and their code blocks misplaced), `getting-started/updating.mdx` (two missing `:::info` admonitions), `mission.mdx` (upstream rewrote the mission text).

**Verbatim inline code spans (39 → 0)**

Endpoints, paths, env-var names, template placeholders and commands inside backticks must stay verbatim. A detector compared every such span in the English page against the Chinese page; **39 spans were missing or translated**, including `POST /api/v1/knowledge/{id}/files/batch/add`, `GET /api/v1/users/user/status`, `POST /openai/chat/completions`, `{{CONTEXT}}` / `{{QUERY}}` / `[context]` / `[query]`, `<server ID>_<tool name>`, `<agent>/<model>`, `{{ chat.variables.x }}`, `hf.co/{username}/{repository}:{quantization}`, `pip install --upgrade "open-webui[postgres]"`, `POST /api/tasks/chat/{chat_id}/stop`, `is_legacy_mode()` and `latest-<variant>`. All were restored, and the surrounding prose (RAG-template paragraphs, the Docker Compose v1/v2 warning, the `__chat_id__` filter caveat, the "Universal Compatibility Pattern" paragraph, the OpenAI/user-status env-var descriptions) was translated in.

**Heading title / content permutations (5 files)**

Explicit IDs are positional, so a permuted Chinese heading title still resolves its anchor but shows the wrong topic. Detected and repaired:

- `security/index.mdx` — three consecutive sections had their titles *and* bodies rotated: "Supply Chain and Security Scanners", "Chat Data Privacy & Encryption" and "Vendor Dispositions" now sit under their own IDs with their own bodies.
- `features/open-terminal/terminals/index.mdx` — the whole "Why It Matters" section (needs/benefits table, lifecycle sentence, admin-UI note) was missing, the "Deployment" / "Authentication" / "Troubleshooting" headings had shifted IDs, an empty duplicate "故障排除" heading was present, and two Authentication paragraphs (JWT mode, policy/lifecycle/status API key) were missing.
- `getting-started/quick-start/connect-a-provider/starting-with-ollama.mdx` — the "Updating and Deleting Models" section carried the "Unloading Loaded Models" body; the original "Manage dialog" paragraph was restored.
- `reference/tab-nginx/SelfSigned.md` — a stray duplicate of the "Access the WebUI" block sat under the page's first heading.
- `features/open-terminal/setup/updating.mdx` — "关于 Terminals" retitled to "运行 Terminals" to mirror the upstream heading.

**Factual and technical corrections**

- `security/vendor-dispositions/cve-2025-15603.mdx` — CVSS 3.1 vector typo (`S:U:C/L:I/N:A:N` → `S:U/C:L/I:N/A:N`).
- `security/vendor-dispositions/index.mdx` — link targets pointed at uppercase `./CVE-xxxx.mdx` (case-sensitive server breakage) → lowercase.
- `security/vendor-dispositions/cve-2024-7040.mdx` — two headings had swapped title/ID.
- `reference/monitoring/index.md` — stale model IDs `gpt-4o` / `gpt-4o-mini` → `gpt-5.6-sol` / `gpt-5.6-luna`.
- `tutorials/community/unraid.md` — claimed subpath routing works; upstream states it cannot. Rewritten.
- `tutorials/contributing-tutorial.md` — `docs/tutorial/` → `docs/tutorials/`.
- `reference/https/caddy.md` — `Caddyfile` → `CaddyFile` in prose.
- `license.mdx` — the license comparison table was brought back in line with upstream (2 stale rows removed, 1 row added).

**Second round: section-level structural defects**

A per-section prose-unit counter (paragraphs, list items and table rows, aligned by heading order) exposed a set of
defects the token-level detectors could not see, because every individual token was present somewhere on the page.

- **Collapsed or misplaced sections** - `features/chat-conversations/chat-features/message-queue.mdx` had lost the
  whole "Attachments Still Uploading" body, carried the "Persistence" body under the "Settings" heading, had three
  headings shifted by one ID and one empty duplicate heading; `tutorials/maintenance/database.mdx` had collapsed five
  export steps into two with the `docker stop` / `docker start` code blocks detached from their steps; and
  `troubleshooting/manual-database-migration.md` had lost the `<Tabs>` wrapper around the two "preview upgrade"
  code blocks and translated their upstream comments into semantically wrong ones.
- **Missing admonitions** - the `Forward cookies`, `OAuth auth type`, `Sign-in records for SCIM users`,
  `Include user_message` and "Single Session Requires Redis" blocks were absent;
  `features/extensibility/plugin/development/events.mdx` still described a 300-second default timeout that upstream
  replaced with "waits forever, configurable via `WEBSOCKET_EVENT_CALLER_TIMEOUT`", and had lost the failure-mode
  table and the example.
- **Missing prose** - `getting-started/advanced-topics/hardening.md` ("Token revocation" lost its first four
  paragraphs, including the fail-open behaviour of the revocation check),
  `features/chat-conversations/chat-features/conversation-organization.md` (the folder write-access rules),
  `features/workspace/models.md` ("Bulk management" lost the Available / Unavailable views and the Reset / Delete
  menu), `features/chat-conversations/image-generation-and-editing/usage.md` (the four preconditions for image
  generation), `getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/index.mdx` (the
  LM Studio **Provider** row and both trailing admonitions) and `troubleshooting/web-search.mdx` (the three closing
  paragraphs on persisted settings).
- **Missing `<div>` wrappers** - nine `security/vendor-dispositions/cve-*.mdx` pages had lost the
  `<div className="cve-resolved">` wrapper around the "Resolved" admonition (the CSS class exists in `custom.css`, so
  those callouts rendered unstyled), and `cve-2025-63391.mdx` was missing its entire `<div className="cve-refutation">`
  block.
- **Untranslated admonition titles** - 25 titles across 12 files were still English
  (`:::danger SQLite is only supported on locally-attached SSD/NVMe`, `:::warning Multi-replica deployments REQUIRE PostgreSQL`,
  `:::info OAuth Scopes`, ...) and were translated.


**Verification (all green)**

| Check | Result |
| --- | --- |
| `npm run build` (zh-cn, `onBrokenLinks`/`onBrokenAnchors`/`onDuplicateRoutes` = `throw`) | **SUCCESS** - 0 broken links / anchors / markdown links / duplicate routes |
| Content-gap detector (token coverage per section) | **0** sections missing content |
| Verbatim inline code spans | **0** missing |
| Code-block parity | EN 1441 blocks - **1441 identical**, 0 EN-only, 0 zh-cn-only |
| Code-block placement | **0** violations |
| Identifiers lost inside code blocks | **0** |
| Diverging code blocks | 1433 paired, 1387 identical, 46 diverging - all intentional (translated comments, translated strings, translated mermaid labels) |
| Heading parity | 0 heading-count mismatches, 0 explicit-ID mismatches, 0 headings without an ID |
| Explicit-ID hygiene | 0 IDs inside code blocks, 0 unescaped underscores |
| `TODO` parity (EN vs ZH) | 14 / 14, all matched |
| CJK-literal anchors, U+FFFD characters | **0** |
| Section misalignment detector (ZH section vs. best-matching EN section) | **0** real mismatches |
| Untranslated admonition titles | **0** (product names such as *Docker Hub* / *OpenShift* excluded) |
| Prose-unit parity per section | 51 sections differ by >= 2 units - sampled, see `Todo.md` §2.1 |

### 2026-11-13 Second deep audit (en-us `36b7e50`) — structural realignment, anchor escaping, code-span fidelity

A second full audit of all 461 Chinese documents against the same upstream snapshot, focused on the classes of defect the first pass could not see because its anchor check **skipped every file whose heading count differed from upstream**. 35 files were structurally out of sync, and that defect class had been hiding 458 anchor mismatches.

**Structural drift fixed (35 files)**

- Every Chinese section list was re-aligned to the upstream section list by explicit-anchor identity: stale duplicate sections (e.g. a second copy of "Configuration" carrying the upstream `timeline` fragment), sections that upstream had deleted, and sections that upstream had renamed were removed, merged or re-anchored. Affected: `security/vendor-dispositions/cve-*.mdx` (9 files), `troubleshooting/rag.mdx`, `tutorials/integrations/redis.md`, `troubleshooting/image-generation.md`, `getting-started/advanced-topics/{hardening,scaling}.md`, `getting-started/quick-start/index.mdx` and the Docker/Python tab fragments, `reference/tab-nginx/LetsEncrypt.md`, `reference/monitoring/index.md`, `security/security-policy.mdx`, `features/chat-conversations/chat-features/{reasoning-models,follow-up-prompts}.mdx`, `features/extensibility/plugin/{index,functions/pipe}.mdx`, `features/open-terminal/index.md`, `features/administration/{webhooks,api-keys}.md`, `features/chat-conversations/web-search/providers/exa.md`, `features/chat-conversations/rag/document-extraction/apachetika.md` and `features/extensibility/plugin/development/events.mdx`.
- Heading **levels** were corrected to match upstream (e.g. `## 网络放置` had been demoted to `###`, `## 创建管理员账户` had been promoted to `###`).
- `tutorials/maintenance/offline-mode.mdx` and `troubleshooting/image-generation.md` were rewritten against the upstream section structure (the upstream restructure from "Approach I/II" to "Prepare while connected / Prepare a machine that is already offline" and the "Common Issues / ComfyUI Issues / Automatic1111 Issues" grouping).
- `reference/database-schema.md` had an entire extra "Disclosure Pathway" block and three SQLCipher sections that upstream removed.

**Anchor escaping (silent ID corruption)**

- An explicit ID containing a double underscore (`{#__id__}`, `{#events-using-__event_emitter__-and-__event_call__-in-open-webui}`) is parsed as markdown **emphasis**, so Docusaurus generated `#id` / `#events-using-event_emitter-and-event_call-in-open-webui` and every upstream link to it broke. The correct form escapes the underscores (`{#\_\_id\_\_}`), which renders to the same anchor without triggering the emphasis parser. **1 002 anchors across 29 files** were repaired, and the build now resolves the previously broken `#execute-works-with-both-__event_call__-and-__event_emitter__` and `#__id__` links.

**Upstream behaviour that the Chinese pages contradicted**

- **SQLCipher is no longer supported upstream** (`DATABASE_TYPE=sqlite+sqlcipher` makes Open WebUI refuse to start). `reference/database-schema.md` and `getting-started/advanced-topics/hardening.md` still documented it as a supported feature, including a "Prerequisites / Configuration / Important notes" walkthrough and `DATABASE_TYPE`/`DATABASE_PASSWORD` env-var rows. Both pages now describe the upstream "not supported" behaviour and point at the decryption procedure for existing databases.

**Code-span fidelity (851 inline code spans were translated or dropped)**

- Inline code is code and must stay verbatim. Examples repaired: `placeholder="Enter name"` / `options=["High","Medium","Low"]` / `label="Include analysis"` restored in `features/workspace/prompts.md`; `Cost = (input_tokens × input_price) + (output_tokens × output_price)` restored in `features/administration/analytics/index.mdx`; upstream model IDs restored (`voxtral-mini-2602`, `qwen3.5:0.8b`, `agent:claude/claude-sonnet-5`, `openrouter/gpt-5.6-sol`, `muse-glimmer:30b-q4_K_M`); `@mentions` / `@mention` spellings restored in `features/channels/index.md`.
- `reference/database-schema.md` was rebuilt table-by-table from upstream: column names, data types and constraints are verbatim, all 132 description cells translated, and every missing row (13 new tables, `mfa`/`session_stamp`, the channel-member columns, the message `app_id`/`reply_to_id`/pin columns, the user status columns) restored.

**Missing screenshots**

- 13 Chinese pages referenced **no screenshot at all** although upstream had one; the image references (with translated alt text) were added: `features/authentication-access/index.mdx`, `features/authentication-access/rbac/index.mdx`, `features/chat-conversations/audio/index.mdx`, `features/chat-conversations/image-generation-and-editing/index.mdx`, `features/chat-conversations/chat-features/conversation-organization.md`, `features/chat-conversations/chat-features/code-execution/python.md`, `features/chat-conversations/rag/index.md`, `features/extensibility/plugin/tools/index.mdx`, `features/workspace/models.md`, `features/workspace/prompts.md`, `troubleshooting/performance.md`, `tutorials/maintenance/backups.md`, `features/open-terminal/index.md`. All referenced assets already existed under `zh-cn/static/`.

**Verification (all green)**

| Check | Result |
| --- | --- |
| `npm run build` (zh-cn) | SUCCESS — 0 broken links, 0 broken anchors, 0 broken markdown links, 0 duplicate routes |
| Explicit-ID parity vs upstream (5 964 headings) | 0 mismatched, 0 CJK headings without an ID, 0 duplicate IDs |
| Heading-count parity (EN vs ZH) | 0 files differ (previously 35) |
| Links to Chinese-literal anchors | 0 |
| U+FFFD replacement characters | 0 |
| TODO-comment parity | 14 = 14 across 7 files |
| Image reference parity | 1 intentional difference (the Discord badge, removed by policy) |
| Sections with genuinely missing upstream content | 238 remaining, down from 326 after the structural pass (each is one upstream paragraph, table row or list item in a single page) |

**New conventions recorded in `AGENTS.MD` §6**: explicit IDs must escape underscores when they contain `__`, and the heading-structure audit must compare section lists even when the two files have different heading counts.

### 2026-11-13 Deep translation audit (en-us `36b7e50`) — build-blocking and content-completeness repairs

A full translation-completeness audit of all 461 zh-cn documents against the en-us snapshot. The dominant defect class was **anchor IDs that did not match upstream**, which broke upstream cross-page links; the second class was **stale duplicated blocks** left behind by earlier bulk edits.

**Build blockers fixed (the site did not compile at all before this pass)**

- `getting-started/quick-start/index.mdx` and `getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/index.mdx` failed MDX compilation with `Could not parse expression with acorn`. Root cause: explicit IDs (`{#id}`) on **indented** headings inside `<TabItem>` blocks. Docusaurus only escapes `{#id}` on column-0 headings, so the brace was parsed as a JSX expression. Fixed by escaping the brace (`\{#id}`); the anchors still resolve to the upstream IDs.
- `reference/https/haproxy.md` and `reference/api-flow.md` carried a `{#...}` ID appended to a **shell comment inside a fenced code block** (`# ... other settings {#-other-settings}`, `# Clean the response ... {#clean-the-response-remove-markdown-wrappers}`). Removed — code blocks are now byte-identical to upstream.

**Anchor defects fixed (upstream links resolved to nothing)**

- Six pages had an H2 that duplicated the H1 title with the two anchors swapped, so the upstream anchor landed on the wrong heading: `reference/api-flow.md`, `reference/https/{cloudflare-tunnel,nginx,ngrok,tailscale}.md`. The stale duplicate H2 was removed and the upstream ID restored on the H1.
- `security/accepted-risks/index.mdx` had a duplicated **威胁模型** section and three permuted IDs (`{#known-amp-accepted-risks-2}`, `{#why-we-accept-these}` on the wrong heading). The two sections were merged into one upstream-matching **威胁模型** block.
- `security/accepted-risks/auth-timing.mdx` had a near-duplicate H4 section; removed and the ID corrected.
- Four links pointed at auto-generated Chinese/URL-encoded anchors (`#初始设置`, `#markdown-标题拆分`, `#威胁模型`, `#剩余部分及为何不可修复`) and are now explicit upstream IDs. **Zero** Chinese-literal anchor links remain.

**Content completeness**

- `reference/env-configuration.mdx` (919 variables): 123 sections were structurally out of sync. 14 variable sections were **completely empty**, 40 table header rows and **132 table description cells** were still English, 6 built-in prompt templates had been translated (violating the "do not translate code blocks" rule) and were restored to upstream, and a stale duplicate of the whole Valkey section plus a stray `UVICORN_WORKERS` block had been spliced into unrelated sections. All repaired.
- `reference/database-schema.md`: all table header rows and 132 description cells translated; remaining English cells are SQL keywords (`PRIMARY KEY`, `NOT NULL`, …) and are correctly left alone.
- `reference/api-endpoints.md`: the Chat Completions section had been truncated to two lines; the full upstream section (parameter retention, model controls, `usage` handling, provider errors) was restored, and the Anthropic Messages API section regained the native-connection note, extended thinking, reasoning effort, structured outputs and passthrough parameters.
- `features/extensibility/plugin/development/reserved-args.mdx`: `body` regained the `inlet()`/`request()` note, `__user__` regained the full field list, `__metadata__` regained `user_agent` / `internal` / `user_message` / `automation_id` / `filter_ids` / `chat_variables` / the `params` object, and `__event_call__` regained the timeout semantics.
- `features/authentication-access/auth/sso/index.mdx`, `features/chat-conversations/rag/index.md`, `features/extensibility/plugin/functions/action.mdx`: missing upstream paragraphs, table rows and list items restored.
- Six headings that were still pure English were translated: `features/open-terminal/setup/connecting.md` (Chat Uploads / Working Directory Context / User Shell Tools / AGENTS.md), `features/open-terminal/setup/updating.mdx`, `features/open-terminal/terminal-pane.md`, `features/open-terminal/use-cases/creating-files.md`, `features/open-terminal/terminals/orchestration/contexts.md`, `tutorials/integrations/dev-tools/iterm2.md`, plus `features/extensibility/plugin/functions/filter.mdx` (Toggleable Filters vs. Always-On Filters).

**Verification (all green)**

| Check | Result |
| --- | --- |
| `npm run build` (zh-cn) | SUCCESS — 0 broken links, 0 broken anchors, 0 broken markdown links, 0 duplicate routes |
| Explicit-ID parity vs upstream (4 149 headings) | 0 mismatched, 0 CJK headings without an ID, 0 duplicate IDs |
| TODO-comment parity | 14 = 14 across 7 files |
| Links to Chinese-literal anchors | 0 |
| U+FFFD replacement characters | 0 |
| Heading-count parity (EN vs ZH) | 0 files with fewer headings than upstream |
| Code blocks in `reference/env-configuration.mdx` | 36 byte-identical to upstream, 0 translated |
| Untranslated English prose | 102 lines, all verified benign (66 link lists, 8 code identifiers/paths, 4 upstream TODO comments, 3 error-message strings, 3 UI/config labels, 18 brand/product names) |

**New conventions recorded in `AGENTS.MD` §6**: explicit IDs must be derived from the *English* heading (not the Chinese title), IDs inside JSX blocks must be brace-escaped, and IDs must never be placed inside a fenced code block.

### 2026-11-11 Sync (en-us `cb24519d` -> `36b7e50`)

Large upstream update - 52 new upstream commits covering Channels (encrypted chats, apps, building apps), Open Terminal workspaces, the Community platform, deployment guides, the supply-chain security section, model controls, prompt caching, skills, and a large `reference/env-configuration.mdx` expansion.

- **File set**: en-us grew from 409 -> 461 documents (+52) and 49 -> 52 `_category_.json`. Every en-us path has a zh-cn counterpart (100% file coverage).
- **New / moved upstream directories**: `features/channels/`, `features/open-terminal/`, `ecosystem/community/`, `getting-started/deployment/`, `security/supply-chain-security/` (with `vulnerability-databases/`). `features/extensibility/pipelines/` was removed upstream and deleted from zh-cn.
- **New top-level documents translated**: `features/chat-conversations/chat-features/voice-mode.mdx`, `reference/server-side-tool-calling.md`, plus the Channels apps pages, the deployment guides (AWS ECS, Azure Container Apps, Docker Swarm, Google Cloud Run, Kubernetes), and the accepted-risks / vendor-disposition pages.
- **`reference/env-configuration.mdx`**: rebuilt from the upstream skeleton - 919 environment variables in upstream order, 130 h2/h3 headings, 98 explicit anchor IDs; the image-generation provider block (OpenAI DALL-E / Gemini / ComfyUI / AUTOMATIC1111) was rewritten, and an unterminated code fence plus an orphaned `no_proxy` block were repaired.
- **Anchor normalisation**: every Chinese heading that mirrors an upstream heading now carries the upstream fragment as an explicit ID (e.g. `{#model-controls}`, `{#version-history}`, `{#selected-and-pinned-models-admin}`), so upstream cross-page links resolve on the Chinese site.
- **Section parity**: `features/workspace/models.md`, `features/workspace/skills.md`, `features/extensibility/plugin/tools/index.mdx`, `features/extensibility/mcp.mdx`, `troubleshooting/performance.md`, `troubleshooting/connection-error.mdx`, `getting-started/advanced-topics/scaling.md` and `reference/api-endpoints.md` were brought back to the upstream heading order and gained the missing sections (model controls, tool approval, tool search, MCP elicitation, MCP apps, per-room Redis channels, WebSocket heartbeats, JSON encoder, DNS resolver, token counting, ...).
- **Site code**: `zh-cn/src/`, `zh-cn/scripts/`, `zh-cn/package.json` and the localized `zh-cn/docusaurus.config.ts` were re-synced from the upstream submodule (upstream's PostHog module stays vendored but inert on the Chinese host).
### 2026-11-12 Sync (en-us `36b7e50` — structural and anchor repairs)

Second pass over the `36b7e50` snapshot: section parity, heading-order repair, anchor normalisation and full production-build validation.

- **Section parity**: all 461 en-us documents now have a matching Chinese section for every upstream heading (verified section-by-section against the upstream skeleton). Restored or added the last missing upstream sections, e.g. `features/extensibility/plugin/development/valves.mdx` (full rewrite — the Chinese page had upstream blocks inserted inside code fences), `getting-started/quick-start/connect-a-provider/index.md` (`Looking for Agents?`), `getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/index.mdx` (`Official Partners`, `The Provider Setting`, `From the model selector`, `Step 2: Start Chatting!`), `reference/api-endpoints.md` (RAG intro), `reference/database-schema.md` (`Memory Table`, `Entity Relationship Diagram`, plus the missing `Comment Table`) and `troubleshooting/manual-database-migration.md` (`"Duplicate Emails" Migration Failure`).
- **Heading order**: Chinese section order was realigned to the upstream order in the affected pages (e.g. `reference/database-schema.md`, `features/extensibility/plugin/development/valves.mdx`).
- **Anchor normalisation**: every explicit Chinese heading ID was re-derived with the upstream `github-slugger` slug so upstream cross-page anchors resolve exactly (10 previously mismatched IDs fixed, e.g. `{#appbackend}`, `{#import--export}`, `{#step-5-share-file-storage-across-instances}`, `{#example-specifying-action-frontmatter}`, `{#owning-retrieval-with-file_handler}`).
- **Markdown escaping**: explicit IDs containing `__` (e.g. `{#execute-works-with-both-__event_call__-and-__event_emitter__}`) are written with escaped underscores (`\\_\\_`) so the markdown emphasis parser does not swallow them.
- **Frontmatter parity**: `description` and `sidebar_label` were added to the 9 Chinese pages that lacked them, and the `slug: /features/extensibility/community` frontmatter was restored on `ecosystem/community/plugins.mdx` (Chinese links updated accordingly).
- **Duplicate page removed**: `reference/tab-nginx/NginxProxyManager.md` had a duplicated half-page; it was rewritten from the upstream source.
- **Verification**: production build (`onBrokenLinks`, `onBrokenAnchors`, `onDuplicateRoutes` all `throw`) completes with zero broken links and zero broken anchors; static assets are in sync (376 en-us files, all present in zh-cn).

### 2026-11-12 Sync (en-us `36b7e50` — content parity pass)

Third pass over the same `36b7e50` snapshot, focused on content that was still missing or untranslated inside otherwise complete pages.

- **Built-in system tools reference** (`features/extensibility/plugin/tools/index.mdx`): the whole "Builtin System Tools" / "Tool Reference" / "Disabling Builtin Tools" / "Granular Builtin Tool Categories" half of the page was rebuilt from upstream. It now carries every upstream tool row (`display_file`, `list_memory_paths`, `read_memory_path`, `update_memory`, `read_skill_file`, `grep_skill_files`, `update_skill_files`, `create_skill`, `create_tool`, `ask_user`, `delegate_task`, `timer`, `notify`, `play_animation`, `search_tools`, `call_tool`), the missing `Attached Chat Files` section, the corrected heading IDs (`{#knowledge-tool-availability-at-a-glance}`, `{#tool-reference}`) and the refreshed minimum-model list (GPT-5.6 Luna, Gemini 3.5 Flash-Lite, MiniMax M3, DeepSeek V4 Flash, Muse Glimmer 30B, Qwen 3.6 27B).
- **Alternatives comparison pages** (10 files under `alternatives/`): the "What Open WebUI Does Well" sections were rewritten from upstream so they now advertise the agentic platform, builtin tools, MCP servers, sub-agents, timers and automations; `alternatives/anythingllm.mdx` was ported to the new upstream structure (agent-tools paragraph, updated AnythingLLM feature list, refreshed FAQ JSON-LD).
- **Chat features overview** (`features/chat-conversations/chat-features/index.mdx`): rebuilt from upstream — the page had lost the four screenshots, the chat-input trigger table, the built-in slash-command table (`/compact`, `/status`, `/fork`, `/side`, `/comments`, `/model`, `/settings`, `/compare`, `/skills:create`, `/temporary`), the link-rendering note and the structured-response editor section; a stray `sidebar_position` line and the missing banner were also fixed.
- **RBAC permissions** (`features/authentication-access/rbac/permissions.md`): the workspace / sharing / chat permission tables were completed from upstream (hidden models, skills import & export, folders sharing, open chat sharing, allow-sharing-with users & groups, web upload, chat export & import, allow call, side chat, enforce temporary chat, encrypted channels) and two corrupted table rows (automations / user webhooks) were repaired.
- **Computer deprecation**: upstream marked Open WebUI Computer as gradually deprecated. `ecosystem/computer/choose.md` and `ecosystem/computer/index.md` were rewritten from upstream, and the deprecation notice was added to `ecosystem/computer/quickstart.md`, `getting-started/quick-start/connect-an-agent/cptr.mdx` and `getting-started/quick-start/connect-an-agent/index.md`.
- **Features landing page** (`features/index.mdx`): counts refreshed (13 vector databases, 8 extraction engines, GPT-Image) and the missing rows were added (file browser, model controls, version history, channel apps, MFA, default interface settings, scaling guide).
- **Brand page** (`brand.mdx`): the logo-asset block with its download links was restored and a duplicated "asset source" section was removed.
- **Remaining stray English**: untranslated paragraphs in `filter.mdx`, `pipe.mdx`, `installation.mdx`, `building-apps.md`, `channels/index.md`, `nginx.md`, `rag.mdx` and `env-configuration.mdx` were translated, and the misplaced `AUTOMATION_MIN_INTERVAL` block in `reference/env-configuration.mdx` was put back into upstream order.
- **MCP page** (`features/extensibility/mcp.mdx`): the heading IDs were realigned (they had drifted by one), and the upstream `Connecting an account` section, the OAuth discovery fallback for servers without discovery documents, the `ENABLE_DIRECT_INTEGRATIONS` note, the custom-forwarded-headers explanation and the extended troubleshooting steps were added.
- **Notes page** (`features/notes/index.md`): the heading IDs were repaired, the notes-list screenshot added, and the upstream chat-sidebar behaviour, access-control sharing model, formatting, quick-creation and quick-delete sections were ported.
- **Knowledge page** (`features/workspace/knowledge.mdx`): the `File limits` and `Browsing and previewing files` sections were added, the heading IDs were realigned to upstream (`{#organizing-into-directories}`, `{#renaming-files}`, `{#syncing-a-local-directory}`), and the `kb_exec` output/grep caps, the `view_file` pagination limits and the access-control paragraph were ported.
- **Troubleshooting index** (`troubleshooting/index.mdx`): the missing symptom-lookup rows (blank replies on tool calls, intermittent name lookups, per-room Redis channels, file limits, link/YouTube attachments, Responses-format providers, SSO id-token parameters, MFA requirements and authenticator recovery) were added.
- **Character corruption**: repaired invalid characters in `reference/api-endpoints.md` headings and in two `reference/env-configuration.mdx` paragraphs.
- **Verification**: production build passes with zero broken links, zero broken anchors and zero duplicate routes; 1345 internal links and anchors were re-checked against the generated HTML.

### 2026-11-13 Sync (en-us `36b7e50` — full heading-parity and stray-prose pass)

Fourth pass over the same `36b7e50` snapshot. The previous passes had already reached 100% *file* coverage and section-level parity on most pages, but a strict heading-by-heading comparison against the upstream skeleton still found **247 upstream headings without a Chinese counterpart** across 60 files, plus a number of stale duplicated blocks and stray English fragments. All of it is now resolved.

- **Heading parity (247 sections ported)**: every upstream heading in `en-us/docs` now has a matching Chinese section. The largest restorations were `getting-started/essentials.mdx` (rewritten from upstream in full — Plugins, Tool Calling, Task models, Context management, Basic RAG, Web Search, Open Terminal, Computer, next steps, troubleshooting, questions), `features/chat-conversations/chat-features/history-search.mdx` (`Working with results`, `Filter prefixes` and the refreshed sidebar/search sections), `features/chat-conversations/chat-features/automations.mdx` (`Notes`, `Export and Import`, `Scheduling`, the `Giving a Run a Terminal` and `Quick delete` sections), `features/extensibility/plugin/functions/filter.mdx` (`Write it to be idempotent`, `Other things to watch for`, `The recipe`, `Caveat`, the Responses API filtering example and the `Valves are resolved once per response` note), `features/extensibility/plugin/tools/development.mdx` (`Method Docstrings`, `Return Values`, `Detecting the Mode in Your Tool`, `file_handler`), `security/vendor-dispositions/index.mdx` (the CVE-system background, the "we are not the only ones" section and `All Dispositions`), `features/calendar/index.md` (repeat events, sharing calendars), `getting-started/quick-start/settings.md` (instance-wide starting values, common scenarios), `troubleshooting/performance.md` (connection pool sizing, thread pool size, vector database), `tutorials/integrations/redis.md` (prerequisites, persistence) and `troubleshooting/web-search.mdx` (sections 4 and 5).
- **Anchor normalisation**: every Chinese heading ID was re-derived from the upstream slug, so all upstream cross-page anchors resolve on the Chinese site. Drifted IDs were repaired in `features/calendar/index.md`, `features/chat-conversations/memory.mdx`, `features/extensibility/plugin/development/rich-ui.mdx`, `features/extensibility/plugin/functions/event.mdx`, `features/extensibility/plugin/functions/filter.mdx`, `features/extensibility/plugin/tools/development.mdx`, `features/extensibility/plugin/tools/openapi-servers/open-webui.mdx`, `reference/tab-nginx/{Windows,SelfSigned,NginxProxyManager}.md`, `tutorials/integrations/redis.md` and `troubleshooting/performance.md`; the in-page links that pointed at the old Chinese fragments were updated accordingly.
- **Stale duplicates removed**: `features/chat-conversations/chat-features/{automations,chatshare}.mdx`, `features/calendar/index.md`, `security/security-policy.mdx`, `reference/tab-nginx/{Windows,SelfSigned}.md` and `features/extensibility/plugin/tools/development.mdx` carried an older copy of a section next to the current one; the outdated copies were dropped.
- **Stray English translated**: the remaining untranslated prose in `reference/env-configuration.mdx` (admonition titles), `reference/database-schema.md` (tag table notes), `features/extensibility/plugin/tools/development.mdx` (status event structure), `security/supply-chain-security/vulnerability-databases/incibe.mdx` (duplicate-CVE notes) and `features/chat-conversations/chat-features/conversation-organization.md` (sample system prompt), plus the last English frontmatter titles and page headings (`Task Models`, `Translations`, `API Keys`, `Two-Factor Sign-In (MFA)`, `Apps`, `Encrypted Chats`, `Comments`, `Keyboard Shortcuts`, `Notifications`, `Sub-agents`, `Timers`, `External Document Extraction`, …).
- **Content corrections**: Service Worker behaviour in `troubleshooting/connection-error.mdx` (upstream registers none), the "Open WebUI backend required" section that had lost its heading, the `PATCH operations` and `externalId` sections of `features/authentication-access/auth/scim.mdx`, the Gemini/OpenAI image-engine endpoint settings, the Redis persistence interval (30 seconds, not 30 minutes) and the vector-database placement in `troubleshooting/performance.md`.
- **Verification**: production build (`onBrokenLinks`, `onBrokenAnchors`, `onDuplicateRoutes` all `throw`) completes with zero broken links and zero broken anchors; 1416 in-page links checked, 0 broken; heading parity check reports 0 missing upstream headings; 0 U+FFFD characters in the whole `zh-cn/docs` tree.
- **Edit links fixed**: `zh-cn/docusaurus.config.ts` still pointed at the old `https://github.com/GamblerIX2/open-webui-docs/blob/main` fork, so every “编辑此页” button on the Chinese site linked to the wrong repository. `editUrl` is now `https://github.com/SMYQH/openwebuidocs/blob/main/zh-cn`, which renders as `https://github.com/SMYQH/openwebuidocs/blob/main/zh-cn/docs/<path>` for every Chinese page. The stale fork link in `zh-cn/docs/contributing.mdx` was removed as well, and `AGENTS.MD` now documents the Chinese edit-link target.

## Outstanding

- **`alternatives/` (13 pages)** — the earlier audit recorded pre-existing drift against the August 2026 rewrite. Correction edits from before the tooling task remain uncommitted; a complete semantic re-review is still pending. No translation work was authorized in the tooling task.
- **HAProxy rendering** — the earlier audit recorded malformed upstream fences in `reference/https/haproxy.md`. Uncommitted Chinese rendering repairs predate the tooling task and still need rendered-content verification. The upstream submodule was not modified.

## Deployment Configuration

- **2026-07-25**: Added build-time sitemap synchronization. `zh-cn/scripts/sync-sitemap.mjs` downloads the official `https://docs.openwebui.com/sitemap.xml`, rewrites its origin from the `DOMAIN` secret, and publishes it as `zh-cn/build/sitemap.xml`. Docusaurus's built-in sitemap is disabled to prevent conflicting output.
- **2026-07-25**: Enabled strict broken-anchor validation with `onBrokenAnchors: "throw"`; production builds now fail on broken links or anchors.
- **2026-07-25**: Switched Chinese site deployment to GitHub Actions CI/CD → Cloudflare Workers. Workflow: `.github/workflows/deploy.yml`. Required repository secrets: `DOMAIN` (site URL), `TOKEN` (Cloudflare API Token), `ID` (Cloudflare Account ID). Triggers on push to `main` (relevant paths) and `workflow_dispatch`.
- **2026-07-22**: Added root-level Cloudflare Workers configuration for the Chinese site (`wrangler.jsonc` assets from `zh-cn/build/`).

## Structural Differences

| Difference | Description |
| --- | --- |
| `en-us/docs/ecosystem/` | **New section**: Ecosystem (Computer + Knowledge Base Sync) — fully translated |
| `en-us/docs/security/accepted-risks/` | **New section**: Known & Accepted Risks — 4 files fully translated |
| `en-us/docs/security/vendor-dispositions/_category_.json` | Added for zh-cn (📄 Vendor Dispositions) |

## Fixed Issues

### 2026-07-25 Link and Anchor Integrity

- Fixed **116 broken-anchor references** covering **65 unique targets** across the Chinese documentation.
- Added stable explicit English-compatible IDs to translated headings, including Web Search, Audio, security reporting, knowledge tools, plugin events, Redis, scaling, database schema, and troubleshooting sections.
- Restored missing structure in `reference/env-configuration.mdx`: closed an unterminated admonition and restored the `web-search` and `audio` section headings.
- Restored the missing concurrency and multiple instances section in `features/extensibility/plugin/development/under-the-hood.mdx`.
- Updated same-page and cross-page links to use explicit stable IDs instead of translated or URL-encoded automatic heading fragments.
- Verification: clean-cache production build generated 378 documentation pages with zero broken links, zero broken anchors, and exit code 0.

### 2026-07-25 Sync (en-us `d412c345` → `cb24519d`)

Minor upstream update — 11 commits covering Docker tag docs, version placeholder usage, and expanded CVE vendor dispositions:

- **Docker tag documentation (ManualDocker.md)**: Added "How the tags update" section explaining rolling vs pinned tags (`:main`/`:latest`/`:dev` vs `:vX.Y.Z`/`:git-<sha>`). All pinned version examples changed from concrete versions to `vX.Y.Z` placeholders.
- **Version placeholders (updating.mdx)**: Replaced concrete version examples (`:v0.8.6`, `v0.10.1`) with `:vX.Y.Z` placeholders across table and code blocks.
- **Link extensions (accepted-risks/index.mdx, vendor-dispositions/index.mdx)**: Added `.mdx` extensions to all internal relative links to match en-us conventions.
- **CVE vendor dispositions (25 files)**:
  - **9 new CVE files translated**: cve-2024-7036 (DoS via Oversized Signup Name), cve-2024-7037 (Path Traversal in Pipeline Upload), cve-2024-7045 (Prompt Disclosure), cve-2024-7046 (Admin Details Disclosure), cve-2024-7053 (Session Fixation), cve-2024-7990 (Stored XSS), cve-2024-8060 (Audio Transcription Path Traversal), cve-2024-12534 (Sign-in DoS), cve-2024-12537 (Code Format DoS).
  - **12 existing files updated**: `sidebar_position` values realigned to match new sorting order; "Disclosure Pathway" section standardized (moved to after timeline, before CVE claims).
  - **vendor-dispositions/index.mdx**: Table restructured — added "Issuing CNA" column, updated column headers, added 9 new CVE rows, added `.mdx` to links. All entries now include issuing CNA attribution (huntr/Protect AI, Zero Day Initiative, VulDB, MITRE).
- **File count**: en-us source files increased from 400 → 409 (9 new CVE disposition files).

### 2026-07-22 Sync (en-us `bb2f9782` → `d412c345`)

Minor upstream update — 7 commits covering contact link updates, CVE page refinements, and provider additions:

- **Enterprise contact links (13 files)**: All `mailto:sales@openwebui.com` links replaced with `https://openwebui.com/contact/sales` across `architecture.md`, `customers/index.mdx`, `customization.md`, `deployment/container-service.md`, `deployment/index.md`, `deployment/kubernetes-helm.md`, `deployment/python-pip.md`, `index.mdx` (2 occurrences), `integration.md`, `partners.md`, `security.md` (2 occurrences), `sovereign-ai.mdx`, `support.md`.
- **CVE vendor disposition refinements (9 files)**:
  - cve-2024-7033, cve-2024-7034, cve-2024-7038, cve-2024-7039, cve-2024-7040, cve-2024-7959: Added `:::tip 已解决：此 CVE 现已被拒绝` block unifying the resolved status message.
  - cve-2024-7033: Enhanced the traversal analysis paragraph to include the host allowlist's purpose and scope.
  - cve-2026-0765, cve-2026-0766, cve-2026-0767: Renamed `### CVSS 准确性` → `### 严重性` and rewrote section to align with intended-behavior disposition framework.
- **Vercel AI Gateway (1 new provider)**: Added Vercel AI Gateway tab to `starting-with-openai-compatible.mdx` (connection settings + tip), entry in model detection table, and mention in provider overview table.
- **CORS hardening (hardening.md)**: Added section on disabling CORS entirely via `CORS_ALLOW_ORIGIN=http://cors.invalid`.
- **SERPHouse link update (serphouse.md)**: Updated documentation URL from `www.serphouse.com/docs` to `docs.serphouse.com/`.

### 2026-07-18 Sync (en-us `f07c2a61` → `bb2f9782`)

Minor upstream update — CVE vendor dispositions resolved:

- **CVE status updates (6 CVE files)**: CVE-2024-7033, CVE-2024-7034, CVE-2024-7038, CVE-2024-7039, CVE-2024-7040, CVE-2024-7959 — all withdrawn by the issuing CNA (huntr / Protect AI) on 2026-07-16; records now in **REJECTED** state. Each file updated with Official Resolution row in overview table, new timeline entry for the withdrawal, and revised closing paragraph.
- **CVE-2024-7040**: Extended timeline with 4 additional entries covering the Root routing, CNA review, withdrawal, and dispute closure.
- **index.mdx**: Status column updated from "处理中" (In progress) to CNA REJECTED badge for all 6 resolved CVEs.

### 2026-07-17 Sync (en-us `b9ee002e` → `f07c2a61`)

This was a **major upstream update** spanning ~100+ commits. Key changes:

- **New section — Ecosystem & Computer**: Translated the entire `ecosystem/` directory:
  - `ecosystem/index.md` — Ecosystem overview
  - `ecosystem/computer/` — 63 files covering Computer (cptr): AI features, automation, installation, operation, remote access, reference, use cases (15 scenarios), workspace, FAQ, troubleshooting
  - `ecosystem/knowledge-base-sync/` — oikb daemon and overview (moved from `features/knowledge-base-sync/`)
- **New section — Security Accepted Risks**: 4 new files (`accepted-risks/`): index, agentic-application-risks, auth-timing, llm-output-unpredictability
- **New security files**: `chat-data-privacy-and-encryption.mdx`, `supply-chain-security.mdx`, `troubleshooting/startup.mdx`
- **New features files (20)**: audio/index, image-generation-and-editing/index, chat-conversations/index, web-search/index + providers (firecrawl, microsoft-web-iq, serphouse), extensibility/community, plugin/functions/event, workspace/index, administration banners/evaluation/index, authentication-access api-keys/sso/rbac, calendar, channels, open-terminal/terminals/orchestration (10 files)
- **CVE vendor-disposition files (5 new)**: cve-2024-7033, cve-2024-7034, cve-2024-7038, cve-2024-7039, cve-2024-7959
- **Enterprise**: `sovereign-ai.mdx` new; `security.md` and `index.mdx` significantly expanded
- **Major updates**:
  - `reference/env-configuration.mdx` — v0.9.6→v0.10.0: 41 new env vars (IFRAME_CSP, ENABLE_KB_EXEC, VALKEY_*, LINKUP_API_KEY, CONTEXT_COMPACTION_*, LDAP section, SCIM section, User Permissions expansion, etc.)
  - `reference/database-schema.md` — v0.9.6→v0.10.0: new `chat_message` and `pinned_note` tables; config table restructured to per-key format
  - `reference/api-endpoints.md` — added Programmatic Model Management section
  - `getting-started/essentials.mdx` — restructured: Web Search is now an essential, added Computer chapter, native tool calling is default
  - `security/security-policy.mdx` — major rewrite: transparency intent, advisory-history, extended reporting guidelines (13 rules)
  - `features/chat-conversations/memory.mdx` — fully rewritten: 8 memory tools, memory types & paths
  - `features/extensibility/index.mdx` — fully rewritten with architecture overview
  - `features/workspace/models.md` — Curated-Interface Deployments rewritten
  - `features/open-terminal/index.md` — rewritten with Computer callout
  - `getting-started/advanced-topics/hardening.md` — 4 new sections (redirect protection, CSP, etc.)
  - `tutorials/integrations/redis.md` — added memory eviction and persistence sections
  - `troubleshooting/context-window.mdx` — added Context Compression section
  - `troubleshooting/performance.md` — SQLite memory footprint
  - `troubleshooting/multi-replica.mdx` — THREAD_POOL_SIZE, ACTIVE_STATUS_INTERVAL
- **Renamed files** (upstream):
  - `features/extensibility/index.md` → `index.mdx`
  - `features/workspace/knowledge.md` → `knowledge.mdx`
  - `features/knowledge-base-sync/` → `ecosystem/knowledge-base-sync/` (moved)
- **Deleted file**: `features/open-terminal/terminals/policies.md`
- **Static assets**: banners (78 SVGs) resynced; `agents.txt`, `llms.txt`, `robots.txt` synced
- **Site config**: docusaurus.config.ts — zh-cn was already up to date with local search, gtag guard, webpack plugin

### 2026-06-18 Sync (en-us `d8c9f9d0` → `b9ee002e`)

- **New files translated (10)**: `features/chat-conversations/web-search/providers/linkup.md`, `features/extensibility/plugin/development/under-the-hood.mdx`, `features/knowledge-base-sync/{_category_.json,index.md,daemon.md}`, `getting-started/open-webui-as-app.md`, `getting-started/quick-start/connect-an-agent/cptr.mdx`, `getting-started/quick-start/tab-python/_PythonCompat.md`, `tutorials/integrations/valkey.md`
- **New static asset synced (1)**: `static/docker-compose.otel.yaml` (no translation needed, YAML)
- **Modified files synced (73)**: highlights:
  - `reference/env-configuration.mdx` — major: 23 new env vars added (`ENABLE_KB_EXEC`, `PROFILE_IMAGE_MAX_DATA_URI_SIZE`, `BYPASS_RETRIEVAL_ACCESS_CONTROL`, `MINERU_FILE_EXTENSIONS`, `LINKUP_API_KEY/PARAMS`, `OAUTH_AUTO_REDIRECT`, `VALKEY_*` vector DB cluster, `MCP_INITIALIZE_TIMEOUT`, etc.); `PersistentConfig` → `ConfigVar`; bump v0.9.0 → v0.9.6
  - `features/workspace/knowledge.md` — major: added `kb_exec` filesystem-style access section, `grep_knowledge_files` / `view_file` line-range tools, "when to prefer grep vs query" comparison, sync workflow examples
  - `features/workspace/models.md` — added "Curated-Interface Deployments" section
  - `features/workspace/skills.md` — added per-conversation skills subsection
  - `features/extensibility/pipelines/*` — added deprecation blocks (Pipelines is now legacy)
  - `features/extensibility/plugin/tools/index.mdx` — added `grep_knowledge_files` and `kb_exec` rows
  - `getting-started/essentials.mdx` — added `ENABLE_KB_EXEC` tip, cptr callout
  - `getting-started/index.md` — added "📱 把 Open WebUI 装成 App" PWA install section
  - `getting-started/quick-start/connect-an-agent/index.md` — added cptr entry; converted ASCII diagram to Mermaid
  - `getting-started/advanced-topics/scaling.md` — added `THREAD_POOL_SIZE=2000` and `DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL=300` warnings; converted ASCII diagram to Mermaid
  - `troubleshooting/multi-replica.mdx` — added items 7-8 (THREAD_POOL_SIZE, ACTIVE_STATUS_INTERVAL)
  - `troubleshooting/performance.md` — added SQLite memory footprint section + User Active-Status throttling
  - `tutorials/integrations/redis.md` — replaced `valkey/valkey` image with `redis:7-alpine`; added WebSocket Pub/Sub buffer limits section

Issues found after comparing against en-us snapshot `d2871160` have been resolved:

### 2026-05-26 Fixes

1. **`features/extensibility/plugin/development/reserved-args.mdx`** — Synced with en-us `d8c9f9d`:
   - `__metadata__` added `user_prompt`, `system_prompt`, `sources` fields with comments
   - Added "Read user message before wrapping" tip section (with Python example)
   - Expanded `__event_emitter__` section (socket.io explanation + status/custom event code examples)

### 2026-05-25 Fixes

1. **`chat-features/index.mdx`** — Added missing **🎙️ Voice Mode** section
2. **`chat-features/index.mdx`** — Added missing **Structured Reply Editing** section
3. **`security/vendor-dispositions/_category_.json`** — Created missing sidebar configuration file

## Intentional Differences

- **`troubleshooting/index.mdx`** — Uses "Ask on GitHub Discussions" instead of "Ask on Discord or Reddit"
  - Reason: intentional localization choice, corresponding commit `0712a9b7`

## Verification Method

```bash
# Check en-us submodule version
git submodule status

# Verify all files exist (should have no MISSING_IN_ZH entries)
cd /www/openwebuidocs
diff <(cd en-us/docs && find . -name '*.md' -o -name '*.mdx' | sort) \
     <(cd zh-cn/docs && find . -name '*.md' -o -name '*.mdx' | sort)
```
