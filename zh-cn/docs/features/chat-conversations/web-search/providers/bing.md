---
sidebar_position: 2
title: "Bing"
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

:::warning

Bing Search API 的停用日期为 2025 年 8 月 11 日。不支持新部署。

:::

## Bing API {#bing-api}

### 设置 {#setup}

1. 前往 [AzurePortal](https://portal.azure.com/#create/Microsoft.BingSearch) 并创建一个新资源。创建完成后，你会被重定向到资源概览页。在那里选择 “manage keys”。![manage keys](https://github.com/user-attachments/assets/dd2a3c67-d6a7-4198-ba54-67a3c8acff6d)
2. 在密钥管理页面找到 Key1 或 Key2，并复制你想使用的密钥。
3. 打开 **Settings > Web Search**（管理员区域）。
4. 启用网页搜索，并将网页搜索引擎设为 bing
5. 在 **Bing Search V7 Subscription Key**（`BING_SEARCH_V7_SUBSCRIPTION_KEY`）中填写你在第 2 步从 [Azure Portal](https://portal.azure.com/#create/Microsoft.BingSearch) 仪表盘复制的密钥。**Bing Search V7 Endpoint**（`BING_SEARCH_V7_ENDPOINT`）默认为 `https://api.bing.microsoft.com/v7.0/search`，只有在使用自定义端点时才需修改。Open WebUI 不会检查密钥是否已设置，所以空密钥会在 Bing 侧而不是在 Open WebUI 内报错。
6. 点击 `Save`
