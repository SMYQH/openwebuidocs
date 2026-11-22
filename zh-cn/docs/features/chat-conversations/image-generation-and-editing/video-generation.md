---
sidebar_position: 8
title: "生成视频"
description: "开启视频生成并连接 OpenAI、LiteLLM 或 OpenRouter 等视频提供商，让用户在聊天中通过提示词创建视频。"
---

无需离开聊天，即可用文本提示词或初始图像创建短视频。生成的视频可在聊天中播放。视频模型生成每段视频需数分钟，因此普通用户必须获得管理员授权才能使用视频生成。

## 设置视频生成（管理员） {#set-up-video-generation-admin}

1. 打开**设置** > **图像与视频**（管理员区域），滚动到**视频**，开启**视频生成**。
2. 点击**管理视频连接**下的 **+** 按钮，填写连接信息并保存。
3. 可选：选择**默认视频模型**。聊天和模型都未选定视频模型时，会使用该默认值。
4. 授予用户访问权限。在**用户** > **群组**（或默认权限）中，开启**功能**下的**视频生成**权限。此权限默认关闭，参见[权限](/features/authentication-access/rbac/permissions)。管理员始终拥有此权限。
5. 对于每个需要创建视频的模型，打开**工作区** > **模型** > **编辑**，开启**功能**下的**视频生成**，并保持**内置工具**下的**视频生成**类别开启。参见[模型](/features/workspace/models)。

### 视频连接 {#video-connections}

每个连接对应一个提供视频 API 的提供商。支持两类连接：

- **兼容 OpenAI** 的服务器，例如 OpenAI 或 LiteLLM。
- **OpenRouter**，提供 Veo、Kling、Seedance 等视频模型。Open WebUI 会根据 `openrouter.ai` URL 自动识别此提供商，否则需在**高级**下将**提供商**设为 **OpenRouter**。

| 字段 | 用途 |
| :--- | :--- |
| **URL** 和**身份验证** | 提供商的基础 URL 及验证方式（API 密钥、转发会话或 OAuth、Entra ID 或无），也可添加额外的**请求头**。使用**验证连接**进行测试。 |
| **Model IDs** | 用户可选择的视频模型。留空时实时列出提供商的视频模型。 |
| **视频尺寸**和**视频时长** | 每次请求发送的默认值，例如 `1280x720` 和 `8` 秒。 |
| **API 版本** | 发给提供商的 API 版本查询参数。OpenRouter 不使用此字段。 |
| **额外参数** | 每次请求时原样传给提供商的额外 JSON。 |
| **访问控制** | 哪些用户和群组可以使用该连接的模型。 |

Open WebUI 最多等待 15 分钟，每 5 秒检查一次进度。可分别通过 [`VIDEO_GENERATION_TIMEOUT`](/reference/env-configuration#video_generation_timeout) 和 [`VIDEO_GENERATION_POLL_INTERVAL`](/reference/env-configuration#video_generation_poll_interval) 调整。

## 在聊天中创建视频 {#create-a-video-in-chat}

1. 在消息输入框的 **+** 菜单中开启**视频**。如果连接提供多个视频模型，也在此选择。
2. 描述视频并发送。要使用图像作为第一帧，请先附加该图像。
3. 提供商生成完成后，视频会出现在回复中。

视频通过内置工具创建，聊天模型需要**原生**[函数调用](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)。保持选中平常的聊天模型，和[生成图像](/features/chat-conversations/image-generation-and-editing/usage)时一样。

如果 **+** 菜单中没有**视频**，请确认**设置** > **图像与视频**下的**视频**中已开启视频生成、你的角色拥有**视频生成**权限，且模型已开启**视频生成**功能。
