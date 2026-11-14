---
sidebar_position: 2
title: "Bing"
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

:::warning

Bing Search APIs 将于 2025 年 8 月 11 日停用，不再支持新的部署。

:::

## Bing API {#bing-api}

### 设置 {#setup}

1. 前往 [AzurePortal](https://portal.azure.com/#create/Microsoft.BingSearch) 并创建一个新资源。创建完成后，你会被重定向到资源概览页。在那里选择 “manage keys”。![manage keys](https://github.com/user-attachments/assets/dd2a3c67-d6a7-4198-ba54-67a3c8acff6d)
2. 在密钥管理页面中，找到 Key1 或 Key2，并复制你想使用的 key
3. 打开 **Settings > Admin > Web Search**。
4. 启用网页搜索，并将网页搜索引擎设为 bing
5. 在 **Bing Search V7 Subscription Key**（`BING_SEARCH_V7_SUBSCRIPTION_KEY`）中填写你在第 2 步从 [Azure Portal](https://portal.azure.com/#create/Microsoft.BingSearch) 仪表盘复制的密钥。**Bing Search V7 Endpoint**（`BING_SEARCH_V7_ENDPOINT`）默认为 `https://api.bing.microsoft.com/v7.0/search`，只有在使用自定义端点时才需修改。Open WebUI 不会检查密钥是否已设置，所以空密钥会在 Bing 侧而不是在 Open WebUI 内报错。
6. 点击 `Save`
