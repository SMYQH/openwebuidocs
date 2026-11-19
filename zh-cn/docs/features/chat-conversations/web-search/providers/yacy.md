---
sidebar_position: 18
title: "Yacy"
---

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎参与贡献，请参阅贡献指南。

:::

:::tip

若要查看所有与网页搜索相关的环境变量（包括并发设置、结果数量等），请参阅 [环境配置文档](/reference/env-configuration#web-search)。

:::

:::tip 故障排查

遇到网页搜索问题时，请参阅[网页搜索故障排查指南](/troubleshooting/web-search)，了解如何解决代理配置、连接超时和内容为空等常见问题。

:::

## Yacy API {#yacy-api}

### 设置 {#setup}

1. 前往：`Settings` -> `Web Search`（管理员区域）
2. 打开 `Enable Web Search`
3. 将 `Web Search Engine` 从下拉框中设为 `yacy`
4. 将 `Yacy Instance URL` 设为以下示例之一：

    - `http://yacy:8090`（使用容器名和暴露端口，适合 Docker 部署）
    - `http://host.docker.internal:8090`（使用 `host.docker.internal` 和宿主机端口，适合 Docker 部署）
    - `https://<yacy.local>:8443`（使用本地域名，适合局域网访问）
    - `https://yacy.example.com`（为自托管的 Yacy 实例使用自定义域名，适合公开或私有访问）
    - `https://yacy.example.com:8443`（通过 HTTPS 连接到 Yacy 的默认 HTTPS 端口）

5. 填写 Yacy 用户名，表单要求填写后才能保存。如果你的 Yacy 实例需要身份验证，再填写密码。Open WebUI 仅在 Yacy 要求验证时才发送凭据，所以不要求验证的实例可以使用任意用户名，并将密码留空。
6. 点击保存

![Open WebUI 管理面板中的 Yacy 配置](/images/tutorial_yacy.png)
