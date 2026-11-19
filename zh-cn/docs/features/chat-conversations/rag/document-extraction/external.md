---
sidebar_position: 5
title: "外部文档提取"
---

# 外部文档提取 {#external-document-extraction}

内置引擎（Tika、Docling、Mistral OCR 等）适用于大多数情况，但有些场景需要其他方案。例如，你已有专有 OCR 工具或付费的云端提取 API，希望将重负载转移到配有专用 GPU 或大内存的机器，而不是占用 Open WebUI 服务器，或因合规要求需要在文本到达 Open WebUI 或模型前对 PII 脱敏。**external**（外部）引擎可将文档提取完全交给你自己编写和运行的 HTTP 服务。

因为这个服务由你掌控，它内部发生的事情也由你掌控。这带来了几种可能性，下面会详细说明：

- **按文件类型路由。** 只配置一个 URL，由你的服务在内部决定用哪个解析器或模型处理 `.xlsx`、`.pdf` 或其他类型。
- **把大文档拆分成多个可检索的片段。** 每张表、每页或每张幻灯片返回一个分块，而不是返回一个巨大的整体。
- **按用户执行不同逻辑。** Open WebUI 会在每次请求中转发发起请求的用户身份，因此你的服务可以实施访问规则，或把请求路由到特定客户的后端。
- **携带实时值的自定义请求头。** 可以配置诸如发起请求的用户邮箱或文件名这样的请求头，随每次提取请求一起发送，用于在你的服务上做路由、日志或访问控制。参见下方的[请求头](#the-contract)。
- **处理图片和视频。** 默认情况下，只有外部引擎会收到用于提取的图片和视频上传。一旦设置了 **Supported Media MIME Types**，媒体文件就会改为送往与该列表匹配的引擎。

## 配置 {#configuration}

在 **Settings > Documents**（管理员区域） 中把 **Content Extraction Engine** 设为 **External**，然后填写：

- **Document Loader URL**：你的服务的基础 URL。Open WebUI 会在其后追加 `/process`。
- **API Key**：必填。密钥以 Bearer 令牌的形式发送。选择 External 后若未保存密钥，Open WebUI 会退回内置加载器，不会调用你的服务，管理面板也不会提示。
- **Headers**（可选）：一个 JSON 对象，列出每次请求要额外发送的请求头，参见下方的[模板机制](#the-contract)。如果它不是有效的 JSON 对象，即使当前选中了其他引擎，**Save** 也会提示 `Headers must be a valid JSON object` 并且什么都不保存。请切回 **External** 来修正或清空该字段。

同样的设置也可以通过环境变量提供：[`CONTENT_EXTRACTION_ENGINE=external`](/reference/env-configuration#content_extraction_engine)、[`EXTERNAL_DOCUMENT_LOADER_URL`](/reference/env-configuration#external_document_loader_url)、[`EXTERNAL_DOCUMENT_LOADER_API_KEY`](/reference/env-configuration#external_document_loader_api_key)、[`EXTERNAL_DOCUMENT_LOADER_HEADERS`](/reference/env-configuration#external_document_loader_headers)。

## 接口约定 {#the-contract}

对每个文件，Open WebUI 都会发送：

```
PUT {EXTERNAL_DOCUMENT_LOADER_URL}/process
```

- **请求体**：未经修改的原始文件字节。
- **`Content-Type`**：检测到的文件 MIME 类型。
- **`Authorization`**：如果配置了 API 密钥，则为 `Bearer {EXTERNAL_DOCUMENT_LOADER_API_KEY}`。
- **`X-Filename`**：已存储的文件名 `<file id>_<original name>`，经过 URL 编码。在自定义请求头中使用 `{{FILE_NAME}}` 占位符，即可单独收到原始名称。
- 在 **Headers** / [`EXTERNAL_DOCUMENT_LOADER_HEADERS`](/reference/env-configuration#external_document_loader_headers) 中设置的任何请求头，一个带占位符模板的自定义请求头 JSON 对象：`{{FILE_ID}}`、`{{FILE_NAME}}`、`{{FILE_CONTENT_TYPE}}`、`{{USER_ID}}`、`{{USER_NAME}}`、`{{USER_EMAIL}}`、`{{USER_ROLE}}`、`{{USER_GROUPS}}`、`{{USER_GROUP_IDS}}`。
- 自动转发的用户身份：若设置了 [`FORWARD_USER_INFO_HEADER_JWT_SECRET`](/reference/env-configuration#forward_user_info_header_jwt_secret)，则以签名 JWT 的形式放在 `X-OpenWebUI-User-Jwt` 中；否则使用普通的 `X-OpenWebUI-User-Name`、`X-OpenWebUI-User-Id`、`X-OpenWebUI-User-Email` 和 `X-OpenWebUI-User-Role` 请求头。

你的服务应返回 `2xx` 状态码及 JSON 响应体。响应体可以是单个对象，也可以是对象列表：

```json
{
  "page_content": "extracted text for this document",
  "metadata": { "any": "extra fields you want stored alongside the chunk" }
}
```

如果返回列表，每个条目会生成一个可独立检索的 Document。这样就可以将一次上传拆分成多个片段，例如每张工作表、每页或每张幻灯片各占一个条目，而不是返回一个巨大的整体。非 2xx 响应或不含内容的响应都会导致提取失败，并向用户显示错误。

## 最小示例 {#minimal-example}

一个只实现了上述约定的朴素 FastAPI 服务，它返回占位内容而不是真实提取结果：

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()


@app.put("/process")
async def process(request: Request):
    filename = request.headers.get("x-filename", "")
    content_type = request.headers.get("content-type", "")
    file_bytes = await request.body()

    # TODO: replace with real extraction logic
    extracted_text = f"Placeholder text for {filename} ({len(file_bytes)} bytes)"

    return JSONResponse({
        "page_content": extracted_text,
        "metadata": {"source": filename, "content_type": content_type},
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

运行它（先 `pip install fastapi uvicorn`），然后把 **Document Loader URL** 设为从你的 Open WebUI 实例可以访问到的地址，例如本地部署时用 `http://localhost:5000`，共享 Docker 网络上用 `http://your-service:5000`。

## 参考 {#reference}

- [`CONTENT_EXTRACTION_ENGINE`](/reference/env-configuration#content_extraction_engine)
- [`EXTERNAL_DOCUMENT_LOADER_URL`](/reference/env-configuration#external_document_loader_url)
- [`EXTERNAL_DOCUMENT_LOADER_API_KEY`](/reference/env-configuration#external_document_loader_api_key)
- [`EXTERNAL_DOCUMENT_LOADER_HEADERS`](/reference/env-configuration#external_document_loader_headers)
