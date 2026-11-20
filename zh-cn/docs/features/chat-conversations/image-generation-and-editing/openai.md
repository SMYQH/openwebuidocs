---
sidebar_position: 4
title: "OpenAI"
---

:::warning
本教程由社区贡献，不在 Open WebUI 团队的支持范围内。它仅演示如何按实际需求自定义 Open WebUI。欢迎贡献，详情请参阅贡献教程。
:::

Open WebUI 支持通过 **OpenAI API** 生成和编辑图像，也支持 Azure OpenAI、LiteLLM 等提供兼容 OpenAI 的图像 API 的服务器。它们都使用**兼容 OpenAI** 的连接类型。

### 初始设置 {#initial-setup}
1. 从 OpenAI 获取 [API 密钥](https://platform.openai.com/api-keys)。

### 配置 Open WebUI {#configuring-open-webui}

1. 在 Open WebUI 中前往**设置** > **图像**（管理员区域），添加连接。
2. 将**连接类型**设为**兼容 OpenAI**，将 **URL** 设为 `https://api.openai.com/v1`，并输入 API 密钥。
3. 将 **Model IDs** 留空可使用 `gpt-image-2`，也可添加要提供的模型，例如 `gpt-image-1.5`。
4. 可选：打开**高级**并设置**图像尺寸**。GPT-Image 模型接受 `auto`、`1024x1024`、`1536x1024` 或 `1024x1536`。
5. 设置**访问控制**并点击**保存**。未授予访问权限时，只有管理员能使用该连接。

### Azure OpenAI {#azure-openai}

Azure OpenAI 使用相同的连接类型。添加连接后，配置以下项目：

1. 将 **URL** 设为 `https://<instance-id>.cognitiveservices.azure.com/openai/deployments/<model>/`。从 Azure AI Foundry 设置中获取实例和模型名称。
2. 填入 Azure AI Foundry 中的 API 密钥。
3. 将 **Model IDs** 设为已部署的模型名称。
4. 在**高级**下，将 **API 版本**设为 Azure AI Foundry 中显示的值。

:::tip Azure GPT-Image-1.5 配置
在 Azure OpenAI 中使用 **gpt-image-1.5** 时，采用以下设置：
- **Model IDs**：`gpt-image-1.5`
- **Image Size**：`1024x1024`
- **API Version**：`2025-04-01-preview`
- **URL**：`https://<your-resource-name>.openai.azure.com/openai/deployments/<your-deployment-name>/`
:::

:::tip
也可以从部署页面复制目标 URI，并删除模型名称之后的内容。例如，目标 URI `https://test.openai.azure.com/openai/deployments/gpt-image-1/images/generations?api-version=2025-04-01-preview` 对应的 URL 为 `https://test.openai.azure.com/openai/deployments/gpt-image-1/`。
:::

### 使用 OpenAI 端点的 LiteLLM 代理 {#litellm-proxy-with-openai-endpoints}

1. 添加**兼容 OpenAI** 的连接。
2. 将 **URL** 设为 `https://<your-litellm-url>:<port>/v1`，并输入 LiteLLM API 密钥。
3. 将 **Model IDs** 留空，连接会自动列出 LiteLLM 服务器的图像模型。仅在只提供部分模型时添加模型 ID。
4. 将 **API 版本**留空。

:::tip
可以在**设置** > **连接**（管理员区域）的 OpenAI API 连接中找到 LiteLLM 连接信息。
:::
