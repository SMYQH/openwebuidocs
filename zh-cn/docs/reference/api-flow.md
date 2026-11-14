---
sidebar_position: 40
title: "后端控制的 API 流程"
---

# 后端控制、兼容前端的 API 流程 {#backend-controlled-ui-compatible-api-flow}

---


:::warning

本教程为社区贡献内容，并不属于 Open WebUI 团队的官方支持。它仅用于展示如何根据你的具体需求定制 Open WebUI。想要贡献？请查看[贡献指南](/tutorials/contributing-tutorial)。

:::

本教程展示如何实现对 Open WebUI 对话的服务器端编排，并确保助手回复能在前端 UI 中正常显示。这种方法不需前端任何介入，并允许完全的后端控制聊天流程。
本教程已验证适用于 Open WebUI 版本 v0.6.15。未来版本可能会展开行为或 API 结构的变化。

:::tip 你关心的是工具调用？
如果你的目标是让模型使用工具（内置工具、工作区工具、MCP 服务器或终端），并让 Open WebUI 在服务器端执行它们，请参见 [Server-Side Tool Calling (API)](/reference/server-side-tool-calling)。它在此处记述的聊天结构之上添加了开启工具执行所需的字段。
:::

## 前置条件 {#prerequisites}

在实践本教程之前，请确保你有：

- 一个运行中的 Open WebUI 实例
- 有效的 API 认证令牌
- 能够访问 Open WebUI 后端 API
- 对 REST API 和 JSON 的基本了解
- 命令行工具：`curl`、`jq`（可选，用于 JSON 解析）

## 概述 {#overview}

本教程描述了一个包含 6 个步骤的完整流程，能够实现对 Open WebUI 对话的服务器端编排，同时确保助手回复能在前端 UI 中正常显示。

### 流程步骤 {#process-flow}

核心步骤如下：

1. **创建包含用户和助手消息的新对话** —— 使用用户输入和空助手占位符初始化对话
2. **触发助手补全** —— 生成实际的 AI 响应（可带知识集成）
3. **等待响应完成** —— 监控助手响应直到完全生成
4. **获取并处理最终对话** —— 获取并解析已完成的对话

这将实现服务器端编排，同时使回复在前端 UI 中显示，完全如同通过正常用户交互生成一样。

## 重要概念 {#important-concepts}

### 消息 ID 由调用方生成 {#message-ids-are-caller-generated}

所有消息 ID（`user-msg-id`、`assistant-msg-id`）必须在**发起 API 调用之前**由**调用方以有效的 UUID 生成**。Open WebUI 不会为你分配消息 ID。使用任何 UUID v4 生成器即可。

示例（bash）：

``` bash
USER_MSG_ID=$(uuidgen || python3 -c "import uuid; print(uuid.uuid4())")
ASSISTANT_MSG_ID=$(uuidgen || python3 -c "import uuid; print(uuid.uuid4())")
```

### `childrenIds` 字段 {#the-childrenids-field}

Open WebUI 前端将消息渲染为一个**树形结构**。每条消息必须包含 `childrenIds` 数组，列出其直接子消息的 ID。没有这个字段，前端无法遍历消息树，**消息将无法显示**，即使它们已存在于数据库中。

- **用户消息**必须在 `childrenIds` 中列出其对应的助手回复 ID
- **助手消息**通常使用 `childrenIds: []`（空数组），除非后面还有继续对话的消息

### `currentId` 字段 {#the-currentid-field}

`history` 对象必须使用 `currentId`（**camelCase**，不是 `current_id`）。这个字段告诉前端当前活动对话线程最后一条消息是哪一条。

## 实现指南 {#implementation-guide}

### 关键步骤：在聊天响应中补充助手消息 {#critical-step-enrich-chat-response-with-assistant-message}

在触发补全之前，助手消息必须作为关键前提先存在于聊天数据中。这个步骤至关重要，因为 Open WebUI 前端期望助手消息具有特定的结构。

助手消息必须同时出现在以下两个位置：

