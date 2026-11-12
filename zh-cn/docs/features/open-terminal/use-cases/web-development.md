---
sidebar_position: 3
title: "构建和预览网站"
---

# 构建和预览网站 {#build-and-preview-websites}

Open Terminal 最令人印象深刻的功能之一：AI 构建一个网站，启动服务器，你可以**在预览面板中实时看到它**，全部在 Open WebUI 内部完成。然后你告诉它需要更改什么，预览会实时更新。
## 工作原理 {#how-it-works}

1. 你要求 AI 创建一个网站（或 Web 应用、落地页，或任何基于 Web 的内容）
2. AI 创建文件并启动 Web 服务器
3. Open Terminal **自动检测**运行中的服务器
4. 一个**预览面板**出现在 Open WebUI 中，显示实时页面
5. 你提出更改要求 → AI 编辑文件 → 预览更新

![AI 创建落地页，文件浏览器显示已创建的文件](/images/open-terminal-ai-web-dev.png)

---

## "给我做一个落地页" {#make-me-a-landing-page}

> **你：** 为我的摄影业务创建一个落地页。包含一个作品集、一个关于部分和一个联系表单。

AI 创建 HTML、CSS 和 JavaScript 文件，启动 Web 服务器，预览会自动出现。页面看起来专业且精致，而不是一个骨架线框图。

![文件浏览器显示已创建的 HTML 文件](/images/open-terminal-ai-web-dev-files.png)

---

## "更改颜色和布局" {#change-the-colors-and-layout}

页面上线后，只需继续对话即可迭代：

> **你：** 将背景设为深色，使用更温暖的配色方案。将作品集移到关于部分的上方。

AI 编辑 CSS 和 HTML 文件，预览会立即更新。

---

## "给我做一个交互式的东西" {#build-me-something-interactive}

AI 可以创建交互式 Web 应用程序，而不仅仅是静态页面：

> **你：** 构建一个在浏览器中运行的简单计算器。

![AI 为交互式应用创建和运行代码](/images/open-terminal-ai-code-execution.png)

---

## "帮我修复我的网站" {#help-me-fix-my-website}

有现有的网站需要修复或更改？上传文件并提问：

> **你：** *(通过文件浏览器上传 HTML/CSS 文件)* <br/>
> 联系表单无法提交。你能修复它吗？

AI 读取你的代码，识别问题，修复它，你可以在预览中验证。

![AI 识别并修复代码错误](/images/open-terminal-ai-debug-fix.png)

---

## 端口检测的工作原理 {#how-port-detection-works}

你无需做任何特殊操作即可让预览出现。幕后机制如下：

1. AI 启动一个 Web 服务器（如 `python -m http.server 3000` 或任何其他服务器）
2. Open Terminal 监控新的网络端口
3. 当检测到服务器正在运行时，它将端口报告给 Open WebUI
4. Open WebUI 显示预览面板，通过其自身连接代理流量

这意味着**你不需要打开额外端口**或更改任何防火墙设置。它开箱即用。

:::tip 多个预览
如果 AI 启动了多个服务器（例如，前端在端口 3000，后端 API 在端口 5000），你可以在端口部分之间切换。
:::

## 浏览器标签页 {#the-browser-tab}

在支持浏览器会话的终端上，**标签页**的 **+** 菜单会提供 **浏览器**。它的起始页会列出该终端正在提供的**端口**；点击其中一个即可加载，也可以直接输入任意 http 或 https 地址。

选项菜单（**...**）用于选择页面的加载方式。**Chrome** 会在终端上运行 Chrome，并把它以远程视图的形式推送到该标签页，同时提供 **移动视图** 和一个画质设置。**代理** 则通过终端加载页面。当终端提供 Chrome 时，新的浏览器标签页默认以 Chrome 启动，否则使用代理。如果 Chrome 启动失败，标签页会切换到代理并显示 **Chrome failed. Switched to Proxy.**。当你自己或终端失去访问权限时，这个在线会话就会结束。

## 桌面标签页 {#the-desktop-tab}

在支持该功能的终端上，**+** 菜单还会提供 **桌面**。它显示终端的桌面，你可以用鼠标和键盘操作它（包括粘贴），还有一个按钮可以全屏打开。当终端提供桌面音频时，扬声器按钮（**取消静音** / **静音**）会播放其声音。

## 还可以尝试这些 {#more-things-to-try}

:::tip
想从手机预览和迭代网站？[**Open WebUI Computer**](/ecosystem/computer) 将你的整台计算机放入浏览器标签页，可从任何设备访问。
:::
- **[从对话中运行代码 →](./code-execution.md)**：AI 编写、运行并调试代码
- **[分析文档与数据 →](./file-analysis.md)**：电子表格、PDF、Word 文档、邮件
- **[自动化任务 →](./system-automation.md)**：文件管理、备份、批量操作


---
