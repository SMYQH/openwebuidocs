---
sidebar_position: 8
title: "Kagi"
---

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎贡献更多内容，可查看 contributing 教程。

:::

:::tip

若要查看所有与 Web Search 相关的环境变量（包括并发设置、结果数量等），请参阅 [环境配置文档](/reference/env-configuration#web-search)。

:::

:::tip 故障排查

如果你在 web search 上遇到问题，请查看 [Web Search 故障排查指南](/troubleshooting/web-search)，其中涵盖了代理配置、连接超时、内容为空等常见问题。

:::

## Kagi Search API

[Kagi](https://kagi.com) 是一个高级搜索引擎，它聚合了来自多个来源（包括自有索引）的结果，并按准确性和相关性重新排序。Kagi Search API 可让程序化访问这些结果。

### 前提条件

- 一个 [Kagi 账户](https://kagi.com)（任何套餐均可）
- **独立的 API 计费** —— API 访问与 Kagi 订阅是分开计费的。在 [kagi.com/api](https://kagi.com/api) 开通计费并生成 API key
- Search API 定价：**每 1,000 次请求 12 美元**（按量计费，每 30 天或累计达到 100 美元时开具发票）

### 设置步骤

1. 前往 [kagi.com/api](https://kagi.com/api) 开通 API 计费。
2. 前往 [kagi.com/api/keys](https://kagi.com/api/keys) 创建一个 API key，并复制它。
3. 打开 **Open WebUI 管理面板**，点击 **Settings**，再点击 **Web Search**。
4. 启用 **Web search**，并将 **Web Search Engine** 设为 `kagi`。
5. 将 API key 粘贴到 **Kagi Search API Key** 字段。
6. 点击 **Save**。

### Docker Compose 设置

将以下环境变量添加到你的 Open WebUI `docker-compose.yaml` 文件中：

```yaml
services:
  open-webui:
    environment:
      ENABLE_WEB_SEARCH: True
      WEB_SEARCH_ENGINE: "kagi"
      KAGI_SEARCH_API_KEY: "YOUR_API_KEY"
      WEB_SEARCH_RESULT_COUNT: 3
      WEB_SEARCH_CONCURRENT_REQUESTS: 1
```

### 账户设置继承

Kagi Search API 会继承你 Kagi 账户的设置，包括：

- **屏蔽或置顶的网站** —— 你的[个性化规则](https://help.kagi.com/kagi/getting-started/index.html) 同样会作用于 API 返回结果
- **摘要片段长度** —— 在 [Settings → Search](https://help.kagi.com/kagi/settings/search.html) 中配置

这意味着你可以像自定义 Kagi 网页界面那样，自定义通过 API 返回的搜索结果。

### Kagi MCP 服务器（备选方案）

如果你不想使用内置的 web search 集成，Kagi 还提供一个托管的 [MCP（Model Context Protocol）服务器](https://kagi.com/api/docs/openapi/section/mcp)，可以作为一个 MCP 工具接入到 Open WebUI。它让模型能够绕过 web search 流程，直接使用 Kagi 的搜索与提取能力。

**MCP 端点：** `https://mcp.kagi.com/mcp`

**认证方式：** 使用你的 Kagi API key 作为 Bearer token。

### 更多资源

- [Kagi API 文档](https://kagi.com/api/docs)
- [Kagi API 定价](https://kagi.com/api/pricing)
- [Kagi Search API 帮助](https://help.kagi.com/kagi/api/search.html)
- [Kagi MCP 服务器](https://kagi.com/api/docs/openapi/section/mcp)