- `chat.messages[]` — 主要消息数组（用于旧版兼容）
- `chat.history.messages[<assistantId>]` — 按 ID 索引的消息历史（前端用它来渲染树状结构）

**助手消息的预期结构：**

``` json
{
  "id": "<uuid>",
  "role": "assistant",
  "content": "",
  "parentId": "<user-msg-id>",
  "childrenIds": [],
  "model": "gpt-5.6-sol",
  "modelName": "gpt-5.6-sol",
  "modelIdx": 0,
  "done": false,
  "timestamp": 1720000001
}
```

如果不做这一步补充，即使补全成功，助手的回复也不会出现在前端界面中。

## 分步实现 {#step-by-step-implementation}

### 第 1 步：创建包含用户和助手消息的对话 {#step-1-create-chat-with-user-and-assistant-messages}

这一步会在一次请求中同时创建用户消息和一个空的助手占位符。响应会返回一个 `chatId`（位于 `id` 字段），后续请求会使用它。

:::tip

你可以把创建对话和补充助手消息合并到这一步。关键是在初始载荷中同时包含用户消息和空的助手消息，并正确设置 `parentId`、`childrenIds` 和 `currentId` 字段。

:::

``` bash
USER_MSG_ID=$(uuidgen || python3 -c "import uuid; print(uuid.uuid4())")
ASSISTANT_MSG_ID=$(uuidgen || python3 -c "import uuid; print(uuid.uuid4())")
TIMESTAMP=$(date +%s)

curl -X POST https://<host>/api/v1/chats/new \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "chat": {
      "title": "New Chat",
      "models": ["gpt-5.6-sol"],
      "messages": [
        {
          "id": "'"$USER_MSG_ID"'",
          "role": "user",
          "content": "Hi, what is the capital of France?",
          "timestamp": '"$TIMESTAMP"',
          "models": ["gpt-5.6-sol"],
          "childrenIds": ["'"$ASSISTANT_MSG_ID"'"]
        },
        {
          "id": "'"$ASSISTANT_MSG_ID"'",
          "role": "assistant",
          "content": "",
          "parentId": "'"$USER_MSG_ID"'",
          "childrenIds": [],
          "model": "gpt-5.6-sol",
          "modelName": "gpt-5.6-sol",
          "modelIdx": 0,
          "done": false,
          "timestamp": '"$((TIMESTAMP + 1))"'
        }
      ],
      "history": {
        "currentId": "'"$ASSISTANT_MSG_ID"'",
        "messages": {
          "'"$USER_MSG_ID"'": {
            "id": "'"$USER_MSG_ID"'",
            "role": "user",
            "content": "Hi, what is the capital of France?",
            "timestamp": '"$TIMESTAMP"',
            "models": ["gpt-5.6-sol"],
            "childrenIds": ["'"$ASSISTANT_MSG_ID"'"]
          },
          "'"$ASSISTANT_MSG_ID"'": {
            "id": "'"$ASSISTANT_MSG_ID"'",
            "role": "assistant",
            "content": "",
            "parentId": "'"$USER_MSG_ID"'",
            "childrenIds": [],
            "model": "gpt-5.6-sol",
            "modelName": "gpt-5.6-sol",
            "modelIdx": 0,
            "done": false,
            "timestamp": '"$((TIMESTAMP + 1))"'
          }
        }
      }
    }
  }'
```

**请保存响应中的 `id` 字段** —— 这就是后续步骤要用的 `chatId`。

:::note

顶层的 `messages[]` 数组是用于旧版兼容的扁平列表。`history.messages{}` 对象才是权威结构——它是一个以消息 ID 为键的字典，前端会通过 `parentId` 和 `childrenIds` 用它来构建对话树。

:::

### 第 2 步：触发助手补全 {#step-2-trigger-assistant-completion}

使用补全端点生成实际的 AI 响应。请使用第 1 步得到的 `chatId`：

