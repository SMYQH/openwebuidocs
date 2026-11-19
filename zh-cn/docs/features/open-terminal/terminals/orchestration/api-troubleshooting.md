---
sidebar_position: 10
title: "API 和故障排除"
---

# API 和故障排除 {#api-and-troubleshooting}

调用编排器的任何策略或生命周期端点时，都必须提供以下请求头：

```http
Authorization: Bearer {TERMINALS_API_KEY}
```

## 策略 API {#policy-api}

| 方法 | 端点 | 用途 |
| :--- | :--- | :--- |
| `GET` | `/api/v1/policies` | 列出策略 |
| `POST` | `/api/v1/policies` | 创建策略 |
| `GET` | `/api/v1/policies/{policy_id}` | 读取策略 |
| `PUT` | `/api/v1/policies/{policy_id}` | 创建或更新策略 |
| `DELETE` | `/api/v1/policies/{policy_id}` | 删除策略 |

策略请求体示例：

```json
{
  "image": "ghcr.io/acme/open-terminal:python-ds",
  "cpu_limit": "4",
  "memory_limit": "16Gi",
  "storage": "20Gi",
  "storage_mode": "per-user",
  "env": {
    "OPEN_TERMINAL_ALLOWED_DOMAINS": "*.pypi.org,github.com",
    "OPEN_TERMINAL_SYSTEM_PROMPT": "You are working on {{os}} at {{home}}."
  },
  "idle_timeout_minutes": 60
}
```

## 策略生命周期 API {#policy-lifecycle-api}

| 方法 | 端点 | 用途 |
| :--- | :--- | :--- |
| `GET` | `/api/v1/policies/{policy_id}/lifecycle` | 读取策略生命周期配置 |
| `PUT` | `/api/v1/policies/{policy_id}/lifecycle` | 创建或更新策略生命周期配置 |

生命周期请求体示例：

```json
{
  "reset": {
    "schedule": "@weekly",
    "timezone": "UTC"
  }
}
```

## 状态 API {#status-api}

| 方法 | 端点 | 用途 |
| :--- | :--- | :--- |
| `GET` | `/api/v1/status` | 编排器状态（用于管理 UI） |
| `GET` | `/api/v1/terminals` | 列出活跃终端/会话（用于管理 UI） |

## 刷新 API {#refresh-api}

| 方法 | 端点 | 用途 |
| :--- | :--- | :--- |
| `POST` | `/api/v1/terminals/refresh` | 停止匹配的终端，以便下次重新预配 |
| `POST` | `/api/v1/terminals/stop` | 停止指定用户的指定终端，下次访问时重新启动 |

刷新请求体：

```json
{
  "user_id": "optional-user-id",
  "policy_id": "optional-policy-id",
  "context_id": "optional-context-id",
  "only_idle": true,
  "reset": false
}
```

`only_idle` 默认为 `true`。`reset` 默认为 `false`。省略 `context_id` 则匹配用户的所有上下文。

停止请求体：

```json
{
  "user_id": "...",
  "policy_id": "default",
  "context_id": "default"
}
```

`policy_id` 默认为 `default`。

`context_id` 也默认为 `default`，对应共享终端。传入 `chat:<chat-id>` 或 `automation:<automation-id>`，可指定由[终端上下文](/features/open-terminal/terminals/orchestration/contexts)创建的一个独立终端。停止操作默认只影响共享终端。对于按聊天分配终端的连接，只有显式指定该聊天的终端才会将其停止。

## 故障排除 {#troubleshooting}

### 环境变量需要加引号吗？ {#do-i-need-quotes-around-env-vars}

不需要。完全按照容器应接收的方式输入值。仅当引号字符是预期值的一部分时才需要引号。

### 我可以将环境变量传递给编排器并让它转发吗？ {#can-i-pass-env-vars-to-the-orchestrator-and-have-it-forward-them}

在策略的 `env` 中设置要传入各用户 Open Terminal 容器的变量。编排器进程的环境变量只用于配置编排器本身。

### 为什么我的环境变量或镜像更改没有生效？ {#why-did-my-env-var-or-image-change-not-apply}

用户可能已有正在运行的终端。保存策略，然后刷新匹配的终端，或等待终端因空闲而停止。

### 为什么用户无法在文件浏览器中访问 `/etc`？ {#why-cant-users-browse-to-etc-in-the-file-browser}

对于编排器管理的终端，文件浏览器从 Open Terminal 报告的根目录开始，不显示其上级目录。默认根目录为 `Home`。这项设计旨在减少用户困惑和相关支持请求，不构成安全边界。

要更改文件浏览器显示的根目录，请将 `OPEN_TERMINAL_FILE_BROWSER_ROOT` 设为明确的路径，例如 `/workspace`。若不想限制显示范围，请在策略的 `env` 中设置 `OPEN_TERMINAL_FILE_BROWSER_ROOT=filesystem`，然后刷新受影响的终端。
