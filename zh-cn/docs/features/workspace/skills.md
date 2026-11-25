---
sidebar_position: 6
title: "技能"
sidebar_label: "技能"
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# 技能 {#skills}

<ThemedImage
  alt="工作区技能：四块玩具积木，上面还放着一块。"
  sources={{
    light: useBaseUrl('/images/banners/workspace-skills-light.svg'),
    dark: useBaseUrl('/images/banners/workspace-skills-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**用纯文本指令教会你的 AI 如何处理某项任务。**

技能是可复用的、基于 Markdown 的指令集，你可以把它们附加到模型上，或在对话中即时调用。与[工具](/features/extensibility/plugin/tools)（可执行的 Python 脚本）不同，技能是纯文本指令：代码审查准则、写作风格规则、故障排查手册、数据分析流程。模型会阅读并遵循它们。

在对话中用 `$` 提及某个技能，或者把它绑定到模型上，使每个新对话一开始就选中它。其他所有你可读的技能仍然可用，模型会在需要时加载。

---

## 为什么使用技能？ {#why-skills}

![工作区中的技能](/images/workspace/skills-list.png)

### 无需代码的指令 {#instructions-without-code}

用 Markdown 编写准则。无需 Python，无需 API 调用，无需部署。只要你能写文档，就能创建技能。

### 按需上下文加载 {#on-demand-context-loading}

借助[技能工具](#skill-tools)，你可读的每个技能都会以名称和描述列出，模型会在需要时加载其中之一。选中的技能会在模型回答前加载。

### 跨模型复用 {#reusable-across-models}

创建一个“代码审查准则”技能并附加到每个编程模型上。只需更新一次技能，所有模型都会获得新版本。

### 与工具组合使用 {#composable-with-tools}

把技能与[Open Terminal](/features/open-terminal)或任意工具服务器搭配使用。技能教会模型*如何*使用该工具（检查退出码、处理错误、对长时间运行的命令使用流式输出），而工具提供*能力*本身。

---

## 主要功能 {#key-features}

| | | 
| :--- | :--- | 
| **Markdown 内容** | 用纯 Markdown 编写指令 |
| **配套文件** | 在 `SKILL.md` 旁边附带脚本、参考文档、模板和资源 |
| **版本历史** | 每次保存都是一个版本，可以对比、导出或恢复为当前版本 |
| **对话中 `$` 提及** | 输入 `$` 即可把技能的指令注入当前消息 |
| **每对话切换** | 通过 **+** 菜单为单个对话启用技能，无需编辑模型 |
| **模型绑定** | 把技能附加到模型，使新对话一开始就选中它们 |
| **懒加载** | 未选中的技能会列在清单中，按需加载 |
| **导入/导出** | 导入 ZIP 压缩包、`.skill` 文件、技能文件夹、JSON 或单个 `.md` 文件，也可以从 URL 加载；可导出为 `.skill`、ZIP 或 JSON |
| **社区** | 在 openwebui.com 上查找技能并分享你自己的技能 |
| **访问控制** | 默认私有，可与用户或用户组共享 |
| **启用/禁用切换** | 停用技能而不删除它们 |

---

## 技能的工作原理 {#how-skills-work}

### 用户选择的技能（$ 提及） {#user-selected-skills--mention}

在对话输入框中输入 `$`，或使用 `/` 菜单，然后选择一个技能。借助[技能工具](#skill-tools)，技能会在模型回答前加载，每个对话加载一次。若没有这些工具，其指令会随每条消息进入系统提示词。如果消息仅包含一个 `$` 技能提及，发送时会以技能名称作为消息正文。

### 每对话技能 {#per-chat-skills}

通过 **+** 菜单 > **技能**为当前聊天启用技能。列表按**工作区**及所选机器分组，机器分组以其名称命名。参见[机器中的技能](#skills-from-a-machine)。徽标显示已开启的数量。所选技能的加载方式与用 `$` 提及的技能相同。

### 绑定到模型的技能 {#model-attached-skills}

使用单个模型开启的新对话，默认就会选中该模型附加的技能。

有了[技能工具](#skill-tools)之后，你有权访问的每个启用技能都会在你的消息之后，以隐藏的 `list_available_skills` 结果按名称和描述列出。模型在需要时用 `view_skill` 加载其中某个，因此挂载大量技能几乎不占用上下文。选中的技能也以同样的方式加载——每个对话一次，以隐藏的 `view_skill` 结果呈现。在对话中关闭的技能仍会留在列表里。

如果没有技能工具，就没有这份列表。选中的、被 `$` 提及的以及模型附加的技能会在每条消息中注入系统提示词，最多取 `SKILL.md` 的前 100,000 个字符；而且即使在对话中关闭，模型附加的技能仍然会被注入。

超过[读取上限](#read-limits)的 `SKILL.md` 会以预览形式送达，模型再用 `read_skill_file` 继续读取。

### 按需加载选中的技能 {#loading-selected-skills-on-demand}

**Settings > General**（管理员区域）中的 **按需加载选中的技能**（[`ENABLE_SKILL_LAZY_LOADING`](/reference/env-configuration#enable_skill_lazy_loading)，默认关闭）会让选中的技能和模型附加的技能不再在模型回答前加载，而是等模型请求时才加载。对话中用 `$` 提及的技能仍会随消息加载。该设置需要技能工具。

### 技能工具 {#skill-tools}

启用原生函数调用、**内置工具** 能力以及模型的 **技能** 类别后，模型会获得以下工具。前三个只要列出了至少一个技能就会提供，而 `update_skill_files` 在列出了工作区技能时提供。`/skills:create` 也需要它们。

| 工具 | 作用 |
| :--- | :--- |
| `view_skill` | 加载某个技能的 `SKILL.md` 及其文件列表，上限为读取限制。 |
| `read_skill_file` | 从给定偏移量读取技能的一个文件，单次调用不超过读取限制。对二进制文件会返回文件大小以及指向技能编辑器的链接。 |
| `grep_skill_files` | 在技能的文本文件中搜索单词、短语或正则表达式并返回摘录，默认 10 条，最多 30 条。 |
| `update_skill_files` | 将文件改动保存为该技能的新版本，前提是用户有权编辑该技能。若期间有人保存过该技能，则会因冲突而被拒绝。 |
| `create_skill` | 根据 `SKILL.md` 文本和可选的文本文件在工作区中创建一个新的私有技能。向管理员以及拥有 **技能访问** 权限的用户提供。 |

读取技能的工具会检查用户对该技能的访问权限。对非活跃技能拥有写入权限的用户，模型仍可加载并读取它。

### 读取限制 {#read-limits}

**Settings > General**（管理员区域）中的两项设置决定模型一次能获得多少技能内容：

| 设置 | 默认值 | 作用 |
| :--- | :--- | :--- |
| **技能读取上限** | 20,000 | 模型单次读取最多获得的字符数 |
| **技能预览长度** | 5,000 | 当 `SKILL.md` 长于读取上限时，模型首先获得的字符数 |

留空即使用默认值，也可以设置 [`SKILL_CONTENT_MAX_CHARS`](/reference/env-configuration#skill_content_max_chars) 和 [`SKILL_PREVIEW_MAX_CHARS`](/reference/env-configuration#skill_preview_max_chars)。

### 机器中的技能 {#skills-from-a-machine}

已连接的 [Open Terminal](/features/open-terminal) 机器可以拥有自己的技能，它们与所描述的文件一起留在工作区中。Open WebUI 从服务器读取它们，并在 `$` 选择器中与工作区技能一起提供，ID 格式为 `terminal:<url-encoded name>`。它们与其他技能的用法相同：用 `$` 提及时会注入内容，否则它们留在同一清单中，通过 `view_skill` 加载。注入的内容包含技能目录及随附文件信息，让模型知道在工作区中的何处读取。`read_skill_file` 分页读取终端技能的 `SKILL.md`，`grep_skill_files` 则搜索该文件。其他文件仍留在机器上，由模型通过机器自带的文件工具打开。技能编辑器、版本历史和 `update_skill_files` 适用于工作区技能。

管理员配置的机器由 Open WebUI 服务器调用，使用连接的认证信息、`Accept: application/json`、`X-User-Id`、`X-Session-Id`（聊天 ID），以及编排机器的 [`X-Terminal-*` 请求头](/features/open-terminal/terminals/orchestration/api-troubleshooting#headers-sent-to-the-terminals-server)。这些身份请求头与其他机器调用相同，因此按用户或聊天划分技能作用域的服务器可以获得所需信息。不会跟随重定向。用户在 [Tether 应用](/ecosystem/tether#bring-your-own-models-and-tools)中添加的机器由 Tether 从该用户的电脑调用，因此只要 Tether 保持连接，该机器就可用于托管在别处的 Open WebUI。

---

## 创建技能 {#creating-a-skill}

前往**工作区 > 技能**，点击工作区页眉中的 **创建**。

| 字段 | 说明 |
| :--- | :--- |
| **名称** | 人类可读的显示名称（例如“代码审查准则”） |
| **技能 ID** | 唯一的 slug，从名称自动生成。创建时可编辑，之后只读 |
| **描述** | 清单中显示的简短摘要。对于绑定到模型的技能，模型用此决定是否加载完整指令 |
| **文件** | 包含完整技能指令的 Markdown 文件 `SKILL.md`，以及任何配套文件 |

名称旁的地球图标选择器可按语言翻译 **名称** 和 **描述**，因此技能无论出现在哪里都以用户自己的语言呈现。参见[翻译](/features/administration/translations)。

创建技能时，在 `SKILL.md` 中键入或粘贴的 YAML frontmatter 会填充空的 **名称** 和 **描述**：`name: code-review-guidelines` 会得到名称“Code Review Guidelines”。frontmatter 会按真正的 YAML 解析，因此带引号和多行的值都能按原样读入。

在 **保存** 旁的 **描述此次变更** 中添加一句简短说明，为这次保存创建的版本加上标签（参见[版本历史](#version-history)）。

### 配套文件 {#supporting-files}

技能是一个小型文件夹，根目录有 `SKILL.md`，以及指令引用的文件，例如 `scripts/` 下的脚本、`references/` 下的详细文档、`templates/` 下可复用的输出模板以及 `assets/` 下的图片或其他资源。编辑器的文件面板以树状结构列出这些内容。**...** 菜单提供 **New File**、**New Folder**、**Upload** 和 **Upload Folder**。条目可重命名、删除或拖到其他文件夹。打开的文件提供 **Download** 按钮。文本文件还提供用于复制内容的 **Copy**。如果有权编辑该技能，还可以使用 **Compare revision**：它会在文件旁打开空白的 **Proposed revision** 窗格。将修改版本粘贴到那里，点击 **Compare** 标出更改，再使用箭头逐项查看。点击 **Apply to draft** 将右侧窗格内容填入文件，随后保存技能。Markdown 文件可 **Preview**，图片和 PDF 可直接打开，其他二进制文件可下载。

| 限制 | 数值 |
| :--- | :--- |
| 单个文件大小 | 10 MiB |
| 一个技能中所有文件的总大小 | 50 MiB |
| 每个技能的文件数 | 1,000 |

文本文件按文本存储，其他文件按二进制存储。`SKILL.md` 保持在根目录且必须是 UTF-8 文本。点击 **保存** 时，所有文件改动会一并写入。

### 导入技能 {#importing-skills}

**创建** 旁的箭头菜单中有三个导入入口：

- **导入** 接受一个或多个 `.zip`、`.skill`、`.json` 或 `.md` 文件，单次导入最大 200 MiB。`.skill` 文件就是 ZIP，按同样方式读取。ZIP 可以包含一个根目录下带 `SKILL.md` 的技能，也可以包含多个各自含有 `SKILL.md` 的技能文件夹。`.md` 文件会成为一个技能，该文件即为其 `SKILL.md`。JSON 文件是 Open WebUI 的技能导出，较旧的导出中带有单个 `content` 字段的也支持。包含符号链接或其他特殊文件的 ZIP 或 `.skill` 文件会被拒绝，并提示 `Archives cannot contain links or special files`。需要 **技能访问** 和 **导入技能** 权限。
- **从 URL 导入**（仅管理员）可从链接下载技能。参见[从 URL 导入](#importing-from-a-url)。
- **导入文件夹** 接受你电脑上的技能文件夹，或包含多个技能文件夹的目录，每个文件夹都有自己的 `SKILL.md`。需要 **技能访问** 和 **导入技能** 权限。

每次导入都会打开一个预览，列出每个技能及其名称、ID 和文件。对每一个技能，可以选择 **创建**、**创建副本**、**替换** 或 **跳过**。ID 或名称已存在的技能默认选中 **跳过**；为其指定唯一的 ID 和名称即可创建副本。对你有权编辑的已有技能会显示 **替换**，它会把导入内容保存为该技能的新版本，共享设置保持不变。新建的技能和副本默认为私有。

### 从 Markdown 导入 {#importing-from-markdown}

从 ZIP、文件夹或 `.md` 文件导入的技能，其名称和描述取自 `SKILL.md` frontmatter，ID 由名称生成；JSON 导出则自带这些信息：

```yaml
---
name: code-review-guidelines
description: Step-by-step instructions for thorough code reviews
---

# Code Review Guidelines

1. Check for correctness...
```

### 从 URL 导入 {#importing-from-a-url}

**创建** 旁的箭头菜单中的 **从 URL 导入** 可直接从网页加载技能，仅管理员可用。粘贴以下任一链接：

| 链接 | 导入的内容 |
| :--- | :--- |
| GitHub 仓库，例如 `https://github.com/owner/repo` | 仓库中的每个技能：每个含有 `SKILL.md` 的文件夹，或当 `SKILL.md` 位于根目录时的整个仓库 |
| GitHub 文件夹，`https://github.com/owner/repo/tree/<branch>/<folder>` | 该文件夹中的技能 |
| GitHub 的 `SKILL.md`，`https://github.com/owner/repo/blob/<branch>/<folder>/SKILL.md` | 该 `SKILL.md` 所在文件夹中的技能，含其所有文件 |
| 指向 `.zip`、`.skill`、`.json` 或 `.md` 文件的直接链接 | 该文件中的技能，按与上传相同的方式读取 |

GitHub 链接会按对应分支、标签或提交下载为仓库的 ZIP，因此技能到达时会带上其配套文件。包含 `/` 的分支名必须进行 URL 编码（`%2F`），或改用提交链接。从任意链接下载的 ZIP 或 `.skill` 文件会跳过技能文件夹之外的符号链接和其他特殊文件，因此仓库中其他地方存在此类链接时仍能正常导入。技能文件夹内部的符号链接或特殊文件会拒绝导入，并提示 `Archives cannot contain links or special files`。找到的技能会与上传时一样打开在导入预览中，由你决定创建哪些。

该链接在下载开始前以及每次重定向时，都会按与网页抓取相同的地址规则进行检查，因此在 [`ENABLE_LOCAL_WEB_FETCH`](/reference/env-configuration#enable_local_web_fetch) 关闭时，通向内网的链接会被拒绝。它最多跟随 5 次重定向，60 秒后放弃，最大 200 MiB。返回网页的链接会被拒绝，并提示请改用原始文件或 ZIP 下载链接；在 GitHub 上，上表中的仓库、文件夹和 `SKILL.md` 链接可直接使用。

### 通过 `/skills:create` 从对话生成 {#from-a-chat-with-skillscreate}

你刚在对话中走过的工作流程，无需自己动手书写就能变成技能。在该对话中输入 `/skills:create`，后面可以附上这个技能应涵盖的内容，模型会收集素材，按下述标准编写一份 `SKILL.md`，并用 `create_skill` 工具把它连同 `scripts/`、`references/`、`templates/` 或 `assets/` 下的配套文本文件保存到你的 **工作区 > 技能**。新技能为私有。完成后模型会报告名称、位置和一句话摘要，并且可以用 `update_skill_files` 修改你有权编辑的已有技能。

命令之后写下的所有内容都会被完整地视为编写指导。要引用的素材来源（路径、URL、“我们刚做过的事”、粘贴的笔记）和塑造结果的要求（重点、排除项、命名、风格）可以在一次请求中自由混合。

该命令需要：

- **技能访问** 工作区权限（管理员始终拥有该权限），
- 一个已启用内置工具、且在 **内置工具** 下打开了 **技能** 类别的模型，
- 一个**已有内容**的对话，因为对话才是原始素材。

服务端会先检查这三项，模型才可以保存任何内容。当对话已有内容且你拥有相应权限时，`/` 菜单中会提供该命令。

---

## 技能编写标准 {#skill-authoring-standard}

这是 Open WebUI 自身在通过 `/skills:create` 编写技能时遵循的标准，也应当用同样的标准来要求你自己的技能。

**Frontmatter**

| 键 | 规则 |
| :--- | :--- |
| `name` | 全小写并使用连字符，不含空格，最长 64 个字符。 |
| `description` | 清晰的描述，**最长 1024 个字符**，以句号结尾。写明这项能力，略过实现方式，不要重复技能名称，并避免使用“强大”“全面”“无缝”“高级”“健壮”之类的词。保存前请数一下字符数。 |
| `platforms` | `[macos]`、`[linux]` 或 `[windows]`，仅当技能使用与操作系统绑定的内容时才填写。可移植的技能请省略。 |

**正文小节，按此顺序**

1. `# <Human Title>`，以及一段简短引言：它做什么、不做什么、假设哪些东西已安装。
2. `## When to Use`，给出具体的触发短语。
3. `## Prerequisites`：确切的环境变量、凭据和安装步骤，或写 `None`。
4. `## How to Run`：标准工作流，通过模型实际拥有的工具来表述。
5. `## Quick Reference`：命令、路由、文件或 API 的扁平列表。
6. `## Procedure`：编号步骤，可直接复制粘贴。
7. `## Pitfalls`：已知的限制和失败模式。
8. `## Verification`：一个聚焦的检查，证明技能确实可用。

**工具的表述方式。** 用反引号标出工具名称，其中包括 `run_command`、`write_file` 和 `view_skill`，并把 shell 操作描述为通过 `run_command` 执行。凡是存在专门的读取或搜索工具时，都优先使用它们而不是原始 shell 工具。第三方 CLI 在流程步骤中使用没有问题，前提是明确说明智能体是通过 `run_command` 调用它们的。

**质量底线。** 命令、路由、路径、函数名、配置键和错误文本都要与源码中的写法完全一致；杜撰的标志位或 API 是技能出错的主要原因。保持 `SKILL.md` 便于速览，简单的流程大约 100 行，复杂的约 200 行，把大块内容放到别处：较大的脚本放在 `scripts/`，详细文档放在 `references/`，可复用输出放在 `templates/`，二进制或可视化资源放在 `assets/`。只指向其他技能的技能毫无价值；请写下真正完成工作的那一个。

---

## 将技能绑定到模型 {#binding-skills-to-a-model}

1. 进入**工作区 > 模型**。
2. 编辑一个模型，打开 **技能** 一行。
3. 选择你希望该模型始终可以访问的技能。
4. 点击 **保存并更新**。

使用该模型的每个新对话都会默认选中这些技能。清单中已经列出了用户可读的每个技能，因此只在模型需要在每个对话中都遵循某个技能时才绑定它。

---

## 技能管理 {#skill-management}

在技能工作区列表中，对你有权限编辑的技能使用省略号菜单（**...**）：

| 操作 | 说明 |
| :--- | :--- |
| **编辑** | 在编辑器中打开该技能 |
| **访问** | 直接从列表中打开该技能的访问设置。改动会随改随存。非管理员只有在拥有 **技能共享** 权限时才能看到 |
| **克隆** | 复制当前版本及其所有文件，创建一个私有副本并在编辑器中打开。副本的名称和 ID 会加上一个短随机后缀 |
| **导出 .skill** | 将技能及其所有文件下载为单个 `.skill` 文件（即包含技能文件夹的 ZIP）。导入时名称和描述取自 `SKILL.md` frontmatter，ID 由该名称生成；标签不会保留。若要保留 ID、名称、描述和标签，请使用 **导出 JSON**。需要 **技能访问** 和 **导出技能** 权限 |
| **导出 JSON** / **导出 ZIP** | 下载技能及其所有文件。需要 **技能访问** 和 **导出技能** 权限 |
| **分享** | 在 openwebui.com 上发布该技能及其所有文件。需要开启 **社区共享** 并拥有 **导出技能** 权限。参见[社区技能](#community-skills) |
| **删除** | 永久删除该技能及其全部版本历史（Shift+点击 可快速删除） |

**批量导出**：点击 **创建** 旁的箭头菜单中的 **导出 ZIP** 或 **导出 JSON**，可将所有可访问的技能导出为一个文件。ZIP 中每个技能一个文件夹。两者都需要 **技能访问** 和 **导出技能** 权限。

**启用/禁用切换**：非活跃的技能不会出现在清单和 `$` 提及中，即使它被绑定到模型也是如此。拥有写入权限的用户仍可让模型加载它们（参见[技能工具](#skill-tools)）。

### 社区技能 {#community-skills}

开启 **社区共享** 后（参见 [Open WebUI 社区](/ecosystem/community#turn-it-off)），技能工作区会连接到 openwebui.com：

- **发现技能** 位于技能列表底部，可打开 openwebui.com 上发布的技能。
- 从 openwebui.com 的技能页面导入的技能，会在你的实例中打开一个新的技能编辑器，并填好其名称、描述和所有文件。审阅后点击 **保存并创建** 即可添加。这需要 **技能访问** 和 **导入技能** 权限。
- 技能 **...** 菜单中的 **分享** 会在新标签页打开 openwebui.com，并新建一条包含该技能及其所有文件的帖子。在那边完成帖子之前不会有任何内容被发布。这需要 **导出技能** 权限，且单个技能分享总大小不超过 15 MiB。

---

## 版本历史 {#version-history}

每次改变技能名称、描述、翻译或文件的保存，都会把该技能的完整快照存为一个新版本。启用或停用技能以及修改其访问权限不会影响历史记录。升级前已存在的技能会从一个包含其当前内容的版本开始。

编辑器文件面板顶部的版本菜单列出 **当前** 和所有较早版本，按时间倒序排列，每页 20 条，每条附带作者和 **描述此次变更** 中的说明（没有说明时显示一个简短的版本 ID）。选择较早的版本会以只读方式打开，并提供两个操作：

- **与当前版本对比** 显示该版本与当前版本之间的差异：名称、描述和翻译，以及每个新增、删除或修改的文件，文本文件还会给出逐行差异。任一版本中超过 5000 行的文件不会给出逐行差异（`Diff is limited to 5000 lines per version`）。
- **设为生产环境** 会让该版本重新成为当前版本。这需要写入权限。如果在你打开该版本之后有人保存过该技能，切换会被拒绝，编辑器会提示重新加载最新状态。

每个较早版本旁的 **...** 中有 **删除**，供拥有写入权限的用户使用。基于已删除版本创建的版本会链接到其父版本，从而保持版本链完整。拥有 **导出技能** 权限时，文件面板的 **...** 菜单还可以把当前查看的版本导出为 `.skill`、JSON 或 ZIP。

如果你在编辑期间别人保存了该技能，你的保存会被拒绝，草稿会保留在编辑器中。横幅会提供 **重新加载最新版本**、**将草稿另存为副本** 或 **继续编辑**。

---

## 访问控制 {#access-control}

技能使用与其他工作区资源相同的[访问控制](/features/authentication-access/rbac)系统：

- **默认私有**：只有创建者可以查看和编辑新技能。
- **与用户或用户组共享**：通过编辑器中的 **访问** 按钮或列表菜单中的 **访问** 项授予 `read`（读取）或 `write`（写入）访问权限。非管理员只有在拥有 [**技能共享**](/features/authentication-access/rbac/permissions#2-sharing-permissions) 权限时才能看到这两处。
- **只读访问**：拥有读取权限的用户可以查看但不能编辑。编辑器显示“只读”标识。

:::caution 已附加的技能仍需要用户访问权限
将技能附加到模型**不会**绕过访问控制。当用户与模型对话时，Open WebUI 会检查该用户是否对每个已附加技能有读取权限。用户无法访问的技能会被静默排除。

**示例**：管理员创建一个私有技能并附加到共享模型。与此模型对话的普通用户将无法获得该技能，因为他们没有读取权限。

**解决方案**：确保需要使用模型技能的用户也对每个技能有读取权限（通过访问授权、用户组权限或将技能设为公开）。
:::

### 所需权限 {#required-permissions}

| 权限 | 控制内容 |
| :--- | :--- |
| **工作区 > 技能访问** | 访问技能工作区并创建/管理技能 |
| **工作区 > 导入技能** | 从 ZIP、`.skill`、文件夹、JSON 或 Markdown 导入技能，并打开来自 openwebui.com 的技能 |
| **工作区 > 导出技能** | 将技能及其版本导出为 `.skill`、ZIP 或 JSON，并向 openwebui.com 分享技能 |
| **共享 > 技能共享** | 与单个用户或用户组共享技能 |
| **共享 > 技能公开共享** | 使技能公开可访问 |

有关配置详情，请参阅[权限](/features/authentication-access/rbac/permissions)。

---

## 技能 API {#skills-api}

编辑器中的文件、版本、导入和导出功能由 `/api/v1/skills` 下的以下端点支撑。读取需要对该技能有读取权限；更改当前版本和删除版本需要写入权限。

| 端点 | 作用 |
| :--- | :--- |
| `GET /id/{id}/files` | 列出技能的文件及其路径、大小和编码。`version_id` 可指定某个历史版本。 |
| `GET /id/{id}/files/content` | 下载一个文件，需提供 `path` 和 `version_id`。 |
| `GET /id/{id}/history` | 列出版本，按时间倒序，每 `page` 20 条。 |
| `GET /id/{id}/history/{history_id}` | 返回一个版本及其文件列表。 |
| `GET /id/{id}/history/diff` | 列出 `from_id` 与 `to_id` 之间的变化：元数据以及新增、删除或修改的文件。带 `path` 的 `/history/diff/file` 返回某个文本文件的逐行差异。 |
| `POST /id/{id}/update/version` | 将某个已存储的版本设为当前版本。请求体携带 `version_id` 和 `expected_version_id`（你认为是当前版本的那个）；当它不再匹配时，调用返回 `409`。 |
| `DELETE /id/{id}/history/{history_id}` | 删除当前版本之外的某个版本，并将其子版本链接到其父版本。 |
| `POST /id/{id}/clone` | 以新的 `id` 和 `name` 复制该技能，可选从指定的 `version_id` 复制。副本为私有。 |
| `GET /export` | 以 `format=json`、`format=zip` 或 `format=skill` 导出技能。重复 `ids` 可选择多个技能；`format=skill` 只能指定一个。只有一个 id 时，`version_id` 用于导出某个历史版本。 |
| `POST /load/url` | 仅管理员。下载 `{"url": "..."}` 对应的技能（参见[从 URL 导入](#importing-from-a-url)）并以技能包返回，不保存任何内容。 |
| `POST /import/preview` | 读取上传的 ZIP、`.skill`、JSON 或 Markdown 文件（总计最大 200 MiB），并列出找到的技能，同时标记已存在的 ID 和名称。 |
| `POST /import` | 导入相同的上传内容，并附带 `decisions` 列表，每个技能一项：`action`（`create`、`copy`、`replace` 或 `skip`）、可选的 `id` 和 `name`，以及 `replace` 时所需的 `expected_version_id`。 |

`POST /create` 和 `POST /id/{id}/update` 通过 `files` 接收技能的文件，并可附带可选的 `commit_message` 为新版本加上标签。更新可以通过 `operations`（`put`、`move`、`delete`）修改单个文件。发送 `files` 或 `operations` 的更新需要 `expected_version_id`，若期间有人保存过该技能则返回 `409`。

---

## 使用场景 {#use-cases}

### 代码审查标准 {#code-review-standards}

将团队的审查清单写为技能：命名规范、错误处理模式、测试覆盖要求。附加到您的编程模型，使每次审查都遵循同样的标准。

### 写作风格指南 {#writing-style-guide}

在技能中记录语气、格式规则和术语。附加到内容写作模型。每份草稿都遵循您的品牌风格。

### 故障排查手册 {#troubleshooting-playbooks}

将常见问题的操作手册编码为技能：“先检查日志，验证配置，测试连接，如果 X 则上报。”模型遵循与您的高级工程师相同的诊断步骤。

### 工具使用指南 {#tool-usage-instructions}

将技能与 Open Terminal 配合使用，教模型*如何*更好地使用它。“始终检查退出码。在脚本中使用 `set -e`。对需要超过 10 秒的命令使用流式输出。”

---

## 局限性 {#limitations}

### 纯文本 {#plain-text-only}

Open WebUI 会存储技能的脚本供模型阅读。要运行它，需要能够执行代码的工具，例如[Open Terminal](/features/open-terminal)或代码解释器。对于计算、API 调用或系统访问，请使用[工具](/features/extensibility/plugin/tools)。

### $ 提及时的上下文窗口 {#context-window-with--mention}

没有技能工具时，选中的技能会随每条消息进入系统提示词。在上下文窗口较小的模型上，过长的技能会挤占对话空间。

### 懒加载需要函数调用 {#lazy-loading-requires-function-calling}

清单和技能工具需要启用 **内置工具** 的[原生函数调用](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)。参见[绑定到模型的技能](#model-attached-skills)。
