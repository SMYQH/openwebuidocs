---
sidebar_position: 15
title: "与团队共享 Open WebUI"
sidebar_label: "共享 Open WebUI"
description: "让团队访问同一个 Open WebUI 实例，配置账户与资源权限，并以普通用户身份验证访问权限。"
---

# 与团队共享 Open WebUI {#sharing-open-webui}

共享同一个 Open WebUI 实例，让你的团队可以用浏览器使用已连接的模型。在邀请用户之前，先配置好网络访问、账户与权限。

Open WebUI 天生就适合共享。一套实例可以服务整个组织。用户只需打开浏览器即可开始聊天，无需按座位单独安装、无需客户端依赖，也不会把数据割裂在不同机器上。

---

## 搭建一支小团队 {#set-up-a-small-team}

先准备一个管理员账户，以及一个 Open WebUI 服务器能够访问到的模型端点。小团队可以从一套实例开始；当你的工作负载需要更大容量时，再参考[扩展指南](/getting-started/advanced-topics/scaling)。

1. [安装 Open WebUI](/getting-started/quick-start) 并[连接一个模型](/getting-started/quick-start/connect-a-provider)。确认管理员可以发送消息并收到回复。
2. 从下面选择一个[网络访问方式](#opening-your-instance-to-the-team)，并确认同事能访问到登录页。远程访问请使用 HTTPS。
3. [审批用户账户](#the-pending-queue)，或使用你的身份提供商[配置 SSO](/features/authentication-access/auth/sso)。
4. 创建[组](/features/authentication-access/rbac/groups)，并授予合适的[模型](/features/workspace/models)和[知识库](/features/workspace/knowledge)访问权限。请一并查看[默认权限与组权限](/features/authentication-access/rbac/permissions)：权限是累加的。
5. 以普通用户身份登录，并按本页末尾的[访问检查项](#verify-team-access)逐条验证。管理员看到的内容并不能证明同事真的拥有预期权限。

共享实例并不会自动共享所有人的文档或对话。请显式授予知识库访问权限；想分享某段对话快照时，请使用[聊天分享](/features/chat-conversations/chat-features/chatshare)。

## 为团队而生 {#built-for-teams}

### 顺畅接入 {#streamlined-onboarding}

终端用户无需安装任何东西、管理 Docker 或操作终端。只要打开浏览器，访问你的实例 URL 并登录即可。

### 协作式智能 {#collaborative-intelligence}

共享实例意味着共享知识。

| | |
| :--- | :--- |
| **[Channels](/features/channels)** | 团队与 AI 模型实时协作的持久化空间 |
| **共享聊天** | 向同事发送对话的原样快照。只有获得授权的用户和组才能访问私有分享链接。面向整个实例或无需登录的链接需要相应的公开共享和开放共享聊天权限，非管理员用户默认没有这两项权限 |
| **全局提示词与知识库** | 构建专用 Agent，并立即提供给所有人使用 |

分享对话框还可以将聊天上传到 Open WebUI Community 站点。如果希望所有内容都留在内部，请在 Settings > General（管理员区域） 中关闭 **Community Sharing**（或在首次启动前设置 `ENABLE_COMMUNITY_SHARING=false`）。

### 共享算力 {#shared-compute}

如果运行的是本地模型，一台强大的服务器（或集群）就能为整个团队提供能力，而不需要每张桌面都配备足够强的硬件。

### 集中式管理 {#centralized-administration}

在一个地方统一管理所有内容：控制用户可访问的模型、配置 [**基于角色的访问控制（RBAC）**](/features/authentication-access/rbac)、查看审计日志，并按需限制功能。

---

## 将实例开放给团队 {#opening-your-instance-to-the-team}

要共享实例，你需要让它能够通过网络访问。常见做法有三种：从简单的局域网访问，到面向生产的公网域名。

### 1. 零配置局域网访问 {#1-zero-config-lan-local-network}

如果团队成员位于同一局域网或 VPN 中，他们可以通过你的机器本地 IP 和端口访问 Open WebUI。

> `http://192.168.1.100:3000`

Open WebUI 监听所有网络接口（`0.0.0.0`），除非 [`HOST`](/reference/env-configuration#host) 或 `--host` 另有说明。如果同事无法加载页面，请先检查以下几点：

- 在同事的设备上，使用主机的局域网 IP 地址。那里的 `localhost` 指向同事自己的设备。
- 使用主机端口：Docker 快速开始用 `3000`（`-p 3000:8080`），`open-webui serve` 用 `8080`。
- 以 `-p 127.0.0.1:3000:8080` 发布的端口只接受来自主机自身的连接。若要允许局域网访问，请发布为 `-p 3000:8080`。参见 [Docker 端口发布](https://docs.docker.com/engine/network/port-publishing/)。
- 在主机的防火墙中允许该端口的入站连接。在 Windows 上，检查当前所用网络配置文件（专用或公用）对应的规则。
- 如果 Open WebUI 运行在 WSL 2 中，默认情况下其他设备无法访问它。请启用镜像网络模式，或添加 `netsh interface portproxy` 规则，详见[使用 WSL 访问网络应用](https://learn.microsoft.com/en-us/windows/wsl/networking#accessing-a-wsl-2-distribution-from-your-local-area-network-lan)。

### 2. 安全的私有网络（推荐） {#2-secure-private-networks-recommended}

适合无需暴露到公共互联网的远程团队。叠加网络和安全隧道可以在不开放防火墙端口的情况下提供加密访问。

| | |
| :--- | :--- |
| **[Tailscale](/reference/https/tailscale)** | 带 MagicDNS 的私有 mesh 网络（`https://open-webui.tailnet-name.ts.net`） |
| **[Cloudflare Tunnels](/reference/https/cloudflare-tunnel)** | 通过 Cloudflare 边缘暴露，并由 Cloudflare Access（Zero Trust）保护 |
| **[ngrok](/reference/https/ngrok)** | 适合开发或测试时的临时快速共享 |

### 3. 公网 HTTPS（反向代理） {#3-public-https-reverse-proxy}

对于生产部署，请将 Open WebUI 放在反向代理之后，在你自己的域名上完成 SSL/TLS 终止（例如 `ai.yourcompany.com`）。

| | |
| :--- | :--- |
| **[Nginx](/reference/https/nginx)** | 行业标准 Web 服务器与反向代理 |
| **[Caddy](/reference/https/caddy)** | 配置简洁，自动启用 HTTPS |
| **[HAProxy](/reference/https/haproxy)** | 高性能负载均衡与代理 |

---

## 团队接入方式 {#onboarding-your-team}

当实例可以通过网络访问后，你还需要管理用户如何创建账号并登录。

### 待审核队列 {#the-pending-queue}

第一个注册的用户会成为**管理员**。创建首个账户时，系统会自动关闭管理员区域设置 > 认证中的**新用户注册**。管理员重新打开后，其他人才能注册。除非该页面的**默认用户角色**设为 `user`，否则新账户会进入**待审核**状态，管理员批准前无法访问模型或使用平台。`DEFAULT_USER_ROLE` 只在首次启动时设置默认角色，此后以已保存的设置为准。创建首个账户时，系统会将 `ENABLE_SIGNUP` 覆盖为关闭。

### 企业级单点登录（SSO） {#enterprise-single-sign-on-sso}

对于手动审批无法扩展的组织，Open WebUI 可以与现有身份提供商集成。

| | |
| :--- | :--- |
| **OAuth / OIDC** | 通过 **Google**、**Microsoft**、**Okta** 或 **Keycloak** 认证 |
| **组映射** | 将 IdP 组直接映射到 Open WebUI 组 |
| **[SCIM 2.0](/features/authentication-access/auth/scim)** | 自动完成用户和组的开通与回收 |

[**了解如何设置 SSO →**](/features/authentication-access/auth/sso)

## 验证团队访问权限 {#verify-team-access}

用一个属于目标组的普通账户检查以下各项：

- 被允许的模型可见，并能回复测试消息。
- 共享的知识库可以访问，并能回答来自测试文档的问题。
- 该账户无法访问受限的模型和知识库，即使使用直达链接也不行。

再用组外的账户重复检查，确认仍然无法访问受限资源。如果任一账户能访问超出预期的资源，请查阅[组与资源访问权限](/features/authentication-access/rbac/groups#resource-access-rbac)。
