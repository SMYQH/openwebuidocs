---
sidebar_position: 9
title: "Coding Agents"
---

# Coding Agents {#coding-agents}

当所选的 Open Terminal 列出了编码智能体时，它们会出现在模型选择器中，与你的常规模型并列。选中其中一个，该智能体就会在终端的工作区中工作，使用该环境的文件与工具。

出现哪些智能体与模型取决于你选择的 Open Terminal。终端报告为不可用的智能体不会被列出。

有关安装、登录和连接步骤，请先阅读[连接 Agent](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

## 支持的智能体 {#supported-agents}

Open Terminal 通过下表的接口启动已安装的 CLI。请以运行终端的用户身份安装 CLI 并完成其身份验证；对某个智能体的支持并不意味着每个终端镜像都包含它的可执行文件或凭据。`:agents` Docker 镜像包含 Codex 和 Claude Code。

| 智能体 | 接口 | 可执行文件 |
| :--- | :--- | :--- |
| **Codex** | 原生 app-server 协议 | `codex` |
| **Claude Code** | 原生流式 JSON 协议 | `claude` |
| **Pi** | 原生 RPC 协议 | `pi` |
| **Cursor** | ACP | `agent` |
| **Grok** | ACP | `grok` |
| **OpenCode** | ACP | `opencode` |
| **Cline** | ACP | `cline` |
| **Gemini CLI** | ACP | `gemini` |
| **Hermes** | ACP | `hermes` |
| **Antigravity** | ACP | `agy` |
| **GitHub Copilot** | ACP | `copilot` |
| **Goose** | ACP | `goose` |
| **Qwen Code** | ACP | `qwen` |

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/get-started/introduction) 规范化了智能体与其客户端之间的通信。这些集成使用 ACP v1。Open Terminal 负责启动智能体进程，Open WebUI 负责处理其协议消息，包括聊天输出、工具审批和会话延续。其余三个智能体有专用的协议适配器。

可用模型来自各 CLI 的发现响应。推理控制和会话恢复等功能取决于智能体及其版本。请使用支持目标集成的 Open WebUI、Open Terminal 和 CLI 版本。[Open Terminal 智能体参考](https://github.com/open-webui/open-terminal#coding-agents-in-chat)列出了启动命令和可执行文件覆盖方式。

## 添加另一个 ACP 智能体 {#add-another-acp-agent}

先在终端环境中安装并配置该智能体。然后在 **Open Terminal 服务器**上设置 `OPEN_TERMINAL_ACP_AGENTS`，其值为一个 JSON 对象，包含 ID、显示名称和启动命令。例如，对于已安装的 Kiro CLI：

```bash
export OPEN_TERMINAL_ACP_AGENTS='{"kiro":{"name":"Kiro","command":"kiro-cli acp"}}'
```

如果使用 Docker，请把同一个变量透传到容器环境中。重启 Open Terminal 以加载它，然后在 Open WebUI 中选择该终端。发现的模型显示为 `acp-kiro/<model>`。

该命令必须通过标准输入/输出启动一个 ACP v1 智能体。它以终端用户的文件、环境和凭据运行。此设置只注册命令，不会安装智能体，也不会完成交互式登录。智能体必须在发现阶段成功报告模型，才会出现在选择器中。

## 选择智能体 {#picking-an-agent}

在聊天中选中一个终端，然后打开模型选择器。每个智能体模型的名称形如 `<agent>/<model>`。

- **每个会话只能使用一个智能体。** 一个聊天中只添加一个智能体模型。在多模型聊天中，智能体不能与其他模型组合使用。
- **只能发送新消息。** 通过发送新消息来继续智能体会话。智能体聊天无法重新生成、无法继续或编辑后重发，也无法从较早的消息分叉；请改为开启一个新的聊天。
- **缺失的智能体。** 当终端或其智能体模型不可用时，该智能体会从可选项中移除，并改用默认模型。
- **仅限已保存的聊天。** 智能体会话需要一个已保存的聊天，因此它们在临时聊天中不可用。

## 选项 {#options}

如果智能体为所选模型提供了这些选项，**Reasoning effort** 与 **Service tier** 就会出现在消息输入框的模型控制菜单中。你的选择会保存到设置中。

## 与智能体协作 {#working-with-an-agent}

- **附件。** 你附加的文件会被上传到终端，智能体也会获知它们的路径。
- **工作区。** 新会话从终端当前的工作目录开始。已有的智能体会话会保留它自己的工作区，即使你在[文件浏览器](./file-browser.md)中浏览到其他文件夹也是如此。
- **工具请求。** 当智能体想运行某个工具时，请求会出现在聊天中，并遵循[工具权限模式](/features/extensibility/plugin/tools#tool-approval)。
- **提问。** 当智能体向你提问时，问题会出现在聊天中，智能体会等待你的回答。无论设置的是哪种权限模式，问题始终会显示。
- **语音。** 选中了终端时，智能体可以在[实时语音通话](/features/chat-conversations/chat-features/voice-mode#realtime-calls)中工作。
- **聊天标题。** 新聊天的标题取自你第一条消息的前 50 个字符。当设置了[任务模型](/features/administration/task-models)且开启了自动标题生成时，生成的标题会取代它。
