# Chinese Documentation Translation Status

## en-us Source Version

- **Repo**: `en-us` (submodule)
- **Git commit**: `ee47d77ed76357560568dd5a1b0898fd514e96d3`
- **Branch**: `main`
- **Snapshot date**: 2026-11-27

## Translation Progress Overview

| Metric | Value |
| --- | --- |
| en-us source files (.md/.mdx) | 412 |
| zh-cn files (.md/.mdx) | 412 |
| en-us `_category_.json` | 43 |
| zh-cn `_category_.json` | 43 |
| File coverage | **100%** (all 412 en-us documents have corresponding zh-cn translations) |
| Semantic review | **1/1 changed pair passed** full bilingual review. The checker validated the source, installed translation, and configuration hashes. |
| Strict checker audit | **455/455 pairs** with 0 errors, 0 warnings, 15 notes, and 48 exact exceptions. |
| Verbatim code blocks | No hard code-preservation errors. The HAProxy and Nginx Proxy Manager fence repairs were reviewed against upstream. |
| Upstream inline code spans preserved | No unwaived hard preservation errors. Review signals and exact exceptions remain; this is not a universal preservation certification. |
| Explicit heading IDs matching upstream | No hard heading-structure failures. The reviewed HAProxy repair restored a heading hidden by upstream fence markup. |
| Untranslated English prose | No unwaived language warnings. Leftover English `endpoint` wording was normalized to the project terminology (`端点`, `API 端点`, `基础 API 端点`), and the `终结点` variant was replaced. |
| Production build | **Passed on 2026-11-27** with Node.js 24.15.0 and zero broken links, anchors, Markdown links, or duplicate routes. The build generated 390 routed documentation pages. Local sitemap synchronization skips runs without `DOMAIN`. |
| Checker behaviour tests | **185 tests passed on 2026-11-27**, including diagnostic terminology and selective review reuse. |

Workflow: [semantic review](.agents/skills/translation-semantic-review/SKILL.md) is separate from the [Python checker](.agents/skills/translation-checker/SKILL.md), which owns the scripts, tests, config, provider helpers, and ignored local artifacts. Changes to either document beyond line endings expire its exact exceptions. `scripts/restamp_exceptions.py` re-binds the surviving exceptions and reports findings that need a manual decision.

### 2026-11-27 Sync through `ee47d77e`

- Translated the environment reference update for `ENABLE_PERSISTENT_CONFIG`. When persistence is disabled, Admin UI changes stay in the worker that handled the save. Redis does not propagate these changes. Set the corresponding environment variable on every instance to apply the same value.
- Corrected existing wording on PDF re-extraction, embedding prefixes, OAuth recipient clients, required LDAP fields, and the audience for public calendars.
- Rebound the existing heading-order exception for `TERMINAL_PROXY_HEADERS`. The full bilingual review passed for the changed page.

### 2026-11-25 Sync through `99a03080`

- Updated 106 documents and added three guides for Router Models, Local Machine setup, and SSH Machines setup. Copied seven screenshots and the coding-agent redirect byte for byte.
- Major updates cover Router Models and blind evaluation, Open Terminal setup, built-in tools, model and tool version history, database storage, and environment settings. Tether chat uploads use **Filesystem** and shell tools use **Automatic**.
- The changed-scope audit validated all 109 semantic reviews with 0 errors, 0 warnings, 2 notes, and 12 exact exceptions. Offline provider plans also passed.

#### Upstream discrepancies

- History & Search says “all three tools” after listing two. The translation refers to the listed tools.
- Automations says admins cannot delete another user's automation from the interface. Its shared-automation section says creators and admins can delete. The translation preserves both scopes.
- Analytics says all endpoints require admin authentication and lists a personal endpoint for any signed-in user. The translation limits the admin authentication instruction to admin endpoints.
- RAG Troubleshooting calls Native the default. The RAG overview also uses Default as a distinct model setting. The troubleshooting guide suggests switching embedding models between ingestion and queries, while the overview requires compatible embeddings and reindexing after a model change.
- The environment reference counts six forwarded headers in a table that also lists `X-OpenWebUI-Auth-Type`. The translation makes clear that the count covers the six user and session headers.
- The async embedding tip ends mid-sentence after “to prevent”. The translation retains the instruction to consider raising `THREAD_POOL_SIZE` under concurrent use.
- The `ONEDRIVE_CLIENT_ID_BUSINESS` description refers to personal Microsoft accounts. The translation specifies organizational accounts, consistent with the Business setting.

### 2026-11-25 Translation tooling CI

- The November 22 CI run reported 18 warnings because the existing exceptions were fingerprinted with CRLF translation files. The checker now normalizes line endings to LF for exception fingerprints. Semantic review still uses hashes of the original file bytes.
- Rebound the 18 affected exceptions and preserved all 46 recorded reasons. The strict audit passed all 452 pairs with 0 errors, 0 warnings, and 15 notes.
- Added `mixed content` as a protected browser warning term. After an addition to the protected term list, the checker reruns the deterministic audit and reopens affected reviews while retaining eligible reviews of unchanged pairs.

### 2026-11-22 Sync through `307b3ad8`

- Translated 168 upstream documents and added 12 new pages under `getting-started/quick-start/connect-an-agent/` (Antigravity, Claude Code, Cline, Codex CLI, Cursor CLI, Gemini CLI, GitHub Copilot, Goose, Grok Build, OpenCode, Pi, Qwen Code) plus `reference/https/apache.md`.
- Renamed `features/open-terminal/coding-agents.md` to `features/open-terminal/agents.md` and copied the new `static/features/open-terminal/coding-agents/index.html` asset byte for byte.
- The upstream release adds explanations for Notes audio capture, the code-block Save button, the LDAP TLS error, `OPENSEARCH_SSL`, the Settings > Documents danger zone, retrieval query generation variance, the Ollama embedding-model swap, the `/app/backend` mount warning, the `DATA_DIR` defaults and backups, the admin password reset, an empty `DATABASE_URL`, Open Terminal `run_command` returning no output, Filter Functions skipping background task calls, tool requirement reinstalls, `--gpus all`, the encrypted ID token username claim fallback, the proxy body-size limit, the MCP OAuth redirect URI, private CA bundles, the Ollama OpenAI-compatible routes, pending SSO sign-ins, the Microsoft client secret value, and the workspace model settings a plain API call does not apply.
- `reference/env-configuration.mdx` picked up the upstream variable changes. 17 sections that upstream marks as environment variables (not `ConfigVar`) had a stale Chinese persistence line corrected, and 9 descriptions that had dropped a clause were restored.
- Agent product names (`Claude Code`, `Cline CLI`, `OpenAI Codex CLI`, `Cursor CLI`, `Gemini CLI`, `GitHub Copilot CLI`, `Google Antigravity CLI`, `Goose`, `Grok Build`, `OpenCode`, `Qwen Code`) are now terminology exclusions, so the untranslated `sidebar_label` metadata stays verbatim. `Pi` is deliberately not a global term because it collides with "Raspberry Pi"; `connect-an-agent/pi.md` uses a per-file exception instead.
- The strict audit reported **0 errors, 0 warnings, 15 notes, and 46 exact exceptions** across **452 pairs**. The heading-structure audit reported no mismatch, and the production build passed with zero broken links, anchors, Markdown links, or duplicate routes.

### 2026-11-20 Translation tool setup

