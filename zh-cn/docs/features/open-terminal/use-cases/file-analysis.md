---
sidebar_position: 2
title: "分析文档和数据"
---

# 分析您的文档和数据

有一堆电子表格、PDF、Word 文档或邮件需要整理？将它们拖入文件浏览器，让 AI 为你读取。Open Terminal 可以打开并理解所有这些格式，无需特殊设置。

## 支持读取哪些文件类型？

| 类型 | 格式 |
| :--- | :--- |
| **电子表格** | Excel (.xlsx, .xls), OpenDocument (.ods), CSV |
| **文档** | Word (.docx), OpenDocument (.odt), Rich Text (.rtf), PDF |
| **演示文稿** | PowerPoint (.pptx), OpenDocument (.odp) |
| **其他** | 邮件 (.eml), 电子书 (.epub), 纯文本, HTML, Markdown, JSON, XML |

AI 可以直接读取所有这些文件。它不需要将它们上传到任何外部服务。文件内容保留在你的服务器上，并在本地处理。

---

## "总结这份报告"

> **你：** *(将 PDF 拖放入文件浏览器)* <br/>
> 你能阅读这份季度报告并给我关键要点吗？

AI 打开 PDF，通读它，并给出一个简洁的摘要，提取收入数据、关键决策、显著变化等所有重要信息。

![AI 读取和分析文件内容](/images/open-terminal-ai-csv-analysis.png)

---

## "查看所有这些发票"

> **你：** /invoices 文件夹中大约有 30 张发票。你能全部读取并制作一个包含供应商名称、日期和金额的电子表格吗？

AI 打开文件夹中的每个文件（即使它们是 PDF 和 Word 文档的混合），提取信息，并创建一个你可以下载的干净电子表格。

![AI 列出文件并提供结构化分析](/images/open-terminal-ai-file-listing.png)

---

## "这些邮件关于截止日期说了什么？"

> **你：** *(上传几个 .eml 文件)* <br/>
> 阅读这些邮件，找出任何提及截止日期或到期日的内容。

AI 读取邮件文件（包括发件人、日期、主题和正文）并提取相关信息。

![AI 读取文件并提取特定信息](/images/open-terminal-ai-file-listing.png)

---

## "分析这些数据并制作图表"

> **你：** *(将 sales_data.xlsx 放入文件浏览器)* <br/>
> 按地区细分销售额并制作饼图。

AI 读取电子表格，处理数据，创建图表，并将其保存为可以预览和下载的图片。

![AI 分析销售数据并按产品汇总](/images/open-terminal-ai-csv-analysis.png)

---

## "搜索所有这些文档"

> **你：** 搜索 /contracts 文件夹中的所有内容，查找任何提及"termination clause"或"cancellation"的地方。

AI 搜索每个文件（PDF、Word 文档、电子表格，无论什么格式），并准确告诉你它在哪些位置找到了匹配项。

![AI 跨文件搜索特定内容](/images/open-terminal-ai-file-listing.png)

:::tip 无需索引
与传统搜索或 RAG 系统不同，AI 每次询问时都会实时读取文件。这意味着它看到的是磁盘上的当前版本：无需重新索引、无需同步延迟、无需管理数据库。
:::

---

## 处理大文件

如果文档非常长，AI 会智能地分段读取，而不是一次性读完。你也可以要求它关注特定部分：

> "只阅读这份报告的执行摘要部分"

> "显示这个电子表格的第 500 到 600 行"

## 更多尝试

- **[从聊天运行代码 →](./code-execution)**：AI 编写、运行和调试代码
- **[构建和预览网站 →](./web-development)**：创建和迭代网页
- **[探索文件浏览器 →](../file-browser)**：上传、预览、下载和编辑文件
