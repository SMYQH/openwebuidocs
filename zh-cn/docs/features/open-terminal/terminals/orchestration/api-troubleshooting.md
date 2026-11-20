---
sidebar_position: 10
title: "API 和故障排除"
---

# API 和故障排除 {#api-and-troubleshooting}

## Open WebUI 的 Terminals API {#open-webui-terminals-api}

也可以使用用户令牌，通过 Open WebUI API 管理终端。读写规则见[连接访问权限](/features/open-terminal/terminals/orchestration/creating-terminals#connection-access)。这些端点经常变化，因此此处不列出。可让 AI 智能体从 Open WebUI 后端读取最新的端点和规范。

## 发往 Terminals 服务器的请求头 {#headers-sent-to-the-terminals-server}

Open WebUI 在发往终端执行的请求中携带以下请求头：

| 请求头 | 值 |
| :--- | :--- |
| `X-User-Id` | 发出请求的用户的已验证 ID |
| `X-Session-Id` | 请求属于某个聊天时，填入聊天 ID |
| `X-Terminal-Template-Id` | 终端在 Terminals 服务器上的 ID |
| `X-Terminal-Chat-Id` | 请求属于某个已保存聊天时，填入该聊天的 ID |
| `X-Terminal-Model-Id` | **Model** 终端对应的模型 ID |

## 故障排除 {#troubleshooting}

### 环境变量需要加引号吗？ {#do-i-need-quotes-around-env-vars}

不需要。完全按照容器应接收的方式输入值。仅当引号字符是预期值的一部分时才需要引号。

### 我可以将环境变量传递给编排器并让它转发吗？ {#can-i-pass-env-vars-to-the-orchestrator-and-have-it-forward-them}

使用终端的 **Environment variables**。参见[转发行为](/features/open-terminal/terminals/orchestration/environment-variables#forwarding-behavior)。

### 为什么我的环境变量或镜像更改没有生效？ {#why-did-my-env-var-or-image-change-not-apply}

该实例可能已经在运行。请从终端的 **Instances** 列表重启它，或等待空闲清理。

### 为什么用户无法在文件浏览器中访问 `/etc`？ {#why-cant-users-browse-to-etc-in-the-file-browser}

对于编排终端，文件浏览器从主目录开始，将其显示为 `Home`，并隐藏其上级文件夹。要更改或移除这个根目录，参见[文件浏览器根目录](/features/open-terminal/terminals/orchestration/file-browser-home-boundary#configure-the-root)。
