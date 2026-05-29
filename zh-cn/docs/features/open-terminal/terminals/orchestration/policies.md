---
sidebar_position: 1
title: "策略"
---

# 策略

策略描述用户 Open Terminal 容器应该是什么样子。它控制镜像、资源、存储、环境变量和空闲超时。

在 Open WebUI 中，进入**管理面板 → 设置 → 集成 → Open Terminal**，添加编排器连接，验证它，然后编辑策略字段。

## 策略字段

| 策略字段 | 示例 | 控制内容 |
| :--- | :--- | :--- |
| `image` | `ghcr.io/acme/open-terminal:python` | 用于新容器的 Open Terminal 镜像 |
| `cpu_limit` | `2` 或 `500m` | 传递给 Docker/Kubernetes 的 CPU 限制 |
| `memory_limit` | `4Gi` | 传递给 Docker/Kubernetes 的内存限制 |
| `storage` | `10Gi` | Kubernetes 上的持久化文件存储；Docker 将文件存储在编排器数据目录下。在 Docker 上，上限是尽力而为：仅通过 `StorageOpt` 限制可写层，需要支持配额功能的驱动（带 `pquota` 的 overlay2 on XFS），并且 `/home/user` 是绑定挂载的，不受配额限制。使用 Kubernetes 后端获得硬存储上限 |
| `storage_mode` | `per-user` | Kubernetes 存储模式：`per-user`、`shared` 或 `shared-rwo` |
| `env` | `OPENAI_API_KEY=sk-...` | 注入到用户容器的原始环境变量 |
| `idle_timeout_minutes` | `30` | 终端被停止和移除前的空闲时间 |
| `restricted` | `true` | 在受限安全上下文下运行（Kubernetes/OpenShift 后端） |
| `pod_security_context` | `{"fsGroup": 1000}` | Kubernetes Pod `securityContext` 覆盖（Kubernetes/OpenShift 后端） |
| `container_security_context` | `{"runAsNonRoot": true}` | Kubernetes 容器 `securityContext` 覆盖（Kubernetes/OpenShift 后端） |

所有字段都是可选的。如果省略某个字段，编排器使用其全局默认值，例如 `TERMINALS_IMAGE` 或 `TERMINALS_KUBERNETES_STORAGE_MODE`。

策略变更在终端新预配时应用。正在运行的现有终端保留其当前镜像和环境，直到它们被停止、刷新或被空闲超时清理。Open WebUI 是此策略状态的管理客户端；Terminals 仍然是策略和生命周期配置的权威来源。

定时重置通过策略生命周期配置，而不是策略字段。这使预配设置与持续维护分离。
