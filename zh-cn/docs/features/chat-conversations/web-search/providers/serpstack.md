---
sidebar_position: 16
title: "Serpstack"
description: "在 Open WebUI 中配置 Serpstack 网页搜索，确认账号的 HTTPS 访问权限，并在聊天中验证结果。"
---

使用 Serpstack 为 Open WebUI 对话获取搜索引擎结果。Open WebUI 会使用你账号的访问密钥，将搜索查询发送到 Serpstack 的托管 API。

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎贡献更多内容，可查看 [contributing 教程](/contributing)。

:::

## 前置要求 {#requirements}

- 一个正在运行的 Open WebUI 实例，以及一个管理员账号。
- Open WebUI 服务器能够对外访问搜索提供商；如果需要整页抓取，还需要能够访问搜索返回的站点。
- 一个原生工具调用稳定、且已启用 Web Search 能力的对话模型。

创建 [Serpstack 账号](https://serpstack.com/signup/free)，并从账号控制台复制访问密钥。对照[当前套餐说明](https://serpstack.com/pricing)，确认账号的搜索额度和 HTTPS 访问权限。定价页面列出免费和付费套餐均支持 HTTPS 加密，[常见问题](https://serpstack.com/faq)却仍表示 HTTPS 支持取决于套餐。请确认你的账号能否使用该功能，不要假定所有免费账号都只能使用 HTTP。

## 在 Open WebUI 中配置 {#configure-in-open-webui}

1. 打开 **Settings → Web Search**（管理员区域），启用网页搜索。
2. 将 **Web Search Engine** 设为 `serpstack`。
3. 将密钥粘贴到 **Serpstack API Key**，并保存设置。
4. 启用该模型的 **Web Search** 能力及其 **Web Search** 默认特性，或在当前对话中打开 Web Search。模型设置请参考 [原生搜索配置](/features/chat-conversations/web-search/agentic-search#how-to-enable-agentic-behavior)。

如果账号支持 HTTPS，请保留默认值 **`SERPSTACK_HTTPS=true`**。如果 API 提示 HTTPS 不可用，请向 Serpstack 确认该账号的访问权限。`SERPSTACK_HTTPS=false` 会改用未加密的 HTTP，在传输途中暴露访问密钥和搜索查询。对于敏感查询，请使用支持 HTTPS 的账号。

## 环境变量示例 {#environment-example}

对于通过环境变量配置的部署：

```bash
ENABLE_WEB_SEARCH=true
WEB_SEARCH_ENGINE=serpstack
SERPSTACK_API_KEY=your-api-key
SERPSTACK_HTTPS=true
```

修改环境变量后需要重启 Open WebUI。此前保存的管理员设置可能优先于这些启动值；如果所选引擎或密钥没有变化，请在管理面板中重新设置。关于持久化行为及更多选项，请参阅 [网页搜索配置参考](/reference/env-configuration#web-search)。

## 验证 {#verify}

用配置好的模型开始一段新对话；如果 **Web Search** 尚未启用，请在聊天的 **+** 菜单中打开它。提问：“搜索 Python 官方文档，并给我一个链接。”

确认对话中出现了网页搜索工具调用和返回的来源，然后打开其中一个来源进行检查。没有搜索工具调用、只有看似合理的回答，并不能说明该提供商已经接入成功。

## 故障排查 {#troubleshooting}

- **认证或配额错误：** 检查保存的 API 密钥是否正确，以及提供商账号是否有可用的搜索额度。
- **HTTPS 访问错误：** 确认你的账号是否具备 HTTPS 权益。不要仅仅因为账号处于免费层级就改用 HTTP，详见上面的 HTTPS 说明。
- **没有搜索工具调用：** 使用 [原生搜索配置](/features/chat-conversations/web-search/agentic-search#how-to-enable-agentic-behavior) 检查模型的 Web Search 能力、聊天中的开关或默认特性，以及 Native function calling。
- **搜索成功但页面内容为空：** 参阅 [Web Search 故障排查](/troubleshooting/web-search)，检查对外连通性、代理设置和网页加载器错误。搜索结果与整页抓取是两个独立的步骤。
