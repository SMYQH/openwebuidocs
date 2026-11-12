---
sidebar_position: 7
title: "URL 参数"
---

在 Open WebUI 中，可以通过各种 URL 参数来定制聊天会话。这些参数让你能够按会话设置特定配置、启用功能并定义模型设置，直接从 URL 就能对单个聊天会话进行精细控制。

## URL 参数总览 {#url-parameter-overview}

下表列出了可用的 URL 参数、它们的作用以及示例用法。

| **参数**         | **说明**                                                                   | **示例**                      |
|-----------------------|-----------------------------------------------------------------------------------|----------------------------------|
| `models`              | 指定要使用的模型列表，多个模型以逗号分隔。 | `/?models=model1,model2`         |
| `model`               | 为该聊天会话指定单个模型。 | `/?model=model1`                 |
| `youtube`             | 指定要在聊天中转录的 YouTube 视频 ID，需经用户确认。 | `/?youtube=VIDEO_ID`             |
| `load-url`            | 指定要抓取并作为文档上传到聊天中的网站 URL，需经用户确认。 | `/?load-url=https://google.com`  |
| `web-search`          | 若设为 `true`，则启用网络搜索功能。 | `/?web-search=true`              |
| `tools` or `tool-ids` | 指定要在聊天中启用的工具 ID 列表，多个以逗号分隔。工具服务器连接使用带前缀的 ID。 | `/?tools=tool1,tool2`            |
| `call` or `voice`     | 若设为 `true`，则启动语音模式，需经用户确认。 | `/?call=true`                    |
| `q`                   | 在消息输入框中填入一段提示词，供用户查看后发送。 | `/?q=Hello%20there`              |
| `temporary-chat`      | 若设为 `true`，则将聊天标记为临时会话，用于一次性场景。 | `/?temporary-chat=true`          |
| `code-interpreter`    | 若设为 `true`，则启用代码解释器功能。 | `/?code-interpreter=true`        |
| `image-generation`    | 若设为 `true`，则启用图像生成功能。 | `/?image-generation=true`        |
| `settings`            | 在某个标签页上打开设置对话框；`admin:` 标签页仅管理员可见。 | `/?settings=admin:documents`     |

### 1. **模型与模型选择** {#1-models-and-model-selection}

- **说明**：`models` 和 `model` 参数可让你指定某个聊天会话使用哪些[语言模型](/features/workspace/models)
- **如何设置**：多个模型用 `models`，单个模型用 `model`
- **示例**：
  - `/?models=model1,model2` —— 使用 `model1` 和 `model2` 初始化聊天
  - `/?model=model1` —— 将 `model1` 作为该聊天唯一模型
