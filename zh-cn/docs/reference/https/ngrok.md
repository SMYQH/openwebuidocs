---
sidebar_position: 2
title: "通过 ngrok 启用 HTTPS"
---

# 通过 ngrok 启用 HTTPS {#https-using-ngrok}


**为本地 Open WebUI 立刻获得公网 HTTPS。零配置、零开放端口。**

ngrok 会在公网 URL 和本机之间建立安全隧道。这样可以快速启用 HTTPS，便于开发、演示或测试语音通话等需要安全上下文的功能。

:::tip 何时使用 ngrok
ngrok 适合**开发与测试**。生产部署请使用 [Nginx](/reference/https/nginx) 或 [Caddy](/reference/https/caddy) 等反向代理，或使用 [Cloudflare Tunnel](/reference/https/cloudflare-tunnel) 实现零信任访问。
:::

---

## 前提条件 {#prerequisites}

| 要求 | 详情 |
| :--- | :--- |
| **Open WebUI** | 已在本地端口 `8080`（默认值）运行 |
| **ngrok 账号** | 可在 [ngrok.com](https://ngrok.com) 免费注册，并获得稳定的 authtoken |

---

## 1. 安装 ngrok {#1-install-ngrok}

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="mac" label="macOS" default>

```bash
brew install ngrok
```

  </TabItem>
  <TabItem value="linux" label="Linux">

```bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok-v3-stable-linux-amd64.tgz \
  | sudo tar xz -C /usr/local/bin
```

  </TabItem>
  <TabItem value="windows" label="Windows">

```powershell
choco install ngrok
```

或直接从 [ngrok.com/download](https://ngrok.com/download) 下载。

  </TabItem>
</Tabs>

## 2. 完成认证 {#2-authenticate}

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

你的 authtoken 可在 [dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken) 获取。

## 3. 启动隧道 {#3-start-the-tunnel}

```bash
ngrok http 8080
```

ngrok 会输出类似下面的公网 URL：

```
Forwarding  https://a1b2-203-0-113-42.ngrok-free.app → http://localhost:8080
```

直接在浏览器中打开这个 `https://` URL 即可。

---

## 配置 Open WebUI {#configure-open-webui}

设置 `WEBUI_URL`，确保 OAuth 回调与内部链接都能正确解析：

```bash
docker run -d \
  -p 8080:8080 \
  -e WEBUI_URL=https://a1b2-203-0-113-42.ngrok-free.app \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

:::warning
使用 ngrok 免费套餐时，每次重启隧道都会更换 URL。请相应更新 `WEBUI_URL`，或使用付费的 [ngrok 自定义域名](https://ngrok.com/docs/guides/how-to-set-up-a-custom-domain/)获得固定 URL。
:::

---

## 自定义域名（可选） {#custom-domain-optional}

在付费 ngrok 计划中，你可以申请固定子域名，使 URL 不再变化：

```bash
ngrok http 8080 --url=your-name.ngrok-free.app
```

这样你就能将固定 URL 填入 `WEBUI_URL`，无需再更新。

---

## 快速参考 {#quick-reference}

| 操作 | 命令 / 值 |
| :--- | :--- |
| 启动隧道 | `ngrok http 8080` |
| 自定义域名 | `ngrok http 8080 --url=your-name.ngrok-free.app` |
| 控制台 | [dashboard.ngrok.com](https://dashboard.ngrok.com) |
| 查看请求流量 | `http://localhost:4040`（ngrok 本地调试面板） |
| 设置 CORS 来源 | `CORS_ALLOW_ORIGIN=https://your-name.ngrok-free.app` |

---

## 限制 {#limitations}

| 问题 | 说明 |
| :--- | :--- |
| **免费套餐的 URL 会变更** | 未使用自定义域名时，每次重启隧道都会更换 URL |
| **首次访问提示页** | 免费套餐会在首次访问时显示 ngrok 提示页 |
| **不适合生产环境** | ngrok 会增加延迟，也是单点故障；请改用反向代理或 Cloudflare Tunnel |
| **速率限制** | 免费套餐有连接速率限制，付费套餐不受此限制 |
