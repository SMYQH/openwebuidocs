---
sidebar_position: 15
title: "性能与内存"
---

# 优化、性能与内存占用 {#optimization-performance--ram-usage}

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

## ⚡ 性能调优（速度与响应） {#performance-tuning-speed--responsiveness}

当 Open WebUI 在聊天生成或高并发下显得缓慢、卡顿时，可以优先考虑这些优化点。

### 1. 专用 Task Models {#1-dedicated-task-models}

默认情况下，Open WebUI 会为标题生成、标签生成、自动补全等后台任务调用模型。这些任务虽然在后台执行，但如果与你的主聊天模型共用同一资源，往往会拖慢主对话体验。

![设置 > 界面（管理员区域）中的任务模型设置](/images/admin/admin-interface.png)

**建议：** 为这些任务使用**非常快、体积小、成本低的非推理模型**。不要把大型 reasoning 模型用于这类简单后台任务——它们既慢又贵。在给出三个词的聊天标题之前，此类模型会先花上数秒进行思考，并为此收取思考 token 的费用。主流供应商都提供更适合此场景的小型档位，远胜于其旗舰模型。

**合适的选项：**
*   **外部/云端**：`gpt-5.6-luna`、`gemini-3.5-flash-lite`、`claude-haiku-4-5-20251001`（直接使用 OpenAI、Google 和 Anthropic，或通过 OpenRouter 使用相同的模型）。
*   **本地**：`qwen3.5:2b`、`gemma4:e2b`、`llama3.2:3b`。

**配置方式：** 两个模型选择器、这些后台请求所带的参数，以及逐项关闭单个任务的开关，都在 **设置 > Interface**（管理员区域）中。详细说明参见[任务模型](/features/administration/task-models)。

### 2. 缓存与延迟优化 {#2-caching--latency-optimization}

这些设置可以减少延迟和外部 API 请求量。

#### 模型缓存 {#model-caching}
大幅降低启动时间，并减少向外部提供商拉取模型列表的次数。

:::warning 对 OpenRouter 和多模型提供商尤其重要
如果你在使用 **OpenRouter** 或其他拥有数百/数千模型的提供商，**强烈建议**开启模型缓存。不启用缓存时，初次页面加载可能需要 **10-15+ 秒**；开启后通常接近瞬时完成。
:::

- **Admin Panel**：`Settings > Connections > Cache Base Model List`（管理员区域）
- **Env Var**：`ENABLE_BASE_MODELS_CACHE=True`
  - 说明：缓存基础模型列表；配置了 Redis 时缓存在 Redis 中（所有副本共享），否则缓存在每个副本自己的内存里。在 Connections 设置中点击 **Save**、或使用开关旁边的刷新按钮时会刷新；没有 Redis 时重启也会刷新。
- **Env Var**：`MODELS_CACHE_TTL=300`
  - 说明：缓存每个 OpenAI 和 Ollama 连接的模型列表响应 5 分钟。默认值为 `1` 秒。

#### 搜索查询缓存 {#search-query-caching}
在同一轮对话中，复用为 Web Search / RAG 生成的搜索查询，避免重复调用 LLM。

- **Env Var**：`ENABLE_QUERIES_CACHE=True`
  - 说明：启用后，RAG 会复用同一个搜索查询，而不是为 RAG 重新生成查询，从而节省推理成本与 API 调用，进而提升性能。

## 📦 数据库优化 {#database-optimization}

对大规模部署来说，数据库配置是稳定性的核心。

### PostgreSQL（大规模部署必需） {#postgresql-mandatory-for-scale}
对任何多用户或高并发部署，**PostgreSQL 都是必需的**。SQLite（默认值）不是为高并发设计的，最终会成为瓶颈，并带来锁冲突。

- **Variable**：`DATABASE_URL`
- **Example**：`postgres://user:password@localhost:5432/webui`

### 在线状态写入节流（每个部署都建议设置） {#user-active-status-write-throttling-set-this-on-every-deployment}

Open WebUI 通过向数据库写入每个用户的 `last_active_at` 时间戳来跟踪在线/“活跃”状态。**不加节流时，基本上每个已认证请求都会各自发起一次 `UPDATE` 和一次 `COMMIT`**——大量细小的写入事务会压垮数据库和连接池，却毫无收益，因为在线状态只需要大约分钟级的粒度。

