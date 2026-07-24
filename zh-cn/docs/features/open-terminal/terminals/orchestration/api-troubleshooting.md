---
sidebar_position: 8
title: "API 和故障排除"
---

# API 和故障排除

所有编排器策略和生命周期端点都需要：

```http
Authorization: Bearer {TERMINALS_API_KEY}
```

## 策略 API

| 方法 | 端点 | 用途 |
| :--- | :--- | :--- |
| `GET` | `/api/v1/policies` | 列出策略 |
| `POST` | `/api/v1/policies` | 创建策略 |
| `GET` | `/api/v1/policies/{policy_id}` | 读取策略 |
| `PUT` | `/api/v1/policies/{policy_id}` | 创建或更新策略 |
| `DELETE` | `/api/v1/policies/{policy_id}` | 删除策略 |

策略负载示例：

```json
{
  "image": "ghcr.io/acme/open-terminal:python-ds",
  "cpu_limit": "4",
  "memory_limit": "16Gi",
  "storage": "20Gi",
  "storage_mode": "per-user",
  "env": {
    "OPEN_TERMINAL_ALLOWED_DOMAINS": "*.pypi.org,github.com",
    "OPEN_TERMINAL_SYSTEM_PROMPT": "你在 {{os}} 上工作，位于 {{home}}。"
  },
  "idle_timeout_minutes": 60
}
```

## 策略生命周期 API

| 方法 | 端点 | 用途 |
| :--- | :--- | :--- |
| `GET` | `/api/v1/policies/{policy_id}/lifecycle` | 读取策略生命周期配置 |
| `PUT` | `/api/v1/policies/{policy_id}/lifecycle` | 创建或更新策略生命周期配置 |

生命周期负载示例：

```json
{
  "reset": {
    "schedule": "@weekly",
    "timezone": "UTC"
  }
}
```

## 状态 API

| 方法 | 端点 | 用途 |
| :--- | :--- | :--- |
| `GET` | `/api/v1/status` | 编排器状态（用于管理 UI） |
| `GET` | `/api/v1/terminals` | 列出活跃终端/会话（用于管理 UI） |

## 刷新 API

| 方法 | 端点 | 用途 |
| :--- | :--- | :--- |
| `POST` | `/api/v1/terminals/refresh` | 停止匹配的终端，以便下次重新预配 |
| `POST` | `/api/v1/terminals/stop` | 停止一个用户的终端，以便下次访问时重新开始 |

刷新请求体：

```json
{
  "user_id": "optional-user-id",
  "policy_id": "optional-policy-id",
  "only_idle": true,
  "reset": false
}
```

`only_idle` 默认为 `true`。`reset` 默认为 `false`。

停止请求体：

```json
{
  "user_id": "...",
  "policy_id": "default"
}
```

`policy_id` 默认为 `default`。

## 故障排除

### 环境变量需要加引号吗？

不需要。完全按照容器应接收的方式输入值。仅当引号字符是预期值的一部分时才需要引号。

### 我可以将环境变量传递给编排器并让它转发吗？

使用策略 `env` 放置应出现在每用户 Open Terminal 容器中的值。编排器进程环境变量配置编排器本身。

### 为什么我的环境变量或镜像更改没有生效？

用户可能已经有一个正在运行的终端。保存策略，然后刷新匹配的终端或等待空闲清理。

### 为什么用户无法再在文件浏览器中浏览到 `/etc`？

对于编排的终端，文件浏览器有意从 Open Terminal 报告的根目录内部开始，并隐藏该根目录以上的父目录。默认情况下，该根目录是 `Home`。这可以防止令人困惑的支持案例。它不是安全边界。

要使用不同的可视根目录，将 `OPEN_TERMINAL_FILE_BROWSER_ROOT` 设置为显式路径，例如 `/workspace`。要退出，在策略 `env` 中设置 `OPEN_TERMINAL_FILE_BROWSER_ROOT=filesystem` 并刷新受影响的终端。
