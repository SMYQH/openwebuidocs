---
sidebar_position: 5
title: "本地机器"
---

# 添加本地机器 {#add-a-local-machine}

:::warning 实验性功能
本地机器是实验性功能，可能发生变化。
:::

填写名称并点击安装即可让 Open WebUI 在自身所在的服务器上安装并运行 Open Terminal。随后，AI 可以使用运行 Open WebUI 的用户可访问的文件和工具，效果等同于在该服务器上[裸机安装](./installation.mdx)。

:::warning 谁可以使用
任何有权访问本地机器的人都能在 Open WebUI 服务器上以 Open WebUI 进程的用户身份运行命令，并查看该用户可见的所有文件。只与足够信任的人共享。在机器的**访问权限**区域设置谁可以访问，参见[连接 Open Terminal](./connecting.md#6-optional-restrict-access-to-specific-groups)。
:::

---

## 要求 {#requirements}

- 你是 Open WebUI 的管理员。
- Open WebUI 服务器运行 Linux（x86_64 或 aarch64）或 macOS（Apple silicon）。
- 服务器已安装 `curl` 和 `tar`。
- 服务器可以联网下载 uv、Python 3.12 和 Open Terminal。

---

## 添加机器 {#add-the-machine}

### 1. 打开机器区域 {#1-open-the-machines-section}

进入**设置 > 集成**，滚动到**机器**并点击 **+**，参见[连接 Open Terminal](./connecting.md)。

### 2. 选择本地类型 {#2-choose-the-local-type}

点击**远程**，这是**类型**旁的选项，然后选择**本地**。名称可选。

每个 Open WebUI 实例只允许一台本地机器。添加后，**类型**选项就会消失。

### 3. 选择目录和版本 {#3-choose-a-folder-and-a-version}

**起始目录**是终端会话启动的位置。留空则从项目目录启动。如果 `/workspace` 存在，就用该目录。否则，使用数据卷中的 `workspace` 目录（Open WebUI 在 Docker 中运行时），或使用启动 Open WebUI 时所在的目录。要使用其他目录，请输入已存在的绝对路径，例如 `/home/user/project`。

**版本**留空时安装最新版。要固定版本，请输入版本号，例如 `0.17.21`。`0.17.21` 是 Open WebUI 支持的最低版本。

### 4. 安装 {#4-install}

点击**安装**。进度列表会显示安装过程。状态变为**就绪**后，机器会出现在**机器**列表中，用法与其他机器相同。

Open Terminal 安装在 `~/.open-webui/`，此目录位于 Open WebUI 用户的主目录下。在 Docker 中，它安装在数据卷中，因此更新容器后仍会保留。

---

## 管理机器 {#manage-the-machine}

从**机器**列表打开机器，即可修改**起始目录**，以及升级、重启或查看日志，详见 [SSH 机器](./ssh-machines.md#manage-the-machine)。更改**起始目录**会在新目录中重启 Open Terminal。**启动参数**的用法与 [SSH 机器](./ssh-machines.md)相同。

删除机器时，Open WebUI 会卸载 Open Terminal。起始目录中的文件会保留。
