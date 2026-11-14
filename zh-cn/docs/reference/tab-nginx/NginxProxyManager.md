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
- Agree to Let’s Encrypt terms and save. Change propagation time **if needed** (120 seconds).

5. **Create Proxy Hosts:**

- For each service (e.g., openwebui, nextcloud), go to Hosts → Proxy Hosts → Add Proxy Host.

- Fill in the domain name (e.g., openwebui.hello.duckdns.org).
- Set the scheme to HTTP (default), enable ``Websockets support`` and point to your Docker IP (if docker with open-webui is running on the same computer as NGINX manager, this will be the same IP as earlier (example: ``192.168.0.6``)
- Select the SSL certificate generated earlier, force SSL, and enable HTTP/2.

:::danger 关键：为 WebSocket 连接配置 CORS

A very common and difficult-to-debug issue with WebSocket connections is a misconfigured Cross-Origin Resource Sharing (CORS) policy. When running Open WebUI behind a reverse proxy like Nginx Proxy Manager, you **must** set the `CORS_ALLOW_ORIGIN` environment variable in your Open WebUI configuration.

Failure to do so will cause WebSocket connections to fail, even if you have enabled "Websockets support" in Nginx Proxy Manager.

:::

:::danger 关键：关闭流式响应的代理缓冲

**This is the most common cause of garbled markdown and broken streaming responses.**

In Nginx Proxy Manager, go to your proxy host → **Advanced** tab → and add these directives to the **Custom Nginx Configuration** field:

```nginx
proxy_buffering off;
proxy_cache off;
```

Without this, Nginx re-chunks SSE streams, breaking markdown formatting (visible `##`, `**`, missing words). This also makes streaming responses significantly faster.

:::

:::tip 为长时间补全放宽超时

Long LLM completions (30+ minutes for complex tasks) may exceed the default 60-second timeout. Add these directives in the **Advanced** tab → **Custom Nginx Configuration**:

```nginx
proxy_read_timeout 1800;
proxy_send_timeout 1800;
proxy_connect_timeout 1800;
```

This sets a 30-minute timeout. Adjust as needed for your use case.

:::

:::tip 缓存最佳实践

While Nginx Proxy Manager handles most configuration automatically, be aware that:

- **Static assets** (CSS, JS, images) are cached by default for better performance
- **Authentication endpoints** should never be cached
- If you add custom caching rules in NPM's "Advanced" tab, ensure you exclude paths like `/api/`, `/auth/`, `/signup/` , `/signin/`, `/sso/`, `/admin/`, `/signout/`, `/oauth/`, `/login/`, and `/logout/`

The default NPM configuration handles this correctly - only modify caching if you know what you're doing.

:::

**Example:**
If you access your UI at `https://openwebui.hello.duckdns.org`, you must set:

```bash
CORS_ALLOW_ORIGIN="https://openwebui.hello.duckdns.org"
```

You can also provide a semicolon-separated list of allowed domains. **Do not skip this step.**

:::

6. **Add your url to open-webui (otherwise getting HTTPS error):**

- Go to your open-webui → Settings → Admin → General
- In the **Webhook URL** text field, enter your URL through which you will connect to your open-webui via Nginx reverse proxy. Example: ``hello.duckdns.org`` (not essential with this one) or ``openwebui.hello.duckdns.org`` (essential with this one).

#### 访问 WebUI {#access-the-webui}

Access Open WebUI via HTTPS at either ``hello.duckdns.org`` or ``openwebui.hello.duckdns.org`` (in whatever way you set it up).

:::note

Firewall Note: Be aware that local firewall software (like Portmaster) might block internal Docker network traffic or required ports. If you experience issues, check your firewall rules to ensure necessary communication for this setup is allowed.

:::
