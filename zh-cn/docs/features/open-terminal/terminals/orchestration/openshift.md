---
sidebar_position: 9
title: "OpenShift"
---

# OpenShift {#openshift}

Terminals 可以在 OpenShift 上运行，为每位用户提供受限的终端沙箱。

OpenShift 的受限 SCC 不支持让智能体以 root 权限运行的完整开发环境。请使用预构建的终端镜像，由 OpenShift 为每位用户分配独立 Pod，实现隔离。

## 支持的模式 {#supported-model}

- 每个用户与策略的组合对应一个 Open Terminal Pod。
- 通过 PVC 提供持久化用户文件。
- 策略选择的镜像、环境变量、CPU、内存、存储和空闲超时。
- 刷新或定时重置持久化的终端文件。
- 文件浏览、命令执行、笔记本和镜像中预装的工具。

## 受限 SCC 限制 {#restricted-scc-limits}

在 OpenShift 上以受限模式部署时，以下功能不可用：

- 使用 `OPEN_TERMINAL_PACKAGES` 运行时安装 OS 包。
- 使用 `OPEN_TERMINAL_PIP_PACKAGES` 或 `OPEN_TERMINAL_NPM_PACKAGES` 运行时全局安装。
- `sudo`、动态 Linux 用户创建或 `OPEN_TERMINAL_MULTI_USER=true`。
- Docker 套接字访问或 Docker-in-Docker 工作流。
- 来自 `OPEN_TERMINAL_ALLOWED_DOMAINS` 的 iptables/dnsmasq 出口防火墙。

当用户需要额外工具时，构建自定义 Open Terminal 镜像。

## 数据库 {#database}

PostgreSQL 不是必需的。Terminals 默认使用 SQLite，并将其存储在 Terminals 数据目录下。

如果使用默认的 SQLite 数据库，请把 Terminals 服务的持久化存储挂载到 `/app/data`。仅在使用外部数据库时设置 `TERMINALS_DATABASE_URL`。

## 部署 {#deployment}

安装 CRD 和 Operator：

```bash
oc apply -f manifests/terminal-crd.yaml
oc apply -f manifests/operator-deployment.yaml
```

使用 Operator 后端以受限模式运行 Terminals 服务：

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

受限模式会采用适合 OpenShift 受限部署的 Kubernetes 默认安全上下文。如果集群需要其他值，可在策略中使用 `pod_security_context` 和 `container_security_context` 覆盖默认值。

在 OpenShift 上使用集群网络策略进行出口控制。
