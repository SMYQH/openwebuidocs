## 更新 {#updating}

要把本地 Docker 安装更新到最新版本，你可以使用 **Watchtower**，或手动更新容器。

### 方案 1：使用 Watchtower {#option-1-using-watchtower}

借助 [Watchtower](https://github.com/nicholas-fedor/watchtower)，你可以自动化更新流程：

```bash
docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock nickfedor/watchtower --run-once open-webui
```

*（如果你的容器名称不是 `open-webui`，请将其替换成实际名称。）*

### 方案 2：手动更新 {#option-2-manual-update}

1. 停止并删除当前容器：

   ```bash
   docker rm -f open-webui
   ```

2. 拉取最新版本：

   ```bash
   docker pull ghcr.io/open-webui/open-webui:main
   ```

   请拉取与你正在运行的相同标签，例如 `:cuda`、`:ollama` 或某个版本标签，并在第 3 步中继续使用它。拉取 `:main` 不会更新由 `:cuda` 启动的容器所使用的镜像，因此它仍会启动旧版本。

3. 重新启动容器：

   ```bash
   docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data \
     -e WEBUI_SECRET_KEY="your-secret-key" \
     --name open-webui --restart always \
     ghcr.io/open-webui/open-webui:main
   ```

:::warning 设置 WEBUI_SECRET_KEY
如果没有持久化的 `WEBUI_SECRET_KEY`，每次重建容器时你都会被登出。可通过 `openssl rand -hex 32` 生成。
:::

有关版本固定、回滚、自动更新工具和备份流程，请参见[完整更新指南](/getting-started/updating)。
