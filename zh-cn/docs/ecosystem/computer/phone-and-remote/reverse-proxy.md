---
title: "反向代理和 SSO"
sidebar_position: 4
---

# 反向代理和 SSO

`cptr` 没有自己的 TLS：代理终止 HTTPS 并将纯 HTTP 转发到 `127.0.0.1:8000`。有一件事常常让人困扰：Computer 是基于 Socket.IO 的，因此代理**必须**转发 WebSocket 升级，否则终端和流式传输会中断。

## nginx

```nginx
server {
    listen 443 ssl;
    server_name computer.example.com;

    # ssl_certificate / ssl_certificate_key 像往常一样

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400s;   # 长生命周期的终端 WebSocket
    }
}
```

## Caddy

Caddy 自动处理 TLS 和 WebSocket 升级：

```caddyfile
computer.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

## Traefik

将路由器指向一个目标为 `http://127.0.0.1:8000` 的服务。Traefik 默认转发 WebSocket 升级；无需额外的中间件。

## 使用受信任标头认证的单点登录

如果你的代理已经对用户进行认证（Authentik、Authelia、oauth2-proxy……），Computer 可以信任它注入的身份标头，而不是显示自己的登录页面。在 `config.toml` 中（在数据目录中，默认为 `~/.cptr`）：

```toml
[auth]
mode = "trusted_header"
header = "Remote-User"          # 默认标头名称
trusted_sources = ["127.0.0.1"] # 可选：仅接受来自这些 IP 的标头
```

编辑后重启 `cptr`。查看[配置参考](/ecosystem/computer/reference/configuration)了解所有选项。

:::warning 代理必须拥有该标头
在 `trusted_header` 模式下，设置 `Remote-User` 的人即登录成功。你的代理必须从传入请求中剥离该标头，仅在其自身认证成功后设置它。Computer 也应仅能通过代理访问（保持默认的 `127.0.0.1` 绑定）。一个传递客户端提供标头的代理就是一个未经认证的 shell。
:::

## PAM：使用系统用户登录

在 Linux 上，你可以针对主机的用户账户进行认证：

```toml
[auth]
mode = "pam"
```

需要 PAM 额外包（`pip install 'cptr[pam]'`）。用户在首次成功登录时自动在 Computer 中创建。
