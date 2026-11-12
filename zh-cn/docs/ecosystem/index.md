---
title: "生态系统"
sidebar_position: 1
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# 生态系统 {#ecosystem}

<ThemedImage
  alt="生态系统：中心方块向四周四个方块伸出连接"
  sources={{
    light: useBaseUrl('/images/banners/ecosystem-light.svg'),
    dark: useBaseUrl('/images/banners/ecosystem-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

Open WebUI 是核心 AI 界面和代理控制层。生态系统是一组独立的 Open WebUI 项目，它们连接到核心平台、扩展其功能或解决邻近的任务，同时自身也能独立使用。

**对于新的代理部署，我们推荐 [Open WebUI](/getting-started) 搭配 [Open Terminal](/features/open-terminal)。**

## 项目 {#projects}

- [**Open Terminal 与终端**](/ecosystem/open-terminal)：把 Open WebUI 变成完整代理框架的行动层，以及面向企业的编排器——它按策略为每位用户开通受管控的工作区，覆盖镜像、工具、资源、存储、安全上下文、清理与重置。
- [**知识库同步 (oikb)**](/ecosystem/knowledge-base-sync)：将文件夹、仓库、存储桶、Wiki 和其他来源镜像到 Open WebUI 知识库，支持增量同步。
- [**Tether**](/ecosystem/tether)：桌面伴侣应用，把你自己的电脑作为终端连接到 Open WebUI，并显示桌面通知。
- [**Open WebUI 社区**](/ecosystem/community)：位于 openwebui.com 的社区平台，人们在这里分享模型、提示词、工具、函数和聊天，评价模型，并按真实使用量排名。模型、提示词、工具和函数可以直接从帖子导入你的实例。

## 逐步弃用 {#being-phased-out}

[Open WebUI Computer](/ecosystem/computer) 正在逐步弃用。其文档仍会为现有安装保留。
