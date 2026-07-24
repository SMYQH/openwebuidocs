---
title: "从 Telegram 给你的电脑发消息"
sidebar_position: 5
---

# 从 Telegram 给你的电脑发消息

你在外面，想知道你启动的构建是否通过了，不想打开笔记本电脑甚至浏览器标签页。所以你对你的电脑像对人一样发消息：

> ~/code/api 中的构建完成了吗？如果失败了，粘贴最后几行

它回答你，因为"它"是在该工作区中运行的完整代理。

**你需要：** 完成快速入门，已连接 [AI 模型](/ecosystem/computer/ai/)，以及五分钟设置机器人。不需要隧道或公共 URL；Telegram 向外长轮询。（Discord、Slack 和 Signal 的工作方式相同；WhatsApp 需要公共 webhook。参见[消息机器人](/ecosystem/computer/automate/messaging-bots)了解这些平台。）

## 操作步骤

1. **创建机器人。** 在 Telegram 上给 [@BotFather](https://t.me/BotFather) 发消息，发送 `/newbot`，命名并复制令牌。

2. **将其添加到 Computer。** 在**设置 → 管理 → 机器人**中，创建一个机器人，选择 Telegram，粘贴令牌，点击**验证**。

3. **锁定给你自己。** 将你的数字 Telegram 用户 ID 放入**允许发送者**（像 @userinfobot 这样的机器人会告诉你你的 ID）。这是人们跳过且不应该跳过的步骤：空列表会回复任何找到机器人的人，而机器人消息以完全工具审批模式运行。

4. **选择它的家。** 选择机器人启动时使用的工作区和模型，然后启动它。

5. **与它对话。** 问构建的问题。你会看到回复在代理工作时流式传入：先是工具活动行，然后是答案。对话中有用的命令：

   - `/workspace api` 切换项目
   - `/new` 开始新的聊天，`/stop` 取消失控的任务
   - `/model` 即时切换模型

6. **稍后在浏览器中继续。** 每个机器人对话都是该工作区中的真实聊天；当你回到电脑屏幕前时，它就在侧边栏中，包含完整的历史记录。

## 为什么这样有效

机器人不是一个通知垫片；它是 Web 聊天使用的相同代理循环，在你选择的工作区中具有文件、终端和工具访问权限。这也是为什么允许发送者列表不可协商，以及为什么固定到一个范围明确的工作区的机器人比指向你的主目录的机器人更好。从外面问只读问题；把破坏性的操作留到你能看到差异时再做。

**深入了解：** [消息机器人](/ecosystem/computer/automate/messaging-bots) · [通知](/ecosystem/computer/automate/notifications) · [安全模型](/ecosystem/computer/phone-and-remote/security)
