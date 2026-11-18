# Kubernetes 上的 Helm 配置 {#helm-setup-for-kubernetes}

这是在集群上试用 Open WebUI 最快的方式。如果需要持久化或生产级安装（版本锁定、密钥、PostgreSQL、Redis、对象存储、ingress 以及安全更新），请参阅 [Kubernetes 部署](/deployment/kubernetes) 指南。

## 前置要求 {#prerequisites}

- 一个正在运行的 Kubernetes 集群，并且已针对它配置好 `kubectl`。
- Helm 3。

## Helm 步骤 {#helm-steps}

1. **添加 Open WebUI Helm 仓库：**

   ```bash
   helm repo add open-webui https://open-webui.github.io/helm-charts
   helm repo update
   ```

2. **安装 Open WebUI Chart：**

   ```bash
   helm install openwebui open-webui/open-webui
   ```

   使用默认值时，该 chart 还会一并部署 Ollama、Pipelines 和一个 Redis 实例，并把 Open WebUI 的数据存放在 2 GiB 的 PVC 上。如果你打算在其他地方连接模型，请加上 `--set ollama.enabled=false --set pipelines.enabled=false`。

3. **验证安装：**

   ```bash
   kubectl get pods
   ```

在运行多个副本或 worker 之前，请阅读[扩展 Open WebUI](/getting-started/advanced-topics/scaling)。多副本环境下的更新请参阅[更新与恢复](/deployment/kubernetes#updates-and-recovery)。

## 访问 WebUI {#access-the-webui}

将服务转发到你的机器，然后打开 [http://localhost:3000](http://localhost:3000)：

```bash
kubectl port-forward service/openwebui-open-webui 3000:80
```

如需通过 ingress controller 暴露它，请参阅[完成生产环境安装](/deployment/kubernetes#finish-the-production-installation)。

## 卸载 {#uninstall}

1.  **卸载 Helm Release：**
    ```bash
    helm uninstall openwebui
    ```
    使用默认值时，这也会删除 Open WebUI 的 PVC 及其上的数据。若想在卸载后保留数据，请参阅[卸载时避免误删数据](/deployment/kubernetes#uninstall-without-accidentally-deleting-data)。

2.  **删除剩余的 Persistent Volume Claims（警告：会删除所有数据）：**
    为了确保该 release 没有遗留任何卷：
    ```bash
    kubectl delete pvc -l app.kubernetes.io/instance=openwebui
    ```
