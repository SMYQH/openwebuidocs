---
sidebar_position: 2
title: "Apache Tika 提取"
---

:::warning

本教程由社区贡献，Open WebUI 团队不提供支持。它仅演示如何针对你的使用场景自定义 Open WebUI。想投稿？请查看教程投稿指南。

:::

## Apache Tika 提取 {#apache-tika-extraction}

本文提供一个逐步指南，说明如何将 Apache Tika 集成到 Open WebUI 中。Apache Tika 是一个内容分析工具包，可用于检测并提取一千多种文件类型中的元数据与文本内容。所有这些文件类型都可通过统一接口解析，因此 Tika 在搜索引擎索引、内容分析、翻译等场景中都非常有用。

## 前提条件 {#prerequisites}

- Open WebUI 实例
- 已在系统中安装 Docker
- 已为 Open WebUI 准备 Docker 网络

# 集成步骤 {#integration-steps}

### 第 1 步：创建 Apache Tika 的 Docker Compose 文件，或直接运行 Docker 命令 {#step-1-create-a-docker-compose-file-or-run-the-docker-command-for-apache-tika}
你有两种方式运行 Apache Tika：

**方式 1：使用 Docker Compose**

在与你的 Open WebUI 实例相同目录下创建一个名为 `docker-compose.yml` 的新文件，并加入以下配置：

```yml
services:
  tika:
    image: apache/tika:latest-full
    container_name: tika
    ports:
      - "9998:9998"
    restart: unless-stopped
```

执行以下命令，使用 Docker Compose 文件启动服务：

```bash
docker compose up -d
```

**方式 2：使用 Docker Run 命令**

也可以用以下 Docker 命令直接启动 Apache Tika：

```bash
docker run -d --name tika \
  -p 9998:9998 \
  --restart unless-stopped \
  apache/tika:latest-full
```

请注意：如果你选择使用 Docker run，并且希望让该容器与 Open WebUI 处于同一个网络中，则需要显式加上 `--network` 参数。

### 第 2 步：配置 Open WebUI 使用 Apache Tika {#step-2-configure-open-webui-to-use-apache-tika}

若要在 Open WebUI 中把 Apache Tika 作为上下文提取引擎，请按以下步骤操作：

- 登录你的 Open WebUI 实例
- 进入 `管理面板`
- 点击 `设置`
- 打开 `文档` 标签
- 将 **Content Extraction Engine** 设置为 **Tika**
- 将 **Tika Server URL** 设置为 `http://tika:9998`
- 将 **Tika Server Version** 设置为与正在运行的服务器一致，即 **Tika 3.x** 或 **Tika 4.x**。两个大版本暴露的端点不同，版本不匹配会让提取失败，即便服务器本身运行正常。默认为 **Tika 3.x**，同样的选择也可以通过 [`TIKA_SERVER_VERSION`](/reference/env-configuration#tika_server_version) 设置。**Tika 4.x** 还会提取为 Markdown 而非纯文本，因此标题、列表和表格能保留完整结构传给模型。
- 保存更改

## 在 Docker 中验证 Apache Tika {#verifying-apache-tika-in-docker}

若要验证 Apache Tika 在 Docker 环境中是否正常工作，可按以下步骤进行：

### 1. 启动 Apache Tika Docker 容器 {#1-start-the-apache-tika-docker-container}

首先，确保 Apache Tika Docker 容器已经运行。你可以使用以下命令启动：

```bash
docker run -p 9998:9998 apache/tika
```

此命令会启动 Apache Tika 容器，并将容器的 9998 端口映射到本机的 9998 端口。

### 2. 验证服务是否正常运行 {#2-verify-the-server-is-running}

你可以通过发送 GET 请求来验证 Apache Tika 服务是否已启动：

```bash
curl -X GET http://localhost:9998/tika
```

此命令应返回以下响应：

```txt
This is Tika Server. Please PUT
```

### 3. 验证集成 {#3-verify-the-integration}

向知识库上传一个小型、文本可选中的 PDF。打开文件的**已索引文本**选项卡，查找 PDF 中你能识别的句子。即使选择了 Tika，Open WebUI 也会在本地读取纯文本文件，因此请用 PDF 验证 Tika 提取流程。

如果能提取可选中的文本，但无法从扫描版 PDF 中提取文本，请检查 Tika 服务器日志及其 OCR 设置。PDF 预览显示的是原始文件。请查看**已索引文本**来确认提取结果。

## 故障排查 {#troubleshooting}

- 确保 Apache Tika 服务正在运行，并且 Open WebUI 实例可以访问它
- 查看 Docker 日志，确认 Apache Tika 服务没有报错
- 确认 Open WebUI 中配置的 **Tika Server URL** 正确无误

### 上传时连接被拒绝 {#connection-refused-during-upload}

Open WebUI 后端负责将文档发送给 Tika。如果在 Docker 宿主机上测试成功，但上传失败并显示 `Connection refused`，请从 Open WebUI 容器内检查 URL。

- 在共享 Compose 网络中，使用 Tika 服务名和容器端口，例如 `http://tika:9998`。
- 在 Docker Desktop 上，如果 Tika 在宿主机上发布了端口，请使用 `http://host.docker.internal:9998`，并将 `9998` 替换为宿主机上发布的端口。参阅 [Docker Desktop 网络文档](https://docs.docker.com/desktop/features/networking/#i-want-to-connect-from-a-container-to-a-service-on-the-host)。

将 **Tika 服务器 URL** 设为容器可访问的地址，再向知识库上传一个 PDF 来验证提取结果。

## 集成优势 {#benefits-of-integration}

将 Apache Tika 集成到 Open WebUI 可带来以下优势：

- **更强的元数据提取能力**：Apache Tika 能从文件中提取准确、相关的元数据
- **支持多种文件格式**：Apache Tika 支持大量文件格式，非常适合需要处理多样文档类型的组织
- **增强内容分析能力**：Apache Tika 的高级内容分析能力可以帮助你从文件中提取更多有价值的信息

## 结论 {#conclusion}

将 Apache Tika 集成到 Open WebUI 并不复杂，还能增强 Open WebUI 实例的元数据提取能力。按本文步骤操作，即可将 Apache Tika 设置为 Open WebUI 的上下文提取引擎。
