---
sidebar_position: 8
title: "文件浏览器根目录"
---

# 文件浏览器根目录 {#file-browser-root}

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

Open WebUI 等客户端应使用这些元数据，让文件浏览器在 `root.path` 打开。路径导航的第一项显示 `root.label`，并隐藏通往该根目录上级的导航。

这样可以避免不熟悉系统的用户误入 `/etc` 等系统目录，并误以为自己看到了其他用户的文件。

## 配置根目录 {#configure-the-root}

默认值是 `home`，它将用户的主目录报告为 `Home`。

可指定路径，将文件浏览器界面显示的根目录改到其他位置：

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

若要完全禁用文件浏览器的根目录设置，请在策略的 `env` 中设置此值：

```json
{
  "OPEN_TERMINAL_FILE_BROWSER_ROOT": "filesystem"
}
```

当此值为 `filesystem` 时，Open Terminal 不会从 `GET /files/cwd` 报告 `root` 元数据，因此客户端保持完整的文件系统浏览能力。

## 客户端行为 {#client-behavior}

- 当存在 `root` 时，在报告的根目录处打开。
- 将第一个面包屑显示为 `root.label`。
- 隐藏根目录以上的父文件夹。
- 在客户端 UI 中处理尝试导航到根目录以上的操作。
- 当 `root` 不存在时，保持完整的文件系统浏览能力。

## 这不能做什么 {#what-this-does-not-do}

这个设置仅影响客户端界面，不是安全边界。

终端命令和模型工具仍然以终端容器的权限运行。使用容器隔离、文件系统权限、Kubernetes 安全上下文、网络策略和每用户存储来确保安全。
