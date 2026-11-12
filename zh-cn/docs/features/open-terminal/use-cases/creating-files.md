---
sidebar_position: 5
title: "Create Documents & Files"
---

# Create Documents and Files

读取文件只是一半。Open Terminal 同样可以**写入**文件：Word 文档、PDF、幻灯片、图表、脚本。AI 用镜像中已有的常规 Python 库构建该文件，把它保存到你的工作区，并可以直接放进聊天里，还带上一个下载按钮。

为此不需要任何配置。没有插件，没有导出服务，也不用从代码块里复制粘贴。

## 它能产出什么 {#what-it-can-produce}

| 类型 | 格式 |
| :--- | :--- |
| **文档** | Word（.docx）、PDF、Markdown、纯文本、HTML |
| **电子表格** | Excel（.xlsx）、CSV |
| **演示文稿** | PowerPoint（.pptx） |
| **图形** | SVG、PNG 图表、缩放与转换后的图片 |
| **代码** | Python、shell 脚本、配置文件，以及其他一切基于文本的内容 |

默认镜像内置了 `python-docx`、`python-pptx`、`fpdf`、`openpyxl`、`Pillow` 和 `matplotlib`，已覆盖上述全部内容。缺少的东西可以就地安装。

---

## "把这个放进一个 Word 文档" {#put-this-in-a-word-document}

> **你：** 把各站点的读数整理成一页 Word 文档，包含一段摘要和一张各站点合计的表格，然后展示给我看。

AI 读取数据，构建出带有标题、摘要段落和一张真正表格的 `.docx`，并在聊天中显示出来。

![The AI generating a Word document and displaying it in the chat](/images/open-terminal-create-docx.png)

---

## "给我做个 PDF" {#make-me-a-pdf}

> **你：** 用同样的读数做一页 PDF，带一个标题和各站点的合计。

![The AI generating a PDF and displaying it in the chat](/images/open-terminal-create-pdf.png)

长文档会从你指定的那一页打开。参见[聊天消息中显示的文件](../file-browser.md#files-shown-in-the-chat-message)。

---

## "把它做成幻灯片" {#turn-it-into-a-deck}

> **你：** 做一份三页的幻灯片，涵盖这些读数：标题页、各站点的合计，以及需要关注的站点。

这份幻灯片带着幻灯片导航栏和翻页控件，因此你无需离开对话即可逐页浏览。

![The AI generating a PowerPoint deck and displaying it in the chat](/images/open-terminal-create-pptx.png)

---

## "把它画成 SVG" {#draw-it-as-an-svg}

> **你：** 把各站点的输出画成一个柱状图，存成纯 SVG 文件，不引用任何外部资源。

矢量输出是以文本形式写下的，因此 AI 之后可以像编辑其他任何文件那样编辑它。要求换个颜色或加一个标签，它会重写这些图形，而不是重新生成一张图片。

![The AI generating an SVG chart and displaying it in the chat](/images/open-terminal-create-svg.png)

---

## "给我写个脚本" {#write-me-a-script-for-it}

> **你：** 给我写一个脚本，用原始 CSV 重新生成这份调研报告，这样下个季度我还能再跑一次。

代码以文件形式回到你的工作区，而不是需要你从聊天里复制出来的代码块，因此拿来就能跑、拿来就能改。

![The AI writing a Python script into the workspace](/images/open-terminal-create-python.png)

---

## "帮我写成 wiki 文档" {#write-it-up-for-the-wiki}

> **你：** 把这次调研的结论写成 markdown，用于 wiki。

Markdown 会在预览中渲染，因此你可以在粘贴到任何地方之前先读一遍成稿。

![The AI writing the findings up as markdown](/images/open-terminal-create-markdown.png)

---

## 把文件取出来 {#getting-the-file-out}

聊天中显示的每个文件，其卡片右上角都有一个**下载按钮**，紧挨着在文件浏览器中打开它的控件。

![The download button on a file shown in the chat](/images/open-terminal-inline-download-button.png)

该文件同时也放在你的工作区里，因此[文件浏览器](../file-browser.md)中也能看到它，与 AI 生成的其他一切并列。在聊天中索取它，只是省得你去找。

:::tip 直接说明你想要的格式
"as a Word document"、"as a PDF"、"as a deck"、"as an SVG" 用日常说法提出来都行。如果你不说，AI 通常会选 Markdown——用于阅读没问题，但要发出去就不那么有用了。
:::

---

## 相关阅读 {#related}

- [分析文档与数据](./file-analysis.md)
- [文件浏览器](../file-browser.md)
