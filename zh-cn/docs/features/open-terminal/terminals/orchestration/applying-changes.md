---
sidebar_position: 4
title: "应用变更"
---

# 应用变更 {#applying-changes}

策略变更在终端新预配时应用。它们不会重写已经正在运行的容器。

这影响镜像变更、环境变量变更、资源变更、存储变更和重置设置。

你不需要为策略镜像或环境变量变更重启编排器。保存策略，然后刷新受影响的用户终端。仅在更改编排器部署本身时才需要重启编排器。

## 刷新终端 {#refresh-terminals}

更改策略后，刷新匹配的终端：

```bash
curl -X POST http://terminals-orchestrator:3000/api/v1/terminals/refresh \
  -H "Authorization: Bearer $TERMINALS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "data-science",
    "only_idle": true
  }'
```

`only_idle` 默认为 `true`，因此活跃用户不会被打断。仅当你确实想要立即停止匹配的运行中终端时，才将其设置为 `false`。

要刷新某个用户的终端：

```json
{
  "user_id": "user-123",
  "policy_id": "data-science"
}
```

这会覆盖该用户在同一策略下的所有终端。如果某个连接使用了 [终端上下文](/features/open-terminal/terminals/orchestration/contexts)、因而拥有多个终端，请再加上 `context_id` 以只刷新其中一个：

```json
{
  "user_id": "user-123",
  "policy_id": "data-science",
  "context_id": "chat:0f3c1a2b-7d55-4a19-9c0e-2b8f6d4e1a37"
}
```

共享终端用 `default`，某个聊天的终端用 `chat:<chat-id>`，某个自动化的终端用 `automation:<automation-id>`。

要在刷新时同时清除持久化的终端文件：

```json
{
  "policy_id": "training-lab",
  "only_idle": true,
  "reset": true
}
```
