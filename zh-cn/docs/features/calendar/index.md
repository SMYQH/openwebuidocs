---
sidebar_position: 2
title: "日历"
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

# 📅 日历 {#calendar}

<ThemedImage
  alt="日历：一个月的日期方格，其中一天被抬起"
  sources={{
    light: useBaseUrl('/images/banners/calendar-light.svg'),
    dark: useBaseUrl('/images/banners/calendar-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

**日程安排、事件跟踪与管理——AI 可以为您规划。**

日历是一项内置的日程安排功能，为每个用户提供个人日历。创建事件、设置重复日程、与队友共享日历，并让 AI 模型通过自然对话自主创建和管理事件。

活跃的[自动化](/features/chat-conversations/chat-features/automations)会自动显示在专用的**定时任务**日历中，让您在同一界面同时查看手动事件和自动化工作流。

:::note
日历默认启用，但管理员可通过 [`ENABLE_CALENDAR`](/reference/env-configuration#enable_calendar) 环境变量或管理面板开关禁用。
:::

---

## 为什么使用日历？ {#why-calendar}

日历为模型提供了一种与时间交互的方式。启用之后，你可以让模型在某时提醒你做某事、安排一个重复任务，或者查看本周有哪些安排——开箱即用。

### AI 驱动的日程安排 {#ai-powered-scheduling}

启用[原生函数调用](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)后，模型可以通过自然语言搜索、创建、更新和删除日历事件。例如说出"*周五下午 3 点提醒我跟进设计团队*"，模型就会创建一个带提醒的事件。到达时间后，你会收到 toast 通知、浏览器通知，以及（可选的）Webhook，全程无需你手动创建事件。

### 与自动化集成 {#automation-integration}

活跃的[自动化](/features/chat-conversations/chat-features/automations)会作为虚拟事件显示在专用的**定时任务**日历中。即将到来的运行会显示下一次执行的时间，已完成的运行会直接链接到它生成的对话，让你能在同一时间轴上同时看到自己的事件与自动化工作流。

### 共享日历 {#shared-calendars}

通过访问授权把日历共享给特定用户或用户组。团队成员会看到共享事件以及自己的事件，并内置 RSVP 跟踪（待定、已接受、已拒绝、暂定）。

### 多日历组织 {#multi-calendar-organization}

跨多个日历组织事件（例如"个人"、"团队会议"），并使用颜色编码。每个用户首次访问时会自动创建**个人**和**定时任务**日历。

---

## 主要功能 {#key-features}

| | |
| :--- | :--- |
| 📅 **月/周/日视图** | 完整的日历 UI，支持月、周、日视图 |
| 🔁 **重复事件** | 基于 RRULE 的重复规则（每日、每周、每月、自定义） |
| 🤖 **智能体管理** | 模型可以自主搜索、创建、更新和删除事件 |
| ⚡ **自动化叠加** | 活跃自动化和过去运行以虚拟日历事件形式显示 |
| 👥 **日历共享** | 通过访问授权与用户或用户组共享日历 |
| 📍 **地点和描述** | 为事件添加地点和详细描述 |
| 🎨 **颜色编码** | 按日历和按事件自定义颜色 |
| ✅ **RSVP/参与者** | 邀请用户参加事件，支持待定/接受/拒绝/暂定状态 |
| 🔔 **提醒** | 通过 toast 通知、浏览器通知和 Webhook 发送每事件提醒 |

---

## 访问控制 {#access-control}

日历对非管理员用户实行权限门控。

- **管理员**：始终有权访问日历
- **用户**：需要 **功能 > 日历** 权限

若未获得所需权限而打开 `/calendar`，系统将把用户重定向至主页。

有关权限类别，请参阅 [RBAC 权限](/features/authentication-access/rbac/permissions#4-features-permissions)。

授予用户访问权限：

1. 打开 **管理面板 > 用户 > 用户组**
2. 编辑 **默认权限** 或特定用户组
3. 启用 **功能 > 日历**

也可以通过 [`USER_PERMISSIONS_FEATURES_CALENDAR`](/reference/env-configuration#user_permissions_features_calendar) 设置此默认值。

---

## 入门指南 {#getting-started}

### 访问日历 {#access-the-calendar}

从侧边栏打开 **用户菜单 > 日历**。首次访问时，会自动创建两个默认日历：

:::tip 快速访问
在用户菜单中按住 **Shift** 键可显示固定/取消固定按钮。固定日历会在侧边栏导航栏添加快捷图标，一键访问。
:::

- **个人** — 用于手动事件的默认日历（蓝色，首次访问时自动创建）
- **定时任务** — 自动化日程和运行的虚拟只读叠加层（紫色，仅在用户有[自动化](/features/chat-conversations/chat-features/automations)访问权限时可见）

### 创建日历 {#create-a-calendar}

点击日历侧边栏中**日历**标题旁的小 **+** 按钮，打开**新建日历**对话框。输入名称，并从预设调色板中选择颜色（蓝、红、绿、琥珀、紫、粉、青、橙），然后点击**创建**。新日历会立刻出现在侧边栏中，并在创建或编辑事件时显示在日历选择器中。每个日历归其创建者所有，可通过[共享日历](#sharing-calendars)进行共享。

### 创建事件 {#create-an-event}

1. 点击 **新建事件**（侧边栏或顶部栏），或点击日历网格上的任意日期/时间格
2. 填写事件详情：
   - **标题**（必填）
   - **日历** — 将事件添加到哪个日历
   - **时间** — 日期和时间，或切换**全天**
   - **地点**（可选）
   - **重复**：事件重复的频率，参见 [重复事件](#recurring-events)
   - **描述**（可选）
3. 点击 **创建**

**新建事件** 会打开一个表单。事件的默认日期为今天；开始时间是当前本地时间，结束时间是开始时间后一小时。这两个时间均采用设备时钟，因此即使在深夜或凌晨，日期仍显示为今天。若通过点击网格打开表单，则会预填该时间段：在周视图和日视图中，预填您点击时的具体小时；在月视图中，预填 09:00。

### 编辑或删除事件 {#edit-or-delete-an-event}

点击日历上的任意事件打开事件编辑器。在那里您可以更新详情或删除事件。自动化生成的虚拟事件无法直接编辑——点击它们会导航到自动化或运行的对话。

单击重复事件中的某一次，即可打开整个系列，日期从该事件的首次出现开始计算。 **保存** 会更改该系列中的每次事件，而 **删除** 则会删除整个系列。

---

## 日历视图 {#calendar-views}

使用顶部栏的下拉菜单切换视图：

| 视图 | 说明 |
|------|-------------|
| **月视图** | 完整月度网格，带事件标签。溢出的事件显示"+N 更多"链接到日视图。 |
| **周视图** | 7 天时间网格，带每小时时间槽。垂直滚动浏览全天。 |
| **日视图** | 单天时间网格，带每小时时间槽，用于精细日程安排。 |

使用**箭头按钮**向前/后导航，或点击**今天**跳转到当前日期。侧边栏中的小型日历提供快速日期导航。

---

## 重复事件 {#recurring-events}

在事件表单中设置**重复**，让事件再次出现：**不重复**（默认）、**每天**、**周一至周五**、**每周**、**每月**或**每年**。重复次数从事件自身的开始时间计算，因此每周事件会落在它开始的那一天，每个月的则会落在每月的同一天。

每次重复都位于你设定的时钟时间，按你的时区而非服务器的时区读取。09:00 的站会无论服务器运行在 UTC 还是别处都显示为 09:00，并且在夏令时拨快或拨回之后仍然是 09:00。

你的时区来自浏览器并保存在你的账户上，因此无需任何配置。当某个账户没有可用的时区时，它的重复事件会回退到服务器的时区。

### 每天已是事件可重复的最频繁频率 {#daily-is-as-often-as-an-event-can-repeat}

事件的重复频率不能高于每天一次。保存每小时或每十五分钟就重复一次的规则时，会被拒绝并提示 **Recurring events cannot repeat more often than daily**。该校验在服务端执行，因此对通过 API 创建、由模型创建以及在界面中创建的事件同样有效。

比每天更频繁的是任务而不是约会，它应当放在[自动化](/features/chat-conversations/chat-features/automations)中，自动化正是为这类调度设计的。

在限制出现之前保存的按日以下事件仍会照常运行。它们在重复规则被更改之前无法再次保存，因此若要修改这类事件的其他属性，就需要同时修正重复规则。

---

## 自动化集成 {#automation-integration-1}

**定时任务**日历连接了自动化和日历视图。它是一个**虚拟日历**——不存储在数据库中——在用户有自动化功能访问权限时，于 API 响应时间动态生成。

### 未来运行 {#future-runs}

对于每个具有 RRULE 日程的活跃自动化，日历计算即将发生的事件，并在请求的日期范围内按你自己的时区将其渲染为虚拟事件。

### 过去运行 {#past-runs}

已完成的自动化运行显示为历史事件。每个事件显示自动化名称，并包含链接到生成的对话（如果有）的元数据。点击过去的运行事件可打开其创建的对话。

### 工作原理 {#how-it-works}

- 虚拟日历使用固定 ID（`__scheduled_tasks__`），并从事件编辑器的日历选择器中排除
- 虚拟事件 ID 以 `auto_`（未来）或 `run_`（过去）为前缀
- 无法从日历 UI 中编辑或删除
- 点击未来运行事件导航到自动化编辑器
- 点击过去运行事件导航到运行的对话

---

## 智能体事件管理 {#agentic-event-management}

启用[**原生函数调用**](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)后，模型可以自主管理您的日历：

| 工具 | 功能 |
|------|-------------|
| `search_calendar_events` | 跨所有可访问日历按文本和/或日期范围搜索事件 |
| `create_calendar_event` | 在默认或指定日历上创建新事件 |
| `update_calendar_event` | 更新事件的标题、时间、描述、地点，或取消事件 |
| `delete_calendar_event` | 永久删除事件 |

> **您：** 从下周一开始，每个工作日上午 9 点安排团队站立会议。
>
> **您：** 本周我的日历上有什么安排？
>
> **您：** 把明天的设计评审改到下午 3 点，并将地点添加为 A 楼。

### 要求 {#requirements}

要使基于对话的日历工具可用：

1. 模型必须启用**原生函数调用**
2. 模型必须启用**内置工具**能力
3. 模型的内置工具设置中必须启用**日历**类别（默认启用）
4. **`ENABLE_CALENDAR`** 必须全局启用（默认启用）
5. 用户必须有 **功能 > 日历** 权限（管理员始终通过）

所有日期时间值会自动按用户检测到的时区处理。

有关所有内置工具的完整详情，请参阅[内置工具参考](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)。

---

## 共享日历 {#sharing-calendars}

日历支持与知识库、模型及其他资源相同的访问授权系统。

### 共享日历 {#share-a-calendar}

共享通过 API 完成：把该日历完整的访问授权列表发送到 `POST /api/v1/calendars/{calendar_id}/access/update`，每条授权指明一个用户或用户组，并带有 `read` 或 `write` 权限。

### 共享访问提供的功能 {#what-shared-access-provides}

| 权限 | 效果 |
|------------|--------|
| **读取** | 查看日历及其事件 |
| **写入** | 读取 + 在日历上创建、更新和删除事件 |

只有日历**所有者**（或管理员）才能管理访问授权和删除日历本身。

:::info 公开共享受权限控制
非管理员用户只能在 [共享权限](/features/authentication-access/rbac/permissions#2-sharing-permissions) 允许的范围内进行共享。 **日历公开共享** 向所有拥有日历权限的用户开放日历。日历绝不能与未登录的用户共享。
:::

---

## 参与者与 RSVP {#attendees-and-rsvp}

事件支持带有 RSVP 跟踪的参与者：

| 状态 | 含义 |
|--------|---------|
| `pending` | 已发送邀请，尚无回复 |
| `accepted` | 参与者已确认出席 |
| `declined` | 参与者已拒绝 |
| `tentative` | 参与者不确定 |

参与者可以通过 API 更新自己的 RSVP 状态。作为参与者的用户可以查看其受邀事件，无论日历所有权如何。

---

## 提醒与提示 {#reminders--alerts}

每个事件都有**提醒**设置，控制事件开始前何时触发提示。

| 选项 | 行为 |
|--------|----------|
| **无** | 不提示 |
| **事件开始时** | 事件开始时提示 |
| **提前 5/10/15/30 分钟** | 提前相应分钟数提示 |
| **提前 1 小时** | 提前 60 分钟提示 |

默认为**提前 10 分钟**。

### 提示的发送方式 {#how-alerts-are-delivered}

1. **Toast 通知** — 在 Open WebUI 界面显示带事件标题和剩余时间的提示。点击 toast 导航到日历。
2. **浏览器通知** — 如果用户设置中启用了浏览器通知，会显示原生 OS 通知。
3. **Webhook** — 如果用户在 **设置 > 通知** 中配置了 Webhook URL，会发送 `calendar_alert` 负载。

提示通过 `meta.alerted_at` 在服务端进行去重，因此每个事件每个开始时间最多触发一次——即使重启或多实例部署也不例外。

全局提示轮询窗口可通过 [`CALENDAR_ALERT_LOOKAHEAD_MINUTES`](/reference/env-configuration#calendar_alert_lookahead_minutes) 配置（默认：10 分钟）。

---

## 配置 {#configuration}

| 变量 | 默认值 | 说明 |
|----------|---------|-------------|
| [`ENABLE_CALENDAR`](/reference/env-configuration#enable_calendar) | `True` | 全局启用或禁用日历功能 |
| [`USER_PERMISSIONS_FEATURES_CALENDAR`](/reference/env-configuration#user_permissions_features_calendar) | `True` | 默认启用或禁用非管理员用户的日历访问 |
| [`USER_PERMISSIONS_CALENDAR_ALLOW_PUBLIC_SHARING`](/reference/env-configuration#user_permissions_calendar_allow_public_sharing) | `False` | 是否允许非管理员所有者为日历附加通配符读取/写入访问授权 |
| [`SCHEDULER_POLL_INTERVAL`](/reference/env-configuration#scheduler_poll_interval) | `10` | 调度器心跳间隔秒数（与自动化共享） |
| [`CALENDAR_ALERT_LOOKAHEAD_MINUTES`](/reference/env-configuration#calendar_alert_lookahead_minutes) | `10` | 即将到来事件的默认提示窗口（分钟） |

也可以从**设置 > 通用**（管理员区域）的功能部分切换日历。

---

## 局限性 {#limitations}

### 不支持外部日历同步 {#no-external-calendar-sync}

日历目前是 Open WebUI 中的独立功能。它不与 Google Calendar、Outlook 或其他外部日历服务通过 CalDAV/iCal 同步。

### 定时任务日历是虚拟且只读的 {#scheduled-tasks-calendar-is-virtual-and-read-only}

定时任务日历在运行时生成，不存储在数据库中。其事件无法从日历 UI 中编辑或删除。请从[自动化](/features/chat-conversations/chat-features/automations)页面管理底层自动化。

### 重复事件展开 {#recurring-event-expansion}

重复事件在查询时在服务端展开。非常复杂的 RRULE 模式或极长的日期范围可能会增加响应时间。
