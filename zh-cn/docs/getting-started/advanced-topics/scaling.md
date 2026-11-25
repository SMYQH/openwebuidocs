---
sidebar_position: 2
title: "扩展 Open WebUI"
---

# 扩展 Open WebUI {#scaling-open-webui}

Open WebUI 可以从单用户扩展到全组织部署。它采用**无状态、容器优先的架构**，扩展方式与其他现代 Web 应用相同：先将状态迁移到共享服务，再在负载均衡器后增加实例。

本指南概述扩展步骤。各变量的详细说明见[环境变量参考](/reference/env-configuration)。单实例调优请参见[优化、性能与内存占用](/troubleshooting/performance)。扩展后的部署出现问题时，请参见[扩缩容与高可用故障排查](/troubleshooting/multi-replica)。

---

## 了解默认配置 {#understanding-the-defaults}
Open WebUI 默认是**自包含的单实例部署**。标准 Docker 镜像包含：

- **内嵌 SQLite**，通过持久化卷保存应用数据
- **内嵌 ChromaDB**（同样基于 SQLite），用于 RAG 嵌入
- **本地文件存储**（`STORAGE_PROVIDER=local`），用于 `DATA_DIR/uploads` 下的上传文件
- **单个 Uvicorn worker**，不需要外部数据库或 Redis

这让部署时间和运维开销都很低，也让**气隙部署**变得简单。

**水平扩展需要共享的持久化与协调机制**，这样每个副本才能基于同一份数据工作。在增加副本之前，请先切换到 PostgreSQL 和客户端/服务器模式的向量数据库，配置共享文件存储并加入 Redis。之后应用层就可以在负载均衡器后面独立扩展。

