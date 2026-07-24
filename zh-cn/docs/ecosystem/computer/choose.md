---
title: "Computer、Open WebUI 还是 Open Terminal？"
sidebar_position: 14
---

# Computer、Open WebUI 还是 Open Terminal？

三个工具，三个不同的重心。根据工作在哪个位置来选择，并且可以自由组合它们；它们本来就是为配合使用而设计的。

| | **Open WebUI** | **Open Terminal** | **Open WebUI Computer** |
| --- | --- | --- | --- |
| 重心 | 对话 | 干净的执行环境 | 你真实的机器 |
| 最适合 | 模型选择、知识、提示词、共享的 AI 工作流 | 自包含的任务：分析上传内容、构建原型、运行脚本 | 已在一台计算机上的项目、终端、服务和登录信息 |
| 环境 | 不适用 | 全新、隔离（Docker）或主机 | 真实主机：现有文件、状态、工具 |
| 用户 | 一到多人 | 跟随 Open WebUI | 一位受信任的拥有者 |
| 是否需要 AI | 是 | 是 | 否；文件、终端和 git 无需 AI 也能工作 |

**从 Open WebUI 开始**，当重要的上下文是对话或连接的知识，且不需要特定的机器时。

**添加 [Open Terminal](/features/open-terminal)**，当聊天需要一个执行场所时：写入文件、安装包、运行代码、返回结果。每个任务一个全新环境；无需保留任何东西。

**从 Computer 开始**，当答案以"让我查一下我的电脑"开始时：你离开时未清理的分支、正在运行的开发服务器、PDF 文件夹、执行中的代理。Computer 从任何浏览器打开同一台机器，而不是在其他地方重新创建工作。

## 一起使用它们

- **Open WebUI 作为大门，Computer 作为双手。** 连接[网关](/ecosystem/computer/automate/open-webui)，每个 Computer 工作区在 Open WebUI 的模型选择器中显示为 `cptr/<workspace>`。聊天发生在 Open WebUI；文件编辑、命令和工具发生在 Computer 主机上。知识库、提示词和用户不会在两者之间传输，所以在 Computer 端配置工作区所需的内容。
- **三者同时使用**是正常的：Open WebUI 用于思考和整理，Open Terminal 用于一次性执行，Computer 用于需要持续运行的机器。

## 已经在使用编码代理 CLI？

Computer 不会取代它。在[终端标签页](/ecosystem/computer/workspace/terminals)中运行任何代理 CLI，就像你今天做的那样。或者，对于 Codex、Claude Code、Cursor、Grok、OpenCode、Cline 和 Pi，[将其添加为原生后端](/ecosystem/computer/ai/coding-agents)，使其成为一个具有流式传输、审批和会话恢复功能的聊天模型，使用你已有的订阅和登录信息。

一个信任提示：Open Terminal 为聊天提供一次性的执行环境。Computer 为你拥有的机器提供服务，你选择它的边界：裸机运行则服务于整个工作站，或者[在 Docker 中运行](/ecosystem/computer/install/docker)使其只看到你挂载的文件夹。无论哪种方式，你允许登录的每个人共享该边界；参见[安全模型](/ecosystem/computer/phone-and-remote/security)。
