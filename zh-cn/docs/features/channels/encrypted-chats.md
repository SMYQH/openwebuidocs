---
sidebar_position: 4
title: "加密聊天"
---

# 加密聊天 {#encrypted-chats}

加密聊天是在[私信](/features/channels#direct-messages)或私有群组频道中进行的、临时的端到端加密会话。消息在每位参与者的浏览器中加密与解密。Open WebUI 服务器只在参与者之间转发加密数据包，不存储任何消息。加密聊天中的内容不会被保存、无法被搜索，也不会出现在频道的常规历史记录中。

加密采用 MLS 协议（Messaging Layer Security），通过编译为 WebAssembly 并在浏览器中运行的 openmls 库实现。

:::warning 有意设计为临时
加密聊天只在参与者身处其中时存在。离开或重新加载页面会清除该设备上的聊天，而且无法找回消息。当发起者离开时，这个聊天对所有人都会结束。
:::

---

## 使用加密聊天 {#using-encrypted-chats}

### 发起加密聊天 {#start-an-encrypted-chat}

1. 打开一个私信或私有群组频道。
2. 在侧边栏或顶部栏中打开该会话的 **...** 菜单。
3. 点击 **Encrypted Chat**。

加密聊天会在独立页面中打开，并标记为 **Encrypted**。你是它的主持人。每个会话同一时间最多只能有一个加密聊天。

### 加入加密聊天 {#join-an-encrypted-chat}

加密聊天进行期间，其他成员会在会话名称下方看到 **Encrypted chat in progress · Join**。点击 **Join** 即可进入。主持人的浏览器会把你加入加密群组，你从此刻起就能看到发送的消息。一个加密聊天最多容纳 128 名参与者，且每人同一时间只能从一个标签页或设备参与。

### 消息 {#messages}

- 一条消息最多容纳 16 KiB 文本。更长的消息会显示 **Message exceeds the 16 KiB limit.**，并且不会被发送。
- 一旦其他所有参与者都收到了你的消息，将鼠标悬停到该消息上或让它获得焦点时，下方就会显示 **Delivered**。
- 正在输入提示会显示是谁在打字。
- 每台设备最多保留当前聊天最近 500 条消息，更早的会被丢弃。

### 核验参与者 {#verify-participants}

每位参与者都有一个由其加密密钥生成的校验码。打开 **Participants**（顶栏中的参与者数量），点击某位参与者即可看到其校验码。通过另一个渠道与此人核对，例如当面或通话。校验码一致时，点击 **Codes match**，该参与者就会显示为 **Verified**。核验结果仅在你的设备上为当前聊天保留。

同一面板中的 **Refresh encryption keys** 会为你的设备在群组中获取新的加密密钥。在一场长时间的聊天中途需要更换密钥时可以使用它。

### 聊天何时结束 {#when-a-chat-ends}

在以下情况下会出现 **Encrypted chat ended**，且消息会从你的屏幕上消失：

- 你点击 **Leave**、重新加载页面、关闭标签页或失去连接；
- 主持人离开；
- 某位成员被移出频道、频道被编辑或删除，或某个私信被通过 **Hide conversation** 隐藏；
- 某位参与者失去访问权限，例如因角色或权限变更；或
- 服务器无法协调该会话。

浏览器约 45 秒无响应的参与者会被移出聊天。向频道添加新成员不会让聊天中断；新成员可以加入其中。

---

## 设置加密聊天 {#setting-up-encrypted-chats}

### 启用加密聊天 {#enable-encrypted-chats}

1. 前往 **Settings > Admin > General**。
2. 打开 **Channels**。其下方会出现 **Encrypted channels** 开关。
3. 打开 **Encrypted channels** 并保存。

同一个开关也可以通过 [`ENABLE_ENCRYPTED_CHANNELS`](/reference/env-configuration#enable_encrypted_channels) 设置。它默认关闭。

### 谁可以使用 {#who-can-use-it}

管理员始终可以发起和加入加密聊天。普通用户则需要同时拥有 **Channels** 与 **Encrypted Channels** 权限（[`USER_PERMISSIONS_FEATURES_CHANNELS`](/reference/env-configuration#user_permissions_features_channels) 与 [`USER_PERMISSIONS_FEATURES_ENCRYPTED_CHANNELS`](/reference/env-configuration#user_permissions_features_encrypted_channels)）。**Encrypted Channels** 默认关闭；你可以在默认权限中授予，也可以按[群组](/features/authentication-access/rbac/groups)授予。参见[权限](/features/authentication-access/rbac/permissions#4-features-permissions)。

加密聊天仅在私信和私有群组频道中可用，且仅对该会话的成员开放。

### 环境要求 {#requirements}

除非以下条件全部满足，否则 Open WebUI 会拒绝发起或加入加密聊天：

| 要求 | 设置 |
|-------------|---------|
| 浏览器通过 websocket 连接。HTTP 长轮询会被拒绝。 | [`ENABLE_WEBSOCKET_SUPPORT`](/reference/env-configuration#enable_websocket_support) 已开启（默认），且反向代理会转发 websocket 升级请求 |
| websocket 服务端日志已关闭，因此数据包不会进入日志 | [`WEBSOCKET_SERVER_LOGGING`](/reference/env-configuration#websocket_server_logging) 与 [`WEBSOCKET_SERVER_ENGINEIO_LOGGING`](/reference/env-configuration#websocket_server_engineio_logging) 已关闭（默认） |
| 当 [`ENV`](/reference/env-configuration#env) 为 `prod`（Docker 默认值）时使用 HTTPS | 通过 HTTPS 提供 Open WebUI 服务。若位于终止 TLS 的反向代理之后，代理必须发送 `X-Forwarded-Proto`，且 [`FORWARDED_ALLOW_IPS`](/reference/env-configuration#forwarded_allow_ips) 必须信任它 |

浏览器还需要一个安全上下文：HTTPS，或本地测试时的 `localhost`。

缺少任何一项要求时，加密聊天在打开后就会立即结束。

### 多实例 {#multiple-instances}

当多个工作进程或实例共享 Redis（`WEBSOCKET_MANAGER=redis`）时，会话元数据（谁在哪个聊天中及其公钥）通过 Redis 协调。每条记录在最后一次活动之后 90 秒过期。加密数据包在实例之间通过 Redis Pub/Sub 传输，且绝不会存放在其中。参见[扩展 Open WebUI](/getting-started/advanced-topics/scaling)。

### 速率限制 {#rate-limits}

每位用户每分钟最多发起或加入 10 个加密聊天。其他所有加密聊天流量（消息、正在输入提示、回执与保活）限制为每位用户每秒 100 个请求和 4 MiB。有 Redis 时这些限制在所有实例之间生效；没有 Redis 时则按工作进程计算。
