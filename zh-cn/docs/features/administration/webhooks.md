---
sidebar_position: 17
title: "Webhook 集成"
---

## 概述 {#overview}

Open WebUI 提供三种不同的 Webhook 集成，帮助您随时了解实例内发生的事件，并支持外部服务集成。这些 Webhook 允许您在 Discord、Slack 或任何支持传入 Webhook 的应用程序等外部服务中接收自动通知，也可以让外部服务向 Open WebUI 频道发送消息。

共有三种类型的 Webhook：

1.  **事件 Webhooks：** 由管理员配置的 Webhook，接收事件目录中的各类事件（注册、用户变更、对话、频道、文件、模型、配置、启动与关闭），每条 Webhook 都带有名称、URL、事件过滤器和接收范围。
2.  **用户 Webhook：** 当对话响应就绪时通知单个用户的个人 Webhook，对于长时间运行的任务特别有用。
3.  **频道 Webhooks：** 允许外部服务向特定频道发送消息的传入 Webhook。

## 1. 管理员 Webhook：新用户通知 {#1-admin-webhook-new-user-notifications}

此 Webhook 专为管理员设计，用于监控 Open WebUI 实例上的新用户注册情况。

### 使用场景 {#use-case}

- **用户注册跟踪：** 每当有新用户创建账户时，在专用的 Slack 或 Discord 频道中接收实时通知。这有助于您跟踪用户群并欢迎新成员。

### 配置 {#configuration}

您可以通过两种方式配置管理员 Webhook：

#### 方式 1：通过管理面板 {#option-1-through-the-admin-panel}

1.  以管理员身份登录。
2.  导航到 **设置 > 通用**（管理员区域）。
3.  滚动到 **Events** > **Webhooks**，点击 **+**。为该 Webhook 设置名称和 URL，选择 **Send events for** 和 **Events**，然后保存。已有条目提供 **Configure** 和 **Delete** 操作。
4.  输入您的外部服务（例如 Discord、Slack）提供的 Webhook URL。
5.  点击 **"保存"**。

**Send events for** 决定接收范围。**All users and system events** 会发送所有符合事件过滤条件的事件。**System events only** 只发送与具体用户无关的事件，例如启动与关闭。**Specific users or groups** 只发送所选用户或群组成员参与其中的事件，例如他们拥有的某次自动化运行失败。

#### 方式 2：通过环境变量 {#option-2-through-environment-variables}

