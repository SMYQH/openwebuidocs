---
sidebar_position: 2
title: "Mistral Voxtral 语音转文本"
---

# 使用 Mistral Voxtral 实现语音转文本 {#using-mistral-voxtral-for-speech-to-text}

本指南介绍如何在 Open WebUI 中使用 Mistral 的 Voxtral 模型进行语音转文本。Voxtral 是 Mistral 的语音转文本模型，可提供较准确的转录结果。

:::tip 想配置 TTS？
请查看配套指南：[使用 Mistral 实现文本转语音](/features/chat-conversations/audio/text-to-speech/mistral-tts-integration)
:::

## 前置要求 {#requirements}

- 一个 Mistral API 密钥
- Open WebUI 已安装并正常运行

## 快速配置（UI） {#quick-setup-ui}

1. 点击你的**头像图标**（左下角）
2. 选择 **管理面板**
3. 点击 **设置** → **音频** 标签
4. 按如下方式配置：

| 设置 | 值 |
|---------|-------|
| **语音转文本引擎** | `MistralAI` |
| **API 密钥** | 你的 Mistral API 密钥 |
| **STT 模型** | `voxtral-mini-2602`（留空则回退到 `voxtral-mini-latest`，这是 Mistral 可能已不再提供的别名，因此请设置它） |

5. 点击**保存**

## 可用模型 {#available-models}

| 模型 | 说明 |
|-------|-------------|
| `voxtral-mini-2602` | Voxtral Mini Transcribe 2 —— 当前的转录模型（推荐） |

:::caution 请显式设置模型
Mistral 不再发布 `voxtral-mini-latest` 之类的 `-latest` 别名。请使用 [Mistral 模型总览](https://docs.mistral.ai/getting-started/models/models_overview/)中的带日期 ID。
:::

## 环境变量配置 {#environment-variables-setup}

如果你更倾向于使用环境变量：

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - AUDIO_STT_ENGINE=mistral
      - AUDIO_STT_MISTRAL_API_KEY=your-mistral-api-key
      - AUDIO_STT_MODEL=voxtral-mini-2602
    # ... other configuration
```

### 全部 Mistral STT 环境变量 {#all-mistral-stt-environment-variables}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_STT_ENGINE` | 设置为 `mistral` | empty（使用本地 Whisper） |
| `AUDIO_STT_MISTRAL_API_KEY` | 你的 Mistral API 密钥 | empty |
| `AUDIO_STT_MISTRAL_API_BASE_URL` | Mistral API 基础 URL | `https://api.mistral.ai/v1` |
| `AUDIO_STT_MISTRAL_USE_CHAT_COMPLETIONS` | 使用聊天补全端点 | `false` |
| `AUDIO_STT_MODEL` | STT 模型 | 留空（请求时使用 `voxtral-mini-latest`） |

## 转录方式 {#transcription-methods}

Mistral 支持两种转录方式：

### 标准转录（默认） {#standard-transcription-default}

使用专用转录端点。这是推荐方式。

### Chat Completions 方式 {#chat-completions-method}

在管理员的**音频**设置中打开**使用 Chat Completions API**，或设置 `AUDIO_STT_MISTRAL_USE_CHAT_COMPLETIONS=true`，即可改用 Mistral 的 Chat Completions API 进行转录。只有在**语音转文本引擎**为 `MistralAI` 时才会显示该开关。

随后 Open WebUI 会向 `<API Base URL>/chat/completions` 发送请求，而不是 `<API Base URL>/audio/transcriptions`。请求会把**STT 模型**作为 `model` 发送，并附带一条由两部分组成的用户消息：base64 编码的音频作为 `input_audio`，以及指令 `Transcribe this audio exactly as spoken in its original language. Do not translate it to another language.`。当你在**设置 > 音频**中设置了**语言**时，指令会变成 `Transcribe this audio exactly as spoken in <language>. Do not translate it.`。Open WebUI 使用回复中的消息内容作为转录结果，因此请把**STT 模型**设为一个在 chat completions 端点接受音频输入的 Mistral 模型。

该方式：
- 原样发送 FLAC、M4A、MP3、MP4、MPEG、WAV 和 WebM 音频，其他格式以及 MP4 容器中的 AAC 音频会先转换为 MP3。启用 [`BYPASS_PYDUB_PREPROCESSING`](/reference/env-configuration#bypass_pydub_preprocessing) 时不会做任何转换，而 slim 镜像始终启用该设置
- 结果可能与标准转录端点的结果不同

## 使用 STT {#using-stt}

1. 点击聊天输入框中的**麦克风图标**
2. 说出你的内容
3. 再次点击麦克风停止录音，或等待系统检测到静音
4. 你的语音会被转录并显示在输入框中

## 支持的音频格式 {#supported-audio-formats}

Voxtral 接受常见音频格式。系统默认允许 `audio/*` 和 `video/webm`。

如果使用 chat completions 方式，音频会自动转换为 mp3。

## 故障排查 {#troubleshooting}

### API 密钥错误 {#api-key-errors}

如果看到错误“Mistral API key is required”：

1. 确认 API 密钥填写正确
2. 检查 API 密钥是否已过期
3. 确认你的 Mistral 账号已开通 API 访问权限

### 转录无法工作 {#transcription-not-working}

1. 检查容器日志：`docker logs open-webui -f`
2. 确认 STT 引擎设置为 `MistralAI`
3. 优先尝试标准转录方式（关闭 chat completions）
4. 如果错误为 `Failed to parse Mistral response: Empty transcript in response`，说明回复中没有文本。开启**使用 Chat Completions API** 时，请换一个**STT 模型**或关闭该开关

### 音频格式问题 {#audio-format-issues}

如果你使用 chat completions 方式且音频转换失败，错误为 `Audio conversion failed. Chat completions API requires mp3 or wav format.`。在使用 `USE_SLIM_DOCKER=true` 的镜像上，Open WebUI 不会为该方式转换音频，因此到达它的音频如果不是 `.mp3` 或 `.wav` 文件，就会以 `Mistral chat transcription requires MP3 or WAV in slim; local conversion is unavailable.` 失败。要解决这两种错误：

- 确保容器中可用 FFmpeg
- 尝试录制为其他格式（wav 或 mp3）
- 切回标准转录方式

更多排查信息请参阅 [音频故障排查指南](/troubleshooting/audio)。

## 与其他 STT 方案对比 {#comparison-with-other-stt-options}

| 特性 | Mistral Voxtral | OpenAI Whisper | 本地 Whisper |
| --------- | ----------------- | ---------------- | --------------- |
| **成本** | 按分钟计费 | 按分钟计费 | 免费 |
| **隐私** | 音频发送到 Mistral | 音频发送到 OpenAI | 音频保留本地 |
| **模型选项** | `voxtral-mini-2602` | `gpt-transcribe`、`whisper-1` | tiny → large |
| **需要 GPU** | 否 | 否 | 推荐 |

## 成本说明 {#cost-considerations}

Mistral 的 STT 按音频分钟数计费。当前价格请查看 [Mistral 定价页](https://mistral.ai/products/la-plateforme#pricing)。

:::tip
如果想使用免费 STT，可选择 **Local Whisper**（默认方案）或浏览器 **Web API** 进行基础转录。
:::
