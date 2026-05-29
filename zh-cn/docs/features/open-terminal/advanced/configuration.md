---
sidebar_position: 2
title: "配置"
---

# 配置参考
Open Terminal 开箱即用，提供合理的默认值。本页面涵盖所有可自定义的设置。

设置按以下顺序应用（后者覆盖前者）：

1. 内置默认值
2. 系统配置文件（`/etc/open-terminal/config.toml`）
3. 用户配置文件（`~/.config/open-terminal/config.toml`）
4. 环境变量（`OPEN_TERMINAL_*`）
5. CLI 标志（`--host`、`--port` 等）

---

## 所有设置

| 设置 | 默认值 | 环境变量 | 说明 |
| :--- | :--- | :--- | :--- |
| **Host** | `0.0.0.0` | — | 监听的网络地址 |
| **Port** | `8000` | — | 端口号 |
| **API Key** | 自动生成 | `OPEN_TERMINAL_API_KEY` | 连接密码 |
| **API Key File** | — | `OPEN_TERMINAL_API_KEY_FILE` | 从文件加载密钥（用于 Docker secrets） |
| **Log Directory** | `~/.local/state/open-terminal/logs` | `OPEN_TERMINAL_LOG_DIR` | 日志文件保存位置 |
| **Max Sessions** | `16` | `OPEN_TERMINAL_MAX_SESSIONS` | 最大并发终端会话数 |
| **Enable Terminal** | `true` | `OPEN_TERMINAL_ENABLE_TERMINAL` | 开启/关闭交互式终端 |
| **Enable Notebooks** | `true` | `OPEN_TERMINAL_ENABLE_NOTEBOOKS` | 开启/关闭 Jupyter notebook 执行 |
| **TERM** | `xterm-256color` | `OPEN_TERMINAL_TERM` | 终端颜色支持 |
| **Execute Timeout** | 未设置 | `OPEN_TERMINAL_EXECUTE_TIMEOUT` | 等待命令输出的时长（秒） |
| **Execute Description** | — | `OPEN_TERMINAL_EXECUTE_DESCRIPTION` | 告知 AI 已安装工具的自定义文本 |
| **Enable System Prompt** | `true` | `OPEN_TERMINAL_ENABLE_SYSTEM_PROMPT` | 暴露 `/system` 提示词端点 |
| **System Prompt** | 自动生成 | `OPEN_TERMINAL_SYSTEM_PROMPT` | 用自定义模板替换生成的提示词 |
| **Environment Info** | — | `OPEN_TERMINAL_INFO` | 追加操作员提供的环境上下文到生成的提示词 |
| **File Browser Root** | `home` | `OPEN_TERMINAL_FILE_BROWSER_ROOT` | 使用 `home`、显式路径如 `/workspace`，或 `filesystem` 选择退出 |
| **Multi-User** | `false` | `OPEN_TERMINAL_MULTI_USER` | 启用[每用户隔离](./multi-user) |
| **CORS Origins** | `*` | `OPEN_TERMINAL_CORS_ALLOWED_ORIGINS` | 允许的跨域来源。默认 `*` 允许所有来源（宽松）；未设置时会打印启动警告（自 ~0.11.30） |
| **Allowed Domains** | — | `OPEN_TERMINAL_ALLOWED_DOMAINS` | [出站防火墙](./security#egress-filtering)：仅允许连接到这些域名 |
| **Session CWD TTL** | `604800`（7 天） | `OPEN_TERMINAL_SESSION_CWD_TTL` | 会话保存的工作目录记忆时长 |
| **Max Log Size** | `50000000`（50 MB） | `OPEN_TERMINAL_MAX_LOG_SIZE` | 日志轮转前的最大会话日志大小 |
| **Log Retention** | `604800`（7 天） | `OPEN_TERMINAL_LOG_RETENTION` | 会话日志保留时长 |
| **Log Flush Interval** | `0` | `OPEN_TERMINAL_LOG_FLUSH_INTERVAL` | 日志刷新间隔（秒），0 表示立即刷新；在慢速存储（ARM/eMMC）上增大以批处理写入 |
| **Log Flush Buffer** | `0` | `OPEN_TERMINAL_LOG_FLUSH_BUFFER` | 强制刷新前的缓冲字节数（与间隔配对使用） |
| **Binary MIME Prefixes** | `image` | `OPEN_TERMINAL_BINARY_MIME_PREFIXES` | 文件浏览器中视为二进制的 MIME 前缀 |
| **User Prefix** | 空 | `OPEN_TERMINAL_USER_PREFIX` | 添加到预配的多用户账户名称的前缀 |

---

## 仅限 Docker 的设置

以下设置仅在 Docker 镜像中有效：

| 设置 | 环境变量 | 说明 |
| :--- | :--- | :--- |
| **System Packages** | `OPEN_TERMINAL_PACKAGES` | 启动时安装的系统软件包（空格分隔） |
| **Python Packages** | `OPEN_TERMINAL_PIP_PACKAGES` | 启动时安装的 Python 软件包（空格分隔） |
| **npm Packages** | `OPEN_TERMINAL_NPM_PACKAGES` | 启动时安装的 npm 软件包（空格分隔） |

:::note
这些软件包在每次容器启动时都会重新安装。如果你需要安装大量软件包，考虑[构建自定义镜像](https://github.com/open-webui/open-terminal)替代。
:::

:::note OpenShift 镜像
`ghcr.io/open-webui/open-terminal:openshift` 镜像不支持运行时软件包安装、`OPEN_TERMINAL_ALLOWED_DOMAINS`、Docker 套接字工作流或 `OPEN_TERMINAL_MULTI_USER=true`。在部署到 OpenShift 之前，请在自定义镜像中安装所需工具。
:::

---

## 配置文件

除了环境变量外，你也可以将设置写入文件：

```toml title="~/.config/open-terminal/config.toml"
host = "0.0.0.0"
port = 8000
api_key = "your-secret-key"
log_dir = "/var/log/open-terminal"
max_terminal_sessions = 16
enable_terminal = true
enable_notebooks = true
execute_timeout = 5
execute_description = "This terminal has ffmpeg and ImageMagick installed."
```

<!-- TODO：截图——文本编辑器中展示格式整齐的 config.toml 文件。 -->

:::tip 为什么使用配置文件？
它可以让你的 API Key 不出现在命令行和 shell 历史记录中。在机器上运行 `ps` 或 `htop` 的任何人都不会看到它。
:::

若要使用自定义位置的配置文件：

```bash
open-terminal run --config /path/to/my-config.toml
```

### 系统提示词占位符

设置 `OPEN_TERMINAL_SYSTEM_PROMPT` 时，Open Terminal 会展开以下占位符：

| 占位符 | 值 |
| :--- | :--- |
| `{{os}}` | 操作系统名称 |
| `{{kernel}}` | 内核或操作系统版本 |
| `{{arch}}` | 机器架构 |
| `{{hostname}}` | 主机名 |
| `{{user}}` | 运行用户（如有） |
| `{{shell}}` | Shell 路径 |
| `{{python_version}}` | Python 版本 |
| `{{home}}` | 运行时家目录 |

未知占位符保持不变。

---

## Docker secrets

对于生产 Docker 部署，可以从 secret 文件加载 API Key：

```yaml title="docker-compose.yml"
services:
  open-terminal:
    image: ghcr.io/open-webui/open-terminal
    environment:
      - OPEN_TERMINAL_API_KEY_FILE=/run/secrets/terminal_api_key
    secrets:
      - terminal_api_key

secrets:
  terminal_api_key:
    file: ./terminal_api_key.txt
```

<!-- TODO：截图——在编辑器中高亮 Docker Compose 文件中的 secrets 部分。 -->

---

## 镜像变体

Open Terminal 提供三种大小的镜像：

| | `latest` | `slim` | `alpine` |
| :--- | :--- | :--- | :--- |
| **适合** | 通用用途、AI Agent | 较小体积 | 最小体积 |
| **大小** | ~4 GB | ~430 MB | ~230 MB |
| **包含** | Node.js、Python、编译器、ffmpeg、Docker CLI、数据科学库 | git、curl、jq | git、curl、jq |
| **可安装软件包** | ✔（有 sudo） | ✘ | ✘ |
| **多用户** | ✔ | ✘ | ✘ |

**如果不确定，使用 `latest`。** 它预装了所有工具，AI 无需等待安装即可使用任何工具。

<!-- TODO：截图——三种镜像变体相对大小和能力的可视化对比。 -->

## 相关链接

- [安全最佳实践 →](./security)
- [多用户配置 →](./multi-user)
