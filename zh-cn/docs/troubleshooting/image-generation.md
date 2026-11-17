## 图像生成故障排查 {#image-generation-troubleshooting}

### 常见问题 {#general-issues}

- **图像没有生成**（请求生成图像却没有得到图像，或聊天中出现报错）：
    - 检查**设置 > 图像**（管理员区域）中的**图像**设置，确认"图像生成"已切换为**开启**。
    - 确认消息输入框的 **+** 菜单中 **图像** 开关已打开。在任何函数调用模式下，不开启它就不会发生任何与图像相关的行为。
    - 确认模型在**工作区 > 模型 > 编辑**中具备**图像生成**能力，并且你的角色拥有**图像生成**功能权限。
    - 核对**API 密钥**和**Base URL**（适用于 OpenAI、ComfyUI、Automatic1111）是否正确。
    - 确认所选模型在后端服务中可用并已加载（例如查看 ComfyUI 或 Automatic1111 控制台是否有活动日志）。
    - **Azure OpenAI**：如果你看到 `[ERROR: azure-openai error: Unknown parameter: 'response_format'.]`，请确认使用的是 `2025-04-01-preview` 或更高版本的 API 版本。

- **图像设置无法保存**（保存**设置 > 图像**（管理员区域）时出现诸如 `OpenAI API Key is required.` 的错误）：
    - 只有在相应功能开启时才需要填写密钥和 URL。请填写该字段，或关闭该功能，然后重新保存。
    - **附加参数**中的无效 JSON 会以 `Invalid JSON format for Parameters` 拒绝。请修正或清空它，然后重新保存。

- **引擎设置缺失**（**设置 > 图像**（管理员区域）只显示**图像生成**开关）：
    - **创建图像**和**编辑图像**两个分区（包含引擎及其密钥、**图像提示词生成**和**图像编辑**）只在**图像生成**开启时显示。它们已保存的值在隐藏期间会被保留。

- **图片位置显示"图像不可用"**（原本图片的位置显示成带照片图标的小虚线框）：
    - 浏览器无法从消息中记录的地址加载该图片。这涵盖聊天中的任何图片，无论是上传的还是生成的。
    - 常见原因是其背后的文件已经丢失——通过**设置 > 数据控制 > 管理文件**删除，或随数据目录一起被清除。被删除的文件无法恢复，因此占位符会一直留在那条消息上。
    - 占位符不可点击，因此无法显示的图片不会打开全屏预览。如果该消息后来指向了另一个图片地址，图片会重新加载。
    - 如果你运行了多个副本且占位符时有时无，请检查 `/app/backend/data` 是否确实在它们之间共享。参见[扩展与高可用 → 上传的文件或 RAG 知识不可访问](/troubleshooting/multi-replica#5-uploaded-files-or-rag-knowledge-inaccessible)。

### ComfyUI 问题 {#comfyui-issues}

- **Workflow 不兼容 / JSON 错误**（上传 workflow 后出现 `Invalid workflow` 或 JSON 解析错误）：
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
    - 检查 Open WebUI 设置中默认的"图像编辑"workflow，了解所需的节点结构以确保兼容。

- **当 ComfyUI 位于私有/内网地址时生成或编辑失败**（例如 `10.x`、`192.168.x`、`172.16–31.x` 或 `localhost`），且往往只在 workflow 运行之后才出现：
    - Open WebUI 对外发请求应用 SSRF 防护，只有当图片 URL 与管理员配置的 `COMFYUI_BASE_URL` 同源（协议 + 主机 + 端口严格匹配）时才会信任它。
    - 确保 `COMFYUI_BASE_URL`（以及图像编辑用的 `IMAGES_EDIT_COMFYUI_BASE_URL`，它默认为空，且是编辑路径唯一信任的源）被设为 ComfyUI 提供图片的**准确**源（协议、主机和端口都要匹配）。如果 ComfyUI 返回的图片 URL 与 `COMFYUI_BASE_URL` 的主机/端口不同，这些请求同样会经过 SSRF 校验，并可能被拦截。在较旧的版本上，请升级而不是关闭 SSRF 防护。

### Automatic1111 问题 {#automatic1111-issues}

- **连接被拒绝 / "Api Not Found"**（Automatic1111 正在运行，但 Open WebUI 报告连接错误）：
    - 确认你运行 Automatic1111 时在命令行参数中启用了 `--api` 标志。

- **Docker 连通性**（Open WebUI 无法访问 `localhost` 上的 Automatic1111）：
    - 如果 Open WebUI 运行在 Docker 中而 Automatic1111 在你的宿主机上：
        - 将 Base URL 设为 `http://host.docker.internal:7860`。
        - 确认 `host.docker.internal` 可以解析（在 Docker run 命令中加入 `--add-host=host.docker.internal:host-gateway` 即可）。

### 环境变量与配置 {#environment-variables--configuration}

如需高级配置，可以设置以下环境变量。

#### 通用图像生成 {#general-image-generation}
- `ENABLE_IMAGE_GENERATION`：设为 `true` 以启用图像生成。
- `IMAGE_GENERATION_ENGINE`：使用的引擎（例如 `openai`、`comfyui`、`automatic1111`、`gemini`）。
- `IMAGE_GENERATION_MODEL`：用于生成的模型 ID。
- `IMAGE_SIZE`：默认图像尺寸（例如 `512x512`）。

#### 各引擎专属设置 {#engine-specifics}

**OpenAI / 兼容接口**
- `IMAGES_OPENAI_API_BASE_URL`：OpenAI 兼容图像生成 API 的 Base URL。
- `IMAGES_OPENAI_API_KEY`：图像生成服务的 API 密钥。

**ComfyUI**
- `COMFYUI_BASE_URL`：你的 ComfyUI 实例的 Base URL。
- `COMFYUI_API_KEY`：API 密钥（如果启用了认证）。
- `COMFYUI_WORKFLOW`：自定义 workflow JSON（必须是 API 格式）。

**Automatic1111**
- `AUTOMATIC1111_BASE_URL`：你的 Automatic1111 实例的 Base URL。
- `AUTOMATIC1111_API_AUTH`：认证凭据（username:password）。

**Gemini**
- `IMAGES_GEMINI_API_KEY`：Gemini 的 API 密钥。
- [查看 Gemini 配置指南](/features/chat-conversations/image-generation-and-editing/gemini)

:::tip
有关完整的环境变量列表和详细配置选项，请参阅[环境变量配置指南](/reference/env-configuration)。
:::
