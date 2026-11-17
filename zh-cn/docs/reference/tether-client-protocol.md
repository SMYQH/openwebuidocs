---
title: "Tether 客户端协议"
---

# Tether 客户端协议 {#tether-client-protocol}

本参考文档介绍原生客户端登录以及 Tether 连接握手流程。关于安装桌面应用以及在聊天中使用你的电脑，请参阅 [Open WebUI Tether](/ecosystem/tether)。

每个已登录的应用都有一个独立的、可续期的会话。退出登录或删除该会话会吊销它。未使用的会话会在 [`SESSION_EXPIRES_IN`](/reference/env-configuration#session_expires_in)（默认 `90d`）之后过期。访问令牌有效期为 15 分钟；刷新会同时替换刷新令牌。

## 会话 API {#session-api}

这些端点面向原生客户端开发者。`requests`、`exchange` 和 `refresh` 无需登录；其他所有端点都需要已登录用户的 Bearer 令牌。创建、requests、exchange、refresh 和 authorize 的调用按 IP 地址限制为每分钟 30 次。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/api/v1/auths/sessions/requests` | 启动浏览器登录。发送应用 `name`、回环地址 `redirect_uri`（例如 `http://127.0.0.1:<port>/callback`，主机为 `127.0.0.1`，显式指定端口，不带查询参数或片段）、32 至 256 个 URL 安全字符组成的 `state`，以及 PKCE 的 `code_challenge`（S256，43 个字符）。该请求在 10 分钟内有效。返回 `session_id`，用于打开 `/auth/sessions/<id>`。 |
| `GET` | `/api/v1/auths/sessions/{id}/request` | 返回等待中请求的名称和过期时间。 |
| `POST` | `/api/v1/auths/sessions/{id}/authorize` | 以已登录用户的身份批准该请求，并返回回调地址以及一次性 `code`，后者在 60 秒内有效。`/auth/sessions/<id>` 页面会调用它。 |
| `POST` | `/api/v1/auths/sessions/exchange` | 用 `session_id`、`code`、`redirect_uri` 和 `code_verifier` 换取访问令牌和刷新令牌。 |
| `POST` | `/api/v1/auths/sessions/refresh` | 用刷新令牌换取新的令牌。可以附带可选的 `request_id`，以便在响应丢失时找回新令牌：使用相同的 `request_id` 重复调用会再次返回它们。 |
| `POST` | `/api/v1/auths/sessions` | 直接从已登录的请求创建会话。 |
| `GET` | `/api/v1/auths/sessions` | 列出你的会话。 |
| `DELETE` | `/api/v1/auths/sessions/{id}` | 吊销你的某个会话。 |

### 连接 {#connection}

客户端连接到 websocket `/api/v1/tether/connect`，并发送一条 `hello` 消息，其中包含 `version`（`1` 或 `2`）、某个会话的访问 `token`、`connection_id`、`name` 以及 `services` 列表。将 `notifications` 设为 `true` 表示该连接订阅通知。服务器返回 `ready` 作为应答。
