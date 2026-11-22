---
sidebar_position: 6
sidebar_label: "GitHub Copilot CLI"
title: "使用 Open Terminal 连接 GitHub Copilot CLI"
description: "在 Open Terminal 中安装 GitHub Copilot CLI，使用 GitHub 登录，并在 Open WebUI 中选择 Copilot 模型来处理仓库文件。"
---

# 在 Open WebUI 中使用 GitHub Copilot CLI {#use-github-copilot-cli-in-open-webui}

## 在终端中设置 GitHub Copilot CLI {#set-up-github-copilot-cli-in-the-terminal}

在终端上安装独立的 `copilot` 可执行文件。准备好受支持的 Node.js 版本后，可以用 npm 安装并启动它。

```bash
npm install -g @github/copilot
copilot
```

如果出现提示，输入 `/login` 并授权一个可使用 Copilot 的 GitHub 账户。确认 CLI 能在你的仓库中回答提示。可用的 `gh` 命令只能验证 GitHub CLI 的安装。Open Terminal 的这项集成需要 `copilot`。[安装 GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)

## 在 Open WebUI 中选择 GitHub Copilot {#select-github-copilot-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `copilot/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 在所选工作区中启动 `copilot --acp`。作为第一个任务，可以问它哪些文件定义了仓库的 CI 检查，并让 Copilot 引用相关行。把它的回答与 **Files** 中的工作流文件对照。
