---
sidebar_position: 5
title: "创建文档和文件"
---

# 创建文档和文件 {#create-documents-and-files}

Open Terminal 不仅读取文件，还能**创建** Word 文档、PDF、幻灯片、图表和脚本。AI 使用镜像中已有的常用 Python 库生成文件并保存到工作区，还可以把文件直接显示在聊天中，附上下载按钮。

为此不需要任何配置。没有插件，没有导出服务，也不用从代码块里复制粘贴。

## 它能产出什么 {#what-it-can-produce}

| 类型 | 格式 |
| :--- | :--- |
| **文档** | Word（.docx）、PDF、Markdown、纯文本、HTML |
| **电子表格** | Excel（.xlsx）、CSV |
| **演示文稿** | PowerPoint（.pptx） |
| **图形** | SVG、PNG 图表、缩放与转换后的图片 |
| **代码** | Python、shell 脚本、配置文件，以及其他一切基于文本的内容 |

默认镜像内置了 `python-docx`、`python-pptx`、`fpdf`、`openpyxl`、`Pillow` 和 `matplotlib`，足以生成上述文件。缺少的库可以按需安装。

---

## "把这个放进一个 Word 文档" {#put-this-in-a-word-document}

> **你：** 把各站点的读数整理成一页 Word 文档，包含一段摘要和一张各站点合计的表格，然后展示给我看。

AI 读取数据，生成包含标题、摘要段落和原生表格的 `.docx` 文件，并在聊天中显示它。

![AI 生成一份 Word 文档并在聊天窗口中显示](/images/open-terminal-create-docx.png)

---

## "给我做个 PDF" {#make-me-a-pdf}

> **你：** 用同样的读数做一页 PDF，带一个标题和各站点的合计。

![AI 生成 PDF 文件并在聊天中显示](/images/open-terminal-create-pdf.png)

长文档会从你指定的那一页打开。参见[聊天消息中显示的文件](../file-browser.md#files-shown-in-the-chat-message)。

---

## "把它做成幻灯片" {#turn-it-into-a-deck}

> **你：** 做一份三页的幻灯片，涵盖这些读数：标题页、各站点的合计，以及需要关注的站点。

这份幻灯片带着幻灯片导航栏和翻页控件，因此你无需离开对话即可逐页浏览。

![AI 生成 PowerPoint 演示文稿并在聊天中显示](/images/open-terminal-create-pptx.png)

---

## "把它画成 SVG" {#draw-it-as-an-svg}

> **你：** 把各站点的输出画成一个柱状图，存成纯 SVG 文件，不引用任何外部资源。

矢量输出是以文本形式写下的，因此 AI 之后可以像编辑其他任何文件那样编辑它。要求换个颜色或加一个标签，它会重写这些图形，而不是重新生成一张图片。

![AI 生成 SVG 图表并在聊天中显示](/images/open-terminal-create-svg.png)

---

## "给我写个脚本" {#write-me-a-script-for-it}

> **你：** 给我写一个脚本，用原始 CSV 重新生成这份调研报告，这样下个季度我还能再跑一次。

代码会保存为工作区中的文件，可直接运行或编辑，无需从聊天的代码块中复制。

![AI 正在将一个 Python 脚本写入工作区](/images/open-terminal-create-python.png)

---

## "帮我写成 wiki 文档" {#write-it-up-for-the-wiki}

> **你：** 把这次调研的结论写成 markdown，用于 wiki。

Markdown 会在预览中渲染，因此你可以在粘贴到任何地方之前先读一遍成稿。

![AI 将调研结论整理成 Markdown 文档](/images/open-terminal-create-markdown.png)

---

## 把文件取出来 {#getting-the-file-out}

聊天中显示的每个文件，其卡片右上角都有一个**下载按钮**，紧挨着在文件浏览器中打开它的控件。

![聊天界面中显示的文件上的下载按钮](/images/open-terminal-inline-download-button.png)

该文件同时也放在你的工作区里，因此[文件浏览器](../file-browser.md)中也能看到它，与 AI 生成的其他一切并列。在聊天中索取它，只是省得你去找。

:::tip 直接说明你想要的格式
可以直接说“做成 Word 文档”“做成 PDF”“做成演示文稿”或“输出为 SVG”。如果不指定格式，AI 通常会选择 Markdown，适合阅读，但转发给他人时未必方便。
:::

---

## 相关阅读 {#related}

- [分析文档与数据](./file-analysis.md)
- [文件浏览器](../file-browser.md)
