需要 [Docker](https://docs.docker.com/get-docker/)。将 `your-secret-key` 替换为 `openssl rand -hex 32` 的输出，然后运行下面的命令；它会拉取镜像并启动：

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

| 参数 | 作用 |
|---|---|
| `-p 3000:8080` | 界面运行在你机器的 3000 端口上。如果 3000 已被占用，请修改左边的数字。 |
| `-v open-webui:/app/backend/data` | 你的聊天、用户和设置都保存在这个卷中。它能在更新后保留；切勿在没有它的情况下运行。 |
| `--add-host=host.docker.internal:host-gateway` | 让容器能够访问运行在你机器上的 Ollama 或其他任何服务。 |
| `--restart always` | 重启之后自动恢复运行。 |
| `-e WEBUI_SECRET_KEY=your-secret-key` | 设置一次并妥善保存。没有固定的密钥，每次重建容器都会让所有人退出登录。用 `openssl rand -hex 32` 生成一个。 |



## 镜像变体 {#image-variants}

| 标签 | 适用场景 |
|-----|----------|
| `:main` | 标准镜像（推荐）。功能齐全：应用本身加上内置的语音转文字和 embedding 模型。 |
| `:dev` | 来自 `dev` 分支的预发布（每夜）构建。修复和新功能最先到达这里。参见[使用开发分支](#using-the-dev-branch)。 |
| `:slim`, `:main-slim` | 下载体积约为 **197 MB 而非 1.62 GB**，在 Linux/amd64 上**小 88%**。搭配你的模型提供商，聊天体验完全相同。参见[为什么选择 slim？](#what-slim-leaves-out) |
| `:cuda` | Nvidia GPU 支持，CUDA 12.8（在 `docker run` 中加上 `--gpus all`） |
| `:cuda126` | 与 `:cuda` 相同，基于 CUDA 12.6 构建 |
| `:ollama` | 在容器内捆绑 Ollama，适合一体化部署 |

每个变体也都有对应的开发构建：`:dev-slim`、`:dev-cuda`、`:dev-cuda126` 和 `:dev-ollama`。短标签 `:slim`、`:cuda`、`:cuda126` 和 `:ollama` 跟随 `main`。请选择一个变体；slim 不能与 CUDA 或内置 Ollama 组合使用。

### 为什么选择 slim？ {#what-slim-leaves-out}

**197 MB 而非 1.62 GB，聊天体验完全相同。** `:slim` 镜像比 `:main` **小 88%**，全新拉取时**可节省约 1.42 GB**。这意味着在配置机器或部署新实例时，下载 Open WebUI 所花的时间更少。它适用于搭配托管 API、你自己的模型服务器，或独立的 Ollama 实例——即使该实例就在同一台机器上也可以。

以上是 Linux/amd64 上的压缩下载体积，核验于 2026 年 10 月 16 日。体积会随构建和架构变化。`:slim` 与 `:main-slim` 是同一个镜像的两个标签。

<!-- Verified from GHCR manifest layer sizes on October 16, 2026. main linux/amd64: sha256:d90e4762f94cae56e74d329a176f0dc76c6460ee7cb01ad6e4b91a503aa70d66 = 1,620,712,040 bytes; slim linux/amd64: sha256:c5645947013018ed78b0740ccdb29a01a673dbfd815ac168c641d9a80427ca9f = 197,296,335 bytes. -->

体积的节省来自于不包含捆绑的机器学习栈，其中包括 PyTorch、本地 embedding 与语音运行时，以及文档处理工具和可选的数据库与存储客户端。如果你使用 Open WebUI 通过 API 与模型对话，这些依赖本来就会闲置在你的容器中。

**要开始使用，只需把上面 Docker 命令中的 `:main` 改为 `:slim`。** 默认的 SQLite 数据库和本地文件存储照常工作。连接你的模型提供商并开始聊天；基本的聊天部署不需要任何额外服务。

对于知识检索、文档提取或语音，slim 需要连接由相应服务来完成这些工作。如果你已经在使用这些服务，或者只需要聊天，它会是一个合适的选择。如果你希望 Open WebUI 在自己的容器内完成 embedding、语音识别和文档提取，请选择标准镜像。下表列出了每项功能对应的配置方式。

#### 内存占用 {#slim-memory-usage}

在我们 2026 年 10 月 16 日于 Docker Desktop 的 Linux/arm64 上测试 Open WebUI 0.12.3 时，slim **空闲时约占用 300 MiB 内存**。这仅指 Open WebUI 容器本身；你的浏览器、Docker 的虚拟机以及任何模型服务器或外部服务都需要各自的内存。请为启动过程和活跃负载预留额外内存：这一空闲测量值既不是最低内存要求，也不是容器内存上限。

<details>
<summary>我们是如何测量的</summary>

我们运行了三个全新的容器，使用默认的 SQLite 数据库和一个 Uvicorn worker，未配置任何提供商、用户、聊天、上传或插件。每次运行都使用新的数据目录且没有内存限制。Docker 的 Linux 虚拟机有 16 个 CPU 和 7.65 GiB 可用内存；其他容器保持运行。

在 `/health` 返回 HTTP 200 之后，我们等待 30 秒，然后以 5 秒为间隔采集 12 次读数：

```bash
docker stats --no-stream --format '{{.MemUsage}}' <container-name>
```

在全部 36 次采样中，内存占用在 **291.8 到 292.6 MiB** 之间，中位数为 **292.2 MiB**。

在 Linux 上，[Docker 报告的内存占用](https://docs.docker.com/reference/cli/docker/container/stats/)不包含未激活的文件缓存。这些采样覆盖的是空闲实例，而非模型推理或并发聊天流量。结果会随版本、架构、配置和负载而变化。

所固定的镜像是 `ghcr.io/open-webui/open-webui@sha256:abd02d41e522d41be389d28d1a73752cd2afc4aa46f980b60d490ecc9379c16b`（Linux/arm64，提交 `91ea4e3421d1d8069f13d4a463fcb5986d94ea60`）。

</details>

#### 将现有部署迁移到 slim {#moving-an-existing-deployment-to-slim}

切换前请检查你的数据库和文件存储：

- **数据库：** SQLite 和 PostgreSQL 在 slim 上都可用，它们是 Open WebUI 支持的两种数据库。PostgreSQL 的 AWS RDS IAM 认证需要标准镜像。
- **文件存储：** 支持本地文件和 S3（`STORAGE_PROVIDER=s3`）。Azure Blob 和 Google Cloud Storage 需要标准镜像。

Slim 会在启动时检查这些设置，并对不支持的配置报错。默认安装已经使用 SQLite 和本地文件。

#### 每项功能需要什么 {#what-each-feature-needs}

| 如果你需要 | 让 slim 指向 | 否则 |
|---|---|---|
| **文档、知识库或 RAG** | 一个 embedding 提供商：将 `RAG_EMBEDDING_ENGINE` 设置为 `ollama`、`openai` 或 `azure_openai` | embedding 调用会以 503 失败，且管理面板拒绝保存本地引擎 |
| | 带 pgvector 的 PostgreSQL，这是 slim 默认且唯一支持的向量库。当 `DATABASE_URL` 指向 PostgreSQL 时会使用它；否则请设置 `PGVECTOR_DB_URL` | 检索第一次运行时会返回 503。除此之外没有其他影响，该存储库只在使用时才会被打开 |
| **PDF 和 Office 文件** | Tika、Docling、外部提取器或云端引擎 | 上传此类文件会返回 503。纯文本格式仍由 slim 自行读取 |
| **语音输入** | 任意外部语音转文字引擎：OpenAI、Deepgram、Azure、Mistral 等 | 不提供本地 Whisper，且管理面板拒绝选择它 |
| **语音回复** | 任意外部文字转语音引擎 | 不提供本地 Transformers 语音，且请求语音会返回 503 |
| **网页搜索** | DDGS 以外的任意提供商 | 管理面板中 DDGS 为灰色，且保存时会被拒绝 |
| **重排序** | 外部 reranker | 选择本地重排序模型会被拒绝 |
| **代码解释器** | 无需配置，但浏览器会从 `cdn.jsdelivr.net` 而非你的实例获取 Python 包 | 在浏览器无法访问该 CDN 的地方，运行代码会失败 |

另外不可用的还有：**Playwright** 网页加载器（因此页面只能通过纯 HTTP 获取或交由外部网页加载器处理），以及 **Transformers** 文本分割器（请改用字符分割器或 tiktoken 分词器）。Slim 也不带 `git`，因此那些依赖直接从代码仓库安装的工具或函数需要标准镜像。

如果你只是把 Open WebUI 当作托管模型的聊天前端，上述内容都不适用，slim 就是更小的镜像。

#### 没有服务也能用的功能 {#what-still-works-without-a-service}

- **纯文本提取。** `csv`、`html`、`txt`、`md`、`markdown`、`rst`、`xml` 以及其他被识别为文本的格式都由 slim 自行读取。
- **重排序，只是方式不同。** 把重排序模型留空，结果会依据已有的 embedding 以余弦相似度打分，这不需要任何模型运行时。
- **音频透传。** 来自外部提供商的语音会以该提供商返回的格式提供，因为 slim 无法转码。若提供商返回了浏览器无法播放的内容，请求会被拒绝而不是被存储。

#### 自行构建 {#building-it-yourself}

`USE_SLIM=true` 不能与 `USE_CUDA=true` 或 `USE_OLLAMA=true` 组合使用。构建会直接报错终止，而不是产出一个其 GPU 支持或内置模型服务器无物可跑的镜像。

#### 离线与隔离网络环境 {#offline-and-air-gapped}

Slim 从不下载模型，因为它无法运行模型；而在隔离网络环境中，部署只需要访问你自有网络上的相应服务。`OFFLINE_MODE=true` 仍会屏蔽对 Hugging Face 的流量以及版本检查。

有两项功能会在首次使用时访问互联网。**分词分割器**会下载其 tiktoken 编码，因此离线实例应使用字符分割器。**代码解释器**会让浏览器从 `cdn.jsdelivr.net` 拉取其 Python 包，因为 slim 只包含 Pyodide 运行时，而标准镜像则捆绑了这些包。隔离网络环境的实例应关闭代码解释器，或改用标准镜像。

### 标签的更新机制 {#how-the-tags-update}

`:main` 和 `:latest` 是**同一个滚动镜像**：两者都指向 `main` 分支的最新构建，并且每次有变更合入该分支时都会重建，因此随着开发推进，其摘要不断前移。请注意 `:latest` 跟随 `main`，它**并不**指向最新的稳定发布版本。

`:dev` 是 `dev` 分支的同一套机制，同样是滚动的。它就是预发布版本，实际上相当于每夜构建，并且会比这些修复和功能出现在 `:main` 下早好几周。

版本标签（例如 `:vX.Y.Z` 以及简写的 `:X.Y.Z`）**固定**在某一个稳定发布版本上，永不改变。`:X.Y` 跟随该次版本线的最新补丁发布。`:git-<short-sha>` 固定到某一个确切提交。

这就是 `:main` 与某个具体发布标签可能同时显示不同镜像摘要的原因：`:main` 已经包含了该发布之后合入的所有内容，而版本标签始终冻结在那个发布上。

| 标签 | 指向 | 是否不可变？ |
| :--- | :--- | :--- |
| `:main`, `:latest` | `main` 分支的最新构建 | 否（滚动） |
| `:dev` | `dev` 分支的最新构建，即预发布版本 | 否（滚动） |
| `:vX.Y.Z`, `:X.Y.Z` | 某个特定的稳定发布版本 | 是 |
| `:X.Y` | 该次版本线的最新补丁发布 | 否（在该次版本内滚动） |
| `:git-<sha>` | 某个确切提交 | 是 |

对于可重现或生产部署，请固定到版本标签。想要最新构建就用 `:main`（或与之相同的 `:latest`）。想在正式发布前抢先体验下一个版本就用 `:dev`。

### 固定特定发布版本 {#specific-release-versions}

生产环境建议固定到具体版本，而不是使用浮动标签。将 `X.Y.Z` 替换为 [releases 页面](https://github.com/open-webui/open-webui/releases) 中的版本号：

```bash
docker pull ghcr.io/open-webui/open-webui:vX.Y.Z
docker pull ghcr.io/open-webui/open-webui:vX.Y.Z-slim
docker pull ghcr.io/open-webui/open-webui:vX.Y.Z-cuda
docker pull ghcr.io/open-webui/open-webui:vX.Y.Z-ollama
```

:::info Docker Hub
同样的镜像也以 `openwebui/open-webui` 的形式镜像到 Docker Hub，但只覆盖一部分：`latest`、`latest-<variant>` 以及裸的 `<variant>` 标签（例如 `slim`、`cuda`、`ollama`）跟随 `main`，而 `X.Y.Z` / `X.Y`（带或不带变体后缀）跟随发布版本。`:main`、`:dev`、`:vX.Y.Z` 和 `:git-<sha>` 只存在于 ghcr.io，因此本文档中的每条命令都使用 `ghcr.io/open-webui/open-webui`。
:::

---

## 常见配置 {#common-configurations}

### GPU 支持（Nvidia） {#gpu-support-nvidia}

```bash
docker run -d -p 3000:8080 --gpus all --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui --restart always ghcr.io/open-webui/open-webui:cuda
```

### 与 Ollama 打包在一起 {#bundled-with-ollama}

将 Open WebUI 和 Ollama 放在同一个容器中：

**使用 GPU：**
```bash
docker run -d -p 3000:8080 --gpus=all -v ollama:/root/.ollama -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui --restart always ghcr.io/open-webui/open-webui:ollama
```

**仅 CPU：**
```bash
docker run -d -p 3000:8080 -v ollama:/root/.ollama -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui --restart always ghcr.io/open-webui/open-webui:ollama
```

### 连接另一台服务器上的 Ollama {#connecting-to-ollama-on-a-different-server}

```bash
docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=https://example.com -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

### 单用户模式（无登录） {#single-user-mode-no-login}

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -e WEBUI_AUTH=False -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

:::warning
切换到单用户模式后，不能再无缝切回多账户模式。
:::

---

## 使用开发分支 {#using-the-dev-branch}

`:dev` 是 Open WebUI 的预发布通道，实际上就是每夜构建：镜像会随着变更合入 `dev` 分支而重建，而且每一处变更都会先落到那里，再落到别处。不存在单独的 beta 计划，因为 `dev` 承担了这个角色。到达它的变更不会被回退，因此下一个发布版本就是发布当天的 `dev`。

这带来两点值得了解的影响：

- **如果你在等一个修复，它很可能已经可以用了。** 查看 `dev` 上的[更新日志](https://github.com/open-webui/open-webui/blob/dev/CHANGELOG.md)，然后运行 `:dev`，而不是等正式发布。
- **如果你为他人运行 Open WebUI，测试预发布版本是避免意外的方式。** 在 `:dev` 上跑第二个实例，能让你的用户遇到下一个版本之前先看到它，并告诉你你的插件、模型和配置是否仍然行为正常。

是否运行它完全由你决定，而正是这些运行让发布变得更好。预发布版本的测试程度，取决于选择安装它的人的数量，而这个数字目前并不大。

配置方式与其他任何镜像相同，只需改动标签：

```bash
docker run -d -p 3001:8080 --add-host=host.docker.internal:host-gateway -v open-webui-dev:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui-dev --restart always ghcr.io/open-webui/open-webui:dev
```

:::warning 使用单独的卷
**绝不要在 dev 与生产之间共享数据卷。** Dev 构建可能包含发布镜像无法回读的数据库迁移，因此共享卷会让你无法再回到 `:main`。上面的 `-v open-webui-dev:/app/backend/data` 与快速开始中使用的 `open-webui` 是不同的卷，这是有意为之。容器名也不同，因此两者可以同时运行。
:::

任何在 `:dev` 上看起来不对的地方，都值得在 [GitHub](https://github.com/open-webui/open-webui/issues) 上报告。在这个阶段报告的问题会在发布前而不是发布后得到修复，这正是预发布版本存在的意义。

如果你不想使用 Docker，也可以参考[开发 Open WebUI](/getting-started/advanced-topics/development)。

---

## 卸载 {#uninstall}

### 使用 docker run 时 {#with-docker-run}

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
