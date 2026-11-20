---
sidebar_position: 6
title: "Image Router"
---

:::warning
本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。想参与贡献？请查看贡献教程。
:::

Open WebUI 也支持通过 **Image Router API** 进行图像生成。Image Router 是一个 [开源](https://github.com/DaWe35/image-router) 图像生成代理，可将大多数流行模型统一封装为单一 API。

### 初始设置 {#initial-setup}
1. 从 Image Router 获取 [API 密钥](https://imagerouter.io/api-keys)。

### 配置 Open WebUI {#configuring-open-webui}

1. 在 Open WebUI 中前往**设置** > **图像**（管理员区域），添加连接。
2. 将**连接类型**设为**兼容 OpenAI**（Image Router 使用与 OpenAI 相同的语法）。
3. 将 **URL** 设为 `https://api.imagerouter.io/v1/openai`，并输入 Image Router API 密钥。
4. 在 **Model IDs** 中输入要使用的模型名称以添加模型。详情见[所有模型](https://imagerouter.io/models)。
5. 设置**访问控制**并点击**保存**。未授予访问权限时，只有管理员能使用该连接。
