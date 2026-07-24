---
title: 网络搜索和浏览
sidebar_position: 8
---

# 网络搜索和浏览

网络搜索开箱即用：无需任何配置，AI 通过 DuckDuckGo 进行搜索。浏览（AI 可以导航和点击的真实浏览器）默认关闭，按实例启用。

## 网络搜索

在**设置 → 管理 → 网络**中配置：一个主开关，以及一个设置为 **auto** 或特定提供商的提供商。

| 提供商 | 需要 |
| --- | --- |
| DuckDuckGo | 无需任何配置；始终可用 |
| Exa、Perplexity、Tavily、Brave、Firecrawl | API 密钥 |
| SearXNG | 你的实例的基础 URL，无需密钥 |
| 聊天补全端点 | 密钥 + URL + 模型（任何支持搜索的聊天 API） |

在 **auto** 模式下，Computer 按此优先级使用第一个配置的提供商：Exa → Perplexity → Tavily → Brave → Firecrawl → SearXNG → DuckDuckGo。密钥放在 UI 或环境变量中（`EXA_API_KEY` 等；参见[环境变量](/ecosystem/computer/reference/environment-variables)）。

## 浏览

默认关闭；在同一**设置 → 管理 → 网络**页面中有一个主开关。三个提供商：

- **local**：驱动机器上已安装的浏览器（Chrome、Chromium、Brave 或 Edge），通过 Chrome DevTools 协议以无头模式运行。浏览器会自动发现和自动启动；CDP URL 默认为 `http://localhost:9222`。这不是 Playwright：无需下载浏览器，无需庞大依赖，只需要 `websockets` 包。
- **firecrawl**：Firecrawl 的云 API（需要密钥）。
- **browser_use**：Browser-Use 的云 API（需要密钥）。

启用浏览后，AI 可以导航页面、点击元素、填写表单和截图。浏览器会话默认在 **10 分钟**后超时空闲。

UI 中的浏览器标签有一个**标签源**设置：托管浏览器，或你个人的 Chrome 配置文件及其登录信息和扩展。

:::warning
登录了你的账户的浏览器可以以你的身份操作：发帖、购买、删除。除非任务确实需要你已登录的配置文件，否则让 AI 使用托管浏览器，并密切关注这些任务。
:::
