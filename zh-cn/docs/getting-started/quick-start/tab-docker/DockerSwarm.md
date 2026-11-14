
## Docker Swarm {#docker-swarm}

这种安装方式要求你熟悉 Docker Swarm，因为它会使用 stack 文件在 Docker Swarm 中将 3 个独立容器部署为服务。

其中包含独立运行的 ChromaDB、Ollama 与 Open WebUI 容器。
另外还预填了一些[环境变量](/reference/env-configuration)，以便更直观地说明部署方式。

:::info 为什么要将 ChromaDB 作为独立容器运行

这个 stack 正确地将 ChromaDB 部署为**独立的 HTTP 服务容器**，Open WebUI 通过 `CHROMA_HTTP_HOST` 和 `CHROMA_HTTP_PORT` 与其连接。对于任何多 worker 或多副本部署，这都是**必须的**。

默认的 ChromaDB 模式（未设置 `CHROMA_HTTP_HOST`）使用本地基于 SQLite 的 `PersistentClient`，**不具备 fork 安全性**——多个 worker 进程并发写入会立刻导致 worker 崩溃。将 ChromaDB 作为独立服务运行，可以通过 HTTP 连接避免直接访问 SQLite。

如果你打算把 `openWebUI` 服务扩展到多个副本，还应同时把主数据库切换到 PostgreSQL，并配置 Redis。完整要求请参见 [扩展与高可用指南](/troubleshooting/multi-replica)。

:::

请根据你的硬件情况选择相应命令：

- **开始前：**

  需要先在宿主机上创建用于卷的数据目录，或者改用你自己的自定义路径 / 卷。

  当前示例使用的是与 `docker-stack.yaml` 位于同一目录下的隔离目录 `data`。

      - **例如：**


- **启用 GPU：**
