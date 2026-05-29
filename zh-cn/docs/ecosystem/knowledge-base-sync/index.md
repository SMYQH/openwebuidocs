---
sidebar_position: 1
title: "知识库同步 (oikb)"
slug: /ecosystem/knowledge-base-sync
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# 知识库同步 (oikb)

<ThemedImage
  alt="知识库同步：多种不同的源连接器通过 oikb 同步枢纽流入 Open WebUI 知识库"
  sources={{
    light: useBaseUrl('/images/banners/kbsync-light.svg'),
    dark: useBaseUrl('/images/banners/kbsync-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**让知识库与事实源自动保持同步。**

[oikb](https://github.com/open-webui/oikb) 是官方配套工具，用于将内容镜像到[知识库](/features/workspace/knowledge)。将其指向本地文件夹、GitHub 仓库、Confluence 空间、S3 存储桶或其余 44 种连接器中的任何一种，它就能让知识库保持最新状态。

与一次性上传（源一旦发生变化就会过时）不同，oikb 执行的是**增量**同步：它将知识库与一个动态源一次性连接，然后通过定时调度、每次推送或按需触发的方式保持其新鲜度。文档仓库、Wiki、存储桶——全都能保持最新，无需专人照看。

它是一个独立的程序（命令行工具加一个可选的长期运行[守护进程](/ecosystem/knowledge-base-sync/daemon)），并非 Open WebUI 服务器的一部分，但它是为 Open WebUI 构建的，并通过标准 REST API 与其通信。

:::info 需要 Open WebUI 0.9.6+
oikb 驱动了 **v0.9.6** 中新增的增量同步端点（`/sync/diff` 和 `/sync/cleanup`）。如果服务器版本更旧，则没有可供调用的接口。这些端点的服务器端行为在[知识库 → 同步本地目录](/features/workspace/knowledge#syncing-a-local-directory)中有文档说明。
:::

---

## 为什么要使用知识库同步？

### 仅传输变更内容

每个文件都会计算哈希值（SHA-256）并与服务器已有的内容进行比较，因此只有新增和修改过的文件会上传，删除操作也会被同步移除。一个包含 10,000 个文件且未发生变化的仓库，重新同步只需几秒钟，因为没有任何内容需要重新上传或重新嵌入。频繁运行几乎没有成本。

### 专为大型库设计

应用内的**同步目录**操作在浏览器中运行，因此对于大型集合（数千个文件或数 GB 的库），它会变得缓慢且进度显示不明显。oikb 原生运行，带有进度条、并行上传和重试机制，因此数万个文件的库也能可靠同步。**如果你的语料库很大，这是推荐的加载方式。**

### 一个工具，覆盖所有来源

将其指向本地文件夹、Git 仓库、Confluence 或 Notion 空间、S3 存储桶、Jira 项目、Slack 频道以及 30 多种其他来源。相同的命令和相同的增量引擎适用于所有来源。

### 自动保持最新

手动同步一次，或者交给[守护进程](/ecosystem/knowledge-base-sync/daemon)按时间间隔、cron 或有人推送时立即运行。一个与动态源连接的知识库再也不会悄悄过时。

### 模型也能驱动它

守护进程还充当 [OpenAPI 工具服务器](/ecosystem/knowledge-base-sync/daemon#let-the-model-trigger-syncs)，因此模型可以在对话中触发重新同步并报告结果，无需任何人接触命令行。

---

## 主要功能

| | |
| :--- | :--- |
| ⚡ **增量同步** | SHA-256 差异比较，仅上传新增和修改的文件；删除的文件被移除，未变化的文件保持不变 |
| 🌐 **44 种连接器** | 本地文件夹、Git、云存储、Wiki、工单系统、聊天、CRM，以及一个网页爬虫 |
| ⏱️ **定时与 Webhook 同步** | 按时间间隔、cron 或有人推送时立即运行（通过守护进程） |
| 👀 **监听模式** | 每次保存时自动同步本地文件夹 |
| 🎯 **选择性同步** | 包含/排除 glob 模式、大小限制，以及将一个来源拆分为多个知识库 |
| 🤖 **模型可触发** | 守护进程是一个 OpenAPI 工具服务器，因此模型可以从聊天中启动和检查同步 |
| 🔑 **使用你的权限** | 以你的用户身份进行身份验证，绝不绕过知识库访问控制 |
| 📊 **生产就绪** | Prometheus 指标、结构化 JSON 日志、同步历史和失败通知 |

---

## 安装

```bash
pip install oikb
```

需要 **Python 3.11+** 和 **Open WebUI 0.9.6+** 服务器。大多数连接器使用普通 HTTP 通信，无需额外依赖。少数连接器需要各自的 SDK，可作为可选附加组件安装：

```bash
pip install oikb[s3]       # Amazon S3
pip install oikb[gcs]      # Google Cloud Storage
pip install oikb[azure]    # Azure Blob
pip install oikb[dropbox]  # Dropbox
pip install oikb[gdrive]   # Google Drive
pip install oikb[all]      # 一次性安装所有可选连接器
```

完整的可选组件列表为：`s3`、`gcs`、`azure`、`dropbox`、`r2`、`gdrive`、`gmail`、`gsites`、`web`、`oracle`、`sharepoint-cert` 和 `all`。表中未列出的连接器（GitHub、Confluence、Notion、Jira、Slack 以及大多数其他连接器）无需额外安装。

对于生产环境，Docker 镜像发布在 `ghcr.io/open-webui/oikb`。请参阅[运行守护进程](/ecosystem/knowledge-base-sync/daemon#deployment)。

---

## 快速开始

```bash
export OPEN_WEBUI_URL=http://localhost:3000
export OPEN_WEBUI_API_KEY=sk-your-api-key   # 设置 → 账户 → API 密钥

# 将本地文件夹同步到知识库
oikb sync ./docs --kb-id your-kb-id

# 或者同步 GitHub 仓库，无需本地克隆
oikb sync github:owner/repo --kb-id your-kb-id

# 预览将要发生的变化，不上传任何内容
oikb sync ./docs --kb-id your-kb-id --dry-run
```

`--kb-id` 是知识库的 ID，即工作区中 URL 的 UUID（`.../knowledge/<kb-id>`）。重复运行相同的命令两次，第二次运行将不执行任何操作：只有内容发生变化的文件才会被处理。

### 同步过程示例

第一次运行上传所有内容；之后的每次运行只传输发生变化的部分：

```console
$ oikb sync github:acme/handbook --kb-id 8f3a2b1c-...
  1,204 files found
  Diff: +3, ~1, -2, 1198 unchanged
  Uploading ━━━━━━━━━━━━━━━━━━━━ 4/4 • 0:00:02
Sync complete: 3 added, 1 modified, 2 deleted, 1198 unchanged
```

`Diff` 行是服务器对"实际发生了什么变化"的回答：三个新文件、一个修改、两个删除，以及 1,198 个保持原样。

:::note 访问权限即你的权限
API 密钥以**你**的用户身份进行身份验证。oikb 只能读取和写入该用户已有权限的知识库。它不是管理员后门，也不会绕过[访问控制](/features/authentication-access/rbac)。
:::

### 保存凭据

这样你就不必在每次命令时重复输入 URL 和密钥：

```bash
oikb config set url http://localhost:3000
oikb config set token sk-your-api-key
oikb config get                    # 显示已保存的内容（令牌会被掩码处理）
```

保存到 `~/.config/oikb/config.yaml`（通过 `OIKB_CONFIG_DIR` 覆盖目录）。解析顺序，优先级从高到低：

1. CLI 标志（`--url`、`--token`）
2. 环境变量（`OPEN_WEBUI_URL`、`OPEN_WEBUI_API_KEY`）
3. 配置文件

---

## 增量同步的工作原理

1. oikb 扫描源并为每个文件计算 **SHA-256** 校验和。
2. 它将这个清单（路径、文件名和校验和，**不是**文件内容）发送到 Open WebUI 的 `/sync/diff`，服务器回复确切**新增**、**修改**和**删除**的内容，以及需要创建或移除的目录。此调用是只读的，不会更改知识库。
3. oikb 删除过时的文件（以及现在为空的目录），创建缺失的目录，然后仅上传**新增**和**修改**的文件，每个文件都带有其哈希标签，以便服务器跳过重新哈希。

由于差异比较基于内容哈希，未发生变化的仓库几乎可以立即重新同步：没有内容被重新上传、重新提取或重新嵌入，因此频繁运行没有成本。只有真正的变更才会产生工作。

上传期间的临时服务器错误（HTTP 5xx）会以指数退避方式重试最多三次。默认情况下上传按顺序执行；对于大型同步，传递 `--concurrency N`（或在每个条目中设置 `concurrency:`）可并行上传 N 个文件。

对应的服务器端行为以及为你自己的脚本公开的相同两个端点在[知识库 → 同步本地目录](/features/workspace/knowledge#syncing-a-local-directory)和[知识库 → API 访问](/features/workspace/knowledge#api-access)中有文档说明。oikb 是经过维护的客户端，实现了完整的同步循环，并在其基础上增加了调度、webhook 和 44 种连接器。

---

## 来源与连接器

**来源**可以是本地路径，也可以是 `scheme:target` 格式的字符串。oikb 将 scheme 解析为对应的连接器，拉取文件并将其同步到知识库。凭据永远不会写入来源字符串或 `.oikb.yaml` 中；每个连接器从**环境变量**中读取凭据，因此密钥不会出现在你的配置中（配合 [`${VAR}` 插值](/ecosystem/knowledge-base-sync/daemon#the-oikbyaml-config-file)使用，可使配置文件可提交）。

在下表中，`[括号]` 表示来源字符串中的可选部分。

| 分组 | 连接器 | 来源字符串 | 凭据（环境变量） |
|---|---|---|---|
| **本地** | 本地目录 | `./path`（任意文件系统路径） | 无 |
| **代码** | GitHub | `github:owner/repo` | `GITHUB_TOKEN`（私有仓库） |
| | GitLab | `gitlab:owner/repo` | `GITLAB_TOKEN`、`GITLAB_URL`（自托管） |
| | Bitbucket | `bitbucket:owner/repo` | `BITBUCKET_USER`、`BITBUCKET_APP_PASSWORD` |
| **云存储** | Amazon S3 | `s3://bucket/prefix` | 标准 AWS 凭据链（boto3） |
| | Google Cloud Storage | `gs://bucket/prefix` | `GOOGLE_APPLICATION_CREDENTIALS` |
| | Azure Blob | `az://container/prefix` | `AZURE_STORAGE_CONNECTION_STRING` |
| | Cloudflare R2 | `r2://bucket/prefix` | `R2_ACCOUNT_ID`、`R2_ACCESS_KEY_ID`、`R2_SECRET_ACCESS_KEY` |
| | Oracle Cloud | `oci://bucket/prefix` | `OCI_NAMESPACE` + OCI SDK 配置 |
| | Dropbox | `dropbox:/path` | `DROPBOX_TOKEN` |
| | Google Drive | `gdrive:folder_id` | `GOOGLE_APPLICATION_CREDENTIALS` |
| | SharePoint | `sharepoint:site[/library]` | `SHAREPOINT_TENANT_ID`、`SHAREPOINT_CLIENT_ID` 和 `SHAREPOINT_CLIENT_SECRET` **或** `SHAREPOINT_CERTIFICATE_PATH` |
| | Egnyte | `egnyte:/path` | `EGNYTE_DOMAIN`、`EGNYTE_TOKEN` |
| **Wiki 与知识库** | Confluence | `confluence:SPACE` | `CONFLUENCE_URL`、`CONFLUENCE_USER`、`CONFLUENCE_TOKEN` |
| | Notion | `notion:root_id` | `NOTION_TOKEN` |
| | BookStack | `bookstack:` | `BOOKSTACK_URL`、`BOOKSTACK_TOKEN_ID`、`BOOKSTACK_TOKEN_SECRET` |
| | Discourse | `discourse:[category]` | `DISCOURSE_URL`、`DISCOURSE_API_KEY`、`DISCOURSE_API_USERNAME` |
| | GitBook | `gitbook:space_id` | `GITBOOK_TOKEN` |
| | Guru | `guru:[collection]` | `GURU_USER`、`GURU_TOKEN` |
| | Outline | `outline:[collection]` | `OUTLINE_URL`、`OUTLINE_TOKEN` |
| | Slab | `slab:[org]` | `SLAB_ORG`、`SLAB_TOKEN` |
| | Document360 | `document360:project_id` | `DOCUMENT360_TOKEN` |
| | DokuWiki | `dokuwiki:[namespace]` | `DOKUWIKI_URL`、`DOKUWIKI_USER`、`DOKUWIKI_PASSWORD` |
| | Google Sites | `gsites:site_id` | `GOOGLE_SITES_TOKEN` |
| **工单系统** | Jira | `jira:PROJECT` | `JIRA_URL`、`JIRA_USER`、`JIRA_TOKEN` |
| | Linear | `linear:team_key` | `LINEAR_TOKEN` |
| | Zendesk | `zendesk:[subdomain]` | `ZENDESK_SUBDOMAIN`、`ZENDESK_USER`、`ZENDESK_TOKEN` |
| | Freshdesk | `freshdesk:[domain]` | `FRESHDESK_DOMAIN`、`FRESHDESK_TOKEN` |
| | Asana | `asana:project_id` | `ASANA_TOKEN` |
| | ClickUp | `clickup:space_id` | `CLICKUP_TOKEN` |
| | Airtable | `airtable:base_id[/table]` | `AIRTABLE_TOKEN` |
| | ServiceNow | `servicenow:[table]` | `SERVICENOW_INSTANCE`、`SERVICENOW_USER`、`SERVICENOW_PASSWORD` |
| | ProductBoard | `productboard:` | `PRODUCTBOARD_TOKEN` |
| **消息** | Slack | `slack:channel_id` | `SLACK_TOKEN` |
| | Discord | `discord:channel_id` | `DISCORD_TOKEN` |
| | Microsoft Teams | `teams:team_id/channel_id` | `TEAMS_TENANT_ID`、`TEAMS_CLIENT_ID`、`TEAMS_CLIENT_SECRET` |
| | Gmail | `gmail:user@example.com` | `GOOGLE_APPLICATION_CREDENTIALS` |
| | Zulip | `zulip:[stream]` | `ZULIP_URL`、`ZULIP_EMAIL`、`ZULIP_KEY` |
| **会议** | Gong | `gong:` | `GONG_ACCESS_KEY`、`GONG_ACCESS_KEY_SECRET` |
| | Fireflies | `fireflies:` | `FIREFLIES_TOKEN` |
| **销售与 CRM** | Salesforce | `salesforce:` | `SALESFORCE_URL`、`SALESFORCE_TOKEN` |
| | HubSpot | `hubspot:` | `HUBSPOT_TOKEN` |
| **论坛** | XenForo | `xenforo:[forum_id]` | `XENFORO_URL`、`XENFORO_KEY` |
| **网页** | 网站 / sitemap | `web:https://example.com` | 无 |

一些值得了解的连接器说明：

- **GitHub** 通过 Trees API 读取，因此无需本地克隆。添加 `--branch` 和 `--path`（或在配置中使用 `branch:` / `path:`）来定位特定分支或子目录。
- **聊天连接器**（Slack、Discord、Teams）按天分割历史记录，从而实现真正的增量同步：过去的日子是不可变的，因此它们的校验和永远不会改变，也永远不会被重新上传。
- **Jira** 和 **ServiceNow** 接受来源字符串中的额外选项（查询条件、字段、输出格式、结果限制），例如 `servicenow:incident?query=...&limit=500`。请参阅 [oikb 仓库](https://github.com/open-webui/oikb)了解每个连接器的完整选项。

---

## 过滤同步内容

使用包含/排除 glob 模式和大小的限制来缩小来源范围。这些配置位于 [`.oikb.yaml`](/ecosystem/knowledge-base-sync/daemon#the-oikbyaml-config-file) 的 `filter:` 下：

```yaml
sources:
  - name: docs
    source: github:owner/repo
    kb-id: your-kb-id
    filter:
      include: ["docs/**/*.md", "*.txt"]   # 仅包含这些
      exclude: ["drafts/**", "**/*.tmp"]   # 排除这些（在包含之后应用）
      max-size: 50mb                        # 跳过任何大于此值的文件
```

`max-size` 支持 `b`、`kb`、`mb`、`gb`。超过大小限制的文件会在差异比较前发出警告并跳过，因此它们永远不会上传。它也可以作为 CLI 标志使用：`oikb sync ./docs --kb-id abc --max-file-size 50mb`。

要将一个来源的不同部分路由到不同的知识库，请使用不同的 `filter.include` 和 `kb-id` 创建单独的条目：

```yaml
sources:
  - name: user-docs
    source: github:owner/repo
    kb-id: abc123
    filter: { include: ["docs/**"] }
  - name: api-reference
    source: github:owner/repo
    kb-id: def456
    filter: { include: ["api/**"] }
```

### 跳过的文件和 `.oikbignore`

同步**本地目录**时，oikb 始终跳过隐藏条目（任何以 `.` 开头的）以及内置列表：`.git`、`.svn`、`.hg`、`.DS_Store`、`Thumbs.db`、`__pycache__`、`.pytest_cache`、`node_modules`、`.oikb`、`.env`。

对于项目特定的排除项，请在同步根目录下放置一个 `.oikbignore` 文件。它使用 gitignore 风格的 glob 模式（末尾的 `/` 仅匹配目录，开头的 `/` 锚定到根目录）。暂不支持使用 `!` 进行否定。

---

## 监听模式

对于你正在积极编辑的本地目录，`watch` 会在文件发生变化的瞬间重新同步：

```bash
oikb watch ./docs --kb-id your-kb-id
```

它使用文件系统事件（而非轮询），去抖时间为一秒（通过 `--debounce` 调整），并持续运行直到你按 Ctrl+C 停止。适用于实时笔记文件夹；对于远程或无人值守的场景，请改用[守护进程](/ecosystem/knowledge-base-sync/daemon)。

---

## CI 中的一次性同步

Docker 镜像可以作为一次性命令运行，使其成为[GitHub Actions](/ecosystem/knowledge-base-sync/daemon#deployment) 中一个即插即用的步骤，用于在每次合并时将文档推送到知识库：

```yaml
- name: Sync docs to Open WebUI
  uses: docker://ghcr.io/open-webui/oikb:latest
  with:
    args: sync /github/workspace/docs --kb-id ${{ secrets.KB_ID }}
  env:
    OPEN_WEBUI_URL: ${{ secrets.OPEN_WEBUI_URL }}
    OPEN_WEBUI_API_KEY: ${{ secrets.OPEN_WEBUI_API_KEY }}
```

---

## CLI 参考

| 命令 | 功能 |
|---|---|
| `oikb sync <source>` | 从来源增量同步到知识库（`--kb-id`）。省略 `<source>` 将同步 [`.oikb.yaml`](/ecosystem/knowledge-base-sync/daemon#the-oikbyaml-config-file) 中的所有条目。 |
| `oikb sync --dry-run` | 预览新增/修改/删除的内容，不执行上传。 |
| `oikb sync --concurrency N` | 并行上传 N 个文件（默认为 1，顺序执行）。 |
| `oikb sync --max-file-size 50mb` | 跳过超过指定大小的文件。 |
| `oikb sync --name <alias>` | 在 `.oikb.yaml` 模式下，仅同步匹配的条目。 |
| `oikb diff <source> --kb-id ID` | 预览变更（`sync --dry-run` 的别名）。 |
| `oikb watch <dir> --kb-id ID` | 本地目录变更时自动同步（`--debounce`）。 |
| `oikb init` | 交互式向导，生成 `.oikb.yaml` 文件。 |
| `oikb validate` | 检查 `.oikb.yaml` 语法。添加 `--deep` 还会 ping Open WebUI、验证 API 密钥并确认每个知识库存在。 |
| `oikb daemon` | 运行带有 HTTP API 的定时[守护进程](/ecosystem/knowledge-base-sync/daemon)。 |
| `oikb ls --kb-id ID` | 列出知识库中的文件。 |
| `oikb status --kb-id ID` | 显示知识库的名称、文件数和总大小。 |
| `oikb history` | 查看同步历史记录（`--json`、`--errors`、`--kb-id`、`--clear --days N`）。 |
| `oikb reset --kb-id ID` | 删除知识库中的所有文件（`--keep-directories` 保留文件夹结构）。需要确认。 |
| `oikb config set url\|token <value>` | 保存 Open WebUI URL 或 API 密钥。`oikb config get` 显示它们。 |

在任何命令后添加 `-q` / `--quiet` 可抑制非错误输出（在脚本中很有用），添加 `-v` / `--verbose` 可查看每个文件的详细信息。

:::warning `oikb reset` 会删除知识库中的所有内容
`reset` 会删除目标知识库中的**所有**文件，而不仅仅是 oikb 上传的文件。这是唯一一个有破坏性的命令。确认提示的存在是有原因的。
:::

---

## 使用场景

### 始终保持最新的产品文档

将你的文档仓库（`github:acme/docs`）连接到知识库，并在 CI 中每次合并时或在 webhook 触发时进行同步。支持人员和客户查询的文档永远不会超过一次提交的滞后。

### 大型个人或家庭文档库

数以千计的混合文档（PDF、Markdown、扫描件、记录）存放在一个组织良好的文件夹中。将 oikb 指向该文档库的顶层，它会同步整个树（包括所有子目录）到单个知识库中，这样家庭成员就可以提问，而无需知道答案在哪个子文件夹中。应用内同步在这种规模下表现不佳；oikb 正是为此而构建的。

### 来自 Wiki 的公司手册

通过早晨的 cron 任务将 Confluence 空间或 Notion 工作区镜像到知识库。一个"HR 问答"模型会从当前手册中回答，而 Wiki 中的编辑会在第二天自动显示，无需任何人重新上传。

### 来自工单的支持知识

将已解决的 Zendesk 或 Jira 工单同步到知识库中，这样分类模型可以查找类似问题之前是如何处理的，基于你自己的历史数据而非通用训练数据。

### 代码感知助手

使用过滤器将一个仓库拆分为两个知识库：`docs/**` 下的文档放入"文档"知识库，`src/**` 下的源代码放入"代码"知识库。根据需要附加相应的知识库，两者都通过单个配置保持同步。

---

## 限制

### 需要 Open WebUI 0.9.6+

增量同步端点在 v0.9.6 中引入。如果服务器版本更旧，oikb 将无法调用任何接口。

### 守护进程以单进程运行

定时调度和每个知识库的锁位于单个进程中，因此[守护进程](/ecosystem/knowledge-base-sync/daemon#deployment)应以**一个副本**的形式运行。要覆盖更多来源，请在一个守护进程中添加条目，而不是运行多个副本。

### 索引仍在服务端进行

oikb 上传很快，但 Open WebUI 会异步提取和嵌入每个新文件。刚刚同步的文件已在知识库中，但可能需要片刻才能被查询到。

---

## 故障排除

**`Connection refused` 或 `401 Unauthorized`**：URL 或密钥错误或未设置。使用 `oikb config get` 检查，或运行 `echo $OPEN_WEBUI_URL` 和 `echo $OPEN_WEBUI_API_KEY`。密钥必须是有效的 Open WebUI API 密钥（设置 → 账户）。

**`No source specified and no .oikb.yaml found`**：你运行了 `oikb sync` 但未指定来源，且当前目录中没有 `.oikb.yaml`。请传递一个来源（`oikb sync ./docs --kb-id ...`）或使用 `oikb init` 创建配置文件。

**大型同步速度慢**：添加 `--concurrency 4` 实现并行上传，设置 `filter.max-size` 跳过大型二进制文件，并使用 `filter.exclude` 排除模型不需要的内容。

**守护进程无法启动 / 知识库似乎缺失**：运行 `oikb validate --deep`。它会验证服务器是否可达、API 密钥是否有效以及配置中的每个 `kb-id` 是否确实存在。

**我的知识库 ID 在哪里？**在工作区中打开知识库；UUID 是 URL 的最后一个路径段 `.../knowledge/<kb-id>`。

---

## 另请参阅

- **[运行守护进程 →](/ecosystem/knowledge-base-sync/daemon)**：定时同步、webhook、HTTP API、可观测性、部署以及让模型触发同步。
- **[知识库](/features/workspace/knowledge)**：oikb 所对接的知识库功能，包括服务端[同步端点](/features/workspace/knowledge#api-access)。
- **[OpenAPI / MCP 工具服务器](/features/extensibility/mcp)**：守护进程如何作为模型可调用的工具接入。
