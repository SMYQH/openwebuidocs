---
sidebar_position: 3
title: "Docling 文档提取"
---

:::warning

本教程由社区贡献，不在 Open WebUI 团队的支持范围内。它仅演示如何按实际需求自定义 Open WebUI。欢迎贡献，详情请参阅贡献教程。

:::

## Docling 文档提取 {#docling-document-extraction}

本文提供一个逐步指南，说明如何将 Docling 集成到 Open WebUI 中。Docling 是一个文档处理库，可将多种文件格式——包括 PDF、Word、电子表格、HTML 与图片——转换为 JSON 或 Markdown 等结构化数据。它内置版面检测、表格解析和语言感知处理能力，可通过统一且可扩展的接口，为搜索、总结与检索增强生成等 AI 场景简化文档准备流程。

## 前提条件 {#prerequisites}

- Open WebUI 实例
- 已在系统中安装 Docker
- 已为 Open WebUI 准备 Docker 网络

## 集成步骤 {#integration-steps}

### 第 1 步：运行 Docling-Serve 容器 {#step-1-run-docling-serve-container}

**基础 CPU 部署：**

```bash
docker run -p 5001:5001 \
  -e DOCLING_SERVE_ENABLE_UI=true \
  quay.io/docling-project/docling-serve
```

**GPU 部署（NVIDIA CUDA）：**

```bash
docker run --gpus all -p 5001:5001 \
  -e DOCLING_SERVE_ENABLE_UI=true \
  quay.io/docling-project/docling-serve-cu128
```

**推荐的生产环境 Docker Compose 部署：**

```yaml
services:
  docling-serve:
    image: quay.io/docling-project/docling-serve-cu128:latest
    container_name: docling-serve
    ports:
      - "5001:5001"
    environment:
      # Enable the web UI for testing
      - DOCLING_SERVE_ENABLE_UI=true
      # CRITICAL: Required for picture description with external LLM APIs
      - DOCLING_SERVE_ENABLE_REMOTE_SERVICES=true
      # Number of local engine workers
      - DOCLING_SERVE_ENG_LOC_NUM_WORKERS=2
      # CPU thread configuration
      - OMP_NUM_THREADS=4
      - MKL_NUM_THREADS=4
      # IMPORTANT: Keep at 1 to avoid "Task Not Found" errors
      - UVICORN_WORKERS=1
    restart: unless-stopped
    # For GPU support with NVIDIA:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

:::danger 重要：UVICORN_WORKERS 设置

使用默认的 `LocalOrchestrator` 时，如果 `UVICORN_WORKERS` 大于 1，就会遇到 **"Task Not Found (404)"** 错误。每个 worker 都在自己的内存中保存任务，因此另一个 worker 无法访问这些任务。

**除非你已配置 Redis 等共享状态机制，否则始终使用 `UVICORN_WORKERS=1`。**

:::

### 第 2 步：配置 Open WebUI {#step-2-configure-open-webui}

1. 登录你的 Open WebUI 实例
2. 前往 **设置** → **文档**（管理员区域）
3. 将 **Content Extraction Engine** 设置为 **Docling**
4. 将 **Docling Server URL** 设置为 `http://host.docker.internal:5001`（Docker）或 `http://localhost:5001`（原生部署）。默认值为 `http://docling:5001`。
5. 可选：设置 **API Key**（`DOCLING_API_KEY`），它会作为 `X-Api-Key` 请求头发送给 docling-serve
6. 保存更改

### 第 3 步：配置图片描述（可选） {#step-3-configure-picture-description-optional}

若要启用文档中的 AI 图片描述，请在 **文档** 标签中 Docling 设置的 **Parameters** JSON 字段中加入图片描述选项。共有两种模式：

- **local**：Vision 模型在 Docling 容器内部运行，通过 `picture_description_local` 配置
- **API**：Docling 调用外部服务（如 Ollama 或兼容 OpenAI 的端点），通过 `picture_description_api` 配置

