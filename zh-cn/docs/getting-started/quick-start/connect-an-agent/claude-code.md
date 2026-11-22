---
sidebar_position: 1
sidebar_label: "Claude Code"
title: "使用 Open Terminal 连接 Claude Code"
description: "在 Open Terminal 工作区中登录 Claude Code，在 Open WebUI 中选择 Claude 模型，并检查它读取和编辑的文件。"
---

# 在 Open WebUI 中使用 Claude Code {#use-claude-code-in-open-webui}

## 在终端中设置 Claude Code {#set-up-claude-code-in-the-terminal}

Open Terminal 的 `:agents` Docker 镜像包含 `claude`。如果你使用其他镜像或宿主机终端，请以运行 Open Terminal 的用户身份在那里安装 Claude Code。[Claude Code 快速开始](https://code.claude.com/docs/en/quickstart)

在你的项目文件夹中启动 `claude`。按其登录提示操作，或在 Claude Code 内部使用 `/login` 选择账户。让它读取项目 README 并引用其中的第一个标题。它回答之后，退出 CLI。

## 在 Open WebUI 中选择 Claude Code {#select-claude-code-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `claude-code/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 以流式 JSON 模式启动 Claude Code。文件读取和编辑会作为步骤显示在聊天中。可以试着让 Claude 更新文档中的一句话，然后在 **Files** 中打开该文件检查改动。
