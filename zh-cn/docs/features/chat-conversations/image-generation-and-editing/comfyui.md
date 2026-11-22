---
sidebar_position: 3
title: "ComfyUI"
---

:::warning
本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎贡献更多内容，可查看贡献教程。
:::

ComfyUI 是一个强大且模块化的 Stable Diffusion 节点式图形界面，为用户提供了对图像生成流程的高度控制。了解更多信息或下载安装，请访问其 [GitHub 页面](https://github.com/comfyanonymous/ComfyUI)。

若要运行 ComfyUI 并让 Open WebUI 能访问它，你必须在启动时添加 `--listen` 参数，并绑定到 `0.0.0.0`。这样它才能接受来自局域网其他设备的连接。

启动后，ComfyUI 界面通常可通过 `http://<your_comfyui_ip>:8188` 访问。

![ComfyUI 服务器启动命令的截图，其中突出显示了 --listen 参数。](/images/image-generation-and-editing/comfyui-listen-flag.png)

## 将 ComfyUI 连接到 Open WebUI {#connecting-comfyui-to-open-webui}

Open WebUI 通常在 Docker 中运行，因此容器需要通过 `host.docker.internal` 访问宿主机上的 ComfyUI。

1. **检查宿主机监听地址：** 确保 ComfyUI 使用 `--listen` 标志启动，使其绑定到 `0.0.0.0`。
2. **检查防火墙：** 如果宿主机启用了防火墙（如 UFW），请确认已放行 8188 端口（`sudo ufw allow 8188/tcp`）
3. **Linux 原生 Docker：** 如果没有使用 Docker Desktop，请在启动 Open WebUI 容器时将 `--add-host=host.docker.internal:host-gateway` 加入 `docker run` 命令，映射宿主机网关。

一个 ComfyUI 连接可以包含一个图像生成工作流和一个图像编辑工作流。在连接的**功能**设置中，上传生成工作流后可使用**生成**，上传编辑工作流后可使用**编辑**。

## 图像提示词生成 {#image-prompt-generation}

该功能会使用语言模型，根据你的初始输入自动生成更详细、更有创意的提示词，从而提升图像生成效果。它仅适用于旧版函数调用（Legacy function calling）；在默认的 Native 模式下，模型调用工具时会自行编写提示词。

**图像提示词生成**开关位于**设置 > 图像**（管理员区域）的**旧版**区域。

若要自定义用于生成提示词的模板，请前往 **Settings > Interface**（管理员区域），在 **Generation** 部分。

## 创建图像（Image Generation） {#create-image-image-generation}

1. 在 Open WebUI 中前往**设置** > **图像**（管理员区域），开启**图像生成**。
2. 添加连接，将**连接类型**设为 **ComfyUI**。
3. 在 **URL** 中输入运行中的 ComfyUI 实例的地址（例如 `http://host.docker.internal:8188/`），然后点击旁边的验证图标。连接成功时会显示提示。Open WebUI 还会连接该地址的 `/ws` 建立 WebSocket，因此 ComfyUI 前方的任何代理都必须放行 WebSocket 升级。
4. 如果 ComfyUI 实例需要 API 密钥，请在密钥字段输入。
5. **从 ComfyUI 导出工作流。** 点击 ComfyUI 界面左上角的 ComfyUI 标志，选择 **Settings**。找到并开启 **"Dev Mode"**，其说明为 **"Enable dev mode options (API save, etc.)"**。

    ![ComfyUI 设置界面的截图，其中“开发者模式”开关已被高亮显示。](/images/image-generation-and-editing/comfyui-dev-mode.png)

    加载要使用的**图像生成**工作流，点击 ComfyUI 标志，在 **File** 子菜单中点击 **"Export (API)"**，为文件命名并下载。

    ![ComfyUI“文件”菜单中“导出（API）”选项的屏幕截图。](/images/image-generation-and-editing/comfyui-save-api-format.png)

6. **上传工作流。** 在 Open WebUI 的 **Generation Workflow** 区域点击 **Upload**，选择刚下载的 JSON 文件。

7. **映射工作流节点。** 导入工作流后，将工作流中的节点 ID 映射到 Open WebUI 中对应的字段。每个参数有两个字段：

    - **Key（左侧字段）**：workflow 中的输入参数名（例如 `text`、`ckpt_name`、`seed`）
    - **Node Ids（右侧字段）**：包含该输入的 node ID，多个 ID 用逗号分隔

    UI 中会显示六个可配置的图像生成参数：

    | 参数 | 默认键 | 是否必填 | 说明 |
    |-----------|-------------|----------|-------------|
    | Prompt* | `text` | Yes | 正向提示词文本 |
    | Model | `ckpt_name` | No | Checkpoint 模型名 |
    | Width | `width` | No | 输出图像宽度 |
    | Height | `height` | No | 输出图像高度 |
    | Steps | `steps` | No | 采样步数 |
    | Seed | `seed` | No | 用于复现的随机种子 |

    仅提示词节点 ID 为必填项。在 ComfyUI 中点击节点并查看详情，可找到节点 ID。

    Open WebUI 会从 workflow 的 **Save Image**、**Save Image (Advanced)**、**Save Animated WEBP**、**Save Animated PNG** 和 **Preview Image** 节点返回图片。动画图片在聊天中会保持为动画。

    :::info
    可能需要调整 `Key` 以匹配工作流中的节点。例如，视工作流结构而定，默认的 `seed` 键可能需要改成 `noise_seed`。
    :::

    :::tip
    部分工作流（例如使用任一 Flux 模型的工作流）需要为同一项填写多个节点 ID。用逗号分隔，例如 `1` 或 `1, 2`。
    :::

8. 将 **Model IDs** 留空可使用工作流中设定的模型，也可添加模型名称供选择。建议的名称来自上一次验证：来自被映射为 Model 的节点（它的第一个名称中含 `_name` 的输入，例如 `ckpt_name` 或 `unet_name`）；若没有映射 Model 节点，则来自 CheckpointLoaderSimple 的检查点，因此在映射节点后需要重新验证。**高级**下的**图像尺寸**和**步数**是可选默认值。不设置图像尺寸时，ComfyUI 收到的是 512x512。已映射的 Seed 节点每次请求都会得到新的随机种子。
9. 设置**访问控制**并点击**保存**。未授予访问权限时，只有管理员能使用该连接。

![使用 ComfyUI 在聊天中生成图片的截图。](/images/image-generation-and-editing/comfyui-create-image-in-chat.png)

:::info
消息上没有“生成图像”按钮。生成是从聊天本身发起的：在消息输入框的 **+** 菜单中开启 **图像**，然后再请求生成图片。具体需要满足的条件，以及如何用社区提供的 Action 添加此按钮，请参见[使用方法](/features/chat-conversations/image-generation-and-editing/usage)。
:::

## 编辑图像 {#edit-image}

Open WebUI 同样支持通过 ComfyUI 进行图像编辑，从而修改已有图片。

1. 在**设置** > **图像**（管理员区域）中开启**图像编辑**。
2. 在同一连接的 **Edit Workflow** 区域上传为图像编辑设计的工作流，导出方式与生成工作流相同。
3. 映射工作流节点。图像编辑包含五个参数，其默认值与生成参数不同：

    | 参数 | 默认键 | 是否必填 | 说明 |
    |-----------|-------------|----------|-------------|
    | Image* | `image` | Yes | 待编辑的输入图像 |
    | Prompt* | `prompt` | Yes | 编辑提示词文本 |
    | Model | `unet_name` | No | Diffusion 模型名 |
    | Width | `width` | No | 输出图像宽度 |
    | Height | `height` | No | 输出图像高度 |

    若要编辑多张输入图像，请在 Image 行中为每张图像填写一个 LoadImage 节点 ID，并用逗号分隔。每张图像会按顺序送入对应的节点 ID，超出 ID 数量的图像会被丢弃。

    **高级**下的**编辑图像尺寸**用于设置输出尺寸。

![在对话中使用 ComfyUI 编辑图像的截图](/images/image-generation-and-editing/comfyui-edit-image-in-chat.png)

### 深入了解：将 ComfyUI Nodes 映射到 Open WebUI {#deeper-dive-mapping-comfyui-nodes-to-open-webui}

理解 node ID 映射，往往是将 ComfyUI 与 Open WebUI 这类外部服务集成时最容易卡住的一步。通过 API 集成 ComfyUI，本质上就是把 Open WebUI 的通用控制项（如 “Model”、“Width”、“Prompt”）映射到静态 ComfyUI workflow JSON 中的特定 node 输入。

#### 将 Workflow Nodes 映射到 Open WebUI {#mapping-workflow-nodes-to-open-webui}

每个工作流的节点映射都可将通用控件对应到静态 ComfyUI 工作流 JSON 中的具体节点输入。每行有两个字段：

| 字段 | 说明 | 示例 |
|-------|-------------|---------|
| **Key**（左侧） | node 的 `inputs` 块中的输入参数名 | `text`、`ckpt_name`、`seed` |
| **Node Ids**（右侧） | 目标 node ID，可为逗号分隔 | `6` 或 `1, 2, 3` |

#### 在 ComfyUI 中识别 Node ID 和 Input Key {#identifying-node-ids-and-input-keys-in-comfyui}

在配置 Open WebUI 之前，你必须先用文本编辑器直接检查导出的 workflow JSON 文件。Node ID 是 ComfyUI 在 JSON 结构中标识某个 node 的唯一编号；JSON 对象的顶层键就是这些节点 ID。

**识别 Input Key（参数名）**

Key 就是该 node JSON 结构里你要控制的确切字段名（例如 `seed`、`width`、`ckpt_name`）。

1. **查看 JSON**：打开你的 API workflow JSON（如 `workflow_api.json`）
2. **找到 Node ID**：定位到对应 node 的那一段（例如 `"37"`）
3. **识别 Key**：在 `"inputs"` 块中找到你要控制的变量

**示例：CheckpointLoaderSimple Node（ID 37）**

```json
"37": {
  "inputs": {
      "ckpt_name": "qwen_image_fp8_e4m3fn.safetensors"
  },
  "class_type": "CheckpointLoaderSimple",
  "_meta": {
    "title": "Load Checkpoint"
  }
},
```

**示例：KSampler Node（ID 3）**

```json
"3": {
  "inputs": {
      "seed": 42,
      "steps": 20,
      "cfg": 8.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0
  },
  "class_type": "KSampler",
  "_meta": {
    "title": "KSampler"
  }
},
```

#### 按任务类型区分的默认 Key 值 {#default-key-values-by-task-type}

**图像生成：**
- Prompt: `text`
- Model: `ckpt_name`
- Width: `width`
- Height: `height`
- Steps: `steps`
- Seed: `seed`

**图像编辑：**
- Image: `image`
- Prompt: `prompt`
- Model: `unet_name`
- Width: `width`
- Height: `height`

#### 示例：映射 KSampler 的 Seed {#example-mapping-ksampler-seed}

假设要控制 ID 为 `3` 的 KSampler 节点中的 `seed`。在节点映射的 `seed` 行中：

| Key | 节点 ID |
|-----|----------|
| `seed` | `3` |

#### 处理多个 Node ID {#handling-multiple-node-ids}

如果多个 node 需要使用相同值（例如多个 sampler 共享同一个 seed），请填写逗号分隔的多个 ID：

| Key | 节点 ID |
|-----|----------|
| `seed` | `3, 15, 22` |

#### 处理复杂 / 多模态 Nodes（Qwen 示例） {#handling-complexmultimodal-nodes-qwen-example}

对于某些特殊 node，Key 可能不只是简单文本字段。

| 参数 | Key | 节点 ID | 说明 |
|-----------|-----|----------|------|
| **Prompt** | `text` 或 `prompt` | `76` | 取决于 node 类型（CLIPTextEncode 或 TextEncodeQwen） |
| **Model** | `ckpt_name` | `37` | 用于 CheckpointLoaderSimple |
| **Model** | `unet_name` | varies | 用于某些 workflow 中的 UNETLoader |
| **Image Input** | `image` | `78` | 该 key 会把文件名传递给 LoadImage node |

#### 排查不匹配错误 {#troubleshooting-mismatch-errors}

如果 ComfyUI 卡住或抛出校验错误，请结合日志和 JSON 结构排查：

| 错误类型 | 原因与排查 | 解决方案 |
|---------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Value not in list: ckpt_name: 'xyz.safetensors'` | 你映射了正确的 node ID（如 37），但传入值（如 `xyz.safetensors`）对该 node 类型来说不是合法模型名（例如把 VAE 模型错误传给了 checkpoint loader） | 修正 Open WebUI 中图像生成或编辑使用的模型名，确保它与 ComfyUI node 所期望的模型类型一致 |
| `Missing input <key>` | 你的 workflow 需要某个输入（如 `cfg` 或 `sampler_name`），但 Open WebUI 没有发送该值，因为该字段未映射 | 要么在 workflow JSON 中硬编码默认值，要么把对应输入 key 映射到正确的 node ID |

只要精确匹配 Node ID 与具体 Key，Open WebUI 就能在提交 prompt 给 ComfyUI 前，正确覆盖 workflow JSON 中的默认值。

## 示例配置：Qwen 图像生成与编辑 {#example-setup-qwen-image-generation-and-editing}

本节提供一个额外示例，演示如何为 Qwen 模型配置图像生成与编辑。

### Qwen 图像生成 {#qwen-image-generation}

#### 模型下载 {#model-download}

- **扩散模型**: [qwen_image_fp8_e4m3fn.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors)
- **文本编码器**: [qwen_2.5_vl_7b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors)
- **VAE**: [qwen_image_vae.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors)

#### 模型存放位置 {#model-storage-location}

```
ComfyUI/
├── models/
│   ├── diffusion_models/
│   │   └── qwen_image_fp8_e4m3fn.safetensors
│   ├── vae/
│   │   └── qwen_image_vae.safetensors
│   └── text_encoders/
│       └── qwen_2.5_vl_7b_fp8_scaled.safetensors
```

#### Qwen 生成工作流节点映射 {#workflow-node-mapping-for-qwen-generation}

| 参数 | Key | 节点 ID |
|-----------|-----|----------|
| 提示词 | `prompt` | （取决于你的 workflow） |
| 模型 | `ckpt_name` | （checkpoint loader node ID） |

### Qwen 图像编辑 {#qwen-image-editing}

#### 模型下载 {#model-download-1}

- **扩散模型**: [qwen_image_edit_fp8_e4m3fn.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_fp8_e4m3fn.safetensors)
- **文本编码器**: [qwen_2.5_vl_7b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors)
- **VAE**: [qwen_image_vae.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors)

#### 模型存放位置 {#model-storage-location-1}

```
ComfyUI/
├── models/
│   ├── diffusion_models/
│   │   └── qwen_image_edit_fp8_e4m3fn.safetensors
│   ├── vae/
│   │   └── qwen_image_vae.safetensors
│   └── text_encoders/
│       └── qwen_2.5_vl_7b_fp8_scaled.safetensors
```

#### Qwen 编辑工作流节点映射 {#workflow-node-mapping-for-qwen-editing}

| 参数 | Key | 节点 ID |
|-----------|-----|----------|
| 图像 | `image` | （load image node ID） |
| 提示词 | `prompt` | （text encoder node ID） |
| 模型 | `unet_name` | （UNET loader node ID） |

## 示例配置：FLUX.1 图像生成 {#example-setup-flux1-image-generation}

本节提供一个额外示例，说明如何为 FLUX.1 模型配置图像生成。

### FLUX.1 Dev {#flux1-dev}

#### 模型下载 {#model-download-2}

- **扩散模型**: [flux1-dev.safetensors](https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors)
- **文本编码器 1**: [clip_l.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true)
- **文本编码器 2**: [t5xxl_fp16.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors?download=true)（推荐在 VRAM 大于 32GB 时使用）
- **VAE**: [ae.safetensors](https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors?download=true)

#### 模型存放位置 {#model-storage-location-2}

```
ComfyUI/
├── models/
│   ├── diffusion_models/
│   │   └── flux1-dev.safetensors
│   ├── vae/
│   │   └── ae.safetensors
│   └── text_encoders/
│       ├── clip_l.safetensors
│       └── t5xxl_fp16.safetensors
```

### FLUX.1 Schnell {#flux1-schnell}

#### 模型下载 {#model-download-3}

- **扩散模型**: [flux1-schnell.safetensors](https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors)
- **文本编码器 1**: [clip_l.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true)
- **文本编码器 2**: [t5xxl_fp8_e4m3fn.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true)（推荐在 VRAM 大于 32GB 时使用）
- **VAE**: [ae.safetensors](https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors?download=true)

#### 模型存放位置 {#model-storage-location-3}

```
ComfyUI/
├── models/
│   ├── diffusion_models/
│   │   └── flux1-schnell.safetensors
│   ├── vae/
│   │   └── ae.safetensors
│   └── text_encoders/
│       ├── clip_l.safetensors
│       └── t5xxl_fp8_e4m3fn.safetensors
```

## 配置 SwarmUI {#configuring-with-swarmui}

SwarmUI 使用 ComfyUI 作为后端。要让 Open WebUI 连接 SwarmUI，请在连接的 **URL** 末尾添加 `ComfyBackendDirect`，并在 SwarmUI 中启用局域网访问。完成这些设置后，配置 SwarmUI 与 Open WebUI 配合使用的步骤与上述 ComfyUI 图像生成步骤相同。
![安装 SwarmUI 并启用局域网访问](https://github.com/user-attachments/assets/a6567e13-1ced-4743-8d8e-be526207f9f6)

### SwarmUI API URL {#swarmui-api-url}

在 **URL** 中填入的地址形如 `http://<your_swarmui_address>:7801/ComfyBackendDirect`。
