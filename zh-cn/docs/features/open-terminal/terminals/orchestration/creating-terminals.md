---
sidebar_position: 1
title: "创建终端"
---

# 创建终端 {#creating-terminals}

**终端**是预先配置好的工作区，AI 可在其中运行命令和处理文件。你可以从聊天中创建终端，为其命名并决定谁可以使用。每个终端会启动一个或多个**实例**，即实际运行命令的容器。

如果 AI 需要在实际的计算环境中运行代码、编辑文件或构建项目，并且每个人或聊天都需要一个独立、干净的工作区，可以使用终端。一个终端可通过群组供整个团队使用，也可让每个用户、聊天或模型拥有独立实例，使文件彼此隔离。只需配置一次镜像、资源、启动目录和初始化脚本，所有实例就会以相同方式启动。

管理员将 Terminals 服务器添加为连接，并授予用户 **Write** 权限。拥有 **Write** 权限的用户可以创建和管理终端。其他人只能使用共享给他们的终端。

## 连接访问权限 {#connection-access}

按照[连接到 Open WebUI](/features/open-terminal/setup/connecting)和[身份验证](/features/open-terminal/terminals#authentication)一节中的说明，在 **Settings > Integrations**（管理员区域）添加连接。连接表单提供 Name、ID、URL、API Key、Auth、**Verify Connection**、Chat Uploads、**Access** 和 **Advanced** 选项。终端从聊天中创建。

连接的 **Access** 有两种权限：

| 权限 | 用户可以执行的操作 |
| :--- | :--- |
| **Read** | 查看和使用共享给自己的终端 |
| **Write** | 创建和管理此服务器上的终端，并查看服务器上的所有终端 |

## 新建终端 {#create-a-terminal}

1. 打开消息输入框中的终端菜单（云图标）。拥有 **Write** 权限时，即使还没有终端，也会显示此菜单。
2. 在 **Terminals** 下点击 **New terminal**。
3. 填写对话框并点击 **Create**。

| 字段 | 用途 |
| :--- | :--- |
| **Name** | 终端菜单中显示的名称 |
| **Server** | 运行该终端的 Terminals 连接。只有在创建终端且存在多个可用的 Terminals 连接时才显示 |
| **Separate instances** | 开关。开启后，通过旁边的下拉菜单选择 **User**、**Chat** 或 **Model**，初始值为 **User**。关闭时，所有拥有访问权限的人共用一个实例。参见[实例范围](#machine-scope)。存在实例时此设置会锁定，须删除所有实例才能更改 |
| **Start directory** | 位于 **Advanced** 下，指定命令开始运行的文件夹。该文件夹须位于主目录内，否则命令会在主目录中启动。保存为 `OPEN_TERMINAL_START_DIR` |
| **Setup script** | 位于 **Advanced** 下。每次启动实例时，系统都会在启动目录中运行此 Shell 脚本，运行完毕后实例才可用。重启时只保留主目录，因此脚本应能安全地重复运行。保存为 `OPEN_TERMINAL_SETUP_SCRIPT`。**System info** 会显示进度和失败信息，包括退出码及日志的末尾内容 |
| **Advanced** | 包含 **Start directory**、**Setup script**、**Image**、**CPU**、**Memory**、**Storage**、**Network** 和 **Environment variables**。留空时使用服务器默认值。填写的值会按服务器上限核验 |

新建的终端为私有。创建后，从终端菜单打开 **Terminal settings**，点击对话框顶部的 **Private** 按钮进入 **Access**，即可与选定的用户和群组共享终端。共享权限只允许使用终端。

:::warning 写入权限可访问他人的实例
拥有 Terminals 连接 **Write** 权限的用户可以打开该连接上任意运行中实例的 **System info**，并完全访问其实例文件。仅将 **Write** 权限授予你信任的用户，因为他们能够访问每个人的工作区。
:::

原始值与保留键见[环境变量](/features/open-terminal/terminals/orchestration/environment-variables)，**Image** 字段见[自定义镜像](/features/open-terminal/terminals/orchestration/custom-images)。

拥有终端访问权限的人都可以在其中运行命令。关闭 **Separate instances** 时，所有拥有权限的人共用一个实例。选择 **Model** 时，使用同一模型的人共用一个实例。这些人都能看到实例中的文件，因此请只与有权查看这些文件的人共享此类终端。

## 实例范围 {#machine-scope}

| Separate instances | 结果 |
| :--- | :--- |
| 关闭 | 所有使用此终端的人共用一个实例 |
| 开启，**User** | 每个用户拥有独立实例 |
| 开启，**Chat** | 每个已保存的聊天拥有独立实例和文件 |
| 开启，**Model** | 每个模型拥有独立实例 |

- **Chat** 终端需要已保存的聊天。发送第一条消息后，终端可在保存的聊天中使用。
- **Model** 终端需要对应模型的访问权限。
- 对通过 **Allow replies** 共享的聊天，有权回复的人使用该聊天自己的终端。
- 向频道发布消息的自动化无法使用 **Chat** 终端。

**Chat** 和 **User** 会增加同时运行的实例数。可请管理员设置空闲超时，以清理已不再使用的聊天实例。参见[空闲清理、最长运行时间和计划重置](/features/open-terminal/terminals/orchestration#idle-cleanup-lifetime-and-scheduled-resets)。

## 管理实例 {#manage-machines}

对话框中的 **Instances** 列表显示此终端的所有实例，以及它们的名称和运行或停止状态。打开某行的 **More options** 菜单可对该实例执行操作。正在运行的实例提供 **Restart**、**Stop**、**System info** 和 **View files**。已停止的实例提供 **Start**。所有实例都提供 **Delete instance**。执行操作时，该行会显示旋转指示器及当前状态（**Restarting...**、**Stopping...**、**Starting...** 或 **Deleting...**）。**Delete terminal** 会移除终端及其实例和文件。

## 终端菜单 {#terminal-menu}

菜单中的每个终端都有一个 **More** 菜单。实例运行时提供 **Restart** 和 **Stop**，停止时提供 **Start**。实例运行时还会显示 **System info** 和 **View files**。**Terminal settings** 始终可用。**View files** 可打开该终端的[文件浏览器](/features/open-terminal/file-browser)，无需在聊天中选择该终端。**System info** 显示 CPU、内存、磁盘和网络用量、运行时长以及资源占用最高的进程，在打开期间每 5 秒刷新一次。

## 聊天 {#chats}

每个聊天都会保存所选终端和工作文件夹，并在重新打开时恢复。保存时没有选择终端的聊天，再次打开时也不会选择终端。
