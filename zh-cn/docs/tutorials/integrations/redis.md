---
sidebar_position: 50
title: "Redis WebSocket 支持"
---

# 🔗 Redis WebSocket 支持

:::warning
本教程由社区贡献，不受 Open WebUI 团队官方维护或审核。它仅作为演示，说明如何根据你的具体场景自定义 Open WebUI。想参与贡献？请查看贡献教程。
:::

## 概述

本文介绍将 Redis 与 Open WebUI 集成以支持 WebSocket 所需的步骤。按照这些步骤操作，您将能够在 Open WebUI 实例中启用 WebSocket 功能，实现客户端与应用之间的实时通信和更新。

## 何时需要 Redis？

Redis 在 Open WebUI 中服务于两个不同的目的，了解何时需要它对于正确部署至关重要。有关所有扩展要求（PostgreSQL、Redis、向量数据库、存储）的高层概述，请参阅 [扩展 Open WebUI](/getting-started/advanced-topics/scaling) 指南。

### 单实例部署

如果您以**单实例**模式运行 Open WebUI，`UVICORN_WORKERS=1`（默认值），则**基本功能不需要 Redis**。大多数操作不依赖 Redis 就能正常运行。

:::warning 安全性：令牌撤销需要 Redis

没有 Redis 时，**登出不会使用户的 JWT 令牌失效**。该令牌将保持有效，直到自然过期（默认：4 周）。密码更改和管理员主动封禁账户也无法在没有 Redis 的情况下撤销现有令牌。

