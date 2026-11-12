---
sidebar_position: 2
title: "Azure AI Speech TTS"
---

# 使用 Azure AI Speech 实现文本转语音 {#using-azure-ai-speech-for-text-to-speech}

本指南介绍如何在 Open WebUI 中使用 Azure AI Speech 实现文本转语音。Open WebUI 会把文本发送到 Azure 的[文本转语音 REST API](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech)，并播放返回的音频。

:::tip 在找语音转文字（STT）？
请参阅配套指南：[使用 Azure AI Speech 实现语音转文字](/features/chat-conversations/audio/speech-to-text/azure-stt-integration)
:::

## 环境要求 {#requirements}

- 一个 Azure Speech 资源（微软文档中也称其为 Speech 的 Foundry 资源）。各区域对文本转语音的支持情况参见微软的 [Speech 服务区域表](https://learn.microsoft.com/azure/ai-services/speech-service/regions?tabs=tts)。
- 该资源的密钥，可在 Azure 门户的 **Resource Management** > **Keys and Endpoint** 中获取。两个密钥任选其一即可。
- 已安装并运行 Open WebUI

## 快速配置（界面） {#quick-setup-ui}

1. 点击你的**个人资料图标**（左下角）
2. 选择 **Admin Panel**，然后选择 **Settings**。设置会在一个窗口中打开。
3. 在侧边栏中，从 **Admin** 下的 *Tools* 组选择 **Audio**。另一个位于 *Preferences* 组的 **Audio** 条目保存的是你的个人音频设置。在窄屏上这些标签会被隐藏，可直接访问 `/?settings=admin:audio` 打开管理员的那个。
4. 按下列方式配置：

| 设置项 | 值 |
|---------|-------|
| **Text-to-Speech Engine** | `Azure AI Speech` |
| **API Key** | 你的 Speech 资源密钥 |
| **Azure Region** | 你的 Speech 资源所在区域，以 `westus` 或 `westeurope` 之类的标识符表示 |
| **Endpoint URL** | 留空，除非你使用主权云（参见 [Endpoint URL](#endpoint-url)） |

5. 点击 **Save**。选择引擎本身就会保存，并清空 **TTS Voice**，这也是为什么语音的设置放在这一步之后。
6. 切换到另一个设置标签页，再切回 **Audio**。语音列表是在 Audio 标签页打开时获取的，因此只有做完这一步才会带上你的密钥加载。
7. 配置语音与格式：

| 设置项 | 值 |
|---------|-------|
| **TTS Voice** | 输入语音名称或语言的一部分进行搜索，然后选择一个语音，例如 `en-US-JennyNeural` |
| **Output format** | 保持默认值 `audio-24khz-160kbitrate-mono-mp3`（参见 [Output Format](#output-format)） |

8. 点击 **Save**

该密钥只能在创建资源时所在的区域中使用。微软指出密钥是按区域划分的，因此用其他区域使用该密钥会导致认证失败。

:::caution 请务必设置区域
如果 **Azure Region** 和 **Endpoint URL** 都留空，语音请求仍会发往 `eastus`，但语音列表完全不会加载。请设置你的资源所在的区域。
:::

## 选择语音 {#choosing-voices}

Open WebUI 会从 Azure 加载你所在区域的语音列表。**TTS Voice** 中的每一行显示语音的完整名称，例如 `en-US-JennyNeural`，旁边以灰色显示其展示标签。列表一次只显示几行，因此请输入名称的一部分或一种语言（例如 `en-GB`）来缩小范围。

Open WebUI 发送给 Azure 的是完整名称，并从名称的前两段中取出语音语言（`en-US-JennyNeural` 对应 `en-US`）。如果你手动输入而不是从列表中选择，请使用完整名称。

回复使用哪个语音：

1. 模型自身的 **TTS Voice**（如果在 **Workspace** → **Models** 中编辑模型时设置过）
2. 否则，是用户在个人 **Audio** 设置中通过 **Set Voice** 选择的语音，前提是管理员的 **TTS Voice** 仍与他们选择时相同。如果管理员修改了它，用户会听到新的默认值，直到他们重新选择。
3. 否则，就是管理员的 **TTS Voice**

完整的语音与语言列表请参见微软的[语言与语音支持](https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts)。

## Endpoint URL {#endpoint-url}

默认情况下，Open WebUI 会根据 **Azure Region** 把请求发往 `https://<region>.tts.speech.microsoft.com`。**Endpoint URL** 用于替换该地址。Open WebUI 会在其后追加 `/cognitiveservices/v1` 来请求语音、追加 `/cognitiveservices/voices/list` 来加载语音列表，因此只需填写协议和主机，不要带路径。

这并不是你在 **Keys and Endpoint** 中看到的资源端点（[STT 指南](/features/chat-conversations/audio/speech-to-text/azure-stt-integration#endpoint-url)可以使用那个地址）。微软文档中语音列表位于该地址的 `/tts/cognitiveservices/voices/list`，而 Open WebUI 请求的是 `/cognitiveservices/voices/list`，因此语音列表不会加载。

对于主权云，微软文档给出了下列地址，其中 `<region>` 替换为你的区域标识符：

| 云 | Endpoint URL |
|-------|--------------|
| Azure Government | `https://<region>.tts.speech.azure.us` |
| 由 21Vianet 运营的 Azure | `https://<region>.tts.speech.azure.cn` |

区域标识符参见[主权云中的 Speech 服务](https://learn.microsoft.com/azure/ai-services/speech-service/sovereign-clouds)。

## Output Format {#output-format}

**Output format** 会作为要返回的音频格式发送给 Azure。请保持使用 MP3 格式之一，例如默认的 `audio-24khz-160kbitrate-mono-mp3`。Open WebUI 会把收到的音频保存为 `.mp3` 文件，并且除 slim 镜像外，无论 Azure 返回何种格式都以 MP3 提供。slim 镜像会拒绝其浏览器可播放格式列表之外的音频类型，例如 MP3、WAV 和 Ogg 之外的类型。微软的[音频输出列表](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)列出了所有可用值。

## 通过环境变量配置 {#environment-variables-setup}

如果你更愿意通过环境变量来配置：

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - AUDIO_TTS_ENGINE=azure
      - AUDIO_TTS_API_KEY=your-speech-resource-key
      - AUDIO_TTS_AZURE_SPEECH_REGION=westeurope
      - AUDIO_TTS_VOICE=en-US-JennyNeural
    # ... other configuration
```

把 `AUDIO_TTS_VOICE` 设为一个 Azure 语音名称。其默认值 `alloy` 是 OpenAI 的语音。

### 全部 Azure TTS 环境变量 {#all-azure-tts-environment-variables}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `AUDIO_TTS_ENGINE` | 设为 `azure` | 空（使用浏览器内置 TTS） |
| `AUDIO_TTS_API_KEY` | 你的 Speech 资源密钥（与 ElevenLabs 引擎共用） | 空 |
| `AUDIO_TTS_AZURE_SPEECH_REGION` | 你的 Speech 资源所在区域标识符 | 空（语音使用 `eastus`；没有基础 URL 时语音列表不会加载） |
| `AUDIO_TTS_AZURE_SPEECH_BASE_URL` | 替换 `https://<region>.tts.speech.microsoft.com` | 空 |
| `AUDIO_TTS_AZURE_SPEECH_OUTPUT_FORMAT` | 音频输出格式 | `audio-24khz-160kbitrate-mono-mp3` |
| `AUDIO_TTS_VOICE` | 完整的 Azure 语音名称 | `alloy`（不是 Azure 语音） |

:::info 在界面中保存的设置优先
保存管理员的 **Audio** 设置会存储该标签页上的每一个字段（包括留空的字段），选择引擎同样也会保存。在默认的 `ENABLE_PERSISTENT_CONFIG=true` 下，这些已存储的值此后优先于 `AUDIO_*` 环境变量。参见 [`ENABLE_PERSISTENT_CONFIG`](/reference/env-configuration#enable_persistent_config)。
:::

## 测试 TTS {#testing-tts}

1. 开启一个新的聊天
2. 向任意模型发送一条消息
3. 点击 AI 回复上的**扬声器图标**收听朗读效果

## 故障排查 {#troubleshooting}

### 列表中没有语音 {#no-voices-shown-in-the-list}

1. 确认 **API Key** 与 **Azure Region** 已设置并保存
2. 切换到另一个设置标签页再切回 **Audio**，以重新加载列表
3. 在 Open WebUI 日志中查找 `Error fetching Azure voices`

### 语音请求返回 401 错误 {#speech-fails-with-a-401-error}

Azure 拒绝了该密钥。请确认密钥是从 **Keys and Endpoint** 中正确复制的，并且 **Azure Region** 正是你的 Speech 资源所在区域。

### 语音请求返回其他错误 {#speech-fails-with-another-error}

1. 确认 **TTS Voice** 已设置为列表中的完整 Azure 语音名称
2. 确认 **Output format** 是微软[音频输出列表](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)中的某个 MP3 取值
3. 在 Open WebUI 日志中查看完整错误信息

有关更全面的音频调试，请参阅[音频故障排查指南](/troubleshooting/audio)。

## 成本考量 {#cost-considerations}

Azure 会按你的 Azure 订阅对 Speech 用量计费。当前费率请查阅 [Azure Speech 定价页](https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/)。
