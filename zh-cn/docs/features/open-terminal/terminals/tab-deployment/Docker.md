<!-- markdownlint-disable MD041 -->

## 前置条件 {#prerequisites}

- 已安装并运行 [Docker Engine](https://docs.docker.com/engine/install/)
- Open WebUI 正在运行（或准备好一同部署）
- [Open WebUI 企业版许可证](/enterprise)（生产环境使用必须）

## 使用 Docker Compose 快速开始 {#quick-start-with-docker-compose}

此 Compose 文件将 Open WebUI 和 Terminals 编排器一起部署。

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - >-
        MACHINE_CONNECTIONS=[{
          "id": "terminals",
          "name": "Terminals",
          "enabled": true,
          "url": "http://terminals:3000",
          "key": "${TERMINALS_API_KEY}",
          "auth_type": "bearer",
          "server_type": "orchestrator",
          "config": {
            "access_grants": [{
              "principal_type": "user",
              "principal_id": "*",
              "permission": "read"
            }]
          }
        }]
    volumes:
      - open-webui:/app/backend/data
    networks:
      - webui
    depends_on:
      - terminals

  terminals:
    image: ghcr.io/open-webui/terminals:latest
    environment:
      - TERMINALS_BACKEND=docker
      - TERMINALS_API_KEY=${TERMINALS_API_KEY}
      - TERMINALS_IMAGE=ghcr.io/open-webui/open-terminal:latest
      - TERMINALS_DOCKER_NETWORK=open-webui-network
      - TERMINALS_DOCKER_HOST_DATA_DIR=${PWD}/data/terminals
      - TERMINALS_IDLE_TIMEOUT_MINUTES=30
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/app/data
    networks:
      - webui

volumes:
  open-webui:

networks:
  webui:
    name: open-webui-network
```

Terminals 将数据库和各实例的文件保存在 Compose 文件旁的 `data` 目录中。`TERMINALS_DOCKER_HOST_DATA_DIR` 告知 Docker 该目录在主机上的位置，使实例容器挂载编排器所管理的同一批文件。

在 Compose 文件旁边的 `.env` 文件中设置共享 API 密钥：

```env
TERMINALS_API_KEY=change-me-to-a-strong-random-value
```

然后启动所有内容：

```bash
docker compose up -d
```

Open WebUI 可通过 `http://localhost:3000` 访问。上述连接向每个用户授予**读取**权限，因此用户可使用共享给自己的终端。请在连接的**访问权限**设置中向创建终端的人员授予**写入**权限，参见[创建机器](/features/open-terminal/terminals/orchestration/creating-terminals)。用户打开终端时，编排器会自动配置实例。

:::warning Docker 套接字访问
编排器需要访问 Docker 套接字 (`/var/run/docker.sock`) 来管理容器。在生产环境中，请使用 Docker 套接字代理，如 [Tecnativa/docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy)，以限制其可以进行的 API 调用。
:::

---

此部署的编排器设置包括 `TERMINALS_DOCKER_NETWORK`、`TERMINALS_DOCKER_DATA_DIR` 和 `TERMINALS_IDLE_TIMEOUT_MINUTES`，详见[编排器环境变量](/features/open-terminal/terminals/orchestration#orchestrator-environment-variables)。

---

<details>
<summary>容器生命周期详情</summary>

**筛选。** 可用 `docker ps --filter "label=app.kubernetes.io/managed-by=terminals"` 筛选容器。

**启动。** 创建容器后，编排器会等待容器响应，最长 15 秒，再开始代理流量。如果容器未能及时就绪，会记录一条警告。

</details>

---

## 限制 {#limitations}

- **单主机。** 所有用户容器都在一个 Docker 主机上运行。如需高可用性或服务更大的团队，请使用 Kubernetes Operator 后端。
- **没有内置高可用性。** 编排器宕机会中断正在使用的终端会话。容器仍会运行，编排器重启后会重新接管。
- **需要 Docker 套接字。** 编排器需要访问 Docker 套接字来管理容器。
