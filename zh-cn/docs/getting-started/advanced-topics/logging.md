---
sidebar_position: 5
title: "Open WebUI 日志"
---

# Open WebUI 日志 {#logging-open-webui}

**控制 Open WebUI 记录什么、输出到哪里、采用什么格式——从快速调试到生产日志管道都适用。**

Open WebUI 在两处记录日志：**浏览器控制台**用于调试前端，**Python 后端**记录服务端事件。大多数日志设置在后端。可以通过一个环境变量调整日志详细程度，也可以切换到结构化 JSON 输出，以对接 Loki、Datadog 或 CloudWatch 等日志聚合工具。

---

## 前端日志 {#frontend-logging}

前端使用标准浏览器 `console` 调用。打开浏览器开发者工具（**F12**，或 macOS 上的 **Cmd+Option+I**）并切换到 **控制台** 标签页。生产构建（Docker 镜像也包括在内）会在构建时剥离 `console.log`、`console.debug` 和 `console.error` 调用，除非前端是用 `ENV=dev` 构建的，因此在那里你主要看到的是 `console.warn` 和 `console.info` 的输出，以及浏览器自身的错误。

各浏览器文档：

- [Chrome/Chromium DevTools](https://developer.chrome.com/docs/devtools/)
- [Firefox Developer Tools](https://firefox-source-docs.mozilla.org/devtools-user/)
- [Safari Developer Tools](https://developer.apple.com/safari/tools/)

---

## 后端日志 {#backend-logging}

后端使用 Python 内置的 `logging` 模块。默认情况下，日志以 `INFO` 级别输出到 **标准输出（stdout）**，因此你可以直接在终端或容器日志中看到它们。

### 日志级别 {#log-levels}

| 级别 | 数值 | 适用场景 |
|---|---|---|
| `CRITICAL` | 50 | 灾难性故障；应用可能终止 |
| `ERROR` | 40 | 操作失败；应用继续运行，但已有功能出错 |
| `WARNING` | 30 | 值得调查的异常情况：弃用提示、资源压力等 |
| `INFO` | 20 | 正常运行流程：启动、关键事件、请求处理 **（默认）** |
| `DEBUG` | 10 | 详细诊断输出：函数调用、变量值、执行步骤 |

---

### 设置全局日志级别 {#setting-the-global-log-level}

设置 `GLOBAL_LOG_LEVEL` 可调整整个后端的日志详细程度。它通过 `logging.basicConfig(force=True)` 配置 Python 根日志记录器，影响所有 Open WebUI 日志记录器及大多数第三方库。

**Docker：**

```bash
--env GLOBAL_LOG_LEVEL="DEBUG"
```

**Docker Compose：**

```yaml
environment:
  - GLOBAL_LOG_LEVEL=DEBUG
```

:::tip
`DEBUG` 适合开发和故障排查。生产环境建议保持在 `INFO` 或 `WARNING`，以免日志量过大。
:::

Python `logging` 模块无法识别的值（例如 `TRACE`）会回退为 `INFO`。请使用上表中的级别名称：别名 `WARN` 和 `FATAL` 能通过该检查，但 Loguru 会拒绝它们，后端将无法启动。

---

### 日志级别的代价 {#what-the-log-level-costs}

提高日志级别不仅能减少日志量，还能减少处理开销，因为被该级别过滤掉的消息根本不会生成。知识库搜索只在 `DEBUG` 级别记录找到的文件名和完整结果。External、Firecrawl、Kagi、Mojeek、SearchApi、SerpApi、Serply 和 Yandex 搜索引擎也是如此。`DEBUG` 级别的运行开销最高，还会记录完整的聊天请求载荷。排查完问题后，请将日志级别调回原值。

---

### 关闭访问日志 {#turning-off-access-logs}

每个 HTTP 请求都会由 uvicorn 的 `uvicorn.access` 记录器在 `INFO` 级别写出一行访问日志。启动时，Open WebUI 会接管 `AUDIT_UVICORN_LOGGER_NAMES` 中列出的所有记录器，默认是 `uvicorn.access`：它把该记录器的处理器替换为自己的，并把级别设置为 `GLOBAL_LOG_LEVEL`。这就是为什么单独设置 `UVICORN_ACCESS_LOG=false` 不会去掉这些访问日志行。

在 Docker 镜像中，uvicorn 是从命令行启动的。要去掉访问日志行并保持 `GLOBAL_LOG_LEVEL=INFO`，请同时设置：

```bash
UVICORN_ACCESS_LOG=false
AUDIT_UVICORN_LOGGER_NAMES=
```

空的 `AUDIT_UVICORN_LOGGER_NAMES` 会停止接管，于是 uvicorn 自身的开关才生效。`open-webui serve` 是从 Python 启动 uvicorn 的，不读取 `UVICORN_ACCESS_LOG`，因此那里的访问日志行遵循 `GLOBAL_LOG_LEVEL`，只有高于 `INFO` 的级别（例如 `WARNING`）才能隐藏它们。[审计日志](/getting-started/advanced-topics/hardening#audit-logging)由 Open WebUI 自己写入，而不是由 `uvicorn.access` 写入，因此它仍然可用。

---

### 结构化 JSON 日志 {#structured-json-logging}

如果生产环境使用日志聚合工具，可设置 `LOG_FORMAT=json`，将标准输出（stdout）的内容改为每行一个 JSON 对象。

**Docker：**

```bash
--env LOG_FORMAT="json"
```

**Docker Compose：**

```yaml
environment:
  - LOG_FORMAT=json
```

**JSON 字段：**

| 字段 | 说明 |
|---|---|
| `ts` | ISO 8601 时间戳 |
| `level` | 日志级别（`debug`、`info`、`warn`、`error`、`fatal`） |
| `msg` | 日志消息 |
| `caller` | 源代码位置（`module:function:line`） |
| `extra` | 额外上下文数据（如有） |
| `error` | 错误详情（如适用）：包含 `type`、`message` 和 `stacktrace` 的对象，或启动早期行中的纯字符串 |
| `stacktrace` | 堆栈跟踪，仅出现在以 `stack_info=True` 记录的启动早期行中 |

**示例输出：**

```json
{"ts": "2026-02-22T20:14:53.386+00:00", "level": "info", "msg": "GLOBAL_LOG_LEVEL: INFO", "caller": "open_webui.env"}
{"ts": "2026-02-22T20:15:02.245+00:00", "level": "info", "msg": "Context impl SQLiteImpl.", "caller": "alembic.runtime.migration"}
```

:::note
- 默认行为（未设置 `LOG_FORMAT`）保持不变：仍为纯文本输出
- 设置 `LOG_FORMAT=json` 后会隐藏 ASCII banner，以保证日志流便于解析
- JSON 日志覆盖早期启动日志（stdlib `logging`）和运行期日志（Loguru）
:::
