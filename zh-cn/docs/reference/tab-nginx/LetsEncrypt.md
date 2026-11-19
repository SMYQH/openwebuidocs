
### Let's Encrypt {#lets-encrypt}

Let's Encrypt 提供免费的 SSL 证书，被大多数浏览器信任，非常适合为你的生产环境提供保护。

本指南采用两阶段方案：

1.  **阶段 1：** 临时运行 Nginx，证明你拥有该域名，并从 Let's Encrypt 获取证书。
2.  **阶段 2：** 重新配置 Nginx，使用新证书建立安全的 HTTPS 连接。

#### 前提条件 {#prerequisites}

* 一个 **域名**（例如 `my-webui.com`），并带有指向服务器公网 IP 的 **DNS `A` 记录**。
* 已在服务器上安装 **Docker** 和 **Docker Compose**。
* 具备在终端中执行命令的基础知识。

:::info
**注意！** Let's Encrypt 已支持[**短期 IP 地址证书**](https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability/)，但本指南的配置针对域名。按本指南操作时，**必须**使用域名。
:::

-----

### 第 1 步：为证书验证准备初始配置 {#step-1-initial-setup-for-certificate-validation}

首先创建所需文件，并准备一个临时的 Nginx 配置，让 Let's Encrypt 的服务器可以验证你的域名。

