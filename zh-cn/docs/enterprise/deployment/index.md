---
sidebar_position: 3
title: "部署选项"
---

# 可扩展的企业部署选项 {#scalable-enterprise-deployment-options}

Open WebUI 的**无状态、容器优先架构**意味着：无论你把它部署为虚拟机上的 Python 进程、托管容器服务中的容器，还是 Kubernetes 集群中的 Pod，本质上运行的都是同一个应用。不同部署模式之间的差异，在于你如何**编排、扩展和运维**它，而不是应用本身的行为发生改变。

:::tip 模型推理是独立维度
LLM 模型如何提供服务，与 Open WebUI 如何部署是两个独立问题。无论采用哪种部署模式，你都可以使用**托管 API**（OpenAI、Anthropic、Azure OpenAI、Google Gemini）或**自托管推理**（Ollama、vLLM）。关于模型接入方式，详见[集成](/enterprise/integration)。
:::

:::info 主权 AI 规划
对于主权 AI 部署，在选择运行时模式之前，请先定义四个边界：部署边界、模型边界、身份边界和数据边界。[主权 AI 平台](/enterprise/sovereign-ai)指南将这些决策映射到相应的 Open WebUI 控制项。
:::

---

## 共享基础设施要求 {#shared-infrastructure-requirements}

无论你选择哪一种部署模式，任何需要扩展的 Open WebUI 部署都依赖同一组后端服务。在从单实例扩展之前，请先完成这些基础设施配置。

| 组件 | 为什么必需 | 可选方案 |
| :--- | :--- | :--- |
| **PostgreSQL** | 多实例部署必须使用真正的数据库。SQLite 不支持多个进程并发写入。 | 自托管、Amazon RDS、Azure Database for PostgreSQL、Google Cloud SQL |
| **Redis** | 用于会话管理、WebSocket 协调和实例间配置同步。 | 自托管、Amazon ElastiCache、Azure Cache for Redis、Google Memorystore |
| **向量数据库** | 默认 ChromaDB 使用本地 SQLite 后端，不适合多进程访问。 | PGVector（复用 PostgreSQL）、Milvus、Qdrant，或 HTTP Server 模式的 ChromaDB |
| **共享存储** | 上传文件必须能被所有实例访问。 | 共享文件系统（NFS、EFS、CephFS）或对象存储（`S3`、`GCS`、`Azure Blob`） |
| **内容提取** | 默认 `pypdf` 提取器在持续负载下会发生内存泄漏。 | 以 Sidecar 方式运行 Apache Tika 或 Docling |
| **Embedding 引擎** | 默认 SentenceTransformers 模型会为每个 worker 进程加载约 500 MB 内存。 | OpenAI Embeddings API，或运行 embedding 模型的 Ollama |

### 关键配置 {#critical-configuration}

以下环境变量**必须**在所有实例中保持一致：

``` bash
# 共享密钥 —— 所有实例必须完全一致
WEBUI_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/openwebui

# Vector Database（PGVector 默认使用 DATABASE_URL，除非设置了 PGVECTOR_DB_URL）
VECTOR_DB=pgvector

# Redis
REDIS_URL=redis://redis-host:6379/0
WEBSOCKET_MANAGER=redis

# Content Extraction
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://tika:9998

# Embeddings
RAG_EMBEDDING_ENGINE=openai

# 存储 —— 二选一：
# 方案 A：共享文件系统（为所有实例挂载同一个卷，无需额外环境变量）
# 方案 B：对象存储（所有所需变量见 https://docs.openwebui.com/reference/env-configuration#cloud-storage）
# STORAGE_PROVIDER=s3

# Workers —— 让编排器负责扩缩容
UVICORN_WORKERS=1

# 数据库迁移 —— 只能有一个实例负责执行迁移
ENABLE_DB_MIGRATIONS=false
```

:::warning 数据库迁移
除一个实例外，**所有实例**都应设置 `ENABLE_DB_MIGRATIONS=false`。更新时，先缩容到单实例，等待迁移完成，再重新扩容。并发迁移可能损坏数据库。