``` bash
curl -X POST https://<host>/api/chat/completions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "<chatId>",
    "id": "'"$ASSISTANT_MSG_ID"'",
    "user_message": {
      "id": "'"$USER_MSG_ID"'",
      "role": "user",
      "content": "Hi, what is the capital of France?",
      "parentId": null,
      "childrenIds": ["'"$ASSISTANT_MSG_ID"'"],
      "timestamp": '"$TIMESTAMP"',
      "models": ["gpt-5.6-sol"]
    },
    "messages": [
      {
        "role": "user",
        "content": "Hi, what is the capital of France?"
      }
    ],
    "model": "gpt-5.6-sol",
    "stream": true,
    "background_tasks": {
      "title_generation": true,
      "tags_generation": false,
      "follow_up_generation": false
    },
    "features": {
      "code_interpreter": false,
      "web_search": false,
      "image_generation": false,
      "memory": false
    },
    "variables": {
      "{{USER_NAME}}": "",
      "{{USER_LANGUAGE}}": "en-US",
      "{{CURRENT_DATETIME}}": "2025-07-14T12:00:00Z",
      "{{CURRENT_TIMEZONE}}": "Europe"
    },
    "session_id": "<session-uuid>"
  }'
```

:::note

`session_id` 应该是你为本次会话生成的唯一 UUID。它有助于保持对话上下文，如果前端处于打开状态，它也会用于 WebSocket 事件路由。

:::

:::warning 一定要带上 `user_message`

`user_message` 承载本次补全所应答的用户消息，也就是你在第 1 步中保存的同一个对象。后端会把助手消息的 `parentId` 设置为那条消息的 `id` 后保存，从而让用户消息留在会话线程中。如果不带上它，助手消息保存时就没有父级，页面刷新后聊天中只会剩下助手回复。

:::

#### 第 2.1 步：结合知识集成（RAG）触发助手补全 {#step-21-trigger-assistant-completion-with-knowledge-integration-rag}

对于涉及知识库或文档集合的高级用例，可以在补全请求中包含知识文件：

``` bash
curl -X POST https://<host>/api/chat/completions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "<chatId>",
    "id": "'"$ASSISTANT_MSG_ID"'",
    "user_message": {
      "id": "'"$USER_MSG_ID"'",
      "role": "user",
      "content": "Hi, what is the capital of France?",
      "parentId": null,
      "childrenIds": ["'"$ASSISTANT_MSG_ID"'"],
      "timestamp": '"$TIMESTAMP"',
      "models": ["gpt-5.6-sol"]
    },
    "messages": [
      {
        "role": "user",
        "content": "Hi, what is the capital of France?"
      }
    ],
    "model": "gpt-5.6-sol",
    "stream": true,
    "files": [
      {
        "id": "knowledge-collection-id",
        "type": "collection",
        "status": "processed"
      }
    ],
    "background_tasks": {
      "title_generation": true,
      "tags_generation": false,
      "follow_up_generation": false
    },
    "features": {
      "code_interpreter": false,
      "web_search": false,
      "image_generation": false,
      "memory": false
    },
    "variables": {
      "{{USER_NAME}}": "",
      "{{USER_LANGUAGE}}": "en-US",
      "{{CURRENT_DATETIME}}": "2025-07-14T12:00:00Z",
      "{{CURRENT_TIMEZONE}}": "Europe"
    },
    "session_id": "<session-uuid>"
  }'
```

### 第 3 步：等待助手响应完成 {#step-3-wait-for-assistant-response-completion}

根据你的实现需求，助手响应可以通过两种方式处理：

#### 选项 A：流式处理（推荐） {#option-a-stream-processing-recommended}

如果在补全请求中使用 `stream: true`，你就可以实时处理流式响应，并等待流结束。这是 OpenWebUI Web 界面采用的方式，能提供即时反馈。

#### 选项 B：轮询方式 {#option-b-polling-approach}

对于无法处理流式响应的实现，可以轮询聊天端点，直到响应准备好。请使用带指数退避的重试机制：

