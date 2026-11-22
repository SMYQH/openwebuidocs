---
sidebar_position: 15
title: "Serply"
description: "将 Serply 网页搜索接入 Open WebUI，配置其 API 密钥，并验证对话能否获取搜索结果。"
---

使用 Serply 为 Open WebUI 对话获取网页搜索结果。Open WebUI 会使用你账号的 API 密钥，把搜索查询发送到 Serply 的托管 API。

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎参与贡献，请参阅[贡献指南](/contributing)。

:::

## 前置要求 {#requirements}

- 一个正在运行的 Open WebUI 实例，以及一个管理员账号。
- Open WebUI 服务器能够对外访问搜索提供商；如果需要整页抓取，还需要能够访问搜索返回的站点。
- 一个能可靠地进行原生工具调用且已启用网页搜索能力的对话模型。

创建 Serply 账号，并按照 [官方快速入门](https://serply.io/docs/guides/quickstart) 从 **Dashboard → Settings → API Key** 复制 API 密钥。你的账号必须具备可用的搜索额度。

## 在 Open WebUI 中配置 {#configure-in-open-webui}

1. 打开 **Settings → Web Search**（管理员区域），启用网页搜索。
2. 将 **Web Search Engine** 设为 `serply`。
3. 将密钥粘贴到 **Serply API Key**，并保存设置。
4. 启用该模型的**网页搜索**能力及其**网页搜索**默认功能，或为当前对话开启网页搜索。模型设置请参考 [原生搜索配置](/features/chat-conversations/web-search/agentic-search#how-to-enable-agentic-behavior)。

## 环境变量示例 {#environment-example}

对于通过环境变量配置的部署：

```bash
ENABLE_WEB_SEARCH=true
WEB_SEARCH_ENGINE=serply
SERPLY_API_KEY=your-api-key
```

修改环境变量后需要重启 Open WebUI。此前保存的管理员设置可能优先于这些启动值；如果所选引擎或密钥没有变化，请在管理面板中重新设置。关于持久化行为及更多选项，请参阅 [网页搜索配置参考](/reference/env-configuration#web-search)。

## 验证 {#verify}

用配置好的模型开始一段新对话。如果**网页搜索**尚未开启，请在聊天的 **+** 菜单中开启它。提问：“搜索 Python 官方文档，并给我一个链接。”

确认对话中出现了网页搜索工具调用，然后打开它并检查输出中的链接。在 Native 模式下，搜索结果不会列为来源。没有搜索工具调用、只有看似合理的回答，并不能说明该提供商已经接入成功。

## 故障排查 {#troubleshooting}

- **认证或配额错误：** 检查保存的 API 密钥是否正确，以及提供商账号是否有可用的搜索额度。
- **认证失败：** 再次从 Serply 控制台复制密钥。在 Open WebUI 中只填写密钥本身，不要带上 Serply 直连 API 示例中出现的 `X-Api-Key:` 请求头名称。
- **没有搜索工具调用：** 使用 [原生搜索配置](/features/chat-conversations/web-search/agentic-search#how-to-enable-agentic-behavior) 检查模型的网页搜索能力、聊天中的开关或默认功能，以及原生函数调用设置。
- **搜索成功但页面内容为空：** 参阅[网页搜索故障排查指南](/troubleshooting/web-search)，检查对外连通性、代理设置和网页加载器错误。搜索结果与整页抓取是两个独立的步骤。
