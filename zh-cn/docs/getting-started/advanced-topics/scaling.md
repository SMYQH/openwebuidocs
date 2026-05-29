---
sidebar_position: 2
title: "扩展 Open WebUI"
---

# 扩展 Open WebUI

Open WebUI 的设计允许你随着需求增长而扩展——从单用户一路扩展到覆盖大型企业和机构的全组织部署。下面的步骤会带你了解在需求不断扩大时，应该如何逐步调整部署方式。

Open WebUI 采用**无状态、容器优先架构**，因此它的扩展方式与大多数现代 Web 应用很相似。无论你是从个人兴趣项目升级到支撑一个部门，还是从数百用户扩展到数千用户，所需的基础构件基本是一致的。

本指南会从较高层面介绍关键概念和配置。具体环境变量说明请参见[环境变量参考](/reference/env-configuration)。

---

## 了解默认配置

开箱即用时，Open WebUI 以**单容器**形式运行，并具备：

- 存储在本地卷中的**内嵌 SQLite 主数据库**
- 用于 RAG 向量嵌入的**内嵌 ChromaDB 向量数据库**（同样由 SQLite 支撑）
- **单个 Uvicorn worker** 进程
- **无外部依赖**（没有 Redis、没有外部数据库）

这非常适合个人使用、小团队或评估场景。当你超出这些默认能力时，扩展之旅就开始了——尤其要注意的是，在安全运行多进程之前，**这两个 SQLite 数据库**（主库与向量库）都必须被替换。

---

## 第 1 步——切换到 PostgreSQL {#step-1--switch-to-postgresql}

**何时需要：** 你计划运行多个 Open WebUI 实例，或希望数据库具备更好的性能与可靠性。**如果你的 SQLite 文件不在本地直连 SSD/NVMe 上，也应该尽快切换**——见下方提示。

:::tip 如果你是单副本、数据库位于本地磁盘，这一步并非必需
**以下场景继续使用 SQLite 完全没问题：** 单副本部署、个人使用、评估、homelab、小团队——前提是数据库文件位于本地直连 SSD/NVMe 上，并且你没有运行多个副本或多个 worker。0.8 → 0.9 的异步后端问题，主要会在 `webui.db` 位于网络存储时暴露；在本地磁盘上，SQLite 依然快速、受支持，而且是合理的默认值。无需迁移。你可以跳过这一步，直接处理真正需要的后续步骤。
:::

SQLite 把所有内容存放在一个文件中，不擅长处理多个进程的并发写入。PostgreSQL 是面向生产的数据库，能够支持大量同时连接。

**需要做什么：**

将 `DATABASE_URL` 环境变量指向你的 PostgreSQL 服务器：

```
DATABASE_URL=postgresql://user:password@db-host:5432/openwebui
```

**关键点：**

