---
slug: /deployment/aws-ecs
sidebar_position: 2
title: "AWS ECS / Fargate"
description: "在 AWS ECS 上使用 Fargate、共享数据服务、Secrets Manager 与应用负载均衡器部署 Open WebUI。"
---

# 在 AWS ECS / Fargate 上部署 Open WebUI {#open-webui-on-aws-ecs--fargate}

以 Fargate 上的 ECS 服务方式运行 Open WebUI。本指南假设你已在管理一个 AWS 账户与 VPC；它通过 ECS 控制台讲解应用设置与部署流程，并附带用于验证的 CLI 命令。

架构概览参见已有的[容器服务指南](/enterprise/deployment/container-service)。若使用 EKS 或其他 Kubernetes 集群，请参阅 [Kubernetes 部署](./kubernetes)。

## 1. 准备 AWS 服务 {#1-prepare-the-aws-services}

| 组件 | 创建服务前需要准备 |
| :--- | :--- |
| 容器镜像 | 将 `ghcr.io/open-webui/open-webui:v0.13.0-slim` 镜像同步到 ECR 并使用其不可变 digest。slim 变体支持本指南中的全部服务，并且不包含本地机器学习组件，参见 [slim](/getting-started/quick-start#what-slim-leaves-out)。镜像架构需与 Fargate 任务一致。 |
| ECS 与网络 | 一个 ECS 集群、私有子网与安全组。放行镜像拉取、密钥获取、日志投递、模型 API 以及后端服务连接。这些路径请使用 NAT 或相应的 VPC 端点。 |
| 数据库 | RDS PostgreSQL 或 Aurora PostgreSQL、一个应用数据库与角色，并由数据库管理员启用 `vector` 扩展。 |
| Redis | 一个 ElastiCache Redis 兼容端点或其他 Redis 服务。将 Open WebUI 的 Redis 模式与 TLS 设置调整为与实际服务一致。 |
| 文件 | 一个用于应用上传的 S3 存储桶。 |
| 模型与文档解析 | 可访问的对话与嵌入 API，以及一个私有的 Tika 服务。模型推理独立于 ECS 应用任务。 |
| HTTPS | 一个应用负载均衡器、HTTPS 监听器与证书、DNS 主机名，以及一个转发到 `8080` 端口的 **IP 类型**目标组。 |

使用任务安全组，仅允许负载均衡器向 `8080` 发起入站访问。根据组织的访问要求选择内部或面向互联网的负载均衡。Fargate 的 `awsvpc` 网络模式要求使用 IP 目标，参见 [ECS 与应用负载均衡器](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/alb.html)。

为任务的应用访问权限与 ECS 执行分别创建独立的 IAM 角色。**执行角色**需要镜像拉取、CloudWatch Logs 与密钥获取权限，必要时还需要 KMS 解密权限。**任务角色**需要相应的 S3 存储桶/对象权限。请使用任务角色凭据访问 S3，而不是把 AWS 访问密钥写进任务定义。执行侧权限参见 [ECS 任务执行角色](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html)。

## 2. 创建应用任务定义 {#2-create-the-application-task-definition}

在 ECS 控制台中创建一个名为 `openwebui` 的 Linux Fargate 任务定义：

| 设置项 | 初始值 |
| :--- | :--- |
| 网络模式 | `awsvpc` |
| 任务资源 | 1 vCPU 与 4 GiB 内存；请在测量负载后再调整。 |
| 容器名称 | `openwebui` |
| 镜像 | 你固定的 ECR 镜像 digest。 |
| 容器端口 | `8080/TCP` |
| 持久化文件系统 | 无；请使用外部数据库与 S3。 |
| 日志 | `awslogs`，搭配已存在的 CloudWatch 日志组与流前缀。 |
| 应用命令 | 保持镜像默认的入口点与命令。 |

设置以下非机密环境变量，并替换示例中的端点与存储桶：

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
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=REPLACE_WITH_BUCKET
S3_REGION_NAME=REPLACE_WITH_AWS_REGION
```

在 Secrets Manager 中创建凭据，并映射到容器的 **Secrets** 设置中：

| 环境变量 | 密钥值 |
| :--- | :--- |
| `WEBUI_SECRET_KEY` | 一个稳定的随机签名密钥，所有实例保持一致。使用 `openssl rand -hex 32` 生成一次即可。 |
| `DATABASE_URL` | PostgreSQL 连接 URL，并附带服务商要求的 TLS 参数。除非设置了 `PGVECTOR_DB_URL`，PGVector 也会使用它。 |
| `REDIS_URL` | Redis 连接 URL，包含所需的认证与 TLS 配置。除非设置了 `WEBSOCKET_REDIS_URL`，WebSocket 也会使用它。 |
| `OPENAI_API_KEY` | 对话提供方的 API 密钥。 |
| `RAG_OPENAI_API_KEY` | 嵌入提供方的 API 密钥。未设置时默认使用 `OPENAI_API_KEY`。 |
| `WEBUI_ADMIN_EMAIL` 与 `WEBUI_ADMIN_PASSWORD` | 空数据库的初始管理员凭据。请将密码保存在密钥库中。 |
| `LICENSE_KEY` | 可选，已签发的企业版许可证密钥。 |

环境变量名与密钥 ARN 是彼此独立的字段。例如，下面是任务定义中容器配置的一个片段：

```json
{
  "secrets": [
    {
      "name": "DATABASE_URL",
      "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:openwebui-database-SUFFIX"
    }
  ]
}
```

每个密钥变量都要重复上述配置；两个变量可以引用同一个密钥。通过环境变量注入的密钥在任务启动时读取，因此轮换密钥需要替换任务。参见 [ECS 密钥注入](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-tutorial.html)。

不要把 SQLite 或本地向量数据保存在任务的临时磁盘上。把一个已有数据的安装切换到 PostgreSQL 或 S3，并不会迁移其现有数据。

## 3. 使用一个独立任务初始化数据库 {#3-initialize-the-database-with-one-standalone-task}

复制应用任务定义，创建第二个任务定义族 `openwebui-migrate`。如果配置了 HTTP 健康检查，请将其移除，因为该任务会直接退出而不会提供 HTTP 服务。

使用与服务相同的固定应用镜像。设置 `ENABLE_DB_MIGRATIONS=true`，并按如下方式覆盖容器命令：

| 字段 | 值 |
| :--- | :--- |
| 可执行文件 / 入口点 | `python` |
| 参数，拆分为两个独立值 | `-c` 与 `import open_webui.config` |

导入该模块会在上述标志为 true 时执行数据库结构迁移，并在失败时以错误退出。它是内部入口点而非稳定的迁移 CLI，因此在升级版本时请对照[迁移代码](https://github.com/open-webui/open-webui/blob/v0.13.0/backend/open_webui/config.py)重新确认。它负责初始化数据库结构；此后应用的正常启动会继续初始化运行时设置与管理员账户。

迁移容器需要相同的数据库连接、签名密钥、网络访问权限与镜像拉取权限。每次只运行一个执行实例，关闭自动重试，并确保所有使用该数据库的应用实例都已停止。只有在它成功退出且日志中没有迁移错误时才能继续。

使用 **Run new task**，选择 Fargate，把任务数设为 `1`，并使用应用的子网与安全组，不挂载负载均衡器。独立任务不由 ECS 服务维护，参见[独立任务](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/standalone-tasks.html)。

**预期结果：** 任务状态变为 `STOPPED`，`openwebui` 容器的退出码为 `0`，日志显示迁移成功。仅凭 `STOPPED` 不能作为成功信号。

## 4. 创建 ECS 服务 {#4-create-the-ecs-service}

使用**应用**任务定义创建 ECS 服务，保持 `ENABLE_DB_MIGRATIONS=false` 与常规命令。先把期望任务数设为 `1`，并把 ALB 目标组连接到容器 `openwebui` 的 `8080` 端口。

把目标组的健康检查路径设置为 `/ready`，它在启动完成且数据库与 Redis 正常响应后返回结果。先把服务健康检查宽限期设为 300 秒，再根据实测启动时间调整。`/health` 用作独立的进程存活检查。模型 API 与 S3 权限需要通过[添加用户前的验证](#verify-before-adding-users)中的检查。

根据你的流式负载调整 ALB 空闲超时。目标组粘性会话是可选的，仅在 `ENABLE_WEBSOCKET_SUPPORT=false` 时才必须开启。参见[会话亲和性](/troubleshooting/multi-replica#session-affinity-sticky-sessions)。请通过 ALB 验证 WebSocket 与流式响应。

使用 AWS CLI 等待并查看服务事件，替换其中的标识符：

```bash
aws ecs wait services-stable --cluster CLUSTER --services openwebui
aws ecs describe-services --cluster CLUSTER --services openwebui \
  --query 'services[0].{running:runningCount,desired:desiredCount,events:events[0:5]}'
```

打开 `WEBUI_URL` 中配置的 HTTPS 主机名。初始管理员凭据会在启动过程中创建第一个账户。验证通过后即可提高期望任务数，并可选择配置 Service Auto Scaling。请为最大任务数预留 PostgreSQL 与 Redis 连接数。

## 添加用户前的验证 {#verify-before-adding-users}

- 使用初始管理员账户登录，确认开放注册已关闭。在放开更多访问权限前，请先配置你的[身份提供方](/features/authentication-access/auth/sso)。
- 选择一个模型并以流式方式获取响应，然后重新打开已保存的会话。
- 上传一份包含明显事实的小文档。确认索引完成，并就该事实提问以验证能够检索到来源。
- 替换一个应用实例，确认同一账户、会话与已上传文件依然可用。
- 在多实例场景下，通过真实入口测试重复请求与 WebSocket 重连，检查是否存在登录循环与状态不一致。

初始管理员环境变量仅在数据库中没有用户时创建账户；之后再修改这些变量不会重置其密码。请在初始化完成后在应用内轮换初始密码。许多应用设置在首次启动后会持久化保存；在期待通过修改环境变量来替换已保存的设置之前，请先阅读[配置持久化](/reference/env-configuration#important-note-on-configvar-environment-variables)。

对于企业部署，许可证状态需与服务健康状况分开验证。应用设置与许可证的网络要求参见[许可与品牌](./kubernetes#enterprise-licensing-and-branding)；请通过该平台的密钥机制注入密钥，而不是使用 Kubernetes Secrets。

## 更新与恢复 {#updates-and-recovery}

涉及结构变更的更新请在维护窗口内进行：

1. 保存已部署的任务定义与服务配置。阻断新流量，暂停服务自动扩缩容与部署自动化，把期望任务数设为零，并确认所有旧的应用任务都已停止。同时也要停止共享该数据库的独立任务。
2. 协调完成数据库与 S3 备份，并保留签名密钥。
3. 使用新镜像注册一个新的迁移任务修订版本。运行一个独立迁移任务，必须以退出码 `0` 结束才能继续。
4. 使用同一镜像注册应用任务修订版本，并关闭迁移。在期望任务数保持为零的状态下更新服务，然后恢复期望任务数并验证服务，再恢复流量与自动扩缩容。

ECS 回滚只更换镜像，不会回退数据库结构。不要在涉及结构变更时启用回滚到不兼容的旧应用版本；必要时恢复兼容的数据库/存储备份。参见[备份与恢复](/getting-started/updating#backup--restore)。

## 故障排查与移除 {#troubleshooting-and-removal}

| 现象 | 检查项 |
| :--- | :--- |
| 任务无法启动或拉取镜像 | 执行角色、ECR 权限、子网出口/VPC 端点、架构，以及 Secrets Manager 访问权限。 |
| ALB 报告目标不健康 | IP 目标类型、容器端口、任务安全组、`/ready`、启动日志，以及数据库与 Redis 连通性。 |
| 对话正常但上传失败 | 任务角色的 S3 权限、存储桶名称/区域，以及解析与嵌入端点。 |
| 跨任务出现登录循环 | 共享的签名密钥、公共数据库与统一的 Redis URL。 |
| 流式响应中断 | ALB 空闲超时、客户端重连与 Redis 模式。 |

删除 ECS 服务不会删除单独创建的 RDS、S3 或 Secrets Manager 资源。请依据你的保留策略有意识地清理资源；在移除持久化服务之前，保留可恢复的备份。