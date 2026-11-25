---
title: "Open Terminal 与 Terminals"
description: "在 Open WebUI 中构建应用、产出报告并运行智能体。Open Terminal 为你的 AI 提供一台计算机；Terminals 为每个人或项目提供独立工作区。"
sidebar_position: 2
---

# Open Terminal 与 Terminals {#open-terminal--terminals}

**给你的 AI 一台计算机。在聊天里把活干完。**

让 AI 做一个仪表盘，然后在对话旁打开可用的应用。给它一份电子表格，它就能生成一份可以直接发送的报告。提供一个代码库，它可以修改代码、运行测试并修复发现的问题。

**Open Terminal** 为你的 AI 提供文件、软件、浏览器和命令行，让它能真正动手。**Terminals** 则按需提供这些环境：既可以按人、按项目隔离工作区，也可以共享一个用于协作。两者都直接接入 Open WebUI。

**[安装 Open Terminal](/features/open-terminal/setup/installation)** · **[部署 Terminals](https://github.com/open-webui/terminals#quick-start)**

## 从想法到可用成果 {#from-an-idea-to-something-you-can-open}

> 用这个 CSV 做一个小仪表盘，让我能按日期和类别筛选。然后启动它，让我在这里预览。

你的 AI 可以安装依赖、编写应用、启动服务器并检查输出。Open WebUI 把文件、终端和预览放在对话旁边，你可以直接试用结果并提出修改意见。

同一个循环也适用于演示文稿、一批修过的图片，或者对上千行数据的分析。脚本和交付物都是真实文件：可以检查、下载并在此基础上继续。持久化的工作区让下一个任务从你已经做完的部分开始。

![在 Open WebUI 界面中，Open Terminal 工作区及其文件浏览器会与聊天窗口并排显示。](/images/open-terminal-file-browser.png)

## 用你想用的 AI 一起工作 {#use-the-ai-you-want-to-work-with}

通过 Open WebUI 接入一个能力足够的本地或云端模型，并启用[原生工具调用](/features/open-terminal/setup/connecting#8-enable-native-function-calling)。Open Terminal 给它一个可以按你的要求行动、检查成果并重试的地方。

更想用 **Claude Code、Codex、Cursor 还是 Gemini CLI**？在终端环境里安装并登录该智能体，然后在 Open WebUI 的模型选择器中选中它。它自己的智能体软件会针对你的项目运行，在聊天中提供流式响应、审批和会话续接。[连接智能体](/getting-started/quick-start/connect-an-agent)介绍了受支持的智能体，以及通过 ACP 添加其他智能体的方式。

把工作区放在你自己的机器或服务器上，用浏览器访问它。

## 为每个项目提供工作场所 {#give-every-project-a-place-to-work}

**Terminals** 让你在 Open WebUI 中创建并共享已配置好的工作区。软件、起始目录和初始化脚本只需设定一次；Terminals 会在需要时启动 Open Terminal 容器，运行在 Docker 或 Kubernetes 上。

为了自己的工作，可以让个人环境跨对话保留，或者给每个已保存的聊天分配独立环境，让不同项目拥有各自的文件和进程。

对于协作，聊天范围内的环境让获得授权的协作者共享同一批文件和运行环境。有人提出修改要求，另一个人检查结果，成果与讨论放在一起。

对于团队，可以先安装所需的软件包、准备报表脚本，搭建分析环境，再向用户组共享其模板。采用用户作用域时，每个人都会获得独立的容器和持久化文件。将机器设为模型预设的**默认机器**，用户便可选择一个已有工作环境的报表助手。也可以为一个模型预设专门分配环境，或向所有获授权的用户共享环境。

人们通过 Open WebUI 干活；运维人员在集中位置维护模板、访问权限和资源限制。你可以为整个团队提供一个有用的助手，而不必在每台笔记本上都搭一套开发环境。

## 自动重复执行任务 {#make-useful-work-repeatable}

在个人或共享工作区中编写报表脚本，然后为 Open WebUI [自动化](/features/chat-conversations/chat-features/automations)指定这台机器及工作目录。定时运行提示词，让它针对新数据执行脚本并汇总结果。工作区既可用于交互式工作，也可用于定期任务，可以使用模型或受支持的智能体。

Terminals 可以停止空闲的环境，同时保留其持久化文件，然后按需重新启动。为每个模板设置 CPU 和内存上限。工作区可以为下一个任务保持可用，而不必让它的容器整天运行。

## 从一个真实任务开始 {#start-with-one-real-task}

1. **[安装 Open Terminal](/features/open-terminal/setup/installation)。** Docker 会给它一个独立的容器环境；直接安装在宿主机上则可以使用该机器的文件和软件，权限受操作系统用户限制。
2. **[连接到 Open WebUI](/features/open-terminal/setup/connecting)。** 在管理区域的**设置 > 集成**中，找到**机器**区域，添加地址和 API 密钥。
3. **在聊天中选择并使用机器。** 选择合适的模型或已安装的智能体，提供一个文件或项目，并说明你需要什么可用的结果。

如需按需创建工作区，请**[部署 Terminals](https://github.com/open-webui/terminals#quick-start)**，然后在 Open WebUI 的**新建机器**菜单中创建第一个模板。如需用桌面应用连接自己的电脑，请使用 [Open WebUI Tether](/ecosystem/tether)。

Open Terminal 采用 [MIT 许可证](https://github.com/open-webui/open-terminal/blob/main/LICENSE)，也可以通过它的 REST API 与你自己的应用集成。[Terminals](https://github.com/open-webui/terminals/blob/main/LICENSE) 对个人非商业用途免费；商业或组织内部的生产使用需要带 Terminals 权限的 [Open WebUI 企业版许可证](/enterprise)。
