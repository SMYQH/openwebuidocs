---
sidebar_position: 3
title: "在 Kubernetes 上使用 Helm 部署"
---

# 在 Kubernetes 上使用 Helm 部署 {#kubernetes-with-helm}

可在任意 Kubernetes 发行版（EKS、AKS、GKE、OpenShift、Rancher、自建集群）上，使用官方 Open WebUI Helm Chart 进行部署。

:::info 前置条件
继续前，请按[共享基础设施要求](/enterprise/deployment#shared-infrastructure-requirements)配置 PostgreSQL、Redis、向量数据库、共享存储和内容提取服务。
:::

## 何时选择这种模式 {#when-to-choose-this-pattern}

- 你的组织已经在运行 Kubernetes，并具备平台工程能力
- 你需要声明式基础设施即代码与 GitOps 工作流
- 你需要自动扩缩容（HPA）、声明式更新和 Pod Disruption Budget
- 你正在为数百到数千用户的关键任务环境部署

## 架构 {#architecture}

```mermaid
flowchart LR
    subgraph K8s["Kubernetes Cluster"]

        subgraph mgmt["Cluster Management"]
            Ingress["Ingress Controller"]
            HPA["HPA"]
        end

        subgraph genai["GenAI Namespace"]
            subgraph Deploy["Open WebUI Deployment"]
                P1["Pod 1"]
                P2["Pod 2"]
                P3["Pod N"]
            end
        end

        subgraph data["Data Namespace"]
            PG["PostgreSQL + PGVector"]
            Redis["Redis"]
            Storage["Shared Storage"]
            Tika["Tika"]
        end

    end

    Ingress --> Deploy
    HPA -.- Deploy
    Deploy --> data
```

## Helm Chart 配置 {#helm-chart-setup}

```bash
# Add the repository
helm repo add open-webui https://open-webui.github.io/helm-charts
helm repo update

# Install with custom values
helm install openwebui open-webui/open-webui -f values.yaml
```

在 `values.yaml` 中覆盖默认值，使部署连接到共享基础设施。Chart 为许多常见设置提供了专用配置项；如果有专用配置项，请优先使用，不要直接传入环境变量：

```yaml
# Example values.yaml overrides (refer to chart documentation for full schema)
replicaCount: 3

# -- Database: use an external PostgreSQL instance
databaseUrl: "postgresql://user:password@db-host:5432/openwebui"

# -- WebSocket & Redis: the chart can auto-deploy Redis in-cluster,
#    or you can point to an external Redis instance via websocket.url
websocket:
  enabled: true
  manager: redis
  # url: "redis://my-external-redis:6379/0"  # uncomment to use external Redis
  redis:
    enabled: true  # set to false if using external Redis

# -- Tika: the chart can auto-deploy Tika in-cluster
tika:
  enabled: true

# -- Ollama and Pipelines are deployed by default; disable what you do not use
ollama:
  enabled: false
pipelines:
  enabled: false

# -- Storage: use object storage instead of local PVC for multi-replica
persistence:
  provider: s3  # or "gcs" / "azure"
  s3:
    bucket: "my-openwebui-bucket"
    region: "us-east-1"
    accessKeyExistingSecret: "openwebui-s3-creds"
    accessKeyExistingAccessKey: "access-key"
    secretKeyExistingSecret: "openwebui-s3-creds"
    secretKeyExistingSecretKey: "secret-key"
  # -- Alternatively, use a shared filesystem (RWX PVC) instead of object storage:
  # provider: local
  # accessModes:
  #   - ReadWriteMany
  # storageClass: "efs-sc"

# -- Ingress: configure if exposing via an ingress controller
ingress:
  enabled: true
  class: "nginx"
  host: "ai.example.com"
  tls: true
  existingSecret: "openwebui-tls"

# -- Remaining settings that don't have dedicated chart values
extraEnvVars:
  - name: WEBUI_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: openwebui-secrets
        key: secret-key
  - name: VECTOR_DB
    value: "pgvector"  # uses DATABASE_URL unless PGVECTOR_DB_URL is set
  - name: UVICORN_WORKERS
    value: "1"
  - name: ENABLE_DB_MIGRATIONS
    value: "false"
  - name: RAG_EMBEDDING_ENGINE
    value: "openai"
```

## 扩展策略 {#scaling-strategy}

- **Horizontal Pod Autoscaler (HPA)**：基于 CPU 或内存利用率扩缩容。每个 Pod 保持 `UVICORN_WORKERS=1`，由 Kubernetes 管理副本数。
- **资源请求与限制**：设置合理的 CPU / 内存 request 和 limit，确保调度器正确放置 Pod，并使 HPA 获取准确指标。
- **Pod Disruption Budget**：配置 PDB，确保节点排空、集群升级等主动中断期间仍有规定数量的 Pod 保持可用。

## 更新流程 {#update-procedure}

:::danger 关键更新流程
绝不能让多个副本同时执行迁移，也绝不能让新旧版本同时访问同一个数据库。停止所有副本，用新版本启动一个副本并设置 `ENABLE_DB_MIGRATIONS=true`，等待其就绪，然后在关闭迁移的情况下重新扩容。Helm 回滚不会撤销迁移。完整的操作步骤和命令见[更新与恢复](/deployment/kubernetes#updates-and-recovery)。
:::

## 关键注意事项 {#key-considerations}

| 注意事项 | 说明 |
| :--- | :--- |
| **存储** | 上传文件应使用 **ReadWriteMany (RWX)** 共享文件系统（EFS、CephFS、NFS）或对象存储（S3、GCS、Azure Blob）。`ReadWriteOnce` 卷无法支持多 Pod。 |
| **密钥** | 凭证应存储在 Kubernetes Secrets 中，并通过 `secretKeyRef` 引用。对于 GitOps 工作流，可集成 External Secrets、Sealed Secrets 等外部密钥方案。 |
| **数据库** | 生产环境建议使用托管 PostgreSQL 服务（RDS、Cloud SQL、Azure DB）。集群内 PostgreSQL Operator（CloudNativePG、Zalando）虽可行，但会增加运维负担。 |
| **Redis** | 对于大多数部署，单个 Redis 实例配合 `timeout 1800` 和 `maxclients 10000` 已足够。只有当 Redis 本身也必须高可用时，才需要 Redis Sentinel 或 Cluster。 |
| **网络** | 将所有服务部署在同一可用区，目标是将数据库延迟控制在 2 ms 以下。审查网络策略，确保 Pod 能访问 PostgreSQL、Redis 和存储后端。 |

完整 Helm 配置指南请参阅 [Kubernetes 部署](/deployment/kubernetes)。多副本问题排查见 [多副本故障排查](/troubleshooting/multi-replica)。

---

**需要帮助规划企业部署？** 我们的团队正与全球组织合作，共同设计和落地生产级 Open WebUI 环境。

[**联系企业销售 →**](https://openwebui.com/contact/sales)
