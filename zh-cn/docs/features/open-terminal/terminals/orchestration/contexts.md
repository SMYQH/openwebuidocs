---
sidebar_position: 2
title: "Terminal Contexts"
---

# Terminal Contexts

编排器（orchestrator）连接可以按上下文划定范围。针对聊天和自动化任务，管理员分别要决定两件事：

- 该终端在那里究竟能不能使用
- 是所有内容共用一个工作区，还是每个已保存的聊天（或每个自动化任务）都拥有各自独立的工作区

连接到普通 Open Terminal 服务器的连接没有上下文划分。它们在任何地方都可用，并且始终解析到同一个工作区。

:::info 需要 Terminals 0.2.0 或更高版本
编排器提供按聊天、按自动化任务划分独立工作区的能力。在较早版本的编排器上，**Per chat** 与 **Per automation** 的行为等同于 **Shared**。无论版本如何，Open WebUI 都会应用 **Off** 以及对已保存聊天的要求。
:::

## 配置 {#configure}

1. 打开 **Settings > Admin > Integrations**，滚动到 **Terminal** 区域。
2. 添加或编辑一个连接，然后使用 URL 旁边的 **Verify Connection**，以便 Open WebUI 识别服务器类型。只有当该连接被识别为编排器、或它已带有 **Policy ID** 时，**Orchestrator** 区域才会出现。
3. 展开 **Orchestrator** 并设置 **Terminal Contexts**。

| 行 | 可选项 |
| :--- | :--- |
| **Chat** | **Shared**、**Per chat**、**Off** |
| **Automation** | **Shared**、**Per automation**、**Off** |

两行都默认为 **Shared**。

## 各模式的作用 {#what-each-mode-does}

| 模式 | 效果 |
| :--- | :--- |
| **Shared** | 同一用户的每个聊天（或每个自动化任务）都在同一个工作区中工作 |
| **Per chat** | 每个已保存的聊天都拥有自己的工作区，以及属于自己的文件 |
| **Per automation** | 每个自动化任务都拥有自己的工作区，并在该任务的多次运行之间复用 |
| **Off** | 该终端不会出现在该上下文中，对它的请求也会被拒绝 |

这两行彼此独立。一个终端在聊天中可以是 **Per chat**、在自动化任务中是 **Off**；也可以在聊天中是 **Off**、在自动化任务中是 **Shared**。

无论你选择哪种模式，都适用于整个终端：模型的工具、文件浏览器和终端面板都在同一个地方工作。

在聊天中为 **Off** 的终端不会出现在聊天的终端选择器中；在自动化任务中为 **Off** 的终端不会出现在[自动化](/features/chat-conversations/chat-features/automations#giving-a-run-a-terminal)编辑器中，因此用户不会误触到它们。模型编辑器会列出所有终端。指向一个对自动化任务关闭的终端的模型，在聊天中仍然可用，而它的自动化运行会失败并提示该终端不可用于自动化任务。

## Per Chat 需要已保存的聊天 {#per-chat-needs-a-saved-chat}

按聊天划分的工作区归属于某个具体会话，因此该会话必须先存在。发送第一条消息并让聊天出现在侧边栏之后，它就存在了。

- 在尚未发送过消息的新会话中，该终端的终端面板与文件浏览器不可用。聊天被保存后它们才会出现。若第一条消息附带文件，且 [Chat Uploads](/features/open-terminal/setup/connecting#chat-uploads) 设为 `Filesystem`，该文件会等待到你发送消息后才上传进新聊天的工作区。
- 在[临时聊天](/features/chat-conversations/chat-features/url-params#8-temporary-chat-sessions)中，按聊天划分的终端没有可依附的对象，因为临时聊天从不被保存。开启临时聊天时，终端选择器会把它隐藏起来，而打开临时聊天也会取消对它的选中。
- 界面中没有任何地方会悄悄回退到共享工作区。在聊天被保存之前，该终端会被拒绝，而被要求使用它的模型会报出一个点明该终端名称的错误。
- 完全没有聊天 ID 就到达代理的请求（例如直接调用 API）不会归属任何聊天，即便该行设为 **Per chat**，它也会落入共享工作区。Open WebUI 的界面总会发送聊天 ID。系统信息是个例外：在 **Per chat** 终端上它需要一个已保存的聊天，否则代理会返回 `409`，并附带 `A saved chat is required for this terminal`。

## 容量 {#capacity}

**Per chat** 会成倍增加单个用户可同时运行的工作区数量——每个他正在使用的聊天一个，每个都要计入策略的资源限制。在把一个繁忙的连接切换为 **Per chat** 之前，请先在策略上设置 `idle_timeout_minutes`，以便被遗弃聊天的工作区能够被清理。参见[策略](/features/open-terminal/terminals/orchestration/policies)。

## 预先配置 {#pre-configuring-it}

同样的设置也可以通过 [`TERMINAL_SERVER_CONNECTIONS`](/reference/env-configuration#terminal_server_connections) 随连接一起下发，放在该连接的 `config.contexts` 下——这对于在启动时就配置好一切的部署很有用。

## 这不能做什么 {#what-this-does-not-do}

上下文不是用来把用户彼此分开的手段。那本来就是编排器通过为每个用户分配独立工作区所做的事；上下文只是把单个用户自己的工作区进一步细分。有关隔离层级，请参见[多用户设置](/features/open-terminal/advanced/multi-user)。

上下文同样不适用于普通的 Open Terminal 服务器、不适用于通过个人 **Settings > Integrations** 添加的连接，也不适用于任何未被 Open WebUI 识别为编排器的连接。
