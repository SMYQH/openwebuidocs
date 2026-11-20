# AGENTS.MD — Open WebUI Documentation Knowledge Base

> AGENTS.MD (this document) is time-sensitive. Agent assistants **must** update this document synchronously as the project evolves. See Section 8.
> Do not blindly trust this document; content may be out of date.
> Current document snapshot `Git Commit Hash`: `a7d62b3`, `Commit` timestamp: `2026-11-20T12:25:42+08:00`

---

## 1. Project Overview

**Remote Repositories**: `[https://github.com/SMYQH/openwebuidocs](https://github.com/SMYQH/openwebuidocs)` (Chinese version); `[https://github.com/open-webui/docs](https://github.com/open-webui/docs)` (Official English version)

**Official English Site**: `[https://docs.openwebui.com](https://docs.openwebui.com)`

**Unofficial Chinese Preview**: `[https://open-webui-docs.pages.dev](https://open-webui-docs.pages.dev)`

**Project Goal**: Provide an unofficial Simplified Chinese translation of the official Open WebUI self-hosted documentation.

The root repository contains a Git submodule and a directly maintained subdirectory:

| Path | Role | Git Repository | Language | Deployment |
| --- | --- | --- | --- | --- |
| `en-us/` | Git Submodule | `open-webui/docs` | English | GitHub Pages (deployed upstream) |
| `zh-cn/` | Directly Maintained | This repository | Simplified Chinese | Cloudflare Workers |

* `en-us/` is included as a Git submodule pointing to `[https://github.com/open-webui/docs.git](https://github.com/open-webui/docs.git)`.
* The internationalization strategy uses "cloning the full project then translating" rather than Docusaurus's built-in i18n mechanism for two reasons: 1. Upstream does not have built-in i18n enabled; 2. This maintenance strategy facilitates side-by-side English-Chinese comparison and makes syncing future upstream updates easier.

---

## 2. Tech Stack

Built on Docusaurus. Documentation formats are primarily MDX, with some `.md` files. The repository root provides a `wrangler.jsonc` configuration that deploys the Chinese site's `zh-cn/build/` static output to Cloudflare Workers.

**CI/CD**: `.github/workflows/deploy.yml` builds `zh-cn/` and deploys via Wrangler on push to `main` (or manual dispatch). Required GitHub Actions secrets: `DOMAIN` (site URL for Docusaurus `url`/`baseUrl`; hostname is also checked against account zones for automatic Custom Domain binding), `TOKEN` (Cloudflare API Token → `CLOUDFLARE_API_TOKEN`; needs Workers deploy + `Zone:Zone:Read`), `ID` (Cloudflare Account ID → `CLOUDFLARE_ACCOUNT_ID`).