:::danger API 模式的必要条件

当使用 `API` 模式（即调用 Ollama 等外部服务）时，你**必须**在 docling-serve 上设置以下环境变量：

```bash
DOCLING_SERVE_ENABLE_REMOTE_SERVICES=true
```

否则，Docling 会以 `OperationNotAllowed` 错误拒绝向外部服务发起请求。

:::

#### JSON 配置示例 {#json-configuration-examples}

请确保你的配置是**合法 JSON**！

:::warning 嵌套对象必须写成 JSON 字符串

Open WebUI 会把你填写的 Docling Parameters 值原样作为 multipart 表单字段转发给 docling-serve，不做重新编码。Docling 从 JSON **字符串** 中解析其嵌套选项（`picture_description_local`、`picture_description_api`、`picture_description_custom_config`），因此内联写出的对象无法被正确传输，上传会在 docling-serve 端报 `Invalid JSON for field ...` 错误。请像下面这样把这些值写成转义后的 JSON 字符串。普通值、布尔值和列表不需要转义。

:::

**本地模型配置：**

```json
{
  "do_picture_description": true,
  "picture_description_local": "{\"repo_id\": \"HuggingFaceTB/SmolVLM-256M-Instruct\", \"generation_config\": {\"max_new_tokens\": 200, \"do_sample\": false}, \"prompt\": \"Describe this image in a few sentences.\"}"
}
```

**API 配置（Ollama）：**

```json
{
  "do_picture_description": true,
  "picture_description_api": "{\"url\": \"http://host.docker.internal:11434/v1/chat/completions\", \"params\": {\"model\": \"llava:7b\"}, \"timeout\": 60, \"prompt\": \"Describe this image in great detail.\"}"
}
```

## Docling-Serve 环境变量参考 {#docling-serve-environment-variables-reference}

| 变量 | 默认值 | 说明 |
| -------- | ------- | ---- |
| `DOCLING_SERVE_ENABLE_UI` | `false` | 在 `/ui` 端点启用 Web UI |
| `DOCLING_SERVE_ENABLE_REMOTE_SERVICES` | `false` | **API 模式图片描述所必需** |
| `DOCLING_SERVE_ENG_LOC_NUM_WORKERS` | `1` | 本地引擎 worker 数量 |
| `DOCLING_SERVE_ARTIFACTS_PATH` | `/app/data` | 模型 artifacts 存储路径 |
| `UVICORN_WORKERS` | `1` | Uvicorn worker 数量（**务必保持为 1！**） |
| `OMP_NUM_THREADS` | `4` | CPU 处理时的 OpenMP 线程数 |
| `MKL_NUM_THREADS` | `4` | Intel MKL 线程数 |

## Docling 参数参考（Open WebUI） {#docling-parameters-reference-open-webui}

可通过 **设置 > 文档**（管理员区域） 中的 `DOCLING_PARAMS` JSON，或通过环境变量进行配置。

| 参数 | 类型 | 说明 | 允许值 |
| ----------- | ---- | ---- | ---------------- |
| `pdf_backend` | `string` | PDF 解析引擎 | `dlparse_v1`, `dlparse_v2`, `dlparse_v4`, `pypdfium2` |
| `table_mode` | `string` | 表格提取质量 | `fast`, `accurate` |
| `ocr_engine` | `string` | OCR 库 | `tesseract`, `easyocr`, `ocrmac`, `rapidocr` |
| `do_ocr` | `bool` | 是否启用 OCR | `true`, `false` |
| `force_ocr` | `bool` | 是否对数字 PDF 强制 OCR | `true`, `false` |
| `pipeline` | `string` | 处理复杂度 | `standard`, `fast` |
| `ocr_lang` | `list[string]` | OCR 语言 | 见下方说明 |

:::tip 语言代码