- **注意**：当没有选中任何有效模型时——例如上次使用的模型已被移除或隐藏——不带这两个参数的新聊天会回退到[用户所在组的默认模型](/features/authentication-access/rbac/groups#default-models-per-group)；若没有任何组设置默认模型，则回退到实例的[已选模型](/features/workspace/models#selected-and-pinned-models-admin)（[`DEFAULT_MODELS`](/reference/env-configuration#default_models)）。传入其中任一参数会抑制这种回退，因此聊天会等待你指定的模型。

### 2. **YouTube 转录** {#2-youtube-transcription}

- **说明**：`youtube` 参数接收一个 YouTube 视频 ID，让聊天对指定视频执行转录
- **如何设置**：将 YouTube 视频 ID 作为该参数值
- **示例**：`/?youtube=VIDEO_ID`
- **行为**：会弹出一个 **打开链接** 对话框，列出视频 URL 并询问是否加载。用户确认后，该视频的转录文本会被加入聊天；取消则不会加载任何内容。

### 3. **网站插入** {#3-website-insertion}

- **说明**：`load-url` 参数会下载指定网站，并提取内容，将其作为文档上传到聊天中
- **如何设置**：将完整的网站 URL 作为该参数值
- **示例**：`/?load-url=https://google.com`
- **行为**：会弹出一个 **打开链接** 对话框，列出该 URL 并询问是否加载。用户确认后，页面内容会作为文档加入聊天；取消则不会加载任何内容。当同时使用 `youtube` 和 `load-url` 时，同一个对话框会列出两个 URL。

### 4. **网络搜索** {#4-web-search}

- **说明**：启用 `web-search` 后，该聊天会话即可访问[网络搜索](/features/chat-conversations/web-search)功能
- **如何设置**：将该参数设为 `true` 以启用网络搜索
- **示例**：`/?web-search=true`
- **行为**：启用后，聊天可将网络搜索结果纳入回复内容。

### 5. **工具选择** {#5-tool-selection}

- **说明**：`tools` 或 `tool-ids` 参数用于指定在聊天中启用哪些[tools](/features/extensibility/plugin/tools)
- **如何设置**：以逗号分隔的工具 ID 列表作为该参数值
- **示例**：`/?tools=tool1,tool2` 或 `/?tool-ids=tool1,tool2`
- **行为**：系统会匹配并激活这些工具，以供当前会话使用
- **注意**：该值必须是 Open WebUI 内部使用的 ID，它不一定与你在 **+** 菜单中看到的名称一致。工作区工具使用其原始 ID，例如 `/?tools=my_workspace_tool`。工具服务器连接会在连接上设置的 ID 前加一个前缀：MCP 连接用 `server:mcp:<server-id>`，OpenAPI 连接用 `server:<server-id>`，例如 `/?tool-ids=server:mcp:my_mcp_server`。未设置 ID 的 OpenAPI 连接使用它在连接列表中的位置，从 `0` 开始。没有匹配到任何内容的 ID 不会被激活。tools 列表接口会返回准确的 ID，参见[通过 API 使用 Open WebUI 工具（含 MCP）](/reference/api-endpoints#using-open-webui-tools-including-mcp-from-the-api)。

### 6. **通话叠层** {#6-call-overlay}

- **说明**：`call` 参数会启动[语音模式](/features/chat-conversations/chat-features/voice-mode)，即聊天界面中的通话叠层。`voice` 是它的别名，行为完全相同。
- **如何设置**：将该参数设为 `true` 以启动通话叠层
- **示例**：`/?call=true` 或 `/?voice=true`
- **行为**：会弹出一个 **打开链接** 对话框，询问是否使用麦克风开始语音通话。用户确认后才会打开通话叠层，以支持实时转录、视频输入等功能；取消则不会开启麦克风。当链接同时带有 `youtube` 或 `load-url` 时，同一个对话框会列出这些 URL，确认后两者都会执行。该通话与 **语音模式** 按钮遵循相同的校验：用户需要拥有 [**Allow Call**](/features/authentication-access/rbac/permissions#3-chat-permissions) 权限，且只能选中一个模型。在 Standard 通话模式下，语音转文本引擎还必须不是 **Web API**。

### 7. **初始查询提示词** {#7-initial-query-prompt}

- **说明**：`q` 参数允许为聊天预设初始查询或提示词
- **如何设置**：将查询或提示词文本作为该参数值
- **示例**：`/?q=Hello%20there`
- **行为**：文本会落入消息输入框，由用户决定何时发送。

### 8. **临时聊天会话** {#8-temporary-chat-sessions}

- **说明**：`temporary-chat` 参数会把聊天标记为临时会话。这可能会限制保存聊天历史或应用持久化设置等能力
- **如何设置**：将该参数设为 `true` 以开启临时聊天会话
- **示例**：`/?temporary-chat=true`
- **行为**：启动一个一次性聊天会话，不保存历史，也不会应用高级持久配置
  - **注意**：临时聊天在重新连接后会接上仍在进行中的回复。
  - **注意**：出于隐私考虑，临时聊天中的文档处理仅在前端进行。需要后端解析的复杂文件（例如 DOCX）可能无法完整支持。
  - **注意**：临时聊天以按会话分配的 ID 存在，不保存聊天记录，因此运行过程中产生的内容（消息、生成的图片、状态更新、标题或标签）都不会写入数据库。需要已保存聊天的功能——例如[任务列表](/features/chat-conversations/chat-features/task-management)、[按聊天划分的终端](/features/open-terminal/terminals/orchestration/contexts)、[子智能体](/features/chat-conversations/chat-features/subagents)、[定时器](/features/chat-conversations/chat-features/timers) 和分叉——在其中都不可用。临时聊天在回复下方不显示 **Fork chat** 操作，`/` 菜单中也没有 `/fork`，手动输入 `/fork` 会得到 **No chat to fork** 的回答。[频道](/features/channels)中的聊天同理，[询问用户工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode) 在频道中也不可用。
  - **注意**：在临时聊天中，来自[询问用户工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)的问题，或等待 [**Ask for approval**](/features/extensibility/plugin/tools#tool-approval) 的工具调用，会以对话框形式出现在打开的浏览器标签页中。大约两分钟内无人回答、离开该聊天，或标签页失去连接，都视为拒绝。在已保存的聊天中，刷新或连接中断并不是终局：如果你在 60 秒内、且在超时之前重新打开该聊天，问题会再次发出。必须是该标签页中打开的那个临时聊天，否则请求会立即被取消。
  - **注意**：上面列出的不可用功能是完整的。列表之外的任何功能或工具在临时聊天中的表现与普通聊天完全一致——包括会自行存储或发送数据的工具、记忆、便签和网络搜索等。如果你不希望临时聊天使用某个工具，请在模型上禁用它。

### 9. **代码解释器** {#9-code-interpreter}

- **说明**：`code-interpreter` 参数用于启用代码解释器功能
- **如何设置**：将该参数设为 `true`，为这个新的聊天会话启用代码解释器功能
- **示例**：`/?code-interpreter=true`
- **行为**：激活代码解释器按钮，并在下一次发送提示词时调用代码解释器。

### 10. **图像生成** {#10-image-generation}

- **说明**：`image-generation` 参数会为所给提示词启用图像生成
- **如何设置**：将该参数设为 `true` 以启用该聊天的图像生成
- **示例**：`/?image-generation=true`
- **行为**：激活图像生成按钮以生成图像。

### 11. **设置深链** {#11-settings-deep-link}

- **说明**：`settings` 参数会在指定标签页上打开设置对话框，随后把自己从 URL 中移除
- **如何设置**：使用用户标签页 id（`general`、`interface`、`notifications`、`shortcuts`、`connections`、`tools`、`personalization`、`audio`、`data_controls`、`usage`、`archived_chats`、`account`、`about`），或以 `admin:<tab>` 形式使用管理员标签页（`general`、`authentication`、`connections`、`models`、`subagents`、`evaluations`、`analytics`、`integrations`、`documents`、`web`、`code-execution`、`interface`、`audio`、`images`、`db`、`pipelines`）
- **示例**：`/?settings=admin:documents`
- **行为**：对话框会在该标签页上打开。非管理员打开 `admin:` 链接时，会改为显示常规（General）标签页。

### 12. **新建便签** {#12-new-note}

- **说明**：在[便签页面](/features/notes#quick-creation)上，`title` 和 `content` 会预填一条新便签
- **如何设置**：用其中任一参数打开 `/notes/new`（或 `/notes`）
- **示例**：`/notes/new?title=Meeting&content=Agenda%3A`
- **行为**：一个 **创建新便签** 对话框会显示标题和正文，并在创建任何内容之前先征求确认。用户确认后，便签被创建并在编辑器中打开。只提供 `content` 时，标题默认为今天的日期。在 `/notes/new` 上取消则返回便签列表。

<!-- markdownlint-disable-next-line MD033 -->
<details>
<!-- markdownlint-disable-next-line MD033 -->
<summary>示例用法</summary>

:::tip

**临时聊天会话**
假设用户想发起一次不保存历史的快速聊天会话，可以在 URL 中设置 `temporary-chat=true` 来实现。这提供了一个一次性聊天环境，非常适合一次性交互。

:::
</details>

## 组合使用多个参数 {#using-multiple-parameters-together}

这些 URL 参数可以组合起来，创建高度定制的聊天会话。例如：

```bash
/?models=model1&youtube=VIDEO_ID&web-search=true&tools=tool1,tool2&call=true&q=Hello%20there&temporary-chat=true
```

这个 URL 将：

- 使用 `model1` 初始化聊天。
- 启用网络搜索和指定的工具。
- 弹出一个 **打开链接** 对话框，其中列出该 YouTube 视频并询问是否开始语音通话。确认后会加载转录文本并打开通话叠层。
- 把 "Hello there" 放入消息输入框，随时可以发送。
- 将聊天标记为临时，不保存任何历史。