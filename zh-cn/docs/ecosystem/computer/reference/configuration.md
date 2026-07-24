---
title: config.toml
sidebar_position: 4
---

# config.toml

Computer 的服务器配置位于 `<data-dir>/config.toml`：默认为 `~/.cptr/config.toml`，Docker 中为 `/data/config.toml`。

```toml
[server]
secret = "..."              # JWT 签名密钥，首次运行时生成

[auth]
mode = "password"           # "password"（默认）、"pam" 或 "trusted_header"
header = "Remote-User"      # trusted_header 模式：哪个标头携带用户名
trusted_sources = []        # trusted_header 模式：可选的代理 IP 白名单

[app_config]
# 存储在数据库中的应用配置镜像
```

## `[server]`：密钥

`secret` 签署会话 JWT。轮换它并重启会使所有设备上的所有会话登出；这就是"让所有人立即登出"的杠杆。

:::warning 轮换密钥会使存储的提供商密钥失效
Computer 加密存储的值（前缀为 `encrypted:`），例如提供商 API 密钥和机器人令牌，都是基于服务器密钥的。轮换后，在设置中重新输入这些密钥。
:::

## `[auth]`：用户登录方式

| 模式 | 行为 |
| --- | --- |
| `password` | 默认。存储在 Computer 数据库中的用户名/密码账户。 |
| `pam` | 针对 Linux 系统用户认证。需要 `pip install 'cptr[pam]'`；账户在首次登录时自动创建。 |
| `trusted_header` | 反向代理 SSO：Computer 信任由 `header` 命名的标头中的用户名（默认 `Remote-User`）。可选择使用 `trusted_sources` 限制哪些源 IP 可以断言它。设置：[反向代理](/ecosystem/computer/phone-and-remote/reverse-proxy)。 |

任何模式下都没有 localhost 绕过；每个请求都需要认证。更多关于整体模型的信息：[安全](/ecosystem/computer/phone-and-remote/security)。

## `[app_config]`：镜像

你在 UI 中更改的设置会存储在数据库*中并*镜像到此部分。启动时，文件会重新写入数据库：**文件优先**。两个后果：

- 手动编辑 `config.toml` 是更改应用配置的合法方式：停止服务器，编辑，启动。不要在服务器运行时编辑它，因为 UI 更改可能会覆盖你的编辑。
- 配置在数据库丢失后仍然存在。恢复 `config.toml`，即使 `app.db` 不存在，你的设置也会恢复。
