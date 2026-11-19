### 在 Windows 上不使用 Docker，配合自签名证书与 Nginx 使用 {#using-a-self-signed-certificate-and-nginx-on-windows-without-docker}

对于基本的内部部署或开发环境，你可以使用 nginx 和自签名证书，通过 HTTPS 访问 Open WebUI。这样就能在局域网内使用麦克风等功能。（大多数浏览器默认不允许在 localhost 之外的不安全 URL 上使用麦克风。）

本指南假设你已通过 pip 安装了 Open WebUI，并正在运行 `open-webui serve`

#### 第 1 步：安装用于生成证书的 openssl {#step-1-installing-openssl-for-certificate-generation}

你首先需要安装 openssl。

你可以从 [Shining Light Productions (SLP)](https://slproweb.com/) 网站下载并安装预编译二进制文件。

或者，如果你已经安装了 [Chocolatey](https://chocolatey.org/)，可以直接快速安装 OpenSSL：

1. 打开命令提示符或 PowerShell。
2. 运行以下命令安装 OpenSSL：

   ```bash
   choco install openssl -y
   ```

---

### **验证安装** {#verify-installation}

安装完成后，打开命令提示符并输入：

```bash
openssl version
```

如果它输出 OpenSSL 版本号（例如 `OpenSSL 3.x.x ...`），说明安装成功。

#### 第 2 步：安装 nginx {#step-2-installing-nginx}

从 [nginx.org](https://nginx.org) 下载官方的 Windows 版 Nginx，或使用 Chocolatey 之类的包管理器。
把下载的 ZIP 文件解压到某个目录（例如 C:\nginx）。

#### 第 3 步：生成证书 {#step-3-generate-certificate}

运行以下命令：

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx.key -out nginx.crt
```

把生成的 nginx.key 和 nginx.crt 文件移动到你选择的目录，或移动到 C:\nginx 目录

#### 第 4 步：配置 nginx {#step-4-configure-nginx}

用文本编辑器打开 `C:\nginx\conf\nginx.conf`。

如果要从局域网访问 Open WebUI，请先用 `ipconfig` 查出本机的局域网 IP 地址，例如 192.168.1.15。

将配置修改为如下内容：

```conf

#user  nobody;
worker_processes  1;

#error_log  logs/error.log;

#error_log  logs/error.log  notice;

#error_log  logs/error.log  info;

#pid        logs/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  120;

    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    server {
        listen 80;
        server_name 192.168.1.15;

        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name 192.168.1.15;

        ssl_certificate C:\\nginx\\nginx.crt;
        ssl_certificate_key C:\\nginx\\nginx.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers on;

        location ~* ^/(auth|api|oauth|admin|signin|signup|signout|login|logout|sso)/ {
            proxy_pass http://localhost:8080;

            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_buffering off;
            proxy_cache off;
            client_max_body_size 20M;
            proxy_read_timeout 10m;

            add_header Cache-Control "no-store, no-cache, must-revalidate" always;
            expires -1;
        }

        # Profile and model images - cached for performance
        location ~ ^/api/v1/(users/[^/]+/profile/image|models/model/profile/image)$ {
            proxy_pass http://localhost:8080;
            proxy_http_version 1.1;
            proxy_set_header Host $host;

            # Cache images for 1 day
            expires 1d;
            add_header Cache-Control "public, max-age=86400";
        }

        location ~* \.(css|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://localhost:8080;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            
            expires 7d;
            add_header Cache-Control "public, immutable";
        }

        location / {
            proxy_pass http://localhost:8080;

            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_buffering off;
            proxy_cache off;
            client_max_body_size 20M;
            
            # Extended timeout for long LLM completions (30 minutes)
            proxy_read_timeout 1800;
            proxy_send_timeout 1800;
            proxy_connect_timeout 1800;

            add_header Cache-Control "public, max-age=300, must-revalidate";
        }
    }
}
```

保存文件后，运行 `nginx -t` 检查配置是否存在语法问题或其他错误。根据安装方式，可能需要先运行 `cd C:\nginx`。

运行 `nginx` 启动 nginx。如果 nginx 服务已经在运行，可以通过 `nginx -s reload` 重新加载配置。

---

现在你应该可以通过 `https://192.168.1.15`（或你的实际 LAN IP）访问 Open WebUI。请根据需要允许 Windows 防火墙放行相关访问。
