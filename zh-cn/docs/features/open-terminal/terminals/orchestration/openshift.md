---
sidebar_position: 8
title: "OpenShift"
---

# OpenShift

Terminals 可以在 OpenShift 上作为受限的每用户终端沙箱运行。

OpenShift 受限 SCC 不支持完整的 rootful agent 开发箱模型。使用预构建的终端镜像，让 OpenShift 通过每用户一个 Pod 提供隔离边界。

## 支持的模式

- 每个用户和策略一个 Open Terminal Pod。
- 通过 PVC 提供持久化用户文件。
- 策略选择的镜像、环境变量、CPU、内存、存储和空闲超时。
- 持久化终端文件的刷新和定时重置。
- 镜像中已安装的文件浏览器、命令执行、笔记本和工具。

## 受限 SCC 限制

以下功能在受限 OpenShift 路径中不可用：

- 使用 `OPEN_TERMINAL_PACKAGES` 运行时安装 OS 包。
- 使用 `OPEN_TERMINAL_PIP_PACKAGES` 或 `OPEN_TERMINAL_NPM_PACKAGES` 运行时全局安装。
- `sudo`、动态 Linux 用户创建或 `OPEN_TERMINAL_MULTI_USER=true`。
- Docker 套接字访问或 Docker-in-Docker 工作流。
- 来自 `OPEN_TERMINAL_ALLOWED_DOMAINS` 的 iptables/dnsmasq 出口防火墙。

当用户需要额外工具时，构建自定义 Open Terminal 镜像。

## 数据库

PostgreSQL 不是必需的。Terminals 默认使用 SQLite，并将其存储在 Terminals 数据目录下。

如果你使用默认的 SQLite 数据库，在 `/app/data` 挂载终端服务的持久化存储。仅当你想要外部数据库时才使用 `TERMINALS_DATABASE_URL`。

## 部署

安装 CRD 和操作员：

```bash
oc apply -f manifests/terminal-crd.yaml
oc apply -f manifests/operator-deployment.yaml
```

使用操作员后端和受限模式运行 Terminals 服务：

```yaml
env:
  - name: TERMINALS_BACKEND
    value: kubernetes-operator
  - name: TERMINALS_KUBERNETES_NAMESPACE
    value: terminals
  - name: TERMINALS_KUBERNETES_RESTRICTED
    value: "true"
```

在策略配置中使用 OpenShift 兼容的 Open Terminal 镜像：

```json
{
  "image": "ghcr.io/open-webui/open-terminal:openshift",
  "restricted": true,
  "storage": "5Gi",
  "storage_mode": "per-user",
  "cpu_limit": "1",
  "memory_limit": "1Gi",
  "env": {
    "OPEN_TERMINAL_FILE_BROWSER_ROOT": "home"
  }
}
```

受限模式应用适用于受限 OpenShift 部署的 Kubernetes 安全上下文默认值。当你的集群需要不同的值时，你可以在策略中使用 `pod_security_context` 和 `container_security_context` 覆盖它们。

在 OpenShift 上使用集群网络策略进行出口控制。
