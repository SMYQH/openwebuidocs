---
sidebar_position: 3
sidebar_label: "Cline CLI"
title: "使用 Open Terminal 连接 Cline CLI"
description: "通过 Open Terminal 把 Cline CLI 接入 Open WebUI。用 cline auth 配置模型提供商，并在聊天中选择 Cline 模型。"
---

# 在 Open WebUI 中使用 Cline CLI {#use-cline-cli-in-open-webui}

## 在终端中设置 Cline CLI {#set-up-cline-cli-in-the-terminal}

在你的终端工作区中安装 Cline CLI。如果你使用 npm，请以终端用户身份运行以下命令。

```bash
npm install -g cline
cline auth
```

在认证流程中选择你的提供商，然后从项目文件夹运行 `cline` 并发送一条简短提示。如果你已经在编辑器中配置过 Cline，仍要确认这个终端用户的 CLI 能够访问该提供商。[Cline CLI 设置](https://docs.cline.bot/usage/cli-overview)

## 在 Open WebUI 中选择 Cline {#select-cline-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `cline/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 运行 `cline --acp`，以 Agent Client Protocol (ACP) 启动会话。让 Cline 找出项目的测试命令并说明它在哪里找到的。你可以在同一个对话中审查任何工具请求。
