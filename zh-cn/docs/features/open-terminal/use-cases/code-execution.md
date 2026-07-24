---
sidebar_position: 1
title: "代码执行"
---

# 代码执行

Open Terminal 允许 AI 实时编写、执行和调试代码。它处理完整的周期：编写脚本、运行脚本、读取错误并迭代，直到结果正确为止。

---

## 数据可视化

> **你：** 创建一个显示人口最多的前 10 个国家的图表。

AI 编写 Python 脚本，执行它，并保存输出。结果可在文件浏览器中查看。

![AI 创建并运行 Python 脚本及输出](/images/open-terminal-ai-code-execution.png)

---

## 下载和处理文件

> **你：** 从这个网页下载图片并按大小排序。

AI 安装所需包，编写脚本，下载文件并整理它们：

![AI 安装库并运行脚本](/images/open-terminal-ai-install-run.png)

:::tip 自动安装依赖
在 Docker 模式下，AI 可以根据需要安装软件包。如果某个任务需要未预装的库，它会在继续之前自动安装。
:::

---

## 自我纠错

当代码失败时，AI 读取错误输出并调整：

> **你：** 从这个新闻网站抓取所有文章标题。

AI 编写一个爬虫，遇到意外的页面布局，读取 `AttributeError` 回溯信息，调整 CSS 选择器，并成功重新运行。

![AI 检测到错误，修复脚本并成功运行](/images/open-terminal-ai-debug-fix.png)

---

## 多步骤项目脚手架

> **你：** 创建一个带有 Web 界面和数据库的待办事项应用。

AI：
1. 创建项目文件（HTML、CSS、JavaScript、Python 后端）
2. 安装依赖
3. 设置数据库
4. 启动服务器
5. 在 Web 预览中验证结果

![AI 列出文件并描述项目结构](/images/open-terminal-ai-file-listing.png)

---

## 系统查询

> **你：** 检查什么占用了最多的磁盘空间。

![AI 分析磁盘使用情况并识别大文件](/images/open-terminal-ai-disk-usage.png)

---

## 可用语言

| 语言 | 状态 |
| :--- | :--- |
| Python | 预装 |
| JavaScript (Node.js) | 预装 |
| Bash | 始终可用 |
| Ruby | 预装 |
| C / C++ | 编译器预装 |

其他语言（Rust、Go、Java 等）可以在需要时即时安装。

## 相关

- **[软件开发 →](./software-development)**：仓库、测试、调试、重构
- **[文档与数据分析 →](./file-analysis)**：电子表格、PDF、Word 文档
- **[Web 开发 →](./web-development)**：构建和预览网站
- **[系统自动化 →](./system-automation)**：文件管理、备份、批量操作

:::tip
想要在你的真实机器上拥有持久环境？[**Open WebUI Computer**](/ecosystem/computer) 将你的计算机放入浏览器标签页，可从任何设备访问。
:::
