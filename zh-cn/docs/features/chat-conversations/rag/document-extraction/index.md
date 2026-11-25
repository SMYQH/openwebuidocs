---
sidebar_position: 1
title: "文档提取"
---

## Open WebUI 中的文档提取 {#document-extraction-in-open-webui}

Open WebUI 提供强大的文档提取能力，使你可以在 RAG（Retrieval Augmented Generation）工作流中处理并分析多种类型的文档。文档提取是把非结构化文档内容转换为结构化数据的关键步骤，从而让语言模型更有效地使用这些内容。

## 什么是文档提取？ {#what-is-document-extraction}

文档提取指的是自动识别并提取各种文件格式中的文本与数据的过程，其中包括：

- PDF（文本型和扫描版）
- 含文字的图片
- 手写文档
- 以及更多格式

通过恰当的文档提取，Open WebUI 可以帮助你：

- 将基于图像的文档转换为可搜索文本
- 保留文档结构与版面信息
- 以结构化格式提取数据，供后续处理
- 支持多语言内容识别

### 临时聊天中的文档附件 {#document-attachments-in-temporary-chats}

在**临时聊天**中附加本地文档时，浏览器会提取文本，不会将原始文档作为 Open WebUI 文件上传。发送消息时，提取的文本会作为聊天请求的一部分发送给 Open WebUI 后端。

浏览器在这一步使用内置解析器。PDF 提取会读取文本层并用空格连接文本项，不执行 OCR，因此扫描页可能无法提取到文本，表格布局也可能丢失。DOCX 提取返回纯文本。如果需要服务器配置的提取引擎，请使用普通聊天。

:::info 将图片和视频发送到提取引擎

上传的图片或视频会按原样保存，供视觉模型查看，而不会经过提取引擎处理。[`external` 引擎](/features/chat-conversations/rag/document-extraction/external)默认会接收媒体。

[`CONTENT_EXTRACTION_SUPPORTED_MEDIA_MIME_TYPES`](/reference/env-configuration#content_extraction_supported_media_mime_types)（或者 **设置 > 文档**（管理员区域） 中的 **支持的媒体 MIME 类型**）允许你自行选择：列出你的引擎能够读取的 MIME 类型，例如 OCR 引擎对应 `image/*`；此后匹配的上传文件无论使用哪个引擎都会被提取。如果在管理面板中把该字段留空保存，或把该变量设为空字符串，就会存储一个空列表，从而对包括 `external` 在内的所有引擎关闭媒体提取。

:::

## PDF 加载器模式 {#pdf-loader-mode}

使用默认的**内容提取引擎**时，**设置 > 文档**（管理员区域）中的 **PDF Loader Mode**，或 [`PDF_LOADER_MODE`](/reference/env-configuration#pdf_loader_mode)，决定 PDF 的页面在切块之前如何转换成文本。其他引擎会忽略该设置。

| | **Page**（默认） | **Single** |
| --- | --- | --- |
| 文本 | 每页一个文档 | 所有页面合并为一个文档 |
| 语块 | 不会跨页 | 可以跨页 |
| 引用 | 显示 `(page N)` 并打开到该页的 PDF | 不显示页码 |

当句子或表格经常延续到下一页，并且你可以不使用引用页码时，选择 **Single**。该模式在文件被提取时生效。已经在知识库中的文件，只有在同一设置页面执行 **Reindex Knowledge and Memory Vectors**、重新提取之后才会改变。

## ODT、MSG 和 PowerPoint 的依赖项 {#dependencies-for-odt-msg-and-powerpoint}

在非精简版安装中，默认的**内容提取引擎**使用下列解析器处理这些格式。

| 格式 | 提取依赖项 |
| --- | --- |
| OpenDocument Text (`.odt`) | 需要 `unstructured`、`pypandoc` 及 Pandoc 可执行文件。解析器先将文件转换为 DOCX，再提取文本。 |
| Outlook 邮件 (`.msg`) | 需要 `unstructured` 和 `python-oxmsg` 来处理 Outlook MSG 内容。Open WebUI 会跳过邮件附件。 |
| PowerPoint (`.ppt`、`.pptx`) | 如果能导入 `unstructured`，就使用它。导入失败时，Open WebUI 会尝试使用可读取 `.pptx` 文件的 `python-pptx`。旧版二进制 `.ppt` 文件需要支持该格式的提取器。 |

PowerPoint 的回退机制发生在选择加载器时。如果成功导入 `unstructured`，但随后解析失败，则不会触发回退。

**允许的文件扩展名**决定哪些上传文件会被接受处理。要编制 RAG 索引，所选提取器还必须能读取文件。能否预览取决于文件查看器。

## 没有专用加载器的文件 {#files-without-a-dedicated-loader}

使用默认的**内容提取引擎**时，扩展名没有专用加载器的文件会按纯文本读取。源代码和配置文件，例如 `.py`、`.js`、`.ts`、`.go`、`.sql`、`.json`、`.yaml` 或 `.toml`，在 RAG 中就是这样工作的。没有加载器的二进制格式，例如 `.ods` 或 `.odp`，同样按此方式读取，产生的不是错误而是一堆无法辨认的文本，因此检索会从中返回噪声。在 slim 镜像上，这类文件则直接失败并提示 `This file type requires an external document extractor in slim. Configure one that supports it.`。

若只想接受你清楚知道能良好提取的格式，请在 **设置 > 文档**（管理员区域）的 **Allowed File Extensions** 中列出它们（不带前导的点），或写入 [`RAG_ALLOWED_FILE_EXTENSIONS`](/reference/env-configuration#rag_allowed_file_extensions)。此后上传其他扩展名的文件会失败并提示 `File type <extension> is not allowed`。

## 可用提取方式 {#available-extraction-methods}

Open WebUI 支持多种文档提取引擎，以适配不同需求与文档类型。每种提取方式都有各自优势，适合不同场景。

你可以查阅各个提取方式的专门文档，了解如何配置并在 Open WebUI 实例中有效使用它们。其中有四个引擎尚无独立页面：Datalab Marker、MinerU、Azure Document Intelligence 和 PaddleOCR-VL。它们的配置项列在[环境变量参考](/reference/env-configuration#rag-content-extraction-engine)中。
