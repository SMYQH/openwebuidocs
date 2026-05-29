---
title: 自动化和集成
sidebar_position: 1
---

# 自动化和集成

Open WebUI Computer 在浏览器标签页关闭后仍在继续工作。你可以从 Telegram 或 Slack 给它发消息，按计划运行任务，通过 webhook 从其他系统触发任务，将工作区暴露为 OpenAI 兼容的模型，以及通过 MCP 或 OpenAPI 服务器为代理提供额外工具。

:::warning 无人值守运行使用完全工具审批
本节中的所有内容都在你没有注视的情况下运行：没有人点击**允许**，因此机器人消息、定时运行、webhook 触发器和网关请求都会执行文件编辑、shell 命令和工具调用，而没有逐操作的门控。将它们指向一个你愿意让代理操作的工作区，并编写精确说明要做什么的提示词。如需交互式审批，请使用 Web UI；参见[审批和计划模式](/ecosystem/computer/ai/approvals-and-plan-mode)。
:::

| 我想…… | 前往 |
| --- | --- |
| 从 Telegram、Discord、Slack、WhatsApp 或 Signal 与我的电脑聊天 | [给你的电脑发消息](./messaging-bots) |
| 每天早上、每小时或每周一运行一个提示词 | [定时任务](./scheduled-tasks) |
| 从 CI、cron 作业或其他服务触发任务 | [定时任务 → webhook 触发器](./scheduled-tasks#trigger-a-task-with-a-webhook) |
| 在聊天或定时运行完成或失败时收到通知 | [通知和 webhook](./notifications) |
| 在 Open WebUI 中使用 Computer 工作区作为模型 | [在 Open WebUI 中使用工作区](./open-webui) |
| 通过 MCP 或 OpenAPI 服务器为代理提供工具 | [MCP 和 OpenAPI 工具服务器](./tool-servers) |

所有这些都会在工作区侧边栏中生成真实的聊天，所以你不在时运行的内容在你回来后都可以查看。