``` bash

# Poll every few seconds until assistant content is populated
while true; do
  response=$(curl -s -X GET https://<host>/api/v1/chats/<chatId> \
    -H "Authorization: Bearer <token>")

  # Check if assistant message has content (response is ready)
  assistant_content=$(echo "$response" | jq -r ".chat.history.messages[\"$ASSISTANT_MSG_ID\"].content // empty")
  if [ -n "$assistant_content" ]; then
    echo "Assistant response is ready!"
    echo "$assistant_content"
    break
  fi

  echo "Waiting for assistant response..."
  sleep 2
done
```

### 第 4 步：获取最终对话 {#step-4-fetch-final-chat}

获取已完成的对话：

``` bash
curl -X GET https://<host>/api/v1/chats/<chatId> \
  -H "Authorization: Bearer <token>"
```

## 其他 API 端点 {#additional-api-endpoints}

### 获取知识集合 {#fetch-knowledge-collection}

获取用于 RAG 集成的知识库信息：

``` bash
curl -X GET https://<host>/api/v1/knowledge/<knowledge-id> \
  -H "Authorization: Bearer <token>"
```

### 获取模型信息 {#fetch-model-information}

获取某个特定模型的详细信息：

``` bash
curl -X GET https://<host>/api/v1/models/model?id=<model-name> \
  -H "Authorization: Bearer <token>"
```

### 向现有对话发送更多消息 {#send-additional-messages-to-an-existing-chat}

对于多轮对话，你可以向现有聊天中追加新消息。你必须提供完整更新后的消息树，并正确维护 `parentId` 和 `childrenIds` 的关联：

``` bash
NEW_USER_MSG_ID=$(uuidgen || python3 -c "import uuid; print(uuid.uuid4())")
NEW_ASSISTANT_MSG_ID=$(uuidgen || python3 -c "import uuid; print(uuid.uuid4())")

# First: update the chat to add the new user + assistant placeholder
# You need to link the previous assistant message to the new user message via childrenIds
curl -X POST https://<host>/api/v1/chats/<chatId> \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "chat": {
      "history": {
        "currentId": "'"$NEW_ASSISTANT_MSG_ID"'",
        "messages": {
          "'"$ASSISTANT_MSG_ID"'": {
            "childrenIds": ["'"$NEW_USER_MSG_ID"'"]
          },
          "'"$NEW_USER_MSG_ID"'": {
            "id": "'"$NEW_USER_MSG_ID"'",
            "role": "user",
            "content": "Can you tell me more about Paris?",
            "parentId": "'"$ASSISTANT_MSG_ID"'",
            "childrenIds": ["'"$NEW_ASSISTANT_MSG_ID"'"],
            "timestamp": '"$(date +%s)"',
            "models": ["gpt-5.6-sol"]
          },
          "'"$NEW_ASSISTANT_MSG_ID"'": {
            "id": "'"$NEW_ASSISTANT_MSG_ID"'",
            "role": "assistant",
            "content": "",
            "parentId": "'"$NEW_USER_MSG_ID"'",
            "childrenIds": [],
            "model": "gpt-5.6-sol",
            "modelName": "gpt-5.6-sol",
            "modelIdx": 0,
            "done": false,
            "timestamp": '"$(($(date +%s) + 1))"'
          }
        }
      }
    }
  }'

# Then: trigger completion for the new assistant message (same as Step 2)
curl -X POST https://<host>/api/chat/completions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "<chatId>",
    "id": "'"$NEW_ASSISTANT_MSG_ID"'",
    "user_message": {
      "id": "'"$NEW_USER_MSG_ID"'",
      "role": "user",
      "content": "Can you tell me more about Paris?",
      "parentId": "'"$ASSISTANT_MSG_ID"'",
      "childrenIds": ["'"$NEW_ASSISTANT_MSG_ID"'"],
      "models": ["gpt-5.6-sol"]
    },
    "messages": [
      { "role": "user", "content": "Hi, what is the capital of France?" },
      { "role": "assistant", "content": "The capital of France is Paris." },
      { "role": "user", "content": "Can you tell me more about Paris?" }
    ],
    "model": "gpt-5.6-sol",
    "stream": true,
    "session_id": "<session-uuid>"
  }'
```

