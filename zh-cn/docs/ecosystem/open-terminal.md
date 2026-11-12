---
title: "Open Terminal & Terminals"
sidebar_position: 2
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Open Terminal & Terminals

<ThemedImage
  alt="终端：一个带光标的屏幕方块"
  sources={{
    light: useBaseUrl('/images/banners/terminal-light.svg'),
    dark: useBaseUrl('/images/banners/terminal-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**把 Open WebUI 变成一套完整的智能体框架：控制层、行动层，以及两者之间的反馈闭环。**

[Open Terminal](/features/open-terminal)是补全 Open WebUI 框架的行动层。Open WebUI 已经具备模型、聊天、提示、知识库、工具、MCP 连接、记忆、用户、权限、自动化任务以及工作流控制。Open Terminal 补上的是计算机底座：文件、shell、包管理器、运行中的进程、文档与数据处理、生成的产物以及实时预览。

它为模型提供了一个有状态的工作区，模型可以在其中创建、运行、检查、修复，并交回可直接使用的结果。

当一次聊天需要的不只是文字答案时就用它：分析电子表格、编写脚本、构建一个小应用、渲染报告、检查日志、运行测试、整理文件，或启动一个服务器并预览结果。Open WebUI 依然是界面；Open Terminal 则给智能体一个真正能产出这些结果的工作区。

[Terminals](/features/open-terminal/terminals/) 是面向企业版的 Open Terminal 编排器。它把单个智能体工作区变成一支受管理的集群：按用户和策略划分独立工作区、受控镜像、资源限制、存储、环境变量、安全上下文、空闲清理、刷新以及定时重置。

## 那些熟悉的说法 {#the-familiar-words}

如果你听人们谈论过智能体框架、agentic 工作流、工具使用、计算机使用、运行时、护栏和编排，那么 Open Terminal 与 Terminals 就在这里对上了号。

| 人们常用的说法 | 在这里的含义 |
| :--- | :--- |
| **智能体框架** | Open WebUI 加上 Open Terminal：控制、上下文与工具来自 Open WebUI，真实的行动与观察发生在 Open Terminal |
| **Agentic 工作流** | 模型进行规划、采取行动、观察结果并继续推进，而不是给出一个静态答案 |
| **工具使用 / 函数调用** | Open WebUI 让模型调用工具；Open Terminal 为这些工具提供真实的文件系统、shell 与进程环境 |
| **计算机使用** | 智能体在一个类计算机的工作区中工作：文件、命令、软件包、预览和生成的产物 |
| **智能体运行时** | 模型周围的循环与状态；Open Terminal 在其中提供操作系统级的行动工作区 |
| **有状态会话** | 工作区把文件、输出、进程和任务上下文保留足够久，以支撑多步骤工作 |
| **护栏 / 人工复核** | Open WebUI 控制用户、模型、工具与审批层；Terminals 依据策略控制工作区边界 |
| **编排** | Terminals 为团队置备、路由、隔离、刷新并清理 Open Terminal 工作区 |
| **可观测性 / 可审计性** | 管理员可以推知是哪个用户、策略、工作区、镜像、限制和生命周期产生了某个结果 |

## 从 Open Terminal 开始 {#start-with-open-terminal}

| 我想要…… | 前往 |
| :--- | :--- |
| 了解产品定位 | [Open Terminal 概览](/features/open-terminal) |
| 安装 Open Terminal | [安装](/features/open-terminal/setup/installation) |
| 把它连接到 Open WebUI | [连接](/features/open-terminal/setup/connecting) |
| 浏览、上传、预览和编辑文件 | [文件浏览器](/features/open-terminal/file-browser) |
| 运行代码并调试脚本 | [代码执行](/features/open-terminal/use-cases/code-execution) |
| 进行软件开发 | [软件开发](/features/open-terminal/use-cases/software-development) |
| 分析文档与数据 | [文档与数据分析](/features/open-terminal/use-cases/file-analysis) |
| 构建并预览 Web 应用 | [Web 开发](/features/open-terminal/use-cases/web-development) |
| 把 Claude Code、Codex 或 Pi 当作聊天模型使用 | [编码智能体](/features/open-terminal/coding-agents) |
| 自动化文件夹和系统任务 | [系统自动化](/features/open-terminal/use-cases/system-automation) |
| 查看更完整的工作流 | [高级工作流](/features/open-terminal/use-cases/advanced-workflows) |

## 用 Terminals 横向扩展 {#scale-with-terminals}

当智能体工作区需要按策略置备、隔离、复用、刷新和重置，而不是一次手工接线一个环境时，就使用 Terminals。

| 我想要…… | 前往 |
| :--- | :--- |
| 阅读 Terminals 概览 | [Terminals 概览](/features/open-terminal/terminals/) |
| 了解置备流程 | [编排](/features/open-terminal/terminals/orchestration) |
| 配置镜像、资源、存储、环境变量和空闲超时 | [策略](/features/open-terminal/terminals/orchestration/policies) |
| 了解环境变量转发与保留键 | [环境变量](/features/open-terminal/terminals/orchestration/environment-variables) |
| 构建并发布自定义工作区镜像 | [自定义镜像](/features/open-terminal/terminals/orchestration/custom-images) |
| 在策略变更后刷新用户 | [应用变更](/features/open-terminal/terminals/orchestration/applying-changes) |
| 按计划重置已持久化的工作区 | [定时重置](/features/open-terminal/terminals/orchestration/scheduled-resets) |
| 在 OpenShift 上运行 | [OpenShift](/features/open-terminal/terminals/orchestration/openshift) |
| 调整生成的系统提示 | [系统提示](/features/open-terminal/terminals/orchestration/system-prompts) |
| 暴露干净的文件浏览器根目录 | [文件浏览器根目录](/features/open-terminal/terminals/orchestration/file-browser-home-boundary) |
| 调试 API 与支持问题 | [API 与故障排查](/features/open-terminal/terminals/orchestration/api-troubleshooting) |

## 该如何理解它 {#how-to-think-about-it}

Open WebUI 是这套框架的控制侧：模型、聊天、提示、知识库、用户、权限、自动化任务、工具、审批与共享工作流。Open Terminal 则补上聊天背后那个形如操作系统的、原本缺失的行动层。

仅仅加上这一层，就改变了 Open WebUI 的用途。模型可以从"说明下一步怎么做"变成"直接去做下一步"：创建文件、运行命令、检查失败、修复问题，然后交回完成的产物。

智能体循环变得具体起来：

1. 检查工作区。
2. 选择一个行动。
3. 创建或编辑文件。
4. 运行代码、命令、工具或服务器。
5. 读取输出。
6. 修复失败之处。
7. 交回产物。

这就是"关于这项工作的一个答案"与"一个真正动手做这项工作的智能体"之间的差别。

对团队而言，同一个模型就变成了基础设施：

| 层次 | 作用 |
| :--- | :--- |
| Open WebUI | 聊天、用户、权限、模型选择、工具以及可见的工作流 |
| Terminals | 认证、路由、策略解析、置备、生命周期、刷新与清理 |
| Open Terminal 工作区 | 文件、shell、进程、软件包、代码执行、预览与产物 |
| 策略 | 镜像、工具、限制、存储、环境变量、安全上下文与空闲超时 |

用框架工程的术语来说：Open WebUI 加上 Open Terminal 构成完整的框架，Open Terminal 是其中的计算机底座，而 Terminals 则是这些底座的集群管理器。

## 安全地运维它 {#operate-it-safely}

Open Terminal 既可以在 Docker 中隔离运行，也可以直接运行在宿主机上，取决于你希望给智能体多大的访问权限。Terminals 为共享部署补充了策略、生命周期与按用户的隔离。在赋予智能体广泛的文件系统、进程或网络访问权限之前，请先阅读安全与配置相关页面。

| 需求 | 前往 |
| :--- | :--- |
| 安全模型与部署边界 | [安全](/features/open-terminal/advanced/security) |
| 配置选项 | [配置](/features/open-terminal/advanced/configuration) |
| 多用户部署选项 | [多用户](/features/open-terminal/advanced/multi-user) |
| Terminals 故障排查 | [故障排查](/features/open-terminal/terminals/#troubleshooting) |

在生产环境中使用 Terminals 需要 [Open WebUI 企业版许可证](https://docs.openwebui.com/enterprise)。项目位于 [github.com/open-webui/terminals](https://github.com/open-webui/terminals)。
