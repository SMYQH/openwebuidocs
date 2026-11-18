---
title: "Open WebUI Tether"
description: "让你的 AI 在你自己的电脑上干活，用手机查看结果，并接入你自己的模型与工具。Tether 提供 macOS、Windows 和 Linux 版本。"
sidebar_position: 3
---

# Open WebUI Tether {#open-webui-tether}

**即使你不在电脑前，也让 AI 在你的电脑上干活。**

让它把一批导出文件整理成报告、修掉项目里的一个 bug，或者归类你的文件。用手机查看结果。回来继续处理它在电脑上创建的文件。

Tether 是把你的电脑连接到你的 Open WebUI 的桌面应用。它把你的文件、工具和本地模型带进聊天，并提供可选的工作区沙箱，用来限定 AI 可以在哪里工作。

**[下载 macOS、Windows 和 Linux 版本](https://github.com/open-webui/tether/releases/latest)** · **[开始使用](#get-started)**

## 触手可及的工作区 {#your-workspace-within-reach}

该项目已安装好所需依赖项，文档已存放在相应文件夹中，相关工具也已配置完毕。Tether 让你的 AI 通过 **Open Terminal** 在这个环境中工作。在 Open WebUI 中观察命令的执行过程，检查文件，并提出修改请求。你也可以在终端环境里安装并登录[受支持的智能体，例如 Claude Code 和 Codex](/getting-started/quick-start/connect-an-agent)后使用它们。

在另一台设备上打开同一个 Open WebUI 实例，用相同账户登录，然后在终端菜单的 **Your devices** 下选择你的电脑。工作会运行在已连接的电脑上。对团队来说，每个人的设备各自连接到共享实例上的自己的账户。

Tether 是向外连接的，所以你不需要入站端口，也不需要路由器端口转发。让电脑保持唤醒、联网并运行 Tether。启用 **Run in background**，这样关闭窗口后仍能保持连接；再在 Open WebUI 中开启 **Browser Notifications**，聊天完成或失败时就能收到提醒。系统层面也要允许通知。

## 询问你屏幕上的内容 {#ask-about-whats-on-your-screen}

一个你认不出来的报错。一张你想让人解释的图表。一段你原本得从头描述的东西。

在 macOS 上按 **Cmd+Shift+I**，在 Windows 和 Linux 上按 **Ctrl+Shift+I**，在当前应用之上打开 **Spotlight**。截取一块屏幕区域或附上剪贴板图片，提出你的问题，然后发给 Open WebUI。截图请使用支持图像的模型；快捷键可在 **Tether Settings > General** 中自定义。

## 给它一个可以工作的文件夹 {#give-it-a-folder-to-work-in}

Tether 可选的**工作区沙箱**让你从一个明确的文件集合开始。操作系统层面的限制会把 Open Terminal 及其命令限定在选定的工作区、临时存储和必要的程序文件内。沙箱中的命令默认关闭网络访问；任务需要时再打开。

沙箱原生运行在 **macOS 和受支持的 Windows 设备**上，不需要 Docker 或虚拟机，在 **Linux** 上**不可用**。在 **Tether Settings > Open Terminal > Sandbox** 下选择 **Restrict file access**，选定文件夹，然后点击 **Apply and restart**。Tether 会在启动前检查这些限制；等到出现 **Sandbox active** 再继续。

<details>
<summary>沙箱范围</summary>

工作区内的文件仍然可以被修改或删除。该 Tether 安装中的所有 WebUI 连接共享同一个选定文件夹。沙箱生效期间，浏览器控制、桌面控制和直接 HTTP 访问都会被禁用。

本地 MCP 命令、单独连接的终端，以及 **Host shell (unrestricted)** 都在这个沙箱之外。仅设置文件浏览器的起始目录并不能限制访问。各平台和进程生命周期的细节见[沙箱指南](https://github.com/open-webui/tether/blob/main/docs/sandbox.md)。

</details>

## 接入你自己的模型和工具 {#bring-your-own-models-and-tools}

在 Open WebUI 中使用你在 Ollama 或 LM Studio 里运行的模型。把已安装的 MCP 服务器的工具带进聊天，或通过 OpenAPI 连接内部服务。在 **Tether Settings > Integrations** 中添加它们；Tether 通过已有的连接从你的电脑访问它们。本地 MCP 命令不需要单独的 HTTP 桥接。参见 [MCP 配置](https://github.com/open-webui/tether/blob/main/docs/mcp.md)。

对于浏览器相关的工作，Open Terminal 可以使用独立的 Chrome 配置文件，或者在你开启远程调试并同意后使用你正在运行的 Chrome 会话。桌面控制在受支持的系统上可用。两者都要求关闭工作区沙箱。

集成用的密钥留在 Tether 电脑上。聊天中使用的提示、文件内容和工具结果仍会经过 Open WebUI 以及相关的模型服务。

## 开始使用 {#get-started}

你需要一个现成的 Open WebUI 实例和一个账户。

1. 在你想使用的电脑上**[安装 Tether](https://github.com/open-webui/tether/releases/latest)**。
2. **输入你的 Open WebUI 地址**并登录。
3. 选择 **Install and connect** 以启用本地文件和命令，Tether 会为你安装 Open Terminal。选择 **Not now** 则可以在不启用本地执行的情况下使用桌面聊天。
4. **设置你的访问偏好**，然后在聊天的 **Your devices** 下选择这台电脑。选一个能力足够的工具调用模型，并在[文件浏览器](/features/open-terminal/file-browser)中打开你的文件夹。

![Tether 连接界面，显示 Open WebUI 地址和可选的连接名称](/images/tether-connect.png)

拿工作区里的几份文本文档试试：

> 阅读这些文件，创建 summary.md，为每一份写一段简短摘要。带上源文件名，并保持原文件不变。

打开结果，检查一下，再提出下一步的修改。

个人非商业用途按[个人使用例外条款](https://github.com/open-webui/tether/blob/main/LICENSE)免费。商业或组织内部的生产使用需要 [Open WebUI 企业版许可证](/enterprise)。

## 环境要求与帮助 {#requirements}

<details>
<summary>连接要求与故障排查</summary>

请使用相互兼容的 Tether、Open WebUI 和 Open Terminal 版本。实例需要 [`ENABLE_WEBSOCKET_SUPPORT`](/reference/env-configuration#enable_websocket_support)；若要访问终端，还需要 [`ENABLE_TOOL_SERVERS`](/reference/env-configuration#enable_tool_servers)。当 [`UVICORN_WORKERS`](/reference/env-configuration#uvicorn_workers) 大于 1 时，还需要 [Redis](/reference/env-configuration#redis_url)。

如果你的电脑没有出现，检查 Tether 和 Open Terminal 是否都在运行并已连接，以及两台设备是否使用同一个实例和账户。如果模型没有使用它，检查模型的 [Terminal 能力](/features/workspace/models#capabilities-and-bindings)和[原生工具调用模式](/features/open-terminal/setup/connecting#8-enable-native-function-calling)。

如果缺少模型或工具，在 Tether 中启用对应的连接，并确认这些服务从那台电脑可以访问。MCP 需要中继支持匹配，并在 Open WebUI 中启用外部工具。

</details>

[GitHub](https://github.com/open-webui/tether) · [客户端协议参考](/reference/tether-client-protocol) · [反馈问题](https://github.com/open-webui/tether/issues)
