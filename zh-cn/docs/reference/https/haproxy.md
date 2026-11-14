---
sidebar_position: 201
title: "使用 HAProxy 的 HTTPS"
---

# Open WebUI 的 HAProxy 配置 {#haproxy-configuration-for-open-webui}


HAProxy（High Availability Proxy，高可用代理）是一款专门的负载均衡和反向代理方案，可配置性很强，设计目标是在较低资源占用下处理大量连接。更多信息请参阅：[https://www.haproxy.org/](https://www.haproxy.org/)

## 安装 HAProxy 和 Let's Encrypt {#install-haproxy-and-lets-encrypt}

首先安装 HAProxy 和 Let's Encrypt 的 certbot：

### Red Hat 系发行版 {#redhat-derivatives}

```sudo dnf install haproxy certbot openssl -y```

### Debian 系发行版 {#debian-derivatives}

```sudo apt install haproxy certbot openssl -y```

## HAProxy 配置基础 {#haproxy-configuration-basics}

HAProxy 的配置默认保存在 ```/etc/haproxy/haproxy.cfg```。这个文件包含了决定 HAProxy 如何运行的全部配置指令。

让 HAProxy 与 Open WebUI 协同工作的基础配置其实很简单。

``` shell
 #---------------------------------------------------------------------

# Global settings

#---------------------------------------------------------------------
global
    # to have these messages end up in /var/log/haproxy.log you will
    # need to:
    #
    # 1) configure syslog to accept network log events. This is done
    #    by adding the '-r' option to the SYSLOGD_OPTIONS in
    #    /etc/sysconfig/syslog
    #
    # 2) configure local2 events to go to the /var/log/haproxy.log
    #   file. A line like the following can be added to
    #   /etc/sysconfig/syslog
    #
    #    local2.*                       /var/log/haproxy.log
    #
    log         127.0.0.1 local2

    chroot      /var/lib/haproxy
    pidfile     /var/run/haproxy.pid
    maxconn     4000
    user        haproxy
    group       haproxy
    daemon

 #adjust the dh-param if too low
    tune.ssl.default-dh-param 2048

#---------------------------------------------------------------------

# common defaults that all the 'listen' and 'backend' sections will

# use if not designated in their block

#---------------------------------------------------------------------
defaults
    mode                    http
    log                     global
    option                  httplog
    option                  dontlognull
    option http-server-close
    option forwardfor       #except 127.0.0.0/8
    option                  redispatch
    retries                 3
    timeout http-request    300s
    timeout queue           2m
    timeout connect         120s
    timeout client          10m
    timeout server          10m
    timeout http-keep-alive 120s
    timeout check           10s
    maxconn                 3000

#http
frontend web
 #Non-SSL
    bind 0.0.0.0:80
 #SSL/TLS
 bind 0.0.0.0:443 ssl crt /path/to/ssl/folder/

    #Let's Encrypt SSL
    acl letsencrypt-acl path_beg /.well-known/acme-challenge/
    use_backend letsencrypt-backend if letsencrypt-acl

 #Subdomain method
    acl chat-acl hdr(host) -i subdomain.domain.tld
    #Path Method
    acl chat-acl path_beg /owui/
    use_backend owui_chat if chat-acl

#Pass SSL Requests to Lets Encrypt
backend letsencrypt-backend
    server letsencrypt 127.0.0.1:8688

#OWUI Chat
backend owui_chat
    # add X-FORWARDED-FOR
    option forwardfor
    # add X-CLIENT-IP
    http-request add-header X-CLIENT-IP %[src]
 http-request set-header X-Forwarded-Proto https if { ssl_fc }
    server chat <ip>:3000

## WebSocket and HTTP/2 Compatibility

Starting with recent versions (including HAProxy 3.x), HAProxy may enable HTTP/2 by default. While HTTP/2 supports WebSockets (RFC 8441), some clients or backend configurations may experience "freezes" or unresponsiveness when icons or data start loading via WebSockets over an H2 tunnel.

If you experience these issues:
1. **Force HTTP/1.1 for WebSockets**: Add `option h2-workaround-bogus-websocket-clients` to your `frontend` or `defaults` section. This prevents HAProxy from advertising RFC 8441 support to the client, forcing a fallback to the more stable HTTP/1.1 Upgrade mechanism.
2. **Backend Version**: Ensure your backend connection is using HTTP/1.1 (the default for `mode http`).

Example addition to your `defaults` or `frontend`:
```shell
defaults
    # ... other settings
    option h2-workaround-bogus-websocket-clients
```

You will see that we have ACL records (routers) for both Open WebUI and Let's Encrypt. To use WebSocket with OWUI, you need to have an SSL configured, and the easiest way to do that is to use Let's Encrypt.

You can use either the subdomain method or the path method for routing traffic to Open WebUI. The subdomain method requires a dedicated subdomain (e.g., chat.yourdomain.com), while the path method allows you to access Open WebUI through a specific path on your domain (e.g., yourdomain.com/owui/). Choose the method that best suits your needs and update the configuration accordingly.

:::info

You will need to expose port 80 and 443 to your HAProxy server. These ports are required for Let's Encrypt to validate your domain and for HTTPS traffic. You will also need to ensure your DNS records are properly configured to point to your HAProxy server. If you are running HAProxy at home, you will need to use port forwarding in your router to forward ports 80 and 443 to your HAProxy server.

:::

## 使用 Let's Encrypt 签发 SSL 证书 {#issuing-ssl-certificates-with-lets-encrypt}

Before starting HAProxy, you will want to generate a self-signed certificate to use as a placeholder until Let's Encrypt issues a proper one. Here's how to generate a self-signed certificate:

```shell
openssl req -x509 -newkey rsa:2048 -keyout /tmp/haproxy.key -out /tmp/haproxy.crt -days 3650 -nodes -subj "/CN=localhost"
```

Then combine the key and certificate into a PEM file that HAProxy can use:

```cat /tmp/haproxy.crt /tmp/haproxy.key > /etc/haproxy/certs/haproxy.pem```

:::info

请务必根据自己的需求和配置更新 HAProxy 设置。

:::

配置好 HAProxy 之后，你就可以使用 certbot 获取并管理 SSL 证书。Certbot 会负责与 Let's Encrypt 的验证流程，并在证书接近过期时自动更新（前提是你启用了 certbot 的自动续期服务）。

你可以运行 `haproxy -c -f /etc/haproxy/haproxy.cfg` 来验证 HAProxy 配置。如果没有错误，就可以用 `systemctl start haproxy` 启动 HAProxy，并用 `systemctl status haproxy` 检查它是否正在运行。

若希望 HAProxy 随系统启动，可执行 `systemctl enable haproxy`。

当 HAProxy 配置完成后，你可以使用 Let's Encrypt 签发正式的 SSL 证书。
首先需要注册 Let's Encrypt，这一步通常只需执行一次：

`certbot register --agree-tos --email your@email.com --non-interactive`

然后申请证书：

```shell
certbot certonly -n --standalone --preferred-challenges http --http-01-port-8688 -d yourdomain.com
```

证书签发后，需要把证书文件和私钥文件合并成一个 HAProxy 可用的 PEM 文件。

```shell
cat /etc/letsencrypt/live/{domain}/fullchain.pem /etc/letsencrypt/live/{domain}/privkey.pem > /etc/haproxy/certs/{domain}.pem
chmod 600 /etc/haproxy/certs/{domain}.pem
chown haproxy:haproxy /etc/haproxy/certs/{domain}.pem
```

随后重启 HAProxy 以应用新证书：
`systemctl restart haproxy`

## HAProxy Manager（便捷部署方案） {#haproxy-manager-easy-deployment-option}

如果你希望有工具自动管理 HAProxy 配置和 Let's Encrypt SSL 证书，我写了一个简单的 Python 脚本，并提供了一个 Docker 容器，可用于创建和管理 HAProxy 配置，以及处理 Let's Encrypt 证书的生命周期。

[https://github.com/shadowdao/haproxy-manager](https://github.com/shadowdao/haproxy-manager)

:::warning

如果你使用这个脚本或容器，请不要把 8000 端口公开暴露到公网！

:::
