## 使用 Docker 快速开始

:::info
必须支持 **WebSocket**。请确认你的网络配置允许 WebSocket 连接。
:::

:::tip Docker Hub 现已可用
Open WebUI 镜像同时发布到了**两个**镜像仓库：
- **GitHub Container Registry：** `ghcr.io/open-webui/open-webui`
- **Docker Hub：** `openwebui/open-webui`

两者内容完全一致。你可以在下面的命令中把 `ghcr.io/open-webui/open-webui` 替换成 `openwebui/open-webui`。
:::

### 1. 拉取镜像

```bash
docker pull ghcr.io/open-webui/open-webui:main
```

### 2. 运行容器

```bash
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```

| 参数 | 作用 |
|------|---------|
| `-v open-webui:/app/backend/data` | 持久化存储，避免重启后数据丢失 |
| `-p 3000:8080` | 将界面暴露在本机的 3000 端口 |

### 3. 打开界面

访问 [http://localhost:3000](http://localhost:3000)。

---

## 镜像变体

| 标签 | 适用场景 |
|-----|----------|
| `:main` | 标准镜像（推荐） |
| `:main-slim` | 更小的镜像，首次使用时下载 Whisper 和 embedding 模型 |
| `:cuda` | 提供 Nvidia GPU 支持（需在 `docker run` 中加入 `--gpus all`） |
| `:ollama` | 在容器内集成 Ollama，适合一体化部署 |

### 标签更新机制

`:main` 和 `:latest` 是**相同的滚动镜像**：两者都指向 `main` 分支的最新构建，每次有变更合入时都会重建，因此其摘要会随开发进展不断变化。注意 `:latest` 跟随 `main`，**不**指向最新的稳定版本。

`:dev` 对 `dev` 分支（即将推出的功能）采用相同机制，也是滚动更新。

版本标签（例如 `:vX.Y.Z` 以及简写 `:X.Y.Z` 和 `:X.Y`）是**固定的**，指向特定稳定发布版本，永不改变。`:git-<commit-sha>` 则固定到某个确切提交。

这就是 `:main` 和特定发布标签可能同时显示不同镜像摘要的原因：`:main` 已包含该发布之后的所有合入内容，而版本标签始终保持不变。

| 标签 | 指向 | 是否不可变？ |
| :--- | :--- | :--- |
| `:main`, `:latest` | `main` 分支的最新构建 | 否（滚动） |
| `:dev` | `dev` 分支的最新构建 | 否（滚动） |
| `:vX.Y.Z`, `:X.Y.Z`, `:X.Y` | 特定稳定发布版本 | 是 |
| `:git-<sha>` | 某个确切提交 | 是 |

对于可重现或生产部署，请固定到版本标签。如需最新构建，请使用 `:main`（或与之相同的 `:latest`）。

### 固定特定发布版本

生产环境建议固定版本，而不是使用浮动标签。将 `X.Y.Z` 替换为 [releases 页面](https://github.com/open-webui/open-webui/releases) 中的版本号：

```bash
docker pull ghcr.io/open-webui/open-webui:vX.Y.Z
docker pull ghcr.io/open-webui/open-webui:vX.Y.Z-cuda
docker pull ghcr.io/open-webui/open-webui:vX.Y.Z-ollama
```

---

## 常见配置

### GPU 支持（Nvidia）

```bash
docker run -d -p 3000:8080 --gpus all -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:cuda
```

### 与 Ollama 打包在一起

将 Open WebUI 和 Ollama 放在同一个容器中：

**使用 GPU：**
```bash
docker run -d -p 3000:8080 --gpus=all -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:ollama
```

**仅 CPU：**
```bash
docker run -d -p 3000:8080 -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:ollama
```

### 连接另一台服务器上的 Ollama

```bash
docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=https://example.com -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

### 单用户模式（无登录）

```bash
docker run -d -p 3000:8080 -e WEBUI_AUTH=False -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```

:::warning
切换到单用户模式后，不能再无缝切回多账户模式。
:::

---

## 使用开发分支

:::tip
测试 dev 构建是很有价值的贡献方式之一。建议在测试实例中运行，并通过 [GitHub](https://github.com/open-webui/open-webui/issues) 报告问题。
:::

`:dev` 标签包含的是进入稳定版前的最新功能。

```bash
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:dev
```

:::warning
**不要在 dev 与生产之间共享数据卷。** dev 构建可能包含向后不兼容的数据库迁移。请始终使用单独卷（例如 `-v open-webui-dev:/app/backend/data`）。
:::

如果你不想使用 Docker，也可以参考 [开发 Open WebUI](/getting-started/advanced-topics/development)。

---

## 卸载

1. **停止并删除容器：**
    ```bash
    docker rm -f open-webui
    ```

2. **删除镜像（可选）：**
    ```bash
    docker rmi ghcr.io/open-webui/open-webui:main
    ```

3. **删除数据卷（可选，会删除所有数据）：**
    ```bash
    docker volume rm open-webui
    ```
