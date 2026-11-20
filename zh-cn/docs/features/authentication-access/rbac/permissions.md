---
sidebar_position: 3
title: "权限"
---


Open WebUI 提供了一个灵活的权限系统，允许管理员为用户配置访问控制和功能可用性。这实现了对用户在应用程序中可以访问和修改的内容的细粒度控制。

管理员可以通过两种主要方式管理权限：
1.  **默认权限：** 通过**管理面板 > 用户 > 用户组 > 默认权限**设置适用于所有用户（包括管理员）的基础权限。
2.  **用户组权限：** 通过**管理面板 > 用户 > 用户组**创建具有特定权限覆盖的用户组（例如，拥有图像生成访问权限的"高级用户"组）。

拥有 `Pending` 角色的用户在获得批准之前没有访问权限，`Admin` 用户拥有完整的管理员访问权限，而 `User` 账户受下面描述的权限系统约束。

:::warning RBAC 范围边界
RBAC 权限控制用户在 Open WebUI 内部能做什么。

RBAC 不替代提供商端的最小权限设计。对于 OpenAI 兼容的提供商/代理（包括 LiteLLM），请使用部署所需最小范围的凭据进行配置。
:::

:::info 权限逻辑
Open WebUI 中的权限是**累加**的。
*   用户的有效权限是**全局默认值**和其所有**用户组成员资格**的组合，包括他们所属用户组的所有父级用户组（参见[嵌套用户组](/features/authentication-access/rbac/groups#nested-groups)）。
*   **True 优先于 False**：如果*任何*来源（全局默认值或*任何*单个用户组）授予了某个权限，用户**将**拥有该权限。
*   **不存在"拒绝"功能**：您不能使用特定用户组来"取消"另一个用户组或全局默认值授予的权限。要限制某个功能，必须在全局默认值*和*用户所属的**所有**用户组中将其禁用（包括父级用户组）。
:::

:::tip 最佳实践：最小权限原则
由于权限是**累加**的，推荐的安全策略是从**限制**开始：
1.  **最小化全局默认权限**：将默认权限（**管理面板 > 用户 > 用户组 > 默认权限**）配置为仅包含*所有用户绝对必须*拥有的内容。
2.  **通过用户组授权**：创建特定用户组（例如"创作者"、"高级用户"）来明确**授予**高级功能，如图像生成或文件上传。

这种方式确保新用户不会意外获得敏感功能的访问权限，同时允许您通过简单地将用户添加到相关用户组来轻松提升权限。
:::

## 权限类别 {#permission-categories}

权限分为五个主要类别：**工作区**、**共享**、**对话**、**功能**和**设置**。

有些开关只有在整个实例启用对应功能时才会显示，例如**笔记共享**、**API Keys** 和**网页搜索**。隐藏的开关会保留其取值。管理员不受本页任何权限的限制。

### 1. 工作区权限 {#1-workspace-permissions}
控制对"工作区"部分的访问，用户在此创建和管理资源。
某些权限**依赖**于其他权限（例如，如果无法访问模型工作区，就无法导入模型）。

| 权限 | 说明 |
| :--- | :--- |
| **模型访问** | **（父级）** 访问**模型**工作区以创建或编辑自定义模型。 |
| **模型导入** | *（需要模型访问）* 从 JSON/文件导入模型的能力。 |
| **模型导出** | *（需要模型访问）* 将模型导出到文件的能力。 |
| **隐藏模型** | *（需要模型访问）* 在工作区模型中选择隐藏模型作为基础模型的能力（[`USER_PERMISSIONS_WORKSPACE_MODELS_HIDDEN`](/reference/env-configuration#user_permissions_workspace_models_hidden)）。默认关闭。 |
| **知识库访问** | 访问**知识库**工作区以管理知识库。 |
| **提示词访问** | **（父级）** 访问**提示词**工作区以管理自定义系统提示词。 |
| **提示词导入** | *（需要提示词访问）* 导入提示词的能力。 |
| **提示词导出** | *（需要提示词访问）* 导出提示词的能力。 |
| **工具访问** | **（父级）** 访问**工具**工作区以管理函数/工具。当 [`ENABLE_PLUGINS`](/reference/env-configuration#enable_plugins) 或 [`ENABLE_TOOLS`](/reference/env-configuration#enable_tools) 为 `false` 时，该权限及其"导入"和"导出"子开关会被隐藏，因为此时工具工作区并不存在。 |
| **工具导入** | *（需要工具访问）* 导入工具的能力。它如何影响代码改动请参见[版本历史](/features/extensibility/plugin/tools#version-history)。 |
| **工具导出** | *（需要工具访问）* 导出工具的能力。 |
| **技能访问** | **（父级）** 访问**技能**工作区以创建和管理可复用指令集。使用 [`/skills:create`](/features/workspace/skills#from-a-chat-with-skillscreate) 同样需要该权限。 |
| **导入技能** | *（需要技能访问）* 将技能导入技能工作区（参见[导入技能](/features/workspace/skills#importing-skills)和[社区技能](/features/workspace/skills#community-skills)）。 |
| **导出技能** | *（需要技能访问）* 从技能工作区导出技能（参见[技能管理](/features/workspace/skills#skill-management)和[社区技能](/features/workspace/skills#community-skills)）。 |

:::danger 工具访问 = 等同 Root 级别的访问权限
**将工具访问权限视为等同 root 的访问权限。** 授予用户创建或导入工具的访问权限等同于给予其服务器的 shell 访问权限，因为工具和函数会执行任意 Python 代码。只将此权限授予您信任能直接访问服务器的用户。如果您为不受信任的用户启用此权限，则是在接受在主机上任意执行代码的风险。有关完整详情，请参阅[插件安全警告](/features/extensibility/plugin/)。
:::

### 2. 共享权限 {#2-sharing-permissions}
控制用户可以与社区共享或公开的内容。

每个**（父级）**权限决定用户是否能够共享该类型的资源。没有它，**访问**按钮会被隐藏，服务器也会拒绝该类型的共享变更。下面的**公开共享**和**允许共享给**权限决定用户可以添加哪些受众。

如果一次共享变更请求了用户无权添加的受众，将以 `403` 拒绝（`You do not have permission to share with the requested audience`）。保存某个项目永远不会改变它的共享设置。即便对管理员而言，文件夹也永远不能公开，只有对话分享链接可以对没有账户的人开放。

| 权限 | 说明 |
| :--- | :--- |
| **共享模型** | **（父级）** 共享模型（使其他人可访问）的能力。 |
| **公开模型** | *（需要共享模型）* 使模型可公开发现的能力。 |
| **共享知识库** | **（父级）** 共享知识库的能力。 |
| **公开知识库** | *（需要共享知识库）* 使知识库公开的能力。 |
| **共享提示词** | **（父级）** 共享提示词的能力。 |
| **公开提示词** | *（需要共享提示词）* 使提示词公开的能力。 |
| **共享工具** | **（父级）** 共享工具的能力。 |
| **公开工具** | *（需要共享工具）* 使工具公开的能力。 |
| **共享技能** | **（父级）** 共享技能的能力。 |
| **公开技能** | *（需要共享技能）* 使技能公开的能力。 |
| **共享笔记** | **（父级）** 共享笔记的能力。 |
| **公开笔记** | *（需要共享笔记）* 使笔记公开的能力。 |
| **共享文件夹** | 将对话文件夹及其中的对话共享给特定用户或用户组的能力。参见[共享文件夹](/features/chat-conversations/chat-features/conversation-organization#sharing-folders)。 |
| **对话公开共享** | *（需要共享对话）* 使对话分享链接可被该实例中每个已登录用户访问的能力。打开链接仍需要登录。禁用时，用户仍可通过访问控制选择器与特定用户或用户组共享对话，但非管理员的"公开"选项将被隐藏。管理员始终豁免。 |
| **对话开放共享** | *（需要共享对话）* 使对话分享链接无需登录即可被任何持有链接的人阅读的能力。这是唯一会把内容暴露到实例之外的权限。默认关闭。参见[开放链接](/features/chat-conversations/chat-features/chatshare#open-links-no-sign-in)。 |
| **日历公开共享** | *（需要功能 > 日历）* 可以向所有具备日历功能的用户授予读取或写入权限。未启用此权限时，所有者仍可与特定用户或用户组共享日历。 |
| **允许共享给用户** | 与**特定用户**共享的能力（[`USER_PERMISSIONS_ACCESS_GRANTS_ALLOW_USERS`](/reference/env-configuration#user_permissions_access_grants_allow_users)）。 |
| **允许共享给用户组** | 与**用户组**共享的能力（[`USER_PERMISSIONS_ACCESS_GRANTS_ALLOW_GROUPS`](/reference/env-configuration#user_permissions_access_grants_allow_groups)）。 |

面板**共享权限**部分中的每个开关默认都是关闭的，只有当其行中注明的父级权限打开时才会显示公开开关。两个**允许共享给……**行位于单独的**访问授权**部分，默认打开。关闭**允许共享给用户组**后，**添加访问**选择器不会列出任何用户组；关闭**允许共享给用户**后，它不会列出任何用户。

:::warning 升级后请重新检查工具与笔记的公开共享

在从早于**公开共享工具**和**公开共享笔记**的版本升级而来的实例上，管理面板过去会把这两个开关显示为开启，而后端仍然拒绝该操作。当时在该页面保存任何权限都会把它们持久化为已启用，从而授予了从未配置过的公开工具与笔记共享。现在面板与实际执行已经一致，但已经写入数据库的值不会回滚。

如果你在受影响的版本上保存过默认权限，请打开**管理面板 > 用户 > 用户组**，编辑**默认权限**并确认这两个开关的状态符合你的预期。用户组级别的覆盖同样值得检查。

:::

### 3. 对话权限 {#3-chat-permissions}
控制对话界面中用户可用的功能。

| 权限 | 说明 |
| :--- | :--- |
| **对话控制** | **（父级）** 访问高级对话设置。禁用后，对话中**模型控制**菜单里的**控制**以及**设置 > 通用**中的**系统提示词**和**高级参数**部分会被隐藏。[模型控制](/features/workspace/models#using-model-controls-in-chat)仍然可用，因此管理员仍可提供诸如思考级别之类的选项，而无需开放完整的**控制**部分。 |
| **模型 Valves** | *（需要对话控制）* 访问 [valves](/features/extensibility/plugin/development/valves)（[`USER_PERMISSIONS_CHAT_VALVES`](/reference/env-configuration#user_permissions_chat_valves)），包括聊天输入框中管道模型的 **Valves** 按钮。 |
| **系统提示词** | *（需要对话控制）* 编辑对话系统提示词的能力。 |
| **参数** | *（需要对话控制）* 调整 LLM 参数（如温度、top_k）的能力。禁用后，对话中以及**设置 > 通用**里的**高级参数**部分会被隐藏。这只是隐藏界面：用户仍可通过 API 设置参数。这一取舍让管理员既能隐藏面板，又能继续提供[模型控制](/features/workspace/models#using-model-controls-in-chat)。 |
| **文件上传** | 向对话上传文件的能力。 |
| **网页上传** | 通过 URL 将网页附加到对话的能力，使用消息输入框附加菜单中的**附加网页**（[`USER_PERMISSIONS_CHAT_WEB_UPLOAD`](/reference/env-configuration#user_permissions_chat_web_upload)）。默认开启。禁用后该选项会置灰并拒绝附加。管理员始终豁免。 |
| **删除对话** | 删除对话的能力（[`USER_PERMISSIONS_CHAT_DELETE`](/reference/env-configuration#user_permissions_chat_delete)）。默认开启。禁用后，所有删除对话的控件都会被隐藏，包括**删除所有对话**，连同其中的对话一起删除文件夹也会被拒绝。归档仍然可用。 |
| **删除消息** | 删除单条消息的能力。 |
| **编辑消息** | 编辑消息的能力（[`USER_PERMISSIONS_CHAT_EDIT`](/reference/env-configuration#user_permissions_chat_edit)），既包括自己的消息，也包括回复。 |
| **继续响应** | 对截断的响应使用"继续"功能的能力。 |
| **重新生成响应** | 重新生成 AI 响应的能力。 |
| **评价回复** | 可以给回复点赞或点踩。 |
| **分享对话** | 为对话生成分享链接的能力（[`USER_PERMISSIONS_CHAT_SHARE`](/reference/env-configuration#user_permissions_chat_share)）。若希望被你分享的人可以回复，请参见[允许回复](/features/chat-conversations/chat-features/chatshare#allowing-replies)。 |
| **导出对话** | 导出对话的能力（[`USER_PERMISSIONS_CHAT_EXPORT`](/reference/env-configuration#user_permissions_chat_export)）。默认开启。禁用后，所有下载或复制完整对话的选项都会被隐藏，包括文件夹的**导出**和**导出对话**。 |
| **允许对话导入** | 导入对话（将先前导出的对话重新上传到 Open WebUI）以及[分叉对话](/features/chat-conversations/chat-features/)或[克隆他人共享的对话](/features/chat-conversations/chat-features/chatshare#cloning-or-forking-a-shared-chat)（把现有对话复制为新对话）的能力（[`USER_PERMISSIONS_CHAT_IMPORT`](/reference/env-configuration#user_permissions_chat_import)）。默认开启。禁用后，**设置 > 数据控制**中的**导入对话**、共享对话上的**克隆对话**按钮、助手回复下方的**分叉对话**操作以及聊天输入框 `/` 菜单中的 `/fork` 条目都会对非管理员隐藏。管理员始终豁免。 |
| **语音转文字** | 使用语音输入的能力。 |
| **文字转语音** | 使用语音输出的能力。 |
| **允许通话** | 发起[语音模式](/features/chat-conversations/chat-features/voice-mode)通话的能力，在标准通话模式和实时通话模式下均可用。 |
| **多模型** | 同时使用多个模型的能力（[`USER_PERMISSIONS_CHAT_MULTIPLE_MODELS`](/reference/env-configuration#user_permissions_chat_multiple_models)）。禁用后，对话只使用其第一个模型。 |
| **临时对话** | **（父级）** 切换"临时对话"（隐身模式/关闭历史记录）的能力。**注意：** 为保护隐私，此模式下后端文档解析被禁用。 |
| **侧边对话** | 打开[侧边对话](/features/chat-conversations/chat-features/#tabs-side-panel)的能力（[`USER_PERMISSIONS_CHAT_SIDE_CHAT`](/reference/env-configuration#user_permissions_chat_side_chat)）。默认关闭。管理员始终拥有。用户组权限表单仅在**允许临时对话**打开时显示该开关。 |
| **强制临时** | *（需要临时对话）* **限制**用户*始终*使用临时对话（禁用历史记录）（[`USER_PERMISSIONS_CHAT_TEMPORARY_ENFORCED`](/reference/env-configuration#user_permissions_chat_temporary_enforced)）。 |

**设置**中的**音频**标签页需要**允许语音转文字**、**允许文字转语音**和**允许通话**三者中的至少一项。

### 4. 功能权限 {#4-features-permissions}
控制对广泛平台能力的访问。

| 权限 | 说明 |
| :--- | :--- |
| **API Keys** | 非管理员用户在用户设置中生成个人访问令牌（API Keys）的能力。 |
| **笔记** | 访问"笔记"功能，包括聊天输入框中的**附加笔记**。 |
| **频道** | 访问"频道"功能（[`USER_PERMISSIONS_FEATURES_CHANNELS`](/reference/env-configuration#user_permissions_features_channels)，包含实时频道消息和频道自动化）。 |
| **加密频道** | 在私信和私密群组频道中使用[加密对话](/features/channels/encrypted-chats)的能力（[`USER_PERMISSIONS_FEATURES_ENCRYPTED_CHANNELS`](/reference/env-configuration#user_permissions_features_encrypted_channels)）。同时需要**频道**权限。默认关闭。 |
| **文件夹** | 使用文件夹整理对话的能力。 |
| **网络搜索** | 使用网络搜索集成的能力。 |
| **图像生成** | 使用图像生成工具。为 AUTOMATIC1111 连接设置 Model IDs 后，此权限也允许用户切换服务器已加载的模型，变更对所有用户生效。见下方说明。 |
| **视频生成** | 使用[视频生成](/features/chat-conversations/image-generation-and-editing/video-generation)（[`USER_PERMISSIONS_FEATURES_VIDEO_GENERATION`](/reference/env-configuration#user_permissions_features_video_generation)）。默认关闭，管理员始终拥有此权限。视频生成启用时才会显示此开关。 |
| **代码解释器** | 使用 Python 代码解释器的能力。手动执行代码（代码块上的**运行**按钮）没有单独的权限，它对所有人都遵循 [`ENABLE_CODE_EXECUTION`](/reference/env-configuration#enable_code_execution)。参见[手动代码执行](/features/chat-conversations/chat-features/code-execution/python#manual-code-execution-pyodide)。 |
| **记忆** | 访问用于持久化用户上下文的记忆功能。收回该权限会隐藏**个性化**设置标签页、屏蔽记忆 API 端点、不向模型提供记忆工具，并阻止已存储的记忆被注入聊天的系统上下文中。注入检查会在每次聊天请求时于服务端执行，因此仍在请求记忆的客户端也不会得到它。管理员始终不受此限制。 |
| **自动化** | 非管理员用户可访问自动化页面，并创建、编辑、运行、暂停或删除自己的定时自动化。能编辑文件夹的用户也能暂停向该文件夹发布内容的自动化。见[文件夹](/features/chat-conversations/chat-features/automations#folders)。 |
| **日历** | 访问日历功能，用于创建日历、管理事件和查看共享日历。 |
| **子智能体** | 使用 `delegate_task` 和 `timer` 工具（[`USER_PERMISSIONS_FEATURES_SUBAGENTS`](/reference/env-configuration#user_permissions_features_subagents)）。启用[子智能体](/features/chat-conversations/chat-features/subagents)后才会显示此开关。 |
| **用户 Webhooks** | 用户设置其个人 Webhook URL（位于 **设置 > 账户**）以接收通知的能力。默认禁用。 |

:::info 图像生成与当前启用模型

AUTOMATIC1111 只加载一个 checkpoint，并用它生成图像。如果已为 AUTOMATIC1111 连接设置 **Model IDs**，有权访问该连接的用户选择其他模型时，会切换服务器已加载的 checkpoint，影响该服务器上的所有用户，直到再次切换。将 **Model IDs** 留空即可避免这种情况。

其他连接类型接受在每次请求中指定模型，因此用户的选择只影响自己的生成。可以在[图像生成](/features/chat-conversations/image-generation-and-editing#set-up-a-connection)的连接**访问控制**中设置用户可以使用哪些连接。

:::

:::info 自动化权限范围

对于自动化访问：

1. **非管理员的权限检查**：拥有 `user` 角色的用户需要 **功能 > 自动化**（`features.automations`）权限。
2. **管理员免于 `features.automations`**：拥有 `admin` 角色的用户无需该特定权限即可访问自动化。

默认权限可通过 [`USER_PERMISSIONS_FEATURES_AUTOMATIONS`](/reference/env-configuration#user_permissions_features_automations) 进行配置。

:::

:::info 日历权限范围

对于日历访问：

1. **非管理员的权限检查**：拥有 `user` 角色的用户需要 **功能 > 日历**（`features.calendar`）权限。
2. **管理员免于 `features.calendar`**：拥有 `admin` 角色的用户无需该特定权限即可访问日历。
3. **直接链接会被重定向**：没有访问权限时，打开 `/calendar` 会跳转到首页。

默认权限可通过 [`USER_PERMISSIONS_FEATURES_CALENDAR`](/reference/env-configuration#user_permissions_features_calendar) 进行配置。

:::

### 5. 设置权限 {#5-settings-permissions}
控制对用户设置区域的访问。

| 权限 | 说明 |
| :--- | :--- |
| **界面设置访问** | 在用户设置中访问和修改界面设置的能力。 |

:::info 界面设置访问与实例默认值

收回该权限会隐藏**界面**页面，因此受影响的人只能沿用你所配置的[默认界面设置](/features/administration/interface-defaults)。保留该权限时，这些默认值只是一个起点，每个人都可以自行更改。管理员不受此限制。

它的影响范围仅止此。来自此类用户的保存请求中，界面字段会被丢弃，其余部分照常保存，因此系统提示词、置顶模型、音频、通知和快捷键仍然可以保存。**允许聊天系统提示词**对系统提示词而言也是同样的处理。

唯一的例外是用户在模型选择器中通过**设为默认**保存的**默认模型**。它以界面字段的形式存储，因此当该权限关闭时将不再被保存。

没有任何权限会整体锁定个人设置。该权限只是隐藏一个页面并过滤该页面上的字段，不做更多事情。

:::

:::info API Keys 权限范围

对于 API Key 创建：

1.  **需要全局开关**：必须在**设置 > 认证 > API Keys**（管理员区域） 中全局启用该功能。如果此项关闭，*任何人*都无法生成密钥。
2.  **非管理员的权限检查**：拥有 `user` 角色的用户必须具有 `features.api_keys` 权限。
3.  **管理员免于 `features.api_keys`**：当 API Keys 全局启用时，拥有 `admin` 角色的用户可以生成 API Keys，无需该特定权限。

:::

:::tip 最佳实践：创建管理员用户组

**为应对未来的权限变更，请为管理员创建专用用户组：**

1.  **创建"管理员"用户组**，通过**管理面板 > 用户 > 用户组**
2.  将所有管理员用户**添加到此用户组**
3.  根据需要向该用户组**授予用户可见功能权限**（例如，为非管理员组成员授予 API Keys 权限）

这种方式确保当新增的权限适用于管理员时，您可以通过用户组轻松授予所有管理员，而无需修改各个用户设置。它还提供了对哪些管理员可以访问哪些功能的细粒度控制。

:::

## 环境变量 {#environment-variables}

虽然推荐通过 UI 管理权限，但初始默认值可以通过环境变量设置。这些变量通常以 `USER_PERMISSIONS_` 为前缀。
*   `ENABLE_IMAGE_GENERATION=True`
*   `ENABLE_WEB_SEARCH=True`
*   `USER_PERMISSIONS_CHAT_FILE_UPLOAD=True`

有关有效变量的完整列表，请参阅[环境配置](/reference/env-configuration)指南。
