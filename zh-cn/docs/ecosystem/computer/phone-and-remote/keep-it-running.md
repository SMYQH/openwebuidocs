---
title: "保持运行"
sidebar_position: 6
---

# 保持运行

两件不同的事情可能停止你的工作：关闭浏览器标签页（无害）和 `cptr` 进程死亡（有害）。以下是让第二件事不再发生的方法。

## 什么在什么情况下幸存

| 事件 | 会发生什么 |
|---|---|
| 你关闭标签页 / 失去信号 / 锁定手机 | 没有任何停止。终端、代理任务和会话在服务器端运行；从任何设备重新连接并继续你离开的地方。 |
| `cptr` 进程退出，或主机重启或休眠 | 会话结束。你的文件、聊天和配置安全地保留在磁盘上，但正在运行的终端和执行中的代理工作会停止。 |

所以任务是：在启动时启动 `cptr`，如果崩溃则重新启动，并阻止机器休眠。

## 开机启动

在你的虚拟环境中使用 `cptr` 的绝对路径（在 venv 激活时使用 `which cptr` 查找）；启动时的服务没有你的 shell 的 PATH。

### macOS（launchd）

创建 `~/Library/LaunchAgents/com.openwebui.cptr.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openwebui.cptr</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/you/venvs/cptr/bin/cptr</string>
        <string>run</string>
        <string>--headless</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

立即加载（并自动在每次登录时加载）：

```bash
launchctl load ~/Library/LaunchAgents/com.openwebui.cptr.plist
```

`--headless` 阻止 `cptr` 尝试打开浏览器窗口。

### Linux（systemd 用户服务）

创建 `~/.config/systemd/user/cptr.service`：

```ini
[Unit]
Description=Open WebUI Computer

[Service]
ExecStart=/home/you/venvs/cptr/bin/cptr run --headless
Restart=on-failure

[Install]
WantedBy=default.target
```

```bash
systemctl --user enable --now cptr
loginctl enable-linger $USER   # 即使未登录也保持运行
```

### Windows（任务计划程序）

任务计划程序 → **创建任务**：触发器**登录时**，操作**启动程序**，使用 `cptr.exe` 的完整路径（例如 `C:\Users\you\venvs\cptr\Scripts\cptr.exe`）和参数 `run --headless`。在设置下，启用"如果任务失败，每隔……重新启动"。

### Docker

使用重启策略；Docker 在崩溃和重启后重新启动容器：

```yaml
services:
  cptr:
    image: ghcr.io/open-webui/computer:latest
    restart: unless-stopped
```

（或 `docker run --restart unless-stopped ...`）。完整设置：[Docker 安装](/ecosystem/computer/install/docker)。

## 阻止机器休眠

休眠的主机无法提供任何服务。

- **macOS：** **系统设置 → 电池 → 选项 → 显示器关闭时防止自动休眠**（适用于电源适配器）。或者从终端临时操作：`caffeinate -s` 在运行时保持 Mac 唤醒。
- **Linux：** 桌面发行版默认会挂起。在桌面电源设置中禁用自动挂起，或在 `/etc/systemd/logind.conf` 中设置 `IdleAction=ignore`。
- **Windows：** **设置 → 系统 → 电源** → 将"插入电源时，让设备进入睡眠状态"设置为**从不**。
- **合上盖子的笔记本电脑：** 合上盖子会使机器休眠，与上述设置无关。保持插电状态，并将合上盖子设置为"不执行任何操作"（macOS 需要上述防止休眠设置；Linux：`logind.conf` 中的 `HandleLidSwitch=ignore`；Windows：电源设置中的合盖动作）。

## 验证

重启机器，不要碰它，然后从你的手机打开 Computer。如果加载成功，你就完成了：主机上的 `curl http://127.0.0.1:8000/api/health` 确认服务已启动。如果出了问题，检查[故障排除](/ecosystem/computer/troubleshooting)。
