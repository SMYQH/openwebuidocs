---
sidebar_position: 5
title: "Tutorials"
---

## Pipeline 教程

:::danger Pipelines 已过时——请勿用于新部署
**Pipelines 已过时并被标记为 legacy，不再推荐使用。** Pipeline 可以以 **pipe** 或 **filter** 形式运行；这两种形式现在都有进程内的替代方案，它们内置、配置更简单、且无需额外的 worker 容器：

- Pipeline **pipe**（自定义 provider、RAG、请求路由）→ [Pipe Function](/features/extensibility/plugin/functions/pipe)
- Pipeline **filter**（消息预处理/后处理）→ [Filter Function](/features/extensibility/plugin/functions/filter)

本教程页面仅供现有部署参考。
:::

## 欢迎投稿教程

如果你在博客或 YouTube 上创作了关于自己 pipeline 配置的内容，欢迎与我们联系，我们非常乐意把它收录到此处！

## 精选教程

[使用 Filters 监控 Open WebUI](https://medium.com/@0xthresh/monitor-open-webui-with-datadog-llm-observability-620ef3a598c6)（@0xthresh 的 Medium 文章）

- 使用 DataDog LLM 可观测性监控 Open WebUI 的详细指南。

[构建自定义文本转 SQL Pipeline](https://www.youtube.com/watch?v=y7frgUWrcT4)（Jordan Nanos 的 YouTube 视频）

- 了解如何开发定制的文本转 SQL Pipeline，释放数据分析和提取的力量。

[Open-WebUI 文本转 SQL 演示和代码审查](https://www.youtube.com/watch?v=iLVyEgxGbg4)（Jordan Nanos 的 YouTube 视频）

- 关于利用 Open WebUI 支持的文本转 SQL 工具的实操演示和代码审查。

[使用 Open-WebUI 部署自定义文档 RAG Pipeline](https://github.com/Sebulba46/document-RAG-pipeline)（Sebulba46 的 GitHub 指南）

- 逐步指南，部署 Open-WebUI 和 Pipeline 容器，并使用本地 LLM API 创建自己的文档 RAG。
