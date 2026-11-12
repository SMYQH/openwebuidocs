---
sidebar_position: 0
title: "OpenAI 文本转语音集成"
---

# 使用 OpenAI 实现文本转语音 {#using-openai-for-text-to-speech}

本指南介绍如何在 Open WebUI 中使用 OpenAI 官方 Text-to-Speech API。如果你已经拥有 OpenAI API 密钥，这是最简单的配置方式。

:::tip 想配置 STT？
请查看配套指南：[使用 OpenAI 实现语音转文本](/features/chat-conversations/audio/speech-to-text/openai-stt-integration)
:::

## 前置要求 {#requirements}

- 拥有可访问 Audio API 的 OpenAI API 密钥
- Open WebUI 已安装并正常运行

## 快速配置（UI） {#quick-setup-ui}

1. 点击你的**头像图标**（左下角）
2. 选择 **管理面板**
3. 点击 **设置** → **音频** 标签
4. 按如下方式配置：

| 设置 | 值 |
|---------|-------|
| **文本转语音引擎** | `OpenAI` |
| **API 基础 URL** | `https://api.openai.com/v1` |
| **API 密钥** | 你的 OpenAI API 密钥 |
| **TTS 模型** | `tts-1` 或 `tts-1-hd` |
| **TTS 语音** | 从可用语音中选择 |

5. 点击 **Save**

## 可用模型 {#available-models}

| 模型 | 说明 | 最适合 |
|-------|-------------|----------|
| `tts-1` | 标准音质、延迟更低 | 实时应用、更快响应 |
| `tts-1-hd` | 更高音质 | 预录内容、高品质音频 |

## 可用语音 {#available-voices}

OpenAI 提供 6 种内置语音：

| 语音 | 说明 |
|-------|-------------|
| `alloy` | 中性、均衡 |
| `echo` | 温暖、偏对话风格 |
| `fable` | 表现力更强、英式口音 |
| `onyx` | 低沉、权威感强 |
| `nova` | 友好、轻快 |
| `shimmer` | 柔和、轻柔 |

:::tip
你可以多试几种语音，找到最适合自己场景的一种。也可以在 OpenAI 文档中预览相关语音。
:::

## 按模型设置 TTS 语音 {#per-model-tts-voice}

你可以为单个模型指定专属 TTS 语音，让不同 AI persona 拥有不同声音。该设置位于模型编辑器中。

### 设置模型专属语音 {#setting-a-model-specific-voice}

1. 前往 **Workspace > Models**
2. 点击要配置模型上的 **Edit**（铅笔）图标
3. 向下滚动找到 **TTS 语音** 字段
4. 输入语音名称（例如 `alloy`、`echo`、`shimmer`、`onyx`、`nova`、`fable`）
5. 点击 **Save**

### 语音优先级 {#voice-priority}

播放 TTS 音频时，Open WebUI 按以下优先级选择语音：

1. **模型专属 TTS 语音**（如果在模型编辑器中已设置）
2. **用户个人语音设置**（如果已在用户设置中配置）
3. **系统默认语音**（由管理员配置）

这样管理员就可以为每个 AI persona 设定稳定的声音，同时仍允许用户在没有模型专属语音时使用自己的偏好设置。

### 使用场景 {#use-cases}

- **角色化 persona**：例如让 “British Butler” 模型使用 `fable`，而 “Energetic Assistant” 使用 `nova`
- **语言学习**：为不同语言教师分配合适的声音
- **无障碍场景**：为无障碍用途模型设置更清晰的语音

## 环境变量配置 {#environment-variables-setup}

如果你更倾向于通过环境变量配置：

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - AUDIO_TTS_ENGINE=openai
      - AUDIO_TTS_OPENAI_API_BASE_URL=https://api.openai.com/v1
      - AUDIO_TTS_OPENAI_API_KEY=sk-...
      - AUDIO_TTS_MODEL=tts-1
      - AUDIO_TTS_VOICE=alloy
    # ... 其他配置
