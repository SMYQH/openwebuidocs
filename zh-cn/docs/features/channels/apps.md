---
sidebar_position: 2
title: "应用"
---

# 应用 {#apps}

App 是以成员身份加入[频道](/features/channels)的外部服务。提及某个 App，它就会在频道中作答。App 可以发布带有卡片和按钮的消息、私下回复你的按钮点击、更新自己的消息，并且在管理员允许时关注它们所属频道中的每一条消息。

App 运行在它自己的服务器上。由 Open WebUI 主动向 App 建立连接，因此 Open WebUI 本身可以留在私有网络中，无需公开的回调地址。若只是想往频道里发消息而不回复任何人，[频道 webhook](/features/administration/webhooks#3-channel-webhooks-external-message-integration) 会更简单。

:::info
App 属于实验性功能。**Settings > Admin > Apps** 会显示 **Experimental** 徽标。
:::

---

## 在频道中使用 App {#using-apps-in-a-channel}

### 把 App 添加到频道 {#add-an-app-to-a-channel}

1. 打开该频道，点击顶栏中人物图标旁的人数。
2. 点击 **Add Member**。
3. 在 **Apps** 下选择该 App 并点击 **Add**。

该 App 现在会带着 **App** 徽标出现在成员列表中。要再次移除它，请使用同一列表中它旁边的移除按钮。

只有频道创建者和管理员才能添加、移除 App。添加 App 还需要你拥有它的访问权限，并且该 App 必须处于启用状态。你只会看到自己有权使用的 App。App 加入标准频道和群组频道；私信仍然只在人与人之间进行。

被授予 **Read messages and history in joined channels** 的 App 会收到该频道中发布的每一条消息，并能读取其历史记录。把 App 添加到含敏感内容的频道之前，请先向管理员确认它拥有哪些 scope。

### 提及某个 App {#mention-an-app}

在 App 作为成员的频道中键入 `@`，并从建议列表的 **Apps** 分组中选中它。你也可以键入 `@` 加上该 App 的全名，参见[标记人员与链接频道](/features/channels#tagging-people-and-linking-channels)。发送消息后，App 就会收到它。一条消息最多只会送达它所提及的前 10 个 App。App 会确认已收到消息，并在准备好后把回答发布到频道中。

### 私有回复与频道回复 {#private-and-channel-replies}

App 对提及的回应是一条频道消息。而对按钮点击的回应可以是以下两种之一：

- **私有回复**出现在你点击了按钮的那条 App 消息下方，标注为 **Only visible to you**，并带有一个 **Dismiss** 链接。只有你能看到它们，且只在你关闭它、重新加载页面或切换到其他频道/主题之前可见。只有当它到达时你仍处于该频道或主题中，私有回复才会出现。文件下载也始终只对你可见。
- **频道回复**会以 App 的名义作为普通频道消息发布，并带有 **App** 标签。频道中的所有人都能看到它们，并且它们会保留在历史记录中。

按钮点击之后，App 还可以把一个 Markdown 文件作为私有回复发送。它会显示为一个带文件名的 **Download** 按钮，例如 **Download report.md**，点击即可把文件保存到你的设备。

如果提及失败，Open WebUI 会以该 App 的名义把原因作为对你消息的回复发布出来，开头是 `App error:`，频道中的所有人都能看到。如果该 App 无法在频道中发言（例如它已被禁用或缺少发言所需的 scope），原因会显示在你的消息下方，且只有你能看到。如果按钮点击失败，原因会显示在该 App 的消息下方，同样只有你能看到。请让管理员在 **Settings > Admin > Apps** 中检查该 App。[故障排查](#troubleshooting)列出了你最可能看到的各类信息。

### 按钮 {#buttons}

App 发布的频道消息可以带有按钮和卡片。卡片显示标题、文本、字段和一张小图，侧面有一条彩色条。链接按钮会在新标签页中打开网页。其他任何按钮都会把点击发送给该 App，App 可以私下回复、发布一条新消息，或更新该按钮所属的那条消息。

---

## 设置 App {#setting-up-apps}

### 启用 App {#enable-apps}

1. 前往 **Settings > Admin > General**。
2. 打开 **Apps** 与 **Channels**，然后保存。App 只在频道中起作用，因此两者都需要。
3. 管理设置中会出现 **Apps** 标签页。

同一个开关也可以通过 [`ENABLE_APPS`](/reference/env-configuration#enable_apps) 设置。关闭它会断开所有 App 连接。

### 安装 App {#install-an-app}

你需要从 App 运营方获得两样东西：它的 **App URL**（例如 `https://app.example.com/events`）和它的 **API key**。

若该 App 位于你自己的网络、Docker 宿主机上，或使用纯 HTTP，请先配置[私有与纯 HTTP 的 App 服务器](#private-and-plain-http-app-servers)。

1. 前往 **Settings > Admin > Apps** 并点击 **Add app**（加号按钮）。
2. 填写 **App URL** 与 **API Key**，然后点击 **Continue**。Open WebUI 会从该 URL 加载 App 的详情。
3. 审阅该 App 请求的 scope。关掉你不想授予的项，然后点击 **Continue**。
4. 检查 **Name**、**App handle** 与 **Access**。handle 是一个简短的唯一 ID，会显示在 **Apps** 列表中名称旁边。它由小写字母、数字和连字符组成，以字母开头，长度最多 40 个字符。App 保存后，handle 与 App URL 即固定；若要把 App 迁移到新地址，请用一个新 handle 重新安装。
5. 点击 **Connect**。

如果 **Connect** 失败，该 App 仍会被保存，但处于禁用状态，并保留其 handle。排查并解决原因后再次点击 **Connect**。

如果该 App 不公布自己的详情，请填写 **App URL** 与 **API Key**，然后点击 **Enter details manually**。填写 **Name** 以及该 App 的 Ed25519 **Public key**。点击 **Requested scopes**，打开该 App 请求的 scope 并点击 **Continue**。接着点击 **Scopes** 旁的 **Review**，打开你愿意授予的 scope。把 **App handle** 设为与该 App 的 ID（oix 中的 `manifest_id`）完全一致：对手动录入的 App，Open WebUI 会把 handle 当作该 ID，两者不一致时连接会失败。这就要求该 App 的 ID 同时也是合法的 handle。ID 不符合这一条件的 App 必须公布自己的详情。

App URL 不能包含凭据、查询串（`?`）或片段（`#`），并且必须直接响应而不做重定向。Open WebUI 会直连 App，并忽略 `HTTP_PROXY`、`HTTPS_PROXY` 和 `NO_PROXY`，因此 Open WebUI 服务器需要到每个 App 都有直达的网络路径。

API key 与该 App 的连接凭据都使用派生自 [`WEBUI_SECRET_KEY`](/reference/env-configuration#webui_secret_key) 的密钥加密存储。请保持该值稳定，并在每个 Open WebUI 实例上保持一致；如果它发生变化，请参阅[更改 WEBUI_SECRET_KEY 后 App 无法连接](#apps-stop-connecting-after-webui_secret_key-changed)。

### 私有与纯 HTTP 的 App 服务器 {#private-and-plain-http-app-servers}

默认情况下，每个 App URL 都必须使用 HTTPS，并且其主机名解析到的所有地址都必须是公网地址。若要允许位于 localhost、私有网络或使用纯 HTTP 的 App，请在 Open WebUI 服务器上把它的 origin 列入 [`APP_ALLOWED_PRIVATE_ORIGINS`](/reference/env-configuration#app_allowed_private_origins) 并重启：

```bash
APP_ALLOWED_PRIVATE_ORIGINS=http://127.0.0.1:8000
```

匹配在协议、主机和端口上都是精确的。列入的 `http://` origin 可以使用纯 HTTP；无论协议为何，列入的 origin 都可以解析到私有、回环或保留地址。每一项都要写明协议，例如 `http://host.docker.internal:8000`。缺少协议、或含有凭据或片段的条目会让所有 App（包括公网 App）都无法工作：加载 App 详情时会失败并提示 `Invalid app URL`，已安装的 App 会一直停留在 **Connecting**。

在 Docker 内部，`127.0.0.1` 指的是 Open WebUI 容器自身。若 App 运行在 Docker 宿主机上，请以 `http://host.docker.internal:8000` 作为 origin（在 Linux 上需以 `--add-host=host.docker.internal:host-gateway` 启动容器）。若 App 位于同一 Docker 网络中的另一个容器，请使用它的服务名或容器名，例如 `http://hello-app:8000`。若 App 位于你网络中的另一台机器上，请使用它的局域网地址，例如 `http://192.168.1.50:8000`。此时 App URL 就以该 origin 开头，例如 `http://192.168.1.50:8000/events`。

App 连接始终会校验该 App 的证书。对于位于你网络中且使用自签名证书的 App，请列出其 `http://` origin 并使用纯 HTTP，或者为该 App 配置一个 Open WebUI 服务器信任的证书。

### 作用域 {#scopes}

Scope 限定了 App 能做什么。安装 App 时由你选择授予哪些 scope，之后也可以在 **Configure** 中点击 **Scopes** 旁的 **Edit** 更改选择。两份列表都只提供该 App 请求过的 scope。

请求的 scope 来自该 App 的详情。对于手动录入详情的 App，可在 **Configure** 中修改：点击 **Edit details manually**，然后点击 **Requested scopes**。关掉某个请求的 scope 也会把它从已授予的 scope 中移除。

| Scope | 显示为 | 它允许的操作 |
|-------|----------|----------------|
| `channels:mentions:read` | Read app mentions in joined channels | 接收提及该 App 的消息 |
| `channels:messages:read` | Read messages and history in joined channels | 接收提及，以及已加入频道中每一条新增、编辑和删除的消息。读取消息历史与主题 |
| `channels:messages:write` | Send messages and edit own messages in joined channels | 发布频道消息并编辑该 App 自己的消息 |
| `channels:read` | Read joined channel details | 列出该 App 被加入的频道，包括名称、类型以及是否为私有 |

接收提及需要 `channels:mentions:read` 或 `channels:messages:read`。回复提及还需要 `channels:messages:write`，因为回复本身是一条频道消息。按钮点击在任何 scope 下都能送达该 App。频道回复与按钮更新需要 `channels:messages:write`；对按钮点击的私有回复无需额外 scope。每个 scope 只对该 App 被加入的频道生效。

### 访问权限 {#access}

**Access** 决定谁可以使用该 App：提及它、点击它的按钮，以及把它添加到频道。在频道中使用它还需要对该频道的读取权限。

- **Everyone**（新 App 的默认设置）：所有用户。
- **Restricted**：管理员，加上你添加的用户与[群组](/features/authentication-access/rbac/groups)。若未添加任何人，则只有管理员能使用该 App。

### 连接状态 {#connection-status}

Open WebUI 会与每个已启用的 App 保持一条长连接，并自动重连，两次尝试之间最多等待 30 秒。每个 Open WebUI 工作进程都会各自建立连接；关于工作进程与 Redis，请参阅[扩展 Open WebUI](/getting-started/advanced-topics/scaling)。**Apps** 标签页会显示每个已启用 App 的状态，并每隔几秒刷新一次：

| 状态 | 含义 |
|--------|---------|
| **Connected** | 已建立经过校验的连接。多个工作进程共享 Redis 时，其中至少有一个已连接。 |
| **Connecting** | Open WebUI 正在尝试连接该 App，并会持续重试。 |
| **Disconnected** | 没有建立任何连接。 |

已禁用的 App 会以暗色显示。将鼠标悬停在开关上可看到 **Enabled**、**Disabled** 或 **Uninstalled**。

当某个 App 一直停留在 **Connecting** 或 **Disconnected** 时，把它的开关关掉再打开，然后在弹出的对话框中点击 **Connect**。该对话框会显示连接失败的原因；[故障排查](#troubleshooting)会解释每一条信息。

### 更新、禁用与卸载 {#update-disable-and-uninstall}

- **Configure**（齿轮图标）会打开该 App 的设置。**Update app**（URL 旁的刷新按钮）会重新加载该 App 的详情，例如运营方新增了 scope 或更换了头像之后。保存会批准更新后的详情与所选 scope，并重新连接该 App。当公钥或 API key 发生变化时，保存会像首次安装那样从头重新连接该 App。
- **Edit details manually**（URL 下方）会打开该 App 的 **Public key** 与 **Requested scopes** 供你编辑。用于不公布自身详情的 App。保存会以同样方式批准编辑后的详情并重新连接该 App。
- 开关会立即禁用已启用的 App。重新打开它会弹出设置，其中的 **Connect** 可再次连接该 App。
- **Configure** 对话框底部的 **Uninstall** 会移除 API key、连接凭据以及该 App 的频道成员关系。该 App 已发布的消息仍会留在频道中。该 App 会以 **Uninstalled** 状态留在列表里，保留其 handle、scope 与访问权限。若要再次使用，请打开其开关、填入 API key、点击 **Connect**，并重新把它添加到频道中。

只要还存在由 App 发布的消息，把数据库回滚到 Apps 迁移（`c92da83b017f`）之前就会被拒绝；参见[降级（回滚）](/troubleshooting/manual-database-migration#downgrade-rollback)。

---

## 故障排查 {#troubleshooting}

### 在 App 设置中 {#in-the-app-settings}

安装、更新或连接 App 时，App 设置对话框中会出现下列信息。

| 信息 | 需要检查什么 |
|---------|---------------|
| `App endpoints require HTTPS. For local HTTP, configure APP_ALLOWED_PRIVATE_ORIGINS.` | 改用 HTTPS URL，或把该 origin 列入 `APP_ALLOWED_PRIVATE_ORIGINS`。 |
| `App resolves to a private or reserved address. For local development, configure APP_ALLOWED_PRIVATE_ORIGINS.` | 该主机名指向私有地址。请把该 origin 列入 `APP_ALLOWED_PRIVATE_ORIGINS`。 |
| `Invalid app URL. Use an HTTP(S) URL without credentials or a fragment.` | 从 URL 中移除凭据和 `#fragment`。如果所有 App URL 都以这种方式失败，说明某条 `APP_ALLOWED_PRIVATE_ORIGINS` 记录缺少协议。 |
| `Invalid app URL` | 手动录入详情后在 **Connect** 处显示。该 URL 使用了没有 `APP_ALLOWED_PRIVATE_ORIGINS` 记录的纯 HTTP，或含有凭据、查询串或片段。 |
| `App returned an invalid response. Expected JSON.` | App URL 中含有查询串（`?...`），或该 App 返回的不是 JSON。请移除查询串，或检查该 App URL 返回的内容。 |
| `App response exceeds the allowed size.` | 该 App 的详情超过 256 KiB。 |
| `App rejected the API key. Check the API key configured on the app server.` | 该密钥与 App 上的密钥不一致。 |
| `App manifest endpoint returned HTTP <code>. Check the URL or enter details manually.` | URL 有误，或该 App 发生了重定向。请使用最终 URL，或手动录入详情。 |
| `App returned an invalid manifest. Check its app details or enter them manually.` | 该 App 的详情格式有误（参见[清单](/features/channels/building-apps#manifest)）。 |
| `App request timed out. Check that the app server is running and reachable.` | 加载其详情时，该 App 未能在 10 秒内响应。 |
| `The app connection failed before a complete response was received.` | 加载其详情时，该 App 关闭了连接或返回了损坏的 HTTP 响应。请查看 App 服务器日志。 |
| `App TLS verification failed. Check its certificate and hostname.` | 该 App 的证书无效，或与其主机名不匹配。 |
| `App hostname could not be resolved. Check DNS from the WebUI server.` | 在 Open WebUI 服务器上 DNS 解析失败。 |
| `Could not reach the app server. Check its address, port and network access.` | 网络路径、防火墙或端口。 |
| `App connection failed. Check the API key, pinned public key and Socket.IO endpoint.` | Open WebUI 未能完成连接：该 App 拒绝了 API key、Socket.IO 路径有误、代理阻断了 WebSocket、证书/DNS/网络失败、该 App 耗时超过 20 秒，或其证明无法与已存储的公钥匹配。对于手动录入的 App，其 handle 可能与该 App 的 ID 不同，或者地址是私有的且未被列入 `APP_ALLOWED_PRIVATE_ORIGINS`。如果该 App 的密钥有变化，请点击 **Update app**。如果 `WEBUI_SECRET_KEY` 发生变化，请参阅[更改 WEBUI_SECRET_KEY 后 App 无法连接](#apps-stop-connecting-after-webui_secret_key-changed)。 |
| `App rejected its connection credential. Review credentials before reconnecting.` | 该 App 不再接受上一次 **Connect** 时签发的凭据，通常是因为它的签名密钥被替换了。请在 **Configure** 中点击 **Update app** 并保存；使用新的公钥时，Open WebUI 会从头重新连接，该 App 也保留其频道。如果该 App 的 API key 发生了变化，请填入新的密钥并点击 **Connect**。若两者都没有变化，请卸载该 App，用其 API key 重新连接，并把它重新添加到频道中。 |
| `App could not complete its bidirectional connection check` | 该 App 没有正确确认最后的连接步骤（参见[连接](/features/channels/building-apps#connection)）。 |
| `App slug is already registered` | 另一个 App（可能是已卸载的）正在使用该 handle。请换一个 handle，或重新启用那个已卸载的 App。 |
| `App identity cannot change` | 该 App 的 ID 发生了变化。请把它作为一个新 App 安装。 |

有关 TLS、DNS 和可达性的信息都来自加载该 App 的详情的过程。在 **Connect** 处，同样的问题会显示为 `App connection failed`。

### 在频道中 {#in-a-channel}

提及之后，下列信息会出现在 App 以 `App error:` 开头的回复中；如果该 App 无法在频道中发言，则出现在你的消息下方。按钮点击之后，它们会出现在该 App 的消息下方。当该 App 以错误状态和它自己的错误文本作答时，你会看到那段文本，最多 2,000 个字符。下列状态信息则出现在该 App 只发送状态而没有文本时。

| 信息 | 需要检查什么 |
|---------|---------------|
| `App is disconnected; event was not sent` | 在 **Apps** 标签页中检查状态。 |
| `App response timed out; execution outcome may be unknown` | 该 App 未能在 10 秒内确认提及、未能在 3 秒内回复按钮点击，或在 Open WebUI 等待期间断开了连接。它可能实际上已经执行了动作。提及之后还会跟上一行：`Delivery was not confirmed. The app may have accepted the message; check before retrying.` |
| `App returned an invalid delivery receipt` | 提及之后显示。该 App 的应答不是它的送达确认。使用 oix 构建的 App 需要 oix 0.8.0 或更高版本。 |
| `App is inactive` | 该 App 已被禁用或已卸载。 |
| `App invocation denied` | 你无权使用该 App。请检查其 **Access**。 |
| `Channel access denied` | 你已失去对该频道的访问权限。 |
| `Invite the app into this channel first` | 该 App 不是该频道的成员。 |
| `App scope was not granted` | 提及之后，该 App 既没有 `channels:mentions:read` 也没有 `channels:messages:read`。按钮点击之后，该 App 在没有 `channels:messages:write` 的情况下试图发布或更新频道消息。请检查它的 scope。 |
| `App rejected the API key. Update the key in app settings.` | 该 App 因其 API key 拒绝了该事件。请比较 **Configure** 中的密钥与 App 服务器上的密钥。 |
| `App rejected event authorization. Check the app server logs for the verification failure.` | 该 App 无法向 Open WebUI 确认该提及或点击。该 App 的日志会指出原因。 |
| `App returned HTTP <code>. Check the app server logs.` | 该 App 以错误状态作答，例如其处理器崩溃之后。 |
| `App processing timed out; execution outcome may be unknown.` | 该 App 的处理器超时。它可能实际上已经执行了动作。 |
| `App is busy or shutting down. The event was not accepted.` | 该 App 已满负荷或正在重启。请稍后再试。 |
| `App returned an invalid response` | 按钮点击之后显示。该 App 的回复含有未知字段或超出了某个字段的长度限制（参见[回复交互](/features/channels/building-apps#replying-to-interactions)）。 |
| `App returned an invalid or oversized response` | 该 App 的应答不是 JSON 对象，或超过 256 KiB。 |
| `Buttons require a channel message` | 按钮点击之后显示。该 App 在私有回复中、或在 `message` 与 `update` 之外的回复中发送了按钮。按钮需要 `visibility` 为 `channel`。 |
| `App event could not be delivered. Check the WebUI server logs.` | 发给该 App 的事件超过 1 MiB，例如一条非常长的消息。 |

### 更改 WEBUI_SECRET_KEY 后 App 无法连接 {#apps-stop-connecting-after-webui\_secret\_key-changed}

Open WebUI 使用派生自 `WEBUI_SECRET_KEY` 的密钥加密每个 App 的 API key 与连接凭据。一旦该值发生变化，Open WebUI 就无法再读取它们：每个 App 都会停留在 **Connecting**，在 **Configure** 中重新填写 API key 也会失败。恢复方法如下，对每个 App 分别操作：

1. 打开 **Configure** 并点击 **Uninstall**。这会清除旧的凭据。
2. 打开该 App 的开关，填入其 API key 并点击 **Connect**。
3. 把该 App 重新添加到它的频道中。

---

## 构建 App {#building-an-app}

App 是 Open WebUI 会主动连接的一个服务器。你可以用 [oix](https://github.com/open-webui/oix#readme)（Python SDK）构建一个，或者按[构建 App](/features/channels/building-apps)中描述的协议自行实现。
