---
sidebar_position: 400
title: "API 接口"
---

本指南提供了有效使用 API 接口所需的关键信息，帮助你实现与模型的无缝集成和自动化。请注意，该配置目前处于实验阶段，未来可能会有更新和改进。

:::note 接口不再被文档化
API 变化频繁，为它编写文档意义不大。要查找最新的接口和规范，可以让 AI Agent 指向 Open WebUI 后端并让它自行读取。下面的接口仅供参考。
:::

## 认证 {#authentication}

为确保 API 的安全访问，需要进行身份认证 🛡️。你可以使用 Bearer Token 机制对 API 请求进行认证。在 Open WebUI 的**设置 > 账户**中获取你的 API Key，或者使用 JWT（JSON Web Token）进行认证。有关启用和生成 API Key 的完整说明（包括管理员开关和非管理员用户所需的群组权限），请参阅 [API 密钥](/features/authentication-access/api-keys)。

:::tip 用于代理密集环境的备用凭证头
当 Open WebUI 位于已使用 `Authorization` 头进行自身认证的反向代理之后时，你可以通过自定义头（默认为 `x-api-key`）传递 API 密钥。管理员可以通过 [`CUSTOM_API_KEY_HEADER`](/reference/env-configuration#custom_api_key_header) 环境变量重命名该头以避免冲突。详见[在反向代理后使用 `Authorization`？](/features/authentication-access/api-keys#behind-a-reverse-proxy-that-consumes-authorization) 的完整模式。
:::

## Swagger 文档链接 {#swagger-documentation-links}

:::important

请确保将 `ENV` 环境变量设置为 `dev`，以访问这些服务的 Swagger 文档。没有此配置，文档将不可用。

:::

访问 Open WebUI 提供的各服务的详细 API 文档：

| 应用 | 文档路径 |
|-------------|-------------------------|
| 主应用 | `/docs` |

## 主要 API 端点 {#notable-api-endpoints}

### 📜 获取所有模型 {#retrieve-all-models}

- **端点**：`GET /api/models`
- **说明**：获取通过 Open WebUI 创建或添加的所有模型。
- **示例**：

  ```bash
  curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:3000/api/models
  ```

### 程序化模型管理（导出 / 导入 / 同步） {#programmatic-model-management-export--import--sync}

自定义模型本质上是纯 JSON，因此你可以以声明式方式（在 Git 中、通过脚本或从 AI Agent）管理它们，而无需 UI。这些端点位于 `/api/v1/models` 下：

| 端点 | 说明 |
| :--- | :--- |
| `GET /api/v1/models/all` | **（管理员）** 在一个不分页的列表中返回每一条已保存的模型记录，包括当前没有任何连接提供的模型。管理页面的模型列表即由此支撑。 |
| `GET /api/v1/models/export` | 将**所有**自定义模型导出为 JSON 数组，或仅导出你用重复的 `ids` 查询参数指定的模型（`?ids=a&ids=b`）。请求一个你没有写入权限的模型会返回 `403`，而不是被悄悄略过。 |
| `POST /api/v1/models/import` | 批量**新增或更新**：创建新模型并更新现有模型（按 `id` 匹配），不会删除任何模型。 |
| `POST /api/v1/models/sync` | **（管理员）** 声明式**同步**：按请求中的列表创建或更新模型，并**删除**未列出的模型，使实例与列表完全一致。 |
| `POST /api/v1/models/create` | 创建单个模型。 |
| `POST /api/v1/models/model/update` | 更新单个模型。 |
| `POST /api/v1/models/model/delete` | 删除单个模型。 |

**认证：** 需要管理员 [API Key](/features/authentication-access/api-keys)（或对于 `import`，具有 `workspace.models_import` 权限的用户）。`sync` 仅限管理员。`import` 和 `sync` 都接受形如 `{"models": [ ... ]}` 的请求体，其中数组正是 `export` 返回的内容。

**背景图片以数据形式随行。** 模型的背景会以文件形式存储在实例上，因此 `export` 会读取该文件并以 `background_image_data`（一个 `data:image/...;base64,...` URI）的形式放入记录中，同时将 `meta.background_image_url` 设为 `null`。`import` 则反向处理：解码该 data URI，在目标实例上重新上传为文件，并把新的文件 URL 写回 `meta`。这使导出的模型可以在实例之间移植。编写脚本时有两个值得注意的结果：导出一个背景文件已丢失的模型会使整个请求以 `400` 失败；超出限制（5 MiB、2500 万像素、PNG/JPEG/WebP/GIF）的图片会在导入时被拒绝。

**语音头像以引用的形式随行。** [语音头像](/features/chat-conversations/chat-features/voice-mode#voice-avatars) 及其动画始终以文件形式保存在源实例上，导出时只会带上它们的文件 ID。导入或同步一个头像或动画文件在目标实例上缺失或不可访问的模型时，请求会失败并返回 `403`（`Avatar or animation file is not accessible. Upload it again.`）。请先在目标实例上上传头像。

**版本控制、代码驱动的工作流：**

```bash
# 1. Snapshot your live models into a file you can commit to git
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/v1/models/export > models.json

# 2. Edit or generate models.json with your scripts or an agent, commit it, then
#    reconcile the instance to match the file exactly (creates, updates, prunes)
curl -X POST -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"models\": $(cat models.json)}" \
  http://localhost:3000/api/v1/models/sync
```

这样就得到了可重现、受版本控制的模型定义。使用 `/import` 替代 `/sync` 进行更新，可创建或更新模型，且不会删除现有模型。在部署、CI 或容器启动时运行同步步骤，以自动加载你的模型。

### 聊天补全 {#chat-completions}

- **端点**：`POST /api/chat/completions`
- **说明**：作为兼容 OpenAI API 的聊天补全端点，为 Open WebUI 上的模型提供服务，包括 Ollama 模型、OpenAI 模型以及 Open WebUI Function 模型。位于 Responses API 连接上的模型同样会以 Chat Completions 格式作答（无论是否流式）；当回复被截断时，`finish_reason` 会被设为 `length` 或 `content_filter`。

:::warning 读取使用了工具的回复中的 `usage`

一次回复可能涉及多次模型调用，每一轮工具使用对应一次。`input_tokens`、`output_tokens`、`total_tokens` 和 `cost` 会累加所有调用。`prompt_tokens` 和 `completion_tokens` 只包含最近一次调用，这正是上下文压缩所读取的值。

:::

**请求中的参数会被保留。** 工作区模型自带自己的高级参数，管理员也可以在**设置 > 模型**（管理员区域）的**模型默认值**下设置实例级的参数。两者都只会补全你的请求中未指定的部分，因此 `temperature`、`max_tokens`、`top_p`、`seed`、`stop`、`reasoning_effort`、`response_format`、`logit_bias` 以及 Ollama 模型的 `options` 对象都会保留你传入的值。对于 Ollama 模型，`max_tokens` 会以 `num_predict` 的形式传给 Ollama。某个参数未传入时，仍按之前的做法使用模型已保存的值。唯一的例外是**流式聊天响应**，无论请求中的 `stream` 值是什么，该模型设置仍会决定回复是否流式返回。下文的 [Anthropic 消息 API](#anthropic-messages-api) 也经由该端点运行，因此在那里同样成立，SDK 的 `max_tokens` 会完整地传到提供方。

**模型控制项。** 带有[模型控制项](/features/workspace/models#model-controls)的模型，也会把每个控制项的默认选项应用到 API 请求上，这些参数同样只补全请求中未指定的部分。若要选择其他选项，请在 `params.model_controls` 下按模型 ID 发送控制项 ID 和选项 ID。`GET /api/models` 会在 `info.params.model_controls` 下列出模型的各个控制项，其中包含每个控制项的 ID、标签、默认值，以及其各选项的 ID 和标签：

```json
{
  "model": "gpt-5",
  "messages": [{ "role": "user", "content": "Plan a three-day trip to Lisbon." }],
  "params": { "model_controls": { "gpt-5": { "thinking": "high" } } }
}
```

任何有权访问该模型的调用者都可以选择选项，无论其**允许聊天控制项**和**允许聊天参数**[权限](/features/authentication-access/rbac/permissions#3-chat-permissions)如何设置。为模型已不再拥有的控制项所做的选择会被忽略，而为控制项已不再拥有的选项进行选择会返回 `400`。

**如何获取 `usage` 块。** 除非显式要求，大多数兼容 OpenAI 的提供方不会在流式回复中包含用量信息。当模型启用了**用量**能力时，Open WebUI 会自行添加 `stream_options: {"include_usage": true}`，因此你无需自己发送。非流式请求保持不变；你发送的 `stream_options` 会保留其余键，但其中的 `include_usage` 会被强制设为 `true`，因此在该能力启用期间无法按请求关闭用量统计。

**提供方错误。** 当模型提供方拒绝请求时，该端点会返回提供方自己的状态码和错误，例如触发其速率限制时返回 `429`，并透传其 `Retry-After` 和 `retry-after-ms` 头，以便你的客户端进行退避。OpenAI、Ollama 和 Anthropic 代理路由同样会转发这些重试头。

#### 通过 API 使用 Open WebUI 工具（包括 MCP） {#using-open-webui-tools-including-mcp-from-the-api}

`/api/chat/completions` 端点可以在请求体中传入 Open WebUI 工具 ID 时，服务端执行这些工具——包括已在 Open WebUI 中配置并启用的原生 Python 工具、OpenAPI 工具服务器和 MCP 工具服务器。

1. 先在 Open WebUI 中配置好工具服务器。MCP 相关内容参见 [Model Context Protocol (MCP)](/features/extensibility/mcp)。
2. 从工具列表端点获取工具 ID，或在聊天中启用该工具时通过浏览器网络请求获取。MCP 工具服务器的 ID 形如 `server:mcp:<server-id>`。
3. 调用 `/api/chat/completions` 时，在 `tool_ids` 中传入该 ID：

```bash
curl -X POST http://localhost:3000/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.6:27b",
    "messages": [
      {"role": "user", "content": "Use the configured MCP tool if it helps."}
    ],
    "tool_ids": ["server:mcp:YOUR_MCP_SERVER_ID"]
  }'
```

Open WebUI 会在解析工具之前检查调用者对每个所选工具服务器的访问权限。对于受 OAuth 保护的 MCP 服务器，与该 API 密钥关联的用户必须已经在 Web UI 中完成了 OAuth 授权流程；否则在 API 请求过程中工具连接可能失败。

如果你的外部客户端自行发送了 OpenAI 风格的 `tools` 数组，Open WebUI 会把调用方提供的这些工具定义转发给模型，而不是服务端解析 `tool_ids`。

要查看某个 MCP 连接提供了哪些工具，请用 `server:mcp:<server-id>` 形式的 ID 调用 `GET /api/v1/tools/id/{id}/specs`。它会连接到该服务器并返回 `{"specs": [{"name": ..., "description": ...}]}`。传入其他任何 ID，或者你无权访问的服务器，都会返回 `404`。尚未登录授权的 OAuth 服务器返回 `401`，15 秒内没有响应的服务器返回 `504`，其他任何失败都返回 `502`。

:::tip 想让模型真正在循环中运行这些工具，并同时使用内置工具吗？
你发送哪些字段，决定了 Open WebUI 是替你执行工具调用，还是把它们交回给你的客户端去执行，也决定了最终答案出现在 HTTP 响应体里还是聊天记录里。[服务器端工具调用（API）](/reference/server-side-tool-calling) 会完整讲解这两种方式下的每一次调用——流式与非流式、保存聊天与不保存聊天——最后给出一个可直接复用的脚本。
:::

- **Curl 示例**：

  ```bash
  curl -X POST http://localhost:3000/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "qwen3.6:27b",
        "messages": [
          {
            "role": "user",
            "content": "Why is the sky blue?"
          }
        ]
      }'
  ```

- **Python 示例**：

  ```python
  import requests

  def chat_with_model(token):
      url = 'http://localhost:3000/api/chat/completions'
      headers = {
          'Authorization': f'Bearer {token}',
          'Content-Type': 'application/json'
      }
      data = {
        "model": "granite3.1-dense:8b",
        "messages": [
          {
            "role": "user",
            "content": "Why is the sky blue?"
          }
        ]
      }
      response = requests.post(url, headers=headers, json=data)
      return response.json()
  ```

### 🔮 Anthropic 消息 API {#anthropic-messages-api}

Open WebUI 提供兼容 Anthropic 消息 API 的端点。这允许为 Anthropic API 构建的工具、SDK 和应用程序直接与 Open WebUI 配合工作——通过所有已配置的模型、过滤器和流水线路由请求。

在内部，该端点将 Anthropic 请求格式转换为 OpenAI 聊天补全格式，通过现有的聊天补全流水线路由，并将响应转换回 Anthropic 格式。支持流式和非流式请求。

:::info 原生 Anthropic 连接会跳过转换

当目标连接本身使用的就是 Anthropic 消息 API 时，请求会被原样转发，而不会先转换成 OpenAI 格式再转回来。直接转发保留了提供方专属字段，因此这些字段可以完整往返，无需 `passthrough_params`。

当连接的基础 URL 指向 Anthropic，或连接设置中 **高级** 选项下的**提供方**设为 **LiteLLM** 时，会适用这一规则，因为 LiteLLM 也提供兼容 Anthropic 的路由。请求会直接发给提供方，不会使用过滤器、工具或知识库。其他连接仍按上文所述转换请求。下拉框中的其余选项见[提供方设置](/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible#the-provider-setting)。

:::

- **端点**：`POST /api/message`，`POST /api/v1/messages`
- **认证**：支持 `Authorization: Bearer YOUR_API_KEY` 和 Anthropic 的 `x-api-key: YOUR_API_KEY` 头
- **扩展思考**：底层模型的推理输出会以 Anthropic `thinking` 内容块的形式返回，流式和非流式响应均如此。
- **推理强度**：`reasoning_effort` 以及 `output_config.effort` 会被映射到底层模型的推理强度设置。
- **结构化输出**：`output_config.format`（`json_schema` 或 `json_object`）会被映射到模型的响应格式设置。
- **传递额外参数**：标准转换之外的参数默认会被丢弃。在连接上设置**透传参数**（`passthrough_params`，一个以逗号分隔的参数名列表，或 `*` 表示所有非标准参数）即可将其原样转发给上游提供方。

- **Curl 示例**（非流式）：

  ```bash
  curl -X POST http://localhost:3000/api/v1/messages \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "gpt-5.6-sol",
        "max_tokens": 1024,
        "messages": [
          {
            "role": "user",
            "content": "Why is the sky blue?"
          }
        ]
      }'
  ```

- **Curl 示例**（流式）：

  ```bash
  curl -X POST http://localhost:3000/api/v1/messages \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "gpt-5.6-sol",
        "max_tokens": 1024,
        "stream": true,
        "messages": [
          {
            "role": "user",
            "content": "Why is the sky blue?"
          }
        ]
      }'
  ```

- **Python 示例**（使用 Anthropic SDK）：

  ```python
  from anthropic import Anthropic

  client = Anthropic(
      api_key="YOUR_OPEN_WEBUI_API_KEY",
      base_url="http://localhost:3000/api",
  )

  message = client.messages.create(
      model="gpt-5.6-sol",
      max_tokens=1024,
      messages=[
          {"role": "user", "content": "Why is the sky blue?"}
      ],
  )
  print(message.content[0].text)
  ```

  :::warning
  `base_url` 必须是 `http://localhost:3000/api`（而非 `/api/v1`）。Anthropic SDK 会自动在该 URL 后追加 `/v1/messages`。
  :::

- **Claude Code 配置**：

  要将 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 与 Open WebUI 作为代理一起使用，请将其配置为指向你的 Open WebUI 实例：

  ```bash
  # Set environment variables for Claude Code
  export ANTHROPIC_BASE_URL="http://localhost:3000/api"
  export ANTHROPIC_API_KEY="YOUR_OPEN_WEBUI_API_KEY"

  # Then run Claude Code as normal
  claude
  ```

  或者，创建或编辑 `~/.claude/settings.json`：

  ```json
  {
    "env": {
      "ANTHROPIC_BASE_URL": "http://localhost:3000/api",
      "ANTHROPIC_AUTH_TOKEN": "YOUR_OPEN_WEBUI_API_KEY"
    }
  }
  ```

  这会将所有 Claude Code 请求通过 Open WebUI 的认证和访问控制层路由，让你可以使用任何已配置的模型（包括通过 Ollama 或 vLLM 的本地模型）与 Claude Code 的界面配合使用。

:::info
Open WebUI 中配置的所有模型都可以通过此端点访问——包括 Ollama 模型、OpenAI 模型和任何自定义 Function 模型。`model` 字段应使用模型在 Open WebUI 中显示的模型 ID。过滤器（inlet/stream）应用于这些请求，与兼容 OpenAI 的端点相同。

**工具使用：** Anthropic 消息端点支持工具使用（`tools` 和 `tool_choice` 参数）。来自上游模型的工具调用会被转换为流式和非流式响应中的 Anthropic 格式 `tool_use` 内容块。

**用量上报：** 响应会携带上游模型上报的用量信息：流式时位于收尾的 `message_delta` 中，非流式时位于 `usage` 中。当提供方发送这些字段时，提示词缓存计数器（`cache_creation_input_tokens`、`cache_read_input_tokens`）、`output_tokens_details`、`server_tool_use` 和 `service_tier` 都会被透传，因此追踪缓存命中或推理 token 的客户端看到的是真实数值，而不是在转换中丢失。以 OpenAI 风格上报缓存 token 的提供方，其 `prompt_tokens_details.cached_tokens` 会被映射为 `cache_read_input_tokens`；而 `input_tokens` 会按照 Anthropic 客户端的预期上报：即未被缓存的提示词 token，缓存创建与缓存读取单独计数，而不是重复计算一次。在流式请求中，只有在确实已知时才会上报 `input_tokens`，因此从不报告该字段的提供方会把它整体省略，而不是显示一个凭空捏造的零值。

只有在模型的编辑器中启用了 **Usage** 能力时，才会向上游提供方请求用量信息。未启用时，不会要求提供方在流中包含用量，客户端收到的 token 计数会退回到 Open WebUI 自身能够判定的结果。
:::

#### Token 计数 {#counting-tokens}

Messages API 的配套端点，用于报告某个请求会消耗多少输入 token，而不会真正执行该请求。它与 Anthropic 自带的 token 计数端点保持一致，因此那些会预先估算请求以便做预算或上下文适配的 SDK 无需改动即可使用。

- **端点**：`POST /api/v1/messages/count_tokens`、`POST /api/message/count_tokens`
- **认证**：与 Messages API 相同
- **返回**：`{"input_tokens": <int>}`

```bash
curl -X POST http://localhost:3000/api/v1/messages/count_tokens \
-H "x-api-key: YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
      "model": "gpt-5.6-sol",
      "messages": [
        {
          "role": "user",
          "content": "Why is the sky blue?"
        }
      ]
    }'
```

计数结果来自解析出的连接背后的上游提供商，因此提供商必须实现 token 计数。如果没有实现，或返回了意料之外的结果，请求会失败并返回 `502`。

:::info 报告的 `input_tokens` 现在是真实值
Messages API 此前在流式响应的 `message_start` 块中总是报告 `input_tokens: 0`。现在输入 token 会被预先计数，并在流式和非流式响应中一并报告。若计数失败，请求仍然会成功，因此客户端应将该值视为尽力而为的结果，而非绝对保证。
:::

### `POST /api/v1/users/user/settings/update` 是补丁而非替换 {#post-apiv1usersusersettingsupdate-patches-it-does-not-replace}

该请求中的 `ui` 对象会按字段逐一应用。你略去的字段会保留当前值，而以 `null` 发送的字段会被清空，从而使该项回退到实例默认值。因此，发送局部对象是修改单个设置的常规做法。

读取设置、修改其中一个键后再把整个对象提交回去的脚本仍然可用。但如果某个脚本提交的是手写对象并期望其余内容被清空，那就不再生效了，因为凡是被它略去的字段都不会再被删除。

### 已移除：`POST /api/v1/utils/pdf` {#removed-post-apiv1utilspdf}

那个在服务端把对话渲染为 PDF 的端点连同其字体和 PDF 库一起被移除了。对使用 Open WebUI 的人来说没有任何变化：**对话 > 下载 > PDF** 仍然可用，并且始终在浏览器中渲染。只有直接调用该端点的脚本会受到影响，并且没有替代端点。

### 🔧 API 请求中的过滤器和 Function 行为 {#filter-and-function-behavior-with-api-requests}

直接使用 API 接口时，过滤器（Functions）的行为与通过 Web 界面发出请求时有所不同。

:::info 认证说明
Open WebUI 同时接受 **API Key**（以 `sk-` 为前缀）和 **JWT Token** 进行 API 认证。这是有意为之的——Web 界面在内部对相同的 API 接口使用 JWT Token。两种认证方式提供同等的 API 访问权限。
:::

#### 过滤器执行 {#filter-execution}

| 过滤器 Function | WebUI 请求 | 直接 API |
|----------------|--------------|------------|
| `inlet()` | 执行 | 执行 |
| `stream()` | 执行 | 执行 |
| `outlet()` | 执行 | 默认内联执行，由 `ENABLE_API_OUTLET_FILTERS` 控制（见下文） |

`inlet()` 函数始终执行，非常适合用于：
- **速率限制**：追踪并限制每用户的请求数
- **请求日志**：记录所有 API 使用情况以供监控
- **输入验证**：在请求到达模型之前拒绝无效请求

:::danger 直接 API 调用的 Outlet 行为——请仔细阅读
`outlet()` 在 `/api/chat/completions` 之后**默认**内联运行，在**流式与非流式两条路径上**都会运行，由 [`ENABLE_API_OUTLET_FILTERS`](/reference/env-configuration#enable_api_outlet_filters) 控制（默认 `True`）。请求体中**不需要** `chat_id` 和消息 `id`：两者都不在时，对话会根据你发送的 `messages` 加上助手回复重建，并为它生成一个消息 ID。把 `ENABLE_API_OUTLET_FILTERS=False` 即可为直接 API 流量关闭内联执行。

`chat_id` 与 `id` 决定的是响应的去向。两者都发送时，请求会走为 WebUI 构建的那条路径：服务器自行消费上游流，并通过 WebSocket 把内容路由给用户，因此流式调用方收到的 HTTP 响应实际上为空。不发送它们时，上游流会照常通过 HTTP 转发给你，`outlet()` 在流结束后运行一次。

在任何情况下，**`outlet()` 都不会改写 HTTP 响应体**。它会更新已持久化的聊天消息并发出 `chat:outlet` WebSocket 事件，但你的客户端收到的 JSON 仍是 outlet 之前的内容。如果你需要 outlet 过滤后的文本，请从聊天记录中回读、订阅 WebSocket，或者继续使用 `/api/chat/completed`。

**实用建议**：如果你是纯 API 消费者（Continue.dev、Claude Code、自定义脚本等），并且需要通过 HTTP 拿回 `outlet()` 的输出，请在补全之后调用 `/api/chat/completed`。内联执行仍然会运行你的 outlet 过滤器及其副作用，只是不会把过滤后的负载交给你。
:::

#### 旧版端点（支持 API）：`/api/chat/completed` {#legacy--supported-for-api-endpoint-apichatcompleted}

`POST /api/chat/completed` 是为直接 API 集成可靠运行 `outlet()` 的端点。它被标记为已弃用，但如上所述，内联执行目前不会向纯 API 调用者返回过滤后的响应体——因此在实践中，`/api/chat/completed` 仍是当今大多数 API 集成的正确选择。

- **端点**：`POST /api/chat/completed`
- **说明**：对已完成的聊天载荷无条件运行 `outlet()` 过滤器（以及流水线 outlet 过滤器）。返回过滤后的载荷。

- **Curl 示例**：

  ```bash
  curl -X POST http://localhost:3000/api/chat/completed \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "qwen3.6:27b",
        "messages": [
          {"role": "user", "content": "Hello"},
          {"role": "assistant", "content": "Hi! How can I help you today?"}
        ],
        "chat_id": "optional-uuid",
        "session_id": "optional-session-id"
      }'
  ```

- **Python 示例**：

  ```python
  import requests

  def complete_chat_with_outlet(token, model, messages, chat_id=None):
      """
      Second-step call that returns outlet()'s output to direct API callers.
      /api/chat/completions runs outlet inline by default but does not rewrite
      the HTTP response body, so this endpoint is still the right call for API
      integrations that want outlet's output over HTTP.
      """
      url = 'http://localhost:3000/api/chat/completed'
      headers = {
          'Authorization': f'Bearer {token}',
          'Content-Type': 'application/json'
      }
      payload = {
          'model': model,
          'messages': messages  # Include the full conversation with assistant response
      }
      if chat_id:
          payload['chat_id'] = chat_id
      
      response = requests.post(url, headers=headers, json=payload)
      return response.json()
  ```

:::tip
如果你今天需要通过 HTTP 获取 `outlet()` 的输出，请先调用 `/api/chat/completions`，再调用 `/api/chat/completed`。`dev` 版本上的内联执行仍会运行你的 outlet 过滤器及其副作用（持久化消息、`chat:outlet` WebSocket 事件、日志或追踪调用），但过滤后的文本不会在 HTTP 响应中返回。有关过滤器行为的更多详情，请参阅[过滤器 Function 文档](/features/extensibility/plugin/functions/filter#filter-behavior-with-api-requests)。
:::

### 🦙 Ollama API 代理支持 {#ollama-api-proxy-support}

如果你想直接与 Ollama 模型交互——包括生成嵌入向量或原始提示词流式传输——Open WebUI 通过代理路由提供对原生 Ollama API 的透明直通。

- **基础 URL**：`/ollama/<api>`
- **参考**：[Ollama API 文档](https://github.com/ollama/ollama/blob/main/docs/api.md)

#### 🔁 生成补全（流式） {#generate-completion-streaming}

```bash
curl http://localhost:3000/ollama/api/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "qwen3.6:27b",
  "prompt": "Why is the sky blue?"
}'
```

#### 📦 列出可用模型 {#list-available-models}

```bash
curl http://localhost:3000/ollama/api/tags \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### 🧠 生成嵌入向量 {#generate-embeddings}

```bash
curl -X POST http://localhost:3000/ollama/api/embed \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "qwen3.6:27b",
  "input": ["Open WebUI is great!", "Let'\''s generate embeddings."]
}'
```

:::info
使用 Ollama 代理接口时，POST 请求**必须**包含 `Content-Type: application/json` 头部，否则 API 可能无法解析请求体。如果实例已配置安全认证，还需要包含授权头部。
:::

#### 🔮 Responses API（兼容 OpenAI） {#responses-api-openai-compatible}

Ollama 支持 OpenAI Responses API 格式。Open WebUI 通过 Ollama 路由器代理路由，使用与聊天补全相同的模型解析、访问控制和前缀处理。

```bash
curl -X POST http://localhost:3000/ollama/v1/responses \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "qwen3.6:27b",
  "input": "Why is the sky blue?"
}'
```

这允许 API 消费者（Codex、Claude Code 等）直接将 Responses API 与 Ollama 托管模型配合使用，无需配置单独的兼容 OpenAI 连接。

这非常适合使用 Ollama 模型在 Open WebUI 后端构建搜索索引、检索系统或自定义流水线。

#### 嵌入（兼容 OpenAI） {#embeddings-openai-compatible}

除了上面原生的 `/ollama/api/embed` 路由之外，Open WebUI 还代理了一个兼容 OpenAI 的嵌入端点，因此已经使用 OpenAI 嵌入格式的客户端无需配置单独的连接即可使用 Ollama 托管的嵌入模型。它与其他被代理的路由采用相同的模型解析、访问控制和前缀处理。

```bash
curl -X POST http://localhost:3000/ollama/v1/embeddings \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "qwen3.6:27b",
  "input": "Open WebUI is great!"
}'
```

可以用 `/ollama/v1/embeddings/{url_idx}` 指定某个具体后端。如果 Ollama 集成被禁用，该端点会返回 `503`。

### 🧩 检索增强生成（RAG） {#retrieval-augmented-generation-rag}

检索增强生成（RAG）功能允许你将外部数据源内容融入到响应中。以下介绍如何通过 API 管理文件和知识库集合，以及如何在聊天补全中有效使用它们。

#### 上传文件 {#uploading-files}

要在 RAG 响应中使用外部数据，首先需要上传文件。上传文件的内容会自动提取并存储到向量数据库中。

- **端点**：`POST /api/v1/files/`
- **查询参数**：
  - `process`（布尔型，默认：`true`）：是否提取内容并计算嵌入向量
  - `process_in_background`（布尔型，默认：`true`）：是否异步处理
- **Curl 示例**：

  ```bash
  curl -X POST -H "Authorization: Bearer YOUR_API_KEY" -H "Accept: application/json" \
  -F "file=@/path/to/your/file" http://localhost:3000/api/v1/files/
  ```

- **Python 示例**：
  ```python
  import requests

  def upload_file(token, file_path):
      url = 'http://localhost:3000/api/v1/files/'
      headers = {
          'Authorization': f'Bearer {token}',
          'Accept': 'application/json'
      }
      files = {'file': open(file_path, 'rb')}
      response = requests.post(url, headers=headers, files=files)
      return response.json()
  ```

:::warning 异步处理与竞争条件

默认情况下，文件上传为**异步处理**。上传端点会立即返回文件 ID，内容提取和嵌入向量计算在后台继续进行。

如果在处理完成之前尝试将文件添加到知识库，你会收到 `400` 错误：

```
The content provided is empty. Please ensure that there is text or data present before proceeding.
```

**在将文件添加到知识库之前，必须等待文件处理完成。** 详见下方[检查文件处理状态](#checking-file-processing-status)部分。

:::

#### 检查文件处理状态 {#checking-file-processing-status}

将文件添加到知识库之前，请通过状态端点验证处理已完成。

- **端点**：`GET /api/v1/files/{id}/process/status`
- **查询参数**：
  - `stream`（布尔型，默认：`false`）：如果为 `true`，则返回服务器发送事件（SSE）流

**状态值：**
| 状态 | 说明 |
|--------|-------------|
| `pending` | 文件仍在处理中 |
| `completed` | 处理成功完成 |
| `failed` | 处理失败（查看 `error` 字段了解详情） |

- **Python 示例**（轮询）：

  ```python
  import requests
  import time

  def wait_for_file_processing(token, file_id, timeout=300, poll_interval=2):
      """
      Wait for a file to finish processing.
      
      Returns:
          dict: Final status with 'status' key ('completed' or 'failed')
      
      Raises:
          TimeoutError: If processing doesn't complete within timeout
      """
      url = f'http://localhost:3000/api/v1/files/{file_id}/process/status'
      headers = {'Authorization': f'Bearer {token}'}
      
      start_time = time.time()
      while time.time() - start_time < timeout:
          response = requests.get(url, headers=headers)
          result = response.json()
          status = result.get('status')
          
          if status == 'completed':
              return result
          elif status == 'failed':
              raise Exception(f"File processing failed: {result.get('error')}")
          
          time.sleep(poll_interval)
      
      raise TimeoutError(f"File processing did not complete within {timeout} seconds")
  ```

- **Python 示例**（SSE 流式）：

  ```python
  import requests
  import json

  def wait_for_file_processing_stream(token, file_id):
      """
      Wait for file processing using Server-Sent Events stream.
      More efficient than polling for long-running operations.
      """
      url = f'http://localhost:3000/api/v1/files/{file_id}/process/status?stream=true'
      headers = {'Authorization': f'Bearer {token}'}
      
      with requests.get(url, headers=headers, stream=True) as response:
          for line in response.iter_lines():
              if line:
                  line = line.decode('utf-8')
                  if line.startswith('data: '):
                      data = json.loads(line[6:])
                      status = data.get('status')
                      
                      if status == 'completed':
                          return data
                      elif status == 'failed':
                          raise Exception(f"File processing failed: {data.get('error')}")
      
      raise Exception("Stream ended unexpectedly")
  ```

#### 将文件添加到知识库集合 {#adding-files-to-knowledge-collections}

上传完成后，你可以将文件分组到知识库集合中，或在聊天中单独引用。

:::important
**将文件添加到知识库之前，必须等待文件处理完成。** 仍在处理中的文件内容为空，会导致 `400` 错误。使用上方的状态端点验证文件状态为 `completed`。
:::

- **端点**：`POST /api/v1/knowledge/{id}/file/add`
- **Curl 示例**：

  ```bash
  curl -X POST http://localhost:3000/api/v1/knowledge/{knowledge_id}/file/add \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id-here"}'
  ```

- **Python 示例**：

  ```python
  import requests

  def add_file_to_knowledge(token, knowledge_id, file_id):
      url = f'http://localhost:3000/api/v1/knowledge/{knowledge_id}/file/add'
      headers = {
          'Authorization': f'Bearer {token}',
          'Content-Type': 'application/json'
      }
      data = {'file_id': file_id}
      response = requests.post(url, headers=headers, json=data)
      return response.json()
  ```

如果某个文件的提取文本已经存在于知识库中，该请求会以 `400` 被拒绝，错误详情为 `400: Duplicate content detected. Please provide unique content to proceed.`。同样的检查也会在 `POST /api/v1/knowledge/{id}/files/batch/add` 上执行，该端点接受一组 `{"file_id": ...}` 对象：此时重复的文件会在响应的 warnings 中被报告为失败文件，而该批次中的其它文件仍会被添加。这两个调用都受知识库[文件限制](/features/workspace/knowledge#file-limits)的约束。


#### 将网页 URL 处理入知识库集合 {#processing-web-urls-into-knowledge-collections}

使用此端点获取网页并提取内容，然后将切分得到的片段存入向量集合。

- **端点**：`POST /api/v1/retrieval/process/web`
- **查询参数**：
  - `process`（布尔型，默认：`true`）：如果为 `false`，仅获取并返回提取的内容而不保存向量
  - `overwrite`（布尔型，默认：`true`）：是否在保存新块之前替换目标集合中现有的向量，即清空给定集合并用给定 URL 的内容替换它
- **请求体**：
  - `url`（字符串，必需）：要获取和解析的网页 URL
  - `collection_name`（字符串，可选）：目标集合名称。如果省略，Open WebUI 会根据 URL 自动生成
- **错误**：无法获取或没有返回内容的链接（例如主机拒绝连接）会返回 `400`，detail 为 `[ERROR: Could not read content from <url>]`；在 `process=false` 时同样如此。

**`overwrite` 行为：**
| 值 | 结果 |
|-------|--------|
| `true`（默认） | 插入新 URL 块之前，目标集合中现有的向量被替换 |
| `false` | 保留现有向量，新 URL 块被添加到同一集合中 |

- **Curl 示例**（保留现有向量）：

  ```bash
  curl -X POST 'http://localhost:3000/api/v1/retrieval/process/web?process=true&overwrite=false' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
        "url": "https://example.com/docs",
        "collection_name": "testkb"
      }'
  ```

- **Python 示例**：

  ```python
  import requests

  def process_web_url(token, url, collection_name="testkb", overwrite=False):
      response = requests.post(
          'http://localhost:3000/api/v1/retrieval/process/web',
          headers={
              'Authorization': f'Bearer {token}',
              'Content-Type': 'application/json'
          },
          params={
              'process': 'true',
              'overwrite': str(overwrite).lower()
          },
          json={
              'url': url,
              'collection_name': collection_name
          }
      )
      return response.json()
  ```

:::tip
如果启用了 `ENV=dev`，此端点的 schema（包括 `overwrite` 等查询参数）也可在 Swagger 的 `/docs` 中查看。
:::

#### 完整工作流程示例 {#complete-workflow-example}

以下是一个完整示例，展示如何上传文件、等待处理并将其添加到知识库：

```python
import requests
import time

WEBUI_URL = 'http://localhost:3000'
TOKEN = 'your-api-key-here'

def upload_and_add_to_knowledge(file_path, knowledge_id, timeout=300):
    """
    Upload a file and add it to a knowledge base.
    Properly waits for processing to complete before adding.
    """
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Accept': 'application/json'
    }
    
    # Step 1: Upload the file
    with open(file_path, 'rb') as f:
        response = requests.post(
            f'{WEBUI_URL}/api/v1/files/',
            headers=headers,
            files={'file': f}
        )
    
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.text}")
    
    file_data = response.json()
    file_id = file_data['id']
    print(f"File uploaded with ID: {file_id}")
    
    # Step 2: Wait for processing to complete
    print("Waiting for file processing...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status_response = requests.get(
            f'{WEBUI_URL}/api/v1/files/{file_id}/process/status',
            headers=headers
        )
        status_data = status_response.json()
        status = status_data.get('status')
        
        if status == 'completed':
            print("File processing completed!")
            break
        elif status == 'failed':
            raise Exception(f"Processing failed: {status_data.get('error')}")
        
        time.sleep(2)  # Poll every 2 seconds
    else:
        raise TimeoutError("File processing timed out")
    
    # Step 3: Add to knowledge base
    add_response = requests.post(
        f'{WEBUI_URL}/api/v1/knowledge/{knowledge_id}/file/add',
        headers={**headers, 'Content-Type': 'application/json'},
        json={'file_id': file_id}
    )
    
    if add_response.status_code != 200:
        raise Exception(f"Failed to add to knowledge: {add_response.text}")
    
    print(f"File successfully added to knowledge base!")
    return add_response.json()

# Usage
result = upload_and_add_to_knowledge('/path/to/document.pdf', 'your-knowledge-id')
```

#### 在聊天补全中使用文件和集合 {#using-files-and-collections-in-chat-completions}

你可以在 RAG 查询中引用单个文件或整个知识库，以丰富响应内容。

##### 在聊天补全中使用单个文件 {#using-an-individual-file-in-chat-completions}

当你希望聊天模型的响应聚焦在特定文件的内容上时，此方法非常适用。

- **端点**：`POST /api/chat/completions`
- **Curl 示例**：

  ```bash
  curl -X POST http://localhost:3000/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "gpt-5.6-terra",
        "messages": [
          {"role": "user", "content": "Explain the concepts in this document."}
        ],
        "files": [
          {"type": "file", "id": "your-file-id-here"}
        ]
      }'
  ```

- **Python 示例**：

  ```python
  import requests

  def chat_with_file(token, model, query, file_id):
      url = 'http://localhost:3000/api/chat/completions'
      headers = {
          'Authorization': f'Bearer {token}',
          'Content-Type': 'application/json'
      }
      payload = {
          'model': model,
          'messages': [{'role': 'user', 'content': query}],
          'files': [{'type': 'file', 'id': file_id}]
      }
      response = requests.post(url, headers=headers, json=payload)
      return response.json()
  ```

##### 在聊天补全中使用知识库集合 {#using-a-knowledge-collection-in-chat-completions}

当查询可能需要更广泛的上下文或多个文档时，利用知识库集合来增强响应。

- **端点**：`POST /api/chat/completions`
- **Curl 示例**：

  ```bash
  curl -X POST http://localhost:3000/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "gpt-5.6-terra",
        "messages": [
          {"role": "user", "content": "Provide insights on the historical perspectives covered in the knowledge base."}
        ],
        "files": [
          {"type": "collection", "id": "your-collection-id-here"}
        ]
      }'
  ```

- **Python 示例**：

  ```python
  import requests

  def chat_with_collection(token, model, query, collection_id):
      url = 'http://localhost:3000/api/chat/completions'
      headers = {
          'Authorization': f'Bearer {token}',
          'Content-Type': 'application/json'
      }
      payload = {
          'model': model,
          'messages': [{'role': 'user', 'content': query}],
          'files': [{'type': 'collection', 'id': collection_id}]
      }
      response = requests.post(url, headers=headers, json=payload)
      return response.json()
  ```

借助 Open WebUI API，这些方法可以利用上传的文件和整理好的知识库中的外部知识，增强聊天应用的能力。无论是单独使用文件还是将其纳入知识库，你都可以根据具体需要自定义集成方式。

## 将 Open WebUI 作为统一 LLM 提供商的优势 {#advantages-of-using-open-webui-as-a-unified-llm-provider}

Open WebUI 提供了许多优势，使其成为开发者和企业的重要工具：

- **统一界面**：通过单一的集成平台，简化与不同 LLM 的交互。
- **实现简便**：配合全面的文档和社区支持，快速开始集成。

按照这些指南，你可以迅速集成并开始使用 Open WebUI API。如果遇到任何问题，请透过我们的 Discord 社区进行反馈，或查阅 FAQ。祝编程愉快！🌟
