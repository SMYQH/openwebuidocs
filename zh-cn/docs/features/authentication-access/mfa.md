---
sidebar_position: 200
title: "双因素登录（MFA）"
---

# 双因素登录（MFA）{#two-factor-sign-in-mfa}

**要求每位用户每次登录时都提供来自身份验证器应用的验证码。**

开启多因素认证（MFA）后，登录需要两步：先是常规密码（或 LDAP、SSO、可信标头登录），然后是用户手机或电脑上身份验证器应用给出的六位验证码。任何支持基于时间的一次性验证码的应用都可以，例如 Proton Authenticator、Aegis、Bitwarden、Bitwarden Authenticator、Microsoft Authenticator、1Password 或 Google Authenticator。这样，仅凭被盗的密码已不足以进入账户。

该设置覆盖实例上的每一位用户。尚未设置身份验证器的用户会在下次登录时被引导完成设置。

---

## 环境要求 {#requirements}

- **已开启认证。** [`WEBUI_AUTH`](/reference/env-configuration#webui_auth) 必须保持默认的 `True`。
- **已开启持久化配置。** [`ENABLE_PERSISTENT_CONFIG`](/reference/env-configuration#enable_persistent_config) 必须保持默认的 `True`。
- **一个稳定的加密密钥。** 每个用户身份验证器的密钥都经过加密后存放在数据库中。该密钥派生自 [`WEBUI_SECRET_KEY`](/reference/env-configuration#webui_secret_key)，或在设置了 [`MFA_ENCRYPTION_KEY`](/reference/env-configuration#mfa_encryption_key) 时取自后者。如果在用户注册之后密钥发生变化，他们的身份验证器将无法再被读取。

在 MFA 开启期间，Open WebUI 会在启动时检查以上全部条件，并在认证或持久化配置关闭、`MFA_ENCRYPTION_KEY` 不是有效密钥、或已存储的身份验证器密钥无法用当前密钥解密时拒绝启动。在最后一种情况下，日志会显示 `ValueError: Stored MFA secrets cannot be decrypted. Restore the WEBUI_SECRET_KEY or MFA_ENCRYPTION_KEY they were encrypted with.`。请恢复先前的密钥，让实例重新运行起来。

---

## 开启 {#turning-it-on}

1. 打开 **Settings > Authentication**（管理员区域）。
2. 在 **Multi-factor authentication** 区域中，打开 **Require an authenticator for all users**。
3. 可选地打开其下方出现的一项或两项豁免：
   - **Allow OAuth sign-in without an authenticator**：通过你的 OAuth 或 OIDC 提供方登录的用户可跳过验证码。当提供方本身已经强制要求第二因素时使用它。
   - **Allow trusted-header sign-in without an authenticator**：通过[可信标头认证](/features/authentication-access/auth/sso#trusted-header)进入的用户可跳过验证码。当你的认证代理已经强制要求第二因素时使用它。
4. 点击 **Save**。

![Settings > Authentication（管理员区域） 中的 Multi-factor authentication 区域，其中 Require an authenticator for all users 已开启，下方是 OAuth 与可信标头豁免项](/images/features/auth/mfa-admin-setting.webp)

:::warning 保存改动会让所有人退出登录
对这三个开关的任何改动都会让每位用户在所有设备上退出登录（包括你自己），你会回到登录页。已设置身份验证器的用户需要输入验证码；尚未设置的用户则当场完成设置。
:::

只有管理员的登录会话才能修改这些开关；使用 API key 发出的请求会被拒绝。

同样的开关也可以通过环境变量设置：[`ENABLE_MFA`](/reference/env-configuration#enable_mfa)、[`MFA_ALLOW_OAUTH_BYPASS`](/reference/env-configuration#mfa_allow_oauth_bypass) 和 [`MFA_ALLOW_TRUSTED_HEADER_BYPASS`](/reference/env-configuration#mfa_allow_trusted_header_bypass)。它们设定的是首次启动时的初始值；此后以管理面板中保存的值为准。

---

## 登录 {#signing-in}

在 MFA 开启期间，仍在等待管理员审批的账户不会获得会话：对它的每次登录都会停在登录页并显示固定提示 **Your account is awaiting administrator approval.**。通过 [`PENDING_USER_OVERLAY_TITLE`](/reference/env-configuration#pending_user_overlay_title) 和 [`PENDING_USER_OVERLAY_CONTENT`](/reference/env-configuration#pending_user_overlay_content) 设置的自定义待审批浮层需要会话才能显示，因此它只在 MFA 关闭时出现。

### 设置身份验证器 {#setting-up-an-authenticator}

MFA 开启后用户第一次登录时：

1. 他们像平时一样用密码登录。
2. Open WebUI 显示带有二维码的 **Set up your authenticator**。他们用身份验证器应用扫描该二维码，或打开 **Enter the key manually** 把密钥手动输入应用。该条目在应用中显示为 **Open WebUI**，并附带他们的邮箱地址。
3. 他们输入应用上显示的六位验证码。
4. Open WebUI 一次性显示十个**恢复码**。他们可以下载这些恢复码，必须确认已保存好，随后即完成登录。

![Set up your authenticator 界面，含二维码、Enter the key manually 以及身份验证器验证码输入框](/images/features/auth/mfa-setup-qr.webp)

![Save your recovery codes 界面，列出十个恢复码，并提供 Download recovery codes 与确认复选框](/images/features/auth/mfa-recovery-codes.webp)

每个恢复码只能使用一次，可以替代身份验证器验证码使用。它们是手机丢失后重新登录的途径，因此用户应把它们保存在安全且与手机分开的地方。

### 之后的每次登录 {#every-later-sign-in}

输入密码后，Open WebUI 会要求提供当前的六位验证码。**Use a recovery code** 可把输入框切换为填写已保存的恢复码。

验证码每 30 秒变化一次。Open WebUI 也会接受当前验证码的前一个和后一个，以吸收细小的时钟差异；每个验证码只会被接受一次。第二步必须在输入密码后的五分钟内完成，超时后用户需要从密码重新开始。

---

## 管理你的身份验证器 {#managing-your-authenticator}

用户可以在 **Settings > Account > Multi-factor authentication** 下找到自己的身份验证器。它会显示是否已设置身份验证器以及还剩多少恢复码。只有当其登录方式确实需要身份验证器时该区域才会显示：即 MFA 已开启且其登录方式不在豁免之列。在那里，**Manage** 提供两个操作：

- **Replace authenticator**：把账户迁移到新的应用或手机。确认新身份验证器后，会显示一组新的十个恢复码。
- **Generate recovery codes**：签发十个新的恢复码，旧的恢复码随即失效。

两个操作都需要当前的身份验证器验证码（或恢复码），并且登录时间需在最近五分钟内。若登录时间更早，Open WebUI 会先要求用户 **Sign in again**。两个操作都会让该账户在所有设备上退出登录，包括执行该操作的设备。

---

## 恢复丢失的身份验证器 {#recovering-a-lost-authenticator}

当用户同时丢失了身份验证器和恢复码时，需要由拥有服务器 shell 访问权限的人重置其 MFA。请先核实此人身份，然后运行：

```bash
open-webui mfa reset user@example.com --reason "Lost phone, identity confirmed by video call"
```

在 Docker 镜像中，请通过容器内的 Python 运行同样的命令：

```bash
docker exec -it open-webui python -c "from open_webui import app; app()" mfa reset user@example.com --reason "Lost phone, identity confirmed by video call"
```

该命令会：

1. 移除该用户的身份验证器与恢复码，并让其退出所有设备。
2. 打印一个**恢复令牌**，它只能使用一次，并在 30 分钟后过期。

请通过你信任的渠道把该令牌发送给用户。他们下次登录时先输入密码，然后在 **Operator recovery token** 字段中输入该令牌，接着设置新的身份验证器，并像首次设置时那样获得新的恢复码。如果令牌未被使用就过期了，请重新运行该命令获取新的令牌。

必须提供原因。该命令必须针对与服务器相同的数据库运行，并需要相同的 `WEBUI_SECRET_KEY`：它从环境变量读取该密钥，或从当前目录下的 `.webui_secret_key` 文件读取。

---

## 尝试次数限制 {#attempt-limits}

在 MFA 开启期间，Open WebUI 会限制登录尝试的频率：

| 限制 | 适用范围 |
|---|---|
| 每个账户每 15 分钟 10 次 | 密码与 LDAP 登录。成功次数同样计入。 |
| 每个账户每 15 分钟 10 次 | 为该账户输入的身份验证器验证码与恢复码。 |
| 每次登录 5 次 | 在一次登录中输入的验证码。超出后用户需从密码重新开始。 |
| 每个 IP 地址每 15 分钟 100 次 | 会改动认证 API 状态的请求：登录、注册、MFA 步骤、修改密码，以及 `/api/v1/auths` 下的其他账户操作。 |

配置了 Redis 时，按地址计算的限制会在所有工作进程和副本之间共享；否则按进程分别计算。它依赖真实的客户端地址，因此请把 [`FORWARDED_ALLOW_IPS`](/reference/env-configuration#forwarded_allow_ips) 设置为你的反向代理地址。

---

## API 访问与自动化 {#api-access-and-automation}

- **API key 不受影响。** 它们无需验证码即可继续工作，因此脚本和集成应使用 [API key](/features/authentication-access/api-keys)。
- **通过 API 登录**时，只要该登录需要验证码，返回的就是一个 MFA 步骤而非会话令牌。[OAuth 令牌交换](/reference/env-configuration#enable_oauth_token_exchange)端点同理，除非 OAuth 登录被豁免。
- MFA 开启期间，通过 API **将用户添加为管理员**时，返回的新账户不含会话令牌。

---

## 事件与日志 {#events-and-logs}

Open WebUI 会发出下列事件。[事件函数](/features/extensibility/plugin/functions/event)会在其中之一触发时运行你自己的 Python 代码，例如在某个账户不断出现错误验证码时提醒你的安全团队、在有人修改 MFA 开关时通知管理员，或把注册与恢复码使用情况记录到外部系统中：

| 事件 | 何时触发 |
|---|---|
| `auth.mfa.enrolled` | 用户设置了自己的身份验证器。 |
| `auth.mfa.replaced` | 用户更换了自己的身份验证器。 |
| `auth.mfa.failed` | 输入了错误或已使用过的验证码。 |
| `auth.mfa.recovery_used` | 使用了恢复码。 |
| `auth.mfa.recovery_codes_regenerated` | 用户生成了新的恢复码。 |
| `auth.mfa.policy_changed` | 管理员修改了 MFA 开关。 |

上述每个事件，以及因触及按账户限制而被拒绝的登录，都会以 `MFA security event` 的形式写入服务器日志；启用审计日志时还会写入[审计日志](/getting-started/advanced-topics/hardening#audit-logging)。
