---
title: 安装
sidebar_position: 1
---

# 安装

最快的安装是在你想要提供服务的机器上执行两个命令：

```bash
pip install cptr
cptr run
```

如果使用 uv，也可以使用 `uvx cptr@latest run`。这种方式在[快速入门](/ecosystem/computer/quickstart)中有逐步说明。本节涵盖其他所有方式：

| 你想要 | 前往 |
|---|---|
| 使用 pip 或 uv 在机器本身上安装 | [快速入门](/ecosystem/computer/quickstart) |
| 在容器中运行（compose、命名卷、项目挂载） | [Docker](./docker) |
| 在 Windows 机器上安装 | [Windows](./windows) |
| 在没有互联网访问的主机上安装 | [离线安装](./air-gapped) |
| 升级现有安装 | [更新](./updating) |

## 要求

- Python 3.10 或更新版本（Docker 不需要）
- macOS、Linux 或 Windows
- 一台浏览器，在同一台机器或任何其他设备上

可选功能组作为 pip extras 安装：`cptr[mcp]` 用于 MCP 工具服务器，`cptr[pam]` 用于 PAM 认证，或 `cptr[all]` 包含所有功能。Docker 镜像已包含所有这些功能。
