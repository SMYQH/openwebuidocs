---
title: 网关 API（OpenAI 兼容）
sidebar_position: 5
---

# 网关 API（OpenAI 兼容）

网关将你的每个工作区暴露为 OpenAI 兼容的模型，因此任何 OpenAI 风格的客户端都可以在真实工作区中运行代理任务。

| 端点 | 行为 |
| --- | --- |
| `GET /v1/models` | 列出密钥拥有者的工作区作为模型。 |
| `POST /v1/chat/completions` | 在所选工作区中运行代理任务。默认使用 SSE 流式传输。 |

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-cptr-..." \
  -H "Content-Type: application/json" \
  -d '{"model": "cptr/my-project", "messages": [{"role": "user", "content": "总结 README"}]}'
```

要连接 Open WebUI？请按照[从 Open WebUI 使用 Computer](/ecosystem/computer/automate/open-webui) 中的步骤操作；此页面是端点参考。

## API 密钥

在**设置 → 管理 → 网关**中创建密钥。`sk-cptr-...` 值只显示一次并以哈希形式存储，所以立即复制。密钥管理本身（创建、撤销）需要浏览器会话；你不能使用 bearer 密钥管理密钥。

## 工作区作为模型

密钥用户拥有的每个工作区显示为 `cptr/<folder-name>`；重复的文件夹名称会获得 `-2` 后缀。执行任务的实际底层模型按优先级顺序：

1. **设置 → 管理 → 网关**中设置的模型
2. `<workspace>/.cptr/model` 覆盖文件
3. 默认聊天模型
4. 第一个启用连接的第一个模型

## 对话连续性

无状态请求每次都会创建一个新的 Computer 聊天。要延续对话，发送 `X-Chat-Id`（任何客户端）或 Open WebUI 标头集：

```json
{
  "X-OpenWebUI-Chat-Id": "{{CHAT_ID}}",
  "X-OpenWebUI-Message-Id": "{{MESSAGE_ID}}",
  "X-OpenWebUI-User-Message-Id": "{{USER_MESSAGE_ID}}",
  "X-OpenWebUI-User-Message-Parent-Id": "{{USER_MESSAGE_PARENT_ID}}",
  "X-OpenWebUI-Task": "{{TASK}}"
}
```

`{{USER_MESSAGE_ID}}`、`{{USER_MESSAGE_PARENT_ID}}` 和 `{{TASK}}` 需要 Open WebUI 0.10.0 或更新版本。没有它们，基本聊天可以工作，但编辑/重新生成分支和实用任务过滤不会生效。

Open WebUI 标记为标题、标签或后续生成（通过 `X-OpenWebUI-Task`）的请求由普通 LLM 回答，而不会在工作区中启动代理任务。

## 限制

:::warning 网关任务以完全工具审批运行
在 OpenAI 兼容的 API 中没有逐操作审批：代理无需询问即可编辑文件、运行命令和调用工具。将网关密钥视为 SSH 凭据，仅交给受信任的客户端。
:::

- `temperature`、`top_p` 和 `max_tokens` 会被接受但忽略；使用工作区配置的模型和设置。
- 响应中的 `usage` 令牌数始终为 0。
- 空闲 300 秒的流会被关闭。
