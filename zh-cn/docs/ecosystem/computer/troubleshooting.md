---
title: 故障排除
sidebar_position: 12
---

# 故障排除

在下面找到你的症状（使用 Ctrl+F）。首先检查是否有明显问题：`curl http://127.0.0.1:8000/api/health` 可以告诉你服务器是否正常运行。

## "cptr: command not found"

包安装到了一个与你 PATH 上不同的 Python 环境中。将其安装到你实际运行的 Python 中：

```bash
python -m pip install cptr
```

如果你使用 pipx 或在虚拟环境中安装的，先激活该环境（或使用 `pipx run cptr run` / `uvx cptr@latest run`）。然后用 `cptr run` 启动。

## "Port 8000 already in use"

其他程序占用了该端口。要么在另一个端口上运行：

```bash
cptr run --port 8001
```

要么找到并停止占用者：`lsof -i :8000`（macOS/Linux）或 `netstat -ano | findstr :8000`（Windows）。

## 设置 URL 不起作用 / 我丢失了设置令牌

设置令牌在 `cptr run` 启动时打印一次，设置 URL 仅在**尚不存在账户时**有效。如果你丢失了它，只需重新启动 `cptr run`：会打印一个新的令牌。如果已经存在账户，设置 URL 按设计失效；前往 `http://localhost:8000` 正常登录。

## 我忘记了密码 / 我被锁定了

如果存在其他管理员，他们可以在**设置 → 管理 → 用户**中重置你的密码。有两件事可能先会让你困惑：

- 登录受限于**每个 IP 每分钟 5 次尝试**。如果收到 `429`，等待一分钟再试。
- 在 `config.toml` 中轮换 `[server] secret` 会使所有会话登出；它**不会**重置任何密码。

如果你是唯一的管理员，请停止服务器。没有 CLI 密码重置。按顺序尝试以下选项：

1. 从密码仍有效的时期恢复 `app.db` 的备份。
2. 最后的手段：使用 SQLite 客户端打开 `app.db`，删除用户行（account 和 auth 表），然后重新启动。首次运行设置会再次触发，你可以创建一个新的管理员。你的配置（`config.toml`）和工作区聊天（`<workspace>/.cptr/chats/`）会保留；只有账户被重新创建。

## 我的手机无法访问

手机上的 `localhost` 指的是手机本身。它永远无法访问你的电脑。

- **同一 Wi-Fi：** 使用 `cptr run --host 0.0.0.0` 重新启动，在手机上打开 `http://<your-computer-ip>:8000`，并在主机防火墙中允许该端口。
- **离家在外：** 你需要 Tailscale 或隧道；参见[手机和远程访问](/ecosystem/computer/phone-and-remote/)。
- **主机休眠：** 休眠的机器无法提供服务；参见[保持运行](/ecosystem/computer/phone-and-remote/keep-it-running)。

## Windows 上终端无法打开（VCRUNTIME140.dll）

终端后端需要 Microsoft Visual C++ Redistributable。从 Microsoft 安装 x64 版本，重启机器，然后重新启动 `cptr run`。

## Docker：设置向导重现 / 我的状态丢失了

容器启动时没有挂载 `/data` 卷，所以看起来像是全新安装。你的数据几乎肯定还在卷中；诊断时切勿删除它。使用附加的卷重新创建容器：

```bash
docker run -d -p 8000:8000 -v cptr-data:/data ghcr.io/open-webui/computer:latest
```

你的账户、工作区和设置都会恢复。

## Docker：SQLite 无法写入 /data

你绑定挂载了一个容器用户无法写入的主机目录。修复主机目录的所有权，或者（更简单更可靠）使用命名卷（`-v cptr-data:/data`）而不是绑定挂载。不要为了走捷径而以特权模式运行容器。

## 我的项目文件夹在 Docker 中不可见

容器只看到你挂载到其中的内容。将你的项目添加为绑定挂载，并使用**容器**路径作为工作区路径：

```bash
docker run -d -p 8000:8000 -v cptr-data:/data -v ~/code/myproject:/workspace/myproject ghcr.io/open-webui/computer:latest
```

然后添加 `/workspace/myproject` 作为工作区。

## 代理模型在选择器中缺失 / 检测未就绪

在**设置 → 管理 → 代理**中检查配置文件状态；每个状态都有特定的修复方法：

- **not found**：代理 CLI 不在服务器的 PATH 上。安装它，或者在配置文件的命令字段中设置绝对路径。
- **missing dependency**：Claude Code 还需要 `claude-agent-sdk` Python 包在 cptr 的环境中：`pip install claude-agent-sdk`。
- **auth unknown**：在主机上运行代理自己的登录命令（`claude`、`codex login`、`agent login`、`cline auth`……）。

检测结果会缓存约 30 秒，所以修复后稍等片刻。每个代理的完整设置：[编码代理](/ecosystem/computer/ai/coding-agents)。

## 我的机器人不回复

按此列表排查：

1. 服务器是否在运行？机器人的**启用**开关是否在**设置 → 管理 → 机器人**中打开？
2. 保存令牌时是否通过了**验证**检查？
3. **允许发送者**中是否包含你的平台用户 ID？非空列表会静默忽略所有其他人。
4. Discord 和 Slack 需要 `websockets` Python 包：`pip install websockets`。
5. WhatsApp 仅支持 webhook；Meta webhook URL 必须指向一个可公开访问的 `https://<your-host>/api/webhooks/whatsapp/<bot_id>`。

各平台完整设置：[消息机器人](/ecosystem/computer/automate/messaging-bots)。

## 终端或聊天在反向代理后面断开连接

Computer 使用 Socket.IO：如果你的代理不转发 WebSocket 升级头（`Upgrade` / `Connection`），终端和流式传输会中断。将它们添加到你的代理配置中；参见 nginx/Caddy/Traefik 配置片段：[反向代理](/ecosystem/computer/phone-and-remote/reverse-proxy)。

## 服务器是否健康？

```bash
curl http://127.0.0.1:8000/api/health
```

返回 `{status, uptime_seconds, pid}`，无需登录。如果这在主机本身上失败，说明服务器没有运行；检查你启动 `cptr run` 的终端。
