---
sidebar_position: 5
sidebar_label: "Gemini CLI"
title: "使用 Open Terminal 连接 Gemini CLI"
description: "在 Open Terminal 中设置 Google Gemini CLI，为你的项目完成认证，并在 Open WebUI 聊天中选择它的 Gemini 模型。"
---

# 在 Open WebUI 中使用 Gemini CLI {#use-gemini-cli-in-open-webui}

## 在终端中设置 Gemini CLI {#set-up-gemini-cli-in-the-terminal}

在存放项目的终端中安装 CLI。准备好 Node.js 和 npm 后，运行以下命令。

```bash
npm install -g @google/gemini-cli
gemini
```

选择你的账户可用的认证方式，例如 Gemini API key 或 Vertex AI。如果该方式使用环境变量，请把它们提供给 Open Terminal 进程，以便它启动的 CLI 能够使用。用同一个项目和凭据验证一次提示能够成功。[Gemini CLI 安装](https://geminicli.com/docs/get-started/installation/) · [认证方式](https://geminicli.com/docs/get-started/authentication/)

## 在 Open WebUI 中选择 Gemini CLI {#select-gemini-cli-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `gemini/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 运行 `gemini --acp`。如果你同时安装了 Gemini CLI 和 Google Antigravity，两者各有自己的选择器前缀。为这个 CLI 选择 `gemini/`，或按 [Antigravity 指南](./antigravity.md)使用 `agy`。