1. **请确保你已经完成上面的[前提条件](#prerequisites)。**

2. **创建目录结构**

   在项目根目录执行以下命令，为 Nginx 配置和 Let's Encrypt 证书创建目录：

    ```bash
    mkdir -p nginx/conf.d ssl/certbot/conf ssl/certbot/www
    ```

3. **创建临时的 Nginx 配置**

   创建文件 `nginx/conf.d/open-webui.conf`。这个初始配置只监听 80 端口，并为 Certbot 提供验证文件。

   **记得把 `<YOUR_DOMAIN_NAME>` 替换成你的真实域名。**

    ```nginx
    # nginx/conf.d/open-webui.conf

    server {
        listen 80;
        listen [::]:80;
        server_name <YOUR_DOMAIN_NAME>;

        # Route for Let's Encrypt validation challenges
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # All other requests will be ignored for now
        location / {
            return 404;
        }
    }
    ```

4. **更新你的 `docker-compose.yml`**

   将 `nginx` 服务添加到 `docker-compose.yml` 中，并确保 `open-webui` 服务使用共享的 Docker 网络。

    ```yaml
    services:
      nginx:
        image: nginx:alpine
        restart: always
        ports:
          # Expose HTTP and HTTPS ports to the host machine
          - "80:80"
          - "443:443"
        volumes:
          # Mount Nginx configs and SSL certificate data
          - ./nginx/conf.d:/etc/nginx/conf.d
          - ./ssl/certbot/conf:/etc/letsencrypt
          - ./ssl/certbot/www:/var/www/certbot
        depends_on:
          - open-webui
        networks:
          - open-webui-network

      open-webui:
        # Your existing open-webui configuration...
        # ...
        # Ensure it's on the same network
        networks:
          - open-webui-network
        # Expose the port internally to the Docker network.
        # You do NOT need to publish it to the host (e.g., no `ports` section is needed here).
        expose:
          - 8080

    networks:
        open-webui-network:
            driver: bridge
    ```

-----

### 第 2 步：获取 SSL 证书 {#step-2-obtain-the-ssl-certificate}

接下来我们将运行一个脚本，借助 Docker 获取证书。

1. **创建证书申请脚本**

   在项目根目录创建一个名为 `enable_letsencrypt.sh` 的可执行脚本。

   **记得把 `<YOUR_DOMAIN_NAME>` 和 `<YOUR_EMAIL_ADDRESS>` 替换成你的真实信息。**

    ```bash
    #!/bin/bash
    # enable_letsencrypt.sh

    DOMAIN="<YOUR_DOMAIN_NAME>"
    EMAIL="<YOUR_EMAIL_ADDRESS>"

    echo "### Obtaining SSL certificate for $DOMAIN ###"

    # Start Nginx to serve the challenge
    docker compose up -d nginx

    # Run Certbot in a container to get the certificate
    docker run --rm \
      -v "./ssl/certbot/conf:/etc/letsencrypt" \
      -v "./ssl/certbot/www:/var/www/certbot" \
      certbot/certbot certonly \
      --webroot \
      --webroot-path=/var/www/certbot \
      --email "$EMAIL" \
      --agree-tos \
      --no-eff-email \
      --force-renewal \
      -d "$DOMAIN"

    if [[ $? != 0 ]]; then
        echo "Error: Failed to obtain SSL certificate."
        docker compose stop nginx
        exit 1
    fi

    # Stop Nginx before we apply the final config
    docker compose stop nginx
    echo "### Certificate obtained successfully! ###"
    ```

2. **让脚本可执行**

    ```bash
    chmod +x enable_letsencrypt.sh
    ```

3. **运行脚本**

   执行脚本。它会自动启动 Nginx、申请证书，然后停止 Nginx。

    ```bash
    ./enable_letsencrypt.sh
    ```

-----

### 重要：缓存配置 {#important-caching-configuration}

在 Open WebUI 中使用 NGINX 时，正确的缓存配置对性能至关重要，同时还要确保认证保持安全。下面的配置包含：

- **缓存**：静态资源（CSS、JS、字体、图片），以提升性能
- **不缓存**：认证端点、API 调用、SSO/OAuth 回调和会话数据
- **结果**：页面加载更快，同时不会破坏登录功能

下面的配置会自动落实这些规则。

### 第 3 步：完成用于 HTTPS 的 Nginx 配置 {#step-3-finalize-nginx-configuration-for-https}

证书保存到 `ssl` 目录后，现在可以更新 Nginx 配置以启用 HTTPS。

1. **更新用于 SSL 的 Nginx 配置**

   将 `nginx/conf.d/open-webui.conf` 的**全部内容替换为下面的最终配置。**

   **把 `<YOUR_DOMAIN_NAME>` 的 4 处都替换成你的域名。**

    ```nginx
    # nginx/conf.d/open-webui.conf

    # Redirect all HTTP traffic to HTTPS
    server {
        listen 80;
        listen [::]:80;
        server_name <YOUR_DOMAIN_NAME>;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl;
        listen [::]:443 ssl;
        http2 on;
        server_name <YOUR_DOMAIN_NAME>;

        ssl_certificate /etc/letsencrypt/live/<YOUR_DOMAIN_NAME>/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/<YOUR_DOMAIN_NAME>/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:ECDHE-RSA-AES128-GCM-SHA256';
        ssl_prefer_server_ciphers off;

        location ~* ^/(auth|api|oauth|admin|signin|signup|signout|login|logout|sso)/ {
            proxy_pass http://open-webui:8080;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 10m;
            proxy_buffering off;
            proxy_cache off;
            client_max_body_size 20M;

            proxy_no_cache 1;
            proxy_cache_bypass 1;
            add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0" always;
            add_header Pragma "no-cache" always;
            expires -1;
        }

        # Profile and model images - cached for performance
        location ~ ^/api/v1/(users/[^/]+/profile/image|models/model/profile/image)$ {
            proxy_pass http://open-webui:8080;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Cache images for 1 day
            expires 1d;
            add_header Cache-Control "public, max-age=86400";
        }

        location ~* \.(css|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://open-webui:8080;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Cache static assets for 7 days
            expires 7d;
            add_header Cache-Control "public, immutable";
        }

        location / {
            proxy_pass http://open-webui:8080;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Extended timeout for long LLM completions (30 minutes)
            proxy_read_timeout 1800;
            proxy_send_timeout 1800;
            proxy_connect_timeout 1800;
            
            proxy_buffering off;
            proxy_cache off;
            client_max_body_size 20M;

            add_header Cache-Control "public, max-age=300, must-revalidate";
        }
    }
    ```

2. **启动所有服务**

   使用最终的安全配置启动 Nginx 和 Open WebUI：

    ```bash
    docker compose up -d
    ```

-----

### 第 4 步：访问你的安全 WebUI {#step-4-access-your-secure-webui}

现在你可以通过 HTTPS 安全访问 Open WebUI 实例了。

→ **`https://<YOUR_DOMAIN_NAME>`**

-----

### （可选）第 5 步：设置自动续期 {#optional-step-5-setting-up-automatic-renewal}

Let's Encrypt 默认签发有效期为 90 天的证书。建议设置 `cron` 任务，自动检查并续期。

1. 打开 crontab 编辑器：

    ```bash
    sudo crontab -e
    ```

2. 添加以下行，以便每天凌晨 3:30 运行续期检查。只有当证书接近过期时，它才会执行续期。

    ```cron
    30 3 * * * /usr/bin/docker run --rm -v "<absolute_path>/ssl/certbot/conf:/etc/letsencrypt" -v "<absolute_path>/ssl/certbot/www:/var/www/certbot" certbot/certbot renew --quiet --webroot --webroot-path=/var/www/certbot --deploy-hook "/usr/bin/docker compose -f <absolute_path>/docker-compose.yml restart nginx"
    ```
