# AGENTS.MD — Open WebUI Documentation Knowledge Base

> AGENTS.MD (this document) is time-sensitive. Agent assistants **must** update this document synchronously as the project evolves. See Section 8.
> Do not blindly trust this document; content may be out of date.
> Current document snapshot `Git Commit Hash`: `6929d535287dc2496f756049795c9543021866a9`, `Commit` timestamp: `2026-07-22T01:17:52+08:00`

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
| `zh-cn/` | Directly Maintained | This repository | Simplified Chinese | Cloudflare Pages |

* `en-us/` is included as a Git submodule pointing to `[https://github.com/open-webui/docs.git](https://github.com/open-webui/docs.git)`.
* The internationalization strategy uses "cloning the full project then translating" rather than Docusaurus's built-in i18n mechanism for two reasons: 1. Upstream does not have built-in i18n enabled; 2. This maintenance strategy facilitates side-by-side English-Chinese comparison and makes syncing future upstream updates easier.

---

## 2. Tech Stack

Built on Docusaurus. Documentation formats are primarily MDX, with some `.md` files.

---

## 3. Key Differences Between EN and ZH Sites

| Configuration Item | en-us | zh-cn |
| --- | --- | --- |
| tagline | "On a mission to build the best AI interface" | "致力于打造最佳 AI 界面" |
| doc Exclude Rules | `**/tab-**/**`, `**/_template.*` | `**/tab-**/**` |
| Navbar | Blog, GitHub, Discord | 博客, GitHub |
| Footer | Docs, Community, More | 文档, 社区, 更多 |

### Documentation Organization

* Sidebar is fully auto-generated; sorting and labels are controlled via `_category_.json` (supports emoji prefixes).
* Tab contents (`tab-*/` directories) are included via MDX `<Tabs>` components and do not appear in the sidebar.
* Edit links point to `[https://github.com/open-webui/docs/blob/main](https://github.com/open-webui/docs/blob/main)`.

---

## 4. Repository Directory Structure

```text
open-webui-docs/                # Root repository
├── AGENTS.MD                   # This document
├── Readme.md
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
├── ecosystem/                  # Standalone Open WebUI ecosystem projects (Computer, Knowledge Base Sync)
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
| `getting-started/` | Installation methods (Docker/K8s/Python), provider connections (Ollama/OpenAI, etc.), upgrade guides | Keep commands and configuration keys in English. |
| `features/` | Largest section: Chat, Voice, Image Generation, RAG, Web Search, Auth/RBAC, Plugins/Pipelines, Open Terminal, etc. | Translate feature names and UI interaction descriptions. |
| `ecosystem/` | Standalone Open WebUI projects: Computer (cptr) — full OS environment in-browser; Knowledge Base Sync (oikb) — folder/repo incremental sync | The Computer section is quite large (~63 files); keep commands and environment variable names in English. |
| `reference/` | Environment variables reference (2500+ lines), API docs, HTTPS setup, monitoring | **Do not** translate environment variable names and code snippets. |
| `tutorials/` | Auth/SSO integration tutorials, third-party tool integrations, community deployments | Translate step-by-step instructions; keep code blocks and configurations untouched. |
| `troubleshooting/` | Various troubleshooting guides | Keep error messages in their original form. |
| `enterprise/` | Enterprise architecture, deployment, case studies | Same as above. |
| `security/` | Security policy, CVE disclosures | Same as above. |
| `alternatives/` | Comparisons with 13 alternative products | Same as above. |

---

## 6. Content Conventions

* Format: Primarily MDX, with some `.md` files.
* Category sorting: Controlled via `_category_.json` (`label`, `position`, `collapsible`, `collapsed`).
* Tab contents: Placed in `tab-*/` directories, imported via MDX `Tabs` components, hidden from the sidebar.
* Category labels can use emojis, e.g., `💬`, `⭐`, `🎓`, `🔧` inside `_category_.json`.

### Translation Principles

* **Do NOT translate**: Code blocks, commands, environment variable names, configuration keys, error messages, and product/brand names.
* **DO translate**: Body text, headers, UI interaction descriptions, and step-by-step instructions.
* When syncing standalone static assets (images, etc.) from `en-us` to `zh-cn`, make sure to copy them to `./zh-cn/` as well.
* The Chinese version will remove non-compliant external links (Discord, Reddit, X, etc.).

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
3. Modifying translation conventions → Update AGENTS.MD "Content Conventions"; modifying upstream sync procedures → Update `.github/skills/upstream-sync/SKILL.md`.
4. Adding new language sites → Update AGENTS.MD "Project Overview".
5. Changes in the `en-us` submodule snapshot → Update the commit hash, file count, and coverage rate data in STATUS.md.

---

## 9. Upstream Sync Workflow

When new commits appear in the official English documentation (`en-us/` submodule), updates will be synchronized and translated into `zh-cn/`.

**The full procedure has migrated to a Skill**: [`.github/skills/upstream-sync/SKILL.md`](https://www.google.com/search?q=.github/skills/upstream-sync/SKILL.md)

* Trigger method: Type `/upstream-sync` in Chat, or describe "sync upstream / sync upstream / pull en-us updates".
* This file only retains project-level conventions (translation principles, directory structure, EN-ZH differences); step-level operations follow that Skill.
* When modifying the sync workflow, you **must** update that Skill simultaneously and adjust the pointers in this section accordingly.
