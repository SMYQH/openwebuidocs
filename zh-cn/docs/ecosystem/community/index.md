---
title: "Open WebUI Community"
sidebar_position: 0
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Open WebUI Community {#open-webui-community}

<ThemedImage
  alt="Open WebUI 社区：一面帖子看板，其中一张被取出并指向你的实例"
  sources={{
    light: useBaseUrl('/images/banners/community-platform-light.svg'),
    dark: useBaseUrl('/images/banners/community-platform-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**使用别人已经构建好的模型、提示、技能和插件，也把你自己的分享出去。**

你不必亲手编写每一条系统提示、每一个 Tool 或 Function。[Open WebUI 社区](https://openwebui.com/)是一个独立的网站，人们在那里发布自己为 Open WebUI 构建的东西，在那里发布的任何内容都可以用几次点击导入你的实例。

你在运维这个服务器吗？[面向管理员](#for-admins)一节讲清了谁可以通过该网站把代码带到你的服务器上、哪些内容会到达 openwebui.com，以及如何把它关闭。

## 导入帖子 {#import-a-post}

你需要一个 openwebui.com 账号，它与你在自己实例上的账号是分开的。

1. 在 openwebui.com 上打开该帖子并点击 **Get**。
2. 输入你的 Open WebUI URL，例如 `http://localhost:3000`，然后点击 **Import**。
3. 如果尚未登录，你会在登录后看到实例在新标签页中打开、编辑器中已填好内容。阅读该条目（包括 Tool 或 Function 的全部代码），然后保存。

| 帖子类型 | 导入到 | 谁可以导入 |
| :--- | :--- | :--- |
| 模型预设 | **Workspace > Models** | 被允许创建模型的用户 |
| 提示 | **Workspace > Prompts** | 被允许创建提示的用户 |
| 技能 | **Workspace > Skills** | 被允许创建和导入技能的用户 |
| Tool | **Workspace > Tools** | 被允许创建 Tool 的用户 |
| Function | **Admin Panel > Functions** | 仅管理员 |

## 分享你构建的东西 {#share-what-you-built}

**Share** 会在新标签页中打开 openwebui.com，并预填一篇新帖子。在那里完成帖子之前，什么都不会被发布。

- **模型预设、提示或 Tool：** 在 **Workspace** 中打开该条目的菜单并点击 **Share**。
- **技能：** 在 **Workspace > Skills** 中打开该技能的菜单并点击 **Share**。这需要 **Export Skills** 权限。帖子会带上该技能及其所有文件，总计最多 15 MiB。
- **Function（仅管理员）：** 在 **Admin Panel > Functions** 中打开该函数的菜单并点击 **Share**。
- **聊天：** 在聊天的 **Share** 对话框中点击 **Share to Open WebUI Community**。

分享 Tool 或 Function 会发布其完整的源代码。请检查其中是否含有 API key、内部地址或其他你不愿公开的内容。你在 Valves 中填写的内容不会被包含。

## 为模型写评测 {#review-a-model}

openwebui.com 上的评测能让你在花时间配置某个模型之前，先了解它对其他人而言表现如何；你的评测对别人也有同样作用。Open WebUI 中有两个链接会跳转到某个模型的评测：

- **阅读评测：** 在模型选择器中打开某个模型的菜单并点击 **Community Reviews**。
- **撰写评测：** 用点赞或点踩为一条回复评分，然后在打开的面板中点击该模型的 **Leave a public review for**。在 openwebui.com 上从搜索结果中打开该模型。在 **Write a review** 下填写星级、标题，以及对你而言哪些地方好用、哪些不好用，然后点击 **Post**。

这两个链接都会在该站点的 [Models](https://openwebui.com/models) 目录中按该模型在你实例上的 ID 查找，因此自定义模型或预设可能匹配不到条目。你的聊天内容不会被发送，你的评测会以你的 openwebui.com 账号公开发布。

## 把你的使用情况加入排行榜 {#add-your-usage-to-the-leaderboard}

[排行榜](https://openwebui.com/leaderboard)按人们实际发送给各模型的消息数量对模型进行排名。同步你的使用情况会把你依赖的模型计入其中，你的 openwebui.com 主页随后会显示你最常用的模型，以及你全年消息的分布热力图。

1. 在 openwebui.com 上登录，打开 **Leaderboard** 并点击 **Sync Stats**。你主页上的同步按钮以及侧边栏底部你名字上方的同步按钮作用相同。
2. 在 **Sync Open WebUI Stats** 中输入你的 Open WebUI URL 并点击 **Sync**。你的实例需要 Open WebUI v0.7.0 或更高版本。
3. 你的实例会在新标签页中打开，并弹出 **Sync Usage Stats** 对话框，列出哪些内容会共享、哪些不会。**Download as JSON** 可以把数据保存下来，便于你先阅读一遍。
4. 点击 **Sync**。

只会发送关于你自己聊天的统计信息，绝不发送聊天正文。[哪些内容会到达 openwebui.com](#what-reaches-openwebuicom)一节列出了每一个字段。首次同步之后，后续同步只发送自上次同步以来发生过变化的聊天的统计信息。

## 面向管理员 {#for-admins}

### 谁可以把代码带到你的服务器上 {#who-can-bring-code-onto-your-server}

从该网站导入的 Tool 或 Function 是一段 Python 代码，从保存的那一刻起就在你的服务器上运行。

- **Function** 只能由管理员导入。
- **Tool**、模型预设和提示可以由任何[工作区权限](/features/authentication-access/rbac/permissions#1-workspace-permissions)允许创建该类条目的用户导入。
- Tool 或 Function 可以在顶部的 `requirements` 一行列出 Python 包，Open WebUI 在加载该插件时会用 pip 安装它们。若要阻止这一点，请把 [`ENABLE_PIP_INSTALL_FRONTMATTER_REQUIREMENTS`](/reference/env-configuration#enable_pip_install_frontmatter_requirements) 设为 `False`。

### 哪些内容会到达 openwebui.com {#what-reaches-openwebuicom}

openwebui.com 从不连接你的服务器。所有内容都在用户浏览器的两个标签页之间传递，因此运行在 `localhost` 或私有网络上的实例与公开实例表现相同，并且在用户主动点击之前不会发送任何内容。用户可以发送两类东西：

- **一次分享。** 用户分享的内容会作为帖子发布：按当前配置导出的模型预设或提示、带上所有文件的技能、Tool 的完整源代码，或一份聊天快照（含消息）。管理员还可以分享 Function 的完整源代码。
- **一次统计同步**，用于[排行榜](#add-your-usage-to-the-leaderboard)。每位用户自行决定是否同步，且只覆盖他自己的聊天。他们会在你实例上的 **Sync Usage Stats** 对话框中确认。

一次统计同步会发送：

- Open WebUI 版本
- 每个聊天：其 ID、该用户在你实例上的 ID、创建与更新时间，以及它的标签
- 每条消息：其 ID、角色、模型、以字符计的长度、token 数、时间戳，以及它获得的评分与标签
- 每个聊天的汇总：消息数量、使用过的模型、平均消息长度与平均响应时间

它不会发送消息正文、提示、模型回复、聊天标题，也不会发送上传的文件和图片。

你实例自身的[评估](/features/administration/evaluation)排行榜由用户的评分构建而成，它永远不会离开你的实例。

### 关闭它 {#turn-it-off}

| 设置项 | 位置 | 默认值 |
| :--- | :--- | :--- |
| **Community Sharing** | **Settings > Admin > General** | 开启 |

[`ENABLE_COMMUNITY_SHARING`](/reference/env-configuration#enable_community_sharing) 会在实例首次启动时设定它。此后以管理面板中保存的值为准。

关闭它会对所有用户（包括管理员）隐藏以下内容：

- Models、Prompts、Skills、Tools 和 Functions 页面上的 **Made by Open WebUI Community** 链接
- 模型、提示、技能、Tool 和 Function 菜单中的 **Share**
- 聊天分享对话框中的 **Share to Open WebUI Community**
- 模型选择器中的 **Community Reviews**，以及为回复评分后出现的评测链接
- **Sync Usage Stats** 对话框
- 新建聊天中的 **By** 行，它会把从 openwebui.com 导入的模型链接到那里的作者；模型会保留其作者信息，因此重新开启共享后该链接就会回来

该对话框背后的统计导出仍会通过 API 响应管理员，并拒绝其他所有人。

## 接下来可以看什么 {#where-to-go-next}

- **[社区插件](/features/extensibility/community)**：按你想要的效果挑选插件。
- **[从 Functions 起步](/getting-started/quick-start/connect-a-provider/starting-with-functions)**：完成第一次 Function 导入，从找到它到设置它的 Valves。
- **[分享聊天](/features/chat-conversations/chat-features/chatshare#sharing-to-open-webui-community)**：分享链接，以及谁能看到你分享到该站点的聊天。
