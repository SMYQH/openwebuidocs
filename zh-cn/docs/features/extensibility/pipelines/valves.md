---
sidebar_position: 4
title: "Valves"
---

## Valves

:::danger Pipelines 已过时——请勿用于新部署
**Pipelines 已过时并被标记为 legacy，不再推荐使用。** Pipeline 可以以 **pipe** 或 **filter** 形式运行；这两种形式现在都有进程内的替代方案——它们也支持 [Valves](/features/extensibility/plugin/development/valves)、内置、且无需额外的 worker 容器：

- Pipeline **pipe**（自定义 provider、RAG、请求路由）→ [Pipe Function](/features/extensibility/plugin/functions/pipe)
- Pipeline **filter**（消息预处理/后处理）→ [Filter Function](/features/extensibility/plugin/functions/filter)

本页面仅供现有部署参考。
:::

`Valves`（参见专用的 [Valves & UserValves](/features/extensibility/plugin/development/valves) 页面）也可以为 `Pipeline` 设置。简而言之，`Valves` 是每个 Pipeline 单独设置的输入变量。

`Valves` 作为 `Pipeline` 类的子类设置，并在 `Pipeline` 类的 `__init__` 方法中初始化。

向 Pipeline 添加 Valve 时，请包含一种确保管理员可以在 Web UI 中重新配置 Valve 的方法。有以下几个选项：

- 使用 `os.getenv()` 为 Pipeline 设置一个环境变量，并提供一个当环境变量未设置时使用的默认值。示例如下：

```python
self.valves = self.Valves(
    **{
        "LLAMAINDEX_OLLAMA_BASE_URL": os.getenv("LLAMAINDEX_OLLAMA_BASE_URL", "http://localhost:11434"),
        "LLAMAINDEX_MODEL_NAME": os.getenv("LLAMAINDEX_MODEL_NAME", "llama3"),
        "LLAMAINDEX_EMBEDDING_MODEL_NAME": os.getenv("LLAMAINDEX_EMBEDDING_MODEL_NAME", "nomic-embed-text"),
    }
)
```

- 将 Valve 设置为 `Optional` 类型，即使未为 Valve 设置值，也允许 Pipeline 加载。

```python
class Pipeline:
    class Valves(BaseModel):
        target_user_roles: List[str] = ["user"]
        max_turns: Optional[int] = None
```

如果你不提供在 Web UI 中更新 Valve 的方法，在尝试将 Pipeline 添加到 Web UI 后，你会在 Pipelines 服务器日志中看到以下错误：
`WARNING:root:No Pipeline class found in <pipeline name>`
