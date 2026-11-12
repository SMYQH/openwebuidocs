---
sidebar_position: 2
title: "Artifacts"
---

## 什么是 Artifacts？如何在 Open WebUI 中使用它们？ {#what-are-artifacts-and-how-do-i-use-them-in-open-webui}

Open WebUI 中的 Artifacts 是一项受 Claude.AI Artifacts 启发的创新功能，它允许你在聊天中直接与 LLM 生成的、较大且独立的内容进行交互。通过 Artifacts，你可以将重要内容与主对话分离地查看、修改、迭代、构建或引用，从而更容易处理复杂输出，也能在之后再次访问关键信息。

## Open WebUI 何时会使用 Artifacts？ {#when-does-open-webui-use-artifacts}

当生成内容满足本平台特定条件时，Open WebUI 就会创建 Artifact：

1. **可渲染**：要作为 Artifact 显示，内容必须是 Open WebUI 支持渲染的格式，包括：

- 单页 HTML 网站
- 可缩放矢量图（SVG）
- 完整网页，即同一个 Artifact 中同时包含 HTML、JavaScript 和 CSS。若要生成完整网页，必须包含 HTML
- ThreeJS 可视化，以及 D3.js 等其他 JavaScript 可视化库

其他内容类型，例如文档（Markdown 或纯文本）、代码片段和 React 组件，不会在 Open WebUI 中被渲染为 Artifact。

## Open WebUI 的模型如何创建 Artifacts？ {#how-does-open-webuis-model-create-artifacts}

若要在 Open WebUI 中使用 Artifacts，模型必须生成会触发渲染流程的内容。这通常意味着模型要生成有效的 HTML、SVG 或其他受支持的 Artifact 渲染格式。当生成内容满足上述条件时，Open WebUI 就会将其显示为可交互的 Artifact。

## 如何在 Open WebUI 中使用 Artifacts？ {#how-do-i-use-artifacts-in-open-webui}

当 Open WebUI 创建 Artifact 后，你会在主聊天右侧看到一个专门的 Artifacts 窗口。你可以这样与它交互：

- **编辑与迭代**：直接在聊天中要求 LLM 修改或迭代该内容，更新结果会立即显示在 Artifact 窗口中。你可通过 Artifact 左下角的版本选择器切换不同版本。每次编辑都会生成一个新版本，方便追踪变化
- **自动更新**：Open WebUI 可能会根据你的后续消息更新现有 Artifact，窗口会显示最新内容
- **操作按钮**：在 Artifact 右下角可以使用更多操作，例如复制内容或全屏打开 Artifact

## 使用 CSP 保护 Artifact 预览 {#securing-artifact-previews-with-a-csp}

