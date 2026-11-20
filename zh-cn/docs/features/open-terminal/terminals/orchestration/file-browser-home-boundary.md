---
sidebar_position: 8
title: "文件浏览器根目录"
---

# 文件浏览器根目录 {#file-browser-root}

Open Terminal 会告诉 Open WebUI 等客户端文件浏览器应从哪个文件夹打开，并将它作为浏览根目录。默认使用主目录，将其显示为 `Home`，并隐藏上级文件夹。这样可以避免不熟悉系统的用户进入 `/etc` 等系统目录，误以为自己看到了其他用户的文件。

## 配置根目录 {#configure-the-root}

默认值为 `home`，即使用用户的主目录，并将其显示为 `Home`。

可指定路径，将文件浏览器界面显示的根目录改到其他位置：

```json
{
  "OPEN_TERMINAL_FILE_BROWSER_ROOT": "/workspace"
}
```

Open Terminal 会为当前用户解析路径。若路径为该用户的主目录，第一项面包屑显示 `Home`，否则显示路径的最后一段。

你也可以为当前用户主目录下的路径使用 `{{home}}` 或 `~`：

```json
{
  "OPEN_TERMINAL_FILE_BROWSER_ROOT": "{{home}}/project"
}
```

要完全禁用此限制，请在终端的 **Environment variables** 中设置以下值：

```json
{
  "OPEN_TERMINAL_FILE_BROWSER_ROOT": "filesystem"
}
```

当值为 `filesystem` 时，文件浏览器会显示完整的文件系统。

## 客户端行为 {#client-behavior}

- 从根目录打开。
- 将根目录的标签显示为第一项面包屑。
- 隐藏根目录以上的父文件夹。
- 用户尝试进入根目录以上的文件夹时，仍留在根目录范围内。
- 当值为 `filesystem` 时，显示完整的文件系统。

## 这不能做什么 {#what-this-does-not-do}

根目录只决定文件浏览器显示的内容。终端命令和模型工具以终端容器的权限运行。要限制访问，请使用容器隔离、文件系统权限、Kubernetes 安全上下文、网络策略以及按用户划分的存储。
