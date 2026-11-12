---
slug: /deployment/kubernetes
sidebar_position: 1
title: "Kubernetes 部署"
description: "使用 Helm 在 Kubernetes 上部署 Open WebUI，从单个持久化实例到使用共享服务的生产部署。"
---

# Kubernetes 部署 {#kubernetes-deployment}

使用官方 Open WebUI Helm chart 在你的 Kubernetes 集群上部署。本指南在一处集中讲解准备、安装、验证与更新。

如需企业版许可部署，请参阅[企业版 Helm 部署指南](/enterprise/deployment/kubernetes-helm)。

Open WebUI 会连接到已有的模型服务器或 API。本指南中的示例不会安装 Ollama、Pipelines 或 Terminals，也不要求 Open WebUI Pod 具备 GPU。

## 选择部署方式 {#choose-your-deployment}

| 路径 | 你会得到什么 | 何时使用 |
| :--- | :--- | :--- |
| [单副本](#single-replica) | 一个应用 Pod，并为数据库和文件挂载持久卷。 | 你希望在适合 SQLite 的存储上进行简单安装。 |
| [生产环境](#production) | 一个或多个应用 Pod，使用共享的 PostgreSQL、Redis 和对象存储。 | 你需要共享服务、多个副本，或存储不适合 SQLite。 |

企业版许可适用于这两条路径中的任意一条。仅凭用户数量并不能决定副本数；请根据并发聊天、文档处理和模型延迟来估算。

**请按顺序执行第 1–5 步。** 在第 3 步中选择一条部署路径。许可、品牌定制、扩缩容与维护将在之后讲解。

## 1. 检查你的集群 {#1-check-your-cluster}

你需要一个正在运行的 Kubernetes 集群、Helm 3，以及已针对该集群配置好的 `kubectl`。你还需要创建命名空间、工作负载、Service 和 Secret 的权限，以及访问 chart 仓库、容器镜像仓库和模型端点的权限。

```bash
kubectl config current-context
kubectl get nodes
kubectl create namespace openwebui
helm repo add open-webui https://open-webui.github.io/helm-charts
helm repo update
```

**预期结果：** 节点处于就绪状态，且 `openwebui` 命名空间已存在。如果命名空间已存在，请直接复用。

本指南固定使用 **chart 18.0.0** 与 **application v0.13.0**。Chart 版本与应用版本彼此独立。修改版本之前，请查阅[已发布的 chart](https://github.com/open-webui/helm-charts/tree/open-webui-17.5.0/charts/open-webui)与[镜像参考](/getting-started/quick-start#image-variants)。

## 2. 配置应用 {#2-configure-the-application}

### 保存签名密钥与模型 API 密钥 {#store-the-signing-key-and-model-api-key}

生成一次签名密钥，然后将其保存在密钥管理器中，供日后重启与恢复使用：

```bash
openssl rand -hex 32
```

在 Git 之外的私有目录中创建 `secrets.env`。在填入真实凭据之前，将其权限设置为 `600`。替换其中的两个占位符；使用不带引号的单行值。

```ini title="secrets.env"
WEBUI_SECRET_KEY=REPLACE_WITH_GENERATED_KEY
OPENAI_API_KEY=REPLACE_WITH_MODEL_API_KEY
```

```bash
kubectl -n openwebui create secret generic openwebui-secrets \
  --from-env-file=secrets.env
```

**预期结果：** Secret `openwebui-secrets` 已创建。Kubernetes Secret 需要恰当的 RBAC 与静态加密。你也可以让密钥运维工具创建同名 Secret 与同名键。

### 保存共享的 Helm 配置值 {#save-the-shared-helm-values}

将以下内容保存为 `values-common.yaml`。把 `https://models.example.com/v1` 替换为你自己的 OpenAI 兼容 API 基础 URL。你的 Pod 必须能够访问它，并且它的模型列表中必须包含一个聊天模型。

<details>
<summary>显示 values-common.yaml</summary>

```yaml title="values-common.yaml"
fullnameOverride: openwebui
workload:
  kind: Deployment
strategy:
  type: Recreate
image:
  repository: ghcr.io/open-webui/open-webui
  tag: v0.13.0
ollama:
  enabled: false
pipelines:
  enabled: false
terminals:
  enabled: false
tika:
  enabled: false
service:
  type: ClusterIP
  port: 80
openaiBaseApiUrl: https://models.example.com/v1
openaiApiKeyExistingSecret: openwebui-secrets
openaiApiKeyExistingSecretKey: OPENAI_API_KEY
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: '2'
    memory: 4Gi
startupProbe:
  httpGet:
    path: /health
    port: http
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 60
readinessProbe:
  httpGet:
    path: /ready
    port: http
  periodSeconds: 10
  timeoutSeconds: 5
livenessProbe:
  httpGet:
    path: /health
    port: http
  periodSeconds: 30
  timeoutSeconds: 5
  failureThreshold: 3
extraEnvVars:
  WEBUI_SECRET_KEY:
    valueFrom:
      secretKeyRef:
        name: openwebui-secrets
        key: WEBUI_SECRET_KEY
  UVICORN_WORKERS: '1'
```

</details>

这些配置为应用提供了可预期的资源名称、通过 Secret 引用其凭据，并配置健康探针。`/ready` 会在启动完成、且数据库与 Redis（配置了的话）响应之后才返回。`Recreate` 会在滚动更新期间先停止旧的应用 Pod，再启动替代者。资源请求与上限只是起点；请根据实际观测到的用量进行调整。

该 chart 支持映射式的 `extraEnvVars`，此处用于跨文件合并配置。Helm 3 可能报告合并警告，因为 chart 的默认值是一个列表；安装前请在渲染出的 manifest 中确认环境变量与 Secret 引用。

## 3. 选择存储配置 {#3-choose-a-storage-configuration}

将以下**其中一份**配置与 `values-common.yaml` 放在一起保存。

### 单副本 {#single-replica}

检查你现有的存储类：

```bash
kubectl get storageclass
```

选择具备可靠文件锁定和低延迟文件系统访问、适合 SQLite 的存储，例如本地存储或块存储。不要把 SQLite 放在 NFS、SMB 或其他共享网络文件系统上。如果你的存储不合适，请使用搭配 PostgreSQL 的生产环境配置。参见[数据库存储指引](/getting-started/advanced-topics/scaling#step-1-switch-to-postgresql)。

将以下内容保存为 `values-single.yaml`，并替换 `your-storage-class`：

```yaml title="values-single.yaml"
replicaCount: 1
websocket:
  enabled: true
  manager: ''
  redis:
    enabled: false
persistence:
  enabled: true
  provider: local
  storageClass: your-storage-class
  accessModes:
  - ReadWriteOnce
  size: 10Gi
  annotations:
    helm.sh/resource-policy: keep
ingress:
  enabled: false
extraEnvVars:
  ENABLE_DB_MIGRATIONS: 'true'
```

该 PVC 会在 `/app/backend/data` 下保存 SQLite、本地向量数据、上传文件和模型缓存。副本数与工作进程数都请保持为 1。keep 注解会在 Helm 卸载时保留这个 PVC。

本地嵌入模型可能会在首次启动时下载。请允许必要的模型下载访问，或提前准备好这些资源文件。这条路径中 Redis 是可选的；在生产环境中使用它之前，请先了解[令牌吊销](/getting-started/advanced-topics/hardening#token-revocation)。

### 生产环境 {#production}

安装前请先准备好下列服务。下面的 chart 配置会连接它们，但不会创建它们。

| 服务 | 需要准备的内容 |
| :--- | :--- |
| PostgreSQL + PGVector | 一个具备 schema 迁移权限的应用数据库与角色。请让数据库管理员在该数据库中启用 `vector` 扩展。 |
| Redis | 一个共享端点，并按需配置认证与 TLS。 |
| S3 兼容存储 | 一个已有的存储桶，以及具备所需读、写、列举和删除权限的凭据。 |
| 嵌入 API | 一个 OpenAI 兼容的嵌入端点、其 API 密钥，以及受支持的嵌入模型 ID。 |
| 内容提取 | 一个可达的 Apache Tika 服务。 |
| HTTPS 访问 | 已安装的 ingress controller、一个 DNS 主机名，以及它的 TLS 证书与私钥。 |

PGVector 会取代默认的 ChromaDB，因为 ChromaDB 的本地 SQLite 存储无法由多个副本共享。参见[外部向量数据库](/getting-started/advanced-topics/scaling#step-4-switch-to-an-external-vector-database)。

在应用网络内，验证数据库登录与向量扩展、Redis 访问、存储桶的上传/下载/删除、模型响应、嵌入请求以及 Tika 访问。按需为这些服务配置网络策略与私有 CA 信任。

:::warning 已有安装
这些配置面向全新的数据库与存储桶。设置 PostgreSQL URL 并不会迁移已有的 SQLite 用户、聊天或设置。在已有数据的安装上更换后端之前，请先规划数据迁移、文件迁移以及向量迁移或重新索引。
:::

创建一个私有的 `backends.env`，像保护 `secrets.env` 一样保护它，并替换其中的占位符。对数据库与 Redis 凭据中的特殊字符进行 URL 编码。请使用你的数据库服务商所要求的 [TLS 参数](/reference/env-configuration#database_url)。

```ini title="backends.env"
DATABASE_URL=postgresql://REPLACE_USER:REPLACE_PASSWORD@postgres.example.com:5432/openwebui
REDIS_URL=rediss://default:REPLACE_PASSWORD@redis.example.com:6379/0
RAG_OPENAI_API_KEY=REPLACE_WITH_EMBEDDING_API_KEY
S3_ACCESS_KEY_ID=REPLACE_WITH_STORAGE_ACCESS_KEY
S3_SECRET_ACCESS_KEY=REPLACE_WITH_STORAGE_SECRET_KEY
```

```bash
kubectl -n openwebui create secret generic openwebui-backends \
  --from-env-file=backends.env
kubectl -n openwebui create secret tls openwebui-tls \
  --cert=/path/to/tls.crt --key=/path/to/tls.key
```

将以下内容保存为 `values-production.yaml`。替换主机名、ingress class、存储桶、区域和嵌入模型。让 `WEBUI_URL` 与你的 ingress 主机名保持一致；即使在禁用 ingress 的情况下，它在首次启动时也必须正确。

<details>
<summary>显示 values-production.yaml</summary>

```yaml title="values-production.yaml"
replicaCount: 3
websocket:
  enabled: true
  manager: redis
  redis:
    enabled: false
  existingSecret: openwebui-backends
  existingSecretKey: REDIS_URL
databaseUrl: ''
persistence:
  enabled: false
  provider: s3
  s3:
    bucket: openwebui
    region: us-east-1
    endpointUrl: https://s3.example.com
    accessKeyExistingSecret: openwebui-backends
    accessKeyExistingAccessKey: S3_ACCESS_KEY_ID
    secretKeyExistingSecret: openwebui-backends
    secretKeyExistingSecretKey: S3_SECRET_ACCESS_KEY
ingress:
  enabled: true
  class: your-ingress-class
  host: ai.example.com
  tls: true
  existingSecret: openwebui-tls
extraEnvVars:
  WEBUI_URL: https://ai.example.com
  DATABASE_URL:
    valueFrom:
      secretKeyRef:
        name: openwebui-backends
        key: DATABASE_URL
  VECTOR_DB: pgvector
  PGVECTOR_CREATE_EXTENSION: 'false'
  RAG_EMBEDDING_ENGINE: openai
  RAG_EMBEDDING_MODEL: REPLACE_WITH_EMBEDDING_MODEL_ID
  RAG_OPENAI_API_BASE_URL: https://embeddings.example.com/v1
  RAG_OPENAI_API_KEY:
    valueFrom:
      secretKeyRef:
        name: openwebui-backends
        key: RAG_OPENAI_API_KEY
  CONTENT_EXTRACTION_ENGINE: tika
  TIKA_SERVER_URL: http://tika.example.com:9998
  ENABLE_DB_MIGRATIONS: 'false'
```

</details>

该 chart 使用同一个 Secret 设置应用与 WebSocket 的 Redis URL。PostgreSQL 保存应用记录与向量（除非你设置了 [`PGVECTOR_DB_URL`](/reference/env-configuration#pgvector_db_url)，否则 PGVector 使用 `DATABASE_URL`）；存储桶保存上传的文件。在这套配置下 `/app/backend/data` 是临时的，因此位于这些共享后端之外的本地缓存和特定功能文件不会在 Pod 被替换后保留。

如果生产环境只需要一个副本，请在此文件中设置 `replicaCount: 1`。更多副本需要足够的数据库连接容量和共享服务；当需要抵御节点故障的韧性时，请把它们分散到不同节点。参见[扩缩容指引](/getting-started/advanced-topics/scaling)。

slim 镜像支持这套配置用到的所有服务，因此使用它时可以设置 `image.tag: v0.13.0-slim`，获得体积小得多的镜像而不含本地机器学习栈。参见[slim 镜像省略了哪些内容](/getting-started/quick-start#what-slim-leaves-out)。

## 4. 使用 Helm 安装 {#4-install-with-helm}

选择你保存的配置：

```bash
# Choose ONE:
OPENWEBUI_PROFILE=values-single.yaml
# OPENWEBUI_PROFILE=values-production.yaml
```

两条路径都以**恰好一个启用迁移的工作进程**启动，并禁用 ingress。请先检查渲染出的 manifest，然后安装：

```bash
helm template openwebui open-webui/open-webui \
  --version 18.0.0 --namespace openwebui \
  -f values-common.yaml -f "$OPENWEBUI_PROFILE" \
  --set replicaCount=1 --set ingress.enabled=false \
  --set-string extraEnvVars.ENABLE_DB_MIGRATIONS=true > rendered.yaml

helm install openwebui open-webui/open-webui \
  --version 18.0.0 --namespace openwebui \
  -f values-common.yaml -f "$OPENWEBUI_PROFILE" \
  --set replicaCount=1 --set ingress.enabled=false \
  --set-string extraEnvVars.ENABLE_DB_MIGRATIONS=true \
  --wait --timeout 15m

kubectl -n openwebui rollout status deployment/openwebui --timeout=10m
kubectl -n openwebui get pods,pvc,services
```

**预期结果：** 一个处于就绪状态的应用 Pod。单副本路径还会有一个已绑定的 `openwebui` PVC。镜像拉取与首次模型下载可能需要几分钟。

如果 Helm 超时，请检查 `helm status openwebui -n openwebui`、Pod 事件与日志。如果 release 已存在，请使用相同的引导参数改用 `helm upgrade` 重试。在初始化成功之前不要增加副本。

## 5. 打开并验证 Open WebUI {#5-open-and-verify-open-webui}

让下面这条命令保持运行：

```bash
kubectl -n openwebui port-forward service/openwebui 3000:80
```

打开 [http://localhost:3000](http://localhost:3000)，创建第一个管理员账户，选择一个模型并发送一条消息。如果模型缺失，请检查 **Admin Panel → Settings → Connections**。

在对外开放服务之前，请禁用开放注册或配置你的[身份提供方](/features/authentication-access/auth/sso)。请阅读[加固指南](/getting-started/advanced-topics/hardening)。

### 完成生产环境安装 {#finish-the-production-installation}

对于生产环境路径，请在第一个副本成功初始化之后应用已保存的配置：

```bash
helm upgrade openwebui open-webui/open-webui \
  --version 18.0.0 --namespace openwebui \
  -f values-common.yaml -f values-production.yaml \
  --wait --timeout 15m
kubectl -n openwebui rollout status deployment/openwebui --timeout=10m
kubectl -n openwebui get pods,ingress
```

这会在所有副本上禁用迁移、应用期望的副本数，并启用 ingress。预期会短暂重启。请把 DNS 指向你的 ingress controller，然后打开你的 HTTPS 主机名。

请为你的 controller 配置 WebSocket、无缓冲的流式响应、合适的请求/空闲超时，以及你所需的上传大小。参见[连接故障排查](/troubleshooting/connection-error)。

会话亲和性在启用 WebSocket 时是可选的，但在设置 [`ENABLE_WEBSOCKET_SUPPORT=false`](/reference/env-configuration#enable_websocket_support) 时是必需的；参见[会话亲和性](/troubleshooting/multi-replica#session-affinity-sticky-sessions)。亲和性不能替代 Redis。在 NGINX Ingress Controller 上，请把以下注解添加到 Ingress 资源中：

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/affinity: 'cookie'
    nginx.ingress.kubernetes.io/session-cookie-name: 'open-webui-session'
    nginx.ingress.kubernetes.io/session-cookie-expires: '172800'
    nginx.ingress.kubernetes.io/session-cookie-max-age: '172800'
```

### 验证部署 {#verify-the-deployment}

- **聊天：** 登录，流式接收模型响应，然后重新打开已保存的会话。
- **持久性：** 运行 `kubectl -n openwebui rollout restart deployment/openwebui`，等待滚动完成，必要时重新建立端口转发，并确认会话仍然存在。
- **生产文档：** 上传一份包含醒目事实的小文档。确认索引完成，并就该事实提问以验证能检索到正确的来源。检查上传的对象确实存在于存储桶中。
- **多副本：** 在不同本地端口上分别端口转发两个不同的 Pod，分别登录，并验证两者都能访问同一份已保存的会话和同一个上传文件。同时也要通过 ingress 测试。运行在被替换 Pod 上的流式响应可能需要重试。

就绪的 Pod 只是连上了数据库与 Redis；模型 API、存储和许可仍需按上面的检查项验证。许多应用设置在首次启动后会被持久化保存，因此之后修改环境变量可能无法覆盖它们。参见[配置持久化](/reference/env-configuration#important-note-on-configvar-environment-variables)。

## 企业许可与品牌定制 {#enterprise-licensing-and-branding}

<details>
<summary>添加企业版许可</summary>

创建一个私有且权限受限的 `license.env`，其中包含 `LICENSE_KEY=YOUR_ISSUED_KEY`，然后为它创建 Secret：

```bash
kubectl -n openwebui create secret generic openwebui-license \
  --from-env-file=license.env
```

在 `values-common.yaml` 的 `extraEnvVars` 下添加以下条目，与已有条目并列：

```yaml
  LICENSE_KEY:
    valueFrom:
      secretKeyRef:
        name: openwebui-license
        key: LICENSE_KEY
```

请在安装之前创建该 Secret，或者使用下面的更新流程来应用这项变更。Secret 的环境变量变更需要替换 Pod。请在应用的管理界面中确认预期的企业状态与许可用户上限；仅有就绪状态并不能证明许可已激活。

</details>

<details>
<summary>使用你自己的品牌镜像或托管品牌定制</summary>

对于内部维护的品牌定制，请构建你获得许可的分支镜像并推送到你的镜像仓库。修改 `values-common.yaml` 中已有的镜像设置，并添加拉取 Secret 引用：

```yaml
image:
  repository: registry.example.com/platform/openwebui
  tag: v0.13.0-branding.1
imagePullSecrets:
  - name: openwebui-registry
```

请通过你认可的镜像仓库凭据流程，在同一命名空间中创建该 Secret，例如：

```bash
kubectl -n openwebui create secret generic openwebui-registry \
  --type=kubernetes.io/dockerconfigjson \
  --from-file=.dockerconfigjson=/path/to/private/docker-config.json
```

请使用不可变的镜像标签，并通过下面的更新流程进行部署。在运行中的 Pod 内部所做的修改，会在 Pod 被替换后丢失。

托管品牌定制通过许可配置来提供。[许可实现](https://github.com/open-webui/open-webui/blob/v0.13.0/backend/open_webui/utils/auth.py)会尝试在启动时通过 `api.openwebui.com` 与 `licenses.api.openwebui.com` 以 HTTPS 方式获取许可。请为该流程放行 DNS 解析与出站 HTTPS。自定义品牌镜像本身并不能免除许可的网络要求。对于离线部署，请向你的企业联系人获取受支持的离线许可发放说明；仅设置 `OFFLINE_MODE` 并不能发放许可。

</details>

## 更新与恢复 {#updates-and-recovery}

请安排一个维护窗口。`Recreate` 可以防止普通的 Deployment 滚动更新让新旧 Pod 重叠，但无法在多个新副本之间串行化迁移。

1. 记录已部署的镜像、chart 与配置值，保留你的签名密钥，并准备好备份。停止入口流量，并暂停任何可能重启应用 Pod 的自动扩缩容器或 GitOps 协调流程。
2. 停止**所有**共享该数据库的应用实例，并等待它们终止：

```bash
kubectl -n openwebui scale deployment/openwebui --replicas=0
kubectl -n openwebui wait --for=delete pod \
  -l app.kubernetes.io/instance=openwebui,app.kubernetes.io/name=open-webui \
  --timeout=10m
```

3. 对单副本路径执行 PVC 的最终备份，或对生产环境执行 PostgreSQL 与对象存储的最终备份。
4. 更新 `values-common.yaml` 中的镜像标签，并查看目标版本的发布说明。如果你使用了新的 shell，请重新把 `OPENWEBUI_PROFILE` 设为你保存的配置。启动一个启用迁移的工作进程，并保持 ingress 禁用：

```bash
helm upgrade openwebui open-webui/open-webui \
  --version 18.0.0 --namespace openwebui \
  -f values-common.yaml -f "$OPENWEBUI_PROFILE" \
  --set replicaCount=1 --set ingress.enabled=false \
  --set-string extraEnvVars.ENABLE_DB_MIGRATIONS=true \
  --wait --timeout 15m
kubectl -n openwebui logs deployment/openwebui -c open-webui --tail=100
```

5. 使用端口转发验证启动情况与已有数据。对于生产环境，请运行**完成生产环境安装**的命令，以恢复正常的副本数、ingress 以及禁用迁移的状态。单副本配置会在它唯一的工作进程上保持迁移启用。在恢复正常流量与控制器之前，请重复执行上述验证检查。

更换 chart 版本时，还应查看其发布说明并更新命令中的 `--version`。如果初始化失败，请保持其他副本处于停止状态并加以排查。Helm 回滚（包括 `--atomic`）无法撤销数据库迁移。恢复到不兼容的旧版本应用，需要还原兼容的数据库与存储状态。参见[备份与恢复](/getting-started/updating#backup--restore)。

## 可选：自动扩缩容 {#optional-autoscaling}

<details>
<summary>在生产环境部署正常运行后添加 HPA 和 PodDisruptionBudget</summary>

Chart 18.0.0 不会通过专门的配置项创建这些资源。请把下面这些独立资源保存为 `scaling.yaml`。HPA 需要可用的 metrics API 和 CPU requests；请先确认 `kubectl top pods -n openwebui` 可以正常工作。

```yaml title="scaling.yaml"
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openwebui
  namespace: openwebui
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openwebui
  minReplicas: 2
  maxReplicas: 4
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: openwebui
  namespace: openwebui
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/instance: openwebui
      app.kubernetes.io/name: open-webui
```

使用 `kubectl -n openwebui apply -f scaling.yaml` 应用。这些阈值只是示例，并不代表用户容量保证。请按最大副本数预留数据库连接，并避免 GitOps 与 HPA 对 `spec.replicas` 的修改相互冲突。Helm 升级也可能重置副本数。

在更新之前，请使用 `kubectl -n openwebui delete hpa openwebui` 删除该 HPA，并暂停任何会重新创建它的控制器。只有在验证恢复后的部署之后，才重新应用它。PDB 会限制诸如节点排空这类自愿驱逐；它不会阻止 Deployment 缩容，也不会阻止上文所述的维护停机。

</details>

## 故障排查 {#troubleshooting}

```bash
kubectl -n openwebui get pods,pvc,services,ingress
kubectl -n openwebui get events --sort-by=.metadata.creationTimestamp
kubectl -n openwebui describe deployment openwebui
kubectl -n openwebui logs deployment/openwebui -c open-webui --tail=100
```

| 现象 | 检查项 |
| :--- | :--- |
| Pod 或 PVC 处于 Pending | 可用资源、StorageClass、访问模式以及调度器事件。生产环境的 S3 配置不会创建应用 PVC。 |
| ImagePullBackOff 或 init 容器失败 | 镜像标签、镜像仓库访问、拉取 Secret，以及 `copy-app-data` 的日志。 |
| 缺少 Secret 或键 | 同一命名空间中的确切 Secret 与键名。避免把凭据打印到诊断信息中。 |
| 数据库初始化失败 | 数据库登录/TLS、schema 权限、向量扩展，以及恰好一个启用迁移的工作进程。 |
| 上传或检索失败 | 存储桶权限、Tika 访问、嵌入模型/凭据，以及向量数据库连通性。 |
| 登录循环或设置不一致 | 共享签名密钥、数据库、Redis、公开 URL，以及已持久化的配置。 |
| 流式响应中断 | Redis 连通性、ingress 缓冲、WebSocket 处理，以及请求/空闲超时。 |
| 缺少许可 | 已发放的许可、Secret 引用、Pod 替换，以及许可端点访问。 |
| OOMKilled 或启动超时 | 应用日志、内存占用、模型下载，以及数据库延迟。 |

更多诊断信息请参阅[多副本故障排查](/troubleshooting/multi-replica)。

## 卸载时避免误删数据 {#uninstall-without-accidentally-deleting-data}

如果你安装了 `scaling.yaml`，请先删除这些可选资源。然后卸载 release：

```bash
helm uninstall openwebui --namespace openwebui
```

单副本配置的 **keep 注解**会保留它的 PVC。请用 `kubectl -n openwebui get pvc openwebui` 进行确认；不要想当然地认为所有 chart 配置都会保留 PVC。若要复用它，请设置 `persistence.existingClaim: openwebui` 并复用签名密钥。

release 不会删除外部的生产数据库与对象存储。单独创建的 Secret 同样会保留。请按你的恢复策略保留备份与凭据。

:::danger 有意删除数据
删除命名空间会同时删除其中的 Secret 和 PVC。只有当你不再需要这些数据并且已有所需备份时，才删除保留的 `openwebui` PVC；它的回收策略也可能删除底层存储。
:::