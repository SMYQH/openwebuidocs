---
sidebar_position: 45
title: "服务端工具调用 (API)"
---

# 通过 API 进行服务端工具调用 {#server-side-tool-calling-over-the-api}

**把提示词发给 Open WebUI，由 Open WebUI 运行工具，并把最终答案取回来。**

本页介绍当你想让*服务器*完成智能体工作时所需的准确请求：模型决定调用某个工具，Open WebUI 使用你的用户凭据和权限执行它，把结果回传给模型，并如此反复直到模型完成。你的脚本永远不会收到需要自己执行的 `tool_calls` 对象。

这包括：

- **[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)**：网络搜索、知识库与文件浏览、代码解释器、笔记、频道、记忆、日历、自动化、子智能体、图像生成。
- **[工作区工具](/features/extensibility/plugin/tools)**：你自己的 Python 工具。
- 在 Open WebUI 中配置的 **[MCP 服务器](/features/extensibility/mcp)** 和 OpenAPI 工具服务器。
- **[开放终端](/features/open-terminal)**：模型或你的用户有权访问的终端服务器。

---

## 开始之前 {#before-you-start}

| 你需要 | 在哪里获取 |
| :--- | :--- |
| 一个 API 密钥 | [API 密钥](/features/authentication-access/api-keys)。管理员必须先启用全局的 **API 密钥**开关，非管理员还需要 **API 密钥**功能权限。 |
| 工具所需的权限 | 密钥以*你*的身份行事。网络搜索、代码解释器、图像生成、笔记、频道、记忆和文件上传，除了受全局管理员开关控制外，还分别受[用户权限](/features/authentication-access/rbac/permissions)限制。如果你的用户在浏览器里做不到的事，密钥同样做不到。 |
| 支持**原生**函数调用的模型 | [工具调用模式](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)。原生是默认模式，也是唯一支持内置工具和多轮循环的模式。 |
| 能力未被关闭的模型 | 内置工具遵循按模型划分的**内置工具**类别和能力设置。参见[按模型禁用内置工具](/features/extensibility/plugin/tools#disabling-builtin-tools-per-model)。 |

:::tip 反向代理已经在使用 `Authorization`？
改为在 `x-api-key` 中发送密钥，或使用 [`CUSTOM_API_KEY_HEADER`](/reference/env-configuration#custom_api_key_header) 重命名该请求头。参见 [API 密钥](/features/authentication-access/api-keys#behind-a-reverse-proxy-that-consumes-authorization)。
:::

---

## 决定整个集成方式的那一条规则 {#the-one-rule-that-decides-your-whole-integration}

`POST /api/chat/completions` 会根据你发送的字段表现出三种不同的行为。在动手写任何代码*之前*先选定你想要的行。

| 你发送的内容 | 由谁运行工具 | 答案从哪里返回 | 内置工具 |
| :--- | :--- | :--- | :--- |
| `chat_id` + `id` + `stream: true`（可加 `session_id`） | **Open WebUI**，完整的多轮原生循环 | **聊天记录**（以及 socket）。HTTP 响应体为空。 | 配合 `session_id` 时可用 |
| `params.function_calling: "legacy"` + `tool_ids` | **Open WebUI**，在模型回答前执行一轮 | **HTTP 响应体**，常规 OpenAI 结构 | 不可用 |
| 以上都不是 | **没有人**。原始的 `tool_calls` 会被交还给你 | HTTP 响应体 | 不可用 |

原生工具执行循环位于把事件流入聊天的代码路径中，因此它只在请求同时标识了一个聊天（`chat_id`）和一条助手消息（`id`）时才会运行，且仅适用于 `stream: true`。该路径会把结果写入聊天，而不是 HTTP 响应。

因此有两种实际可用的集成方式，详见下文：

- **[路径 A](#path-a-full-agentic-loop)**，完整的智能体循环。调用次数更多，但一切都能用。
- **[路径 B](#path-b-one-request-answer-in-the-body)**，一次请求进去，一个补全出来。更简单，但只有一轮工具调用，且没有内置工具。

---

## 找出你可以调用什么 {#discover-what-you-can-call}

运行一次这些命令并缓存其中的 ID。

```bash
# Models
curl -s -H "Authorization: Bearer $OWUI_KEY" $OWUI_URL/api/models | jq '.data[].id'

# Workspace tools you have access to (use .id as a tool_ids entry)
curl -s -H "Authorization: Bearer $OWUI_KEY" $OWUI_URL/api/v1/tools/ | jq '.[] | {id, name}'

# Terminal servers you have access to (use .id as terminal_id)
curl -s -H "Authorization: Bearer $OWUI_KEY" $OWUI_URL/api/v1/terminals/ | jq '.[] | {id, name, contexts}'
```

MCP 服务器以 `server:mcp:<server-id>` 形式的工具 ID 来寻址。参见[在 API 中使用 Open WebUI 工具（含 MCP）](/reference/api-endpoints#using-open-webui-tools-including-mcp-from-the-api)。

:::warning 模型的默认终端是界面默认值，而非服务端默认值
在浏览器中挑选模型时，前端会读取模型上的 `meta.terminalId` 并替你放进请求里。后端**不会**这样做。API 调用方必须显式发送 `terminal_id`，否则即使模型配置了终端，模型也拿不到任何终端工具。

你可以通过 `GET /api/v1/models/model?id=<model-id>` 读取模型配置的终端并使用 `meta.terminalId`，或者直接从 `/api/v1/terminals/` 中挑选，后者已经只列出你的用户被允许使用的终端。
:::

### 终端上下文 {#terminal-contexts}

由编排器（orchestrator）承载的终端（`server_type: orchestrator` 的连接，或任何带 `policy_id` 的连接）可以由管理员按上下文限定范围。该范围会出现在 `/api/v1/terminals/` 的 `contexts` 字段中，并决定你的请求能否使用该终端：

| `contexts.chat` | 对 API 调用方的含义 |
| :--- | :--- |
| 缺失或 `{}` | 共享终端。可用于任何请求，包括没有聊天的请求。 |
| `{"context_id": "chat_id"}` | 按聊天限定范围。请求**必须**携带已保存的 `chat_id`，并且每个聊天在服务端都有各自的运行时上下文。 |
| `false` | 在聊天中完全不可用。请求它会失败。 |

由自动化发起的请求通过 `contexts.automation` 以同样方式限定范围，只是以 `automation_id` 为键。

非编排器承载的连接没有 `contexts` 条目，始终可用。

实际做法：在选择终端之前先读 `contexts.chat`。如果它是 `false`，就换一个。如果它是 `{"context_id": "chat_id"}`，你必须使用[路径 A](#path-a-full-agentic-loop)并配合真实保存的聊天，因为[路径 B](#path-b-one-request-answer-in-the-body)从不创建聊天。

[终端上下文](/features/open-terminal/terminals/orchestration/contexts)介绍了管理员一侧的内容：该设置在哪里，以及每种模式对终端背后的工作区有什么影响。

---

## 路径 A：完整的智能体循环 {#path-a-full-agentic-loop}

四次调用。这就是 Web 界面所做的事情，只是没有浏览器。

### A1. 创建聊天 {#a1-create-the-chat}

补全请求必须依附于一个已经存在的聊天和一条助手消息。请先创建好两者：

```bash
USER_MSG_ID=$(uuidgen)
ASSISTANT_MSG_ID=$(uuidgen)
TS=$(date +%s)

CHAT_ID=$(curl -s -X POST $OWUI_URL/api/v1/chats/new \
  -H "Authorization: Bearer $OWUI_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"chat\": {
        \"title\": \"API run\",
        \"models\": [\"gpt-5.6-sol\"],
        \"history\": {
          \"currentId\": \"$ASSISTANT_MSG_ID\",
          \"messages\": {
            \"$USER_MSG_ID\": {\"id\": \"$USER_MSG_ID\", \"role\": \"user\", \"content\": \"Search the web for the latest Open WebUI release and summarise it.\", \"timestamp\": $TS, \"models\": [\"gpt-5.6-sol\"], \"childrenIds\": [\"$ASSISTANT_MSG_ID\"]},
            \"$ASSISTANT_MSG_ID\": {\"id\": \"$ASSISTANT_MSG_ID\", \"role\": \"assistant\", \"content\": \"\", \"parentId\": \"$USER_MSG_ID\", \"childrenIds\": [], \"model\": \"gpt-5.6-sol\", \"modelName\": \"gpt-5.6-sol\", \"modelIdx\": 0, \"done\": false, \"timestamp\": $((TS + 1))}
          }
        }
      }}" | jq -r '.id')
```

如果你还希望该聊天能在浏览器中正确渲染，那么消息树的确切字段（`childrenIds`、`currentId`、`parentId`）就很关键。[后端可控的 API 流程](/reference/api-flow)完整记录了该结构。

### A2. 发起补全 {#a2-fire-the-completion}

```bash
curl -s -X POST $OWUI_URL/api/chat/completions \
  -H "Authorization: Bearer $OWUI_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"gpt-5.6-sol\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Search the web for the latest Open WebUI release and summarise it.\"}],
    \"stream\": true,
    \"chat_id\": \"$CHAT_ID\",
    \"id\": \"$ASSISTANT_MSG_ID\",
    \"session_id\": \"api-$(uuidgen)\",
    \"features\": {\"web_search\": true, \"code_interpreter\": true, \"image_generation\": false, \"memory\": true},
    \"tool_ids\": [\"my_workspace_tool\", \"server:mcp:my_mcp_server\"],
    \"terminal_id\": \"open-terminal\",
    \"background_tasks\": {\"title_generation\": false, \"tags_generation\": false, \"follow_up_generation\": false}
  }"
```

响应：

```json
{"status": true, "task_ids": ["..."], "chat_id": "..."}
```

该响应确认任务已被接受并在服务端运行。

逐字段说明：

| 字段 | 存在的原因 |
| :--- | :--- |
| `stream: true` | 必需。原生工具循环只存在于流式路径上。 |
| `chat_id` + `id` | 必需。缺少两者时，服务端完全不会执行任何工具。 |
| `session_id` | **内置工具的开关。** 任意非空字符串都可以。缺少它时，内置工具不会提供给模型。它还会让请求变为异步（你得到 `task_ids`，而不是阻塞等待）。 |
| `features` | 开启四组可切换的内置工具：`web_search`、`code_interpreter`、`image_generation`、`memory`。其他内置工具（知识库、文件、笔记、频道、日历、自动化、聊天、时间、任务、子智能体）不需要开关，只要其全局设置、你的权限和模型类别允许，就会被提供。 |
| `tool_ids` | 工作区工具和 MCP 服务器。可选。 |
| `terminal_id` | 开放终端服务器。可选，且与 `session_id` 相互独立。按聊天限定范围的编排器终端还要求 `chat_id` 是已保存的聊天，而路径 A 已经满足这一点。 |
| `background_tasks` | 关闭标题、标签和后续问题生成，除非你想要这些额外的模型调用。 |

:::danger 不要发送你自己的 `tools` 数组
如果请求体中包含 `tools` 键，Open WebUI 会跳过所有服务端的工具解析，并把你的定义原样转发给模型。发送 `"tools": []` 是完全退出内置工具注入的官方方式。

在模型上设置的自定义 `tools` 参数（模型编辑器中的**添加自定义参数**）则表现不同。Open WebUI 仍会解析自己的工具，并连同模型的自定义工具一起发送。
:::

### A3. 等待完成 {#a3-wait-for-it-to-finish}

```bash
while [ "$(curl -s -H "Authorization: Bearer $OWUI_KEY" \
  "$OWUI_URL/api/tasks/chat/$CHAT_ID" | jq '.task_ids | length')" != "0" ]; do
  sleep 2
done
```

### A4. 读取答案 {#a4-read-the-answer}

```bash
curl -s -H "Authorization: Bearer $OWUI_KEY" "$OWUI_URL/api/v1/chats/$CHAT_ID" \
  | jq -r ".chat.history.messages[\"$ASSISTANT_MSG_ID\"].content"
```

`content` 是纯文本。同一条消息还携带 `output`（结构化条目列表：推理块、工具调用、代码解释器运行）、`usage` 和 `sources`，如果你想要比正文更多的内容。

### A5. 如果你不想保存这个聊天 {#a5-if-you-did-not-want-the-chat-saved}

路径 A 会写入一个真实的聊天。若只需要“API 请求与响应”，请在完成后删除该聊天：

```bash
curl -s -X DELETE -H "Authorization: Bearer $OWUI_KEY" "$OWUI_URL/api/v1/chats/$CHAT_ID"
```

:::info `temporary:` 替代方案
`chat_id` 为 `temporary:<session_id>` 时同样会运行完整循环且完全不持久化任何内容。`<session_id>` 是你自己已登录客户端的 socket.io 会话 ID，同时也作为 `session_id` 发送；其他任何 `temporary:` ID 都会以 `404` 拒绝。输出只会通过该 socket 送出，因此这需要真实的 socket.io 客户端。对于纯 HTTP 场景，请采用创建再删除的方式。
:::

### 阻塞式变体（不带 `session_id`） {#blocking-variant-no-session_id}

去掉 `session_id` 后请求将不再异步：HTTP 调用会阻塞直到整个工具循环结束，然后返回 `null`。你仍然从聊天中读取答案，但可以跳过 A3 中的轮询。代价是这种模式下**不可用内置工具**。当 `tool_ids`、`terminal_id` 和 MCP 就足够时使用它。

---

## 路径 B：一次请求，答案在响应体中 {#path-b-one-request-answer-in-the-body}

如果你想要单次 HTTP 请求返回一个常规的 OpenAI 补全，并且工具结果已经融合其中，请把该请求切换到旧版函数调用：

```bash
curl -s -X POST $OWUI_URL/api/chat/completions \
  -H "Authorization: Bearer $OWUI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.6-sol",
    "messages": [{"role": "user", "content": "What does the my_workspace_tool say about order 4711?"}],
    "stream": false,
    "params": {"function_calling": "legacy"},
    "tool_ids": ["my_workspace_tool", "server:mcp:my_mcp_server"],
    "terminal_id": "open-terminal"
  }'
```

发生的过程：Open WebUI 询问任务模型要调用哪些工具，使用你的权限在服务端执行它们，把结果作为上下文注入提示词，然后运行真正的补全。不会持久化任何内容，不需要聊天，响应就是你的 HTTP 客户端所期望的常规对象，另外还带有一个顶层 `sources` 数组，其中保存每个工具的结果。

把 `"stream"` 设为 `true` 可以得到同样内容的 SSE 版本。工具轮发生在第一个 token 之前，因此流会在工具执行完之后才开始。`sources` 负载会作为第一个 `data:` 帧到达，先于模型的增量输出。

为换取简洁性，需要接受以下限制：

- **只有一轮工具调用。** 模型无法查看结果后再决定调用别的工具。
- **没有内置工具。** 没有网络搜索，没有代码解释器，没有知识库浏览，也没有终端驱动的智能体工作。
- **没有按聊天限定范围的终端。** 这种模式的请求不携带 `chat_id`，因此配置了 `contexts.chat.context_id = "chat_id"` 的编排器终端无法使用。共享终端可以正常使用。
- 旧版模式**不受支持**，并且依赖一个能稳定输出 JSON 的任务模型。参见[工具调用模式](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)。

---

## 按模式对照实际返回值 {#what-you-actually-get-back-by-mode}

| 请求 | HTTP 响应 |
| :--- | :--- |
| 带 `session_id` 的路径 A | `{"status": true, "task_ids": [...], "chat_id": "..."}`，立即返回 |
| 不带 `session_id` 的路径 A | `null`，在完整循环结束后返回 |
| 路径 B，`stream: false` | 常规聊天补全对象，外加 `sources` |
| 路径 B，`stream: true` | SSE：一个 `sources` 帧，然后是标准的 OpenAI 增量，最后是 `[DONE]` |
| 原生模式但没有 `chat_id`/`id` | 包含**未执行**的 `tool_calls` 的标准 OpenAI 响应 |

---

## 可复用脚本 {#reusable-script}

开箱即用的 Python 脚本。设置顶部的四个常量，然后调用 `run()`。

```python
"""Run a prompt through Open WebUI with server-side tool calling."""

import json
import time
import uuid

import requests

OWUI_URL = "http://localhost:3000"
OWUI_KEY = "sk-..."
MODEL = "gpt-5.6-sol"
DELETE_CHAT_WHEN_DONE = True  # False keeps the conversation in the user's chat list


def _headers():
    return {"Authorization": f"Bearer {OWUI_KEY}", "Content-Type": "application/json"}


def run(
    prompt,
    tool_ids=None,
    terminal_id=None,
    features=None,
    system=None,
    builtin_tools=True,
    timeout=600,
):
    """Returns the finished assistant message as a dict (content, output, usage, sources)."""
    user_msg_id, assistant_msg_id = str(uuid.uuid4()), str(uuid.uuid4())
    now = int(time.time())

    chat = requests.post(
        f"{OWUI_URL}/api/v1/chats/new",
        headers=_headers(),
        json={
            "chat": {
                "title": "API run",
                "models": [MODEL],
                "history": {
                    "currentId": assistant_msg_id,
                    "messages": {
                        user_msg_id: {
                            "id": user_msg_id,
                            "role": "user",
                            "content": prompt,
                            "timestamp": now,
                            "models": [MODEL],
                            "childrenIds": [assistant_msg_id],
                        },
                        assistant_msg_id: {
                            "id": assistant_msg_id,
                            "role": "assistant",
                            "content": "",
                            "parentId": user_msg_id,
                            "childrenIds": [],
                            "model": MODEL,
                            "modelName": MODEL,
                            "modelIdx": 0,
                            "done": False,
                            "timestamp": now + 1,
                        },
                    },
                },
            }
        },
    )
    chat.raise_for_status()
    chat_id = chat.json()["id"]

    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]

    body = {
        "model": MODEL,
        "messages": messages,
        "stream": True,  # required, the native tool loop is streaming-only
        "chat_id": chat_id,
        "id": assistant_msg_id,
        "background_tasks": {
            "title_generation": False,
            "tags_generation": False,
            "follow_up_generation": False,
        },
        "features": features
        or {
            "web_search": True,
            "code_interpreter": True,
            "image_generation": False,
            "memory": False,
        },
    }
    if builtin_tools:
        body["session_id"] = f"api-{uuid.uuid4()}"  # unlocks the built-in tools
    if tool_ids:
        body["tool_ids"] = tool_ids
    if terminal_id:
        body["terminal_id"] = terminal_id

    started = requests.post(
        f"{OWUI_URL}/api/chat/completions", headers=_headers(), json=body, timeout=timeout
    )
    started.raise_for_status()

    deadline = time.time() + timeout
    while time.time() < deadline:
        tasks = requests.get(
            f"{OWUI_URL}/api/tasks/chat/{chat_id}", headers=_headers()
        ).json()
        if not tasks.get("task_ids"):
            break
        time.sleep(2)
    else:
        raise TimeoutError(f"chat {chat_id} did not finish within {timeout}s")

    final = requests.get(f"{OWUI_URL}/api/v1/chats/{chat_id}", headers=_headers())
    final.raise_for_status()
    message = final.json()["chat"]["history"]["messages"][assistant_msg_id]

    if DELETE_CHAT_WHEN_DONE:
        requests.delete(f"{OWUI_URL}/api/v1/chats/{chat_id}", headers=_headers())

    return message


def run_single_request(prompt, tool_ids=None, terminal_id=None, stream=False):
    """Path B: one call, completion in the body. One tool round, no built-in tools."""
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": stream,
        "params": {"function_calling": "legacy"},
    }
    if tool_ids:
        body["tool_ids"] = tool_ids
    if terminal_id:
        body["terminal_id"] = terminal_id

    if not stream:
        response = requests.post(
            f"{OWUI_URL}/api/chat/completions", headers=_headers(), json=body
        )
        response.raise_for_status()
        return response.json()

    with requests.post(
        f"{OWUI_URL}/api/chat/completions", headers=_headers(), json=body, stream=True
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                payload = line[6:]
                if payload == "[DONE]":
                    return
                yield json.loads(payload)


if __name__ == "__main__":
    result = run(
        "Search the web for the newest Open WebUI release, then write a three-bullet summary.",
        terminal_id=None,
        tool_ids=None,
    )
    print(result["content"])
```

如何改造它：

- **不同的工具**：传入 `tool_ids=["my_tool", "server:mcp:my_server"]`。
- **终端工作**：传入 `terminal_id="<id from /api/v1/terminals/>"`。
- **保留对话**：设置 `DELETE_CHAT_WHEN_DONE = False`。此后它会像一次浏览器对话一样出现在用户的聊天列表中。
- **多轮对话**：复用 `chat_id`，向消息树中新增一条用户消息和一个助手占位消息，并发送完整的 `messages` 历史。参见[后端可控的 API 流程](/reference/api-flow#send-additional-messages-to-an-existing-chat)。
- **不需要内置工具**：`builtin_tools=False` 会让请求变为阻塞式，并跳过轮询循环。

---

## 疑难问题 {#gotchas}

| 现象 | 原因 | 解决办法 |
| :--- | :--- | :--- |
| 响应中包含需要你的脚本执行的 `tool_calls` | 原生模式缺少 `chat_id` + `id` | 改用路径 A，或把该请求切换到旧版模式 |
| 完全没有调用任何工具，且 `stream` 为 `false` | 原生循环仅在流式路径上运行 | 发送 `stream: true` |
| 发送了 `stream: true` 却没有任何流式输出 | 工作区模型的**流式聊天响应**参数覆盖了请求 | 在模型上清除该设置，或接受模型的设置 |
| 网络搜索、代码解释器、记忆或图像生成始终不被提供 | 缺少 `session_id`、缺少 `features` 开关、缺少用户权限、被全局关闭，或模型的**内置工具**类别被关闭 | 这五项必须全部对齐，请按此顺序检查 |
| `execute_code` 返回 “WebSocket connection required” | 代码解释器引擎是 `pyodide`，它在浏览器中运行 | 在 **设置 > 管理 > 代码执行** 中把引擎切换为 **Jupyter**，或从 `features` 中去掉 `code_interpreter` |
| 文件工具（`view_file`、`grep_chat_files` 等）缺失 | 它们需要请求体中有 `files`、有 `session_id`、开启模型的**文件上传**能力，并且**预加载文件**为关闭。API 请求会把预加载文件视为开启，除非模型将其保存为关闭 | 参见[提示词缓存与上下文优化](/features/chat-conversations/prompt-caching) |
| `503 Terminal unavailable` | 终端服务器不可达、已被禁用，或你的用户没有访问授权 | 确认该 ID 出现在该密钥的 `GET /api/v1/terminals/` 结果中 |
| `503`，聊天中终端不可用 | 该终端的 `contexts.chat` 为 `false`，说明管理员已把它从聊天中移除 | 换一个 `contexts.chat` 不为 `false` 的终端 |
| `503`，终端需要已保存的聊天上下文 | 该终端按 `contexts.chat.context_id = "chat_id"` 限定范围，而请求没有已保存的 `chat_id` | 使用路径 A 并配合已保存的聊天，或换一个共享终端 |
| MCP 工具连接失败 | 该 OAuth 受保护的 MCP 服务器尚未被 API 密钥所属用户授权 | 以该用户身份在浏览器中完成一次 OAuth 流程 |
| 聊天已创建但在界面中始终为空 | 消息树损坏 | `currentId` 使用驼峰命名，每条消息都需要 `parentId` 和 `childrenIds`。参见[后端可控的 API 流程](/reference/api-flow) |

---

## 另请参阅 {#see-also}

- [API 端点](/reference/api-endpoints)：完整的端点列表、Anthropic Messages API、RAG 与文件上传。
- [后端可控的 API 流程](/reference/api-flow)：路径 A 中使用的聊天与消息树结构。
- [工具](/features/extensibility/plugin/tools)：内置工具参考、原生与旧版对比、按模型的启用控制。
- [模型上下文协议 (MCP)](/features/extensibility/mcp)：添加 MCP 服务器。
- [开放终端](/features/open-terminal)：配置终端服务器。
- [API 密钥](/features/authentication-access/api-keys)与[权限](/features/authentication-access/rbac/permissions)。