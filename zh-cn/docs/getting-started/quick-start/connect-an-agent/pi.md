---
sidebar_position: 12
sidebar_label: "Pi"
title: "使用 Open Terminal 连接 Pi"
description: "通过 Open Terminal 的 Pi 原生 RPC 模式把 Pi 智能体接入 Open WebUI。登录提供商，并在聊天中选择 Pi 模型。"
---

# 在 Open WebUI 中使用 Pi {#use-pi-in-open-webui}

## 在终端中设置 Pi {#set-up-pi-in-the-terminal}

在工作区中安装 Pi 的终端应用，然后从你的项目运行 `pi`。输入 `/login` 连接受支持的提供商，或在 Open Terminal 使用的环境中配置该提供商的 API 密钥。用 `/model` 选择模型并发送一条测试消息。[Pi 安装](https://pi.dev/) · [Pi 命令](https://docs.pi.dev/latest/usage)

## 在 Open WebUI 中选择 Pi {#select-pi-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `pi/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 启动 `pi --mode rpc` 来发现模型并交换消息。Pi 有原生集成，因此不需要 ACP 注册步骤。作为第一个任务，让 Pi 读取两个文件，并指出一个你可以在工作区中验证的差异。