对于面向生产的部署，请配置 Redis 或缩短 `JWT_EXPIRES_IN` 以限制暴露窗口。有关详情，请参阅 [安全加固指南](/getting-started/advanced-topics/hardening#token-revocation)。

:::

### 多 Worker 和多实例部署

在以下场景中 Redis 是**必需的**：

1. **多个 Uvicorn Worker**（`UVICORN_WORKERS > 1`）
   - 在单一宿主机上运行多个 Worker 进程
   - 需要 Redis 在 Worker 之间共享会话状态和应用配置

2. **多节点部署**
   - 具有多个 Pod 的 Kubernetes 集群
   - 具有多个副本的 Docker Swarm
   - 具有多个 Open WebUI 实例的负载均衡设置
   - 需要 Redis 协调所有实例之间的状态

3. **高可用设置**
   - 任何多个 Open WebUI 进程同时运行的部署模式
   - 需要 Redis 进行会话管理、WebSocket 协调和状态同步

:::warning

**关键要求**

在多 Worker 或多实例场景中没有 Redis，您将会遇到：

- 跨 Worker 的会话管理失败
- 实例间应用状态不一致
- WebSocket 连接无法正常工作
- 间歇性认证失败
- 实时聊天更新丢失

:::

### 前提条件

- 一个有效的 Open WebUI 实例（运行 1.0 或更高版本）
- 一个 Redis 容器（本示例使用 `redis:7-alpine`）
- 系统上已安装 Docker Compose（版本 2.0 或更高）
- 用于 Open WebUI 和 Redis 通信的 Docker 网络
- 对 Docker、Redis 和 Open WebUI 有基本了解

### 关键：Redis 服务器配置

:::danger

**防止“达到最大客户端数”错误**

在配置 Open WebUI 使用 Redis 之前，您**必须**确保 Redis 服务器本身配置正确。一个常见的错误配置会导致连接随时间累积，最终耗尽连接限制，导致**完全认证失败**（所有用户均得到 500 Internal Server Error）。

**问题所在：**

Open WebUI 使用 Redis 进行：
- 令牌验证/撤销检查（每次认证请求）
- WebSocket 管理（实时更新）
- 会话存储（如果启用了 `ENABLE_STAR_SESSIONS_MIDDLEWARE`）

在某些发行版上使用 Redis 默认设置（`maxclients 1000`、`timeout 0`）时，连接永远不会关闭。这些连接在数天或数周内默默累积，直到达到限制。然后，突然所有用户都无法登录。

**症状：**
- 应用程序正常运行数天/数周
- 突然所有用户登录时都得到 500 Internal Server Error
- 日志中出现错误：`redis.exceptions.ConnectionError: max number of clients reached`
- 随着旧连接最终断开，故障可能临时“自愈”，然后再次失败

**解决方案：**

将以下设置添加到您的 Redis 配置中：

```conf
# 允许足够的并发连接
maxclients 10000

# 30 分钟后关闭空闲连接（1800 秒）
# 这不会影响会话有效性，只影响到 Redis 的 TCP 连接
timeout 1800
```

**Docker 部署**时，将以下内容添加到 Redis 命令中：

```yml
services:
  redis:
    image: redis:7-alpine
    command: "redis-server --save 30 1 --appendonly yes --maxclients 10000 --timeout 1800 --maxmemory-policy noeviction"
    # ... 其余配置
```

**为何 `timeout 1800` 是安全的：**

这个超时只影响空闲的 Redis TCP 连接，而不影响用户会话。当连接超时时：
- 用户的 JWT 令牌仍然有效
- 其会话不受影响
- 下一次请求只需重新打开 Redis 连接（增加约 1-5ms，几乎无感知）

**监控：**

检查当前连接数：
```bash
redis-cli INFO clients | grep connected_clients
```

配置正确的 `timeout` 后，该数字应自然波动（活跃时段上升，安静时段下降），而非无限增长。

:::

### 关键：内存驱逐策略

Redis 的 `maxmemory-policy` 决定了当达到内存上限时，Redis 会驱逐（删除）哪些键。配置错误可能导致 Open WebUI 的会话和令牌撤销突然失效。

**Open WebUI 的 Redis 工作集很小**（会话、撤销列表、锁、配置），因此在 `maxmemory` 未设置的情况下，Redis 只需要多少用多少，永远不会驱逐。只有在你确有理由时才设置 `maxmemory` 上限，如果设置后，请监控使用量而非依赖驱逐。

如果你确实必须在有**驱逐**的情况下限制内存，唯一可接受的策略是 `volatile-ttl` 或 `volatile-lru`：它们**仅**驱逐带有 TTL 的键（锁和撤销列表），绝不会驱逐持久化数据。请注意，这仍可能提前丢弃撤销记录，因此相比启用驱逐，更推荐增加 RAM。

### 关键：持久化

示例命令使用 `--save 30 1`（每 30 分钟生成一次 RDB 快照，前提是至少有一个键发生了变化）。在**非正常**重启时，Redis 会丢失自上次快照以来的所有写入——最多 30 分钟的令牌撤销和会话状态——因此崩溃可能导致已登出的令牌被复活，或活动会话被丢弃。

对于生产环境，还应启用追加文件（AOF），使持久化粒度在秒级而非分钟级：

```conf
appendonly yes
appendfsync everysec
```

`appendfsync everysec` 每秒将 AOF 刷新到磁盘，在最坏情况下约丢失一秒钟的数据，对于 Open WebUI 适度的 Redis 工作负载来说，I/O 开销很小且通常可忽略。RDB 和 AOF 可以共存；同时保留两者既能实现快速重启，又能提供秒级持久化。下一节的示例 `command` 已包含 `--appendonly yes` 和 `--maxmemory-policy noeviction`。

:::

## 设置 Redis

要为 WebSocket 支持配置 Redis，需要创建一个包含以下内容的 `docker-compose.yml` 文件：

```yml
services:
  redis:
    image: redis:7-alpine
    container_name: redis
    volumes:
      - redis-data:/data
    command: "redis-server --save 30 1 --appendonly yes --maxclients 10000 --timeout 1800 --maxmemory-policy noeviction"
    healthcheck:
      test: "[ $$(redis-cli ping) = 'PONG' ]"
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
  redis-data:

networks:
  openwebui-network:
    external: true
```

:::info

注意事项

此配置中未包含 `ports` 指令，因为大多数情况下不需要。Redis 服务仍可在 Docker 网络内被 Open WebUI 服务访问。但是，如果需要从 Docker 网络外部访问 Redis 实例（例如用于调试或监控），可以添加 `ports` 指令来暴露 Redis 端口（例如 `6379:6379`）。

上述配置会创建一个名为 `redis` 的 Redis 容器，并挂载一个持久化数据的卷。`healthcheck` 指令确保容器在无法响应 `ping` 命令时重启。`--save 30 1` 命令选项会在至少 1 个键发生更改时，每 30 分钟将 Redis 数据库保存到磁盘，而 `--appendonly yes` 则提供了秒级持久化。

**重要提示：** `--maxclients 10000 --timeout 1800` 标志用于防止连接耗尽，而 `--maxmemory-policy noeviction` 可防止 Redis 静默驱逐 Open WebUI 的会话和令牌撤销键。详情请参阅上方的"关键：Redis 服务器配置"、"关键：内存驱逐策略"和"关键：持久化"部分。

:::

### WebSocket Pub/Sub 缓冲区限制

当 `WEBSOCKET_MANAGER=redis` 启用时，Open WebUI 通过 Redis Pub/Sub 使用 Socket.IO。流式响应和工具事件可能产生较大的 WebSocket 事件，因为部分更新会包含累积的消息状态，而不仅仅是最新的 token 增量。如果 Redis 在传递这些事件时断开了 Pub/Sub 客户端，用户可能会看到流停滞、实时更新丢失，或日志中出现类似以下的消息：

```text
Cannot publish to redis... retrying
Cannot publish to redis... giving up
redis.exceptions.TimeoutError: Timeout connecting to server
```

可通过以下方式检查 Redis 是否因输出缓冲区限制而断开了 Pub/Sub 客户端：

```bash
redis-cli INFO stats | grep client_output_buffer_limit_disconnections
redis-cli SLOWLOG GET 50
redis-cli CONFIG GET client-output-buffer-limit
```

如果慢日志中出现较大的 `PUBLISH socketio ...` 负载，并且 `client_output_buffer_limit_disconnections` 计数持续增加，则应提高 Redis 的 Pub/Sub 输出缓冲区限制。例如：

```conf
# 保持普通客户端不变；允许更大的 WebSocket Pub/Sub 突发流量。
client-output-buffer-limit normal 0 0 0 replica 268435456 67108864 60 pubsub 1073741824 268435456 180
```

上述配置将 Pub/Sub 硬上限设为 1 GB，软上限设为 256 MB，持续 180 秒。请根据你的 Redis 可用内存与预期的 WebSocket 负载大小调整这些数值。较高的限制会让 Redis 对临时较慢的订阅者更具容忍度，但同时也会让每个较慢的 Pub/Sub 客户端在被 Redis 断开前缓存更多内存。

如果你是运行时修改的 Redis 配置，可通过以下命令验证当前生效的值：

```bash
redis-cli CONFIG GET client-output-buffer-limit
```

要为 Open WebUI 和 Redis 之间的通信创建 Docker 网络，运行以下命令：

```bash
docker network create openwebui-network
```

## 配置 Open WebUI

要在 Open WebUI 中启用 Redis 支持，需要根据部署类型配置不同的环境变量。

### 基本配置（所有部署）

对于使用 Redis 的**所有部署**（单实例或多实例），设置以下基本环境变量：

```bash
REDIS_URL="redis://redis:6379/0"
```

此变量配置用于应用状态管理、会话存储和实例间协调的主要 Redis 连接。

### WebSocket 配置

要专门启用 WebSocket 支持，添加以下额外的环境变量：

```bash
ENABLE_WEBSOCKET_SUPPORT="true"
WEBSOCKET_MANAGER="redis"
WEBSOCKET_REDIS_URL="redis://redis:6379/1"
```

:::danger 关键：为 WebSocket 连接配置 CORS

WebSocket 连接中一个非常常见且难以调试的问题是跨源资源共享（CORS）策略配置错误。如果您的 Open WebUI 实例从与后端不同的域或端口访问（例如在反向代理后面），您**必须**设置 `CORS_ALLOW_ORIGIN` 环境变量。该变量告知服务器哪些源被允许访问其资源。

如果未正确配置，WebSocket 连接将静默失败或出现浏览器中晦涩难懂的错误，而忘记设置此变量是 WebSocket 连接问题的常见原因。

**示例：**
如果您通过 `https://my-open-webui.com` 访问 UI，必须设置：

```bash
CORS_ALLOW_ORIGIN="https://my-open-webui.com"
```

您也可以提供以分号分隔的允许域列表。**在生产环境或反向代理设置中请勿跳过此步骤。**

:::

:::info

**Redis 数据库编号**

注意 URL 中不同的数据库编号（`/0` 与 `/1`）：

- `REDIS_URL` 使用数据库 `0` 用于通用应用状态
- `WEBSOCKET_REDIS_URL` 使用数据库 `1` 用于 WebSocket 专用数据

这种分离有助于隔离不同类型的数据。如果您愿意，可以对两者使用相同的数据库编号，但使用单独的数据库有助于更好地组织和潜在的性能优化。

:::

### 可选配置

```bash
REDIS_KEY_PREFIX="open-webui"
```

`REDIS_KEY_PREFIX` 允许多个 Open WebUI 实例共享同一个 Redis 实例而不会发生键冲突。在 Redis 集群模式中，前缀格式为 `{prefix}:`（例如 `{open-webui}:config:*`），以确保配置键的多键操作在同一哈希槽内执行。

### Sentinel 故障转移配置

:::danger 关键：Sentinel 部署的套接字超时

Redis Sentinel 设置需要明确的套接字连接超时配置，以确保正确的故障转移行为。如果没有超时，当 Redis 主节点下线时，应用程序可能无限期挂起——甚至可能阻止应用重启。

**缺少超时配置的症状：**
- 故障转移期间应用程序完全无响应
- 如果第一个 Sentinel 主机无法访问，应用程序在启动时挂起
- 主节点故障转移后恢复需要几分钟而非几秒

**所需配置：**
```bash
REDIS_SOCKET_CONNECT_TIMEOUT=5
```

这将为到 Redis/Sentinel 节点的套接字连接尝试设置 5 秒超时，允许应用程序优雅地故障转移。

:::

:::warning

**如果使用 WEBSOCKET_REDIS_OPTIONS**

当您明确设置 `WEBSOCKET_REDIS_OPTIONS` 时，`REDIS_SOCKET_CONNECT_TIMEOUT` 不会自动应用于 WebSocket 连接。您必须在两处都包含超时：
```bash
REDIS_SOCKET_CONNECT_TIMEOUT=5
WEBSOCKET_REDIS_OPTIONS='{"socket_connect_timeout": 5}'
```

:::

#### 重试和重连逻辑

为了增强 Sentinel 故障转移期间的弹性——即新主节点正在选举和提升的时间窗口——您可以配置重试行为，防止应用程序过快耗尽重连尝试次数。

- **`REDIS_SENTINEL_MAX_RETRY_COUNT`**：设置使用 Sentinel 时 Redis 操作的最大重试次数（默认：`2`）。
- **`REDIS_RECONNECT_DELAY`**：在重试尝试之间添加可选延迟（以**毫秒**为单位）（例如 `REDIS_RECONNECT_DELAY=500`）。这可以防止紧密的重试循环，否则可能在新主节点就绪之前压垮事件循环或阻塞应用程序。

#### 连接健康检查

如果您的 Redis 服务器配置了 `timeout`（推荐——见上文），空闲时间超过该超时的连接池连接将被服务器端回收。没有健康检查时，下一个获取这些死连接的请求将因 `ConnectionError: Connection reset by peer` 而失败。

- **`REDIS_HEALTH_CHECK_INTERVAL`**：redis-py 在重用之前对空闲连接池连接发送 PING 的频率（秒）（例如 `REDIS_HEALTH_CHECK_INTERVAL=60`）。该值必须**短于** Redis 服务器的 `timeout` 以及到 Redis 路径上任何防火墙/负载均衡器的空闲超时。设置为 `0` 或留空以禁用。
- **`REDIS_SOCKET_KEEPALIVE`**：在所有 Redis 客户端套接字上启用 TCP `SO_KEEPALIVE`（例如 `REDIS_SOCKET_KEEPALIVE=True`）。启用后，OS 内核会在空闲连接上发送 TCP keepalive 探测，检测由防火墙/负载均衡器静默重置或 TCP 层网络抖动引起的半关闭套接字。

这两种机制是互补的：
- `REDIS_HEALTH_CHECK_INTERVAL` 在**应用层**工作——redis-py 在检出时对空闲连接发送 PING，验证套接字并重置服务器的空闲计时器。
- `REDIS_SOCKET_KEEPALIVE` 在 **TCP 层**工作——内核即使在没有应用层流量流动时也能检测到死连接。

:::tip 推荐组合

对于稳健的生产部署，将三层机制一起配置：

| 机制 | 层级 | 覆盖范围 | 示例 |
|-----------|-------|--------|---------|
| `timeout 1800`（redis.conf） | 服务器 | 回收应用程序遗忘的泄漏/孤立连接 | 安全网 |
| `REDIS_HEALTH_CHECK_INTERVAL=60` | 应用 | 在真实命令使用前检测死连接；保持连接池连接活跃 | 主动保护 |
| `REDIS_SOCKET_KEEPALIVE=True` | TCP/内核 | 检测防火墙、负载均衡器、网卡抖动导致的静默网络重置引起的半关闭套接字 | 网络层保护 |

:::

### Redis 集群模式

对于使用 Redis 集群（包括 **AWS Elasticache Serverless** 等托管服务）的部署，使用以下配置启用集群模式：

```bash
REDIS_URL="redis://your-cluster-endpoint:6379/0"
REDIS_CLUSTER="true"
```

:::info

**关键配置说明**

- `REDIS_CLUSTER` 启用集群感知连接处理
- `REDIS_URL` 应指向集群的配置端点
- 如果定义了 `REDIS_SENTINEL_HOSTS`，此选项无效（Sentinel 优先）
- 使用集群模式时，`REDIS_KEY_PREFIX` 自动格式化为 `{prefix}:`，以确保多键操作在同一哈希槽内执行

:::

#### AWS Elasticache Serverless

对于 AWS Elasticache Serverless 部署，使用以下配置：

```bash
REDIS_URL="rediss://your-elasticache-endpoint.serverless.use1.cache.amazonaws.com:6379/0"
REDIS_CLUSTER="true"
```

注意 `rediss://` 方案（双 's'），它启用 TLS，这是 Elasticache Serverless 所必需的。

#### OpenTelemetry 支持

Redis 集群模式与 OpenTelemetry 仪表完全兼容。启用 `ENABLE_OTEL` 后，无论使用单 Redis 实例、Redis Sentinel 还是 Redis 集群模式，Redis 操作都会被正确追踪。

### 完整配置示例

以下是显示所有 Redis 相关环境变量的完整示例：
```bash
# 多 Worker/多实例部署所需
REDIS_URL="redis://redis:6379/0"

# WebSocket 支持所需
ENABLE_WEBSOCKET_SUPPORT="true"
WEBSOCKET_MANAGER="redis"
WEBSOCKET_REDIS_URL="redis://redis:6379/1"

# Sentinel 部署推荐（防止故障转移挂起）
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_SENTINEL_MAX_RETRY_COUNT=5
REDIS_RECONNECT_DELAY=1000

# 推荐：检测陈旧的连接池连接（必须小于 Redis 服务器超时）
REDIS_HEALTH_CHECK_INTERVAL=60

# 推荐：在内核级启用 TCP keepalive 进行死连接检测
REDIS_SOCKET_KEEPALIVE=True

# 可选
REDIS_KEY_PREFIX="open-webui"
```

对于 Redis Sentinel 部署，请确保设置 `REDIS_SOCKET_CONNECT_TIMEOUT` 以防止主节点故障转移期间应用程序挂起。

#### Redis 集群模式示例

对于 Redis 集群部署（包括 AWS Elasticache Serverless）：

```bash
# Redis 集群模式所需
REDIS_URL="rediss://your-cluster-endpoint:6379/0"
REDIS_CLUSTER="true"

# WebSocket 支持所需
ENABLE_WEBSOCKET_SUPPORT="true"
WEBSOCKET_MANAGER="redis"
WEBSOCKET_REDIS_URL="rediss://your-cluster-endpoint:6379/0"
WEBSOCKET_REDIS_CLUSTER="true"

# 可选
REDIS_KEY_PREFIX="open-webui"
```

### Docker 运行示例

使用 Docker 运行 Open WebUI 时，将其连接到同一 Docker 网络并包含所有必要的 Redis 变量：

```bash
docker run -d \
  --name open-webui \
  --network openwebui-network \
  -v open-webui:/app/backend/data \
  -p 3000:8080 \
  -e REDIS_URL="redis://redis:6379/0" \
  -e ENABLE_WEBSOCKET_SUPPORT="true" \
  -e WEBSOCKET_MANAGER="redis" \
  -e WEBSOCKET_REDIS_URL="redis://redis:6379/1" \
  -e REDIS_KEY_PREFIX="open-webui" \
  ghcr.io/open-webui/open-webui:main
```

:::warning

**关于服务名称的重要说明**

在上述示例中，我们使用 `redis://redis:6379`，因为：

- `redis` 是 docker-compose.yml 中定义的容器名称
- Docker 内部 DNS 将此名称解析为网络内正确的 IP 地址
- 这是 Docker 部署的推荐方式

从一个容器连接到另一个容器时，**不要**使用 `127.0.0.1` 或 `localhost`——这些指向容器自身的 localhost，而非 Redis 容器。

:::

### 多 Worker 配置

如果在单台主机上运行多个 Uvicorn worker，添加此变量：

```bash
UVICORN_WORKERS="4"  # 根据 CPU 核心数调整
REDIS_URL="redis://redis:6379/0"  # UVICORN_WORKERS > 1 时必须
```

:::danger

**关键：UVICORN_WORKERS > 1 时必须使用 Redis**

如果将 `UVICORN_WORKERS` 设置为大于 1 的值，则**必须**配置 `REDIS_URL`。否则将导致：

- 请求之间会话状态丢失
- 身份验证间歇性失败
- 应用程序配置不一致
- WebSocket 功能异常

:::

:::danger

**关键：默认 ChromaDB（SQLite）与多 Worker 不兼容**

除 Redis 外，您还必须处理**向量数据库**问题。默认 ChromaDB 使用本地 SQLite 支持的 `PersistentClient`，**不支持 fork 安全**。当 uvicorn 派生多个 worker 时，对同一 SQLite 文件的并发写入将在文档上传时立即导致 worker 崩溃（`Child process died`）。

您必须：
- 切换到客户端-服务器向量数据库（`VECTOR_DB=pgvector`、`mariadb-vector`、`milvus` 或 `qdrant`）
- 将 ChromaDB 作为独立 HTTP 服务器运行并设置 `CHROMA_HTTP_HOST` / `CHROMA_HTTP_PORT`

详情见 [扩展与高可用指南](/troubleshooting/multi-replica#6-worker-crashes-during-document-upload-chromadb--multi-worker)。

:::

## 验证

### 验证 Redis 连接

首先，确认 Redis 实例正在运行并接受连接：

```bash
docker exec -it redis redis-cli -p 6379 ping
```

如果 Redis 实例运行正常，此命令应输出 `PONG`。

### 验证 Open WebUI 配置

使用正确的 Redis 配置启动 Open WebUI 实例后，检查日志以确认集成成功：

#### 检查通用 Redis 连接

查找表明 Redis 正在用于应用程序状态的日志消息：

```bash
docker logs open-webui 2>&1 | grep -i redis
```

#### 检查 WebSocket Redis 连接

如果已启用 WebSocket 支持，您应看到此特定日志消息：

```
DEBUG:open_webui.socket.main:Using Redis to manage websockets.
```

专门检查此项：

```bash
docker logs open-webui 2>&1 | grep "Using Redis to manage websockets"
```

### 验证 Redis 键

您还可以验证 Open WebUI 实际上正在向 Redis 写入数据：

```bash
# 列出所有 Open WebUI 键
docker exec -it redis redis-cli --scan --pattern "open-webui*"

# 或使用默认 Redis CLI
docker exec -it redis redis-cli --scan --pattern "open-webui*"
```

如果 Redis 配置正确，您应看到具有已配置前缀的键（例如 `open-webui:session:*`、`open-webui:config:*`）。

### 测试多 Worker 设置

如果运行 `UVICORN_WORKERS > 1`，测试会话是否在 worker 之间持久化：

1. 登录 Open WebUI
2. 多次刷新页面
3. 您应始终保持登录状态

如果随机被登出或看到身份验证错误，Redis 可能未正确配置。

## 故障排除

### 常见问题与解决方案

#### 问题："Connection to Redis failed"

**症状：**

- 日志中出现关于 Redis 连接的错误消息
- 应用程序无法启动或崩溃
- WebSocket 不工作

**解决方案：**

1. 验证 Redis 容器是否正在运行：`docker ps | grep redis`
2. 检查 Redis 健康状态：`docker exec -it redis redis-cli ping`
3. 验证网络连接：`docker network inspect openwebui-network`
4. 确保 `REDIS_URL` 使用正确的容器名称，而非 `127.0.0.1` 或 `localhost`
5. 检查两个容器是否在同一 Docker 网络上

#### 问题：页面刷新后"会话丢失"（使用 UVICORN_WORKERS > 1 时）

**症状：**

- 用户随机被登出
- 身份验证有效但不持久
- 每次刷新页面行为不同

**原因：** 使用多个 worker 时未配置 `REDIS_URL`

**解决方案：**
添加 `REDIS_URL` 环境变量：

```bash
REDIS_URL="redis://redis:6379/0"
```

#### 问题："WebSocket 不工作"

**症状：**

- 实时聊天更新不显示
- 需要刷新页面才能看到新消息
- 浏览器控制台出现连接错误

**解决方案：**

1. 验证所有 WebSocket 环境变量已设置：
   - `ENABLE_WEBSOCKET_SUPPORT="true"`
   - `WEBSOCKET_MANAGER="redis"`
   - `WEBSOCKET_REDIS_URL="redis://redis:6379/1"`
2. 检查日志中是否有：`DEBUG:open_webui.socket.main:Using Redis to manage websockets.`
3. 验证 Redis 可从 Open WebUI 容器访问

#### 问题："多个 Open WebUI 实例互相干扰"

**症状：**

- 配置更改影响其他实例
- 部署之间会话冲突
- 运行多个 Open WebUI 安装时出现意外行为

**解决方案：**
为每个安装使用不同的 `REDIS_KEY_PREFIX` 值：

```bash
# 实例 1
REDIS_KEY_PREFIX="openwebui-prod"

# 实例 2
REDIS_KEY_PREFIX="openwebui-dev"
```

#### 问题："Redis 内存使用持续增长"

**症状：**

- Redis 内存使用随时间增加
- 容器最终耗尽内存

:::danger
**不要**用 `--maxmemory-policy allkeys-lru` 来"修复"这个问题。Open WebUI 的 Redis 存储的是令牌撤销键、会话池和锁，而不是可丢弃的缓存。`allkeys-*` 策略可能静默地重新激活已登出的令牌，并破坏会话。请参阅[内存驱逐策略](#关键内存驱逐策略)。
:::

内存持续增长通常意味着键在不断增加，而非缺少驱逐策略，因此应先调查原因，而不是用驱逐来掩盖问题。

**解决方案：**

1. 查找是什么在消耗内存，以及它是否在不断增长：

   ```bash
   docker exec -it redis redis-cli info memory
   docker exec -it redis redis-cli --bigkeys
   docker exec -it redis redis-cli info keyspace   # 每个 DB 的键数量
   ```

2. 确认 `timeout` 已设置（空闲连接累积也会表现为内存增长），参见[关键：Redis 服务器配置](#关键redis-服务器配置)部分。

3. 如果必须限制内存，请同时设置 `maxmemory` 上限并搭配 **`noeviction`**，这样 Redis 会大声报错而不是丢弃认证/会话状态，然后对 `used_memory` 设置告警：

   ```conf
   maxmemory 512mb
   maxmemory-policy noeviction
   ```

4. 不要对正在运行的实例执行 `FLUSHDB`/`FLUSHALL`：这会清除活动会话、撤销列表和锁。如果需要清理累积的状态，请在维护窗口重启 Redis 容器。

#### 问题：运行数天/数周后出现 "max number of clients reached"

**症状：**

- 应用程序运行良好一段时间后突然失败
- 所有登录尝试返回 500 Internal Server Error
- 日志中出现错误：`redis.exceptions.ConnectionError: max number of clients reached`
- 可能暂时恢复，然后再次失败

**原因：** 由于连接积累，达到 Redis `maxclients` 限制。发生这种情况时：
- `timeout` 设置为 `0`（连接从不关闭）
- `maxclients` 对于您的使用模式来说太低

**解决方案：**

1. 检查当前连接数：
   ```bash
   redis-cli INFO clients | grep connected_clients
   ```

2. 检查当前设置：
   ```bash
   redis-cli CONFIG GET maxclients
   redis-cli CONFIG GET timeout
   ```

3. 修复配置：
   ```bash
   redis-cli CONFIG SET maxclients 10000
   redis-cli CONFIG SET timeout 1800
   ```

4. 通过添加到 `redis.conf` 或 Docker 命令使其永久生效：
   ```conf
   maxclients 10000
   timeout 1800
   ```

5. 重启 Redis 以清除积累的连接：
   ```bash
   # 对于 systemd
   sudo systemctl restart redis
   
   # 对于 Docker
   docker restart redis
   ```

**预防：** 始终将 `timeout` 配置为合理的值（例如 1800 秒）。超时仅影响空闲 TCP 连接，不影响用户会话——这是安全且推荐的做法。与客户端侧的 `REDIS_HEALTH_CHECK_INTERVAL` 配合使用（见下文）。

#### 问题：空闲期后首次请求出现 "Connection reset by peer" 错误

**症状：**

- 日志中零星出现 `redis.exceptions.ConnectionError: Connection reset by peer`
- 错误往往在低活动期（夜晚、周末）后出现
- 触发错误的请求以 500 Internal Server Error 失败，但后续请求成功
- 配置了 Redis 服务器 `timeout` 时更常见（这是推荐做法——见上文）

**原因：** Redis 服务器通过其 `timeout` 设置回收了空闲连接，但 redis-py 中的连接池套接字未意识到连接已死。下一个从池中获取该套接字的请求向已关闭的连接发送了命令。

**解决方案：**

将 `REDIS_HEALTH_CHECK_INTERVAL` 环境变量设置为**小于** Redis 服务器 `timeout` 的值：

```bash
# Redis 服务器超时为 1800 秒（30 分钟），所以每 60 秒检查一次
REDIS_HEALTH_CHECK_INTERVAL=60
```

这告知 redis-py 在重用空闲时间超过 60 秒的连接池连接之前先发送 PING。如果连接已死，则透明替换。PING 还会重置服务器的空闲计时器，保持活跃使用的连接存活。

**如何选择合适的值：**

| Redis `timeout` | 建议的 `REDIS_HEALTH_CHECK_INTERVAL` |
|-----------------------|-----------------------------------------|
| 300（5 分钟）         | 30                                      |
| 900（15 分钟）        | 60                                      |
| 1800（30 分钟）       | 60                                      |
| 3600（1 小时）        | 120                                     |

健康检查间隔还应短于应用程序与 Redis 之间任何防火墙或负载均衡器的空闲超时。

### 其他资源

- [Redis 文档](https://redis.io/docs)
- [使用 Valkey](/tutorials/integrations/valkey)：开源、兼容 Redis 的即插即用替代方案
- [Docker Compose 文档](https://docs.docker.com/compose/overview/)
- [Open WebUI 环境变量](/reference/env-configuration/)
- [sysctl 文档](https://man7.org/linux/man-pages/man8/sysctl.8.html)

### 获取帮助

如果按照本指南操作后仍遇到问题：

1. 查看 [Open WebUI GitHub Issues](https://github.com/open-webui/open-webui/issues)
2. 检查完整配置是否有拼写错误
3. 验证所有容器可以在 Docker 网络上通信
4. 收集 Open WebUI 和 Redis 容器的相关日志
5. 加入 Open WebUI Discord 获取社区支持

按照这些步骤和故障排除提示，您应该能够为 Open WebUI 配置 Redis，实现应用程序状态管理和 WebSocket 支持，从而实现可靠的多实例部署和客户端与应用程序之间的实时通信。
