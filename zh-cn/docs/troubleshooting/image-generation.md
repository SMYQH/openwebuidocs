---
sidebar_position: 100
title: "图像生成"
---

## 图像生成故障排查 {#image-generation-troubleshooting}

### 常见问题 {#general-issues}

- **图像没有生成**（请求生成图像却没有得到图像，或聊天中出现报错）：
    - 检查 **设置** > **图像**（管理员区域）中的**图像**设置，确认“图像生成”已切换为**开启**。
    - 确认消息输入框的 **+** 菜单中 **图像** 开关已打开。在任何函数调用模式下，不开启它就不会发生任何与图像相关的行为。
    - 确认模型在 **工作区** > **模型** > **编辑**中具备**图像生成**能力，并且你的角色拥有**图像生成**功能权限。
    - 在 **Settings** > **Images**（管理员区域）打开连接，检查其 **URL** 和密钥，然后点击 URL 旁的验证图标。
    - 确认连接已启用，开启了 **Generate** 能力，并且 **Access Control** 包含该用户。未列入连接访问名单的非管理员用户看不到其模型。
    - 确认所选模型在后端服务中可用并已加载（例如查看 ComfyUI 或 Automatic1111 控制台是否有活动日志）。
    - **Azure OpenAI**：如果你看到 `[ERROR: azure-openai error: Unknown parameter: 'response_format'.]`，请确认使用的是 `2025-04-01-preview` 或更高版本的 API 版本。

- **无法保存连接**（保存时显示 `URL is required` 等错误）：
    - 填写 **URL**，然后重新保存。
    - 如果 **Additional Parameters** 或 **Headers** 中的 JSON 无效，系统会显示 `Invalid JSON format for Parameters` 或 `Headers must be a valid JSON object` 并拒绝保存。修正或清空相应字段后，重新保存。

- **连接未显示**（**Settings** > **Images**（管理员区域）只显示 **Image Generation** 和 **Image Edit** 开关）：
    - **Image Generation** 或 **Image Edit** 开启时，会显示 **Manage Image Connections** 和 **Default Models**。

- **只提供一个图像模型，或使用了错误的模型**：
    - **Model IDs** 留空时，连接会提供 OpenAI 兼容服务器明确标记为图像模型的所有模型（LiteLLM 会添加此标记）。其他后端只提供一个默认模型：OpenAI 的 `gpt-image-2`、AUTOMATIC1111 中已加载的检查点、ComfyUI 工作流指定的模型，或 Gemini 的 `imagen-3.0-generate-002`。请添加你希望提供的模型 ID。
    - **Default Models** 设置聊天未指定模型时使用的默认模型。用户可从 **+** 菜单的 **Image** 项选择模型。

- **图片位置显示"图像不可用"**（原本图片的位置显示成带照片图标的小虚线框）：
    - 浏览器无法从消息中记录的地址加载该图片。这涵盖聊天中的任何图片，无论是上传的还是生成的。
    - 常见原因是原文件已被删除，例如通过 **设置** > **数据控制** > **管理文件**删除，或随数据目录一起被清除。被删除的文件无法恢复，因此占位符会一直留在那条消息上。
    - 占位符不可点击，因此无法显示的图片不会打开全屏预览。如果该消息后来指向了另一个图片地址，图片会重新加载。
    - 如果你运行了多个副本且占位符时有时无，请检查 `/app/backend/data` 是否确实在它们之间共享。参见[扩展与高可用 → 上传的文件或 RAG 知识不可访问](/troubleshooting/multi-replica#5-uploaded-files-or-rag-knowledge-inaccessible)。

### OpenAI 兼容图像编辑 {#openai-compatible-image-edits}

- **编辑模型只收到一张输入图像。** 在 Open WebUI v0.13.4 中，服务器向连接的 `/images/edits` 端点发送图像列表时，使用 multipart 表单数据，每个文件对应一个 `image[]` 部分。以字符串形式提供的单张图像使用 `image` 字段。
- 测试自定义提供商或代理时，请使用两张小测试图像，并在端点检查字段名和部分数量。配置 multipart 解析器，使其收集所有 `image[]` 值。手动测试时反复发送 `image` 字段，使用的是另一种请求结构。

### ComfyUI 问题 {#comfyui-issues}

- **工作流不兼容／JSON 错误**（上传工作流后显示 `Invalid JSON format for ComfyUI Workflow.`）：
    - **必须使用 API 格式**：Open WebUI 要求 workflow 采用 **API 格式**。
    - 在 ComfyUI 中：
        1. 点击"设置"（齿轮图标）。
        2. 启用"Enable Dev mode Options"。
        3. 在菜单中点击"Save (API Format)"。
    - **不要**使用标准的"Save"按钮或标准 JSON 导出。

- **生成或编辑时报错**（workflow 在 ComfyUI 内部失败）：
    - Open WebUI 服务端日志会以 `ComfyUI <node type> failed: <message>` 的形式指出失败的节点及其错误。请在 workflow 中修复该节点。

- **图像编辑 / 图像变体失败**（从文本生成正常，但编辑或图生图悄无声息地失败）：
    - 如果你使用图像编辑或 Image+Image 生成，你的自定义 workflow **必须**包含配置为接受输入图像的节点（通常是经过有效替换或链接的 `LoadImage` 节点）。
    - 确认已为连接上传 **Edit Workflow**，其中映射了 **Image** 和 **Prompt** 节点，并在 **Capabilities** 下开启了 **Edit**。

- **当 ComfyUI 位于私有/内网地址时生成或编辑失败**（例如 `10.x`、`192.168.x`、`172.16–31.x` 或 `localhost`），且往往只在 workflow 运行之后才出现：
    - Open WebUI 会对出站请求应用 SSRF 防护，只信任与连接的 **URL** 同源的图像 URL，即协议、主机和端口必须完全匹配。
    - 将连接的 **URL** 设为 ComfyUI 提供图像的**确切**来源。如果 ComfyUI 返回的图像 URL 使用不同主机或端口，这些请求仍会经过 SSRF 校验，可能会被阻止。

### Automatic1111 问题 {#automatic1111-issues}

- **连接被拒绝 / "Api Not Found"**（Automatic1111 正在运行，但 Open WebUI 报告连接错误）：
    - 确认你运行 Automatic1111 时在命令行参数中启用了 `--api` 标志。

- **Docker 连通性**（Open WebUI 无法访问 `localhost` 上的 Automatic1111）：
    - 如果 Open WebUI 运行在 Docker 中而 Automatic1111 在你的宿主机上：
        - 将连接的 **URL** 设为 `http://host.docker.internal:7860`。
        - 确认 `host.docker.internal` 可以解析（在 Docker run 命令中加入 `--add-host=host.docker.internal:host-gateway` 即可）。

### 环境变量与配置 {#environment-variables--configuration}

在 **Settings** > **Images**（管理员区域）管理图像连接。

#### 通用图像生成 {#general-image-generation}

- `ENABLE_IMAGE_GENERATION`：设为 `true` 以启用图像生成。
- `ENABLE_IMAGE_EDIT`：设为 `true` 以启用图像编辑。这两个变量均见[环境配置指南](/reference/env-configuration)。

#### 各引擎专属设置 {#engine-specifics}

各引擎分别对应一种连接类型，参见[图像生成和编辑](/features/chat-conversations/image-generation-and-editing#set-up-a-connection)。
