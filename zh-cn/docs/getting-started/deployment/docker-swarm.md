---
slug: /deployment/docker-swarm
sidebar_position: 15
title: "Docker Swarm"
---

# Docker Swarm

本栈将 Open WebUI、ChromaDB 与 Ollama 作为三个服务部署在 Docker Swarm 中。它假设你已经运行了一个 Swarm。

ChromaDB 作为独立的 HTTP 服务器运行，Open WebUI 通过 [`CHROMA_HTTP_HOST`](/reference/env-configuration#chroma_http_host) 访问它。默认的本地 ChromaDB 无法被多个 worker 或副本共享。在把 `openWebUI` 服务扩展到超过一个副本之前，还需迁移到 PostgreSQL、Redis 和共享文件存储，参见[扩缩容 Open WebUI](/getting-started/advanced-topics/scaling)。

`chromadb/chroma` 镜像固定为 Open WebUI 镜像内 `chromadb` 客户端的版本，因为 1.x 客户端只支持 v2 API。更新其中任意一个时请保持两者版本一致。1.x 服务端把数据存放在 `/data` 下。Open WebUI 的**重置向量存储/知识库**与**重置上传目录**操作会调用 Chroma 的重置端点，除非在挂载到 `/config.yaml` 的配置文件中设置 `allow_reset: true`，否则 1.x 服务端会拒绝该请求（参见 [Chroma 的 Docker 指南](https://docs.trychroma.com/guides/deploy/docker)）。

嵌入模型运行在 Ollama 中，因此 Open WebUI 容器不加载本地嵌入模型。栈启动后使用 `docker exec <ollama-container> ollama pull nomic-embed-text` 拉取一次模型。

在 `docker-stack.yaml` 旁创建数据目录：

```bash
mkdir -p data/open-webui data/chromadb data/ollama
```

#### Docker-stack.yaml

```yaml title="docker-stack.yaml"
services:
  openWebUI:
    image: ghcr.io/open-webui/open-webui:main
    volumes:
      - ./data/open-webui:/app/backend/data
    environment:
      WEBUI_SECRET_KEY: your-secret-key
      OLLAMA_BASE_URL: http://ollama:11434
      VECTOR_DB: chroma
      CHROMA_HTTP_HOST: chromadb
      CHROMA_HTTP_PORT: 8000
      RAG_EMBEDDING_ENGINE: ollama
      RAG_EMBEDDING_MODEL: nomic-embed-text
    ports:
      - target: 8080
        published: 8080
    deploy:
      replicas: 1
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3

  chromadb:
    image: chromadb/chroma:1.5.9
    volumes:
      - ./data/chromadb:/data
    deploy:
      replicas: 1
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ./data/ollama:/root/.ollama
    deploy:
      replicas: 1
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
      resources:
        reservations:
          generic_resources:
            - discrete_resource_spec:
                kind: "NVIDIA-GPU"
                value: 0
```

请把 `your-secret-key` 替换为 `openssl rand -hex 32` 的输出。服务之间通过栈网络中的服务名互相访问，因此只有 Open WebUI 发布端口。像 `./data/...` 这样的绑定挂载只存在于任务所在的节点上，因此请通过放置约束把服务固定到单个节点，或使用每个节点都能访问的卷。

**GPU：** `generic_resources` 块用于 GPU 节点。它需要 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)，以及每个 GPU 节点上的 GPU 资源广播：在 `/etc/nvidia-container-runtime/config.toml` 中取消注释 `swarm-resource = "DOCKER_RESOURCE_GPU"`，然后重启 Docker 守护进程。参见[为 GPU 配置 Docker Swarm](https://gist.github.com/tomlankhorst/33da3c4b9edbde5c83fc1244f010815c#configuring-docker-to-work-with-your-gpus)。

**仅 CPU：** 删除 `ollama` 服务中的 `resources:` 块。

部署该栈：

```bash
docker stack deploy -c docker-stack.yaml -d open-webui
```