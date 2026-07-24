---
sidebar_position: 6
title: "Firecrawl"
---

:::warning

本教程是社区贡献，不受 Open WebUI 团队支持。仅作为演示如何为特定用例自定义 Open WebUI。想要贡献？请查看[贡献教程](/contributing)。

:::

:::tip

有关网络搜索的所有环境变量（包括并发设置、结果数量等）的完整列表，请参阅[环境配置文档](/reference/env-configuration#web-search)。

:::

:::tip 故障排除

网络搜索遇到问题？请查看[网络搜索故障排除指南](/troubleshooting/web-search)以解决代理配置、连接超时和内容为空等常见问题。

:::

## 概述

[Firecrawl](https://firecrawl.dev) 是一个为 AI 应用构建的搜索和抓取 API。作为 Open WebUI 的网络搜索引擎，它运行你的查询，返回排序结果，并以干净、模型可用的形式拉回页面内容。你可以使用托管服务 `api.firecrawl.dev`，或者由于 Firecrawl 是开源的，将 Open WebUI 指向自托管的 Firecrawl 实例，这样每个查询都保持在内部。

## 前提条件

- **已安装 Open WebUI**：正在运行的 Open WebUI 实例（本地或 Docker）。
- **Firecrawl API 密钥**：来自 [firecrawl.dev](https://firecrawl.dev) 的托管服务，或来自你自己的自托管 Firecrawl 部署。
- **管理员权限**：对 Open WebUI 实例的管理员访问权限。

## 配置步骤

1. 获取 API 密钥：
   - **托管版**：在 [firecrawl.dev](https://firecrawl.dev) 注册并从仪表板复制密钥。
   - **自托管版**：使用你自己 Firecrawl 实例的密钥。
2. 在 Open WebUI 中，打开 **管理面板 > 设置 > 网络搜索**。
3. 开启**启用网络搜索**开关。
4. 从**网络搜索引擎**下拉菜单中选择 **Firecrawl**（引擎值为 `firecrawl`）。
5. 将你的密钥粘贴到 **Firecrawl API 密钥**字段。
6. （仅自托管）将 **Firecrawl API 基础 URL** 设置为你的实例，例如 `https://firecrawl.example.com`。默认为 `https://api.firecrawl.dev`。
7. 保存。

然后开始一个聊天，在提示词字段中用 **+** 按钮启用网络搜索，运行一个查询以确认 Firecrawl 返回结果。

## 环境变量

你可以使用环境变量来配置 Firecrawl，作为管理面板的补充或替代：

| 变量 | 默认值 | 用途 |
| :--- | :--- | :--- |
| `WEB_SEARCH_ENGINE` | （空） | 设置为 `firecrawl` 以选择此引擎。 |
| `ENABLE_WEB_SEARCH` | `false` | 设置为 `true` 以开启网络搜索。 |
| `FIRECRAWL_API_KEY` | （空） | 你的 Firecrawl API 密钥。 |
| `FIRECRAWL_API_BASE_URL` | `https://api.firecrawl.dev` | API 端点。指向自托管实例以保持查询在内部进行。 |
| `FIRECRAWL_TIMEOUT` | （Firecrawl 默认值） | 请求超时时间（毫秒）。 |

有关网络搜索变量的完整列表，请参阅[环境配置参考](/reference/env-configuration#web-search)。

## 故障排除

- **无效的 API 密钥**：确认密钥复制时没有多余空格，并且与端点匹配（托管密钥用于 `api.firecrawl.dev`，实例密钥用于自托管）。
- **无结果**：确保网络搜索开关（`+`）已开启，并且实例可以访问 Firecrawl 端点。
- **超时**：对于慢页面或大量抓取查询，提高 `FIRECRAWL_TIMEOUT`。
- **自托管连接错误**：验证从 Open WebUI 容器或主机能否访问 `FIRECRAWL_API_BASE_URL`。

## 更多资源

- [Firecrawl 文档](https://docs.firecrawl.dev)
- [Open WebUI 网络搜索环境变量](/reference/env-configuration#web-search)