- The [setup guide](.agents/skills/translation-checker/references/usage.md#first-run-setup) uses repo-relative commands. `uv sync --locked` creates `.venv` and installs the four CLI entry points. `--files` accepts either slash style, and DeepL `translate --input-file` reads UTF-8 text.
- Verified a fresh Windows clone in a path with spaces, starting with an empty uv cache and no `.env`. The strict audit passed **439/439 pairs** with **0 errors, 0 warnings, 15 notes, and 55 exact exceptions**. Both DeepL plan commands ran offline, and all **182 behavior tests passed**.

### 2026-11-20 Sync through `f53eb330`

- Fixed 176 findings across 57 pages from the review below. The API reference now preserves the streaming setting's precedence over the request's `stream` field. The multi-replica guide restores the shared database condition.
- Translated 96 modified upstream documents and added the visualization, video generation, and terminal creation guides. Removed Direct Connections and four superseded terminal orchestration pages. Copied the two connection screenshots.
- The terminal guide specifies **Filesystem** uploads and **Automatic** shell tools for Tether terminals. The oikb daemon guide directs personal OpenAPI connections to **Tether Settings > Integrations**, as documented in [Tether's integration guide](en-us/docs/ecosystem/tether.md#bring-your-own-models-and-tools).
- The Rich UI guide describes dynamic payloads through citation previews and the `null` payload for event and Action embeds. It records that assistant-message embeds always allow form submission.
- The strict audit reported **0 errors, 0 warnings, 15 notes, and 55 exact exceptions**. All **439 pairs passed semantic review**. This includes 131 completed readings and 308 reused passes for unchanged pairs. See the [local audit](.agents/skills/translation-checker/.reports/sync-f53-reviewed-audit.json).

### 2026-11-20 DeepL CLI and translation review

- Added `translate`, `usage`, and resumable `review` commands to the [translation-checker skill](.agents/skills/translation-checker/references/usage.md#deepl-cli). The existing translation update workflow shares the same DeepL client.
- DeepL reported **999,999 of 1,000,000 characters used** on November 20. The offline plan found zero pending texts within the remaining character. The [local checkpoint](.agents/skills/translation-checker/.reports/deepl-translation-review.json) holds 3,721 unique replies covering 3,880 of 6,097 eligible sections. The remaining 2,202 texts need 544,925 characters.
- Completed the read-only bilingual review of all **441 pairs** against `3072f18c`. **384 passed. 57 had 176 open findings.** This review superseded the November 19 semantic pass for that revision. The API reference reversed streaming precedence, and the multi-replica guide dropped the shared database condition. See the [finding summary](.agents/skills/translation-checker/.reports/deepl-findings.md) and [full results](.agents/skills/translation-checker/.reports/offline-review-results.json).
- The [strict audit](.agents/skills/translation-checker/.reports/offline-review-verified.json) reports **0 preservation errors, 0 warnings, 18 notes, and 53 exact exceptions**. It accepted all 441 review records and returned exit status `1` for the open findings. The [57 pairs with findings](.agents/skills/translation-checker/.reports/offline-review-unpassed.json) are available for reviewing corrections.

### 2026-11-19 Removal of the legacy documentation agent definitions

- Deleted `.codex/agents/doc-check.agent.md` and `.codex/agents/doc-review.agent.md`. Both files used the VS Code Copilot Chat custom-agent format (`tools:` entries such as `vscode/askQuestions`, `ms-vscode.vscode-websearchforcopilot`, `search/fileSearch`). Copilot discovers those files under `.github/agents/`, and Codex 0.170 declares agent roles through `[agents.<name>]` in `config.toml`; this repository declares none, and the session agent tool exposes no role selector. After the move out of `.github/agents/` nothing loaded them.
- The review workflow stays in the shared skills: `.agents/skills/translation-semantic-review` for bilingual reading and `.agents/skills/translation-checker` for the deterministic audit. The deleted orchestrator also mandated a question round and sub-agent dispatch for every check, which conflicts with the current no-sub-agent rule and with the deterministic audit.
- Updated the `AGENTS.MD` repository tree and the `Readme.md` structure section to drop the removed directory. No translated document changed.
- Verification: **176 behavior tests pass**; the strict audit still reports **441/441 counterparts, 0 errors, 0 warnings, 18 notes, and 53 exact exceptions**.

### 2026-11-19 Policy-link text, endpoint terminology, and exception re-binding

- Restored the upstream text of five policy-link bullets whose only link is removed by the external-link policy: the Discord referral in the Open Responses troubleshooting list, the Nous Research Discord entry in the Hermes Agent learn-more list, the Discord entry in the landing page "Get Involved" list, the Discord and Reddit referral in the troubleshooting community-support list, and the Voice AI & TTS Discord support line. The community-support bullet keeps the upstream wording and still offers the GitHub Discussions link.
- Normalized the endpoint terminology across the Chinese docs: English `endpoint`/`endpoints` in prose became `端点`, `API 端点` or `REST 端点`, the `终结点` variant became `端点`, and the Azure portal labels (`Keys and Endpoint`, `API Endpoint URL`, `Bing Search V7 Endpoint`) and the quoted Azure error message stay verbatim. Corrected one mistranslation in the Hugging Face SSL section (`改用镜像` -> `切换端点`).
- Removed one Chinese-only leftover paragraph in the oikb limitations section that upstream emptied, restored the paragraph break in the OpenTelemetry configuration section, and tightened the migration cheat-sheet wording.
- Added `scripts/restamp_exceptions.py`: it re-binds exact exceptions to their current fingerprints after an edit, keeps the reviewed reason of every finding that still exists, drops exceptions whose finding disappeared, and lists findings that need a manual decision. Added four behavior tests; the suite now runs 176 tests.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 53 exact exceptions**. The checker accepted **441/441** submitted review results at that checkpoint. The November 20 reread supersedes that semantic result. The production build passed with zero broken links, anchors, Markdown links, or duplicate routes.

### 2026-11-19 Astellas, Public Storage, and TRG case studies

- Reviewed three full pairs. Restored the distinction between open weights and open source, clarified the employee-led rollout and PII handling, and corrected who benefited from faster client onboarding.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 74 exact exceptions**. Validated **331/441** full reviews. No checker rules or exceptions changed in this batch.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-70-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-70-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-71-pending.json`.

### 2026-11-19 Agent gateways, DeepSeek-R1, and Langfuse

- Reviewed three full pairs. Clarified gateway API compatibility, GPU offloading, and Langfuse trace fields. Kept code samples unchanged.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 74 exact exceptions**. Validated **328/441** full reviews. No checker rules or exceptions changed in this batch.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-69-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-69-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-70-pending.json`.

### 2026-11-19 Community, image generation, and OpenTelemetry

- Reviewed three full pairs. Clarified the data sent by model review links, chat model selection for image generation, and OpenTelemetry metric types and export frequency.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 74 exact exceptions**. Validated **325/441** full reviews. Refreshed one existing exception for the unchanged local Markdown lint directive.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-68-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-68-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-69-pending.json`.

### 2026-11-19 Backups, offline mode, and S3 storage

- Reviewed three full pairs: backups, offline mode, and S3 storage. Refreshed two existing exact exceptions for the verified local encryption link.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 74 exact exceptions**. Validated **322/441** full reviews.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-67-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-67-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-68-pending.json`.

### 2026-11-19 Deployment diagrams and database maintenance

- Reviewed three full pairs. Corrected the Linux diagram description, clarified PVC reuse when a terminal Pod is rebuilt, and restored the command summary to its upstream position in the database migration guide.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 74 exact exceptions**. Validated **319/441** full reviews. No checker rules or exceptions changed in this review batch.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-66-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-66-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-67-pending.json`.

### 2026-11-19 Roles, groups, and permissions

- Reviewed three full pairs. Restored the Access button alongside the menu entry, corrected response rating, and clarified administrator access, session sign-out, and calendar sharing. Aligned permission rows with upstream.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 74 exact exceptions**. Validated **316/441** full reviews. The prior `TTS` exception no longer applies; the translated label no longer adds the acronym. No checker rules changed.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-65-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-65-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-66-pending.json`.

### 2026-11-19 Development, Continue.dev, and Noerr guides

- Reviewed three full pairs. Clarified the `dev` branch workflow and CORS setup, the Continue.dev base API endpoint, and the Noerr adoption timeline and RAG sources.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 75 exact exceptions**. Validated **313/441** full reviews. No checker rules or exceptions changed in this review batch.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-64-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-64-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-65-pending.json`.

### 2026-11-19 Open Terminal and security guides

- Reviewed five full pairs. Clarified agent conversation controls, ACP transport and permissions, endpoint validation, scanner classifications, and what first-run admin promotion denies when it fails. Confirmed the Nginx self-signed certificate guide without edits.
- Strict audit: **0 errors, 0 warnings, 18 notes, and 75 exact exceptions**. Validated **310/441** full reviews. No checker rules or exceptions changed in this review batch.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-63-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-63-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-64-pending.json`.

### 2026-11-19 Authentication, evaluation, and feature guides

- Reviewed ten complete pairs. Corrected who adds users in the MFA flow, restored the OAuth error text and missing arena scoring rules, and clarified external extraction response and retrieval behavior.
- Rechecked all four Keycloak code blocks against upstream before refreshing the existing exception for the unclosed source fence. No new exceptions or rule changes.
- The full strict audit found **0 errors, 0 warnings, 18 notes, and 75 matching exact exceptions**. The semantic review remains incomplete. All 169 offline tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-62-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-62-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-62-pending.json`.

### 2026-11-19 Terminal API, database analysis, and roadmap

- Reviewed three complete pairs. Clarified which terminal a stop request affects, how the database analysis skill receives credentials, and roadmap wording. Code samples, identifiers, and anchors are unchanged.
- The full strict audit found **0 errors, 0 warnings, 18 notes, and 75 matching exact exceptions**. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-61-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-61-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-61-pending.json`.

### 2026-11-19 Authentication, terminals, and integration guides

- Reviewed ten complete pairs. Corrected Samsung's development cycle result, authentication labels, terminal context behavior, API terminology, community support language, and accessible descriptions.
- Kokoro-FastAPI's source lists CUDA 12.3 in prerequisites and CUDA 12.8 in the GPU setup heading. The translation preserves both values; no runtime compatibility was inferred.
- The full strict audit found **0 errors, 0 warnings, 18 notes, and 75 matching exact exceptions**. No checker rules or exceptions changed. All 169 offline tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-60-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-60-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-60-pending.json`.

### 2026-11-19 Deployment, chat, and API terminology

- Reviewed ten deployment, chat, notification, tutorial, and administration pairs. Corrected shared key, session affinity, attachment queue, and notification masking descriptions.
- Documented context-sensitive API terminology and spacing. Rechecked four notification and speech-to-text pairs after wording edits; code, URLs, and anchors are unchanged.
- The strict audit found **0 warnings, 0 errors, 18 notes, and 75 matching exact exceptions**. It validated 282 passed pairs and left 159 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-59-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-59-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-59-pending.json`.

### 2026-11-19 Speech-to-text guides

- Reviewed the Mistral, OpenAI, and self-hosted speech-to-text guides in full. Restored the verbatim Mistral error and clarified recording, local transcription, and server settings. Model IDs and code examples are unchanged.
- The strict audit found **0 warnings, 0 errors, 18 notes, and 75 matching exact exceptions**. It validated 272 passed pairs and left 169 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-57-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-57-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-57-pending.json`.

### 2026-11-19 Mission, autocomplete, and file workflow guides

- Reviewed four pairs in full. Restored the Mission example's offline behavior, clarified the autocomplete model fallback and switch labels, and improved Open Terminal's file creation and analysis examples.
- The strict audit found **0 warnings, 0 errors, 18 notes, and 75 matching exact exceptions**. It validated 269 passed pairs and left 172 pending. All 169 tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-56-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-56-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-56-pending.json`.

### 2026-11-19 Filter, Mistral TTS, and search Action guides

- Reviewed the three guides in full. Fixed the Filter hook and switch descriptions and aligned its retrieval recipe with the instance-attribute warning. All 37 Filter code bodies match upstream.
- Restored the TTS troubleshooting model ID and the Action setup location. Added a section-level warning for a new inline code identifier replacing a repeated source identifier.
- The new check also caught stale OneDrive settings. Restored the client IDs, legacy fallback, and startup-only behavior. Renewed five unchanged exact exceptions after verifying the edits did not touch their sections. The environment reference still needs full review.
- The strict audit found **0 warnings, 0 errors, 18 notes, and 75 matching exact exceptions**. It validated 265 passed pairs and left 176 pending. All 169 tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-55-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-55-final-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-55-final-pending.json`.

### 2026-11-19 Terminal, enterprise, and browser integration guides

- Reviewed nine pairs in full. Clarified per-user OpenShift isolation, terminal secret visibility, the authentication timing mitigation, and the code review workflow.
- Corrected the browser search query behavior, customer rollout and workflow metrics, Direct Connections credential scope, and enterprise integration and support language. No new exceptions were needed.
- The full audit found **0 warnings, 0 errors, 18 notes, and 75 matching exact exceptions**. It validated 262 passed pairs and left 179 pending, so the combined audit exited nonzero. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-54-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-54-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-54-pending.json`.

### 2026-11-19 Chat features and integration guides

- Reviewed the integrations index, follow-up prompts, Mermaid rendering, and Podman setup. Clarified the follow-up input behavior and restored the avatar navigation step in the Podman guide.
- Corrected the Mermaid code-fence instruction against `src/lib/components/chat/Messages/CodeBlock.svelte` at application revision `abcebd7d0dada9119c8d32c18dd981e896151709`. Both examples are unchanged.
- The full audit found **0 warnings, 0 errors, 18 notes, and 75 matching exact exceptions**. It validated 253 passed pairs and left 188 pending, so the combined audit exited nonzero. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-53-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-53-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-53-pending.json`.

### 2026-11-19 Terminal policies, Tether, and RBAC

- Reviewed the terminal policy fields, Tether client protocol, and RBAC overview. Clarified Docker storage quota limits, the authorization callback's one-time code, and the distinction between a user's role and their permissions.
- The full audit found **0 warnings, 0 errors, 18 notes, and 75 matching exact exceptions**. It validated 249 passed pairs and left 192 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-52-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-52-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-52-pending.json`.

### 2026-11-19 Alternatives review complete

- Reviewed AnythingLLM, ChatGPT, Claude, Gemini, llama.cpp, and Onyx against the pinned source. Corrected terminology, UI labels, and awkward phrasing while preserving commands and anchors.
- Updated Onyx's self-hosted SSO and permission tiers using its [access-control documentation](https://docs.onyx.app/security/architecture/access_controls). Distinguished those features from [Onyx Cloud pricing](https://onyx.app/pricing) and retained the July 2026 price as historical context.
- All 13 comparison pages now have passing semantic reviews. The full audit found **0 warnings, 0 errors, 18 notes, and 75 matching exact exceptions**. It validated 246 passed pairs and left 195 pending, so the combined audit exited nonzero. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-51-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-51-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-51-pending.json`.

### 2026-11-19 Alternatives review

- Reviewed Jan, Msty, LibreChat, Dify, LM Studio, and Ollama, including frontmatter, structured FAQs, tables, and links.
- Corrected the Dify integration instructions against its [app API documentation](https://docs.dify.ai/en/api-reference/guides/get-started). An OpenAI-compatible adapter is required. Clarified the LM Studio loopback and Ollama default-address assumptions using the pinned provider guides. No code blocks changed.
- The strict audit found **0 warnings, 0 errors, 18 notes, and 74 matching exact exceptions**. Semantic validation passed 240 pairs and left 201 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-50-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-50-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-50-pending.json`.

### 2026-11-19 Environment reference and semantic review checkpoint

- Added checks for literal setting types and boolean defaults in their own rows. Corrected mismatched types, defaults, and missing UI guidance in the environment reference. The reference still needs a full semantic review.
- Verified the Firecrawl timeout against application revision `abcebd7d0dada9119c8d32c18dd981e896151709`: the configuration stores a string, the loader parses integer seconds, and the scrape request clamps the converted value to 1000–300000 milliseconds. Retained the duplicate Analytics Sessions link and verified historical notes under exact fingerprints.
- Reviewed six more complete pairs. Corrected the temporal tool's future-date limitation, localized terminal labels, and fixed wording in the HTTPS index.
- The strict audit found **0 warnings, 0 errors, 18 notes, and 71 matching exact exceptions**. Semantic validation passed 234 pairs and left 207 pending, so the combined audit exited nonzero. All 168 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-49-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-49-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-49-final-pending.json`.

### 2026-11-19 Filter behavior and vendor dispositions

- Restored the Filter guide's switch locations and conditions, retrieval wording, and emphasis without changing code examples. The guide still needs full semantic review.
- Restored the vendor's reach-and-impact caveat, renewed the exact fingerprint for an unchanged evidence quotation, and retained the TTS abbreviation in the permissions table.
- The strict audit found **4 warnings, 0 errors, 18 notes, and 66 matching exact exceptions**. It validated 228 passed pairs and left 213 pending. The production build passed. All remaining warnings are in the environment reference.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-48-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-48-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-48-pending.json`.

### 2026-11-19 Connection and database troubleshooting

- Restored the General settings step and clarified URL resolution and proxy inheritance. Aligned the database prerequisites and clarified which older Open WebUI versions the fresh-install guidance covers. Both pairs still need full semantic review.
- The strict audit found **10 warnings, 0 errors, 18 notes, and 65 matching exact exceptions**. It validated 228 passed pairs and left 213 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-46-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-46-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-46-pending.json`.

### 2026-11-19 MCP proxy and audio troubleshooting

- Restored the source of alternate MCP server implementations, the tool schema explanation, and the CPU performance comparison. Kept examples unchanged. Both pairs still need full semantic review.
- The strict audit found **14 warnings, 0 errors, 18 notes, and 65 matching exact exceptions**. It validated 228 passed pairs and left 213 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-45-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-45-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-45-pending.json`.

### 2026-11-19 Extensibility guide corrections

- Aligned the MCP authentication and connection wording, restored emphasis in the tool migration guide, and distinguished per-replica startup installs from concurrent workers sharing one environment. All three pairs still need full review.
- The strict audit found **16 warnings, 0 errors, 18 notes, and 65 matching exact exceptions**. It validated 228 passed pairs and left 213 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-44-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-44-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-44-pending.json`.

### 2026-11-19 Open Terminal overview and settings

- Reviewed the full Open Terminal overview. Restored missing workload details, Browser-tab and Git guidance, and multi-user provisioning options. Aligned the section breaks and link order.
- Restored the OAuth settings' read-only state in the overview table. Clarified Docker data persistence and Kokoro.js GPU fallback. The FAQ, SSO, and Voice Mode pairs remain pending full review.
- The strict audit found **22 warnings, 0 errors, 18 notes, and 65 matching exact exceptions**. It validated 228 passed pairs and left 213 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-43-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-43-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-43-pending.json`.

### 2026-11-19 Azure Speech, Artifacts, and terminology review

- Reviewed Azure Speech STT and Artifacts in full. Corrected the recording preprocessing conditions and restored the example's Open WebUI version selector. The CSP explanation follows the standard: [multiple active policies are enforced together](https://www.w3.org/TR/CSP3/#multiple-policies). The configuration example is unchanged.
- Removed a misleading HTML-only banner heading, clarified automatic reconnect wording, and kept the oikb version requirement and explanation. Those three pairs are deterministically clean and still need full review.
- The strict audit found **27 warnings, 0 errors, 18 notes, and 65 matching exact exceptions**. It validated 227 passed pairs and left 214 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-42-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-42-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-42-pending.json`.

### 2026-11-19 Section-level diagnostics and environment settings

- The checker now reports heading locations and local counts for file-wide terminology and Markdown symbol warnings. An audit before the documentation edits matched all 115 prior findings and fingerprints.
- Restored channel, follow-up, tag, full-text retrieval, and chat-permission behavior. Fixed the documented types for four permission settings and the default for public note sharing. The environment reference still needs full semantic review.
- The strict audit found **32 warnings, 0 errors, 18 notes, and 65 matching exact exceptions**. It validated 225 passed pairs and left 216 pending. All 166 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-41-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-41-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-41-pending.json`.

### 2026-11-19 Azure identity and LDAP reviews

- Reviewed three complete pairs, including one previously passed pair. Clarified the Entra token claim, Helm namespace use, and identity authentication. Removed duplicate bilingual labels without removing any setup step.
- Recorded one exact exception for the corrected Open WebUI spelling in the Workload Identity prerequisites heading. No code or identifiers changed.
- The strict audit found **32 warnings, 0 errors, 18 notes, and 65 matching exact exceptions**. It validated 225 passed pairs and left 216 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-40-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-40-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-40-pending.json`.

### 2026-11-19 Vendor dispositions and History Search

- Reviewed four complete pairs. Restored the OpenAI versus Ollama comparison, the vendor disposition formatting, and the file-drop instruction. Removed the unsupported claim that the opening search example used Python.
- Kept GitHub Discussions as the troubleshooting support channel in place of the policy-excluded links, with two exact exceptions.
- The strict audit found **36 warnings, 0 errors, 18 notes, and 64 matching exact exceptions**. It validated 223 passed pairs and left 218 pending. All 165 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-39-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-39-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-39-pending.json`.

### 2026-11-19 Security policy and disposition reviews

- Reviewed both complete pairs. Restored the security policy's separate issue and bug categories, reporting rationale, and confidentiality emphasis. Restored the disposition's disclosure rationale, URL reference in the prose, and section divider. Two exact exceptions record the omitted duplicate disclosure link; its original destination is still linked from the dated disclosure.
- The strict audit found **43 warnings, 0 errors, 18 notes, and 62 matching exact exceptions**. It validated 219 passed pairs and left 222 pending. All 165 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-38-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-38-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-38-pending.json`.

### 2026-11-19 Environment reference review

- Restored six missing cross-references and the accompanying MFA, Helm, external extraction, and embedding behavior. Restored emphasis on 24 Oracle field labels. Removed one extra divider before OAuth without removing prose.
- The strict audit found **54 warnings, 0 errors, 18 notes, and 60 matching exact exceptions**. It validated 217 passed pairs and left 224 pending. All 165 behavior tests and the production build passed.
- Four findings in the environment reference still need review: emphasis, terminology counts, an extra Analytics cross-reference, and version or numeric claims. The reference has not passed semantic review.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-37-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-37-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-37-pending.json`.

### 2026-11-19 Repeated identifier preservation

- The verifier now credits exact extra code spans toward bare identifier counts without counting a required code span twice. Restored the omitted `WEBUI_URL` mention. The environment reference still needs full review.
- The strict audit found **56 warnings, 0 errors, 18 notes, and 60 matching exact exceptions**. It validated 217 passed pairs and left 224 pending. All 165 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-36-final-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-36-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-36-pending.json`.

### 2026-11-19 Hardening, chat, and speech reviews

- Reviewed five complete pairs. Restored the required multi-replica migration sequence, the audit-log model field, the reply-entry conditions, and the recommendation for two-factor sign-in. Clarified terminal isolation, chat input commands, and the distinction between networking and file mounts.
- Verified all 80 fenced blocks across the six focused pairs. Three exact exceptions cover the Hardening page's rendered anchor, a preserved filename formatted as code, and a Discord referral excluded by site policy.
- The strict audit found **57 warnings, 0 errors, 18 notes, and 60 matching exact exceptions**. It validated 217 passed pairs and left 224 pending. All 164 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-35-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-35-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-35-pending.json`.

### 2026-11-19 Plugin, terminal, and deployment reviews

- Reviewed twelve complete pairs. Restored the Podman Quadlet sample to its numbered step, clarified the file-browser root's UI-only scope, and fixed omissions in several workflow examples. Verified all 35 fenced code bodies match upstream.
- Corrected the Let's Encrypt guide's obsolete IP certificate claim using its official January 15, 2026 announcement. Kept the existing domain-based setup and all code unchanged. Four exact exceptions cover the verified differences in three Nginx guides.
- Restored the plugin guide's page-serving heading and emphasis on cross-replica coordination and embedded icon data. The four edited plugin pairs pass focused checks and remain pending full review.
- The strict audit found **66 warnings, 0 errors, 18 notes, and 57 matching exact exceptions**. It verified 212 passed pairs and left 229 pending. All 164 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-34-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-34-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-34-pending.json`.

### 2026-11-19 OAuth and local cross-references

- Corrected which party issues OAuth tokens, clarified the global trusted-client allowlist, and combined two equivalent links. The OAuth pair passed full review.
- Kept the Chinese translation Beta notice and the local knowledge-sync and encrypted-storage references. Clarified that the backup cross-reference is about storage encryption, not SQLCipher support. Eight exact exceptions cover these differences and the policy-removed Discord referral on the intro page.
- The strict audit found **74 warnings, 0 errors, 18 notes, and 53 matching exact exceptions**. It verified 200 passed pairs and left 241 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-31-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-31-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-31-pending.json`.

### 2026-11-19 Search, extensibility, and integration reviews

- Reviewed ten complete pairs across Apache Tika, Terminals, speech environment variables, Tailscale, web search, extensibility, and three CVE notices. Verified all 24 fenced code bodies against upstream.
- Restored the web search diagnostic and clarified page fetching, workspace scope, and authentication. Fixed the direction of OpenAPI configuration and restored emphasis on access-control claims and search requirements. The agentic search table now identifies traditional RAG as Legacy mode, consistent with that page's Native-default instructions.
- The inline scanner now jumps to candidate characters rather than walking ordinary prose one character at a time. Its full audit, including every finding fingerprint and review result, exactly matched the pre-change audit. All 164 behavior tests and the production build passed.
- The strict audit found **86 warnings, 0 errors, 18 notes, and 45 matching exact exceptions**. It verified 199 passed pairs and left 242 pending.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-30-optimized-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-30-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-30-pending.json`.

### 2026-11-19 Provider, terminal, and alternatives reviews

- Corrected the Gemini and LiteLLM configuration labels, clarified Azure credential selection, and aligned the encrypted chat limits and Open Terminal setup. Restored the shared Open WebUI instance label in Tether. All five pairs passed review.
- Restored the `ee/` license scope in the Onyx comparison row after reviewing the alternatives index. Its focused audit already had no warnings, so only the full review caught this omission.
- Verified 11 exact exceptions for existing differences: equivalent OpenAI and Firefox links, the legacy Monitoring anchor, three editor directives, and Caddy's security-headers contents entry and product spelling. No checker rule changed.
- The strict audit found **97 warnings, 0 errors, 19 notes, and 45 matching exact exceptions**. It verified 189 passed pairs and left 252 pending. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-28-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-28-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-28-pending.json`.

### 2026-11-19 Kokoro-FastAPI guide

- Restored the Docker Compose option and the generation-speed claim. Kept all code bodies unchanged. The pinned English guide cites CUDA 12.3 and 12.8 in different sections. The `v0.2.1` GPU Dockerfile uses a CUDA 12.4.1 runtime, which does not establish the minimum host driver. The pair remains pending.
- The strict audit found **113 warnings, 0 errors, 20 notes, and 33 matching exact exceptions**. It validated 183 passed reviews and left 258 pending.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-25-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-25-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-25-pending.json`.

### 2026-11-19 Kokoro Web guide review

- Restored the API test command to its troubleshooting step without changing either code body. Corrected the guidance about voice mixes and localized the remaining link label.
- Rechecked the full pair and recorded one exact exception for the four uses of the standard Open WebUI product spelling in place of upstream `OpenWebUI`.
- The strict audit found **114 warnings, 0 errors, 20 notes, and 33 matching exact exceptions**. It validated 183 passed reviews. The production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-24-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-24-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-24-pending.json`.

### 2026-11-19 Badge accessibility and platform spelling

- Preserved the descriptive GitHub Sponsors badge alt text and the correct capitalization of Windows in the Azure CLI guide. Rechecked both full pairs and recorded two exact exceptions. Their previously passed reviews still match the same source and target bytes.
- The strict audit found **115 warnings, 0 errors, 20 notes, and 32 matching exact exceptions**. It validated 182 passed reviews and left 259 pending.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-23-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-23-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-23-pending.json`.

### 2026-11-19 Evidence quotation audit

- Verified that all six remaining language warnings came from exact evidence quotations in the BaseFortify and INCIBE reports and the vendor quotation in CVE-2025-15603. Kept the quotations and added six exact exceptions. No language check was disabled, and the three pairs still need full semantic review.
- The strict audit found **117 warnings, 0 errors, 20 notes, and 30 matching exact exceptions**. The verifier carried forward 182 passed pairs and left 259 pending.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-22-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-22-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-22-pending.json`.

### 2026-11-19 Numeric warnings and semantic review

- Restored the missing Pipe description, list nesting, and section breaks. Replaced inline retry history with the existing settings reference. Aligned the CVE disposition timeline, version wording, and emphasis. Both pairs passed full review.
- Reviewed the email screenshot and kept the alt text that identifies five overdue items. The exact exception applies only to the added count. The previously passed review still matches the unchanged pair.
- Restored the RAG cutoff behavior and corrected several environment setting descriptions. Application revision `abcebd7d0dada9119c8d32c18dd981e896151709`, as of the pinned docs snapshot, takes integer seconds at the Firecrawl web loader boundary and converts them to milliseconds for scraping. The reference's remaining discrepancies require full review.
- The numeric verifier recognizes plural HTTP status codes in a narrow error context without accepting changed codes or treating elapsed seconds as status codes.
- The full strict audit found **123 warnings, 0 errors, 20 notes, and 24 matching exact exceptions**. All 163 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-21-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-21-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-21-pending.json`.

### 2026-11-19 HAProxy repair and semantic review

- Verified all eight HAProxy code bodies against a source copy with only its broken fence delimiters repaired. The remaining differences are two explicit links to unchanged upstream URLs. Recorded nine exact exceptions for the existing repair and link markup.
- Reviewed 14 more complete pairs. Restored the image troubleshooting menu emphasis and Unraid diagnostic grouping. Corrected comment notification direction and clarified terminal refresh and reset behavior.
- Added `--reuse-review-config` for exception-only changes. The verifier checks the old config digest, reuses only unchanged passed pairs, and reruns the deterministic audit with the current config.
- The full strict audit found **130 warnings, 0 errors, 20 notes, and 23 matching exact exceptions**. All 162 behavior tests and the production build passed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-20-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-20-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-20-pending.json`.

### 2026-11-19 Chat imports, prompt versions, and migration guidance

- Reviewed the complete chat import and workspace prompt pairs. Restored import behavior for missing or read-only folders and clarified which prompt edits create a version. All nine example code bodies match upstream.
- Corrected migration startup behavior, restored the row-count thresholds, aligned the idempotency guidance with upstream, and moved the diagnostic example beneath its introduction. Restored emphasis in the skills and Okta guides. These pairs remain pending review.
- The verifier now recognizes two coordinated deadlines that share an implicit unit. Regression tests cover changed and omitted units, changed values, and unrelated counts.
- The full strict audit found **141 warnings, 0 errors, 20 notes, and 14 matching exact exceptions**. All 161 behavior tests and the production build passed. No exceptions changed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-19-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-19-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-19-pending.json`.

### 2026-11-19 CVE notices and date verification

- Localized the administrative prose in six CNA rejection notices while preserving advisory IDs and the nested vendor quotation. Kept the original evidence quotes in the BaseFortify and INCIBE reports. Restored omitted RBAC terminology and upstream formatting in the security docs.
- Reviewed three complete CVE pairs. The date checker now compares two days that share a month and year as two complete dates. Tests cover equivalent formats and changed or missing days.
- The full strict audit found **149 warnings, 0 errors, 20 notes, and 14 matching exact exceptions**. All 160 behavior tests and the production build passed. No exceptions changed.
- Audit: `.agents/skills/translation-checker/.reports/goal-semantic-18-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-18-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-18-pending.json`.

### 2026-11-19 HTTPS, Notion, and Firefox guide review

- Reviewed six complete pairs and verified all 38 fenced code bodies match upstream. Restored the Notion connection ID guidance, OAuth recovery steps, and screenshot description. Aligned the proxy guides with upstream and kept the local Firefox link and Nginx lint directive.
- The verifier now protects bare Windows drive-letter paths as whole literals. Regression tests cover paths containing protected terms and numbers, changed paths, and paths wrapped in backticks.
- The full strict audit found **170 warnings, 0 errors, 20 notes, and 14 matching exact exceptions**. All 159 behavior tests and the production build passed. No exceptions changed.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-17-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-17-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-17-pending.json`.

### 2026-11-19 License, landing pages, troubleshooting, and Edge TTS review

- Reviewed five complete pairs and verified all 14 fenced code bodies match upstream. Updated the license guide's branding restrictions and restored its table. Restored the Features page's scaling explanation and corrected the Functions description.
- Retained the homepage translation notice, knowledge-sync guidance, and community support link. Their intentional differences remain visible in the audit.
- Fixed recognition of duration units in prose rates after a slash. Regression tests cover changed values, changed or omitted units, and protected URL/path literals.
- The full strict audit found **179 warnings, 0 errors, 20 notes, and 14 matching exact exceptions**. The previous homepage callout exception no longer applies. All 158 behavior tests and the production build passed.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-16-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-16-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-16-pending.json`.

### 2026-11-19 Azure, RAG, migration, and Valkey review

- Reviewed five complete pairs and confirmed 25 fenced code bodies match upstream. Restored RAG links and default-mode tool behavior, aligned migration markup and Azure TTS settings, and synced stale guidance in Valkey and Azure Workload Identity.
- The Azure Workload Identity terminology warning remains visible because the translation corrects `OpenWebUI` to `Open WebUI`. No exceptions changed.
- The full strict audit found **189 warnings, 0 errors, 20 notes, and 15 exact exceptions**. All 157 behavior tests and the production build passed.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-15-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-15-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-15-pending.json`.

### 2026-11-19 Advanced Workflows, Caddy, and Docker deployment review

- Reviewed three complete pairs. Restored skill discovery, model attachment, and sharing requirements. Clarified Caddy domain configuration and Docker orchestrator recovery.
- Kept Caddy's local contents link and its standardized Open WebUI spelling. Kept the editor lint directive on the Docker tab. Their warnings remain visible. No exceptions changed.
- The full strict audit found **206 warnings, 0 errors, 20 notes, and 15 exact exceptions**. The production build passed.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-14-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-14-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-14-pending.json`.

### 2026-11-19 OpenAPI integration, startup, and monitoring review

- Reviewed five complete pairs. Removed a duplicated CORS passage, restored OpenAPI connection guidance and startup troubleshooting emphasis, and clarified monitoring and context-window terminology.
- Recognized spelled-out zero in numeric comparisons and tested changed and repeated counts. The Monitoring warning remains visible because its legacy anchor is intentional. Confirmed the anchor renders in the production build.
- The full strict audit found **207 warnings, 0 errors, 20 notes, and 15 exact exceptions**. All 157 behavior tests and the production build passed. No exceptions changed.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-13-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-13-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-13-pending.json`.

### 2026-11-19 Notes and OpenAPI tool-server overview review

- Reviewed both complete pairs. Restored the chat-based Notes editing workflow, audio controls, page-level tools, and PDF and page export behavior. Clarified the OpenAPI parser's JSON-to-YAML fallback.
- Both pairs passed strict checks and hash-bound semantic review. The full audit found **216 warnings, 0 errors, 20 notes, and 15 exact exceptions**. No exceptions changed. The production build passed.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-12-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-12-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-12-pending.json`.

### 2026-11-19 Events, Docling, and section overview review

- Reviewed ten complete pairs. Restored the Event Functions settings path and clarified field redaction and onboarding timing. Kept Docling's worker threshold outside the configuration-key code span and distinguished two-letter from three-letter OCR language codes.
- The verifier compares day labels by ordinal, without treating daily counts or durations as equivalent. The ten pairs passed strict checks with one informational note for a translated interface label.
- The full strict audit found **222 warnings, 0 errors, 20 notes, and 15 exact exceptions**. All 156 behavior tests and the production build passed.
- Report: `.agents/skills/translation-checker/.reports/goal-semantic-11-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-11-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-11-pending.json`.

### 2026-11-19 HAProxy rendering review

- Reconstructed the upstream fence boundaries in memory and verified all eight code bodies in order. The built Chinese page renders eight separate code blocks, the restored WebSocket/HTTP/2 heading, and both upstream link destinations.
- The HAProxy semantic review passed. Its nine unwaived warnings reflect the merged upstream fence and explicit links for two upstream bare URLs. No exceptions changed.
- The full strict audit remains at **224 warnings, 0 errors, 20 notes, and 15 exact exceptions**. Report: `.agents/skills/translation-checker/.reports/goal-semantic-10-audit.json`. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-10-results.json`. Pending pairs: `.agents/skills/translation-checker/.reports/semantic-review-10-pending.json`.

### 2026-11-19 Image configuration, risk documentation, and Milvus review

- Reviewed four complete pairs. Restored the deployment tradeoff in Accepted Risks, clarified how Open WebUI limits the effects of unpredictable model output, and kept the Milvus monitoring script verbatim.
- Kept the Azure AI Foundry link labels descriptive. Their destinations match upstream; the Markdown-symbol warning remains visible because upstream uses bare URLs.
- The full strict audit found **224 warnings, 0 errors, 20 notes, and 15 exact exceptions**. Report: `.agents/skills/translation-checker/.reports/goal-semantic-09-audit.json`.
- Validated 124 reviews in `.agents/skills/translation-checker/.reports/semantic-review-batch-09-results.json`. The remaining 317 pairs are in `.agents/skills/translation-checker/.reports/semantic-review-09-pending.json`. The production build passed.

### 2026-11-19 Workspace, audio, browser, and deployment guide review

- Reviewed eight complete pairs. Restored file download and deletion behavior, corrected the speech-to-text extension allowlist instructions, and clarified browser fallback, desktop audio, and deployment guidance.
- The verifier distinguishes explicitly localized calendar spans from durations while still checking both endpoints. The Azure CLI guide's Windows capitalization warning remains visible: upstream uses lowercase for the platform name.
- The full strict audit found **230 warnings, 0 errors, 20 notes, and 15 exact exceptions**. Report: `.agents/skills/translation-checker/.reports/goal-semantic-08-audit.json`.
- Validated 120 reviews in `.agents/skills/translation-checker/.reports/semantic-review-batch-08-results.json`. The remaining 321 pairs are in `.agents/skills/translation-checker/.reports/semantic-review-08-pending.json`. All 155 behavior tests and the production build passed.

### 2026-11-19 Image, document, and troubleshooting guide review

- Reviewed nine complete pairs. Restored folder deletion behavior for shared chats, corrected Mistral OCR request and indexing descriptions, and clarified the Intel GPU and custom CA guides.
- Kept two accurate accessibility additions visible to the audit: the email screenshot shows five urgent items, and the sponsorship badge identifies GitHub Sponsors. Neither warning was exempted.
- The full strict audit found **239 warnings, 0 errors, 20 notes, and 15 exact exceptions** across 441 counterparts. Report: `.agents/skills/translation-checker/.reports/goal-semantic-07-audit.json`.
- Validated 112 reviews in `.agents/skills/translation-checker/.reports/semantic-review-batch-07-results.json`. The remaining 329 pairs are in `.agents/skills/translation-checker/.reports/semantic-review-07-pending.json`. The production build passed.

### 2026-11-19 Deployment and connection guide review

- Reviewed the Scaling, Kubernetes, OpenClaw, and OpenAI-Compatible guides in full. Restored troubleshooting links and deployment prerequisites, corrected the OpenClaw verification failure heading, and updated model labels and endpoint descriptions.
- Fixed a numeric false positive: the checker no longer interprets a capitalized modal `May` as a month after a word that merely ends in a date preposition. Regression tests cover both ordinary headings and real dates.
- The four guides passed strict checks and hash-bound semantic review. The full strict audit found **247 warnings, 0 errors, 20 notes, and 15 exact exceptions** across 441 counterparts. No exceptions changed. Report: `.agents/skills/translation-checker/.reports/goal-semantic-06-audit.json`.
- Validated 103 reviews in `.agents/skills/translation-checker/.reports/semantic-review-batch-06-results.json`. The remaining 338 pairs are in `.agents/skills/translation-checker/.reports/semantic-review-06-pending.json`. All 154 behavior tests and the production build passed.

### 2026-11-18 Provider connections and Docker Compose review

- Compared four complete pairs. Restored the OpenAI connection steps and automatic Azure provider selection. Clarified ai& inference hosting, per-model ID entry, and Docker Compose GPU and volume behavior.
- The four pages passed strict checks and semantic review. The full strict audit found **255 warnings, 0 errors, 20 notes, and 15 exact exceptions** across 441 counterparts. No verifier rules or exceptions changed. Report: `.agents/skills/translation-checker/.reports/goal-semantic-05-audit.json`.
- Validated 99 current reviews in `.agents/skills/translation-checker/.reports/semantic-review-batch-05-results.json`. The remaining 342 pairs are in `.agents/skills/translation-checker/.reports/semantic-review-05-pending.json`. All 153 behavior tests and the production build passed.

### 2026-11-18 Setup guide review

- Reviewed 20 setup guides and tabs. Restored browser notification and webhook behavior, the model selector's default-model action, and the Anthropic connection settings. Clarified team access checks, context retention, and Python upgrade and data-storage guidance.
- The focused strict audit passed with **0 errors, 0 warnings, and 5 exact exceptions** for policy-removed referrals in Essentials and Hermes Agent. Removing only those three referral items from a temporary upstream copy eliminated all five findings. No verifier rule changed.
- The full strict audit found **257 warnings, 0 errors, and 15 exact exceptions** across 441 counterparts. Report: `.agents/skills/translation-checker/.reports/goal-semantic-04-audit.json`.
- Validated 95 reviewed pairs in `.agents/skills/translation-checker/.reports/semantic-review-batch-04-results.json`. The remaining 346 pairs are in `.agents/skills/translation-checker/.reports/semantic-review-04-pending.json`. All 153 behavior tests passed.

### 2026-11-18 Web search provider review

- Reviewed all 28 provider guides and their category. Restored Brave's web-loader setting and shared HTTP session behavior, Yacy's required username, and chat search controls. Clarified SearXNG certificate mounts and Firecrawl's search timeout budget.
- The provider audit passed with zero errors, warnings, or exceptions. The full strict audit found **276 warnings, 0 errors, and 10 exact exceptions** across 441 counterparts. No verifier rules or exceptions changed. Report: `.agents/skills/translation-checker/.reports/goal-semantic-03-audit.json`.
- Validated 75 reviewed pairs in `.agents/skills/translation-checker/.reports/semantic-review-batch-03-results.json`. The 366 remaining pairs are in `.agents/skills/translation-checker/.reports/semantic-review-03-pending.json`. All 153 behavior tests passed.

### 2026-11-18 Provider and proxy guide review

- Strict audit covered **441/441 counterparts with 0 errors, 291 warnings, and 10 exact exceptions**. Strict mode exits 1. The largest remaining groups are terminology (113) and Markdown symbols (83). Report: `.agents/skills/translation-checker/.reports/goal-semantic-02-audit.json`.
- Completed full review of the Linkup, vLLM, and Nginx Proxy Manager guides. Clarified the single Linkup JSON field and the Nginx timeout. Rechecked all eight Nginx code samples and the orphan CORS callout closer before refreshing four exact fingerprints. The remaining Nginx terminology recount stays visible.
- Validated 48 reviewed pairs: `.agents/skills/translation-checker/.reports/semantic-review-batch-02-results.json`. The remaining 393 full pairs are in `.agents/skills/translation-checker/.reports/semantic-review-02-pending.json`.
- **153 behavior tests passed**. The verifier recognizes localized AM/PM clocks, preserves open-duration bounds and units, and compares rendered ordered-list sequences without ignoring changed start numbers.

### 2026-11-18 Semantic review and restored instructions

- Strict audit covered **441/441 counterparts with 0 errors, 311 warnings, and 10 exact exceptions**. Strict mode exits 1. Report: `.agents/skills/translation-checker/.reports/goal-semantic-01-audit.json`.
- Reviewed all 43 category pairs plus the Getting Started and iTerm2 pages for completeness, accuracy, fluency, and terminology. Preserved the localized category labels, stable audio category routes, and Channels ordering. Corrected the distinction between replicas and workers in Getting Started and clarified iTerm2 configuration.
- Validated the 45 reviewed pairs against their source, target, and configuration hashes. Results: `.agents/skills/translation-checker/.reports/semantic-review-batch-01-results.json`. The remaining 396 source and target pairs are in `.agents/skills/translation-checker/.reports/semantic-review-pending.json`.
- Restored memory setting persistence, audit-path behavior, Open Terminal isolation guidance, endpoint timeout concurrency, API passthrough warnings, and descriptive Jupyter image text.
- All **151 behavior tests** passed. The production build passed with zero broken-link, broken-anchor, or duplicate-route diagnostics.

### 2026-11-18 Section omissions and Markdown repairs

- Strict audit covered **441/441 counterparts with 0 errors, 339 warnings, and 10 exact exceptions**. Strict mode still exits 1. The largest remaining groups are terminology (140) and Markdown symbols (86). Full report: `.agents/skills/translation-checker/.reports/goal-markdown.json`.
- Restored 24 environment-variable descriptions, file deletion controls, Event Functions model-list events, terminal authentication steps, Ollama model filtering behavior, and Windows troubleshooting coverage. Repaired list nesting and localized accessibility text where the text was descriptive.
- Protected OS and product names while excluding the common noun in “context windows.” The verifier compares equivalent year durations and pixel scales and keeps section-level terminology omissions and mention-count differences visible as warnings.
- All **151 behavior tests** passed. The production build passed with zero broken-link, broken-anchor, or duplicate-route diagnostics. Full semantic review remains pending.

### 2026-11-18 Direct translation cleanup and numeric verification

- Strict audit: **441/441 counterparts, 0 errors, 457 warnings across 232 files, 10 exact exceptions**. Report: `.agents/skills/translation-checker/.reports/direct-final-audit.json`. Strict mode still exits 1.
- Localized remaining English headings, setup labels, and accessibility text in reviewed sections. Removed a stale duplicate benchmark from the RAG guide; the upstream benchmark remains in its original section.
- The verifier now compares equivalent pixel counts, percentile notation, and open token ranges. It still reports changed values, dropped units, and closed ranges that replace open ones. This pass added no exceptions.
- **150 behavior tests passed**. The production build passed. Full semantic review remains pending.

### 2026-11-18 Serial translation review and verifier fixes (historical)

- Strict audit at this checkpoint: **441/441 counterparts, 0 errors, 680 warnings, 1 exact exception**. Report: `.agents/skills/translation-checker/.reports/goal-resume.json`.
- Reviewed translation batches sequentially. Restored the model controls and version history, an omitted Functions guide entry, and calendar alert behavior. Fixed the audio environment-variable table and retained the monitoring guide's legacy anchor.
- Normalized equivalent acronym plurals, calendar dates, explicit clock notation, and numeric ranges without changing code checks. No translated answers are embedded in the verifier.
- All **138 behavior tests** and the production build passed. The remaining warnings still require review; semantic completeness is not certified.

### 2026-11-18 Warning and exception cleanup, follow-up

- Strict audit: **441/441 counterparts, 0 errors, 810 warnings, 1 exact exception**. Warnings still cause exit 1. Full report: `.agents/skills/translation-checker/.reports/warning-cleanup-final.json`.
- Protected advisory IDs and product names. Normalized equivalent numeric notation and list markers without allowing changes to values, code, or parsed block structure.
- Restored the OpenAI-compatible provider guide's connection verification and model ID details. Localized the community guide's video accessibility labels and fixed nested link indentation.
- All **131 behavior tests** and the production build passed. This does not certify full semantic coverage.

### 2026-11-18 Warning and exception cleanup

- Strict audit: **441/441 counterparts, 0 errors, 951 warnings, 1 exact exception**. Warnings still cause exit 1. The remaining exception preserves the homepage's intentional translation-status notice. Four prior exceptions were replaced with scoped checks for source punctuation, UI labels, empty-string defaults, and terminology typos.
- Localized 58 interface settings labels while retaining keys, default values, and anchors. That page has one numeric review warning, down from 44 warnings. The checker now compares equivalent English and Chinese date formats and reports one language finding per metadata value or heading.
- **127 behavior tests passed**. The environment-reference audit took about 5.2 seconds locally, compared with 7.3 seconds before this pass. Full report: `.agents/skills/translation-checker/.reports/continuation-final-audit.json`.

### 2026-11-18 Verifier and translation repairs

- Checked all 441 counterparts: **0 unwaived errors, 1,079 warnings, 5 exact exceptions**. Strict mode exits 1. All **120 behavior tests**, the Skill validator, and the production build passed. Local evidence: `.agents/skills/translation-checker/.reports/optimized-audit.json`, `optimized-category-review.json` and `optimized-build.log` under the same reports directory.
- The checker now compares numeric defaults within the individual setting. It found two stale defaults: `MCP_INITIALIZE_TIMEOUT` is `10` seconds and `CHUNK_SIZE` is `1024`. The latter entry also lacked the instruction to reindex existing documents. Section checks now group prose in a single pass. A local environment-reference audit took 6.8 seconds versus 13.4 seconds before the change.
- Corrected `PLAYWRIGHT_TIMEOUT` to `10000` milliseconds. The Firecrawl loader accepts positive integer seconds, then clamps the scrape payload to 1000–300000 milliseconds. Verified against `config.py`, `retrieval/web/utils.py`, and `retrieval/web/firecrawl.py` in `open-webui/open-webui@29b4af6b`.
- Restored Firefox link confirmation and prompt-prefill behavior; confirmed the rendered heading and anchor without a verifier exception. Corrected stale banner descriptions, ecosystem instructions, Langfuse tutorial estimates, and task-management links. A clean build does not certify semantic accuracy.
- Rechecked the 43 category pairs under the new configuration. The earlier page reviews below do not count as current passes. Installed-document audits and candidate writes both reject review results missing the configuration hash.

### 2026-11-18 Full translation review checkpoint (prior configuration)

- The English submodule remains pinned at `3072f18`. The working tree updates 91 Chinese pages, including restored code and literals, corrected MCP and Open Terminal guidance, comparison metadata and FAQ translations, and Llama.cpp and vLLM connection instructions. DeepL supplied targeted corrections; translation agents ran one at a time.
- The Firefox heading now renders the literal `browser.ml.chat.prompts.{#}` and keeps the `browsermlchatprompts` anchor. The Chinese HAProxy and Nginx Proxy Manager guides repair malformed upstream fences without changing the commands. Five whitespace-only Nginx code lines intentionally retain upstream bytes.
- **117 behavior tests passed**. The production build passed. The full strict audit covered **441/441 counterparts: 0 unwaived errors, 1,094 warnings, 6 exact exceptions**. Strict mode still exits 1 because warnings remain. Reports: `.agents/skills/translation-checker/.reports/review-checkpoint-audit.json` and `.agents/skills/translation-checker/.reports/review-checkpoint-build.log`.
- **74/441 pairs passed full semantic review**: 43 categories and 31 documents, including all 13 comparison pages. The ignored `.agents/skills/translation-checker/.reports/review-progress.json` binds those results to source, target, and configuration hashes. `.agents/skills/translation-checker/.reports/review-checkpoint-pending.json` contains the remaining 367 pairs. Do not treat the deterministic audit as a semantic pass.
- Issues at this checkpoint included missing Firefox confirmation and prefill details and contradictory upstream `FIRECRAWL_TIMEOUT` units. The later verifier and translation repairs above resolved these issues.

### 2026-11-18 Translation workflow acceptance

- Standardized both providers on offline planning, protected prose extraction, full candidate review, and a strict audit and site build after apply. DeepL resumes saved responses and reuses validated, exact same-page segments. Autonomous mode requires no key. Reviews are bound to the audited file bytes; only passed reviews with matching source, target, and configuration hashes can be reused.
- The offline DeepL plan for `alternatives/` and `reference/env-configuration.mdx` found **2,052 duplicate segments** across 14 files. No API request was needed for the estimate. No live provider calls or documentation changes were made during acceptance.
- **114 offline behavior tests passed** on Python 3.14. The Skill validator and production build passed. Full strict audit: **441/441 counterparts, 80 errors, 1,202 warnings, 0 exceptions**. Matching counterparts include 398 pages and 43 category files. The strict audit still fails; no full semantic pass is claimed. The audit is in ignored `.agents/skills/translation-checker/.reports/acceptance-audit-final.json`.

### 2026-11-18 Translation repairs and focused verifier improvements

- Updated 89 Chinese documents across authentication/access, enterprise, chat/audio/search, extensibility, getting started, reference, and troubleshooting. Repairs restore upstream code comments, string values and literals; align stale navigation and instructions; and remove obsolete or duplicated content. The upstream submodule remains at `3072f18`; both trees still contain 398 documents and 43 categories.
- OpenAPI server guides restore model-reliability guidance and array-query support, and follow current integration, MCP and OAuth instructions. SSO troubleshooting distinguishes signup controls and logout scope. Manual database migration restores the revision-history explanation and matching-version requirement for offline migration. A quoted Mistral diagnostic was restored verbatim from upstream.
- Preservation checks now reject changed code comments/strings, preserve all fence directives except prose titles, protect JSON-LD technical values, and check literal-only lines. Both translation providers receive prose fence titles; filename/path titles remain literal. Source-derived quoted diagnostics inside troubleshooting/error sections stay verbatim. No translations or bilingual answer tables are hard-coded in tests; fixtures use generated CJK characters.
- Fixed demonstrated parser false positives involving dollar prices, bare-path sentence punctuation, keyword lists, backticked identifiers/product names, indented JSX children, and inline HTML examples. Broken upstream fence boundaries produce visible review signals when code comparison is unreliable; unrelated upstream parse defects never relax code preservation. No fingerprint exceptions were added.
- Validation: **99 behavior tests passed**. Full audit: **441/441 counterparts, 79 errors, 1195 warnings, 0 exceptions**. The 89 edited documents have **0 errors and 289 heuristic warnings**. The full strict audit still fails; remaining findings need triage and cannot be treated as a semantic certification. Production build passes with zero broken-link, anchor, Markdown-link, or duplicate-route diagnostics.
- Hash-bound full-pair semantic review passes for **20 edited authentication/enterprise pages**. The other **69 edited pages remain pending full semantic review** after translation agents encountered service-capacity errors. Subsequent retries ran sequentially as requested and also failed; no unfinished review was marked passed. Local audit and review artifacts are under ignored `.agents/skills/translation-checker/.reports/`. No live DeepL requests were made.
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
- `non_compliant_link_patterns` in `.agents/skills/translation-checker/translation_config.json` lists the community links the project policy removes. A listed link may be absent from the translation, a translation that keeps one is reported as `non-compliant-link`, and a code span that exists only in the removed sentence disappears with it.
- Validation: **81 behavior tests passed** on Python 3.14. Strict working-tree audit covered **441/441** files, reporting **182 errors, 1422 warnings, 0 exceptions** (down from 646 errors / 1365 warnings when the tooling landed and 272 errors after the first repair pass). The remaining findings are historical drift outside this pass and need triage, not blanket suppression. The strict audit still returns failure and semantic review remains **required**.

### 2026-11-17 Translation verification tooling

- Added the Python suite under `test/`, including source-derived completeness/preservation checks, quality warnings, full-pair AI review bundles, and validation of hash-bound semantic review results.
- Translation expectations are never hard-coded. Behavior tests use generated CJK text; only terminology and other literal exclusions are stored verbatim.
- Added autonomous AI translation tasks requiring no configuration, plus optional DeepL mode requiring only `DEEPL_AUTH_KEY` in root `.env`. Both use protected placeholders and the same guarded apply path. No live translation requests were made.
- Updated `.agents/skills/upstream-sync/SKILL.md` and fixed `AGENTS.MD` pointers for the user's `.github/` to `.codex/` skill/agent move.
- Validation: **58 behavior tests passed** on Python 3.14. CI tests Python 3.10 and 3.14. Strict working-tree audit covered **441/441** files (398 documents and 43 categories), reporting **646 errors, 1365 warnings, 0 exceptions**. These include historical differences and possible intentional localization; they require triage, not blanket suppression. Reproduce with `python .agents/skills/translation-checker/scripts/translation_check.py --strict --report .agents/skills/translation-checker/.reports/full-audit.json`.
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

Run from the repository root after installing Git and uv. Check the pinned
submodule revision, verify counterpart coverage and preservation, and run the
behavior tests.

```sh
git submodule update --init -- en-us
git submodule status
uv sync --locked
uv run --locked --offline translation-check --strict --summary-only
uv run --locked --offline python -m unittest discover -s .agents/skills/translation-checker/scripts -p "test_*.py"
```
