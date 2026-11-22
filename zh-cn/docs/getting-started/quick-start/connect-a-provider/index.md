---
sidebar_position: 0
title: "连接本地与云端模型"
sidebar_label: "连接提供商"
description: "将本地模型服务器和托管 API 连接到 Open WebUI，在同一个界面中切换模型并比较回复。"
---

# 连接本地与云端模型 {#connect-a-provider}

将本地模型服务器与云端 API 连接到同一个 Open WebUI 实例。为每个提供商添加一条连接，然后选择在对话中使用哪个模型。

Open WebUI 支持多种连接协议，包括 **Ollama**、**兼容 OpenAI 的 API** 与 **Open Responses**。任何实现这些协议的云端 API 或本地服务器都可以开箱即用。你只需填写 URL 和 API 密钥，你的模型就会出现在下拉列表中。

---

## 工作原理 {#how-it-works}

```mermaid
flowchart LR
    A["Open WebUI<br/>(frontend)"]
    B["Provider API<br/>(cloud / local)"]
    C["Model<br/>(LLM / VLM)"]

    A -- HTTP --> B
    B -- Inference --> C
    C -- Tokens --> B
    B -- Stream --> A
```

![管理设置中的提供商连接](/images/admin/admin-connections.png)

1. **你在 Open WebUI 中输入消息**
2. Open WebUI 将消息发送到你的提供商 API 端点
3. 提供商在所选模型上执行推理
4. token **实时流式返回**到 Open WebUI
5. 你在聊天界面中看到回复

:::tip
添加提供商通常只需要在 **设置 → 连接**（管理员区域） 中填写 URL 和 API 密钥。对于大多数提供商，Open WebUI 都能自动发现可用模型。
:::

---

## 同时使用本地与云端模型 {#use-local-and-cloud-models-together}

你需要：一个正在运行的 Open WebUI 实例、管理员权限、一个可访问的本地模型服务器，以及你所选择的托管提供商的 API 密钥。

1. [连接 Ollama](/getting-started/quick-start/connect-a-provider/starting-with-ollama)，并确认已下载的本地模型出现在模型选择器中。
2. 按照 [OpenAI](/getting-started/quick-start/connect-a-provider/starting-with-openai)、[Anthropic](/getting-started/quick-start/connect-a-provider/starting-with-anthropic) 或[兼容 OpenAI 的提供商](/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible) 指南添加一条托管连接。
3. 开始一段对话，选择本地模型，发送一条简短的测试消息。然后另起一段对话选择托管模型，确认它也能正常回复。
4. 若要把同一条提示词同时发送给两个模型，请使用[多模型对话](/features/chat-conversations/chat-features/multi-model-chats)。

所选的端点决定了推理发生的位置。选择云端模型会把提示词和附带上下文发送到该提供商；比较模型时，提示词会分别发送到每个选中的端点。本地推理并不会让单独配置的云端工具、文档提取或嵌入服务变成本地执行。对于敏感内容，请参阅[聊天数据隐私与加密](/security/chat-data-privacy-and-encryption)来选择合适的提供商。

## 选择合适的连接设置 {#choose-the-right-connection-settings}

大多数提供商只需要 URL 和 API 密钥。有些还需要在连接对话框中选择一项设置，让 Open WebUI 识别连接另一端的服务。在 **Admin Settings > Connections** 中，通过 **Manage Ollama API Connections** 添加 Ollama 服务器，其他服务则通过 **Manage OpenAI API Connections** 添加。根据下表配置相应的提供商。

![已填写 URL 和 API 密钥的添加连接对话框](/images/getting-started/quick-start/connection-dialog.png)

| 要连接的服务 | 添加位置 | 要更改的设置 |
|---|---|---|
| **Ollama** | Ollama 连接 | 只需 URL。Open WebUI 会自动识别 Ollama。参见 [Ollama 入门](/getting-started/quick-start/connect-a-provider/starting-with-ollama)。 |
| **OpenAI、Anthropic、Gemini、Mistral、Groq、OpenRouter、xAI、vLLM 及其他使用 OpenAI 格式的服务器** | OpenAI 连接 | URL 和 API 密钥。将 **Provider** 保持为 **Default**。 |
| **DeepSeek（托管 API）** | OpenAI 连接 | 填写 URL 和 API 密钥，再选择 **Advanced > Provider > llama.cpp**。DeepSeek 的思考模式要求在每轮工具调用时把之前的推理发回服务器，llama.cpp 选项会发送这些内容。 |
| **Azure OpenAI** | OpenAI 连接 | 选择 **Provider > Azure OpenAI**，设置 **API Version**，并在 **Model IDs** 下填入部署名称。Open WebUI 识别到 Azure 格式的 URL 时也会自动切换到 Azure 模式。 |
| **llama.cpp 服务器** | OpenAI 连接 | 选择 **Provider > llama.cpp**，即可在 Open WebUI 中管理模型。参见 [llama.cpp 入门](/getting-started/quick-start/connect-a-provider/starting-with-llama-cpp)。 |
| **LM Studio** | OpenAI 连接 | 选择 **Provider > LM Studio**，即可在 Open WebUI 中管理模型。 |
| **LiteLLM 代理** | OpenAI 连接 | 选择 **Provider > LiteLLM**，即可把发往 Open WebUI 自身 Anthropic Messages 端点的请求直接转给 LiteLLM。 |
| **提供 Responses API 的提供商** | OpenAI 连接 | 选择 **API Type > Responses**。参见 [Open Responses](/getting-started/quick-start/connect-a-provider/starting-with-open-responses)。 |

