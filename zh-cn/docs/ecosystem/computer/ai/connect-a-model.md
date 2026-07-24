---
title: 连接模型（API 密钥和 Ollama）
sidebar_position: 2
---

# 连接模型（API 密钥和 Ollama）

前往**设置 → 管理 → 连接**并添加一个连接。有两种提供商类型：**OpenAI** 和 **Anthropic**。没有单独的"Ollama"或"OpenAI 兼容"类型：任何使用 OpenAI API 的服务（Ollama、OpenRouter、vLLM、LM Studio、Groq……）都以提供商 **OpenAI** 添加，并带有自定义基础 URL。

## 连接字段

| 字段 | 作用 |
| --- | --- |
| **名称** | 连接的可选显示名称 |
| **提供商** | `OpenAI` 或 `Anthropic` |
| **API 类型** | 仅 OpenAI：聊天补全或响应 |
| **基础 URL** | 必需。例如 `https://api.openai.com/v1`、`http://localhost:11434/v1` |
| **API 密钥** | 必需。Ollama 会忽略该值，但字段不能为空 |
| **前缀 ID** | 可选命名空间，添加到模型 ID 前面，例如 `openrouter/gpt-4o` |
| **模型** | 可选的逗号分隔列表。留空以自动发现 |

## Ollama

- **提供商：** OpenAI
- **基础 URL：** `http://localhost:11434/v1`
- **API 密钥：** 任意文本（`ollama` 就可以）；Ollama 不检查它，但字段不能为空

你已拉取的模型会自动发现并出现在模型选择器中。

## OpenRouter

- **提供商：** OpenAI
- **基础 URL：** `https://openrouter.ai/api/v1`
- **API 密钥：** 你的 OpenRouter 密钥

OpenRouter 暴露许多模型；设置一个**前缀 ID** 如 `openrouter`，使其模型带有命名空间（`openrouter/gpt-4o`），避免与其他连接的模型冲突。

## Anthropic

- **提供商：** Anthropic
- **基础 URL：** `https://api.anthropic.com/v1`
- **API 密钥：** 你的 Anthropic 密钥

## 模型发现、默认值、启用

- **自动发现：** 模型字段留空时，Computer 查询提供商的 `/models` 端点并列出返回的所有内容。
- **手动列表：** 在模型字段中输入逗号分隔的列表，仅暴露这些模型。这对于拥有庞大目录或没有 `/models` 路由的端点很有用。
- **启用/禁用：** 可以单独切换模型的开启或关闭，因此选择器只显示你实际使用的模型。
- **默认模型：** 在设置中设置新聊天的默认模型（配置键 `chat.default_model`）。

偏好订阅而不是 API 密钥？参见[使用你的编码代理订阅](./coding-agents)。
