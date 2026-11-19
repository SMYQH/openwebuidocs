---
sidebar_position: 0
title: "高级工作流"
---

# 使用技能的高级工作流 {#advanced-workflows-with-skills}

这些工作流将多种 Open Terminal 能力组合成强大的多步骤流水线。每个工作流都包含一个**技能（Skill）**——你在 Open WebUI 中创建的可复用指令集，它告诉 AI 如何处理特定类型的任务。

---

## 什么是技能？ {#what-are-skills}

**技能**是一组你保存在 Open WebUI 中的可复用 Markdown 指令。当你调用某个技能时，其指令会注入到该对话的 AI 系统提示中，使 AI 成为该特定任务的专家。

就像在让人做某件工作前给他一份详细的 SOP（标准操作流程）——只是 AI 可以在不同对话中始终如一地参考这份流程。

### 创建技能 {#creating-a-skill}

1. 点击左侧边栏的**工作区**
2. 点击**技能**
3. 点击**创建**（+ 按钮）
4. 填写**名称**（例如"数据报告生成器"）和**描述**
5. 在**内容区域**用 Markdown 编写指令
6. 点击**保存并创建**

![Open WebUI 模型能力页面](/images/open-terminal-model-capabilities.png)

:::tip Frontmatter 快捷方式
如果技能指令以 YAML frontmatter 开头，名称和描述字段会自动填充：

```markdown
---
name: data-report-generator
description: Analyzes data files and creates professional PDF reports
---

## Instructions
When asked to analyze data:
1. First, read the file...
```
:::

### 使用技能 {#using-a-skill}

有两种方式使用技能：

**方式 1：在聊天中提及（`$`）**

在聊天输入框中输入 `$`，然后按名称搜索你的技能。选择后，AI 会在该对话中接收**完整指令**。这适合你想明确告诉 AI 现在遵循特定技能的情况。

![AI 使用技能和结构化工作流与数据交互](/images/open-terminal-ai-csv-analysis.png)

**方式 2：让 AI 自动发现技能**

启用内置工具并打开模型的**技能**类别后，AI 会**在任务相关时自动发现并使用你有权读取的任何已启用技能**，无需在对话中提及。前往**工作区 → 模型 → 编辑**，在**技能**一栏将技能附加到模型，即可在对话中预选它。若未启用内置工具，附加技能的指令会注入该模型的每个对话。

幕后工作原理：

1. AI 收到一份清单，列出你有权读取的所有已启用技能的**名称和描述**，包括已附加的技能。完整指令只在需要时加载
2. 当请求与某项技能的描述匹配时，AI **自主调用内置的 `view_skill` 工具**，加载指令和配套文件列表
3. AI 然后按这些指令处理你的请求

如果工作区中有可用的「数据报告生成器」技能，你上传 CSV 并说「分析这个」时，AI 就会自动加载并遵循报告指令。无需记住该技能的名称。

![模型能力设置页面](/images/open-terminal-model-capabilities.png)

:::tip 附加多个技能打造瑞士军刀型模型
将多个技能附加到单个模型，使其成为多用途专家。上传电子表格 → 加载数据分析技能。说"调研电动汽车电池" → 加载研究技能。构建着陆页 → 加载 Web 开发技能。全部自动完成。
:::

### 分享技能 {#sharing-skills}

技能有访问控制。你可以：
- 保持**私有**（仅自己可用）
- 与**特定用户或群组**共享
- 设为**公开**（实例上所有人可用）

在技能编辑器中点击**访问**按钮，设置谁可以使用该技能。非管理员只有获得**技能共享**权限后才看得到该按钮。

![AI 集成设置和访问控制](/images/open-terminal-integrations-page.png)

---

## 工作流库 {#workflow-library}

以下每个页面都是一个完整工作流，包含可直接粘贴的技能：

| 工作流 | 功能说明 |
| :--- | :--- |
| **[数据报告](./data-reports)** | 将杂乱的 CSV 转化为带有图表的精美 PDF 报告 |
| **[数据库分析](./database-analysis)** | 连接 PostgreSQL/MySQL/SQLite，运行查询，产出洞察 |
| **[研究助手](./research-assistant)** | 收集网络资料并撰写结构化简报 |
| **[邮件处理](./email-processing)** | 从 .eml 文件中提取待办事项和截止日期 |
| **[文档比较](./document-comparison)** | 对合同或提案的两个版本进行差异对比 |
| **[财务仪表盘](./finance-dashboard)** | 分析银行账单并生成支出图表 |
| **[图像处理](./image-processing)** | 批量调整大小、添加水印和转换图片格式 |
| **[竞争分析](./competitive-analysis)** | 抓取竞争对手定价并建立比较 |
| **[应用构建器](./app-builder)** | 从描述中构建完整的 Web 应用 |
| **[代码审查](./code-review)** | 审查代码变更的安全性、性能和风格问题 |

---

## 编写优质技能的技巧 {#tips-for-writing-great-skills}

### 让指令具体 {#keep-instructions-specific}
差：「分析数据」
好：「读取文件，统计行数，识别列，检查缺失值，然后按类别计算平均值」

### 对步骤编号 {#number-your-steps}
LLM 遵循编号指令比遵循散文段落更可靠。

### 包含输出预期 {#include-output-expectations}
告诉技能最终交付物应该是什么样：「创建一个包含封面和 3 个部分的 PDF」比「做一份报告」更好。

### 测试并迭代 {#test-and-iterate}
创建技能，在真实任务上试用，并根据 AI 做对做错的地方完善指令。

### 与 Open Terminal 能力结合 {#combine-with-open-terminal-capabilities}
真正的力量来自于将技能与 Open Terminal 的工具结合：文件读取、代码执行、网页预览和文件浏览器。指令中写「读取电子表格，用 Python 生成图表，并保存为 PNG」可以充分发挥所有这些功能。