```

### 全部 TTS 环境变量 {#all-tts-environment-variables}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_TTS_ENGINE` | 设置为 `openai` | empty |
| `AUDIO_TTS_OPENAI_API_BASE_URL` | OpenAI API 基础 URL | `https://api.openai.com/v1` |
| `AUDIO_TTS_OPENAI_API_KEY` | 你的 OpenAI API 密钥 | empty |
| `AUDIO_TTS_MODEL` | TTS 模型（`tts-1` 或 `tts-1-hd`） | `tts-1` |
| `AUDIO_TTS_VOICE` | 使用的语音 | `alloy` |

## 测试 TTS {#using-the-openai-realtime-engine}

1. 新建一个聊天
2. 向任意模型发送一条消息
3. 点击 AI 回复上的**扬声器图标**，听它朗读内容

## 响应切分 {#using-openrouter-as-a-text-to-speech-provider}

朗读较长回复时，Open WebUI 可以在发送到 TTS 引擎前先把文本拆分成多个片段。该设置位于 **管理面板 > 设置 > 音频** 下的 **响应切分**。

| 选项 | 说明 |
|--------|-------------|
| **Punctuation**（默认） | 按句子边界切分：句号（`.`）、感叹号（`!`）、问号（`?`）和换行。自然感最佳。 |
| **Paragraphs** | 仅按段落分隔（双换行）切分。生成的音频块更长。 |
| **None** | 整段回复作为一个整体发送。长回复可能会导致音频启动延迟。 |

:::tip
大多数场景建议使用 **Punctuation** 模式。它在流式性能（更快开始播放）和自然语音节奏之间取得了最好平衡。
:::

### 400 错误为何发生 {#why-the-400-error-happens}

OpenRouter 的 [`/audio/speech` 端点](https://openrouter.ai/docs/guides/overview/multimodal/tts)在省略该字段时会把 `response_format` 默认为 `pcm`。Open WebUI 在其请求载荷中不会发送 `response_format`，因此 OpenRouter 返回原始 PCM 音频，而 Open WebUI 无法播放它，最终导致 `400 Bad Request`。

修复方法是在 TTS 设置的 **OpenAI Params** 字段（额外参数）中加入 `{"response_format": "mp3"}`，显式请求 MP3。

## 故障排查 {#testing-tts}

## 响应切分 {#response-splitting}

在读取较长的响应时，Open WebUI 可以在把文本发送给 TTS 引擎之前将其切分为多个块。这在 **设置 > 管理 > 音频** 的 **响应切分** 中配置。

| 选项 | 说明 |
|--------|-------------|
| **标点符号**（默认） | 在句子边界处切分：句号（`.`）、感叹号（!）、问号（`?`）和换行。最适合自然的语速节奏。 |
| **段落** | 仅在段落分隔处（两个换行）切分。得到的音频块更长。 |
| **无** | 将整个响应作为单个块发送。在较长响应上可能导致音频开始前出现延迟。 |

:::tip
大多数使用场景推荐使用 **标点符号** 模式。它在流式性能（音频快速开始）和自然语音节奏之间提供了最佳平衡。
:::

## 排查问题 {#troubleshooting}

### 没有音频播放 {#no-audio-plays}

1. 检查 OpenAI API 密钥是否有效，并确认已开通 Audio API
2. 确认 API 基础 URL 是否正确（`https://api.openai.com/v1`）
3. 检查浏览器控制台（F12）是否有报错

### 音质问题 {#audio-quality-issues}

- 将 `tts-1` 切换为 `tts-1-hd` 可获得更高音质
- 注意：`tts-1-hd` 延迟会略高

### 速率限制 {#rate-limits}

OpenAI Audio API 有速率限制。如果你经常触发限制：
- 可考虑缓存常用短语
- 使用 `tts-1` 代替 `tts-1-hd`（消耗更少 token）

更多排查信息请参阅 [音频故障排查指南](/troubleshooting/audio)。

## 成本说明 {#cost-considerations}

OpenAI 的 TTS 按字符数计费。当前价格请查看 [OpenAI Pricing](https://platform.openai.com/docs/pricing)。注意 `tts-1-hd` 的价格高于 `tts-1`。

:::info
如果你想要免费替代方案，可考虑 [OpenAI Edge TTS](/features/chat-conversations/audio/text-to-speech/openai-edge-tts-integration)，它利用微软 Edge 浏览器的免费 TTS 能力。
:::
