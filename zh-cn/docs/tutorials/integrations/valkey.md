---
sidebar_position: 51
title: "使用 Valkey（兼容 Redis）"
---

# 🔗 使用 Valkey

:::warning

本教程由社区贡献，不受 Open WebUI 团队官方维护或审核。它仅作为演示，说明如何根据你的具体场景自定义 Open WebUI。想参与贡献？请查看贡献教程。

:::

## 什么是 Valkey？

[Valkey](https://valkey.io/) 是 Redis 的开源（BSD 协议）分支，由社区和 Linux 基金会在 Redis 更改许可证后启动。它使用 **Redis 协议**，因此 Open WebUI 通过完全相同的 `REDIS_*` 设置与它通信；在缓存和 WebSocket 方面并没有针对 Valkey 的专属代码路径。如果你想要一个宽松许可证的方案，Valkey 是 Redis 在 Open WebUI 所有使用场景下的直接替代品：登出时的令牌撤销、WebSocket 协调，以及多个 Worker 或实例之间的共享状态。

简而言之，这就是 **[Redis 教程](/tutorials/integrations/redis)** 的同款配置，只是把镜像换成了 Valkey。Open WebUI 所需的全部内容依然通过 `REDIS_URL` 和其他 `REDIS_*` 变量传递。

:::info 两个不同的 "Valkey" 功能，请勿混淆
- **Valkey 作为 Redis 层（本文）** 是缓存、WebSocket 和会话存储。它使用 **`REDIS_URL`** 和 `redis://` 协议配置，因为 Open WebUI 使用的是 Redis 协议。
- **Valkey 作为向量数据库** 是一项独立的、由社区维护的 [向量存储](/reference/env-configuration#valkey)（`VECTOR_DB=valkey`，使用 `valkey-search` 模块）。它使用 **`VALKEY_URL`** 和 `valkey://` 协议配置。

两者互不相关，你可以单独使用其中一个、同时使用两者，或都不用。本教程讨论的是前者。
:::

## 何时需要它？

规则与 Redis 相同：单实例且 `UVICORN_WORKERS=1` 的部署并不严格要求它，但多 Worker（`UVICORN_WORKERS > 1`）和多实例部署需要；没有它时，登出操作无法在 JWT 过期前使其失效。完整分析请参阅 [何时需要 Redis？](/tutorials/integrations/redis#when-is-redis-required)，以及 [扩展指南](/getting-started/advanced-topics/scaling) 中它在更大部署中的位置。

## 设置 Valkey

创建一份 `docker-compose.yml`：

```yml
services:
  valkey:
    image: docker.io/valkey/valkey:8.0.1-alpine
    container_name: valkey
    volumes:
      - valkey-data:/data
    command: "valkey-server --save 30 1 --maxclients 10000 --timeout 1800"
    healthcheck:
      test: "[ $$(valkey-cli ping) = 'PONG' ]"
      start_period: 5s
      interval: 1s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
      - DAC_OVERRIDE
    logging:
      driver: "json-file"
      options:
        max-size: "1m"
        max-file: "1"
    networks:
      - openwebui-network

volumes:
  valkey-data:

networks:
  openwebui-network:
    external: true
```

如果还没有共享网络，请先创建：

```bash
docker network create openwebui-network
```

:::tip 不要省略 `--maxclients` 和 `--timeout`
这些标志不是装饰。默认 `timeout 0` 时，空闲连接永远不会关闭，会慢慢累积直到触达上限，届时所有用户都会在登录时遇到 500 而被锁在外面。完整的原理说明以及配套的客户端 `REDIS_HEALTH_CHECK_INTERVAL` 在 Redis 教程的 [关键：Redis 服务器配置](/tutorials/integrations/redis#critical-redis-server-configuration) 章节中介绍，对 Valkey 同样适用。
:::

## 连接 Open WebUI

让 Open WebUI 指向 Valkey 容器。变量和 `redis://` 协议保持不变；只有主机名（即容器名）发生了变化：

```bash
REDIS_URL="redis://valkey:6379/0"

# WebSocket 支持
ENABLE_WEBSOCKET_SUPPORT="true"
WEBSOCKET_MANAGER="redis"
WEBSOCKET_REDIS_URL="redis://valkey:6379/1"
```

:::info 协议仍然是 `redis://`
Open WebUI 通过 Redis 协议连接，因此连接字符串是 `redis://...`，尽管服务器是 Valkey。这些变量没有 `valkey://` 形式（该协议属于上文提到的、不相关的向量数据库特性）。
:::

除基础配置之外的更多内容（Sentinel、Cluster、AWS Elasticache、键前缀、WebSocket 的 CORS、连接健康检查），请以 [Redis 教程的配置章节](/tutorials/integrations/redis#configuring-open-webui) 作为参考。每一个变量都完全一致。

## 验证

```bash
docker exec -it valkey valkey-cli ping                              # → PONG
docker logs open-webui 2>&1 | grep -i redis                          # 通用连接
docker logs open-webui 2>&1 | grep "Using Redis to manage websockets"
```

日志中出现 "Redis" 是预期的，因为 Open WebUI 使用的是 Redis 协议；当服务器是 Valkey 时，这是正常且正确的。

## 其他所有内容都与 Redis 完全一致

由于 Open WebUI 通过 Redis 协议与 Valkey 通信，[Redis WebSocket 支持](/tutorials/integrations/redis) 教程中的所有配置和故障排查都可以直接套用。只需把镜像替换为 `docker.io/valkey/valkey`，把命令替换为 `valkey-cli` / `valkey-server` 即可。尤其需要关注：

- [配置变量](/tutorials/integrations/redis#configuring-open-webui)，包括 `REDIS_*`、WebSocket、Sentinel 和 Cluster 设置
- [连接耗尽问题的修复](/tutorials/integrations/redis#critical-redis-server-configuration)，`maxclients`、`timeout` 与健康检查
- [故障排查](/tutorials/integrations/redis#troubleshooting)，所有问题与对应解决方案

## 其他资源

- [Valkey 文档](https://valkey.io/docs/)
- [Redis WebSocket 支持](/tutorials/integrations/redis)，同时适用于 Redis 与 Valkey 的完整参考
- [Open WebUI 环境变量](/reference/env-configuration)
