---
sidebar_position: 50
title: "数据库 Schema"
---

<!-- markdownlint-disable MD060 -->

<a id="database-encryption-with-sqlcipher"></a>

:::warning

本教程是社区贡献，不受 Open WebUI 团队支持。它仅作为如何针对特定用例定制 Open WebUI 的演示。想做出贡献？请查看贡献教程。

:::

> [!WARNING]
> 本文档反映了截至 Open WebUI v0.10.0 的 schema 更改。

## Open-WebUI 内部 SQLite 数据库 {#open-webui-internal-sqlite-database}

对于 Open-WebUI，SQLite 数据库充当用户管理、聊天历史、文件存储和各种其他核心功能的骨干。了解此结构对于任何希望有效地做出贡献或维护该项目的人来说都是必不可少的。

## 内部 SQLite 位置 {#internal-sqlite-location}

你可以在 `root` -> `data` -> `webui.db` 找到 SQLite 数据库

```txt
Root (/)
├── data
│   ├── cache
│   ├── uploads
│   ├── vector_db
│   └── webui.db
├── dev.sh
├── open_webui
├── requirements.txt
├── start.sh
└── start_windows.bat
```

## 本地复制数据库 {#copy-database-locally}

如果你想将容器中运行的 Open-WebUI SQLite 数据库复制到本地机器，可以使用：

```bash
docker cp open-webui:/app/backend/data/webui.db ./webui.db
```

或者，你可以使用以下命令在容器内访问数据库：

```bash
docker exec -it open-webui /bin/sh
```

## 表概览 {#table-overview}

以下是 Open-WebUI SQLite 数据库中所有表的完整列表。为方便起见，各表按字母顺序排列并编号。

| **编号** | **表名**   | **描述**                                              |
| ------- | ---------------- | ------------------------------------------------------------ |
| 01 | access_grant | 存储所有资源的标准化访问控制授权 |
| 02 | auth | 存储用户认证凭据和登录信息 |
| 03 | calendar | 存储用户拥有的带访问控制的日历 |
| 04 | calendar_event | 存储支持重复 (RRULE) 的日历事件 |
| 05 | calendar_event_attendee | 跟踪共享日历事件的参与者 RSVP 状态 |
| 06 | channel | 管理聊天频道及其配置 |
| 07 | channel_file | 将文件链接到频道和消息 |
| 08 | channel_member | 跟踪频道内的用户成员资格和权限 |
| 09 | chat | 存储聊天会话及其元数据 |
| 10 | chat_file | 将文件链接到聊天和消息 |
| 11 | chatidtag | 映射聊天与其关联标签之间的关系 |
| 12 | config | 维护系统范围的配置设置 |
| 13 | document | 存储文档及其元数据以进行知识管理 |
| 14 | feedback | 捕获用户反馈和评分 |
| 15 | file | 管理上传的文件及其元数据 |
| 16 | folder | 将文件和内容组织成分层结构 |
| 17 | function | 存储自定义 Function 及其配置 |
| 18 | group | 管理用户组及其权限 |
| 19 | group_member | 跟踪组内的用户成员资格 |
| 20 | knowledge | 存储知识库条目及相关信息 |
| 21 | knowledge_file | 将文件链接到知识库 |
| 22 | memory | 维护聊天历史和上下文记忆 |
| 23 | message | 存储单个聊天消息及其内容 |
| 24 | message_reaction | 记录用户对消息的反应（表情/响应） |
| 25 | migrate_history | 跟踪数据库 schema 版本和迁移记录 |
| 26 | model | 管理 AI 模型配置和设置 |
| 27 | note | 存储用户创建的笔记和注释 |
| 28 | oauth_session | 管理用户的活动 OAuth 会话 |
| 29 | prompt | 存储 AI 提示词的模板和配置 |
| 30 | prompt_history | 跟踪提示词的版本历史和快照 |
| 31 | shared_chat | 存储共享聊天的快照以便链接共享 |
| 32 | skill | 存储可重用的 Markdown 指令集 (Skills) |
| 33 | tag | 管理内容分类的标签 |
| 34 | tool | 存储系统工具和集成的配置 |
| 35 | user | 维护用户资料和账户信息 |
| 36 | automation | 存储用户定义的计划自动化 |
| 37 | automation_run | 存储自动化运行的执行历史 |
| 38 | pinned_note | 跟踪每个用户的笔记置顶（每行 = 一个用户置顶一个笔记） |
| 39 | chat_message | 聊天会话的标准化逐条消息存储 |
| 40 | api_key | 存储每位用户的 API 密钥 |
| 41 | knowledge_directory | 知识库中用于组织文件的可嵌套文件夹 |
| 42 | channel_webhook | 存储各频道的传入 webhook，用于无需认证的发布 |
| 43 | model_history | 工作区模型配置的历史版本 |
| 44 | tool_history | 工具源代码和元数据的历史版本 |
| 45 | function_history | Function 源代码和元数据的历史版本 |
| 46 | skill_history | Skill 的历史版本，包含其配套文件 |
| 47 | app | 已安装的 [App](/features/channels/apps) 及其加密凭据 |
| 48 | auth_session | 为 [Tether](/ecosystem/tether) 等原生应用提供的可续期登录会话 |
| 49 | comment | 存储工作区条目、笔记和聊天上的评论与回复 |
| 50 | comment_reaction | 记录对评论的表情回应 |
| 51 | notification | 存储每位用户的收件箱通知 |
| 52 | chat_view_state | 存储每位用户为某个聊天保存的标签页布局 |

注意：记录已应用迁移的 `alembic_version` 表与 Open-WebUI 的核心功能无关，因此未列入本表。

关于 `document` 表的说明：这是 Knowledge 功能之前的**旧版**表。其数据行已迁移到 `knowledge` 表（迁移 `6a39f3d8e55c`），现在已不再写入该表，但也没有任何迁移会将其删除，因此早于 Knowledge 功能的数据库中可能仍会保留它（为空）。当前代码中没有对应的模型。

现在我们已经列出了所有表，下面来了解每个表的结构。
## Access Grant 表 {#access-grant-table}

| **列名** | **数据类型** | **约束**         | **描述**                                        |
| --------------- | ------------- | ----------------------- | ------------------------------------------------------ |
| id | Text | PRIMARY KEY | 唯一标识符 |
| resource_type | Text | NOT NULL | 资源类型（例如：`model`, `knowledge`, `tool`） |
| resource_id | Text | NOT NULL | 特定资源的 ID |
| principal_type | Text | NOT NULL | 授权对象类型：`user` 或 `group` |
| principal_id | Text | NOT NULL | 用户或组的 ID（或使用 `*` 表示公开） |
| permission | Text | NOT NULL | 权限级别：`read` 或 `write` |
| created_at | BigInteger | NOT NULL | 授权创建时间戳 |

关于 access_grant 表的注意事项：

- 在 (`resource_type`, `resource_id`, `principal_type`, `principal_id`, `permission`) 上有唯一约束，以防止重复授权
- 在 (`resource_type`, `resource_id`) 和 (`principal_type`, `principal_id`) 上有索引，以提高查询效率
- `principal_type` 为 `user` 且 `principal_id` 为 `*` 表示公共访问，即所有已登录用户。它不包含未登录的访客
- `principal_type` 为 `anyone` 是[开放分享链接](/features/chat-conversations/chat-features/chatshare#open-links-no-sign-in)背后的无需登录授权。它只会以 `anyone` / `*` / `read` 的形式存储，其他组合都会被拒绝，并且仅对 `shared_chat` 资源类型生效。其他所有资源都会将其剥离
- 同时支持组级别和个人用户级别的访问授权
- 组级别的授权同样适用于该组各子组的成员。删除一个组会同时删除其授权
## API Key 表 {#api-key-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | -------------------------------------- | ------------------------------------- |
| id | Text | PRIMARY KEY, UNIQUE | 唯一标识符 |
| user_id | Text | FOREIGN KEY(user.id) CASCADE | 密钥的所有者 |
| key | Text | UNIQUE, NOT NULL | API 密钥本身 |
| data | JSON | nullable | 可扩展的数据载荷 |
| expires_at | BigInteger | nullable | 过期时间戳 |
| last_used_at | BigInteger | nullable | 密钥最后使用的时间戳 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 api_key 表的注意事项：

- 删除用户会级联删除其密钥。
- 生成密钥时会先删除该账户已有的行，因此一个账户最多持有一个密钥。行使用固定的 id `key_{user_id}`。
- 密钥的生成、获取和删除都通过 `/api/v1/auths/api_key` 进行。除非 `auth.enable_api_keys` 配置键已开启，否则三者都会被拒绝；非管理员还需要 `features.api_keys` 权限。
- `data`、`expires_at` 和 `last_used_at` 存在于结构中，但没有任何代码路径写入它们。密钥查找仅按 `key` 进行连接，不会参考 `expires_at`。

## App 表 {#app-table}

由迁移 `c92da83b017f` 为 [Apps](/features/channels/apps) 引入。

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ---------------------------- | -------------------------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID)，即发送给应用的 `app_id` |
| slug | Text | UNIQUE, NOT NULL | 安装时选择的应用标识 |
| name | Text | NOT NULL | 显示名称 |
| user_id | Text | nullable | 安装该应用的管理员 |
| is_active | Boolean | NOT NULL, server_default=false | 应用是否已启用 |
| data | JSON | NOT NULL | 应用 URL、清单、已授予的作用域、设置、安装 ID 以及加密后的连接凭据 |
| api_key | Text | nullable | 该应用的 API 密钥，已加密 |
| created_at | BigInteger | NOT NULL | 创建时间戳（纳秒） |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳（纳秒） |

关于 app 表的注意事项：

- `api_key` 以及 `data` 中的连接凭据使用由 `WEBUI_SECRET_KEY` 派生的密钥加密。
- 卸载应用会保留该行及其 `slug`：它会清空 `api_key`、连接凭据和安装 ID，把 `is_active` 设为 false，并停用该应用的频道成员关系。
- 谁可以使用某个应用，记录在 `access_grant` 表中，`resource_type = 'app'`。
- 只要 `message` 表中有任何一行带有 `app_id`，回退到 `c92da83b017f` 之前的版本就会被拒绝。

