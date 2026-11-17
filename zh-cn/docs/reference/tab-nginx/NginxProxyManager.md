### Nginx Proxy Manager {#nginx-proxy-manager}

Nginx Proxy Manager（NPM）可以让你轻松管理反向代理，并使用 Let's Encrypt 的有效 SSL 证书为本地应用（如 Open WebUI）提供保护。
这种配置可以启用 HTTPS 访问；由于许多移动浏览器的安全要求，这对于使用语音输入等功能很有必要，同时又不会把应用的特定端口直接暴露到互联网。

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

###### 这里有一个简单示例，展示在 [DuckDNS 域名页](https://www.duckdns.org/domains) 中如何操作 {#here-is-a-simple-example-how-its-done-in-httpswwwduckdnsorgdomains}

4. **设置 SSL 证书：**

- 使用 `http://server_ip:81` 访问 Nginx Proxy Manager。例如：``192.168.0.6:81``

- 使用默认凭据登录（`admin@example.com` / `changeme`）。按提示修改它们。
- 进入 **SSL 证书 → 添加 SSL 证书 → Let's Encrypt**。
- 填写你从 DuckDNS 获得的邮箱和域名。一个域名带星号，另一个不带。例如：``*.hello.duckdns.org`` 和 ``hello.duckdns.org``。
- 选择 **使用 DNS 验证**，选择 DuckDNS，然后粘贴你的 API token。例如：
```dns_duckdns_token=f4e2a1b9-c78d-e593-b0d7-67f2e1c9a5b8```
- 同意 Let's Encrypt 的服务条款并保存。变更传播时间**按需**调整（120 秒）。

5. **创建代理主机：**

- 对每个服务（例如 openwebui、nextcloud），进入 Hosts → Proxy Hosts → Add Proxy Host。

- 填写域名（例如 openwebui.hello.duckdns.org）。
- 将 scheme 设为 HTTP（默认），启用 ``Websockets support``，并指向你的 Docker IP（如果 open-webui 的 docker 与 NGINX manager 运行在同一台电脑上，这里与前面是同一个 IP，例如 ``192.168.0.6``）
- 选择前面生成的 SSL 证书，强制启用 SSL，并开启 HTTP/2。

:::danger 关键：为 WebSocket 连接配置 CORS

WebSocket 连接有一个非常常见且难以调试的问题：跨域资源共享（CORS）策略配置错误。当 Open WebUI 运行在 Nginx Proxy Manager 之类的反向代理之后时，你**必须**在 Open WebUI 配置中设置 `CORS_ALLOW_ORIGIN` 环境变量。

即使你已在 Nginx Proxy Manager 中启用 "Websockets support"，不这样做仍会导致 WebSocket 连接失败。

:::

:::danger 关键：关闭流式响应的代理缓冲

**这是 Markdown 乱码和流式响应损坏最常见的原因。**

在 Nginx Proxy Manager 中，进入你的代理主机 → **Advanced** 标签页，并把以下指令添加到 **Custom Nginx Configuration** 字段：

```nginx
proxy_buffering off;
proxy_cache off;
```

不加这段配置，Nginx 会重新切分 SSE 数据流，破坏 Markdown 格式（表现为可见的 `##`、`**`、文字缺失）。这也会让流式响应明显更快。

:::

:::tip 为长时间补全放宽超时

长时间的 LLM 补全（复杂任务可能超过 30 分钟）会超出默认的 60 秒超时。在 **Advanced** 标签页 → **Custom Nginx Configuration** 中添加以下指令：

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

**示例：**
如果你通过 `https://openwebui.hello.duckdns.org` 访问 UI，则必须设置：

```bash
CORS_ALLOW_ORIGIN="https://openwebui.hello.duckdns.org"
```

你也可以提供一个用分号分隔的允许域名列表。**不要跳过这一步。**

:::

6. **把你的 URL 添加到 open-webui（否则会出现 HTTPS 错误）：**

- Go to your open-webui → Settings → General（管理员区域）
- 在 **Webhook URL** 输入框中，填入你通过 Nginx 反向代理连接 open-webui 所使用的 URL。例如：``hello.duckdns.org``（这个不关键）或 ``openwebui.hello.duckdns.org``（这个必须填）。

#### 访问 WebUI {#access-the-webui}

通过 ``hello.duckdns.org`` 或 ``openwebui.hello.duckdns.org`` 以 HTTPS 方式访问 Open WebUI（按你实际配置的方式访问即可）。

:::note

防火墙提示：请注意，本地防火墙软件（例如 Portmaster）可能会拦截 Docker 网络内部的流量或所需端口。如果遇到问题，请检查防火墙规则，确保该配置所需的通信被允许。

:::
