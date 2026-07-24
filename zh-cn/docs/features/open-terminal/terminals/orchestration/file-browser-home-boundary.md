---
sidebar_position: 7
title: "文件浏览器根目录"
---

# 文件浏览器根目录

Open Terminal 通过 `GET /files/cwd` 报告文件浏览器根目录：

```json
{
  "cwd": "/home/user/project",
  "home": "/home/user",
  "root": {
    "path": "/home/user",
    "label": "Home"
  }
}
```

客户端（如 Open WebUI）应使用此元数据在 `root.path` 内启动文件浏览器，将第一个面包屑渲染为 `root.label`，并隐藏根目录以上的父导航。

这可以防止非技术用户意外浏览到诸如 `/etc` 等系统文件夹并认为他们访问了其他用户文件的令人困惑的支持案例。

## 配置根目录

默认值是 `home`，它将用户的主目录报告为 `Home`。

设置显式路径以将文件浏览器可视根目录定位到其他位置：

```json
{
  "OPEN_TERMINAL_FILE_BROWSER_ROOT": "/workspace"
}
```

Open Terminal 为当前用户解析路径并将其报告为 `root.path`。根标签对于用户的主目录是 `Home`，否则使用路径的最后一段。

你也可以为当前用户主目录下的路径使用 `{{home}}` 或 `~`：

```json
{
  "OPEN_TERMINAL_FILE_BROWSER_ROOT": "{{home}}/project"
}
```

在策略 `env` 中设置此值以完全退出：

```json
{
  "OPEN_TERMINAL_FILE_BROWSER_ROOT": "filesystem"
}
```

当此值为 `filesystem` 时，Open Terminal 不会从 `GET /files/cwd` 报告 `root` 元数据，因此客户端保持完整的文件系统浏览能力。

## 客户端行为

- 当存在 `root` 时，在报告的根目录处打开。
- 将第一个面包屑显示为 `root.label`。
- 隐藏根目录以上的父文件夹。
- 在客户端 UI 中处理尝试导航到根目录以上的操作。
- 当 `root` 不存在时，保持完整的文件系统浏览能力。

## 这不能做什么

这不是安全边界。

终端命令和模型工具仍然以终端容器的权限运行。使用容器隔离、文件系统权限、Kubernetes 安全上下文、网络策略和每用户存储来确保安全。
