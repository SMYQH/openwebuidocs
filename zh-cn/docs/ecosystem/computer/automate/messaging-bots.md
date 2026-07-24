---
title: 给你的电脑发消息（Telegram、Discord、Slack、WhatsApp、Signal）
sidebar_position: 2
---

# 给你的电脑发消息

连接一个机器人，你的电脑会在 Telegram、Discord、Slack、WhatsApp 或 Signal 中回复：同样的代理、同样的工作区、完整的工具访问权限。让它检查构建、推送修复或总结文件，从任何安装了聊天应用的手机上。Telegram、Discord、Slack 和 Signal 不需要隧道或公共 URL。

## 设置任意机器人

1. 打开**设置 → 管理 → 机器人**并创建一个机器人。
2. 选择平台并粘贴凭据（各平台说明见下文）。令牌会加密存储。
3. 点击**验证**以确认凭据有效。
4. 选择机器人启动时使用的工作区和模型。
5. 设置**允许发送者**：一个能收到回复的平台用户 ID 列表。
6. 启动机器人并给它发消息。

:::warning 设置允许发送者
空的允许发送者列表意味着任何找到机器人的人都可以使用它，而机器人消息会在你的机器上以完全工具审批模式运行代理。在启动机器人之前添加你自己的平台用户 ID，并将机器人保持在群组频道之外。
:::

## 命令

所有平台通用：

| 命令 | 作用 |
| --- | --- |
| `/new`（也支持 `/reset`） | 开始新的聊天 |
| `/stop` | 取消正在运行的任务 |
| `/retry` | 重新运行你的最后一条消息 |
| `/model [id]` | 显示或切换模型（持久化） |
| `/workspaces` | 列出可用的工作区 |
| `/workspace <name>` | 切换工作区（模糊匹配）并开始新的聊天 |
| `/help` | 列出命令 |

## 预期效果

- **流式传输**：机器人大约每 2 秒编辑一次其消息，显示进度：工具活动行加上当前的文本。最终答案作为持久消息到达，按平台的长度限制分块。（WhatsApp 和 Signal 不支持编辑；你只会收到最终答案。）
- **附件输入**：你发送的图片和文档会附加到聊天中。
- **语音笔记**：配置语音转文字后会进行转写和回答；参见[语音和音频](/ecosystem/computer/ai/voice-and-audio)。否则机器人会告诉你 STT 未设置。
- **排队**：任务运行时发送的消息会排队并按顺序处理。
- **同步**：每个机器人对话都是所选工作区中的真实聊天；它会出现在 Computer 侧边栏中，你可以在 Web UI 中继续。

## Telegram

1. 在 Telegram 上给 [@BotFather](https://t.me/BotFather) 发消息，发送 `/newbot`，命名并复制给出的令牌。
2. 将令牌粘贴为凭据，验证并启动。

Telegram 使用长轮询，因此你的 Computer 不需要公共 URL。你的发送者 ID 是你的数字 Telegram 用户 ID；从 @userinfobot 这样的机器人获取。在 Bot API 10.1+ 上，你可以获得丰富的草稿流式传输；旧版本回退到 4096 字符块中的纯文本消息。

## Discord

1. 在 Discord 开发者门户中，创建一个应用，打开**机器人**，并复制令牌。
2. 在同一机器人页面上，启用**消息内容**意图。
3. 将机器人邀请到你的服务器（使用 `bot` 范围的 OAuth2 URL 生成器）。
4. 将令牌粘贴为凭据。

Discord 通过 Gateway WebSocket 连接，因此不需要公共 URL。它需要 `websockets` Python 包，默认不会安装：

```bash
pip install websockets
```

消息分块到 2000 个字符。

## Slack

1. 创建一个 Slack 应用并将其安装到你的工作区以获取机器人令牌（`xoxb-...`）。
2. 启用**套接字模式**，这会给一个应用级令牌（`xapp-...`）。
3. 将两者以竖线分隔作为凭据输入：

```text
xoxb-your-bot-token|xapp-your-app-token
```

套接字模式意味着不需要公共 URL。与 Discord 一样，Slack 需要在主机上安装 `pip install websockets`。消息分块到 4000 个字符。

## WhatsApp

使用 Meta Cloud API。从你的 Meta 应用获取访问令牌和电话号码 ID，并以竖线分隔输入：

```text
access_token|phone_number_id
```

入站消息仅通过 webhook 到达，因此你的 Computer 必须可公开访问（在暴露之前请参见[安全](/ecosystem/computer/phone-and-remote/security)）。在 Meta 应用中将 webhook URL 配置为：

```text
https://<your-host>/api/webhooks/whatsapp/<bot_id>
```

Webhook 验证目前接受任何验证令牌。WhatsApp 不支持消息编辑，因此没有流式传输；你会收到最终答案。

## Signal

需要一个在 Computer 旁边运行的 signal-cli REST API 桥接：

```bash
docker run -p 8080:8080 bbernhard/signal-cli-rest-api
```

使用桥接注册你的 Signal 号码，然后将桥接 URL 和号码以竖线分隔作为凭据输入：

```text
http://localhost:8080|+15551234567
```

机器人每 2 秒轮询桥接一次。不支持消息编辑，因此没有流式传输。
