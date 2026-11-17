---
sidebar_position: 750
title: "提示词缓存（KV Cache）优化"
---

# 提示词缓存（KV Cache）优化 {#prompt-caching-kv-cache-optimization}

大多数托管的 LLM 提供方都会缓存请求**前缀**的 KV 状态。当两个请求共享完全相同的前导 token 序列时，提供方会直接从缓存中提供共享部分，而不必重新计算，这既**更便宜也更快**。如果你想通过尽可能多的缓存命中来省钱，这一页就是为你准备的。

:::tip 适合谁阅读
任何希望在支持提示词/前缀缓存的提供方（Anthropic、OpenAI、Google Gemini、DeepSeek 以及 OpenAI 兼容网关）上最大化缓存命中（并最小化支出与延迟）的人。
:::

:::warning 开始之前
你的模型（或提供该模型的提供方/网关）必须**支持提示词缓存**，并且它实际上已为你的请求**启用**。

- **完全自动**：相同的前导 token 会被缓存并复用，无需选择加入，也无需额外付费即可启用（例如 OpenAI、Gemini、DeepSeek）。通常称为**隐式**或**自动前缀缓存**。
- **按请求选择加入**：只有当请求明确提出要求时提供方才缓存。**Anthropic** 同时支持**显式**缓存（缓存断点）和它所谓的**隐式**缓存，但两种情况下都必须在**每次请求**中发送缓存指令，而且**缓存写入会计费**，因此绝不会悄悄开启。你必须发送该选择加入指令，缓存才会生效。

如果你的模型或端点根本不缓存提示词，下面的任何设置都不会改变你的成本或延迟。
:::

## 提示词缓存如何工作（一分钟版） {#how-prompt-caching-works-in-one-minute}

- 提供方从请求的**开头**开始往后缓存。
- 缓存命中要求前缀与之前的某个请求**完全相同**。
- 一旦请求出现差异，缓存就会**从该处到末尾**失效。

因此，核心法则是：

> **保持每个请求开头部分稳定，只在末尾追加新内容。**

聊天对话天然就是在末尾追加新轮次，这本身就对缓存友好，**除非有东西在每一轮都重写请求中更早的部分**。消除这些重写正是本指南的主题。

## 在 Open WebUI 中什么会破坏缓存 {#what-breaks-the-cache-in-open-webui}

Open WebUI 可以在每一轮动态插入内容。任何改变**系统消息**或**更早的用户消息**的行为都会让缓存前缀失效。常见的原因有：