即使你的平台提供了滚动部署能力，也不支持跨越会改变 schema 的发布进行滚动更新：每个实例都必须同时升到新版本，而旧实例和新实例绝不能同时对同一个数据库提供服务。开始前请先备份数据库。参见[更新与迁移](/troubleshooting/multi-replica#updates-and-migrations)。
:::

如需完整的逐步扩展指南，请参阅 [扩展 Open WebUI](/getting-started/advanced-topics/scaling)。完整环境变量参考见 [环境变量配置](/reference/env-configuration)。

---

## 选择你的部署模式 {#choose-your-deployment-pattern}

Open WebUI 支持三种生产级部署模式。每份指南都涵盖该模式对应的架构、扩展策略和关键注意事项。

### [自动扩缩容虚拟机上的 Python / Pip](./python-pip) {#python--pip-on-auto-scaling-vms}

将 `open-webui serve` 以 systemd 管理的进程形式，部署在云自动扩缩容虚拟机组（AWS ASG、Azure VMSS、GCP MIG）中。适合已经具备 VM 基础设施和较强 Linux 运维能力的团队，或受监管要求必须进行操作系统层直接控制的场景。

### [容器服务](./container-service) {#container-service}

在 AWS ECS/Fargate、Azure Container Apps、Google Cloud Run 等托管平台上运行官方 Open WebUI 容器镜像。适合希望获得容器优势（不可变镜像、版本化部署、无需管理操作系统），但又不想引入 Kubernetes 复杂度的团队。

### [使用 Helm 的 Kubernetes](./kubernetes-helm) {#kubernetes-with-helm}

在任意 Kubernetes 发行版（EKS、AKS、GKE、OpenShift、Rancher、自建集群）上使用官方 Open WebUI Helm Chart 部署。适合需要声明式基础设施、进阶自动扩缩容与 GitOps 工作流的大规模关键任务级场景。

---

## 部署模式对比 {#deployment-comparison}

| | **Python / Pip（VM）** | **容器服务** | **Kubernetes（Helm）** |
| :--- | :--- | :--- | :--- |
| **运维复杂度** | 中等 —— 需管理 OS 补丁和 Python 运行环境 | 低 —— 容器由平台托管 | 较高 —— 需要 K8s 专业能力 |
| **自动扩缩容** | 云 ASG/VMSS + 健康检查 | 平台原生，配置较少 | HPA，控制更精细 |
| **容器隔离** | 无 —— 进程直接运行在 OS 上 | 完整容器隔离 | 完整容器 + namespace 隔离 |
| **滚动更新** | 手动（缩容、更新、再扩容） | 平台托管滚动部署 | 声明式滚动更新，并支持回滚 |
| **基础设施即代码** | Terraform/Pulumi + 配置管理 | 任务/服务定义（CloudFormation、Bicep、Terraform） | Helm Chart + GitOps（Argo CD、Flux） |
| **最适用场景** | 以虚拟机为核心的团队，或受监管限制的环境 | 想要容器收益但不想承担 K8s 复杂度的团队 | 大规模、关键任务级部署 |
| **团队最低能力要求** | Linux 运维、Python | 容器基础、云平台 | Kubernetes、Helm、云原生模式 |

---

## 可观测性 {#observability}

无论采用哪种部署模式，生产环境都应具备监控与可观测性。

### 健康检查 {#health-checks}

- **`/health`** —— 基础存活检查。应用正常运行时返回 HTTP 200。可用于负载均衡器和自动扩缩容健康检查。
- **`/ready`** —— 就绪检查。在启动完成、且数据库与 Redis（如果已配置）响应 ping 之前返回 503。用于就绪探测和负载均衡器健康检查。
- **`/api/models`** —— 列出调用者可用的模型。当模型后端不可达时它仍会返回 200，因此并不能证明后端的健康状况。需要已认证的用户令牌；只有管理员启用 API 密钥后（`ENABLE_API_KEYS`，默认关闭），API 密钥才可用。

### OpenTelemetry {#opentelemetry}

Open WebUI 支持使用 **OpenTelemetry** 进行分布式追踪和 HTTP 指标采集。启用方式如下：

```bash
ENABLE_OTEL=true
ENABLE_OTEL_TRACES=true
ENABLE_OTEL_METRICS=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317
OTEL_EXPORTER_OTLP_INSECURE=true
OTEL_SERVICE_NAME=open-webui
```

它会自动为 FastAPI、SQLAlchemy、Redis 和 HTTP 客户端注入观测能力，从而帮助你了解请求延迟、数据库查询性能和跨服务链路。单独设置 `ENABLE_OTEL` 不会导出任何数据：每种信号都有各自的开关（日志对应 `ENABLE_OTEL_LOGS`）。导出器默认使用 gRPC 传输 OTLP，这也是端点使用 4317 端口的原因。当收集器的 gRPC 端口没有 TLS 时，请设置 `OTEL_EXPORTER_OTLP_INSECURE=true`；Open WebUI 会显式传递该标志，因此仅把端点写成 `http://` 并不会关闭 TLS。若要改用 HTTP 收集器，请设置 `OTEL_OTLP_SPAN_EXPORTER=http` 并给出完整的信号 URL，例如 `http://your-collector:4318/v1/traces`（以及分别以 `/v1/metrics` 和 `/v1/logs` 结尾的 `OTEL_METRICS_EXPORTER_OTLP_ENDPOINT` 和 `OTEL_LOGS_EXPORTER_OTLP_ENDPOINT`），因为 Open WebUI 会把端点原样传给导出器。

### 结构化日志 {#structured-logging}

启用 JSON 格式日志，以便接入 Datadog、Loki、CloudWatch、Splunk 等日志平台：

```bash
LOG_FORMAT=json
GLOBAL_LOG_LEVEL=INFO
```

完整监控配置详情请参阅 [监控](/reference/monitoring) 和 [OpenTelemetry](/reference/monitoring/otel)。

---

## 下一步 {#next-steps}

- **[架构与高可用性](/enterprise/architecture)** —— 深入了解 Open WebUI 的无状态设计与高可用能力。
- **[安全](/enterprise/security)** —— 合规框架、SSO/LDAP 集成、RBAC 与审计日志。
- **[集成](/enterprise/integration)** —— 连接 AI 模型、Pipeline，并扩展平台能力。
- **[扩展 Open WebUI](/getting-started/advanced-topics/scaling)** —— 完整的逐步技术扩展指南。
- **[多副本故障排查](/troubleshooting/multi-replica)** —— 多副本扩展部署中的常见问题解决方案。

---

**需要帮助规划企业部署？** 我们的团队正与全球组织合作，共同设计和落地生产级 Open WebUI 环境。

[**联系企业销售 →**](https://openwebui.com/contact/sales)
