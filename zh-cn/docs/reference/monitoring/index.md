---
sidebar_position: 6
title: "监控"
---

# 监控 {#monitoring}

**在用户发现问题之前就先发现问题。**

Open WebUI 提供健康检查和模型端点，便于接入可用性监控、检查模型连通性并测试端到端响应。无论是单实例还是多节点部署，这些检查都能确认服务是否在线、模型是否可达，以及推理是否正常。

---

## 为什么要监控？ {#why-monitor}

### 快速发现故障 {#catch-outages-quickly}

每 60 秒运行一次健康检查，意味着你可以在一分钟内发现服务中断，而不是等用户来反馈。

### 验证模型连通性 {#verify-model-connectivity}

Open WebUI 可能运行正常，而你的模型提供商却已经离线。监控 `/api/models` 接口就能发现这类情况。

### 验证端到端响应 {#end-to-end-confidence}

深度检查会发送真实提示词并验证响应。检查通过，说明 API、后端、模型提供商和推理组成的整条链路都正常。

---

## 主要功能 {#key-features}

| | |
| :--- | :--- |
| ✅ **健康检查接口** | 无需认证的 `/health` 检查，服务运行时返回 `200` |
| 🔗 **模型连通性** | 带认证的 `/api/models` 检查，用于验证提供商连接 |
| 🤖 **深度健康检查** | 发送真实聊天补全请求并验证响应 |
| 🐻 **Uptime Kuma 配置示例** | 每个监控级别都提供可直接使用的配置 |

---

## 第 1 级：基础健康检查 {#level-1-basic-health-check}

`/health` 接口公开可访问（无需认证），服务运行时返回 `200 OK`。

```bash
curl http://your-open-webui-instance:8080/health
```

这只能验证 Web 服务器是否在响应：`/health` 无条件返回 `{"status": true}`。`GET /health/db` 用于探测数据库，`GET /ready` 在启动完成、数据库以及已配置的 Redis 都能响应之前一直返回 503，因此就绪探针应使用 `/ready`。

### Uptime Kuma 配置（健康检查） {#uptime-kuma-setup}

1. 选择 **添加新监控项**，类型选 **HTTP(s)**
2. **URL：** `http://your-open-webui-instance:8080/health`
3. **间隔：** `60 seconds`
4. **重试次数：** `3`

---

## 第 2 级：模型连通性检查 {#level-2-model-connectivity-check}

`/api/models` 端点**需要认证**，它能确认 Open WebUI 可以访问你的模型提供商并列出可用模型。

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://your-open-webui-instance:8080/api/models
```

<a id="authentication-setup-for-api-key-"></a>

你需要一个 API key。配置说明请参阅 [API 密钥](/features/authentication-access/api-keys)。

:::tip 专用监控账户
创建一个**非管理员用户**（例如 `monitoring-bot`），从该账户生成 API key，并将其用于所有监控请求。这样即使密钥泄露，也能把影响范围降到最低。
:::

### Uptime Kuma 配置（模型连通性） {#uptime-kuma-setup-1}

1. **监控类型：** HTTP(s) - JSON Query
2. **URL：** `http://your-open-webui-instance:8080/api/models`
3. **请求方法：** GET
4. **请求头：** `Authorization: Bearer YOUR_API_KEY`
5. **JSON 查询：** `$count(data[*])>0`
6. **预期值：** `true`
7. **间隔：** `300 seconds`（5 分钟）

### 高级 JSONata 查询 {#advanced-jsonata-queries}

| 目标 | 查询 |
| :--- | :--- |
| 至少存在一个 Ollama 模型 | `$count(data[owned_by='ollama'])>0` |
| 存在指定模型 | `$exists(data[id='gpt-5.6-sol'])` |
| 存在多个模型 | `$count(data[id in ['gpt-5.6-sol', 'gpt-5.6-luna']]) = 2` |

可以在 [jsonata.org](https://try.jsonata.org/) 上使用示例 API 响应测试这些查询。

---

## 第 3 级：深度健康检查 {#level-3-deep-health-check}

发送一条真实的聊天补全请求，以端到端验证整条推理链路。

``` bash
curl -X POST http://your-open-webui-instance:8080/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Respond with the word HEALTHY"}],
    "model": "qwen3.6:27b",
    "temperature": 0
  }'
```

成功响应会返回 `200 OK`，并带有包含 “HEALTHY” 的聊天补全结果。这样可以发现模型加载失败、后端处理错误，以及第 1 级和第 2 级检查无法发现的提供商问题。

:::info
在 Uptime Kuma 中配置第 3 级检查，需要用带有 POST 请求体、认证头和 JSON 查询的 HTTP(s) 监控项来验证响应。有关 POST 监控配置，请参阅 [Uptime Kuma 文档](https://github.com/louislam/uptime-kuma)。
:::

---

## 下一步 {#next-steps}

- **[OpenTelemetry](/reference/monitoring/otel)** - 使用 Grafana、Prometheus、Jaeger 等实现分布式追踪、指标和日志
- **[API 密钥](/features/authentication-access/api-keys)** - 启用和生成用于程序化访问的 API key 完整指南
