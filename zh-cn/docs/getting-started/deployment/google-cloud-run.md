---
slug: /deployment/google-cloud-run
sidebar_position: 4
title: "Google Cloud Run"
description: "在 Google Cloud Run 上部署 Open WebUI，配合 Cloud SQL、Redis、Cloud 存储与独立的迁移作业。"
---

# 在 Google Cloud Run 上部署 Open WebUI {#open-webui-on-google-cloud-run}

本指南使用 Cloud Run 作为 Google Cloud 的托管容器方案。请使用共享的外部状态与独立的迁移作业。对于 GKE，请参阅 [Kubernetes 部署](./kubernetes)；通用架构参见已有的[容器服务指南](/enterprise/deployment/container-service)。

:::info 检查负载适配性
Cloud Run 支持 WebSocket，但连接仍受其请求超时限制，最长可达 60 分钟。客户端必须能够重连，实例之间也仍然需要 Redis。引入该平台前请先测试长会话与后台任务。参见 [Cloud Run WebSocket](https://docs.cloud.google.com/run/docs/triggering/websockets)。
:::

## 1. 准备 Google Cloud 服务 {#1-prepare-the-google-cloud-services}

| 组件 | 创建服务前需要准备 |
| :--- | :--- |
| 镜像 | 将 `ghcr.io/open-webui/open-webui:v0.13.0` 同步到 Artifact Registry 并保留其不可变 digest。请使用标准镜像：slim 镜像不包含 Cloud Storage 客户端。 |
| 数据库 | Cloud SQL for PostgreSQL、一个应用数据库/角色，并由管理员启用 `vector` 扩展。本指南使用私有 IP 的数据库连接。 |
| Redis | 一个兼容的 Memorystore 或其他 Redis 端点。将认证、TLS 与集群设置调整为与所选服务一致。 |
| 文件 | 一个私有 Cloud Storage 存储桶。 |
| 标识与密钥 | 一个专用服务账号，以及用于应用凭据的 Secret Manager 密钥。 |
| VPC 访问 | 直连 VPC 出口，或 Serverless VPC Access 连接器，用于访问私有数据库、Redis 与文档解析服务。 |
| 模型与文档解析 | 可访问的对话/嵌入 API，以及应用可以调用的 Tika 端点。 |
| 浏览器访问 | 一个经过批准的 HTTPS 主机名，以及浏览器身份验证/访问路径。 |

为所有后端服务配置防火墙规则、私有 DNS 与出口。如果全部流量都经由 VPC 路由，请为模型 API 与其他外部端点提供相应的 NAT 或私有访问。迁移作业应使用相同的网络配置。参见[直连 VPC 出口](https://docs.cloud.google.com/run/docs/configuring/vpc-direct-vpc)。

## 2. 配置服务标识与环境 {#2-configure-the-service-identity-and-environment}

授予服务账号访问指定 Secret Manager 密钥的权限，以及存储桶上所需的对象读/写/列出/删除权限。通过 Application Default Credentials 使用附带的服务标识访问 Cloud Storage；不要把下载的服务账号密钥打进镜像。

创建并映射以下密钥环境变量。固定密钥版本，以便部署使用一组已知的凭据；授予运行时标识对每个被引用密钥的访问权限。参见 [Cloud Run 密钥配置](https://docs.cloud.google.com/run/docs/configuring/services/secrets)。

| 环境变量 | 密钥值 |
| :--- | :--- |
| `WEBUI_SECRET_KEY` | 一个稳定的随机签名密钥，所有实例保持一致。使用 `openssl rand -hex 32` 生成一次即可。 |
| `DATABASE_URL` | PostgreSQL 连接 URL，并附带服务商要求的 TLS 参数。除非设置了 `PGVECTOR_DB_URL`，PGVector 也会使用它。 |
| `REDIS_URL` | Redis 连接 URL，包含所需的认证与 TLS 配置。除非设置了 `WEBSOCKET_REDIS_URL`，WebSocket 也会使用它。 |
| `OPENAI_API_KEY` | 对话提供方的 API 密钥。 |
| `RAG_OPENAI_API_KEY` | 嵌入提供方的 API 密钥。未设置时默认使用 `OPENAI_API_KEY`。 |
| `WEBUI_ADMIN_EMAIL` 与 `WEBUI_ADMIN_PASSWORD` | 空数据库的初始管理员凭据。请将密码保存在密钥库中。 |
| `LICENSE_KEY` | 可选，已签发的企业版许可证密钥。 |

配置以下非机密取值，并替换示例中的端点与存储桶：

```ini
WEBUI_URL=https://ai.example.com
UVICORN_WORKERS=1
ENABLE_DB_MIGRATIONS=false
ENABLE_OLLAMA_API=false
WEBSOCKET_MANAGER=redis
VECTOR_DB=pgvector
PGVECTOR_CREATE_EXTENSION=false
OPENAI_API_BASE_URL=https://models.example.com/v1
RAG_EMBEDDING_ENGINE=openai
RAG_EMBEDDING_MODEL=REPLACE_WITH_EMBEDDING_MODEL_ID
RAG_OPENAI_API_BASE_URL=https://embeddings.example.com/v1
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://REPLACE_WITH_PRIVATE_TIKA_ENDPOINT:9998
STORAGE_PROVIDER=gcs
GCS_BUCKET_NAME=REPLACE_WITH_BUCKET
```

Cloud Run 会设置 `PORT`；请把容器端口配置为 `8080`。Open WebUI 常规的容器入口点会监听该端口以及 `0.0.0.0`。

容器本地文件是临时的，并且会占用实例内存。请勿使用 SQLite、本地 ChromaDB 或 Cloud Storage FUSE 挂载来替代共享的数据库/向量后端。上传请使用应用的 Cloud Storage 存储提供方。

## 3. 使用 Cloud Run Job 初始化数据库 {#3-initialize-the-database-with-a-cloud-run-job}

创建一个名为 `openwebui-migrate` 的作业，使用固定的镜像、服务账号、密钥引用与 VPC 配置。把任务数设为 `1`、并行度 `1`、重试 `0`，并按预期迁移耗时设置任务超时；1800 秒可作为起点。

使用与服务相同的固定应用镜像。设置 `ENABLE_DB_MIGRATIONS=true`，并按如下方式覆盖容器命令：

| 字段 | 值 |
| :--- | :--- |
| 可执行文件 / 入口点 | `python` |
| 参数，拆分为两个独立值 | `-c` 与 `import open_webui.config` |

导入该模块会在上述标志为 true 时执行数据库结构迁移，并在失败时以错误退出。它是内部入口点而非稳定的迁移 CLI，因此在升级版本时请对照[迁移代码](https://github.com/open-webui/open-webui/blob/v0.13.0/backend/open_webui/config.py)重新确认。它负责初始化数据库结构；此后应用的正常启动会继续初始化运行时设置与管理员账户。

迁移容器需要相同的数据库连接、签名密钥、网络访问权限与镜像拉取权限。每次只运行一个执行实例，关闭自动重试，并确保所有使用该数据库的应用实例都已停止。只有在它成功退出且日志中没有迁移错误时才能继续。

运行一次作业执行并等待成功。作业必须退出；不要让它一直运行镜像默认的 Web 服务器命令。参见[创建 Cloud Run 作业](https://docs.cloud.google.com/run/docs/create-jobs)。

```bash
gcloud run jobs execute openwebui-migrate --region REGION --wait
```

**预期结果：** 一个已完成的任务，执行成功且迁移日志正常。把服务最大实例数限制为 1 并不能替代该作业：[Cloud Run 的实例上限可以被临时突破](https://docs.cloud.google.com/run/docs/configuring/max-instances)。

## 4. 创建 Cloud Run 服务 {#4-create-the-cloud-run-service}

在 Cloud Run 控制台中，使用相同的镜像、标识、VPC 访问与各项设置部署 `openwebui`。保持镜像默认入口点，并设置 `ENABLE_DB_MIGRATIONS=false`。

| 服务设置 | 初始值 |
| :--- | :--- |
| 容器端口 | `8080` |
| CPU / 内存 | 1 vCPU / 4 GiB；请实测后调整。 |
| 计费 / CPU | 按实例计费，CPU 在请求之外也可用。 |
| 实例数 | 最小 `1`，最大 `1`，直至验证通过。 |
| 并发 | 从 `20` 开始，并按真实的对话/摄取流量调整。 |
| 请求超时 | `3600` 秒；客户端仍需能够重连。 |
| 会话亲和性 | 可选；仅在 `ENABLE_WEBSOCKET_SUPPORT=false` 时必须开启。参见[会话亲和性](/troubleshooting/multi-replica#session-affinity-sticky-sessions)。 |
| 启动探针 | HTTP `/ready`，端口 `8080`，周期 10 秒，超时 5 秒，失败阈值 `24`。 |
| 存活探针 | HTTP `/health`，端口 `8080`，使用合适的间隔与失败阈值。 |

启动耗时需控制在 Cloud Run [支持的探针预算](https://docs.cloud.google.com/run/docs/configuring/healthchecks)之内。在独立服务中计算嵌入向量，并用单独的作业执行迁移，可以减少启动时的工作量。探针成功并不能验证模型提供方或存储桶权限。

按实例计费与最小实例可以支撑活跃请求之外的工作，但实例仍可能被终止。它们不能让进程内的后台任务持久执行。参见 [Cloud Run 计费设置](https://docs.cloud.google.com/run/docs/configuring/billing-settings)。

请显式选择浏览器访问方式。Cloud Run 的 IAM 身份验证需要 Google 身份令牌；Open WebUI 的登录并不满足这一外层认证。请使用你组织的面向浏览器的身份网关，或仅在应用认证与网络暴露满足你策略的前提下才有意配置公开调用。切勿仅为绕过 Cloud Run 访问错误而关闭 Open WebUI 身份验证。

查看服务与日志：

```bash
gcloud run services describe openwebui --region REGION \
  --format='value(status.url,status.latestReadyRevisionName)'
gcloud run services logs read openwebui --region REGION --limit=50
```

打开经过批准的 HTTPS 主机名，并使用初始管理员凭据登录。验证通过后即可提高实例上限，同时为共享数据库连接预留预算，并测试跨实例的 WebSocket 重连。

## 添加用户前的验证 {#verify-before-adding-users}

- 使用初始管理员账户登录，确认开放注册已关闭（用 `WEBUI_ADMIN_EMAIL` 和 `WEBUI_ADMIN_PASSWORD` 创建管理员会关闭它）。在放开更多访问权限前，请先配置你的[身份提供方](/features/authentication-access/auth/sso)。
- 选择一个模型并以流式方式获取响应，然后重新打开已保存的会话。
- 上传一份包含明显事实的小文档。确认索引完成，并就该事实提问以验证能够检索到来源。
- 替换一个应用实例，确认同一账户、会话与已上传文件依然可用。
- 在多实例场景下，通过真实入口测试重复请求与 WebSocket 重连，检查是否存在登录循环与状态不一致。

初始管理员环境变量仅在数据库中没有用户时创建账户；之后再修改这些变量不会重置其密码。请在初始化完成后在应用内轮换初始密码。许多应用设置在首次启动后会持久化保存；在期待通过修改环境变量来替换已保存的设置之前，请先阅读[配置持久化](/reference/env-configuration#important-note-on-configvar-environment-variables)。

对于企业部署，许可证状态需与服务健康状况分开验证。应用设置与许可证的网络要求参见[许可与品牌](./kubernetes#enterprise-licensing-and-branding)；请通过该平台的密钥机制注入密钥，而不是使用 Kubernetes Secrets。

## 更新与恢复 {#updates-and-recovery}

在跨不兼容结构版本之间进行流量切分是不安全的。把某个修订版本的流量设为零，或把最小实例数设为零，都不能证明旧容器已经停止。

对于涉及结构变更的版本，请使用维护窗口并遵循以下保守流程：

1. 导出服务配置与 IAM 策略，记录你的域名/访问配置，并暂停部署自动化。阻断新请求并排空活动连接。
2. 删除 **Cloud Run 应用服务**，使旧修订版本无法再被调用；并在迁移前确认旧的应用数据库连接已排空。保留数据库、存储桶、密钥与迁移作业。为重建后的服务保留一个稳定的自定义主机名。
3. 协调完成数据库/存储备份，并保留签名密钥。
4. 把迁移作业更新到新镜像，并运行一次执行直至成功完成。
5. 使用新镜像重建服务，关闭迁移，并恢复已保存的网络、密钥、扩缩容、IAM 与入口设置。仅在验证服务之后再恢复域名路由。

例如，在删除 Cloud Run 服务**之前**先导出服务配置和 IAM 配置：

```bash
gcloud run services describe openwebui --region REGION \
  --format=export > openwebui-service.yaml
gcloud run services get-iam-policy openwebui --region REGION \
  --format=yaml > openwebui-iam.yaml
```

导出并不能替代数据库备份，IAM/域名设置也必须单独恢复。该流程会产生停机并重建服务；如果这种运维模式不适合你，请考虑使用 GKE 或具备明确停止应用进程能力的虚拟机/容器平台。

迁移完成后请勿再路由到不兼容的旧镜像。必要时恢复兼容的数据库/存储状态；参见[备份与恢复](/getting-started/updating#backup--restore)。

## 故障排查与移除 {#troubleshooting-and-removal}

| 现象 | 检查项 |
| :--- | :--- |
| 服务在登录页之前返回 403 | Cloud Run 的 IAM/入口策略与浏览器的访问路径。 |
| 启动失败 | 端口、启动预算、数据库私有 IP 路由/TLS、密钥权限与日志。 |
| Redis 无法连接 | VPC 出口、防火墙/DNS、认证/TLS，以及 Redis 集群模式。 |
| 文件消失或上传失败 | `STORAGE_PROVIDER=gcs`、存储桶名称、服务账号权限，以及外部向量存储。 |
| 长会话后 WebSocket 断开 | 请求超时与客户端重连。 |
| 后台任务暂停或消失 | CPU 分配、最小实例数与进程终止；对于必须在实例终止后继续执行的工作，请使用持久化的作业基础设施。 |

删除 Cloud Run 服务或作业不会删除单独创建的 Cloud SQL、Redis、Cloud Storage 或 Secret Manager 资源。请仅依据你的备份与保留策略删除这些资源。
