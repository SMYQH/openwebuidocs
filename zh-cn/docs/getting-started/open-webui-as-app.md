---
sidebar_position: 3
title: "将 Open WebUI 作为应用安装"
---

# 将 Open WebUI 作为应用安装 {#open-webui-as-an-app}

每个 Open WebUI 实例都是一个**渐进式 Web 应用（Progressive Web App, PWA）**。你可以直接从浏览器把它安装为手机、平板或桌面上的独立应用，无需单独下载。

## 你将得到 {#what-you-get}

- 出现在主屏幕、任务栏或 Dock 上的**应用图标**
- **全屏体验**，没有浏览器工具栏或地址栏
- 桌面端为**独立窗口**，移动端为全屏
- **与浏览器分离**，拥有独立的窗口和任务入口
- **浏览器通知**：在设置 > 通知中开启**浏览器通知**后，可收到回复完成、频道消息和日历提醒。通知仅在应用打开时触发，没有推送服务。如果管理员启用了用户 Webhook（并为非管理员用户授予使用权限），同一页面的**通知目标**可通过 Webhook 发送聊天完成或失败、频道消息、日历事件和文件处理失败通知。可选择仅在离开时发送，或始终发送。

---

## 在你的设备上安装 {#install-on-your-device}

### Chrome / Edge（桌面） {#chrome--edge-desktop}

1. 在 Chrome 或 Edge 中打开你的 Open WebUI 实例。
2. 点击地址栏中的**安装图标**（⊕），或前往 **菜单 → 安装 Open WebUI**。
3. 点击**安装**。

Open WebUI 随后会出现在你的应用启动器中，并以独立窗口运行。

### Chrome（Android） {#chrome-android}

1. 在 Chrome 中打开你的 Open WebUI 实例。
2. 点击**菜单（⋮）→ 添加到主屏幕**或**安装应用**。
3. 点击**安装**。

### Safari（iPhone / iPad） {#safari-iphone--ipad}

1. 在 Safari 中打开你的 Open WebUI 实例。
2. 点击**分享按钮**（↑）。
3. 向下滚动并点击**添加到主屏幕**。
4. 点击**添加**。

:::info
Safari 是 iOS 上唯一支持 PWA 安装的浏览器。iOS 上的 Chrome 和 Firefox 无法安装 PWA。
:::

### Firefox（Android） {#firefox-android}

1. 在 Firefox 中打开你的 Open WebUI 实例。
2. 点击**菜单（⋮）→ 安装**。

---

## 自定义 PWA（管理员） {#customizing-the-pwa-admins}

管理员可以将 [`EXTERNAL_PWA_MANIFEST_URL`](/reference/env-configuration#external_pwa_manifest_url) 环境变量指向自定义清单，为 PWA 设置自己的应用名称、图标和主题色。服务器会在每次收到 `/manifest.json` 请求时访问该 URL，因此该地址必须对服务器可达，仅能从浏览器访问还不够。如果不设置该变量，清单会使用 `WEBUI_NAME` 作为应用名称（当它不是默认值时会追加 ` (Open WebUI)`），并以 Open WebUI 标志作为图标。
