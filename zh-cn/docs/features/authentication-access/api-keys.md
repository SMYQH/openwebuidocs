---
sidebar_position: 500
title: "API 密钥"
---

# 🔑 API 密钥 {#api-keys}

**Open WebUI 的程序化访问——适用于脚本、机器人和集成。**

API Keys 是个人访问令牌，允许外部代码调用 Web 界面使用的相同端点。您在浏览器中能做的任何事情——对话补全、模型列举、文件上传、RAG 查询——您的脚本都可以通过单个 `Authorization: Bearer` 请求头来完成。每个密钥继承创建者的权限，因此无需学习单独的权限模型。

---

## 为什么使用 API Keys？ {#why-api-keys}

### 无需浏览器的自动化 {#automation-without-a-browser}

脚本、CI/CD 流水线、监控机器人和第三方工具都需要程序化访问。API Keys 为它们提供了稳定的凭证，不会随浏览器会话过期。

### 相同权限，不同接口 {#same-permissions-different-interface}

API Key 代表您行事。它继承您的角色和用户组权限——管理 Web 界面的相同访问控制也适用于每个 API 请求。

### 可撤销且可审计 {#revocable-and-auditable}

一个密钥可以直接替换或删除。创建新密钥会覆盖旧密钥，删除密钥则会让账号不再拥有任何密钥——无论采用哪种方式，泄露的凭据都只需一步就能完成退役，且变更立即生效。这个过程不涉及重置密码，也不涉及使会话失效。管理员还可以通过关闭全局 **API Keys** 开关一次性弄残所有密钥，或者通过移除某用户的功能权限、或者[代为其删除](#managing-a-users-key-admin)来一次性开除某个用户的密钥。密钥的创建与删除都会被记录为认证事件。开启[审计日志](/getting-started/advanced-topics/hardening#audit-logging)后，使用密钥发起的请求都会出现在审计日志中，并归属于该密钥的所有者——无论密钥是以 Bearer token 还是以 `x-api-key` 请求头的形式到达（请求头名可通过 [`CUSTOM_API_KEY_HEADER`](/reference/env-configuration#custom_api_key_header) 重命名）。

## 主要功能 {#key-features}

| | |
| :--- | :--- |
| 🔐 **Bearer token 认证** | 标准 `Authorization: Bearer` 请求头，适用于任何 HTTP 客户端或 SDK |
| 🛡️ **限定于用户范围** | 密钥继承创建用户的角色和用户组权限 |
| 🚫 **端点限制** | 可选择限制密钥可访问的 API 路由 |
| 👥 **权限门控** | 非管理员用户需要全局管理员开关加上每用户组的功能权限 |

---

## 入门指南 {#getting-started}

### 第一步：全局启用 API Keys（管理员操作） {#step-1-enable-api-keys-globally-admin}

1. 以**管理员**身份登录
2. 打开 **管理面板 > 设置 > 通用**
3. 滚动到 **认证** 部分
4. 切换 **启用 API Keys** 为开
5. 点击 **保存**

:::info
这是全局主开关。关闭时，任何人——包括管理员——都无法生成密钥。开启时：
- **管理员**用户可以立即生成密钥
- **非管理员**用户仍需要 API Keys 功能权限（第二步）
:::

*（可选）* 启用 **API Key 端点限制**，以限制 API Keys 可调用的路由。将允许的端点指定为逗号分隔的列表（例如 `/api/v1/models,/api/v1/chat/completions`）。

### 第二步：向非管理员用户授予权限（管理员操作） {#step-2-grant-permission-to-non-admin-users-admin}

非管理员用户需要 **API Keys** 功能权限。使用以下任一方式授予：

#### 方式 A：默认权限（所有用户） {#option-a-default-permissions-all-users}

1. **管理面板 > 用户 > 用户组 > 默认权限**
2. 在 **功能权限** 下，切换 **API Keys** 为开
3. 点击 **保存**

:::warning
这会授予所有具有"user"角色的用户生成 API Keys 的能力。要进行更严格的控制，请使用方式 B。
:::

#### 方式 B：用户组（特定用户） {#option-b-user-groups-specific-users}

1. **管理面板 > 用户 > 用户组**
2. 选择或创建一个用户组（例如"API 用户"）
3. 在 **权限 > 功能权限** 下，切换 **API Keys** 为开
4. 点击 **保存**

:::tip
创建一个专用的"API 用户"或"监控"用户组，只将需要程序化访问的账户添加进去。这遵循最小权限原则。
:::

### 第三步：生成密钥 {#step-3-generate-a-key}

1. 点击**个人资料图标**（左下角侧边栏）
2. 选择 **设置 > 账户**
3. 在 **API Keys** 部分，点击 **生成新 API Key**
4. 为其起一个描述性名称（例如"监控机器人"）
5. **立即复制密钥**——您以后将无法再次查看它

:::warning
将 API Keys 视为密码。将其存储在密钥管理器中，永远不要将其提交到版本控制，也不要在公共频道中分享。如果密钥泄露，立即删除并生成新的。
:::

---

### 管理用户的密钥（管理员） {#managing-a-users-key-admin}

管理员可以替换或删除任意用户的密钥。在**管理面板 > 用户**中打开该用户，在编辑对话框中 **API Key** 旁使用**轮换**或**删除**。

- **轮换**会签发新密钥并只显示一次，请在关闭对话框前复制它。它需要全局的 **API Keys** 开关已开启，且该用户被允许拥有密钥。
- **删除**会移除密钥，即使 API 密钥功能处于关闭状态也可以使用。
- 只有[主管理员](/features/authentication-access/rbac/roles#the-primary-administrator)才能更改主管理员的密钥。

脚本可以使用管理员的 API 密钥做同样的事：`POST /api/v1/users/{user_id}/api_key/rotate` 返回新密钥，`DELETE /api/v1/users/{user_id}/api_key` 则将其移除。

---

## 使用您的 API Key {#using-your-api-key}

在 `Authorization` 请求头中将密钥作为 Bearer token 传递：

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8080/api/models
```

```python
import requests

response = requests.get(
    "http://localhost:8080/api/models",
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
print(response.json())
```

有关完整的端点参考——对话补全、Ollama 代理、RAG、文件管理等——请参阅 [API 端点](/reference/api-endpoints)。

### 反向代理消耗了 `Authorization` 怎么办？ {#behind-a-reverse-proxy-that-consumes-authorization}

如果 Open WebUI 部署在使用 `Authorization` 头进行自身认证的网关之后（basic auth、SSO sidecar、企业 API 网关、mutual-TLS 适配器等），客户端可以改用一个专用 header 来传递 API key。中间件会按以下顺序检查：`Authorization: Bearer`、`token` cookie，以及一个可配置的自定义 header。

该自定义 header 默认是 `x-api-key`，管理员可通过 [`CUSTOM_API_KEY_HEADER`](/reference/env-configuration#custom_api_key_header) 环境变量重命名它，避免与请求链中其他组件冲突。

```bash
curl -H "X-OpenWebUI-Key: YOUR_API_KEY" \
  http://openwebui.internal/api/models
```

```
# Open WebUI 容器环境变量
CUSTOM_API_KEY_HEADER=X-OpenWebUI-Key
```

---

## 最佳实践 {#best-practices}

### 专用服务账户 {#dedicated-service-accounts}

专门为自动化创建一个**非管理员用户**（例如 `monitoring-bot`、`ci-pipeline`），从该账户生成密钥。如果密钥泄露，攻击者只能获得该用户的权限——而不是管理员访问权限。

### 端点限制 {#endpoint-restrictions}

启用 **API Key 端点限制**，并只将您的集成实际需要的路由加入白名单。当请求路径与某一条目完全匹配，或者以路径段的方式位于其之下时，该请求就会被允许——例如 `/api/v1/models` 也覆盖了 `/api/v1/models/anything`。监控机器人只需要 `/api/models` 和 `/api/chat/completions`，所以不要开放 `/api/v1/files/` 或管理员端点。该白名单是实例级的，因此必须取所有集成需要的并集。

### 密钥轮换 {#key-rotation}

定期删除旧密钥并生成新密钥，特别是对于长期运行的集成。为密钥起名时加上日期或版本以跟踪轮换（"监控机器人 - 2025-Q1"）。

---

## 故障排查 {#troubleshooting}

**在设置 > 账户中看不到 API Keys 部分？**

- **检查全局开关：** 确认管理员已在 **管理面板 > 设置 > 通用 > 启用 API Keys** 中启用 API Keys。参见 [`ENABLE_API_KEYS`](/reference/env-configuration#enable_api_keys)。
- **检查您的权限（非管理员用户）：** 确认您的账户或用户组在 **功能权限** 下具有 **API Keys** 功能权限。参见 [`USER_PERMISSIONS_FEATURES_API_KEYS`](/reference/env-configuration#user_permissions_features_api_keys)。

**收到 `401 Unauthorized` 响应？**

- 验证密钥格式是否正确：`Authorization: Bearer sk-...`
- 检查密钥是否已被删除
- 检查该密钥是否已被同一账户上的更新密钥替换
- 确认该账户仍然存在且不处于待审批状态
- 如果启用了端点限制，确认您调用的路由在允许列表中

**收到 `403 Forbidden` 响应？**

- 全局的 **API Keys** 开关可能已被关闭，这会使已有密钥失效
- 密钥所有者可能已失去 **API Keys** 功能权限
- 如果启用了端点限制，确认您调用的路由在允许列表中

---

## 限制 {#limitations}

### 每个账户一个密钥 {#one-key-per-account}

一个账户只持有一个没有名称的密钥。无法为同一用户并行运行两个密钥，创建密钥总会覆盖已有的那个。请为每个集成使用独立的账户。

### 不支持按密钥设置权限 {#no-per-key-permissions}

密钥会继承创建者的完整权限。除了端点限制之外，您无法把某个密钥限制为其所有者权限的子集。

### 不会自动过期 {#no-automatic-expiration}

API Keys 不会自动过期，您必须手动删除并轮换它们。