- Open WebUI **不会**在数据库之间自动迁移数据——请在你的 SQLite 中积累生产数据之前就做好规划。
- 对高并发部署，请根据实际使用模式调整 `DATABASE_POOL_SIZE` 与 `DATABASE_POOL_MAX_OVERFLOW`。详细说明见 [数据库优化](/troubleshooting/performance#-database-optimization)。
- 请记住，**每个 Open WebUI 实例都有自己的连接池**，因此总连接数 = 连接池大小 × 实例数。
- 如果跳过这一步仍用 SQLite 运行多实例，你会遇到 `database is locked` 错误甚至数据损坏。详见 [数据库损坏 / “Locked” 错误](/troubleshooting/multi-replica#4-database-corruption--locked-errors)。

:::tip
一个不错的起点是 `DATABASE_POOL_SIZE=15` 与 `DATABASE_POOL_MAX_OVERFLOW=20`。每个实例的总连接数应明显低于 PostgreSQL 的 `max_connections`（默认 100）。
:::

关于凭据管理以及使用 SQLCipher 加密 SQLite 的方案，请参阅 [硬化指南中的数据库一节](/getting-started/advanced-topics/hardening#database)。

### 为什么一旦扩展（或升级），网络存储上的 SQLite 就会出问题

从 0.9.0 开始，后端数据层变成了**完全异步**（async SQLAlchemy + `aiosqlite`）。这一改动极大提升了并发能力，但副作用是：所有既有的“SQLite 在 NFS/CephFS/Azure Files 上很慢”问题，会从“还能忍”瞬间升级成“直接致命”。很多运维人员在从 0.8.x 升级后，明明没改部署，却立刻踩中了这个坑。

原理可以概括为：SQLite 的持久性保障依赖每次提交都执行 `fsync()`。在本地 SSD 上，这大约是 100 微秒；在 NFS / CephFS / Azure Files / 由网络存储支撑的 Kubernetes PVC 上，可能需要 50–500 毫秒，甚至更久。旧的同步后端里，FastAPI 大约 40 线程的 worker 池天然形成了节流，所以慢存储只会让应用“变慢”。而异步后端没有线程池上限——asyncio 事件循环会并发调度成千上万个数据库协程，每个慢速 `fsync` 都会占住连接整整一段时间，SQLAlchemy 的异步连接池（默认 `pool_size=5` + `max_overflow=10` = 15 个连接）很快就会被打满。随后你会看到：

```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached,
connection timed out, timeout 30.00
```

把连接池调大并不会真正解决问题，只是把崩溃点向后挪。更多连接意味着更多慢速 `fsync` 同时打到同一套慢存储上；瓶颈仍然在文件系统。

此外，SQLite 的 WAL 模式依赖内存映射的 `-shm` 文件来协调跨进程访问，而 SQLite 官方已经明确指出 [NFS 上的 `mmap` 并不可靠](https://www.sqlite.org/faq.html#q5)。在高并发异步场景下，这还可能导致真正的锁问题（死锁、`PRAGMA journal_mode=WAL` 启动后卡死、简单查询也要等数分钟）。

**只要 SQLite 仍放在网络存储上，就没有哪个配置可以彻底解决问题。** 你只有三个选择：

1. **最佳方案——切到 PostgreSQL（本步骤）。** 数据库服务器在自己的本地存储上管理 I/O。应用虽然通过网络访问它，但这种开销远远低于 NFS 上的 `fsync`，而 Postgres 从诞生起就是为并发写入设计的。这也是多副本、多用户、Kubernetes/Swarm 部署的唯一受支持配置。
2. **把 `webui.db` 从网络存储移到本地 SSD/NVMe。** 这只适合单节点、低用户量部署。你的 RAG 文件和上传文件依然可以放 NFS——问题针对的是 SQLite，不是共享文件系统本身。
3. **如果暂时做不到以上两点，可临时缓解：**
   ```bash
   DATABASE_POOL_SIZE=1
   DATABASE_SQLITE_PRAGMA_BUSY_TIMEOUT=30000
   ```
   这会把异步数据库访问串行化为单连接，用牺牲并发来换稳定。**不适合作为长期方案**——请尽快完成真正迁移。

简而言之：同步后端通过线程池限制了并发，因此慢存储只会让系统*变慢*；异步后端允许大规模并发，于是慢速 `fsync` 会堆积、连接长时间不归还、连接池迅速打满，整个系统卡死。以前能勉强承受，是因为应用根本不会同时发起 20 个 `fsync`。

---

## 第 2 步——加入 Redis

**何时需要：** 你想运行多个 Open WebUI 实例（横向扩展），或在单实例内运行多个 Uvicorn worker。

Redis 充当**共享状态存储**，让所有 Open WebUI 实例能够协调会话、WebSocket 连接和应用状态。没有它时，用户会因请求被不同实例处理而看到不一致行为。

**需要做什么：**

设置以下环境变量：

```
REDIS_URL=redis://redis-host:6379/0
WEBSOCKET_MANAGER=redis
ENABLE_WEBSOCKET_SUPPORT=true
```

**关键点：**

- 对单实例基础使用来说，Redis **不是必须的**。但要注意，**没有 Redis 时，登出并不会撤销 token**——它们会一直有效，直到过期（默认 4 周）。如果你的部署面向生产或涉及敏感数据，即使单实例也强烈建议启用 Redis；否则至少应缩短 `JWT_EXPIRES_IN` 来降低暴露时间。详见硬化指南中的 [Token 撤销](/getting-started/advanced-topics/hardening#token-revocation)。
- 如果你用的是 Redis Sentinel 做高可用，还应设置 `REDIS_SENTINEL_HOSTS`，并考虑设置 `REDIS_SOCKET_CONNECT_TIMEOUT=5`，避免故障切换时长时间挂起。
- 对 AWS ElastiCache 或其他托管 Redis Cluster 服务，请设置 `REDIS_CLUSTER=true`。
- 请确保 Redis 服务器的 `timeout 1800` 与足够高的 `maxclients`（10000+），以避免长期运行后连接耗尽。
- 高并发 WebSocket 流式场景下，请检查 Redis Pub/Sub 的输出缓冲区限制。较大的 Socket.IO 事件在 Redis 使用较小默认缓冲区时可能让 Pub/Sub 客户端断开；详见 [WebSocket Pub/Sub 缓冲区限制](/tutorials/integrations/redis#websocket-pubsub-buffer-limits)。
- 对绝大多数部署而言，**单个 Redis 实例**就足够了，即使用户数量达到数千。除非你有明确的高可用或带宽需求，否则几乎不需要 Redis Cluster。若你以为自己需要它，先确认连接数和内存占用问题是否只是配置不当（见 [常见反模式](/troubleshooting/performance#%EF%B8%8F-common-anti-patterns)）。
- 如果在多实例环境中没有 Redis，你会遇到 [WebSocket 403 错误](/troubleshooting/multi-replica#2-websocket-403-errors--connection-failures)、[配置不同步问题](/troubleshooting/multi-replica#3-model-not-found-or-configuration-mismatch) 和间歇性认证失败。

关于 Redis 的完整分步配置（Docker Compose、Sentinel、Cluster 模式、验证），请参考 [Redis WebSocket 支持](/tutorials/integrations/redis) 教程。反向代理后的 WebSocket 与 CORS 问题见 [连接错误](/troubleshooting/connection-error#-https-tls-cors--websocket-issues)。

---

## 第 3 步——运行多个实例

**何时需要：** 你需要处理更多用户，或者希望获得高可用（部署时无停机，或单个容器崩溃时不影响服务）。

Open WebUI 是无状态的，因此你可以在**负载均衡器**后按需运行任意数量的实例。每个实例都完全一致且可互换。

:::warning
在运行多实例前，请确保已完成**第 1 步和第 2 步**（PostgreSQL 与 Redis）。此外，所有副本还必须共享同一个 `WEBUI_SECRET_KEY`——否则用户会遇到[登录循环和 401 错误](/troubleshooting/multi-replica#1-login-loops--401-unauthorized-errors)。关于如何生成、存储和轮换该密钥（以及配套的 `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY`），请参阅硬化指南中的 [Secret Key](/getting-started/advanced-topics/hardening#secret-key)。完整上线前检查项见 [核心要求检查清单](/troubleshooting/multi-replica#core-requirements-checklist)。
:::

### 方案 A：容器编排（推荐）

使用 Kubernetes、Docker Swarm 等平台来管理多个副本：

- 每个容器保持 `UVICORN_WORKERS=1`（让编排器负责扩展，不要让应用自己扩展）
- 在除一个指定“主” pod 外的所有副本上设置 `ENABLE_DB_MIGRATIONS=false`，避免迁移竞争——安全流程见 [更新与迁移](/troubleshooting/multi-replica#updates-and-migrations)
- 通过调整副本数实现扩缩容

### 方案 B：单容器多 worker

如果部署更简单（例如单台高性能服务器），可以增大 `UVICORN_WORKERS`：

```
UVICORN_WORKERS=4
```

这会在单个容器内生成多个应用进程。但即便如此，你依然需要 PostgreSQL 和 Redis。

:::info
通常更推荐容器编排，因为它具备自动重启、滚动更新和更细粒度资源控制。单容器多 worker 则是在没有编排平台时更简单的替代方案。
:::

---

## 第 4 步——切换到外部向量数据库 {#step-4--switch-to-an-external-vector-database}

**何时需要：** 当你运行多个 Uvicorn worker（`UVICORN_WORKERS > 1`）或多个副本时。**这一步不是可选项。**

:::danger 默认 ChromaDB 会在多进程环境中崩溃

默认向量数据库（ChromaDB）使用基于 **SQLite** 的本地 `PersistentClient`。SQLite 连接**不具备 fork 安全性**——当 uvicorn fork 出多个 worker 后，每个进程都会继承同一数据库连接。并发写入（例如上传文档时）会导致 **worker 立刻死亡**：

```
save_docs_to_vector_db:1619 - adding to collection file-id
INFO:     Waiting for child process [pid]
INFO:     Child process [pid] died
```

这不是 bug，而是 [SQLite 众所周知的限制](https://www.sqlite.org/howtocorrupt.html#_carrying_an_open_database_connection_across_a_fork_)。在多副本部署中，如果多个容器访问同一个 ChromaDB 数据目录，也会触发同类问题。

关于完整崩溃链路分析，参见 [文档上传期间 worker 崩溃](/troubleshooting/multi-replica#6-worker-crashes-during-document-upload-chromadb--multi-worker) 或 [RAG → Worker 崩溃](/troubleshooting/rag#12-worker-dies-during-document-upload)。

:::

**需要做什么：**

把 `VECTOR_DB` 环境变量设置为一个客户端-服务端模式的向量数据库：

```
VECTOR_DB=pgvector
```

**推荐替代方案：**

| 向量数据库 | 最适合 | 配置 |
|---|---|---|
| **PGVector** | 已经在使用 PostgreSQL 的团队——复用现有数据库基础设施 | `VECTOR_DB=pgvector` + `PGVECTOR_DB_URL=postgresql://...` |
| **MariaDB Vector** | 基于 HNSW 的向量检索——在多连接负载下具备较强扩展性 | `VECTOR_DB=mariadb-vector` + `MARIADB_VECTOR_DB_URL=mariadb+mariadbconnector://...` |
| **Milvus** | 面向大规模自托管部署与高吞吐查询；支持多租户隔离 | `VECTOR_DB=milvus` + `MILVUS_URI=http://milvus-host:19530` |
| **Qdrant** | 适合需要高效过滤与元数据检索的自托管部署；支持多租户 | `VECTOR_DB=qdrant` + `QDRANT_URI=http://qdrant-host:6333` |
| **Pinecone** | 全托管云服务——无需自己维护基础设施，按用量付费 | `VECTOR_DB=pinecone` + `PINECONE_API_KEY=...` |
| **ChromaDB（HTTP 模式）** | 想继续用 ChromaDB，但通过独立服务进程保证多进程安全 | `VECTOR_DB=chroma` + `CHROMA_HTTP_HOST=chroma-host` + `CHROMA_HTTP_PORT=8000` |

:::note

只有 PGVector 和 ChromaDB 会由 Open WebUI 团队持续稳定维护。其他向量存储主要由社区贡献加入。

:::

:::tip
如果你已经在使用 PostgreSQL，**PGVector** 是最简单的选择——无需新增基础设施，就能在现有数据库上增加向量检索能力。

对于追求自托管环境中最大扩展性的场景，**Milvus** 与 **Qdrant** 都支持**多租户模式**（`ENABLE_MILVUS_MULTITENANCY_MODE=True` / `ENABLE_QDRANT_MULTITENANCY_MODE=True`），可在大规模环境中提供更好的资源共享能力。
:::

---

## 第 5 步——在多个实例之间共享文件存储 {#step-5--share-file-storage-across-instances}

**何时需要：** 当你运行多个实例，并且它们都需要访问上传文件、生成图片等用户数据时。

默认情况下，Open WebUI 会把上传文件存到 `DATA_DIR`（通常是 `/app/backend/data`）下的本地文件系统。在多实例环境中，每个实例都必须能访问同一批文件。没有共享存储时，当请求打到不同副本上，你会看到[上传文件和 RAG 知识不可访问](/troubleshooting/multi-replica#5-uploaded-files-or-rag-knowledge-inaccessible)。

### 我一定需要云存储（S3）吗？

**不一定。** Open WebUI 会用**基于 UUID 的唯一文件名**保存所有上传文件。多个进程和多个副本只会**创建新文件**或**读取已有文件**，不会同时写入同一文件。因此，在正常情况下，简单的**共享文件系统挂载**就能正确工作，不会发生写冲突。但你必须确保所有 worker / 副本都能访问同一个共享 `DATA_DIR` 目录。

**可选方案：**

| 方案 | 适用场景 |
|---|---|
| **共享文件系统**（NFS、AWS EFS、CephFS、GlusterFS 或共享 Docker 卷） | 大多数部署最简单的做法。把同一目录挂载到所有实例的 `/app/backend/data`。适用于本地部署、Docker Swarm，以及支持 ReadWriteMany（RWX）卷的 Kubernetes。 |
| **云对象存储**（S3、GCS、Azure Blob） | 更适合云原生、超大规模部署，或你希望获得托管级持久性（11 个 9）并避免自己维护共享文件系统。需要配置 `STORAGE_PROVIDER`。 |

:::info `STORAGE_PROVIDER` 实际控制什么？
`STORAGE_PROVIDER` 只控制**上传文件**（文档、图片等）存储在哪里。它**不会**影响主数据库（主数据库用 `DATABASE_URL`）或向量数据库（用 `VECTOR_DB`）。如果不设置，文件默认仍存放在 `DATA_DIR` 本地文件系统中。
:::

### 方案 A：共享文件系统（最简单）

无需修改配置——只要确保所有实例都挂载同一个目录即可：

**Kubernetes 示例：**
```yaml
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: openwebui-data  # 必须支持 ReadWriteMany (RWX)
```

**Docker Compose 示例：**
```yaml
volumes:
  - /opt/data/openwebui-data:/app/backend/data
```

:::warning
**不要**把 SQLite 数据库存放在网络文件系统上。SQLite 的文件锁在 NFS 上无法可靠工作。这也是为什么在扩展到多实例前，应先切换到 PostgreSQL（第 1 步）。
:::

### 方案 B：云对象存储

设置 `STORAGE_PROVIDER` 及对应凭证：

**支持的提供商：**

| 提供商 | `STORAGE_PROVIDER` 取值 |
|---|---|
| Amazon S3（或兼容 S3 的 MinIO、R2） | `s3` |
| Google Cloud Storage | `gcs` |
| Microsoft Azure Blob Storage | `azure` |

```
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=my-openwebui-bucket
S3_REGION_NAME=us-east-1
```

各提供商对应的凭证和 bucket 配置环境变量不同，详见[环境变量参考](/reference/env-configuration#cloud-storage)。

数据目录共享后，请进一步收紧能落到其中的内容：见 [文件上传限制](/getting-started/advanced-topics/hardening#file-upload-limits)（大小、数量、扩展名限额）和 [数据目录](/getting-started/advanced-topics/hardening#data-directory)（文件系统权限与备份指引）。

---

## 第 6 步——修复内容提取与 Embeddings 默认配置

**何时需要：** 你在生产环境中会持续处理文档（RAG、知识库等）时。

:::danger 这些默认值在规模化环境中会导致内存泄漏
默认内容提取引擎（pypdf）和默认 embedding 引擎（SentenceTransformers）是生产环境中 Open WebUI **最常见的两大内存泄漏来源**。修复它们的重要性不亚于切换 PostgreSQL 或加入 Redis。
:::

**需要做什么：**

1. **把内容提取引擎切换到外部服务：**

```
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://tika:9998
```

2. **把 embedding 引擎切换到外部提供商：**

```
RAG_EMBEDDING_ENGINE=openai
# 或自托管：
RAG_EMBEDDING_ENGINE=ollama
```

**关键点：**

- 默认内容提取器（pypdf）存在难以避免的**已知内存泄漏**，会导致 Open WebUI 进程内存持续增长。改用外部提取器（Tika、Docling）后，这些泄漏会被隔离在独立进程/容器中。
- 默认 SentenceTransformers embedding 模型每个 worker 会加载约 500MB 内存。8 个 worker 就是 4GB，仅 embeddings 就能吃掉不少资源。外部 embedding 服务可避免这一点。
- 详细说明与配置项请参考性能指南中的 [内容提取引擎](/troubleshooting/performance#content-extraction-engine) 和 [嵌入引擎](/troubleshooting/performance#embedding-engine)。
- 外部 Tika、Docling 或 embedding 端点会成为 Open WebUI 新的出站目标。仅通过内网与它们通信，并查阅硬化指南中的 [网络与出站请求](/getting-started/advanced-topics/hardening#network-and-outbound-requests) 一节，了解默认的 SSRF 防护（`AIOHTTP_CLIENT_ALLOW_REDIRECTS=false`、`WEB_FETCH_FILTER_LIST`），以确保错误配置的提取器 URL 不会被重定向到内部地址。

---

## 第 7 步——加入可观测性

**何时需要：** 你想监控性能、排查问题，并理解系统在规模化运行时的真实状态。

Open WebUI 支持通过 **OpenTelemetry** 导出 traces、metrics 和 logs 到你的观测平台（Grafana、Datadog、New Relic 等）：

```
ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317
```

这样你就能看到请求延迟、数据库查询性能、错误率等关键指标。

完整配置请参阅 [OpenTelemetry](/reference/monitoring/otel)。应用级日志配置（日志级别、调试输出）见 [Open WebUI 日志](/getting-started/advanced-topics/logging)。面向日志聚合器的结构化日志默认设置，以及记录认证事件、管理员动作和数据访问的专用审计日志，请见硬化指南中的 [Observability](/getting-started/advanced-topics/hardening#observability) 与 [Audit Logging](/getting-started/advanced-topics/hardening#audit-logging)。

---

## 组合起来是什么样子

一个可用于生产的扩展型部署通常会长这样：

```mermaid
flowchart TD
    %% Main Flow
    LB["Load Balancer<br/>(Nginx, HAProxy, Cloud LB)"]

    subgraph Pods ["无状态容器"]
        direction LR
        P1["WebUI<br/>Pod 1"]
        P2["WebUI<br/>Pod 2"]
        PN["WebUI<br/>Pod N"]
    end

    subgraph Shared ["共享基础设施"]
        direction LR
        DB[("PostgreSQL<br/>(+ PGVector for RAG)")]
        Redis{{"Redis"}}
        Storage[/"Shared Storage<br/>(NFS or S3)"/]
    end

    %% Annotations
    DBNote["共享主数据库<br/>+ 向量数据库"]
    RedisNote["共享状态与 WebSocket"]
    StoreNote["共享文件存储"]

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

**遇到问题？** [扩缩容与高可用](/troubleshooting/multi-replica) 覆盖了常见问题（登录循环、WebSocket 失败、数据库锁、worker 崩溃）及其解决方法。性能调优请参见 [优化、性能与内存占用](/troubleshooting/performance)。

### 扩展部署的最小环境变量集合

```bash
# 主数据库
DATABASE_URL=postgresql://user:password@db-host:5432/openwebui

# 向量数据库（多 worker/多副本时不要使用默认 ChromaDB）
VECTOR_DB=pgvector
PGVECTOR_DB_URL=postgresql://user:password@db-host:5432/openwebui

# Redis
REDIS_URL=redis://redis-host:6379/0
WEBSOCKET_MANAGER=redis
ENABLE_WEBSOCKET_SUPPORT=true

# 存储——二选一：
# 方案 A：共享文件系统（无需环境变量，只需挂载同一卷）
# 方案 B：云存储
# STORAGE_PROVIDER=s3
# S3_BUCKET_NAME=my-openwebui-bucket
# S3_REGION_NAME=us-east-1

# 内容提取（生产环境不要使用默认 pypdf）
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://tika:9998

# Embeddings（规模化环境不要使用默认 SentenceTransformers）
RAG_EMBEDDING_ENGINE=openai
# 或：RAG_EMBEDDING_ENGINE=ollama

# Workers（让编排器做扩展，worker 保持 1）
UVICORN_WORKERS=1

# 迁移（除一个实例外，其余实例设为 false）
ENABLE_DB_MIGRATIONS=false

# 并发与数据库写节流（规模化部署必备——见下方说明）
THREAD_POOL_SIZE=2000
DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL=300
```

:::warning 两个最常被遗忘、却会让扩展部署卡死的设置
- **`THREAD_POOL_SIZE=2000`** —— Open WebUI 会把阻塞型工作（数据库调用、文件 I/O、同步处理函数）丢给一个线程池，其默认的并发上限只有 **40**。在规模化部署中，一旦有 40 个阻塞操作同时进行，后续每个请求都会**排队**，整个应用看起来会陷入卡死，尽管 CPU/RAM 都很空闲。`2000` 对大型实例来说是*下限*；它只是并发上限，**不是** CPU/线程数，因此设大并不会造成争用。绝对不要调小它。（唯一的例外是硬件确实非常小的情况——这就不是“扩展部署”了。）
- **`DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL=300`** —— 在线状态追踪会把每位用户的 `last_active_at` 写入数据库。**未设置（即使用默认值）意味着该写入完全不限流——大致每次认证请求都会触发一次 `UPDATE` + `COMMIT`。** 在规模化部署中，这会形成持续的、细粒度的写入事务风暴，把连接池打满，却没有带来任何功能上的收益。推荐设为 `300`–`500` 秒；它在大规模/生产部署中是必须的，在其他场景中也能免费换取性能提升。

两者都仅在启动时读取一次，且无法在管理界面中配置。详见 [性能 → 数据库优化](/troubleshooting/performance#-database-optimization) 与 [性能 → 高并发](/troubleshooting/performance#-high-concurrency--network-optimization)。
:::

### 大规模场景下需要重新审视的安全默认值

有些默认配置在单用户评估场景下没有问题，但一旦把部署放到 SSO 之后并面向真实用户提供服务，就不再合适。完整讨论见 [硬化指南](/getting-started/advanced-topics/hardening)；在企业部署中最常被忽略的几项是：

- **禁用外部头像 URL 重定向** —— `ENABLE_PROFILE_IMAGE_URL_FORWARDING=false`。默认情况下，用户/模型头像端点会 `302` 跳转到 `profile_image_url` 中保存的任意外部 URL，这会让每一个查看头像的浏览器把自己的 IP、User-Agent 和 Referer 泄露给该源站。共享部署应将其设为 `false`，**除非**你的 IdP 仅以 `data:` URI 提供头像（Open WebUI 会将其本地化保存，不受影响），或你有意保留 IdP 托管的头像渲染——例如 `OAUTH_PICTURE_CLAIM` 返回 Google/Gravatar URL，且你希望它们直接显示。配套的 OAuth picture-claim 设置见 [SSO 配置](/features/authentication-access/auth/sso)。
- **`WEBUI_SECRET_KEY` 与 `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY` 在所有副本上保持同一个值**。否则，滚动重启时会话会断裂，一个 pod 写入的 OAuth 令牌也无法被另一个 pod 解密。
- **缩短 `JWT_EXPIRES_IN`**，不要继续使用 4 周的默认值——尤其是在处理敏感数据，且 Redis 还没就位（无法在登出时撤销令牌）的场景。详见 [Token 撤销](/getting-started/advanced-topics/hardening#token-revocation)。
- 一旦所有客户端都迁移到新的服务端会话模型，就**关闭 `ENABLE_OAUTH_ID_TOKEN_COOKIE`**（设为 `false`）。旧的 cookie 会把 IdP 原始的 id_token 透出到浏览器，新模型只保留在服务端。

这些都是配置默认值的调整，而不是新功能——只是当部署进入到多用户、且前面已经有一个真实身份提供商时，这些原有的开关就更重要了。

除了这份简短的清单外，硬化指南按主题对相同的关注点进行了分组，便于你逐项推进：[网络位置](/getting-started/advanced-topics/hardening#network-placement)、[认证与注册](/getting-started/advanced-topics/hardening#authentication-and-signup)、[会话与 Cookie 安全](/getting-started/advanced-topics/hardening#session-and-cookie-security)、[安全响应头](/getting-started/advanced-topics/hardening#security-headers)、[访问控制](/getting-started/advanced-topics/hardening#access-control)、[Tools、Functions 与 Pipelines](/getting-started/advanced-topics/hardening#tools-functions-and-pipelines)，以及结尾的 [安全优先部署](/getting-started/advanced-topics/hardening#security-first-deployment) 清单。

---

## 速查：什么场景需要哪些组件？

| 场景 | PostgreSQL | Redis | 外部向量数据库 | 外部内容提取 | 外部 Embeddings | 共享存储 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| 单用户 / 评估 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| 小团队（< 50 用户，单实例） | 推荐 | 推荐† | ✗ | 推荐 | ✗ | ✗ |
| 多 Uvicorn worker | **必须** | **必须** | **必须** | **强烈推荐** | **强烈推荐** | ✗（同一文件系统） |
| 多实例 / 高可用 | **必须** | **必须** | **必须** | **强烈推荐** | **强烈推荐** | **可选**（NFS 或 S3） |
| 大规模（1000+ 用户） | **必须** | **必须** | **必须** | **强烈推荐** | **强烈推荐** | **可选**（NFS 或 S3） |

† 没有 Redis 时，登出和密码变更**不会**撤销 token——它们会一直有效直到 `JWT_EXPIRES_IN` 到期（默认 4 周）。如果是处理敏感数据的生产环境，建议启用 Redis 以支持正确的 token 撤销。详见 [Token 撤销](/getting-started/advanced-topics/hardening#token-revocation)。

:::note 关于“外部向量数据库”
默认 ChromaDB 使用本地 SQLite 后端，在多进程访问下会崩溃。这里的“外部向量数据库”指的是客户端-服务端数据库（PGVector、Milvus、Qdrant、Pinecone），或作为独立 HTTP 服务运行的 ChromaDB。详情见 [第 4 步](#step-4--switch-to-an-external-vector-database)。
:::

:::note 关于“共享存储”
多实例场景下，所有副本都必须能访问相同的上传文件。**共享文件系统挂载**（本地磁盘、NFS、EFS、CephFS）已经足够——云对象存储（S3/GCS/Azure）是更易扩展的替代方案，但不是硬性要求。文件名基于 UUID，不会产生写冲突。详情见 [第 5 步](#step-5--share-file-storage-across-instances)。
:::
