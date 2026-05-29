---
title: 环境变量
sidebar_position: 3
---

# 环境变量

所有变量在启动时读取一次；重启服务器以应用更改。

## 核心

| 变量 | 默认值 | 作用 |
| --- | --- | --- |
| `CPTR_DATA_DIR` | `~/.cptr` | 数据库、配置、上传和日志的数据目录。Docker 镜像将其设置为 `/data`。 |
| `CPTR_LOG_LEVEL` | `INFO` | 服务器日志级别。 |
| `CPTR_LOG_FORMAT` | `text` | `text` 或 `json`（结构化输出，用于日志收集器）。 |
| `CPTR_AUDIT_LOG_LEVEL` | `NONE` | `NONE` 禁用审计日志；`METADATA` 记录变异；`REQUEST` 添加经过编辑的请求体；`REQUEST_RESPONSE` 添加经过编辑的响应体。 |
| `CPTR_AUDIT_LOG_PATH` | `<data>/logs/audit.jsonl` | 审计日志文件位置。 |
| `CPTR_AUDIT_LOG_ROTATION` | `10 MB` | 审计日志轮转大小。 |
| `CPTR_AUDIT_MAX_BODY_SIZE` | `2048` | 每条审计记录捕获的请求/响应体最大字节数。 |
| `CPTR_AUDIT_EXCLUDED_PATHS` | `/api/chats,/v1/chat` | 从审计日志中排除的路径。 |
| `CPTR_LOG_UPSTREAM_REQUESTS` | `false` | 记录出站的模型 API 请求，用于调试模型调用。 |
| `CPTR_UPSTREAM_REQUEST_LOG_PATH` | `<data>/logs/upstream-requests.jsonl` | 上游请求日志位置。 |
| `CPTR_UPSTREAM_REQUEST_LOG_ROTATION` | `50 MB` | 上游请求日志轮转大小。 |

## 聊天和代理调优

| 变量 | 默认值 | 作用 |
| --- | --- | --- |
| `CHAT_MAX_ITERATIONS` | `2048` | 每次轮次中代理在停止前的最大工具调用迭代次数。 |
| `ENABLE_CHAT_RECONCILE_ON_STARTUP` | `true` | 启动时，恢复因崩溃而卡住的聊天。 |
| `CHAT_TOOL_MAX_CHARS` | `50000` | 工具的输出保留在上下文中的最大字符数。 |
| `CHAT_TOOL_COMMAND_MAX_CHARS` | `8000` | 命令输出保留在上下文中的最大字符数。 |
| `CHAT_COMPACT_TOKEN_THRESHOLD` | `80000` | 触发上下文压缩的令牌数。 |
| `CPTR_CLAUDE_CODE_MAX_BUFFER_SIZE` | `134217728` | Claude SDK 子进程的 stdout 缓冲区大小（字节）。 |
| `CPTR_EXECUTE_TIMEOUT` | 未设置 | `run_command` 返回前等待的默认秒数，命令继续在后台运行。 |
| `CPTR_STREAM_CONNECT_TIMEOUT` | `30` | 连接模型流时等待的秒数。 |
| `CPTR_STREAM_READ_TIMEOUT` | `300` | 等待模型流下一个数据块的秒数。 |
| `CPTR_STREAM_WRITE_TIMEOUT` | `600` | 写入模型流时等待的秒数。 |

## 调度器

| 变量 | 默认值 | 作用 |
| --- | --- | --- |
| `AUTOMATION_POLL_INTERVAL` | `10` | 调度器检查到期自动任务的频率（秒）。 |

## 网络

| 变量 | 默认值 | 作用 |
| --- | --- | --- |
| `CPTR_CORS_ALLOWED_ORIGINS` | `*` | 允许调用 API 的浏览器来源的逗号分隔列表。 |

## 网络搜索提供商

在此设置的密钥优先于在设置中输入的密钥。完全没有密钥时，网络搜索回退到 DuckDuckGo；否则按此顺序第一个配置的提供商获胜：Exa → Perplexity → Tavily → Brave → Firecrawl → SearXNG → DuckDuckGo。

| 变量 | 默认值 | 作用 |
| --- | --- | --- |
| `EXA_API_KEY` | 未设置 | Exa 搜索。 |
| `PERPLEXITY_API_KEY` | 未设置 | Perplexity 搜索。 |
| `PERPLEXITY_BASE_URL` | 未设置 | 自定义 Perplexity 端点。 |
| `TAVILY_API_KEY` | 未设置 | Tavily 搜索。 |
| `BRAVE_API_KEY` | 未设置 | Brave 搜索。 |
| `FIRECRAWL_API_KEY` | 未设置 | Firecrawl 搜索。 |
| `FIRECRAWL_BASE_URL` | 未设置 | 自定义 Firecrawl 端点。 |
| `SEARXNG_BASE_URL` | 未设置 | 自托管的 SearXNG 实例。 |
| `CHAT_COMPLETIONS_SEARCH_API_KEY` | 未设置 | 通过 OpenAI 兼容的聊天补全端点进行搜索。 |
| `CHAT_COMPLETIONS_SEARCH_BASE_URL` | 未设置 | 该端点的基础 URL。 |
| `CHAT_COMPLETIONS_SEARCH_MODEL` | 未设置 | 该端点的模型。 |
| `XAI_API_KEY` | 未设置 | 用于 Grok 代理检测。 |