## Auth 表 {#auth-table}

| **列名** | **数据类型** | **约束** | **描述**   |
| --------------- | ------------- | --------------- | ----------------- |
| id | String | PRIMARY KEY | 唯一标识符 |
| email | String | - | 用户邮箱 |
| password | Text | - | 哈希密码 |
| active | Boolean | - | 账户状态 |
| mfa | JSON | nullable | 双因素登录状态：加密的验证器密钥、哈希后的恢复码、待完成的登录步骤以及尝试计数 |
| session_stamp | Text | nullable | 每个会话令牌都携带的标记；替换它会让该账户在所有设备上退出登录 |

关于 auth 表的注意事项：

- 使用 UUID 作为主键
- 与 `user` 表是一对一关系（共享 id）
- `mfa` 和 `session_stamp` 由迁移 `a7d3e9f2b641` 添加。此前已存在的行这两项均为空，升级前签发的会话在账户首次于所有设备退出登录之前仍然有效。
- 迁移 `0bd252b206fb` 会为每个尚无该行的用户添加一行，其 `password` 为空、永远不会匹配。该迁移只改动数据，其降级操作会保留已添加的行。
## Auth Session 表 {#auth-session-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ---------------------------------------------------------------------------------- |
| id | Text | PRIMARY KEY | 唯一会话标识符 (UUID) |
| user_id | Text | nullable | 已登录用户；在浏览器登录请求等待批准期间为空 |
| refresh_token_id | Text | nullable | 当前刷新令牌的标识；在登录完成前为空 |
| data | JSON | NOT NULL | 应用名称以及待处理登录请求的状态 |
| created_at | BigInteger | NOT NULL | 会话创建时间戳 |
| updated_at | BigInteger | NOT NULL | 会话最后更新时间戳 |
| expires_at | BigInteger | NOT NULL | 会话过期时间戳 |

关于 auth_session 表的注意事项：