Artifact 预览渲染在经过沙箱限制的 `srcdoc` iframe 中。若想更严格地控制这段生成的 HTML 能做什么（对外网络请求、脚本、样式），可以通过 [`IFRAME_CSP`](/reference/env-configuration#iframe_csp) 环境变量为预览注入一条专门的内容安全策略，它与主应用使用的 `CONTENT_SECURITY_POLICY` 相互独立。

该变量默认为空（iframe 的 `sandbox` 已经提供了基础隔离），并且作用于界面中**每一个** `srcdoc` iframe：Artifacts、代码 / HTML 预览、文件预览以及引用弹窗。设置之后，Open WebUI 会在 iframe 文档前插入 `<meta http-equiv="Content-Security-Policy">` 标签；按照 CSP 规范，第一条策略生效，因此它会覆盖生成的 HTML 中已经声明的任何 CSP。一个合理的起点是：

```bash
IFRAME_CSP=default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; connect-src 'none'
```

这样既能让内联脚本和样式继续工作（大多数 Artifact 都需要），又阻止 `fetch` / `XMLHttpRequest` / `WebSocket`，使 Artifact 无法悄悄向网络发起调用。

:::tip 先放宽，再收紧
过于严格的策略可能让预览显示为空白，因为许多 Artifact 依赖内联的 `<script>` 和 `<style>`。请从宽松策略开始，再逐步收窄。`IFRAME_CSP` 是启动时读取的环境变量（不是管理面板设置），因此修改它需要重启服务。有关面向安全的完整说明，请参阅[加固 → Iframe content-security-policy](/getting-started/advanced-topics/hardening#iframe-content-security-policy)。
:::

## 预览被允许做什么 {#what-a-preview-is-allowed-to-do}

预览 iframe 上的沙箱由 **设置 > 界面** 下的四项设置组合而成，因此你无需改动 CSP，就能收紧或放宽生成的 HTML 可以做什么。

| 设置项 | 默认值 | 允许什么 |
| :--- | :--- | :--- |
| **iframe Sandbox Allow Scripts** | 开启 | JavaScript 在预览内运行。大多数 Artifact 都需要它，关掉之后任何交互都会失效。 |
| **iframe Sandbox Allow Forms** | 开启 | 预览内的表单可以被提交。 |
| **iframe Sandbox Allow Downloads** | 开启 | 预览可以发起文件下载。 |
| **iframe Sandbox Allow Same Origin** | 关闭 | 预览会被视为与你的 Open WebUI 同源。 |

除非确有功能需要，否则请保持 **Allow Same Origin** 关闭。开启它之后，预览内的脚本与应用同源，也就是说它可以访问你的会话，而不再被限制在框架内。下方的[故障排查章节](#artifacts-preview-not-working-uncaught-securityerror)介绍了一个确实需要开启它的错误。

另外三项关系到内容在自己的框架内能做什么，把它们关掉，是一种既渲染你并不信任的内容、又不给它任何行动能力的方式。

## 编辑 Artifacts {#editing-artifacts}

1. **定向更新**：描述你想改什么以及改哪里。例如：

- “请把图表中柱子的颜色从蓝色改成红色。”
- “请将 SVG 图像的标题更新为 'New Title'。”

2. **整体重写**：如果变更涉及大部分内容、结构调整较大或需要同时修改多个区域，可以要求整体重写。例如：

- “请把这个单页 HTML 网站重写成一个落地页。”
- “请重新设计这个 SVG，让它用 ThreeJS 动画化。”

**最佳实践：**

- 明确指出你想修改 Artifact 的哪一部分
- 对于定向更新，可引用目标附近的唯一文本作为定位依据
- 根据你的需求判断：是小范围修改更合适，还是整体重写更合适

## 使用场景 {#use-cases}

Open WebUI 中的 Artifacts 能帮助不同团队快速高效地产出高质量工作成果。以下是一些适合本平台的例子：

- **设计师**：
  - 创建用于 UI/UX 设计的交互式 SVG 图形
  - 设计单页 HTML 网站或落地页
- **开发者**：创建简单 HTML 原型，或为项目生成 SVG 图标
- **市场团队**：
  - 设计带效果指标的活动落地页
  - 创建用于广告创意或社交媒体发布的 SVG 图形

## 你可以用 Open WebUI Artifacts 创建哪些项目 {#examples-of-projects-you-can-create-with-open-webuis-artifacts}

Open WebUI 中的 Artifacts 让不同团队和个人能够快速高效地创建高质量成果。以下示例展示了它的多样性，也希望能激发你探索其潜力：

1. **交互式可视化**

- 组件：ThreeJS、D3.js、SVG
- 优势：可创建沉浸式数据叙事与交互式可视化。Open WebUI 的 Artifacts 支持版本切换，因此你可以更容易测试不同可视化方案并跟踪修改

示例项目：用 ThreeJS 构建一个展示股价时间变化的交互式折线图。通过不同版本分别调整颜色和坐标轴比例，以比较不同可视化策略。

2. **单页 Web 应用**

- 组件：HTML、CSS、JavaScript
- 优势：可直接在 Open WebUI 中开发单页 Web 应用，并通过定向更新或整体重写不断迭代内容

示例项目：设计一个基于 HTML 和 CSS 的待办事项应用，并用 JavaScript 增加交互功能。随后通过定向更新和整体重写，持续改进布局与 UI/UX。

3. **动画 SVG 图形**

- 组件：SVG、ThreeJS
- 优势：为营销活动、社交媒体或网页设计创建吸引人的动画 SVG 图形。Open WebUI 的 Artifacts 允许你在同一个窗口中持续编辑和迭代

示例项目：为某公司品牌设计一个带动画效果的 SVG Logo。使用 ThreeJS 添加动画，再利用 Open WebUI 的定向更新优化配色和设计。

4. **网页原型**

- 组件：HTML、CSS、JavaScript
- 优势：可直接在 Open WebUI 中构建并测试网页原型，并通过版本切换对比不同设计方案，不断打磨原型

示例项目：用 HTML、CSS 和 JavaScript 为一个新的电商网站制作原型，并通过 Open WebUI 的定向更新不断优化导航、布局和 UI/UX。

5. **交互式叙事**

- 组件：HTML、CSS、JavaScript
- 优势：可创建带滚动效果、动画及其他交互元素的互动故事。Open WebUI 的 Artifacts 支持你持续优化故事内容，并测试不同版本

示例项目：制作一个讲述公司发展历史的交互式故事，使用滚动效果和动画增强阅读体验，并通过定向更新优化叙事内容，再利用版本选择器测试不同故事版本。

## 故障排查 {#troubleshooting}

### Artifacts 预览无法工作（Uncaught SecurityError） {#artifacts-preview-not-working-uncaught-securityerror}

如果你遇到聊天界面中代码预览不显示，并在浏览器控制台中看到类似 `Artifacts.svelte:40 Uncaught SecurityError` 的报错，这通常是某些环境配置下的跨域 iframe 限制造成的。

**解决方案：**

1. 前往 **Settings > Interface**
2. 开启 **iframe Sandbox Allow Same Origin**
3. 保存设置

### 设置 CSP 后 Artifact 预览无法显示 {#artifact-preview-is-blank-after-setting-a-csp}

如果你设置 [`IFRAME_CSP`](/reference/env-configuration#iframe_csp) 后预览停止渲染，可能是安全策略阻止了生成的 HTML 所需的内容。

1. 打开浏览器开发者工具，在控制台中查找 **CSP 违规**消息。
2. 仅针对被阻止的资源类型或来源放宽策略（通常是内联 `script`/`style`、`eval`，或特定的图片、字体、`connect` 来源）。
3. 要完全排除 CSP 的影响，暂时取消设置 `IFRAME_CSP` 并重启；预览将回退到仅沙箱隔离。
