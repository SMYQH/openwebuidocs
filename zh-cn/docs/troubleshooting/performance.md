---
sidebar_position: 15
title: "性能与内存"
---

# 优化、性能与内存占用

本指南系统梳理了优化 Open WebUI 的常见思路。最合适的配置高度取决于你的部署目标。你可以先判断自己更接近哪一种场景：

1. **弱硬件上的最大隐私（例如 Raspberry Pi）**
   - **目标**：全部本地运行，尽量降低资源占用
   - **代价**：需要使用轻量本地模型（如 SentenceTransformers），并关闭重型功能避免崩溃
2. **单用户最高质量（例如桌面环境）**
   - **目标**：在速度和质量之间取得最佳体验
   - **策略**：利用外部 API（OpenAI/Anthropic）承担 embeddings 和 task model 负载，把计算从本地机器移走
3. **多用户大规模部署（例如企业/生产）**
   - **目标**：稳定性与并发能力
   - **策略**：需要专用 Vector DB（Milvus/Qdrant）、更大的线程池、缓存，以及用 **PostgreSQL** 替代 SQLite

---

## ⚡ 性能调优（速度与响应）

当 Open WebUI 在聊天生成或高并发下显得缓慢、卡顿时，可以优先考虑这些优化点。

<span id="1-dedicated-task-models"></span>
### 1. 专用 Task Models {#1-dedicated-task-models}

默认情况下，Open WebUI 会为标题生成、标签生成、自动补全等后台任务调用模型。这些任务虽然在后台执行，但如果与你的主聊天模型共用同一资源，往往会拖慢主对话体验。

**建议：** 为这些任务使用**非常快、体积小、成本低的非推理模型**。不要把大型 reasoning 模型（如 o1、r1、Claude）用于这类简单后台任务——它们既慢又贵。

**配置方式：**
在 **管理面板 > 设置 > Interface** 中有两项独立设置，系统会根据你当前聊天模型类型自动选择：
- **任务模型（外部）**：当你在使用外部模型（例如 OpenAI）聊天时使用
- **任务模型（本地）**：当你在使用本地模型（例如 Ollama）聊天时使用

**推荐模型（2025）：**
- **外部/云端**：`gpt-5-nano`、`gemini-2.5-flash-lite`、`llama-3.1-8b-instant`
- **本地**：`qwen3:1b`、`gemma3:1b`、`llama3.2:3b`

### 2. 缓存与延迟优化

这些设置可以减少延迟和外部 API 请求量。

#### 模型缓存
大幅降低启动时间，并减少向外部提供商拉取模型列表的次数。

:::warning 对 OpenRouter 和多模型提供商尤其重要
如果你在使用 **OpenRouter** 或其他拥有数百/数千模型的提供商，**强烈建议**开启模型缓存。不启用缓存时，初次页面加载可能需要 **10-15+ 秒**；开启后通常接近瞬时完成。
:::

- **Admin Panel**：`Settings > Connections > Cache Base Model List`
- **Env Var**：`ENABLE_BASE_MODELS_CACHE=True`
  - 说明：在内存中缓存模型列表，只会在应用重启或你在 Connections 页面点击 **Save** 时刷新
- **Env Var**：`MODELS_CACHE_TTL=300`
  - 说明：为外部 API 响应设置 5 分钟缓存

#### 搜索查询缓存
在同一轮对话中，复用为 Web Search / RAG 生成的搜索查询，避免重复调用 LLM。

- **Env Var**：`ENABLE_QUERIES_CACHE=True`
- **管理面板**：`Settings > Connections > Cache Base Model List`
- **环境变量**：`ENABLE_BASE_MODELS_CACHE=True`

<span id="-database-optimization"></span>
## 📦 数据库优化 {#-database-optimization}

对大规模部署来说，数据库配置是稳定性的核心。

### PostgreSQL（大规模部署必需）
对任何多用户或高并发部署，**PostgreSQL 都是必需的**。SQLite（默认值）不是为高并发设计的，最终会成为瓶颈，并带来锁冲突。

- **Variable**：`DATABASE_URL`
- **Example**：`postgres://user:password@localhost:5432/webui`

### 聊天保存策略
默认情况下，Open WebUI 会在生成完成后保存聊天。虽然也支持实时逐 token 保存，但这会带来极高的数据库写入压力，**强烈不建议**开启。

