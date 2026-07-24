---
sidebar_position: 3
title: "应用变更"
---

# 应用变更

策略变更在终端新预配时应用。它们不会重写已经正在运行的容器。

这影响镜像变更、环境变量变更、资源变更、存储变更和重置设置。

你不需要为策略镜像或环境变量变更重启编排器。保存策略，然后刷新受影响的用户终端。仅在更改编排器部署本身时才需要重启编排器。

## 刷新终端

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

要刷新一个用户的终端：

```json
{
  "user_id": "user-123",
  "policy_id": "data-science"
}
```

要在刷新时同时清除持久化的终端文件：

```json
{
  "policy_id": "training-lab",
  "only_idle": true,
  "reset": true
}
```
