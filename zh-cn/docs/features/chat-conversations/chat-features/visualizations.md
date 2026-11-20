---
sidebar_position: 19
title: "可视化"
---

# 可视化 {#visualizations}

可视化让模型直接在聊天中绘制交互式图表、示意图、计算器和讲解内容。

可以粘贴表格并请模型绘制图表，或要求它制作流程图、时间线、带可编辑字段的小型计算器，甚至带滑块的互动讲解。当图像或交互内容能比纯文本更清楚地解释答案时，可以使用此功能。管理员和模型所有者可按模型开启。

## 工作原理 {#how-it-works}

模型通过内置工具 `render_visualization` 编写少量 HTML、SVG 和 JavaScript，聊天界面在简短标题下显示结果。图表可以使用 Chart.js。启用此工具的模型会在可视内容比纯文本更有帮助时使用它。

## 开启可视化 {#turn-it-on}

可视化默认关闭。在模型编辑器的**内置工具** > **可视化**下按模型开启。基础模型的编辑器位于**设置 > 模型**（管理员区域），自有模型的编辑器位于**工作区 > 模型**。此工具需要[原生函数调用](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)，且模型须具备**内置工具**能力。

## 更改指令 {#change-the-instructions}

模型收到的工具指令决定它何时绘制以及如何绘制。管理员可在**设置 > 界面 > 可视化提示词**（管理员区域）中改写指令，也可设置 [`VISUALIZATION_PROMPT_TEMPLATE`](/reference/env-configuration#visualization_prompt_template)。留空时使用默认值。

## 隔离和安全 {#isolation-and-security}

可视化内容在独立框架中渲染，有两项设置控制其行为：

- [`IFRAME_CSP`](/reference/env-configuration#iframe_csp) 对该框架生效，与其他 `srcdoc` iframe 一样。
- 只有在**设置 > 界面**中开启 **iframe Sandbox Allow Scripts** 时，框架中的脚本才能运行。见[预览可以执行哪些操作](/features/chat-conversations/chat-features/code-execution/artifacts#what-a-preview-is-allowed-to-do)。

可视化内容尝试向聊天发送消息时，必须先由用户确认。
