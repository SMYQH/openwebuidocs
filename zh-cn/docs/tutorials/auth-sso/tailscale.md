---
sidebar_position: 50
title: "Tailscale"
---

# Tailscale 集成 {#tailscale-integration}

**从任意设备私密、加密地访问 Open WebUI——无需开放端口，也无需手动管理证书。**

[Tailscale](https://tailscale.com) 会在你的设备之间建立一个基于 WireGuard 的 mesh VPN（即 “tailnet”）。每台设备都会获得一个稳定主机名，例如 `my-server.tail1234.ts.net`，并且 Tailscale 还能自动配置受信任的 HTTPS 证书。你的 Open WebUI 实例可以保持完全私有，只有 tailnet 中的设备才能访问。

:::tip 何时使用 Tailscale
如果你希望跨设备**私密地访问 Open WebUI，并要求身份认证**，而不把它暴露到公网，可以使用 Tailscale。它适合个人用户、小团队，或需要在外通过手机、笔记本访问家庭服务器的场景。
:::

---

## 前提条件 {#prerequisites}

| 要求 | 详情 |
| :--- | :--- |
| **Open WebUI** | 已运行在本地端口 `8080`（默认值） |
| **Tailscale 账号** | 个人使用可免费注册，见 [tailscale.com](https://tailscale.com) |
| **已安装 Tailscale** | 运行 Open WebUI 的服务器以及所有客户端设备都需安装 |

---

## 快速开始 {#quick-start}

### 1. 安装 Tailscale {#1-install-tailscale}

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

### 2. 连接服务器 {#2-connect-the-server}

在运行 Open WebUI 的机器上执行：

```bash
sudo tailscale up
```

你的机器将获得一个类似 `my-server.tail1234.ts.net` 的 tailnet 主机名。可通过以下命令查看：

```bash
tailscale status
```

### 3. 访问 Open WebUI {#3-access-open-webui}

在同一 tailnet 上的任意设备中打开：

```
http://my-server.tail1234.ts.net:8080
```

此连接已由 WireGuard 端到端加密。如果你需要语音通话等要求 HTTPS 的浏览器功能，请继续阅读下一节。

---

## 使用 Tailscale 启用 HTTPS {#https-with-tailscale}

Tailscale 可以为你的 tailnet 主机名自动配置受信任的 Let's Encrypt 证书，而无需反向代理。

完整 HTTPS 配置步骤（包括证书生成、`tailscale serve`、`WEBUI_URL` 配置等），请参阅专门的参考指南：

👉 [**使用 Tailscale 启用 HTTPS**](/reference/https/tailscale)

简要版本如下：

```bash
# Proxy HTTPS traffic directly to Open WebUI
sudo tailscale serve https / http://localhost:8080
```

此时你的实例就可以通过 `https://my-server.tail1234.ts.net` 访问，并带有有效 TLS 证书。

---

## 通过 Tailscale 实现认证（SSO） {#authentication-via-tailscale-sso}

[Tailscale Serve](https://tailscale.com/kb/1242/tailscale-serve) 可以充当负责认证的反向代理。请求经过 `tailscale serve` 时，Tailscale 会自动在 `Tailscale-User-Login` 请求头中写入已认证用户的邮箱地址。Open WebUI 可以信任此请求头来实现单点登录，因此 tailnet 中的用户无需再输入 Open WebUI 密码即可登录。

### 工作原理 {#how-it-works}

1. Tailscale 边车容器与 Open WebUI 一起运行
2. Tailscale Serve 将 HTTPS 流量代理到 Open WebUI，并注入标识用户身份的请求头
3. Open WebUI 读取 `Tailscale-User-Login` 和 `Tailscale-User-Name` 来识别用户
4. 用户首次访问时会被自动注册并自动登录

### Docker Compose 配置 {#docker-compose-setup}

先创建一个 `tailscale/serve.json` 文件，用于配置 Tailscale Serve 把流量代理到 Open WebUI：

```json title="tailscale/serve.json"
{
    "TCP": {
        "443": {
            "HTTPS": true
        }
    },
    "Web": {
        "${TS_CERT_DOMAIN}:443": {
            "Handlers": {
                "/": {
                    "Proxy": "http://open-webui:8080"
                }
            }
        }
    }
}
```

然后在 Docker Compose 中增加 Tailscale 边车容器：

```yaml title="docker-compose.yaml"
---
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    volumes:
      - open-webui:/app/backend/data
    environment:
      - WEBUI_AUTH_TRUSTED_EMAIL_HEADER=Tailscale-User-Login
      - WEBUI_AUTH_TRUSTED_NAME_HEADER=Tailscale-User-Name
    restart: unless-stopped
  tailscale:
    image: tailscale/tailscale:latest
    environment:
      - TS_AUTH_ONCE=true
      - TS_AUTHKEY=${TS_AUTHKEY}
      - TS_EXTRA_ARGS=--advertise-tags=tag:open-webui
      - TS_SERVE_CONFIG=/config/serve.json
      - TS_STATE_DIR=/var/lib/tailscale
      - TS_HOSTNAME=open-webui
    volumes:
      - tailscale:/var/lib/tailscale
      - ./tailscale:/config
      - /dev/net/tun:/dev/net/tun
    cap_add:
      - net_admin
      - sys_module
    restart: unless-stopped

volumes:
  open-webui: {}
  tailscale: {}
```

你还需要在 Tailscale 管理后台创建一个拥有 **device write** 权限的 [OAuth 客户端](https://tailscale.com/kb/1215/oauth-clients)，并通过 `TS_AUTHKEY` 传入密钥。

你的实例之后会通过 `https://open-webui.TAILNET_NAME.ts.net` 访问。

:::warning 使用 ACLs 限制绕过直连
如果 Tailscale 与 Open WebUI 运行在同一网络环境中，用户可能绕过 Serve 代理直连 Open WebUI，从而跳过受信任请求头认证。请使用 [Tailscale ACLs](https://tailscale.com/kb/1018/acls)，仅允许访问 443 端口。
:::

有关受信任请求头认证的详情，请参阅 [SSO 文档](/features/authentication-access/auth/sso#tailscale-serve)。

---

## Tailscale Funnel（可选的公网访问） {#tailscale-funnel-optional-public-access}

如果你想公开 Open WebUI，又不要求客户端安装 Tailscale，可以通过 [Tailscale Funnel](https://tailscale.com/kb/1223/funnel) 将 `tailscale serve` 端点暴露到公网：

```bash
sudo tailscale funnel https / http://localhost:8080
```

此时你的 Open WebUI 将通过 `https://my-server.tail1234.ts.net` 对公网可访问，并带有有效 TLS 证书。Funnel 会通过 Tailscale 基础设施转发流量，类似于 Cloudflare Tunnel。

:::warning
Funnel 会让你的 Open WebUI 对**整个互联网**开放。启用前，请务必先在 Open WebUI 中完成认证配置。
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
| 设置 CORS 来源 | `CORS_ALLOW_ORIGIN=https://my-server.tail1234.ts.net` |
| 受信任的邮箱请求头 | `WEBUI_AUTH_TRUSTED_EMAIL_HEADER=Tailscale-User-Login` |
| 受信任的姓名请求头 | `WEBUI_AUTH_TRUSTED_NAME_HEADER=Tailscale-User-Name` |

---

## 相关页面 {#related-pages}

- [使用 Tailscale 启用 HTTPS](/reference/https/tailscale)：HTTPS 和 TLS 配置参考
- [SSO（受信任请求头）](/features/authentication-access/auth/sso#tailscale-serve)：受信任请求头的通用配置
- [共享 Open WebUI](/getting-started/sharing)：各类共享方式的总览