:::note

通过 `POST /api/v1/chats/<chatId>` 更新现有聊天时，请求体将与现有的聊天数据**合并**。你只需包含你要更改的字段。对于 `history.messages`，你可以传递部分更新——未包含在更新中的现有消息将被保留。

:::

## 响应处理 {#response-processing}

### 解析助手回复 {#parsing-assistant-responses}

助手回复有时会被包裹在 Markdown 代码块中。可以按以下方式清理：

``` bash

# Example raw response from assistant
raw_response='```json
{
  "result": "The capital of France is Paris.",
  "confidence": 0.99
}
```'

# Clean the response (remove markdown wrappers)
cleaned_response=$(echo "$raw_response" | sed 's/^```json//' | sed 's/```$//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')

echo "$cleaned_response" | jq '.'
```

This cleaning process handles:

- Removal of ````json` prefix
- Removal of ```` suffix
- Trimming whitespace
- JSON validation

## API Reference

### DTO Structures

#### Chat DTO (Complete Structure)

``` json
{
  "id": "chat-uuid-12345",
  "title": "New Chat",
  "models": ["gpt-5.6-sol"],
  "files": [],
  "tags": [],
  "params": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "timestamp": 1720000000,
  "messages": [
    {
      "id": "user-msg-id",
      "role": "user",
      "content": "Hi, what is the capital of France?",
      "timestamp": 1720000000,
      "models": ["gpt-5.6-sol"],
      "childrenIds": ["assistant-msg-id"]
    },
    {
      "id": "assistant-msg-id",
      "role": "assistant",
      "content": "",
      "parentId": "user-msg-id",
      "childrenIds": [],
      "model": "gpt-5.6-sol",
      "modelName": "gpt-5.6-sol",
      "modelIdx": 0,
      "done": false,
      "timestamp": 1720000001
    }
  ],
  "history": {
    "currentId": "assistant-msg-id",
    "messages": {
      "user-msg-id": {
        "id": "user-msg-id",
        "role": "user",
        "content": "Hi, what is the capital of France?",
        "timestamp": 1720000000,
        "models": ["gpt-5.6-sol"],
        "childrenIds": ["assistant-msg-id"]
      },
      "assistant-msg-id": {
        "id": "assistant-msg-id",
        "role": "assistant",
        "content": "",
        "parentId": "user-msg-id",
        "childrenIds": [],
        "model": "gpt-5.6-sol",
        "modelName": "gpt-5.6-sol",
        "modelIdx": 0,
        "done": false,
        "timestamp": 1720000001
      }
    }
  },
  "currentId": "assistant-msg-id"
}
```

#### ChatCompletionsRequest DTO


``` json
{
  "chat_id": "chat-uuid-12345",
  "id": "assistant-msg-id",
  "user_message": {
    "id": "user-msg-id",
    "role": "user",
    "content": "Hi, what is the capital of France?",
    "parentId": null,
    "childrenIds": ["assistant-msg-id"],
    "timestamp": 1720000000,
    "models": ["gpt-5.6-sol"]
  },
  "messages": [
    {
      "role": "user",
      "content": "Hi, what is the capital of France?"
    }
  ],
  "model": "gpt-5.6-sol",
  "stream": true,
  "background_tasks": {
    "title_generation": true,
    "tags_generation": false,
    "follow_up_generation": false
  },
  "features": {
    "code_interpreter": false,
    "web_search": false,
    "image_generation": false,
    "memory": false
  },
  "variables": {
    "{{USER_NAME}}": "",
    "{{USER_LANGUAGE}}": "en-US",
    "{{CURRENT_DATETIME}}": "2025-07-14T12:00:00Z",
    "{{CURRENT_TIMEZONE}}": "Europe"
  },
  "session_id": "session-uuid-67890",
  "filter_ids": [],
  "files": [
    {
      "id": "knowledge-collection-id",
      "type": "collection",
      "status": "processed"
    }
  ]
}
```
#### ChatCompletionMessage DTO

