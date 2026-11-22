---
sidebar_position: 4
sidebar_label: "Cursor CLI"
title: "使用 Open Terminal 连接 Cursor CLI"
description: "从 Open WebUI 运行 Cursor CLI。在本地或远程 Open Terminal 中认证 agent 可执行文件，并在聊天模型选择器中找到 Cursor 模型。"
---

# 在 Open WebUI 中使用 Cursor CLI {#use-cursor-cli-in-open-webui}

## 在终端中设置 Cursor CLI {#set-up-cursor-cli-in-the-terminal}

在运行 Open Terminal 的环境中安装 Cursor CLI。它的可执行文件名为 `agent`。在远程机器上，请打印登录 URL 并在自己的浏览器中打开。

```bash
NO_OPEN_BROWSER=1 agent login
agent status
```

在带浏览器的计算机上，直接使用 `agent login`。确认 `agent status` 显示的是预期账户。[Cursor CLI 安装](https://cursor.com/docs/cli/installation) · [Cursor 认证](https://cursor.com/docs/cli/reference/authentication)

## 在 Open WebUI 中选择 Cursor {#select-cursor-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `cursor/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 使用 Cursor 登录启动 `agent acp`。如果选择器中没有 Cursor 条目，请在项目所在的终端中运行 `command -v agent`。在另一台计算机上安装桌面编辑器，并不会把 CLI 装进该工作区。
