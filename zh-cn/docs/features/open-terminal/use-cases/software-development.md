---
sidebar_position: 2
title: "软件开发"
---

# 软件开发

Open Terminal 使 AI 能够与真实的代码库交互：克隆仓库、运行测试、读取错误、安装依赖以及迭代修复。

:::tip
如需可从任何设备访问的完整开发环境，请参阅 [**Open WebUI Computer**](/ecosystem/computer)。你的计算机在浏览器标签页中。
:::

---

## 克隆和探索仓库

> **你：** 克隆 https://github.com/user/project 并给我一个代码库概览。架构是什么样的？入口点在哪里？

AI：
1. 运行 `git clone` 拉取仓库
2. 扫描目录结构，读取关键文件（`README`、`package.json`、`pyproject.toml` 等）
3. 识别技术栈、入口点和主要组件
4. 返回包含文件数量、依赖关系和架构说明的结构化摘要

![AI 列出项目文件并描述结构](/images/open-terminal-ai-file-listing.png)

---

## 运行测试套件并修复失败

> **你：** 运行测试。如果有任何失败，找出原因并修复。

AI：
1. 检测测试框架（`pytest`、`jest`、`go test` 等）
2. 如果需要，安装依赖
3. 运行完整的测试套件
4. 读取失败输出，追踪错误，编辑源代码
5. 重新运行失败的测试以确认修复

![AI 运行测试并迭代修复](/images/open-terminal-ai-test-suite.png)

:::tip 迭代式调试
AI 看到的是开发者会看到的相同终端输出：堆栈跟踪、断言错误、日志消息。"运行、读取错误、修复、重新运行"的多轮操作会自动进行。
:::

---

## 设置开发环境

> **你：** 设置这个项目，以便我可以在上面进行开发。安装所有依赖，创建数据库，然后运行开发服务器。

AI：
1. 读取设置文档（`README`、`Makefile`、`docker-compose.yml`）
2. 安装系统包和语言依赖
3. 创建配置文件，设置数据库，运行迁移
4. 启动开发服务器并确认它正在运行
5. 报告你可以访问的 URL

![AI 安装依赖并运行项目](/images/open-terminal-ai-install-run.png)

---

## 自信地重构

> **你：** 将 `users.py` 中的数据库查询重构为使用 async/await。确保测试仍然通过。

AI：
1. 读取当前实现
2. 按你要求的更改重写代码
3. 运行测试套件以验证没有破坏任何东西
4. 如果测试失败，调整重构后的代码直到它们通过
5. 显示更改的 `git diff`

![AI 自动调试和修复代码错误](/images/open-terminal-ai-debug-fix.png)

---

## Git 工作流

> **你：** 显示自上一个发布标签以来的更改。总结提交信息。

AI 直接使用 Git 工作：

- `git log`、`git diff`、`git blame` 分析历史
- 创建分支、暂存更改、提交
- 从提交历史生成变更日志
- 使用 `git bisect` 查找错误引入的时间点
- 解决合并冲突

![AI 初始化 git 仓库并使用 git 工作](/images/open-terminal-ai-git-workflow.png)

---

## 编写和运行测试

> **你：** 为 `orders.py` 中的 `calculate_shipping()` 函数编写单元测试。覆盖边界情况。

AI：
1. 读取函数以理解其逻辑和参数
2. 识别边界情况（数量为零、负值、国际与国内、免运费门槛）
3. 使用项目现有的测试框架编写测试用例
4. 运行测试以验证它们通过
5. 如果任何测试失败，判断是测试错误还是代码错误

![AI 使用 pytest 编写和运行单元测试](/images/open-terminal-ai-test-suite.png)

---

## 调试特定问题

> **你：** 用户报告登录端点有时返回 500。这是来自日志的错误：`KeyError: 'session_token'`。找到并修复它。

AI：
1. 搜索代码库中 `session_token` 的使用位置
2. 阅读周围代码以理解流程
3. 识别错误（例如，会话过期时缺少键检查）
4. 编写带有适当错误处理的修复
5. 为边界情况添加测试用例
6. 运行测试以确认

![AI 在代码库中查找并修复错误](/images/open-terminal-ai-debug-fix.png)

---

## 构建和验证 API

> **你：** 创建一个用于管理书店的 REST API。我需要书籍、作者和分类的 CRUD 操作。使用 FastAPI 和 SQLite。

AI：
1. 搭建项目结构
2. 定义数据库模型和模式
3. 实现所有端点并包含验证
4. 创建种子数据
5. 启动服务器并使用 `curl` 测试每个端点
6. 显示 Swagger 文档页面

![AI 创建并运行 Web 应用程序](/images/open-terminal-ai-web-dev.png)

---

## 支持哪些语言和工具？

Docker 镜像预装了常见的开发工具：

| 类别 | 可用工具 |
| :--- | :--- |
| **语言** | Python, Node.js, Ruby, C/C++, Bash |
| **包管理器** | pip, npm, gem, apt |
| **版本控制** | Git |
| **编辑器** | nano, vim |
| **构建工具** | make, gcc, g++ |

AI 可以即时安装其他工具：Rust、Go、Java、Docker CLI、数据库客户端以及通过 `apt` 或语言特定包管理器可用的任何其他工具。

## 相关

- **[代码执行 →](./code-execution)**：快速脚本和一次性任务
- **[Web 开发 →](./web-development)**：构建和预览网站
- **[高级工作流 →](./advanced-workflows)**：代码审查、数据库分析等技能
