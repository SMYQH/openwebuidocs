---
sidebar_position: 4
title: "自动化任务"
---

# 自动化任务

Open Terminal 不仅仅用于代码。AI 可以管理文件、整理文件夹、批量处理数据、处理备份以及自动化重复性工作，全部通过对话完成。

---

## "重命名并整理这些文件"

> **你：** 我在 /photos 文件夹中有 200 张照片，名称类似于 IMG_4521.jpg。将它们重命名为包含日期，并按月份整理到文件夹中。

AI 读取文件日期，重命名所有文件，并创建按月份分类的文件夹：

![AI 创建和重命名带有日期前缀的文件](/images/open-terminal-ai-file-rename.png)

---

## "查找并删除重复文件"

> **你：** 我的文档文件夹中有重复文件吗？

AI 检查文件大小和内容以找到完全相同的重复文件，然后询问你要如何处理：

![AI 分析文件及磁盘使用详情](/images/open-terminal-ai-disk-usage.png)

---

## "备份这个文件夹"

> **你：** 创建 /projects 文件夹的 zip 备份，文件名中包含今天的日期。

![AI 执行系统自动化命令](/images/open-terminal-ai-file-rename.png)

---

## "转换这些文件"

> **你：** 将这个文件夹中的所有 .png 截图转换为 .jpg，并将尺寸缩小一半。

AI 使用图像工具（Docker 中已预装）进行批量转换和调整大小：

![AI 使用 run_command 进行批量文件操作](/images/open-terminal-ai-install-run.png)

---

## "检查系统状态"

> **你：** 还剩多少磁盘空间？有没有我应该清理的大文件？

![AI 检查磁盘使用情况并分析存储](/images/open-terminal-ai-disk-usage.png)

---

## "对文件夹中的每个文件执行此操作"

> **你：** 对于 /data 中的每个 CSV 文件，添加一个包含"Name, Date, Amount"的标题行并保存。

AI 编写脚本，处理每个文件，并返回结果：

![AI 读取和分析 CSV 数据](/images/open-terminal-ai-csv-analysis.png)

---

## 预装工具

Docker 镜像预装了常用的工具：

| 你想做什么 | 可用工具 |
| :--- | :--- |
| 从互联网下载文件 | curl, wget |
| 处理 JSON 数据 | jq |
| 压缩/解压文件 | zip, tar, gzip, 7z |
| 处理图片 | ffmpeg, ImageMagick（如果已安装） |
| 操作数据库 | sqlite3 |
| 在服务器间传输文件 | rsync, scp |

如果某个工具未安装，AI 可以即时安装（`sudo apt install ...`）。

## 更多尝试

- **[从聊天运行代码 →](./code-execution)**：AI 编写、运行和调试代码
- **[分析文档和数据 →](./file-analysis)**：电子表格、PDF、Word 文档、邮件
- **[构建和预览网站 →](./web-development)**：创建和迭代网页

:::tip
想要从任何地方自动化你的真实机器上的任务？[**Open WebUI Computer**](/ecosystem/computer) 将你的计算机放入浏览器标签页，可从任何设备访问。
:::
