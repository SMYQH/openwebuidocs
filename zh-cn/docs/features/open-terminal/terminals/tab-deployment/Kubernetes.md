## 前置条件 {#prerequisites}

- 正在运行的 Kubernetes 集群
- 已安装 [Helm](https://helm.sh/docs/intro/install/) v3
- 已配置 `kubectl` 以访问你的集群
- [Open WebUI 企业版许可证](/enterprise)（生产环境必需）

## 使用 Helm 部署 {#deploy-with-helm}

Open WebUI 的 Helm chart 将 Terminals 作为可选子 chart 提供。在 values 文件中添加 `terminals` 部分：

```yaml
# values.yaml
terminals:
  enabled: true
  apiKey: ""  # Auto-generated if left empty

  crd:
    install: false  # install the CRD from the Terminals repository, see below

  operator:
    image:
      repository: ghcr.io/open-webui/terminals-operator
      tag: latest

  orchestrator:
    image:
      repository: ghcr.io/open-webui/terminals
      tag: latest
    backend: kubernetes-operator
    terminalImage: "ghcr.io/open-webui/open-terminal:latest"
    idleTimeoutMinutes: 30
```

然后安装或升级：

```bash
helm upgrade --install open-webui open-webui/open-webui \
  -f values.yaml \
  --namespace open-webui --create-namespace
```

:::tip 自动配置连接
当 `terminals.enabled` 为 `true` 时，Chart 会将 `TERMINAL_SERVER_CONNECTIONS` 指向集群内的编排器。在管理区域的**设置 > 集成**中打开连接并保存一次，让 Open WebUI 将其识别为编排器。在连接的**访问权限**设置中向创建终端的人员授予**写入**权限，参见[创建机器](/features/open-terminal/terminals/orchestration/creating-terminals)。
:::

Terminal CRD 必须定义 `spec.templateId`。Helm Chart 附带的 CRD 要求 `spec.userId`，因此请从 [Terminals 仓库](https://github.com/open-webui/terminals/blob/main/manifests/terminal-crd.yaml)安装与你的 Terminals 版本匹配的 CRD，并设置 `terminals.crd.install: false`。

### 验证 {#verify}

```bash
# Check that all pods are running
kubectl get pods -n open-webui -l app.kubernetes.io/part-of=open-terminal

# Check that the CRD is installed
kubectl get crd terminals.openwebui.com
```

---

## 部署了什么 {#what-gets-deployed}

当 `terminals.enabled: true` 时，chart 将创建：

| 资源 | 目的 |
| :--- | :--- |
| **CRD** (`terminals.openwebui.com`) | 定义 `Terminal` 自定义资源 |
| **Operator 部署** | Kopf 控制器，监听 Terminal CR 并配置 Pod、Service、PVC、Secret |
| **编排器 Deployment 和 Service** | FastAPI 服务，接收 Open WebUI 请求并代理到实例 Pod |
| **Secret** | 共享 API 密钥（如果未提供则自动生成） |

对于**每个实例**，Operator 会创建一个 Pod、一个 Service、一个 Secret（API 密钥），以及可选的持久存储 PVC。

---

## 生命周期 {#lifecycle}

需要实例时，编排器会创建 `Terminal` CR。Operator 会置备 Pod、Service、Secret 以及可选的 PVC。Pod 通过就绪检查后，编排器将流量代理到该 Pod。

当实例闲置时间超过 `idleTimeoutMinutes` 时，Operator 会删除 Pod，但保留 PVC 和 Secret。下一次请求会新建 Pod 并重新挂载同一个 PVC，使**用户数据在空闲清理后得以保留**。

```bash
# List all terminals
kubectl get terminals -n open-webui

# Inspect a specific terminal
kubectl describe terminal <name> -n open-webui

# Delete a terminal (its Pod, Service and Secret are removed)
kubectl delete terminal <name> -n open-webui
```

删除终端时，会移除其 Pod、Service 和 Secret。包含其文件的 PVC 会保留，直到你单独执行 `kubectl delete pvc` 将其删除。

---

## 监控 {#monitoring}

```bash
# Operator logs
kubectl logs -n open-webui deployment/<release>-terminals-operator --tail=50

# Orchestrator logs
kubectl logs -n open-webui deployment/<release>-terminals-orchestrator --tail=50
```

---

<details>
<summary>Terminal CRD 参考</summary>

### Spec 字段 {#spec-fields}

| 字段 | 类型 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- |
| `templateId` | 字符串 | *（必填）* | 此实例所属终端的 ID |
| `contextId` | 字符串 | `default` | 标识终端的具体实例，可为 `default`、`user:<id>`、`chat:<id>` 或 `model:<id>` |
| `image` | 字符串 | `ghcr.io/open-webui/open-terminal:latest` | 容器镜像 |
| `imagePullPolicy` | 字符串 | *（Kubernetes 默认值）* | `Always`、`IfNotPresent` 或 `Never` |
| `resources.requests.cpu` | 字符串 | *（未设置）* | CPU 请求量。编排器只设置上限 |
| `resources.requests.memory` | 字符串 | *（未设置）* | 内存请求量。编排器只设置上限 |
| `resources.limits.cpu` | 字符串 | *（未设置）* | CPU 上限。终端指定 CPU 上限时，编排器会设置此字段 |
| `resources.limits.memory` | 字符串 | *（未设置）* | 内存上限。终端指定内存上限时，编排器会设置此字段 |
| `idleTimeoutMinutes` | 整数 | `30` | 停止 Pod 前的空闲超时，`0` 表示禁用。编排器始终根据终端配置或 `TERMINALS_IDLE_TIMEOUT_MINUTES` 设置该值，因此默认值仅适用于手动编写的资源 |
| `packages` | 数组 | `[]` | 预安装的 Apt 包 |
| `pipPackages` | 数组 | `[]` | 预安装的 Pip 包 |
| `env` | 对象 | `{}` | 传递给容器的环境变量 |
| `restricted` | 布尔值 | `false` | Kubernetes 和 OpenShift 受限 Pod 的默认设置 |
| `podSecurityContext`, `containerSecurityContext` | 对象 | *（未设置）* | 分别复制到 Pod 和容器的安全上下文 |
| `podTemplate` | 对象 | *（未设置）* | 合并到生成的 Pod 中的元数据和规范覆盖项 |
| `persistence.enabled` | 布尔值 | `true` | 启用持久化存储 |
| `persistence.size` | 字符串 | `1Gi` | PVC 大小 |
| `persistence.storageClass` | 字符串 | *(集群默认)* | 存储类 |

### Status 字段 {#status-fields}

| 字段 | 描述 |
| :--- | :--- |
| `phase` | `Pending`, `Provisioning`, `Running`, `Idle`, 或 `Error` |
| `podName` | 终端 Pod 的名称 |
| `serviceUrl` | 终端的集群内 URL |
| `apiKeySecret` | 保存终端 API 密钥的 Secret |
| `lastActivityAt` | 上次代理请求的时间戳 |
| `message` | 人类可读的状态消息 |

</details>

<details>
<summary>完整 Helm values 参考</summary>

| 键 | 默认值 | 描述 |
| :--- | :--- | :--- |
| `terminals.enabled` | `false` | 启用 Terminals 子 chart |
| `terminals.apiKey` | (空) | 共享 API 密钥（如果为空则自动生成） |
| `terminals.existingSecret` | (空) | 预存在的 Secret 名称 (键: `api-key`) |
| `terminals.crd.install` | `true` | 安装 Terminal CRD |
| `terminals.operator.image.repository` | `ghcr.io/open-webui/terminals-operator` | Operator 镜像 |
| `terminals.operator.image.tag` | `latest` | Operator 镜像标签 |
| `terminals.operator.replicaCount` | `1` | Operator 副本数 |
| `terminals.orchestrator.image.repository` | `ghcr.io/open-webui/terminals` | 编排器镜像 |
| `terminals.orchestrator.image.tag` | `latest` | 编排器镜像标签 |
| `terminals.orchestrator.backend` | `kubernetes-operator` | 后端类型 |
| `terminals.orchestrator.terminalImage` | `ghcr.io/open-webui/open-terminal:latest` | 用户 Pod 的默认镜像 |
| `terminals.orchestrator.idleTimeoutMinutes` | `30` | 空闲超时（分钟） |
| `terminals.orchestrator.terminalImagePullPolicy` | `IfNotPresent` | 实例镜像拉取策略 |
| `terminals.orchestrator.replicaCount` | `1` | 编排器副本数 |
| `terminals.operator.extraEnvVars`, `terminals.orchestrator.extraEnvVars` | `[]` | 以列表或映射形式指定的额外环境变量 |
| `terminals.networkPolicy.enabled` | `false` | 为 Operator、编排器和实例 Pod 创建 NetworkPolicy |
| `terminals.orchestrator.service.type` | `ClusterIP` | 编排器 Service 类型 |
| `terminals.orchestrator.service.port` | `8080` | 编排器 Service 端口 |

</details>

<details>
<summary>RBAC 要求（仅限手动安装）</summary>

如果不使用 Helm chart，Operator 的 ServiceAccount 需要一个具有以下权限的 ClusterRole：

| 资源 | 动作 (Verbs) |
| :--- | :--- |
| `terminals.openwebui.com` | `get`、`list`、`watch`、`create`、`update`、`patch`、`delete` |
| `pods`, `services`, `persistentvolumeclaims`, `secrets` | `get`、`list`、`watch`、`create`、`update`、`patch`、`delete` |
| `events` | `create` |
| `configmaps`, `leases` | `get`、`list`、`watch`、`create`、`update`、`patch` |

</details>