:::warning 外部数据库不保存上传的文件
PostgreSQL 保存文件元数据和存储路径，向量数据库保存嵌入向量，两者都不保存文件本身。在增加副本之前，请配置**外部对象存储（S3、GCS 或 Azure Blob）**，或配置每个副本都能访问的**共享文件系统**。参见[第 5 步](#step-5-share-file-storage-across-instances)。
:::

---

## 第 1 步——切换到 PostgreSQL {#step-1-switch-to-postgresql}
**何时需要：** 你计划运行不止一个 Open WebUI 实例，或者你的 SQLite 文件位于本地直连的 SSD/NVMe 之外的任何介质上。

:::tip 如果你是本地磁盘上的单副本部署，就不需要这一步
对于单副本部署、个人使用、评估、家庭实验室和小团队，SQLite 完全够用，**只要数据库文件位于本地直连的 SSD/NVMe 上。** 你可以直接跳到后面需要的步骤。
:::

SQLite 把所有内容存在单个文件中，对多进程的并发写入处理不佳。PostgreSQL 支持大量并发连接。

**需要做什么：**

把 [`DATABASE_URL`](/reference/env-configuration#database_url) 指向你的 PostgreSQL 服务器：

```
DATABASE_URL=postgresql://user:password@db-host:5432/openwebui
```

请使用普通的 `postgresql://` URL，Open WebUI 会自行选择异步驱动（psycopg 3）。

**需要了解的关键点：**

- Open WebUI **不会**在数据库之间迁移数据，因此在 SQLite 中已有生产数据之前就要规划好这一步。
- **连接池。** 未设置 [`DATABASE_POOL_SIZE`](/reference/env-configuration#database_pool_size) 时，每个进程使用 SQLAlchemy 默认的 5 个连接加 10 个溢出连接。一旦设置了 `DATABASE_POOL_SIZE`，溢出连接默认值会降为 `0`，因此还要设置 [`DATABASE_POOL_MAX_OVERFLOW`](/reference/env-configuration#database_pool_max_overflow)。`DATABASE_POOL_SIZE=0` 会禁用连接池。对于繁忙实例，`DATABASE_POOL_SIZE=15` 配 `DATABASE_POOL_MAX_OVERFLOW=20` 是一个不错的起点。
- **按数据库服务器规划连接数。** 启用 PostgreSQL 池后，每个工作进程各有一个同步和一个异步应用连接池。当 `VECTOR_DB=pgvector` 且未设置 `PGVECTOR_DB_URL` 时，后者默认使用 `DATABASE_URL`。即使它指向同一台服务器，pgvector 也会针对该 URL 创建独立引擎。统计连接到每台服务器的连接池，再乘以所有副本的工作进程总数。示例见 [PostgreSQL 连接池容量](/reference/env-configuration#database_pool_size)。
- 单实例的连接池调优请参见[连接池大小](/troubleshooting/performance#connection-pool-sizing)。

凭据处理和静态加密请参见[加固指南的数据库一节](/getting-started/advanced-topics/hardening#database)。

### 为什么一旦扩展（或升级），网络存储上的 SQLite 就会出问题 {#why-sqlite-on-network-storage-fails-the-moment-you-scale-or-upgrade}

在 NFS、CephFS、Azure Files 或网络支撑的 Kubernetes PVC 上，SQLite 在低负载时还能正常工作，一旦并发上来就会失败：连接池超时、`database is locked`，以及简单查询卡住数秒甚至数分钟。每次提交都要等待一次缓慢的网络 `fsync`，而 SQLite 的文件锁定[在网络文件系统上并不可靠](https://www.sqlite.org/faq.html#q5)。把连接池调得更大只会让情况更糟。

只要 SQLite 仍留在网络存储上，就没有哪个配置能解决这个问题。请切换到 PostgreSQL（本步骤），或者在单节点部署中把 `webui.db` 移到本地 SSD/NVMe。上传文件与 RAG 文件仍可留在共享文件系统上。机制层面的说明见[磁盘 I/O 延迟](/troubleshooting/performance#disk-io-latency-sqlite--storage)；症状与临时缓解办法见[数据库损坏 / “锁定”错误](/troubleshooting/multi-replica#4-database-corruption--locked-errors)。

---

## 第 2 步——加入 Redis {#step-2-add-redis}
**何时需要：** 你运行不止一个 Open WebUI 实例。

Redis 让所有实例能够协同工作。它有两个作用：

- [`REDIS_URL`](/reference/env-configuration#redis_url)：登出时的令牌吊销、停止和恢复在其他实例上运行的响应、登录限流、OAuth 令牌刷新锁，以及可选的基础模型缓存。
- [`WEBSOCKET_MANAGER=redis`](/reference/env-configuration#websocket_manager)：把实时更新（流式 token、频道消息、笔记编辑）送达连接在其他实例上的用户，并在实例之间共享模型列表、活跃用户和在线状态。它连接到 [`WEBSOCKET_REDIS_URL`](/reference/env-configuration#websocket_redis_url)，后者默认为 `REDIS_URL`。

**需要做什么：**

在每个实例上同时设置：

```
REDIS_URL=redis://redis-host:6379/0
WEBSOCKET_MANAGER=redis
```

请让 [`ENABLE_WEBSOCKET_SUPPORT`](/reference/env-configuration#enable_websocket_support) 保持默认值 `true`。

Open WebUI 使用的是普通 Redis 命令，因此像 [**Valkey**](/tutorials/integrations/valkey) 或 **Dragonfly** 这样的 Redis 协议服务器用同样的设置也能工作。两者都不在 Open WebUI 的测试范围内。请使用较新的版本，并让 Dragonfly 以独立模式运行，因为它的集群模式不具备实时更新所依赖的发布/订阅能力。

**需要了解的关键点：**

- 单实例部署在没有 Redis 时也能工作，但此时**登出不会吊销会话令牌**：它会一直有效直到过期（默认 4 周）。修改密码和**登出所有设备**在没有 Redis 时也照常可用。对于生产环境或敏感数据，请添加 Redis 或缩短 `JWT_EXPIRES_IN`。参见[令牌吊销](/getting-started/advanced-topics/hardening#token-revocation)。
- [Tether](/ecosystem/tether) 连接在 [`UVICORN_WORKERS`](/reference/env-configuration#uvicorn_workers) 大于 1 时需要 Redis。参见它的[要求](/ecosystem/tether#requirements)。
- **Redis Sentinel：** 设置 [`REDIS_SENTINEL_HOSTS`](/reference/env-configuration#redis_sentinel_hosts) 和 [`WEBSOCKET_SENTINEL_HOSTS`](/reference/env-configuration#websocket_sentinel_hosts)（websocket 管理器只读取后者）。`REDIS_URL` 的主机部分应为 master 的服务名。设置 `REDIS_SOCKET_CONNECT_TIMEOUT=5`，避免故障转移时长时间挂起。
- **Redis Cluster**（例如以集群模式运行的 AWS ElastiCache）：设置 [`REDIS_CLUSTER=true`](/reference/env-configuration#redis_cluster)。websocket 管理器会遵循该设置。
- 设置 Redis 服务器的 `timeout`（例如 `1800`）以及足够高的 `maxclients`（10000+），以防止连接耗尽。
- 对于大流量流式输出，请提高 Redis 的 Pub/Sub 输出缓冲区限制；参见 [WebSocket Pub/Sub 缓冲区限制](/tutorials/integrations/redis#websocket-pubsub-buffer-limits)。
- 所有实例必须使用相同的 [`WEBSOCKET_REDIS_ROOM_CHANNELS`](/reference/env-configuration#websocket_redis_room_channels) 值。参见[按房间分配的 Redis 频道](#per-room-redis-channels)。
- 对于绝大多数部署，即使有数千名用户，**单个 Redis 实例**也足够。在考虑 Redis Cluster 之前，请先排查可修复的配置问题（参见[常见错误模式](/troubleshooting/performance#common-anti-patterns)）。

如需完整的 Redis 搭置（Docker Compose、Sentinel、Cluster、验证），请参阅 [Redis WebSocket 支持](/tutorials/integrations/redis) 教程。若需处理反向代理后的 WebSocket 和 CORS 问题，请参见[连接错误](/troubleshooting/connection-error#https-tls-cors--websocket-issues)。

---

## 第 3 步——运行多个实例 {#step-3-run-multiple-instances}
**何时需要：** 你需要服务更多用户，或希望获得高可用性。

在共享状态就绪之后，在**负载均衡器**后面按需运行任意数量的相同实例。

:::warning
请先完成**第 1、2、4、5 步**。所有副本还必须使用相同的 `WEBUI_SECRET_KEY`，否则用户会遇到[登录循环和 401 错误](/troubleshooting/multi-replica#1-login-loops--401-unauthorized-errors)。关于如何生成、保存和轮换该密钥（以及 `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY`），参见[密钥](/getting-started/advanced-topics/hardening#secret-key)。预检查清单参见[核心要求检查表](/troubleshooting/multi-replica#core-requirements-checklist)。
:::

每个实例保持一个 worker（[`UVICORN_WORKERS=1`](/reference/env-configuration#uvicorn_workers)，默认值），通过调整副本数来扩展。这样每个副本都有自己的内存上限，也可以单独重启。

- **Docker Compose**（单主机）：在 Open WebUI 服务上设置 `deploy.replicas`，或运行 `docker compose up -d --scale open-webui=3`。请移除该服务上固定的主机端口映射（如 `3000:8080`），因为只有一个容器能绑定主机端口。在同一个 Compose 项目中放置一个反向代理（Nginx、Traefik 或 Caddy），并将其指向 `open-webui:8080`；Docker 的 DNS 会为该服务名返回所有副本，代理再以轮询方式把请求分摊到它们。启用 WebSocket（默认开启）时，普通的轮询即可；粘性会话何时有帮助请参见[会话亲和性](/troubleshooting/multi-replica#session-affinity-sticky-sessions)。Nginx 只在启动时解析该名称，因此修改副本数后需要重新加载它。
- **Docker Swarm** 或 **Kubernetes**（多主机）：设置服务或 Deployment 的副本数，或交给自动扩缩容机制管理。参见 [Docker Swarm](/deployment/docker-swarm) 和 [Kubernetes](/deployment/kubernetes)。

只让一个进程执行数据库迁移；参见[更新与迁移](/troubleshooting/multi-replica#updates-and-migrations)。Compose 会给每个副本相同的设置，因此 `ENABLE_DB_MIGRATIONS` 无法自行挑选其中一个。升级时先缩容到一个副本（`docker compose up -d --scale open-webui=1`），等待其健康后再扩回去。

### 将 HTTP 压缩卸载给负载均衡器 {#offload-http-compression-to-the-load-balancer}

当负载均衡器、Ingress 或 CDN 位于 Open WebUI 之前时，让它来压缩 HTTP 响应，并关闭应用自身的压缩：

```
ENABLE_COMPRESSION_MIDDLEWARE=false
```

否则每个副本都要花费几个百分点的 CPU 来压缩响应。流式对话响应和 WebSocket 流量两种情况下都不受影响。如果前方没有任何组件进行压缩，首次页面加载和大型 JSON 响应会变大。参见 [`ENABLE_COMPRESSION_MIDDLEWARE`](/reference/env-configuration#enable_compression_middleware)。

WebSocket 帧由 WebSocket 服务器自身压缩。在高强度流式传输下，可以将其关闭：

```
UVICORN_WS_PER_MESSAGE_DEFLATE=false
```

对话响应以每个 token 一个小帧的方式流式传输，因此压缩每一帧都要为每个订阅者消耗 CPU，却几乎没有任何收益。参见 [`UVICORN_WS_PER_MESSAGE_DEFLATE`](/reference/env-configuration#uvicorn_ws_per_message_deflate)。

在较大规模下还有两项设置很重要：

- **心跳。** [`WEBSOCKET_HEARTBEAT_INTERVAL=60`](/reference/env-configuration#websocket_heartbeat_interval) 会把每个打开标签页的心跳流量减半（默认每 30 秒一次）。其代价参见 [WebSocket 心跳](/troubleshooting/performance#websocket-heartbeats)。
- **残留的流。** 流式响应会保存在 Redis 中，以便重新连接的浏览器能够继续接收，并在完成时删除。[`REDIS_RESPONSE_STREAM_TTL`](/reference/env-configuration#redis_response_stream_ttl)（默认 `3600` 秒）会清理副本在流式传输中途被杀死时留下的条目。

#### 在代理层配合静态资源缓存 {#pair-it-with-static-asset-caching-at-the-proxy}

关闭应用侧压缩时，如果代理还能**缓存静态资源**，效果会更好，这样每个浏览器只需下载一次压缩后的资源包。

所有前端 JavaScript 和 CSS 都位于 `/_app/immutable/` 下，文件名带有**内容哈希**。同一个 URL 的内容永不改变，因此这些文件可以安全地长时间缓存。HTML 外壳和 `/_app/version.json` 必须保持短时效，因为浏览器要靠它们来发现新的构建版本。

以 Nginx 为例：

``` nginx
proxy_cache_path /var/cache/nginx/openwebui levels=1:2 keys_zone=OPENWEBUI_STATIC:10m
                 max_size=1g inactive=7d use_temp_path=off;

# Content-hashed bundles: immutable by construction
location ^~ /_app/immutable/ {
    proxy_pass http://openwebui;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header Connection "";
    proxy_buffering on;
    proxy_cache OPENWEBUI_STATIC;
    proxy_cache_valid 200 7d;
    proxy_cache_lock on;
    add_header Cache-Control "public, max-age=31536000, immutable" always;
}
```

- `immutable` 可以阻止浏览器在重新加载时重新验证。`max-age=2592000, immutable`（30 天）效果几乎一样。
- HTML 外壳和 `/_app/version.json` 应保持不缓存或只缓存几分钟，否则用户会错过升级。除非设置了 [`CACHE_CONTROL`](/reference/env-configuration#cache_control)，否则 Open WebUI 会以 `Cache-Control: no-cache` 发送 HTML 外壳；请在代理层保留该头部。
- `proxy_cache` 让每个资源在每个缓存生命周期内只从某个副本获取一次，而不是每个用户获取一次。
- Nginx 会对每个响应都进行压缩（它的缓存保存的是未压缩的响应体），因此请使用适中的级别：`gzip_comp_level 4;` 或 brotli 质量 4 到 5，并加上 `gzip_min_length 1000;`。

### 将 JSON 编码器切换为 orjson {#switch-the-json-encoder-to-orjson}

在有多个实例时，每一次实时更新都会穿过 Redis 并以 JSON 编码和解码。[`ENABLE_ORJSON`](/reference/env-configuration#enable_orjson)（默认 `True`）会为这一环节以及应用其余部分使用快得多的 [orjson](https://pypi.org/project/orjson/) 库。请保持它开启。行为差异参见[使用更快的 JSON 编码器](/troubleshooting/multi-replica#use-the-faster-json-encoder)。

### 按房间划分的 Redis 频道 {#per-room-redis-channels}

当 `WEBSOCKET_MANAGER=redis` 时，发往特定用户、频道或笔记的实时更新会各自通过独立的 Redis 频道发出。每个实例只订阅与自身相连用户所属的房间，因此它会跳过面向其他实例的更新解码。确认消息和控制消息仍走共享频道。实例数量越多，节省越多。该功能默认开启：

```
WEBSOCKET_REDIS_ROOM_CHANNELS=True
```

:::warning 所有实例要一起更新

每个实例必须运行在相同模式下。滚动重启会让实例处于不同模式，实时更新随后会在它们之间丢失。请停止所有实例，在各处修改该设置，然后再启动。

:::

如果你的 Redis 用户受到 ACL 限制，它需要 `PUBLISH`、`SUBSCRIBE`、`UNSUBSCRIBE` 和 `PING` 命令，以及对 `&socketio` 和 `&socketio#*` 频道的访问权限。房间频道命名为 `socketio#<namespace>#<room>`。当缺少某项权限时，实时更新会失败，日志中会显示 `Redis denied publishing` 或 `Redis denied subscribing`，并给出需要检查的权限和频道。

`WEBSOCKET_REDIS_ROOM_CHANNELS=False` 会让所有内容都通过唯一的共享频道发送。参见 [`WEBSOCKET_REDIS_ROOM_CHANNELS`](/reference/env-configuration#websocket_redis_room_channels)。

### 加快名称查找 {#speed-up-name-lookups}

在高负载下，主机名查找会相互排队，导致各自所属的请求被延迟。c-ares 解析器可以消除这种排队：

```
AIOHTTP_CLIENT_ASYNC_DNS_RESOLVER=True
```

它是可选开启的，因为 c-ares 读取的名称来源比操作系统少。之后的测试项参见 [DNS 解析器](/troubleshooting/performance#dns-resolver)。

---

## 第 4 步——切换到外部向量数据库 {#step-4-switch-to-an-external-vector-database}
**何时需要：** 你运行不止一个副本。**这是必需的。**

:::danger 多进程设置下默认的 ChromaDB 会导致崩溃

默认的 ChromaDB 以嵌入方式运行在 Open WebUI 进程内部，并把数据存放在 `DATA_DIR/vector_db` 下的本地 SQLite 文件中。只有一个进程可以写入这些文件。当存在多个副本时，并发写入（例如在上传文档期间）会导致进程崩溃：

```
save_docs_to_vector_db:1619 - adding to collection file-id
INFO:     Waiting for child process [pid]
INFO:     Child process [pid] died
```

参见[文档上传期间 worker 崩溃](/troubleshooting/multi-replica#6-worker-crashes-during-document-upload-chromadb--multi-worker)。

:::

**需要做什么：**

把 [`VECTOR_DB`](/reference/env-configuration#vector_db) 设置为客户端/服务器模式的向量数据库：

```
VECTOR_DB=pgvector
```

**推荐的替代方案：**

| 向量数据库 | 最适合 | 配置 |
|---|---|---|
| **PGVector** | 已经在运行 PostgreSQL 的团队 | `VECTOR_DB=pgvector` + `PGVECTOR_DB_URL=postgresql://...`（默认为 `DATABASE_URL`） |
| **MariaDB Vector** | 运行 MariaDB 的团队 | `VECTOR_DB=mariadb-vector` + `MARIADB_VECTOR_DB_URL=mariadb+mariadbconnector://...` |
| **Milvus** | 查询吞吐很高的大型自托管部署 | `VECTOR_DB=milvus` + `MILVUS_URI=http://milvus-host:19530` |
| **Qdrant** | 需要高效过滤和元数据搜索的自托管部署 | `VECTOR_DB=qdrant` + `QDRANT_URI=http://qdrant-host:6333` |
| **Pinecone** | 完全托管的云服务 | `VECTOR_DB=pinecone` + `PINECONE_API_KEY=...` |
| **ChromaDB（HTTP 模式）** | 保留 ChromaDB，但作为独立服务器运行 | `VECTOR_DB=chroma` + `CHROMA_HTTP_HOST=chroma-host` + `CHROMA_HTTP_PORT=8000` |

:::note

核心团队维护 PGVector 和 ChromaDB，其他向量存储是社区贡献的集成。

:::

:::tip
**PGVector** 是最省事的选择，如果你已经在为主数据库运行 PostgreSQL：不需要额外基础设施。

**Milvus** 和 **Qdrant** 都有多租户模式，我们建议在使用它们时一律开启。不开启的话，每个文件、知识库、用户记忆和网页搜索都会拥有自己的集合，在稍大一些的实例上很快就会遇到扩展问题。开启后，所有数据共享少数几个集合。Qdrant 默认开启（[`ENABLE_QDRANT_MULTITENANCY_MODE`](/reference/env-configuration#enable_qdrant_multitenancy_mode)），Milvus 默认关闭（[`ENABLE_MILVUS_MULTITENANCY_MODE`](/reference/env-configuration#enable_milvus_multitenancy_mode)），因此 Milvus 需要手动开启。请在首次启动前决定；之后再切换需要重建索引。
:::

slim 镜像只支持 PGVector，也就是它默认的 `VECTOR_DB`。

---

## 第 5 步——在多个实例之间共享文件存储 {#step-5-share-file-storage-across-instances}

**何时需要：** 当你运行多个实例时。要让附件、知识库文档和生成的图片在各副本上正常使用，**所有副本都必须能访问同一批上传文件**。

默认情况下，Open WebUI 会把上传文件存到 `DATA_DIR`（通常是 `/app/backend/data`）下的本地文件系统。在多实例环境中，每个实例都必须能访问同一批文件。没有共享存储时，当请求打到不同副本上，你会看到[上传文件和 RAG 知识不可访问](/troubleshooting/multi-replica#5-uploaded-files-or-rag-knowledge-inaccessible)。

### 我一定需要云存储（S3）吗？ {#do-i-need-cloud-storage-s3}
**要求的是共享的文件访问能力，对象存储只是实现方式之一。** 你可以使用 S3、GCS 或 Azure Blob，也可以保持 `STORAGE_PROVIDER=local`，并在每个副本上以相同路径挂载同一个共享文件系统。

**你的可选方案：**

| 方案 | 何时使用 |
|---|---|
| **共享文件系统**（NFS、AWS EFS、CephFS，或单主机上的共享卷） | 你已经在运维共享存储。在所有实例上以相同路径挂载同一目录；多节点 Kubernetes 需要 ReadWriteMany（RWX）存储。 |
| **外部对象存储**（S3、GCS、Azure Blob） | 副本运行在不同主机上，或者文件需要在没有共享卷的情况下在容器替换后依然保留。请在每个副本上配置 `STORAGE_PROVIDER` 和同一个存储桶或容器。 |

:::info STORAGE_PROVIDER 究竟控制什么？
`STORAGE_PROVIDER` 覆盖的是通过 Open WebUI 文件上传 API 保存的文件：文档、附件和生成的图片。主数据库（`DATABASE_URL`）、向量数据库（`VECTOR_DB`）以及 `DATA_DIR` 的其余部分仍留在原处。直接从 `/cache/` 提供的文件（例如某些工具输出）使用文件系统，如果需要由其他副本提供，同样需要共享访问。
:::

### 方案 A：共享文件系统（最简单） {#option-a-shared-filesystem-simplest}
保持 `STORAGE_PROVIDER=local`，并在所有实例上以相同路径挂载同一目录：

**Kubernetes 示例：**
``` yaml
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: openwebui-data  # Must be ReadWriteMany (RWX)
```

**Docker Compose 示例：**
``` yaml
volumes:
  - /opt/data/openwebui-data:/app/backend/data
```

这种绑定挂载只在**同一主机**上的容器之间共享文件。在不同主机上，源目录本身必须位于共享存储上。不同主机上同名的 Docker 卷是彼此独立的卷。

:::warning
请把 SQLite 数据库放在网络文件系统之外。这也是在扩展之前切换到 PostgreSQL（[第 1 步](#step-1-switch-to-postgresql)）的原因之一。
:::

数据目录共享之后，请收紧其中可以落盘的内容：大小、数量和扩展名限制参见[文件上传限制](/getting-started/advanced-topics/hardening#file-upload-limits)，文件系统权限和备份参见[数据目录](/getting-started/advanced-topics/hardening#data-directory)。

### 方案 B：云对象存储 {#option-b-cloud-object-storage}
在**每个副本**上设置 `STORAGE_PROVIDER` 以及存储桶或容器和凭据。所有副本必须使用同一个目标位置，包括在设置了 `S3_KEY_PREFIX` 时使用相同的前缀，并拥有读、写和删除文件的权限。

**支持的提供方：**

| 提供方 | 将 `STORAGE_PROVIDER` 设为 |
|---|---|
| Amazon S3（或像 MinIO、R2 这样的 S3 兼容服务） | `s3` |
| Google Cloud Storage | `gcs` |
| Microsoft Azure Blob Storage | `azure` |

``` bash
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=my-openwebui-bucket
S3_REGION_NAME=us-east-1

# For an S3-compatible service, also set its endpoint:
# S3_ENDPOINT_URL=https://s3.example.com
# S3_ADDRESSING_STYLE=path
```

对于 S3，省略 `S3_ACCESS_KEY_ID` 和 `S3_SECRET_ACCESS_KEY` 即可使用默认的 AWS 凭据链（例如 IAM 角色），也可以通过你的密钥管理系统同时提供两者。GCS 使用 `GCS_BUCKET_NAME` 配合应用默认凭据或 `GOOGLE_APPLICATION_CREDENTIALS_JSON`。Azure 使用 `AZURE_STORAGE_ENDPOINT` 和 `AZURE_STORAGE_CONTAINER_NAME`，配合 `AZURE_STORAGE_KEY` 或默认的 Azure 凭据。slim 镜像只支持 `local` 和 `s3`。

所有提供方设置请参见[环境变量参考](/reference/env-configuration#cloud-storage)，完整示例请参见 [S3 存储教程](/tutorials/maintenance/s3-storage)。

:::warning 对象存储仍然需要本地磁盘
上传的文件会先写入 `DATA_DIR/uploads`，然后再发送到存储桶。读取时则先把文件下载到那里，Open WebUI 才会处理或提供它们。请为每个副本准备一个可写的数据目录，其空间和 I/O 能力足以应对并发传输。

`STORAGE_LOCAL_CACHE=false` 会在处理完成后移除云端文件的本地副本。但无论如何都要规划本地磁盘容量，因为下载和尚未处理的上传仍会占用它。
:::

### 切换已有部署 {#switching-an-existing-deployment}

更改 `STORAGE_PROVIDER` **不会**迁移已有文件，也不会改写它们存储时的路径。切换前请规划好已有对象及其文件记录的迁移方案；把文件复制进存储桶是不够的。请先备份数据库和文件。

在把生产流量发往多个副本之前，先通过一个副本上传文件，再通过另一个副本下载它。知识库文档和生成的图片也要一并检查，然后在替换上传副本后重复一次。

---

## 第 6 步——修复内容提取与 Embeddings 默认配置 {#step-6-fix-content-extraction--embeddings}
**何时需要：** 你在生产环境中经常处理文档（RAG、知识库）。

默认的内容提取器（pypdf）和默认的本地嵌入模型（SentenceTransformers）都运行在每个 Open WebUI 进程内部，因此它们的内存开销会在每个副本上重复出现，而提取器也是内存增长的一个常见来源。请把两者都迁移到外部服务。

**需要做什么：**

1. **把内容提取引擎**切换到外部服务：

```
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://tika:9998
```

若要把不同文件类型路由到不同后端，请运行你自己的服务并设置 `CONTENT_EXTRACTION_ENGINE=external`。参见[外部文档提取](/features/chat-conversations/rag/document-extraction/external)。

2. **把嵌入引擎**切换到外部提供方：

```
RAG_EMBEDDING_ENGINE=openai
# or for self-hosted:
RAG_EMBEDDING_ENGINE=ollama
```

**需要了解的关键点：**

- 详情和可选项参见[内容提取引擎](/troubleshooting/performance#content-extraction-engine)和[嵌入引擎](/troubleshooting/performance#embedding-engine)。
- slim 镜像不包含本地嵌入或重排模型，因此必须使用外部嵌入引擎。
- 外部的 Tika、Docling 或嵌入端点都是新增的外发目的地。请仅通过内部网络访问它们，并查阅加固指南中的[网络与外发请求](/getting-started/advanced-topics/hardening#network-and-outbound-requests)（`AIOHTTP_CLIENT_ALLOW_REDIRECTS=false`、`WEB_FETCH_FILTER_LIST`）。

---

## 第 7 步——加入可观测性 {#step-7-add-observability}
**何时需要：** 你想监控性能并排查大规模部署中的问题。

Open WebUI 通过 **OpenTelemetry** 向 Grafana、Datadog、New Relic 等平台导出链路追踪、指标和日志。打开总开关以及你需要的每种信号：

```
ENABLE_OTEL=true
ENABLE_OTEL_TRACES=true
ENABLE_OTEL_METRICS=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317
```

完整配置请参见 [OpenTelemetry 监控](/reference/monitoring/otel)。日志级别参见[记录 Open WebUI 日志](/getting-started/advanced-topics/logging)。结构化日志和审计日志参见加固指南中的[可观测性](/getting-started/advanced-topics/hardening#observability)和[审计日志](/getting-started/advanced-topics/hardening#audit-logging)。

---

## 组合起来是什么样子 {#putting-it-all-together}

一个可用于生产的扩展型部署通常会长这样：

``` mermaid
flowchart TD
    %% Main Flow
    LB["Load Balancer<br/>(Nginx, HAProxy, Cloud LB)"]

    subgraph Pods ["Stateless Containers"]
        direction LR
        P1["WebUI<br/>Pod 1"]
        P2["WebUI<br/>Pod 2"]
        PN["WebUI<br/>Pod N"]
    end

    subgraph Shared ["Shared Infrastructure"]
        direction LR
        DB[("PostgreSQL<br/>(+ PGVector for RAG)")]
        Redis{{"Redis"}}
        Storage[/"Shared Storage<br/>(NFS or S3)"/]
    end

    %% Annotations
    DBNote["Shared database<br/>+ Vector DB"]
    RedisNote["Shared state & websockets"]
    StoreNote["Shared file storage"]

    %% Connections
    LB --> P1
    LB --> P2
    LB --> PN
    P1 --> Shared
    P2 --> Shared
    PN --> Shared

    %% Alignment Links
    DB -.-> DBNote
    Redis -.-> RedisNote
    Storage -.-> StoreNote
```

**遇到问题？** 登录循环、WebSocket 故障、数据库锁和上传时崩溃等问题，请参见[扩缩容与高可用故障排查](/troubleshooting/multi-replica)。

### 扩展部署的最小环境变量集合 {#minimum-environment-variables-for-scaled-deployments}
``` bash
# Same value on every replica
WEBUI_SECRET_KEY=your-shared-secret

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/openwebui
DATABASE_POOL_SIZE=15
DATABASE_POOL_MAX_OVERFLOW=20

# Vector database (never the embedded ChromaDB with several replicas)
VECTOR_DB=pgvector
PGVECTOR_DB_URL=postgresql://user:password@db-host:5432/openwebui

# Redis
REDIS_URL=redis://redis-host:6379/0
WEBSOCKET_MANAGER=redis

# File storage: required across replicas, configure ONE option on all of them.
# Option A: STORAGE_PROVIDER=local with the same shared filesystem and mount path.
#           Separate per-host Docker volumes do not share files.
# Option B: external object storage (same bucket and key prefix on all replicas)
# STORAGE_PROVIDER=s3
# S3_BUCKET_NAME=my-openwebui-bucket
# S3_REGION_NAME=us-east-1
# Object storage still needs writable local disk; see Step 5.

# Content extraction and embeddings outside the app process
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://tika:9998
RAG_EMBEDDING_ENGINE=openai
# or: RAG_EMBEDDING_ENGINE=ollama

# Migrations: false on all but one instance; see Updates and Migrations
ENABLE_DB_MIGRATIONS=false

# Room for blocking work (DB calls, file I/O); the default limit is 40
THREAD_POOL_SIZE=2000

# Only if your load balancer, ingress or CDN compresses responses
# ENABLE_COMPRESSION_MIDDLEWARE=false

# Per-token WebSocket compression costs CPU for little gain
# UVICORN_WS_PER_MESSAGE_DEFLATE=false

# Fewer idle heartbeats; a dropped user lingers longer in the active count
# WEBSOCKET_HEARTBEAT_INTERVAL=60

# Grow streamed responses in place; helps long answers under concurrency
ENABLE_CHAT_RESPONSE_STREAM_INPLACE_APPEND=True

# Faster name lookups; verify your names still resolve after enabling
AIOHTTP_CLIENT_ASYNC_DNS_RESOLVER=True
```

:::warning 不要跳过 THREAD_POOL_SIZE
Open WebUI 把阻塞型工作（数据库调用、文件 I/O、同步处理函数）放在线程池中执行，默认最多并发 **40** 个操作。一旦有 40 个在执行中，后续请求就会排队，应用看起来像是卡住了，而 CPU 和内存看起来都很正常。`THREAD_POOL_SIZE` 可以提高这个上限。线程只在需要时才创建，因此取值较大是安全的。参见[线程池大小](/troubleshooting/performance#thread-pool-size)。
:::

### 大规模场景下需要重新审视的安全默认值 {#security-defaults-to-revisit-at-scale}
有些在单用户评估场景下合理的默认值，一旦真实用户通过 SSO 登录就变得更重要。完整讨论见[加固指南](/getting-started/advanced-topics/hardening)。最常被忽略的几项：

- **用 `ENABLE_PROFILE_IMAGE_URL_FORWARDING=false` 关闭外部头像重定向。** 默认情况下，头像端点会重定向到 `profile_image_url` 所持有的任意外部 URL，因此每个显示该头像的浏览器都会把自己的 IP、User-Agent 和 Referer 发送到那个来源。只有当你希望显示由 IdP 托管的头像（例如来自 `OAUTH_PICTURE_CLAIM` 的 Google 或 Gravatar URL）时才保留默认值；`data:` URI 头像无论如何都存放在本地。参见[SSO 配置](/features/authentication-access/auth/sso)。
- **把 `WEBUI_SECRET_KEY` 设置为每个副本上相同的值。** `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY` 默认取它的值；如果你单独设置了该变量，它也必须在所有地方保持一致。否则会话会跨副本失效，由某个 Pod 存储的 OAuth 令牌也无法被另一个 Pod 解密。
- **如果你的部署涉及敏感数据，请调低 `JWT_EXPIRES_IN`**（默认四周），尤其是在没有 Redis 做登出吊销的情况下。参见[令牌吊销](/getting-started/advanced-topics/hardening#token-revocation)。
- **设置 `ENABLE_OAUTH_ID_TOKEN_COOKIE=false`。** 默认情况下，原始的 IdP id_token 也会作为 Cookie 发送到浏览器。Open WebUI 会把 id_token 保存在服务端的 OAuth 会话中，并在登出时使用该副本。

除这份清单之外，加固指南还按主题逐一讨论了同样的问题：[网络放置](/getting-started/advanced-topics/hardening#network-placement)、[认证与注册](/getting-started/advanced-topics/hardening#authentication-and-signup)、[会话与 Cookie 安全](/getting-started/advanced-topics/hardening#session-and-cookie-security)、[安全响应头](/getting-started/advanced-topics/hardening#security-headers)、[访问控制](/getting-started/advanced-topics/hardening#access-control)、[工具、函数与管道](/getting-started/advanced-topics/hardening#tools-functions-and-pipelines)，以及[安全优先的部署](/getting-started/advanced-topics/hardening#security-first-deployment)检查表。

---

## 速查：什么场景需要哪些组件？ {#quick-reference-when-do-i-need-what}

<div className="responsive-table">

| 场景 | PostgreSQL | Redis | 外部向量数据库 | 外部内容提取 | 外部 Embeddings | 共享存储 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| 单用户 / 评估 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| 小团队（< 50 用户，单实例） | 可选 | 推荐† | ✗ | 推荐 | ✗ | ✗ |
| 多实例 / 高可用 | **必须** | **必须** | **必须** | **强烈推荐** | **强烈推荐** | **必须**（共享文件系统或对象存储） |
| 大规模（1000+ 用户） | **必须** | **必须** | **必须** | **强烈推荐** | **强烈推荐** | **跨副本必须** |

</div>

† 没有 Redis 时，登出**不会**撤销会话令牌：它会一直有效直到 `JWT_EXPIRES_IN` 到期（默认 4 周）。参见[令牌吊销](/getting-started/advanced-topics/hardening#token-revocation)。

:::note 关于“外部向量数据库”
客户端-服务端数据库（PGVector、Milvus、Qdrant、Pinecone 等），或作为独立 HTTP 服务运行的 ChromaDB。参见[第 4 步](#step-4-switch-to-an-external-vector-database)。
:::

:::note 关于“共享存储”
所有副本都必须通过**外部对象存储**（S3、GCS、Azure）或**共享文件系统**（NFS、EFS、CephFS，或同一主机上共享的卷）访问同一批上传文件。参见[第 5 步](#step-5-share-file-storage-across-instances)。
:::
