---
sidebar_position: 13
title: "SerpApi"
---

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎参与贡献，请参阅贡献指南。

:::

:::tip

若要查看所有与网页搜索相关的环境变量（包括并发设置、结果数量等），请参阅 [环境配置文档](/reference/env-configuration#web-search)。

:::

:::tip 故障排查

遇到网页搜索问题时，请参阅[网页搜索故障排查指南](/troubleshooting/web-search)，了解如何解决代理配置、连接超时和内容为空等常见问题。

:::

## SerpApi API {#serpapi-api}

[SerpApi](https://serpapi.com/) 提供快速、易用且功能完整的 API，用于抓取 Google 等搜索引擎的结果。现在或将来推出的 SERP 引擎，只要返回 `organic_results`，就可以使用。默认的网页搜索引擎是 `google`，也可以改用 `bing`、`baidu`、`google_news`、`google_scholar`、`google_patents` 等。

### 设置 {#setup}

1. 前往 [SerpApi](https://serpapi.com/) 并登录或创建账号
2. 进入 `Dashboard`（控制台），复制 API key
3. 拿到 `API key` 后，打开 `Open WebUI 管理面板`，点击 `Settings`，再进入 `Web Search`
4. 启用 `Web Search`，并将 `Web Search Engine` 设为 `serpapi`
5. 在 `SerpApi API Key` 中填写你在第 2 步从 [SerpApi](https://serpapi.com/) 控制台复制的 `API key`
6. [可选] 输入你要查询的 `SerpApi engine` 名称，例如 `google`、`bing`、`baidu`、`google_news`、`google_videos`、`google_scholar`、`google_patents`。默认值为 `google`。更多选项请参阅 [SerpApi 文档](https://serpapi.com/dashboard)
7. 点击 `Save`

![Open WebUI 管理面板](/images/tutorial_serpapi_search.png)

#### 注意 {#note}

要在聊天中搜索网页，请打开消息输入框中的 **+** 菜单，并开启**网页搜索**。搜索将使用 [SerpApi](https://serpapi.com/) 引擎。

![启用 Web search](/images/enable_web_search.png)
