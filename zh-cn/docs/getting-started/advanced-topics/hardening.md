---
sidebar_position: 4
title: "强化 Open WebUI 安全"
---

<a id="hardening-open-webui"></a>

# 强化 Open WebUI 安全 {#hardening-open-webui}

Open WebUI 是一个自托管应用，会向已认证用户提供模型推理、工具执行、代码流水线等能力。与数据库、容器仓库、CI 服务器等其他自托管基础设施一样，部署方需要自行管理运行环境、网络暴露方式和配置。Open WebUI 提供了本指南中介绍的控制项；具体如何配置，取决于你的环境与威胁模型。

本指南聚焦于可用于强化部署安全性的配置项。每一节都会说明某个设置的作用、默认值以及如何修改。它并不是一份面面俱到的安全手册；最终，保障部署安全仍是你的责任。你的运行环境、合规要求和威胁模型，将决定哪些项与你最相关。

## 网络放置 {#network-placement}
Open WebUI 的设计预期是运行在私有、可信网络中，类似数据库、容器仓库或 CI 服务器这类自托管基础设施。大多数部署都会放在企业防火墙、VPN 或其他仅允许已知用户访问的网络边界之后。

对于把安全放在优先位置的组织，推荐将 Open WebUI 放在以下一种或多种保护层之后：

- VPN（WireGuard、Tailscale）
- Zero Trust 访问代理（Cloudflare Access、Pomerium）
- 带认证与 IP allowlist 的反向代理

DDoS 防护和暴力破解防护（限速、连接节流、fail2ban）应由代理层或网络层承担。

### 请求不存在的路径 {#requests-for-paths-that-do-not-exist}

Open WebUI 提供的是单页应用，因此请求应用不认识的路径时，返回的是应用外壳且状态为 200，而不是 404。对 JavaScript 文件的请求是例外，它们会返回 404，因为缺失的脚本必须失败，而不能被塞给浏览器一页 HTML。

看得见的后果出现在访问日志中。自动化扫描器会对它们发现的每个主机探测同样的一批路径——`/wp-admin/`、`/phpmyadmin`、`.env` 之类——而每一次这样的探测都会得到一个 200 的响应。什么都没有被发现，也没有什么被暴露，因为每个访客收到的都是同一个外壳，但日志给人的印象却是这些请求成功了。

过滤这类流量应该交给反向代理，与上面的限流和暴力破解防护放在一起。代理可以在这些路径到达应用之前就回应或丢弃它们，这样它们根本不会进入日志，也不会给应用带来任何开销。如果在 Open WebUI 内部拦截它们，就意味着要维护一份扫描器当前使用的路径清单，而这份清单需要永远更新下去。

