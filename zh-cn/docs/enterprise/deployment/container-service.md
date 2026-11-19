---
sidebar_position: 2
title: "容器服务"
---

# 容器服务 {#container-service}

在 AWS ECS/Fargate、Azure Container Apps 或 Google Cloud Run 等托管容器平台上运行官方 `ghcr.io/open-webui/open-webui` 镜像。

:::info 前置条件
继续前，请按[共享基础设施要求](/enterprise/deployment#shared-infrastructure-requirements)配置 PostgreSQL、Redis、向量数据库、共享存储和内容提取服务。
:::

## 何时选择这种模式 {#when-to-choose-this-pattern}

- 你希望获得容器的优势（不可变镜像、版本化部署、无需管理操作系统），但不想引入 Kubernetes 复杂度
- 你的组织已经在使用托管容器平台
- 你需要以较低运维开销实现快速扩缩容
- 你更偏好平台原生自动扩缩容的托管基础设施

## 架构 {#architecture}

```mermaid
flowchart TB
    LB["Load Balancer"]

    subgraph CS["Container Service"]
        T1["Container Task 1"]
        T2["Container Task 2"]
        T3["Container Task N"]
    end

    subgraph Backend["Managed Backing Services"]
        PG["PostgreSQL + PGVector"]
        Redis["Redis"]
        S3["Object Storage"]
        Tika["Tika"]
    end

    LB --> CS
    CS --> Backend
```

## 镜像选择 {#image-selection}

为保证生产稳定性，请使用**版本号 tag**：

```
ghcr.io/open-webui/open-webui:v0.x.x
```

请避免在生产环境中使用滚动更新的 `:main` 和 `:latest` tag；请从 [Open WebUI 发布版本](https://github.com/open-webui/open-webui/releases)中固定一个 `v0.x.y` tag。配合 PostgreSQL、PGVector、S3 存储以及外部的嵌入与提取服务，`v0.x.y-slim` 变体已经足够，而且体积小得多。参见[镜像变体](/getting-started/quick-start#image-variants)。

## 扩展策略 {#scaling-strategy}

- **平台原生自动扩缩容**：按 CPU 利用率、内存或请求数配置扩缩容规则。
- **健康检查**：用 `/health` 做存活检查，用 `/ready` 做就绪检查；`/ready` 会等待启动完成，并检查数据库和 Redis 的连通性。
- **任务级环境变量**：在任务定义中通过环境变量或密钥传入所有共享基础设施配置。
- **会话亲和性**：仅在 `ENABLE_WEBSOCKET_SUPPORT=false` 时必需，其余情况下可选。参见[会话亲和性](/troubleshooting/multi-replica#session-affinity-sticky-sessions)。设置 `WEBSOCKET_MANAGER=redis` 后，无论是否启用会话亲和性，Redis 都会在实例之间传递实时更新。

## 关键注意事项 {#key-considerations}

| 注意事项 | 说明 |
| :--- | :--- |
| **存储** | 使用对象存储（S3、GCS、Azure Blob）或共享文件系统（例如 EFS）。容器本地存储是临时性的，且不会在任务间共享。 |
| **Tika Sidecar** | 可将 Tika 作为同一任务定义中的 sidecar 容器运行，或作为独立服务运行。采用 sidecar 模式时，提取流量不会离开该任务。 |
| **密钥管理** | 对于 `DATABASE_URL`、`REDIS_URL` 和 `WEBUI_SECRET_KEY`，请使用平台提供的密钥管理器（AWS Secrets Manager、Azure Key Vault、GCP Secret Manager）。 |
| **更新** | 将服务缩减到单个任务，在其上部署新镜像（`ENABLE_DB_MIGRATIONS=true`），等待其变为健康状态，然后将其余任务重新扩容（`ENABLE_DB_MIGRATIONS=false`）。在更改数据库架构的版本之间不支持滚动更新，因此新旧任务绝不能同时承载流量。参见[更新与迁移](/troubleshooting/multi-replica#updates-and-migrations)。 |

## 需要避免的反模式 {#anti-patterns-to-avoid}

| 反模式 | 影响 | 修复方式 |
| :--- | :--- | :--- |
| 使用本地 SQLite | 任务重启即丢数据，多任务时会出现数据库锁 | 将 `DATABASE_URL` 设置为 PostgreSQL |
| 使用默认 ChromaDB | 基于 SQLite 的向量数据库在多进程访问下容易崩溃 | 设置 `VECTOR_DB=pgvector`（或 Milvus/Qdrant） |
| `WEBUI_SECRET_KEY` 不一致 | 登录循环、401 错误、会话无法跨任务保持 | 通过密钥管理器为所有任务设置同一密钥 |
| 未配置 Redis | WebSocket 失败、“Model Not Found” 错误 | 设置 `REDIS_URL` 和 `WEBSOCKET_MANAGER=redis` |

容器基础部署可参考 [快速入门指南](/getting-started/quick-start)。

---

**需要帮助规划企业部署？** 我们的团队正与全球组织合作，共同设计和落地生产级 Open WebUI 环境。

[**联系企业销售 →**](https://openwebui.com/contact/sales)
