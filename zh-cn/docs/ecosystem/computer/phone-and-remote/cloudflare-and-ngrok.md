---
title: "Cloudflare Tunnel 和 ngrok"
sidebar_position: 3
---

# Cloudflare Tunnel 和 ngrok

两者都给你一个转发到 `localhost:8000` 的公共 URL：无需端口转发，默认的 `cptr run` 绑定按原样工作。公开意味着任何找到该 URL 的人都能到达你的登录页面，而 Computer 的密码此时是互联网和你的 shell 之间的唯一屏障。因此，使用提供商的认证层作为第二道门。两个提供商都传递 WebSocket，Computer 的终端和流式传输需要它。

## Cloudflare Tunnel

快速试用（临时随机 URL，无需账户配置）：

```bash
cloudflared tunnel --url http://localhost:8000
```

`cloudflared` 打印一个 `https://....trycloudflare.com` URL；在你的手机上打开它。

对于实际使用，在你的域名上创建一个**命名隧道**，并在主机名前放置一个 **Cloudflare Access** 策略，这样 Cloudflare 会在任何请求到达 Computer 之前对你进行认证（电子邮件 OTP、Google、GitHub……）。按照 Cloudflare 的文档操作：

- [创建隧道](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
- [添加 Access 应用](https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/)

## ngrok

```bash
ngrok http 8000
```

ngrok 打印一个公共的 `https://` URL。添加 ngrok 自己的认证，使 URL 不对所有人开放。基本认证：

```bash
ngrok http 8000 --basic-auth "you:a-long-password"
```

或通过 `--oauth` 使用 OAuth（Google、GitHub 等）。参见 [ngrok 文档](https://ngrok.com/docs)了解当前标志和仪表板管理的边缘。

## 选择哪一个？

- **Cloudflare Tunnel**：如果你在 Cloudflare 上有一个域名，并希望拥有带有真实访问策略的永久 URL。
- **ngrok**：如果你现在就想用一个命令获得一个 URL。
- 如果你根本不需要公共 URL，[Tailscale](./tailscale) 是更好的默认选择：天生私有，无需配置第二认证层。

:::warning
不要裸机运行其中任何一个。如果没有 Cloudflare Access 或 ngrok 认证在前面，你就向互联网发布了一个 SSH 等效的登录页面。参见[安全模型](./security)。
:::
