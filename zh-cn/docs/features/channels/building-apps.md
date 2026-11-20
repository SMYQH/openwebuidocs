---
sidebar_position: 3
title: "构建应用"
---

# 构建 App {#building-apps}

App 是 Open WebUI 会主动连接的一个服务器。管理员负责安装它；管理员和频道创建者负责把它添加到频道中，详见 [Apps](/features/channels/apps)。

## 使用 oix 快速上手 {#quick-start-with-oix}

构建 App 最快的方式是使用 [oix](https://github.com/open-webui/oix#readme)——Python SDK（需要 Python 3.11 或更高版本）。它实现了本页描述的协议，因此你的代码只需处理事件：

```bash
python -m pip install oix
```

嵌入卡片与链接按钮需要 oix 0.7.0 或更高版本。提及功能需要 oix 0.8.0 或更高版本。

```python
from oix import App

app = App(
    manifest_id="hello",
    name="Hello",
    scopes=["channels:messages:read", "channels:messages:write"],
)


@app.on("channel.message.created")
async def hello(event):
    if event.content == "hello":
        await event.reply("Hello!")


if __name__ == "__main__":
    app.run()
```

把它保存为 `app.py`。该 App 从 `API_KEY` 读取自己的 API key，从 `APP_PRIVATE_KEY_FILE` 指定的文件读取私钥；oix 的 README 中有一个脚本可一次性把两者写入 `.env`。用 `. ./.env && python app.py` 启动该 App。它在 `8000` 端口的 `/events` 路径上监听。请通过支持 WebSocket 升级的 HTTPS 提供该服务，其 App URL 例如 `https://hello.example.com/events`。用该 URL 和 API key [安装它](/features/channels/apps#install-an-app)，把它添加到一个频道，然后发送 `hello`。

若要对着本地的 Open WebUI 测试，请同时遵循 oix 的[本地开发](https://github.com/open-webui/oix#local-development)步骤与[私有与纯 HTTP 的 App 服务器](/features/channels/apps#private-and-plain-http-app-servers)。

使用其他语言编写的 App 可直接实现下面的协议。

## App 需要提供什么 {#what-an-app-provides}

1. App URL 上可选的 **manifest**（清单）。
2. 位于 App URL 路径之下的 **Socket.IO 服务器**，使用 `/apps` 命名空间。
3. 一对 **Ed25519 密钥**，例如 `openssl genpkey -algorithm ED25519 > app-private-key.pem`，公钥可通过 `openssl pkey -in app-private-key.pem -pubout` 取得。公钥放在 manifest 中；私钥用于签署连接证明。
4. 一个 **API key**：由你创建的随机机密，例如用 `openssl rand -hex 32` 生成，并交给管理员。Open WebUI 会在 manifest 请求和 Socket.IO 握手中以 `Authorization: Bearer <API key>` 的形式发送它。没有该密钥的请求应予拒绝。

## Manifest（清单） {#manifest}

Open WebUI 会携带 API key 发送 `GET <App URL>`。请在 10 秒内以 HTTP 200 和一个不超过 256 KiB 的 JSON 对象作答：

```json
{
  "id": "hello",
  "name": "Hello",
  "description": "Says hello.",
  "profile_image_url": "https://example.com/hello.png",
  "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n",
  "requested_scopes": ["channels:mentions:read", "channels:messages:write"]
}
```

| 字段 | 规则 |
|-------|-------|
| `id` | 必填，1 到 100 个字符。用于标识该 App，App 安装后此 ID 必须保持不变。 |
| `name` | 必填，1 到 100 个字符。 |
| `description` | 可选，最多 2,000 个字符。 |
| `profile_image_url` | 可选。一个不超过 2,048 个字符且不含凭据的 `http(s)` URL，或一个 base64 的 `data:image/png`、`jpeg`、`gif` 或 `webp` URL。总计最多 192 KiB。用户浏览器会直接加载它。 |
| `public_key` | 必填。PEM 格式的 Ed25519 公钥（`-----BEGIN PUBLIC KEY-----`）。Open WebUI 会在安装时将其固定。 |
| `requested_scopes` | 必填。[scope](/features/channels/apps#scopes)列表。 |

出现未知字段会使该 manifest 无效。

## 连接 {#connection}

对于形如 `https://app.example.com/events` 的 App URL，Open WebUI 会以 Socket.IO 客户端的身份连接到 `https://app.example.com`，使用 Socket.IO 路径 `/events/socket.io`、仅 WebSocket 传输、命名空间 `/apps` 以及 `Authorization: Bearer <API key>` 请求头。若该 App 位于反向代理之后，代理必须在 Socket.IO 路径上转发 WebSocket 升级请求。随后握手通过带确认的 Socket.IO 事件进行：

1. Open WebUI 发出 `app:connect`，其中包含：

   ```json
   { "app_id": "<id Open WebUI assigned>", "challenge": "<random UUID>", "connection_token": null }
   ```

   当 Open WebUI 手上没有令牌时，`connection_token` 为 `null`：首次连接时、管理员填入新 API key 之后、该 App 的公钥变化之后，以及卸载之后。除此之外，它是该 App 在管理员上次点击 **Connect** 时返回的令牌。

2. 应用会返回如下确认信息：

   ```json
   { "status": 200, "data": { "installation_id": "<UUID>", "connection_token": "<string>", "proof": "<JWT>" } }
   ```

   由应用自行选择 `installation_id`（在该次安装中保持不变的 UUID）和 `connection_token`（最长 8,192 个字符）。管理员点击 **Connect** 时，Open WebUI 会加密保存该令牌，并在每次重连时发送它。自动重连时会继续使用已保存的令牌，忽略应用返回的令牌，因此应用必须继续接受先前签发的令牌。

   **App** 使用其 **Ed25519 私钥**签署 `proof`（JWT 算法 `EdDSA`，头部 `typ` 为 `oix-connect+jwt`）。Open WebUI 使用 manifest 中固定的公钥进行验证。必需的声明包括：

   | 声明 | 取值 |
   |-------|-------|
   | `aud` | `oix:connect` |
   | `sub` | 该 `installation_id` |
   | `app_id` | `app:connect` 中的 `app_id` |
   | `manifest_id` | manifest 中的 `id` |
   | `challenge` | `app:connect` 中的 `challenge` |
   | `token_hash` | 本次确认中 `connection_token` 的 SHA-256 十六进制摘要 |
   | `iat`、`exp` | 整数，`exp` 至多比 `iat` 晚 60 秒 |

   只要 Open WebUI 持有令牌，`installation_id` 就必须保持不变。当它发送 `null` 时，该 App 可以用新的 `installation_id` 作答。

3. Open WebUI 发出 `app:ready`，内容为 `{}`。该 App 必须以 `{"status": 200, "data": {"received": true}}` 精确确认。

连接至此建立。Open WebUI 用 API key 证明自己的身份；该 App 则用签名后的证明证明自己的身份。每个 Open WebUI 工作进程都会各自建立连接，因此该 App 必须接受同一次安装的多个连接。

整个连接过程必须在 20 秒内完成，每次确认必须在 10 秒内完成。在 Open WebUI 验证证明之前，每个 `app:request` 都会失败并提示 `App connection is not ready`。从验证通过到该 App 确认 `app:ready` 之间，只有 `ping` 可用。

## 事件 {#events}

Open WebUI 发出 `app:event` 并等待确认。每个事件都携带 `type`、`app_id`（Open WebUI 为该 App 分配的 id）和 `installation_id`。

**交互**事件为 `channel.mention` 与 `channel.action`：

```json
{
  "id": "<operation id>",
  "type": "channel.mention",
  "actor": { "id": "<user id>", "name": "Ada", "is_admin": false },
  "channel": { "id": "<channel id>" },
  "data": { "text": "<@A:<app_id>|Hello> hi", "message_id": "<id>", "parent_id": null },
  "execution_token": "<token>",
  "source": null,
  "app_id": "<app id>",
  "installation_id": "<installation id>"
}
```

- `channel.mention`：有用户提及了该 App。`data.text` 是原始消息，其中的提及形如 `<@A:<app_id>|<name>>`。如果用户在线程中提及 App，`data.parent_id` 就是该线程的根消息。需要 `channels:mentions:read` 或 `channels:messages:read`。请在 **10 秒**内以 `{"status": 200, "data": {"received": true}}` 精确确认。这只确认已投递。之后再用 `create_message` 操作发布回答，该操作需要 `channels:messages:write`；把 `data.message_id` 作为 `reply_to_id`、`data.parent_id` 作为 `parent_id`，即可在原处回复该提及。
- `channel.action`：有用户点击了某个按钮。`data` 包含 `message_id`、`etag`、`parent_id`、`action_id` 以及该按钮的 `context`；`source` 包含该消息的 `id` 和 `updated_at`。请在 **3 秒**内以[回复](#replying-to-interactions)作答。

**消息事件**会发送给拥有 `channels:messages:read` 的 App，涵盖它们所加入频道中的每一条消息（包括该 App 自己发的消息）：`channel.message.created`、`channel.message.updated` 和 `channel.message.deleted`。请在 10 秒内以 2xx 的 `status` 确认。

```json
{
  "id": "<event id>",
  "type": "channel.message.created",
  "channel": { "id": "<channel id>" },
  "message": {
    "id": "<id>", "channel_id": "<id>", "author": { "type": "user", "id": "<id>" },
    "content": "...", "parent_id": null, "reply_to_id": null, "files": [], "actions": [], "embeds": [],
    "created_at": "<ns>", "updated_at": "<ns>", "etag": "<ns>"
  },
  "event_token": "<token>",
  "app_id": "<app id>",
  "installation_id": "<installation id>"
}
```

`author.type` 取值为 `user`、`model`、`webhook` 或 `app`。`model` 与 `webhook` 沿用消息上存储的标签，且只有 Open WebUI 会设置它：通过频道 webhook 发布的消息为 `webhook`，模型的回复为 `model`。随发布或编辑消息的请求一同发送的标签会被忽略。`model` 消息的正文仍可由通过提及模型触发这条回复的成员和管理员编辑，`webhook` 消息的正文则可由创建该 webhook 的账户编辑。对于模型的回复，只有在回复完成后才会发送 `channel.message.updated`。消息删除事件只携带 `id`、`channel_id`、`parent_id`、`author` 和 `updated_at`。消息事件属于尽力而为：每个事件只发送一次，失败的事件或在该 App 断开期间发生的事件都会被丢弃。

对拥有 `channels:messages:read` 的 App 而言，一次提及会到达两次：一次是 `channel.mention`，另一次是 `channel.message.created`。请在两个处理器中的任意一个中作答。

`execution_token` 与 `event_token` 都由 Open WebUI 签名。该 App 通过下文中的 `authorize` 或 `verify_event` 操作把它们发回以进行校验。`execution_token` 有效期为 24 小时，`event_token` 为 5 分钟。当该 App 的 API key 或公钥变化时，两者都会失效。

## 回复交互 {#replying-to-interactions}

对按钮点击（`channel.action`）的确认应使用 `{"status": 200, "data": <reply>}`，最多 256 KiB：

```json
{
  "status": 200,
  "data": {
    "type": "message",
    "visibility": "channel",
    "content": "Ready to publish?",
    "actions": [{ "action_id": "publish", "label": "Publish", "context": { "draft": 42 } }]
  }
}
```

| 字段 | 含义 |
|-------|---------|
| `type` | `message`（默认）、`update`、`ack`、`download` 或 `error`。 |
| `visibility` | `private`（默认，仅点击者可见）或 `channel`。 |
| `content` | Markdown，最多 32,000 个字符。 |
| `title` | 私有回复的可选标题，最多 200 个字符。 |
| `actions` | 最多 30 个按钮。每个按钮都有一个 `label`（最多 200 个字符），以及以下二者之一：要么是 `action_id`（最多 100 个字符）加可选的 `context` 对象（会在 `channel.action` 中回传），要么是一个 `url`：不超过 2,048 个字符、不含凭据的 `http(s)` 链接，在新标签页中打开。只允许出现在 `visibility` 为 `channel` 的 `message` 或 `update` 上。 |
| `embeds` | 最多 10 张卡片，用于 `message` 或 `update`。每张卡片可含 `title`（最多 256 个字符）、`description`（Markdown，最多 4,096）、`url`（链接标题）、`color`（从 `0` 到 `0xFFFFFF` 的整数，用作强调条颜色）、`author`（`{"name": ...}`，最多 256）、`footer`（`{"text": ...}`，最多 2,048）、`thumbnail`（`{"url": ...}`）以及最多 25 个 `fields`（`name` 最多 256，`value` 为 Markdown，最多 1,024，`inline` 可选）。一条消息中的所有卡片合计最多容纳 6,000 个字符的文本。URL 为不含凭据的 `http(s)`，最多 2,048 个字符。缩略图由用户浏览器直接加载。 |
| `parent_id`、`reply_to_id` | 将回复发到线程，或设为对某条消息的回复。未指定 `parent_id` 的频道回复会发到频道的主时间线。 |
| `filename` | 用于 `download`：字母、数字、`_`、`.` 和 `-`，以 `.md` 结尾。默认 `report.md`。 |

- `visibility` 为 `channel` 的 `message` 会发布一条频道消息，需要 `channels:messages:write`。
- `update` 会替换被点击按钮所属那条消息的内容、按钮和卡片，需要 `channels:messages:write`。请把 `visibility` 设为 `channel`：若保持默认的 `private`，按钮会被拒绝，用户还会额外收到一份内容的私有副本。
- `download` 会把 `content` 以 Markdown 文件的形式交给用户。
- `error` 会把 `content` 展示给用户；当 `content` 为空时显示 `The app could not complete this operation.`。
- 请以 `visibility` 为 `private`（默认）发送 `download`；若为 `channel`，它不会在任何地方显示。`error` 无论采用哪种 visibility，都只显示给点击者本人。
- `ack` 不显示任何内容。请以 `{"type": "ack"}` 发送。

出现未知字段会使该回复无效。

若要拒绝一次提及或一次按钮点击，请以错误 `status` 和一个 `error` 字符串确认，例如 `{"status": 403, "error": "Only the on-call team can run this."}`。Open WebUI 最多展示该字符串的前 2,000 个字符；若没有提供，则显示一段与状态码对应的说明。提及之后，Open WebUI 会以该 App 的名义把这条消息作为以 `App error:` 开头的回复发布到频道中，因此频道中的所有人都能看到它。若该 App 无法在那里发言，则只有提及它的那位用户能看到。按钮点击之后，则只有点击者本人能看到。[故障排查](/features/channels/apps#troubleshooting)列出了管理员和用户会看到的各类信息。

## 调用 Open WebUI {#calling-open-webui}

该 App 在同一条连接上发出 `app:request`，格式为 `{"operation": "<name>", "arguments": {...}}`。确认格式为 `{"status": 200, "data": ...}` 或 `{"status": <code>, "error": "<message>"}`。每个请求必须在 10 秒内完成。请求只在该 App 作为成员的频道中生效。

| 操作 | 参数 | Scope | 返回值 |
|-----------|-----------|-------|---------|
| `ping` | `{}` | 无 | `{"received": true}` |
| `get_me` | 无 | 无 | 该 App 的记录 |
| `list_channels` | 无 | `channels:read` | 已加入的频道：`id`、`name`、`type`、`is_private` |
| `list_messages` | `channel_id`，可选的 `parent_id`、`before`、`limit`（1 到 100，默认 50） | `channels:messages:read` | 按最新优先排列的 `messages` 以及 `next_cursor` |
| `create_message` | `channel_id`，可选的 `content`、`actions`、`embeds`、`parent_id`、`reply_to_id` | `channels:messages:write` | 新消息，含其 `etag` |
| `update_message` | `message_id`、`etag`，可选的 `content`、`actions`、`embeds` | `channels:messages:write` | 更新后的消息 |
| `authorize` | `token`：一个 `execution_token` | 该交互的 scope | `authorized`、`operation_id`、`actor`、`channel_id`、`type`、`data` |
| `verify_event` | `token`：一个 `event_token` | `channels:messages:read` | 校验通过的事件 |

`update_message` 只能编辑该 App 自己的消息。`content`、`actions` 和 `embeds` 会替换旧值，因此未提供的项会被清空。如果自读取 `etag` 以来消息发生了变化，该请求会以状态码 412（`Message changed`）失败。

## 长时间运行的工作 {#long-running-work}

提及只需送达回执，因此该 App 可以随后再干活，并用 `create_message` 发布结果。而按钮点击必须在 3 秒内作答。对于更慢的工作：

1. 立即回复 `{"type": "ack"}`。用户看不到任何东西。
2. 干活。
3. 可选用该事件的 `execution_token`（有效期 24 小时）调用 `authorize`，确认该用户仍能使用这个 App 并读取该频道。
4. 用 `create_message` 操作发布结果，并使用事件中的 `data.parent_id` 以留在该主题内。这需要 `channels:messages:write`，结果是一条频道消息，频道中的所有人都能看到。私有回复只能作为对按钮点击的直接应答。

## 限制 {#limits}

| 限制 | 取值 |
|-------|-------|
| Socket.IO 数据包 | 16 MiB，仅限 JSON 文本。二进制数据包会被拒绝。 |
| 发给该 App 的事件 | 1 MiB |
| 对事件的回复 | 256 KiB |
| Manifest 响应 | 256 KiB，10 秒内 |
| 消息内容 | 32,000 个字符，最多 30 个按钮和 10 张卡片（卡片文本合计 6,000 个字符） |
| 连接与握手 | 总计 20 秒，每次确认 10 秒 |
| 提及回执时间 | 10 秒 |
| 按钮点击应答时间 | 3 秒 |
| 消息事件应答时间 | 10 秒 |
| `app:request` 处理 | 10 秒 |
| `execution_token` 有效期 | 24 小时 |
| `event_token` 有效期 | 5 分钟 |