- **Tesseract**：使用 3 字母的 ISO 639-2 代码（例如 `eng`、`deu`、`fra`）
- **EasyOCR**：使用 2 字母的 ISO 639-1 代码（例如 `en`、`de`、`fr`）
:::

**配置示例：**

```json
{
  "do_ocr": true,
  "pdf_backend": "dlparse_v4",
  "table_mode": "accurate",
  "ocr_engine": "tesseract",
  "ocr_lang": ["eng"]
}
```

## 验证集成 {#verifying-the-integration}

1. 访问 Docling UI：`http://127.0.0.1:5001/ui`
2. 上传一个测试文档，确认它能返回 markdown 输出
3. 在 Open WebUI 中向知识库上传一个文件，确认处理流程可成功完成

## 故障排查 {#troubleshooting}

### "Task result not found. Please wait for a completion status." {#task-result-not-found-please-wait-for-a-completion-status}

**原因：** 使用了多个 Uvicorn worker，而任务存储又是内存级别。

**解决方案：** 在 docling-serve 配置中将 `UVICORN_WORKERS=1`。

### "Connections to remote services is only allowed when set explicitly" {#connections-to-remote-services-is-only-allowed-when-set-explicitly}

**原因：** 图片描述的 API 模式需要显式开启对外服务访问。

**解决方案：** 在 docling-serve 环境变量中加入 `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=true`。

### `/v1alpha/convert/file` 返回 404 Not Found {#404-not-found-on-v1alphaconvertfile}

**原因：** 使用了过旧版本的 docling-serve 或 Open WebUI。

**解决方案：**

- 将 Open WebUI 更新到最新版本
- 将 docling-serve 更新到 v1.0 或更高版本

### docling-serve 日志中的 "Invalid JSON for field ..." {#invalid-json-for-field--in-the-docling-serve-logs}

**原因：** 某个嵌套的 Docling 参数被写成了内联对象。Open WebUI 会把 Docling 参数原样作为表单字段透传，因此 Docling 收到的是该对象的各个键，而不是对象本身。

**解决方案：** 把 `picture_description_api` 之类的嵌套值写成经过转义的 JSON 字符串。参见 [JSON 配置示例](#json-configuration-examples)。

### OCR 不工作或语言识别错误 {#ocr-not-working-or-incorrect-language-detection}

**原因：** 针对当前 OCR engine，`ocr_lang` 使用了错误格式。

**解决方案：**

- Tesseract 使用 3 字母代码：`["eng", "deu"]`
- EasyOCR 使用 2 字母代码：`["en", "de"]`

### 引用指向错误的页码 {#citations-point-to-the-wrong-page}

**原因**：Docling 在其 Markdown 输出中只标记页码变化，因此空白页不会留下分页符。以这些分页符计数得到的页码会使空白页之后的每条引用都显示更早的页码。Open WebUI 从 Docling 与 Markdown 一同返回的 JSON 输出中获取页码。

**解决方案**：在 **设置 > 文档**（管理员区域） 中运行 **重建知识库与记忆向量索引**，它会重新提取每个知识库文件；对于不在知识库中的受影响文件，请重新上传一次。页码是在 Docling 提取文件时确定的。

### "Error calling Docling" 但没有具体细节 {#error-calling-docling-with-no-specific-details}

**排查步骤：**

1. 查看 docling-serve 日志：`docker logs docling-serve`
2. 直接通过 `http://localhost:5001/ui` 测试 Docling
3. 验证 Open WebUI 与 docling-serve 容器之间的网络连通性

## 结论 {#conclusion}

将 Docling 集成到 Open WebUI 后，文档处理能力会明显增强。需要牢记的关键点包括：

- **始终设置 `UVICORN_WORKERS=1`**，避免任务路由问题
- 在使用 API 模式图片描述时，**务必开启 `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=true`**
- 在所有配置字段中，**务必校验 JSON 语法**