**Provider** 设置指定 Open WebUI 发送请求时使用的格式。llama.cpp 选项因 llama.cpp 首先引入该格式而得名。支持该格式的任何服务器都可以使用此选项，包括 DeepSeek 的托管 API。**Default** 发送标准 OpenAI 格式，任何兼容 OpenAI 的服务器都能接受。[Provider 设置](/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible#the-provider-setting)列出各选项启用的功能。[如何发回推理](/features/chat-conversations/chat-features/reasoning-models#how-reasoning-is-sent-back)说明了各提供商接收推理内容时使用的字段。

要修改此设置，请打开 **Admin Settings > Connections**，点击连接旁的齿轮图标（新建时点击 **+**），展开 **Advanced**，在 **Provider** 中选择相应选项。保存对话框和连接列表。此下拉菜单只在 OpenAI 连接中出现。

![连接的 Advanced 区域，其中 Provider 设为 llama.cpp](/images/getting-started/quick-start/connection-provider-setting.png)

对话框中的其他设置：

| 设置 | 用途 |
|---|---|
| **Connection Type** | 将连接标为 **Local** 或 **External**。模型选择器用此标签进行 Local 和 External 筛选。 |
| **Auth** | **Bearer** 发送你的 API 密钥。**None** 调用服务器时不发送密钥。**Session**、**OAuth** 和 **Entra ID** 转发已登录用户的凭据或 Azure 身份。 |
| **API Type** | 默认使用 **Chat Completions**。选择 **Responses** 可将连接切换到 Responses API。 |
| **Forward cookies** | 将发往 Open WebUI 的请求中的 Cookie 转发给此服务器。 |
| **Headers** | JSON 格式的额外请求头。 |
| **Prefix ID** | 为此连接的每个模型的 ID 和显示名称添加前缀和一个点，例如 `work.gpt-5.6`，从而区分两个连接提供的同一模型。在 **Settings > Models**（管理员区域）中为该模型保存的名称会替换带前缀的名称。 |
| **Model IDs** | 要显示的模型列表。留空时显示服务器上报的所有模型。 |

---

## 云端提供商 {#cloud-providers}

需要账户和 API 密钥的托管 API。无需自备硬件。

| 提供商 | 模型 | 指南 |
|----------|--------|-------|
| **OpenAI** | GPT-5.6 Sol、GPT-5.6 Terra、GPT-5.6 Luna | [从 OpenAI 开始 →](/getting-started/quick-start/connect-a-provider/starting-with-openai) |
| **Anthropic** | Claude Opus 5、Sonnet 5、Haiku 4.5 | [从 Anthropic 开始 →](/getting-started/quick-start/connect-a-provider/starting-with-anthropic) |
| **兼容 OpenAI** | DeepSeek、Mistral、Groq、OpenRouter、Vercel AI Gateway、Amazon Bedrock、Azure 等 | [兼容 OpenAI 的提供商 →](/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible) |

---

## 本地服务器 {#local-servers}

在你自己的硬件上运行已下载的模型。认证方式取决于本地服务器的配置方式。

| 服务器 | 说明 | 指南 |
|--------|-------------|-------|
| **Ollama** | 在本地运行和管理已下载的模型 | [从 Ollama 开始 →](/getting-started/quick-start/connect-a-provider/starting-with-ollama) |
| **llama.cpp** | 通过兼容 OpenAI 的 API 高效进行 GGUF 模型推理 | [从 llama.cpp 开始 →](/getting-started/quick-start/connect-a-provider/starting-with-llama-cpp) |
| **vLLM** | 面向生产负载的高吞吐推理引擎 | [从 vLLM 开始 →](/getting-started/quick-start/connect-a-provider/starting-with-vllm) |

更多本地服务器（LM Studio、LocalAI、Docker Model Runner、Lemonade）可参见[兼容 OpenAI 的提供商](/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible#local-servers)指南。

---

## 其他连接方式 {#other-connection-methods}

| 功能 | 说明 | 指南 |
|---------|-------------|-------|
| **Open Responses** | 通过 Open Responses 规范连接提供商 | [从 Open Responses 开始 →](/getting-started/quick-start/connect-a-provider/starting-with-open-responses) |
| **Functions** | 通过自定义 pipe functions 将任意后端接入 Open WebUI | [从 Functions 开始 →](/getting-started/quick-start/connect-a-provider/starting-with-functions) |

---

## 在找 Agent？ {#looking-for-agents}

如果你想连接的是一个自主 AI Agent（具备终端访问、文件操作、网页搜索等能力），而不是普通的模型提供商，请参阅[**连接 Agent**](/getting-started/quick-start/connect-an-agent)。
