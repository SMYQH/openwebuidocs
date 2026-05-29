---
sidebar_position: 26
title: "SERPHouse"
---

:::warning

本教程是社区贡献，不受 Open WebUI 团队支持。仅作为演示如何为特定用例自定义 Open WebUI。想要贡献？请查看[贡献教程](/contributing)。

:::

:::tip

有关网络搜索的所有环境变量的完整列表，请参阅[环境配置文档](/reference/env-configuration#web-search)。

:::

:::tip 故障排除

网络搜索遇到问题？请查看[网络搜索故障排除指南](/troubleshooting/web-search)以解决代理配置、连接超时和内容为空等常见问题。

:::

## 概述

[SERPHouse](https://www.serphouse.com/) 是一个实时 SERP（搜索引擎结果页）API。将其与 Open WebUI 集成，可以让你的语言模型运行实时网络搜索，并根据当前来源进行回答。本指南将 SERPHouse 配置为网络搜索提供商。

## 前提条件

- **已安装 Open WebUI**：正在运行的 Open WebUI 实例（本地或 Docker）。请参阅[入门指南](/getting-started)。
- **SERPHouse 账户**：一个拥有 API 密钥的 [SERPHouse](https://www.serphouse.com/) 账户。
- **管理员权限**：对 Open WebUI 实例的管理员访问权限。

## 逐步配置

### 1. 获取 SERPHouse API 密钥

1. 登录或注册 [SERPHouse](https://www.serphouse.com/)。
2. 打开仪表板的 API 部分，复制或生成一个 API 密钥。确保安全保管。

### 2. 配置 Open WebUI

1. 使用管理员账户登录 Open WebUI。
2. 打开**管理面板 → 设置 → 网络搜索**。
3. 开启**网络搜索**开关。
4. 从**网络搜索引擎**下拉菜单中选择 **serphouse**。
5. 将你的 SERPHouse API 密钥粘贴到 **SERPHouse API 密钥**字段。
6. （可选）设置 **SERPHouse 域名**（要查询的 Google 域名，例如 `google.com`、`google.co.uk`）。
7. 保存你的设置。

### 3. 测试集成

1. 在 Open WebUI 中开始一个聊天会话。
2. 点击提示词字段中的 **加号 (+)** 按钮以启用网络搜索。
3. 输入查询（例如 `+latest AI news`）并确认 SERPHouse 返回实时结果。

## 配置参考

| 设置项 | 环境变量 | 默认值 | 说明 |
|---|---|---|---|
| API 密钥 | [`SERPHOUSE_API_KEY`](/reference/env-configuration#serphouse_api_key) | （空） | 必填。 |
| Google 域名 | [`SERPHOUSE_DOMAIN`](/reference/env-configuration#serphouse_domain) | `google.com` | SERPHouse 查询的 Google 域名。 |

选择 `serphouse` 引擎时，管理 UI 中也会显示相同字段，因此除非你更喜欢通过环境变量管理配置，否则不需要使用环境变量。

## 故障排除

- **无效的 API 密钥**：确保密钥复制正确，没有多余空格。
- **无结果**：确认网络搜索开关（`+`）已启用且网络连接正常。
- **区域错误**：将 `SERPHOUSE_DOMAIN` 调整为目标区域对应的 Google 域名。

## 更多资源

- [SERPHouse 文档](https://www.serphouse.com/docs)：API 参考和高级选项。
- [Open WebUI 功能](/features)：有关 RAG 和网络搜索的详细信息。
