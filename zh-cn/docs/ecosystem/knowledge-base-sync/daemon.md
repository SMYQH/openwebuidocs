---
sidebar_position: 2
title: "守护进程、Webhook 与部署"
---

# 运行守护进程

[主页](/ecosystem/knowledge-base-sync)上的 CLI 介绍了一次性和监听式同步。对于无人值守、定时或由外部事件驱动的同步，请将 oikb 作为长期运行的**守护进程**来使用。它会读取你的 [`.oikb.yaml`](#the-oikbyaml-config-file)，按各自的时间表同步每个来源，并提供一个小型 HTTP API，用于健康检查、指标、历史记录和按需触发。

```bash
oikb daemon
```

| 标志 | 默认值 | 用途 |
|---|---|---|
| `--port` | `8080` | HTTP API 和健康检查的端口。 |
| `--config` | `./.oikb.yaml` | 配置文件的路径。 |
| `--log-format` | `text` | `text` 或 `json`。也可通过 `LOG_FORMAT` 设置。 |
| `--no-server` | 关闭 | 仅运行调度器，不启动 HTTP 服务器（无 API、无 webhook、无指标）。 |

启动时，它会打印已配置的来源、身份验证是否开启以及端点 URL。

---

## `.oikb.yaml` 配置文件

命令行上的单个来源不需要配置文件。对于多个来源、定时调度、webhook 或守护进程，你需要在 `.oikb.yaml` 中描述所有内容。使用 `oikb init` 交互式生成，或手动编写：

```yaml
defaults:                      # 可选，应用于下方的每个条目
  interval: 1h
  concurrency: 4
  filter:
    max-size: 50mb

sources:
  - name: wiki                 # 友好的别名，用于 CLI/API 定位
    source: github:owner/repo
    kb-id: 8f3a2b1c-...
    webhook: true              # 也在推送时同步（参见 Webhook）

  - name: handbook
    source: confluence:ENG
    kb-id: 4e7d9a0f-...
    interval: "0 6 * * 1-5"    # 覆盖默认的时间间隔
    notify:
      url: https://hooks.slack.com/services/T.../B.../xxx
      on: error
```

**每个条目的键：** `name`、`source`、`kb-id`（两个必需的键是 `source` 和 `kb-id`）、`interval`、`concurrency`、`branch`、`path`、`filter`（`include` / `exclude` / `max-size`）、`notify`、`webhook` 以及各供应商的 webhook 密钥（`github_secret`、`gitlab_secret`、`slack_signing_secret`）。你还可以为每个条目单独设置 `url` 和 `token`，以便将不同的来源指向不同的服务器。

**默认值**会深度合并到每个条目中，因此 `filter` 和 `notify` 等嵌套块会组合而非替换；条目上设置的任何键都会覆盖默认值。

**环境变量插值：** 所有字符串值都支持 `${VAR}` 和 `${VAR:-default}`。这可以将密钥排除在文件之外，使其可提交：

```yaml
sources:
  - name: docs
    source: github:${GITHUB_ORG}/docs
    kb-id: ${KB_DOCS_ID}
    token: ${OPEN_WEBUI_API_KEY}
    notify:
      url: ${SLACK_WEBHOOK:-https://hooks.slack.com/fallback}
```

:::note
顶层键是 `sources:`。旧的名称 `sync:` 仍然有效，以保持向后兼容。
:::

文件存在后，`oikb sync`（不带来源参数）会运行每个条目一次，而 `oikb sync --name wiki` 只运行一个。

---

## 定时调度

每个条目的 `interval` 可以是简单的持续时间或 cron 表达式。oikb 通过计数字段自动检测，因此无需标志：

```yaml
interval: 30m               # 简单：每 30 分钟
interval: 1h                # 每小时
interval: "0 6 * * 1-5"     # cron：工作日上午 6:00
interval: "0 */6 * * *"     # cron：每 6 小时
```

简单持续时间支持 `s`、`m`、`h`、`d`。同一文件中的不同条目可以混合使用两种格式。

---

## HTTP API

| 端点 | 认证 | 描述 |
|---|:---:|---|
| `GET /` | 公开 | 状态仪表板（一个轮询 `/health` 的小页面）。 |
| `GET /health` | 公开 | 每个来源的同步状态：上次运行时间、持续时间、文件数、错误。 |
| `GET /health/ready` | 公开 | Docker/Kubernetes 的就绪探针。 |
| `GET /metrics` | 公开 | Prometheus 指标。 |
| `GET /history` | 🔒 | 同步历史记录，可通过 `kb_id` 和 `errors_only` 进行过滤。 |
| `POST /sync/{name-or-kb-id}` | 🔒 | 触发立即同步。添加 `?dry_run=true` 仅预览。 |
| `POST /webhooks/github` · `/gitlab` · `/slack` · `/confluence` | 签名 | 推送时实时同步（参见 [Webhook](#webhooks)）。 |

触发的同步在后台运行并立即返回；轮询 `/health` 以了解进度。`dry_run=true` 触发器同步运行并返回新增/修改/删除的计数。

### 身份验证

设置 `OIKB_API_KEY` 以保护守护进程。健康检查、就绪探针、指标和仪表板端点保持公开（以便探针和采集器继续工作）；`/history` 和 `/sync` 则需要 bearer 令牌：

```bash
export OIKB_API_KEY=your-secret-key
oikb daemon
```

```bash
curl -X POST http://localhost:8080/sync/wiki \
  -H "Authorization: Bearer your-secret-key"
```

对于 Docker/Kubernetes 密钥，请设置 `OIKB_API_KEY_FILE` 为文件路径，而不是将密钥放在环境变量中。（同时设置两者会报错。）

---

## Webhook

为条目启用 `webhook: true` 后，守护进程会在来源发生变化的瞬间进行同步，而无需等待下一次定时调度。推送负载通过仓库或空间匹配到正确的条目，因此一个守护进程可以为多个来源提供服务。

```yaml
sources:
  - name: docs
    source: github:owner/repo
    kb-id: abc123
    webhook: true
    github_secret: ${GITHUB_WEBHOOK_SECRET}   # 验证负载签名
```

然后在源系统中添加一个指向守护进程的 webhook：

- **GitHub** → 仓库设置 → Webhooks → `http://your-daemon:8080/webhooks/github`。设置了 `github_secret` 后，`X-Hub-Signature-256` HMAC 会被验证，任何未签名或签名不匹配的请求将被拒绝并返回 `403`。
- **GitLab** → `…/webhooks/gitlab`，通过 `X-Gitlab-Token` 标头使用 `gitlab_secret` 进行验证。
- **Slack** → `…/webhooks/slack`，使用 `slack_signing_secret`（Slack 的 v0 请求签名）进行验证。该端点还会响应 Slack 的 URL 验证挑战。
- **Confluence** → `…/webhooks/confluence`，按空间键匹配。

如果你不设置密钥，签名检查将被跳过，因此在这种情况下，请仅在受信任的网络中暴露守护进程。

### 同步锁定

每个知识库都有自己的锁。如果一个 webhook 在同一个知识库的定时同步仍在运行时触发，重复的同步将被跳过（并记录日志），而不是与第一个同步竞争。这是自动的，无需配置。

---

## 可观测性

### Prometheus 指标

`GET /metrics` 导出计数器和持续时间直方图，所有指标都按来源标记：

| 指标 | 类型 | 含义 |
|---|---|---|
| `oikb_sync_total` | counter | 同步次数，按来源和状态区分。 |
| `oikb_sync_duration_seconds` | histogram | 同步持续时间。 |
| `oikb_files_uploaded_total` | counter | 新增加修改的文件数。 |
| `oikb_files_deleted_total` | counter | 删除的文件数。 |
| `oikb_sync_errors_total` | counter | 失败的同步次数。 |
| `oikb_info` | gauge | 构建版本。 |

```yaml
scrape_configs:
  - job_name: oikb
    static_configs:
      - targets: ["oikb:8080"]
```

### 结构化 JSON 日志

对于日志聚合器（Datadog、Splunk、ELK、CloudWatch、Loki），每行输出一个 JSON 对象：

```bash
oikb daemon --log-format json     # 或 LOG_FORMAT=json
```

### 失败通知

为条目添加 `notify`，可在同步失败（或始终）时向任意 HTTP 端点 POST 一个 JSON 负载。负载包含一个 `text` 字段，因此 Slack 的 incoming webhook 可以直接渲染它：

```yaml
notify:
  url: https://hooks.slack.com/services/T.../B.../xxx
  on: error            # error（默认）| always
```

同样的格式也适用于 PagerDuty、Opsgenie 或你自己的接收器。除了 `text` 字段外，它还包含结构化的字段（`source`、`status`、`error`、`duration_ms`、文件计数）。

### 同步历史记录

每次运行都会记录在本地 SQLite 数据库中。通过 API（`GET /history`）或 CLI 查询：

```bash
oikb history                    # 最近的运行记录，表格视图
oikb history --errors           # 仅失败的记录
oikb history --json             # 机器可读格式
oikb history --clear --days 7   # 清理超过 7 天的记录
```

---

## 让模型触发同步

守护进程也是一个 **[OpenAPI 工具服务器](/features/extensibility/mcp)**。将 Open WebUI 指向它，模型就可以在聊天过程中通过工具调用来触发同步、检查状态和读取同步历史记录：

> **你：** 手册知识库看起来过时了。重新同步一下，告诉我有什么变化。
>
> *（模型调用 `trigger_sync`，轮询 `get_sync_status`，然后回答。）*
>
> **助手：** 已重新同步 `handbook`：4 个文件已更新，1 个已移除。目前是最新状态。

它在 `GET /openapi.json` 处提供一个规范，暴露了恰好三个操作（仪表板、指标、健康检查和 webhook 路由被隐藏，因此模型只能看到有用的那些）：

| 工具 | 映射到 | 功能 |
|---|---|---|
| `trigger_sync` | `POST /sync/{identifier}` | 按别名或知识库 ID 启动同步（可选 dry-run）。 |
| `get_sync_status` | `GET /health` | 报告每个来源的当前状态和上次结果。 |
| `get_sync_history` | `GET /history` | 返回最近的同步运行记录。 |

连接方法：

1. **首先确保安全。** 设置 `OIKB_API_KEY`，使 `/sync` 和 `/history` 不对任何能访问守护进程的人开放。
2. 将守护进程的 URL（例如 `http://oikb:8080`）添加为工具服务器：**管理员设置 → 外部工具** 用于实例范围连接，或**设置 → 工具** 用于个人连接。提供相同的 `OIKB_API_KEY` 作为连接的 API 密钥。

这是一个标准的 OpenAPI 工具服务器连接，与 [OpenAPI / MCP 工具服务器](/features/extensibility/mcp)页面描述的机制相同；oikb 恰好是另一端的服务。

---

## 部署

### Docker

```bash
docker run -d \
  -e OPEN_WEBUI_URL=http://open-webui:8080 \
  -e OPEN_WEBUI_API_KEY=sk-... \
  -e OIKB_API_KEY=your-daemon-key \
  -e LOG_FORMAT=json \
  -v ./.oikb.yaml:/app/.oikb.yaml:ro \
  -p 8080:8080 \
  ghcr.io/open-webui/oikb:latest daemon
```

### Docker Compose

将其与 Open WebUI 部署在同一个网络上，以便通过服务名称访问服务器：

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"

  oikb:
    image: ghcr.io/open-webui/oikb:latest
    environment:
      - OPEN_WEBUI_URL=http://open-webui:8080
      - OPEN_WEBUI_API_KEY=${OPEN_WEBUI_API_KEY}
      - OIKB_API_KEY=${OIKB_API_KEY}
      - LOG_FORMAT=json
    volumes:
      - ./.oikb.yaml:/app/.oikb.yaml:ro
    command: daemon
    ports:
      - "8080:8080"
    depends_on:
      - open-webui
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health/ready"]
      interval: 30s
      timeout: 5s
```

### Kubernetes

从 ConfigMap 挂载配置，从 Secret 拉取密钥，并将探针连接到健康端点：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oikb
spec:
  replicas: 1
  selector:
    matchLabels: { app: oikb }
  template:
    metadata:
      labels: { app: oikb }
    spec:
      containers:
        - name: oikb
          image: ghcr.io/open-webui/oikb:latest
          args: ["daemon"]
          ports:
            - containerPort: 8080
          env:
            - name: OPEN_WEBUI_URL
              value: http://open-webui:8080
            - name: OPEN_WEBUI_API_KEY
              valueFrom: { secretKeyRef: { name: oikb-secrets, key: open-webui-api-key } }
            - name: OIKB_API_KEY
              valueFrom: { secretKeyRef: { name: oikb-secrets, key: oikb-api-key } }
            - name: LOG_FORMAT
              value: json
          volumeMounts:
            - name: config
              mountPath: /app/.oikb.yaml
              subPath: .oikb.yaml
          livenessProbe:
            httpGet: { path: /health/ready, port: 8080 }
            initialDelaySeconds: 5
            periodSeconds: 30
          readinessProbe:
            httpGet: { path: /health, port: 8080 }
            initialDelaySeconds: 10
            periodSeconds: 60
      volumes:
        - name: config
          configMap: { name: oikb-config }
```

:::caution 运行单个副本
定时调度器和每个知识库的锁存在于单个进程中，因此守护进程应以**一个副本**的形式运行。水平扩展会导致两个调度器同时同步同一个知识库。要覆盖更多来源，请在一个守护进程中添加条目，而不是运行多个配置副本。
:::

### GitHub Actions

对于基于推送的、构建时的一次性同步（而非长期运行的守护进程），将镜像作为一次性步骤运行。请参阅主页上的 [CI 中的一次性同步](/ecosystem/knowledge-base-sync#one-shot-sync-in-ci)。

---

## 另请参阅

- **[知识库同步 (oikb)](/ecosystem/knowledge-base-sync)**：安装、来源、连接器、过滤和 CLI。
- **[知识库](/features/workspace/knowledge)**：oikb 所保持同步的知识库功能。
- **[OpenAPI / MCP 工具服务器](/features/extensibility/mcp)**：连接外部工具服务器到 Open WebUI。
