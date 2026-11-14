---
sidebar_position: 4
title: "Mistral OCR"
---

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎贡献更多内容，可查看 contributing 教程。

:::

## Mistral OCR {#mistral-ocr}

本文提供一个逐步指南，说明如何将 Mistral OCR 集成到 Open WebUI 中。Mistral OCR 是一个光学字符识别库，专门用于从多种基于图像的文件格式中提取文本——包括扫描版 PDF、图片和手写文档——并转换为 JSON 或纯文本等结构化数据。它支持多语言文本识别、版面分析与手写内容理解，能够以强大且可定制的方式简化 AI 文档搜索、总结与数据提取流程。

## 前提条件 {#prerequisites}

- Open WebUI 实例
- Mistral AI 账号

# 集成步骤 {#integration-steps}

### 第 1 步：注册或登录 Mistral AI Console {#step-1-sign-up-or-login-to-mistral-ai-console}

- 前往 `https://console.mistral.ai`
- 按页面提示完成流程
- 授权成功后，你应该能进入控制台首页

### 第 2 步：生成 API 密钥 {#step-2-generate-an-api-key}

- 前往 `API 密钥` 或 `https://console.mistral.ai/api-keys`
- 创建一个新的密钥，并务必复制保存

### 第 3 步：配置 Open WebUI 使用 Mistral OCR {#step-3-configure-open-webui-to-use-mistral-ocr}

- 登录你的 Open WebUI 实例
- 进入 `管理面板`
- 点击 `设置`
- 打开 `文档` 标签
- 将 **Content Extraction Engine** 设置为 **Mistral OCR**
- 将密钥粘贴到 **API Key**
- 保持 **API Base URL**（`MISTRAL_OCR_API_BASE_URL`，默认 `https://api.mistral.ai/v1`）不变，除非你要通过代理或区域端点访问
- 保存管理面板设置

### 可选：以 Base64 发送 PDF {#optional-send-pdfs-as-base64}

默认情况下，Open WebUI 会先把 PDF 上传到 Mistral 的文件存储，然后对其运行 OCR。在 **设置 → 管理 → 文档** 中开启 **Use Base64**（或设置 [`MISTRAL_OCR_USE_BASE64=true`](/reference/env-configuration#mistral_ocr_use_base64)）后，PDF 会改为以 **base64 data URL** 的形式**内联在单个请求中**发送，从而跳过分步上传。这在代理或隔离网络环境中很有用，也能在上传步骤失败时派上用场；代价是单个请求会更大。

### 可选：选择 OCR 模型 {#optional-choose-the-ocr-model}

**设置 → 管理 → 文档** 中的 **Parameters** 字段（或 [`MISTRAL_OCR_PARAMS`](/reference/env-configuration#mistral_ocr_params)）接受一个 JSON 对象，会被合并进每一次 OCR 请求。例如，`{"model": "mistral-ocr-2512"}` 会把默认的 `mistral-ocr-latest` 模型替换掉。

### 会发送什么，以及失败时会发生什么 {#what-is-sent-and-what-happens-on-failure}

Open WebUI 只把 `.pdf` 上传发送给 Mistral OCR。其他所有文件类型（包括图片）都走内置的加载器。OCR 调用失败并不会导致上传失败：文件会带着一个内容为 `Error during processing: ...` 的分块完成索引，因此当某个文档看起来已经处理过、却没有返回有用内容时，请检查该文件的提取内容。

## 验证 Mistral OCR {#verifying-mistral-ocr}

若要通过脚本验证 Mistral OCR 是否工作正常，请参阅 `https://docs.mistral.ai/capabilities/document_ai/basic_ocr/`

### 结论 {#conclusion}

将 Mistral OCR 集成到 Open WebUI，是增强文档处理与内容提取能力的一种简单而有效的方法。按照本指南完成配置后，你就可以把 Mistral OCR 设为默认提取引擎，并利用其先进的文本识别能力。配置完成后，Mistral OCR 将为 Open WebUI 提供强大的多语言文档解析能力，支持多种格式，并显著增强 AI 驱动的文档分析能力。