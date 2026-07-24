---
sidebar_position: 2
title: "环境变量"
---

# 环境变量

策略环境变量被传递到每用户的 Open Terminal 容器中。它们是原始字符串，不是 shell 命令。

在 Open WebUI 管理面板中使用原始值：

| 容器内期望的值 | 在管理面板中输入 |
| :--- | :--- |
| `sk-proj-abc` | `sk-proj-abc` |
| `*.pypi.org,github.com` | `*.pypi.org,github.com` |
| `hello world` | `hello world` |
| 包含引号字符的 `"hello world"` | `"hello world"` |

不要在值周围添加 `'` 或 `"`，除非引号字符是你希望容器看到的值的一部分。

## 转发行为

使用策略 `env` 放置应出现在每用户 Open Terminal 容器中的值。编排器进程环境变量配置编排器本身。

编排器拒绝从策略 env 转发 `OPEN_TERMINAL_API_KEY`。它会为每个终端实例生成一个私有 API 密钥，并使用该密钥安全地代理请求。

:::warning
策略环境变量对用户在其终端内是可见的。除非允许用户查看和使用它们，否则不要将机密放在策略中。
:::

## 常见的 Open Terminal 环境变量

| 变量 | 用途 |
| :--- | :--- |
| `OPEN_TERMINAL_ALLOWED_DOMAINS` | 限制出站网络访问，例如 `*.pypi.org,github.com` |
| `OPEN_TERMINAL_EXECUTE_TIMEOUT` | 默认命令等待超时（秒） |
| `OPEN_TERMINAL_EXECUTE_DESCRIPTION` | 显示给模型的额外工具描述文本 |
| `OPEN_TERMINAL_SYSTEM_PROMPT` | 自定义系统提示词模板 |
| `OPEN_TERMINAL_INFO` | 附加到生成提示词末尾的额外环境信息 |
| `OPEN_TERMINAL_FILE_BROWSER_ROOT` | 文件浏览器可视根目录。使用 `home`、显式路径如 `/workspace`，或 `filesystem` 以退出 |
| `OPEN_TERMINAL_PACKAGES` | 容器启动时安装的空格分隔的 apt 包 |
| `OPEN_TERMINAL_PIP_PACKAGES` | 容器启动时安装的空格分隔的 Python 包 |
| `OPEN_TERMINAL_NPM_PACKAGES` | 容器启动时全局安装的空格分隔的 npm 包 |

## 自动注入的资源变量

这些由编排器根据策略的 `cpu_limit` 和 `memory_limit` 自动设置，以便系统提示词或工具可以读取容器的资源预算。它们不是用户配置的。

| 变量 | 用途 |
| :--- | :--- |
| `OPEN_TERMINAL_CPU_LIMIT` | 来自策略 `cpu_limit` 的 CPU 限制 |
| `OPEN_TERMINAL_CPU_COUNT` | 从策略 `cpu_limit` 派生的 CPU 数量 |
| `OPEN_TERMINAL_MEMORY_LIMIT` | 来自策略 `memory_limit` 的内存限制 |
| `OPEN_TERMINAL_MEMORY_BYTES` | 从策略 `memory_limit` 派生的内存限制（字节） |
