---
sidebar_position: 9
sidebar_label: "Grok Build"
title: "使用 Open Terminal 连接 Grok Build"
description: "把 Grok Build CLI 接入 Open WebUI，在远程 Open Terminal 上使用设备登录，并为项目聊天选择一个 Grok 模型。"
---

# 在 Open WebUI 中使用 Grok Build {#use-grok-build-in-open-webui}

## 在终端中设置 Grok Build {#set-up-grok-build-in-the-terminal}

在终端环境中安装 Grok Build 并运行 `grok` 登录。如果工作区是远程的，请从该工作区启动设备登录。

```bash
grok login --device-auth
```

完成浏览器步骤后，返回终端并验证 `grok` 中的一个提示。如果你改用 API 密钥，请确保运行 Open Terminal 的进程能访问 `XAI_API_KEY`。[Grok Build 安装与认证](https://docs.x.ai/build/overview)

## 在 Open WebUI 中选择 Grok {#select-grok-in-open-webui}

在一个新的已保存聊天中，先选择你的 **Terminal**，再用 **Choose working directory** 选定项目。打开模型选择器，选择以 `grok/` 开头的模型。如果你仍需要连接工作区，请参阅 [Open Terminal 快速开始](/getting-started/quick-start/connect-an-agent#quick-start-with-open-terminal)。

Open Terminal 以 `agent stdio` 模式启动 Grok。让它检查一个项目文件，并在聊天中展开它的步骤。在支持自动工具审查的版本上，Grok 可以处理常规请求，并把需要升级的操作转发给 Open WebUI。[工具审批模式](/features/extensibility/plugin/tools#tool-approval)
