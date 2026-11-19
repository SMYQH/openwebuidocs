---
sidebar_position: 1
title: "策略"
---

# 策略 {#policies}

策略定义如何配置用户的 Open Terminal 工作区，包括镜像、工具、资源、存储、环境变量、安全上下文和空闲超时。

可以把策略看作智能体工作区的配置模板。数据团队可以配备 Python、笔记本和更大的存储空间；培训实验室可以采用受严格限制的镜像和定时重置；软件团队可以配备 Git、构建工具、语言运行时和持久化文件。

在 Open WebUI 管理员区域打开**设置 > 集成**，在**终端**部分添加并验证编排器连接，然后编辑策略字段。

## 策略字段 {#policy-fields}

| 策略字段 | 示例 | 控制内容 |
| :--- | :--- | :--- |
| `image` | `ghcr.io/acme/open-terminal:python` | 用于新工作区的 Open Terminal 镜像 |
| `cpu_limit` | `2` 或 `500m` | 传递给 Docker/Kubernetes 的 CPU 限制 |
| `memory_limit` | `4Gi` | 传递给 Docker/Kubernetes 的内存限制 |
| `storage` | `10Gi` | Kubernetes 上的持久化文件存储；Docker 将文件存储在编排器数据目录下。Docker 无法保证严格执行上限：`StorageOpt` 只限制可写层，需要支持配额的驱动（例如在启用 `pquota` 的 XFS 上使用 overlay2）。通过绑定挂载提供的 `/home/user` 不受此限制。需要强制执行存储上限时，请使用 Kubernetes 后端 |
| `storage_mode` | `per-user` | Kubernetes 存储模式：`per-user`、`shared` 或 `shared-rwo` |
| `env` | `OPENAI_API_KEY=sk-...` | 注入到用户工作区的原始环境变量 |
| `idle_timeout_minutes` | `30` | 工作区被停止和移除前的空闲时间 |
| `restricted` | `true` | 在受限安全上下文下运行（Kubernetes/OpenShift 后端） |
| `pod_security_context` | `{"fsGroup": 1000}` | Kubernetes Pod `securityContext` 覆盖（Kubernetes/OpenShift 后端） |
| `container_security_context` | `{"runAsNonRoot": true}` | Kubernetes 容器 `securityContext` 覆盖（Kubernetes/OpenShift 后端） |

所有字段都是可选的。如果省略某个字段，编排器使用其全局默认值，例如 `TERMINALS_IMAGE` 或 `TERMINALS_KUBERNETES_STORAGE_MODE`。

策略变更在工作区新预配时应用。正在运行的现有工作区保留其当前镜像和环境，直到它们被停止、刷新或被空闲超时清理。Open WebUI 是此策略状态的管理客户端；Terminals 仍然是策略和生命周期配置的权威来源。

请在策略的生命周期设置中配置定时重置，而不是在上述策略字段中配置。这样可以将工作区预配与日常维护分开。
