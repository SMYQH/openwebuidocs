---
sidebar_position: 2
title: "Filters"
---

## Filters

:::danger Pipelines 已过时——请勿用于新部署
**Pipelines 已过时并被标记为 legacy，不再推荐使用。** Pipeline 可以以 **pipe** 或 **filter** 形式运行；这两种形式现在都有进程内的替代方案，它们内置、配置更简单、且无需额外的 worker 容器：

- Pipeline **pipe**（自定义 provider、RAG、请求路由）→ [Pipe Function](/features/extensibility/plugin/functions/pipe)
- Pipeline **filter**（消息预处理/后处理）→ [Filter Function](/features/extensibility/plugin/functions/filter)

本页面仅供现有部署参考。
:::

Filters 用于对传入的用户消息和传出的助手（LLM）消息执行操作。过滤器中可以执行的操作包括：将消息发送到监控平台（如 Langfuse 或 DataDog）、修改消息内容、屏蔽有毒消息、将消息翻译成另一种语言，或对特定用户的消息进行速率限制。示例列表维护在 [Pipelines 仓库](https://github.com/open-webui/pipelines/tree/main/examples/filters)中。Filters 可以作为 Function 执行，也可以在 Pipelines 服务器上执行。一般工作流如下图所示。

<div align="center">
  <a href="#">
    ![Filter Workflow](/images/pipelines/filters.png)
  </a>
</div>

在模型或 Pipe 上启用过滤器 Pipeline 后，来自用户的传入消息（即"inlet"）会传递给过滤器进行处理。过滤器在向 LLM 模型请求对话完成之前对消息执行所需的操作。最后，过滤器在将传出的 LLM 消息（即"outlet"）发送给用户之前对其进行后处理。
