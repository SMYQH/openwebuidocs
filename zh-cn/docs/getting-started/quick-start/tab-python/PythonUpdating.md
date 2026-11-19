# 使用 Python 更新 {#updating-with-python}

如果你是通过 `pip` 在本地安装的 **Open-WebUI** 包，可按以下方式升级到最新版本：

```bash
pip install -U open-webui
```

`-U`（或 `--upgrade`）标志会让 `pip` 升级到最新可用版本。

升级后，重启服务并确认能够正常启动：

```bash
open-webui serve
```

:::warning 多个工作进程
每个进程启动时都会运行迁移。如果 `UVICORN_WORKERS` 大于 `1`，请先以 `UVICORN_WORKERS=1` 启动新版本，等迁移完成后再重启。不建议运行多个工作进程；需要扩容时，请改用[副本](/getting-started/advanced-topics/scaling#step-3-run-multiple-instances)。
:::

有关版本固定、回滚和备份流程，请参见[完整更新指南](/getting-started/updating)。
