---
sidebar_position: 3
title: "自托管语音转文本"
description: "将 Open WebUI 连接到自托管的 OpenAI 兼容转录服务器。"
---

# 自托管语音转文本 {#self-hosted-speech-to-text}

Open WebUI 可以将录音发送到提供 OpenAI 兼容的 `/v1/audio/transcriptions` 端点的自托管服务器。本指南以 LocalAI 搭配标准 Whisper base 模型为例。服务器负责转录音频；Open WebUI 负责录音，并将返回的文本填入聊天输入框。

:::warning

本教程是社区贡献内容，不受 Open WebUI 团队支持。它仅用于演示如何针对你的具体使用场景定制 Open WebUI。想参与贡献？请查看[贡献教程](/tutorials/contributing-tutorial)。

:::

## 配置 Open WebUI {#configure-open-webui}

转录服务器启动后，打开管理面板中的**设置 > 音频**，按下表配置：

| 设置 | 下方 LocalAI 示例中的值 |
|---------|------------------------------------|
| **语音转文本引擎** | `OpenAI` |
| **API 基础 URL** | 当两个应用都直接运行在同一主机上时为 `http://127.0.0.1:8081/v1` |
| **API 密钥** | 你在 `LOCALAI_API_KEY` 中设置的密钥 |
| **请求格式** | `Multipart Upload` |
| **STT 模型** | `whisper-1` |

点击**保存**。在用户音频设置中，将**语音转文本引擎**保持为**默认**，以便使用管理员配置的服务器转录录音。

`OpenAI` 引擎仅决定使用哪种 API 协议。使用上述基础 URL 时，请求会被发往你的 LocalAI 服务器。你不需要 OpenAI 账号或 OpenAI API 密钥。模型名称必须与转录服务器提供的名称一致。

:::important 服务器地址

Open WebUI 的后端会发起转录请求。请使用后端可访问的地址，它可能与浏览器中的地址不同。在容器中，`127.0.0.1` 指的是该容器本身。

| 部署方式 | API 基础 URL 示例 |
|------------|----------------------|
| 两个应用都直接运行在同一主机上 | `http://127.0.0.1:8081/v1` |
| 两个容器共享同一 Docker 网络，LocalAI 以服务名 `localai` 监听 8080 端口 | `http://localai:8080/v1` |
| Open WebUI 运行在 Docker Desktop 中，LocalAI 在主机可访问的接口上监听 8081 端口 | `http://host.docker.internal:8081/v1` |

仅绑定到 `127.0.0.1` 的主机服务可能无法从容器访问。在更改绑定地址之前，请查阅你所用容器平台的网络文档；在让其他主机访问 LocalAI 时请保留身份验证。

:::

## 启动 LocalAI 转录服务器 {#start-a-localai-transcription-server}

在服务器上安装 [LocalAI](https://localai.io/docs/installation/) 和 FFmpeg。对于原生安装，以下命令会安装 Whisper 后端和 `whisper-1` gallery 模型，然后在 8081 端口启动一个带身份验证的服务器：

```bash
mkdir -p models backends
local-ai backends install whisper --backends-path ./backends
local-ai models install whisper-1 --models-path ./models --backends-path ./backends

export LOCALAI_API_KEY='replace-with-your-own-secret'
local-ai run --address 127.0.0.1:8081 --models-path ./models --backends-path ./backends
```

LocalAI 的 [`whisper-1` gallery 条目](https://github.com/mudler/LocalAI/blob/master/gallery/index.yaml)通过 `whisper.cpp` 使用 Whisper base 模型。它的名称是一个本地 API 标识符。其他自托管服务器可能使用不同的名称，或需要不同的安装步骤。

在能够访问 LocalAI 的机器上，先测试一段短录音，然后再配置 Open WebUI：

```bash
curl --fail-with-body http://127.0.0.1:8081/v1/audio/transcriptions \
  -H "Authorization: Bearer $LOCALAI_API_KEY" \
  -F model=whisper-1 \
  -F file=@recording.wav \
  -F response_format=json
```

响应中应包含带有转录文本的 `text` 字段。LocalAI 还接受 FFmpeg 支持的格式，包括浏览器录制的 WebM。有关后端特定选项，请参阅 [LocalAI 的转录文档](https://localai.io/docs/features/audio-to-text/)。

## 环境变量 {#environment-variables}

对于全新配置的 Open WebUI，你可以通过环境变量设置相同的值：

```bash
AUDIO_STT_ENGINE=openai
AUDIO_STT_OPENAI_API_BASE_URL=http://127.0.0.1:8081/v1
AUDIO_STT_OPENAI_API_KEY=replace-with-your-own-secret
AUDIO_STT_MODEL=whisper-1
```

请根据部署方式填写后端可访问的基础 URL，并使用与 LocalAI 相同的密钥。Open WebUI 数据库中保存的设置可能会覆盖这些初始值；重启后，请检查管理面板中的**设置 > 音频**。

## 测试与排查 {#test-and-troubleshoot}

点击聊天输入框中的麦克风，录制一句短句，然后结束录音。转录文本应出现在输入框中。浏览器录音需要麦克风权限以及安全上下文，例如 HTTPS 或 localhost。

- **连接被拒绝或超时**：检查从 Open WebUI 后端所在主机或容器访问时使用的地址。确认 LocalAI 正在可访问的接口和端口上监听。
- **401 或 403**：检查已保存的 STT API 密钥是否与 LocalAI 的密钥一致。
- **模型未找到**：使用相同的授权头通过 `GET /v1/models` 检查已安装的模型名称。
- **404**：基础 API 端点的 URL 应以 `/v1` 结尾，而不是 `/v1/audio/transcriptions`；Open WebUI 会自动追加转录端点的路径。
- **音频解码错误**：确认 LocalAI 可以访问 FFmpeg，并用 `curl` 命令直接尝试一个 WAV 文件。对于浏览器录音，还要检查 Open WebUI 允许的扩展名和内容类型是否包含你的浏览器所发送的格式。

该配置仅针对录音转文本，不涉及文本转语音或实时语音 API。
