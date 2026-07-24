---
sidebar_position: 100
title: "图像生成"
---

## 🎨 图像生成故障排查

### 常见问题

#### 图像没有生成

1. 检查 **管理面板** > **设置** > **图像** 中的 **图像生成** 设置，确认它已切换为 **开启**。
2. 确认你的 **API 密钥** 和 **Base URL**（适用于 OpenAI、ComfyUI、Automatic1111）填写正确。
3. 确认所选模型已在后端服务中可用并完成加载（例如查看 ComfyUI 或 Automatic1111 控制台是否有活动日志）。
4. **Azure OpenAI**：如果你看到 `[ERROR: azure-openai error: Unknown parameter: 'response_format'.]`，请确认使用的是 `2025-04-01-preview` 或更高版本的 API 版本。

### ComfyUI 问题

#### 工作流格式问题

1. **Workflow 不兼容 / JSON 错误**（上传 workflow 后出现 `Invalid workflow` 或 JSON 解析错误）：Open WebUI 要求 workflow 使用 **API 格式**。
2. 在 ComfyUI 中点击 “设置”（齿轮图标），启用 “启用开发者模式选项”，然后在菜单中点击 “保存（API 格式）”。
3. **不要** 使用普通的 “保存” 按钮或标准 JSON 导出。

#### 图像编辑问题

1. 如果你正在使用图像编辑或 image-to-image 生成，自定义 workflow **必须** 包含可接收输入图像的节点（通常是正确替换或连接的 `LoadImage` 节点）。
2. 请参考 Open WebUI 设置中的默认 “图像编辑” workflow，确认所需节点结构兼容。

- **当 ComfyUI 处于内网/私有地址时，生成或编辑失败**（例如 `10.x`、`192.168.x`、`172.16–31.x` 或 `localhost`，且通常仅在工作流运行之后出现）：
    - Open WebUI 对出站请求启用了 SSRF 保护，历史上会阻止从内网中的 ComfyUI 实例取回渲染后的图像。
    - **v0.9.6 已修复**：当图像 URL 与管理员配置的 `COMFYUI_BASE_URL` 同源时（严格的 scheme + host + port 匹配，不是字符串前缀），会被信任；因此内网 ComfyUI 在不削弱全局 SSRF 保护的前提下也能正常工作。
    - 请确保 `COMFYUI_BASE_URL` 指向 ComfyUI 提供图像的**完全一致**的源（scheme、host、port 全部匹配）。如果 ComfyUI 返回的图像 URL 使用的 host/port 与 `COMFYUI_BASE_URL` 不同，那些请求仍会经过 SSRF 校验并可能被拒绝。对于旧版本，请升级到 v0.9.6 或更高，而不是关闭 SSRF 保护。

### Automatic1111 问题

#### 连接问题

1. **连接被拒绝 / “Api Not Found”**（Automatic1111 正在运行，但 Open WebUI 报连接错误）：请确认你在启动 Automatic1111 时，命令行参数中启用了 `--api`。

#### Docker 连接问题

1. **Docker 连接问题**（Open WebUI 无法通过 `localhost` 访问 Automatic1111）：如果 Open WebUI 运行在 Docker 中，而 Automatic1111 运行在宿主机，请把 Base URL 设为 `http://host.docker.internal:7860`，并确保 `host.docker.internal` 可解析（在 `docker run` 中通过 `--add-host=host.docker.internal:host-gateway` 添加）。

### 环境变量与配置

如需高级配置，你可以设置以下环境变量。

#### 通用图像生成

- `ENABLE_IMAGE_GENERATION`：设为 `true` 以启用图像生成。
- `IMAGE_GENERATION_ENGINE`：要使用的引擎（例如 `openai`、`comfyui`、`automatic1111`、`gemini`）。
- `IMAGE_GENERATION_MODEL`：用于生成的模型 ID。
- `IMAGE_SIZE`：默认图像尺寸（例如 `512x512`）。

#### 各引擎专属设置

#### OpenAI / 兼容接口

- `IMAGES_OPENAI_API_BASE_URL`：OpenAI 兼容图像生成 API 的 Base URL。
- `IMAGES_OPENAI_API_KEY`：图像生成服务的 API 密钥。

#### ComfyUI

- `COMFYUI_BASE_URL`：你的 ComfyUI 实例 Base URL。
- `COMFYUI_API_KEY`：API 密钥（如果启用了认证）。
- `COMFYUI_WORKFLOW`：自定义 workflow JSON（必须是 API 格式）。

#### Automatic1111

- `AUTOMATIC1111_BASE_URL`：你的 Automatic1111 实例 Base URL。
- `AUTOMATIC1111_API_AUTH`：认证凭据（username:password）。

#### Gemini

- `IMAGES_GEMINI_API_KEY`：Gemini 的 API 密钥。
- [查看 Gemini 配置指南](/features/chat-conversations/image-generation-and-editing/gemini)

:::tip
完整的环境变量列表和更详细的配置选项，请参阅 [环境变量配置指南](/reference/env-configuration)。
:::