``` json
{
  "role": "user",
  "content": "Hi, what is the capital of France?"
}
```

#### History DTO

``` json
{
  "currentId": "assistant-msg-id",
  "messages": {
    "user-msg-id": {
      "id": "user-msg-id",
      "role": "user",
      "content": "Hi, what is the capital of France?",
      "timestamp": 1720000000,
      "models": ["gpt-5.6-sol"],
      "childrenIds": ["assistant-msg-id"]
    },
    "assistant-msg-id": {
      "id": "assistant-msg-id",
      "role": "assistant",
      "content": "The capital of France is Paris.",
      "parentId": "user-msg-id",
      "childrenIds": [],
      "model": "gpt-5.6-sol",
      "modelName": "gpt-5.6-sol",
      "modelIdx": 0,
      "timestamp": 1720000001
    }
  }
}
```

#### Message DTO (Complete Structure)

**User message:**

``` json
{
  "id": "user-msg-id",
  "role": "user",
  "content": "Hi, what is the capital of France?",
  "timestamp": 1720000000,
  "models": ["gpt-5.6-sol"],
  "childrenIds": ["assistant-msg-id"]
}
```

**Assistant message:**

``` json
{
  "id": "assistant-msg-id",
  "role": "assistant",
  "content": "The capital of France is Paris.",
  "parentId": "user-msg-id",
  "childrenIds": [],
  "model": "gpt-5.6-sol",
  "modelName": "gpt-5.6-sol",
  "modelIdx": 0,
  "done": true,
  "timestamp": 1720000001
}
```

### 响应示例 {#response-examples}

#### 创建对话响应 {#create-chat-response}

``` json
{
  "id": "chat-uuid-12345",
  "user_id": "user-uuid",
  "title": "New Chat",
  "chat": {
    "title": "New Chat",
    "models": ["gpt-5.6-sol"],
    "messages": [
      {
        "id": "user-msg-id",
        "role": "user",
        "content": "Hi, what is the capital of France?",
        "timestamp": 1720000000,
        "models": ["gpt-5.6-sol"],
        "childrenIds": ["assistant-msg-id"]
      },
      {
        "id": "assistant-msg-id",
        "role": "assistant",
        "content": "",
        "parentId": "user-msg-id",
        "childrenIds": [],
        "model": "gpt-5.6-sol",
        "modelName": "gpt-5.6-sol",
        "modelIdx": 0,
        "done": false,
        "timestamp": 1720000001
      }
    ],
    "history": {
      "currentId": "assistant-msg-id",
      "messages": {
        "user-msg-id": {
          "id": "user-msg-id",
          "role": "user",
          "content": "Hi, what is the capital of France?",
          "timestamp": 1720000000,
          "models": ["gpt-5.6-sol"],
          "childrenIds": ["assistant-msg-id"]
        },
        "assistant-msg-id": {
          "id": "assistant-msg-id",
          "role": "assistant",
          "content": "",
          "parentId": "user-msg-id",
          "childrenIds": [],
          "model": "gpt-5.6-sol",
          "modelName": "gpt-5.6-sol",
          "modelIdx": 0,
          "done": false,
          "timestamp": 1720000001
        }
      }
    },
    "currentId": "assistant-msg-id"
  },
  "updated_at": 1720000000,
  "created_at": 1720000000
}
```

#### 最终对话响应（完成后） {#final-chat-response-after-completion}

