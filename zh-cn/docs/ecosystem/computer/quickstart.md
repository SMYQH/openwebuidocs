---
title: "快速入门"
sidebar_position: 3
---

# 快速入门

从零到在浏览器中看到真实文件，大约两分钟。你需要在存有工作的机器上有 Python 3.10+（macOS、Linux 或 Windows）。不需要 AI 密钥，不需要任何人的账户，不需要云服务。

## 1. 安装并运行

```bash
pip install cptr
cptr run
```

或者无需永久安装：`uvx cptr@latest run`。喜欢容器？改用 [Docker](/ecosystem/computer/install/docker)；结果相同。

`cptr run` 在 `http://127.0.0.1:8000` 启动服务器，并在浏览器中打开一个一次性设置链接（`/?token=...`）。在无头机器上使用 `cptr run --headless`，然后手动打开打印的 URL。

## 2. 创建账户

设置页面要求输入用户名和密码。这是管理员账户，存储在本地机器上。一次性令牌仅在尚不存在账户时有效，所以其他人无法抢先注册。

## 3. 打开一个文件夹

选择**打开文件夹**并选择机器上的任意文件夹：一个代码仓库、你的文档、一个项目目录。该文件夹现在成为一个**工作区**。Computer 显示文件夹本身，而非上传的副本。你可以在设置过程中跳过可选的 AI 连接，并在以后随时添加。

从工作区你可以获得：

- **文件**：浏览、使用语法高亮编辑、预览 Markdown、PDF、CSV 和 Office 文件。
- **终端**：机器上的真实 shell。关闭标签页后它继续运行。
- **Git**：分支、差异、暂存、提交、推送（如果该文件夹是一个仓库）。
- **聊天**：一旦你[连接了模型或代理](/ecosystem/computer/ai/)，即可使用。

随时从工作区选择器添加更多文件夹。参见[工作区](/ecosystem/computer/workspace/workspaces)。

## 4. 现在让它成为你的

几乎每个人都想要的两个升级：

1. **从手机访问。** 在同一个 Wi-Fi 上，只需一个标志（`cptr run --host 0.0.0.0`）；从任何地方访问需要十分钟的 [Tailscale 设置](/ecosystem/computer/phone-and-remote/tailscale)。然后[将其安装为应用](/ecosystem/computer/phone-and-remote/phone-app)到你的主屏幕。
2. **给它 AI。** [连接 API 密钥或 Ollama](/ecosystem/computer/ai/connect-a-model)，或者[接入你已经拥有的 Claude Code / Codex / Cursor 订阅](/ecosystem/computer/ai/coding-agents)。

如果机器是笔记本电脑或偶尔重启，设置[保持运行](/ecosystem/computer/phone-and-remote/keep-it-running)，这样服务器、终端和代理都能在你离开后继续工作。

## 如果出了什么问题

- `cptr: command not found`：你的 shell 找不到 pip 的脚本目录。在你想要的 Python 环境中运行 `python -m pip install cptr`，或者重新打开终端。
- 端口被占用：运行 `cptr run --port 8001`。
- 其他问题：[故障排除](/ecosystem/computer/troubleshooting)。