`WEBHOOK_URL` 环境变量会在启动时一次性迁移为一个订阅了全部事件的 **Default webhook**。如果你只想接收注册事件，可以把它收窄为 `auth.signup` 或 `user.created`。更多详情请参阅[环境变量配置](https://docs.openwebui.com/reference/env-configuration/#webhook_url)文档。

### 负载格式 {#payload-format}
当匹配的事件触发时，Open WebUI 会向配置的 URL 发送一个 `POST` 请求。表单注册会先触发 `user.created`，然后触发 `auth.signup`，因此订阅了全部事件的 webhook 会收到两次 POST。通过 OAuth、LDAP、SCIM 或由管理员创建的用户只会触发 `user.created`，并相应设置 `source`。通用 URL 会收到事件信封；Slack 和 Google Chat 收到 `{"text": ...}`，Discord 收到 `{"content": ...}`，Teams 收到 MessageCard。

**负载示例：**

```json
{
  "schema": "0.11.3",
  "id": "8b1f...",
  "event": "auth.signup",
  "resource": "auth",
  "operation": "signup",
  "created_at": 1758150000,
  "source": "api",
  "actor": {"type": "user", "id": "...", "name": "Tim", "email": "tim@example.com", "role": "pending"},
  "subject": {"type": "user", "id": "..."},
  "data": {"email": "tim@example.com"}
}
```

## 2. 用户 Webhook：对话响应通知 {#2-user-webhook-notification-targets}
此 Webhook 允许单个用户在关心的事情发生时收到通知，例如模型完成一次长时间响应、收到频道消息，或日历提醒触发。当你已离开 Open WebUI 标签页时，它尤其有用。

每位用户在 **设置 > 通知** 中配置一个或多个**通知目标**，并为每个目标选择它接收哪些事件，以及只在离开时触发还是始终触发。模型也可以通过 `notify` 工具自行发送通知。

完整功能请参阅 **[通知](/features/chat-conversations/chat-features/notifications)**：目标、可订阅的事件、投递模式、URL 遮蔽以及 `notify` 工具。

### 使用场景 {#use-case-1}

- **长时间任务提醒：** 如果您提交了需要数分钟处理的复杂提示词，可以关闭浏览器标签页，仍会在响应就绪时立即收到通知。这让您可以处理其他任务，无需不断查看 Open WebUI 界面。

### 工作原理 {#how-it-works}

使用默认的 **away** 投递方式时，只有在您**未主动使用 WebUI** 时才会发送通知，因此不会就您正在关注的事情打扰您。将目标设置为 **always** 则无论状态如何都会发送。频道消息忽略投递方式，在群组频道和私信中也是如此，并且只有在您没有打开任何 Open WebUI 标签页时才会发送。只要有人发布消息就会发送，其中也包括通过 API 发布的机器人账号。在标准频道中，只有当您已打开过该频道或在频道中发过言后，这些消息才会送达您。设置为[**仅提及**](/features/channels#muting-a-channel)的频道只发送 @提及您的消息。

### 启用/禁用用户 Webhook {#enablingdisabling-user-webhooks}
用户 Webhook 默认禁用。管理员可以在需要时为所有用户启用此功能，也可以保持禁用以防止外部请求。

可通过两种方式操作：

1.  **直接在管理面板中：**
    - 转到 **设置 > 通用 > 功能**（管理员区域）。
    - 切换 **"用户 Webhook"** 开关。

2.  **使用环境变量：**
    - 该功能默认关闭。`ENABLE_USER_WEBHOOKS` 默认为 `False`，**用户 Webhook** 权限同样默认关闭，因此要提供该功能，请设置 `ENABLE_USER_WEBHOOKS=True`（或使用上面的开关）并授予该权限。将其设为 `False` 会重新关闭该功能，并从用户个人资料中隐藏该设置。

用户还需要 `features.webhooks` 权限（[`USER_PERMISSIONS_FEATURES_USER_WEBHOOKS`](/reference/env-configuration#user_permissions_features_user_webhooks)）；管理员始终拥有该权限。

### 配置 {#configuration-1}
1.  点击左下角的头像打开设置菜单。
2.  导航到 **设置 > 通知**。
3.  添加一个目标并填入您的 webhook URL，然后选择它应接收哪些事件。
4.  使用 **Send Test** 确认其正常工作。

:::info 从旧的 Notification Webhook 字段升级
**设置 > 账户** 下的单一 **Notification Webhook** 字段已被"目标"取代。已有的 URL 会自动迁移为一个订阅了全部事件的目标，因此无需任何操作，通知仍会照常送达。
:::

## 3. 频道 Webhooks：外部消息集成 {#3-channel-webhooks-external-message-integration}
频道 Webhooks 让外部服务、自动化工具或脚本直接向 Open WebUI 频道发布消息，例如来自监控系统、CI/CD 流水线、通知服务或任何自定义自动化工具。一个 webhook 会把消息发布到某一个频道。如果某个服务还需要响应 `@mentions` 或发布按钮，请把它构建为 [App](/features/channels/apps)。

### 使用场景 {#use-cases}

- **系统监控：** 将监控工具（Prometheus、Grafana、Nagios）的告警直接发送到团队频道。
- **CI/CD 集成：** 将来自 GitHub Actions、GitLab CI 或 Jenkins 的构建状态通知发送到开发频道。
- **自定义自动化：** 与 n8n、Zapier 或自定义脚本集成，自动化消息发送。
- **外部通知：** 将外部服务的通知转发到您的 Open WebUI 工作空间。

### 工作原理 {#how-it-works-1}

每个频道可以有多个 Webhook。每个 Webhook 具有：
- 外部服务可向其 `POST` 的唯一 **Webhook URL**
- 显示为消息作者的**显示名称**
- 可选的**头像图片**，用于直观识别 Webhook 来源
- **最后使用时间戳**，用于跟踪 Webhook 活动

通过 Webhook 发送的消息会以 Webhook 的身份显示在频道中，清楚表明它来自外部来源而非用户。

### 管理频道 Webhooks {#managing-channel-webhooks}

只有频道创建者和**管理员**才能为频道创建和管理 Webhook。

#### 创建 Webhook {#creating-a-webhook}

1.  导航到要添加 Webhook 的频道。
2.  点击频道菜单（**⋮**）并选择 **编辑频道**。
3.  在频道设置模态框中，找到 **Webhooks** 部分。
4.  点击 **管理** 打开 Webhooks 模态框。
5.  点击 **New Webhook**，会立即创建一个名为 "New Webhook" 的可用 Webhook。**Save** 只在之后修改名称和图片时生效。
6.  配置 Webhook：
    - **名称：** 将显示为消息作者的显示名称
    - **头像图片：** （可选）上传图片以代表此 Webhook
7.  点击 **Save** 应用名称和图片。
8.  使用 **复制 URL** 按钮复制生成的 Webhook URL。

#### Webhook URL 格式 {#webhook-url-format}

```
{WEBUI_API_BASE_URL}/channels/webhooks/{webhook_id}/{token}
```

此 URL 是唯一的，包含身份验证令牌。任何拥有此 URL 的人都可以向频道发送消息，请妥善保管。

#### 更新 Webhook {#updating-a-webhook}

1.  从频道设置中打开 **Webhooks** 模态框。
2.  点击要编辑的 Webhook 展开它。
3.  根据需要修改**名称**或**头像图片**。
4.  点击 **保存** 应用更改。

更新名称或图片时，Webhook URL 保持不变。由该 Webhook 发布的所有消息（包括更早发布的消息）都会显示它当前的名称和图片。

#### 删除 Webhook {#deleting-a-webhook}

1.  从频道设置中打开 **Webhooks** 模态框。
2.  点击要删除的 Webhook 展开它。
3.  点击 **删除**（垃圾桶）图标。
4.  确认删除。

删除后，Webhook URL 立即停止工作。此前由该 Webhook 发送的消息仍保留在频道中，但作者显示为"已删除的 Webhook"。

### 通过 Webhook 发送消息 {#posting-messages-via-webhook}

要从外部服务发送消息，请向 Webhook URL 发送包含 JSON 负载的 `POST` 请求。

#### 请求格式 {#request-format}

**端点：** `POST {webhook_url}`
**请求头：** `Content-Type: application/json`
**请求体：**

```json
{
  "content": "Your message content here"
}
```

#### 示例：使用 cURL {#example-using-curl}

```bash
curl -X POST "https://your-instance.com/api/v1/channels/webhooks/{webhook_id}/{token}" \
  -H "Content-Type: application/json" \
  -d '{"content": "Deployment to production completed successfully!"}'
```

#### 示例：使用 Python {#example-using-python}

```python
import requests

webhook_url = "https://your-instance.com/api/v1/channels/webhooks/{webhook_id}/{token}"
message = {
    "content": "Build #1234 failed: Unit tests did not pass."
}

response = requests.post(webhook_url, json=message)
print(response.json())
```

#### 响应格式 {#response-format}

成功时，Webhook 将返回：

```json
{
  "success": true,
  "message_id": "abc-123-def-456"
}
```

### 安全注意事项 {#security-considerations}

-   **URL 保护：** Webhook URL 包含身份验证令牌，请妥善保管，不要在公共仓库或日志中暴露。
-   **频道访问：** 任何拥有 Webhook URL 的人都可以向频道发送消息。仅与可信服务共享 URL。
-   **消息内容：** 在发送端验证和过滤消息内容，防止注入攻击。
-   **重新生成：** 如果 Webhook URL 泄露，请删除该 Webhook 并创建新的。

### Webhook 身份 {#webhook-identity}

通过 Webhook 发送的消息具有特殊的身份系统：
- 消息以 Webhook 的**名称**和**头像图片**显示
- 用户角色标记为 **"webhook"**，以区别于普通用户
- 如果 Webhook 被删除，其消息仍然可见，但显示"已删除的 Webhook"并使用默认头像
- 每条消息在其元数据中存储 Webhook ID，即使 Webhook 后来被修改或删除，也能正确归因
- 只有 Open WebUI 会写入这类元数据。通过普通请求发送或编辑消息时附带的元数据会被忽略，因此以某个账号发布的消息始终显示该账号

## 故障排查 {#troubleshooting}

如果您没有收到 Webhook 通知，请检查以下几点：

-   **验证 URL：** 确保 Webhook URL 正确并已正确粘贴到设置字段中。
-   **服务配置：** 仔细检查 Webhook 是否在外部服务（例如 Discord、Slack）中正确设置。
-   **防火墙/代理：** 确保您的网络或防火墙没有阻止来自 Open WebUI 服务器的传出请求。
-   **Open WebUI 日志：** 检查 Open WebUI 服务器日志中与 Webhook 失败相关的错误消息。

:::note

Open WebUI 中的 Webhook 功能正在持续改进。请关注未来更新中的更多事件类型和自定义选项。

:::