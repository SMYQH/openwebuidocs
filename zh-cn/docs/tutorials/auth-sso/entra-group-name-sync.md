---
sidebar_position: 40
title: "Entra ID 群组名称同步"
---

# Microsoft Entra ID 群组名称同步

:::warning
本教程由社区贡献，不受 Open WebUI 团队官方维护或审核。它仅作为演示，说明如何根据你的具体场景自定义 Open WebUI。想参与贡献？请查看贡献教程。
:::

默认情况下，当您为 Open WebUI 配置 Microsoft Entra ID OAuth 和自动群组创建时，安全组会使用其**群组 ID（GUID）**而非人类可读的群组名称进行同步。这是 Microsoft 的一个限制——ID 令牌默认不包含群组显示名称。

本教程说明如何配置 Microsoft Entra ID 以返回群组**名称**而非 ID，从而在 Open WebUI 中使用群组时获得更好的用户体验。

## 前提条件

- 已配置 [Microsoft OAuth](/features/authentication-access/auth/sso#microsoft) 的 Open WebUI 实例
- 具有修改应用注册权限的 Azure 账户
- 可访问 Microsoft Entra 管理中心
- 对 Microsoft Entra ID 应用程序配置有基本了解

## 概述

要在 Open WebUI 中获取人类可读的群组名称，需要：

1. 配置应用注册以在令牌中包含群组
2. 修改应用程序清单以使用 `cloud_displayname`
3. 将 `groupMembershipClaims` 设置为仅 `ApplicationGroup`
4. 将安全组分配给企业应用程序
5. 为 [OAuth 群组管理](/features/authentication-access/auth/sso#oauth-group-management) 配置 Open WebUI 环境变量

:::info 关键要求

清单中的 `cloud_displayname` 属性**仅在** `groupMembershipClaims` 设置为 `ApplicationGroup` 时有效。如果包含其他选项（如 `SecurityGroup` 或 `All`），令牌将恢复使用群组 ID 而非名称。

:::

## 步骤 1：在应用注册中配置令牌声明

1. 导航至 **Microsoft Entra 管理中心** > **App registrations（应用注册）**
2. 选择您的 Open WebUI 应用程序
3. 在左侧菜单中转到 **Token configuration（令牌配置）**
4. 点击 **Add groups claim（添加群组声明）**
5. 选择 **Security groups（安全组）**（或适合您需求的群组类型）
6. 在 **Customize token properties by type（按类型自定义令牌属性）** 下，确保为以下令牌类型添加群组：
   - ID 令牌
   - 访问令牌
7. 点击 **Add（添加）**

## 步骤 2：修改应用程序清单

这是启用群组名称而非 ID 的关键步骤。

1. 在应用注册中，在左侧菜单中转到 **Manifest（清单）**
2. 找到 `optionalClaims` 部分
3. 为每种令牌类型在 `additionalProperties` 数组中添加 `cloud_displayname`

清单应如下所示：

```json
"optionalClaims": {
    "idToken": [
        {
            "name": "groups",
            "source": null,
            "essential": false,
            "additionalProperties": [
                "cloud_displayname"
            ]
        }
    ],
    "accessToken": [
        {
            "name": "groups",
            "source": null,
            "essential": false,
            "additionalProperties": [
                "cloud_displayname"
            ]
        }
    ],
    "saml2Token": [
        {
            "name": "groups",
            "source": null,
            "essential": false,
            "additionalProperties": [
                "cloud_displayname"
            ]
        }
    ]
}
```

4. **关键**：将 `groupMembershipClaims` 设置为仅 `ApplicationGroup`：

```json
"groupMembershipClaims": "ApplicationGroup"
```

:::warning

如果 `groupMembershipClaims` 包含其他值（如 `SecurityGroup` 或 `All`），`cloud_displayname` 属性将被忽略，令牌将包含群组 ID 而非名称。有关更多详情，请参阅 [Microsoft 的可选声明文档](https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims)。

:::

5. 点击 **Save（保存）**

## 步骤 3：将群组分配给企业应用程序

使用 `ApplicationGroup` 时，只有明确分配给企业应用程序的群组才会包含在令牌中。

1. 导航至 **Microsoft Entra 管理中心** > **Enterprise applications（企业应用程序）**
2. 找到并选择您的 Open WebUI 应用程序
3. 在左侧菜单中转到 **Users and groups（用户和群组）**
4. 点击 **Add user/group（添加用户/群组）**
5. 选择要与 Open WebUI 同步的安全组
6. 点击 **Assign（分配）**

:::warning 多群组分配

当用户属于多个群组时，确保所有相关群组都已分配给企业应用程序。请注意，只有在此处明确分配的群组才会出现在用户的令牌中，并随后同步到 Open WebUI。

:::

## 步骤 4：配置 API 权限

确保您的应用注册具有所需的 Microsoft Graph 权限：

1. 在应用注册中，转到 **API permissions（API 权限）**
2. 点击 **Add a permission（添加权限）** > **Microsoft Graph** > **Delegated permissions（委托权限）**
3. 如果尚未添加，请从 OpenID 部分添加以下权限：
   - `openid`
   - `email`
   - `profile`
4. 点击 **Grant admin consent for [your organization]（为 [您的组织] 授予管理员同意）**

## 步骤 5：配置 Open WebUI 环境变量

为您的 Open WebUI 部署配置以下环境变量。有关每个变量的更多详情，请参阅[环境变量文档](/reference/env-configuration)。

```bash
# 必填：您的 WebUI 公共地址
WEBUI_URL=https://your-open-webui-domain

# Microsoft OAuth 配置（必填）
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_CLIENT_TENANT_ID=your_tenant_id
MICROSOFT_REDIRECT_URI=https://your-open-webui-domain/oauth/microsoft/callback

# 正确退出所需
OPENID_PROVIDER_URL=https://login.microsoftonline.com/your_tenant_id/v2.0/.well-known/openid-configuration

# 启用 OAuth 注册
ENABLE_OAUTH_SIGNUP=true

# OAuth 群组管理
OAUTH_GROUP_CLAIM=groups
ENABLE_OAUTH_GROUP_MANAGEMENT=true
ENABLE_OAUTH_GROUP_CREATION=true

# 推荐：设置一致的密钥
WEBUI_SECRET_KEY=your_secure_secret_key
```

### 环境变量参考

| 变量 | 默认值 | 描述 |
| ------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `OAUTH_GROUP_CLAIM`             | `groups` | ID/访问令牌中包含用户群组成员资格的声明。 |
| `ENABLE_OAUTH_GROUP_MANAGEMENT` | `false`  | 设置为 `true` 时，每次登录时用户群组成员资格将与 OAuth 声明同步。 |
| `ENABLE_OAUTH_GROUP_CREATION`   | `false`  | 设置为 `true` 时，启用**即时（JIT）群组创建**——OAuth 声明中存在但 Open WebUI 中不存在的群组将自动创建。 |

:::warning 严格群组同步

当 `ENABLE_OAUTH_GROUP_MANAGEMENT` 设置为 `true` 时，用户在 Open WebUI 中的群组成员资格将在每次登录时与其 OAuth 声明中收到的群组**严格同步**。

- 用户将被**添加**到与其 OAuth 声明匹配的 Open WebUI 群组中。
- 如果某个 Open WebUI 群组（包括在 Open WebUI 中手动分配的群组）**不**存在于该登录会话的 OAuth 声明中，用户将被从该群组中**移除**。

:::

## 验证

完成配置后：

1. **测试令牌**：使用 [https://jwt.ms](https://jwt.ms) 解码您的 ID 令牌，验证 `groups` 声明包含显示名称而非 GUID。
2. **以非管理员用户身份登录**：管理员用户的群组成员资格不会通过 OAuth 群组管理自动更新。使用标准用户账户进行测试。
3. **检查 Open WebUI**：导航至管理面板，验证群组显示的是可读名称。

:::info 管理员用户

管理员用户的群组成员资格**不会**通过 OAuth 群组管理自动更新。如果需要测试配置，请使用非管理员用户账户。

:::


## 混合 AD 群组（本地 Active Directory）

上面描述的 `cloud_displayname` 方法适用于**云原生**的 Entra ID 安全组。但如果你所在组织将群组从**本地 Active Directory** 同步到 Entra ID，那么即使按上面的步骤配置，这些同步过来的群组在 Open WebUI 中仍可能以 GUID 的形式显示。

这是因为 `cloud_displayname` 只能解析源自 Entra ID 的群组名称。从本地 AD 同步过来的群组需要不同的令牌配置。

### 解决方法：对混合群组使用 sAMAccountName

1. 在 **Azure 门户**中，导航到你的 **App Registration**
2. 进入 **Token configuration**
3. 如果已有群组声明，点击它进行编辑；否则点击 **Add groups claim**
4. 在 **ID** 令牌类型下，将群组标识符格式设置为 **sAMAccountName**
5. 点击 **Save**

这会告诉 Entra ID 在 AD 同步过来的群组中包含本地 `sAMAccountName` 属性，从而解析为人类可读的群组名称。

:::info 混合环境

如果你的环境中**同时存在**云原生和本地 AD 同步的群组，使用 `sAMAccountName` 也能正确解析这两种类型的群组名称。

:::

## 其他资源

- [SSO（OAuth、OIDC、Trusted Header）](/features/authentication-access/auth/sso) - OAuth 配置概览
- [OAuth 群组管理](/features/authentication-access/auth/sso#oauth-group-management) - 群组同步详情
- [群组管理](/features/authentication-access/rbac/groups) - Open WebUI 中的群组管理
- [SSO 故障排查指南](/troubleshooting/sso) - 常见 OAuth 问题与解决方案
- [环境变量配置](/reference/env-configuration) - 所有环境变量
- [Microsoft 可选声明文档](https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims) - Microsoft 官方文档
