---
sidebar_position: 6
title: "定时重置"
---

# 定时重置 {#scheduled-resets}

由编排器管理的终端可以保留持久化文件，即使空闲容器被清理或容器被重建。

- Docker 将文件存储在编排器的 `TERMINALS_DATA_DIR` 下。
- Kubernetes `per-user` 模式为每个用户与策略的组合提供一个 PVC。
- Kubernetes `shared` 和 `shared-rwo` 使用带有每用户子路径的共享 PVC。

如果需要定期清空用户的终端文件，请配置策略生命周期。生命周期配置与策略配置分开：前者定义定期维护，后者定义创建终端时使用的环境。

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

## 重置计划 {#reset-schedules}

支持的调度格式：

| 调度 | 含义 |
| :--- | :--- |
| `2026-07-01T09:00:00Z` | 在确切日期时间的一次性重置 |
| `@weekly` | 每周在配置时区的周日 00:00 重置 |
| `@monthly` | 每月在第一天 00:00 重置 |
| `0 3 * * 1` | 标准的 5 字段 cron 表达式 |

设置 `reset.timezone` 来控制类似 cron 的调度。除非你的重置策略与本地运营时间相关，否则使用 `UTC`。

## 重置何时发生 {#when-reset-happens}

对持久化文件的定时重置不会停止正在运行的终端。

当重置到期时，编排器等待用户的终端不在运行或已被空闲超时回收。然后它删除持久化终端文件存储的内容。

重置不会删除：

- 策略
- Open WebUI 连接
- 用户账户
- 终端镜像

## 刷新时手动重置 {#manual-reset-during-refresh}

你也可以在刷新时重置持久化终端文件：

```json
{
  "policy_id": "training-lab",
  "only_idle": true,
  "reset": true
}
```

在正常操作中保持 `only_idle` 启用，以便用户不会在积极工作时被打断。
