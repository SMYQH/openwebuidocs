---
title: Docker
sidebar_position: 2
---

# Docker

从官方镜像运行 Open WebUI Computer：

```bash
docker run --rm -it \
  -p 8000:8000 \
  -v cptr-data:/data \
  -v "$PWD:/workspace" \
  -w /workspace \
  ghcr.io/open-webui/computer:latest
```

然后打开日志中打印的 URL，通常是 `http://localhost:8000/?token=...`。令牌仅在尚无用户时一次性使用，用于创建你的管理员账户。

- `-v cptr-data:/data`：将应用状态（数据库、配置、上传）保存在命名卷中。保留此挂载，否则每次重启都会丢失账户和设置。
- `-v "$PWD:/workspace"`：将你当前的项目挂载到容器中，以便 Open WebUI Computer 可以处理它。

## docker-compose.yaml

对于需要保持运行的主机：

```yaml
services:
  cptr:
    image: ghcr.io/open-webui/computer:latest
    container_name: cptr
    ports:
      - "8000:8000"
    volumes:
      - cptr-data:/data
      - ~/projects:/projects
      # 挂载任意多个目录；每个挂载的
      # 路径都可以在 UI 中添加为工作区：
      # - ~/notes:/notes
      # - /srv/sites:/sites
    restart: unless-stopped

volumes:
  cptr-data:
```

```bash
docker compose up -d
docker compose logs cptr
```

首次运行的设置 URL 及其令牌在日志中（`docker logs cptr` 也可以）。在应用内部，添加 `/projects`（或任何其他挂载的路径）作为工作区。

## 镜像的工作原理

容器运行 `cptr run --host 0.0.0.0 --headless` 并设置 `CPTR_DATA_DIR=/data`，因此它监听所有容器接口，从不尝试打开浏览器，并将所有有状态内容（SQLite 数据库、`config.toml`、上传、日志）保存在 `/data` 下。镜像包含所有可选功能组，因此无需额外安装。

`:dev` 标签跟踪 `main` 分支，如果你想要最新更改；固定使用 `:latest` 或发布标签以获得稳定性。

:::info 绑定挂载 `/data`
如果你将主机目录绑定挂载到 `/data` 而不是使用命名卷，该目录必须可由容器用户写入：SQLite 需要创建和更新 `/data/app.db`，主机目录权限会覆盖镜像内置的 `/data` 所有权。命名卷完全避免了这个问题。
:::

## 升级

拉取新镜像并使用相同 `/data` 卷重新创建容器：

```bash
docker compose pull
docker compose up -d
```

或者对于普通的 `docker run`：停止容器，`docker pull ghcr.io/open-webui/computer:latest`，然后使用相同的 `-v cptr-data:/data` 标志再次启动。数据库迁移在启动时自动运行；无需手动步骤。对于重大升级，先备份卷：参见[数据和备份](/ecosystem/computer/operate/data-and-backups)。
