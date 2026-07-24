---
sidebar_position: 6
title: "系统提示词"
---

# 系统提示词

Open Terminal 默认提供生成的系统提示词。它包括运行时详细信息，如操作系统、内核、架构、主机名、用户、shell 和 Python 版本。

设置 `OPEN_TERMINAL_SYSTEM_PROMPT` 以用自己的模板替换生成的提示词。

## 占位符

这些占位符会在 `OPEN_TERMINAL_SYSTEM_PROMPT` 中展开：

| 占位符 | 值 |
| :--- | :--- |
| `{{os}}` | 操作系统名称 |
| `{{kernel}}` | 内核或 OS 版本 |
| `{{arch}}` | 机器架构 |
| `{{hostname}}` | 容器主机名 |
| `{{user}}` | 运行时用户（如果可用） |
| `{{shell}}` | Shell 路径 |
| `{{python_version}}` | Python 版本 |
| `{{home}}` | 运行时主目录 |

未知的占位符保持不变。

示例：

```text
你在 {{home}} 上工作，使用 {{os}} {{kernel}}。
终端示例使用 {{shell}}。
```

## OPEN_TERMINAL_INFO

当你希望保留生成的提示词并附加运维人员提供的上下文时使用 `OPEN_TERMINAL_INFO`，例如已安装的工具、实验说明或环境说明。

当你希望完全替换生成的提示词时使用 `OPEN_TERMINAL_SYSTEM_PROMPT`。
