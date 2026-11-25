---
sidebar_position: 11
title: "路由模型"
---

路由模型和其他模型一样显示在模型选择器中。它收到每条消息后，会转发给一个实际模型作答。你可以指定选择规则。

常见用途：

- 将编程问题交给代码模型，其余问题交给费用较低的通用模型。
- 根据对话中的词语，让敏感内容只由本地模型处理。
- 盲测模型。为路由模型配置两个或更多默认模型，让它随机选择并隐藏所选模型，即可为[评估排行榜](/features/administration/evaluation)收集无偏评分。

## 创建路由模型 {#create-a-router-model}

打开管理区域的**设置 > 模型**，找到**路由模型**，点击 **+**。像创建其他模型一样填写名称和 ID，再添加规则。保存后，模型会出现在模型选择器中。

用户还需要有权访问路由模型调用的模型。设置路由模型的访问控制，指定谁可以选择它，并确保这些用户也可以使用它转发到的模型。

### 规则 {#rules}

路由模型按以下顺序检查规则，由第一条适用的规则决定使用哪个模型。

| 规则 | 匹配方式 |
| :--- | :--- |
| **模式** | 用不区分大小写的正则表达式匹配对话。第一条匹配的模式生效，无需调用**决策 API**。 |
| **条件** | 用自然语言描述条件，例如“用户询问编程问题”。调用一次**决策 API**为所有条件评分。最有可能的条件达到**阈值**时生效。 |
| **默认** | 没有适用的模式或条件时使用。 |

先检查模式，再检查条件。两类规则各自按列表顺序检查。

请至少添加一个默认模型。如果请求没有匹配任何规则，又没有默认模型，请求将失败。

### 默认模型 {#default-models}

添加一个或多个默认模型，然后选择**策略**。

- **第一个**始终使用列表顶部的模型。
- **随机**至少需要两个默认模型。没有适用的模式或条件时，该策略为每条消息随机选择一个默认模型，并隐藏所选模型，直到你打开回复评分。这是[评估](/features/administration/evaluation#1-blind-comparison-with-a-router-model)所用的盲测方法。

### 决策 API {#decisions-api}

条件需要由服务评分。在**决策 API**下设置**API 基础 URL**、**API 密钥**、**模型**和**阈值**（概率范围为 0 到 1，默认为 0.5）。该服务与[工具搜索](/features/extensibility/plugin/tools#tool-search)使用的服务类型相同。只有在没有匹配模式时才会调用该服务，每个请求最多调用一次。调用失败时，路由模型会回退到默认模型。

**阈值**下方的输入框显示“留空以使用默认提示词，或输入自定义提示词”。框内的文本用于设置发送到服务的输入。各个条件会作为独立问题一同发送，无需在提示词中重复。该输入框支持[消息和提示词修饰符](/features/workspace/prompts#message-and-prompt-modifiers)，例如 `{{MESSAGES:END:6|middletruncate:2000}}` 和 `{{prompt}}`。默认提示词包含近期聊天记录。自定义提示词如果不包含 `{{MESSAGES}}`，则不会发送聊天记录。

对已保存的聊天，模式和条件可以看到当前对话分支中截至新消息的内容。

## 通过环境变量配置 {#set-them-up-from-the-environment}

[`ROUTER_MODELS`](/reference/env-configuration#router_models)以 JSON 列表接收相同的规则，适合自动化部署。

```json
[
  {
    "id": "smart-router",
    "name": "Smart Router",
    "meta": {
      "routes": [
        { "model_id": "code-model", "pattern": "```|def |function " },
        { "model_id": "legal-model", "condition": "The user asks about contracts or legal questions" },
        { "model_id": "general-model" }
      ],
      "strategy": "first"
    },
    "config": {
      "decisions": {
        "api_base_url": "https://decisions.example.com/v1",
        "api_key": "<your key>",
        "model": "example-decisions-model",
        "threshold": 0.5,
        "prompt": ""
      }
    }
  }
]
```
