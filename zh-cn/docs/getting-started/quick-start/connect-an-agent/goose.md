---
sidebar_position: 8
sidebar_label: "Goose"
title: "使用 Open Terminal 连接 Goose"
description: "在 Open Terminal 工作区中配置 Goose 的提供商和模型，并从 Open WebUI 聊天中使用该 Goose 会话。"
---

# 在 Open WebUI 中使用 Goose {#use-goose-in-open-webui}

## 在终端中设置 Goose {#set-up-goose-in-the-terminal}

为终端的操作系统安装 Goose CLI，然后以终端用户身份配置提供商和模型。

```bash
goose configure
goose session
```

在新会话中，让 Goose 总结一个你认识的文件。这既检查了提供商配置，也检查了 Goose 对工作区的访问权限。等它回答后退出会话。[Goose CLI 安装与提供商设置](https://github.com/aaif-goose/goose/blob/main/documentation/docs/getting-started/installation.md)

## 在 Open WebUI 中选择 Goose {#select-goose-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `goose/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 启动 `goose acp` 并向 Goose 查询它可用的模型。如果提供商在你的笔记本上可用，但聊天运行在容器里，请在该容器内部运行 `goose configure`，并使用它自己的提供商凭据。
