---
sidebar_position: 9
title: "智能体"
---

# 智能体 {#agents}

如果所选的 Open Terminal 列出了智能体，模型选择器就会将它们与常规模型一同显示。选中一个后，它会在终端的工作区中使用该环境的文件和工具。

出现哪些智能体与模型取决于你选择的 Open Terminal。终端报告为不可用的智能体不会被列出。

可以让智能体总结项目文件、准备报告，或修复缺陷并运行测试。你可以在聊天中跟进它的工作、回答问题并审查工具请求。

有关安装、登录和连接步骤，请先阅读[连接智能体](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

## 支持的智能体 {#supported-agents}

Open Terminal 通过下表的接口启动已安装的 CLI。请以运行终端的用户身份安装 CLI 并完成其身份验证；对某个智能体的支持并不意味着每个终端镜像都包含它的可执行文件或凭据。`:agents` Docker 镜像包含 Codex 和 Claude Code。

| 智能体 | 接口 | 可执行文件 |
| :--- | :--- | :--- |
| [Codex](/getting-started/quick-start/connect-an-agent/codex-cli) | 原生 app-server 协议 | `codex` |
| [Claude Code](/getting-started/quick-start/connect-an-agent/claude-code) | 原生流式 JSON 协议 | `claude` |
| [Pi](/getting-started/quick-start/connect-an-agent/pi) | 原生 RPC 协议 | `pi` |
| [Cursor](/getting-started/quick-start/connect-an-agent/cursor-cli) | ACP | `agent` |
| [Grok](/getting-started/quick-start/connect-an-agent/grok-build) | ACP | `grok` |
| [OpenCode](/getting-started/quick-start/connect-an-agent/opencode) | ACP | `opencode` |
| [Cline](/getting-started/quick-start/connect-an-agent/cline) | ACP | `cline` |
| [Gemini CLI](/getting-started/quick-start/connect-an-agent/gemini-cli) | ACP | `gemini` |
| [Hermes](/getting-started/quick-start/connect-an-agent/hermes-agent) | ACP | `hermes` |
| [Antigravity](/getting-started/quick-start/connect-an-agent/antigravity) | ACP | `agy` |
| [GitHub Copilot](/getting-started/quick-start/connect-an-agent/github-copilot) | ACP | `copilot` |
| [Goose](/getting-started/quick-start/connect-an-agent/goose) | ACP | `goose` |
| [Qwen Code](/getting-started/quick-start/connect-an-agent/qwen-code) | ACP | `qwen` |

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/get-started/introduction) 规范化了智能体与其客户端之间的通信。这些集成使用 ACP v1。Open Terminal 负责启动智能体进程，Open WebUI 负责处理其协议消息，包括聊天输出、工具审批和会话延续。其余三个智能体有专用的协议适配器。

