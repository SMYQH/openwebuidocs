---
sidebar_position: 6
title: "HTTPS 与反向代理"
---

# HTTPS 与反向代理 {#https--reverse-proxies}

**使用 TLS 加密、反向代理或托管隔道保护你的 Open WebUI 部署。**

HTTPS 对用户与 Open WebUI 之间的所有流量进行加密，保护聊天历史、凭据和上传的文件。它同时是语音通话等浏览器功能的**必要条件**，这些功能需要安全上下文才能访问麦克风。

:::warning 语音通话需要 HTTPS
现代浏览器在非 HTTPS 源上阻止麦克风访问。除非你在 `localhost` 上，否则**语音通话无法工作**，无法通过纯 `http://` 使用。
:::

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
| `WEBUI_URL` | 设置为你的公共 HTTPS URL，使 OAuth 回调和内部链接能正确解析 |
| `CORS_ALLOW_ORIGIN` | 必须与你的公共 URL 匹配，否则 WebSocket 连接将静默失败 |
| 代理缓冲**关闭** | SSE 流式传输的必要条件。开启缓冲会导致聊天响应中 Markdown 渲染异常 |
| WebSocket 支持 | 确保你的代理传递 `Upgrade` 和 `Connection` 头部以支持实时功能 |
| 延长超时 | LLM 响应可能需要几分钟。将代理读取超时至少设为 300 秒 |
