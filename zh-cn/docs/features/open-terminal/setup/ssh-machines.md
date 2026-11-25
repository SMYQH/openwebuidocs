---
sidebar_position: 4
title: "SSH 机器"
---

# 通过 SSH 添加机器 {#add-a-machine-over-ssh}

你可以用自己的服务器、备用电脑或笔记本电脑作为 Open Terminal 机器，无需运行 Docker，也无需开放端口。向 Open WebUI 提供 SSH 地址后，它会在该机器上安装并启动 Open Terminal，然后通过 SSH 访问它。

随后，AI 可以使用该机器上 SSH 用户可访问的文件和工具，效果等同于[裸机安装](./installation.mdx)。

---

## 要求 {#requirements}

- Open WebUI 服务器须能通过 SSH 访问该机器，并在 Linux 或 macOS 上运行，例如在 Docker 中运行。原生安装在 Windows 上的 Open WebUI 无法使用 SSH 机器，因为此连接需要 Open WebUI 一侧提供 Unix 套接字。
- 该机器运行 Linux（x86_64 或 aarch64）或 macOS（Apple silicon）。
- 该机器已安装 `curl` 和 `tar`。
- 该机器可以联网下载 uv、Python 3.12 和 Open Terminal。
- 你是 Open WebUI 的管理员。

---

## 添加机器 {#add-the-machine}

### 1. 打开机器区域 {#1-open-the-machines-section}

进入**设置 > 集成**，滚动到**机器**并点击 **+**，参见[连接 Open Terminal](./connecting.md)。

### 2. 输入地址 {#2-enter-the-address}

在 URL 字段中输入机器地址，格式为 `ssh://user@host` 或 `ssh://user@host:port`（默认端口为 22）。填写机器的**名称**（必填）。表单随后会询问 Open WebUI 应如何登录。

### 3. 选择登录方式 {#3-choose-how-to-sign-in}

Open WebUI 会为该机器创建自己的 SSH 密钥，并要求将其添加到该用户的 `~/.ssh/authorized_keys` 文件中。使用**登录方式**下的一种方式添加密钥。

| 选项 | 说明 |
| :--- | :--- |
| **密码** | 输入用户的 SSH 密码。Open WebUI 会登录一次、添加自己的密钥，然后丢弃密码。 |
| **私钥** | 粘贴或上传该机器已接受的私钥。如果私钥设有口令，也请填写。Open WebUI 只使用它一次来添加自己的密钥，随后将其丢弃。 |
| **手动添加密钥** | Open WebUI 会显示一条命令。以该用户身份在机器上执行命令，然后点击**继续**。 |

### 4. 选择 Open Terminal 版本 {#4-choose-an-open-terminal-version}

**版本**留空时安装最新版。要固定版本，请输入版本号，例如 `0.17.21`。`0.17.21` 是 Open WebUI 支持的最低版本。

**软件包**可以留空，也可以列出要添加到机器的软件，例如 `desktop browser ffmpeg`。`desktop` 安装桌面环境，`browser` 安装 Chrome，从而启用[桌面和浏览器选项卡](../use-cases/web-development.md)。其他名称会作为 apt 软件包安装。这需要能免密运行 `sudo` 的用户。

### 5. 核对指纹并安装 {#5-check-the-fingerprint-and-install}

点击**安装**。Open WebUI 会显示该机器的主机密钥指纹。将它与预期指纹对照，再点击**信任并安装**。Open WebUI 会记录该指纹，一旦指纹变化就拒绝连接。

进度列表会显示安装过程。状态变为**就绪**后，机器会出现在**机器**列表中，用法与其他机器相同。Open Terminal 位于 `~/.open-webui/`，此目录在 SSH 用户的主目录下。如果某个软件包安装失败，机器仍然可用，并会显示警告，其中包含可在机器上手动运行的命令。

:::warning 谁可以使用
任何有权访问该机器的人都能运行命令，并查看 SSH 用户可见的所有文件。对于共享机器，请使用专用用户，并在机器的**访问权限**区域设置谁可以访问，参见[连接 Open Terminal](./connecting.md#6-optional-restrict-access-to-specific-groups)。
:::

---

## 管理机器 {#manage-the-machine}

从**机器**列表打开机器，即可查看它的 Open Terminal 版本和这些按钮。

| 按钮 | 功能 |
| :--- | :--- |
| **升级** | 安装版本字段指定的版本。留空则安装最新版。也会修复损坏的安装，并安装**软件包**中列出的软件。 |
| **安装**（**软件包**旁） | 将**软件包**中列出的软件安装到机器上，无需升级。 |
| **重启** | 重启该机器上的 Open Terminal。 |
| **日志** | 显示 Open Terminal 日志的最新几行。机器报错时，先查看这里。 |

**起始目录**是终端会话启动的位置。留空时使用 SSH 用户的主目录。要从其他目录启动，请在添加或编辑机器时输入机器上已存在的绝对路径，例如 `/home/user/project`。更改该设置会在新目录中重启 Open Terminal。

**启动参数**为 `open-terminal run` 命令添加选项。该命令在机器上启动 Open Terminal。例如，可用 `--desktop-mode host` 共享你已登录的 Linux 桌面。Open WebUI 会自行设置 `--ipc` 和 `--api-key`，此处不接受这两个参数。保存更改会重启 Open Terminal。如果新参数导致启动失败，Open WebUI 会恢复原先的参数和起始目录，并显示错误。

要移除机器，请删除它并确认。Open WebUI 会从机器上卸载 Open Terminal 并丢弃自己的密钥。如果机器无法访问，Open WebUI 仍会让你选择从 Open WebUI 中移除它。`~/.open-webui/` 下的文件会留在机器上，直到你自行删除。

Open WebUI 的密钥始终保留在机器的 `~/.ssh/authorized_keys` 中。对应行以 `open-webui-` 加机器 ID 结尾。删除该行即可撤销密钥。