可用模型来自各 CLI 的发现响应。推理控制和会话恢复等功能取决于智能体及其版本。请使用支持目标集成的 Open WebUI、Open Terminal 和 CLI 版本。[Open Terminal 智能体参考](https://github.com/open-webui/open-terminal#coding-agents-in-chat)列出了启动命令和可执行文件覆盖方式。

## 添加另一个 ACP 智能体 {#add-another-acp-agent}

先在终端环境中安装并配置该智能体。然后在 **Open Terminal 服务器**上设置 `OPEN_TERMINAL_ACP_AGENTS`，其值为一个 JSON 对象，包含 ID、显示名称和启动命令。例如，对于已安装的 Kiro CLI：

```bash
export OPEN_TERMINAL_ACP_AGENTS='{"kiro":{"name":"Kiro","command":"kiro-cli acp"}}'
```

如果使用 Docker，请把同一个变量透传到容器环境中。重启 Open Terminal 以加载它，然后在 Open WebUI 中选择该终端。发现的模型显示为 `acp-kiro/<model>`。

该命令必须启动通过标准输入和输出通信的 ACP v1 智能体。智能体在终端用户的环境中运行，可使用该用户的文件和凭据。此设置只注册命令，不会安装智能体，也不会完成交互式登录。智能体必须在发现阶段成功报告模型，才会出现在选择器中。

## 选择智能体 {#picking-an-agent}

在聊天中选中一个终端，然后打开模型选择器。每个智能体模型的名称形如 `<agent>/<model>`。

- **每个会话只能使用一个智能体。** 一个聊天中只添加一个智能体模型。在多模型聊天中，智能体不能与其他模型组合使用。
- **重新生成、编辑或分叉。** 自 Open WebUI 0.13.4 起，你可以重新生成回复、编辑较早的消息，以及分叉或克隆智能体聊天。Codex 可以在终端上装有新版 Codex CLI 时从所选轮次继续。Claude Code 需要新版 [Open Terminal](/features/open-terminal/setup/updating) 才能做到同样的事。其他智能体会以截至该点的聊天记录开启新会话。文件改动会留在工作区中。[版本要求](https://github.com/open-webui/open-webui/releases/tag/v0.13.4)
- **缺失的智能体。** 当终端或其智能体模型不可用时，该智能体会从可选项中移除，并改用默认模型。
- **仅限已保存的聊天。** 智能体会话需要一个已保存的聊天，因此它们在临时聊天中不可用。

## 查看执行步骤 {#reading-the-steps}

智能体的步骤和普通模型的终端工具调用会显示为易读的卡片，例如命令及其输出，或每个改动文件的差异。

## 模型 ID {#model-ids}

智能体模型 ID 中的模型部分只含字母、数字、连字符和下划线。模型名称含有句点等其他字符时，这些字符会替换成连字符并加上短后缀。置顶项、默认模型和[自动化](/features/chat-conversations/chat-features/automations#running-a-coding-agent)都使用该 ID。

## 选项 {#options}

如果智能体为所选模型提供了这些选项，**Reasoning effort** 与 **Service tier** 就会出现在消息输入框的模型控制菜单中。你的选择会保存到设置中。

在聊天控件或模型高级参数中手动设置**推理强度**后，该参数也会传给智能体。名为 `reasoningEffort` 或 `reasoning_effort` 的自定义参数也按同样方式读取。Claude Code 将其用作 effort 级别，Pi 用作 thinking 级别，Codex 用作当轮的推理强度。其他智能体会使用其为该模型提供的思考级别。如果智能体不支持该模型的所选级别，回复会失败并提示 **Agent does not support the selected reasoning effort for this model**。请选择其他级别或清除该参数。

## 与智能体协作 {#working-with-an-agent}

- **附件。** 你附加的文件会被上传到终端，智能体也会获知它们的路径。
- **工作区。** 新会话从消息输入框中 **Choose working directory** 下所选的文件夹开始。已有的智能体会话会保留它自己的工作区，即使你在[文件浏览器](./file-browser.md)中浏览到其他文件夹也是如此。
- **工具请求。** 智能体请求运行工具时，聊天中会显示该请求，并遵循[工具权限模式](/features/extensibility/plugin/tools#tool-approval)。启用 [`ENABLE_TOOL_PERMISSIONS`](/reference/env-configuration#enable_tool_permissions) 和 [`ENABLE_TOOL_PERMISSIONS_AUTO`](/reference/env-configuration#enable_tool_permissions_auto) 后可使用 **Auto**。在此模式下，Codex 使用自己的审核机制，只转交需要升级审核的请求。支持此功能的 Claude Code 和 Grok 版本也采用同样方式。升级请求仍须经过 Open WebUI 的批准检查。其他 ACP 智能体在 **Auto** 下仍会请求批准，除非管理员在[自动权限](/features/extensibility/plugin/tools#auto)下设置了 **Engine**。
- **提问。** 当智能体向你提问时，问题会出现在聊天中，智能体会等待你的回答。无论设置的是哪种权限模式，问题始终会显示。
- **语音。** 选中了终端时，智能体可以在[实时语音通话](/features/chat-conversations/chat-features/voice-mode#realtime-calls)中工作。
- **聊天标题。** 新聊天的标题取自你第一条消息的前 50 个字符。当设置了[任务模型](/features/administration/task-models)且开启了自动标题生成时，生成的标题会取代它。