**DeepL CLI**: The [checker skill](.agents/skills/translation-checker/references/usage.md#deepl-cli) documents plain-text translation, quota lookup, and resumable back-translation of installed Chinese prose. Use back-translations as evidence for bilingual review. Verify differences against both original documents. If quota cannot cover any pending text, keep the checkpoint and continue reading the pairs offline.

**Sitemap generation**: The Chinese site intentionally disables Docusaurus's built-in sitemap output. During `postbuild`, `zh-cn/scripts/sync-sitemap.mjs` downloads `https://docs.openwebui.com/sitemap.xml`, rewrites the upstream origin to the origin parsed from `DOMAIN` (defaulting to HTTPS when the scheme is omitted), and writes `zh-cn/build/sitemap.xml`. Deployment builds must pass `DOMAIN`; local or pull-request builds without `DOMAIN` skip synchronization. Download, validation, or write failures must fail the deployment build rather than publish a missing/stale sitemap.

**Link validation**: `zh-cn/docusaurus.config.ts` sets `onBrokenLinks: "throw"`, `onBrokenAnchors: "throw"`, `onDuplicateRoutes: "throw"` and `markdown.hooks.onBrokenMarkdownLinks: "throw"`. Production and CI builds must contain zero broken links, zero broken anchors, zero broken markdown links and zero duplicate routes.

**Translation verification and providers**: Python translation checks, behavior tests, and both provider helpers live in the [translation-checker skill](.agents/skills/translation-checker/SKILL.md); see its [usage reference](.agents/skills/translation-checker/references/usage.md). Install `.agents/skills/translation-checker/requirements.txt`, run the behavior tests, then run `python .agents/skills/translation-checker/scripts/translation_check.py --strict --report .agents/skills/translation-checker/.reports/audit.json`. Deterministic checks distinguish hard preservation failures from heuristic quality warnings: a dropped literal fails, an added or re-counted literal is a review signal; link destinations are compared after resolution and JSON-LD prose fields separately from protected types, contexts, URLs and surrounding code; upstream parse defects are warnings, so a translation never inherits broken upstream structure. Two classes are exempt from the verbatim rule: an interface label in a code span may be translated, and a link the project policy removes may be dropped - `non_compliant_link_patterns` lists the allowed hosts and a kept link is reported as `non-compliant-link`. Code comments and string values remain verbatim; only prose fence title values may be translated, and both update providers expose those titles as prose segments. Literal-only lines are checked. Prices are not math, sentence punctuation is not part of bare paths, and keyword lists do not count as copied prose. JSX child indentation and inline HTML examples cannot hide prose. Quoted diagnostic headings inside upstream troubleshooting/error sections remain literal in both providers and language checks. Code mismatches caused by broken upstream fence boundaries require direct review; unrelated parse defects never relax code preservation. File/heading coverage does not prove semantic completeness. Full source/target review bundles and hash-bound review results support autonomous AI review without configuration. An edit to a translated file expires the exact exceptions of that file, because a fingerprint mixes the file path, both file hashes, the finding line, the rule and the finding text; `scripts/restamp_exceptions.py` re-binds the surviving exceptions to their current fingerprints, keeps the reviewed reason of every finding that still exists, and reports the findings that need a manual decision. Translation updates default to autonomous AI tasks with protected placeholders. Optional DeepL mode requires only `DEEPL_AUTH_KEY` in root `.env`; both providers share validation before writes. `.github/workflows/translation-tools.yml` tests the tooling on Python 3.10 and 3.14 without calling DeepL.

**Upstream site-code sync**: `zh-cn/src/`, `zh-cn/scripts/`, `zh-cn/package.json` and the localized `zh-cn/docusaurus.config.ts` are re-synced from the `en-us` submodule on every upstream sync, but the zh-cn localization of `docusaurus.config.ts` (tagline, url, i18n locale, navbar/footer labels, `editUrl`, `exclude` rules, `sitemap: false` and the Google Analytics setup) is preserved — never overwrite it with the upstream file. Upstream's PostHog module (`src/clientModules/analytics.js`) is vendored so the newly ported components compile, but it is inert on the Chinese host because `isProductionHost()` only matches `docs.openwebui.com`; the Chinese site keeps its own GA4 setup (`src/clientModules/ensure-gtag.js`). Upstream's `scripts/check-index-links.mjs` is vendored as `npm run check-index-links` but is **not** wired into `prebuild`: the Chinese pages intentionally use relative links on index pages, which that script rejects.

**Custom domain auto-bind**: Before `wrangler deploy`, the workflow uses the API token to list zones under the account. If `DOMAIN`'s hostname is covered by an active zone, it patches `wrangler.jsonc` with `routes: [{ pattern, custom_domain: true }]`, sets `workers_dev: false` (production `*.workers.dev` off), and keeps `preview_urls: true`. If the hostname is `*.workers.dev` / `*.pages.dev`, or no matching zone exists, binding is skipped and production `workers.dev` remains enabled.

**Public-repo log hygiene**: This repository is public; Actions logs are world-readable. Workflow steps must **never** print secret values or secret-derived inventory (Account ID, API token, full DOMAIN/url/hostname, zone name lists, zone IDs). Diagnostics may log counts and generic status only (e.g. zone count, “bound custom domain”). Cloudflare API error logs must not dump response bodies or request paths that embed account/zone identifiers. Note: `wrangler deploy` itself may still emit the public site URL in its own CLI output.
---

## 3. Key Differences Between EN and ZH Sites

| Configuration Item | en-us | zh-cn |
| --- | --- | --- |
| tagline | "On a mission to build the best AI interface" | "致力于打造最佳 AI 界面" |
| doc Exclude Rules | `**/tab-**/**`, `**/_template.*` | `**/tab-**/**` |
| Navbar | Blog, GitHub, Discord | 博客, GitHub |
| Footer | Docs, Community, More | 文档, 社区, 更多 |
| Sitemap | Docusaurus/upstream-generated | Build-time mirror of upstream sitemap with origin rewritten from `DOMAIN` |
| Duplicate routes | `onDuplicateRoutes: "throw"` | `onDuplicateRoutes: "throw"` (same) |
| Broken markdown links | `markdown.hooks.onBrokenMarkdownLinks: "throw"` | `markdown.hooks.onBrokenMarkdownLinks: "throw"` (same) |
| Analytics | PostHog (`src/clientModules/analytics.js`), enabled only on `docs.openwebui.com` | Google Analytics (`G-522JSJVWTB`) via `src/clientModules/ensure-gtag.js`; upstream's PostHog module is vendored but inert on the Chinese host |
| Broken anchor handling | Upstream configuration | Build fails (`onBrokenAnchors: "throw"`) |

### Documentation Organization

* Sidebar is fully auto-generated; sorting and labels are controlled via `_category_.json` (supports emoji prefixes).
* Tab contents (`tab-*/` directories) are included via MDX `<Tabs>` components and do not appear in the sidebar.
* Edit links on the Chinese site point at the Chinese sources in this repository: `editUrl: "https://github.com/SMYQH/openwebuidocs/blob/main/zh-cn"` in the localized `zh-cn/docusaurus.config.ts`, which renders as `[https://github.com/SMYQH/openwebuidocs/blob/main/zh-cn/docs/<path>](https://github.com/SMYQH/openwebuidocs/blob/main/zh-cn/docs/<path>)`. The English upstream site keeps pointing at `[https://github.com/open-webui/docs/blob/main](https://github.com/open-webui/docs/blob/main)`.

---

## 4. Repository Directory Structure

```text
open-webui-docs/                # Root repository
├── AGENTS.MD                   # This document
├── Readme.md
├── .agents/skills/             # Shared skills and Python translation tooling
├── en-us/                      # English upstream (Git submodule → open-webui/docs)
│   └── docs/                   # English documentation source (translation baseline)
└── zh-cn/                      # Chinese translation (directly maintained)
    ├── docs/                   # Translated MD/MDX documents
    ├── src/                    # Custom components and styles
    └── static/                 # Standalone static assets (images, etc.)

```

### docs/ Top-Level Directory Structure

```text
docs/
├── intro.mdx                   # Home / Landing page
├── getting-started/             # Quick start
├── features/                   # Core features (largest section)
├── ecosystem/                  # Standalone Open WebUI ecosystem projects (Tether, Knowledge Base Sync, Community)
├── tutorials/                  # Tutorials
├── troubleshooting/            # Troubleshooting
├── reference/                  # Reference documents
├── enterprise/                 # Enterprise
├── security/                   # Security
└── alternatives/               # Competitor comparisons

```

---

## 5. Documentation Domains Overview

| Directory | Content | Translation Notes |
| --- | --- | --- |
| `getting-started/` | Installation methods (Docker/K8s/Python), production `deployment/` guides (AWS ECS, Azure Container Apps, Docker Swarm, Google Cloud Run, Kubernetes), provider connections (Ollama/OpenAI, etc.), upgrade guides | Keep commands and configuration keys in English. |
| `features/` | Largest section: Chat, Voice, Image Generation, RAG, Web Search, Auth/RBAC, Plugins (the standalone Pipelines section was removed upstream in 2026-07), Open Terminal, Channels (Apps, encrypted chats), Workspace, Administration, etc. | Translate feature names and UI interaction descriptions. |
| `ecosystem/` | Standalone Open WebUI projects: Tether — desktop companion app that connects your computer to the instance; Knowledge Base Sync (oikb) — folder/repo incremental sync; Community (openwebui.com) — shared models, prompts, tools and functions | Keep commands and environment variable names in English. |
| `reference/` | Environment variables reference (2500+ lines), API docs, HTTPS setup, monitoring, Tether client protocol (native-client sign-in and handshake) | **Do not** translate environment variable names and code snippets. |
| `tutorials/` | Auth/SSO integration tutorials, third-party tool integrations, community deployments | Translate step-by-step instructions; keep code blocks and configurations untouched. |
| `troubleshooting/` | Various troubleshooting guides | Keep error messages in their original form. |
| `enterprise/` | Enterprise architecture, deployment, case studies | Same as above. |
| `security/` | Security policy, CVE vendor dispositions, accepted risks, supply-chain security (scanner behaviour and rejected-CVE records in downstream vulnerability databases) | Same as above. |
| `alternatives/` | Comparisons with 13 alternative products | Same as above. |

---

## 6. Content Conventions

* Format: Primarily MDX, with some `.md` files.
* Category sorting: Controlled via `_category_.json` (`label`, `position`, `collapsible`, `collapsed`).
* Tab contents: Placed in `tab-*/` directories, imported via MDX `Tabs` components, hidden from the sidebar.
* Category labels can use emojis, e.g., `💬`, `⭐`, `🎓`, `🔧` inside `_category_.json`.
* Cross-page and durable section links must use explicit stable IDs. When translating a heading referenced by an English fragment, preserve that fragment on the Chinese heading, e.g. `## Web 搜索 {#web-search}`, and update same-page links to the explicit ID. Do not rely on automatically generated Chinese/URL-encoded heading IDs for durable links.
* **Explicit IDs must be derived from upstream, not from the Chinese title.** Re-derive every ID with the upstream `github-slugger` slug of the *English* heading (including Docusaurus's dedup suffixes `slug-1`, `slug-2`, …). Two headings that share a Chinese title therefore need distinct IDs, and a Chinese-only heading still needs a unique, English-style ID.
* **MDX escaping for explicit IDs.** Docusaurus only escapes `{#id}` on headings that start at column 0, so inside a JSX block (e.g. a heading nested in `<TabItem>`) the brace is parsed as a JSX expression and the build fails with `Could not parse expression with acorn`. Write the ID as `\{#id}` in that position. In `.md` files, keep the plain `{#id}` form.
* If a heading contains a literal `{#}` before its explicit ID, escape both opening braces. Verify the displayed text and anchor in the built page; the MDX preprocessor only escapes the first occurrence, even in `.md` files compiled as MDX. The verifier treats the escaped form as the same literal, not as an MDX expression.
* **Never place an explicit ID inside a fenced code block.** A `{#id}` appended to a shell/YAML comment is rendered literally and is not an anchor; keep code blocks byte-identical to upstream.
* **Escape underscores inside explicit IDs.** Docusaurus extracts the ID from the *rendered* heading text, so a double underscore in an ID (`{#__id__}`, `{#events-using-__event_emitter__-in-open-webui}`) is parsed as markdown emphasis and silently drops the underscores from the generated anchor (`#id`, `#events-using-event_emitter-in-open-webui`). Upstream links then resolve to nothing. Write such IDs with escaped underscores (`{#\_\_id\_\_}`, `{#events-using-\_\_event\_emitter\_\_-in-open-webui}`) - the rendered anchor is unchanged, but the emphasis parser no longer eats it.
* **A Chinese heading's title and its body must belong to the same upstream section.** Explicit IDs are positional: when the upstream heading list is ported, the *n*-th Chinese heading gets the *n*-th upstream ID. If a Chinese heading title is permuted relative to that position (or a whole block of prose is rotated into the neighbouring section), the anchor still resolves but the page shows the wrong content under the right anchor. After any structural realignment, re-verify per section that the Chinese title, the Chinese body and the upstream heading for the ID all describe the same topic - do not verify the ID alone.
* **Inline code spans that carry verbatim content must stay verbatim.** Endpoints (`POST /api/v1/...`), filesystem paths, environment variable names, template placeholders (`{{CONTEXT}}`, `<server ID>_<tool name>`, `hf.co/{username}/{repository}:{quantization}`), CLI commands and identifiers in backticks are literals, not prose: translating the placeholders inside them changes the meaning and breaks the upstream reference. UI *menu labels* outside code spans may be translated, and an interface label that upstream marks with a code span (`Settings`, `Admin Panel`, `Image Generation Engine`) may be translated as well, because the Chinese site shows a Chinese interface. Identifiers, commands, paths, values and product names keep their spelling inside code spans.
* **The heading-structure audit must not be skipped when the section counts differ.** Compare the Chinese heading list against the English one section by section even if the two files have different numbers of headings; a count mismatch is itself the defect signal (a stale, duplicated or deleted section) and hides every anchor mismatch below it.
* Bare identifiers may gain backticks without changing their counts. A surplus code span must contain the whole identifier verbatim. An upstream code span cannot satisfy both an inline and a bare occurrence.
* A thematic break must be preceded by a blank line. A `---` line that directly follows a paragraph is parsed as a **setext H2**, which silently turns the rule into an empty heading and drops the horizontal rule. This applies after `:::` admonition blocks and after list items too.
* Escape a literal pipe as `\|` inside code spans in GFM table cells. The table parser consumes the escape and renders the original code value. The verifier rejects unescaped pipes that split code across cells and unexpected control characters in documents.
* Verify types and numeric or boolean defaults within the setting row they belong to. The same value elsewhere is not evidence of correctness. Treat `setting-type` and `setting-default` warnings as review leads, especially for reordered fields, unit conversions, and conflicting upstream documentation.
* When two calendar days share a month and year, preserve both complete dates. The verifier compares their calendar values, not their word order.
* Preserve deadline values and units. When upstream uses one unit for two coordinated deadlines, the translation may state the unit for both.
* Before completing documentation changes, run a production build and require zero broken-link and broken-anchor diagnostics. Do not suppress failures with `onBrokenAnchors: "warn"` or `"ignore"`.
* Translation verification must derive checks from the current source and structure. Never hard-code translations, bilingual answer tables, or expected translated-answer snapshots in the checker tooling; terminology and other literal exclusions are the only exceptions. Behavior tests use generated text. Semantic completeness, accuracy, fluency, and heading/body alignment require full pair review. Exact-fingerprint exceptions need specific reasons and expire when either document changes.
* Prefer narrow preservation rules over exact exceptions for recurring source defects. The verifier compares localized dates and explicit AM/PM times by value. A standalone English month needs date context, not a preposition found inside another word. The verifier preserves empty-string defaults in their own setting row and recognizes documented bare terminology corrections without relaxing code or configuration keys.
* Review protected terms within each matching section, including terms in headings, bold text, and code spans. A repeated mention elsewhere cannot establish that the original section is complete. Inspect the source context when a term may be part of an interface label.
* Verify replaced inline code identifiers in the sections that use them. The checker warns when a repeated identifier disappears from one section and a new identifier appears there.
* Preserve advisory identifiers such as CVE and GHSA IDs verbatim, including in titles. Equivalent list marker spellings require matching parsed structure. Ordered lists must keep their start value; subsequent marker numbers may differ when the rendered sequence is unchanged. Localized numeric ranges must retain their endpoints and units.
* An explicit Chinese calendar span (`年间`) with two four-digit years may match a bare range. It is not equivalent to a duration in years.
* Day ordinals compare by sequence position. A label such as `on day 8` is not an eight-day duration or a count per day.
* Prose durations after a slash retain their units in rate expressions. URL and path literals remain verbatim.
* Protect bare Windows drive-letter paths as whole literals. Do not treat their directory names as prose terminology.
* Duration and token ranges must preserve whether the upper bound can be exceeded. A standalone open duration such as `12+ minutes` must preserve its open bound, value, and unit. Localized pixel counts and percentile ranks must preserve their value and unit. Policy-listed contact links may be removed with their directory row when the row contains only a host label and its link. Preserve surrounding rows and other links.

### Translation Principles

* **Do NOT translate**: Code blocks, commands, environment variable names, configuration keys, error messages, and product/brand names.
* **DO translate**: Body text, header display text, UI interaction descriptions, and step-by-step instructions. Preserve stable explicit heading IDs where links depend on the original English fragment.
* **API terminology**: Use `端点` for explicit request URIs, `API` or `协议` for a named interface or protocol, `基础 API 端点` for a BaseURL, and `API 端点` for a common address shared by a family of routes. Keep webhook destinations distinct. Separate English words from adjacent Chinese text with spaces in prose; preserve literal UI labels, URLs, and code.
* When syncing standalone static assets (images, etc.) from `en-us` to `zh-cn`, make sure to copy them to `./zh-cn/` as well.
* The Chinese version will remove non-compliant external links (Discord, Reddit, X, etc.). The verifier reads `non_compliant_link_patterns` in `.agents/skills/translation-checker/translation_config.json`: a listed link may be absent from the translation, and a translation that keeps one is reported as `non-compliant-link`.

---

## 7. External References

* **Open WebUI GitHub**: `[https://github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)`
* **Release Notes**: `[https://github.com/open-webui/open-webui/blob/main/CHANGELOG.md](https://github.com/open-webui/open-webui/blob/main/CHANGELOG.md)`
* **Official Online Docs**: `[https://docs.openwebui.com](https://docs.openwebui.com)`

---

## 8. Self-Maintenance Guidelines

When the following changes occur in the project, `AGENTS.MD` and `STATUS.md` **must** be updated:

1. Adding or deleting documentation directories/categories → Update AGENTS.MD "Documentation Domains Overview".
2. Modifying build tools or site configurations → Update AGENTS.MD "Tech Stack" and "Key Differences Between EN and ZH Sites".
3. Modifying translation conventions → Update AGENTS.MD "Content Conventions"; modifying upstream sync procedures → Update `.agents/skills/upstream-sync/SKILL.md`.
4. Adding new language sites → Update AGENTS.MD "Project Overview".
5. Changes in the `en-us` submodule snapshot → Update the commit hash, file count, and coverage rate data in STATUS.md.

---

## 9. Upstream Sync Workflow

When new commits appear in the official English documentation (`en-us/` submodule), updates will be synchronized and translated into `zh-cn/`.

**Upstream synchronization and release gates**: [`upstream-sync`](.agents/skills/upstream-sync/SKILL.md).

**Verification skills**: [`translation-semantic-review`](.agents/skills/translation-semantic-review/SKILL.md) covers full bilingual reading and evidence. [`translation-checker`](.agents/skills/translation-checker/SKILL.md) covers Python commands, diagnostics, and review artifacts.

* Trigger method: Type `/upstream-sync` in Chat, or describe "sync upstream / sync upstream / pull en-us updates".
* This file only retains project-level conventions (translation principles, directory structure, EN-ZH differences); step-level operations follow that Skill.
* When modifying the sync workflow, you **must** update that Skill simultaneously and adjust the pointers in this section accordingly.
* Use one audit to validate installed review results and export the remaining pairs. The checker skill and its [usage reference](.agents/skills/translation-checker/references/usage.md) document the combined options.
* For file-wide terminology recount and Markdown symbol warnings, use the JSON report's `section_drift` to find the affected headings and compare their text. Locations do not change the finding or its fingerprint.
* Verification/tooling-only requests use offline acceptance tests, not translation requests. Autonomous translation needs no provider configuration; DeepL requires only the root `.env` key. Use the Skill's offline plan, exact-match reuse, and checkpoint resume to avoid repeat requests. Both modes require a full, hash-bound candidate review before CLI writes, then a strict audit and production build. Only unchanged passed reviews may be reused. An exception-only config update requires the old config digest and a fresh deterministic audit before reuse. Respect user-directed delegation and concurrency limits.
