---
title: "给 Open WebUI 真正的双手"
sidebar_position: 13
---

# 给 Open WebUI 真正的双手

Open WebUI 是你已经聊天的地方：你的模型、你的提示词、你的历史。但当你问它"我们的限流器实际上做什么？"时，一个普通模型只能猜测。连接 Computer 的网关后，同一个 Open WebUI 聊天可以读取真实仓库、运行真实测试，并从代码中回答，因为工作区本身就成为了选择器中的一个模型。

**你需要：** 两个应用都在运行，Open WebUI 可以访问 Computer 的端口，在 Computer 中有一个已配置[模型或代理](/ecosystem/computer/ai/)的工作区，以及一个网关密钥。

## 操作步骤

1. **铸造密钥。** 在 Computer 中，前往**设置 → 管理 → 网关**并创建一个 API 密钥。立即复制；它只显示一次并以哈希形式存储。

2. **在 Open WebUI 中添加连接。** 管理设置 → 连接 → 添加 OpenAI API 连接：

   - **基础 URL：** `http://<computer-host>:8000/v1`
   - **API 密钥：** `sk-cptr-...` 密钥

3. **添加连续性标头。** 将 Computer 网关设置中的自定义标头块复制到 Open WebUI 连接中。它们携带聊天标识（`X-OpenWebUI-Chat-Id` 等），这使得后续轮次继续同一个 Computer 对话，并保持编辑和重新生成作为适当的分支。

4. **选择工作区作为模型。** 你的工作区现在在 Open WebUI 的模型选择器中显示为 `cptr/<folder-name>`。选择一个开始聊天并问一个基于实际项目的问题：

   > 读取限流器实现并解释当 Redis 宕机时会发生什么。不要更改任何内容。

5. **观察两边。** 答案流式传入 Open WebUI，工具活动内联总结。在 Computer 中，同一个对话出现在该工作区的侧边栏中，包含逐文件的详细内容，你可以从任一应用继续。

## 为什么这样有效

Open WebUI 保持你的大门；Computer 提供机器。无需复制或同步：没有克隆的仓库、没有上传的上下文、没有知识库导入。两个诚实的提醒。网关任务以**完全工具审批**运行（OpenAI 兼容的 API 没有办法暂停等待允许按钮），所以连接受信任的客户端到精心选择的工作区。而且 Open WebUI 自己的知识库、工具和提示词不会一起过来；如果工作区任务需要某个能力，在 Computer 中配置它。

**深入了解：** [Open WebUI 设置详情](/ecosystem/computer/automate/open-webui) · [网关 API 参考](/ecosystem/computer/reference/gateway-api) · [何时使用哪个工具？](/ecosystem/computer/choose)
