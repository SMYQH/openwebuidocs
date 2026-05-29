---
title: 更新
sidebar_position: 5
---

# 更新

使用与安装时相同的工具升级，然后重启：

```bash
# pip
pip install --upgrade cptr
# 然后重启 cptr run

# uv（始终运行最新版本）
uvx cptr@latest run
```

对于 Docker，拉取新镜像并使用相同的 `/data` 卷重新创建容器；参见 [Docker](./docker#upgrading)。

## 迁移是自动的

数据库迁移在启动时自动运行。没有手动迁移步骤，也没有迁移命令：启动新版本，它会自动更新数据库。

## 升级后

- 升级后应用内会显示更新说明，总结更改内容。
- 管理 UI 可以检查 GitHub 上的最新发布版本。这仅供信息参考；它从不自行更新应用。
- 如果升级后 UI 看起来过时或损坏，请执行浏览器硬刷新（旧的前端可能被缓存）。
