---
title: 工作区中的 AI
sidebar_position: 1
---

# 工作区中的 AI

有两种方式为 Open WebUI Computer 聊天添加 AI：

1. **通过 API 连接模型**：OpenAI、Anthropic、Ollama、OpenRouter 或任何 OpenAI 兼容的端点。在**设置 → 管理 → 连接**中添加。参见[连接模型](./connect-a-model)。
2. **接入你已经订阅的编码代理**：Codex、Claude Code、Cursor、Grok、OpenCode、Cline 或 Pi 作为原生聊天后端运行，使用机器上已有的 CLI 登录。无需 API 密钥。参见[使用你的编码代理订阅](./coding-agents)。

两者都会出现在同一个模型选择器中，并在同一个工作区聊天中工作。你可以混合使用：Ollama 模型用于快速提问，你的 Claude Code 订阅用于真正的工作。

| | API 连接 | 编码代理后端 |
| --- | --- | --- |
| 凭据 | API 密钥（Ollama 接受任意文本） | CLI 在主机上的现有登录（你的订阅） |
| 谁执行工具 | Computer 的内置工具（文件、命令、浏览器、搜索） | 代理自己的 CLI，在你的机器上运行 |
| 会话恢复 | 聊天持久化在每个工作区中，可在任何地方重新打开 | 同上，另外后端的自己的会话在每次轮次中自动恢复 |

## AI 能在你的机器上做什么

无论选择哪种方式，AI 都在你文件实际所在的位置工作。它可以：

- **读取和编辑**工作区中的文件，并在整个代码库中搜索
- **运行 shell 命令**并读取输出，前台或后台
- **浏览网页**（导航、点击、填写表单、截图）并运行[网络搜索](./web-search-and-browsing)
- **启动[子代理](./subagents)** 进行并行工作
- **按计划运行**：重复性任务如"每天早上运行测试"（参见[定时任务](/ecosystem/computer/automate/scheduled-tasks)）

你可以控制其中有多少在未经你许可的情况下发生：参见[审批、计划模式和审查](./approvals-and-plan-mode)。

## AI 是可选的

Computer 中的其他所有功能（文件、编辑器、终端、git、远程访问）无需配置模型也能工作。在你想要的时候添加 AI，而不是在此之前。

## 本节内容

- [连接模型（API 密钥和 Ollama）](./connect-a-model)
- [使用你的编码代理订阅](./coding-agents)
- [审批、计划模式和审查](./approvals-and-plan-mode)
- [聊天功能](./chat-features)
- [技能和记忆](./skills-and-memory)
- [子代理](./subagents)
- [网络搜索和浏览](./web-search-and-browsing)
- [语音、语音和音频](./voice-and-audio)
