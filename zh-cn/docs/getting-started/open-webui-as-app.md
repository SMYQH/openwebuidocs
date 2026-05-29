---
sidebar_position: 3
title: "将 Open WebUI 作为应用安装"
---

# 将 Open WebUI 作为应用安装

每个 Open WebUI 实例都是一个**渐进式 Web 应用（Progressive Web App, PWA）**。你可以直接从浏览器把它安装为手机、平板或桌面上的独立应用，无需单独下载。

## 你将得到

- 出现在主屏幕、任务栏或 Dock 上的**应用图标**
- **全屏体验**，没有浏览器工具栏或地址栏
- 桌面端为**独立窗口**，移动端为**全屏**
- **与浏览器分离**，拥有独立的窗口和任务入口
- **推送通知**（由管理员开启后可用）

---

## 在你的设备上安装

### Chrome / Edge（桌面）

1. 在 Chrome 或 Edge 中打开你的 Open WebUI 实例。
2. 点击地址栏中的**安装图标**（⊕），或前往 **菜单 → 安装 Open WebUI**。
3. 点击**安装**。

Open WebUI 随后会出现在你的应用启动器中，并以独立窗口运行。

### Chrome（Android）

1. 在 Chrome 中打开你的 Open WebUI 实例。
2. 点击**菜单（⋮）→ 添加到主屏幕**或**安装应用**。
3. 点击**安装**。

### Safari（iPhone / iPad）

1. 在 Safari 中打开你的 Open WebUI 实例。
2. 点击**分享按钮**（↑）。
3. 向下滚动并点击**添加到主屏幕**。
4. 点击**添加**。

:::info
Safari 是 iOS 上唯一支持 PWA 安装的浏览器。iOS 上的 Chrome 和 Firefox 无法安装 PWA。
:::

### Firefox（Android）

1. 在 Firefox 中打开你的 Open WebUI 实例。
2. 点击**菜单（⋮）→ 安装**。

---

## 自定义 PWA（管理员）

管理员可以通过 [`EXTERNAL_PWA_MANIFEST_URL`](/reference/env-configuration#external_pwa_manifest_url) 环境变量指向自定义 manifest，对 PWA 进行白标定制。这让你可以设置自定义的应用名称、图标和主题色。
