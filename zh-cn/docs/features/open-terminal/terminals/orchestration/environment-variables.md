---
sidebar_position: 3
title: "环境变量"
---

# 环境变量 {#environment-variables}

[终端对话框](/features/open-terminal/terminals/orchestration/creating-terminals)的 **Advanced** 下提供 **Environment variables** 字段。该字段中的环境变量会传入此终端启动的每个 Open Terminal 实例。变量值按原样传入，属于字符串，不会作为 Shell 命令执行。

请在对话框中输入原始值：

| 容器中应得到的值 | 在对话框中输入 |
| :--- | :--- |
| `sk-proj-abc` | `sk-proj-abc` |
| `*.pypi.org,github.com` | `*.pypi.org,github.com` |
| `hello world` | `hello world` |
| 包含引号字符的 `"hello world"` | `"hello world"` |

不要用 `'` 或 `"` 括起值，除非你希望容器收到的值本身就包含这些引号。

## 转发行为 {#forwarding-behavior}

要让值出现在 Open Terminal 实例中，请使用终端的 **Environment variables**。编排器进程的环境变量用于配置编排器自身。例外是编排器自身环境中的 `OPEN_TERMINAL_SYSTEM_PROMPT`：每个实例都会收到它作为默认值，终端自己的值可覆盖该默认值。

编排器会丢弃终端环境变量中的 `OPEN_TERMINAL_API_KEY`。它会为每个终端实例单独生成私有 API 密钥，并用该密钥代理请求。

:::warning
使用终端的人都能看到环境变量。仅当所有共享用户都有权查看和使用某个密钥时，才将它放入终端。
:::

## 常见的 Open Terminal 环境变量 {#common-open-terminal-env-vars}

| 变量 | 用途 |
| :--- | :--- |
| `OPEN_TERMINAL_ALLOWED_DOMAINS` | 限制出站网络访问，例如 `*.pypi.org,github.com` |
| `OPEN_TERMINAL_EXECUTE_TIMEOUT` | 默认命令等待超时（秒） |
| `OPEN_TERMINAL_EXECUTE_DESCRIPTION` | 显示给模型的额外工具描述文本 |
| `OPEN_TERMINAL_SYSTEM_PROMPT` | 自定义系统提示词模板 |
| `OPEN_TERMINAL_INFO` | 附加到生成提示词末尾的额外环境信息 |
| `OPEN_TERMINAL_FILE_BROWSER_ROOT` | 文件浏览器中显示的根目录。可使用 `home` 或 `/workspace` 等显式路径；设为 `filesystem` 可取消此限制 |
| `OPEN_TERMINAL_PACKAGES` | 容器启动时安装的空格分隔的 apt 包 |
| `OPEN_TERMINAL_PIP_PACKAGES` | 容器启动时安装的空格分隔的 Python 包 |
| `OPEN_TERMINAL_NPM_PACKAGES` | 容器启动时全局安装的空格分隔的 npm 包 |

## 自动注入的资源变量 {#automatically-injected-resource-vars}

编排器会根据 **CPU** 和 **Memory** 中已填写的字段自动设置以下变量，让系统提示词或工具可以读取容器的资源预算。这些变量反映工作区的实际限制。

| 变量 | 用途 |
| :--- | :--- |
| `OPEN_TERMINAL_CPU_LIMIT` | 终端 **CPU** 字段指定的 CPU 上限 |
| `OPEN_TERMINAL_CPU_COUNT` | 根据终端的 **CPU** 字段算出的 CPU 数量 |
| `OPEN_TERMINAL_MEMORY_LIMIT` | 终端 **Memory** 字段指定的内存上限 |
| `OPEN_TERMINAL_MEMORY_BYTES` | 根据终端的 **Memory** 字段算出的内存上限，以字节为单位 |
