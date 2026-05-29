---
title: 技能和记忆
sidebar_position: 6
---

# 技能和记忆

**技能**是一个包含 `SKILL.md` 文件的文件夹：一组可重用的指令集，AI 可以按需调用（[agentskills.io](https://agentskills.io) 规范）。**记忆**跨聊天存储持久的每个用户的事实。如果你已经为其他工具保留了技能或 `CLAUDE.md`/`AGENTS.md`，Computer 会自动识别它们。

## 技能格式

```markdown
---
name: release-checklist
description: 我们在这个仓库中如何进行发布
---

1. 运行完整的测试套件……
```

Frontmatter 需要 `name` 和 `description`；正文是指令。可选的子目录：`references/`、`templates/`、`scripts/`、`assets/`。技能渐进式加载：目录始终对模型可见，完整的 `SKILL.md` 在激活时加载，资源按需加载。

## 技能发现位置

| 范围 | 路径 |
| --- | --- |
| 工作区 | `.cptr/skills`、`.agents/skills`、`.claude/skills`、`.codex/skills` |
| 全局 | `~/.cptr/skills`、`~/.agents/skills` |

你已经为 Claude Code 或 Codex 创建的技能会自动被识别，无需复制。

## 使用和管理技能

- 在聊天输入中键入 **`$`** 来提及一个技能；**`/`** 也可以找到技能。
- 在 UI 中创建的技能会写入 `.cptr/skills`（工作区）或 `~/.cptr/skills`（全局）。
- 管理员的**技能**页面控制哪些技能已启用。
- 可选的**后台技能审查**：每 N 次轮次（默认 10），AI 可以根据实际工作方式提出对技能的更新。

## 记忆

记忆是按用户划分的：在**设置**中切换开启。被调用的事实会包含在后续的聊天上下文中。条目存储在 `<data-dir>/memory/users/<id>/` 下，可以在记忆视图中查看、编辑或删除。不要将秘密放在技能或记忆中；两者最终都会进入模型上下文。

## 系统提示

系统提示按顺序解析；第一个匹配的胜出：

1. 工作区文件 `<workspace>/.cptr/system.md`
2. 每个模型的系统提示（模型设置）
3. 全局（`*` 模型）
4. 内置默认值

提示支持 `{{VAR}}` 模板变量：`WORKSPACE_NAME`、`WORKSPACE_PATH`、`FILE_TREE`、`INSTRUCTIONS`、`MEMORY`、`SKILLS`、`CPTR_CONTEXT`、`RUNTIME_ENV`、`HOSTNAME`、`OS`、`PLATFORM`、`ARCH`、`SHELL`、`HOME`、`CPTR_VERSION`、`DATE`、`MODEL`。

## 自动加载的指令文件

Computer 按此顺序从工作区根目录读取指令文件（最多 32KB）：**`MEMORY.md`、`AGENTS.md`、`AGENT.md`、`CLAUDE.md`**。现有的 `CLAUDE.md` 或 `AGENTS.md` 可以直接使用：AI 在每次轮次中都能看到它，以及紧凑的文件树（跳过 `.git`、`node_modules`、`.venv`、`dist`……）、记忆和技能目录。