- 由迁移 `8bc7e5a902d1` 创建。表中的一行要么是已登录用户创建的会话，要么是待处理的登录请求，在应用完成登录后即会成为会话。登录流程参见 [Tether 客户端协议](/reference/tether-client-protocol)。
- `user_id` 不带外键。它与 `user` 的关系是一对多：一个用户可以持有多个会话，每个已登录应用一个。
- 在 `user_id` 和 `expires_at` 上建有索引（`idx_auth_session_user`、`idx_auth_session_expires`）。
- 待处理请求的 `expires_at` 为创建后 10 分钟。会话的 `expires_at` 为创建或上次令牌刷新后 [`SESSION_EXPIRES_IN`](/reference/env-configuration#session_expires_in)。每创建新行时，已过期的行都会被删除。
- 通过 API 退出登录或删除会话会移除该行。
## Channel 表 {#channel-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ----------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| user_id | Text | - | 频道的拥有者/创建者 |
| type | Text | nullable | 频道类型 |
| name | Text | - | 频道名称 |
| description | Text | nullable | 频道描述 |
| is_private | Boolean | nullable | `group` 类型频道的私有标志 |
| data | JSON | nullable | 灵活的数据存储 |
| meta | JSON | nullable | 频道元数据 |
| created_at | BigInteger | - | 创建时间戳（纳秒） |
| updated_at | BigInteger | - | 最后更新时间戳（纳秒） |
| updated_by | Text | nullable | 最后更新该频道的用户 |
| archived_at | BigInteger | nullable | 归档时间戳（纳秒） |
| archived_by | Text | nullable | 归档该频道的用户 |
| deleted_at | BigInteger | nullable | 删除时间戳（纳秒） |
| deleted_by | Text | nullable | 删除该频道的用户 |

关于 channel 表的注意事项：

- 使用 UUID 作为主键
- 频道名称不区分大小写（以小写存储）
- `type` 由迁移 `3781e22d8b01` 添加。`is_private`、`updated_by`、`archived_at`、`archived_by`、`deleted_at` 和 `deleted_by` 由迁移 `90ef40d4714e` 添加。
- 频道列表和成员查询只返回 `archived_at` 与 `deleted_at` 均为 null 的行，因此该表结构是为归档和软删除设计的。
- 没有任何代码路径会写入 `archived_at`、`archived_by`、`deleted_at`、`deleted_by` 或 `updated_by`。删除频道会直接移除该行，因此已删除的频道不会留下任何内容供 `deleted_at` 过滤器排除。任何直接查询该表的人都会发现这五列在每一行都是 null。
- 该表创建时带的 `access_control` 列已在迁移 `f1e2d3c4b5a6` 中删除。频道访问通过 `access_grant` 表管理，其 `resource_type = 'channel'`。
## Channel Member 表 {#channel-member-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | -------------------------------------------- |
| id | Text | PRIMARY KEY, UNIQUE | 频道成员资格的唯一标识符 |
| channel_id | Text | NOT NULL | 对频道的引用 |
| user_id | Text | nullable | 对用户的引用 |
| app_id | Text | nullable | 对 App 的引用，用于 App 成员身份 |
| role | Text | nullable | 成员在频道中的角色 |
| status | Text | nullable | 成员状态：`joined` 或 `left` |
| is_active | Boolean | NOT NULL, server_default=true | 该成员身份是否有效 |
| is_channel_muted | Boolean | NOT NULL, server_default=false | 按成员设置的静音标志 |
| is_channel_pinned | Boolean | NOT NULL, server_default=false | 按成员设置的置顶标志 |
| data | JSON | nullable | 可扩展的数据载荷 |
| meta | JSON | nullable | 可选的元数据 |
| invited_at | BigInteger | nullable | 邀请时间戳（纳秒） |
| invited_by | Text | nullable | 添加该成员的用户 |
| joined_at | BigInteger | NOT NULL | 加入时间戳（纳秒） |
| left_at | BigInteger | nullable | 离开时间戳（纳秒） |
| last_read_at | BigInteger | nullable | 最后阅读时间戳，决定未读状态 |
| created_at | BigInteger | - | 创建成员资格的时间戳 |
| updated_at | BigInteger | nullable | 最后更新时间戳（纳秒） |

关于 channel_member 表的注意事项：

- `role`、`invited_at` 和 `invited_by` 由迁移 `90ef40d4714e` 添加。`status`、`is_active`、`is_channel_muted`、`is_channel_pinned`、`data`、`meta`、`joined_at`、`left_at`、`last_read_at` 和 `updated_at` 由迁移 `2f1211949ecc` 添加。
- 成员关系创建时 `status` 写入 `joined`。离开频道会写入 `left`，将 `is_active` 置为 false 并记录 `left_at`。该行会保留。
- `is_active` 是频道列表和成员列表所依据的过滤标志，因此已离开的成员关系会从这些结果中消失，但仍留在表中。它也会由 `POST /api/v1/channels/{id}/members/active` 写入。
- 成员关系创建时会记录 `last_read_at`，用户阅读频道时通过 socket 连接更新。
- `role` 只在一处被读取，用于判断成员是否为 `manager`。没有任何地方写入 `manager`：用户成员关系的 `role` 保持为 null，App 成员关系则写为 `member`，因此该判断永远不会命中。仅限管理者执行的操作（例如查看和创建频道 webhook）会落到该判断的另外两个分支：频道自身的 `user_id`，或实例管理员。
- `is_channel_muted` 是成员的[**仅提及**](/features/channels#muting-a-channel)设置，由 `POST /api/v1/channels/{id}/members/mute` 写入。对成员从未打开过的标准频道执行静音，会为其创建成员关系行。在该值为 true 期间，频道通知 webhook 只有在消息提及该成员时才会送达该成员。`is_channel_pinned` 在模型上有一个名为 `Channels.pin_channel` 的 setter，但没有任何地方调用它。
- `joined_at` 在数据库中是 NOT NULL（迁移 `2f1211949ecc`），而 SQLAlchemy 模型中省略了该标志。以数据库约束为准。
- 将 App 从频道中移除或卸载该 App，会将 `is_active` 置为 false 并记录 `left_at`；`status` 仍为 `joined`。再次添加该 App 会重新激活同一行。
- 迁移 `c92da83b017f` 将 `user_id` 改为可空并添加了 `app_id`。检查约束要求每一行两者中恰好有一个非空，且 (`channel_id`, `app_id`) 唯一。
- 删除用户账户会保留其 `channel_member` 行。成员列表、频道上的成员数，以及为一批人查找已有私信的查询，都会跳过 `user_id` 已无对应账户的行，因此残留行不会被计为成员，也不会把私信推送给它本不该发送给的人。
## Channel Webhook 表 {#channel-webhook-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | -------------------------------------------- | ----------------------------------- |
| id | Text | PRIMARY KEY, UNIQUE | 唯一标识符 |
| channel_id | Text | FOREIGN KEY(channel.id) CASCADE, NOT NULL | webhook 发布到的频道 |
| user_id | Text | NOT NULL | 创建该 webhook 的用户 |
| name | Text | NOT NULL | 显示在其消息上的名称 |
| profile_image_url | Text | nullable | 显示在其消息上的头像 |
| token | Text | NOT NULL | 用于授权发布的密钥 |
| last_used_at | BigInteger | nullable | 最后一次发布的时间戳 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

用于在没有登录用户的情况下向某个频道发布消息的传入 webhook。由迁移 `90ef40d4714e` 添加。

关于 channel_webhook 表的注意事项：

- 删除频道会级联删除其 webhook。
- `token` 是 URL 安全的随机令牌，包含 32 字节熵，使用 `secrets.token_urlsafe(32)` 生成，以明文存储并出现在请求路径中。`POST /api/v1/channels/webhooks/{webhook_id}/{token}` 不接受任何认证，而是用 `id` 与 `token` 这一对值到表中匹配，因此任何持有这对值的人都可以向该频道发布消息。
- 每次成功发布的请求都会记录 `last_used_at`。
- 列出和创建 webhook 要求调用者是实例管理员或该频道的创建者。关于该检查中基于成员身份的 manager 分支为何永远不命中，请参见[频道成员表](#channel-member-table)中的 `role` 说明。
- webhook 的 `id` 和 `name` 会被复制到所发布消息的 `meta.webhook` 中，界面用它来代替作者账户进行渲染。
## Channel File 表 {#channel-file-table}

| **列名** | **数据类型** | **约束**                    | **描述**                   |
| --------------- | ------------- | ---------------------------------- | --------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| user_id | Text | NOT NULL | 关系的拥有者 |
| channel_id | Text | FOREIGN KEY(channel.id) CASCADE, NOT NULL | 对频道的引用 |
| file_id | Text | FOREIGN KEY(file.id) CASCADE, NOT NULL | 对文件的引用 |
| message_id | Text | FOREIGN KEY(message.id) CASCADE, nullable | 对关联消息的引用 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 channel_file 表的注意事项：

- 在 (`channel_id`, `file_id`) 上的唯一约束以防止重复条目
- 带有 CASCADE 删除的外键关系
- 在 `channel_id`, `file_id` 和 `user_id` 上建立索引以提高性能

## Chat 表 {#chat-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ----------------------- | ------------------------ |
| id | String | PRIMARY KEY | 唯一标识符（UUID） |
| user_id | String | - | 聊天的拥有者 |
| title | Text | - | 聊天标题 |
| chat | JSON | - | 聊天内容和历史 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |
| share_id | Text | UNIQUE, nullable | 共享标识符 |
| archived | Boolean | default=False | 归档状态 |
| pinned | Boolean | default=False, nullable | 置顶状态 |
| meta | JSON | server_default="{}" | 包含标签的元数据 |
| folder_id | Text | nullable | 父文件夹 ID |
| tasks | JSON | nullable | 代理工作流使用的聊天级任务/待办事项列表 |
| summary | Text | nullable | 可选的聊天摘要文本 |
| last_read_at | BigInteger | nullable | 用于未读指示器的最后阅读时间戳 |
| current_message_id | Text | nullable | 聊天历史中当前（活动叶子）消息 |
| variables | JSON | nullable | 为模型聊天变量填入的值 |
| timer_at | BigInteger | nullable | 到期时间（纳秒），仅在定时聊天等待被领取时设置 |

关于 chat 表的注意事项：

- `tasks` 和 `summary` 支持聊天会话中的结构化计划/状态 UX。
- `last_read_at` 由侧边栏未读状态逻辑使用（与 `updated_at` 比较）。
- 当聊天具有活动的分享链接时，`share_id` 引用 `shared_chat.id` 令牌。
- `current_message_id` 由迁移 `9a1b2c3d4e5f` 添加。它记录聊天当前所处的消息，即新回复所延续的活动分支的叶子节点，并在迁移运行时依据现有历史回填。上下文压缩和上下文用量解析会读取它，因此它们作用于实际生效的分支，而不是整棵消息树。
- `variables` 由迁移 `c49178636c78` 添加。它以变量名为键的扁平映射保存用户为模型系统提示词所声明的[聊天变量](/features/chat-conversations/chat-features/chat-params#chat-variables)填入的值，并在聊天所有者派生或克隆该聊天时一并复制。由其他人创建的副本从空映射开始。临时聊天只在请求中保留其值，因此不会存储任何内容。
- 迁移 `242a2047eae0` 添加了一个 **`old_chat`** 列（Text），用于以文本形式备份原始的 JSON `chat` blob。它是迁移阶段的安全网，不属于活动模型，运行时也不会读取。
## Shared Chat 表 {#shared-chat-table}

| **列名** | **数据类型** | **约束**                  | **描述**                    |
| --------------- | ------------- | -------------------------------- | ---------------------------------- |
| id | Text | PRIMARY KEY | 用于 `/s/{id}` URL 的分享令牌 (UUID) |
| chat_id | Text | FOREIGN KEY(chat.id) CASCADE, NOT NULL | 对原始聊天的引用 |
| user_id | Text | NOT NULL | 创建分享的用户 |
| title | Text | nullable | 分享时的聊天标题 |
| chat | JSON | nullable | 分享时的聊天内容快照 |
| created_at | BigInteger | nullable | 分享创建时间戳 |
| updated_at | BigInteger | nullable | 最后重新快照时间戳 |

关于 shared_chat 表的注意事项：

- 替换了以前将共享聊天快照作为幽灵行存储在 `chat` 表中（`user_id` 设置为 `shared-{chat_id}`）的模式。
- 每行都是原始聊天在共享（或最后一次重新共享）时不可变的快照。当用户点击“更新并复制链接”时会更新此快照。
- 删除原始聊天会级联删除共享快照。
- 共享聊天的访问控制通过 `access_grant` 表（`resource_type = 'shared_chat'`）进行管理。

## Chat Message 表 {#chat-message-table}

`chat_message` 表是聊天会话的**标准化逐条消息存储**：每条消息一行，独立于 `chat.chat` 中的 JSON 历史 blob，并且与频道 [Message 表](#message-table)（保存频道/线程消息，而非聊天模型轮次）不同。

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ---------------------------------------- | -------------------------------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| chat_id | Text | FOREIGN KEY(chat.id) CASCADE, NOT NULL | 父级聊天 |
| user_id | Text | indexed | 消息作者 |
| role | Text | NOT NULL | 消息角色：`user`、`assistant` 或 `system` |
| parent_id | Text | nullable | 父消息 ID（用于分支对话） |
| content | JSON | nullable | 消息内容（字符串或内容块列表） |
| output | JSON | nullable | 生成的输出载荷 |
| model_id | Text | nullable, indexed | 生成该消息的模型 |
| files | JSON | nullable | 附加文件 |
| sources | JSON | nullable | 检索/引用来源 |
| embeds | JSON | nullable | 嵌入的工件 |
| meta | JSON | nullable | 消息元数据；标记内部的子代理消息和定时消息 |
| done | Boolean | default=True | 生成是否完成 |
| status_history | JSON | nullable | 生成期间的流式状态更新 |
| error | JSON | nullable | 生成失败时的错误载荷 |
| usage | JSON | nullable | Token/使用统计 |
| context_summary | Text | nullable | 每条消息的上下文摘要（v0.10.0 新增） |
| created_at | BigInteger | indexed | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

`chat_message` 表是聊天会话的**标准化逐条消息存储**：每条消息一行，独立于 `chat.chat` 中的 JSON 历史 blob，并且与频道 [Message 表](#message-table)（保存频道/线程消息，而非聊天模型轮次）不同。

关于 chat_message 表的注意事项：

- 删除聊天会级联删除其消息（带有 `ON DELETE CASCADE` 的 `chat_id` 外键）。
- 复合索引支持常见的访问模式：(`chat_id`, `parent_id`)、(`model_id`, `created_at`) 和 (`user_id`, `created_at`)。
- `context_summary` 由迁移 `4c5ce3d2f27f` 添加，用于存储消息上下文的摘要。
- `meta` 由迁移 `856c5b02fb54` 添加。它保存逐条消息的元数据，也正是它标记了 Open WebUI 代表用户注入的消息，例如[子代理](/features/chat-conversations/chat-features/subagents)的结果或已触发的[定时器](/features/chat-conversations/chat-features/timers)，从而让界面可以将它们与用户亲手输入的消息区别渲染。
- [聊天搜索](/features/chat-conversations/chat-features/history-search)针对不同后端读取不同的存储位置。在 PostgreSQL 上，它会匹配 `chat_message.content`，以及 `chat.chat` blob 内部的 `history.messages` 映射和更早的扁平 `messages` 数组。在 SQLite 上，它只匹配后两处 JSON 位置。
## Chat View State 表 {#chat-view-state-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ------------------------------------------------------------ |
| user_id | Text | PRIMARY KEY | 该视图所属的用户 |
| chat_id | Text | PRIMARY KEY, indexed | 该视图所属的聊天 |
| state | JSON | NOT NULL | 打开的标签页、分栏布局以及选中的终端 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳（秒） |

关于 chat_view_state 表的注意事项：

- 由迁移 `6a23bd107e54` 创建。主键为 (`user_id`, `chat_id`)，并在 `chat_id` 上建有索引 (`ix_chat_view_state_chat_id`)。
- 它保存用户在某个聊天中打开过的标签页，因此在任何设备上重新打开该聊天时都会恢复。`GET` 与 `POST /api/v1/chats/{id}/view` 会为任何有权读取该聊天的用户读取和保存它。
- 每一行都只对其所属用户可见，即使对于共享聊天也是如此：这些端点只读写当前登录用户自己的行。保存的视图上限为 1 MiB。
- 删除聊天会删除其相关行，删除用户会删除该用户的行。

## Automation 表 {#automation-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ----------------------- | --------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| user_id | Text | NOT NULL | 自动化任务的所有者 |
| folder_id | Text | nullable | 运行所创建的聊天所在的文件夹 |
| name | Text | NOT NULL | 自动化的显示名称 |
| data | JSON | NOT NULL | 自动化有效负载 (`prompt`, `model_id`, `rrule`, 可选终端配置) |
| meta | JSON | nullable | 可选元数据 |
| is_active | Boolean | NOT NULL, default=True | 激活/暂停状态 |
| last_run_at | BigInteger | nullable | 上次执行时间 |
| next_run_at | BigInteger | nullable | 下一次计划执行时间 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 automation 表的注意事项：

- `next_run_at` 已建立索引以便进行高效的到期运行轮询。
- `data.rrule` 定义了重复发生频率并驱动调度器计算。
- `folder_id` 由迁移 `959eaac8f909` 添加，并同时建立了 (`user_id`, `folder_id`) 索引，因此所有者的自动化可以按文件夹列出。它不是外键：删除文件夹会清空该所有者自动化上的该列，而不是删除自动化本身；若某次运行期间其文件夹已消失，该列同样会被清空，其聊天也会被归入任何文件夹之外。
## Automation Run 表 {#automation-run-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | --------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| automation_id | Text | NOT NULL | 对自动化的引用 |
| chat_id | Text | nullable | 此次运行创建的聊天（如果可用） |
| status | Text | NOT NULL | 运行状态 (`success` / `error`) |
| error | Text | nullable | 当状态为 `error` 时的错误详情 |
| created_at | BigInteger | NOT NULL | 执行记录时间戳 |

关于 automation_run 表的注意事项：

- 在 `automation_id` 上建立索引以快速查询每个自动化的运行历史。
- 删除自动化时删除关联行。

## Calendar 表 {#calendar-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ----------------------- | ---------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| user_id | Text | NOT NULL | 日历的所有者 |
| name | Text | NOT NULL | 日历显示名称 |
| color | Text | nullable | 显示颜色（十六进制，例如 `#3b82f6`） |
| is_default | Boolean | NOT NULL, default=False | 这是否是用户的默认日历 |
| data | JSON | nullable | 可扩展的数据有效负载 |
| meta | JSON | nullable | 可选的元数据 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 calendar 表的注意事项：

- 在 `user_id` 上建立索引以高效列出每个用户的日历。
- 在首次访问时自动创建一个默认的“Personal”（个人）日历。
- “Scheduled Tasks”（计划任务）日历是**虚拟的** — 它不存储在此表中。相反，对于具有自动化访问权限的用户，API 在响应时（使用恒定 ID `__scheduled_tasks__`）综合出它。自动化 RRULE 的未来运行和过去的执行记录都会作为该日历上的虚拟事件呈现。
- 访问控制通过 `access_grant` 表（`resource_type = 'calendar'`）进行管理，从而实现用户和组之间的日历共享。
- 用户只能删除非默认日历。删除日历会级联到其所有事件、参与者和访问授权。

## Calendar Event 表 {#calendar-event-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ----------------------- | ---------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| calendar_id | Text | NOT NULL | 对父日历的引用 |
| user_id | Text | NOT NULL | 创建事件的用户 |
| title | Text | NOT NULL | 事件标题 |
| description | Text | nullable | 事件描述 |
| start_at | BigInteger | NOT NULL | 开始时间（纪元纳秒） |
| end_at | BigInteger | nullable | 结束时间（纪元纳秒） |
| all_day | Boolean | NOT NULL, default=False | 这是否是一个全天事件 |
| rrule | Text | nullable | 用于重复发生的 iCalendar RRULE |
| color | Text | nullable | 每个事件颜色覆盖 |
| location | Text | nullable | 事件位置 |
| data | JSON | nullable | 可扩展的数据有效负载 |
| meta | JSON | nullable | 可选元数据（例如 `automation_id`） |
| is_cancelled | Boolean | NOT NULL, default=False | 软取消标志 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 calendar_event 表的注意事项：

- 在 (`calendar_id`, `start_at`) 上建立复合索引，以便在一个日历内进行高效的范围查询。
- 在 (`user_id`, `start_at`) 上建立复合索引，以便每个用户进行高效的日期范围查询。
- 重复事件存储 `rrule` 字符串，并在查询时扩展为单独的实例（使用 `dateutil` 进行服务器端 Python 扩展）。
- 取消的事件（`is_cancelled = True`）被排除在范围查询之外，但保留在数据库中。

## Calendar Event Attendee 表 {#calendar-event-attendee-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ---------------------------------- | ---------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| event_id | Text | NOT NULL | 对日历事件的引用 |
| user_id | Text | NOT NULL | 被邀请参加事件的用户 |
| status | Text | NOT NULL, default='pending' | RSVP 状态：`pending`（待定）、`accepted`（已接受）、`declined`（已拒绝）、`tentative`（暂定） |
| meta | JSON | nullable | 可选的元数据 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 calendar_event_attendee 表的注意事项：

- 在 (`event_id`, `user_id`) 上的唯一约束以防止重复的参与者条目。
- 在 (`user_id`, `status`) 上建立索引以高效查找邀请用户的事件。
- 当使用新参与者列表更新事件时，将批量替换参与者。
- 删除事件会级联删除所有参与者记录。

## Chat File 表 {#chat-file-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | -------------------------------- | --------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| user_id | Text | NOT NULL | 与该文件关联的用户 |
| chat_id | Text | FOREIGN KEY(chat.id), NOT NULL | 聊天引用 |
| file_id | Text | FOREIGN KEY(file.id), NOT NULL | 文件引用 |
| message_id | Text | nullable | 关联消息的引用 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 chat_file 表的注意事项：

- 对 (`chat_id`, `file_id`) 施加唯一约束，以防止重复条目
- 带有 CASCADE 删除的外键关系
- 对 `chat_id`、`file_id`、`message_id`、`user_id` 建立索引以提升性能

**为何添加此表：**

- **查询效率**：此前文件是嵌入在消息对象中的。此表支持通过索引直接查找某个聊天中的全部文件，无需遍历每一条消息。
- **数据一致性**：充当文件关联关系的唯一事实来源。在多节点部署中，所有节点都查询此表，而不依赖可能不一致的嵌入数据。
- **去重**：数据库级的唯一约束可防止重复的文件关联关系，比应用层的检查更可靠。

## Chat ID Tag 表 {#chat-id-tag-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ------------------ |
| id | String | PRIMARY KEY | 唯一标识符 |
| tag_name | String | nullable | 标签名称 |
| chat_id | String | nullable | 聊天引用 |
| user_id | String | nullable | 用户引用 |
| timestamp | BigInteger | nullable | 创建时间戳 |

关于 `chatidtag` 表的说明：这是聊天标签迁移到聊天记录之前的**旧版**表。其数据行已被读入 `chat` 表（迁移 `1af9b942657b`），该迁移把每个标签写入 `chat.meta.tags`，并把 `pinned` 标签转换为 `chat.pinned`，现在已不再向该表写入任何内容。该迁移会保留这些行，且没有任何迁移会删除该表，因此较旧的数据库中可能仍存有过期数据行。当前代码中没有对应的模型。聊天标签现在位于 `tag` 表中。
## Comment 表 {#comment-table}

| **列名** | **数据类型** | **约束** | **描述** |
| --------------- | ------------- | --------------- | ------------------------------------------------------------------------ |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| user_id | Text | nullable | 作者；评论被删除后置空 |
| resource_type | Text | NOT NULL | 被评论对象的类型：`model`、`knowledge`、`prompt`、`skill`、`tool`、`note` 或 `chat` |
| resource_id | Text | NOT NULL | 被评论对象的 ID |
| parent_id | Text | nullable | 主题的顶层评论；顶层评论为空 |
| reply_to_id | Text | nullable | 此回复所答复的评论 |
| content | Text | NOT NULL | 评论文本 |
| target_type | Text | nullable | 评论所指向对象的部分：`note_page` 或 `chat_message` |
| target_id | Text | nullable | 该部分的 ID |
| meta | JSON | nullable | 评论在所选文本上的引用范围（`anchor`） |
| created_at | BigInteger | NOT NULL | 创建时间戳（纳秒） |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳（纳秒） |
| deleted_at | BigInteger | nullable | 删除时间戳（纳秒） |

关于 comment 表的注意事项：

- 在 (`resource_type`, `resource_id`, `parent_id`, `created_at`, `id`)、(`parent_id`, `created_at`, `id`) 以及 (`resource_type`, `resource_id`, `target_type`, `target_id`) 上建立索引。
- 删除评论时会保留其行，以便主题和被引用的回复保持完整：`content` 会被清空，`user_id` 与 `meta` 会被清除，并设置 `deleted_at`。
- 删除被评论的对象会同时删除其评论及其反应。

## Comment Reaction 表 {#comment-reaction-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ---------------------------- | ---------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| user_id | Text | NOT NULL | 作出反应的用户 |
| comment_id | Text | NOT NULL, INDEX | 评论的引用 |
| name | Text | NOT NULL | 反应（表情）名称 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |

关于 comment_reaction 表的注意事项：

- 在 (`comment_id`, `user_id`, `name`) 上有唯一约束：一个用户对同一条评论只能添加一次相同的反应。

## Config 表 {#config}

自 v0.10.0 起，config 表采用**每键一行**格式：每个设置都在自己的行中，以点号路径为键，取代了以前的单行 JSON blob。

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | -------------------------------------------------------- |
| key | Text | PRIMARY KEY | 点号表示法的配置键（例如 `audio.stt.engine`） |
| value | JSON | NOT NULL | 此键的存储值 |
| updated_at | BigInteger | nullable | 最后更新时间戳（纪元） |

关于 config 表的注意事项：

- 在迁移 `3ff2c63645b8` 中进行了重构。旧的单行 schema（`id` INTEGER PK, `data` JSON, `version` INTEGER, `created_at`/`updated_at` DATETIME）通过将 JSON blob 展开为每键一行进行了迁移。
- 迁移前的表被保留为 **`config_old`**（重命名，未删除），因此更改是可逆的；它在运行时不被使用。
- 读写通过各个键进行，这避免了每次更改时重写整个配置 blob。

## Feedback 表 {#feedback-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| user_id | Text | - | 提供反馈的用户 |
| version | BigInteger | default=0 | 反馈版本号 |
| type | Text | - | 反馈类型 |
| data | JSON | nullable | 包括评分在内的反馈数据 |
| meta | JSON | nullable | 元数据 (arena, chat_id 等) |
| snapshot | JSON | nullable | 关联的聊天快照 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

## File 表 {#file-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | --------------------- |
| id | String | PRIMARY KEY | 唯一标识符 |
| user_id | String | - | 文件的所有者 |
| hash | Text | nullable | 文件哈希/校验和 |
| filename | Text | - | 文件名称 |
| path | Text | nullable | 文件系统路径 |
| data | JSON | nullable | 文件相关数据 |
| meta | JSON | nullable | 文件元数据 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

`meta` 字段的预期结构：

```python
{
    "name": string,          # Optional display name
    "content_type": string,  # MIME type
    "size": integer,         # File size in bytes
    # Additional metadata supported via ConfigDict(extra="allow")
}
```

- 在 PostgreSQL 上，部分索引 `file_pending_knowledge_idx`（迁移 `b8f2c6d91a04`）覆盖 `data.status` 为 `pending` 或 `processing` 的文件，并以 `meta.data.knowledge_id` 中的知识库 id 为键。打开知识库时会用它通过一次简短的索引查找找出仍在处理中的文件。在 SQLite 上该迁移不起作用。如果 PostgreSQL 无法创建该索引，迁移会记录一条警告并标记为已应用，因此启动会在没有该索引的情况下继续。
## Folder 表 {#folder-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ------------------------------ |
| id | Text | PK (composite) | 唯一标识符（UUID） |
| parent_id | Text | nullable | 用于分层结构的父文件夹 ID |
| user_id | Text | PK (composite) | 文件夹的所有者 |
| name | Text | - | 文件夹名称 |
| items | JSON | nullable | 文件夹内容 |
| data | JSON | nullable | 额外的文件夹数据 |
| meta | JSON | nullable | 文件夹元数据 |
| is_expanded | Boolean | default=False | UI 展开状态 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

关于 folder 表的注意事项：

- 主键是复合键 (`id`, `user_id`)
- 文件夹可以嵌套（`parent_id` 引用）
- 根文件夹的 `parent_id` 为 null
- 在同一父级文件夹内，文件夹名称必须唯一

## Function 表 {#function-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ------------------------- |
| id | String | PRIMARY KEY | 唯一标识符 |
| user_id | String | - | 函数的所有者 |
| name | Text | - | 函数名称 |
| type | Text | - | 函数类型 |
| content | Text | - | 函数内容/代码 |
| meta | JSON | - | 函数元数据 |
| valves | JSON | - | 函数控制设置 |
| is_active | Boolean | - | 函数激活状态 |
| is_global | Boolean | - | 全局可用性标志 |
| version_id | Text | nullable | 生产版本（`function_history.id`） |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

关于 function 表的注意事项：

- `type` 只能是：`pipe`、`filter`、`action`、`event`。类型会根据函数源代码中的顶层类名自动检测。
## Function History 表 {#function-history-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | -------------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| function_id | Text | NOT NULL, INDEX | 该版本所属的函数 |
| parent_id | Text | nullable | 保存此版本时所基于的版本 |
| snapshot | JSON | NOT NULL | 保存的名称、源代码和元数据 |
| user_id | Text | NOT NULL | 保存该版本的用户 |
| commit_message | Text | nullable | 保存时填写的描述 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |

关于 function history 表的注意事项：

- 快照保存 `name`、源代码，以及 `meta` 中的描述和翻译。Valves、启用/全局开关以及检测到的类型仍保留在 `function` 行上。
- 迁移 `f8c0e5b134cd` 与 `tool_history` 一同创建了该表，并为每个已有函数提供了一个起始版本。
## Group 表 {#group-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ------------------- | ------------------------ |
| id | Text | PRIMARY KEY, UNIQUE | 唯一标识符（UUID） |
| parent_group_id | Text | FOREIGN KEY(group.id), nullable, indexed | [嵌套用户组](/features/authentication-access/rbac/groups#nested-groups)的父用户组，顶层用户组为 `NULL` |
| user_id | Text | - | 群组所有者/创建者 |
| name | Text | - | 群组名称 |
| description | Text | - | 群组描述 |
| data | JSON | nullable | 额外的群组数据 |
| meta | JSON | nullable | 群组元数据 |
| permissions | JSON | nullable | 权限配置 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

注意：`user_ids` 列已迁移到 `group_member` 表。

关于 group 表的注意事项：

- `parent_group_id` 由迁移 `b8e4f0a3c752` 添加。用户组成员会继承其上方所有用户组的权限和访问授权
- 删除一个用户组会把它的子组上移到它自己的父组，并删除其成员关系和访问授权
- `data.config.default_models` 以模型 ID 列表的形式保存该用户组的[默认模型](/features/authentication-access/rbac/groups#default-models-per-group)，`data.config.share` 保存 **谁可以共享到此用户组** 设置
## Group Member 表 {#group-member-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | -------------------------------- | --------------------------------- |
| id | Text | PRIMARY KEY, UNIQUE | 唯一标识符（UUID） |
| group_id | Text | FOREIGN KEY(group.id), NOT NULL | 引用该组 |
| user_id | Text | FOREIGN KEY(user.id), NOT NULL, indexed | 用户引用 |
| created_at | BigInteger | nullable | 创建时间戳 |
| updated_at | BigInteger | nullable | 最后更新时间戳 |

关于 group_member 表的注意事项：

- 在 (`group_id`, `user_id`) 上有唯一约束以防止重复成员关系，它同时也服务于从用户组出发的查询
- 在 (`user_id`, `group_id`) 上有索引，以便高效查询某用户所属的用户组（迁移 `1ce6ade7d93b`）。唯一约束以 `group_id` 开头，无法回答这个问题，因此没有这个索引时，每次权限和访问检查都会读取整个成员关系表，而其开销会随实例上成员关系总数增长，而不是随单个用户的成员关系数量增长
- 到 group 和 user 表的外键关系采用 CASCADE 删除
## Knowledge 表 {#knowledge-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ------------------- | -------------------------- |
| id | Text | PRIMARY KEY, UNIQUE | 唯一标识符（UUID） |
| user_id | Text | - | 知识库所有者 |
| name | Text | - | 知识库名称 |
| description | Text | - | 知识库描述 |
| meta | JSON | nullable | 额外的元数据 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

| created_at      | BigInteger    | -                   | 创建时间戳|
| updated_at      | BigInteger    | -                   | 最后更新时间戳|

## Knowledge Directory 表 {#knowledge-directory-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | -------------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| knowledge_id | Text | FOREIGN KEY(knowledge.id) CASCADE, NOT NULL | 所属的知识库 |
| parent_id | Text | FOREIGN KEY(knowledge_directory.id) CASCADE, nullable | 父目录；顶级目录为空 |
| name | Text | NOT NULL | 目录名称 |
| user_id | Text | NOT NULL | 创建该目录的用户 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

用于组织单个知识库内部文件的可嵌套文件夹。由迁移 `3c9b0ca343fd` 添加，该迁移同时为[知识文件表](#knowledge-file-table)添加了 `directory_id`。

关于 knowledge_directory 表的注意事项：

- 目录通过自引用的 `parent_id` 嵌套。根目录的 `parent_id` 为 null。
- 在 (`knowledge_id`, `parent_id`, `name`) 上有唯一约束（`uq_knowledge_directory_knowledge_parent_name`），因此同一知识库内的同级目录名称唯一。
- 在 `knowledge_id` 和 `parent_id` 上有索引（`ix_knowledge_directory_knowledge_id`、`ix_knowledge_directory_parent_id`）。
- 删除知识库会级联删除其目录。删除目录会级联删除嵌套在其中的目录。
## Knowledge File 表 {#knowledge-file-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ------------------------------------ | --------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| user_id | Text | NOT NULL | 关联关系的所有者 |
| knowledge_id | Text | FOREIGN KEY(knowledge.id), NOT NULL | 引用知识库 |
| file_id | Text | FOREIGN KEY(file.id), NOT NULL | 文件引用 |
| directory_id | Text | FOREIGN KEY(knowledge_directory.id) SET NULL, nullable, indexed | 存放该文件的目录 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 knowledge_file 表的注意事项：

- 在 (`knowledge_id`, `file_id`) 上有唯一约束以防止重复条目
- 外键关系采用 CASCADE 删除
- 在 `knowledge_id`、`file_id` 和 `user_id` 上有索引以提升性能
- `directory_id` 由迁移 `3c9b0ca343fd` 添加，并带有索引 `ix_knowledge_file_directory_id`。这是此处唯一不级联的外键：删除目录会把其文件上的 `directory_id` 置回 null，而不是删除这些文件；`directory_id` 为 null 表示文件位于其知识库的根目录

模型、知识库、工具、提示词、笔记、文件、频道等资源的访问控制通过 `access_grant` 表管理，而不是嵌入在 JSON 中。每条授权记录指定一个资源、一个主体（用户或用户组）和一个权限级别（读或写）。详情请参阅上方的[访问授权表](#access-grant-table)一节。
## Memory 表 {#memory-table}

| **列名** | **数据类型** | **约束** | **描述** |
| --------------- | ------------- | -------------------------- | ------------------------ |
| id | String | PRIMARY KEY | 唯一标识符 (UUID) |
| user_id | String | indexed | 记忆所有者 |
| type | String | default `context`, indexed | 记忆类型：`user` 或 `context` |
| path | Text | nullable | 可选路径，用于将记忆组织成层级结构 |
| content | Text | - | 记忆内容 |
| meta | JSON | nullable | 可选元数据 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

关于 memory 表的注意事项：

- `type` 用于区分 `user` 记忆（用户明确整理的事实）和 `context` 记忆（从对话中学到的）；该列已建立索引以支持按类型查询。由迁移 `7b3f2a9c1d4e` 添加（其后还跟有一个索引修复迁移）。
- `path` 和 `meta` 为扩展后的内置记忆工具提供支持，让模型可以按路径组织记忆并附加结构化元数据。
- 迁移 `55f1302ac17c` 添加了 `(id, user_id)` 上的覆盖索引，以加快按用户查找记忆的速度。
## Message 表 {#message-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ----------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| user_id | Text | - | 消息作者 |
| app_id | Text | nullable | 发布该消息的 App |
| channel_id | Text | nullable | 关联频道 |
| reply_to_id | Text | nullable | 该消息在回复中引用的消息 |
| parent_id | Text | nullable | 会话串的父消息 |
| is_pinned | Boolean | NOT NULL, server_default=false | 该消息在其频道中是否被置顶 |
| pinned_at | BigInteger | nullable | 置顶时间戳（纳秒） |
| pinned_by | Text | nullable | 置顶该消息的用户 |
| content | Text | - | 消息内容 |
| data | JSON | nullable | 额外的消息数据 |
| meta | JSON | nullable | 消息元数据 |
| created_at | BigInteger | - | 创建时间戳（纳秒） |
| updated_at | BigInteger | - | 最后更新时间戳（纳秒） |

关于 message 表的注意事项：

- `parent_id` 由迁移 `3781e22d8b01` 添加，`reply_to_id` 由迁移 `a5c220713937` 添加。`is_pinned`、`pinned_at` 和 `pinned_by` 由迁移 `2f1211949ecc` 添加。
- 在 (`channel_id`, `parent_id`, `created_at`) 以及 `parent_id`（`ix_message_channel_parent_created`、`ix_message_parent_id`，迁移 `9f6c2a8d1b43`）上建有索引，用于加载频道消息列表和线程。
- `parent_id` 和 `reply_to_id` 承担不同的职责。`parent_id` 是线程根：频道的消息列表会选出 `parent_id` 为 null 的行，而线程则通过选出 `parent_id` 等于根消息的行来读取。`reply_to_id` 指向回复所引用的那一条消息，该消息会在消息被返回时取出并附加。它不影响消息出现在哪个列表中。
- `is_pinned`、`pinned_at` 和 `pinned_by` 由 `POST /api/v1/channels/{id}/messages/{message_id}/pin` 一并写入。取消置顶会把 `pinned_at` 和 `pinned_by` 清回 null。`GET /api/v1/channels/{id}/messages/pinned` 负责读取它们。
- `app_id` 由迁移 `c92da83b017f` 添加。由 App 发布的消息会带上其 `app_id` 且 `user_id` 为 null，并在 `data` 的 `app` 下（`actions` 和 `embeds`）保留其按钮和卡片。
- `meta` 通过 `webhook` 键保存通过[频道 webhook](#channel-webhook-table)发布消息时的 webhook 身份，正是它让这些消息以 webhook 的名称和图片渲染。模型的回复在其中带有模型 ID 和名称，并在回复完成后带上 `done`。自动化发布的两类消息都带有其 `automation_id`。`meta` 由 Open WebUI 自行写入，在发布或编辑消息的请求中随附的 `meta` 会被忽略。
## Message Reaction 表 {#message-reaction-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ------------------------ |
| id | Text | PRIMARY KEY, UNIQUE | 唯一标识符（UUID） |
| user_id | Text | NOT NULL | 做出反应的用户 |
| message_id | Text | NOT NULL | 关联消息 |
| name | Text | NOT NULL | 反应名称/表情符号 |
| created_at | BigInteger | nullable | 回应时间戳 |

关于 message_reaction 表的注意事项：

- `user_id`、`message_id` 和 `name` 在数据库中是 NOT NULL（迁移 `3781e22d8b01`），而 SQLAlchemy 模型声明它们时未带该标志。以数据库约束为准。
- 在 `message_id` 上有索引（`ix_message_reaction_message_id`，迁移 `9f6c2a8d1b43`）。
## Model 表 {#model-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ---------------------- |
| id | Text | PRIMARY KEY | 模型标识符 |
| user_id | Text | - | 模型所有者 |
| base_model_id | Text | nullable | 父模型引用 |
| name | Text | - | 显示名称 |
| params | JSON | - | 模型参数 |
| meta | JSON | - | 模型元数据 |
| version_id | Text | nullable | 生产版本（`model_history.id`） |
| is_active | Boolean | default=True | 启用状态 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

| is_active       | Boolean       | default=True    | 激活状态|
| created_at      | BigInteger    | -               | 创建时间戳|
| updated_at      | BigInteger    | -               | 最后更新时间戳|

## Model History 表 {#model-history-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | -------------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| model_id | Text | NOT NULL, INDEX | 该版本所属的模型 |
| parent_id | Text | nullable | 保存此版本时所基于的版本 |
| snapshot | JSON | NOT NULL | 保存的名称、基础模型、参数和元数据 |
| user_id | Text | NOT NULL | 保存该版本的用户 |
| commit_message | Text | nullable | 保存时填写的描述 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |

关于 model history 表的注意事项：

- 快照保存 `name`、`base_model_id`、`params` 和 `meta`。隐藏标志、启用开关和访问授权仍保留在实时模型上。
- 迁移 `e7b9d4a023bc` 创建了该表，并为每个已有模型提供了一个起始版本。

## Note 表 {#note-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | -------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 |
| user_id | Text | nullable | 笔记的所有者 |
| title | Text | nullable | 笔记标题 |
| data | JSON | nullable | 笔记内容与数据 |
| meta | JSON | nullable | 笔记元数据 |
| created_at | BigInteger | nullable | 创建时间戳 |
| updated_at | BigInteger | nullable | 最后更新时间戳 |

笔记正文位于 `data` 的 `content.md` 下，是 Markdown 文本。如果某行在该位置存放的是对象或数组（模型向笔记工具传入结构化数据时可能产生这种情况），那么返回该内容时会将其渲染为围栏 `json` 代码块，并且在下一次保存该笔记时该行会被重写为与之匹配。

置顶状态不再存储在该表中。旧版的 `is_pinned` 列已在迁移 `4de81c2a3af1` 中移除，改为按用户存储的[置顶笔记表](#pinned-note-table)。此前已有的置顶会回填到笔记所有者；API 以针对调用用户行的按请求联接形式提供 `is_pinned`。
## Pinned Note 表 {#pinned-note-table}

每位用户的笔记置顶记录。每一行表示某个用户为侧边栏置顶了某条笔记——置顶是私有的，不会影响能够访问同一笔记的其他用户。

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ---------------------------------------------------- | ------------------------------------------------ |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| user_id | Text | NOT NULL | 置顶笔记的用户 |
| note_id | Text | NOT NULL, FOREIGN KEY(note.id) ON DELETE CASCADE | 被置顶的笔记 |
| created_at | BigInteger | NOT NULL | 置顶创建时间戳（用于排序） |

`UNIQUE(user_id, note_id)` 约束用于防止同一用户/笔记对的重复置顶。置顶笔记列表按每个用户的 `created_at DESC` 排序，因此最近置顶的笔记排在最前面。删除笔记时会级联清理本表；但切换置顶状态**不会**修改 `note.updated_at`。

## Notification 表 {#notification-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ----------------------------------------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| user_id | Text | NOT NULL | 接收者 |
| event_type | Text | NOT NULL | 通知的种类，例如 `comment.replied`、`channel.mentioned`、`calendar.alert`、`automation.run_failed` 或 `system.announcement` |
| event_key | Text | NOT NULL | 引发该通知的事件的标识 |
| actor_type | Text | NOT NULL | `user` 或 `system` |
| actor_id | Text | nullable | 引发通知的用户；`system` 时为空 |
| resource_type | Text | nullable | 其所属条目的类型 |
| resource_id | Text | nullable | 该条目的 ID |
| object_type | Text | nullable | 具体对象的类型，例如 `comment` |
| object_id | Text | nullable | 该对象的 ID |
| data | JSON | NOT NULL | 在收件箱中显示的事件详情 |
| seen_at | BigInteger | nullable | 用户在收件箱中看到它的时间（纳秒） |
| read_at | BigInteger | nullable | 用户阅读它的时间（纳秒） |
| created_at | BigInteger | NOT NULL | 创建时间戳（纳秒） |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳（纳秒） |

关于 notification 表的注意事项：

- 在 (`user_id`, `event_key`) 上有唯一约束，因此同一事件只会通知用户一次。
- `resource_type` 与 `resource_id` 要么都设置，要么都为空；`object_type` 与 `object_id` 同理。
- 只有在通知设置开启时才会创建行。
- 在 (`user_id`, `created_at`, `id`) 上建有索引，对未读行使用相同列另建索引，并在 (`resource_type`, `resource_id`) 和 (`object_type`, `object_id`) 上建有索引。

## OAuth Session 表 {#oauth-session-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | -------------------- | --------------------------------- |
| id | Text | PRIMARY KEY, UNIQUE | 唯一会话标识符 |
| user_id | Text | FOREIGN KEY(user.id) CASCADE, NOT NULL | 关联的用户 |
| provider | Text | NOT NULL | OAuth 提供商（例如：'google'） |
| token | Text | NOT NULL | OAuth 会话令牌 |
| expires_at | BigInteger | NOT NULL | 令牌到期时间戳 |
| created_at | BigInteger | NOT NULL | 会话创建时间戳 |
| updated_at | BigInteger | NOT NULL | 会话最后更新时间戳 |

关于 oauth_session 表的注意事项：

- 与 `user` 的关系是一对多。每次登录都会插入新行，因此同一用户、同一提供方可以存在多行。`OAUTH_MAX_SESSIONS_PER_USER`（默认 10）限制用户每个提供方可持有的会话数量；登录时会删除超出上限的最旧行。
- 在 `user_id`、`expires_at` 以及 (`user_id`, `provider`) 上有索引（`idx_oauth_session_user_id`、`idx_oauth_session_expires_at`、`idx_oauth_session_user_provider`，均来自迁移 `38d63c18f30f`）。
- 删除用户会级联删除其会话。
- `token` 以 JSON 保存提供方的令牌集合（访问令牌、ID 令牌和刷新令牌），写入前用 Fernet 静态加密，读取时解密。密钥来自 `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY`，回退到 `WEBUI_SECRET_KEY`。长度不是 44 个字符的密钥会先用 SHA-256 哈希再进行 base64 编码，以满足 Fernet 要求的长度。
## Prompt 表 {#prompt-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ----------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| command | String | UNIQUE, INDEX | 唯一命令标识符 |
| user_id | String | NOT NULL | 提示词的所有者 |
| name | Text | NOT NULL | 提示词的显示名称 |
| content | Text | NOT NULL | 提示词内容/模板 |
| data | JSON | nullable | 额外的提示词数据 |
| meta | JSON | nullable | 提示词元数据 |
| is_active | Boolean | default=True | 启用状态 |
| version_id | Text | nullable | 当前版本标识符 |
| tags | JSON | nullable | 关联的标签 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

| is_active       | Boolean       | default=True    | 激活状态|
| version_id      | Text          | nullable        | 当前版本标识符          |
| tags            | JSON          | nullable        | 关联标签                     |
| created_at      | BigInteger    | NOT NULL        | 创建时间戳|
| updated_at      | BigInteger    | NOT NULL        | 最后更新时间戳|

## Prompt History 表 {#prompt-history-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | ------------------------------ | --------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符（UUID） |
| prompt_id | Text | FOREIGN KEY(prompt.id), INDEX | 引用该提示词 |
| parent_id | Text | nullable | 引用父版本 |
| snapshot | JSON | NOT NULL | 提示词版本快照 |
| user_id | Text | NOT NULL | 创建该版本的用户 |
| commit_message | Text | nullable | 版本提交信息 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |

## Skill 表 {#skill-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ---------------------------------- |
| id | String | PRIMARY KEY | 唯一标识符（UUID） |
| user_id | String | - | 技能的所有者/创建者 |
| name | Text | NOT NULL | 技能的显示名称 |
| description | Text | nullable | 简短描述（在清单中使用） |
| content | Text | NOT NULL | 完整 Skill 说明 (Markdown) |
| data | JSON | nullable | 技能文件：`SKILL.md` 及其辅助文件 |
| version_id | Text | nullable | 生产版本（`skill_history.id`） |
| meta | JSON | nullable | 技能元数据 |
| is_active | Boolean | default=True | 激活状态 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |
| updated_at | BigInteger | NOT NULL | 最后更新时间戳 |

关于 skill 表的注意事项：

- 使用 UUID 作为主键
- 访问控制通过 `access_grant` 表（resource_type 为 `skill`）管理
- `description` 会列在隐藏的 `list_available_skills` 结果中；`content` 通过 `view_skill` 内置工具按需加载
- `data` 和 `version_id` 由迁移 `d6a8c3f912ab` 添加，该迁移还会为每个已有的 skill 填充一条 `skill_history` 版本
## Skill History 表 {#skill-history-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | -------------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| skill_id | Text | NOT NULL, INDEX | 该版本所属的技能 |
| parent_id | Text | nullable | 保存此版本时所基于的版本 |
| snapshot | JSON | NOT NULL | 保存的技能内容及其文件 |
| user_id | Text | NOT NULL | 保存该版本的用户 |
| commit_message | Text | nullable | 保存时填写的描述 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |

关于 skill history 表的注意事项：

- 快照保存技能内容及其关联文件。
- 迁移 `e7b9d4a023bc` 创建了该表，并为每个已有技能提供了一个起始版本。

## Tag 表 {#tag-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | ------------------------- |
| id | String | PK (composite) | 规范化的标签标识符 |
| name | String | - | 显示名称 |
| user_id | String | PK (composite) | 标签所有者 |
| meta | JSON | nullable | 标签元数据 |

关于 tag 表需要知道的事项：

- 主键是复合主键（id, user_id）

## Tool 表 {#tool-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | --------------------- |
| id | String | PRIMARY KEY | 唯一标识符 |
| user_id | String | - | 工具所有者 |
| name | Text | - | 工具名称 |
| content | Text | - | 工具内容/代码 |
| specs | JSON | - | 工具规范 |
| meta | JSON | - | 工具元数据 |
| valves | JSON | - | 工具控制设置 |
| version_id | Text | nullable | 生产版本（`tool_history.id`） |
| is_active | Boolean | NOT NULL, default=True | 该工具是否已启用 |
| created_at | BigInteger | - | 创建时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |

| created_at      | BigInteger    | -               | 创建时间戳|
| updated_at      | BigInteger    | -               | 最后更新时间戳|

## Tool History 表 {#tool-history-table}

| **列名** | **数据类型** | **约束** | **说明** |
| --------------- | ------------- | --------------- | -------------------------------------- |
| id | Text | PRIMARY KEY | 唯一标识符 (UUID) |
| tool_id | Text | NOT NULL, INDEX | 该版本所属的工具 |
| parent_id | Text | nullable | 保存此版本时所基于的版本 |
| snapshot | JSON | NOT NULL | 保存的名称、源代码和元数据 |
| user_id | Text | NOT NULL | 保存该版本的用户 |
| commit_message | Text | nullable | 保存时填写的描述 |
| created_at | BigInteger | NOT NULL | 创建时间戳 |

关于 tool history 表的注意事项：

- 快照保存 `name`、源代码，以及 `meta` 中的描述和翻译。Valves 和访问授权仍保留在 `tool` 行上。
- 迁移 `f8c0e5b134cd` 创建了该表，并为每个已有工具提供了一个起始版本。
## User 表 {#user-table}

| **列名** | **数据类型** | **约束** | **说明** |
| ----------------- | ------------- | ---------------- | -------------------------- |
| id | String | PRIMARY KEY | 唯一标识符 |
| username | String(50) | nullable | 用户的唯一用户名 |
| name | String | NOT NULL | 用户姓名 |
| email | String | - | 用户邮箱 |
| role | String | default='pending' | 用户角色 |
| profile_image_url | Text | - | 头像路径 |
| profile_banner_image_url | Text | nullable | 个人资料横幅图片路径 |
| bio | Text | nullable | 用户简介 |
| gender | Text | nullable | 用户性别 |
| date_of_birth | Date | nullable | 用户出生日期 |
| timezone | String | nullable | IANA 时区名称 |
| presence_state | String | nullable | 在线状态 |
| status_emoji | String | nullable | 随状态显示的表情 |
| status_message | Text | nullable | 状态文本 |
| status_expires_at | BigInteger | nullable | 状态过期时间戳 |
| last_active_at | BigInteger | - | 最近活动时间戳 |
| updated_at | BigInteger | - | 最后更新时间戳 |
| created_at | BigInteger | - | 创建时间戳 |
| settings | JSON | nullable | 用户首选项 |
| info | JSON | nullable | 额外的用户信息 |
| variables | JSON | nullable | 会被替换进系统提示词的用户变量 |
| oauth | JSON | nullable | 身份提供方的用户标识，按提供方键控 |
| scim | JSON | nullable | SCIM 配置数据 |

关于 user 表的注意事项：

- 使用 UUID 作为主键
- 与 `auth` 表是一对一关系（共享 id）
- 与 `oauth_session` 表是一对多关系（通过 `user_id` 外键），每次登录一行
- `email` 不区分大小写且唯一，由 `lower(email)` 上（`email` 不为 null 时）的部分唯一索引 `uq_user_email_lower` 保证（迁移 `f0bd01a18a3d`）。升级到已存在两个仅大小写不同的账户的数据库时，升级会中止并列出这两个账户，而不是替您二选一；参见[重复邮箱](/troubleshooting/manual-database-migration#duplicate-emails-migration-failure)。
- 数据库中的 `email` 列没有普通的 `UNIQUE` 约束，因此上表才没有显示它。SQLAlchemy 模型在其上声明了 `unique=True`，但 schema 仅由迁移构建，而没有任何迁移创建该约束，因此上面的索引就是全部的约束手段。
- `variables` 由迁移 `b0018471bbbe` 添加。它以字符串键到字符串值的扁平映射保存用户自己的[用户变量](/features/chat-conversations/chat-features/chat-params#user-variables)，并在请求时替换进系统提示词。它不会出现在用户 API 响应中，而是通过自己的端点读取。
- `oauth` 取代了单个 `oauth_sub` 文本列（迁移 `b10670c03dd5`），因此一个账户可以同时持有多个身份提供方的用户标识。它存储 `{"<provider>": {"sub": "<subject>"}}`。跨越大段时间间隔升级的数据库可能把该值写成文本而非对象，从而导致相关账户无法登录；迁移 `6d09d1bf1f23` 会在启动时重写这些行，而不动其他任何行。参见[长时间延迟升级后已有账户无法登录](/troubleshooting/sso#12-existing-accounts-cannot-sign-in-after-a-long-delayed-upgrade)。
- API 密钥是[API Key 表](#api-key-table)中的行。
- `timezone` 保存 IANA 时区名称（例如 `Europe/Vienna`），由 `POST /api/v1/auths/update/timezone` 写入。日历重复规则展开、自动化调度和按用户的使用统计都会读取它。未设置或无法识别的值，对日历和自动化回退到服务器时区，对使用统计回退到 UTC。
- `status_emoji`、`status_message` 和 `status_expires_at` 保存用户为自己设置的状态。它们通过 `POST /api/v1/users/user/status/update` 写入，除非 `users.enable_status` 配置键已开启，否则该请求会被拒绝；它们会随登录响应以及频道成员列表一起返回。
- `presence_state` 会在频道成员列表和 socket 会话载荷中返回。没有任何代码路径会写入它。

`scim` 字段的预期结构：

```python
{
    "<provider>": {
        "external_id": string,  # externalId from the identity provider
    },
    # Multiple providers can be stored simultaneously
    # Example:
    # "microsoft": { "external_id": "abc-123" },
    # "okta": { "external_id": "def-456" }
}
```

**添加该列的原因：**

- **SCIM 账户关联**：存储来自 SCIM 预配的各提供方 `externalId` 值，使身份提供方（如 Azure AD、Okta）能够依据其外部标识符匹配用户，而不只依赖邮箱。
- **多提供方支持**：按提供方分键的结构允许单个用户同时从多个身份提供方预配，各自带自己的 `externalId`。
- **OAuth 回退**：按 `externalId` 查找用户时，如果找不到 `scim` 条目，系统会回退为将其与同一提供方在 `oauth` 字段中存储的用户标识匹配，从而实现 SCIM 预配账户与 OAuth 认证账户之间的无缝关联。
## 实体关系图 (ERD) {#entity-relationship-diagram}

为帮助可视化表之间的关系，请参考下面使用 Mermaid 生成的实体关系图（ERD）。

``` mermaid
erDiagram
    %% User and Authentication
    user ||--o{ auth : "has"
    user ||--o{ chat : "owns"
    user ||--o{ shared_chat : "shares"
    user ||--o{ calendar : "owns"
    user ||--o{ calendar_event : "creates"
    user ||--o{ channel : "owns"
    user ||--o{ message : "creates"
    user ||--o{ folder : "owns"
    user ||--o{ file : "owns"
    user ||--o{ feedback : "provides"
    user ||--o{ function : "manages"
    user ||--o{ group : "manages"
    user ||--o{ knowledge : "manages"
    user ||--o{ memory : "owns"
    user ||--o{ model : "manages"
    user ||--o{ prompt : "creates"
    user ||--o{ prompt_history : "creates"
    prompt ||--o{ prompt_history : "has"
    user ||--o{ tag : "creates"
    user ||--o{ skill : "manages"
    skill ||--o{ skill_history : "has"
    user ||--o{ tool : "manages"
    model ||--o{ model_history : "has"
    tool ||--o{ tool_history : "has"
    function ||--o{ function_history : "has"
    user ||--o{ note : "owns"
    user ||--o{ pinned_note : "pins"
    note ||--o{ pinned_note : "pinned_by"
    user ||--o{ oauth_session : "has"
    user ||--o{ auth_session : "signs_in"
    user ||--o{ api_key : "holds"
    user ||--o{ comment : "writes"
    comment ||--o{ comment_reaction : "has"
    user ||--o{ notification : "receives"

    %% Content Relationships
    message ||--o{ message_reaction : "has"
    chat ||--o{ tag : "tagged_with"
    chat ||--o{ chat_message : "contains"
    chat ||--o{ shared_chat : "shared_via"
    chat ||--o{ chat_view_state : "viewed_as"
    user ||--o{ chat_view_state : "saves"
    chat }|--|| folder : "organized_in"
    calendar ||--o{ calendar_event : "contains"
    calendar_event ||--o{ calendar_event_attendee : "has"
    channel ||--o{ message : "contains"
    channel ||--o{ channel_member : "has"
    channel ||--o{ channel_webhook : "has"
    user ||--o{ channel_member : "joins"
    message ||--o{ message : "replies"
    knowledge ||--o{ knowledge_directory : "contains"
    knowledge_directory ||--o{ knowledge_directory : "nests"
    knowledge_directory ||--o{ knowledge_file : "holds"

    user {
        string id PK
        string username
        string name
        string email
        string role
        text profile_image_url
        text profile_banner_image_url
        text bio
        text gender
        date date_of_birth
        string timezone
        string presence_state
        string status_emoji
        text status_message
        bigint status_expires_at
        bigint last_active_at
        json settings
        json info
        json variables
        json oauth
        json scim
    }

    auth {
        string id PK
        string email
        text password
        boolean active
    }

    chat {
        string id PK
        string user_id FK
        string title
        json chat
        text share_id
        boolean archived
        boolean pinned
        json meta
        text folder_id FK
        bigint timer_at
    }

    shared_chat {
        text id PK
        text chat_id FK
        text user_id FK
        text title
        json chat
        bigint created_at
        bigint updated_at
    }

    chat_message {
        text id PK
        text chat_id FK
        text user_id FK
        text role
        text parent_id FK
        json content
        json output
        text model_id
        json files
        json sources
        boolean done
        json usage
        text context_summary
    }

    chat_view_state {
        text user_id PK
        text chat_id PK
        json state
        bigint updated_at
    }

    calendar {
        text id PK
        text user_id FK
        text name
        text color
        boolean is_default
        json data
        json meta
    }

    calendar_event {
        text id PK
        text calendar_id FK
        text user_id FK
        text title
        text description
        bigint start_at
        bigint end_at
        boolean all_day
        text rrule
        text color
        text location
        json data
        json meta
        boolean is_cancelled
    }

    calendar_event_attendee {
        text id PK
        text event_id FK
        text user_id FK
        text status
        json meta
    }

    channel {
        text id PK
        text user_id FK
        text type
        text name
        text description
        boolean is_private
        json data
        json meta
        text updated_by
        bigint archived_at
        text archived_by
        bigint deleted_at
        text deleted_by
    }

    channel_member {
        text id PK
        text channel_id FK
        text user_id FK
        text role
        text status
        boolean is_active
        boolean is_channel_muted
        boolean is_channel_pinned
        json data
        json meta
        bigint invited_at
        text invited_by
        bigint joined_at
        bigint left_at
        bigint last_read_at
    }

    channel_webhook {
        text id PK
        text channel_id FK
        text user_id FK
        text name
        text profile_image_url
        text token
        bigint last_used_at
    }

    message {
        text id PK
        text user_id FK
        text channel_id FK
        text reply_to_id FK
        text parent_id FK
        boolean is_pinned
        bigint pinned_at
        text pinned_by
        text content
        json data
        json meta
    }

    message_reaction {
        text id PK
        text user_id FK
        text message_id FK
        text name
    }

    feedback {
        text id PK
        text user_id FK
        bigint version
        text type
        json data
        json meta
        json snapshot
    }

    file {
        string id PK
        string user_id FK
        text hash
        text filename
        text path
        json data
        json meta
    }

    folder {
        text id PK "composite"
        text user_id PK "composite"
        text parent_id FK
        text name
        json items
        json data
        json meta
        boolean is_expanded
    }

    function {
        string id PK
        string user_id FK
        text name
        text content
        json meta
        json valves
        boolean is_active
        boolean is_global
        text version_id
    }

    function_history {
        text id PK
        text function_id FK
        text parent_id FK
        json snapshot
        text user_id FK
        text commit_message
    }

    group {
        text id PK
        text user_id FK
        text name
        text description
        json data
        json meta
        json permissions
    }

    knowledge {
        text id PK
        text user_id FK
        text name
        text description
        json data
        json meta
    }

    knowledge_directory {
        text id PK
        text knowledge_id FK
        text parent_id FK
        text name
        text user_id FK
        bigint created_at
        bigint updated_at
    }

    knowledge_file {
        text id PK
        text knowledge_id FK
        text file_id FK
        text directory_id FK
        text user_id FK
        bigint created_at
        bigint updated_at
    }

    memory {
        string id PK
        string user_id FK
        string type
        text path
        text content
        json meta
    }

    model {
        text id PK
        text user_id FK
        text base_model_id FK
        text name
        json params
        json meta
        text version_id
        boolean is_active
    }

    model_history {
        text id PK
        text model_id FK
        text parent_id FK
        json snapshot
        text user_id FK
        text commit_message
    }

    note {
        text id PK
        text user_id FK
        text title
        json data
        json meta
    }

    pinned_note {
        text id PK
        text user_id FK
        text note_id FK
        bigint created_at
    }

    oauth_session {
        text id PK
        text user_id FK
        text provider
        text token
        bigint expires_at
    }

    auth_session {
        text id PK
        text user_id
        text refresh_token_id
        json data
        bigint created_at
        bigint updated_at
        bigint expires_at
    }

    comment {
        text id PK
        text user_id FK
        text resource_type
        text resource_id
        text parent_id FK
        text reply_to_id FK
        text content
        text target_type
        text target_id
        json meta
        bigint created_at
        bigint updated_at
        bigint deleted_at
    }

    comment_reaction {
        text id PK
        text user_id FK
        text comment_id FK
        text name
        bigint created_at
    }

    notification {
        text id PK
        text user_id FK
        text event_type
        text event_key
        text actor_type
        text actor_id FK
        text resource_type
        text resource_id
        text object_type
        text object_id
        json data
        bigint seen_at
        bigint read_at
        bigint created_at
        bigint updated_at
    }

    api_key {
        text id PK
        text user_id FK
        text key
        json data
        bigint expires_at
        bigint last_used_at
    }

    prompt {
        text id PK
        string command
        string user_id FK
        text name
        text content
        json data
        json meta
        boolean is_active
        text version_id
        json tags
    }

    prompt_history {
        text id PK
        text prompt_id FK
        text parent_id FK
        json snapshot
        text user_id FK
        text commit_message
    }

    tag {
        string id PK "composite"
        string user_id PK "composite"
        string name
        json meta
    }

    skill {
        text id PK
        text user_id FK
        text name
        text description
        text content
        json data
        json meta
        boolean is_active
        text version_id
    }

    skill_history {
        text id PK
        text skill_id FK
        text parent_id FK
        json snapshot
        text user_id FK
        text commit_message
    }

    tool {
        string id PK
        string user_id FK
        text name
        text content
        json specs
        json meta
        json valves
        text version_id
        boolean is_active
    }

    tool_history {
        text id PK
        text tool_id FK
        text parent_id FK
        json snapshot
        text user_id FK
        text commit_message
    }
```

---

## 使用 SQLCipher 加密数据库 {#database-encryption-with-sqlcipher}
:::danger 不受支持

不支持 SQLCipher。异步数据库层没有 SQLCipher 驱动，因此当设置 `DATABASE_TYPE=sqlite+sqlcipher` 或 `sqlite+sqlcipher://` URL 时，Open WebUI 会拒绝启动。

:::

若需要静态加密，请将数据目录放在加密文件系统上（Linux 上的 LUKS、Windows 上的 BitLocker、macOS 上的 FileVault），或使用带加密存储的 PostgreSQL。

### 升级现有的 SQLCipher 数据库 {#upgrading-an-existing-sqlcipher-database}
在启动 Open WebUI 之前，请先用 `sqlcipher` CLI 将数据库解密为普通的 SQLite 文件：

```sql
-- run inside: sqlcipher webui.db
PRAGMA key = 'your-secure-password';
ATTACH DATABASE 'webui-plain.db' AS plaintext KEY '';
SELECT sqlcipher_export('plaintext');
DETACH DATABASE plaintext;
```

用 `webui-plain.db` 替换 `webui.db`，然后设置 `DATABASE_TYPE=sqlite`（或不设置 `DATABASE_TYPE`），并移除 `DATABASE_PASSWORD`。

### 相关的数据库环境变量 {#related-database-environment-variables}
| 变量 | 默认值 | 说明 |
|----------|---------|------------|
| `DATABASE_ENABLE_SQLITE_WAL` | `False` | 启用预写式日志（WAL）以获得更好的性能 |
| `DATABASE_SQLITE_PRAGMA_SYNCHRONOUS` | `NORMAL` | SQLite 同步模式（与 WAL 结合安全，避免每个事务执行 fsync） |
| `DATABASE_SQLITE_PRAGMA_BUSY_TIMEOUT` | `5000` | 写锁等待时间（毫秒） |
| `DATABASE_SQLITE_PRAGMA_CACHE_SIZE` | `-65536` | 页面缓存大小（负数 = KiB；≈ 64 MB） |
| `DATABASE_SQLITE_PRAGMA_TEMP_STORE` | `MEMORY` | 临时表存储（`MEMORY` 将临时表保存在 RAM 中） |
| `DATABASE_SQLITE_PRAGMA_MMAP_SIZE` | `268435456` | 内存映射 I/O 大小（以字节为单位，≈ 256 MB） |
| `DATABASE_SQLITE_PRAGMA_JOURNAL_SIZE_LIMIT` | `67108864` | 检查点之后 WAL 文件的最大大小（≈ 64 MB） |
| `DATABASE_POOL_SIZE` | `None` | 数据库连接池大小 |
| `DATABASE_POOL_TIMEOUT` | `30` | 连接池连接超时时间（秒） |
| `DATABASE_POOL_RECYCLE` | `3600` | 连接池连接回收时间（秒） |

更多细节请参阅[环境变量配置](/reference/env-configuration)文档。
