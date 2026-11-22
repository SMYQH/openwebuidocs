---
sidebar_position: 13
sidebar_label: "Qwen Code"
title: "使用 Open Terminal 连接 Qwen Code"
description: "用 Open Terminal 把 Qwen Code 接入 Open WebUI。安装 qwen CLI，配置它的提供商，并在聊天选择器中找到它的模型。"
---

# 在 Open WebUI 中使用 Qwen Code {#use-qwen-code-in-open-webui}

## 在终端中设置 Qwen Code {#set-up-qwen-code-in-the-terminal}

在终端环境中安装 Qwen Code。准备好受支持的 Node.js 版本后，运行以下命令。

```bash
npm install -g @qwen-code/qwen-code
qwen
```

在 Qwen Code 中使用 `/auth` 为你的账户或提供商选择一种认证方式。发送一个提示并确认模型有响应，然后再回到 Open WebUI。[Qwen Code 安装](https://github.com/QwenLM/qwen-code) · [认证选项](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/auth/)

## 在 Open WebUI 中选择 Qwen Code {#select-qwen-code-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `qwen/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 启动 `qwen --acp`。通过 Ollama 或兼容 OpenAI 的端点接入 Open WebUI 的 Qwen 模型，也作为普通模型提供。选择 `qwen/` 条目，即表示你想让 Qwen Code 本身在终端中读取文件和运行工具。
