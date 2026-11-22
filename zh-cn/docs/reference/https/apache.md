---
sidebar_position: 203
title: "使用 Apache、Synology 或 IIS 的 HTTPS"
---

# 使用 Apache、Synology 或 IIS 的 HTTPS {#https-using-apache-synology-or-iis}

Open WebUI 通过 `/ws/socket.io` 上的 Socket.IO 连接流式发送聊天回复和实时更新。默认情况下，浏览器只使用 WebSocket 传输，没有 polling 回退。Apache httpd、Synology DSM 反向代理和 IIS 都需要先做一项设置，才会转发 WebSocket 升级请求。没有它，页面能加载，但实时连接无法建立。

## 症状 {#symptoms}

- 在 **DevTools > Network** 中，对 `/ws/socket.io/` 的请求失败，或以 `101 Switching Protocols` 以外的状态结束，例如 `400`。
- 浏览器控制台记录 `connect_error`。

请从自己主机名的根路径提供 Open WebUI，并原样转发所有路径。放在子路径下提供服务[不受支持](/faq#q-can-i-serve-open-webui-under-a-subpath-such-as-examplecomopenwebui)。

## Apache httpd 服务器 {#apache-httpd}

加载 `mod_proxy`、`mod_proxy_http` 和 `mod_headers`。在 Apache 2.4.46 及更早版本上，还要加载 `mod_proxy_wstunnel`。按 Apache 的 [SSL/TLS how-to](https://httpd.apache.org/docs/2.4/ssl/ssl_howto.html) 用 `mod_ssl` 配置 TLS。

### Apache 2.4.47 及更高版本 {#apache-2447-and-later}

从 2.4.47 开始，`mod_proxy_http` 可以通过 `ProxyPass` 的 `upgrade` 参数端到端隧道传输协议升级（[mod_proxy: Protocol Upgrade](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html#protoupgrade)）。只有当后端返回 `101 Switching Protocols` 时 Apache 才会建立隧道，而 Open WebUI 在 `/ws/socket.io` 上正是如此，因此一条规则即可覆盖整个站点：

```apache
<VirtualHost *:443>
    ServerName chat.example.com

    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"
    ProxyTimeout 300

    ProxyPass        "/" "http://127.0.0.1:8080/" upgrade=websocket
    ProxyPassReverse "/" "http://127.0.0.1:8080/"
</VirtualHost>
```

### Apache 2.4.46 及更早版本 {#apache-2446-and-earlier}

使用 `mod_proxy_wstunnel`，并为 WebSocket 路径配一条 `ws://` 规则（[mod_proxy_wstunnel](https://httpd.apache.org/docs/2.4/mod/mod_proxy_wstunnel.html)）。Open WebUI 在 `/ws` 下提供 Socket.IO，因此一条 `/ws/` 规则即可覆盖 `/ws/socket.io`。请把它放在兜底的 `/` 规则之前：Apache 按出现顺序检查 `ProxyPass` 规则，第一条匹配的生效（[ProxyPass](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html#proxypass)）。

```apache
<VirtualHost *:443>
    ServerName chat.example.com

    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"
    ProxyTimeout 300

    ProxyPass        "/ws/" "ws://127.0.0.1:8080/ws/"
    ProxyPass        "/"    "http://127.0.0.1:8080/"
    ProxyPassReverse "/"    "http://127.0.0.1:8080/"
</VirtualHost>
```

### 各指令的作用 {#what-each-directive-does}

- `ProxyPreserveHost On` 会把浏览器的 `Host` 头部传给 Open WebUI，而不是 `127.0.0.1:8080`。Apache 默认关闭它。
- `mod_proxy_http` 自己会加上 `X-Forwarded-For`、`X-Forwarded-Host` 和 `X-Forwarded-Server`（[Reverse Proxy Request Headers](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html#x-headers)），但不会加 `X-Forwarded-Proto`。`RequestHeader set X-Forwarded-Proto "https"` 补上了它，让 Open WebUI 知道浏览器使用的是 HTTPS。
- `ProxyTimeout 300` 为长请求提供了[关键配置说明](/reference/https#key-configuration-notes)中建议的 300 秒。
- Web 界面通过 `/ws/socket.io` 接收流式回复，因此只要 WebSocket 正常，Apache 的响应缓冲就不会影响它。`ProxyPass` 的 `flushpackets` 参数只适用于 AJP 和 FastCGI 后端，把它加到 `http://` 后端上不会有任何变化。

## Synology DSM 服务器 {#synology-dsm}

DSM 反向代理只有在你在规则中添加 WebSocket 头部之后才会转发 WebSocket（[Synology：登录门户 > 高级](https://kb.synology.com/en-global/DSM/help/DSM/AdminCenter/system_login_portal_advanced?version=7)）：

1. 进入 **控制面板 > 登录门户 > 高级**，点击 **反向代理 > 创建**。
2. 在 **来源** 中选择 HTTPS、你的主机名和端口 443。在 **目的地** 中选择 HTTP、运行 Open WebUI 的主机及其监听的端口（例如容器映射 `3000:8080` 时为 `localhost` 和 `3000`）。
3. 打开 **自定义标头** 标签页，点击 **创建** 并选择 **WebSocket**。
4. 在 **高级设置** 中，调大 **代理读取超时（秒）**，以容纳长请求。
5. 点击 **保存**。

## IIS 服务器 {#iis}

IIS 需要 WebSocket Protocol 功能（IIS 8.0 引入），以及 URL Rewrite 和应用程序请求路由（ARR）才能充当反向代理：

1. 安装 **WebSocket Protocol**：在 **服务器管理器** 中打开 **添加角色和功能**，并选择 **Web 服务器 (IIS) > Web 服务器 > 应用程序开发 > WebSocket Protocol**（[IIS 8.0 WebSocket Protocol 支持](https://learn.microsoft.com/en-us/iis/get-started/whats-new-in-iis-8/iis-80-websocket-protocol-support)）。
2. 安装 URL Rewrite 和 ARR。在 IIS 管理器中选中服务器节点，打开 **应用程序请求路由** 并勾选 **启用代理**（[使用 URL Rewrite v2 和应用程序请求路由实现反向代理](https://learn.microsoft.com/en-us/iis/extensions/url-rewrite-module/reverse-proxy-with-url-rewrite-v2-and-application-request-routing)）。
3. 在站点的 `web.config` 中，在 `system.webServer` 下添加一条规则，把所有路径转发到 Open WebUI：

```xml
<rewrite>
    <rules>
        <rule name="Open WebUI" stopProcessing="true">
            <match url="(.*)" />
            <action type="Rewrite" url="http://localhost:8080/{R:1}" />
        </rule>
    </rules>
</rewrite>
```

Microsoft 的 ARR 演练文档没有覆盖 WebSocket 流量，因此请按[检查连接](#check-the-connection)中的步骤确认连接正常。

## 如果代理无法转发 WebSocket {#if-the-proxy-cannot-forward-websocket}

设置 `ENABLE_WEBSOCKET_SUPPORT=false` 并重启 Open WebUI。服务端随后只接受 HTTP long-polling 并拒绝升级请求，浏览器也会改用 long-polling 连接，它可以穿过任何能转发普通请求的代理。有两个功能需要 WebSocket 传输并会停止工作：[Tether](/ecosystem/tether) 和[加密聊天](/features/channels/encrypted-chats)。

## 检查连接 {#check-the-connection}

打开 **DevTools > Network**，按 **WS** 过滤并重新加载页面。代理工作正常时，会看到对 `/ws/socket.io/` 的请求状态为 `101`。

关于 `WEBUI_URL`、`CORS_ALLOW_ORIGIN`、上传大小限制、超时和安全 Cookie，请参阅[关键配置说明](/reference/https#key-configuration-notes)。