``` json
{
  "id": "chat-uuid-12345",
  "title": "Capital of France Discussion",
  "chat": {
    "models": ["gpt-5.6-sol"],
    "history": {
      "currentId": "assistant-msg-id",
      "messages": {
        "user-msg-id": {
          "id": "user-msg-id",
          "role": "user",
          "content": "Hi, what is the capital of France?",
          "timestamp": 1720000000,
          "models": ["gpt-5.6-sol"],
          "childrenIds": ["assistant-msg-id"]
        },
        "assistant-msg-id": {
          "id": "assistant-msg-id",
          "role": "assistant",
          "content": "The capital of France is Paris. Paris is not only the capital but also the most populous city in France, known for its iconic landmarks such as the Eiffel Tower, the Louvre Museum, and Notre-Dame Cathedral.",
          "parentId": "user-msg-id",
          "childrenIds": [],
          "model": "gpt-5.6-sol",
          "modelName": "gpt-5.6-sol",
          "modelIdx": 0,
          "done": true,
          "timestamp": 1720000001
        }
      }
    },
    "currentId": "assistant-msg-id"
  }
}
```

#### OWUIKnowledge DTO（知识集合） {#owuiknowledge-dto-knowledge-collection}

``` json
{
  "id": "knowledge-collection-id",
  "type": "collection",
  "status": "processed",
  "name": "Geography Knowledge Base",
  "description": "Contains information about world geography and capitals",
  "created_at": 1720000000,
  "updated_at": 1720000001
}
```

#### 模型信息响应 {#model-information-response}

``` json
{
  "id": "gpt-5.6-sol",
  "name": "GPT-5.6 Sol",
  "model": "gpt-5.6-sol",
  "base_model_id": "gpt-5.6-sol",
  "meta": {
    "description": "OpenAI's frontier model for complex professional work",
    "capabilities": ["text", "vision", "function_calling"],
    "context_length": 128000,
    "max_output_tokens": 4096
  },
  "params": {
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  },
  "created_at": 1720000000,
  "updated_at": 1720000001
}
```

### 字段参考 {#field-reference-guide}

#### 必填与可选字段 {#required-vs-optional-fields}

**Chat Creation - Required Fields:**

- `title`: Chat title (string)
- `models`: Array of model names (string[])
- `messages`: Initial message array
- `history`: Message tree with `currentId` and `messages` map

**Chat Creation - Optional Fields:**

- `files`: Knowledge files for RAG (defaults to empty array)
- `tags`: Chat tags (defaults to empty array)
- `params`: Model parameters (defaults to empty object)

**Message Structure - User Message:**

- **Required:** `id`, `role`, `content`, `timestamp`, `models`, `childrenIds`
- **Optional:** `parentId` (for threading; omit for the first message in a chat)

**Message Structure - Assistant Message:**

- **Required:** `id`, `role`, `content`, `parentId`, `childrenIds`, `model`, `modelName`, `modelIdx`, `timestamp`
- **Optional:** `done` (boolean, defaults to false), additional metadata fields

**ChatCompletionsRequest - Required Fields:**

- `chat_id`: Target chat ID
- `id`: Assistant message ID
- `messages`: Array of ChatCompletionMessage
- `model`: Model identifier
- `session_id`: Session identifier (caller-generated UUID)

**ChatCompletionsRequest - Optional Fields:**

- `stream`: Enable streaming (defaults to false)
- `background_tasks`: Control automatic tasks
- `features`: Enable/disable features
- `variables`: Template variables
- `filter_ids`: Pipeline filters
- `files`: Knowledge collections for RAG

#### 字段约束 {#field-constraints}

**Timestamps:**

- Format: Unix timestamp in **seconds** (not milliseconds) for message timestamps in `history.messages`
- The top-level chat `timestamp` field uses milliseconds
- Example: `1720000000` (July 3, 2024)

**UUIDs:**

- All ID fields (`id`, `parentId`, `session_id`) should use valid UUID v4 format
- Example: `550e8400-e29b-41d4-a716-446655440000`
- IDs are **generated by the caller**, not assigned by the server

**Model Names:**

- Must match available models in your Open WebUI instance
- Common examples: `gpt-5.6-sol`, `gpt-5.6-luna`, `claude-sonnet-5`

**Session IDs:**

- Can be any unique string identifier
- Recommendation: Use UUID format for consistency