- **环境变量**：`DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL`
- **默认值**：`60` 秒
- **建议**：`120`，这会让在线状态写入再减少一半。请保持低于 `180`：在线状态的判定依据是用户时间戳是否落在最近 180 秒内，因此间隔过长会让活跃用户数出现波动。设为 `0` 表示不进行节流。详见 [`DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL`](/reference/env-configuration#database_user_active_status_update_interval)。

### 数据库会话共享 {#database-session-sharing}
会话共享允许数据库调用复用请求已持有的会话，而非打开一个新的会话。

- **Env Var**：`DATABASE_ENABLE_SESSION_SHARING`
- **Default**：`False`

:::tip 按数据库类型给出的建议

- **SQLite 与低配硬件**（Raspberry Pi、CPU 配额约 250m 的容器）：保持**关闭**（默认）。在这类系统上启用它会导致 Admin 页面变慢、API 超时和界面无响应。
- **资源充足的 PostgreSQL：** 在多用户或高并发部署中，可以考虑**开启**。

:::

### 连接池大小 {#connection-pool-sizing}

对高并发 PostgreSQL 部署，默认连接池可能不够用。如果未设置 `DATABASE_POOL_SIZE`，PostgreSQL 会使用 SQLAlchemy 的默认值，即 5 个连接加 10 个溢出连接。如果你看到 `QueuePool limit reached` 错误或连接超时，可以调高：

- **Env Var**：`DATABASE_POOL_SIZE=15`
- **Env Var**：`DATABASE_POOL_MAX_OVERFLOW=20`（在 `DATABASE_POOL_SIZE` 设置后生效；默认 `0`）
- **Env Var**：`DATABASE_POOL_TIMEOUT`（请求在失败前等待可用连接的秒数；默认 `30`）

SQLite 使用自己的连接池配置，参见[受限容器中的 SQLite 内存占用](#5-sqlite-memory-footprint-on-constrained-containers)。

**重要：** 这两个值的总和（`DATABASE_POOL_SIZE` + `DATABASE_POOL_MAX_OVERFLOW`）应明显低于数据库的 `max_connections` 上限。PostgreSQL 默认上限是 100 个连接，因此单个 Open WebUI 实例建议保持在 50-80 以下，为其他客户端和维护操作留出余量。

### 向量数据库（RAG） {#vector-database-rag}

对于多用户部署，向量数据库的选择很重要。

知识库搜索不会占住发起它的那个 worker，因此在搜索进行期间，其他人的回复仍会继续流式返回，而且多个集合会被同时搜索，而不是一个接一个。因此一个慢的向量数据库只会拖慢正在搜索的那次对话，而不是该 worker 上的每个用户。它仍然要承受多个副本同时访问的压力，下面的选项正是在这方面做取舍。

- **ChromaDB（默认）**：**不适合**多副本部署。默认 ChromaDB 把数据保存在本地 SQLite 文件中，而同一时间只能有一个进程写入；多个副本同时写入会直接把它们搞坏。完整的崩溃过程与解决方案请见[扩缩容与高可用故障排查指南](/troubleshooting/multi-replica#6-worker-crashes-during-document-upload-chromadb--multi-worker)。
- **推荐方案：**
  - **Milvus** 或 **Qdrant**：以服务器方式运行时，在规模与性能上表现最好。服务器部署对多副本访问是安全的，因为每个副本都通过网络与它通信。
  - **Milvus Lite**：适用于知识库规模较小且基本不再增长的小型单实例部署，此时它比本地 ChromaDB 占用更少的磁盘和内存。如果你要批量上传文档或持续添加文件，则不要使用它：Open WebUI 在每次上传前都会检查文件内容哈希，而 Milvus Lite 不为元数据建立索引，每次都要扫描整个集合，因此你存得越多，导入就越慢。相关实测数据参见[把 ChromaDB 换成 Milvus Lite](#4-swap-chromadb-for-milvus-lite-small-deployments)。规模再大一些就该用 Milvus 服务器；Milvus Lite 是嵌入式数据库，因此它与本地 ChromaDB 一样受多进程写入限制。增加副本前，请把 `MILVUS_URI` 指向 Milvus 服务器。
  - **PGVector**：如果你已经在使用 PostgreSQL，这是很好的选择，同样完全支持多进程访问。
  - **ChromaDB HTTP mode**：若你仍想使用 ChromaDB，请将其作为[独立服务](/reference/env-configuration#chroma_http_host)运行，让 Open WebUI 通过 HTTP 而不是本地 SQLite 连接它。
- **多租户：** 只要使用 Milvus 或 Qdrant 就建议开启；不开启的话，实例规模一大很快就会遇到扩缩容问题。参见[扩缩容指南的第 4 步](/getting-started/advanced-topics/scaling#step-4-switch-to-an-external-vector-database)。
  - `ENABLE_MILVUS_MULTITENANCY_MODE=True`（默认 `False`）
  - `ENABLE_QDRANT_MULTITENANCY_MODE=True`（默认开启）

### 内容提取引擎 {#content-extraction-engine}
:::danger 默认内容提取器会造成内存泄漏
默认内容提取引擎依赖 Python 库（包括 **pypdf**），而这些库在文档导入过程中已知存在**持续性内存泄漏**。在生产环境中，如果经常上传文档，Open WebUI 的内存占用会不断增长，最终导致进程被杀死或容器重启。

这是生产环境中**最常见的无法解释的内存增长来源之一**。
:::

**建议：** 任何会频繁处理文档的部署，都应改用外部内容提取引擎：

| 引擎 | 适用场景 | 配置 |
|---|---|---|
| **Apache Tika** | 通用场景、成熟稳定、支持大多数文档类型 | `CONTENT_EXTRACTION_ENGINE=tika` + `TIKA_SERVER_URL=http://tika:9998` |
| **Docling** | 高质量提取、保留布局语义 | `CONTENT_EXTRACTION_ENGINE=docling` + `DOCLING_SERVER_URL=http://docling:5001` |
| **PaddleOCR-vl** | 以 OCR 为主的工作负载（扫描版 PDF、图片、混合版式）；自托管的视觉-语言 OCR | `CONTENT_EXTRACTION_ENGINE=paddleocr_vl` + `PADDLEOCR_VL_BASE_URL=http://paddleocr-vl:8080` + `PADDLEOCR_VL_TOKEN=...` |
| **任意其他外部加载器** | 生产环境和自定义提取流水线首选 | `CONTENT_EXTRACTION_ENGINE=external` + `EXTERNAL_DOCUMENT_LOADER_URL=...` |

外部提取器会把高内存消耗的解析步骤移出 Open WebUI 进程，从根本上避开这类内存泄漏。


### 嵌入引擎 {#embedding-engine}

:::warning 大规模场景下的 SentenceTransformers
默认的 **SentenceTransformers** 嵌入引擎（all-MiniLM-L6-v2）会在启动时把 PyTorch 和模型一并加载进 Open WebUI 进程，每个副本都会加载自己的一份。个人使用没问题；但在多用户或生产部署中，**请把 embeddings 卸载到外部服务**。
:::

- **推荐**：`RAG_EMBEDDING_ENGINE=openai`（OpenAI 或兼容 API）、`azure_openai`，或 `ollama`（自托管，例如 `nomic-embed-text` 这类模型）。
- **效果**：不会再向 Open WebUI 进程加载任何嵌入模型。

### 优化文档切块 {#optimizing-document-chunking}

切块方式会直接影响存储效率与检索质量：

- **使用 Markdown 标题切分**：这样能保留文档的语义结构
- **设置 Chunk Min Size Target**：使用 markdown header splitter 时，可能产生极小的 chunk（例如只有一个小标题），这类 chunk 存储效率低，检索效果也差
  - **环境变量**：`CHUNK_MIN_SIZE_TARGET=1000`（示例值）
  - **收益**：智能地把小 chunk 与相邻块合并，大幅减少向量总数并提升 RAG 性能

---

## 📈 扩缩容基础设施（多租户与 Kubernetes） {#scaling-infrastructure-multi-tenancy--kubernetes}
对于**企业级规模**（数百用户），应在负载均衡器后面运行多个副本，每个副本一个 worker，可用 Docker Compose、Docker Swarm 或 Kubernetes 部署。

完整扩缩容路径（PostgreSQL、Redis、Vector DB、存储、可观测性）请参阅 **[Scaling Open WebUI](/getting-started/advanced-topics/scaling)**。

- **Kubernetes / Helm**：多副本部署请参阅 [扩缩容与高可用指南](/troubleshooting/multi-replica)
- **Redis（必需）**：当使用多个 worker 或多个副本时，**必须**使用 Redis 处理 WebSocket 与会话同步，详见 [Redis Integration](/tutorials/integrations/redis)
- **负载均衡**：普通轮询（round-robin）即可。粘性会话在哪些场景下有帮助，参见 [Session Affinity](/troubleshooting/multi-replica#session-affinity-sticky-sessions)。
- **反向代理缓存**：把反向代理（例如 Nginx、Caddy、Cloudflare）配置为**缓存静态资源**（JS、CSS、图片），这能显著降低应用服务器的负载。参见 **[Nginx Config](/reference/https/nginx)** 或 **[Caddy Config](/reference/https/caddy)**。
- **关闭代理缓冲（流式输出关键项）**：如果使用 Nginx，**必须**关闭 `proxy_buffering`，否则会导致 Markdown 乱码和流式变慢。请在 location 块中加入 `proxy_buffering off;` 和 `proxy_cache off;`。详见 [Streaming Troubleshooting](/troubleshooting/connection-error#garbled-markdown--streaming-response-corruption)

---

## ⚡ 高并发与网络优化 {#high-concurrency--network-optimization}

当同时在线用户较多时，下列设置很容易成为关键瓶颈。

#### 批量流式输出 token {#batch-streaming-tokens}
默认情况下（`1`），Open WebUI 会把 LLM 返回的**每一个 token**都立即流式推送给前端。高频推流会增加服务器网络 IO 与 CPU 开销。

通过调大 chunk size，可以把这些更新打包后再发送给客户端。代价只是 UI 流式显示会稍微不那么“丝滑”，但对性能通常很有帮助。

- **Env Var**：`CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=7`
  - **建议**：高并发实例可设置为 **5-10**

#### HTTP 响应压缩 {#http-response-compression}

默认情况下，Open WebUI 会在应用内部使用 ZStd/Brotli/Gzip 压缩 HTTP 响应（JSON API 响应以及 Web UI 的静态 JS/CSS 资源）。这会在每个 worker 上消耗 CPU：对生产部署进行性能剖析（py-spy）显示，约有 **3–4% 的 worker CPU 时间**花在压缩中间件上。关闭它可以释放这部分 CPU，并略微降低响应延迟。

*   **作用范围**：仅限大于 500 字节且内容类型可压缩的普通 HTTP 响应。WebSocket（Socket.IO）流量和流式对话响应（SSE）都未经压缩直接透传，因此对话流式传输的热路径两种情况下完全相同。
*   **何时关闭**：你的反向代理 / 负载均衡器 / CDN 已经会压缩响应（推荐：在那里开启并关闭应用内的压缩），或者用户通过快速/本地网络访问实例，额外的传输体积无关紧要。
*   **何时保持开启**：后端直接暴露在互联网上、前面没有任何负责压缩的组件，且用户通过慢速或移动网络连接。未压缩时，首次（未缓存）页面加载会多传输数兆字节，而长对话历史或大模型列表这类大载荷会增长 5–10 倍。

- **环境变量**：`ENABLE_COMPRESSION_MIDDLEWARE=false`

*   **推荐搭配**：当你改用代理来代替应用侧压缩时，也让代理**激进地缓存静态资源**。Open WebUI 的 JS/CSS 资源包位于 `/_app/immutable/` 下且文件名带内容哈希，因此可以用 `Cache-Control: public, max-age=31536000, immutable` 缓存并直接从代理缓存返回，根本不会命中 worker，这消除了除首次访问外每次访问都“首次页面加载更大”的缺点。现成的 Nginx 配置片段参见[扩展 → 在代理层配合静态资源缓存](/getting-started/advanced-topics/scaling#pair-it-with-static-asset-caching-at-the-proxy)。

完整的取舍讨论参见 [`ENABLE_COMPRESSION_MIDDLEWARE`](/reference/env-configuration#enable_compression_middleware)。

#### 流式响应组装 {#streamed-response-assembly}

Open WebUI 会在每个数据块到达时重建响应的文本，每次都复制此前收到的全部内容。其开销随答案长度呈平方级增长，并且消耗在事件循环上，因此一个正在组装超长答案的 worker 会拖住它正在服务的其它所有流。改为就地扩展文本可以消除复制，并随之降低内存峰值，因为复制需要同时在内存中保存新旧两个字符串。

- **环境变量**：`ENABLE_CHAT_RESPONSE_STREAM_INPLACE_APPEND=true`

*   *建议*：在长答案属于常态（智能体记录、大段代码输出、超长工具输出）且同时有多个流在传输的地方开启它。普通对话答案无论哪种方式都在亚毫秒级，因此小型实例不会有明显感觉。
*   *代价*：如果追加过程中内存耗尽，那一条消息会留空，而不是保留已经收集到的文本。容器内存限制则会直接杀死进程，因此这需要一次分配被拒绝，这种情况很少见。

完整说明参见 [`ENABLE_CHAT_RESPONSE_STREAM_INPLACE_APPEND`](/reference/env-configuration#enable_chat_response_stream_inplace_append)。

#### WebSocket 帧压缩 {#websocket-frame-compression}

上面的 HTTP 中间件从不处理 WebSocket 流量，但 WebSocket 服务器会自行压缩帧，而这才是流式负载下值得关闭的那一项。对话响应以每个 token 一个极小帧的形式到达，因此每一帧都会被单独压缩、对每个订阅者各压缩一次，而在这个尺寸下几乎没有任何收益。在高强度流式传输下，这会表现为可测量的 worker CPU 占用。

- **环境变量**：`UVICORN_WS_PER_MESSAGE_DEFLATE=false`

*   *代价*：原本压缩效果好的帧是少数的大帧，例如一条完整消息或一组来源资料，而且即便是一条很长的回复，未压缩也只有几百 KB，任何网络都能无明显延迟地传输。
*   *默认值*：开启。

完整说明参见 [`UVICORN_WS_PER_MESSAGE_DEFLATE`](/reference/env-configuration#uvicorn_ws_per_message_deflate)。

#### WebSocket 心跳 {#websocket-heartbeats}

每个已连接的浏览器都会按固定间隔（默认 30 秒）告诉服务器自己还在。这意味着每个打开的标签页只有一条小消息，因此一个挂着数千个空闲标签页的实例会花掉可观的时间去处理这些不携带任何内容的消息。

- **环境变量**：`WEBSOCKET_HEARTBEAT_INTERVAL=60`

*   **代价**：服务器会保留四倍间隔的时间（即 120 秒）作为在线状态记录，取两者中的较大值，因此合上笔记本离开的用户会在退出活跃用户统计之前更长时间地显示为活跃。
*   **取值范围**：数值限定在 `5` 到 `90` 之间。该设置会发送到浏览器，因此无需重新构建前端即可生效。

参见 [`WEBSOCKET_HEARTBEAT_INTERVAL`](/reference/env-configuration#websocket_heartbeat_interval)。

#### JSON 编码器 {#json-encoder}

Open WebUI 会为每个请求体、API 响应、保存的对话、服务商请求和流式数据块编码和解码 JSON，也会为每个 Socket.IO 事件这样做，包括在多副本下通过 Redis 发布的事件。所有这些都经过 [orjson](https://pypi.org/project/orjson/) 处理，这是一个 Rust 实现，比 Python 标准库的 `json` 模块快数倍。

*   **影响最大的地方**：集群部署中的 Socket.IO 编码、流式数据块的解析，以及长对话的保存与打开。
*   **影响不大的地方**：聊天体积普通的单用户实例。
*   **回退**：orjson 无法编码的内容会回退到标准库。有一处差异：`NaN` 和 `Infinity` 浮点数会被序列化为 `null`，而标准库会抛出错误。

- **环境变量**：`ENABLE_ORJSON=True`
  *   *建议*：保持开启。

完整说明参见[多副本 → 使用更快的 JSON 编码器](/troubleshooting/multi-replica#use-the-faster-json-encoder)，变量本身参见 [`ENABLE_ORJSON`](/reference/env-configuration#enable_orjson)。

#### 日志级别 {#log-level}

被该级别过滤掉的消息根本不会被构造，因此调高级别既节省 CPU 也减少日志量，在繁忙的服务器上以及从大型知识库检索的对话中尤为明显。`WARNING` 还会丢掉记录启动、关键事件和请求处理的 `INFO` 日志行，因此如果你的日志聚合依赖这些行，请保留 `INFO`。

- **环境变量**：`GLOBAL_LOG_LEVEL=WARNING`
  *   *建议*：在繁忙且不依赖 `INFO` 日志行的实例上试用。切勿在生产环境保持 `DEBUG` 级别开启，这是运行成本最高的日志级别。更改后需要重启。

完整说明参见[日志级别的代价](../getting-started/advanced-topics/logging.md#what-the-log-level-costs)。

#### 线程池大小 {#thread-pool-size}
限制 AnyIO 工作线程池中**并发**阻塞操作（同步 DB 调用、文件 I/O、通过 `run_in_threadpool` 卸载的同步路由处理器）一次能同时运行的数量。这是一个**并发上限**，而不是一组固定预生成的 OS 线程，也**不是** CPU 核心/线程数——线程是按需懒加载并复用的，因此设置一个很大的值并**不会**凭空创建这么多线程、消耗 CPU，或在空闲时带来争用。它只决定了多少阻塞操作可以同时进行，超出的必须排队。

- **Default**：40（AnyIO 默认值——对生产环境来说远不够）
- **普通服务器/生产环境**：**2000+**。`2000` 对非常大的实例来说只是*下限*，调得更高也没问题，而且**不会**带来 CPU/争用风险（它是上限，而不是预分配）。
- **如果设得太低的症状**：当同时需要的阻塞操作数超过 `THREAD_POOL_SIZE`（许多用户同时操作，或少量用户各自触发多次阻塞调用）时，更多请求会**排队**等待空闲槽位。**整个应用看起来就像挂起/冻结/停止响应**，即使 CPU 和内存看起来都正常——这是线程池饥饿，不是资源耗尽。
- **警告**：**永远不要低于默认值。** 一个空闲的高上限几乎不消耗任何资源；低上限才会导致冻结。
- **例外——弱硬件**（Raspberry Pi、小型 VPS、CPU 配额约为 250m / 内存很低的容器）：不要在这里设置 `2000`。每个*真正并发*的阻塞操作仍会占用一个真正的 OS 线程（栈内存），所以在极小设备上，一个超大的上限会让一次流量突增耗尽内存。保持默认值，或按设备实际承受能力设置为几百的较小值。这个例外只适用于受限的单板/微型部署——任何正常服务器都应该用 `2000+`。

- **Env Var**：`THREAD_POOL_SIZE=2000`

详见 [`THREAD_POOL_SIZE`](/reference/env-configuration#thread_pool_size) 的完整说明。

#### AIOHTTP 客户端超时 {#aiohttp-client-timeouts}
默认情况下，对模型服务商的请求没有总超时，因此很长的补全也不会被切断。模型列表请求在 10 秒后超时。

- **环境变量**：`AIOHTTP_CLIENT_TIMEOUT`（默认未设置）。可以设置它，例如设为 `1800`，以限制卡死的服务商最长能占用请求多长时间。
- **环境变量**：`AIOHTTP_CLIENT_STREAM_IDLE_TIMEOUT`（默认未设置）。当服务商在该秒数内没有返回新数据时，请求会被终止；而只要长流式响应仍在持续产出，就可以一直运行下去。
- **环境变量**：`AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST`（默认 `10`）。对于要列出数百个模型的慢速服务商，可以调高它。

#### DNS 解析器 {#dns-resolver}

默认情况下，Open WebUI 会让操作系统解析主机名，而这些查找会相互排队，并排在其他后台工作之后，因此在高负载下本应只需毫秒的查找会拖慢它所属的请求。c-ares 解析器不会排队，因此许多并发查找耗时与一次查找相当。在一次发出大量出站请求的实例上收益最大，而在空闲实例上则几乎看不出来。

- **环境变量**：`AIOHTTP_CLIENT_ASYNC_DNS_RESOLVER=True`
  *   *建议*：试用一下，然后实际操作你的模型、网页搜索和各项内部服务；若查找开始失败，请把它关回去。需要重启。

c-ares 读取的名称来源比操作系统少，因此保持它开启前请先阅读 [`AIOHTTP_CLIENT_ASYNC_DNS_RESOLVER`](../reference/env-configuration.mdx#aiohttp_client_async_dns_resolver)。如果你正在排查时好时坏的查找失败，请参阅[间歇性名称查找失败](./connection-error.mdx#intermittent-name-lookup-failures-often-reported-as-model-not-found)。

#### 容器资源限制 {#container-resource-limits}
对 Docker 部署，请确保资源配额充足：

```yaml
deploy:
  resources:
    limits:
      memory: 8G      # Adjust based on usage
      cpus: '4.0'
    reservations:
      memory: 4G
      cpus: '2.0'

# Increase file descriptor limits
ulimits:
  nofile:
    soft: 65536
    hard: 65536
```

**诊断命令：**
```bash
# Check container resource usage
docker stats openwebui --no-stream

# Check connection states
docker exec openwebui netstat -an | grep -E "ESTABLISHED|TIME_WAIT|CLOSE_WAIT" | sort | uniq -c

# Check open file descriptors
docker exec openwebui ls -la /proc/1/fd | wc -l
```

---

## ☁️ 云基础设施延迟 {#cloud-infrastructure-latency}

在云上 Kubernetes（AKS、EKS、GKE）部署 Open WebUI 时，即使资源配额与本地环境看起来一致，也经常会明显比本地 Kubernetes（Rancher Desktop、kind、Minikube）或裸金属部署更慢。绝大多数情况下，根因是**底层基础设施延迟**。

### 网络延迟（数据库与服务） {#network-latency-database--services}

最常见的问题，是 **Open WebUI 与数据库之间的网络延迟**。

很多云部署会把数据库放在其他节点、可用区，甚至托管数据库服务上。这样的架构本身没问题，但它会给**每一条数据库查询**都增加延迟。Open WebUI 每个请求往往会触发多次数据库操作，因此即使单次查询只多出 10-20ms，在并发下也可能叠加成多秒延迟。

**症状：**
- 健康检查 endpoint 响应时间明显偏高，而不是接近瞬时
- 普通 API 或聊天请求在并发下明显变慢，即使 CPU / Memory 看起来并不高
- 本地测试正常，云上生产明显更慢

**诊断：**
- 从 pod 内部测试 Open WebUI 到数据库的延迟：
  ```bash
  # For PostgreSQL
  psql -h <db-host> -U <user> -c "SELECT 1" -d <database>
  
  # Or use ping/nc to check raw latency
  nc -zv <db-host> 5432
  ```
- **理想目标**：数据库查询延迟应尽量做到 **1-2ms 或更低**。如果网络延迟超过 **5ms**，对生产环境来说通常已经不理想，并很可能成为主要性能瓶颈。

**解决方法：**
1. **服务就近部署**：尽量让 Open WebUI 与 PostgreSQL 位于同一可用区，甚至同一节点池
2. **谨慎使用托管数据库**：云上的“一键式”托管数据库虽然省心，但通常比同节点自托管数据库引入更高网络延迟
3. **启用缓存**：使用 `ENABLE_BASE_MODELS_CACHE=True` 以及其他[缓存选项](#2-caching--latency-optimization)，减少每次请求的重复工作
4. **减少数据库写入**：把 [`DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL`](#user-active-status-write-throttling-set-this-on-every-deployment) 保持在 `60` 或更高

### 磁盘 I/O 延迟（SQLite 与存储） {#disk-io-latency-sqlite--storage}
如果你在云环境中继续使用 **SQLite**（默认值），你可能只是把网络延迟换成了**磁盘延迟**。

云存储（Azure Disks、AWS EBS、GCP Persistent Disks）在很多情况下都比本地 NVMe/SSD 延迟更高、IOPS 更低，尤其是低等级存储类。

:::danger SQLite 跑在 NFS / SMB / Azure Files 上不受支持——这是 SQLite 自身的限制
这不是 Open WebUI 的限制，而是 **SQLite 上游项目**的明确说明。SQLite 官方 [明确指出](https://www.sqlite.org/faq.html#q5)，网络文件系统（NFS、SMB/CIFS 等）上的 SQLite 数据库**不受支持**：文件锁并不可靠，并发写入**可能损坏数据库**。SQLite 文档对此有明确警告，而 Open WebUI 因为使用了 SQLite，也就继承了这一限制。

因此，对 Open WebUI 而言，**唯一受支持的存储配置是**：

- **PostgreSQL**：任何多用户部署的推荐方案，也是任何非直连本地 SSD 场景的必需方案。它可以彻底绕开"网络存储上的 SQLite"问题。**或者**
- **直连 SSD / NVMe 上的 SQLite**：仅限单用户 / 小规模部署。必须是宿主机上的**本地**磁盘；无论应用是什么，SQLite 上游的建议都适用。

按 SQLite 自己的文档（而非 Open WebUI 的策略），**不受支持**的 SQLite 存储包括：**NFS、SMB/CIFS、Azure Files、GlusterFS、CephFS、基于对象存储的 FUSE 挂载、网络 PVC，以及任何远程或低 IOPS 的存储。** 这也包括由这些文件系统支撑的 Docker 绑定挂载和 Kubernetes PersistentVolumeClaim。除了下文列出的性能症状之外，你还要冒着**数据库损坏**的风险——依旧是依据 SQLite 自己的说法，而不是我们。

如果你的存储不是本地 SSD/NVMe，**请使用 PostgreSQL**。

SQLite 跑在网络存储上的典型症状：

- `/api/config` 每次请求都要 **10 到 20 多秒**
- `/api/v1/chats/?page=1` 等列表端点在负载下**卡住数分钟**
- OIDC / SSO 回调在重定向回 Open WebUI 时挂起或"空转"
- DEBUG 日志中 `aiosqlite` 与 `httpcore` 两行之间出现长达数秒的间隔
- `PRAGMA journal_mode=WAL` 在日志中启动了却始终没有完成
:::

#### 为什么异步后端会让网络存储上的 SQLite 问题突然变得严重 {#why-the-async-backend-makes-network-storage-sqlite-fail-suddenly}
Open WebUI 异步执行数据库调用，因此许多调用会同时处于进行中。在慢速存储上它们会不断堆积，直到应用停止响应。`DATABASE_POOL_SIZE` 之类的设置只能治标，存储才是病根。

**核心在于 `fsync()`。** SQLite 通过同步落盘来保证持久性（默认 WAL 模式下、`synchronous=NORMAL` 时，在每次检查点处）。`fsync` 的延迟完全取决于文件存放在哪里：

| 存储 | 典型 `fsync` 延迟 |
| :--- | :--- |
| 本地 NVMe | ~100 μs |
| 本地 SATA SSD | 100 μs 到数 ms |
| 本地 HDD | ~10 ms |
| NFS / CephFS / Azure Files（SSD 后端） | 50 到 500 ms |
| NFS（HDD 后端或高延迟） | 数百 ms 到数秒 |

**并发会成倍放大它。** 每次数据库调用都会从 SQLite 连接池中取出一个连接（未设置 `DATABASE_POOL_SIZE` 时为 512 个连接，外加 10 个溢出连接）。在本地 SSD 上，一个连接大约一毫秒就能归还连接池；在 NFS 或 CephFS 上，它每次落盘都会占用数百毫秒，写入者在文件锁上排队，请求随之堆积。一旦连接池耗尽，后续每个请求都要等待 `DATABASE_POOL_TIMEOUT`（30 秒）并最终失败：

```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 512 overflow 10 reached,
connection timed out, timeout 30.00
```

更大的连接池只会把崩溃点往后推：更多连接意味着对同一存储发起更多并发的慢速落盘。

**而且 NFS 上的 WAL 是明确有问题的。** SQLite 的 WAL 模式使用由 `mmap` 支撑的 `-shm` 文件进行跨进程协调。[SQLite 上游直言不讳](https://www.sqlite.org/faq.html#q5)，在 NFS 上使用 `mmap` 不可靠：某些 NFS 版本根本不支持。在并发情况下你会遇到真正的锁异常（死锁、`PRAGMA journal_mode=WAL` 启动了却始终不完成、对简单查询出现数分钟的卡顿）。

**为什么 Postgres 才是解法：** Postgres 服务器自己管理针对其本地存储的 I/O 并发。你的应用通过网络套接字访问它，这一跳的代价比 NFS 的 `fsync` 低若干个数量级，而且 Postgres 正是为并发写入者而生的：没有文件级锁，没有跨进程 `mmap` 协调，也没有网络文件系统上的 WAL 注意事项。Open WebUI 通过异步 `psycopg` 驱动与它通信。

**症状：**
- 单用户时性能尚可，但随着并发增加迅速劣化
- 服务器 "I/O Wait" 很高，但 CPU 占用率却很低

**解决方案（按稳健程度排序）：**

1. **最佳方案：迁移到 PostgreSQL。** 对于任何不是严格单用户且运行在本地磁盘上的部署，这是推荐的修复方案；对于任何运行在远程/网络/低 IOPS 存储上的部署，它都是必需的。请设置：
   ```bash
   DATABASE_URL=postgresql://user:password@host:5432/webui
   ```
2. **可接受方案：把 `webui.db` 放到直连的本地 SSD/NVMe 上。** 仅适合单用户或极小规模部署。请把宿主机**本地** SSD/NVMe 上的目录 bind mount 到 `/app/backend/data`。绝不要为它使用 NFS、SMB、Azure Files 或任何其他网络后端的存储类别。
3. **仅限临时止损：在降低并发的情况下继续在 NFS 上使用 SQLite。** 如果你无法立即迁移存储或切换数据库，请设置：
   ```bash
   DATABASE_POOL_SIZE=1
   DATABASE_SQLITE_PRAGMA_BUSY_TIMEOUT=30000
   ```
   `DATABASE_POOL_SIZE=1` 会把 SQLite 连接池缩小为一个连接加 10 个溢出连接，因此同时打到存储上的写入者少得多，用并发换稳定性。`DATABASE_SQLITE_PRAGMA_BUSY_TIMEOUT=30000` 给 SQLite 30 秒获取锁，而在 NFS 上这可能比本地磁盘慢得多。这**不是受支持的长期配置**：请预期吞吐量下降、间歇性卡顿和潜在的数据损坏。请尽快规划迁移到 PostgreSQL 或本地 SSD。重启后连接池预热时可能短时间内看起来正常，但负载一回来问题就会重现。
4. **云块存储：** 当你使用云块存储承载 Open WebUI 数据卷（无论是给 PostgreSQL 还是应用本身）时，请使用 SSD 支持的 **Block Storage** 类别（例如 Azure Disks 上的 `Premium_LRS`、AWS EBS 上的 `gp3`、GCP 上的 `pd-ssd`）。任何数据库工作负载（包括 SQLite）都应避免基于 "File" 的存储类别（例如 `azurefile-csi`）。

### 其他云端注意事项 {#other-cloud-specific-considerations}

| 因素 | 影响 | 缓解方式 |
|--------|--------|------------|
| **Burstable VMs**（如 Azure B-series、AWS T-series） | 持续负载下 CPU 被限速 | 使用标准或 compute-optimized 节点池 |
| **DNS 解析** | 每次外部请求都经过 CoreDNS，增加延迟 | 适当扩容 CoreDNS，必要时启用 node-local DNS cache |
| **Service Mesh Sidecars** | Istio/Linkerd 为每个请求增加代理延迟 | 检查 pod 中是否有意外 sidecar |
| **Network Policies** | CNI 处理增加额外开销 | 在可能情况下审计并简化策略 |
| **跨可用区流量** | 增加延迟与出网费用 | 尽量把服务固定在同一可用区 |

---

## 📉 资源效率（降低内存占用） {#resource-efficiency-reducing-ram}

如果你部署在内存受限设备上（Raspberry Pi、小型 VPS），可以通过下面这些方式降低 OOM 风险。

### 精简镜像 {#the-slim-image}

如果你的模型、嵌入、文档提取和语音都以外部服务运行，请使用精简镜像：`ghcr.io/open-webui/open-webui:slim`（也有 `:main-slim`，或用 `:<version>-slim` 固定某个版本）。它是用 `USE_SLIM=true` 构建的标准镜像，其特点是：

- 安装精简的 Python 依赖集：不含 PyTorch、SentenceTransformers、Transformers 和 faster-whisper，除 pgvector 外不含任何向量数据库客户端，不含 Playwright，不含本地 PDF 与 Office 解析器，也不含 Azure 或 Google Cloud 存储 SDK
- 跳过 pandoc、ffmpeg、git 以及编译工具链等系统包
- 不内置任何模型（标准镜像会附带嵌入模型、辅助嵌入模型、Whisper `base` 以及 tiktoken 编码）
- 携带代码解释器的 Pyodide 运行时，但不含其 Python 包

**效果**：amd64 下载体积约为 200 MB，而标准镜像约为 1.6 GB。永远不会加载任何本地模型或机器学习库，因此无论启用哪些功能，内存都保持在应用自身的基线水平，额外副本也不会带来模型副本。实测的空闲占用参见[内存占用](/getting-started/quick-start#slim-memory-usage)。

**精简镜像上需要注意的设置：**

| 功能 | 设置 |
|---|---|
| 嵌入 | `RAG_EMBEDDING_ENGINE=openai`、`azure_openai` 或 `ollama`。本地引擎不可用 |
| 向量数据库 | `VECTOR_DB` 默认为 `pgvector`。请设置 `PGVECTOR_DB_URL`，或使用带 pgvector 扩展的 PostgreSQL `DATABASE_URL`。其他存储在首次使用时就会失败 |
| 文档 | `CONTENT_EXTRACTION_ENGINE` 用于 PDF 和 Office 文件。纯文本、Markdown、CSV、HTML 和 XML 在进程内读取 |
| 重排序 | `RAG_RERANKING_ENGINE=external`，或把重排序模型留空以使用余弦打分 |
| 语音 | 外部的 `AUDIO_STT_ENGINE`，或用 `web` 进行浏览器识别。外部的 `AUDIO_TTS_ENGINE`，或默认浏览器语音。`BYPASS_PYDUB_PREPROCESSING` 始终开启 |
| 数据库与文件 | SQLite 或 PostgreSQL 的 `DATABASE_URL`，`STORAGE_PROVIDER=local` 或 `s3`。其他任何组合都会导致启动失败 |

有两样东西改为在运行时下载而非随镜像分发：tiktoken 编码（首次使用 `token` 文本切分器时下载，缓存在 `TIKTOKEN_CACHE_DIR` 中），以及代码解释器的 Python 包（由浏览器从 `cdn.jsdelivr.net` 获取）。完整功能对照表参见[为什么选择精简版？](/getting-started/quick-start#what-slim-leaves-out)。

### 1. 卸载辅助模型（仅本地部署相关） {#1-offload-auxiliary-models-local-deployments-only}

在标准镜像上，Open WebUI 可以在自身进程内运行 RAG 与语音模型。**本节仅在你本地运行这些模型时才相关。**

#### RAG 嵌入 {#rag-embeddings}
- **低配建议：**
  - **方案 A（最简单）**：保持默认 **SentenceTransformers**（all-MiniLM-L6-v2）。它运行在 CPU 上，通常比在同一台 Raspberry Pi 上再跑一个完整 Ollama 更省资源。
  - **方案 B（性能更好）**：改用**外部 API**（OpenAI/Cloud）。
- **配置位置：**
  - **Admin Panel**：`Settings > Documents > Embedding Model Engine`（管理员区域）
  - **Env Var**：`RAG_EMBEDDING_ENGINE=openai`

#### 语音转文本（STT） {#speech-to-text-stt}
默认引擎是本地 Whisper，它会在第一次转写时加载进 Open WebUI 进程，并一直留在那里。

- **建议**：改用 **WebAPI**（浏览器端），让用户设备承担语音识别，服务器几乎零内存负担。
- **配置方式：**
  - **Admin Panel**：`Settings > Audio > STT Engine`（管理员区域）
  - **Env Var**：`AUDIO_STT_ENGINE=web`

- **绕过音频预处理（卸载到 STT 提供方）**：如果你使用的外部 STT 引擎（OpenAI、Deepgram、Azure、Mistral）本身就能接收原始音频并在它那一侧完成格式转换，可以设置 `BYPASS_PYDUB_PREPROCESSING=true`。这会跳过 Open WebUI 基于 pydub 的 MP3 转码、压缩与切块，从而去掉每次上传中一个 CPU 密集的步骤，并降低大文件的延迟。只有在你确信该服务商能正确处理未经处理的音频时，才启用它。

### 2. 关闭未使用功能 {#2-disable-unused-features}
在标准镜像上，以下功能会把本地模型加载进 Open WebUI 进程。请关闭它们，或把它们指向外部服务：

- **重排序**：开启混合搜索（`ENABLE_RAG_HYBRID_SEARCH=True`）且本地引擎上配置了 `RAG_RERANKING_MODEL` 时，每个 worker 都会在启动时加载重排序模型。请改用 `RAG_RERANKING_ENGINE=external`，或者干脆把模型留空。
- **本地文字转语音**：`AUDIO_TTS_ENGINE=transformers` 会在首次使用时加载语音模型。请改用外部引擎。

图像生成和代码解释器运行在外部引擎或浏览器中，因此不会在服务端内存中占用模型。

### 3. 关闭后台任务 {#3-disable-background-tasks}

如果资源非常紧张，可以关闭那些会持续触发模型推理的自动功能。

**建议关闭顺序（影响从高到低）：**
1. **Autocomplete**：`ENABLE_AUTOCOMPLETE_GENERATION=False`（默认值；保持关闭，它会在每次按键时触发）
   - 管理员：`Settings > Interface > Autocomplete`（管理员区域）
2. **Follow-up Questions**：`ENABLE_FOLLOW_UP_GENERATION=False`
   - 管理员：`Settings > Interface > Follow-up`（管理员区域）
3. **Title Generation**：`ENABLE_TITLE_GENERATION=False`
   - 管理员：`Settings > Interface > Chat Title`（管理员区域）
4. **Tag Generation**：`ENABLE_TAGS_GENERATION=False`

### 4. 把 ChromaDB 换成 Milvus Lite（小型部署） {#4-swap-chromadb-for-milvus-lite-small-deployments}

在树莓派或小型 VPS 上，除模型之外，默认的本地 ChromaDB 通常是进程中占用最大的东西。Milvus Lite 与 ChromaDB 类似，是一个嵌入式数据库，不需要服务器，也不需要额外的容器，并且能用明显更少的磁盘和更少的常驻内存保存同样的内容。切换前请先阅读下面的限制，因为它排除了任何批量导入文档的部署。

:::danger 不适用于批量文档导入

磁盘和内存上的节省只有在知识库规模较小且基本保持不变时才有意义。如果你打算上传大规模语料，或者要持续添加文件，请继续使用 ChromaDB 或改用 Milvus 服务器。

Open WebUI 在存储文件之前会查询其内容哈希，以免同一份文档被索引两次。该查询会按元数据字段过滤，而 Milvus Lite 不为元数据建立索引，因此每次都要读取整个集合。于是你已存的文件越多，新增一个文件的代价就越高，导入整个语料的时间也会随其规模的平方级增长。

使用 Open WebUI 自身的集合 schema 对本地 Milvus Lite 数据库进行测量，单次哈希查询耗时如下：

| 集合中的行数 | 单次查询耗时 |
| --- | --- |
| 500 | 0.72s |
| 1,000 | 1.43s |
| 2,000 | 2.94s |
| 3,000 | 4.51s |
| 4,000 | 7.94s |

同样的查询在 ChromaDB 上无论规模多大都保持平稳（500 行时 0.024s，4,000 行时 0.002s），因为 ChromaDB 把元数据存放在带索引的 SQLite 中。

在同一台机器、相同设置和相同嵌入服务商下端到端地导入 Markdown 文件，Milvus Lite 的速度为每分钟 8 个文件，并随着集合增长跌破 5 个，而 ChromaDB 为每分钟 200 到 368 个文件。按实测的每行成本外推，28,000 个文件的语料在 Milvus Lite 上大约需要 170 小时。

这里讨论的是导入。检索性能并未测量，Milvus 服务器也未测量，后者与此处描述的嵌入式 Milvus Lite 属于不同的部署方式。

:::

节省来自多租户，因此请与切换一起启用：

```
VECTOR_DB=milvus
ENABLE_MILVUS_MULTITENANCY_MODE=True
```

请不要设置 `MILVUS_URI`。默认值已经指向数据目录内的嵌入式数据库，把该变量设为那个路径反而会让应用无法启动。原因以及必须事先存在的目录，参见 [`MILVUS_URI`](/reference/env-configuration#milvus_uri-required)。

多租户开启后，用户共享同一组集合，每个用户的向量在其中做分区。若不开启，每个用户和每个知识库都会拥有自己的集合，这正是占用空间增长远快于内容本身的原因。在存储空间紧张或按量计费的设备上，这通常是卸载嵌入模型之后可获得的最大单项缩减。

这适用于单实例部署。Milvus Lite 是由单个进程持有的文件，因此要增加副本就必须改用 Milvus 服务器。

### 5. SQLite 在受限容器中的内存占用 {#5-sqlite-memory-footprint-on-constrained-containers}

这个问题在**快速的本地 SSD/NVMe 上也会出现**。它属于 RAM 问题，而非存储延迟问题（关于网络存储的延迟/损坏问题，请参阅[磁盘 I/O 延迟](#disk-io-latency-sqlite--storage)）。在小型部署上，“编辑模型或知识库权限时容器被 OOM 杀死” 的最常见原因正是这个。

在 SQLite 下，当 `DATABASE_POOL_SIZE` 保持未设置时，当前版本（0.9.x，异步 DB 后端）**不会**回退到 SQLAlchemy 的小默认池，而是回退到一个很大的内部池（目前是 **512** 个连接）。每个被池化的连接各自独立地：

- 把自己的 **SQLite 页面缓存**懒增长到 `DATABASE_SQLITE_PRAGMA_CACHE_SIZE` 上限。默认值 `-65536` 大约是**每个连接 64 MB 已提交 RAM**。
- 内存映射数据库文件，上限为 `DATABASE_SQLITE_PRAGMA_MMAP_SIZE`，默认 **每个连接 256 MB**。这部分大多是虚拟内存、由文件后端承载，不会全部计入已提交匿名 RAM，但它会大幅抬高 `total-vm`，其中驻留部分仍会计入 cgroup 内存限制。
- 运行在它**自己的 OS 线程**上（异步 SQLite 驱动一个连接一个线程），额外消耗线程栈地址空间。

因此峰值内存随**同时活跃连接数**线性放大，而不是由单次查询的体量决定。一个会瞬时扇出大量短生命周期连接的工作流——例如编辑模型或知识库访问控制，然后再去重新加载长长的模型列表——就可能在短时间内让几十个连接同时在线。在一个很小的容器上，仅页面缓存（活跃连接数 × 每个最多 64 MB）就会超出限制，OOM killer 就会终止进程。用 profiler（py-spy、memray）观察时，几乎所有内存都来自 `aiosqlite/core.py`——因为每条连接恰好就在那个栈帧里分配自己的缓存并物化行。这正是 “很多连接” 的特征，而不是驱动内部的泄漏，也与远程向量数据库的体量无关。

:::tip 受限/低配容器（SQLite）
在任何内存限制较紧的部署（小 VPS、Raspberry Pi、1 到 2 GB 的 Docker `mem_limit`）上，请显式设置以下变量，而不要依赖默认值：

```bash
DATABASE_POOL_SIZE=8                       # 8 connections plus 10 overflow instead of 512 plus 10
DATABASE_SQLITE_PRAGMA_CACHE_SIZE=-2000    # ~2 MB page cache per connection instead of ~64 MB
DATABASE_SQLITE_PRAGMA_MMAP_SIZE=0         # disable the per-connection mmap window
```

同时给容器留出合理的 headroom。**1 GB 非常低**，任何涉及 RAG 或 embeddings 的场景都不够用；目标应是 **2 GB 或更多**。在低配硬件上保持 `DATABASE_ENABLE_SESSION_SHARING=False`（默认）；在弱硬件上开启它是错误的杠杆，会让 SQLite 表现得更差（参见[数据库会话共享](#database-session-sharing)）。

对于多用户或持续增长的部署，可持续的解法是 **PostgreSQL**，而不是再去调 SQLite。
:::

---

### 6. 大型文档上传 {#6-large-document-uploads}

处理文档时，其文本块及其嵌入向量会在写入向量数据库的过程中一直驻留在内存中。

-   **环境变量**：`RAG_EMBEDDING_BUFFER_SIZE`（默认 `1000`）。文本块会按这个数量分批嵌入并保存，因此超大文档不会一次性持有全部嵌入向量。在小型设备上可以调低它以降低峰值。参见 [`RAG_EMBEDDING_BUFFER_SIZE`](/reference/env-configuration#rag_embedding_buffer_size)。
-   **环境变量**：`RAG_FILE_MAX_SIZE`（单位 MB，默认不设置）。在提取和嵌入之前就拒绝更大的上传。参见 [`RAG_FILE_MAX_SIZE`](/reference/env-configuration#rag_file_max_size)。

---

## 🚀 推荐配置档案 {#recommended-configuration-profiles}

### 档案 1：最大隐私（弱硬件 / RPi） {#profile-1-maximum-privacy-weak-hardwarerpi}
*目标：100% 本地，Raspberry Pi / 小于 4GB RAM。*

1. **Embeddings**：保持默认 SentenceTransformers（*在 CPU 上运行，负载很轻。*）
2. **Audio**：`AUDIO_STT_ENGINE=web`（*完全不占服务端负载。*）
3. **Task Model**：关闭，或使用一个极小的模型（`qwen3.5:0.8b`）
4. **Scaling**：保留默认 `THREAD_POOL_SIZE`（40）
5. **关闭**：追问、本地重排序和本地文字转语音。保持 Autocomplete 关闭（默认值）
6. **数据库**：SQLite 即可，但限制其内存：`DATABASE_POOL_SIZE=8`、`DATABASE_SQLITE_PRAGMA_CACHE_SIZE=-2000`、`DATABASE_SQLITE_PRAGMA_MMAP_SIZE=0`。未设置时 SQLite 连接池的默认值较大（512），参见 [SQLite 在受限容器中的内存占用](#5-sqlite-memory-footprint-on-constrained-containers)

### 档案 2：单用户极客 {#profile-2-single-user-enthusiast}
*目标：最大质量与速度，本地 + 外部 API 混合。*

1. **Embeddings**：`RAG_EMBEDDING_ENGINE=openai`（或在快速服务器上用 `ollama` + `nomic-embed-text`）
2. **Task Model**：`gpt-5.6-luna` 或 `gemini-3.5-flash-lite`
3. **缓存**：`MODELS_CACHE_TTL=300`
4. **Vector DB**：PGVector（推荐）或 ChromaDB（除非数据量极大，两者都可以）

### 档案 3：高规模 / 企业 {#profile-3-high-scale--enterprise}
*目标：大量并发用户，稳定性优先。*

1. **数据库**：**PostgreSQL**（必需）
2. **内容提取**：**Tika**、**Docling**、**或任何其他外部文档加载器**（必需：默认的 pypdf 会内存泄漏）。参见[内容提取引擎](#content-extraction-engine)。
3. **Embeddings**：**外部服务**——`RAG_EMBEDDING_ENGINE=openai`、`azure_openai` 或 `ollama`（必需：默认的 SentenceTransformers 在大规模下占用过多 RAM）。参见[嵌入引擎](#embedding-engine)。
4. **Tool Calling**：**Native Mode**（默认值；Legacy Mode 已不受支持，并且会破坏 KV cache）。所有模型都应配置为 Native Mode。参见[工具调用模式](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)。
5. **Threads**：`THREAD_POOL_SIZE=2000`（防止超时）
6. **Streaming**：`CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=7`（降低 CPU 与网络负载）
7. **Image**：当向量数据库为 PGVector 时使用 `:slim`。此档案中的所有内容都作为外部服务运行，因此标准镜像中的本地模型栈不会被用到。参见[精简镜像](#the-slim-image)。
8. **Vector DB**：**Milvus**、**Qdrant** 或 **PGVector**。**不要使用 ChromaDB 的默认本地模式**：其 SQLite 后端在多副本访问下会崩溃。
9. **Task Model**：外部/托管模型（卸载计算负载）
10. **Caching**：`ENABLE_BASE_MODELS_CACHE=True`、`MODELS_CACHE_TTL=300`、`ENABLE_QUERIES_CACHE=True`
11. **Redis**：单实例即可，但要配置 `timeout 1800` 和较高的 `maxclients`（10000+）。参见下方的[Redis 调优](#redis-tuning)。
12. **Compression**：如果你的负载均衡器 / ingress / CDN 会压缩响应，请设置 `ENABLE_COMPRESSION_MIDDLEWARE=False`（改为在那里开启压缩）。可为每个 worker 节省约 3–4% 的 CPU。参见[HTTP 响应压缩](#http-response-compression)。
13. **WebSocket 心跳**：`WEBSOCKET_HEARTBEAT_INTERVAL=60`。可以把每个打开的标签页的空闲心跳流量减半，代价是掉线的用户在活跃计数中停留的时间更长。参见[WebSocket 心跳](#websocket-heartbeats)。
14. **WebSocket 压缩**：`UVICORN_WS_PER_MESSAGE_DEFLATE=false`。流式输出每个 token 只发送一个很小的帧，为每个订阅者压缩这些帧会消耗 CPU 却几乎没有任何收益。参见[WebSocket 帧压缩](#websocket-frame-compression)。
15. **JSON 编码器**：`ENABLE_ORJSON=True`，默认已开启，请保持开启。它能大幅降低集群部署中最重的 JSON 开销：编码 Socket.IO 事件、解析提供方的流式数据块，以及保存和打开完整对话。参见[JSON 编码器](#json-encoder)。

#### Redis 调优 {#redis-tuning}
绝大多数部署（包括成千上万用户）都只需要一个单实例 Redis。除非你有明确高可用需求，否则**几乎不需要** Redis Cluster 或 Redis Sentinel。

每个 worker 还会保留它从 Redis 读取的、用于过滤查找的已解析模型列表，每 1000 个模型大约占用 3 MB 内存。

正在流式输出的响应会保存在 Redis 中，以便断线重连的浏览器可以继续接收，响应结束后该条目会被删除。被中途杀死的 worker 遗留的条目会在 `REDIS_RESPONSE_STREAM_TTL` 秒（默认 `3600`）后过期。Redis 内存紧张时可以调低它；设为 `0` 则永久保留。参见 [`REDIS_RESPONSE_STREAM_TTL`](/reference/env-configuration#redis_response_stream_ttl)。

常见 Redis 配置问题：

| 问题 | 症状 | 修复方式 |
|---|---|---|
| **陈旧连接** | Redis 连接数耗尽或内存无限增长 | 在 redis.conf 中设置 `timeout 1800`（30 分钟后终止空闲连接） |
| **maxclients 过小** | 出现 `max number of clients reached` 错误 | 将 `maxclients` 设为 10000 或更高 |
| **没有连接上限** | Open WebUI 的 Pod 可能累积永不关闭的连接 | 在 Redis 客户端配置中把 `timeout` 与连接池上限结合起来 |
| **Pub/Sub 输出缓冲区上限过低** | WebSocket 流停滞，出现 `Cannot publish to redis... giving up`，或在发布大型 Socket.IO 事件时 Redis 日志中出现客户端输出缓冲区断连 | 调高 Redis 的 `client-output-buffer-limit ... pubsub ...` 设置，容量按你的 websocket 负载和可用 Redis 内存确定 |

关于 Pub/Sub 输出缓冲区上限，包括检查它的命令和一份示例配置，请参阅[WebSocket Pub/Sub 缓冲区上限](/tutorials/integrations/redis#websocket-pubsub-buffer-limits)。

---

## ⚠️ 常见反模式 {#common-anti-patterns}
下面这些真实世界中的错误，经常会让组织为了掩盖根因而过度扩容基础设施：

| 反模式 | 会发生什么 | 正确做法 |
|---|---|---|
| **生产环境继续使用默认内容提取器** | pypdf 内存泄漏 → 容器频繁重启 → 被迫加更多副本 | 改用 Tika 或 Docling（`CONTENT_EXTRACTION_ENGINE=tika`） |
| **大规模部署仍使用 SentenceTransformers** | 每个 worker 各自加载 ~500MB 模型 → RAM 爆炸 → 被迫加更多机器 | 改用外部 embeddings（`RAG_EMBEDDING_ENGINE=openai`、`azure_openai` 或 `ollama`），或使用 [slim 镜像](#the-slim-image) |
| **单实例 Redis 就够，却上 Redis Cluster** | 副本太多 → 连接太多 → Redis 扛不住 → 被迫上集群 | 先修根因（减少副本、设置 `timeout 1800`、`maxclients 10000`） |
| **靠加副本掩盖内存泄漏** | 泄漏进程 → OOM → 自动扩容 → Redis 连接更多 → Redis 被打爆 | 先修泄漏（内容提取、嵌入引擎），再做容量规划 |
| **继续用 Default（prompt-based）tool calling** | 已过时 / 不再支持；注入式 prompt 会破坏 KV cache → 延迟更高 → 资源需求更大 | 把所有模型切到 Native Mode |
| **没有为 Redis 配置空闲连接超时** | 连接永远不回收 → Redis OOM → 被迫上 Redis Cluster | 在 redis.conf 中加入 `timeout 1800` |
| **在 Actions/Filters 中使用 base64 图标** | 图标数据会嵌入到 `/api/models` 响应中，前端每次为每个模型都加载一遍。20 个模型 × 3 个 Action × 500KB base64 图标 = 每次请求多 **30 MB 负载** → 前端加载慢、带宽浪费、后端内存压力 | 把图标作为静态文件托管，并用 `icon_url` / `self.icon` 引用。参见 [Action Function icon_url 警告](/features/extensibility/plugin/functions/action#example-specifying-action-frontmatter) |
| **在小容器上使用默认 SQLite 连接池** | 未设置 `DATABASE_POOL_SIZE` 会回退到 512 连接池；每个连接自带约 64 MB 页面缓存和一个 256 MB mmap 窗口，因此一个会扇出大量连接的工作流（编辑模型/知识库权限、重新加载长长的模型列表）会让 1 GB 容器 OOM-kill | 限制 `DATABASE_POOL_SIZE`（例如 `8`），设置 `DATABASE_SQLITE_PRAGMA_CACHE_SIZE=-2000` 和 `DATABASE_SQLITE_PRAGMA_MMAP_SIZE=0`，给容器 **≥2 GB** 内存。参见 [SQLite 内存占用](#5-sqlite-memory-footprint-on-constrained-containers) |
| **在生产环境长期保留 `GLOBAL_LOG_LEVEL=DEBUG`** | 追查问题时设置了一次却再也没有改回来。`DEBUG` 是最耗性能的级别：它新增的每一条消息都会被真正构造并写出，包括完整的对话请求负载，在每个请求上都是如此 → 除了日志量之外还白白浪费 CPU，而且提示词与用户内容就留在你的日志里 | 改回 `INFO`（默认值），或者在不消费这些信息行的繁忙实例上改为 `WARNING`。需要重启。参见[日志级别](#log-level) |

---

## 🔗 环境变量参考 {#environment-variable-references}
所有可用变量的完整说明，请参阅 [Environment Configuration](/reference/env-configuration)。

| 变量 | 说明与链接 |
| :--- | :--- |
| `TASK_MODEL` | [任务模型（本地）](/reference/env-configuration#task_model) |
| `TASK_MODEL_EXTERNAL` | [任务模型（外部）](/reference/env-configuration#task_model_external) |
| `TASK_MODEL_PARAMS` | [任务模型参数](/reference/env-configuration#task_model_params) |
| `ENABLE_BASE_MODELS_CACHE` | [缓存模型列表](/reference/env-configuration#enable_base_models_cache) |
| `MODELS_CACHE_TTL` | [模型缓存 TTL](/reference/env-configuration#models_cache_ttl) |
| `ENABLE_QUERIES_CACHE` | [查询缓存](/reference/env-configuration#enable_queries_cache) |
| `DATABASE_URL` | [数据库 URL](/reference/env-configuration#database_url) |
| `CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE` | [流式分块大小](/reference/env-configuration#chat_response_stream_delta_chunk_size) |
| `ENABLE_COMPRESSION_MIDDLEWARE` | [HTTP 响应压缩](/reference/env-configuration#enable_compression_middleware) |
| `ENABLE_ORJSON` | [JSON 编码器](/reference/env-configuration#enable_orjson) |
| `GLOBAL_LOG_LEVEL` | [日志级别](/reference/env-configuration#global_log_level) |
| `THREAD_POOL_SIZE` | [线程池大小](/reference/env-configuration#thread_pool_size) |
| `AIOHTTP_CLIENT_TIMEOUT` | [HTTP 客户端超时](/reference/env-configuration#aiohttp_client_timeout) |
| `AIOHTTP_CLIENT_ASYNC_DNS_RESOLVER` | [DNS 解析器](/reference/env-configuration#aiohttp_client_async_dns_resolver) |
| `RAG_EMBEDDING_ENGINE` | [嵌入引擎](/reference/env-configuration#rag_embedding_engine) |
| `CONTENT_EXTRACTION_ENGINE` | [内容提取引擎](/reference/env-configuration#content_extraction_engine) |
| `AUDIO_STT_ENGINE` | [STT 引擎](/reference/env-configuration#audio_stt_engine) |
| `BYPASS_PYDUB_PREPROCESSING` | [绕过 pydub 音频预处理](/reference/env-configuration#bypass_pydub_preprocessing) |
| `RAG_RERANKING_ENGINE` | [重排序引擎](/reference/env-configuration#rag_reranking_engine) |
| `RAG_EMBEDDING_BUFFER_SIZE` | [嵌入缓冲区大小](/reference/env-configuration#rag_embedding_buffer_size) |
| `VECTOR_DB` | [向量数据库](/reference/env-configuration#vector_db) |
| `ENABLE_AUTOCOMPLETE_GENERATION` | [自动补全](/reference/env-configuration#enable_autocomplete_generation) |
| `DATABASE_ENABLE_SESSION_SHARING` | [数据库会话共享](/reference/env-configuration#database_enable_session_sharing) |
| `DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL` | [在线状态写入节流](/reference/env-configuration#database_user_active_status_update_interval) |
| `DATABASE_POOL_SIZE` | [连接池大小](/reference/env-configuration#database_pool_size) |
| `DATABASE_SQLITE_PRAGMA_CACHE_SIZE` | [SQLite 页面缓存大小](/reference/env-configuration#database_sqlite_pragma_cache_size) |
| `DATABASE_SQLITE_PRAGMA_MMAP_SIZE` | [SQLite mmap 大小](/reference/env-configuration#database_sqlite_pragma_mmap_size) |
