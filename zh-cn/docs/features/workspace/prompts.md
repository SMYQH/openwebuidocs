---
sidebar_position: 3
title: "提示词"
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# 提示词 {#prompts}

<ThemedImage
  alt="工作区提示词：一个模板块，下方排列着多个相同的副本"
  sources={{
    light: useBaseUrl('/images/banners/workspace-prompts-light.svg'),
    dark: useBaseUrl('/images/banners/workspace-prompts-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**可复用的斜杠命令，将复杂指令转变为一键表单。**

提示词让您将常用指令保存为斜杠命令。在任何对话中输入 `/summarize`，完整提示词立即触发。添加自定义输入变量，用户在发送提示词前会看到一个弹出表单，包含下拉菜单、日期选择器和文本字段。无需记住确切的措辞或结构。

所有内容变更都保存在版本历史中。你可以恢复旧版本、比较改动，并通过访问控制与团队共享提示词。

---

## 为什么使用提示词？ {#why-prompts}
![工作空间中已保存的提示词](/images/workspace/prompts-list.png)
### 停止重复输入相同的指令 {#stop-retyping-the-same-instructions}

保存一次提示词，用 `/command` 使用它。Bug 报告模板、会议记录、代码审查、内容简报：任何您输入超过两次的内容都应该成为提示词。

### 将提示词转变为交互式表单 {#turn-prompts-into-interactive-forms}

添加类型化输入变量（下拉菜单、日期选择器、数字字段、复选框），用户会看到一个清晰的表单而不是编辑原始文本。非技术用户无需理解语法就能运行复杂的提示词。

### 带回滚的版本历史 {#version-history-with-rollback}

每次修改提示词内容都会创建一个新版本。你可以浏览历史记录、预览版本、将它与当前生效的版本比较、编辑后另存为新版本、设为生效版本或删除。每个版本都会记录谁做了哪些更改。取消勾选 **Set as Production** 可以保存版本而不立即启用。重命名、更改标签或修改命令不会创建新版本。

### 受控共享 {#controlled-sharing}

与特定用户或用户组共享提示词。公开提示词出现在所有人的 `/` 建议中。私有提示词留在您自己的工作区中。对于您拥有编辑权限的提示词，在拥有 **Prompts Sharing** 权限的前提下，**工作区 > 提示词** 列表的 **⋯** 菜单中的 **访问** 可以直接打开[共享设置](/features/authentication-access/rbac/groups#resource-access-rbac)，无需进入编辑器，并且其中的每项更改都会立即保存。以写权限保存提示词会保留其原有的共享设置，包括您本身没有权限设置的 **Public** 选项。

---

## 主要功能 {#key-features}

| | |
| :--- | :--- |
| ⚡ **斜杠命令** | 输入 `/command` 插入完整提示词 |
| 📋 **输入变量表单** | 类型化字段（文本、下拉菜单、日期、数字、复选框等）生成弹出表单 |
| 🕑 **版本历史** | 带提交信息的完整变更跟踪、回滚和生产版本固定 |
| 🔄 **系统变量** | `{{CURRENT_DATE}}`、`{{USER_NAME}}`、`{{CLIPBOARD}}` 在运行时自动替换 |
| 🔒 **访问控制** | 与特定用户、用户组共享或设为公开 |
| 🔀 **启用/禁用切换** | 无需删除即可停用提示词 |
| 🏷️ **标签** | 组织和过滤您的提示词库 |

---

## 创建提示词 {#creating-a-prompt}

导航到 **工作区 > 提示词**，点击工作区页头中的 **Create**。

| 字段 | 说明 |
| :--- | :--- |
| **名称** | 用于标识的描述性标题 |
| **标签** | 用于过滤的分类 |
| **访问权限** | 控制谁可以查看和使用该提示词。需要 [**Prompts Sharing**](/features/authentication-access/rbac/permissions#2-sharing-permissions) 权限 |
| **命令** | 斜杠命令触发器（例如 `/summarize`） |
| **提示词内容** | 发送给模型的实际文本，包含变量 |
| **提交信息** | 可选的版本跟踪变更描述 |

点击提示词内容上方的 **Compare revision**，可在当前内容旁打开空白的 **Proposed revision** 窗格。将修改版本粘贴到该窗格，例如模型撰写的版本。点击 **Compare** 标出更改，再使用箭头逐项查看。点击 **Apply to draft** 将右侧窗格的内容填入编辑器，随后保存提示词。

使用清晰的变量名（`{{your_name}}` 而非 `{{var1}}`），添加描述性的 `placeholder` 文本，在合理的地方提供 `default` 值，只将真正必要的字段标记为 `:required`。公开提示词出现在每个用户的 `/` 建议中，因此应谨慎选择公开内容。使用启用/禁用切换将不活跃的提示词从建议中隐藏。

---

## 变量 {#variables}

### 系统变量 {#system-variables}

在运行时自动替换为对应的值：

| 变量 | 说明 |
| :--- | :--- |
| `{{CLIPBOARD}}` | 剪贴板中的内容。如果浏览器阻止了剪贴板访问，会提示无法读取剪贴板 |
| `{{CURRENT_DATE}}` | 当前日期 |
| `{{CURRENT_DATETIME}}` | 当前日期和时间 |
| `{{CURRENT_TIME}}` | 当前时间 |
| `{{CURRENT_TIMEZONE}}` | 当前时区 |
| `{{CURRENT_WEEKDAY}}` | 当前星期几 |
| `{{USER_NAME}}` | 您的显示名称 |
| `{{USER_EMAIL}}` | 您的邮箱地址 |
| `{{USER_ROLE}}` | 您的角色，例如 `admin` 或 `user` |
| `{{USER_BIO}}` | 设置 > 账户 > 用户资料中的个人简介（未设置则不替换） |
| `{{USER_GENDER}}` | 设置 > 账户 > 用户资料中的性别（未设置则不替换） |
| `{{USER_BIRTH_DATE}}` | 设置 > 账户 > 用户资料中的出生日期（未设置则不替换） |
| `{{USER_AGE}}` | 根据出生日期计算的年龄（未设置则不替换） |
| `{{USER_LANGUAGE}}` | 您选择的语言 |
| `{{USER_LOCATION}}` | 您的位置。浏览器会直接请求地理位置权限，这需要 HTTPS。界面开关仅控制随聊天请求发送的位置 |
| `{{USER_GROUPS}}` | 您所属用户组的逗号分隔列表，包含通过父组继承的用户组（若没有则为空）。仅在占位符存在时才会从数据库解析，并且仅用于模型系统提示词和任务模板。在以 `/` 插入的提示词中，它会保持字面量形式。 |

### 自定义输入变量 {#custom-input-variables}

在提示词内容中添加变量，用户使用斜杠命令时会看到弹出表单。

:::info 此语法仅适用于提示词内容

本页描述的语法适用于已保存提示词的内容。把 `{{name | text:required}}` 放入模型的系统提示词中不会有任何效果：它不会声明任何字段，不会打开任何表单，而是以字面文本的形式到达模型。

系统提示词应改用[聊天变量](/features/chat-conversations/chat-features/chat-params#chat-variables)，它们是相同的字段类型，只是带有 `chat.variables.` 前缀，因此上面的示例会变成 `{{chat.variables.name | text:required}}`。

:::

**简单输入**创建单行文本字段：
```
{{variable_name}}
```

**类型化输入**创建具有配置属性的特定字段类型：
```
{{variable_name | type:property="value"}}
```

所有自定义变量**默认为可选**。添加 `:required` 使字段为必填：
```
{{title | text:required}}
{{notes | textarea:placeholder="Additional context (optional)"}}
```

### 可用输入类型 {#available-input-types}

| 类型 | 说明 | 示例 |
| :--- | :--- | :--- |
| **text** | 单行文本（默认） | `{{name \| text:placeholder="Enter name":required}}` |
| **textarea** | 多行文本 | `{{description \| textarea:required}}` |
| **select** | 下拉菜单 | `{{priority \| select:options=["High","Medium","Low"]:required}}` |
| **number** | 数字输入 | `{{count \| number:min=1:max=100:default=5}}` |
| **checkbox** | 布尔开关 | `{{include_details \| checkbox:label="Include analysis"}}` |
| **date** | 日期选择器 | `{{start_date \| date:required}}` |
| **datetime-local** | 日期和时间选择器 | `{{appointment \| datetime-local}}` |
| **color** | 颜色选择器 | `{{brand_color \| color:default="#FFFFFF"}}` |
| **email** | 带验证的邮箱字段 | `{{email \| email:required}}` |
| **range** | 滑块 | `{{rating \| range:min=1:max=10}}` |
| **tel** | 电话号码 | `{{phone \| tel}}` |
| **time** | 时间选择器 | `{{meeting_time \| time}}` |
| **url** | 带验证的 URL | `{{website \| url:required}}` |
| **month** | 月份和年份（仅 Chrome/Edge，Firefox/Safari 降级为文本） | `{{billing_month \| month}}` |
| **map** | 用于坐标的交互式地图（实验性） | `{{location \| map}}` |

---

## 消息和提示词修饰符 {#message-and-prompt-modifiers}

这些修饰符对任务模型提示词特别有用（标题生成、标签生成、后续建议），其中对话包含粘贴的文档或代码等长消息。

### 提示词截断 {#prompt-truncation}

`{{prompt}}` 变量支持基于字符的截断：

| 修饰符 | 功能 |
| :--- | :--- |
| `{{prompt:start:N}}` | 前 N 个字符 |
| `{{prompt:end:N}}` | 后 N 个字符 |
| `{{prompt:middletruncate:N}}` | 前半部分 + 后半部分，共 N 个字符 |

### 消息选择器与管道过滤器 {#message-selectors-vs-pipe-filters}

`{{MESSAGES}}` 变量有两种不同的修饰符类型，在不同层面工作：

**消息选择器**（冒号 `:`）控制**包含多少条消息**：

| 选择器 | 功能 | 示例 |
| :--- | :--- | :--- |
| `START:N` | 前 N 条消息 | `{{MESSAGES:START:5}}` |
| `END:N` | 后 N 条消息 | `{{MESSAGES:END:5}}` |
| `MIDDLETRUNCATE:N` | 前 N/2 + 后 N/2 条消息 | `{{MESSAGES:MIDDLETRUNCATE:6}}` |

有 20 条消息时，`{{MESSAGES:MIDDLETRUNCATE:6}}` 保留消息 1-3 和 18-20，跳过中间的 14 条。

**管道过滤器**（管道 `|`）将**每条消息的内容**截断到字符限制：

| 过滤器 | 功能 | 示例 |
| :--- | :--- | :--- |
| `\|start:N` | 每条消息的前 N 个字符 | `\{\{MESSAGES\|start:300\}\}` |
| `\|end:N` | 每条消息的后 N 个字符 | `\{\{MESSAGES\|end:300\}\}` |
| `\|middletruncate:N` | 每条消息的前半 + 后半部分 | `\{\{MESSAGES\|middletruncate:500\}\}` |

**两者结合**，控制包含哪些消息及每条消息的长度：

| 语法 | 功能 |
| :--- | :--- |
| `\{\{MESSAGES:END:2\|middletruncate:500\}\}` | 最后 2 条消息，每条最多 500 字符 |
| `\{\{MESSAGES:START:5\|start:200\}\}` | 前 5 条消息，每条最多 200 字符 |
| `\{\{MESSAGES:MIDDLETRUNCATE:10\|middletruncate:50\}\}` | 前 5 + 后 5 条消息，每条最多 50 字符 |

:::warning 选择器计数消息而非字符
`{{MESSAGES:MIDDLETRUNCATE:500}}` 选择 **500 条消息**。要限制每条消息的字符数，请使用管道过滤器：`\{\{MESSAGES\|middletruncate:500\}\}`。没有管道过滤器，一个粘贴的文档可能会占满整个上下文窗口。
:::

---

## 版本历史 {#version-history}

每次保存都会在提示词内容发生变化时创建一个新版本。编辑提示词时，提示词内容上方的历史菜单默认显示 **Live**（当前生效的生产版本）。展开它会按从新到旧列出各版本，每条带有提交信息和作者（悬停可看日期），并提供 **Load more** 以加载更早的版本。

- 点击任一版本即可 **Preview**，内容以只读方式打开。
- **Compare to current** 会显示该版本与 Live 版本之间的差异：先并排显示名称和标签，然后以差异视图展示提示词内容。布局菜单可在 **Split** 与 **Unified** 之间切换，浏览器会记住该选择。仅涉及行尾符的更改会显示为 **Only line endings changed**。任一版本的内容超过 5000 行时无法比较（`Diff is limited to 5000 lines per version`）。
- **Edit as new version** 可让预览中的内容变为可编辑，保存后会基于它创建新版本。此处 **Save** 旁边的 **Set as Production** 复选框默认未勾选，因此 Live 提示词会保持不变，直到您勾选它。
- **Set as Production** 可将该版本恢复为当前生效的版本。
- 某个版本的 **⋯** 菜单中的 **Delete** 会在您于 **Delete Version** 对话框中确认后删除它。Live 版本无法删除。建立在已删除版本之上的版本会重新关联到其父版本，因此历史记录始终保持连贯。

![在提示词编辑器中进行对比，采用“分屏”布局，左侧显示旧版本，右侧显示正式发布版本](/images/workspace/prompt-version-compare.webp)

切换到其他版本或在存在未保存更改时离开编辑器，都会先询问是否放弃这些更改。任何可以查看提示词的人都能打开并比较其版本；编辑、将某个版本设为生效以及删除则需要写权限。

通过 API，`GET /api/v1/prompts/id/{prompt_id}/history/diff?from_id=...&to_id=...` 会返回两个快照、按行表示的内容差异，以及 `name_changed` 和 `line_endings_only`；后者在内容仅行尾符不同时为 `true`。

:::note 迁移说明
在引入版本控制之前创建的提示词已自动迁移，原内容保留为初始生效版本。URL 从基于命令改为基于 ID，因此现有书签可能需要更新。从 v0.5.0 起，所有变量默认为可选。
:::

---

## 示例 {#examples}

### Bug 报告生成器（`/bug_report`） {#bug-report-generator-bug\_report}

带有必填摘要、优先级下拉菜单和重现步骤的结构化表单，以及可选上下文字段：

```txt
Generate a bug report with the following details:

**Summary:** {{summary | text:placeholder="A brief summary of the issue":required}}
**Priority:** {{priority | select:options=["Critical","High","Medium","Low"]:default="Medium":required}}
**Steps to Reproduce:**
{{steps | textarea:placeholder="1. Go to...\n2. Click on...\n3. See error...":required}}

**Additional Context:** {{additional_context | textarea:placeholder="Browser version, OS, screenshots, etc."}}
**Workaround:** {{workaround | textarea:placeholder="Any temporary solutions found"}}

Please format this into a clear and complete bug report document.
```

### 会议记录（`/meeting_minutes`） {#meeting-minutes-meeting\_minutes}

日期和时间选择器、必填参与者和议程、可选决定和行动项：

``` txt
# Meeting Minutes

**Date:** {{meeting_date | date:required}}
**Time:** {{meeting_time | time:required}}
**Title:** {{title | text:placeholder="e.g., Weekly Team Sync":required}}
**Attendees:** {{attendees | text:placeholder="Comma-separated list of names":required}}

## Agenda / Key Discussion Points
{{agenda_items | textarea:placeholder="Paste the agenda or list the key topics discussed.":required}}

## Decisions Made
{{decisions | textarea:placeholder="Key decisions and outcomes"}}

## Action Items
{{action_items | textarea:placeholder="Action item, assignee, and deadline for each."}}

## Next Meeting
**Date:** {{next_meeting | date}}
**Topics:** {{next_topics | text:placeholder="Items to discuss next time"}}

Please format this into a clean and professional meeting summary.
```

### 标题生成（任务模型模板） {#title-generation-task-model-template}

使用消息选择器 + 管道过滤器保持上下文小：

```txt
Chat history:
<chat_history>
{{MESSAGES:END:2|middletruncate:500}}
</chat_history>

Generate a short title for this conversation.
```

发送最后 2 条消息，每条最多 500 字符。

---

## 局限性 {#limitations}

### 斜杠命令命名空间 {#slash-command-namespace}

公开提示词出现在每个用户的 `/` 建议中。过多公开提示词会使菜单杂乱。使用启用/禁用切换将不活跃的提示词从建议中排除。

[内置斜杠命令](/features/chat-conversations/chat-features/)的名称实际上是被保留的：`compact`、`status`、`fork` 和 `model`。使用这些命令的提示词仍会显示在菜单中，从菜单中选用时也依然有效；但如果用户手动输入并发送，执行的是内置命令而不是该提示词。请改用其他命令名称。

### 默认为可选 {#optional-by-default}

所有自定义输入变量除非标记为 `:required`，否则默认为可选。如果您的提示词依赖某个字段，请明确添加 `:required`。
