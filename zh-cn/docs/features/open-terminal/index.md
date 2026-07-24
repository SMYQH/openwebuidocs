---
sidebar_position: 3
title: "Open Terminal"
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Open Terminal

<ThemedImage
  alt="Open Terminal：Open WebUI 核心驱动真实的终端会话循环，运行命令并读取输出"
  sources={{
    light: useBaseUrl('/images/banners/terminal-light.svg'),
    dark: useBaseUrl('/images/banners/terminal-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**给你的 AI 一台真正的计算机来工作。**

Open Terminal 将真实计算环境连接到 Open WebUI。AI 可以编写代码、执行代码、读取输出、修复错误并迭代，全程无需离开聊天界面。它可以处理文件、安装软件包、运行服务器，并直接将结果返回给你。你可以在 Docker 容器中运行以实现隔离，也可以直接运行在裸机上以获取对机器的完全访问权限。

在这里，想法变成可运行的软件。提出一个问题，得到一个可运行的脚本。描述一个网站，看到它实时渲染。指向一个数据集，获得一份完整的报告。

![Open WebUI 配合 Open Terminal，显示文件浏览器侧边栏和聊天界面](/images/open-terminal-file-browser.png)

:::tip 想要"浏览器中的电脑"？
Open Terminal 是**聊天 AI** 驱动的工具。如果你想要从任何浏览器操作自己的机器（文件、编辑器、终端和 git，移动优先），AI 作为可选助手，请参阅 [**Open WebUI Computer**](/ecosystem/computer)，一个独立的 Open WebUI 项目。[选择合适的执行环境](/ecosystem/computer/choose)。
:::

---

## 功能

### 数据分析与报告

上传电子表格、CSV 文件或数据库。AI 读取数据、运行分析脚本并生成图表或报告。

![AI 分析电子表格数据](/images/open-terminal-ai-csv-analysis.png)

### 文档搜索与提取

将 AI 指向包含 PDF、Word 文档或邮件的文件夹。它将读取所有文件并返回结构化结果：摘要、提取的字段或交叉引用。

{/* TODO: 截图 — 用户询问 Johnson 合同的聊天。AI 列出在文件夹中找到的文件（contract_v2.docx、notes.pdf、invoice.xlsx），并提供来自每个文件的相关信息的汇总摘要。 */}

### Web 开发与实时预览

AI 构建 HTML/CSS/JS 项目，启动预览服务器，并在 Open WebUI 内渲染结果。通过在聊天中描述更改来进行迭代。

{/* TODO: 截图 — 屏幕左侧为聊天界面。右侧为实时网站预览面板，显示一个干净的活动落地页，包含横幅、日期和注册按钮。 */}

### 软件开发

克隆仓库、运行测试套件、调试失败、重构代码以及使用 Git，全部通过自然语言完成。

### 文件与系统自动化

批量重命名、排序、去重、转换、压缩和组织文件。管理磁盘空间、计划备份、处理日志。

{/* TODO: 截图 — 用户要求"将所有照片重命名为包含日期"的聊天。AI 回复确认"已重命名 43 个文件"，并附带前后示例：IMG_4521.jpg → 2025-03-15_IMG_4521.jpg。 */}

---

## 主要特性

| | |
| :--- | :--- |
| 🖥️ **代码执行** | 运行真实命令并返回输出 |
| 📁 **文件浏览器** | 在侧边栏中浏览、上传、下载和编辑文件 |
| 📄 **文档读取** | PDF、Word、Excel、PowerPoint、RTF、EPUB、邮件 |
| 🌐 **网站预览** | 在 Open WebUI 内实时预览 Web 项目 |
| 🔒 **可选隔离** | 在 Docker 容器中运行以实现沙箱隔离，或直接运行在裸机上以获得完全访问权限 |

---

## 开始使用

**[安装 →](./setup/installation)** · **[连接到 Open WebUI →](./setup/connecting)**

:::info 模型要求
Open Terminal 需要具备 agent 级工具调用质量的模型，而不仅仅是技术上支持工具调用的模型。驱动终端是一个多步骤循环：调用工具、读取输出、决定下一个命令、重复，通常需要很多轮。小型模型无法维持这种操作。4B 到 9B 的模型在这里不够用，即使它勾选了"支持工具"的框。Frontier 级模型（GPT-5.4、Claude Sonnet 4.6、Gemini 3.1 Pro）能很好地处理这些复杂的多步骤工作流。从 v0.10.0 开始，原生是默认的工具调用模式，因此除非模型已切换到 Legacy 模式，否则开箱即用；如果工具无法触发，请[检查模型的工具调用模式](./setup/connecting#8-enable-native-function-calling)。
:::

---

## 使用场景

- **[代码执行](./use-cases/code-execution)**：编写、运行和调试脚本
- **[软件开发](./use-cases/software-development)**：仓库、测试、调试、重构、Git
- **[文档与数据分析](./use-cases/file-analysis)**：电子表格、PDF、Word 文档、邮件
- **[Web 开发](./use-cases/web-development)**：构建和预览网站
- **[系统自动化](./use-cases/system-automation)**：文件管理、备份、批量操作
- **[高级工作流](./use-cases/advanced-workflows)**：数据报告、研究、代码审查等技能
- **[文件浏览器](./file-browser)**：上传、预览、编辑文件

---

## 企业多用户

需要为团队提供隔离的、每个用户独立的终端容器？**[Terminals](./terminals/)** 为每个用户预配专用的 Open Terminal 实例，并支持自动生命周期管理、资源控制和基于策略的环境。

---

## 您的完整机器

Open Terminal 为 Open WebUI 添加了计算环境。[**Open WebUI Computer**](/ecosystem/computer) 就是计算机本身：文件、终端、git、编辑器和 AI 都在一个浏览器标签页中，可从任何设备访问。
