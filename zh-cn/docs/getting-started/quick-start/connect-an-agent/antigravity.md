---
sidebar_position: 7
sidebar_label: "Google Antigravity CLI"
title: "使用 Open Terminal 连接 Google Antigravity CLI"
description: "在 Open WebUI 中使用 Google Antigravity CLI。安装 agy，在运行 Open Terminal 的计算机上登录，并选择一个 Antigravity 模型。"
---

# 在 Open WebUI 中使用 Google Antigravity CLI {#use-google-antigravity-cli-in-open-webui}

## 在终端中设置 Google Antigravity CLI {#set-up-google-antigravity-cli-in-the-terminal}

在运行 Open Terminal 的计算机或容器中安装 Antigravity CLI。在那里运行 `agy --version`，然后在你的项目文件夹中启动 `agy`。[Antigravity CLI 安装](https://antigravity.google/docs/cli-getting-started)

在本地计算机上，如果 CLI 没有保存凭据，请按浏览器登录流程操作。通过 SSH 连接时，`agy` 可以打印一个授权 URL。在你的计算机上打开它，并在远程终端中输入由此得到的代码。在 CLI 中问一个简短问题，确认账户在该处可用。[Antigravity 认证](https://antigravity.google/docs/install?tab=cli)

## 在 Open WebUI 中选择 Antigravity {#select-antigravity-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `antigravity/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 为该对话启动 `agy acp`。如果模型选择器只显示 `gemini/` 条目，请检查所选终端是否有 `agy` 可执行文件。Gemini CLI 使用的是另一套集成。
