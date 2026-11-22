---
sidebar_position: 3
title: "角色"
---


Open WebUI 定义了三种主要的**系统角色**，用于确定用户账户的基础访问级别。这些角色与[用户组](./groups.md)和[权限](./permissions.md)有所不同。

| 角色 | 关键字 | 说明 |
| :--- | :--- | :--- |
| **管理员** | `admin` | **超级用户**。对系统拥有完全控制权。 |
| **用户** | `user` | **标准用户**。受 RBAC 权限约束。 |
| **待审批** | `pending` | **受限**。在获得批准之前无法访问。 |

## 角色详情 {#role-details}

### 管理员（`admin`） {#administrator-admin}
管理员角色专为系统维护人员设计。
*   **完全访问**：默认访问所有资源和设置。
*   **管理权限**：可以管理用户、用户组和全局配置。
*   **绕过检查**：默认情况下绕过大多数权限检查。

:::warning 管理员限制与最佳实践
虽然管理员通常拥有不受限制的访问权限，但某些系统配置可能会出于安全和隐私原因限制其能力：
*   **隐私控制**：[`ENABLE_ADMIN_CHAT_ACCESS=False`](/reference/env-configuration#enable_admin_chat_access) 会在界面中对管理员隐藏用户的对话。它并不会阻止管理员访问数据；参见[聊天数据隐私](/security/chat-data-privacy-and-encryption#admin-users)。
*   **个别功能可能有例外**：某些功能可能不受管理员绕过规则约束，仍会执行额外检查。对于 API 密钥，只要启用了 `ENABLE_API_KEYS`，管理员就可以生成密钥。
*   **访问控制例外**：如果禁用了 `BYPASS_ADMIN_ACCESS_CONTROL`，管理员也会像其他人一样受到访问授权检查。私有的工作区项目（模型、知识库、提示词、工具、技能、笔记）仅所有者以及被共享的人可见。由管理员配置且没有任何授权的连接和 arena 模型仍仅对管理员可见。参见[各资源类型中“私有”的具体含义](/features/authentication-access/rbac/groups#what-private-means-for-each-resource-type)。

为确保安全，建议通过用户组为管理员明确分配权限，不要只依赖管理员角色默认绕过检查。即使日后限制绕过权限检查，管理员也能保有原有的访问权限。
:::

### 标准用户（`user`） {#standard-user-user}
这是团队成员的默认功能角色。
*   **受权限约束**：没有隐式访问权限。所有能力必须通过**全局默认权限**或**用户组成员资格**来授予。
*   **累加权限**：如[权限](./permissions.md)部分所述，其有效权限是所有授予的总和。

### 待审批用户（`pending`） {#pending-user-pending}
新注册用户（如果已配置）或已停用用户的默认状态。
*   **零访问**：无法执行任何操作或查看任何内容。
*   **需要审批**：必须由现有管理员提升为 `user` 或 `admin`。

:::note
`admin` 角色会跳过权限检查：代码先判断角色，再去查找具体权限。细粒度权限（如禁用"网络搜索"）通常**不**适用于管理员。
:::

## 角色分配 {#role-assignment}

### 初始设置 {#initial-setup}

*   **首个用户：** 在全新安装中创建的第一个账户会自动被赋予 **Admin** 角色。该首次注册会忽略 `ENABLE_SIGNUP`，但在登录表单被禁用时会被拒绝，除非 `ENABLE_INITIAL_ADMIN_SIGNUP=true`；注册成功后它会关闭注册功能。
*   **无头创建管理员：** 对于自动化/容器化部署，你可以通过环境变量自动创建管理员账户（见下文）。
*   **后续用户：** 新注册的用户会被赋予 **Default User Role**。

### 配置 {#configuration}
可以通过 `DEFAULT_USER_ROLE` 环境变量控制新用户的默认角色：

```bash
DEFAULT_USER_ROLE=pending
# Options: 'pending' (default), 'user', 'admin'
```
*   **pending（推荐用于公共/共享实例）：** 新用户可以登录，但只能看到 pending 界面；在管理员更改其角色之前，每个 API 请求和 WebSocket 握手都会拒绝他们。
*   **user：** 新用户以默认权限立即获得访问权限。
*   **admin：**（谨慎使用）新用户成为完全管理员。

## 更改角色 {#changing-roles}
管理员可以随时通过**管理面板 > 用户**更改用户的角色，但有三种例外：主管理员不能被其他管理员编辑或降级，也不能自我降级；任何管理员都不能在界面中更改自己的角色；任何管理员都不能删除自己的账户。
*   将用户提升为 `admin` 会授予其完全控制权。
*   将管理员降级为 `user` 会使其再次受到权限系统约束。

### 角色变更何时生效 {#when-a-role-change-takes-effect}

无论变更通过哪条途径到达，角色变更都会立即终止该账户的实时 WebSocket 连接：

*   **管理面板 > 用户**，或其后端的用户更新 API。
*   SCIM 目录同步，包括映射到 `user` 和 `pending` 角色的 `active` 标志（参见 [SCIM 2.0](/features/authentication-access/auth/scim)）。
*   启用了 [OAuth 角色管理](/features/authentication-access/auth/sso#oauth-role-management)的 OAuth 或 OIDC 登录。
*   携带[受信任角色请求头](/features/authentication-access/auth/sso#role-management)的登录。

删除账户会以同样的方式终止其实时连接。

在多副本部署中，如果使用 [`WEBSOCKET_MANAGER=redis`](/reference/env-configuration#websocket_manager)，连接会通过共享会话池找到，并在持有它们的任意副本上被断开，而不只是处理变更的那个副本。

浏览器会自行重连并重新认证，因此在该连接之上运行的功能（频道、协作式笔记编辑）会按新角色而非连接建立时缓存的角色生效。REST API 调用每次请求都会从数据库读取账户，因此被降级的管理员从下一次调用起就会失去仅管理员可用的端点。

:::note 角色变更不会吊销该用户的令牌
他们仍保持登录状态，并以新角色继续浏览。降级为 `pending` 确实会将其锁定，因为 `pending` 账户在每次 API 请求和 WebSocket 握手时都会被拒绝。若要同时结束其会话，请使用[退出所有设备](#signing-a-user-out-of-every-device)。
:::

## 让用户在所有设备上退出登录 {#signing-a-user-out-of-every-device}

在**管理面板 > 用户**中打开该用户，点击编辑对话框底部的**登出所有设备**，然后确认。该用户的每个会话都会结束：使用该账户登录的浏览器标签页和应用在下一次请求时会被拒绝，必须重新登录，它们的实时连接也会被关闭。该用户正在进行的自动化和子智能体运行同样会失去访问权限。当设备丢失、账户可能已被入侵或有人离职时，请使用该功能。

![登出所有设备？确认对话框，说明用户需要在每台设备上重新登录，并且 API 密钥仍然有效](/images/features/auth/sign-out-all-devices.webp)

- **API 密钥仍然有效。** 如需阻止脚本和集成继续访问，请[删除或轮换该用户的密钥](/features/authentication-access/api-keys#managing-a-users-key-admin)。
- **无需 Redis 也能工作。** 登出记录保存在数据库中，因此对每个 worker 和每个副本都生效。
- **主管理员**只能由其本人以这种方式登出。

在同一对话框中为该用户设置新密码，也会使其在所有设备上登出。该操作会记录为 `auth.sessions_revoked` [事件](/features/extensibility/plugin/functions/event)。脚本可以使用管理员的 API 密钥，通过 `POST /api/v1/users/{user_id}/sessions/revoke` 触发它。所有会让账户登出的操作参见[令牌吊销](/getting-started/advanced-topics/hardening#token-revocation)。

## 主管理员 {#the-primary-administrator}

实例上创建的第一个账户（参见[初始设置](#initial-setup)）是**主管理员**。它没有特殊标记：内部仅根据创建时间戳判断，即最早创建的账户。

主管理员享有一项额外的小保护。界面对每个管理员账户都会隐藏删除控件，后端也会拒绝通过用户 API 删除主管理员账户；它同样拒绝其他管理员对该账户的任何更改（角色、姓名、邮箱或密码），并拒绝该账户自我降级。这纯粹是为了防止初始引导账户被意外删除，否则可能导致实例失去其创始管理员或触发不必要的角色重新分配。要更改主管理员的邮箱，请使用该账户登录，并在 **Admin Panel > 用户** 中对它使用 **Edit User**，这会同时更新 `user` 和 `auth` 两张表中的地址；只改其中一张表会破坏登录，因为密码登录在 `user` 表中查找邮箱，而 LDAP 和受信任请求头登录则在 `auth` 表中查找。

这是一项便利性保护措施，而非安全边界。所有管理员共享系统的完全控制权，因此任何管理员仍然可以在数据层更改或删除任何账户，包括主管理员账户。

### 更换主管理员 {#swapping-the-primary-administrator}

有时需要更换主管理员，例如负责初始部署的人离开了组织。主管理员身份只按创建时间戳确定，由最早创建的账户担任，无论它当前是什么角色。因此，在数据库层面调整或删除账户，会改变系统认定的主管理员。

这被设计为数据层操作而非一键按钮，以确保变更创始账户始终是一个有意的、经过深思熟虑的操作。在进行更改之前备份数据库，并在实例空闲时执行。此处不列出确切的查询语句，因为数据库架构在不同版本之间会有所变化；请根据当前架构操作，如需针对你的版本的指导，请通过社区渠道联系我们。

## 无头管理员账户创建 {#headless-admin-account-creation}

对于**自动化部署**（Docker、Kubernetes、云平台），手动交互不切实际时，Open WebUI 支持在首次启动时使用环境变量自动创建管理员账户。

### 工作原理 {#how-it-works}

配置以下环境变量时：
- `WEBUI_ADMIN_EMAIL`：管理员账户的邮箱地址
- `WEBUI_ADMIN_PASSWORD`：管理员账户的密码
- `WEBUI_ADMIN_NAME`：（可选）管理员显示名称（默认为"Admin"）

Open WebUI 将自动：
1. 在启动时检查数据库中是否存在任何用户
2. 如果数据库为空（全新安装），使用提供的凭据创建管理员账户
3. 安全地对密码进行哈希处理并存储
4. 自动禁用注册（`ENABLE_SIGNUP=False`）以防止未经授权的账户创建

### 使用场景 {#use-cases}

此功能在以下场景特别有用：
- **CI/CD 流水线**：使用密钥管理系统中的凭据自动预配 Open WebUI 实例
- **Docker/Kubernetes 部署**：消除容器启动和手动创建管理员之间的时间间隔
- **自动化测试**：创建具有预配置管理员账户的可重现测试环境
- **无头服务器**：部署无法通过 UI 手动创建账户的实例

### 配置示例 {#example-configuration}

#### Docker Compose {#docker-compose}
```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - WEBUI_ADMIN_EMAIL=admin@example.com
      - WEBUI_ADMIN_PASSWORD=${ADMIN_PASSWORD}  # Use secrets management
      - WEBUI_ADMIN_NAME=System Administrator
    # ... other configuration
```

#### Kubernetes Secret {#kubernetes-secret}
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openwebui-admin
type: Opaque
stringData:
  admin-email: admin@example.com
  admin-password: your-secure-password
  admin-name: System Administrator
---
apiVersion: v1
kind: Pod
metadata:
  name: open-webui
spec:
  containers:
  - name: open-webui
    image: ghcr.io/open-webui/open-webui:main
    env:
    - name: WEBUI_ADMIN_EMAIL
      valueFrom:
        secretKeyRef:
          name: openwebui-admin
          key: admin-email
    - name: WEBUI_ADMIN_PASSWORD
      valueFrom:
        secretKeyRef:
          name: openwebui-admin
          key: admin-password
    - name: WEBUI_ADMIN_NAME
      valueFrom:
        secretKeyRef:
          name: openwebui-admin
          key: admin-name
```

### 重要说明 {#important-notes}

:::warning 安全注意事项
- **使用密钥管理**：切勿在 Docker Compose 文件或 Dockerfile 中硬编码 `WEBUI_ADMIN_PASSWORD`。请使用 Docker secrets、Kubernetes secrets 或环境变量注入。
- **强密码**：在生产部署中使用强且唯一的密码。
- **设置后更改**：考虑在初始部署后通过 UI 更改管理员密码以提高安全性。
- **自动禁用注册**：创建管理员账户后，注册将自动禁用。如果需要，可以稍后通过**设置 > 通用**（管理员区域）重新启用。
:::

:::info 行为详情
- **仅在全新安装时**：管理员账户**仅**在数据库中没有用户时创建。如果用户已存在，这些环境变量将被忽略。
- **密码哈希**：密码使用与手动账户创建相同的机制进行安全哈希，确保安全性。
- **一次性操作**：这是首次启动时的一次性操作。使用相同环境变量的后续重启不会修改现有管理员账户。
:::

有关这些环境变量的完整文档，请参阅[环境配置指南](/reference/env-configuration#webui_admin_email)。
