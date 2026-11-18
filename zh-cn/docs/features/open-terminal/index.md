---
sidebar_position: 3
title: "Open Terminal"
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Open Terminal {#open-terminal}
<ThemedImage
  alt="终端：一个带有光标的屏幕块"
  sources={{
    light: useBaseUrl('/images/banners/terminal-light.svg'),
    dark: useBaseUrl('/images/banners/terminal-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**让 Open WebUI 成为一个完整的智能体框架。**

[在 GitHub 上查看 →](https://github.com/open-webui/open-terminal)

智能体框架是围绕模型的那套系统，让模型能够真正完成工作：指令、上下文、工具、状态、权限、反馈回路、可观测性，以及执行环境。Open WebUI 已经提供了这套框架的控制侧：模型、对话、知识库、提示词、工具、MCP 连接、记忆、用户、权限、自动化以及共享的工作流控件。Open Terminal 补上了大多数聊天产品仍然缺失的那部分：真正以计算机为底座的执行环境，行动在其中运行，证据由此返回。

这意味着智能体自己完成工作。它可以规划、创建文件、运行代码、检查输出、安装依赖、启动服务器、渲染预览、从错误中恢复，并持续进行，直到产出一个可用的成果物：脚本、报告、补丁、图表、网站、迁移脚本，或整理好的文件夹。

Open Terminal 是类计算机的工作区，让 Open WebUI 的智能体循环能够作用于文件、代码、软件包、服务器、文档和生成的成果物。你可以把它运行在 Docker 中以获得隔离，也可以在裸机上运行，让智能体直接作用于宿主机。

![在 Open WebUI 中开启一个新的聊天窗口，此时已选中“Open Terminal”，且“文件”选项卡在聊天窗口旁处于打开状态。](/images/open-terminal-file-browser.png)

## 正确的心智模型 {#the-right-mental-model}
现代智能体工作流不是"一次提问、一次作答"，而是有状态的循环：

1. 理解目标。
2. 检查工作区。
3. 选择一个行动。
4. 执行该行动。
5. 观察结果。
6. 修复、继续或验证。

Open WebUI 负责协调这个循环。Open Terminal 则为循环提供了一个真正发生的场所：可供检查的文件、可供运行的代码、可供验证的输出，以及可以交回的成果物。两者合在一起构成完整的框架：模型、上下文、工具、状态、行动、观察和验证。


## 各部分如何组合在一起 {#how-the-harness-fits-together}

| | Open WebUI | Open Terminal |
| :--- | :--- | :--- |
| 承担的角色 | 控制层：提示词、上下文、工具、状态、权限、用户以及工作流界面 | 动作层：模型可以在其中活动的类计算机工作区 |
| 上下文 | 对话、上传的文件、知识库、记忆、笔记、频道 | 文件、文件夹、终端输出、日志、预览、文档以及生成的工件 |
| 动作 | 内置工具、MCP/OpenAPI 工具、自动化、子代理 | 创建文件、运行命令、安装软件包、执行代码、启动服务器、使用 Git、处理文档 |
| 反馈回路 | 工具调用、对话状态、模型路由以及工作流推进 | 观察工作区、修改它、运行它、检查结果、修复、重试、验证 |
| 边界 | Open WebUI 的权限与配置 | Docker 沙箱或直接的主机访问 |

Open WebUI 加上 Open Terminal 就是完整的智能体框架：控制层、动作层，以及两者之间的反馈回路。

---

## 人们使用的术语 {#the-terms-people-use}

不同团队会用不同的语言来描述这套技术栈。Open Terminal 契合人们描述智能体系统时已经在使用的词汇：

| 人们使用的术语 | 在这里的含义 |
| :--- | :--- |
| **智能体式 AI** | 能够执行多步动作、观察结果并持续推进的模型 |
| **智能体工作流** | 由目标驱动的流程：智能体进行规划、行动、观察结果并调整 |
| **AI 智能体** | 模型加上指令、工具、记忆/上下文以及执行循环 |
| **智能体框架（agent harness）** | 模型周围把推理转化为行动的一整套系统：指令、上下文、工具、状态、权限、反馈回路、评估、可观测性和执行环境 |
| **智能体运行时** | 智能体动作真正执行的地方：文件、代码、命令、服务器、文档和进程 |
| **动作运行时** | 专注于可靠执行现实动作的运行时，具备授权与可审计性 |
| **智能体基础设施** | 在生产环境中运行智能体所需的算力、状态、编排、工具、安全与可观测性 |
| **计算机基底** | 框架提供给智能体、让它能够完成工作的文件系统、shell、软件包、进程、预览和工件 |
| **有状态会话** | 跨多个模型/工具轮次持续存在的任务或工作区，而不是一次无状态的请求 |
| **工具调用 / 函数调用** | 模型选择结构化的工具动作，而不只是书写文本 |
| **工具结果 / 上下文返回** | 动作的输出被返回给模型，以便它决定下一步 |
| **动作工具** | 会修改外部环境的工具，例如编辑文件、发送消息或更改记录 |
| **计算机使用** | 智能体通过文件、命令、界面或浏览器动作操作类计算机环境 |
| **代码解释器** | 用于运行代码的更窄的执行面；Open Terminal 更宽，因为它还包含文件系统、shell、软件包、进程和预览 |
| **MCP / 工具服务器** | 向模型暴露能力的标准方式或基于 API 的方式 |
| **编排** | 选择工具、排列步骤、处理失败并验证结果的循环 |
| **人在回路中** | 在本应由智能体驱动的工作流中设置的人工审批或复核节点 |
| **护栏 / 治理** | 围绕智能体可见与可做之事的策略、权限与安全控制 |
| **可观测性 / 可审计性** | 展示智能体做了什么以及为什么做的日志、追踪和记录 |
| **沙箱** | 围绕智能体文件系统、进程和网络访问的隔离边界 |

实用要点很简单：模型已经足够强大，可以使用工具了；但一个框架的价值取决于它能作用于怎样的环境。Open Terminal 为 Open WebUI 提供了计算机形态的动作层，使整个框架得以完整。

---

## 智能体工作负载 {#agent-workloads}

### 数据分析与报告 {#data-analysis-and-reporting}

上传电子表格、CSV 文件或数据库。AI 读取数据、运行分析脚本并生成图表或报告。

![AI 分析电子表格数据](/images/open-terminal-ai-csv-analysis.png)

### 文档搜索与提取 {#document-search-and-extraction}

将 AI 指向包含 PDF、Word 文档或邮件的文件夹。它将读取所有文件并返回结构化结果：摘要、提取的字段或交叉引用。

![AI 阅读一个合同文件文件夹并总结续约情况](/images/open-terminal-document-search.png)

### Web 开发与实时预览 {#web-development-with-live-preview}

AI 构建 HTML/CSS/JS 项目，启动预览服务器，并在 Open WebUI 内渲染结果。通过在聊天中描述更改来进行迭代。

![聊天界面旁边是 AI 正在提供服务的活动网站的实时预览](/images/open-terminal-live-site-preview.png)

### 软件开发 {#software-development}

克隆仓库、运行测试套件、调试失败、重构代码以及使用 Git，全部通过自然语言完成。

### 文件与系统自动化 {#file-and-system-automation}

批量重命名、排序、去重、转换、压缩和组织文件。管理磁盘空间、计划备份、处理日志。

![AI 将 43 张照片重命名并在文件名前加上日期](/images/open-terminal-bulk-rename.png)

---

## 主要特性 {#what-agents-can-do-with-this-substrate}

| | |
| :--- | :--- |
| 🖥️ **代码执行** | 运行真实命令并返回输出 |
| 📁 **文件浏览器** | 在侧边栏中浏览、上传、下载和编辑文件 |
| 📄 **文档读取** | PDF、Word、Excel、PowerPoint、RTF、EPUB、邮件 |
| 🌐 **网站预览** | 在 Open WebUI 内实时预览 Web 项目 |
| 🔒 **可选隔离** | 在 Docker 容器中运行以实现沙箱隔离，或直接运行在裸机上以获得完全访问权限 |

---

## 开始使用 {#get-started}

**[安装 →](./setup/installation)** · **[连接到 Open WebUI →](./setup/connecting)**

:::info 模型要求
Open Terminal 需要具备 agent 级工具调用质量的模型，而不仅仅是技术上支持工具调用的模型。驱动终端是一个多步骤循环：调用工具、读取输出、决定下一个命令、重复，通常需要很多轮。小型模型无法维持这种操作。4B 到 9B 的模型在这里不够用，即使它勾选了"支持工具"的框。Frontier 级模型（GPT-5.4、Claude Sonnet 4.6、Gemini 3.1 Pro）能很好地处理这些复杂的多步骤工作流。从 v0.10.0 开始，原生是默认的工具调用模式，因此除非模型已切换到 Legacy 模式，否则开箱即用；如果工具无法触发，请[检查模型的工具调用模式](./setup/connecting#8-enable-native-function-calling)。
:::

---

## 使用场景 {#use-cases}

- **[代码执行](/features/open-terminal/use-cases/code-execution)**：编写、运行和调试脚本
- **[软件开发](/features/open-terminal/use-cases/software-development)**：仓库、测试、调试、重构、Git
- **[文档与数据分析](/features/open-terminal/use-cases/file-analysis)**：电子表格、PDF、Word 文档、邮件
- **[Web 开发](/features/open-terminal/use-cases/web-development)**：构建和预览网站
- **[系统自动化](/features/open-terminal/use-cases/system-automation)**：文件管理、备份、批量操作
- **[高级工作流](/features/open-terminal/use-cases/advanced-workflows)**：数据报告、研究、代码审查等技能
- **[文件浏览器](/features/open-terminal/file-browser)**：上传、预览、编辑文件
- **[编程智能体](/features/open-terminal/coding-agents)**：在模型选择器中使用 Claude Code、Codex 等 agent

---

## 企业多用户 {#enterprise-multi-user}

需要为团队提供隔离的、每个用户独立的终端容器？**[Terminals](./terminals/)** 为每个用户预配专用的 Open Terminal 实例，并支持自动生命周期管理、资源控制和基于策略的环境。

---
