---
sidebar_position: 20
title: "Langfuse"
---

## 在 Open WebUI 中集成 Langfuse {#langfuse-integration-with-open-webui}

[Langfuse](https://langfuse.com/)（[GitHub](https://github.com/langfuse/langfuse)）为 Open WebUI 提供开源的可观测性与评估能力。启用 Langfuse 过滤器后，Open WebUI 中的每一次模型回复都会被发送到 Langfuse，从而为你带来：

- 应用[追踪（traces）](https://langfuse.com/docs/tracing)，包含每次回复的完整输入与输出
- 每次回复的 token 用量与延迟
- 按用户和模型统计的成本数据
- 把同一次对话的所有回复归拢在一起的会话
- [评估（Evaluations）](https://langfuse.com/docs/scores/overview)

## 如何将 Langfuse 集成到 Open WebUI {#how-to-integrate-langfuse-with-open-webui}

该集成是一个运行在 Open WebUI 内部的[过滤器函数](/features/extensibility/plugin/functions/filter)。它的 `inlet` 在消息发往模型时启动一次 Langfuse 生成（generation），`outlet` 则在回复结束后用回复内容及其 token 计数完成这次生成。

## 快速开始 {#quick-start-guide}

### 第 1 步：准备 Open WebUI {#step-1-setup-open-webui}

你需要有一个正在运行的 Open WebUI 实例，并且拥有该实例上的管理员账户。如果还没有，请参阅[入门指南](/getting-started)。

### 第 2 步：获取 Langfuse API 密钥 {#step-2-get-your-langfuse-api-keys}

在 [Langfuse Cloud](https://cloud.langfuse.com) 注册，或使用你自己的[自托管 Langfuse](https://langfuse.com/self-hosting)，创建一个项目并为它创建一对 API 密钥。你需要三个值：

- **公钥（public key）**（`pk-lf-...`）
- **密钥（secret key）**（`sk-lf-...`）
- **Langfuse URL**：Langfuse Cloud 为 `https://cloud.langfuse.com`，或你的密钥所属的 Langfuse 区域 / 服务器的 URL

### 第 3 步：添加 Langfuse 过滤器 {#step-3-add-the-langfuse-filter}

1. 前往 **管理面板 > 函数**。
2. 点击 **创建**（**+** 按钮）并选择 **新建函数**。
3. 粘贴下面的代码，然后点击 **保存**。

保存时，Open WebUI 会根据 `requirements` 这一行安装 `langfuse` 包。如果你的服务器上关闭了包安装（[`ENABLE_PIP_INSTALL_FRONTMATTER_REQUIREMENTS`](/reference/env-configuration#enable_pip_install_frontmatter_requirements) 或 [`OFFLINE_MODE`](/reference/env-configuration#offline_mode)），请自行把 `langfuse~=3.11` 安装到 Open WebUI 环境中。

```python
"""
title: Langfuse
author: open-webui
version: 1.0.0
license: MIT
description: Sends every chat reply to Langfuse, with its input, output, model, token usage, user and chat.
requirements: langfuse~=3.11
"""

import logging
from typing import Optional

from langfuse import Langfuse, propagate_attributes
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)


class Filter:
    class Valves(BaseModel):
        public_key: str = Field(default="", description="Langfuse public key (pk-lf-...)")
        secret_key: str = Field(default="", description="Langfuse secret key (sk-lf-...)")
        host: str = Field(default="https://cloud.langfuse.com", description="Langfuse URL")

    def __init__(self):
        self.valves = self.Valves()
        self.langfuse = None
        self.langfuse_settings = None

    def get_langfuse(self) -> Optional[Langfuse]:
        settings = (self.valves.public_key, self.valves.secret_key, self.valves.host)
        if not (self.valves.public_key and self.valves.secret_key):
            return None
        if settings != self.langfuse_settings:
            self.langfuse = Langfuse(
                public_key=self.valves.public_key,
                secret_key=self.valves.secret_key,
                host=self.valves.host,
            )
            self.langfuse_settings = settings
        return self.langfuse

    async def inlet(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __metadata__: Optional[dict] = None,
        __model__: Optional[dict] = None,
    ) -> dict:
        langfuse = self.get_langfuse()
        if langfuse is None or __metadata__ is None:
            return body

        try:
            chat_id = __metadata__.get("chat_id") or None
            model = __model__ or {}
            # Langfuse prices a reply by model id, so report the base model behind a workspace model
            model_id = model.get("info", {}).get("base_model_id") or body.get("model")

            with propagate_attributes(
                user_id=(__user__ or {}).get("email"),
                session_id=chat_id,
                trace_name="Open WebUI chat",
                tags=["open-webui"],
            ):
                __metadata__["langfuse_generation"] = langfuse.start_observation(
                    trace_context={"trace_id": Langfuse.create_trace_id(seed=chat_id)} if chat_id else None,
                    name="chat-reply",
                    as_type="generation",
                    model=model_id,
                    input=body.get("messages"),
                    metadata={"model_name": model.get("name")},
                )
        except Exception:
            log.exception("Langfuse: could not start the generation")

        return body

    async def outlet(self, body: dict, __metadata__: Optional[dict] = None) -> dict:
        generation = (__metadata__ or {}).pop("langfuse_generation", None)
        if generation is None:
            return body

        try:
            reply = body["messages"][-1]
            usage = reply.get("usage") or {}
            usage_details = None
            if usage.get("input_tokens") is not None:
                usage_details = {
                    "input": usage["input_tokens"],
                    "output": usage["output_tokens"],
                    "total": usage["total_tokens"],
                }

            generation.update(output=reply.get("content"), usage_details=usage_details)
            generation.end()
        except Exception:
            log.exception("Langfuse: could not finish the generation")

        return body
```

:::note

该过滤器固定使用 Langfuse Python SDK 的第 3 版。第 4 版需要比 Open WebUI 自带版本更新的 OpenTelemetry 包，而安装它会替换掉这些包，从而破坏 Open WebUI 自身的 [OpenTelemetry 支持](/reference/monitoring/otel)。第 3 版可与 Langfuse 服务端第 4 版配合使用。

:::

### 第 4 步：设置阀门并启用过滤器 {#step-4-set-the-valves-and-turn-the-filter-on}

1. 在 **管理面板 > 函数** 中，点击 Langfuse 过滤器旁边的齿轮图标（**Valves**）。
2. 填入 **Public Key**、**Secret Key** 和 **Host**（Langfuse URL），然后保存。
3. 用开关启用该过滤器。
4. 选择它的运行范围：
   - **所有模型**：打开过滤器的 **⋮** 菜单并开启 **全局**。
   - **指定模型**：前往 **工作区 > 模型**，编辑某个模型，并在 **过滤器** 下添加 Langfuse 过滤器。

过滤器会在第一次被追踪的回复时连接 Langfuse。如果之后修改了 **Host** 或 **Secret Key** 而 **Public Key** 保持不变，请重启 Open WebUI 以使改动生效。

:::note

大多数兼容 OpenAI 的服务商只有在被要求时才会报告流式回复的 token 计数。请为每个你想获取 token 计数与成本统计的模型开启 **Usage** 能力，参见[能力与绑定](/features/workspace/models#capabilities-and-bindings)。

:::

### 第 5 步：在 Langfuse 中查看追踪 {#step-5-see-your-traces-in-langfuse}

与任何启用了该过滤器的模型对话，然后在 Langfuse 中打开你的项目：

- 每次对话都是一条名为 **Open WebUI chat** 的追踪，带有 `open-webui` 标签。
- 该对话中的每次模型回复都是一次名为 **chat-reply** 的生成，发送的消息作为输入，回复作为输出，并记录 token 用量与延迟。
- 生成的模型为模型 ID。对于工作区模型，它是所基于的基础模型的 ID，这样 Langfuse 才能把它匹配到自己的价目表。用户选择的模型名称则记录在生成的元数据中。
- 用户是 Open WebUI 用户的邮箱地址，会话是对话 ID，因此 Langfuse 可以按对话和按人员归拢回复。

只要 [`ENABLE_API_OUTLET_FILTERS`](/reference/env-configuration#enable_api_outlet_filters) 处于开启状态（默认开启），对 Open WebUI API 的直接调用同样会被追踪，每次调用一条追踪。

## 了解更多 {#learn-more}

- [过滤器函数](/features/extensibility/plugin/functions/filter)：了解过滤器在 Open WebUI 中如何工作
- [Langfuse 文档](https://langfuse.com/docs)
