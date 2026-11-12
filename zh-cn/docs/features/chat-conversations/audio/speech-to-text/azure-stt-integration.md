---
sidebar_position: 2
title: "Azure AI Speech 语音转文本"
---

# 使用 Azure AI Speech 实现语音转文本 {#using-azure-ai-speech-for-speech-to-text}

本指南介绍如何在 Open WebUI 中使用 Azure AI Speech 进行语音转文本。Open WebUI 会将每段录音发送到 Azure 的[快速转录 API](https://learn.microsoft.com/azure/ai-services/speech-service/fast-transcription-create)，该 API 在单次请求中返回文本。

:::tip 想配置 TTS？
请查看配套指南：[使用 Azure AI Speech 实现文本转语音](/features/chat-conversations/audio/text-to-speech/azure-tts-integration)
:::

## 前置要求 {#requirements}

- 一个 Azure Speech 资源（微软文档中也称其为 Speech 的 Foundry 资源），且所在区域需提供**快速转录**功能。并非所有区域都支持：请查看微软 [Speech 服务区域表](https://learn.microsoft.com/azure/ai-services/speech-service/regions?tabs=stt)中的 **Fast transcription** 列。
- 该资源的密钥，可在 Azure 门户的 **Resource Management** > **Keys and Endpoint** 中获取。两个密钥任选其一均可使用。
- 已安装并运行 Open WebUI

:::caution Azure Government
微软说明快速转录在 Azure Government 中不受支持，因此该引擎无法在其中使用。请参阅 [Speech service in sovereign clouds](https://learn.microsoft.com/azure/ai-services/speech-service/sovereign-clouds)。
:::

## 快速配置（UI） {#quick-setup-ui}

1. 点击你的**头像图标**（左下角）
2. 选择 **管理面板**，然后选择 **设置**。设置会在一个窗口中打开。
3. 在侧边栏中，选择 **Admin** 下的 **Audio**（位于 *Tools* 分组中）。另一个位于 *Preferences* 分组的 **Audio** 条目是你的个人音频设置。在窄屏设备上这些标签会隐藏；可直接通过 `/?settings=admin:audio` 打开管理员的音频设置。
4. 按如下方式配置：

| 设置 | 值 |
|---------|-------|
| **语音转文本引擎** | `Azure AI Speech` |
| **API 密钥** | 你的 Speech 资源密钥 |
| **Azure 区域** | 你的 Speech 资源所在区域的标识符，例如 `westus` 或 `westeurope`。留空时，Open WebUI 使用 `eastus` |
| **语言区域** | 用户所使用的语言，以逗号分隔且不含空格，例如 `en-US,de-DE`。参见[语言区域](#language-locales) |
| **终结点 URL** | 留空，除非你使用资源自身的终结点（参见[终结点 URL](#endpoint-url)） |
| **最大说话人数** | 留空以使用默认值 `3` |

5. 点击 **Save**

该密钥只能配合创建资源时所在的区域使用。微软说明密钥按区域限定（region-scoped），因此将密钥搭配其他区域使用会导致认证失败。

## 语言区域 {#language-locales}

Azure 会根据 Open WebUI 随每段录音一起发送的区域列表来判断所使用的语言：

- 设置了**语言区域**时，Azure 会将这些区域作为候选项。微软说明，如果音频中不包含其中任何一种语言，服务会尝试自行识别语言。
- 留空时，Open WebUI 会发送以下列表：`en-US`、`es-ES`、`es-MX`、`fr-FR`、`hi-IN`、`it-IT`、`de-DE`、`en-GB`、`en-IN`、`ja-JP`、`ko-KR`、`pt-BR` 和 `zh-CN`。

Azure 只会为每段录音识别出一种主要语言。微软说明，更小且准确的候选区域集合可以提升识别效果，因此请仅列出用户实际使用的语言。有关 Azure 支持的区域，请参阅 [Language and voice support](https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=stt)。

区域之间只能用逗号分隔。Open WebUI 不会去除空格，因此 `en-US, de-DE` 会发送带前导空格的 `" de-DE"`。

用户在 **Settings** → **Audio** 下可设置的**语言**不会被该引擎使用。只有管理员的**语言区域**列表会被发送到 Azure。

## 终结点 URL {#endpoint-url}

默认情况下，Open WebUI 会根据 **Azure 区域**构建 `https://<region>.api.cognitive.microsoft.com` 并向其发送请求。**终结点 URL** 会替换该地址，Open WebUI 会在其后追加 `/speechtotext/transcriptions:transcribe?api-version=2024-11-15`。请仅填写协议和主机名，不要包含路径。

你可以使用 **Keys and Endpoint** 中资源自身的终结点，例如 `https://<resource-name>.cognitiveservices.azure.com`。微软的快速转录示例也是在该地址上调用同一路径。请去掉 Azure 显示的结尾 `/`，因为 Open WebUI 会直接追加路径，否则会造成斜杠重复。

## 最大说话人数 {#max-speakers}

Open WebUI 始终要求 Azure 分离说话人（diarization），**最大说话人数** 为上限。Open WebUI 保留的文本是合并后的转录结果，不含说话人标签。

## 环境变量配置 {#environment-variables-setup}

如果你更倾向于使用环境变量进行配置：

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - AUDIO_STT_ENGINE=azure
      - AUDIO_STT_AZURE_API_KEY=your-speech-resource-key
      - AUDIO_STT_AZURE_REGION=westeurope
      - AUDIO_STT_AZURE_LOCALES=en-US,de-DE
    # ... 其他配置
```

### 全部 Azure STT 环境变量 {#all-azure-stt-environment-variables}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_STT_ENGINE` | 设置为 `azure` | empty（使用本地 Whisper） |
| `AUDIO_STT_AZURE_API_KEY` | 你的 Speech 资源密钥 | empty |
| `AUDIO_STT_AZURE_REGION` | 你的 Speech 资源所在区域的标识符 | empty，即使用 `eastus` |
| `AUDIO_STT_AZURE_LOCALES` | 以逗号分隔的区域，不含空格 | empty，即发送上面列出的 13 个区域 |
| `AUDIO_STT_AZURE_BASE_URL` | 替换 `https://<region>.api.cognitive.microsoft.com` | empty |
| `AUDIO_STT_AZURE_MAX_SPEAKERS` | 说话人分离的上限 | empty，即使用 `3` |

:::info 在 UI 中保存的设置具有更高优先级
保存管理员**音频**设置会存储该标签页上的所有字段（包括留空字段），选择引擎同样会保存。在默认的 `ENABLE_PERSISTENT_CONFIG=true` 下，从此刻起这些存储的值将优先于 `AUDIO_*` 环境变量。请参阅 [`ENABLE_PERSISTENT_CONFIG`](/reference/env-configuration#enable_persistent_config)。
:::

## 长录音 {#long-recordings}

在转录之前，Open WebUI 会将不受支持格式的录音转换为 MP3。大于 20 MB 的音频会被重新编码为更小的 MP3，如果仍然过大，则会拆分为每份不超过 20 MB 的片段。每一份片段都会作为独立请求发送到 Azure，因此每份片段会单独检测语言，最后再将文本拼接起来。

精简镜像（即 `BYPASS_PYDUB_PREPROCESSING=true`）会跳过该步骤，直接发送完整文件。此时 Open WebUI 会拒绝超过 200 MB 的文件，而微软针对 Open WebUI 所用 API 版本（`2024-11-15`）的参考文档将音频时长限制在 2 小时以内。

## 使用 STT {#using-stt}

1. 点击聊天输入框中的**麦克风图标**
2. 说出你的消息
3. 说完后点击对勾（**确认录音**）
4. 你的语音会被转录并显示在消息框中；如果在你的**音频**设置中开启了 **Instant Auto-Send After Voice Transcription**，则会立即发送

## 故障排查 {#troubleshooting}

### “Azure API key and region are required for Azure STT”

未保存 API 密钥。请在 **API 密钥** 中填入你的 Speech 资源密钥（或设置 `AUDIO_STT_AZURE_API_KEY`）并保存。

### “External: Access denied due to invalid subscription key or wrong API endpoint”

Azure 拒绝了该密钥。请检查：

1. 密钥是否从 **Keys and Endpoint** 正确复制
2. **Azure 区域** 是否为你的 Speech 资源所在区域
3. 如果设置了**终结点 URL**，它是否为不含路径的资源终结点

### “External: Resource not found”

Azure 无法识别该地址。如果设置了**终结点 URL**，请确认主机名之后没有路径。

### 无法识别语言 {#language-could-not-be-identified}

当 Azure 无法识别语言，或识别出多种语言且没有主导语言时，Open WebUI 会显示 Azure 自身的错误消息。请将**语言区域**设置为你录音中实际使用的语言。

### 其他错误 {#other-errors}

当音频为空或过长时，Open WebUI 会显示 Azure 自身的消息，对于上述两种语言识别错误也是如此。Azure 转录错误格式中的其他错误会显示“An error occurred during transcription.”，同时 Azure 的错误代码和消息会写入服务器日志，所在行包含 `Azure STT error`。

还有一些消息来自 Open WebUI 自身：

- **以 “Failed to parse Azure response:” 开头的消息**：Azure 已响应，但没有返回任何转录文本。
- **以 “Error transcribing chunk:” 开头的消息**：请求根本没有到达 Azure，例如区域标识符拼写错误。

如果密钥和区域都正确但转录仍然失败，请确认你的区域是否提供快速转录功能。

更多排查信息请参阅[音频故障排查指南](/troubleshooting/audio)。

## 成本说明 {#cost-considerations}

Azure 会根据你的 Azure 订阅对 Speech 用量计费。当前费率请查看 [Azure 的 Speech 定价页面](https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/)。微软的[配额与限制](https://learn.microsoft.com/azure/ai-services/speech-service/speech-services-quotas-and-limits)仅列出了 Standard (S0) 层级的快速转录限制。

:::tip
如需免费的 STT，请使用 **Local Whisper**（默认）或浏览器的 **Web API** 进行基础转录。
:::
