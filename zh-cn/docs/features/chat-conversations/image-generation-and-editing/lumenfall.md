---
sidebar_position: 7
title: "Lumenfall"
---

:::warning
本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。想参与贡献？请查看贡献教程。
:::

Open WebUI 还支持通过 [Lumenfall](https://lumenfall.ai) 生成图像。这个 AI 媒体网关通过统一的 OpenAI 兼容 API 提供多个供应商的主流图像模型，其中包括免费模型。

### 初始设置 {#initial-setup}

1. 在 [lumenfall.ai](https://lumenfall.ai) 注册一个免费账号
2. 在你的 [仪表盘](https://lumenfall.ai/app/api_keys) 中生成 API 密钥

### 配置图像生成 {#configuring-image-generation}

1. 在 Open WebUI 中前往**设置** > **图像**（管理员区域），添加连接。
2. 将**连接类型**设为**兼容 OpenAI**（Lumenfall 使用与 OpenAI 相同的语法）。
3. 将 **URL** 设为 `https://api.lumenfall.ai/openai/v1`，并输入 Lumenfall API 密钥。
4. 在 **Model IDs** 中添加要使用的模型，例如 `gemini-3.1-flash-image`、`gpt-image-2` 或 `flux.2-max`。可访问 [lumenfall.ai/models](https://lumenfall.ai/models) 查看所有模型。
5. 可选：打开**高级**并设置**图像尺寸**，例如 `1024x1024`。支持的尺寸取决于模型。
6. 设置**访问控制**并点击**保存**。未授予访问权限时，只有管理员能使用该连接。

### 配置图像编辑 {#configuring-image-editing}

Lumenfall 也支持通过同一连接编辑图像。在 **Model IDs** 中添加支持编辑的模型，例如 `gpt-image-2`。

更多说明请参阅 [Lumenfall 文档](https://docs.lumenfall.ai/integrations/openwebui)。
