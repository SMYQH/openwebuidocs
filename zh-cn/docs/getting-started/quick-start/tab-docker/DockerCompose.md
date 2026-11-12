# Docker Compose 配置

使用 Docker Compose 可以更方便地管理多容器 Docker 应用。

Docker Compose 需要额外安装 `docker-compose-v2`。

:::warning

**注意：** 一些旧版 Docker Compose 教程仍使用 version 1 语法，例如 `docker-compose build`。请确认你使用的是 version 2 语法，即 `docker compose build`（中间是空格，不是连字符）。

:::

## 示例 `docker-compose.yml`

下面是一个用于部署 Open WebUI 的示例配置：

```yaml
services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
volumes:
  open-webui:
```

### 运行预发布镜像 {#running-the-pre-release-image}

`:dev` 是 Open WebUI 的预发布通道，实际上就是每夜构建：每项改动都会先进入 `dev` 分支，然后才会进入其他地方，而发布当天的 `dev` 就是即将发布的版本。在第二个实例上运行它可以让你提前看到那个版本，你反馈的问题也会在正式发布之前而不是之后得到修复。

更改标签，并且重要的是，给它一个**独立的数据卷和独立的端口**：

```yaml
services:
  openwebui-dev:
    image: ghcr.io/open-webui/open-webui:dev
    ports:
      - "3001:8080"
    volumes:
      - open-webui-dev:/app/backend/data
    extra_hosts:
      - host.docker.internal:host-gateway
    environment:
      - WEBUI_SECRET_KEY=your-dev-secret-key
    restart: unless-stopped
volumes:
  open-webui-dev:
```

:::warning 绝不要让 dev 指向你的生产数据卷
开发构建可能包含发布镜像无法回读的数据库迁移，因此共用数据卷可能让你无法再退回 `:main`。请像上面那样，让 `open-webui-dev` 使用自己的数据卷。
:::

把它作为第二个服务与你的常规服务并列添加，两者就会同时运行，分别占用 3000 和 3001 端口。若发现任何看起来不对的地方，请在 [GitHub](https://github.com/open-webui/open-webui/issues) 上反馈。预发布的测试充分程度取决于有多少人选择安装它，因此这是运维人员能够贡献的最有价值的一件事。

## 辅助脚本

代码库中附带了一组辅助脚本，用于简化常见的 Docker 工作流：

- `docker-compose-launcher.sh` —— 交互式 Compose 启动器，具备 GPU 自动检测、可配置的 WebUI/API 端口、宿主机数据卷挂载以及可选的 Playwright 支持。运行 `./docker-compose-launcher.sh --help` 查看完整参数列表。使用 `--drop` 可以销毁整个项目。
- `docker-cleanup.sh` —— 停止 Compose 项目并**删除所有卷**，包括持久化数据。销毁数据前会要求确认。
- `docker-run.sh` —— 构建 Open WebUI 镜像并运行单容器，通过 `OPEN_WEBUI_PORT`（默认 `3000`）对外暴露。
- `docker-ollama.sh` —— 拉取并运行官方 Ollama 容器，支持可选的 GPU 透传，通过 `OLLAMA_PORT`（默认 `11434`）对外暴露。
- `docker-update-models.sh` —— 遍历 Ollama 容器中已安装的每一个模型，并拉取其最新版本。

---

:::note

**说明：** 如果需要 Nvidia GPU 支持，请把镜像从 `ghcr.io/open-webui/open-webui:main` 改为 `ghcr.io/open-webui/open-webui:cuda`，并在 `docker-compose.yml` 的服务定义中增加以下内容：

:::

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

这样就能在可用时让应用使用 GPU 资源。

## 卸载

如果要卸载通过 Docker Compose 运行的 Open WebUI，请按以下步骤操作：

1.  **停止并删除服务：**
    在包含 `docker-compose.yml` 的目录中运行：
    ```bash
    docker compose down
    ```

2.  **删除数据卷（可选，警告：会删除所有数据）：**
    如果你希望彻底移除数据（聊天、设置等）：
    ```bash
    docker compose down -v
    ```
    或手动删除：
    ```bash
    docker volume rm <your_project_name>_open-webui
    ```

3.  **删除镜像（可选）：**
    ```bash
    docker rmi ghcr.io/open-webui/open-webui:main
    ```

### 使用 Slim 镜像 {#helper-scripts}

如果你的环境存储空间或带宽有限，可以使用不预打包模型的 slim 镜像：

```yaml
services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main-slim
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
volumes:
  open-webui:
```

:::note

**说明：** slim 镜像会在首次使用时下载所需模型（whisper、embedding 模型），因此第一次启动可能更慢，但镜像体积会明显更小。

:::

## 启动服务 {#uninstall}

运行以下命令启动服务：

```bash
docker compose up -d
```
