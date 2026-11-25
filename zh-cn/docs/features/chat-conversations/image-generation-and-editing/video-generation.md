---
sidebar_position: 8
title: "生成视频"
description: "启用视频生成，连接 OpenAI、LiteLLM、OpenRouter 或 ComfyUI 等视频提供商，让用户在聊天中通过提示词创建视频。"
---

无需离开聊天，即可用文本提示词或初始图像创建短视频。生成的视频可在聊天中播放。视频模型生成每段视频需数分钟，因此普通用户必须获得管理员授权才能使用视频生成。

## 设置视频生成（管理员） {#set-up-video-generation-admin}

1. 打开**设置** > **图像与视频**（管理员区域），滚动到**视频**，开启**视频生成**。
2. 点击**管理视频连接**下的 **+** 按钮，填写连接信息并保存。
3. 可选：选择**默认视频模型**。聊天和模型都未选定视频模型时，会使用该默认值。
4. 授予用户访问权限。在**用户** > **群组**（或默认权限）中，开启**功能**下的**视频生成**权限。此权限默认关闭，参见[权限](/features/authentication-access/rbac/permissions)。管理员始终拥有此权限。
5. 对于每个需要创建视频的模型，打开**工作区** > **模型** > **编辑**，开启**功能**下的**视频生成**，并保持**内置工具**下的**视频生成**类别开启。参见[模型](/features/workspace/models)。

### 视频连接 {#video-connections}

每个连接对应一个提供视频 API 的提供商。支持三种类型：

- **兼容 OpenAI** 的服务器，例如 OpenAI 或 LiteLLM。
- **OpenRouter**，提供 Veo、Kling、Seedance 等视频模型。Open WebUI 会根据 `openrouter.ai` URL 自动识别此提供商，否则需在**高级**下将**提供商**设为 **OpenRouter**。
- **ComfyUI**，在 ComfyUI 服务器上运行你自己的视频工作流。参见 [ComfyUI 视频连接](#comfyui-video-connections)。

| 字段 | 用途 |
| :--- | :--- |
| **URL** 和**身份验证** | 提供商的基础 URL 及验证方式（API 密钥、转发会话或 OAuth、Entra ID 或无），也可添加额外的**请求头**。使用**验证连接**进行测试。 |
| **模型 ID** | 用户可选择的视频模型。留空可实时列出提供商的视频模型。对于 ComfyUI，留空表示使用工作流加载的模型。 |
| **视频尺寸**和**视频时长** | 每次请求发送的默认值，例如 `1280x720` 和 `8` 秒。 |
| **API 版本** | 发给提供商的 API 版本查询参数。OpenRouter 不使用此字段。 |
| **额外参数** | 每次请求时原样传给提供商的额外 JSON。 |
| **访问控制** | 哪些用户和群组可以使用该连接的模型。 |

Open WebUI 最多等待 15 分钟，每 5 秒检查一次进度。可分别通过 [`VIDEO_GENERATION_TIMEOUT`](/reference/env-configuration#video_generation_timeout) 和 [`VIDEO_GENERATION_POLL_INTERVAL`](/reference/env-configuration#video_generation_poll_interval) 调整。

### ComfyUI 视频连接 {#comfyui-video-connections}

将**连接类型**设为 **ComfyUI**，即可使用自己的工作流生成视频，例如 Wan、LTX-Video 或 HunyuanVideo。按照 [ComfyUI](/features/chat-conversations/image-generation-and-editing/comfyui) 中的说明搭建 ComfyUI 服务器，并将其地址填入 **URL**。

1. 在 ComfyUI 中以 **API 格式**导出视频工作流。工作流必须能保存视频，例如使用 **Save Video**、**SaveWEBM** 或 **Video Combine** 节点。
2. 在连接的**视频工作流**下使用**上传**，或选择**编辑**并粘贴。
3. 映射工作流的节点。每行填入输入**键**及其所在的**节点 ID**，参见[将工作流节点映射到 Open WebUI](/features/chat-conversations/image-generation-and-editing/comfyui#mapping-workflow-nodes-to-open-webui)。只有**提示词**是必填项。
4. 保存连接。

每个请求都会填充已映射的节点。未映射的节点会保留工作流中保存的值。

| 节点 | 默认键 | 接收内容 |
| :--- | :--- | :--- |
| **提示词** | `text` | 聊天中的提示词。 |
| **图像** | `image` | 聊天中的附加图像，用作第一帧。 |
| **宽度**和**高度** | `width`、`height` | 视频尺寸。 |
| **长度** | `length` | 设置**视频时长**时的视频帧数。 |
| **帧率** | `fps` | 如果连接配置了**帧率**，则使用该值。 |

长度指帧数，等于**视频时长**的秒数乘以帧率。帧率优先使用连接所设的**帧率**，否则使用工作流已映射的**帧率**节点的值，两者都没有时使用 24。**模型 ID** 留空会使用工作流已加载的模型。要从 ComfyUI 服务器上的模型中选择，请点击**验证连接**，在**模型 ID** 中添加模型，并映射**模型**节点。

## 在聊天中创建视频 {#create-a-video-in-chat}

1. 在消息输入框的 **+** 菜单中开启**视频**。如果连接提供多个视频模型，也在此选择。
2. 描述视频并发送。要使用图像作为第一帧，请先附加该图像。
3. 提供商生成完成后，视频会出现在回复中。

视频通过内置工具创建，聊天模型需要**原生**[函数调用](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)。保持选中平常的聊天模型，和[生成图像](/features/chat-conversations/image-generation-and-editing/usage)时一样。

如果 **+** 菜单中没有**视频**，请确认**设置** > **图像与视频**下的**视频**中已开启视频生成、你的角色拥有**视频生成**权限，且模型已开启**视频生成**功能。
