---
sidebar_position: 0
title: "OpenAI 语音转文本集成"
---

# 使用 OpenAI 实现语音转文本 {#using-openai-for-speech-to-text}

本指南介绍如何在 Open WebUI 中使用 OpenAI Whisper API 进行语音转文本。这种方式提供云端转录能力，无需本地 GPU 资源。

:::tip 想配置 TTS？
请查看配套指南：[使用 OpenAI 实现文本转语音](/features/chat-conversations/audio/text-to-speech/openai-tts-integration)
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
| **语音转文本引擎** | `OpenAI` |
| **API 基础 URL** | `https://api.openai.com/v1` |
| **API 密钥** | 你的 OpenAI API 密钥 |
| **STT 模型** | `gpt-transcribe` |
| **支持的 MIME 类型** | 留空则使用运行时默认值 `audio/*,video/webm`，或设置为 `audio/wav,audio/mpeg,audio/webm` |

5. 点击**保存**

## 可用模型 {#available-models}

| 模型 | 说明 |
|-------|-------------|
| `gpt-transcribe` | OpenAI 当前的转录模型（推荐）——词错误率约为 `whisper-1` 的一半 |
| `gpt-live-transcribe` | 低延迟流式转录 |
| `whisper-1` | 旧版 Whisper large-v2 模型，将于 2027-02-26 退役 |

:::info
OpenAI 推荐新部署使用 `gpt-transcribe`。`AUDIO_STT_MODEL` 默认为空，因此需要显式设置模型。需要完全在本地转录时，可使用 Open WebUI 内置的本地 Whisper。也可选择 Deepgram 等其他提供商。
:::

:::caution OpenAI 正在退役旧的转录模型
OpenAI 将于 2027-02-26 从其 API 中移除 `whisper-1`、`gpt-4o-transcribe`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe-diarize`。如果 **STT 模型**设为其中之一，请在此之前切换到 `gpt-transcribe`。详情参见 [OpenAI 弃用页面](https://developers.openai.com/api/docs/deprecations#2026-08-26-transcription-models)。
:::

## 环境变量配置 {#environment-variables-setup}

如果你更倾向于使用环境变量：

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - AUDIO_STT_ENGINE=openai
      - AUDIO_STT_OPENAI_API_BASE_URL=https://api.openai.com/v1
      - AUDIO_STT_OPENAI_API_KEY=sk-...
      - AUDIO_STT_MODEL=gpt-transcribe
    # ... other configuration
```

### 全部 STT 环境变量（OpenAI） {#all-stt-environment-variables-openai}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_STT_ENGINE` | 设置为 `openai` | empty（使用本地 Whisper） |
| `AUDIO_STT_OPENAI_API_BASE_URL` | OpenAI API 基础 URL | `https://api.openai.com/v1` |
| `AUDIO_STT_OPENAI_API_KEY` | 你的 OpenAI API 密钥 | empty |
| `AUDIO_STT_MODEL` | STT 模型 | empty |
| `AUDIO_STT_SUPPORTED_CONTENT_TYPES` | 允许的音频 MIME 类型 | `audio/*,video/webm` |

### 支持的音频格式 {#supported-audio-formats}

默认情况下，Open WebUI 接受 `audio/*` 和 `video/webm` 进行转录。如果你想限制或扩展支持格式，可设置 `AUDIO_STT_SUPPORTED_CONTENT_TYPES`：

```yaml
environment:
  - AUDIO_STT_SUPPORTED_CONTENT_TYPES=audio/wav,audio/mpeg,audio/webm
```

OpenAI Whisper API 支持：`mp3`、`mp4`、`mpeg`、`mpga`、`m4a`、`wav`、`webm`

## 使用 STT {#using-stt}

1. 点击聊天输入框中的**麦克风图标**
2. 说出你的内容
3. 再次点击麦克风停止录音，或等待系统检测到静音
4. 你的语音会被转录并显示在输入框中

## OpenAI 与 Local Whisper 对比 {#openai-vs-local-whisper}

| 特性 | OpenAI Whisper API | Local Whisper |
|---------|-------------------|---------------|
| **延迟** | 取决于网络 | 短音频通常更快 |
| **成本** | 按分钟计费 | 免费（使用你的硬件） |
| **隐私** | 音频发送到 OpenAI | 音频留在本地 |
| **需要 GPU** | 否 | 建议使用，可加快转录 |
| **模型选项** | `gpt-transcribe`、`gpt-live-transcribe`、`whisper-1` | tiny、base、small、medium、large |

在以下情况下推荐选择 **OpenAI**：
- 你没有 GPU
- 你希望获得稳定一致的表现
- 隐私不是首要顾虑

在以下情况下推荐选择 **Local Whisper**：
- 你想要免费转录
- 你需要音频保留在本地
- 你拥有可用于加速的 GPU

## 故障排查 {#troubleshooting}

### 麦克风无法工作 {#microphone-not-working}

1. 确保你正在使用 HTTPS 或 localhost
2. 检查浏览器麦克风权限
3. 查看 [麦克风访问问题](/troubleshooting/audio#microphone-access-issues)

### 转录报错 {#transcription-errors}

1. 检查 OpenAI API 密钥是否有效
2. 确认 API 基础 URL 是否正确
3. 查看容器日志中的报错信息
4. 如果 API 基础 URL 指向其他兼容 OpenAI 的服务，请将 **STT 模型**设为该服务支持的模型 ID
5. 如果错误信息中提到 `response_format`，参见[代理后的 OpenAI 兼容 STT 失败](/troubleshooting/audio#openai-compatible-stt-fails-behind-a-proxy)

### 语言识别问题 {#language-issues}

Open WebUI 会发送设置 → 音频 → 语言中的语言；若设置了 `WHISPER_LANGUAGE`，则发送该值（它同样适用于 Local Whisper 和 Deepgram）；如果请求失败，它会不带语言重试。两处都留空则由 OpenAI 检测语言。

更多排查信息请参阅 [音频故障排查指南](/troubleshooting/audio)。

## 成本说明 {#cost-considerations}

OpenAI 的 STT 按音频分钟数计费。当前价格请参阅 [OpenAI Pricing](https://platform.openai.com/docs/pricing)。

:::tip
如果想使用免费 STT，可选择 **Local Whisper**（默认方案）或浏览器 **Web API** 进行基础转录。
:::
