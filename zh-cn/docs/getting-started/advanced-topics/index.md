---
sidebar_position: 500
title: "高级主题"
---

# 高级主题 {#advanced-topics}

**突破默认配置：为生产部署扩容和调试 Open WebUI，并了解如何参与开发。**

Open WebUI 开箱即可满足个人使用，但真实部署通常需要更多能力：生产数据库、横向扩展、结构化日志、可观测性。本分区覆盖了从“它能在我笔记本上跑起来”到“它服务整个组织”之间的关键内容。

---

## 为什么需要高级主题？ {#why-advanced-topics}

### 扩展到单容器之外 {#scale-beyond-a-single-container}

默认的 SQLite 数据库和单工作进程配置最多只能满足小团队的需求。了解如何切换到 PostgreSQL、使用 Redis 共享状态、在负载均衡器后运行多个副本，以及选择外部向量数据库，无需重构部署架构。

### 更有把握地调试 {#debug-with-confidence}

当规模化环境中出现问题时，第一个问题永远是“日志里写了什么？”你可以配置日志级别、为日志聚合器启用结构化 JSON 输出，并接入 OpenTelemetry 以获得贯穿全栈的链路追踪。

### 参与项目贡献 {#contribute-to-the-project}

你还可以搭建本地开发环境，让前端与后端支持热重载，理解贡献流程，并开始提交 pull request。

---

## 本节内容 {#whats-covered}

| | |
| :--- | :--- |
| 🚀 **[扩展 Open WebUI](scaling)** | 从 SQLite 切换到 PostgreSQL，加入 Redis，运行多副本，配置外部向量数据库，并搭建共享存储与可观测性 |
| 🪵 **[Open WebUI 日志](logging)** | 配置日志级别、启用调试输出，并为生产日志聚合器切换到结构化 JSON 日志 |
| 🛠️ **[开发 Open WebUI](development)** | 克隆仓库、前后端并行运行、在其他设备上测试并提交 pull request |
| 🔒 **[强化 Open WebUI 安全](hardening)** | 为生产部署收紧认证、密钥、CORS、安全头、审计日志和网络访问 |
