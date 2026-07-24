---
title: "Open WebUI Computer"
sidebar_position: 1
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# Open WebUI Computer

<ThemedImage
  alt="展示桌面和手机上的真实工作区的 Open WebUI Computer"
  sources={{
    light: useBaseUrl('/images/banners/computer-light.svg'),
    dark: useBaseUrl('/images/banners/computer-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**你的电脑，随时随地。**

Open WebUI Computer（`cptr`）在你的机器上运行，将整个电脑呈现在任何浏览器中：文件、编辑器、终端、git、AI 聊天和编码代理。你可以从手机、平板或另一台电脑上打开它。一切都原封不动地留在你离开的地方，因为它*就是*你的机器，而不是它的副本。

```bash
pip install cptr
cptr run
```

就这样安装好了。它会打印一个一次性设置链接，你创建账户，打开一个文件夹，然后就能在浏览器中看到你真实的文件。[快速入门 →](/ecosystem/computer/quickstart) · [在 GitHub 上查看 →](https://github.com/open-webui/computer)

想知道这到底是什么（远程桌面？IDE？AI 助手？）：[什么是 Computer？](/ecosystem/computer/what-is-computer) 用两分钟给你一个思维模型。

## 你想做什么？

| 我想…… | 前往 |
| --- | --- |
| 两分钟内看到效果 | [快速入门](/ecosystem/computer/quickstart) |
| 看看别人用它做什么 | [使用场景](/ecosystem/computer/use-cases/) |
| 在手机上使用，离家在外 | [手机和远程访问](/ecosystem/computer/phone-and-remote/) |
| 关闭标签页后或机器重启时保持终端和代理继续运行 | [保持运行](/ecosystem/computer/phone-and-remote/keep-it-running) |
| 使用我已经付费的 Claude Code / Codex / Cursor 订阅 | [编码代理](/ecosystem/computer/ai/coding-agents) |
| 连接 OpenAI、Anthropic、Ollama 或任何兼容的 API | [连接模型](/ecosystem/computer/ai/connect-a-model) |
| 从 Telegram、Discord、Slack、WhatsApp 或 Signal 给我的电脑发消息 | [消息机器人](/ecosystem/computer/automate/messaging-bots) |
| 按计划运行 AI 任务（"每天早上运行测试"） | [定时任务](/ecosystem/computer/automate/scheduled-tasks) |
| 在 Open WebUI 中使用 Computer 工作区作为模型 | [Open WebUI 集成](/ecosystem/computer/automate/open-webui) |
| 在 Docker 中运行 | [Docker](/ecosystem/computer/install/docker) |
| 了解我的数据存放在哪里以及如何备份 | [数据和备份](/ecosystem/computer/operate/data-and-backups) |
| 查找标志、环境变量或网关 API | [参考](/ecosystem/computer/reference/) |
| 解决问题 | [故障排除](/ecosystem/computer/troubleshooting) · [常见问题](/ecosystem/computer/faq) |

## 它是什么

浏览器标签页中的工作站。真实的文件，配备完整的编辑器。关闭标签页后仍在运行的 shell，当你从另一台设备重新连接时它还在那里。Git（状态、差异、暂存、提交、分支）无需使用命令行，除非你想用。每个项目的工作区，其聊天、布局和历史记录都保存在一起。

AI 是可选的且可插拔：提供 API 密钥，通过 Ollama 指向本地模型，或接入你已经订阅的编码代理。代理在你的真实项目中工作：它读取文件、编辑、运行命令和浏览网页，每个聊天都设有审批控制。没有配置 AI？其他一切功能仍然可用。

## 它的定位

Open WebUI 是 AI 界面和工作流平台。Open Terminal 为 Open WebUI 聊天提供干净的执行环境。Computer 为你已有的工作机器提供服务，它也可以[作为 Open WebUI 的模型提供商](/ecosystem/computer/automate/open-webui)。不确定你需要哪一个？[比较一下](/ecosystem/computer/choose)。

## 隐私优先设计

Computer 运行在你控制的硬件上，除非你配置它，否则不会与外界通信。在将其暴露到任何地方之前需要了解一件事：已登录用户在你选择的边界内拥有与键盘前操作者相同的权限，即在裸机安装上拥有完整的文件系统和 shell 访问权限，或者如果你[在 Docker 中运行](/ecosystem/computer/install/docker)则仅限于你挂载的文件夹。像对待 SSH 一样对待访问权限，将其保持在像 [Tailscale](/ecosystem/computer/phone-and-remote/tailscale) 这样的私有网络路径上，并在与任何人共享之前阅读[安全模型](/ecosystem/computer/phone-and-remote/security)。

Open WebUI Computer（`cptr`）运行在你的机器上，将整个系统通过任何浏览器提供服务：文件、编辑器、终端、Git、AI 聊天和编码代理。从你的手机、平板或另一台电脑上打开它。一切都在你离开时的位置，因为它就是*你的*机器，而不是它的副本。
