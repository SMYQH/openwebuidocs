---
sidebar_position: 12
title: "默认界面设置"
---

## 概述 {#overview}

每个账户都有自己的 **Settings > Interface** 页面，开箱状态下所有人都从 Open WebUI 自带的取值开始。**Default Interface Settings** 让管理员可以为整个实例选择这些起始值，从而让新账户打开时看到的是你想要的界面，而不是默认界面。

它们只是起始值。任何人都仍然可以自行修改其中任意一项。

你可以用两种方式配置它们：

1. **管理面板**（适合快速修改和试验）
2. **环境变量（`DEFAULT_INTERFACE_SETTINGS`）**（适合自动化 / GitOps 风格的部署）

---

:::tip 重命名界面上的措辞
这些设置决定用户所见选项的起始值。若要修改界面本身的措辞、某个标签或按钮，请使用同一管理页面上的 **UI Translations**。参见[翻译](/features/administration/translations#interface-text)。
:::

## 取值是如何决定的 {#how-a-value-is-decided}

1. 如果此人自己设置过该选项，就使用他设置的值。
2. 否则使用你为实例设置的默认值。
3. 如果你没有为它设置默认值，就使用内置值。

从未被人改动过的开关类选项，会在 **Settings > Interface** 中其开关旁显示一个小小的 **Default** 标签。不是开关的选项没有该标签，但继承方式完全相同。

未被改动过的选项会持续跟随你的默认值，因此之后修改某个默认值时，所有没有覆盖该选项的人都会随之变化。保存 **Interface** 页面会保持这种继承关系，**Font Family** 以及 **Image Compression** 的尺寸也不例外。

:::info 与默认值一致即解除该选项的覆盖
把某个控件改回你当前的默认值，就会解除该覆盖：**Default** 标签重新出现，该选项再次跟随你的默认值。用户就是这样撤销自己先前的选择的。

解除发生在该用户保存设置时，比较的对象是你当时的默认值。因此，把某个默认值设为某人已经为自己选择的值，并不会自动解除他的覆盖：他的选择仍然被固定，你接下来的修改也依然影响不到他。要等到他下一次在 **Interface** 页面上保存任何设置时才会解除，届时他所有与当前默认值一致的选项会一并解除，而不只是刚改动的那一个。
:::

---

## 配置默认值 {#configuring-the-defaults}

### 方式一：使用管理面板 {#option-1-using-the-admin-panel}

1. 以管理员身份登录你的 Open WebUI 实例。
2. 前往 **Settings** → **Admin** → **General**。
3. 找到 **UI** 区域，点击 **Default Interface Settings** 旁边的 **Configure**。
4. 设置你想要的选项。该列表与用户在 **Settings > Interface** 中看到的完全相同。
5. 点击页面底部的 **Save**。

列表上方有一行会统计你已配置的设置数量。你碰过的每个控件都会计入其中，包括改了又改回去的控件，因此请用 **Clear** 清空该集合，把一切恢复为内置取值。

---

### 方式二：使用环境变量（`DEFAULT_INTERFACE_SETTINGS`） {#option-2-using-environment-variables-default_interface_settings}

对于自动化部署，请使用 `DEFAULT_INTERFACE_SETTINGS` 环境变量来配置默认值。该值必须是一个表示 **JSON 对象**的 **JSON 字符串**，其键为[下表](#setting-keys)中列出的设置名称。

**环境变量：**

- `DEFAULT_INTERFACE_SETTINGS`
  - **类型：** `string`（包含一个 JSON 对象）
  - **默认值：** `{}`
  - **说明：** 每个账户在 **Settings > Interface** 中各选项的起始值

#### 示例（Docker Compose） {#example-docker-compose}

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - 'DEFAULT_INTERFACE_SETTINGS={"chatBubble":false,"widescreenMode":true,"chatHoverPreview":false,"title":{"auto":false}}'
```

如果该值不是有效的 JSON，或解析结果不是一个对象，它会被忽略，不会应用任何默认值。

:::tip 覆盖范围超出 Interface 页面
这些默认值作用于个人的整份设置记录，其范围比 **Interface** 页面更广。因此该环境变量也接受其他个人设置页面所使用的键，例如 `system`（个人系统提示）、`params`（个人高级参数）、`notificationSound` 和 `keyboardShortcuts`，尽管管理面板编辑器只提供界面控件。它们的继承与解除方式与表中各键完全一致。
:::

---

## 设置键 {#setting-keys}

下面是 **Settings > Interface** 页面上的每一个选项，按页面中的出现顺序排列，并列出在 `DEFAULT_INTERFACE_SETTINGS` 中应使用的名称，以及在你未设置默认值时 Open WebUI 所使用的取值。

### UI

| 键 | 在 Settings > Interface 中的标签 | 内置默认值 |
| --- | --- | --- |
| `textScale` | UI Scale | `null`（显示为 **Default**），否则为 `1` 到 `1.5` 之间的数字 |
| `fontFamily` | Font Family | `null`（显示为 **Default**），否则为某个字体的名称 |
| `highContrastMode` | Accessibility Mode | `false` |
| `showChatTitleInTab` | Display Chat Title in Tab | `true` |
| `userLocation` | Allow User Location | `false` |
| `hapticFeedback` | Haptic Feedback (Android) | `false` |
| `copyFormatted` | Copy Formatted Text | `false` |
| `showUpdateToast` | Toast Notifications for New Updates | `true` |
| `showChangelog` | Show "What's New" Modal on Login | `true` |

`textScale` 对应 **UI Scale** 滑块，`highContrastMode` 对应 **Accessibility Mode**。开启无障碍模式后，手机允许最多 5 倍的捏合缩放；关闭时缩放会被锁定，因此手机不会自行放大到小号输入框里。

`fontFamily` 指定的是一款必须安装在每个人自己机器上的字体。它不会下载任何东西，因此如果默认值中指定的字体你的用户没有安装，就会回退到标准字体，所有人看到的仍是常见界面。只在你清楚哪些字体已安装的场景下设置它，例如配备了企业字体的受管设备群。

### 聊天 {#chat}

| 键 | 在 Settings > Interface 中的标签 | 内置默认值 |
| --- | --- | --- |
| `enableMessageQueue` | Enable Message Queue | `true` |
| `chatDirection` | Chat Direction | `"auto"`，或 `"LTR"` / `"RTL"` |
| `landingPageMode` | Landing Page Mode | `""`（显示为 **Default**），或 `"chat"` |
| `backgroundImageUrl` | Chat Background Image | `null` |
| `chatBubble` | Chat Bubble UI | `true` |
| `showUsername` | Display the Username Instead of You in the Chat | `false` |
| `widescreenMode` | Widescreen Mode | `false` |
| `temporaryChatByDefault` | Temporary Chat by Default | `false` |
| `chatFadeStreamingText` | Fade Effect for Streaming Text | `true` |
| `renderMarkdownInUserMessages` | Render Markdown in User Messages | `true` |
| `renderMarkdownInAssistantMessages` | Render Markdown in Assistant Messages | `true` |
| `renderMarkdownInPreviews` | Render Markdown in Previews | `true` |
| `title.auto` | Title Auto-Generation | `true` |
| `autoFollowUps` | Follow-Up Auto-Generation | `true` |
| `autoTags` | Chat Tags Auto-Generation | `true` |
| `responseAutoCopy` | Auto-Copy Response to Clipboard | `false` |
| `scrollOnResponseGeneration` | Response Auto-Scroll | `true` |
| `scrollOnBranchChange` | Scroll On Branch Change | `true` |
| `insertSuggestionPrompt` | Insert Suggestion Prompt to Input | `false` |
| `keepFollowUpPrompts` | Keep Follow-Up Prompts in Chat | `false` |
| `insertFollowUpPrompt` | Insert Follow-Up Prompt to Input | `false` |
| `regenerateMenu` | Regenerate Menu | `true` |
| `collapseCodeBlocks` | Always Collapse Code Blocks | `false` |
| `expandDetails` | Always Expand Details | `false` |
| `chatHoverPreview` | Chat Hover Previews | `true` |
| `displayMultiModelResponsesInTabs` | Display Multi-model Responses in Tabs | `false` |
| `terminalFileDisplay` | Terminal File Display | `sidebar` |
| `terminalPreviewAllowSameOrigin` | Terminal Preview Allow Same Origin | `false` |
| `stylizedPdfExport` | Stylized PDF Export | `true` |
| `showFloatingActionButtons` | Floating Quick Actions | `true` |
| `floatingActionButtons` | Floating Quick Actions > **Manage** | `null` |
| `webSearch` | Web Search in Chat | `null`（显示为 **Default**），或 `"always"` |

`title.auto` 是嵌套结构，因此在环境变量中写作 `{"title": {"auto": false}}`。

### 输入 {#input}

| 键 | 在 Settings > Interface 中的标签 | 内置默认值 |
| --- | --- | --- |
| `ctrlEnterToSend` | Enter Key Behavior | `false`（**Enter to Send**）；`true` 表示 **Ctrl+Enter to Send**，在聊天、频道消息和主题回复中均适用 |
| `richTextInput` | Rich Text Input for Chat | `true` |
| `promptAutocomplete` | Prompt Autocompletion | `false` |
| `showFormattingToolbar` | Show Formatting Toolbar | `false` |
| `insertPromptAsRichText` | Insert Prompt as Rich Text | `false` |
| `largeTextAsFile` | Paste Large Text as File | `false` |

### Artifacts

| 键 | 在 Settings > Interface 中的标签 | 内置默认值 |
| --- | --- | --- |
| `detectArtifacts` | Detect Artifacts Automatically | `true` |
| `iframeSandboxAllowScripts` | iframe Sandbox Allow Scripts | `true` |
| `iframeSandboxAllowSameOrigin` | iframe Sandbox Allow Same Origin | `false` |
| `iframeSandboxAllowForms` | iframe Sandbox Allow Forms | `true` |
| `iframeSandboxAllowDownloads` | iframe Sandbox Allow Downloads | `true` |

### 语音 {#voice}

| 键 | 在 Settings > Interface 中的标签 | 内置默认值 |
| --- | --- | --- |
| `voiceInterruption` | Allow Voice Interruption in Call | `false` |
| `showEmojiInCall` | Display Emoji in Call | `false` |

### 文件 {#file}

| 键 | 在 Settings > Interface 中的标签 | 内置默认值 |
| --- | --- | --- |
| `defaultUploadContext` | Default Upload Mode | `"focused"`（**Using Focused Retrieval**）；`"full"` 表示 **Using Entire Document** |
| `imageCompression` | Image Compression | `false` |
| `imageCompressionSize` | Image Compression > **Manage** | `{"width": "", "height": ""}` |
| `imageCompressionInChannels` | Compress Images in Channels | `true` |

:::note 并非始终显示在屏幕上的行
少数控件只有在适用时才会出现，例如用户能够访问终端之后才会显示的终端相关设置，或在 Web 搜索开启且被允许期间的 **Web Search in Chat**。为它们设置默认值仍然有效，只是会对能看到该控件的人生效。
:::

---

## 这不能做什么 {#what-this-does-not-do}

- **它不会限制任何人。** 每个人仍然完全掌控 **Settings > Interface** 中的每一个选项。若要真正让人们遵守你的取值，请收回他们的 **Interface Settings Access** 权限（参见[锁定默认值](#locking-the-defaults)），或用[可见控件](#hiding-controls)隐藏单个选项。
- **它不会清除任何人已有的选择。** 某人已经为自己设置的内容会保持原值。改变的是他们从未设置过的选项：这些选项会从内置取值变成你设定的取值。
- **它不涵盖主题和语言。** 两者都存放在浏览器中而非账户上，因此不属于本功能范围。请使用 [`DEFAULT_LOCALE`](/reference/env-configuration#default_locale) 来选择起始语言。

---

## 锁定默认值 {#locking-the-defaults}

如果某些账户需要严格保持在你设定的取值上，请从它们身上移除 **Interface Settings Access** 权限（参见[权限](/features/authentication-access/rbac/permissions)）。这样 **Interface** 页面会被隐藏，任何保存个人设置的尝试都会被拒绝，这些账户因此会保持你配置的样子。管理员不受该权限约束，始终可以修改自己的设置。

---

## 隐藏控件 {#hiding-controls}

**Settings > Admin > Interface** 中的 **Visible controls** 可以对除管理员之外的所有人隐藏单个控件。隐藏只是把控件从界面上移除：它的取值和背后的功能依然生效，因此要阻止人们使用某项功能，请使用[权限](/features/authentication-access/rbac/permissions)。隐藏 **Archive** 也会一并隐藏取消归档和 **Archive All Chats**。如果某个区域或菜单项下的控件全被隐藏，它也会随之消失，例如聊天输入菜单中的 **Add Context** 或模型编辑器中的 **Capabilities** 区域。同一个列表也可以通过 [`UI_VISIBILITY`](/reference/env-configuration#ui_visibility) 设置。

---

## 检查某个账户覆盖了哪些内容 {#checking-what-an-account-has-overridden}

`GET /api/v1/users/user/settings` 返回已登录账户的设置，其中已经填入你的默认值，这也是应用自身使用的值。加上 `?raw=true` 则改为返回该账户自己存储的设置，不合并默认值，从而可以确切地看出哪些选项被它固定、哪些仍在继承。

---

## 相关阅读 {#related}

- 环境变量参考中的 [`DEFAULT_INTERFACE_SETTINGS`](/reference/env-configuration#default_interface_settings)
- [理解设置](/getting-started/quick-start/settings)，介绍管理员设置与用户设置之间的关系
- [权限](/features/authentication-access/rbac/permissions)，其中包含 **Interface Settings Access**
