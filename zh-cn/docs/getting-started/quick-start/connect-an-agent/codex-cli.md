---
sidebar_position: 2
sidebar_label: "OpenAI Codex CLI"
title: "使用 Open Terminal 连接 OpenAI Codex CLI"
description: "通过 Open Terminal 在 Open WebUI 中使用 OpenAI Codex CLI。设置设备登录，选择 Codex 模型，并验证项目中的 shell 访问权限。"
---

# 在 Open WebUI 中使用 OpenAI Codex CLI {#use-openai-codex-cli-in-open-webui}

## 在终端中设置 OpenAI Codex CLI {#set-up-openai-codex-cli-in-the-terminal}

Open Terminal 的 `:agents` 镜像包含 `codex`。对于宿主机安装或其他镜像，请在存放项目的终端中安装 Codex CLI。[Codex CLI 安装](https://developers.openai.com/codex/cli/)

对于远程终端，运行 `codex login --device-auth` 并在浏览器中完成登录。你的账户或工作区必须启用设备登录。以终端用户身份运行 `codex login status` 可查看 CLI 将使用哪种登录方式。[Codex 认证选项](https://developers.openai.com/codex/auth)

## 在 Open WebUI 中选择 Codex {#select-codex-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `codex/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 通过标准输入和输出启动 Codex app server。让 Codex 运行 `pwd` 并读取 README。如果看到 `bwrap` 命名空间错误，说明 CLI 已启动，但它的 Linux 沙箱无法在该容器中运行命令。[排查终端运行时问题](/getting-started/quick-start/connect-an-agent#why-is-my-agent-missing-from-the-model-picker)
