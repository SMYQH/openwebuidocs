---
sidebar_position: 40
title: "S3 存储"
---

# 🪣 切换到 S3 存储 {#switching-to-s3-storage}

:::warning
本教程由社区贡献，Open WebUI 团队不提供支持。它仅演示如何按具体使用场景自定义 Open WebUI。想参与贡献？请查看贡献教程。
:::

本指南介绍如何将 Open WebUI 配置中默认的 `local` 存储切换为 Amazon S3。

## 前提条件 {#prerequisites}

在学习本教程之前，您需要具备以下条件：

- 一个有效的 AWS 账户
- AWS Access Key 和 Secret Key，或默认 AWS 凭据链可找到的其他凭据（例如 IAM 角色）
- 在 S3 中创建和上传对象所需的 AWS IAM 权限
- 已在系统上安装 Docker

## 什么是 Amazon S3 {#what-is-amazon-s3}

直接引用 AWS 官网的说明：

"Amazon S3 是一项对象存储服务，具有业界领先的可扩展性、数据可用性、安全性和性能。可存储和保护任意数量的数据，适用于数据湖、网站、云原生应用、备份、归档、机器学习和分析等各类使用场景。Amazon S3 专为 99.999999999%（11 个 9）的持久性而设计，为全球数百万客户存储数据。"

了解更多关于 S3 的信息，请访问：[Amazon S3 官方页面](https://aws.amazon.com/s3/)

# 配置方法 {#how-to-set-up}

## 1. 所需环境变量 {#1-s3-environment-variables}

配置 S3 前，请准备以下环境变量。只有 `S3_BUCKET_NAME` 是必填项，参见步骤 2：

| **Open-WebUI 环境变量** | **示例值** |
|-------------------------------------|---------------------------------------------|
| `S3_ACCESS_KEY_ID`                  | ABC123                                      |
| `S3_SECRET_ACCESS_KEY`              | SuperSecret                                 |
| `S3_ENDPOINT_URL`                   | https://s3.us-east-1.amazonaws.com          |
| `S3_REGION_NAME`                    | us-east-1                                   |
| `S3_BUCKET_NAME`                    | my-awesome-bucket-name                      |

- S3_ACCESS_KEY_ID：您 AWS 账户访问密钥的标识符，可在 AWS 管理控制台或 AWS CLI 中创建访问密钥时获取。
- S3_SECRET_ACCESS_KEY：AWS 访问密钥对的密钥部分，在 AWS 中创建访问密钥时提供，请妥善保存。
- S3_ENDPOINT_URL：指向 S3 服务端点的 URL，通常可在 AWS 服务文档或账户设置中找到。
- S3_REGION_NAME：S3 存储桶所在的 AWS 区域，例如 "us-east-1"，可在 AWS 管理控制台的 S3 存储桶详情中查看。
- S3_BUCKET_NAME：您在 AWS 中创建存储桶时指定的唯一名称。

有关可用 S3 端点 URL 的完整列表，请参阅：[Amazon S3 常规端点](https://docs.aws.amazon.com/general/latest/gr/s3.html)

有关所有 `Cloud Storage` 配置选项，请参阅 [Open-WebUI 云存储配置](/reference/env-configuration#cloud-storage) 文档。

## 2. 运行 Open-WebUI {#2-run-open-webui}

在启动 Open-WebUI 实例之前，还需要设置最后一个环境变量 `STORAGE_PROVIDER`。该变量告知 Open-WebUI 你要使用哪个存储提供商。默认情况下，`STORAGE_PROVIDER` 为 `local`；如果值为空或无法识别，启动会直接失败并提示 "Unsupported storage provider"。使用 `s3` 时，每次上传的文件会先写入 `/app/backend/data/uploads`，然后再复制到存储桶；每次读取时对象也会被下载回该目录，因此本地数据卷依然必不可少。

| **存储提供商** | **类型** | **描述** | **默认值** |
|----------------------|----------|-------------------------------------------------------------------------------------------------|-------------|
| `local`              | str      | 文件保留在 `/app/backend/data/uploads` 下                                                    | 是         |
| `s3`                 | str      | 使用 S3 客户端库及 Amazon S3 存储中提到的相关环境变量         | 否          |
| `gcs`                | str      | 使用 GCS 客户端库及 Google Cloud Storage 中提到的相关环境变量     | 否          |
| `azure`              | str      | 使用 Azure Blob Storage 客户端，配合 `AZURE_STORAGE_ENDPOINT` 与 `AZURE_STORAGE_CONTAINER_NAME`，以及 `AZURE_STORAGE_KEY`；若不提供该密钥则使用默认的 Azure 凭据 | 否          |

要使用 Amazon S3，需要将 `STORAGE_PROVIDER` 设置为 `s3`（小写，取值按精确匹配），并配置步骤 1 中收集的环境变量。严格来说只有 `S3_BUCKET_NAME` 是必填项，通常还需要 `S3_REGION_NAME`：如果不设置 `S3_ACCESS_KEY_ID` 和 `S3_SECRET_ACCESS_KEY`，则会使用默认的 AWS 凭据链（例如 IAM 角色）；而 `S3_ENDPOINT_URL` 只有在使用兼容 S3 的服务时才需要。此外还可以使用 `S3_KEY_PREFIX`、`S3_ADDRESSING_STYLE`（MinIO 风格的端点用 `path`）、`S3_USE_ACCELERATE_ENDPOINT` 和 `S3_ENABLE_TAGGING`。

这里还将 `ENV` 设置为 "dev"，这样可以查看 Open-WebUI 的 Swagger 文档，以便进一步测试并确认 S3 存储配置是否正常工作。

```sh
docker run -d \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  -e STORAGE_PROVIDER="s3" \
  -e S3_ACCESS_KEY_ID="ABC123" \
  -e S3_SECRET_ACCESS_KEY="SuperSecret" \
  -e S3_ENDPOINT_URL="https://s3.us-east-1.amazonaws.com" \
  -e S3_REGION_NAME="us-east-1" \
  -e S3_BUCKET_NAME="my-awesome-bucket-name" \
  -e ENV="dev" \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

## 3. 测试配置 {#3-test-the-set-up}

现在 Open-WebUI 已经运行，让我们上传一个简单的 `Hello, World` 文本文件来测试配置。

![在 Open-WebUI 中上传文件](/images/tutorials/amazon-s3/amazon-s3-upload-file.png)

并确认我们能从所选 LLM 获得响应。

![在 Open-WebUI 中获取响应](/images/tutorials/amazon-s3/amazon-s3-oui-response.png)

很好！看起来 Open-WebUI 中的一切都按预期运行了。现在让我们验证文本文件是否确实已上传并存储在指定的 S3 存储桶中。通过 AWS 管理控制台可以看到，S3 存储桶中现在有一个文件。除了我们上传的文件名（`hello.txt`）外，还可以看到对象名称前面加上了一个唯一 ID（即 `<file-id>_hello.txt`；如果设置了 `S3_KEY_PREFIX`，则该前缀位于更前面）。这就是 Open-WebUI 追踪所有已上传文件的方式。

![S3 存储桶中的对象](/images/tutorials/amazon-s3/amazon-s3-object-in-bucket.png)

使用 Open-WebUI 的 Swagger 文档，我们可以通过 `/api/v1/files/{id}` 端点并传入唯一 ID（4405fabb-603e-4919-972b-2b39d6ad7f5b）获取该文件的所有相关信息。

![按 ID 查看文件](/images/tutorials/amazon-s3/amazon-s3-get-file-by-id.png)
