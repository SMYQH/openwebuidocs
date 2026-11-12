---
title: "Tether"
sidebar_position: 3
---

# Tether

Tether 是 Open WebUI 的桌面伴侣应用，提供 macOS、Windows 和 Linux 版本。它会登录到你的实例并把你的电脑连接上去，这样聊天就可以把这台电脑当作终端使用，应用也能显示桌面通知。项目位于 [github.com/open-webui/tether](https://github.com/open-webui/tether)。个人非商业用途免费。商业或组织性的生产使用需要 [Open WebUI 企业版许可证](https://docs.openwebui.com/enterprise)。

## 连接 {#connecting}

所有设置都在 Tether 应用中完成，在那台你想从聊天中使用的电脑上。只要实例满足[环境要求](#requirements)，它就能直接接受该应用，无需在管理面板中开启任何开关。

1. 从[发布页](https://github.com/open-webui/tether/releases/latest)在那台电脑上安装 Tether。
2. 在 Tether 中输入你的 Open WebUI 实例地址。若要添加另一个实例或账户，点击 **Add connection**。请输入实例最终所处的地址：如果 `http://` 会重定向到 `https://`，就填写 `https://` 的地址。
3. Tether 会在该实例上用浏览器打开 `/auth/sessions/<id>`。如果你尚未登录，请先用你用来聊天的账户登录。登录后该页面会把你送回 Tether。
4. Tether 会提示安装 Open Terminal——正是它让聊天能够在这台电脑上工作。请接受安装。若选择了 **Not now**，之后可在 Tether 的 **Settings > Open Terminal** 中安装。
5. Tether 中的终端指示器会显示 **Connected to WebUI**。Tether 会保持登录状态，并在后台续期其会话。

## 在聊天中使用你的电脑 {#using-your-computer-in-a-chat}

用任意设备上的任意浏览器打开你的实例，并登录与 Tether 相同的账户。点击聊天输入框中的**终端按钮**（云图标），在 **Your devices** 下选择你的电脑。它会按电脑名称列出，或按你在 Tether 设置中设定的 **Device name** 列出。之后它的用法与其他终端完全相同，参见[在聊天中选择终端](/features/open-terminal/setup/connecting#7-select-a-terminal-in-chat)。

只要你拥有至少一个终端，终端按钮就会显示出来。如果 Tether 是你唯一的终端，该按钮会在 Tether 连接后立刻出现，并在 Tether 断开后消失。

每个已登录的应用都是一个独立的会话。从应用中退出会结束其会话。会话也会在通过 API 被删除、或在 [`SESSION_EXPIRES_IN`](/reference/env-configuration#session_expires_in)（默认 `90d`）期限内无人使用时结束。访问令牌有效期为 15 分钟，每次续期都会替换刷新令牌。

## 这个应用能获得什么 {#what-the-app-gets}

- **把你的电脑当作终端。** 在 Tether 连接期间，你的电脑会以 `tether:<connection id>` 的形式出现在终端列表中。只有你能看到它，而且只有当 Tether 提供 `open_terminal` 服务时才会出现。如果连接中断，已打开的终端会显示"Connection interrupted. Reconnecting to the same terminal…"，并在 Tether 恢复后继续使用同一个终端。每个连接最多同时处理 16 个活跃操作。
- **通知。** 当聊天完成或失败、发生日历提醒或收到频道消息时，服务器会向已选择接收通知的已连接应用发送通知。只有当你在 **Settings > Notifications** 中开启了 **Browser Notifications** 时，才会发送这些通知。

## 环境要求 {#requirements}

- [`ENABLE_WEBSOCKET_SUPPORT`](/reference/env-configuration#enable_websocket_support) 已开启。
- Open WebUI 以单个工作进程运行，或者在 [`UVICORN_WORKERS`](/reference/env-configuration#uvicorn_workers) 大于 1 时搭配使用 [Redis](/reference/env-configuration#redis_url)。没有 Redis 时，多工作进程实例会拒绝 Tether 连接，对 Tether 终端的请求会失败并提示"Tether requires Redis with multiple WebUI workers."。
- [`ENABLE_TOOL_SERVERS`](/reference/env-configuration#enable_tool_servers) 已开启（这是默认设置）。它是实例上所有终端的总开关，Tether 电脑也包含在内。
- 运行 Tether 的电脑能够访问实例的地址。Tether 是从电脑向实例发起连接的，因此这台电脑无需开放端口，也不需要实例能够反向访问它的地址。

当满足前两项要求时，`/api/config` 中的应用配置会报告 `features.tether`；而 `features.auth_sessions` 则在每个实例上都会出现。

访问权限随账户而定：每个能够登录的用户都可以连接自己的电脑，并且它只对该账户列出。

## 故障排查 {#troubleshooting}

如果聊天输入框中缺少终端按钮或你的电脑，请按顺序检查以下各项：

| 检查项 | 修复方式 |
| --- | --- |
| Tether 显示 **Running locally · Not connected to WebUI** | Tether 尚未连接到该实例。把实例地址添加为一个连接并登录。 |
| 浏览器登录的账户与 Tether 不同 | 在两处都登录同一个账户。 |
| Tether 中尚未安装 Open Terminal | 在 Tether 的 **Settings > Open Terminal** 中安装它。 |
| 实例的 `/api/config` 中没有 `"tether":true` | 由管理员让实例符合[环境要求](#requirements)。 |
| **Settings > Admin > Integrations** 中的 **Tools** 与 **Open Terminal** 分区呈灰色不可用 | 由管理员从实例环境中移除 `ENABLE_TOOL_SERVERS=False` 与 `ENABLE_PLUGINS=False`，然后重启实例。 |

如果电脑已被选中但模型没有使用它，说明该模型的 **Terminal** 能力处于关闭状态。请在模型编辑器中开启它，参见[能力与绑定](/features/workspace/models#capabilities-and-bindings)。

## 会话 API {#session-api}

这些端点面向原生客户端的开发者。`requests`、`exchange` 和 `refresh` 无需登录；其他每个端点都需要已登录用户的 bearer 令牌。对 create、requests、exchange、refresh 和 authorize 的调用，按 IP 地址限制为每分钟 30 次。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/api/v1/auths/sessions/requests` | 发起浏览器登录。需提交应用的 `name`、一个回环地址 `redirect_uri`（例如 `http://127.0.0.1:<port>/callback`，主机为 `127.0.0.1`、端口明确、无 query 或 fragment）、32 到 256 个 URL 安全字符组成的 `state`，以及一个 PKCE `code_challenge`（S256，43 个字符）。该请求有效期为 10 分钟。返回 `session_id`，用于打开 `/auth/sessions/<id>`。 |
| `GET` | `/api/v1/auths/sessions/{id}/request` | 返回一个等待中请求的名称与有效期。 |
| `POST` | `/api/v1/auths/sessions/{id}/authorize` | 以已登录用户的身份批准该请求，并返回一个回调地址及一次性 `code`（有效期 60 秒）。`/auth/sessions/<id>` 页面会调用它。 |
| `POST` | `/api/v1/auths/sessions/exchange` | 用 `session_id`、`code`、`redirect_uri` 和 `code_verifier` 换取访问令牌与刷新令牌。 |
| `POST` | `/api/v1/auths/sessions/refresh` | 用刷新令牌换取新的令牌。可选地提交一个 `request_id`，以便在响应丢失时找回新令牌：使用相同的 `request_id` 重复调用会再次返回它们。 |
| `POST` | `/api/v1/auths/sessions` | 直接从一个已登录的请求创建会话。 |
| `GET` | `/api/v1/auths/sessions` | 列出你的会话。 |
| `DELETE` | `/api/v1/auths/sessions/{id}` | 吊销你的某个会话。 |

### 连接 {#connection}

客户端连接到 websocket `/api/v1/tether/connect`，并发送一条 `hello` 消息，其中包含 `version`（`1` 或 `2`）、某个会话的访问 `token`、`connection_id`、`name` 以及一份 `services` 列表。把 `notifications` 设为 `true` 可让该连接选择接收通知。服务器以 `ready` 作为回应。
