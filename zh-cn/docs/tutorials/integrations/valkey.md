---
sidebar_position: 51
title: "使用 Valkey（兼容 Redis）"
---

# 🔗 使用 Valkey {#using-valkey}

:::warning

本教程由社区贡献，不受 Open WebUI 团队官方维护或审核。它仅作为演示，说明如何根据你的具体场景自定义 Open WebUI。想参与贡献？请查看贡献教程。

:::

## 什么是 Valkey？ {#what-is-valkey}

[Valkey](https://valkey.io/) 是采用 BSD 许可证的 Redis 分支。它使用 **Redis 协议**，因此 Open WebUI 可以使用相同的 `REDIS_*` 设置与它通信。

**配置方式与 [Redis 教程](/tutorials/integrations/redis) 相同**，只需换用 Valkey 镜像。Open WebUI 的测试不覆盖 Valkey。具体含义请参见[步骤 2：添加 Redis](/getting-started/advanced-topics/scaling#step-2-add-redis)。

:::info 两个不同的 "Valkey" 功能，请勿混淆
- **Valkey 作为 Redis 层（本文）** 用于缓存、WebSocket 和会话存储。由于 Open WebUI 使用 Redis 协议，请通过 **`REDIS_URL`** 配置，连接字符串以 `redis://` 开头。
- **Valkey 作为向量数据库** 是一项独立的非核心 [向量存储](/reference/env-configuration#valkey)（`VECTOR_DB=valkey`，使用 `valkey-search` 模块）。它使用 **`VALKEY_URL`** 和 `valkey://` 协议配置。

两者互不相关，你可以单独使用其中一个、同时使用两者，或都不用。本教程讨论的是前者。
:::

## 何时需要它？ {#when-do-you-need-it}

与 Redis 相同：参见 [“何时需要 Redis？”](/tutorials/integrations/redis#when-is-redis-required)。

## 设置 Valkey {#setting-up-valkey}

创建一份 `docker-compose.yml`：

``` yml
services:
  valkey:
    image: docker.io/valkey/valkey:8.0.1-alpine
    container_name: valkey
    volumes:
      - valkey-data:/data
    command: "valkey-server --save 30 1 --appendonly yes --maxmemory-policy noeviction --maxclients 10000 --timeout 1800"
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
使用默认值 `timeout 0` 时，空闲连接不会关闭，会不断累积直至达到上限，导致所有用户登录时收到 500 错误。[关键：Redis 服务器配置](/tutorials/integrations/redis#critical-redis-server-configuration)同样适用于 Valkey。
:::

## 连接 Open WebUI {#connecting-open-webui}

让 Open WebUI 指向 Valkey 容器。变量和 `redis://` 协议保持不变；只有主机名（即容器名）发生了变化：

```bash
REDIS_URL="redis://valkey:6379/0"
WEBSOCKET_MANAGER="redis"
```

:::info 协议仍然是 `redis://`
Open WebUI 通过 Redis 协议连接，因此连接字符串是 `redis://...`，尽管服务器是 Valkey。这些变量没有 `valkey://` 形式（该协议属于上文提到的、不相关的向量数据库特性）。
:::

## 验证 {#verify}

```bash
docker exec -it valkey valkey-cli ping                              # → PONG
docker logs open-webui 2>&1 | grep -i redis                          # general connection
docker logs open-webui 2>&1 | grep "Using Redis to manage websockets"
```

即使服务器用的是 Valkey，日志中出现“Redis”也是正常的，因为 Open WebUI 使用 Redis 协议。

## 其他所有内容都与 Redis 完全一致 {#everything-else-is-identical-to-redis}

由于 Open WebUI 通过 Redis 协议与 Valkey 通信，[Redis WebSocket 支持](/tutorials/integrations/redis) 教程中的所有配置和故障排查都可以直接套用。只需把镜像替换为 `docker.io/valkey/valkey`，把命令替换为 `valkey-cli` / `valkey-server` 即可。尤其需要关注：

- [配置变量](/tutorials/integrations/redis#configuring-open-webui)，包括 `REDIS_*`、WebSocket、Sentinel 和 Cluster 设置
- [连接耗尽问题的修复](/tutorials/integrations/redis#critical-redis-server-configuration)，`maxclients`、`timeout` 与健康检查
- [故障排查](/tutorials/integrations/redis#troubleshooting)，所有问题与对应解决方案

## 其他资源 {#additional-resources}

- [Valkey 文档](https://valkey.io/docs/)
- [Redis WebSocket 支持](/tutorials/integrations/redis)，同时适用于 Redis 与 Valkey 的完整参考
- [Open WebUI 环境变量](/reference/env-configuration)