**Knowledge File Status:**

- Valid values: `"processed"`, `"processing"`, `"error"`
- Only use `"processed"` files for completions

## 重要说明 {#important-notes}

- This workflow is compatible with Open WebUI + backend orchestration scenarios
- **Critical: Use `currentId` (camelCase)** in the history object, not `current_id` (snake_case)
- **Critical: Include `childrenIds`** on every message. The frontend uses this to build the message tree
- No frontend code changes are required for this approach
- The `stream: true` parameter allows for real-time response streaming if needed
- `outlet()` filters run inline during `/api/chat/completions`, on both the streaming and non-streaming paths, controlled by [`ENABLE_API_OUTLET_FILTERS`](/reference/env-configuration#enable_api_outlet_filters) (default `True`). Neither a `chat_id` nor a message `id` is required in the request body; with neither present, the conversation is reconstructed from the `messages` you sent plus the assistant reply, and a message ID is generated for it. Inline execution does not rewrite the HTTP response body, so the filtered payload never comes back to an API caller over HTTP. The separate `/api/chat/completed` endpoint is deprecated and kept for backward compatibility, and it remains the way to have the filtered payload returned to you. See [Filter Behavior with API Requests](/features/extensibility/plugin/functions/filter#filter-behavior-with-api-requests) for the full picture
- Background tasks like title generation can be controlled via the `background_tasks` object
- Session IDs help maintain conversation context across requests
- **Knowledge Integration:** Use the `files` array to include knowledge collections for RAG capabilities
- **Response Parsing:** Handle JSON responses that may be wrapped in markdown code blocks
- **Error Handling:** Implement proper retry mechanisms for network timeouts and server errors

## 常见问题 {#common-pitfalls}

| Symptom | Cause | Fix |
|---|---|---|
| Chat created but messages don't appear in UI | Missing `childrenIds` on messages | Add `childrenIds` array linking parent → child messages |
| Chat shows "How can I help you today?" | Using `current_id` instead of `currentId` | Use camelCase `currentId` in the history object |
| Completion works but response only appears as notification | Assistant message not in chat history before triggering completion | Include empty assistant placeholder in Step 1 |
| Messages exist in DB but frontend shows empty chat | Missing `parentId` or broken tree linkage | Ensure every message has correct `parentId` and parent's `childrenIds` includes the child |
| User message disappears after a page reload once the completion ran | `user_message` missing from the `/api/chat/completions` request, so the assistant message is saved with no parent | Send `user_message` with the user message's `id` in the completion request (Step 2) |

## 总结 {#summary}

Use the Open WebUI backend APIs to:

1. **Start a chat with messages**: Create the conversation with user input and an empty assistant placeholder (including proper `childrenIds` and `currentId`)
2. **Trigger a reply**: Generate the AI response (with optional knowledge integration)
3. **Monitor completion**: Wait for the assistant response using streaming or polling
4. **Fetch the final chat**: Retrieve and parse the completed conversation

**Enhanced Capabilities:**

- **RAG Integration**: Include knowledge collections for context-aware responses
- **Asynchronous Processing**: Handle long-running AI operations with streaming or polling
- **Response Parsing**: Clean and validate JSON responses from the assistant
- **Session Management**: Maintain conversation context across requests

This enables backend-controlled workflows that still appear properly in the Web UI frontend chat interface, providing seamless integration between programmatic control and user experience.

The key advantage of this approach is that it maintains full compatibility with the Open WebUI frontend while allowing complete backend orchestration of the conversation flow, including advanced features like knowledge integration and asynchronous response handling.

## 测试 {#testing}

You can test your implementation by following the step-by-step CURL examples provided above. Make sure to replace placeholder values with your actual:

- Host URL
- Authentication token
- Chat IDs (from the create chat response)
- Message IDs (UUIDs you generate)
- Model names (matching your configured models)

:::tip

Start with a simple user message and gradually add complexity like knowledge integration and advanced features once the basic flow is working.

:::