---
title: 常见问题
sidebar_position: 13
---

# 常见问题

## 基础

### 我需要 AI 提供商或 API 密钥吗？

不需要。文件、编辑器、终端和 git 在零 AI 配置下也能工作。随时添加模型以获得聊天功能；API 密钥、Ollama 或编码代理订阅都可以：[连接模型](/ecosystem/computer/ai/connect-a-model)。

### 运行它需要什么？

macOS、Linux 或 Windows 上的 Python 3.10+（`pip install cptr`），或 Docker（`ghcr.io/open-webui/computer:latest`）。参见[快速入门](/ecosystem/computer/quickstart)。

### 这与 Open WebUI 或 Open Terminal 有何不同？

Open WebUI 是模型的聊天界面；Open Terminal 共享一个终端；Computer 将你的整个机器呈现给任何浏览器：文件、编辑器、终端、git、AI、代理。完整比较：[我需要哪个工具？](/ecosystem/computer/choose)

### 许可证是什么？需要付费吗？

Computer 在 Open Use License 下提供源码，可免费自托管；商业和企业许可证可在 openwebui.com 获取。

### 如何更新？

`pip install --upgrade cptr`（或拉取新的 Docker 镜像并重用相同的 `/data` 卷）。数据库迁移在启动时自动运行；无需手动步骤。详情：[更新](/ecosystem/computer/install/updating)。

### 如何卸载？

`pip uninstall cptr`。如果你想清除所有数据，还要删除 `~/.cptr`（账户、设置、上传）和每个工作区内的 `.cptr/` 文件夹（聊天、制品）。无论哪种方式，你的项目文件都不会受影响。

## 手机和远程

### 如何在离家时访问？

Tailscale 是推荐的路径：你的电脑获得一个稳定的私有地址，可从任何地方访问。Cloudflare Tunnel 和 ngrok 也可以使用，它们有自己的认证层。从这里开始：[手机和远程访问](/ecosystem/computer/phone-and-remote/)。

### 关闭标签页后工作还在继续吗？

是的。聊天、代理任务、终端和定时任务都运行在服务器上，而不是在你的浏览器中。在火车上关闭标签页，在办公桌上重新打开，一切都在你离开的地方。只有停止或重启服务器本身才会结束正在运行的终端和正在进行的后台子代理。

### 我的电脑必须保持开机吗？

是的。Computer 服务于*你的*机器，所以休眠或关机的电脑无法提供服务。阻止它休眠并在开机时启动：[保持运行](/ecosystem/computer/phone-and-remote/keep-it-running)。

### 有移动应用吗？

它是一个 PWA：在手机浏览器中打开它，添加到主屏幕即可获得全屏、类似应用的体验。参见[在手机上使用](/ecosystem/computer/phone-and-remote/phone-app)。

### 放在互联网上安全吗？

像对待 SSH 一样：任何登录的人都能获得主机的完整文件系统和 shell 访问权限。不要公开暴露原始端口。使用 Tailscale 或带有自己访问控制的隧道，并阅读[安全模型](/ecosystem/computer/phone-and-remote/security)。

## AI 和代理

### 我可以使用我的 Claude Code 或 Codex 订阅吗？

可以。在运行 Computer 的机器上安装并登录代理 CLI，在**设置 → 管理 → 代理**中添加，它会作为一个聊天模型出现。不需要 API 密钥，会话可以跨设备恢复。设置：[编码代理](/ecosystem/computer/ai/coding-agents)。

### 它能与 Ollama 一起使用吗？

可以。添加一个提供商为 **OpenAI**、基础 URL 为 `http://localhost:11434/v1` 和任意非空 API 密钥的连接；你的本地模型会被自动发现。参见[连接模型](/ecosystem/computer/ai/connect-a-model)。

### 我可以在手机上批准代理的操作吗？

可以。审批提示内联显示在聊天中，相同的 **询问**/**自动**/**完全**模式和计划模式在任何设备上都能使用。参见[审批和计划模式](/ecosystem/computer/ai/approvals-and-plan-mode)。

### 我可以从 Telegram 或 WhatsApp 给我的电脑发消息吗？

可以。Telegram、Discord、Slack、WhatsApp 和 Signal 机器人都可以在你选择的工作区中运行完整的代理，对话会显示在你的侧边栏中。各平台设置：[消息机器人](/ecosystem/computer/automate/messaging-bots)。

### 它能按计划运行任务吗？

可以。**定时任务**页面可以在重复计划（每日、每周、每小时）上运行任何提示词，带有运行历史和可选的 CI 或 cron 的 webhook 触发器。参见[定时任务](/ecosystem/computer/automate/scheduled-tasks)。

### 有 API 吗？

有：一个 OpenAI 兼容的网关，位于 `/v1`。每个工作区作为一个模型出现（`cptr/<name>`），使用 `sk-cptr-...` 密钥进行认证，所以任何 OpenAI 客户端都可以驱动完整的代理。参考：[网关 API](/ecosystem/computer/reference/gateway-api)。

### 我可以在 Open WebUI 中使用工作区吗？

可以。将网关添加为 Open WebUI 中的 OpenAI 连接，你的工作区会出现在它的模型选择器中。参见[在 Open WebUI 中使用工作区](/ecosystem/computer/automate/open-webui)。

## 数据和隐私

### 我的数据在哪里，什么会离开我的机器？

一切都是本地的：账户、设置和上传在 `~/.cptr` 中，聊天在每个工作区的 `.cptr/` 文件夹内。除了你自行配置的提供商（模型 API、搜索提供商、机器人平台）外，没有任何数据离开你的机器。详情：[数据和备份](/ecosystem/computer/operate/data-and-backups)。

### 如何备份？

复制数据目录（至少包括 `app.db`、`config.toml` 和 `uploads/`）以及你的工作区；聊天随 `.cptr/` 一起移动。方法：[数据和备份](/ecosystem/computer/operate/data-and-backups)。

## 限制

### 可以有多个用户吗？

账户和管理员角色存在，但用户之间没有隔离：每个登录用户在您安装时设定的边界内（裸机上的整个主机，或 Docker 中挂载的文件夹）都拥有完整的文件系统和 shell 访问权限。这是一个信任域，所以只与你愿意给予 SSH 访问权限的人共享。

### 内置 HTTPS 吗？

不。`cptr run` 提供纯 HTTP，没有 TLS 标志。通过 Tailscale、隧道或前面的反向代理获取 HTTPS：[反向代理](/ecosystem/computer/phone-and-remote/reverse-proxy)。
