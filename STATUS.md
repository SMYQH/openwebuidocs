# Chinese Documentation Translation Status

## en-us Source Version

- **Repo**: `en-us` (submodule)
- **Git commit**: `d412c34501c9a0b70891a05948a138482ca7776e`
- **Branch**: `main`
- **Snapshot date**: 2026-07-22

## Translation Progress Overview

| Metric | Value |
| --- | --- |
| en-us source files (.md/.mdx) | 400 |
| zh-cn files (.md/.mdx) | 400 |
| en-us `_category_.json` | 49 |
| zh-cn `_category_.json` | 49 |
| File coverage | **100%** (all 400 en-us documents have corresponding zh-cn translations) |
| Content completeness | **~99.9%** |

## Deployment Configuration

- **2026-07-22**: Added root-level Cloudflare Workers configuration for the Chinese site. The Deploy to Cloudflare button now builds `zh-cn/` and uploads `zh-cn/build/` as Workers static assets without requiring a manual root-directory setting.

## Structural Differences

| Difference | Description |
| --- | --- |
| `en-us/docs/ecosystem/` | **New section**: Ecosystem (Computer + Knowledge Base Sync) — fully translated |
| `en-us/docs/security/accepted-risks/` | **New section**: Known & Accepted Risks — 4 files fully translated |
| `en-us/docs/security/vendor-dispositions/_category_.json` | Added for zh-cn (📄 Vendor Dispositions) |

## Fixed Issues

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
