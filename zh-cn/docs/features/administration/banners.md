---
sidebar_position: 13
title: "可定制的横幅"
---

## 概述 {#overview}

Open WebUI 允许管理员在新建聊天界面展示自定义横幅。横幅仅在未打开任何聊天时显示在聊天标题栏下方，不会出现在工作区、管理面板或其他页面。拥有 `user` 或 `admin` 角色的每个账号都会看到相同的横幅列表。仍处于 `pending` 角色的账号不会看到横幅。横幅适用于公告、全系统警报、维护通知及其他重要消息。

用户可以关闭任意横幅，关闭状态默认仅对当前页面加载有效，横幅也可以选择记住该关闭状态。您可以通过两种方式配置横幅：

1. **管理面板**（推荐用于快速编辑和试验）
2. **环境变量（`WEBUI_BANNERS`）**（推荐用于自动化/GitOps 风格部署）

---

## 横幅的适用场景 {#when-to-use-banners}

横幅最适合简短的高可见度消息，例如：

- 计划维护和预定停机窗口
- 故障通知（性能降级、局部中断）
- 政策提醒（可接受使用、数据处理、保留策略）
- 重大变更（新模型、功能上线、界面变更）
- 指向内部通讯频道的链接，用于更新和答疑

**提示：** 保持横幅简洁，并链接到更详细的信息（状态页面、发布说明、支持频道）。

---

## 配置横幅 {#configuring-banners}

### 方式 1：使用管理面板 {#option-1-using-the-admin-panel}

这是管理横幅最直接的方式：

1. 以管理员身份登录 Open WebUI 实例。
2. 导航到 **设置** → **通用**（管理员区域）。
3. 找到 **横幅** 部分。
4. 点击 **+** 图标添加新横幅。
5. 点击 **保存** 应用更改。

每个横幅可配置以下选项：

- **类型：** 横幅的颜色和样式：
  - `info`（蓝色）
  - `success`（绿色）
  - `warning`（黄色）
  - `error`（红色）
- **标题：** 横幅的主标题。
- **内容：** 主要消息。会渲染 Markdown 并允许内联 HTML，两者都会经过净化器处理。解析前，每个换行符都会转换成渲染时的换行，因此跨行的 Markdown 块（列表、表格、引用块）无法成形；这些内容请改用其 HTML 形式。
- **记住关闭状态：** 启用后，用户关闭过的横幅将保持关闭；禁用后，横幅会在下次页面加载时再次显示。

