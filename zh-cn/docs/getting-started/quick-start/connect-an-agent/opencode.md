---
sidebar_position: 11
sidebar_label: "OpenCode"
title: "使用 Open Terminal 连接 OpenCode"
description: "通过 ACP 把 OpenCode 接入 Open WebUI。在 Open Terminal 内部配置它的提供商，并在选择器中找到带提供商限定的模型。"
---

# 在 Open WebUI 中使用 OpenCode {#use-opencode-in-open-webui}

## 在终端中设置 OpenCode {#set-up-opencode-in-the-terminal}

在你的终端工作区中安装 OpenCode。运行 `opencode`，用 `/connect` 配置提供商，再用 `/models` 选择模型。对于本地模型服务器，请配置一个终端可以访问的地址。让模型读取一个文件，验证提供商和工作区都正常。[OpenCode 安装](https://opencode.ai/docs/) · [OpenCode 提供商](https://opencode.ai/docs/providers/)

## 在 Open WebUI 中选择 OpenCode {#select-opencode-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `opencode/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

OpenCode 可以把提供商包含在模型名称中，所以选择器中的完整条目可能是 `opencode/<provider>/<model>`。Open Terminal 会自动启动 `opencode acp`。手动运行该命令会让进程一直等待协议消息。使用交互式 `opencode` 命令测试你的登录。[OpenCode ACP 指南](https://opencode.ai/docs/cli/acp/)