| 来源 | 它的作用 | 对缓存的影响 |
|---|---|---|
| **Preload files（RAG）** | 检索文件/知识库分块，并在每一轮把它们（连同 RAG 模板）注入到最新消息中 | 高：注入的内容每次查询都会变化 |
| **Citations** | 在 Native 函数调用下，来源标记会附加到产生它们的工具结果上，并随该结果一同保存。在 Legacy 下，来源会连同 RAG 模板在每一轮加入你的消息（通过 `RAG_SYSTEM_CONTEXT` 加入系统消息） | Native 下无影响，参见下方说明；Legacy 下影响高 |
| **Memory** | 在 Native 函数调用下，召回的记忆会作为隐藏的 `recall_memories` 工具结果在每条回复中于你的消息之后加入一次；否则它们会在每一轮被追加到你的消息上 | Native 下无影响；Legacy 下影响高：记忆一变就会变化 |
| **"Using Entire Document"** | 把整个文件注入每一条消息 | 极高：但它是 **Preload files** 的一个子模式，只在 Preload files 开启时才会触发 |
| **动态语音模式提示** | 在系统消息前附加一条简短的语音指令 | 低：语音模式开启期间保持不变 |
| **附件元数据块** | 在该消息中以元数据（id 和名称）的形式列出所附带的文件、知识库、笔记和聊天 | 低：只要附件不变就保持稳定 |
| **已附加的知识库列表** | 在 Native 函数调用下，附着于模型或文件夹的知识会在每条回复中作为隐藏的 `list_attached_knowledge` 工具结果于你的消息之后列出一次。没有可列内容时会跳过 | 无影响：随回复保存并原样重放 |
| **Open Terminal `AGENTS.md`** | 在每一轮读取终端用户主目录下的 `AGENTS.md`，并把它作为一条用户消息加在第一条用户消息之前 | 只要该文件发生变化（例如模型在对话中途编辑了它），从第一条用户消息起的所有内容都会失效。系统消息与工具仍保持缓存 |
| **Open Terminal 技能** | 把终端技能加入技能列表；在 Native 函数调用下，它是每条回复中一次的隐藏 `list_available_skills` 工具结果（没有技能时跳过）。在 Legacy 下，只有你选中的技能会被写入系统消息 | 只在添加或移除技能的那一轮改变请求的尾部。工具列表仅在第一个技能出现或最后一个技能消失时才会改变，因为只要列表中至少有一个技能，技能工具就会提供 |
| **Open Terminal 工作目录** | 在每一轮把终端当前的工作目录写入命令工具的说明中 | 工作目录一变，工具列表就会变化。请关闭该连接的[工作目录上下文](/features/open-terminal/setup/connecting#working-directory-context)以保持稳定 |
| **Open Terminal 用户 shell 工具** | 默认只在你的 shell 打开期间加入对应你自身 shell 的那两个工具 | 打开或关闭 shell 时工具列表会变化。请把连接的[用户 Shell 工具](/features/open-terminal/setup/connecting#user-shell-tools)设为 `Always Include` 以保持稳定 |
| **[Tool Search](/features/extensibility/plugin/tools#tool-search)** | 在系统消息末尾添加固定的 `<available_tools>` 指令，把大型工具排除在工具列表之外，并把 `search_tools` 与 `call_tool` 加入其中。模型通过一次工具调用加载某个工具的完整定义，并通过 `call_tool` 运行它 | 低：该指令与工具列表仅在启用的工具集合发生变化时才会改变。加载某个工具不会改变工具列表 |

:::info
附件元数据块有意只包含**元数据**（不含文件内容），因此它在各轮之间保持稳定，不会明显损害缓存。上表中真正需要留意的是那些会注入内容的行。
:::

:::info Native 函数调用让引用、记忆、技能与知识库列表远离缓存前缀
当 **Citations** 能力开启且某个工具返回来源（`query_chat_files`、`query_knowledge_files`、`view_file`、`view_knowledge_file`、`fetch_url`）时，来源标记会附加到该工具结果上并随之保存，因此后续请求会重放相同的文本。召回的记忆、技能列表和已附加的知识库列表，会在每条回复中于用户消息之后以隐藏工具结果（`recall_memories`、`list_available_skills`、`list_attached_knowledge`）的形式到达。内容为空的列表或召回会被跳过，被继续的回复同样会被跳过，因为其已保存的输出中已经包含它们。它们保存在回复的输出中，并在后续轮次原样重放。请求中更早的部分不会被重写。

这适用于 Web 界面中使用 Native 函数调用且模型的 **Builtin Tools** 能力开启的聊天。技能列表还需要 **Skills** 分类，已附加的知识库列表则需要 **Knowledge Base** 分类。在 Legacy 函数调用下、在没有 Web 界面会话的 API 请求中，以及在 Builtin Tools 关闭时，记忆会在每一轮被追加到你的消息上，并且没有技能列表或知识库列表。

读取最后一条消息的自定义 pipe，在召回记忆、附加知识或用户拥有技能时，可能在那里看到一条工具消息。过滤器在这些结果加入之前运行：`inlet` 永远看不到它们，而 `request` 从一条回复的第二次调用开始才能看到。
:::

### 为什么注入放在最新的用户消息中 {#why-the-injection-goes-into-the-latest-user-message}

这种放置方式是有意为之的，在把它当成需要修复的缺陷之前，值得先理解它。

自动检索的设计前提是：模型主要关注它正在回答的那条消息。非常小的本地模型和较老的模型在实践中确实如此：放在对话更早位置的上下文会被忽略，或者因为上下文窗口太短而容不下全部历史。把检索到的上下文放在被回答消息之外的任何位置，都意味着这些模型无法稳定地看到它——这正是"检索生效"与"检索默默什么都没做"之间的差别。

破坏缓存前缀是这项保证的代价。当替代方案是模型完全无法使用上下文时，这个代价值得付出。而一旦你的模型足够大、上下文足够长，能够关注对话中更靠前的内容——每一个旗舰模型以及当前大多数本地模型都是如此——这个代价就不再值得付出。

因此，这两个能力是在两种设计之间做选择，而不是一个特性与一个缺陷：

| | 开启上下文注入 | 关闭上下文注入 |
| :--- | :--- | :--- |
| **检索** | 强制执行，在模型运行之前 | 按需执行，由模型调用工具 |
| **放置位置** | 每一轮都重写进最新消息 | 作为工具结果追加到末尾 |
| **前缀缓存** | 每轮失效 | 得以保留 |
| **适用对象** | 小型且上下文较短的模型 | 其他所有情况 |

关闭 Preload files 并不是规避上述成本的权宜之计，而是选择了另一种设计——本页所讲的那一种。

## 对缓存最优的配置 {#the-cache-optimal-setup}

目标是拥有一个**静态前缀**（系统提示 + 工具），并以**仅追加**的方式增长（用户轮次与工具结果），同时用**按需检索**取代自动注入。

### 1. 使用静态系统提示 {#1-use-a-static-system-prompt}

在模型上配置一个固定的系统提示，并避免任何每轮重新生成它的机制。这是最值得缓存的单一区块，请把你的指令（包括如何引用，见下文）一次性写在这里。

### 2. 关闭 Preload files（这正是启用文件工具的开关） {#2-turn-preload-files-off-this-is-what-switches-the-file-tools-on}

在模型上禁用 **Preload files** 能力（在 Native 函数调用下它默认关闭），同时保持 **File Upload** 启用。所附带的文件、知识库、笔记和被引用的聊天仍会**以稳定的元数据形式呈现给模型**，放在携带它们的那条消息的 `<attached_files>` 块中，但它们的**内容不再被自动检索或注入**。参见 [Preload files 与 Builtin Tools 的对比](/features/chat-conversations/rag#preload-files-vs-builtin-tools)。

关闭 Preload files 还会让内置的文件工具变得可用，模型可以自行读取和搜索聊天附件：

| 工具 | 模型用它做什么 |
|---|---|
| `list_chat_files` | 查看附带了哪些文件，包括 id、文件名、内容类型和大小 |
| `query_chat_files` | 在附件中做语义搜索，或按 id 检索某个文件 |
| `grep_chat_files` | 精确文本搜索，返回匹配行及其文件 id 和行号 |
| `view_file` | 按字符偏移量或行范围读取一段内容 |

开启 Preload files 会移除这些工具，因为内容已经在对话之中了。

此时检索变为**按需进行**：由模型决定取什么并调用工具。工具结果被追加到对话的**末尾**，因此永远不会重写缓存前缀。

:::info 聊天附带的知识库与笔记不会成为孤儿
关闭 Preload files 还会把聊天附带的任何知识库或笔记重新路由到知识工具路径，使它们仍可通过 `query_knowledge_files` 等工具检索。随后这些知识工具将[仅检索已附加的知识](/features/workspace/knowledge#scoped-access-keeps-things-organized)。

用 `#` 附带或拖入输入框的**聊天文件夹**只能通过 Preload files 抵达模型，而后者是从该文件夹附带的知识中检索的。关闭 Preload files 后，请直接用 `#` 附带该文件夹的知识库和文件，或者在文件夹内部开启聊天，此时其中的知识会经由知识工具处理。
:::

:::info "Using Entire Document" 是 Preload files 的一个子模式
按文件/按知识库的 **Using Entire Document** 模式会把完整文档注入每一条消息，是所有因素中最伤缓存的一个。但它运行在 **Preload files 内部**，因此关闭 Preload files（本步骤）**就已经禁用了它**——在 Preload files 关闭时启用 Using Entire Document 不会有任何作用。请不要把重新开启 Preload files + Using Entire Document 当作检索的变通手段，而应改用按需工具。参见[检索模式](/features/workspace/knowledge#retrieval-modes)。
:::

### 3. 关闭 Citations，并把引用规则移入系统提示 {#3-turn-citations-off-and-move-citation-rules-into-the-system-prompt}

在 Native 函数调用下，**Citations** 不会破坏缓存。关闭它会从工具结果中去掉来源标记（请求更小），界面中回复下方渲染的来源标签也会消失；模型仍然会收到工具结果本身。

若想在回答文本中带上引用但不要标记，请**在系统提示中加入静态的引用说明**。这些说明要针对工具实际返回的内容来写，即文件名或 URL，而不是编号：

- 引用文件和知识库中的段落时，使用工具结果携带的 `source` 文件名，例如 `(handbook.pdf)`。
- 引用网页时，使用基于 `link` 字段构造的 markdown 链接，例如 `[example.com](https://example.com/...)`。

由于该说明位于（被缓存的）系统提示中，你可以获得引用而**无需**每轮注入。

:::warning 不要在这里要求编号式引用
编号式 `[1]`、`[2]` 引用只有在 **Citations** 开启时才有效，因为这些编号来自 Open WebUI 添加到工具结果上的 `<source>` 标记。没有任何内置工具会返回它：文件与知识工具返回 `content`、一个 `source` 文件名和 `file_id`，`search_web` 返回 `title`、`link` 和 `snippet`。在 Citations 关闭时要求 `[1]` 风格的引用，系统提示等于没有给模型任何可编号的对象，模型就会自己编造编号。
:::

:::info `search_web` 返回的是搜索结果，而不是页面正文
`search_web` 为每条命中结果给模型一个标题、一个链接和一段摘要，也就是搜索引擎返回的内容。它不会抓取这些页面。当模型需要了解页面的实际内容时，应对链接调用 `fetch_url`。引用一个只看过摘要的页面，等于在引用搜索引擎，因此请要求模型在引用具体内容之前先抓取页面。
:::

### 4. 让检索保持智能体化 {#4-keep-retrieval-agentic}

在模型上启用 **Builtin Tools**，并保持所需的分类处于开启状态。聊天能携带的每一种资源类型都有对应的内置工具：

| 资源 | 工具 | 分类 |
|---|---|---|
| 聊天附带的文件 | `list_chat_files`、`query_chat_files`、`grep_chat_files`、`view_file`、`display_file` | **Files** |
| 知识库，包括聊天所在文件夹的知识 | `query_knowledge_files`、`search_knowledge_files`、`grep_knowledge_files`、`view_knowledge_file`、`display_file`，以及在模型未附加知识时用于发现的工具 | **Knowledge Base** |
| 笔记 | `search_notes`、`view_note` | **Notes** |
| 用户的聊天 | `search_chats`、`view_chat` | **Chat History** |

这需要 **Native** 函数调用。内置工具是原生模式的功能，不会为设为 Legacy 的模型注入。

四类之中，**Files** 分类的条件最为严格。以下五条必须全部满足，否则这些工具会悄无声息地缺席：

1. 模型上启用了 **Files** 内置分类（默认开启）。
2. 模型的 **File Upload** 能力已开启。
3. 模型的 **Preload files** 能力处于**关闭**状态。
4. 该聊天确实至少附带了一个文件。
5. 用户拥有 `chat.file_upload` 权限（管理员始终满足）。

每个工具在每次调用时都会在服务端重新解析资源并做访问检查，因此除非模型主动请求，否则不会有任何文件内容进入上下文；用户已无权打开的附件会被跳过而不是被读取。参见[内置工具参考](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)。

:::tip 让工具列表本身保持稳定
工具定义与系统提示一样位于缓存前缀中，因此在对话中途切换分类、附带技能或启用 Web 搜索，都会从该处起让缓存失效。请按模型而非按轮次来决定工具集合。请注意，文件工具会在聊天中附带第一个文件的那一刻出现，这属于该对话内的一次性变化，而不是每轮反复变动。
:::

### 5. 有意识地处理 Memory {#5-handle-memory-deliberately}

在 Native 函数调用下，召回的记忆会作为隐藏工具结果在每条回复中于你的消息之后到达一次，并在后续轮次原样重放，因此不会触及缓存前缀。在 Legacy 下，以及在没有 Web 界面会话的 API 请求中，记忆注入会在每一轮追加到你的消息上，并且**不**受 Preload files 管辖，因此可能让缓存反复失效。请使用 Native 函数调用来避免这一点。

`ENABLE_MEMORY_SYSTEM_CONTEXT=false` 会为所有聊天关闭自动注入。在 Native 函数调用下，模型随后会**按需**通过记忆工具读取记忆，因此请在静态系统提示中告知它这样做。参见[记忆](/features/chat-conversations/memory)。

### 6. 语音模式通常没有问题 {#6-voice-mode-is-usually-fine}

动态语音模式提示只前置一次，并在语音模式激活期间保持不变（语音会话通常会开启一个新的聊天），因此不会让缓存反复失效。在已经有键入消息的聊天中发起的通话（无论 Standard 还是 Realtime），会在首个语音轮次重建一次缓存前缀。你可以保持原样；若希望系统提示完全固定，请设置 `ENABLE_VOICE_MODE_PROMPT=false`。

## 结果：稳定且仅追加的请求 {#the-result-a-stable-append-only-request}

采用上述配置后：

- **前缀**：系统提示 + 工具定义，每一轮都相同 → **被缓存**。
- **主体**通过追加新的用户消息与工具结果而增长 → 只有新增的尾部未被缓存。
- 没有任何内容（RAG 模板、来源、引用、记忆、技能与知识库列表）会重写请求中更早的部分。

:::tip 验证你的命中率
留意提供方用量响应中的缓存 token 计数（例如 cache-read / cache-creation 输入 token）。配置正确时，被缓存的部分会**随对话变长而增长**，而每轮未缓存的输入大致保持恒定。
:::

## 提供方说明 {#provider-notes}

- **Anthropic**：如开头所述，缓存需要在每次请求中选择加入。稳定的前缀能最大化被缓存的比例。
- **OpenAI / Gemini / DeepSeek / OpenAI 兼容网关**：自动前缀缓存，无需选择加入。
- **位于 OpenAI 兼容网关之后的 Anthropic 模型（OpenRouter、LiteLLM）**：工具结果上的缓存标记会传到网关，因此在工具循环过程中前缀仍保持缓存。

无论哪种情况，要求都一样：**不要在轮次之间重写请求的开头。**

## 汇总检查清单 {#summary-checklist}

在 **Settings > Models**（管理员区域） 中针对模型，点击铅笔图标（**Edit**），然后进入 **Capabilities** 与 **Builtin Tools**：

- [ ] 静态系统提示（不每轮重新生成）
- [ ] 开启 **File Upload**，关闭 **Preload files**，不做自动内容注入（这也会禁用 "Using Entire Document"），**并且**正是它负责注入文件工具
- [ ] 可选：关闭 **Citations**，把引用规则移入系统提示
- [ ] 开启 **Builtin Tools**，并保持 **Files**、**Knowledge Base**、**Notes** 和 **Chat History** 分类处于启用状态
- [ ] 函数调用设为 **Native**（Legacy 模式下不存在内置工具）
- [ ] 记忆：Native 函数调用让召回的记忆远离缓存前缀
- [ ] 让工具列表在各轮之间保持稳定
