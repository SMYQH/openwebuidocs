---
sidebar_position: 0
sidebar_label: "连接 Agent"
title: "用 Open Terminal 运行 Claude Code、Codex 等"
description: "用 Open Terminal 把 Claude Code、Codex、Gemini CLI 或其他 Agent 接入 Open WebUI。找到你的 Agent，登录，并在项目中运行一个任务。"
---

# 在 Open WebUI 中运行 Claude Code、Codex 和其他 Agent {#run-claude-code-codex-and-other-agents-in-open-webui}

要在 Open WebUI 中使用 Agent，先选择**安装了它 CLI 的终端**，再在**模型选择器中选择该 Agent**。你在聊天中发送消息并审查它的工作。Agent 使用自己的工具和模型提供商，在终端的工作区中读取文件、运行命令并做出修改。

已经连接好终端并且 Agent CLI 可用？直接[开始你的第一个 Agent 聊天](#start-your-first-agent-chat)。如果你已经在运行 Hermes 或 OpenClaw 网关，也可以[直接连接它的 API](#connect-an-existing-agent-gateway)。

## Open Terminal 支持哪些 Agent {#which-agents-does-open-terminal-support}

Open Terminal 内置了下面 13 个 Agent 的集成。`:agents` Docker 镜像自带 **Claude Code 和 Codex**。其他 CLI 请自行安装到同一个终端环境中。从下面选择你的 Agent，了解安装、登录和模型选择方式。

| Agent | CLI 可执行文件 | 模型选择器前缀 |
| :--- | :--- | :--- |
| [Claude Code](/getting-started/quick-start/connect-an-agent/claude-code) | `claude` | `claude-code/` |
| [OpenAI Codex CLI](/getting-started/quick-start/connect-an-agent/codex-cli) | `codex` | `codex/` |
| [Cline CLI](/getting-started/quick-start/connect-an-agent/cline) | `cline` | `cline/` |
| [Cursor CLI](/getting-started/quick-start/connect-an-agent/cursor-cli) | `agent` | `cursor/` |
| [Gemini CLI](/getting-started/quick-start/connect-an-agent/gemini-cli) | `gemini` | `gemini/` |
| [GitHub Copilot CLI](/getting-started/quick-start/connect-an-agent/github-copilot) | `copilot` | `copilot/` |
| [Google Antigravity CLI](/getting-started/quick-start/connect-an-agent/antigravity) | `agy` | `antigravity/` |
| [Goose](/getting-started/quick-start/connect-an-agent/goose) | `goose` | `goose/` |
| [Grok Build](/getting-started/quick-start/connect-an-agent/grok-build) | `grok` | `grok/` |
| [Hermes Agent](/getting-started/quick-start/connect-an-agent/hermes-agent) | `hermes` | `hermes/` |
| [OpenCode](/getting-started/quick-start/connect-an-agent/opencode) | `opencode` | `opencode/` |
| [Pi](/getting-started/quick-start/connect-an-agent/pi) | `pi` | `pi/` |
| [Qwen Code](/getting-started/quick-start/connect-an-agent/qwen-code) | `qwen` | `qwen/` |

Open Terminal 会在需要时启动各个 CLI。Codex 使用它的 app server，Claude Code 使用流式 JSON，Pi 使用 RPC。其他内置 Agent 使用 **Agent Client Protocol (ACP)**。要接入其他 ACP v1 Agent，例如 **Kiro CLI** 或 **Factory Droid**，请安装并配置该 CLI，在 `OPEN_TERMINAL_ACP_AGENTS` 中注册它的启动命令，然后重启 Open Terminal。[自定义 ACP Agent 设置](/features/open-terminal/agents#add-another-acp-agent) · [Agent 启动命令](https://github.com/open-webui/open-terminal#coding-agents-in-chat)

## 用 Open Terminal 快速开始 {#quick-start-with-open-terminal}

### 1. 选择 Agent 的运行位置 {#1-choose-where-the-agent-will-work}

- **在你自己的电脑上。** 用 Open WebUI Tether 把你的电脑连接进来。在那台电脑上安装并登录 CLI。在聊天中于 **Terminal > Your devices** 下选择它，然后继续[开始你的第一个 Agent 聊天](#start-your-first-agent-chat)。[Tether 设置](/ecosystem/tether#get-started)
- **在已有的 Open Terminal 上。** 在该环境中打开一个 shell，继续第 2 步。如果你要把已有容器换成 `:agents` 镜像，请保留它的主目录卷。[更新 Open Terminal](/features/open-terminal/setup/updating)
- **在新的 Docker 工作区中。** 如果 Open WebUI 直接运行在同一台主机上，就启动下面的容器。如果 Open WebUI 本身运行在 Docker Compose 中，就把 `open-terminal` 服务用 `:agents` 镜像加到同一个 Compose 网络里。[Docker Compose 与裸机安装](/features/open-terminal/setup/installation)

把 `your-secret-key` 换成你自己的密钥。这个卷会在你更换容器时保留单用户的工作区、CLI 设置和基于文件的凭据。如果需要分离的用户和凭据，请参阅[团队部署](/features/open-terminal/advanced/multi-user)。

```bash
docker run -d \
  --name open-terminal \
  --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  -v open-terminal:/home/user \
  -e OPEN_TERMINAL_API_KEY=your-secret-key \
  ghcr.io/open-webui/open-terminal:agents
```

### 2. 在终端中登录 Agent {#2-sign-in-to-the-agent-inside-the-terminal}

对于上面的 Docker 示例，以终端用户身份打开一个 shell。

```bash
docker exec -it open-terminal bash
```

**Codex** 需要你的账户允许设备登录时，运行 `codex login --device-auth`，然后启动 `codex`。**Claude Code** 则运行 `claude` 并按其登录提示操作。其他 Agent 请按上表中的设置链接操作。给 CLI 提一个简短问题，确认它在这个 shell 中能回答。用完后退出交互式 CLI。[Agent 认证与 API 密钥选项](https://github.com/open-webui/open-terminal/blob/main/docs/deployment.md#coding-agents)

### 3. 把终端连接到 Open WebUI {#3-connect-the-terminal-to-open-webui}

以管理员身份打开 **Settings > Admin > Integrations**。在 **Open Terminal** 下点击 **+**，给连接起个名字，并填写 **Open WebUI 服务器**能够访问的 URL。上面的主机安装用 `http://127.0.0.1:8000`，Compose 服务名为 `open-terminal` 且在同一网络中时用 `http://open-terminal:8000`。

选择 **Bearer**，填入你的 **Open Terminal API 密钥**。保存并启用该连接。这个密钥让 Open WebUI 获得工作区访问权。CLI 使用第 2 步中的提供商登录来生成回复。[连接设置与访问授权](/features/open-terminal/setup/connecting)

### 开始你的第一个 Agent 聊天 {#start-your-first-agent-chat}

使用终端工作区中已经存在的项目。如果你是从空容器开始的，在它的 shell 中运行下面的命令，创建一个可以从聊天中检查的小项目。

```bash
mkdir -p ~/agent-demo
printf '%s\n' '# Field Notes' 'Run the project with: python -m http.server 8080' > ~/agent-demo/README.md
```

1. 打开 **New Chat**，并关闭 **Temporary Chat**。在消息输入框中打开 **Terminal**，选择你已连接的工作区。
2. 在终端选择器旁边打开 **Choose working directory**，选择你的项目文件夹（Docker 示例中为 `/home/user/agent-demo`）。新的 Agent 对话就从那里开始。在 **Files** 标签中浏览其他文件夹不会改变聊天的工作目录。
3. 打开**模型选择器**，搜索你的 Agent 前缀，例如 `claude-code/` 或 `codex/`。选择 CLI 上报的模型之一。这个聊天只使用一个 Agent 模型。
4. 发送下面的提示。在聊天中展开 Agent 的读取或命令步骤，把它的回复与 **Files** 中的 README 对照。对于示例项目，答案应包含 `python -m http.server 8080`。

   > Read the README in this folder. What command does it give for running the project? Quote the relevant line.

在同一个聊天中继续让 Agent 运行命令或编辑文件。你可以附加文件、回答 Agent 的提问，并按你的[工具权限模式](/features/extensibility/plugin/tools#tool-approval)审查工具请求。重新生成回复或分叉聊天都会保留 Agent 已经做出的文件改动。Agent 如何续接对话取决于 CLI 及其版本。[Agent 聊天行为](/features/open-terminal/agents#picking-an-agent)

## 为什么我的 Agent 没有出现在模型选择器中 {#why-is-my-agent-missing-from-the-model-picker}

| 你看到的现象 | 需要检查 |
| :--- | :--- |
| 终端本身不见了 | 检查从 Open WebUI 服务器看到的连接 URL、Bearer 密钥、启用开关，以及你的账户对终端的访问权限。使用 Tether 时，检查你的设备是否在线并连接到同一账户。 |
| 终端正常，但 Agent 不见了 | 在该终端的 shell 中，用表格里的可执行文件运行 `command -v`（例如 Cursor 用 `command -v agent`）。以终端用户身份完成 CLI 的提供商配置。使用支持该集成的 Open WebUI、Open Terminal 和 CLI 版本，然后重新选择终端以刷新发现结果。 |
| Agent 出现了，但第一次回复失败 | 在该工作区内的 CLI 中试同一个模型。CLI 可能在提供商登录可用之前就上报模型名称。检查它的凭据和到提供商的连通性。 |
| Codex 能回复，但某个 shell 步骤报 `bwrap: No permissions to create a new namespace` | 容器运行时阻止了 Codex 用来执行命令的 Linux 沙箱。请改用支持 Codex 沙箱的终端环境，例如在受支持的主机上直接运行的 Open Terminal，然后重试同一次文件读取。 |
| Agent 看到了错误的文件 | 检查第一条消息之前你选择的终端和工作目录。要切换到别的项目，请开始新的聊天并选择该项目的目录。 |

## 用带终端工具的普通模型 {#use-a-regular-model-with-terminal-tools}

要让已有模型获得 shell 和文件访问权限，请选择终端并保持使用你原来的普通模型。Open WebUI 管理它的工具调用，Open Terminal 负责执行。这条路径需要模型具备原生工具调用能力和 **Terminal** 能力。你可以跳过 Agent CLI 的安装和登录。[模型能力与绑定](/features/workspace/models#capabilities-and-bindings)

## 接入已有的 Agent 网关 {#connect-an-existing-agent-gateway}

如果你的 Agent 已经作为服务运行并提供兼容 OpenAI 的 API，请在 **Settings > Admin > Connections > OpenAI** 下添加它的端点。网关自行管理工作区、工具和对话处理。

- **Hermes Agent** 两条路径都支持。选择上面的终端集成，即可在选定的项目文件夹中使用 Hermes；也可以连接正在运行的 Hermes 网关的 API。[Hermes 网关设置](/getting-started/quick-start/connect-an-agent/hermes-agent#connect-the-hermes-gateway)
- **OpenClaw** 提供一个网关，你可以在聊天中把它选为模型。[OpenClaw 网关设置](/getting-started/quick-start/connect-an-agent/openclaw)