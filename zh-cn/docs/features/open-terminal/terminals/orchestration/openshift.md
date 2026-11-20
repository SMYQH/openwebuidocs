---
sidebar_position: 9
title: "OpenShift"
---

# OpenShift {#openshift}

Terminals 可以在 OpenShift 上运行，为每位用户提供受限的终端沙箱。

受限的 OpenShift 部署以非 root Pod 的形式运行终端。请使用预构建的终端镜像，由 OpenShift 通过为每个实例分配一个 Pod 来提供隔离边界。

## 支持的模式 {#supported-model}

- 每个实例使用一个 Open Terminal Pod。
- 通过 PVC 提供持久化用户文件。
- 按终端配置镜像、环境变量、CPU、内存、存储和空闲超时。
- 文件浏览、命令执行、笔记本和镜像中预装的工具。

## 受限 SCC 限制 {#restricted-scc-limits}

OpenShift 的受限部署不使用 root 权限，因此以下功能不可用：

- 使用 `OPEN_TERMINAL_PACKAGES` 运行时安装 OS 包。
- 使用 `OPEN_TERMINAL_PIP_PACKAGES` 或 `OPEN_TERMINAL_NPM_PACKAGES` 运行时全局安装。
- `sudo`、动态 Linux 用户创建或 `OPEN_TERMINAL_MULTI_USER=true`。
- Docker 套接字访问或 Docker-in-Docker 工作流。
- 来自 `OPEN_TERMINAL_ALLOWED_DOMAINS` 的 iptables/dnsmasq 出口防火墙。

在受限模式下，如果终端的环境变量包含 `OPEN_TERMINAL_ALLOWED_DOMAINS`、`OPEN_TERMINAL_PACKAGES`、`OPEN_TERMINAL_PIP_PACKAGES` 或 `OPEN_TERMINAL_NPM_PACKAGES`，编排器会拒绝该终端。请构建包含用户所需工具的自定义 Open Terminal 镜像。

## 数据库 {#database}

Terminals 默认使用 SQLite，并将数据库放在 Terminals 的数据目录中。要保留数据库，请为 Terminals 服务在 `/app/data` 挂载持久存储。要使用 PostgreSQL 等外部数据库，请设置 `TERMINALS_DATABASE_URL`。

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
  - name: TERMINALS_API_KEY
    valueFrom:
      secretKeyRef:
        name: terminals
        key: api-key
```

创建包含此密钥的 `terminals` Secret，并在 Open WebUI 的连接中将同一密钥用作 **API Key**。

在终端中使用与 OpenShift 兼容的 Open Terminal 镜像。将 **Image** 设为 `ghcr.io/open-webui/open-terminal:openshift`，将 **CPU** 设为 `1`，将 **Memory** 设为 `1Gi`，将 **Storage** 设为 `5Gi`，并将环境变量 `OPEN_TERMINAL_FILE_BROWSER_ROOT` 设为 `home`。

受限模式使用适用于受限 OpenShift 部署的 Kubernetes 安全上下文默认值。如果集群要求不同的值，可使用 `TERMINALS_KUBERNETES_POD_SECURITY_CONTEXT` 和 `TERMINALS_KUBERNETES_CONTAINER_SECURITY_CONTEXT` 覆盖。

在 OpenShift 上使用集群网络策略进行出口控制。
