---
sidebar_position: 3
title: "环境变量"
---

# 环境变量 {#environment-variables}

策略中设置的环境变量会传给每位用户的 Open Terminal 容器。它们是原始字符串，不是 shell 命令。

在 Open WebUI 管理面板中使用原始值：

| 容器内期望的值 | 在管理面板中输入 |
| :--- | :--- |
| `sk-proj-abc` | `sk-proj-abc` |
| `*.pypi.org,github.com` | `*.pypi.org,github.com` |
| `hello world` | `hello world` |
| 包含引号字符的 `"hello world"` | `"hello world"` |

不要用 `'` 或 `"` 括起值，除非你希望容器收到的值本身就包含这些引号。

## 转发行为 {#forwarding-behavior}

通过策略的 `env` 字段设置传给各用户 Open Terminal 容器的值。编排器进程的环境变量只配置编排器本身。

编排器不会转发策略中设置的 `OPEN_TERMINAL_API_KEY`。它会为每个终端实例生成一个私有 API 密钥，并使用该密钥安全地代理请求。

:::warning
用户可以在自己的终端内查看策略环境变量。只有在允许用户查看并使用密钥等敏感信息时，才可将其放入策略。
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

这些由编排器根据策略的 `cpu_limit` 和 `memory_limit` 自动设置，以便系统提示词或工具可以读取容器的资源预算。它们不是用户配置的。在受限制的工作区内，`nproc` 和 `free` 仍然报告宿主机的核数与内存，因此这些变量是容器内获取真实限制的唯一来源。

| 变量 | 用途 |
| :--- | :--- |
| `OPEN_TERMINAL_CPU_LIMIT` | 来自策略 `cpu_limit` 的 CPU 限制 |
| `OPEN_TERMINAL_CPU_COUNT` | 从策略 `cpu_limit` 派生的 CPU 数量 |
| `OPEN_TERMINAL_MEMORY_LIMIT` | 来自策略 `memory_limit` 的内存限制 |
| `OPEN_TERMINAL_MEMORY_BYTES` | 从策略 `memory_limit` 派生的内存限制（字节） |
