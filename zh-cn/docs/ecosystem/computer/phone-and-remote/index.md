---
title: "在手机上使用"
sidebar_position: 1
---

# 在手机上使用

Open WebUI Computer 将你的整个机器呈现给任何浏览器。你的手机就是一个浏览器。根据你所在的位置选择适合的方式：

| 你的情况 | 操作 |
|---|---|
| 手机与电脑在同一个 Wi-Fi 上 | 运行 `cptr run --host 0.0.0.0`，然后在手机上打开 `http://<computer-ip>:8000` |
| 离家在外 | [Tailscale](./tailscale)（推荐），或 [Cloudflare Tunnel / ngrok](./cloudflare-and-ngrok) 获取公共 URL |
| 你已经运行了一个域名和反向代理 | [反向代理和 SSO](./reverse-proxy) |

在选择之前需要了解一件事：已登录用户拥有对你的文件和 shell 的完全访问权限，所以选择一种只有你能访问登录页面的方式（详情见[安全模型](./security)）。

## 同一 Wi-Fi

`cptr run` 默认绑定到 `127.0.0.1`，只有电脑本身可以访问。改为绑定到所有接口：

```bash
cptr run --host 0.0.0.0
```

找到你电脑的 LAN IP（macOS：**系统设置 → Wi-Fi → 详情**；或 `ipconfig getifaddr en0`；Linux：`ip addr`），然后在手机上打开 `http://<computer-ip>:8000` 并登录。

## 离家在外

你需要一条从互联网回到你的机器的路径。三个好选择：

- **[Tailscale](./tailscale)**：推荐。你设备之间的私有网络；没有任何内容是公开的，`cptr` 可以保持在 localhost 上。
- **[Cloudflare Tunnel](./cloudflare-and-ngrok)**：通过 Cloudflare 边缘的永久公共 URL，最好与 Cloudflare Access 配合使用。
- **[ngrok](./cloudflare-and-ngrok)**：一个命令即可获得公共 URL，最好与 ngrok 内置的认证功能配合使用。

## 已经有域名？

如果你在你控制的机器上运行 nginx、Caddy 或 Traefik，将 `cptr` 像任何其他 Web 应用一样放在它后面，包括通过受信任标头认证的单点登录。参见[反向代理和 SSO](./reverse-proxy)。

## 然后让它持久化

每个人都想要的两个后续操作：

- [安装应用 (PWA)](./phone-app)：主屏幕图标、分享到工作区、快捷方式。
- [保持运行](./keep-it-running)：开机启动，在重启后存活，阻止你的机器休眠。
