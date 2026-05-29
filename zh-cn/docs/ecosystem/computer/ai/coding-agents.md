---
title: 使用你的编码代理订阅
sidebar_position: 3
---

# 使用你的编码代理订阅

已经在为 Codex、Claude Code、Cursor、Grok、OpenCode、Cline 或 Pi 付费？将该订阅用作原生聊天后端；无需 API 密钥。在运行 Computer 的机器上安装并登录代理的 CLI，然后前往**设置 → 管理 → 代理**添加一个配置文件。它的模型会像其他提供商一样出现在模型选择器中，ID 格式为 `agent:<profile-id>/<model>`。

一个配置文件包含：**名称**、**类型**（哪个代理）、**配置文件 ID**（用于模型 ID 的标识符）、**命令**（名称或绝对路径；支持 `~`）和可选的**主目录**（见下文）。某些类型会添加额外字段：Claude Code 有**启动参数**，Cursor 有**API 端点**，OpenCode 有**服务器 URL** 和密码。

## 各代理设置

CLI 必须安装在**运行 Computer 的主机上**并登录，而不是在你浏览用的手机或笔记本电脑上。

### Codex

命令：`codex`。使用 `codex login` 登录。需要具有应用服务器支持的较新 CLI；如果检测报告不支持的能力，请更新 CLI。

### Claude Code

命令：`claude`。使用 CLI 的正常登录流程登录。还需要 Python 包 `claude-agent-sdk` 在 Computer 运行的环境中；没有它，配置文件会显示 **missing dependency**：

```bash
pip install claude-agent-sdk
```

可用的模型列表取决于已安装的 CLI 版本。

### Cursor

命令：`agent`。在主机上运行 `agent login`。

### Grok

命令：`grok`。使用 CLI 登录，或设置 `XAI_API_KEY` 环境变量。

### OpenCode

命令：`opencode`。Computer 会自动启动 `opencode serve`，或者在配置文件中设置**服务器 URL**（和密码）以连接到你已经运行的服务器。模型来自 OpenCode 中连接的提供商。

### Cline

命令：`cline`。在主机上运行 `cline auth`。

### Pi

命令：`pi`。模型命名空间为 `provider/id`。

## 检测状态

每个配置文件显示一个实时状态（结果缓存约 30 秒）：

| 状态 | 含义 | 修复 |
| --- | --- | --- |
| **ready** | 找到命令，依赖存在，模型可发现 | 无；选择一个模型并聊天 |
| **not found** | 命令不在 PATH 上 | 安装 CLI，或将命令设置为绝对路径 |
| **missing dependency** | 缺少所需的本地包（Claude Code：`claude-agent-sdk`） | 在 Computer 的环境中安装指定的依赖 |
| **auth unknown** | 找到 CLI 但无法确认登录状态 | 在主机上运行代理的登录命令，然后重新检测 |

配置文件模式：**auto**（仅在就绪时可选择）、**enabled**（强制）或 **disabled**。

## 模型、会话和主目录字段

- **模型：** 将配置文件中的模型列表留空以从 CLI 自动检测，或手动固定列表。模型 ID 格式如 `agent:claude/claude-sonnet-4-5`。
- **会话自动恢复。** 每个后端返回一个会话或线程 ID，存储在聊天中并在下一个轮次传回（Claude Code SDK 会话、Codex 线程恢复、Cursor/Grok/Cline 会话加载）。关闭标签页，在手机上打开聊天，代理会从它离开的地方继续。
- **主目录：** 将配置文件指向替代的代理配置/登录目录。这对于第二个账户或与你默认的 `~` 配置分开的独立登录很有用。

## 任何其他代理仍然可以工作

Gemini CLI、Kilo Code 或任何其他终端代理可以在[终端标签页](/ecosystem/computer/workspace/terminals)中正常运行；只是它不会成为具有模型选择和会话恢复功能的原生聊天后端。