- **Env Var**：`ENABLE_REALTIME_CHAT_SAVE=False`（默认）
- **效果**：只在生成完成后（或按周期）保存聊天
- **建议**：生产环境**不要启用** `ENABLE_REALTIME_CHAT_SAVE`。详情见 [Environment Variable Configuration](/reference/env-configuration#enable_realtime_chat_save)。

### 在线状态写入节流（每个部署都建议设置）

Open WebUI 通过向数据库写入每个用户的 `last_active_at` 时间戳来跟踪在线/“活跃”状态。**默认情况下，这个写入是无限流的**——基本上*每个已认证请求*都会触发自己的 `UPDATE users SET last_active_at = ...` 和一次 `COMMIT`。在繁忙的实例上，这意味着大量细小的写入事务持续涌入，放大数据库负载并消耗连接池容量，却没有带来任何功能性收益（在线状态只需要 ~分钟级的粒度）。

- **环境变量**：`DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL=300`
- **默认值**：未设置（**无限流——每个请求都写入**）
- **建议**：设置一个正整数秒数——`300`–`600` 都是不错的范围。它可以把数千次写入压缩到每个用户每个间隔最多一次。对任何环境都是**免费获得的性能提升**，对大型/生产环境**几乎可以说是必需的**；不设置是一个常见但完全可以避免的数据库瓶颈。在弱硬件上也**没有**副作用——它只会*减少*写入次数。详见 [`DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL`](/reference/env-configuration#database_user_active_status_update_interval)。

### 数据库会话共享
从 v0.7.1 开始，Open WebUI 提供数据库会话共享功能，在高并发下可减少频繁新建 session 的开销。

- **Env Var**：`DATABASE_ENABLE_SESSION_SHARING`
- **Default**：`False`

:::tip 按数据库类型给出的建议
- **SQLite：** 保持关闭（默认）。在 SQLite + 低配硬件上启用它，可能导致严重性能下降或超时。
- **PostgreSQL + 资源充足：** 可以考虑开启，尤其在多用户或高并发部署中通常会更好。
:::

:::warning 低配硬件提示
如果你在升级到 v0.7.0 后看到 Admin 页面加载变慢、API 超时或 UI 无响应，很可能就是因为启用了数据库会话共享。对 Raspberry Pi 或 CPU 配额很低的容器，请确保 `DATABASE_ENABLE_SESSION_SHARING=False`。
:::

### 连接池大小
对高并发 PostgreSQL 部署，默认连接池可能不够用。如果你看到 `QueuePool limit reached` 或连接超时，可考虑提高连接池：

- **Env Var**：`DATABASE_POOL_SIZE=15`
- **Env Var**：`DATABASE_POOL_MAX_OVERFLOW=20`

**重要：** 这两个值的总和应明显低于数据库的 `max_connections`。PostgreSQL 默认上限是 100，因此单个 Open WebUI 实例建议保持在 50-80 以下。

### 向量数据库（RAG）
在多用户场景中，Vector DB 的选择非常关键。

- **ChromaDB（默认）**：**不适合** 多 worker（`UVICORN_WORKERS > 1`）或多副本部署。默认 ChromaDB 使用本地 **SQLite** 支持的 `PersistentClient`，SQLite 不具备 fork-safe 特性；uvicorn fork 多 worker 后，并发写入会直接导致 worker 崩溃（`Child process died`）或数据库损坏。详见 [扩缩容与高可用指南](/troubleshooting/multi-replica#6-worker-crashes-during-document-upload-chromadb--multi-worker)。
- **推荐方案：**
  - **Milvus** 或 **Qdrant**：更适合大规模和高性能场景
  - **PGVector**：如果你已经使用 PostgreSQL，这是很好的选择
  - **ChromaDB HTTP mode**：若你仍想使用 ChromaDB，请将其作为[独立服务](/reference/env-configuration#chroma_http_host)运行，让 Open WebUI 通过 HTTP 访问
- **多租户：** 如果使用 Milvus 或 Qdrant，可考虑开启多租户：
  - `ENABLE_MILVUS_MULTITENANCY_MODE=True`
  - `ENABLE_QDRANT_MULTITENANCY_MODE=True`

<span id="content-extraction-engine"></span>
### 内容提取引擎 {#content-extraction-engine}

:::danger 默认内容提取器会造成内存泄漏
默认内容提取引擎依赖 Python 库（包括 **pypdf**），而这些库在文档导入过程中已知存在**持续性内存泄漏**。在生产环境中，如果经常上传文档，Open WebUI 的内存占用会不断增长，最终导致进程被杀死或容器重启。

这是生产环境中**最常见的无法解释的内存增长来源之一**。
:::

**建议：** 任何会频繁处理文档的部署，都应改用外部内容提取引擎：

| 引擎 | 适用场景 | 配置 |
|---|---|---|
| **Apache Tika** | 通用场景、成熟稳定、支持大多数文档类型 | `CONTENT_EXTRACTION_ENGINE=tika` + `TIKA_SERVER_URL=http://tika:9998` |
| **Docling** | 高质量提取、保留布局语义 | `CONTENT_EXTRACTION_ENGINE=docling` |
| **任意其他外部加载器** | 生产环境和自定义提取流水线首选 | `CONTENT_EXTRACTION_ENGINE=external` + `EXTERNAL_DOCUMENT_LOADER_URL=...` |

外部提取器会把高内存消耗的解析步骤移出 Open WebUI 进程，从根本上避开这类内存泄漏。

<span id="embedding-engine"></span>
### 嵌入引擎 {#embedding-engine}

:::warning 大规模场景下的 SentenceTransformers
默认的 **SentenceTransformers** 嵌入引擎（all-MiniLM-L6-v2）会把一个机器学习模型直接加载到 Open WebUI 进程内存中。对个人使用来说它足够轻量，但在大规模部署中会带来：

- **显著 RAM 占用**（每个 worker 大约 500MB+）
- **旧版本里会阻塞事件循环**
- **随 worker 数量线性放大**——每个 Uvicorn worker 都会各自加载一份模型

对多用户或生产环境，请把 embeddings 卸载到外部服务。
:::

- **推荐**：使用 `RAG_EMBEDDING_ENGINE=openai`（云端 embeddings）或 `RAG_EMBEDDING_ENGINE=ollama`（自托管 embeddings，如 `nomic-embed-text`）
- **Env Var**：`RAG_EMBEDDING_ENGINE=openai`
- **效果**：嵌入模型不会再驻留于 Open WebUI 进程内，每个 worker 能释放数百 MB 内存

### 优化文档切块

切块方式会直接影响存储效率与检索质量：

- **优先使用 Markdown Header Splitting**：这样能保留文档的语义结构
- **设置 Chunk Min Size Target**：使用 markdown header splitter 时，可能产生极小 chunk（例如只有一个小标题）
  - **Env Var**：`CHUNK_MIN_SIZE_TARGET=1000`
  - **收益**：自动把小 chunk 与邻近块合并，减少向量数量并改善 RAG 效果

---

## 📈 扩缩容基础设施（多租户与 Kubernetes）

如果你要支持**企业级规模**（数百用户），简单的 Docker Compose 往往不够，需要迁移到集群环境。

完整扩缩容路径（PostgreSQL、Redis、Vector DB、存储、可观测性）请参阅 **[Scaling Open WebUI](/getting-started/advanced-topics/scaling)**。

- **Kubernetes / Helm**：多副本部署请参阅 [扩缩容与高可用指南](/troubleshooting/multi-replica)
- **Redis（必需）**：当使用多个 worker 或多个副本时，**必须**使用 Redis 处理 WebSocket 与会话同步，详见 [Redis Integration](/tutorials/integrations/redis)
- **负载均衡**：建议 Ingress 支持 **Session Affinity（Sticky Sessions）**
- **反向代理缓存**：为静态资源（JS、CSS、图片）启用缓存，以降低应用服务器负载；参考 [Nginx Config](/reference/https/nginx) 与 [Caddy Config](/reference/https/caddy)
- **关闭代理缓冲（流式输出关键项）**：如果使用 Nginx，**必须**关闭 `proxy_buffering`，否则会导致 Markdown 乱码和流式变慢。详见 [Streaming Troubleshooting](/troubleshooting/connection-error#-garbled-markdown--streaming-response-corruption)

---

## ⚡ 高并发与网络优化

当同时在线用户较多时，下列设置很容易成为关键瓶颈。

#### 批量流式输出 token
默认情况下，Open WebUI 会把 LLM 返回的**每一个 token**都立即流式推送给前端。高频推流会增加服务器网络 IO 与 CPU 开销；若你还启用了实时聊天保存（不推荐），数据库压力会更大。

通过调大 chunk size，可以把这些更新打包后再发送给客户端。代价只是 UI 流式显示会稍微不那么“丝滑”，但对性能通常很有帮助。

- **Env Var**：`CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=7`
  - **建议**：高并发实例可设置为 **5-10**

#### 线程池大小
限制 AnyIO 工作线程池中**并发**阻塞操作（同步 DB 调用、文件 I/O、通过 `run_in_threadpool` 卸载的同步路由处理器）一次能同时运行的数量。这是一个**并发上限**，而不是一组固定预生成的 OS 线程，也**不是** CPU 核心/线程数——线程是按需懒加载并复用的，因此设置一个很大的值并**不会**凭空创建这么多线程、消耗 CPU，或在空闲时带来争用。它只决定了多少阻塞操作可以同时进行，超出的必须排队。

- **Default**：40（AnyIO 默认值——对生产环境来说远不够）
- **普通服务器/生产环境**：**2000+**。`2000` 对非常大的实例来说只是*下限*，调得更高也没问题，而且**不会**带来 CPU/争用风险（它是上限，而不是预分配）。
- **如果设得太低的症状**：当同时需要的阻塞操作数超过 `THREAD_POOL_SIZE`（许多用户同时操作，或少量用户各自触发多次阻塞调用）时，更多请求会**排队**等待空闲槽位。**整个应用看起来就像挂起/冻结/停止响应**，即使 CPU 和内存看起来都正常——这是线程池饥饿，不是资源耗尽。
- **警告**：**永远不要低于默认值。** 一个空闲的高上限几乎不消耗任何资源；低上限才会导致冻结。
- **例外——弱硬件**（Raspberry Pi、小型 VPS、CPU 配额约为 250m / 内存很低的容器）：不要在这里设置 `2000`。每个*真正并发*的阻塞操作仍会占用一个真正的 OS 线程（栈内存），所以在极小设备上，一个超大的上限会让一次流量突增耗尽内存。保持默认值，或按设备实际承受能力设置为几百的较小值。这个例外只适用于受限的单板/微型部署——任何正常服务器都应该用 `2000+`。

- **Env Var**：`THREAD_POOL_SIZE=2000`

详见 [`THREAD_POOL_SIZE`](/reference/env-configuration#thread_pool_size) 的完整说明。

#### AIOHTTP 客户端超时
较长的 LLM 输出可能超过默认超时时间，请按需调大：

- `AIOHTTP_CLIENT_TIMEOUT=1800`
- `AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST=15`
- `AIOHTTP_CLIENT_TIMEOUT_OPENAI_MODEL_LIST=15`

#### 容器资源限制
对 Docker 部署，请确保资源配额充足：

```yaml
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4.0'
    reservations:
      memory: 4G
      cpus: '2.0'

ulimits:
  nofile:
    soft: 65536
    hard: 65536
```

**诊断命令：**
```bash
docker stats openwebui --no-stream
docker exec openwebui netstat -an | grep -E "ESTABLISHED|TIME_WAIT|CLOSE_WAIT" | sort | uniq -c
docker exec openwebui ls -la /proc/1/fd | wc -l
```

---

<span id="️-cloud-infrastructure-latency"></span>
## ☁️ 云基础设施延迟 {#️-cloud-infrastructure-latency}

在云上 Kubernetes（AKS、EKS、GKE）部署 Open WebUI 时，即使资源配额与本地环境看起来一致，也经常会明显比本地 Kubernetes（Rancher Desktop、kind、Minikube）或裸金属部署更慢。绝大多数情况下，根因是**底层基础设施延迟**。

### 网络延迟（数据库与服务）

最常见的问题，是 **Open WebUI 与数据库之间的网络延迟**。

很多云部署会把数据库放在其他节点、可用区，甚至托管数据库服务上。这样的架构本身没问题，但它会给**每一条数据库查询**都增加延迟。Open WebUI 每个请求往往会触发多次数据库操作，因此即使单次查询只多出 10-20ms，在并发下也可能叠加成多秒延迟。

**症状：**
- 健康检查 endpoint 响应时间明显偏高，而不是接近瞬时
- 普通 API 或聊天请求在并发下明显变慢，即使 CPU / Memory 看起来并不高
- 本地测试正常，云上生产明显更慢

**诊断：**
- 从 pod 内部测试 Open WebUI 到数据库的延迟：
  ```bash
  psql -h <db-host> -U <user> -c "SELECT 1" -d <database>
  nc -zv <db-host> 5432
  ```
- **理想目标**：数据库查询延迟应尽量做到 **1-2ms 或更低**。如果网络延迟超过 **5ms**，对生产环境来说通常已经不理想，并很可能成为主要性能瓶颈。

**解决方法：**
1. **服务就近部署**：尽量让 Open WebUI 与 PostgreSQL 位于同一可用区，甚至同一节点池
2. **谨慎使用托管数据库**：云上的“一键式”托管数据库虽然省心，但通常比同节点自托管数据库引入更高网络延迟
3. **启用缓存**：使用 `ENABLE_BASE_MODELS_CACHE=True` 等缓存配置，减少数据库请求频率
4. **减少写入**：设置 `ENABLE_REALTIME_CHAT_SAVE=False`，降低写入压力和 IOPS 需求

<span id="disk-io-latency-sqlite--storage"></span>
### 磁盘 I/O 延迟（SQLite 与存储） {#disk-io-latency-sqlite--storage}

如果你在云环境中继续使用 **SQLite**（默认值），你可能只是把网络延迟换成了**磁盘延迟**。

云存储（Azure Disks、AWS EBS、GCP Persistent Disks）在很多情况下都比本地 NVMe/SSD 延迟更高、IOPS 更低，尤其是低等级存储类。

:::danger SQLite 跑在 NFS / SMB / Azure Files 上不受支持——这是 SQLite 自身的限制
这不是 Open WebUI 的限制，而是 **SQLite 上游项目**的明确说明。SQLite 官方 [明确指出](https://www.sqlite.org/faq.html#q5)，网络文件系统（NFS、SMB/CIFS 等）上的 SQLite 数据库**不受支持**：文件锁并不可靠，并发写入**可能损坏数据库**。

因此，对 Open WebUI 而言，SQLite 只适合：
- **直接连接的本地 SSD / NVMe** —— 只适合单用户或很小规模部署
- 任何不是本地高速盘的场景，都应改用 **PostgreSQL**
:::

#### 为什么异步后端会让网络存储上的 SQLite 问题突然变得严重

如果你从 0.8.x 升级到 0.9.x，部署本身没变，却突然开始出问题，核心原因通常是 `fsync()` 延迟在异步并发下被彻底放大。

| 存储 | 典型 `fsync` 延迟 |
| :--- | :--- |
| 本地 NVMe | ~100 μs |
| 本地 SATA SSD | 100 μs – 数 ms |
| 本地 HDD | ~10 ms |
| NFS / CephFS / Azure Files（SSD 后端） | 50–500 ms |
| 高延迟 NFS（或 HDD 后端） | 数百 ms 到数秒 |

**旧世界——同步 SQLAlchemy（0.8.x）：** FastAPI 大约 40 个线程的工作池天然形成限流，因此慢存储只会让应用“变慢”。

**新世界——异步 `aiosqlite`（0.9.x）：** asyncio 可以同时调度大量数据库协程。只要底层存储慢，连接就会长时间卡在 `fsync` 上，连接池很快被占满，随后所有请求开始排队并最终报：

```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached,
connection timed out, timeout 30.00
```

简单提高 `DATABASE_POOL_SIZE` 并不能解决问题；它只会让更多慢 `fsync` 并发堆积在同一块慢盘上。真正有效的方案只有两种：

1. **最佳方案：迁移到 PostgreSQL**
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/webui
   ```
   这是所有非严格单用户、本地磁盘部署的推荐方案，也是任何网络/远程/低 IOPS 存储场景的必需方案。
2. **可接受方案：把 `webui.db` 放到本地直连 SSD/NVMe**
   只适合单用户或很小规模部署。请把宿主机上的本地 SSD/NVMe 目录 bind mount 到 `/app/backend/data`。**不要** 用 NFS、SMB、Azure Files 或任何网络盘。
3. **仅限临时止损：降低并发**
   ```bash
   DATABASE_POOL_SIZE=1
   DATABASE_SQLITE_PRAGMA_BUSY_TIMEOUT=30000
   ```
   这会以吞吐量换取一点稳定性，但**不属于长期支持配置**。
4. **云块存储建议**
   若你必须在云上使用数据卷（无论给 PostgreSQL 还是应用本身），请选择 SSD-backed 的 **Block Storage** 类别，例如 `Premium_LRS`、`gp3`、`pd-ssd`。不要对数据库工作负载使用 File-based 存储类。

### 其他云端注意事项

| 因素 | 影响 | 缓解方式 |
|--------|--------|------------|
| **Burstable VMs**（如 Azure B-series、AWS T-series） | 持续负载下 CPU 被限速 | 使用标准或 compute-optimized 节点池 |
| **DNS 解析** | 每次外部请求都经过 CoreDNS，增加延迟 | 适当扩容 CoreDNS，必要时启用 node-local DNS cache |
| **Service Mesh Sidecars** | Istio/Linkerd 为每个请求增加代理延迟 | 检查 pod 中是否有意外 sidecar |
| **Network Policies** | CNI 处理增加额外开销 | 在可能情况下审计并简化策略 |
| **跨可用区流量** | 增加延迟与出网费用 | 尽量把服务固定在同一可用区 |

---

## 📉 资源效率（降低内存占用）

如果你部署在内存受限设备上（Raspberry Pi、小型 VPS），可以通过下面这些方式降低 OOM 风险。

### 1. 卸载辅助模型（仅本地部署相关）

Open WebUI 会为 RAG 和 STT 等功能加载本地模型。**这一节只对本地运行模型的场景有意义。**

#### RAG Embeddings
- **低配建议：**
  - **方案 A（最简单）**：保持默认 **SentenceTransformers**（all-MiniLM-L6-v2）。它运行在 CPU 上，通常比在同一台 Raspberry Pi 上再跑一个完整 Ollama 更省资源。
  - **方案 B（性能更好）**：改用**外部 API**（OpenAI/Cloud）。
- **配置位置：**
  - **Admin Panel**：`Settings > Documents > Embedding Model Engine`
  - **Env Var**：`RAG_EMBEDDING_ENGINE=openai`

#### Speech-to-Text（STT）
本地 Whisper 模型较重（约 500MB+ RAM）。

- **建议**：改用 **WebAPI**（浏览器端），让用户设备承担语音识别，服务器几乎零内存负担。
- **配置方式：**
  - **Admin Panel**：`Settings > Audio > STT Engine`
  - **Env Var**：`AUDIO_STT_ENGINE=webapi`

- **绕过音频预处理**：如果你使用的外部 STT 提供商（OpenAI、Deepgram、Azure、Mistral）本身就能接收原始音频并完成格式转换，可以设置 `BYPASS_PYDUB_PREPROCESSING=true`，跳过 Open WebUI 内部基于 pydub 的 MP3 转码、压缩与切块，减少 CPU 开销与 ffmpeg 依赖。

### 2. 关闭未使用功能

避免应用去加载你根本不用的**本地**模型。

- **图像生成**：`ENABLE_IMAGE_GENERATION=False`
- **Code Interpreter**：`ENABLE_CODE_INTERPRETER=False`

### 3. 关闭后台任务

如果资源非常紧张，可以关闭那些会持续触发模型推理的自动功能。

**建议关闭顺序（影响从高到低）：**
1. **Autocomplete**：`ENABLE_AUTOCOMPLETE_GENERATION=False`
2. **Follow-up Questions**：`ENABLE_FOLLOW_UP_GENERATION=False`
3. **Title Generation**：`ENABLE_TITLE_GENERATION=False`
4. **Tag Generation**：`ENABLE_TAGS_GENERATION=False`

### 4. SQLite 在受限容器中的内存占用 {#4-sqlite-在受限容器中的内存占用}

这个问题在**快速的本地 SSD/NVMe 上也会出现**。它属于 RAM 问题，而非存储延迟问题（关于网络存储的延迟/损坏问题，请参阅[磁盘 I/O 延迟](#disk-io-latency-sqlite--storage)）。在小型部署上，“编辑模型或知识库权限时容器被 OOM 杀死” 的最常见原因正是这个。

在 SQLite 下，当 `DATABASE_POOL_SIZE` 保持未设置时，当前版本（0.9.x，异步 DB 后端）**不会**回退到 SQLAlchemy 的小默认池，而是回退到一个很大的内部池（目前是 **512** 个连接）。每个被池化的连接各自独立地：

- 把自己的 **SQLite 页面缓存**懒增长到 `DATABASE_SQLITE_PRAGMA_CACHE_SIZE` 上限。默认值 `-65536` 大约是**每个连接 64 MB 已提交 RAM**。
- 内存映射数据库文件，上限为 `DATABASE_SQLITE_PRAGMA_MMAP_SIZE`，默认 **每个连接 256 MB**。这部分大多是虚拟内存、由文件后端承载，不会全部计入已提交匿名 RAM，但它会大幅抬高 `total-vm`，其中驻留部分仍会计入 cgroup 内存限制。
- 运行在它**自己的 OS 线程**上（异步 SQLite 驱动一个连接一个线程），额外消耗线程栈地址空间。

因此峰值内存随**同时活跃连接数**线性放大，而不是由单次查询的体量决定。一个会瞬时扇出大量短生命周期连接的工作流——例如编辑模型或知识库访问控制，然后再去重新加载长长的模型列表——就可能在短时间内让几十个连接同时在线。在一个很小的容器上，仅页面缓存（活跃连接数 × 每个最多 64 MB）就会超出限制，OOM killer 就会终止进程。用 profiler（py-spy、memray）观察时，几乎所有内存都来自 `aiosqlite/core.py`——因为每条连接恰好就在那个栈帧里分配自己的缓存并物化行。这正是 “很多连接” 的特征，而不是驱动内部的泄漏，也与远程向量数据库的体量无关。

:::tip 受限/低配容器（SQLite）
在任何内存限制较紧的部署（小 VPS、Raspberry Pi、1 到 2 GB 的 Docker `mem_limit`）上，请显式设置以下变量，而不要依赖默认值：

```bash
DATABASE_POOL_SIZE=8                       # 限制 SQLite 连接池（未设置时回退到 512）
DATABASE_SQLITE_PRAGMA_CACHE_SIZE=-2000    # 每个连接的页面缓存约 2 MB，而不是约 64 MB
DATABASE_SQLITE_PRAGMA_MMAP_SIZE=0         # 关闭每连接的 mmap 窗口
```

同时给容器留出合理的 headroom。**1 GB 非常低**，任何涉及 RAG 或 embeddings 的场景都不够用；目标应是 **2 GB 或更多**。在低配硬件上保持 `DATABASE_ENABLE_SESSION_SHARING=False`（默认）；在弱硬件上开启它是错误的杠杆，会让 SQLite 表现得更差（参见[数据库会话共享](#database-session-sharing)）。

对于多用户或持续增长的部署，可持续的解法是 **PostgreSQL**，而不是再去调 SQLite。
:::

---

## 🚀 推荐配置档案

### 档案 1：最大隐私（弱硬件 / RPi）
*目标：100% 本地，Raspberry Pi / 小于 4GB RAM。*

1. **Embeddings**：保持默认 SentenceTransformers
2. **Audio**：`AUDIO_STT_ENGINE=webapi`
3. **Task Model**：关闭或使用极小模型（如 `llama3.2:1b`）
4. **Scaling**：保留默认 `THREAD_POOL_SIZE`（40）
5. **关闭**：图像生成、Code Interpreter、Autocomplete、Follow-up
6. **数据库**：SQLite 即可，但限制其内存：`DATABASE_POOL_SIZE=8`、`DATABASE_SQLITE_PRAGMA_CACHE_SIZE=-2000`、`DATABASE_SQLITE_PRAGMA_MMAP_SIZE=0`。未设置时 SQLite 连接池的默认值较大（512），参见 [SQLite 在受限容器中的内存占用](#4-sqlite-在受限容器中的内存占用)

### 档案 2：单用户极客
*目标：最大质量与速度，本地 + 外部 API 混合。*

1. **Embeddings**：`RAG_EMBEDDING_ENGINE=openai`（或在快速服务器上用 `ollama` + `nomic-embed-text`）
2. **Task Model**：`gpt-5-nano` 或 `llama-3.1-8b-instant`
3. **缓存**：`MODELS_CACHE_TTL=300`
4. **数据库**：保持 `ENABLE_REALTIME_CHAT_SAVE=False`
5. **Vector DB**：PGVector（推荐）或 ChromaDB（仅小规模可接受）

### 档案 3：高规模 / 企业
*目标：大量并发用户，稳定性优先。*

1. **数据库**：**PostgreSQL**（必需）
2. **内容提取**：**Tika**、**Docling**、**或任何其他外部文档加载器**（必需）
3. **Embeddings**：**外部服务**——`RAG_EMBEDDING_ENGINE=openai` 或 `ollama`（必需）
4. **Tool Calling**：**Native Mode**（必需）
5. **Workers**：`THREAD_POOL_SIZE=2000`
6. **Streaming**：`CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=7`
7. **Chat Saving**：`ENABLE_REALTIME_CHAT_SAVE=False`
8. **Vector DB**：**Milvus**、**Qdrant** 或 **PGVector**；不要使用 ChromaDB 默认本地模式
9. **Task Model**：外部/托管模型
10. **Caching**：`ENABLE_BASE_MODELS_CACHE=True`、`MODELS_CACHE_TTL=300`、`ENABLE_QUERIES_CACHE=True`
11. **Redis**：单实例即可，但要配置 `timeout 1800` 和较高的 `maxclients`

#### Redis 调优

绝大多数部署（包括成千上万用户）都只需要一个单实例 Redis。除非你有明确高可用需求，否则**几乎不需要** Redis Cluster 或 Redis Sentinel。

常见 Redis 配置问题：

| 问题 | 症状 | 修复方式 |
|---|---|---|
| **陈旧连接** | Redis 连接耗尽，或内存一直增长 | 在 redis.conf 中设置 `timeout 1800` |
| **maxclients 太低** | 出现 `max number of clients reached` | 设置 `maxclients 10000` 或更高 |
| **没有连接限制** | Open WebUI pod 累积越来越多连接 | 同时配置 `timeout` 与 Redis 客户端连接池限制 |
| **Pub/Sub 输出缓冲区上限过低** | WebSocket 流停滞、`Cannot publish to redis... giving up`，或大尺寸 Socket.IO 事件发布时 Redis 日志中记录客户端输出缓冲区断开 | 调高 Redis 的 `client-output-buffer-limit ... pubsub ...` 设置，按你的 websocket 负载大小和可用 Redis 内存调整 |

对于基于 Redis 的 WebSocket，Open WebUI 使用 Socket.IO 走 Redis Pub/Sub。大型流式响应和工具事件可能产生数 MB 的 `PUBLISH socketio ...` 负载。如果 Redis 因此断开了慢速 Pub/Sub 客户端，可以检查：

```bash
redis-cli INFO stats | grep client_output_buffer_limit_disconnections
redis-cli SLOWLOG GET 50
redis-cli CONFIG GET client-output-buffer-limit
```

适合需要承受大型 WebSocket 突增的部署的 Redis 配置示例：

```conf
client-output-buffer-limit normal 0 0 0 replica 268435456 67108864 60 pubsub 1073741824 268435456 180
```

这一行将普通客户端的限制保持关闭，并把 Pub/Sub 客户端的上限提高到 1 GB 硬限、256 MB 软限，持续 180 秒。根据 Redis 内存余量和实际负载大小调高或调低。

---

<span id="️-common-anti-patterns"></span>
## ⚠️ 常见反模式 {#️-common-anti-patterns}

下面这些真实世界中的错误，经常会让组织为了掩盖根因而过度扩容基础设施：

| 反模式 | 会发生什么 | 正确做法 |
|---|---|---|
| **生产环境继续使用默认内容提取器** | pypdf 内存泄漏 → 容器频繁重启 → 被迫加更多副本 | 改用 Tika 或 Docling（`CONTENT_EXTRACTION_ENGINE=tika`） |
| **大规模部署仍使用 SentenceTransformers** | 每个 worker 各自加载 ~500MB 模型 → RAM 爆炸 → 被迫加更多机器 | 改用外部 embeddings（`RAG_EMBEDDING_ENGINE=openai` 或 `ollama`） |
| **单实例 Redis 就够，却上 Redis Cluster** | 副本太多 → 连接太多 → Redis 扛不住 → 被迫上集群 | 先修根因（减少副本、设置 `timeout 1800`、`maxclients 10000`） |
| **靠加副本掩盖内存泄漏** | 泄漏进程 → OOM → 自动扩容 → Redis 连接更多 → Redis 被打爆 | 先修泄漏（内容提取、嵌入引擎），再做容量规划 |
| **继续用 Default（prompt-based）tool calling** | 已过时 / 不再支持；注入式 prompt 会破坏 KV cache → 延迟更高 → 资源需求更大 | 把所有模型切到 Native Mode |
| **没有为 Redis 配置空闲连接超时** | 连接永远不回收 → Redis OOM → 被迫上 Redis Cluster | 在 redis.conf 中加入 `timeout 1800` |
| **在 Actions/Filters 中使用 base64 图标** | 图标数据会嵌入到 `/api/models` 响应中，前端每次为每个模型都加载一遍。20 个模型 × 3 个 Action × 500KB base64 图标 = 每次请求多 **30 MB 负载** → 前端加载慢、带宽浪费、后端内存压力 | 把图标作为静态文件托管，并用 `icon_url` / `self.icon` 引用。参见 [Action Function icon_url 警告](/features/extensibility/plugin/functions/action#example---specifying-action-frontmatter) |
| **在小容器上使用默认 SQLite 连接池** | 未设置 `DATABASE_POOL_SIZE` 会回退到 512 连接池；每个连接自带约 64 MB 页面缓存和一个 256 MB mmap 窗口，因此一个会扇出大量连接的工作流（编辑模型/知识库权限、重新加载长长的模型列表）会让 1 GB 容器 OOM-kill | 限制 `DATABASE_POOL_SIZE`（例如 `8`），设置 `DATABASE_SQLITE_PRAGMA_CACHE_SIZE=-2000` 和 `DATABASE_SQLITE_PRAGMA_MMAP_SIZE=0`，给容器 **≥2 GB** 内存。参见 [SQLite 内存占用](#4-sqlite-在受限容器中的内存占用) |

---

## 🔗 环境变量参考

所有可用变量的完整说明，请参阅 [Environment Configuration](/reference/env-configuration)。

| Variable | 说明与链接 |
| :--- | :--- |
| `TASK_MODEL` | [Task Model (Local)](/reference/env-configuration#task_model) |
| `TASK_MODEL_EXTERNAL` | [Task Model (External)](/reference/env-configuration#task_model_external) |
| `ENABLE_BASE_MODELS_CACHE` | [Cache Model List](/reference/env-configuration#enable_base_models_cache) |
| `MODELS_CACHE_TTL` | [Model Cache TTL](/reference/env-configuration#models_cache_ttl) |
| `ENABLE_QUERIES_CACHE` | [Queries Cache](/reference/env-configuration#enable_queries_cache) |
| `DATABASE_URL` | [Database URL](/reference/env-configuration#database_url) |
| `ENABLE_REALTIME_CHAT_SAVE` | [Realtime Chat Save](/reference/env-configuration#enable_realtime_chat_save) |
| `CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE` | [Streaming Chunk Size](/reference/env-configuration#chat_response_stream_delta_chunk_size) |
| `THREAD_POOL_SIZE` | [Thread Pool Size](/reference/env-configuration#thread_pool_size) |
| `RAG_EMBEDDING_ENGINE` | [Embedding Engine](/reference/env-configuration#rag_embedding_engine) |
| `CONTENT_EXTRACTION_ENGINE` | [Content Extraction Engine](/reference/env-configuration#content_extraction_engine) |
| `AUDIO_STT_ENGINE` | [STT Engine](/reference/env-configuration#audio_stt_engine) |
| `BYPASS_PYDUB_PREPROCESSING` | [Bypass pydub audio preprocessing](/reference/env-configuration#bypass_pydub_preprocessing) |
| `ENABLE_IMAGE_GENERATION` | [Image Generation](/reference/env-configuration#enable_image_generation) |
| `ENABLE_AUTOCOMPLETE_GENERATION` | [Autocomplete](/reference/env-configuration#enable_autocomplete_generation) || `DATABASE_ENABLE_SESSION_SHARING` | [Database Session Sharing](/reference/env-configuration#database_enable_session_sharing) |
| `DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL` | [Presence Write Throttling](/reference/env-configuration#database_user_active_status_update_interval) |
| `DATABASE_POOL_SIZE` | [Connection Pool Size](/reference/env-configuration#database_pool_size) |
| `DATABASE_SQLITE_PRAGMA_CACHE_SIZE` | [SQLite Page Cache Size](/reference/env-configuration#database_sqlite_pragma_cache_size) |
| `DATABASE_SQLITE_PRAGMA_MMAP_SIZE` | [SQLite mmap Size](/reference/env-configuration#database_sqlite_pragma_mmap_size) |
