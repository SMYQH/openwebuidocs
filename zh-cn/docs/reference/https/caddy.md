---
sidebar_position: 202
title: "使用 Caddy 的 HTTPS"
---


## 使用 Caddy 的 HTTPS {#https-using-caddy}

确保用户与 Open WebUI 之间的通信安全至关重要。HTTPS（HyperText Transfer Protocol Secure）会对传输中的数据进行加密，防止窃听和篡改。通过将 Caddy 配置为反向代理，你可以轻松为 Open WebUI 部署添加 HTTPS，同时提升安全性和可信度。

本指南提供一个简单的实操流程，帮助你在 Ubuntu 服务器上使用 Caddy 作为 Open WebUI 的反向代理，并借助自动证书管理启用 HTTPS。

接下来我们将按以下步骤完成配置：

- [使用 Caddy 的 HTTPS](#https-using-caddy)
- [Docker](#docker)
  - [安装 Docker](#installing-docker)
- [Open WebUI](#openwebui)
  - [安装 Open WebUI](#installing-openwebui)
- [Caddy](#caddy)
  - [安装 Caddy](#installing-caddy)
  - [配置 Caddy](#configure-caddy)
- [测试 HTTPS](#testing-https)
  - [可选：通过反向代理设置安全头](#optional-security-headers-via-reverse-proxy)
- [更新 Open WebUI](#updating-open-webui)
  - [停止 Open WebUI](#stopping-open-webui)
  - [拉取最新镜像](#pulling-the-latest-image)
  - [启动 Open WebUI](#starting-open-webui)

## Docker

按照 Docker 官方指南配置 apt 仓库：[Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)

我在示例中也包含了 `docker-compose`，因为运行 `docker compose` 时会用到它。

### 安装 Docker {#installing-docker}

下面是我在 Ubuntu 上安装 Docker 时使用的命令：

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose
```

## Open WebUI {#openwebui}

先为 Open WebUI 项目创建一个目录：

```bash
mkdir -p ~/open-webui
cd ~/open-webui
```

### 安装 Open WebUI {#installing-openwebui}

在 `~/open-webui` 目录中创建一个 `docker-compose.yml` 文件。示例里保留了一段注释，用于演示如何为 Qdrant 设置环境变量；如果你还需要配置其他[环境变量](/reference/env-configuration)，也可以按同样方式添加。

```yaml
services:
    open-webui:
        image: ghcr.io/open-webui/open-webui:main
        container_name: open-webui
        ports:
            - "8080:8080"
        volumes:
            - ./data:/app/backend/data
        # environment:
        #     - "QDRANT_API_KEY=API_KEY_HERE"
        #     - "QDRANT_URI=https://example.com"
        restart: unless-stopped
```

## Caddy

Caddy 是一个强大的 Web 服务器，会自动替你管理 TLS 证书，因此非常适合通过 HTTPS 提供 Open WebUI 服务。

### 安装 Caddy {#installing-caddy}

请参考 [Caddy 在 Ubuntu 上的安装指南](https://caddyserver.com/docs/install#debian-ubuntu-raspbian)。

### 配置 Caddy {#configure-caddy}

接下来需要修改 `Caddyfile`，将其替换为你的域名。

编辑 `/etc/caddy/Caddyfile` 文件：

```bash
sudo nano /etc/caddy/Caddyfile
```

然后将配置更新为如下内容：

```caddyfile
your-domain.com {
  reverse_proxy localhost:8080
}
```

请务必将 `your-domain.com` 替换为你的真实域名。

## 测试 HTTPS {#testing-https}

假设你已经将 DNS 记录指向服务器 IP，现在可以在 `~/open-webui` 目录中运行 `docker compose up`，测试 Open WebUI 是否可以通过 HTTPS 访问。

```bash
cd ~/open-webui
docker compose up -d
```

现在你应该可以通过 `https://your-domain.com` 访问 Open WebUI。

## 可选：通过反向代理设置安全头

Open WebUI 支持直接在应用层通过环境变量设置安全头（推荐路径——参见 [Security Headers](/getting-started/advanced-topics/hardening#security-headers)）。如果你在同一台 Caddy 实例后面托管了多个应用，或者你的部署不允许直接修改环境变量，也可以选择在代理层设置这些头。

**只在一处设置。** 在应用层和代理层同时设置同一个头会产生重复指令：重复的 `Content-Security-Policy` 头会被浏览器合并（取交集），可能让你的策略意外收紧或失效；重复的 `Strict-Transport-Security` 或 `X-Frame-Options` 头则会因浏览器实现差异而产生歧义行为。如果你已经通过环境变量设置了 `HSTS`、`XFRAME_OPTIONS`、`XCONTENT_TYPE`、`REFERRER_POLICY`、`PERMISSIONS_POLICY` 或 `CONTENT_SECURITY_POLICY` 中的任意一项，请跳过本节。

在你现有的 site 块中追加如下 `header` 块：

```caddyfile
your.domain.example {
	header {
		Strict-Transport-Security "max-age=31536000; includeSubDomains"
		X-Frame-Options "DENY"
		X-Content-Type-Options "nosniff"
		Referrer-Policy "strict-origin-when-cross-origin"
		Permissions-Policy "camera=(), microphone=(), geolocation=()"
		-Server
	}

	reverse_proxy localhost:8080
}
```

**HSTS 一旦启用就很难撤销。** `max-age=31536000`（1 年）配合 `includeSubDomains`，会让所有访问过该域名的浏览器在该域名及其**所有子域名**上拒绝使用明文 HTTP，整整持续一年——这无法在服务端快速撤销（你必须下发 `max-age=0`，并等待每个客户端重新访问）。仅当所有当前和未来的子域名都提供有效的 HTTPS 时，才保留 `includeSubDomains`。如果不确定，可以从一个较短的值开始，例如 `max-age=300`，确认 HTTPS 在各处都正常工作后再逐步调大。除非你完全了解其后果（几乎是永久性的，且需要单独提交到浏览器的 preload 列表），**不要**添加 `preload`。

`-Server` 指令会移除 Caddy 默认添加的 `Server` 响应头。Caddy 会自动处理 WebSocket 升级和 SSE 连接——Open WebUI 的流式响应不需要任何额外配置。

上面的 `Permissions-Policy` 示例是一个常见敏感特性的拒绝列表，并非穷尽。如果你的部署需要使用语音输入或摄像头采集，请把对应指令设为 `(self)` 而不是直接删除。

**Content-Security-Policy。** CSP 与部署强相关（自定义插件、嵌入式 iframe、外部模型提供商、Artifacts/代码渲染、语音输入等），因此本节**不**提供开箱即用的代理层 CSP。请通过 `CONTENT_SECURITY_POLICY` 环境变量设置 CSP，并使用 `CONTENT_SECURITY_POLICY_REPORT_ONLY` 在强制启用前先得到一份可用的策略——参见 [Security Headers](/getting-started/advanced-topics/hardening#security-headers)。

重新加载 Caddy 后，验证这些头是否已生效：

```bash
curl -sI https://your.domain.example | grep -E "Strict-Transport|X-Frame|X-Content|Referrer|Permissions"
```

## 更新 Open WebUI {#updating-open-webui}

再补充一条：如何在不丢失数据的情况下更新 Open WebUI。由于我们使用 volume 存储数据，因此只需拉取最新镜像并重启容器即可。

### 停止 Open WebUI {#stopping-open-webui}

首先停止并删除现有容器：

```bash
docker rm -f open-webui
```

### 拉取最新镜像 {#pulling-the-latest-image}

然后拉取最新镜像：

```bash
docker pull ghcr.io/open-webui/open-webui:main
```

### 启动 Open WebUI {#starting-open-webui}

最后重新启动 Open WebUI 容器：

```bash
docker compose up -d
```
