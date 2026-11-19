---
sidebar_position: 3
title: "使用 Tailscale 配置 HTTPS"
---

# 使用 Tailscale 配置 HTTPS {#https-using-tailscale}


**在你的私有网络中，从任意位置安全访问 Open WebUI。无需开放端口、无需自己管理证书，也无需公网暴露。**

Tailscale 在你的设备之间建立加密的网状 VPN（即 tailnet）。每台设备都有固定的主机名，例如 `my-server.tail1234.ts.net`。Tailscale 可以为该主机名自动签发受信任的 HTTPS 证书。你的 Open WebUI 实例完全不对外公开，只有 tailnet 中的设备可以访问。

:::tip 何时使用 Tailscale
如果你希望在不将 Open WebUI 暴露到公网的情况下，实现**跨设备、私有且可认证的访问**，Tailscale 非常合适。它尤其适用于个人部署、小团队，或需要在外通过手机 / 笔记本访问家庭服务器的场景。
:::

:::info 想看完整指南？
本页只介绍 **HTTPS 配置**。如需完整的 Tailscale 接入方案，包括 SSO 认证和 Docker Compose 边车配置，请参阅[**Tailscale 集成教程**](/tutorials/auth-sso/tailscale)。
:::

---

## 前提条件 {#prerequisites}

| 要求 | 详情 |
| :--- | :--- |
| **Open WebUI** | 已在本地端口 `8080`（默认值）运行 |
| **Tailscale 账号** | 个人用途可免费注册，见 [tailscale.com](https://tailscale.com) |
| **已安装 Tailscale** | 运行 Open WebUI 的服务器及所有客户端设备都需要安装 |

---

## 1. 安装 Tailscale {#1-install-tailscale}

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="mac" label="macOS" default>

从 [Mac App Store](https://apps.apple.com/app/tailscale/id1475387142) 下载，或执行：

```bash
brew install tailscale
```

  </TabItem>
  <TabItem value="linux" label="Linux">

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

  </TabItem>
  <TabItem value="windows" label="Windows">

从 [tailscale.com/download](https://tailscale.com/download/windows) 下载。

  </TabItem>
</Tabs>

## 2. 连接服务器 {#2-connect-the-server}

在运行 Open WebUI 的机器上执行：

```bash
sudo tailscale up
```

你的机器会获得一个类似 `my-server.tail1234.ts.net` 的 tailnet 主机名。可以通过以下命令查看：

```bash
tailscale status
```

## 3. 访问 Open WebUI {#3-access-open-webui}

在同一 tailnet 上的任意设备中打开：

```
http://my-server.tail1234.ts.net:8080
```

此连接已由 WireGuard 端到端加密。若要使用要求 HTTPS 的浏览器功能（例如语音通话），请继续执行下一步。

---

## 使用 Tailscale 证书启用 HTTPS {#enable-https-with-tailscale-certificates}

Tailscale 可以为你的 tailnet 主机名自动申请受信任的 Let's Encrypt 证书。

### 1. 在管理后台启用 HTTPS {#1-enable-https-in-the-admin-console}

前往 [**Tailscale Admin → DNS**](https://login.tailscale.com/admin/dns)，打开 **HTTPS Certificates**。

### 2. 生成证书 {#2-generate-a-certificate}

```bash
sudo tailscale cert my-server.tail1234.ts.net
```

该命令会在当前目录生成两个文件：

- `my-server.tail1234.ts.net.crt`（证书）
- `my-server.tail1234.ts.net.key`（私钥）

### 3. 通过 HTTPS 提供 Open WebUI {#3-serve-open-webui-over-https}

使用 `tailscale serve` 把 HTTPS 流量直接代理到 Open WebUI，而无需额外反向代理：

```bash
sudo tailscale serve https / http://localhost:8080
```

现在你可以通过以下地址访问 Open WebUI：

```
https://my-server.tail1234.ts.net
```

无需显式端口号。Tailscale 会负责 TLS 终止，并把流量转发到本地 Open WebUI。

---

## 配置 Open WebUI {#configure-open-webui}

设置 `WEBUI_URL`，确保 OAuth 回调和内部链接正确解析：

```bash
docker run -d \
  -p 8080:8080 \
  -e WEBUI_URL=https://my-server.tail1234.ts.net \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

---

## Tailscale Funnel（可选的公网访问） {#tailscale-funnel-optional-public-access}

如果你想公开分享 Open WebUI，而不要求客户端安装 Tailscale，可以用 Tailscale Funnel 将 `tailscale serve` 的端点公开到互联网：

```bash
sudo tailscale funnel https / http://localhost:8080
```

你的 Open WebUI 之后将通过 `https://my-server.tail1234.ts.net` 对公网可访问，并带有有效 TLS 证书。Funnel 会通过 Tailscale 基础设施转发流量，类似于 Cloudflare Tunnel。

:::warning
Funnel 会让你的 Open WebUI 对互联网中的所有人开放。启用前，请确保你已经在 Open WebUI 中配置好认证。
:::

---

## 快速参考 {#quick-reference}

| 操作 | 命令 / 值 |
| :--- | :--- |
| 加入 tailnet | `sudo tailscale up` |
| 查看主机名 | `tailscale status` |
| 通过 HTTPS 提供服务 | `sudo tailscale serve https / http://localhost:8080` |
| 公网访问（Funnel） | `sudo tailscale funnel https / http://localhost:8080` |
| 手动生成证书 | `sudo tailscale cert my-server.tail1234.ts.net` |
| 管理后台 | [login.tailscale.com/admin](https://login.tailscale.com/admin) |
| 设置 CORS origin | `CORS_ALLOW_ORIGIN=https://my-server.tail1234.ts.net` |
