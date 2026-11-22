---
slug: /deployment/azure-container-apps
sidebar_position: 3
title: "Azure 容器应用"
description: "在 Azure 容器应用上部署 Open WebUI，配合 PostgreSQL、Redis、Blob 存储与托管密钥。"
---

# 在 Azure 容器应用上部署 Open WebUI {#open-webui-on-azure-container-apps}

Azure 容器应用让你无需运维 Kubernetes 即可运行本应用。本指南使用 Azure 门户来配置应用以及一个单独的手动迁移作业。对于 AKS，请参阅 [Kubernetes 部署](./kubernetes)。

共享架构参见已有的[容器服务指南](/enterprise/deployment/container-service)。下面的应用设置针对 **Open WebUI v0.13.0**。

## 1. 准备 Azure 服务 {#1-prepare-the-azure-services}

| 组件 | 创建应用前需要准备 |
| :--- | :--- |
| 镜像 | 将带版本的标准镜像（`ghcr.io/open-webui/open-webui:v0.13.0`）同步到 Azure 容器注册表，并保留其不可变 digest。slim 镜像不包含 Azure Blob 客户端。 |
| 容器应用环境 | 一个具备后端服务所需 VNet 连通性、DNS、出口与私有端点访问能力的环境。 |
| 数据库 | Azure Database for PostgreSQL 灵活服务器、一个应用数据库/角色，并由管理员启用 `vector` 扩展。 |
| Redis | 一个兼容的 Redis 端点，例如 [Azure 托管 Redis](https://learn.microsoft.com/en-us/azure/redis/overview)。请确认其集群模式、认证与 TLS 设置。 |
| 文件 | 一个 Blob 存储账户，以及一个用于应用上传的私有容器。 |
| 密钥 | Key Vault，以及一个有权读取应用密钥的标识。 |
| 模型与文档解析 | 可访问的对话/嵌入 API，以及一个私有的 Tika 服务。 |
| 浏览器访问 | 一个经过批准的 HTTPS 主机名，以及访问该应用的路径。 |

如果所选端点使用 Redis Cluster，请设置 `REDIS_CLUSTER=true`（除非设置了 `WEBSOCKET_REDIS_CLUSTER`，WebSocket 也会遵循该设置）。请根据所选端点参考 [Redis 配置](/reference/env-configuration#redis_url)。容器应用的本地文件系统是临时的；请勿将其用于 SQLite 或持久化文件存储。

## 2. 配置凭据与环境变量 {#2-configure-credentials-and-environment-values}

在 Key Vault 中存储下列凭据。使用容器应用机密引用获取这些凭据，并为其托管标识授予读取 Key Vault 机密的权限。该标识还需要相应的镜像拉取权限。参见[容器应用机密与 Key Vault 引用](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets)。

| 环境变量 | 密钥值 |
| :--- | :--- |
| `WEBUI_SECRET_KEY` | 一个稳定的随机签名密钥，所有实例保持一致。使用 `openssl rand -hex 32` 生成一次即可。 |
| `DATABASE_URL` | PostgreSQL 连接 URL，并附带服务商要求的 TLS 参数。除非设置了 `PGVECTOR_DB_URL`，PGVector 也会使用它。 |
| `REDIS_URL` | Redis 连接 URL，包含所需的认证与 TLS 配置。除非设置了 `WEBSOCKET_REDIS_URL`，WebSocket 也会使用它。 |
| `OPENAI_API_KEY` | 对话提供方的 API 密钥。 |
| `RAG_OPENAI_API_KEY` | 嵌入提供方的 API 密钥。未设置时默认使用 `OPENAI_API_KEY`。 |
| `WEBUI_ADMIN_EMAIL` 与 `WEBUI_ADMIN_PASSWORD` | 空数据库的初始管理员凭据。请将密码保存在密钥库中。 |
| `LICENSE_KEY` | 可选，已签发的企业版许可证密钥。 |

如果你使用账户密钥，请另外把 `AZURE_STORAGE_KEY` 存为密钥。不设置它时，Open WebUI 会用 `DefaultAzureCredential` 向 Blob 存储进行身份验证，因此只要 Container App 的托管标识在存储账户上拥有 Blob 数据角色，它就能正常工作；仅对 Key Vault 的托管标识访问并不会授予该角色。

在应用配置中把每个密钥映射到对应的环境变量。请替换下面的非机密取值：

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
STORAGE_PROVIDER=azure
AZURE_STORAGE_ENDPOINT=https://REPLACE_ACCOUNT.blob.core.windows.net
AZURE_STORAGE_CONTAINER_NAME=openwebui
```

**预期结果：** 环境中包含全部端点设置与密钥引用，并在各副本之间共享同一个稳定的签名密钥。镜像与部署配置中不会出现真实密码或密钥。

## 3. 运行手动迁移作业 {#3-run-a-manual-migration-job}

在创建服务应用之前，先在同一环境中创建一个 **Container Apps Job**。让它访问相同的镜像、网络、标识与数据库密钥。

| 作业设置 | 值 |
| :--- | :--- |
| 触发器类型 | 手动 |
| 并行度 | `1` |
| 副本完成数 | `1` |
| 副本重试上限 | `0` |
| 副本超时 | 先从 1800 秒开始；更长的迁移请在运行前评估。 |
| CPU / 内存 | 先从 1 vCPU / 2 GiB 开始。 |

使用与服务相同的固定应用镜像。设置 `ENABLE_DB_MIGRATIONS=true`，并按如下方式覆盖容器命令：

| 字段 | 值 |
| :--- | :--- |
| 可执行文件 / 入口点 | `python` |
| 参数，拆分为两个独立值 | `-c` 与 `import open_webui.config` |

导入该模块会在上述标志为 true 时执行数据库结构迁移，并在失败时以错误退出。它是内部入口点而非稳定的迁移 CLI，因此在升级版本时请对照[迁移代码](https://github.com/open-webui/open-webui/blob/v0.13.0/backend/open_webui/config.py)重新确认。它负责初始化数据库结构；此后应用的正常启动会继续初始化运行时设置与管理员账户。

迁移容器需要相同的数据库连接、签名密钥、网络访问权限与镜像拉取权限。每次只运行一个执行实例，关闭自动重试，并确保所有使用该数据库的应用实例都已停止。只有在它成功退出且日志中没有迁移错误时才能继续。

启动一次执行并等待其状态变为 **Succeeded**，同时查看执行日志。请勿为该作业配置 HTTP 健康探针。参见 [Azure 容器应用作业](https://learn.microsoft.com/en-us/azure/container-apps/jobs)。

## 4. 创建服务容器应用 {#4-create-the-serving-container-app}

在同一环境中创建 `openwebui`，使用固定的镜像以及第 2 步中的环境变量/密钥映射。保持镜像默认命令；服务应用使用 `ENABLE_DB_MIGRATIONS=false`。

| 应用设置 | 初始值 |
| :--- | :--- |
| CPU / 内存 | 1 vCPU / 2 GiB，并根据实际负载调整。 |
| 修订版本模式 | 单修订版本。 |
| 扩缩容 | 最小 `1`，最大 `1`，直至验证通过。 |
| 入口 | HTTP，目标端口 `8080`，传输方式 `auto`，仅允许 HTTPS。请选择与环境的访问策略一致的暴露方式。 |
| 启动探针 | `8080` 上的 HTTP `/health`；请为实测启动时间留出余量。 |
| 就绪探针 | `8080` 上的 HTTP `/ready`。它在启动完成且数据库与 Redis 正常响应后返回结果。 |
| 存活探针 | `8080` 上的 HTTP `/health`。 |

请显式配置探针，不要依赖通用默认值。启动探针的初始预算可设为每 10 秒一次、共 60 次失败；探针超时设为 5 秒。实测启动时间与外部服务延迟后再调整。

容器应用的入口支持 WebSocket，而普通 HTTP 请求的超时为 240 秒。请通过真实入口测试长流式响应与文档处理。参见[入口行为](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)。仅在关闭 WebSocket（`ENABLE_WEBSOCKET_SUPPORT=false`）时才需要粘性会话；参见[会话亲和性要求](https://learn.microsoft.com/en-us/azure/container-apps/sticky-sessions)。

使用以下命令验证应用并跟踪日志：

```bash
az containerapp show --name openwebui --resource-group RESOURCE_GROUP \
  --query '{state:properties.provisioningState,fqdn:properties.configuration.ingress.fqdn}'
az containerapp logs show --name openwebui --resource-group RESOURCE_GROUP --follow
```

打开经过批准的 HTTPS 主机名，并使用初始管理员凭据登录。验证通过后即可提高最大副本数。此基线保持最小副本数为 1，并按最大副本数预留数据库连接数。最小副本数可以提升可用性，但无法让后台任务在重启后依然持久执行。

## 添加用户前的验证 {#verify-before-adding-users}

- 使用初始管理员账户登录，确认开放注册已关闭（用 `WEBUI_ADMIN_EMAIL` 和 `WEBUI_ADMIN_PASSWORD` 创建管理员会关闭它）。在放开更多访问权限前，请先配置你的[身份提供方](/features/authentication-access/auth/sso)。
- 选择一个模型并以流式方式获取响应，然后重新打开已保存的会话。
- 上传一份包含明显事实的小文档。确认索引完成，并就该事实提问以验证能够检索到来源。
- 替换一个应用实例，确认同一账户、会话与已上传文件依然可用。
- 在多实例场景下，通过真实入口测试重复请求与 WebSocket 重连，检查是否存在登录循环与状态不一致。

初始管理员环境变量仅在数据库中没有用户时创建账户；之后再修改这些变量不会重置其密码。请在初始化完成后在应用内轮换初始密码。许多应用设置在首次启动后会持久化保存；在期待通过修改环境变量来替换已保存的设置之前，请先阅读[配置持久化](/reference/env-configuration#important-note-on-configvar-environment-variables)。

对于企业部署，许可证状态需与服务健康状况分开验证。应用设置与许可证的网络要求参见[许可与品牌](./kubernetes#enterprise-licensing-and-branding)；请通过该平台的密钥机制注入密钥，而不是使用 Kubernetes Secrets。

## 更新与恢复 {#updates-and-recovery}

单修订版本模式并不是数据库迁移锁：Azure 通常会保留旧修订版本继续服务，直到替代版本就绪。参见[修订版本行为](https://learn.microsoft.com/en-us/azure/container-apps/revisions)。不要在普通的应用修订版本更新中启用启动时迁移。

1. 保存应用配置与活动修订版本列表。阻断新流量并暂停发布自动化。使用[修订版本管理](https://learn.microsoft.com/en-us/azure/container-apps/revisions-manage)停用**所有**应用修订版本，包括可通过标签访问到的修订版本，并确认其副本已终止。必要时切换到多修订版本模式以显式管理停用操作；新版本上线后再切回单修订版本模式。
2. 协调完成 PostgreSQL 与 Blob 存储备份，并保留签名密钥。
3. 把迁移作业更新到新镜像并运行一次手动执行。要求结果为 **Succeeded** 且迁移日志干净。
4. 使用同一镜像部署一个新的服务修订版本，并关闭迁移。在恢复流量与正常扩缩容之前，先验证已有数据、流式响应与上传功能。

在数据库结构迁移完成后，不要重新启用不兼容的旧修订版本。镜像回滚不会撤销数据库变更；必要时恢复兼容的数据库与存储状态。参见[备份与恢复](/getting-started/updating#backup--restore)。

## 故障排查与移除 {#troubleshooting-and-removal}

| 现象 | 检查项 |
| :--- | :--- |
| 镜像或密钥无法加载 | 注册表拉取权限、托管标识、Key Vault 权限，以及私有 DNS/出口。 |
| 修订版本未通过就绪检查 | 端口 `8080`、应用日志、PostgreSQL 的 TLS/登录、向量扩展，以及探针预算。 |
| Redis 连接失败 | TLS、认证、网络可达性，以及单机模式与集群模式的差异。 |
| 上传失败 | Blob 端点/容器、存储密钥或托管标识的 Blob 数据角色、账户网络规则，以及 Tika/嵌入端点。 |
| 流式响应或请求超时 | 入口请求限制、亲和性设置，以及客户端重连行为。 |

删除应用或迁移作业不会删除单独创建的 PostgreSQL、Blob 存储或 Key Vault 资源。在保留策略允许删除之前，请保留备份与凭据。
