---
sidebar_position: 23
title: "Linkup"
---

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎贡献更多内容，可查看 [贡献教程](/contributing)。

:::

:::tip

若要查看所有与 Web Search 相关的环境变量（包括并发设置、结果数量等），请参阅 [环境配置文档](/reference/env-configuration#web-search)。

:::

:::tip 故障排查

如果你在 web search 上遇到问题，请查看 [Web Search 故障排查指南](/troubleshooting/web-search)，其中涵盖了代理配置、连接超时、内容为空等常见问题。

:::

## 概览

[Linkup](https://www.linkup.so/) 是一个为 AI 应用打造的搜索 API。将其集成到 Open WebUI 后，你的语言模型就可以执行实时网页搜索，并基于最新来源进行回答。本教程将指导你把 Linkup 配置为 web search 提供商。

Linkup 支持已在 Open WebUI v0.9.6 中加入。

## 前提条件

请确保你具备：

- **已安装 Open WebUI**：一个可运行的 Open WebUI 实例（本地或 Docker）。参阅 [入门指南](/getting-started)。
- **Linkup 账号**：以及来自 [Linkup](https://www.linkup.so/) 的 API key。
- **管理员权限**：对 Open WebUI 实例具备管理权限。
- **网络连接**：用于发起 Linkup API 请求。

## 分步配置

### 1. 获取 Linkup API Key

1. 在 [Linkup](https://www.linkup.so/) 注册或登录。
2. 打开控制台中的 API keys 页面。
3. 复制或生成一个新的 API key，并妥善保存。

### 2. 配置 Open WebUI

1. 使用管理员账号登录 Open WebUI。
2. 打开 **Admin Panel → Settings → Web Search**。
3. 将 **Web Search** 切换为 **On**。
4. 在 **Web Search Engine** 下拉框中选择 **linkup**。
5. 将你的 Linkup API key 粘贴到 **Linkup API Key** 字段。
6. （可选）按需设置 **Search Depth** 与 **Output Type**（见下文）。
7. 保存设置。

### 3. 测试集成

1. 在 Open WebUI 中开启一段聊天。
2. 点击提示词输入框中的 **加号（+）** 按钮以启用 web search。
3. 输入一个查询（例如 `+latest AI news`），确认 Linkup 能返回实时结果。

## 搜索参数

Linkup 请求由一组可以覆盖的默认值构建而成。查询参数（`q`）和结果数量（`maxResults`）会自动注入，无法被覆盖。

| 参数 | 默认值 | 说明 |
|-----------|---------|-------|
| `depth` | `standard` | `standard` 更快、更便宜；`deep` 会执行更深入的多步搜索。 |
| `outputType` | `sourcedAnswer` | `sourcedAnswer` 返回一个答案及其来源页面；`searchResults` 返回原始结果条目。 |
| `url` | `https://api.linkup.so/v1/search` | 仅在需要指向其他端点时覆盖。 |

这些参数对应 [`LINKUP_SEARCH_PARAMS`](/reference/env-configuration#linkup_search_params) 环境变量，以 JSON 对象形式提供。例如：

```bash
-e LINKUP_API_KEY="your_linkup_api_key"
-e LINKUP_SEARCH_PARAMS='{"depth": "deep", "outputType": "searchResults"}'
```

当选中 `linkup` 引擎时，同样的字段也会出现在管理界面中，因此除非你倾向于通过环境变量管理配置，否则无需设置环境变量。详情与 [`ENABLE_PERSISTENT_CONFIG`](/reference/env-configuration#enable_persistent_config) 的行为，请参阅 [环境变量配置](/reference/env-configuration)。

## 故障排查

- **API Key 无效**：确认复制的 key 没有多余空格。
- **无搜索结果**：确认已启用 web search 开关（`+`）并且网络正常。对于内容稀疏的主题，可尝试 `depth: deep`。
- **额度耗尽**：在 Linkup 控制台查看套餐与用量。
- **设置未保存**：确认拥有管理员权限，并且 `webui.db` 可写。

## 额外资源

- [Linkup 文档](https://docs.linkup.so/)：API 参考与高级选项。
- [Open WebUI 功能](/features)：RAG 与 web search 说明。
- [为 Open WebUI 贡献](/contributing)：提交改进或反馈问题。
