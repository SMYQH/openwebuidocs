---
sidebar_position: 9
title: "应用构建器"
---

# 🏗️ 构建完整应用 {#build-a-complete-application}

描述你想要的，获得一个具有前端、后端和数据库的完整工作应用。

> **你：** $App Builder <br/>
> 帮我做一个库存跟踪器。我需要添加商品并记录名称、数量和价格。请显示库存总价值和低库存预警。

## AI 的工作流程 {#what-the-ai-does}

1. 设计数据库结构
2. 使用 Flask 构建带有 CRUD 接口的 Python API
3. 创建带有仪表盘、图表和搜索功能的精美前端
4. 填充示例数据
5. 启动服务器并测试每个接口
6. 运行中的应用可从[浏览器标签页](../web-development.md#the-browser-tab)的 **端口** 列表中打开

![端口预览中显示一个精致的仪表盘：汇总卡片、按类别划分的柱状图，以及可搜索的商品表格](/images/open-terminal-app-builder-dashboard.png)

![文件浏览器中显示生成的项目结构：app.py、database.py、templates/、static/](/images/open-terminal-app-builder-structure.png)

## 技能内容 {#skill-content}

将下面的内容复制到**工作区 → 技能 → 创建**：

```markdown
---
name: app-builder
description: Builds complete web applications with frontend, backend, and database
---

## Full-Stack Application Builder

When building a web app:

1. **Clarify requirements**: What data is managed? What should the UI show?
2. **Design the database first**: Use SQLite with proper schema
3. **Build the API** with Flask or FastAPI: CRUD, search, filtering, error handling
4. **Build a polished frontend**:
   - Modern CSS (not a skeleton, make it look demo-ready)
   - Dashboard with key metrics and charts (Chart.js)
   - Responsive tables with search
   - Forms for data entry
5. **Seed with realistic sample data** so the demo looks good
6. **Start the server** and test every endpoint with curl
7. **Verify the full flow**: create, read, update, delete, search

Build something polished enough to demo, not a wireframe.
```
