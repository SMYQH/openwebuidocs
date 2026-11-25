---
sidebar_position: 100
title: "理解设置"
---

# 理解设置 {#understanding-settings}

**Open WebUI 有两个独立的设置区域，而不是一个。**

Open WebUI 从一开始就是面向多用户设计的。即使你是唯一使用者，系统架构也假定同一个实例上可能会有很多用户。因此平台需要两层配置：一层属于控制整个实例的管理员，另一层属于控制个人体验的每位用户。

---

## 两个设置区域 {#the-two-settings-areas}

### 管理员设置（全局） {#admin-settings-global}

| | |
| :--- | :--- |
| **位置** | 个人资料头像 > **Settings**，然后进入 **Admin** 区域 |
| **访问权限** | 仅管理员 |
| **作用范围** | 整个实例和所有用户 |

管理员设置控制的是 Open WebUI 实例本身：API 连接、功能开关、安全策略和默认行为。你可以把它理解为**整栋楼的控制面板**——它决定了哪些东西被安装、哪些能力对所有人开放。

**典型示例：**

- 与 Ollama、OpenAI 及其他提供商的连接
- 启用或禁用网页搜索、图片生成与代码执行
- [已选择和置顶的模型](/features/workspace/models#selected-and-pinned-models-admin)与参数预设
- RBAC 策略、SSO 配置和注册限制

---

### 用户设置（个人） {#user-settings-personal}

| | |
| :--- | :--- |
| **位置** | 头像菜单 > **Settings** |
| **访问权限** | 所有用户（包括管理员） |
| **作用范围** | 仅当前用户本人 |

用户设置控制的是个人偏好：你的默认模型、界面主题、语言、通知偏好，以及管理员已开启功能上的个人开关。你可以把它理解为**自己房间里的恒温器**——你可以调整属于自己的体验，但前提仍由整栋楼的基础设施决定。

**典型示例：**

- 系统提示词，以及在模型选择器中用**设为默认**保存的默认模型
- 界面主题与语言
- 自动补全、富文本输入等功能的个人开关

**设置 > 通用**下的**主题**和**语言**保存在浏览器中，而不是你的账户里，因此它们不会跟随你换到另一个浏览器或设备。首次打开 Open WebUI 的浏览器会使用 **系统**主题，以及 [`DEFAULT_LOCALE`](/reference/env-configuration#default_locale) 设置的语言；如果管理员没有设置语言，则使用浏览器自身的语言。

---

## 它们如何协同工作 {#how-they-work-together}

很多功能都遵循一种**双层模式**：

1. 管理员决定该功能是否**可提供**（管理员设置）
2. 每位用户决定自己是否**要使用**（用户设置）

**示例：自动补全（AI 驱动的输入建议）**

| 层级 | 设置位置 | 效果 |
|-------|-----------------|--------|
| 管理员启用 | Settings > Interface（管理员区域） | 让自动补全在实例中**可用** |
| 用户启用 | Settings > Interface | 只为**你本人**打开自动补全 |

:::important 关键规则
如果管理员在全局范围**关闭**某个功能，用户**无法**自行启用它。管理员设置永远是上限。
:::

这一模式适用于网页搜索、图像生成、代码解释器等功能。管理员决定**可以使用哪些功能**，用户决定**要使用哪些功能**。

---

## 实例级起始值 {#instance-wide-starting-values}

功能开关是上限。有一项管理员控制恰好相反：**默认界面设置**决定每个人的 **设置 > 界面** 页面从哪里开始，每个人仍然可以自行修改其中任何一项。某个从未被改动过的选项会一直跟随你的默认值，因此之后对它所做的更改同样会传递给他们。

可在 **设置 > 通用**（管理员区域） 下的 **UI > 默认界面设置** 中配置，或通过 `DEFAULT_INTERFACE_SETTINGS` 环境变量配置。

[**了解默认界面设置 →**](/features/administration/interface-defaults)

---

## 快速对照 {#quick-reference}

| | 管理员设置 | 用户设置 |
|---|---|---|
| **作用范围** | 整个实例（所有用户） | 单个用户 |
| **访问权限** | 仅管理员 | 所有人 |
| **控制内容** | API 连接、功能开关、安全、默认值 | 主题、默认模型、个人偏好 |
| **覆盖行为** | 用户无法覆盖 | 可在管理员允许范围内自定义 |

唯一有意为之的例外是[默认界面设置](/features/administration/interface-defaults)，管理员把它作为起始值而非上限来设置；每位用户仍然可以自行修改其中任何一项。

---

## 常见场景 {#common-scenarios}

**“我在自己的设置里打开了某个功能，但它不生效。”**
请先确认管理员是否已在全局范围内启用该功能。只有当管理员先让实例层面可用时，你的个人开关才会生效。

**“我是管理员。OpenAI 或 Ollama 的连接要在哪里配置？”**
前往 设置 > 连接（管理员区域）。这些连接是实例级的，会被所有用户共享。

**“我想用自己的 API 密钥，但不想和服务器共享。”**
在 Tether 应用中添加的连接会将密钥保存在你的电脑上，参见[自带模型与工具](/ecosystem/tether#bring-your-own-models-and-tools)。管理员可在 **Settings > Connections**（管理员区域）中添加共享连接。

**“我设置了系统提示词，但管理员的模型设置覆盖了它。”**
Open WebUI 按顺序组合工作区模型的系统提示词、文件夹的提示词（如果有），以及聊天的提示词或账户提示词。如果聊天没有自己的提示词，就使用账户提示词。参见[聊天参数](/features/chat-conversations/chat-features/chat-params#how-system-prompts-combine)。

**“设置 > 界面 中的某个开关旁边写着 Default。这是什么意思？”**
这意味着你从未改动过该选项，因此它一直在跟随管理员配置的实例级[默认界面设置](/features/administration/interface-defaults)。改动之后它就归你了；把它改回当前默认值，它又会重新跟随。

**“界面太小，看起来不太舒服。”**
在 **设置 > 界面** 的 **UI** 区域顶部调高 **UI 缩放**。它会放大整个应用，并随你的账户保存。

点击 **UI 缩放**旁边的 **Default** 可显示滑块。它的范围从 `1x` 到 `1.5x`。旁边的减号和加号按钮（屏幕阅读器会朗读为 **Decrease UI Scale** 和 **Increase UI Scale**）每次调整 `0.1`。它们是按钮，不是键盘快捷键。点击数值可回到默认值。

**“我能改字体吗？”**
**Font Family** 位于 **Settings > Interface** 中的 UI Scale 正下方。点击 **Default** 显示文本框，然后输入字体名称，例如 `Aptos`。

该字体必须已经安装在你当前使用的电脑上。系统不会下载字体，因此输入一个未安装的名称只会保留标准字体且不会报错。清空输入框即可恢复。预格式化代码块无论如何都会保持标准字体。

**“Floating Quick Actions 和 Image Compression 旁边的 Manage 按钮是做什么的？”**
每个按钮只在对应的开关打开时才会出现。屏幕阅读器会朗读为 **Open Modal To Manage Floating Quick Actions** 和 **Open Modal To Manage Image Compression**。

- **Floating Quick Actions** 位于 **Chat** 区域，控制你在已完成的回复中选中文字时出现的工具栏。它的 **Manage** 对话框 **Quick Actions** 列出该工具栏的按钮。点击 **Default** 可切换到 **Custom**，其中以内置的 **Ask** 和 **Explain** 按钮开始。用加号图标添加按钮，为每个按钮填写 **Button Label**、**Button ID** 和 **Button Prompt**，然后点击 **Save**。再次点击 **Custom** 会回到内置按钮，列表为空时同样使用内置按钮。点击某个按钮会把它对应的提示词填入聊天输入框，但不会发送。在提示词中，`{{CONTENT}}` 变成选中的文本，`{{SELECTED_CONTENT}}` 变成以 `>` 引用的选中文本，`{{INPUT_CONTENT}}` 则会先打开 **Ask a question** 输入框，并插入你在其中输入的内容。请为每个按钮设置独立的 **Button ID**：当两个按钮共用同一个 ID 时，它们都会执行第一个按钮的提示词。
- **Image Compression** 位于 **File** 区域，在图片发送或存储之前缩小它们。它的 **Manage** 对话框以像素为单位设置 **Image Max Compression Size** 的 **Width** 和 **Height**。图片会保持宽高比，已经同时满足两个限制的图片保持原样。它适用于聊天和笔记中附加的图片，以及开启 **Compress Images in Channels** 时频道中的图片。

**“我在 设置 > 账户 中输入了新密码并点击保存，但旧密码仍然有效。”**
**设置 > 账户** 底部的 **Save** 只保存你的个人资料和用户变量。它从不发送密码字段。要修改密码，请在 **Password** 区域点击 **Show** 打开 **Change Password**，填写 **Current Password**、**New Password** 和 **Confirm Password**，然后点击它们下方的 **Update password**。

成功后你会看到 `Password updated. Please sign in again.`，Open WebUI 会把你登出。任何设备上登录你账户的其他会话会同时失效，因此请在使用 Open WebUI 的每个地方用新密码重新登录。API 密钥仍然有效。

| 消息 | 原因 |
| :--- | :--- |
| `The passwords you entered don't quite match. Please double-check and try again.` | **New Password** 与 **Confirm Password** 不一致。没有发送任何内容。 |
| `The password provided is incorrect. Please check for typos and try again.` | **Current Password** 与你账户存储的密码不匹配。 |
| `The password does not meet the required validation criteria.`，或管理员自己的提示 | 新密码未通过 [`ENABLE_PASSWORD_VALIDATION`](/reference/env-configuration#enable_password_validation) 的规则集。 |
| `The requested action has been restricted as a security measure.` | 该实例使用受信任标头登录（[`WEBUI_AUTH_TRUSTED_EMAIL_HEADER`](/reference/env-configuration#webui_auth_trusted_email_header)），因此密码由 Open WebUI 前面的代理管理。 |

Open WebUI 在首次 OAuth 或 LDAP 登录时创建的账户会得到一个没人看到的随机密码，因此 **Current Password** 永远不匹配，你会收到密码错误的消息。管理员可以在 **Admin Panel > Users** 下的 **Edit User** 对话框中用 **New Password** 为这类账户设置密码。之后该密码就能在这里用作 **Current Password**。当管理员关闭 [`ENABLE_LOGIN_FORM`](/reference/env-configuration#enable_login_form) 或 [`ENABLE_PASSWORD_CHANGE_FORM`](/reference/env-configuration#enable_password_change_form) 时，整个 **Password** 区域都会隐藏。

**“我是管理员。能让所有人使用相同的界面选项开始吗？”**
可以，通过[默认界面设置](/features/administration/interface-defaults)。它决定了每个人的起点；之后每个人仍可自行修改其中任何一项。

:::tip 第一次当管理员？
建议先从 **设置 > 连接**（管理员区域） 开始，连接模型提供商（Ollama、OpenAI 等），再前往 **设置 > 界面**（管理员区域） 按需为用户启用或禁用功能。
:::