如果你是第一次部署 Open WebUI，可以先看本页底部的[速查表](#quick-reference)以获得一份按优先级排序的摘要，再阅读与你的部署相关的小节。

---

## 密钥 {#secret-key}
`WEBUI_SECRET_KEY` 用于签署 JWT（登录令牌），并为 OAuth 会话数据派生加密密钥。

**需要显式设置它的场景：**

如果你在负载均衡器后面运行多个 Open WebUI 实例，每个实例必须共用同一个密钥。否则，一个实例签发的令牌会被另一个实例拒绝，导致登录失败。使用 `openssl rand -base64 32` 生成密钥，并通过环境变量传给所有副本。

**轮换：** 更换密钥会使所有现有会话失效，用户需要重新登录。如果开启了[双因素登录](#two-factor-sign-in)，用户的验证器密钥会用从 `WEBUI_SECRET_KEY` 派生的密钥加密；一旦用户完成注册，轮换后 Open WebUI 将拒绝启动。请在用户注册之前设置 [`MFA_ENCRYPTION_KEY`](/reference/env-configuration#mfa_encryption_key)，这样才能自由轮换 `WEBUI_SECRET_KEY`。已安装的 [App](/features/channels/apps) 在轮换后会停止连接；请卸载每个 App，用其 API 密钥重新连接，并把它们加回各自的频道（参见 [WEBUI_SECRET_KEY 变更后 App 停止连接](/features/channels/apps#apps-stop-connecting-after-webui_secret_key-changed)）。

---

## 认证与注册 {#authentication-and-signup}

### 注册 {#registration}

注册在第一个用户创建前保持开放，该用户会自动成为管理员。此后，注册会自动关闭，无需额外配置。

新账户的默认角色是 `pending`，这意味着管理员批准之前，用户无法访问任何功能。即使管理员重新启用注册（`ENABLE_SIGNUP=true`），`pending` 这一默认角色仍可确保新用户不会在未批准前直接进入系统。

```bash
# 新用户会先进入 "pending" 状态，等待管理员批准（默认行为）
DEFAULT_USER_ROLE=pending
```

### 密码校验 {#password-validation}

默认情况下，Open WebUI 不强制密码复杂度。要启用：

```bash
ENABLE_PASSWORD_VALIDATION=true
PASSWORD_VALIDATION_REGEX_PATTERN='^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$'
PASSWORD_VALIDATION_HINT='Minimum 8 characters with uppercase, lowercase, number, and special character.'
```

密码在存储前会使用 bcrypt 哈希。由于 bcrypt 会在 72 字节处截断输入，Open WebUI 也会强制这一限制。

### 通过环境变量创建管理员账户 {#admin-account-from-environment-variables}

对于自动化部署，你可以在启动时直接创建管理员账户：

```bash
WEBUI_ADMIN_EMAIL=admin@yourcompany.com
WEBUI_ADMIN_PASSWORD=your-strong-password
WEBUI_ADMIN_NAME=Admin
```

这只会在数据库中还没有任何用户时生效。管理员创建完成后，注册会自动关闭。

### 仅使用 SSO 的环境 {#sso-only-environments}

如果所有认证都交由 OAuth/OIDC 提供商处理，你可以完全隐藏本地登录表单：

```bash
ENABLE_LOGIN_FORM=false
```

这会从 UI 中移除邮箱/密码登录入口，引导所有用户走 SSO 流程。同一个开关就是 **设置 > 认证**（管理员区域）中的 **登录表单**，因此 SSO 生效后无需重启即可将其关闭。你也可以在后端层面禁用本地密码认证：

```bash
ENABLE_PASSWORD_AUTH=false
```

如果你希望“登录页密码行为”和“账号页改密行为”分开控制，还可以隐藏 **Settings > Account** 中的修改密码表单：

```bash
ENABLE_PASSWORD_CHANGE_FORM=false
```

这对于以 SSO 为主的部署很有用，因为本地密码改动本就不应对用户展示。

---

### 双因素登录 {#two-factor-sign-in}

Open WebUI 可以要求所有用户在每次登录后提供来自身份验证器应用的验证码：

```bash
ENABLE_MFA=true
```

同一个开关在 **设置 > 认证**（管理员区域） 的 **多因素身份验证** 部分中名为 **要求所有用户使用身份验证器**。当你的身份提供商或代理已经强制要求第二因素时，OAuth 和受信任请求头登录可以被豁免（`MFA_ALLOW_OAUTH_BYPASS`、`MFA_ALLOW_TRUSTED_HEADER_BYPASS`）。更改其中任何一项设置都会让所有用户退出登录。启用 MFA 期间，登录尝试还会按账户和按客户端地址进行限制。有关注册、恢复和这些限制，请参阅[双因素登录（MFA）](/features/authentication-access/mfa)。

---

## 会话与 Cookie 安全 {#session-and-cookie-security}

### Cookie 设置 {#cookie-settings}

当通过 HTTPS 提供 Open WebUI 服务时（见 [HTTPS 配置](/reference/https)），建议同时这样配置 Cookie：

```bash
WEBUI_SESSION_COOKIE_SECURE=true
WEBUI_SESSION_COOKIE_SAME_SITE=strict
```

| 变量 | 默认值 | 作用 |
|---|---|---|
| `WEBUI_SESSION_COOKIE_SECURE` | `false` | 设为 `true` 后，Cookie 只会通过 HTTPS 发送 |
| `WEBUI_SESSION_COOKIE_SAME_SITE` | `lax` | 控制 Cookie 是否会随跨站请求发送，`strict` 保护最强 |

除非分别用 `WEBUI_AUTH_COOKIE_SECURE` 和 `WEBUI_AUTH_COOKIE_SAME_SITE` 覆盖，否则这些设置同样会作用于 OAuth Cookie。

### Token 过期时间 {#token-expiry}
JWT 决定用户保持登录状态的时间。默认是 `4w`（4 周）。你可以缩短它：

```bash
JWT_EXPIRES_IN=24h
```

设置 `JWT_EXPIRES_IN=-1` 会完全关闭令牌过期。如果这样设置，Open WebUI 会记录一条警告。

[Tether](/ecosystem/tether) 等原生应用改用可续期会话，这类会话在闲置 [`SESSION_EXPIRES_IN`](/reference/env-configuration#session_expires_in) 后结束（默认 `90d`）。退出应用、通过 [Session API](/reference/tether-client-protocol#session-api) 删除会话，以及下文提到的每种全账户登出，都会立即吊销此类会话，无论是否使用 Redis。

### Token 撤销 {#token-revocation}

把账户从所有设备登出这一操作会记录在数据库中，无论是否使用 Redis 都会生效。它会在以下情况发生：

- 用户修改了自己的密码，或管理员为其设置了新密码。
- 管理员在用户编辑对话框中点击了 **登出所有设备**（参见[将用户从所有设备登出](/features/authentication-access/rbac/roles#signing-a-user-out-of-every-device)）。
- 用户设置或更换了验证器，或生成了新的恢复码，或运维人员重置了其 MFA。
- 管理员修改了[两步验证](#two-factor-sign-in)设置，这会登出所有账户。

从那一刻起，此前为该账户签发的每一个 token 都会被拒绝。该账户的实时连接会被关闭，该用户正在进行的自动化和子智能体运行也会失去访问权限。每个已打开的实时连接每 30 秒还会重新校验一次，一旦其会话被吊销或已过期就会被关闭。API key 仍然有效；请删除或重新生成 key 以切断它。该检查会在每个请求时读取数据库，数据库无法访问时请求会被拒绝。

停用账户会保留已为它签发的 token，但账户角色会在每个请求时重新校验。请同时使用 **登出所有设备** 来结束其会话。

:::warning 单个会话的登出需要 Redis

如果没有 Redis，**登出不会使该会话的 token 失效**。该 token 会一直保持有效，直到自然过期（默认 4 周）。这意味着：

- 被盗或泄露的 token 无法通过登出来撤销；**登出所有设备** 或修改密码才能终止它
- OIDC back-channel logout 无法撤销 token

配置 Redis 后，登出会把该 token 加入一个会自动过期的撤销列表，而 OIDC back-channel logout 会让受影响的用户从所有设备登出。这才是面向生产的预期行为。

**撤销检查采用 fail-open 策略。** 无法访问 Redis 的撤销检查会接受该 token，并且每个工作进程最多每分钟记录一次 `Revocation check failed; accepting token`。因此 Redis 故障期间，实例会退回到上面列出的无 Redis 行为，登出不会生效——请把 Redis 的可用性视为认证面的一部分，并针对这条日志配置告警。

**如果你暂时无法部署 Redis**， 请缩短 `JWT_EXPIRES_IN`（例如 `1h` 或 `4h`）以缩小暴露窗口。Redis 配置请参考 [Redis 教程](/tutorials/integrations/redis)。

:::
---

## 跨域资源共享（CORS） {#cors}

跨域资源共享（CORS）决定了哪些网站可以在浏览器中向你的 Open WebUI API 发起请求。例如，如果你的实例部署在 `https://chat.yourcompany.com`，CORS 就决定了来自其他域名脚本是否可以与它交互。

默认 `CORS_ALLOW_ORIGIN` 为 `*`，意味着允许任意来源。Open WebUI 在启动时会对此发出警告。

如需限制到你的域名：

```bash
CORS_ALLOW_ORIGIN=https://chat.yourcompany.com
```

多个来源之间用分号分隔：

```bash
CORS_ALLOW_ORIGIN=https://chat.yourcompany.com;https://internal.yourcompany.com
```

如果你想完全禁用 CORS，可以将其设置为[无效域名](https://en.wikipedia.org/wiki/.invalid)：

```bash
CORS_ALLOW_ORIGIN=http://cors.invalid
```

如果你使用带自定义 URL scheme 的桌面应用，可通过以下方式加入：

```bash
CORS_ALLOW_CUSTOM_SCHEME=app
```

---

## 安全响应头 {#security-headers}
Open WebUI 内置了 `SecurityHeadersMiddleware`，它会向响应中注入 HTTP 安全响应头。默认一个都不设置，你需要通过环境变量逐个选择开启。每项可接受的值和回退行为都列在环境变量参考的[安全响应头](/reference/env-configuration#security-headers)一节中。

以下是面向生产部署的推荐起始配置：

```bash
# HTTP Strict Transport Security：告诉浏览器只使用 HTTPS
HSTS=max-age=31536000;includeSubDomains

# 防止页面被嵌入其他站点的 iframe
XFRAME_OPTIONS=DENY

# 防止浏览器进行 MIME 类型嗅探
XCONTENT_TYPE=nosniff

# 控制随请求发送多少引用来源信息
REFERRER_POLICY=strict-origin-when-cross-origin

# 限制对浏览器功能的访问
PERMISSIONS_POLICY=camera=(),microphone=(),geolocation=()

# 内容安全策略
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'

# 仅报告模式的内容安全策略（记录违规但不强制执行）
CONTENT_SECURITY_POLICY_REPORT_ONLY=default-src 'self'; report-uri /csp-report

# 跨源隔离响应头
CROSS_ORIGIN_EMBEDDER_POLICY=require-corp    # 可选值：unsafe-none, require-corp, credentialless
CROSS_ORIGIN_OPENER_POLICY=same-origin       # 可选值：unsafe-none, same-origin-allow-popups, same-origin
CROSS_ORIGIN_RESOURCE_POLICY=same-origin     # 可选值：same-site, same-origin, cross-origin

# 上报 API 端点配置
REPORTING_ENDPOINTS=default="https://your-report-collector.example/reports"
```

:::tip

如果你要设置内容安全策略，请从宽松开始，逐步收紧。过于严格的 CSP 会破坏前端。可以用 `CONTENT_SECURITY_POLICY_REPORT_ONLY` 在强制执行前先测试策略。浏览器开发者工具会告诉你哪些资源被拦截了。

:::

:::warning 跨源隔离

同时设置 `CROSS_ORIGIN_EMBEDDER_POLICY=require-corp` 和 `CROSS_ORIGIN_OPENER_POLICY=same-origin` 会启用跨源隔离。除非这些资源明确设置了合适的 CORS 响应头，否则这可能会破坏从第三方来源加载的资源（例如外部图片、脚本或 iframe）。部署前请充分测试。

:::

---

## HTTPS 与 TLS {#https-and-tls}

Open WebUI 本身不负责 TLS 终止。请将它放在处理 HTTPS 的反向代理（Nginx、Caddy、HAProxy）之后。具体配置见 [HTTPS 配置](/reference/https)。

在 HTTPS 就位后：

```bash
WEBUI_SESSION_COOKIE_SECURE=true
HSTS=max-age=31536000;includeSubDomains
```

### 可信代理 IP {#trusted-proxy-ips}
[`FORWARDED_ALLOW_IPS`](/reference/env-configuration#forwarded_allow_ips) 决定哪些代理被信任可以发送 `X-Forwarded-For` 响应头。Docker 镜像、`open-webui serve` 和 `open-webui dev` 都会读取它。默认值为 `*`（信任全部），这只在前置一个会覆盖这些响应头的反向代理、且其他任何东西都无法访问后端时才合适。否则任何客户端都可以声称任意地址，这会破坏按地址的登录限制，并使审计日志中的地址失真。请将其限制为你的代理 IP：

```bash
FORWARDED_ALLOW_IPS=192.168.1.100
```

---

## OAuth 与 SSO {#oauth-and-sso}

如果你使用 OAuth/OIDC 提供商做认证，可以借助以下配置进一步控制访问范围。

### 域名与组限制 {#domain-and-group-restrictions}

```bash
# 只允许特定邮箱域名的用户登录
OAUTH_ALLOWED_DOMAINS=yourcompany.com

# 阻止特定 IdP 组
OAUTH_BLOCKED_GROUPS='["contractors-external", "temp-accounts"]'
```

### 角色映射 {#role-mapping}

将 IdP 角色映射到 Open WebUI 角色，让访问控制由身份提供商统一管理：

```bash
ENABLE_OAUTH_ROLE_MANAGEMENT=true
OAUTH_ROLES_CLAIM=roles
OAUTH_ADMIN_ROLES=admin,superadmin
OAUTH_ALLOWED_ROLES=user,admin,superadmin
```

### 账户合并 {#account-merging}

```bash
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=false
```

如果启用，当 OAuth 登录邮箱与已有本地账户一致时，系统会自动合并两者。**不建议启用。** 它依赖你的 OAuth 提供商可靠验证邮箱所有权。如果提供商无法保证邮箱已验证，那么控制同一邮箱的用户就可能接管已有账户。除非你已确认提供商强制执行邮箱验证，否则请保持 `false`。

### 会话限制 {#session-limits}

```bash
# 每个用户、每个提供商允许的最大并发 OAuth 会话数（默认：10）
OAUTH_MAX_SESSIONS_PER_USER=5

# 启用 IdP 发起的后端通道登出（需要 Redis）
ENABLE_OAUTH_BACKCHANNEL_LOGOUT=true
```

---

## 可信请求头认证 {#trusted-header-authentication}

如果你的反向代理本身负责认证（如 Authelia、Authentik、oauth2-proxy），它可以通过 HTTP 头把已认证用户身份传给 Open WebUI。**这种方式可行，但风险很大，具体取决于配置是否严谨**——配置错误会让任意客户端通过伪造请求头冒充任意用户：

```bash
WEBUI_AUTH_TRUSTED_EMAIL_HEADER=X-Forwarded-Email
WEBUI_AUTH_TRUSTED_NAME_HEADER=X-Forwarded-Name
```

:::warning

使用可信请求头时，你的代理**必须**先从客户端请求中剥离这些头，再注入自己可信的值。如果代理没有先剥离，任何客户端都可以自己发送伪造头并冒充任意用户。这是可信请求头认证最常见的错误配置。请查阅你的代理文档，确认如何清理上游请求头。

:::

---

## LDAP 认证 {#ldap}

如果你通过 LDAP 做认证，请启用 TLS 来保护传输中的凭据：

```bash
ENABLE_LDAP=true
LDAP_USE_TLS=true
LDAP_VALIDATE_CERT=true
LDAP_CA_CERT_FILE=/path/to/ca-cert.pem
```

如果不启用 TLS，LDAP 凭据会以明文传输。如有需要，你还可以通过 `LDAP_CIPHERS` 限制密码套件。

---

## 数据库 {#database}

### PostgreSQL {#postgresql}

对于生产部署，PostgreSQL 比默认 SQLite 提供更好的并发性与可靠性：

```bash
DATABASE_URL=postgresql://user:password@db-host:5432/openwebui
```

迁移步骤见[扩展指南](/getting-started/advanced-topics/scaling#step-1-switch-to-postgresql)。请使用强且唯一的凭据，并将数据库放在内部网络中。

### SQLCipher {#sqlcipher}
不支持 SQLCipher，设置 `DATABASE_TYPE=sqlite+sqlcipher` 时 Open WebUI 会拒绝启动。对于需要静态加密的 SQLite 部署，请把数据目录放在加密文件系统上（Linux 上的 LUKS、Windows 上的 BitLocker、macOS 上的 FileVault）。若要保留已有 SQLCipher 数据库中的数据，请先按照[升级现有的 SQLCipher 数据库](/reference/database-schema#upgrading-an-existing-sqlcipher-database)中的说明解密它。

### 连接池调优 {#connection-pool-tuning}

对于 PostgreSQL，请根据使用规模调整连接池：

```bash
DATABASE_POOL_SIZE=15
DATABASE_POOL_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

整个部署的总连接数 = 连接池大小 × 实例数。请确保这一数值低于 PostgreSQL 的 `max_connections`（默认 100）。

---

## API 密钥 {#api-keys}

API 密钥允许以创建者本人的权限，以编程方式访问 Open WebUI。

```bash
# 启用 API 密钥创建（默认：非管理员不可创建）
ENABLE_API_KEYS=true
```

### 端点限制 {#endpoint-restrictions}

你可以限制某个 key 能调用哪些 API 路由：

```bash
ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS=true
API_KEYS_ALLOWED_ENDPOINTS=/api/chat/completions,/api/v1/models
```

当你把 key 分发给外部服务或自动化系统时，这很有用——即使 key 泄露，也能降低它可访问的范围。

### 用户权限 {#user-permissions}

默认只有管理员可以创建 API 密钥。要允许普通用户创建：

```bash
USER_PERMISSIONS_FEATURES_API_KEYS=true
```

---

## 访问控制 {#access-control}

Open WebUI 使用分层权限模型：角色、用户组以及资源级访问授权共同生效。

### 角色 {#roles}

| 角色 | 能力 |
|---|---|
| `admin` | 完整系统访问、用户管理、所有配置项 |
| `user` | 聊天访问、已授权模型与资源 |
| `pending` | 在管理员批准前无访问权限 |

### 关键设置 {#key-settings}

```bash
# 新用户默认角色（默认：pending）
DEFAULT_USER_ROLE=pending

# 管理员是否绕过资源级访问控制（默认：true）
BYPASS_ADMIN_ACCESS_CONTROL=true

# 管理员是否可查看所有用户聊天（默认：true）
ENABLE_ADMIN_CHAT_ACCESS=true

# 是否所有用户都能访问所有模型，而不受组限制（默认：false）
BYPASS_MODEL_ACCESS_CONTROL=false
```

### OpenAI API 透传 {#openai-api-passthrough}

```bash
ENABLE_OPENAI_API_PASSTHROUGH=false
```

OpenAI 路由器包含一个兜底代理端点（`/{path:path}`），可以使用管理员配置的 API 密钥，把任意请求转发给上游兼容 OpenAI 的 API。**此功能默认关闭，也建议保持关闭。** 一旦启用，任意已认证用户都可以借助管理员凭据访问任意上游端点——包括 Open WebUI 本身并未原生支持的端点——而且不受模型级访问控制约束。除非你明确需要直通上游 API，并完全理解其安全影响，否则不要启用。

### 数据共享与导出 {#data-sharing-and-export}
有若干功能控制着数据可以如何被共享或导出：

```bash
# 显示 Open WebUI 社区的分享与发现选项（默认：true）
ENABLE_COMMUNITY_SHARING=true

# 允许管理员从数据库批量导出所有用户聊天（默认：true）
ENABLE_ADMIN_EXPORT=true

# 允许用户使用自己的 API 密钥直接连接模型提供商，绕过服务端代理（默认：false）
ENABLE_DIRECT_CONNECTIONS=false
```

`ENABLE_COMMUNITY_SHARING` 控制是否显示把聊天、模型、提示词、工具、Functions、Skills 和使用统计发送到 Open WebUI 社区的选项，以及发现社区内容的链接。设为 `false` 即可让一切都留在你自己的实例上。聊天分享链接是另一个独立功能：新建的链接默认保持私密，直到其所有者选择谁可以查看，参见[聊天分享](/features/chat-conversations/chat-features/chatshare)。

`ENABLE_DIRECT_CONNECTIONS` 开启后，允许用户在浏览器中配置自己的 API 密钥和模型端点。这些连接由后端发起，因此用户的 API 密钥会被发送到 Open WebUI 服务器。该功能默认关闭。

### Workspace 权限 {#workspace-permissions}

这些设置控制普通用户在共享工作区中的可操作范围：

```bash
USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS=false
USER_PERMISSIONS_WORKSPACE_KNOWLEDGE_ACCESS=false
USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS=false
USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS=false
```

默认都为 `false`。如需向特定用户组开放某些能力，可通过组级覆盖实现。

---

## 审计日志 {#audit-logging}

审计日志用于记录 API 活动，以满足合规、调试和使用分析需求。默认关闭。

```bash
AUDIT_LOG_LEVEL=METADATA
```

| 级别 | 记录内容 |
|---|---|
| `NONE` | 不记录（默认） |
| `METADATA` | 用户、IP、user agent、方法、URL、时间戳 |
| `REQUEST` | 元数据 + 请求体 |
| `REQUEST_RESPONSE` | 元数据 + 请求体和响应体 |

### 输出配置 {#output-configuration}

```bash
# 写入文件（默认路径：/app/backend/data/audit.log）
ENABLE_AUDIT_LOGS_FILE=true
AUDIT_LOGS_FILE_PATH=/app/backend/data/audit.log
AUDIT_LOG_FILE_ROTATION_SIZE=10MB

# 同时输出到 stdout，适合日志聚合器
ENABLE_AUDIT_STDOUT=true

# 每个请求/响应体最多记录的字节数（默认：2048）
MAX_BODY_LOG_SIZE=2048
```

### 路径过滤 {#path-filtering}
```bash
# 仅审计特定路径（白名单模式）
AUDIT_INCLUDED_PATHS=auths,users,configs

# 排除特定路径（黑名单模式，默认）
AUDIT_EXCLUDED_PATHS=/chats,/chat,/folders
```

无论路径排除规则如何，认证端点（登录、登出、注册以及 MFA 端点）始终会被审计。`/api/v1/auths` 和 `/oauth/` 下的请求在各层级都只记录其元数据，从而让密码、MFA 验证码和会话令牌不进入日志。其他地方，凡是字段名以 `password`、`secret`、`token`、`key` 或 `authorization` 结尾（或其复数形式，例如 `tokens`）的，无论大小写，在请求体和响应体中都会被遮蔽。这包括值列表以及被请求体大小限制截断的值。

每条记录都有一个 `model_id` 字段，表示客户端请求的模型。对于聊天和补全请求它会被填充：`/api/chat/completions`（同时也以 `/api/v1/chat/completions` 提供）、兼容 Anthropic 的 `/api/v1/messages`（同时也以 `/api/message` 提供）、`/openai/chat/completions`、`/openai/responses`，以及 `/ollama` 下的聊天、补全、Messages 和 Responses 请求。开启 [`ENABLE_OPENAI_API_PASSTHROUGH`](/reference/env-configuration#enable_openai_api_passthrough) 后，转发给 `/openai` 下提供方的每个请求也会记录其请求体中的 `model`。那些让 Open WebUI 转而调用模型的请求（例如 `/api/v1/tasks` 下的任务端点，或提及某个模型的频道消息）可以记录被调用的模型。其他请求则记录 `null`。`AUDIT_INCLUDED_PATHS` 只匹配 `/api/` 下的路由，因此设置它之后，`/openai` 和 `/ollama` 下的请求不会留下审计记录。无论 `MAX_BODY_LOG_SIZE` 如何设置，该字段都在各层级完整写入，因此仅凭 `METADATA` 就足以看出谁使用了哪个模型。默认排除项会跳过 `/api/chat/completions`，也就是聊天界面使用的端点。若要记录这些请求，请从列表中移除 `/chat`：

```bash
AUDIT_EXCLUDED_PATHS=/chats,/folders
```

记录聊天请求后，对 `/api/chat/completions` 请求的每次模型回复都会在请求记录旁边写下自己的审计条目。当回复调用工具时，模型在两次工具调用之间的每一轮回答各有一条。这类条目在 `model_id` 中记录作出回答的模型，并在 `usage` 中记录提供商报告的 token 计数（`input_tokens`、`output_tokens` 和 `total_tokens`）。它的 `extra.request_id` 保存该请求条目的 `id`，两者由此关联。提供商未报告 token 计数的回复不写这些计数。后台任务（例如标题和标签生成）同样不写。

在这些过滤范围内，审计日志覆盖携带凭据的 `POST`、`PUT`、`PATCH` 和 `DELETE` 请求（可通过 [`ENABLE_AUDIT_GET_REQUESTS`](/reference/env-configuration#enable_audit_get_requests) 加入 `GET`），以及上述认证端点。凭据是 `Authorization` 请求头（通常为 `Bearer`）、会话 cookie，或者 `x-api-key` 请求头中的 API 密钥（请求头名可通过 [`CUSTOM_API_KEY_HEADER`](/reference/env-configuration#custom_api_key_header) 重命名）。使用 API 密钥登录的请求会记在该密钥所有者名下。密钥错误的请求则不带用户记录。Socket.IO 流量在两种传输方式上都在其外，包括当 [`ENABLE_WEBSOCKET_SUPPORT`](/reference/env-configuration#enable_websocket_support) 关闭时浏览器使用的 `/ws/socket.io` 长轮询请求。

## 网络与外发请求 {#network-and-outbound-requests}

### 外发 TLS {#outbound-tls}

Open WebUI 会向模型 API、embedding 提供商、工具服务器和网页搜索服务发起外部 HTTPS 请求。默认会开启证书校验：

```bash
REQUESTS_VERIFY=true
AIOHTTP_CLIENT_SESSION_SSL=true
AIOHTTP_CLIENT_SESSION_TOOL_SERVER_SSL=true
ENABLE_WEB_LOADER_SSL_VERIFICATION=true
```

### 离线模式 {#offline-mode}

对于隔离网络环境：

```bash
OFFLINE_MODE=true
```

这会禁用 HuggingFace Hub 下载、版本更新检查，以及 embedding、reranking 和 Whisper 模型的自动更新。模型与 embeddings 必须已经在本地可用。

离线模式管理的是 Open WebUI 代表自己发起的连接。它并不会阻止你自己配置的连接，例如外部模型 API、OAuth 提供商、网络搜索、工具服务器或对象存储。真正能把它们隔离的，是在网络层面将实例隔离。有关仍然可用的功能完整列表，请参见 [`OFFLINE_MODE`](/reference/env-configuration#offline_mode)。

### SSRF 防护 {#ssrf-prevention}
RAG 网页加载器可以从 URL 抓取内容。默认情况下，它无法访问本地网络地址：

```bash
ENABLE_RAG_LOCAL_WEB_FETCH=false
```

将其设为 `true` 允许网页加载器从私有 IP 段抓取内容，这在某些环境中可能是必要的，但也会引入 SSRF 风险。

私有地址检查不仅检查 IPv6，还会查看其内部内容。像 `::ffff:169.254.169.254` 这样的地址，或包裹了 RFC 1918/回环目标的 6to4、Teredo 或 NAT64 地址，在 IPv6 层面是全局可路由的，却仍解析到内部位置；Open WebUI 会提取其中内嵌的 IPv4 地址，并据此阻止该次抓取。这既适用于 URL 校验阶段，也适用于连接阶段，因此返回这些形式的 DNS 解析结果同样会被拒绝。

Open WebUI 默认还会屏蔽云服务商的元数据端点（AWS `169.254.169.254`、GCP `metadata.google.internal`、Azure `metadata.azure.com`，以及阿里云 `100.100.100.200`）。你可以用额外的域名或 IP 扩展这份屏蔽列表：

```bash
WEB_FETCH_FILTER_LIST=!internal.yourcompany.com,!10.0.0.0/8
```

用 `!` 作为条目前缀表示屏蔽。

默认情况下，对外的 HTTP 请求也不会跟随 `3xx` 重定向。没有这道闸门时，攻击者提供的 URL 可以在最初提交的主机上通过白名单检查，随后再以 `302` 重定向到内部地址（RFC 1918、`127.0.0.1`、云元数据 IP），而这些地址未经过重新校验就被访问。默认设置在 RAG 网页加载器、图片加载、OAuth 预检、代码解释器登录以及工具服务器执行中关闭了这条绕过路径。除非你有特定需求（例如短链接 URL）且已部署其他 SSRF 防护，否则请保持默认：

```bash
AIOHTTP_CLIENT_ALLOW_REDIRECTS=false
```

[App](/features/channels/apps) 还有自己的一道闸门：App URL 必须使用 HTTPS 并解析到公网地址。Open WebUI 拒绝来自 App 的重定向，并始终验证其证书。[`APP_ALLOWED_PRIVATE_ORIGINS`](/reference/env-configuration#app_allowed_private_origins) 列出了允许在私有地址或纯 HTTP 上使用的 App 源。

### 头像图片 URL 转发 {#profile-image-url-forwarding}

用户和模型的头像图片端点可以发出 `302 Found` 重定向到 `profile_image_url` 中存储的任意来源，以便在 UI 中显示外部托管的头像（例如通过上游身份提供商的 Gravatar）。该重定向会导致用户的浏览器直接向外部来源发起请求，从而泄露客户端 IP、User-Agent 和 Referer 头。如果某个账户的 `profile_image_url` 被设置为攻击者控制的主机，就可以利用这一点对任何渲染其头像的人进行去匿名化。

要完全禁止重定向并改用捆绑的默认图片：

```bash
ENABLE_PROFILE_IMAGE_URL_FORWARDING=false
```

默认为 `true`，以便依赖外部头像的现有部署继续正常工作。Data URI 和同源/静态图片不受此标志影响——它们继续正常渲染。

存储为 base64 `data:` URI 的头像图片也受 MIME 类型白名单限制。默认为 `image/png,image/jpeg,image/gif,image/webp`；有意排除了 SVG，因为它可以携带内联 `<script>`。响应还会设置 `X-Content-Type-Options: nosniff`，防止浏览器将非图片负载嗅探为可执行类型。如需进一步缩小范围（例如仅 PNG/JPEG），请设置：

```bash
PROFILE_IMAGE_ALLOWED_MIME_TYPES=image/png,image/jpeg
```

### Iframe 内容安全策略 {#iframe-content-security-policy}

Open WebUI 会在 `srcdoc` iframe 中渲染 LLM 生成的和用户上传的 HTML，用于 Artifacts、代码/HTML 预览、文件预览和引用弹窗。这些 iframe 上的 `sandbox` 属性提供了基线隔离。对于希望限制渲染 HTML 能执行的操作（特别是外发网络请求）的部署，可以设置一个注入到每个 iframe 文档中的 CSP：

```bash
IFRAME_CSP=default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; connect-src 'none'
```

上面的示例允许内联脚本在沙箱内运行（大多数 artifacts 需要），但阻止所有 `fetch`/`XMLHttpRequest`/`WebSocket` 流量，适用于你不想让模型通过生成的 artifact 泄露会话数据的场景。请根据实际情况收紧或放宽；过于严格的策略会破坏合法的 artifacts。

### 文件上传限制 {#file-upload-limits}

默认情况下，上传文件既没有大小限制，也没有数量限制。为防止存储被占满，建议设置：

```bash
# 单文件最大大小（MB，默认无限制）
RAG_FILE_MAX_SIZE=50

# 单次上传操作的最大文件数（默认无限制）
RAG_FILE_MAX_COUNT=10

# 限制允许的文件扩展名（留空 = 全部允许）
RAG_ALLOWED_FILE_EXTENSIONS=.pdf,.txt,.md,.docx,.csv
```

---

## Tools、Functions 与 Pipelines {#tools-functions-and-pipelines}

Tools 和 Functions 会在你的服务器上执行任意 Python 代码，权限级别与 Open WebUI 进程本身相同。这是它们的工作机制，因此它们可以读取文件、发起网络请求、访问环境变量并与数据库交互。

关于其安全模型的详细说明，请参见 [安全策略](/security/security-policy#tools-functions-and-pipelines-security)。

由于 Tools 和 Functions 会执行服务端代码，因此任何拥有创建或导入权限的用户，实际上都等同于拥有 Open WebUI 进程级别的权限。这是扩展机制的天然属性。默认情况下，只有管理员可以创建和导入 Tools / Functions。下面这些设置用于控制相关权限。

### 完全禁用此功能 {#disabling-the-feature-entirely}
如果你的部署根本不使用 Tools 或 Functions，那就把这一整面移除：

```bash
# 总开关：Tools、Functions、工具服务器和 Open Terminal
ENABLE_PLUGINS=false

# 或只关闭其中一部分
ENABLE_TOOLS=false
ENABLE_FUNCTIONS=false
ENABLE_TOOL_SERVERS=false
```

这比[安全模式](#safe-mode)更强。安全模式会停用所有 Functions，但保留该功能本身；`ENABLE_PLUGINS=false` 则会隐藏工作区的 **Tools** 页面和管理员的 **Functions** 页面，并阻止 Tools、Functions、OpenAPI 与 MCP 工具服务器、Open Terminal 连接以及用户的直连工具服务器加载或运行。[`ENABLE_TOOLS`](/reference/env-configuration#enable_tools)、[`ENABLE_FUNCTIONS`](/reference/env-configuration#enable_functions) 和 [`ENABLE_TOOL_SERVERS`](/reference/env-configuration#enable_tool_servers) 各自关闭其中一部分。这四个开关都需要重启。

### 代码执行 {#code-execution}
Open WebUI 默认启用两项代码执行功能：

```bash
# 允许执行聊天回复中的代码块（默认：true；引擎 pyodide，旧版）
ENABLE_CODE_EXECUTION=true
CODE_EXECUTION_ENGINE=pyodide

# 允许模型在其推理过程中运行代码（默认：true；引擎 pyodide，旧版）
ENABLE_CODE_INTERPRETER=true
CODE_INTERPRETER_ENGINE=pyodide
```

`pyodide`（浏览器/WebAssembly）和 `jupyter`（服务端）是**旧版**代码执行引擎。**如果你不需要聊天内代码执行，请通过设置 `ENABLE_CODE_EXECUTION=false` 和 `ENABLE_CODE_INTERPRETER=false` 关闭这两项功能。** 如果确实需要，请做好隔离：优先使用 **[Open Terminal](/features/open-terminal)**，它在独立的 Docker 容器中运行代码；在多租户部署中则可使用 **[Terminals](/enterprise)** 实现按用户隔离。不要把基于浏览器的 `pyodide` 引擎当作安全边界，也绝不要在未加固 Jupyter 实例的情况下暴露 `jupyter` 引擎，因为它拥有直接的服务端访问权限。

### 安全模式 {#safe-mode}

如果某个 Function 在启动时导致问题，你可以通过安全模式禁用全部 Functions：

```bash
SAFE_MODE=true
```

这样你就能重新进入管理面板，手动关闭出问题的 Function。

### 依赖安装 {#dependency-installation}

Tools 和 Functions 可以在 frontmatter 中声明 Python 依赖。默认情况下，这些依赖会通过 pip 自动安装：

```bash
# 设为 false 可阻止根据 tool/function frontmatter 自动执行 pip install
ENABLE_PIP_INSTALL_FRONTMATTER_REQUIREMENTS=false
```

关闭后，上传的 Tools 就不能在运行时自动拉取任意包。对于生产部署，尤其是那些允许非管理员创建 Tools 的环境，建议设为 `false`。

### Workspace 访问 {#workspace-access}

控制谁可以创建、导入与共享 Tools / Functions：

```bash
USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS=false
USER_PERMISSIONS_WORKSPACE_TOOLS_IMPORT=false
USER_PERMISSIONS_WORKSPACE_SKILLS_ACCESS=false
```

默认都为 `false`，意味着只有管理员可以管理 Tools 和 Functions。除非你有明确需求且信任被授权用户，否则请保持严格限制。

---

## 容器加固 {#container-hardening}

### 基础镜像 {#base-image}
默认的 Dockerfile 使用 `python:3.12-slim-trixie`（Debian 13 上的 Python 3.12）。如果你的组织要求使用加固过的或已批准的基础镜像，可以修改 Dockerfile 中的 `FROM` 行来替换它。这在要求最小化、经过漏洞扫描基础镜像的企业环境中很常见。

### 非 root 运行 {#non-root-execution}

Dockerfile 支持以非 root 用户运行：

```bash
docker build --build-arg UID=1000 --build-arg GID=1000 .
```

### OpenShift 兼容性 {#openshift-compatibility}

对于会以任意 UID 运行容器的环境（如 OpenShift）：

```bash
docker build --build-arg USE_PERMISSION_HARDENING=true .
```

### 数据目录 {#data-directory}
数据目录（`/app/backend/data`）包含数据库、上传的文件和缓存的插件。自动生成的密钥会写入 `/app/backend/.webui_secret_key`，位于该目录之外，因此请设置 [`WEBUI_SECRET_KEY`](/reference/env-configuration#webui_secret_key)，或把 [`WEBUI_SECRET_KEY_FILE`](/reference/env-configuration#webui_secret_key_file) 指向数据目录内，以便在容器重建后仍然保留。请用合适的文件系统权限保护该目录，并把它纳入备份策略。

### 开发功能 {#development-features}

Docker 镜像默认设置 `ENV=prod`，因此会禁用 `/docs` 上的 Swagger/OpenAPI 文档界面。如果你手动运行，请确保设置 `ENV=prod`，避免这些端点暴露出来。

---

## 可观测性 {#observability}

### 结构化日志 {#structured-logging}

```bash
LOG_FORMAT=json
GLOBAL_LOG_LEVEL=INFO
```

JSON 日志适合接入 ELK、Datadog、Splunk 等日志聚合系统。

### OpenTelemetry {#opentelemetry}
```bash
ENABLE_OTEL=true
ENABLE_OTEL_TRACES=true
ENABLE_OTEL_METRICS=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317
OTEL_SERVICE_NAME=open-webui
```

完整配置请参见[监控](/reference/monitoring)和[记录 Open WebUI 日志](/getting-started/advanced-topics/logging)。

---

## SCIM 预配 {#scim-provisioning}

SCIM 2.0 允许你的身份提供商自动管理用户账户：

```bash
ENABLE_SCIM=true
SCIM_TOKEN=your-bearer-token
SCIM_AUTH_PROVIDER=oidc
```

SCIM token 是一个拥有完整用户管理权限的静态 bearer token。请像保护管理员凭据一样保护它，定期轮换，并且只通过 HTTPS 传输。

---

## 保持 Open WebUI 最新 {#keeping-open-webui-updated}

运行最新版本的 Open WebUI，有助于让你的部署持续获得最新的安全补丁和修复。请关注[变更日志](https://github.com/open-webui/open-webui/releases) 中与安全相关的更新，并尽快应用。

对于 Docker 部署，请拉取最新镜像并重建容器：

```bash
docker pull ghcr.io/open-webui/open-webui:main
```

对于多副本部署，请遵循[滚动更新流程](/troubleshooting/multi-replica#updates-and-migrations)，避免停机。

---

## 速查表 {#quick-reference}

下表总结了本指南中的关键加固动作，每一行都链接到对应章节。

| 动作 | 默认值 | 生产环境建议 |
|---|---|---|
| [保持在私有网络中](#network-placement) | 无限制 | VPN、防火墙或 zero-trust 代理 |
| [通过 HTTPS 提供服务](#https-and-tls) | HTTP | 通过反向代理启用 HTTPS |
| [设置 `WEBUI_SECRET_KEY`](#secret-key)（多副本） | 自动生成 | 显式共享密钥 |
| [检查注册策略](#registration) | 第一个用户后禁用 | 保持禁用，或使用 `pending` 角色 |
| [启用密码校验](#password-validation) | 关闭 | `ENABLE_PASSWORD_VALIDATION=true` |
| [加固 Cookie](#cookie-settings) | `Secure=false`、`SameSite=lax` | `Secure=true`、`SameSite=strict` |
| [启用 token 撤销](#token-revocation) | 无撤销（无 Redis） | 配置 Redis 或缩短 `JWT_EXPIRES_IN` |
| [限制 CORS](#cors) | `*` | 仅允许你的明确域名 |
| [设置安全响应头](#security-headers) | 无 | HSTS、X-Frame-Options、CSP、Cross-Origin 策略 |
| [限制 OAuth 域名](#domain-and-group-restrictions) | 全部允许 | `OAUTH_ALLOWED_DOMAINS=yourdomain.com` |
| [启用审计日志](#audit-logging) | `NONE` | `METADATA` 或更高 |
| [限制 API 密钥端点](#endpoint-restrictions) | 所有端点 | `ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS=true` |
| [保持 OpenAI API 透传关闭](#openai-api-passthrough) | 已关闭 | 继续保持 `ENABLE_OPENAI_API_PASSTHROUGH=false` |
| [禁用自动 pip 安装](#dependency-installation) | 已启用 | `ENABLE_PIP_INSTALL_FRONTMATTER_REQUIREMENTS=false` |
| [检查社区共享](#data-sharing-and-export) | `true` | 有敏感数据时关闭 |
| [检查 direct connections](#data-sharing-and-export) | `false` | 非必要不要开启 |
| [使用 PostgreSQL](#postgresql) | SQLite | PostgreSQL |
| [确认外发 TLS 校验](#outbound-tls) | 已启用 | 保持开启 |
| [启用离线模式](#offline-mode) | 关闭 | 隔离网络环境设为 `OFFLINE_MODE=true` |
| [结构化日志](#structured-logging) | 文本 | `LOG_FORMAT=json` |
| [保持更新](#keeping-open-webui-updated) | N/A | 使用最新稳定版 |

---

## 安全优先的部署基线 {#security-first-deployment}

对于把安全放在首位的组织，以下做法构成推荐部署基线。每一项都覆盖部署中的不同层面，组合起来可以形成纵深防御。括号中的链接可跳转到上文对应配置章节。

### 网络与传输 {#network-and-transport}

1. **将 Open WebUI 放在 VPN、反向代理或 zero-trust 访问层之后，并启用限速与 IP allowlist。** Open WebUI 适合运行在私有、可信网络中。不要在没有额外访问控制层的情况下直接暴露到公网。请在代理上配置连接速率限制、重复认证尝试限制、已知 IP 范围访问限制，并使用 fail2ban 等工具阻断恶意来源。将 `--forwarded-allow-ips` 限制为代理自身 IP，避免头部伪造。[详情](#network-placement)

2. **所有流量都使用 HTTPS，并启用完整安全头。** 使用能够终止 TLS 的反向代理。把会话 Cookie 配置为 `Secure=true` 与 `SameSite=strict`。生产环境不要通过明文 HTTP 提供 Open WebUI。启用 HSTS、Content Security Policy、X-Frame-Options、X-Content-Type-Options、Referrer-Policy 和 Permissions-Policy。不要把 CORS 保持为 `*`；只允许确实需要访问的域名。[详情](#https-and-tls)

### 认证与访问控制 {#authentication-and-access-control}

3. **保持注册关闭。** Open WebUI 会在第一个用户注册后自动关闭注册。任何新账户默认角色都是 `pending`，必须经过管理员明确批准后才能访问功能。对可信网络之外可访问的实例，不要重新开启开放注册。[详情](#registration)

4. **使用身份提供商的 SSO，并关闭本地认证。** 集成组织现有的 OAuth/OIDC 或 LDAP。限制可登录的邮箱域名和 IdP 组，将 IdP 角色映射到 Open WebUI 角色，并完全关闭本地登录表单与密码认证。限制每用户并发会话数，借助 Redis 启用 backchannel logout，以便用户被回收时会话能立刻失效；除非你的提供商保证邮箱已验证，否则不要启用 OAuth 账户合并。[详情](#oauth-and-sso)

5. **强制密码复杂度并缩短会话时长。** 如果仍使用本地账户，请启用密码校验。把默认 4 周的 JWT 过期时间缩短到适合你的环境（例如 8 到 24 小时）。生产环境不要禁用 token 过期。[详情](#password-validation)

6. **定期审查用户账户和权限。** 清理不活跃账户，审计组成员关系，并确认工作区权限仍符合预期。可使用 SCIM 预配，通过身份提供商自动化账户生命周期管理。[详情](#access-control)

### Tools、Functions 与扩展 {#tools-functions-and-extensions}

7. **将 Tool 和 Function 的创建权限严格限制给管理员，导入前审查所有代码。** 默认只有管理员可以创建、导入和管理 Tools / Functions。不要给不可信用户开放工作区权限。把第三方 Tool 看作与你基础设施上运行的其他代码一样进行审查。未经查看源码，不要导入任何 Tool。[详情](#tools-functions-and-pipelines)

8. **如果不需要，就关闭自动依赖安装和代码执行。** 设置 `ENABLE_PIP_INSTALL_FRONTMATTER_REQUIREMENTS=false`，阻止 Tool 在运行时拉取任意包。如果部署不需要聊天中执行代码，直接全部关闭；如果需要，请保持默认 `pyodide` 引擎，因为它运行在浏览器端而不是服务器端。在没有额外保护 Jupyter 实例的情况下，不要切换到 Jupyter 引擎。保持 direct connections 与 direct tool servers 关闭。[详情](#dependency-installation)

### 数据保护 {#data-protection}

9. **限制数据共享、文件上传和 API 密钥访问。** 设置最大文件大小、文件数量和允许的文件扩展名。若业务上不需要，可关闭社区共享（`ENABLE_COMMUNITY_SHARING=false`）和管理员批量导出（`ENABLE_ADMIN_EXPORT=false`）。将 API 密钥创建权限限制在管理员范围，并启用端点限制，让每个密钥只能访问特定路由。[详情](#data-sharing-and-export)

10. **对静态数据进行加密，并保持定期备份。** 对 SQLite 使用 SQLCipher；对 PostgreSQL 使用磁盘级加密或透明数据加密。定期备份，并将备份存放在独立安全域中，同时定期演练恢复流程。[详情](#sqlcipher)

### 外发网络控制 {#outbound-network-controls}

11. **保持 SSRF 防护、外发 TLS 校验和网络限制开启。** 不要启用本地网页抓取。默认配置会阻止访问私有 IP 范围和云厂商元数据端点；你应继续将自身内部域名加入黑名单。不要关闭外发连接的证书校验。对于隔离网络环境，请启用离线模式以禁用所有外发调用。[详情](#ssrf-prevention)

### 供应链与变更管理 {#supply-chain-and-change-management}

12. **使用官方容器镜像，或直接从源码构建。** 从 `ghcr.io/open-webui/open-webui` 或 Docker Hub 上的 `openwebui/open-webui` 拉取镜像。若要完全掌控供应链，可使用官方 Dockerfile 从[源码](https://github.com/open-webui/open-webui)构建。不要使用非官方或第三方镜像。[详情](#container-hardening)

13. **固定到具体版本，并在部署前验证更新。** 使用带标签的发行版，而不是 `:main` 或 `:latest`。升级前查看变更日志，先在预发布环境验证，再推广到生产，并确保具备回滚能力。生产环境不要自动更新。[详情](#keeping-open-webui-updated)

### 容器与基础设施 {#container-and-infrastructure}

14. **以非 root 身份运行，并在分段网络中使用最小权限。** 使用非 root UID/GID，尽量采用只读文件系统挂载，移除不必要的 Linux capabilities，并设置 `--security-opt=no-new-privileges`。对数据目录应用严格权限（如 `0700`）。将 PostgreSQL 部署在独立网络段，并使用强凭据，避免直接暴露到公网。[详情](#non-root-execution)

### 可观测性与事件响应 {#observability-and-incident-response}

15. **将审计日志至少开启到 METADATA 级别，并转发到你的 SIEM。** 始终记录认证端点。配置保留策略，并将日志转发到组织现有的日志基础设施。使用 JSON 日志格式，如果条件允许，还可以启用 OpenTelemetry 做分布式追踪。[详情](#audit-logging)

16. **监控异常。** 跟踪 CPU、内存、网络与磁盘使用情况。对接告警系统，尽早发现异常计算消耗、异常外发流量或存储突增。[详情](#observability)

17. **准备事件响应方案。** 明确被盗账户、未授权访问和异常资源消耗时的处理流程。你需要知道如何禁用用户账户、撤销会话（需要 Redis）、轮换密钥，以及审查审计日志。
