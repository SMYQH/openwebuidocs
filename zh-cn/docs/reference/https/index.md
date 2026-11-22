---
sidebar_position: 6
title: "HTTPS 与反向代理"
---

# HTTPS 与反向代理 {#https--reverse-proxies}

**使用 TLS 加密、反向代理或托管隧道保护你的 Open WebUI 部署。**

HTTPS 对用户与 Open WebUI 之间的所有流量进行加密，保护聊天历史、凭据和上传的文件。它同时是语音通话等浏览器功能的**必要条件**，这些功能需要安全上下文才能访问麦克风。

:::warning 语音通话需要 HTTPS
现代浏览器会阻止非 HTTPS 源访问麦克风。除 `localhost` 外，**语音通话无法通过**纯 `http://` 使用。
:::

`{{CLIPBOARD}}` 和 `{{USER_LOCATION}}` 这两个[提示词变量](/features/workspace/prompts#system-variables)同样需要安全上下文。在 `localhost` 以外的任意地址上使用纯 `http://` 时，Open WebUI 会显示 `Failed to read clipboard contents` 或 `Location access not allowed`。此时 `{{CLIPBOARD}}` 会保持原样留在提示词中，`{{USER_LOCATION}}` 则变成 `LOCATION_UNKNOWN`。当浏览器的剪贴板 API 不可用时，复制按钮会切换到回退方案，因此在没有 HTTPS 的情况下复制仍然可用。

---

## 选择你的方式 {#choose-your-approach}

| 方式 | 适用场景 | TLS 管理 |
| :--- | :--- | :--- |
| [**Cloudflare Tunnel**](/reference/https/cloudflare-tunnel) | 无需开放端口的生产环境 | 自动（Cloudflare 边缘） |
| [**ngrok**](/reference/https/ngrok) | 开发和测试 | 自动（ngrok 边缘） |
| [**Tailscale**](/reference/https/tailscale) | 跨设备私有访问 | 自动（tailscale serve） |
| [**Nginx**](/reference/https/nginx) | 完全控制的自托管生产环境 | 手动或 Let's Encrypt |
| [**Caddy**](/reference/https/caddy) | 最简配置的自托管生产环境 | 自动（Let's Encrypt） |
| [**HAProxy**](/reference/https/haproxy) | 高可用/负载均衡 | 手动或 Let's Encrypt |
| [**Apache、Synology DSM、IIS**](/reference/https/apache) | 你已经在运行的 Web 服务器或 NAS | 手动 |
| **云负载均衡** | AWS ALB、GCP LB、Azure 应用网关 | 由云提供商管理 |

---

## 快速建议 {#quick-recommendations}

- **只想尽快启用 HTTPS？** 使用 [Cloudflare Tunnel](/reference/https/cloudflare-tunnel)（生产环境）或 [ngrok](/reference/https/ngrok)（开发环境）。无需管理证书，无需开放端口。
- **已经在运行反向代理？** 添加 [Caddy](/reference/https/caddy)（自动证书）或 [Nginx](/reference/https/nginx)（最大控制权）。
- **需要负载均衡？** 使用 [HAProxy](/reference/https/haproxy) 或你的云提供商的负载均衡器。

---

## 关键配置注意事项 {#key-configuration-notes}

无论选择哪种方式，请记住以下要点：

| 设置 | 重要性 |
| :--- | :--- |
| `WEBUI_URL` | 设置为你的公共 HTTPS URL。为空时，SSO 登录后返回 Open WebUI 的重定向会回退到请求自身的 URL，但通知和 webhook 事件中的链接会丢失主机名。它不会设置发送给身份提供方的 SSO 回调 URL——它由请求构建，除非设置了 `OPENID_REDIRECT_URI` 或提供商自己的重定向 URI 变量。它属于[持久化配置](/reference/env-configuration#important-note-on-configvar-environment-variables)：首次启动之后，请在管理员设置 > 通用中修改 |
| `CORS_ALLOW_ORIGIN` | 默认为 `*`，因此不设置它永远不会破坏 WebSocket。如果设置，它必须包含你精确的公共源（协议、主机、端口），否则 Socket.IO 连接（以及任何跨源浏览器请求）都会失败 |
| 代理缓冲**关闭** | 让 API 客户端的流式响应持续流动。Web 界面通过 `/ws/socket.io` 流式发送聊天 token，因此只要 WebSocket 正常，缓冲就不会影响它 |
| WebSocket 支持 | 带 `Upgrade` 和 `Connection` 头部代理 `/ws/socket.io`。默认浏览器只使用 WebSocket 传输，没有 polling 回退；在无法升级的代理后面，请设置 `ENABLE_WEBSOCKET_SUPPORT=false`，让服务端和客户端都改用 long-polling |
| 转发头部 | 传递原始 `Host` 头部，并转发 `X-Forwarded-For` 和 `X-Forwarded-Proto`。审计日志中的客户端 IP 来自 `X-Forwarded-For`；发送给身份提供方的 SSO 回调 URL（未设置重定向 URI 时）由 `Host` 和 `X-Forwarded-Proto` 构建。除非 `FORWARDED_ALLOW_IPS` 指明代理地址，否则 Open WebUI 信任来自任何对端的 `X-Forwarded-*` 头部。`X-Real-IP` 不会被读取 |
| 安全 Cookie | `token` 和 `owui-session` cookie 以及 OAuth 会话 cookie 默认不带 `Secure` 发送。一旦前面有 TLS，请设置 `WEBUI_AUTH_COOKIE_SECURE=true` 和 `WEBUI_SESSION_COOKIE_SECURE=true` |
| 延长超时 | 从 `/api/chat/completions` 流式读取的 API 客户端，以及耗时的非流式请求（带处理的上传、网页抓取、转写）可能需要几分钟；请把代理读取超时至少设为 300 秒。Socket.IO 连接每 25 秒发送一次 ping，因此任何高于约 45 秒的空闲超时都能保持连接 |
| 上传大小 | 在设置 Max Upload Size（管理员设置 > 文档，或 `RAG_FILE_MAX_SIZE`）之前，应用没有上传上限，因此返回 413 的是代理的 body size 限制；请把它设为你在那里配置的值或更高。同样的限制也适用于聊天保存：保存编辑过的消息或评分会在一次请求中发送整个聊天，因此限制过低会在长聊天中丢失这些改动（[详情](/troubleshooting/connection-error#edits-and-ratings-lost-after-reload-in-long-chats)） |
| 健康检查 | 让负载均衡器指向 `/health`（存活检查）或 `/ready`（就绪检查：启动已完成、数据库和 Redis 可达） |
| 多实例 | Socket.IO 状态保存在进程内。在多个实例之间做负载均衡，或把 `UVICORN_WORKERS` 设为大于 1，需要 `WEBSOCKET_MANAGER=redis` 配合 `REDIS_URL`、共享数据库，并在每个实例上设置相同的 `WEBUI_SECRET_KEY` |
