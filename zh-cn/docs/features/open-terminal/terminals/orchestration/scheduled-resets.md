---
sidebar_position: 5
title: "定时重置"
---

# 定时重置

每个编排的终端可以在空闲清理和容器重新创建之间保持持久化文件。

- Docker 将文件存储在编排器的 `TERMINALS_DATA_DIR` 下。
- Kubernetes `per-user` 模式为每个用户/策略提供一个 PVC。
- Kubernetes `shared` 和 `shared-rwo` 使用带有每用户子路径的共享 PVC。

当用户应定期回到一组干净的终端文件时，配置策略生命周期。生命周期配置与策略配置分开，因为它描述的是随时间推移的维护行为，而不是被预配的终端环境。

```bash
curl -X PUT http://terminals-orchestrator:3000/api/v1/policies/training-lab/lifecycle \
  -H "Authorization: Bearer $TERMINALS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "reset": {
      "schedule": "@weekly",
      "timezone": "UTC"
    }
  }'
```

## 重置计划

支持的调度格式：

| 调度 | 含义 |
| :--- | :--- |
| `2026-07-01T09:00:00Z` | 在确切日期时间的一次性重置 |
| `@weekly` | 每周在配置时区的周日 00:00 重置 |
| `@monthly` | 每月在第一天 00:00 重置 |
| `0 3 * * 1` | 标准的 5 字段 cron 表达式 |

设置 `reset.timezone` 来控制类似 cron 的调度。除非你的重置策略与本地运营时间相关，否则使用 `UTC`。

## 重置何时发生

重置是空闲安全的。

当重置到期时，编排器等待用户的终端不在运行或已被空闲超时回收。然后它删除持久化终端文件存储的内容。

重置不会删除：

- 策略
- Open WebUI 连接
- 用户账户
- 终端镜像

## 刷新时手动重置

你也可以在刷新时重置持久化终端文件：

```json
{
  "policy_id": "training-lab",
  "only_idle": true,
  "reset": true
}
```

在正常操作中保持 `only_idle` 启用，以便用户不会在积极工作时被打断。
