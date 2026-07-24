---
sidebar_position: 900
title: "数据库迁移"
sidebar_label: 手动迁移
description: 当 Open WebUI 自动迁移失败或需要人工介入时，手动运行 Alembic 数据库迁移的完整指南。
keywords: [alembic, migration, database, troubleshooting, sqlite, postgresql, docker]
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 概览

Open WebUI 会在启动时自动执行数据库迁移。**绝大多数情况下都不需要手动迁移**，只有在特定的失败场景或维护情形下才应进行手动迁移。

:::info 什么时候需要手动迁移
仅在以下场景中需要手动迁移：

- Open WebUI 在启动日志中明确报出迁移错误
- 你正在执行离线数据库维护
- 版本升级后自动迁移失败
- 你要在不同数据库类型之间迁移（SQLite ↔ PostgreSQL）
- 开发者明确指示你手动运行迁移
:::

:::tip 快速判断：升级后的迁移错误
**"No such table"** —— 迁移没有真正应用。进入容器，设置所需环境变量（见[第 2 步](#step-2-diagnose-current-state)），然后运行 `alembic upgrade head`。详情见 [No such table 错误](#no-such-table-errors)。

**"Table already exists"** —— 某次迁移只完成了一部分。你需要先为这次已部分应用的迁移做 stamp，再继续 upgrade。详情见 [Table already exists 错误](#table-already-exists-errors)。

**跨大版本升级后接连出现多种错误**（例如先 "duplicate column"，再 "table already exists"，然后 "no such column"）—— 说明数据库跨多个迁移处于部分迁移状态。需要按迁移链逐个处理。详见[跨大版本升级后的连续失败](#multiple-failures-after-a-major-version-jump)。
:::

:::danger 关键警告
手动迁移操作失误会直接损坏数据库。**开始前务必创建并验证备份。**
:::

## 前置检查清单

在开始之前，请确认：

- [ ] 你拥有 Open WebUI 安装环境的 **root/admin 权限**
- [ ] **已确认数据库位置**（Docker 默认是 `/app/backend/data/webui.db`）
- [ ] **Open WebUI 已完全停止**（没有任何运行中的进程）
- [ ] **备份已创建并验证**（见下文）
- [ ] 你可以**进入容器**或运行 Open WebUI 的 **Python 环境**

:::warning 先停止所有进程
数据库迁移不能在 Open WebUI 仍然运行时执行。手动迁移前，**必须**先停止所有 Open WebUI 进程。
:::

## 第 1 步：创建并验证备份

### 备份数据库

<Tabs groupId="database-type">
  <TabItem value="sqlite" label="SQLite（默认）" default>
    ```bash title="终端"
    # 先确认数据库位置
    docker inspect open-webui | grep -A 5 Mounts

    # 创建带时间戳的备份
    cp /path/to/webui.db /path/to/webui.db.backup.$(date +%Y%m%d_%H%M%S)
    ```
  </TabItem>
  <TabItem value="postgresql" label="PostgreSQL">
    ```bash title="终端"
    pg_dump -h localhost -U your_user -d open_webui_db > backup_$(date +%Y%m%d_%H%M%S).sql
    ```
  </TabItem>
</Tabs>

### 验证备份完整性

**关键：** 在继续之前，请先确认备份文件真的可读。

<Tabs groupId="database-type">
  <TabItem value="sqlite" label="SQLite" default>
    ```bash title="终端 - 验证备份"
    # 测试备份能否打开
    sqlite3 /path/to/webui.db.backup "SELECT count(*) FROM user;"

    # 验证 schema 一致
    sqlite3 /path/to/webui.db ".schema" > current-schema.sql
    sqlite3 /path/to/webui.db.backup ".schema" > backup-schema.sql
    diff current-schema.sql backup-schema.sql
    ```
  </TabItem>
  <TabItem value="postgresql" label="PostgreSQL">
    ```bash title="终端 - 验证备份"
    # 确认备份文件非空且包含 SQL
    head -n 20 backup_*.sql
    grep -c "CREATE TABLE" backup_*.sql
    ```
  </TabItem>
</Tabs>

:::tip 备份存放位置
请把备份保存在**与数据库本体不同的磁盘或卷**上，以防磁盘故障同时丢失原库和备份。
:::

## 第 2 步：诊断当前状态 {#step-2-diagnose-current-state}

在尝试修复前，先收集数据库当前状态的信息。

### 进入运行环境

<Tabs groupId="install-type">
  <TabItem value="docker" label="Docker" default>
    ```bash title="终端"
    # 先停止 Open WebUI
    docker stop open-webui

    # 进入容器执行诊断
    docker run --rm -it \
      -v open-webui:/app/backend/data \
      --entrypoint /bin/bash \
      ghcr.io/open-webui/open-webui:main
    ```

    :::note 确认当前位置
    进入容器后先确认当前所在路径：
    ```bash
    pwd
    ```
    Alembic 配置文件位于 `/app/backend/open_webui/alembic.ini`。无论你当前在哪个目录，最终都需要切换到这里。
    :::
  </TabItem>
  <TabItem value="local" label="本地安装">
    ```bash title="终端"
    # 进入 Open WebUI 安装目录
    cd /path/to/open-webui/backend/open_webui

    # 如使用虚拟环境则激活
    source ../../venv/bin/activate  # Linux/Mac
    # venv\Scripts\activate  # Windows
    ```
  </TabItem>
</Tabs>

### 切换到 Alembic 目录并设置环境

进入包含 `alembic.ini` 的目录并配置所需环境变量：

```bash title="终端 - 切换目录并配置环境"
# 先确认当前所在目录
pwd

# 切换到 Alembic 目录（若 pwd 不同请相应调整路径）
cd /app/backend/open_webui  # Docker
# 或
cd /path/to/open-webui/backend/open_webui  # 本地

# 验证当前目录存在 alembic.ini
ls -la alembic.ini
```

### 设置必需环境变量

<Tabs groupId="install-type">
  <TabItem value="docker" label="Docker" default>

```bash title="终端 - 设置环境变量（Docker）"
# 必需：Database URL
# SQLite（绝对路径需 4 个斜杠）
export DATABASE_URL="sqlite:////app/backend/data/webui.db"

# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/open_webui_db"

# 必需：WEBUI_SECRET_KEY
# 从 backend 目录下的现有文件读取（注意不是 data 目录）
export WEBUI_SECRET_KEY=$(cat /app/backend/.webui_secret_key)

# 若上面失败，可尝试 data 目录位置
# export WEBUI_SECRET_KEY=$(cat /app/backend/data/.webui_secret_key)

# 若两处都没有，可手动生成
# export WEBUI_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
# echo $WEBUI_SECRET_KEY > /app/backend/.webui_secret_key

# 验证两个变量都已设置
echo "DATABASE_URL: $DATABASE_URL"
echo "WEBUI_SECRET_KEY: ${WEBUI_SECRET_KEY:0:10}..."
```

  </TabItem>
  <TabItem value="local" label="本地安装">

```bash title="终端 - 设置环境变量（本地）"
# 必需：Database URL
# SQLite（从 backend/open_webui 目录出发的相对路径）
export DATABASE_URL="sqlite:///../data/webui.db"

# 绝对路径写法
export DATABASE_URL="sqlite:////full/path/to/webui.db"

# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/open_webui_db"

# 必需：WEBUI_SECRET_KEY
# 若使用 .env 文件，Alembic 可能不会自动加载——必须手动 export
export WEBUI_SECRET_KEY=$(cat ../data/.webui_secret_key)

# 或者你已经在环境里有了
# export WEBUI_SECRET_KEY="your-existing-key"

# 验证两个变量都已设置
echo "DATABASE_URL: $DATABASE_URL"
echo "WEBUI_SECRET_KEY: ${WEBUI_SECRET_KEY:0:10}..."
```

:::note 本地安装的环境
本地安装常将 `DATABASE_URL` 写在 `.env` 文件中，但 Alembic 的 `env.py` 可能不会自动加载 `.env`。运行 Alembic 命令前，请先在 shell 中显式 export 这些变量。
:::

  </TabItem>
</Tabs>

:::danger 两个变量都必须设置
如果缺少 `WEBUI_SECRET_KEY`，Alembic 命令会直接因 `Required environment variable not found` 失败。Open WebUI 的代码 import 了 `env.py`，会先校验该变量是否存在，Alembic 甚至还没来得及连上数据库就会退出。
:::

:::warning SQLite 路径语法

- `sqlite:////app/...` = 共 4 个斜杠（绝对路径：`sqlite://` + `/` + `/app/...`）
- `sqlite:///../data/...` = 共 3 个斜杠（相对路径）
:::

### 运行诊断命令

执行以下只读诊断命令：

```bash title="终端 - 诊断（安全，只读）"
# 查看当前迁移版本
alembic current -v

# 查看目标（最新）版本
alembic heads

# 列出所有迁移历史
alembic history

# 预览将要执行的迁移（不会真正应用）
alembic upgrade head --sql | head -30

# 检查是否有分支（出现分支意味着有问题）
alembic branches
```

**预期输出：**

```
# alembic current 通常会显示类似：
ae1027a6acf (head)

# 如果看到多个 head 或分支，说明迁移历史有问题
```

:::info 输出含义

- `alembic current` = 数据库当前认为自己处在哪个版本
- `alembic heads` = 代码期望的最新版本
- `alembic upgrade head --sql` = 预览将要执行的 SQL（不会真正应用）
- 如果 `current` 早于 `heads`，说明还有待执行的迁移
- 如果 `current` 等于 `heads`，说明数据库已是最新
:::

<details>
<summary>检查数据库中实际存在的表</summary>

确认数据库里实际有哪些表：

<Tabs groupId="database-type">
  <TabItem value="sqlite" label="SQLite" default>
    ```bash title="终端"
    sqlite3 /app/backend/data/webui.db ".tables"
    sqlite3 /app/backend/data/webui.db "SELECT * FROM alembic_version;"
    ```
  </TabItem>
  <TabItem value="postgresql" label="PostgreSQL">
    ```bash title="终端"
    psql -h localhost -U user -d dbname -c "\dt"
    psql -h localhost -U user -d dbname -c "SELECT * FROM alembic_version;"
    ```
  </TabItem>
</Tabs>

</details>

## 第 3 步：应用迁移

### 标准升级（最常见）

若诊断结果表明存在待执行的迁移（`current` < `heads`），直接升级到最新：

```bash title="终端 - 升级到最新"
# 确认所在目录正确
cd /app/backend/open_webui

# 执行升级
alembic upgrade head
```

**注意这些输出：**

```bash
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
# highlight-next-line
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, add_new_column
```

:::note "Will assume non-transactional DDL"
对 SQLite 而言，这是一条**正常的提示信息**，不是错误。SQLite 不支持 schema 变更的回滚，因此迁移只能在没有事务保护的情况下执行。

如果这条消息后进程似乎"卡住"，请等 2-3 分钟——某些迁移本就需要时间，尤其是：
- 在大表上加索引（百万级行：1-5 分钟）
- 涉及数据转换的迁移（十万级行：30 秒到数分钟）
- 需要重建表的迁移（SQLite 不支持部分 ALTER 操作）

对于超大数据库（千万级以上），建议安排维护窗口，并在另一个终端用 `sqlite3 /path/to/webui.db ".tables"` 监控进度。
:::

### 升级到指定版本

如果你只想应用到某个特定版本：

```bash title="终端 - 升级到指定版本"
# 先列出所有可用版本
alembic history

# 升级到指定 revision
alembic upgrade ae1027a6acf
```

### 回滚（Downgrade）

:::danger 有数据丢失风险
回滚可能会**永久性丢失数据**，特别是迁移本身删除过列或表的情况。只有在你完全理解后果时才执行。
:::

```bash title="终端 - 回滚迁移"
# 回滚一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>

# 终极手段：清空所有迁移（极少需要）
alembic downgrade base
```

## 第 4 步：验证迁移结果

迁移完成后，请确认一切正常：

```bash title="终端 - 迁移后验证"
# 验证当前版本符合预期
alembic current
# 应显示 (head)，表示已在最新版本
# 例如：ae1027a6acf (head)

# 确认没有遗留的待执行迁移
alembic upgrade head --sql | head -20
# 输出若只剩注释或为空，表示已是最新

# 验证关键表存在（SQLite）
sqlite3 /app/backend/data/webui.db ".tables" | grep -E "user|chat|model"
# 应能看到 user、chat、model 等表

# 用一次简单查询确认 schema 完整
sqlite3 /app/backend/data/webui.db "SELECT COUNT(*) FROM user;"
# 应返回一个数字，而不是报错
```

### 测试应用启动

<Tabs groupId="install-type">
  <TabItem value="docker" label="Docker" default>
    ```bash title="终端"
    # 退出诊断容器
    exit

    # 正常启动 Open WebUI
    docker start open-webui

    # 跟踪日志确认迁移
    docker logs -f open-webui

    # 看到成功启动后，在浏览器测试
    # 访问 http://localhost:8080 验证登录页能正常加载
    ```
  </TabItem>
  <TabItem value="local" label="本地安装">
    ```bash title="终端"
    # 启动 Open WebUI
    python -m open_webui.main

    # 观察启动是否成功
    # 然后访问 http://localhost:8080 测试
    ```
  </TabItem>
</Tabs>

**成功启动时的日志示例：**

```
INFO:     [db] Database initialization complete
INFO:     [main] Open WebUI starting on http://0.0.0.0:8080
```

**启动后建议做 smoke test：**
- 能打开登录页
- 能用原账号正常登录
- 能查看聊天历史
- 浏览器控制台没有新的 JavaScript 错误

## 故障排查

### "No such table" 错误 {#no-such-table-errors}

**症状：** Open WebUI 启动时崩溃并报类似错误：

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: access_grant
```

也可能出现在其他缺失的表上（例如 `message`、`channel`）。

**原因：** 一个或多个 Alembic 迁移没有成功应用。常见原因包括：

- 自动升级过程中某次迁移静默失败（Open WebUI 记录错误后继续启动）
- 升级过程被中途打断
- 环境变量中设置了 `ENABLE_DB_MIGRATIONS=False`（关闭启动时的自动迁移）
- 多个 worker 或副本同时尝试运行迁移

:::warning `ENABLE_DB_MIGRATIONS` 不能修复这种问题
设置 `ENABLE_DB_MIGRATIONS=True`（默认值）只表示告诉 Open WebUI 在下次启动时**尝试**自动迁移。它**不会**追溯修复之前已经失败或被跳过的迁移。一旦数据库进入坏状态，必须手动应用迁移。
:::

**解决方法：**

按[第 2 步](#step-2-diagnose-current-state)进入环境，然后运行：

```bash title="终端"
cd /app/backend/open_webui  # Docker
alembic upgrade head
```

这会应用所有待执行的迁移，包括创建缺失的表。成功后正常重启 Open WebUI 即可。

如果手动迁移过程中又遇到新错误（例如 ["table already exists"](#table-already-exists-errors)），请到对应章节查找相应错误信息的处理方式。

### "Table Already Exists" 错误 {#table-already-exists-errors}

**症状：** 运行 `alembic upgrade head` 时报错：

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) table chat_message already exists
```

或者其他表（例如 `access_grant`）的同类错误。

**原因：** 某次迁移**只完成了一部分**——表已经在数据库里创建出来，但 Alembic 的版本记录没有更新（通常是因为迁移在表创建之后的数据回填阶段被打断）。Alembic 依然认为该迁移没有应用，因此下次又尝试重新创建同一张表。

:::tip v0.9.6 起迁移是幂等的
v0.9.6 重做了内置的 Alembic 迁移，使其在运行时探查实际 schema，并**跳过已经存在的表、索引和列**（同时为遗留的 peewee 时代表补上缺失的主键）。许多过去会触发本错误的“半应用 schema”升级场景，现在直接 `alembic upgrade head` 就能顺利完成。如果你在旧版本上遇到 “table already exists”，先升级到 v0.9.6+ 再做手动处理通常是最简单的修法。下方的手动恢复步骤，对于被以其他方式改动的数据库仍然有效。
:::

**诊断：**

```bash title="终端 - 找出卡住的迁移"
# 查看 Alembic 认为当前在哪个 revision
alembic current
# 输出示例：374d2f66af06 (head)

# 查看下一个待执行的迁移
alembic history
# 找到紧跟在当前版本之后的那个迁移
# 例如：374d2f66af06 -> 8452d01d26d7, Add chat_message table
```

**解决方法：**

有三种方式可选，按"从安全到有损"的顺序列出：

#### 方案 1：从备份恢复（推荐）

从你在[第 1 步](#step-1-create-and-verify-backup)创建的备份恢复数据库，然后在恢复后的干净数据库上重新执行 `alembic upgrade head`。这能确保整个迁移——包括所有数据回填——完整执行。

#### 方案 2：删表后重跑

如果你没有备份，可以删掉部分创建的表，让迁移从头执行。**这样做之前必须先确认安全性：**

```bash title="终端 - 删表前的检查"
# 1. 确认该迁移确实没有完成（current revision 应早于失败的那一个）
alembic current

# 2. 查看这张表里有多少数据（如果有）
# SQLite：
sqlite3 /app/backend/data/webui.db "SELECT COUNT(*) FROM <table_name>;"
# PostgreSQL：
psql $DATABASE_URL -c "SELECT COUNT(*) FROM <table_name>;"

# 3. 打开迁移文件，确认源数据还在
#    按 revision ID 找到对应文件：
ls migrations/versions/ | grep <revision_id>
#    打开它，看它从哪些源列/源表 COPY 数据
#    然后确认那些源列在你的数据库里仍然存在
```

确认迁移确实没完成、且源数据完好后，删表并重跑：

```bash title="终端 - 删表并重跑"
# SQLite：
sqlite3 /app/backend/data/webui.db "DROP TABLE <table_name>;"

# PostgreSQL：
psql $DATABASE_URL -c "DROP TABLE <table_name>;"

# 重新运行迁移
alembic upgrade head
```

:::caution 先看清楚迁移文件
只有当迁移**从旧列复制**数据到新表（原始数据没被改动）时，这种方式才安全。打开迁移文件，确认它使用的是 `INSERT INTO ... SELECT FROM` 这类操作，而**不是**会修改或删除源数据的破坏性操作。不确定就用方案 1。
:::

#### 方案 3：Stamp 跳过（最后手段）

如果上面两种方案都不可行，可以让 Alembic 直接跳过这条卡住的迁移：

```bash title="终端"
# 把该迁移标记为已应用，但不真正执行
alembic stamp <revision_id>

# 继续执行剩下的迁移
alembic upgrade head
```

:::warning 这样做会跳过数据回填
Stamp 只是把迁移标记为已完成，会跳过剩下的步骤（例如把历史数据拷贝到新表）。你的旧数据**不会被删除**——它仍然在原列里——但应用可能不再从那些旧列读取了。某些功能可能表现为"历史数据出现缺口"，另一些则可能直接丢失设置。
:::

如果 `alembic upgrade head` 又对另一个迁移报出 "table already exists"，对每条卡住的迁移重复这套操作。

:::tip 多条迁移都卡住？
如果你每次重试看到的错误都不同——"duplicate column"、然后 "table already exists"、然后 "no such column"——说明你的数据库在多个步骤上都处于部分迁移状态。这通常出现在跨大版本升级之后（例如 0.7.x → 0.8.x）。完整恢复流程见[跨大版本升级后的连续失败](#multiple-failures-after-a-major-version-jump)。
:::

### 跨大版本升级后的连续失败 {#multiple-failures-after-a-major-version-jump}

**症状：** 跨多个版本升级后（例如 0.7.x → 0.8.x），Open WebUI 启动时崩溃并报 "no such column" 错误（例如 `no such column: user.scim`）。运行 `alembic upgrade head` 又会在**更早的**某个迁移上报 "duplicate column" 或 "already exists"。修好一个后又会在**下一个**迁移上失败，如此循环。

**原因：** Open WebUI 在大版本跳跃后启动时，会依次尝试执行所有待执行的迁移。如果其中任意一条迁移中途失败（常见原因：SQLite `NOT NULL` 约束没有默认值、进程被打断、大数据量回填遭遇内存限制），部分 schema 变更会留下——因为 SQLite 迁移是非事务性的——但 `alembic_version` 不会前进。之后每次启动都会重试同一条失败迁移，又在已经应用的部分上崩溃，永远到不了后续迁移。结果就是数据库 schema 变成"补丁拼接"：早期迁移做了一些，后面的什么都没做。

**诊断：**

```bash title="终端 - 确认部分迁移链状态"
# 查看 Alembic 认为当前所在 revision
alembic current
# 例如：37f288994c47  （落后 head 好几个版本）

# 查看 head
alembic heads
# 例如：b2c3d4e5f6a7  (head)

# 列出 current 到 head 之间的完整迁移链
alembic history

# 检查是否存在"理论上当前 revision 不应有"的 schema 元素
# （这些是更晚迁移已部分应用的证据）
sqlite3 /app/backend/data/webui.db "PRAGMA table_info(channel_member);" | grep status
sqlite3 /app/backend/data/webui.db "SELECT name FROM sqlite_master WHERE type='table' AND name='chat_message';"
```

如果 `alembic current` 显示的是早期 revision，但你能在数据库里看到属于后续迁移的表/列，说明你处于"部分迁移链"状态。

**解决方法 —— 一次只升级一个迁移：**

思路：逐个 revision 升级。成功就继续；失败时若错误是 "duplicate column" 或 "already exists"，就 stamp 跳过；若是其他错误，立刻停下来排查。

```bash title="终端 - 分步恢复"
# 拿到按顺序排列的待执行迁移列表
alembic history

# 尝试第一个待执行的迁移
alembic upgrade <first_pending_revision>
```

如果成功：

```bash
# 继续下一个
alembic upgrade <next_revision>
```

如果失败并提示 "duplicate column name" 或 "already exists"：

```bash
# 说明该迁移的 schema 变更其实在之前的某次部分运行中已经应用过。
# 对该 revision 执行 stamp 推进 alembic_version，而不重跑 SQL。
alembic stamp <that_revision>

# 继续下一个迁移
alembic upgrade <next_revision>
```

重复直到达到 head。

:::info 这里的 stamp 什么时候是安全的？
当你已经确认该迁移的 schema 变更**确实存在于数据库中**——而 "already exists" 或 "duplicate column" 错误本身就证明了这一点——此时 stamp 才安全。这与盲目执行 `alembic stamp head` 完全不同，后者会跳过**所有**待执行迁移，无论它们是否真的应用过。
:::

**特殊情况 —— 带数据回填的迁移：**

某些迁移不仅修改 schema，还会把数据从旧表复制到新表（例如 `chat_message` 迁移会从 `chat` 表的 JSON 列做回填）。如果这类迁移的*建表*成功了，但*回填*被打断：

```bash title="终端 - 检查回填是否完成"
# 看新表里有没有数据
sqlite3 /app/backend/data/webui.db "SELECT COUNT(*) FROM <table_name>;"
```

如果行数大于 0，回填很可能已经完成——stamp 跳过即可。如果行数为 0，你有两个选择：

1. **删表后重跑**（不丢数据，但大库回填可能很慢）：
   ```bash
   sqlite3 /app/backend/data/webui.db "DROP TABLE <table_name>;"
   alembic upgrade <that_revision>
   ```

2. **Stamp 跳过**（快，但跳过回填——依赖该新表的功能可能出现历史数据缺口）：
   ```bash
   alembic stamp <that_revision>
   ```

**验证与启动：**

```bash title="终端 - 验证恢复结果"
alembic current
# 应显示：<latest_revision> (head)
```

然后退出容器并正常启动：

```bash
exit
docker start open-webui
docker logs -f open-webui
```

:::warning 出现非预期错误时立即停止
"stamp 后继续"这套策略只适用于 "already exists" 和 "duplicate column" 错误——这类错误本身就证实了对应 schema 变更已经在数据库中。如果某次迁移失败并报出*其他类型*的错误（数据类型不匹配、外键违规、与 schema 冲突无关的 Python traceback），**不要** stamp 跳过。请到 GitHub Issue 上贴出完整错误。
:::

### "Required environment variable not found"

**原因：** 缺少 `WEBUI_SECRET_KEY` 环境变量。

**解决方法：** 按[第 2 步：设置必需环境变量](#set-required-environment-variables)设置 `WEBUI_SECRET_KEY`，然后重试 Alembic 命令。

:::warning 为什么会出现这个错误
Open WebUI 的 `env.py` 在加载时会引入 models，model 又会导入 `open_webui.env`，后者会校验 `WEBUI_SECRET_KEY` 是否存在。缺少该变量时，Python 会在 Alembic 连接数据库之前就崩溃。
:::

### "No config file 'alembic.ini' found"

**原因：** 当前目录不对。

**解决方法：**

```bash title="终端"
# 如果容器名不是 'open-webui'，先查出来
docker ps

# 找到 alembic.ini 的位置
find /app -name "alembic.ini" 2>/dev/null  # Docker
find . -name "alembic.ini"  # 本地

# 切换到该目录
cd /app/backend/open_webui  # 最常见的路径

# 确认目录正确
ls -la alembic.ini
```

### "Target database is not up to date"

**原因：** 数据库版本与代码期望的 schema 不一致。

**诊断：**

```bash title="终端 - 诊断版本不一致"
# 数据库认为自己的版本是
alembic current

# 代码期望的版本是
alembic heads

# 对比两者
```

**根据诊断结果选择方案：**

<Tabs>
  <TabItem value="pending" label="有待执行迁移" default>
    **场景：** `alembic current` 显示的版本早于 `alembic heads`

    **修复：** 直接应用待执行的迁移即可。

    ```bash title="终端"
    alembic upgrade head
    ```
  </TabItem>
  <TabItem value="mismatch" label="Schema 不一致">
    **场景：** `alembic current` 显示版本已正确，但仍然报错

    **原因：** 有人未经迁移手动改了数据库 schema，或某次迁移半途失败。

    **修复：** 从备份恢复——这属于数据库损坏。

    ```bash title="终端"
    # 停止一切
    docker stop open-webui

    # 恢复备份
    cp /path/to/webui.db.backup /path/to/webui.db

    # 重试迁移
    alembic upgrade head
    ```
  </TabItem>
  <TabItem value="fresh" label="全新数据库">
    **场景：** 需要为新建数据库初始化 schema

    **修复：** 从头运行迁移。

    ```bash title="终端"
    alembic upgrade head
    ```
  </TabItem>
</Tabs>

:::danger 永远不要把 "alembic stamp head" 当成修复手段
你可能在网络上看到有人建议用 `alembic stamp head` 来"修复"版本不一致。**这非常危险。**

`alembic stamp head` 是告诉 Alembic"假装*所有*迁移都执行过了"——但其实一条都没真正运行。这会造成永久性数据库损坏：Alembic 以为 schema 已是最新，而实际上并不是。

**`alembic stamp <specific_revision>` 只有在以下情况下才是安全的：**

- 你已经确认该迁移的 schema 变更确实存在于数据库中（例如 "already exists" 或 "duplicate column" 错误本身就证明了）—— 见[跨大版本升级后的连续失败](#multiple-failures-after-a-major-version-jump)
- 你用 `create_all()` 手动建好了所有表，需要把它们标记为已迁移
- 你是开发者，正在为一个与当前 schema 完全匹配的全新数据库做初始化
- 你从其他系统导入了数据库备份，需要把它标记到正确的 revision
- 你已经用裸 SQL 手动应用了迁移，需要更新版本记录

**永远不要用 `alembic stamp head` 一次性跳过所有待执行迁移。**
:::

### 看到 "Will assume non-transactional DDL" 之后像是卡住了

**理解这条消息：** 它**不是错误**，只是提示信息。SQLite 不支持事务性 DDL，所以 Alembic 提醒你迁移无法自动回滚。

**如果确实卡住了：**

<Tabs>
  <TabItem value="wait" label="先等一会" default>
    某些迁移（尤其是加索引或修改大表的）确实要几分钟。

    **操作：** 在判定为"卡死"之前先等 3-5 分钟。
  </TabItem>
  <TabItem value="lock" label="检查数据库锁">
    可能有其他进程把数据库锁住了。

    ```bash title="终端 - 检查锁"
    # 查找在用该数据库文件的进程
    fuser /app/backend/data/webui.db

    # 杀掉残留的进程
    pkill -f "open-webui"

    # 确认已经没有相关进程
    ps aux | grep open-webui

    # 重试迁移
    alembic upgrade head
    ```
  </TabItem>
  <TabItem value="corrupt" label="数据库损坏">
    如果数据库本身已损坏，迁移会一直卡住。

    ```bash title="终端 - 完整性检查"
    sqlite3 /app/backend/data/webui.db "PRAGMA integrity_check;"
    ```

    如果完整性检查不通过，从备份恢复。
  </TabItem>
</Tabs>

### Autogenerate 检测到要删除的表

**症状：** 你跑了 `alembic revision --autogenerate`，它建议删除一些已存在的表。

:::warning 不要执行 autogenerate
**普通用户绝对不要执行 `alembic revision --autogenerate`。** 这条命令是给**开发者生成新迁移文件**用的，不是给应用现有迁移用的。

你真正需要的是 `alembic upgrade head`（没有 `revision`，也没有 `--autogenerate`）。
:::

**如果你不小心生成了错误的迁移文件：**

```bash title="终端 - 删除错误的迁移"
# 列出迁移文件
ls -la /app/backend/open_webui/migrations/versions/

# 删除最新生成的错误文件
rm /app/backend/open_webui/migrations/versions/<newest_timestamp>_*.py

# 恢复到已知正确状态
git checkout /app/backend/open_webui/migrations/  # 如使用 git
```

**技术背景：** "autogenerate 检测到要删除的表"这个问题，本质是因为 Open WebUI 的 Alembic metadata 配置没有导入所有 model 定义。autogenerate 在不完整的 metadata 上做对比，所以认为某些表应该被删除。这是开发者层面的问题，不会影响普通用户运行 `alembic upgrade`。

### PostgreSQL 外键错误

:::info 仅适用于 PostgreSQL
本节仅适用于 PostgreSQL。SQLite 处理外键的方式不同。
:::

**症状：** 出现类似 `psycopg2.errors.InvalidForeignKey: there is no unique constraint matching given keys for referenced table "user"` 的错误。

**原因：** PostgreSQL 要求显式声明的主键约束，而旧版 schema 可能没有。

**PostgreSQL 解决方法：**

```sql title="PostgreSQL 修复"
-- 连接到 PostgreSQL 数据库
psql -h localhost -U your_user -d open_webui_db

-- 补上缺失的主键约束（PostgreSQL 语法）
ALTER TABLE public."user" ADD CONSTRAINT user_pk PRIMARY KEY (id);

-- 验证约束已添加
\d+ public."user"
```

**说明：** `public.` 这个 schema 前缀和加引号的 `"user"` 标识符是 PostgreSQL 特有的。这段 SQL 在 SQLite 或 MySQL 上无法使用。

### Duplicate column 错误

:::danger 关键问题
Duplicate column 错误意味着 schema 已经损坏，通常是某次迁移失败或手工改库导致的。这种情况需要小心处理。
:::

**症状：** 迁移失败并报类似错误：

```
sqlite3.OperationalError: duplicate column name: message.reply_to_id
```

或者 Open WebUI 启动时报：

```
UNIQUE constraint failed: alembic_version.version_num
```

**原因：**

<ul>
  <li>之前某次迁移只完成了一部分，留下了重复列</li>
  <li>数据库被手工改过</li>
  <li>迁移在执行中途被打断</li>
  <li>跨多个大版本升级（跳过了中间迁移）</li>
</ul>

**诊断：**

```bash title="终端 - 查找重复列"
# 列出 message 表的所有列
sqlite3 /app/backend/data/webui.db "PRAGMA table_info(message);"

# 在输出中查找名称重复的列
# 问题示例：
# 10|reply_to_id|TEXT|0||0
# 15|reply_to_id|TEXT|0||0  <- 重复！
```

**解决方法 —— 手动移除列：**

:::warning 有数据丢失风险
移除列可能造成数据丢失。**操作前务必先备份数据库。**
:::

```bash title="终端 - 移除重复列（SQLite）"
# 1. 先备份数据库！
cp /app/backend/data/webui.db /app/backend/data/webui.db.pre-fix

# 2. 进入 SQLite
sqlite3 /app/backend/data/webui.db

# 3. 查看当前表结构
PRAGMA table_info(message);

# 4. SQLite 不支持直接 DROP COLUMN——必须重建表
# 先拿到 CREATE TABLE 语句
.schema message

# 5. 新建一张没有重复列的表
-- 拷贝原 CREATE TABLE 语句，但去掉重复列定义
-- 示例（请按实际 schema 调整）：
CREATE TABLE message_new (
    id TEXT PRIMARY KEY,
    content TEXT,
    role TEXT,
    -- ... 其他列 ...
    reply_to_id TEXT,  -- 只保留一份
    -- ... 剩余列 ...
    FOREIGN KEY (reply_to_id) REFERENCES message(id)
);

# 6. 把数据从旧表复制到新表
INSERT INTO message_new SELECT * FROM message;

# 7. 删掉旧表
DROP TABLE message;

# 8. 把新表改名为原表名
ALTER TABLE message_new RENAME TO message;

# 9. 退出 SQLite
.quit

# 10. 验证修复结果
sqlite3 /app/backend/data/webui.db "PRAGMA table_info(message);"

# 11. 重新尝试迁移
cd /app/backend/open_webui
alembic upgrade head
```

**备选 —— 已确定哪一列是重复时的简化做法：**

```bash title="终端 - 已知重复列的快速修复"
# 仅当该列确实完全重复、且 SQLite 的表重建能正确处理时可用

sqlite3 /app/backend/data/webui.db <<EOF
-- 用正确 schema 建临时表
CREATE TABLE message_temp AS SELECT DISTINCT * FROM message;

-- 删除原表
DROP TABLE message;

-- 用正确 schema 重新创建（先从原始 .schema message 取得定义）
-- 然后把数据复制回去
EOF
```

:::danger 什么时候应该求助
如果你对 SQL 不熟悉，或者不能确定哪一列是重复的，**到这里就停下，去寻求帮助**——Open WebUI GitHub Issue。求助时请附带：
- `PRAGMA table_info(message);` 的输出
- 完整的迁移错误信息
- 你的 Open WebUI 版本升级路径（从哪个版本升到哪个版本）
:::

**预防：**

<ul>
  <li>升级时不要跳过大版本（不要从 v0.1.x 直接跳到 v0.4.x）</li>
  <li>升级前一定先备份</li>
  <li>先在数据库副本上测试升级</li>
  <li>仔细阅读你的版本升级路径上涉及的迁移脚本</li>
</ul>

### Peewee 到 Alembic 的过渡问题

**背景：** 老版本 Open WebUI（0.4.x 之前）使用 Peewee 迁移，新版本使用 Alembic。

**症状：**

- 同时存在 `migratehistory` 与 `alembic_version` 两张表
- 报 "migration already applied" 之类错误

**自动过渡过程：**

1. Open WebUI 的 `internal/db.py` 先通过 `handle_peewee_migration()` 跑旧 Peewee 迁移
2. 然后 `config.py` 通过 `run_migrations()` 跑 Alembic 迁移
3. 这两个系统理论上应该是透明衔接的

**如果自动过渡失败：**

```bash title="终端 - 手动过渡"
# 检查是否还有旧 Peewee 迁移记录
sqlite3 /app/backend/data/webui.db "SELECT * FROM migratehistory;" 2>/dev/null

# 如果 Peewee 迁移存在，先确保它们都完成了
# 然后再跑 Alembic 迁移
cd /app/backend/open_webui
alembic upgrade head
```

:::tip
从非常老的版本升级（< 0.3.x）时，更推荐**重新安装 + 数据导出/导入**，而不是硬跨多个大版本做 schema 迁移。
:::

## 高级操作

### 生产环境与多服务器部署

:::warning 滚动升级可能导致失败
在多服务器部署中，新旧代码同时运行可能导致问题：新代码期望的 schema 还没更新；或旧代码与新 schema 不兼容。
:::

**推荐部署策略：**

<Tabs>
  <TabItem value="separate-job" label="独立迁移 Job" default>

在部署新代码前，先以一次性 Job 运行迁移：

```bash title="Kubernetes Job 示例"
# 1. 运行迁移 Job
kubectl apply -f migration-job.yaml

# 2. 等待完成
kubectl wait --for=condition=complete job/openwebui-migration

# 3. 部署新版本应用
kubectl rollout restart deployment/openwebui
```

这样可以保证 schema 在新代码运行前完成升级。

  </TabItem>
  <TabItem value="maintenance" label="维护窗口">

在迁移期间让应用离线：

```bash title="维护窗口工作流"
# 1. 停止所有应用实例
docker-compose down

# 2. 运行迁移
docker run --rm -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main \
  bash -c "cd /app/backend/open_webui && alembic upgrade head"

# 3. 用新代码重新启动所有实例
docker-compose up -d
```

最简单，但有停机时间。

  </TabItem>
  <TabItem value="blue-green" label="蓝绿部署">

维护两套完全相同的环境，迁移完成后切流量：

```bash title="蓝绿部署工作流"
# 1. 绿（新）环境接入已迁移的数据库
# 2. 在绿环境部署新代码
# 3. 完整验证绿环境
# 4. 把流量从蓝切到绿
# 5. 保留蓝环境作为即时回滚选项
```

零停机，但需要双份基础设施。

  </TabItem>
</Tabs>

### 仅生成 SQL，不直接应用

如需审核或审计，可以生成迁移 SQL 而不真正执行：

```bash title="终端 - 生成迁移 SQL"
# 为待执行迁移生成 SQL
alembic upgrade head --sql > /tmp/migration-plan.sql

# 审查将要应用的内容
cat /tmp/migration-plan.sql
```

**适用场景：**

- 企业环境中的 DBA 审核
- 理解将要发生的具体变更
- 调试迁移问题
- 在受限环境中应用迁移

:::info 什么时候用这个
这是 DBA 或 DevOps 工程师的进阶用法。普通用户直接运行 `alembic upgrade head` 即可。
:::

### 离线迁移（无网络）

如果你的数据库服务器是离线或隔离的：

```bash title="终端 - 离线迁移流程"
# 1. 在开发机上生成 SQL
alembic upgrade head --sql > upgrade-to-head.sql

# 2. 把 SQL 文件传到生产
scp upgrade-to-head.sql production-server:/tmp/

# 3. 在生产手动应用 SQL
sqlite3 /app/backend/data/webui.db < /tmp/upgrade-to-head.sql

# 4. 手动更新 alembic_version 表
sqlite3 /app/backend/data/webui.db \
  "UPDATE alembic_version SET version_num='<target_revision>';"
```

:::danger 手动更新 alembic_version
只有在你**确认对应迁移已经真实执行完成**的前提下，才能更新 `alembic_version`。向 Alembic 撒谎会导致永久性数据库损坏。
:::

## 恢复流程

### 从失败迁移中恢复

:::danger SQLite 没有回滚
SQLite 迁移是**非事务性的**。一旦迁移执行到一半失败，数据库就会停留在部分迁移状态。最安全的恢复方式就是从备份还原。
:::

**部分迁移的症状：**

- 某些表存在，某些表的 schema 与预期不一致
- 外键违规
- 迁移本应添加的列缺失
- 应用报"缺少数据库字段"之类的错误

**恢复步骤：**

```bash title="终端 - 从备份恢复"
# 1. 立刻停止 Open WebUI
docker stop open-webui

# 2. 验证备份完整性
sqlite3 /path/to/webui.db.backup "PRAGMA integrity_check;"

# 3. 恢复备份
cp /path/to/webui.db.backup /path/to/webui.db

# 4. 在重试迁移前先排查根因
docker logs open-webui > migration-failure-logs.txt

# 5. 在重试前带着日志寻求帮助
```

:::warning 不要用 "stamp" 跳过未完成的迁移
如果某次迁移的 schema 变更*并没有*真正应用，就不要用 `alembic stamp` 把它标记为已完成。如果迁移失败时报的是"already exists"或"duplicate column"以外的错误，那么 schema 变更就是真的缺失，stamp 过去只会让数据库陷入损坏状态。具体什么情况下 stamp *可以*使用，见[跨大版本升级后的连续失败](#multiple-failures-after-a-major-version-jump)。
:::

### 验证数据库完整性

迁移前后都应该验证数据库没有损坏：

<Tabs groupId="database-type">
  <TabItem value="sqlite" label="SQLite" default>
    ```bash title="终端 - SQLite 完整性检查"
    sqlite3 /app/backend/data/webui.db "PRAGMA integrity_check;"

    # 输出应该是：ok
    # 出现其他内容就意味着数据库已损坏
    ```
  </TabItem>
  <TabItem value="postgresql" label="PostgreSQL">
    ```bash title="终端 - PostgreSQL 完整性检查"
    # 检查表损坏
    psql -h localhost -U user -d dbname -c "SELECT * FROM pg_stat_database WHERE datname='open_webui_db';"

    # Vacuum 和 analyze
    psql -h localhost -U user -d dbname -c "VACUUM ANALYZE;"
    ```
  </TabItem>
</Tabs>

## 迁移后检查清单

迁移成功后，请确认：

- [ ] `alembic current` 显示 `(head)`，表示已在最新版本
- [ ] Open WebUI 可以无错误启动
- [ ] 可以正常登录
- [ ] 核心功能正常（聊天、模型选择等）
- [ ] 日志中没有错误信息
- [ ] 数据完整（用户、聊天、模型都还在）
- [ ] 在确认稳定运行 1 周后再归档备份

:::tip 保留近期备份
重大迁移前的备份至少保留 1-2 周。某些问题往往要在几天后某个特定业务路径中才会暴露。
:::

## 获取帮助

如果按本指南处理后迁移仍然失败：

**收集诊断信息：**

```bash title="终端 - 收集诊断数据"
# 版本信息
docker logs open-webui 2>&1 | head -20 > diagnostics.txt

# 迁移状态
cd /app/backend/open_webui
alembic current -v >> diagnostics.txt
alembic history >> diagnostics.txt

# 数据库信息（SQLite）
sqlite3 /app/backend/data/webui.db ".tables" >> diagnostics.txt
sqlite3 /app/backend/data/webui.db "SELECT * FROM alembic_version;" >> diagnostics.txt

# 完整的迁移日志
alembic upgrade head 2>&1 >> diagnostics.txt
```

**到哪里寻求帮助：**

1. **Open WebUI 社区**
   - 来自社区成员的实时支持
   - 分享错误信息与诊断数据

2. **请提供以下信息：**
   - Open WebUI 版本
   - 安装方式（Docker / 本地）
   - 数据库类型（SQLite / PostgreSQL）
   - `alembic current` 和 `alembic history` 输出
   - 完整错误信息
   - 错误发生时你正在执行的操作

:::note
不要公开分享你的 `webui.db` 文件——里面有用户凭据和敏感数据。只分享文本形式的诊断输出。
:::
