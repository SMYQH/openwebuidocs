---
title: CLI
sidebar_position: 2
---

# CLI

CLI 只有一个命令：

```bash
cptr run
```

| 标志 | 默认值 | 行为 |
| --- | --- | --- |
| `--host` | `127.0.0.1` | 绑定地址。默认仅限回环；使用 `--host 0.0.0.0` 接受来自网络上其他设备的连接。 |
| `--port` | `8000` | 监听端口。也会导出为进程的 `CPTR_PORT`。 |
| `--headless` | 关闭 | 启动时不自动打开浏览器。用于服务器、systemd 单元和容器。 |
| `--reload` | 关闭 | 代码更改时自动重启。仅限开发使用。 |

首次运行时（尚无用户账户），服务器打印一个一次性设置 URL，格式为 `http://<host>:<port>/?token=<64-hex>`。打开它以创建第一个用户作为管理员。一旦用户存在，令牌立即失效。

## 安装额外包

`pip install cptr` 需要 Python 3.10+。可选功能组：

| 额外包 | 添加 |
| --- | --- |
| `cptr[mcp]` | MCP 工具服务器支持 |
| `cptr[pam]` | PAM 认证（Linux 系统用户） |
| `cptr[agents]` | 编码代理额外功能 |
| `cptr[docs]` | 文档处理额外功能 |
| `cptr[all]` | 以上全部 |

无需安装：

```bash
uvx cptr@latest run
```

## CLI 没有的功能

- **没有其他子命令。** 没有 `cptr user`、`cptr migrate` 或类似命令；数据库迁移在启动时自动运行。
- **没有 TLS 标志。** HTTPS 来自 Computer 前面的反向代理或隧道，而非来自 CLI。
- **没有 `--workers`。** 它作为单个进程运行。
- **没有密码重置命令。** 管理员在 UI 中重置密码；如果你被唯一管理员账户锁定，请参见[故障排除](/ecosystem/computer/troubleshooting)了解恢复过程。
