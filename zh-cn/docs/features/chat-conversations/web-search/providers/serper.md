---
sidebar_position: 14
title: "Serper"
description: "使用 API 密钥将 Serper 网页搜索接入 Open WebUI，配置搜索引擎，并在聊天中验证搜索效果。"
---

使用 Serper 为 Open WebUI 对话获取 Google 搜索结果。Open WebUI 会把搜索查询发送到 Serper 的托管 API，因此服务器需要能够访问互联网，并需要一个 Serper API 密钥。

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎参与贡献，请参阅[贡献指南](/contributing)。

:::

## 前置要求 {#requirements}

- 一个正在运行的 Open WebUI 实例，以及一个管理员账号。
- Open WebUI 服务器能够对外访问搜索提供商；如果需要整页抓取，还需要能够访问搜索返回的站点。
- 一个能可靠地进行原生工具调用且已启用网页搜索能力的对话模型。

前往 [Serper](https://serper.dev/) 注册账号，并从其控制台复制 API 密钥。确认你的账号还有可用的搜索额度。

## 在 Open WebUI 中配置 {#configure-in-open-webui}

1. 打开 **Settings → Web Search**（管理员区域），启用网页搜索。
2. 将 **Web Search Engine** 设为 `serper`。
3. 将密钥粘贴到 **Serper API Key**，并保存设置。
4. 启用该模型的**网页搜索**能力及其**网页搜索**默认功能，或为当前对话开启网页搜索。模型设置请参考 [原生搜索配置](/features/chat-conversations/web-search/agentic-search#how-to-enable-agentic-behavior)。

## 环境变量示例 {#environment-example}

对于通过环境变量配置的部署：

```bash
ENABLE_WEB_SEARCH=true
WEB_SEARCH_ENGINE=serper
SERPER_API_KEY=your-api-key
```

修改环境变量后需要重启 Open WebUI。此前保存的管理员设置可能优先于这些启动值；如果所选引擎或密钥没有变化，请在管理面板中重新设置。关于持久化行为及更多选项，请参阅 [网页搜索配置参考](/reference/env-configuration#web-search)。

## 验证 {#verify}

用配置好的模型开始一段新对话。如果**网页搜索**尚未开启，请在聊天的 **+** 菜单中开启它。提问：“搜索 Python 官方文档，并给我一个链接。”

确认对话中出现了网页搜索工具调用，然后打开它并检查输出中的链接。在 Native 模式下，搜索结果不会列为来源。没有搜索工具调用、只有看似合理的回答，并不能说明该提供商已经接入成功。

## 故障排查 {#troubleshooting}

- **认证或配额错误：** 检查保存的 API 密钥是否正确，以及提供商账号是否有可用的搜索额度。
- **没有结果或出现配额错误：** 在 Serper 控制台查看剩余的搜索额度，以及账号是否受到限制。
- **没有搜索工具调用：** 使用 [原生搜索配置](/features/chat-conversations/web-search/agentic-search#how-to-enable-agentic-behavior) 检查模型的网页搜索能力、聊天中的开关或默认功能，以及原生函数调用设置。
- **搜索成功但页面内容为空：** 参阅[网页搜索故障排查指南](/troubleshooting/web-search)，检查对外连通性、代理设置和网页加载器错误。搜索结果与整页抓取是两个独立的步骤。
