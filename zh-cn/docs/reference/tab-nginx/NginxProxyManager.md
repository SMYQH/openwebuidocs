### Nginx Proxy Manager {#nginx-proxy-manager}

Nginx Proxy Manager（NPM）可以让你轻松管理反向代理，并使用 Let's Encrypt 的有效 SSL 证书为本地应用（如 Open WebUI）提供保护。
这种配置可启用 HTTPS 访问，无需将应用端口直接暴露到互联网。出于安全考虑，许多移动浏览器要求通过 HTTPS 才能使用语音输入功能。

#### 前置条件 {#prerequisites}

- 一台运行 Docker 的家用服务器，以及已经运行中的 open-webui 容器。
- 一个域名（可以是 DuckDNS 这类免费域名，也可以是 Namecheap/GoDaddy 这类付费域名）。
- 对 Docker 和 DNS 配置有基本了解。

#### Nginx Proxy Manager 步骤 {#nginx-proxy-manager-steps}

1. **为 Nginx 文件创建目录：**

    ```bash
    mkdir ~/nginx_config
    cd ~/nginx_config
    ```

2. **用 Docker 搭建 Nginx Proxy Manager：**

    ```bash
    nano docker-compose.yml
    ```

```yaml
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '81:81'
      - '443:443'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
```

运行容器：

```bash
docker compose up -d
```

3. **配置 DNS 与域名：**

    - 登录你的域名服务商（例如 DuckDNS）并创建一个域名。
    - 把该域名指向你的代理所在机器的本地 IP（例如 192.168.0.6）。
    - 如果使用 DuckDNS，请从其控制台获取 API 令牌。

###### 这里有一个在 https://www.duckdns.org/domains 上操作的简单示例 {#here-is-a-simple-example-how-its-done-in-httpswwwduckdnsorgdomains}

4. **设置 SSL 证书：**

- 使用 `http://server_ip:81` 访问 Nginx Proxy Manager。例如：``192.168.0.6:81``

- 使用默认凭据登录（`admin@example.com` / `changeme`）。按提示修改它们。
- 进入 SSL 证书 → 添加 SSL 证书 → Let's Encrypt。
- 输入你的电子邮件地址和从 DuckDNS 获得的域名。一个域名带星号，另一个不带。例如：``*.hello.duckdns.org`` 和 ``hello.duckdns.org``。
- 选择使用 DNS 验证，选中 DuckDNS，然后粘贴你的 API 令牌。例如：
```bash
dns_duckdns_token=f4e2a1b9-c78d-e593-b0d7-67f2e1c9a5b8
```
- 同意 Let's Encrypt 的服务条款并保存。**如有需要**，调整传播时间（120 秒）。

5. **创建代理主机：**

- 对每个服务（例如 openwebui、nextcloud），进入 Hosts → Proxy Hosts → Add Proxy Host。

- 填写域名（例如 openwebui.hello.duckdns.org）。
- 将协议设为 HTTP（默认），启用 ``Websockets support``，并指向你的 Docker IP 地址。如果运行 open-webui 的 Docker 和 NGINX Manager 位于同一台电脑上，就使用前面填过的 IP，例如 ``192.168.0.6``。
- 选择前面生成的 SSL 证书，强制启用 SSL，并开启 HTTP/2。

:::tip 将 CORS_ALLOW_ORIGIN 设置为你的公共源

`CORS_ALLOW_ORIGIN` 默认为 `*`，因此不设置它永远不会破坏 WebSocket 连接。作为加固措施，请把它设置为你精确的公共源（例如 `https://chat.example.com`）。真正会破坏 Socket.IO 连接（以及任何跨源浏览器请求）的，是缺少该源的值，例如在你提供 `https://` 时却填写了 `http://` 条目。

**示例：**
如果你通过 `https://openwebui.hello.duckdns.org` 访问 UI，请设置：

```bash
CORS_ALLOW_ORIGIN="https://openwebui.hello.duckdns.org"
```

你也可以提供一个用分号分隔的允许源列表。默认的 `*` 允许所有源；上面的值则把范围缩小到你的源。

:::

:::warning 关闭流式响应的代理缓冲

Web 界面通过 Socket.IO 连接流式发送聊天 token，因此只要 WebSocket 正常，缓冲就不会让浏览器中的聊天出现乱码。它确实会拖住 API 客户端读取的流式响应。

在 Nginx Proxy Manager 中，进入你的代理主机 → **Advanced** 标签页，并把以下指令添加到 **Custom Nginx Configuration** 字段：

```nginx
proxy_buffering off;
proxy_cache off;
```

不加这段配置，Nginx 会拖住流式响应，因此 API 客户端收到的响应会成批到达，或只在最后一次性到达。

:::

:::tip 为长时间补全放宽超时

耗时较长的 LLM 补全可能超过默认的 60 秒超时限制，复杂任务可能持续 30 分钟或更久。在 **Advanced** 标签页 → **Custom Nginx Configuration** 中添加以下指令：

```nginx
proxy_read_timeout 1800;
proxy_send_timeout 1800;
proxy_connect_timeout 1800;
```

这会把超时设为 30 分钟。请按你的使用场景调整。

:::

:::tip 缓存最佳实践

虽然 Nginx Proxy Manager 会自动处理大部分配置，但请注意：

- **静态资源**（CSS、JS、图片）默认会被缓存，以提升性能
- **认证端点**绝不应被缓存
- 如果你在 NPM 的 "Advanced" 标签页中添加自定义缓存规则，请确保排除 `/api/`、`/auth/`、`/signup/`、`/signin/`、`/sso/`、`/admin/`、`/signout/`、`/oauth/`、`/login/`、`/logout/` 之类的路径

NPM 的默认配置已经正确处理了这一点——只有在明确知道后果时才修改缓存设置。

:::

6. **告诉 Open WebUI 它的公共 URL：**

- 在 Open WebUI 中，转到 Settings → General（管理员区域）。
- 在 **WebUI URL** 字段中，填入你通过代理将使用的 URL，例如 ``https://openwebui.hello.duckdns.org``。它用于 SSO 登录后的重定向以及通知中的链接。

#### 访问 WebUI {#access-the-webui}

通过 ``hello.duckdns.org`` 或 ``openwebui.hello.duckdns.org`` 以 HTTPS 方式访问 Open WebUI（按你实际配置的方式访问即可）。

:::note

防火墙提示：请注意，本地防火墙软件（例如 Portmaster）可能会拦截 Docker 网络内部的流量或所需端口。如果遇到问题，请检查防火墙规则，确保该配置所需的通信被允许。

:::
