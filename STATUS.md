# Chinese Documentation Translation Status

## en-us Source Version

- **Repo**: `en-us` (submodule)
- **Git commit**: `36b7e50e4140f3cca1de0aeef4ae776af21169cb`
- **Branch**: `main`
- **Snapshot date**: 2026-11-11

## Translation Progress Overview

| Metric | Value |
| --- | --- |
| en-us source files (.md/.mdx) | 461 |
| zh-cn files (.md/.mdx) | 461 |
| en-us `_category_.json` | 52 |
| zh-cn `_category_.json` | 52 |
| File coverage | **100%** (all 461 en-us documents have corresponding zh-cn translations) |
| Content completeness | **100%** (every upstream heading has a matching Chinese section) |

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
cd /www/open-webui-docs
diff <(cd en-us/docs && find . -name '*.md' -o -name '*.mdx' | sort) \
     <(cd zh-cn/docs && find . -name '*.md' -o -name '*.mdx' | sort)
```
