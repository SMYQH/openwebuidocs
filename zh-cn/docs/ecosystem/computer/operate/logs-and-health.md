---
title: 日志、健康和诊断
sidebar_position: 3
---

# 日志、健康和诊断

服务器是否在运行？

```bash
curl http://127.0.0.1:8000/api/health
```

返回包含 `status`、`uptime_seconds` 和 `pid` 的 JSON。无需认证，因此你可以将 uptime 监控、systemd 健康检查或 Docker 健康检查指向它。

## 服务器日志

Computer 输出日志到 stdout。两个变量控制它（重启以应用更改，与所有环境变量一样）：

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `CPTR_LOG_LEVEL` | `INFO` | 设置为 `DEBUG` 以获取更多细节。 |
| `CPTR_LOG_FORMAT` | `text` | 设置为 `json` 以获取结构化输出，便于日志收集器解析。 |

## 审计日志

默认关闭。当你需要谁更改了什么的持久记录时开启：

```bash
CPTR_AUDIT_LOG_LEVEL=METADATA cptr run
```

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `CPTR_AUDIT_LOG_LEVEL` | `NONE` | `METADATA` 记录每次变异的谁/什么/何时；`REQUEST` 添加经过编辑的请求体；`REQUEST_RESPONSE` 添加经过编辑的响应体。 |
| `CPTR_AUDIT_LOG_PATH` | `<data>/logs/audit.jsonl` | JSONL 审计文件的位置。 |
| `CPTR_AUDIT_LOG_ROTATION` | `10 MB` | 轮转大小。 |
| `CPTR_AUDIT_MAX_BODY_SIZE` | `2048` | 每条记录捕获的请求体最大字节数。 |
| `CPTR_AUDIT_EXCLUDED_PATHS` | `/api/chats,/v1/chat` | 审计日志跳过的路径。 |

它捕获的内容：HTTP 变异（设置更改、用户更改、上传等），敏感值经过编辑。它不捕获的内容：终端输入/输出不是 HTTP 流量，永远不会出现在这里，聊天路由默认被排除。要获取代理实际做了什么证据，请阅读聊天本身及其终端输出。

## 上游请求日志

当模型行为异常，你想精确查看 Computer 发送给提供商的内容时：

```bash
CPTR_LOG_UPSTREAM_REQUESTS=true cptr run
```

模型 API 请求写入 `<data>/logs/upstream-requests.jsonl`（50 MB 轮转，可通过 `CPTR_UPSTREAM_REQUEST_LOG_PATH` 和 `CPTR_UPSTREAM_REQUEST_LOG_ROTATION` 配置）。完成调查后关闭它：文件增长很快且包含提示内容。

## CORS

`CPTR_CORS_ALLOWED_ORIGINS` 控制哪些浏览器来源可以调用 API。默认值为 `*`。如果你在另一个来源上托管单独的前端，设置一个显式的逗号分隔列表：

```bash
CPTR_CORS_ALLOWED_ORIGINS=https://computer.example.com cptr run
```

完整变量列表，包括聊天调优和调度器设置：[环境变量](/ecosystem/computer/reference/environment-variables)。
