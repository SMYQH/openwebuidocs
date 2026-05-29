---
title: 数据和备份
sidebar_position: 2
---

# 数据和备份

Computer 需要生存下来的一切都在一个数据目录中：默认为 `~/.cptr`，Docker 中为 `/data`，或者 `CPTR_DATA_DIR` 指向的任何位置。唯一的例外是聊天：它们位于每个工作区文件夹内，随项目一起移动。

## 各数据位置

数据目录内部：

| 路径 | 内容 |
| --- | --- |
| `app.db` | WAL 模式下的 SQLite 数据库（`app.db-wal` 和 `app.db-shm` 与其并列）。用户和认证、实例配置、自动化、聊天/消息记录、上传元数据。 |
| `config.toml` | 服务器密钥加上应用配置的镜像。启动时文件会重新写入数据库（**文件优先**），因此在停止时手动编辑是安全的，配置在数据库丢失后仍然存在。参见 [config.toml](/ecosystem/computer/reference/configuration)。 |
| `uploads/` | 上传的文件数据。 |
| `logs/` | 启用时的审计和上游请求日志。 |
| `memory/` | 每个用户的 AI 记忆。 |
| `skills/` | 管理的全局技能。 |

在每个工作区内部，Computer 保留一个 `.cptr/` 文件夹：

| 路径 | 内容 |
| --- | --- |
| `<workspace>/.cptr/chats/<chat_id>.json` | 该工作区的每个聊天；移动文件夹，聊天也随之移动。 |
| `<workspace>/.cptr/artifacts/` | 在该工作区中产生的制品。 |
| `<workspace>/.cptr/task_logs/` | 任务运行的日志。 |

数据目录备份**不包含**你的工作区。项目文件夹需要自己的备份（git 远程、Time Machine，或你已经在使用的任何方式），因为聊天位于 `<workspace>/.cptr/` 中，所以该备份也涵盖了它们。

## 备份数据目录

:::warning 先停止服务器
`app.db` 使用 SQLite WAL 模式。在服务器写入时复制它可能会产生损坏或不一致的备份。停止 Computer，复制，然后重新启动。
:::

对于 Python 安装，归档 `~/.cptr`：

```bash
tar -C "$HOME" -czf cptr-data-backup.tgz .cptr
```

对于 Docker，将已停止的 `cptr-data` 卷归档到当前目录：

```bash
docker run --rm \
  -v cptr-data:/data:ro \
  -v "$PWD:/backup" \
  alpine tar -C /data -czf /backup/cptr-data-backup.tgz .
```

确认归档包含最重要的两个文件：

```bash
tar -tzf cptr-data-backup.tgz | grep -E '(^|/)app\.db$|(^|/)config\.toml$'
```

## 测试恢复

不要等到灾难发生才发现备份是否有效。解压到一个新目录，并使用 `CPTR_DATA_DIR` 指向它以另一个端口启动第二个实例：

```bash
mkdir -p /tmp/cptr-restore
tar -C /tmp/cptr-restore -xzf cptr-data-backup.tgz
CPTR_DATA_DIR=/tmp/cptr-restore/.cptr cptr run --port 8001
```

在 `http://localhost:8001` 登录并检查你的账户和设置是否正常。

对于 Docker，恢复到**新**卷中，而不是覆盖生产环境：

```bash
docker volume create cptr-data-restore
docker run --rm \
  -v cptr-data-restore:/data \
  -v "$PWD:/backup:ro" \
  alpine tar -C /data -xzf /backup/cptr-data-backup.tgz
```

然后使用 `-v cptr-data-restore:/data` 启动测试容器并登录。记住工作区是单独恢复的：数据备份会恢复账户、配置和设置，而不是项目文件。