**横幅** 标题旁的地球图标选择器会按语言分别保存内容，因此每位用户看到的都是其界面语言对应的横幅。参见 [Translations](/features/administration/translations#banners)。

#### 关闭横幅的机制 {#how-dismissing-works}

已关闭的横幅存储在用户浏览器端（客户端）。这意味着：

- 如果用户清除站点数据/缓存，已关闭的横幅可能重新出现
- 在不同设备或浏览器上，已关闭的横幅可能重新出现
- 关闭状态与横幅 `id` 绑定（若 `id` 变更，横幅将被视为新横幅）

如果要让所有人每次加载页面时都重新看到横幅，请设置 `dismissible: false`。

---

### 方式 2：使用环境变量（`WEBUI_BANNERS`） {#option-2-using-environment-variables-webui\_banners}

对于自动化部署，可使用 `WEBUI_BANNERS` 环境变量配置横幅。该值必须是一个**JSON 字符串**，表示横幅对象的**列表**（数组）。

**环境变量：**

- `WEBUI_BANNERS`
  - **类型：** `string`（包含 JSON 对象列表）
  - **默认值：** `[]`
  - **说明：** 要向用户展示的横幅对象列表

#### 示例（Docker Compose） {#example-docker-compose}

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - 'WEBUI_BANNERS=[{"id":"maintenance-2026-03","type":"warning","title":"Maintenance","content":"A maintenance window is planned this week. Expect brief interruptions. <a href=\"https://intranet.example.com/status\" target=\"_blank\">See status page</a>.","dismissible":true,"timestamp":1772500000}]'
```

> 注意：由于 `WEBUI_BANNERS` 是嵌入 YAML 内的 JSON 字符串，必须确保其始终是有效 JSON（参见下方"常见陷阱"）。

---

## 横幅对象属性 {#banner-object-properties}

每个横幅对象支持以下属性：

- `id`（字符串，必填）：横幅的唯一标识符，用于跟踪用户是否已关闭。
- `type`（字符串，必填）：横幅样式，必须为以下之一：`info`、`success`、`warning`、`error`。
- `title`（字符串，可选）：标题文本。
- `content`（字符串，必填）：横幅主要消息（支持 Markdown 和内联 HTML）。
- `dismissible`（布尔值，必填）：已关闭的横幅是否对该用户保持关闭（即 **记住关闭状态** 开关）。
- `timestamp`（整数，必填）：存在于配置中，但目前前端不使用该字段控制显示时间。
- `i18n`（对象，可选）：按语言键控的翻译内容，每个条目包含一个 `content` 字符串。用户会看到与其界面语言匹配的条目，若无匹配则回退到 `content`。参见 [Translations](/features/administration/translations#banners)。

### 推荐的 `id` 策略（重要） {#recommended-id-strategy-important}

选择支持安全更新、避免意外重新显示或永久隐藏的 `id` 格式：

- 小幅文字修改用稳定 `id`：`policy-reminder`
- 需要"再次向所有人显示"时用带版本号 `id`：`incident-2026-03-06-v2`
- 周期性事件用按时间分桶 `id`：`maintenance-2026-03`

如果用户已关闭横幅，而您希望他们看到更新后的消息，请修改 `id`。

---

## 支持的内容格式 {#supported-content-formatting}

横幅的 `content` 会先按 Markdown 解析，再经过净化器处理，因此内联 Markdown（`**bold**`、`[link](url)`、反引号）和内联 HTML 均可正常渲染。解析前，每个换行符都会转换成换行元素，因此跨行的块级 Markdown 无法形成，例如多行列表、表格、引用块或后续行上的标题。HTML 列表、标题、表格和引用块则可以正常渲染。JSON 接受 `title`，但不会显示其值：编辑器没有“标题”字段，横幅仅显示类型标签和内容。

### 文本格式 {#text-formatting}

| HTML | 效果 |
| --- | --- |
| `<b>` / `<strong>` | 粗体 |
| `<i>` / `<em>` | 斜体 |
| `<u>` | 下划线 |
| `<s>` / `<del>` | 删除线 |
| `<mark>` | 高亮 |
| `<small>` | 略小的文字 |
| `<sub>` / `<sup>` | 下标 / 上标 |
| `<code>` / `<kbd>` | 等宽内联代码 |
| `<abbr title="tooltip">` | 悬停提示 |

### 结构 {#structure}

| HTML | 效果 |
| --- | --- |
| `<br>` 或字面换行 | 换行 |
| `<hr>` | 水平分隔线 |
| `<details><summary>Click</summary>...</details>` | 可折叠区块 |

### 链接与媒体 {#links--media}

| HTML | 效果 |
| --- | --- |
| `<a href="...">` | 可点击链接。净化器会移除 `target`，因此链接在当前标签页打开 |
| `<img src="..." width="16" height="16">` | 内联图片 |

### 自定义样式 {#custom-styling}

支持在允许的标签上使用内联样式：

```html
<span style="color: #b91c1c;">Colored text</span>
<span style="font-weight: 600;">Heavier weight</span>
<span style="background: linear-gradient(90deg,#e0f2fe,#fef9c3);">Gradient background</span>
```

您也可以将整个消息区域包裹在块级元素中以应用样式：

```html
<div style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:12px;padding:10px 14px;line-height:1.3;display:block;width:100%;box-sizing:border-box;">
  <b>Notice title</b><br>
  Short supporting message.
</div>
```

> 保持样式有目的性。过大的内边距、字体大小或深度嵌套的布局可能导致横幅过高，或在不同主题下视觉不一致。

---

## 设计高效的横幅 {#designing-effective-banners}

当横幅易于扫读、视觉上突出且简短到不打断正常工作，效果最佳。

### 组织消息结构 {#structure-the-message}

采用可预测的结构：

- 以事件类型或状态开头：`Maintenance`、`Incident`、`Policy update`、`New feature`。
- 把最重要的信息放在最前：日期、时间、影响或所需操作。
- 正文保持一两句话。
- 仅在用户需要更多细节时添加一个链接。

对于较长的通知，使用短分段代替一段长段落。对于多语言通知，使用细 `<hr>` 分隔语言，或使用可折叠的 `<details>` 区块。

### 让严重程度可见 {#make-severity-visible}

保持 `type` 的一致用法：

- `info`：中性公告和产品更新。
- `success`：已解决的故障或已完成的变更。
- `warning`：计划维护、降级的服务或即将到来的待办操作。
- `error`：活跃故障或需要紧急处理。

避免对非紧急公告使用 `error`。当每条消息看起来都"很紧急"时，用户会学会忽略告警。

### 谨慎使用颜色 {#use-color-carefully}

颜色应辅助而非争夺横幅的视觉：

- 对完整消息区域使用柔和背景。
- 对小标签、强调或左边框使用较强的颜色。
- 保持文字对比度足够高，以便在明亮房间和暗光屏幕下都可读。
- 避免在同一条横幅中混用过多无关颜色。

一种有用的模式是柔和背景加上更醒目的左边框：

```html
<div style="background:#f8fafc;color:#334155;border:1px solid #cbd5e1;border-left:6px solid #64748b;border-radius:12px;padding:10px 14px;line-height:1.3;display:block;width:100%;box-sizing:border-box;">
  <b>Notice title</b><br>
  Short supporting message.
</div>
```

### 让布局自适应 {#keep-layouts-responsive}

横幅显示在应用布局内，必须在窄屏下仍能正常显示。

- 对包含标签、日期或徽章的行，优先使用 `display:flex;flex-wrap:wrap`。
- 避免使用固定宽度。
- 对全宽样式块使用 `width:100%;box-sizing:border-box`。
- 保持图标和徽章较小，避免增加横幅高度。
- 在正式使用前，使用窄浏览器窗口测试横幅。

### 避免意外过高 {#avoid-accidental-extra-height}

横幅内容将字面换行视为换行符。如果您显式使用 `<br>` 标签，请保持原始 HTML 紧凑，避免在横幅内容字段中添加额外的空行或缩进。

如下这种紧凑风格：

```html
<b>Notice</b><br>One short sentence.<br>Another short sentence.
```

比含大量换行的格式化 HTML 渲染得更可控。

---

## 不支持的内容 {#unsupported-content}

以下内容在横幅中不受支持，可能以纯文本显示或破坏布局：

- 标题（`<h1>`–`<h6>`）
- 列表（`<ul>`、`<ol>`）
- 表格
- 引用块
- Markdown 语法

如果需要"列表式"内容，请使用 `<br>` 分隔的短行。

---

## 常见陷阱（及如何避免） {#common-pitfalls-and-how-to-avoid-them}

### 1）字面换行导致意外间距 {#1-unexpected-spacing-from-literal-newlines}

横幅内容将**字面换行**视为换行符。如果您粘贴了格式化/缩进良好的 HTML（含大量换行），横幅可能比预期高得多。

**建议：**
- 有意使用 `<br>`，保持原始 HTML 相对紧凑。
- 除非确实需要额外间距，否则不要添加空白行。

### 2）横幅内容中的链接失效 {#2-broken-links-in-banner-content}

如果链接显示为"失效"或横幅其余部分变为可点击，通常是由于无效的 HTML。

请使用以下精确格式：

```html
<a href="https://example.com" target="_blank">Open link</a>
```

**建议：**
- 始终用 `</a>` 关闭锚标签。
- 净化器会移除 `target="_blank"`，因此该属性不起作用。链接会在同一个标签页中打开。
- 如果 URL 包含查询参数，在 `href` 属性中将 `&` 转义为 `&amp;`：
  ```html
  <a href="https://example.com/page?x=1&amp;y=2" target="_blank">Example</a>
  ```
- 如需确保下划线，将链接文字包裹在 `<u>` 中：
  ```html
  <a href="https://example.com" target="_blank"><u>Support</u></a>
  ```

### 3）`WEBUI_BANNERS` 中的 JSON/YAML 转义问题 {#3-jsonyaml-escaping-issues-in-webui\_banners}

使用 `WEBUI_BANNERS` 时，您是在将 JSON 嵌入 YAML 字符串（或 Shell 字符串）中。常见问题包括：

- JSON 内部未转义的双引号
- 插入 JSON 字符串的换行符
- 复制粘贴时使用了"弯引号"（印刷引号）而非普通 `"`

**建议：**
- 部署前在 JSON 验证工具中验证 JSON。
- 保持 `content` 字符串简单；避免未转义的 `"` 字符。
- 如有必要，在 JSON 字符串内部引号使用 `\"` 转义。
- 如果横幅未出现，检查服务器日志。

### 4）过度使用 `<small>` {#4-overusing-small}

`<small>` 适合次要文本，但将横幅的大部分内容包裹在 `<small>` 中会使内容难以阅读。

**建议：** 主要消息使用普通文本，将 `<small>` 保留用于不太重要的细节。

### 5）外部图片 {#5-external-images}

图片可通过 `<img>` 嵌入，但外部图片可能：
- 因网络限制无法加载
- 未加约束时在不同设备上产生大小不一致
- 从第三方域名加载时引入隐私/安全问题

**建议：**
- 尽可能使用内部/静态资源。
- 始终设置明确的 `width` 和 `height`。
- 保持图标较小（例如 16×16），避免增加横幅高度。

---

## 可复用模式（可复制粘贴的片段） {#reusable-patterns-copypaste-snippets}

### 模式：带链接的最简两行公告 {#pattern-minimal-two-line-announcement-with-a-link}

```html
<b>Notice</b><br>
Service updates: <a href="https://example.com/status" target="_blank"><u>Status page</u></a>
```

### 模式：紧凑"标签"徽章（日期/影响标签） {#pattern-compact-label-chip-dateimpact-tag}

```html
<span style="display:inline-block;background:#fff3cd;color:#664d03;padding:2px 8px;border-radius:999px;">
  Scheduled
</span>
```

### 模式：带样式的通知块 {#pattern-styled-notice-block}

当整条消息应作为一个公告区域呈现时，使用全宽样式块。粘贴到横幅内容字段时，请保持该 HTML 紧凑，特别是当其中还包含 `<br>` 标签时。

```html
<div style="background:#f8fafc;color:#334155;border:1px solid #cbd5e1;border-left:6px solid #64748b;border-radius:12px;padding:10px 14px;line-height:1.3;display:block;width:100%;box-sizing:border-box;"><div style="display:flex;flex-wrap:wrap;align-items:center;gap:5px 8px;margin-bottom:5px;"><span style="display:inline-flex;align-items:center;background:#64748b;color:#fff;padding:1px 7px;border-radius:999px;line-height:1.25;font-size:10px;font-weight:700;letter-spacing:.04em;">NOTICE</span><b>Notice title</b><span style="display:inline-flex;align-items:center;background:#fff;color:#334155;padding:1px 8px;border-radius:999px;line-height:1.25;border:1px solid #cbd5e1;">Key detail</span></div><div>Short supporting message.</div></div>
```

此模式使用了：

- 完整消息区域的柔和背景。
- 更醒目的左边框以快速识别。
- 用于事件类型的小型大写标签。
- 用于最重要元数据的紧凑日期/时间徽章。
- `flex-wrap` 使标题行在窄屏下也能正确显示。

### 模式：可折叠详情（保持横幅简短） {#pattern-collapsible-details-keep-banners-short}

```html
<b>Planned update</b><br>
<details>
  <summary>More details</summary>
  <br>
  This update may cause brief interruptions during the deployment window.
</details>
```

---

## 运营最佳实践 {#operational-best-practices}

### 保持横幅易于扫读 {#keep-banners-scannable}

一个好的横幅通常包含：
- 简短的标题
- 一句话描述情况
- 一个详情链接和一个答疑链接（如有需要）

### 保持横幅类型的一致性 {#use-banner-types-consistently}

为减少告警疲劳，建议采用一致的映射：
- `info`：一般公告
- `success`：变更完成/故障已解决
- `warning`：计划维护或局部降级
- `error`：活跃故障/服务中断

### 移除过期横幅 {#remove-expired-banners}

如果不断添加横幅而不删除旧横幅，用户可能会忽略它们。事件结束后请移除或替换横幅。

---

## 故障排查 {#troubleshooting}

### 横幅未显示 {#banner-not-appearing}

- 确保 `WEBUI_BANNERS` 是有效的 JSON **数组**（不是单个对象）。
- 检查服务器日志中与 `WEBUI_BANNERS` 相关的解析错误。
- 如果使用管理面板，确认已点击 **保存**。

### 横幅无法关闭 {#banner-cannot-be-dismissed}

- 确认 `dismissible` 已设为 `true`。
- 每条横幅都可以通过其 × 按钮关闭。`dismissible: true`（编辑器中的 **记住关闭状态** 开关）会在浏览器中记住这次关闭，因此横幅保持消失；`false` 只在页面重新加载前隐藏它。无法将横幅设为不可关闭。

### 横幅布局看起来错乱或过高 {#banner-layout-looks-broken-or-too-tall}

- 移除原始 HTML 中多余的空行和缩进。
- 避免使用不支持的 HTML（列表、表格、标题）。
- 减少过度的内联样式（过大的 `padding`、过大的 `font-size`）。

---

## 常见问题 {#faq}

### 横幅内容可以使用 Markdown 吗？ {#can-i-use-markdown-in-banner-content}

可以，但仅限于内联 Markdown。内容会先按 Markdown 解析，再经过净化器处理。由于换行会先变成换行符，跨行的 Markdown 块无法成形，因此需要多行的列表、表格和标题请改用 HTML。

### `timestamp` 是否控制横幅何时显示？ {#does-timestamp-control-when-a-banner-shows}

不会。`timestamp` 字段当前并未被前端用于控制横幅是否展示。如果需要按时间触发显示，请通过你的部署自动化来管理（按计划添加/移除横幅）。

### 可以同时展示多种语言的内容吗？ {#can-i-show-content-in-multiple-languages}

可以，但更好的做法是翻译横幅，而不是在一条消息中堆叠多种语言：使用 **横幅** 标题旁的地球图标选择器，每位用户只会看到自己的语言。参见 [Translations](/features/administration/translations#banners)。通过 `WEBUI_BANNERS` 设置的横幅也可以携带同样的内容，即在横幅上使用按语言键控的 `i18n` 对象，每个条目中包含一个 `content` 字符串。
