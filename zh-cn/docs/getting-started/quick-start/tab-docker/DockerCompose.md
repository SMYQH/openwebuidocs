将其保存为 `docker-compose.yml`，把密钥替换为 `openssl rand -hex 32` 的输出，然后运行 `docker compose up -d`：

```yaml title="docker-compose.yml"
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
    extra_hosts:
      - host.docker.internal:host-gateway
    environment:
      - WEBUI_SECRET_KEY=your-secret-key
    restart: unless-stopped

volumes:
  open-webui:
```

`extra_hosts` 让 `host.docker.internal` 在 Linux 上解析到宿主机。在未设置 `OLLAMA_BASE_URL` 时，镜像会到 `http://host.docker.internal:11434`（然后是 `:12434`）查找 Ollama，正是这一行让它能够访问运行在宿主机上的 Ollama。

要更新，请运行 `docker compose pull`，然后再运行 `docker compose up -d`。"更新" 选项卡上的 Watchtower 命令针对名为 `open-webui` 的容器；除非你给服务添加 `container_name: open-webui`，Compose 会把这个容器命名为 `<project>-open-webui-1`。

标签与 Docker 选项卡上的相同：修改 `image:` 那一行即可。要试用 `:dev`，请把它作为第二个服务添加，并使用独立的数据卷和端口，参见[运行预发布镜像](/getting-started/quick-start#running-the-pre-release-image)。请使用 Docker Compose v2（`docker compose`，中间带空格）。



下面的各节是对上面这份 `docker-compose.yml` 的扩展。

:::warning

**警告：** 较早的 Docker Compose 教程可能使用 1 版语法，例如 `docker-compose build`。请确保使用 2 版语法，例如 `docker compose build`（注意是空格而不是连字符）。

:::



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
开发构建可能会迁移数据库，而正式发布的镜像可能无法读取迁移后的数据库。因此，共用数据卷可能导致你无法退回 `:main`。请像上面那样，让 `open-webui-dev` 使用独立的数据卷。
:::

把它作为第二个服务与你的常规服务并列添加，两者就会同时运行，分别占用 3000 和 3001 端口。若发现任何看起来不对的地方，请在 [GitHub](https://github.com/open-webui/open-webui/issues) 上反馈。预发布的测试充分程度取决于有多少人选择安装它，因此这是运维人员能够贡献的最有价值的一件事。

### 使用 Compose 支持 GPU {#gpu-support-with-compose}

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

这样，应用就能使用可用的 GPU 资源。`:cuda` 镜像会在 GPU 上运行 Open WebUI 自己的本地模型，包括嵌入、重排序和 Whisper 语音转文字。只有给 Ollama 容器分配 GPU 后，Ollama 的模型才会使用它。如果没有检测到 GPU，镜像会回退到 CPU，不会报错。预发布通道对应的标签是 `:dev-cuda`。

### 辅助脚本 {#helper-scripts}

代码库中附带了一组辅助脚本，用于简化常见的 Docker 工作流：

- `docker-compose-launcher.sh` —— 交互式 Compose 启动器，具备 GPU 自动检测、可配置的 WebUI/API 端口、用于存放 Ollama 模型的宿主机数据卷挂载以及可选的 Playwright 支持。运行 `./docker-compose-launcher.sh --help` 查看完整参数列表。使用 `--drop` 可以停止并移除 Compose 项目。含方括号的选项要用引号括起来，例如 `./docker-compose-launcher.sh '--enable-gpu[count=1]'`，否则 zsh（macOS 的默认 shell）会报 `no matches found`。
- `docker-cleanup.sh` —— 停止 Compose 项目并**删除所有卷**，包括持久化数据。销毁数据前会要求确认。
- `docker-run.sh` —— 构建 Open WebUI 镜像并运行单容器，通过 `OPEN_WEBUI_PORT`（默认 `3000`）对外暴露。它不会设置 `WEBUI_SECRET_KEY`，因此在把该容器用于快速测试之外的场景前，请先在其 `docker run` 命令行中补上一个。
- `docker-ollama.sh` —— 拉取并运行官方 Ollama 容器，支持可选的 GPU 透传，通过 `OLLAMA_PORT`（默认 `11434`）对外暴露。
- `docker-update-models.sh` —— 遍历 Ollama 容器中已安装的每一个模型，并拉取其最新版本。

---

## 卸载 {#uninstall}

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
