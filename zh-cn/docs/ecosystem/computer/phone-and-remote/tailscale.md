---
title: "Tailscale（推荐）"
sidebar_position: 2
---

# Tailscale（推荐）

Tailscale 将你的手机和电脑置于它们自己的私有网络中。没有任何东西暴露给公共互联网，没有端口转发，并且可以在你的手机所在的任何网络上工作。

在两台设备上安装 Tailscale 并登录到同一个账户（[Tailscale 的设置指南](https://tailscale.com/kb/1017/install)）。然后选择两种设置之一。

## 选项 A：纯 tailnet 访问

你 tailnet 上的每台设备都获得一个稳定的私有 IP（以及一个 MagicDNS 名称）。运行 `cptr` 使其在该地址上可访问：

```bash
cptr run --host 0.0.0.0
```

在你的手机上，打开 `http://<tailscale-ip-or-name>:8000`。

需要注意的是：默认的 `cptr run` 绑定到 `127.0.0.1`，tailnet 无法访问。你必须绑定到 Tailscale 接口或 `0.0.0.0`，这也会使其在你的 LAN 上可访问。如果你不确定这对你的网络意味着什么，请改用选项 B。

## 选项 B：Tailscale Serve（HTTPS，cptr 保持在 localhost 上）

Tailscale Serve 从你的 tailnet 代理 HTTPS 到本地端口，因此 `cptr` 保持其默认的 localhost 绑定，而你获得一个合适的 `https://` URL（[PWA 安装](./phone-app)和剪贴板访问等浏览器功能更满意这个）。

`cptr run` 已经运行时：

```bash
tailscale serve --bg localhost:8000
```

获取你的 URL：

```bash
tailscale serve status
```

在手机上打开该 URL 并登录。稍后要移除代理：

```bash
tailscale serve reset
```

Tailscale 可能首次提示管理员为你的 tailnet 启用 HTTPS 证书。

## 验证它离家在外也能工作

关闭手机上的 Wi-Fi，使其使用蜂窝网络，然后再次打开 URL。如果你的工作区和正在运行的终端会话加载成功，就完成了；这正是它在火车上时的样子。

如果无法加载：在电脑上检查 `http://127.0.0.1:8000/api/health`，确认两台设备都出现在 Tailscale 管理控制台中，并重新运行 `tailscale serve status`。

:::warning 不要使用 Funnel
`tailscale funnel` 将 URL 发布到整个互联网，而不仅仅是你的设备。只有当你理解你正在公开时才这样做。然后像对待 [Cloudflare Tunnel / ngrok 设置](./cloudflare-and-ngrok)一样处理：在它前面放置提供商的认证，不要仅依赖 Computer 的登录。
:::
