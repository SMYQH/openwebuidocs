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

:::note 临时聊天中的隐私
在 **临时聊天** 模式下，文档提取会**仅在浏览器中执行**，以防止数据在后端被存储或处理。由于这一严格隐私策略，某些依赖后端解析器的复杂文件格式（例如部分 DOCX 文件）可能无法被正确处理。
:::

:::info 将图片和视频发送到提取引擎

上传的图片或视频会按原样保存，供视觉模型查看，而不会经过提取引擎处理。[`external` 引擎](/features/chat-conversations/rag/document-extraction/external)默认会接收媒体。

[`CONTENT_EXTRACTION_SUPPORTED_MEDIA_MIME_TYPES`](/reference/env-configuration#content_extraction_supported_media_mime_types)（或者 **设置 > 文档**（管理员区域） 中的 **支持的媒体 MIME 类型**）允许你自行选择：列出你的引擎能够读取的 MIME 类型，例如 OCR 引擎对应 `image/*`；此后匹配的上传文件无论使用哪个引擎都会被提取。如果在管理面板中把该字段留空保存，或把该变量设为空字符串，就会存储一个空列表，从而对包括 `external` 在内的所有引擎关闭媒体提取。

:::

## 可用提取方式 {#available-extraction-methods}

Open WebUI 支持多种文档提取引擎，以适配不同需求与文档类型。每种提取方式都有各自优势，适合不同场景。

你可以查阅各个提取方式的专门文档，了解如何配置并在 Open WebUI 实例中有效使用它们。其中有四个引擎尚无独立页面：Datalab Marker、MinerU、Azure Document Intelligence 和 PaddleOCR-VL。它们的配置项列在[环境变量参考](/reference/env-configuration#rag-content-extraction-engine)中。
