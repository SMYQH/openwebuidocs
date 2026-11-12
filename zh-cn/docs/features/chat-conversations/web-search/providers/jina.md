---
sidebar_position: 7
title: "Jina"
---

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎贡献更多内容，可查看 contributing 教程。

:::

:::tip

若要查看所有与 Web Search 相关的环境变量（包括并发设置、结果数量等），请参阅 [环境配置文档](/reference/env-configuration#web-search)。

:::

:::tip 故障排查

如果你在 web search 上遇到问题，请查看 [Web Search 故障排查指南](/troubleshooting/web-search)，其中涵盖了代理配置、连接超时、内容为空等常见问题。

:::

# Jina Web Search 集成 {#jina-web-search-integration}

本指南说明如何将 [Jina AI](https://jina.ai/) 这一强大的 AI 搜索基础设施集成到 Open WebUI 中。该集成使用 Jina 位于 `s.jina.ai` 的 Search API 提供 web search 能力。

## 概览 {#overview}

Open WebUI 会把每个查询发送到 Jina 的 Search API，并把结果以链接、标题和摘要的形式读回。Jina 另有一个独立的 DeepSearch 产品——一个会迭代地进行搜索与推理的 agent——但本集成调用的并不是它，因此它的那些参数在这里并不适用。

## 价格与 API Key {#pricing-and-api-key}

在 Open WebUI 中使用 Jina 的 Search API 需要 API key。Jina 为新用户提供免费层，其中包含 **1000 万 tokens** 可用于任意模型。你可以通过在 Jina AI 平台创建账号来获取免费 API key。

- **API Key：** 需要一个 Jina API key。你可以在 [Jina API 控制台](https://jina.ai/api-dashboard) 登录后获取

## 配置步骤 {#configuration-steps}

### 1. 获取 Jina API Key {#1-obtain-a-jina-api-key}

获取 API key 的步骤如下：

1. **访问 Jina API Dashboard：** 前往 [Jina API 控制台](https://jina.ai/api-dashboard)
2. **登录或注册：** 创建新账号，或登录现有账号
3. **获取 API Key：** 登录后，你的专属 API key 会显示在控制台上，将其复制保存

### 2. 配置 Open WebUI {#2-configure-open-webui}

要在 Open WebUI 中启用 Jina 搜索集成，请在 Open WebUI 管理员设置中按以下步骤操作：

1. **以管理员身份登录：** 进入你的 Open WebUI 实例，并使用管理员账号登录
2. **进入 Web Search 设置：** 前往 **Settings > Admin > Web Search**
3. **将搜索引擎设为 Jina：** 在 “Web Search Engine” 下拉框中选择 **Jina**
4. **输入 API Key：** 将你的 Jina API key 粘贴到 **Jina API Key** 输入框中
5. **（可选）填写 Jina API Base URL：** 如果你需要使用某个特定端点（例如欧盟数据处理节点），可在 **Jina API Base URL** 中填写；默认值为 `https://s.jina.ai/`
6. **保存更改：** 向下滚动并点击 **Save**

### 3. 环境变量配置 {#3-environment-variable-configuration}

对于基于 Docker 的部署，你也可以通过环境变量配置 Jina 集成。

为 Open WebUI 实例设置以下环境变量：

- `JINA_API_KEY`：你的 Jina API key
- `JINA_API_BASE_URL`：（可选）自定义 Jina API 端点

**示例 Docker `run` 命令：**

```bash
docker run -d \\
  -p 3000:8080 \\
  -e JINA_API_KEY="your-jina-api-key-here" \\
  --name open-webui \\
  ghcr.io/open-webui/open-webui:main
```

## 限制 {#limits}

- Jina 每次搜索最多返回 10 条结果。对该引擎而言，更高的 **Search Result Count** 会被限制在 10。
- **Domain Filter List** 不会应用到 Jina 的结果上。

## 验证集成 {#verify-the-integration}

配置完成后，你可以在聊天中启用 web search 并提问测试。此时 Open WebUI 会使用 Jina 的 Search API 获取网页结果，并使用所配置的 web loader 读取这些页面。
