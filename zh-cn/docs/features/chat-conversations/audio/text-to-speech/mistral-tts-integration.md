---
sidebar_position: 2
title: "Mistral TTS 集成"
---

# 使用 Mistral 实现文本转语音 {#using-mistral-for-text-to-speech}

本指南介绍如何在 Open WebUI 中使用 Mistral 的文本转语音 API。

:::tip 想配置 STT？
请查看配套指南：[使用 Mistral Voxtral 实现语音转文本](/features/chat-conversations/audio/speech-to-text/mistral-voxtral-integration)
:::

## 前置要求 {#requirements}

- 一个 Mistral API 密钥
- Open WebUI 已安装并正常运行

## 快速配置（UI） {#quick-setup-ui}

1. 点击你的**头像图标**（左下角）
2. 选择 **管理面板**
3. 点击 **设置** -> **音频** 标签
4. 按如下方式配置：

| 设置 | 值 |
|---------|-------|
| **文本转语音引擎** | `MistralAI` |
| **API 基础 URL** | `https://api.mistral.ai/v1` |
| **API 密钥** | 你的 Mistral API 密钥 |
| **TTS 模型** | `voxtral-tts-26-03`（或留空使用默认值） |
| **TTS 语音** | 从可用语音中选择 |

5. 点击**保存**

## 可用模型 {#available-models}

| 模型 | 说明 |
|-------|-------------|
| `voxtral-tts-26-03` | Voxtral TTS：Mistral 当前的文本转语音模型，支持零样本音色克隆 |

:::info
如果 `AUDIO_TTS_MODEL` 为空，Open WebUI 会回退到 `voxtral-mini-tts-2603`。选择 **MistralAI** 作为引擎时会填入该模型。
:::

## 环境变量配置 {#environment-variables-setup}

如果你更倾向于通过环境变量配置：

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - AUDIO_TTS_ENGINE=mistral
      - AUDIO_TTS_MISTRAL_API_KEY=your-mistral-api-key
      - AUDIO_TTS_MISTRAL_API_BASE_URL=https://api.mistral.ai/v1
      - AUDIO_TTS_MODEL=voxtral-tts-26-03
      - AUDIO_TTS_VOICE=<voice-id>
    # ... other configuration
```

### 全部 Mistral TTS 环境变量 {#all-mistral-tts-environment-variables}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_TTS_ENGINE` | 设置为 `mistral` | empty（仅使用浏览器侧 TTS） |
| `AUDIO_TTS_MISTRAL_API_KEY` | 你的 Mistral API 密钥 | empty |
| `AUDIO_TTS_MISTRAL_API_BASE_URL` | Mistral API 基础 URL | `https://api.mistral.ai/v1` |
| `AUDIO_TTS_MODEL` | TTS 模型 | `tts-1`（与 OpenAI 引擎共用，因此请设置 Mistral 模型；只有该值为空时才使用 `voxtral-mini-tts-2603`） |
| `AUDIO_TTS_VOICE` | 语音 ID | `alloy`（请设置 Mistral 语音 ID，否则请求会以 `alloy` 发出） |

## 选择语音 {#choosing-voices}

Open WebUI 会向已配置的 Mistral 端点请求可用语音列表，并在 **TTS 语音** 选择器中展示它们。

如果语音列表没有显示：
- 确认 API 密钥有效
- 确认 Open WebUI 服务器或容器可以访问 API 基础 URL
- 查看日志中是否有 `/audio/voices` 请求错误

## 测试 TTS {#testing-tts}

1. 新建一个聊天
2. 向任意模型发送一条消息
3. 点击 AI 回复上的**扬声器图标**，听它朗读内容

## 故障排查 {#troubleshooting}

### "Mistral API key is required for Mistral TTS" {#mistral-api-key-is-required-for-mistral-tts}

1. 确认 `AUDIO_TTS_MISTRAL_API_KEY` 已设置（或已在管理面板的音频设置中填写）
2. 保存设置后重试

### 下拉框中没有语音 {#no-voices-shown-in-the-dropdown}

1. 确认 Open WebUI 到 `AUDIO_TTS_MISTRAL_API_BASE_URL` 的网络访问正常
2. 查看 Open WebUI 日志中与 Mistral 语音列表相关的错误
3. 确认该密钥有权访问 Mistral 音频 API

### TTS 请求失败 {#tts-request-fails}

1. 确认 `AUDIO_TTS_ENGINE=mistral`
2. 将模型明确设为当前的模型 ID，例如 `voxtral-tts-26-03`
3. 尝试切换为已获取列表中的其他语音 ID

更广泛的音频调试请参阅 [音频故障排查指南](/troubleshooting/audio)。
