---
sidebar_position: 2
title: "环境变量"
---

## 环境变量清单 {#environment-variables-list}

:::info

如需查看 Open WebUI 的全部环境变量，请参阅 [Environment Variable Configuration](/reference/env-configuration) 页面。

:::

下文汇总了语音转文本（STT）和文本转语音（TTS）相关的环境变量。

:::tip UI 配置
其中大多数设置也可以在 **管理面板 → 设置 → 音频** 中配置。环境变量会在启动时优先生效，但之后仍可在 UI 中覆盖。
:::

## 语音转文本（STT）环境变量 {#speech-to-text-stt-environment-variables}

### 预处理 {#preprocessing}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `BYPASS_PYDUB_PREPROCESSING` | 在将音频发送到 STT 引擎前，跳过基于 pydub 的预处理（MP3 转换、压缩、分块切分）。适用于所有引擎。当上游提供商已处理这些步骤，或主机上没有 ffmpeg 时很有用。 | `false` |

### 本地 Whisper {#local-whisper}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `WHISPER_MODEL` | Whisper 模型大小 | `base` |
| `WHISPER_MODEL_DIR` | Whisper 模型文件的存储目录 | `{CACHE_DIR}/whisper/models` |
| `WHISPER_COMPUTE_TYPE` | 推理使用的计算类型（见下方说明） | `int8` |
| `WHISPER_LANGUAGE` | ISO 639-1 语言代码（留空 = 自动检测） | empty |
| `WHISPER_MULTILINGUAL` | 使用多语言 Whisper 模型 | `false` |
| `WHISPER_MODEL_AUTO_UPDATE` | 自动下载模型更新 | `false` |
| `WHISPER_VAD_FILTER` | 启用语音活动检测过滤器 | `false` |

:::info `WHISPER_COMPUTE_TYPE` 可选值
- `int8` —— CPU 默认值，速度最快，但在较老的 GPU 上可能不可用
- `float16` —— **CUDA / GPU 推荐值**
- `int8_float16` —— 混合模式（int8 权重，float16 计算）
- `float32` —— 兼容性最高，但最慢

如果你使用 `:cuda` Docker 镜像且 GPU 较旧，请设置 `WHISPER_COMPUTE_TYPE=float16` 以避免报错。
:::

### OpenAI 兼容 STT {#openai-compatible-stt}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_STT_ENGINE` | STT 引擎：留空（本地 Whisper）、`openai`、`azure`、`deepgram`、`mistral` | empty |
| `AUDIO_STT_MODEL` | 外部提供商使用的 STT 模型 | empty |
| `AUDIO_STT_OPENAI_API_BASE_URL` | OpenAI 兼容 API 基础 URL | `https://api.openai.com/v1` |
| `AUDIO_STT_OPENAI_API_KEY` | OpenAI API 密钥 | empty |
| `AUDIO_STT_SUPPORTED_CONTENT_TYPES` | 支持的音频 MIME 类型，逗号分隔 | empty |

### Azure STT {#azure-stt}

有关设置，请参阅 [Azure AI Speech STT 指南](/features/chat-conversations/audio/speech-to-text/azure-stt-integration)。

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_STT_AZURE_API_KEY` | Azure Cognitive Services API 密钥 | empty |
| `AUDIO_STT_AZURE_REGION` | Azure 区域 | empty（默认使用 `eastus`） |
| `AUDIO_STT_AZURE_LOCALES` | 地区列表，逗号分隔且不含空格（例如 `en-US,de-DE`） | empty（默认发送内置的 13 种语言列表） |
| `AUDIO_STT_AZURE_BASE_URL` | 自定义 Azure 基础 URL（可选） | empty |
| `AUDIO_STT_AZURE_MAX_SPEAKERS` | 说话人数上限（用于说话人分离） | empty（默认使用 `3`） |

### Deepgram STT {#deepgram-stt}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `DEEPGRAM_API_KEY` | Deepgram API 密钥 | empty |

### Mistral STT {#mistral-stt}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_STT_MISTRAL_API_KEY` | Mistral API 密钥 | empty |
| `AUDIO_STT_MISTRAL_API_BASE_URL` | Mistral API 基础 URL | `https://api.mistral.ai/v1` |
| `AUDIO_STT_MISTRAL_USE_CHAT_COMPLETIONS` | 使用 chat completions 端点 | `false` |

## 文本转语音（TTS）环境变量 {#text-to-speech-tts-environment-variables}

### 通用 TTS {#general-tts}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_TTS_ENGINE` | TTS 引擎：留空（禁用）、`openai`、`openai-realtime`、`mistral`、`elevenlabs`、`azure`、`transformers` | empty |
| `AUDIO_TTS_MODEL` | TTS 模型 | `tts-1` |
| `AUDIO_TTS_VOICE` | 默认语音 | `alloy` |
| `AUDIO_TTS_SPLIT_ON` | 文本切分方式：`punctuation`、`paragraphs` 或 `none` | `punctuation` |
| `AUDIO_TTS_API_KEY` | ElevenLabs 或 Azure TTS 使用的 API 密钥 | empty |

