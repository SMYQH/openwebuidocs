---
title: 在 Open WebUI 中使用工作区
sidebar_position: 5
---

# 在 Open WebUI 中使用工作区

Computer 的网关将每个工作区暴露为一个 OpenAI 兼容的模型，因此你可以在 Open WebUI 的模型选择器中选择 `cptr/<workspace>`，并从你已经在使用的 Open WebUI 界面与真实的机器（文件、终端、git、工具）聊天。

## 连接

1. 在 Computer 中，打开**设置 → 管理 → 网关**并创建一个网关 API 密钥。立即复制它；它只显示一次并以哈希形式存储。
2. 在 Open WebUI 中，前往**管理设置 → 连接**添加一个 **OpenAI API** 连接：
   - 基础 URL：`http(s)://<computer-host>/v1`
   - API 密钥：第一步中的 `sk-cptr-...` 密钥
3. 向连接添加这些自定义标头，以便 Computer 可以跟踪聊天血统并过滤 Open WebUI 的实用请求：

   ```json
   {
     "X-OpenWebUI-Chat-Id": "{{CHAT_ID}}",
     "X-OpenWebUI-Message-Id": "{{MESSAGE_ID}}",
     "X-OpenWebUI-User-Message-Id": "{{USER_MESSAGE_ID}}",
     "X-OpenWebUI-User-Message-Parent-Id": "{{USER_MESSAGE_PARENT_ID}}",
     "X-OpenWebUI-Task": "{{TASK}}"
   }
   ```

   `{{USER_MESSAGE_ID}}`、`{{USER_MESSAGE_PARENT_ID}}` 和 `{{TASK}}` 需要 Open WebUI 0.10.0 或更新版本。没有它们，基本聊天可以工作，但编辑/重新生成分支和后台任务过滤不会生效。
4. 保存。你的每个 Computer 工作区现在在 Open WebUI 的模型选择器中显示为 `cptr/<workspace-name>`。选择一个并聊天。

实际运行的是哪个底层模型在 Computer 中决定，按优先级排序：设置 → 网关模型、`<workspace>/.cptr/model` 覆盖文件、默认聊天模型，然后是第一个启用连接的第一个模型。

:::warning 网关请求是无人值守的
网关任务运行完整的代理循环（文件编辑、shell 命令、网络、工具），具有完全工具审批。Open WebUI 无法暂停等待逐操作确认。将其用于你愿意让代理操作的工作区，并保持密钥私有。
:::

## 这些标头带来的好处

- **对话连续性**：后续消息落在同一个 Computer 聊天中，而不是创建一个新的。
- **分支镜像**：Open WebUI 中的编辑和重新生成显示为 Computer 中相应聊天的分支。
- **实用任务过滤**：Open WebUI 的标题、标签和后续建议生成请求由普通 LLM 回答，而不是在工作区中启动代理任务。

每个网关对话都是 Computer 侧边栏中的真实聊天，因此你可以打开 Computer 并精确查看代理做了什么。

## 不会转移的内容

网关是一个模型端点，而不是同步。Open WebUI 的知识库、工具、提示词、系统提示和用户不会转发到 Computer；如果工作区需要，在 Computer 中配置等效的能力。

## 如果它不工作

使用相同的 bearer 密钥调用 `GET /v1/models` 以区分连接/认证问题和模型选择。检查基础 URL 以 `/v1` 结尾，密钥属于正确的 Computer 用户，并且工作区存在。如果聊天可以工作但分支不行，重新复制标头并检查你的 Open WebUI 版本。

有关原始端点详情（`/v1/models`、`/v1/chat/completions`、流式传输、标头参考），参见[网关 API 参考](/ecosystem/computer/reference/gateway-api)。