### OpenAI 兼容 TTS {#openai-compatible-tts}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_TTS_OPENAI_API_BASE_URL` | OpenAI 兼容 TTS API 基础 URL | `https://api.openai.com/v1` |
| `AUDIO_TTS_OPENAI_API_KEY` | OpenAI TTS API 密钥 | empty |
| `AUDIO_TTS_OPENAI_PARAMS` | OpenAI TTS 附加 JSON 参数 | empty || `REALTIME_TTS_PROMPT_TEMPLATE` | 当 `AUDIO_TTS_ENGINE` 为 `openai-realtime` 时给模型的指令 | empty（使用内置提示词） |

### Mistral TTS {#mistral-tts}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_TTS_MISTRAL_API_KEY` | Mistral TTS API 密钥 | empty |
| `AUDIO_TTS_MISTRAL_API_BASE_URL` | Mistral API 基础 URL | `https://api.mistral.ai/v1` |

:::info
当 `AUDIO_TTS_ENGINE=mistral` 且 `AUDIO_TTS_MODEL` 为空时，Open WebUI 会默认使用 `voxtral-mini-tts-2603`。
:::

### Azure TTS {#azure-tts}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_TTS_AZURE_SPEECH_REGION` | Azure Speech 区域 | `eastus` |
| `AUDIO_TTS_AZURE_SPEECH_BASE_URL` | 自定义 Azure Speech 基础 URL（可选） | empty |

配置步骤请参阅 [Azure AI Speech TTS 指南](/features/chat-conversations/audio/text-to-speech/azure-tts-integration)。
| `AUDIO_TTS_AZURE_SPEECH_OUTPUT_FORMAT` | 音频输出格式 | `audio-24khz-160kbitrate-mono-mp3` |

## 实时语音通话环境变量 {#realtime-voice-calls-environment-variables}

这些变量用于配置[语音模式](/features/chat-conversations/chat-features/voice-mode#realtime-calls)的 **Realtime（实时）**通话模式。详情参见环境变量参考中的[实时语音通话](/reference/env-configuration#realtime-voice-calls)。

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| [`AUDIO_REALTIME_ENABLED`](/reference/env-configuration#audio_realtime_enabled) | 通话模式：`true` 为 **Realtime**，`false` 为 **Standard** | `false` |
| [`AUDIO_REALTIME_PROVIDER`](/reference/env-configuration#audio_realtime_provider) | 服务商：`openai` 表示 OpenAI 或兼容服务器，`azure` 表示 Azure OpenAI | `openai` |
| [`AUDIO_REALTIME_AUTH_TYPE`](/reference/env-configuration#audio_realtime_auth_type) | 认证方式：`api_key`，或在使用 Azure 服务商时使用 `microsoft_entra_id` | `api_key` |
| [`AUDIO_REALTIME_OPENAI_API_BASE_URL`](/reference/env-configuration#audio_realtime_openai_api_base_url) | Realtime API 基础 URL，或 Azure 端点后接 `/openai/v1` | `https://api.openai.com/v1` |
| [`AUDIO_REALTIME_OPENAI_API_KEY`](/reference/env-configuration#audio_realtime_openai_api_key) | Realtime API 密钥 | empty |
| [`AUDIO_REALTIME_MODEL`](/reference/env-configuration#audio_realtime_model) | Realtime 语音模型，或 Azure 上的部署名称 | `gpt-realtime-2.1-mini` |
| [`AUDIO_REALTIME_VOICE`](/reference/env-configuration#audio_realtime_voice) | 语音模型的默认音色 | `marin` |
| [`AUDIO_REALTIME_TRANSCRIPTION_MODEL`](/reference/env-configuration#audio_realtime_transcription_model) | 转录用户说话内容的模型 | `gpt-transcribe` |
| [`AUDIO_REALTIME_INPUT_PARAMS`](/reference/env-configuration#audio_realtime_input_params) | 额外的音频输入设置，JSON 对象形式，例如降噪 | empty |
| [`REALTIME_CALL_PROMPT_TEMPLATE`](/reference/env-configuration#realtime_call_prompt_template) | 给语音模型的指令 | empty（使用内置提示词） |

## 配置音频的提示 {#tips-for-configuring-audio}

### 使用本地 Whisper STT {#using-local-whisper-stt}

如果你遇到 GPU 加速问题或使用较旧 GPU，可以尝试设置：
```yaml
environment:
  - WHISPER_COMPUTE_TYPE=float16
```

### 使用外部 TTS 服务 {#using-external-tts-services}

如果你在 Docker 中运行 Open WebUI 并接入外部 TTS 服务：

```yaml
environment:
  - AUDIO_TTS_ENGINE=openai
  - AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5050/v1
  - AUDIO_TTS_OPENAI_API_KEY=your-api-key
```

:::tip
在 Docker Desktop（Windows / Mac）中可使用 `host.docker.internal` 访问宿主机服务；Linux 上请使用宿主机 IP 或容器网络。
:::

如需排查音频问题，请参阅 [音频故障排查指南](/troubleshooting/audio)。
