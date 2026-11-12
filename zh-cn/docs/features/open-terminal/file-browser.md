---
sidebar_position: 10
title: "文件浏览器"
---

# 文件浏览器 {#the-file-browser}

当 Open Terminal 连接后，[**Tabs**](/features/chat-conversations/chat-features/#tabs-side-panel) 的 **Files** 标签页中会有一个**文件浏览器**。它的使用方式就像你电脑上的文件资源管理器。你可以浏览文件夹、打开文件、上传内容和下载结果。AI 创建的所有内容都会自动显示在这里。

![打开 Files 标签页的新聊天](/images/open-terminal-file-browser.png)

---

## 浏览文件 {#browsing}

点击文件夹进行导航，点击文件预览内容。顶部的面包屑导航栏会显示你当前所在的位置。

Tabs 的 **+** 菜单中的 **Files** 会再打开一个 Files 标签页，因此你可以并排保持多个文件夹处于打开状态。每个 Files 标签页都以它所显示的文件夹命名。

要选中多个文件，可以从列表中的空白处拖出一个选框。在触摸屏上，请先静止按住手指片刻再拖动。

![带有面包屑导航的项目目录浏览](/images/open-terminal-file-browser-project.png)

### 排序 {#sorting}

使用文件列表上方的工具栏，可以按 **Name（名称）**、**Size（大小）**、**Date Modified（修改时间）** 或 **Date Added（添加时间）** 升序或降序排序。文件夹始终排在文件前面，因此排序顺序只会调整每个分组内部的条目顺序。按日期排序时，该日期会与文件大小一起显示在每一行旁边，便于在 AI 刚刚把内容写入工作目录时快速找到最新产物。按 **Date Added** 排序需要终端能报告文件的创建时间。

### 网格视图与列表视图 {#grid-and-list-view}

工具栏中的 **Actions** 菜单（**...**）可在 **List view（列表视图）** 和 **Grid view（网格视图）** 之间切换。你的浏览器会记住这一选择。

---

## 预览文件 {#previewing-files}

在桌面端，将鼠标悬停在文件上会显示它的小预览：文本文件最大 1 MB，其他文件最大 20 MB。

点击任意文件即可查看完整预览。不同文件类型的显示方式各不相同：

:::info Word 和 PowerPoint 的渲染需要较新的终端
这类文件由终端自行排版，这需要运行默认镜像的 Open Terminal 0.12.1 或更高版本。否则浏览器只能绘制一个近似效果。参见[更新](./setup/updating.mdx)，如果你的预览比这里描述的更粗糙的话。
:::

### 文本与代码 {#text-and-code}
源代码和文本文件会在代码编辑器中打开，带有语法高亮和行号。参见[编辑文件](#editing-files)。

![带有语法高亮和行号的 Python 代码](/images/open-terminal-preview-code.png)

### PDF {#pdfs}
PDF 文档可直接在浏览器中渲染——无需下载即可阅读。文档旁边是一条带编号的**缩略图栏**；点击某一页即可跳转过去。在较窄的面板中它会被隐藏。

![带有渲染 Markdown 预览的文件浏览器](/images/open-terminal-preview-markdown.png)

### 电子表格（CSV、TSV） {#spreadsheets-csv-tsv}
数据文件以**格式化表格**的形式呈现，包含标题和整洁的行——比原始逗号分隔文本更易阅读。

![CSV 数据渲染为整洁表格](/images/open-terminal-preview-csv.png)

### Excel 工作簿（XLSX、XLS） {#excel-workbooks-xlsx-xls}
`.xlsx` 和 `.xls` 文件以表格形式打开，一次显示一个工作表。包含多个工作表的工作簿会显示一个选择器用于在工作表之间切换。工作表上方的公式栏显示所选单元格的值或公式。拖动列边缘可以调整列宽，双击边缘则可以让列宽贴合内容。

可写的 `.xlsx` 文件可以在预览中编辑。双击某个单元格或直接开始输入即可修改，也可以粘贴一段单元格区域。**保存**会把工作簿写回文件。含公式的单元格、表头和受保护的表保持只读。如果自你打开之后该文件在终端上发生了变化，保存会中止并请你重新加载，你的修改仍保留在编辑器中。

### Word 文档（DOCX） {#word-documents-docx}
`.docx` 文件由终端本身排版，使用的是办公套件所用的同一套引擎，因此预览呈现的就是排版完成的文档。你看到的就是该文件打印出来的样子：真实的分页、页眉、页脚、脚注和尾注、内嵌图片、字体与间距。

文档旁边是一条带编号的**缩略图栏**；点击某一页即可跳转过去。页面会缩放以适应面板宽度。预览底部悬浮着一个小工具栏，用于放大和缩小，点击缩放级别可回到初始状态。按住 **Ctrl**（macOS 上为 **Cmd**）滚动可围绕指针缩放。

在终端无法为文档排版的情况下，浏览器会代为绘制，预览会提示其结果可能与下载的文件不同。这种渲染保留了文本、表格和图片，但不保证版式完全一致。只有当它也失败时，才会报错并建议改为下载文件。

### 演示文稿（PPTX） {#presentations-pptx}
`.pptx` 文件在**幻灯片查看器**中打开，一次显示一张幻灯片。终端渲染整套演示文稿的方式与渲染 Word 文档相同，因此每张幻灯片呈现的都是完成品：背景、填充、字体、间距，以及每个占位符从版式或母版继承而来的位置。

左侧是幻灯片的编号**缩略图栏**；点击缩略图即可跳到那张幻灯片。在较窄的面板中它会被隐藏。底部悬浮工具栏可在幻灯片之间翻页、显示当前所在幻灯片并缩放。滚动可平移幻灯片；按住 **Ctrl**（macOS 上为 **Cmd**）滚动可缩放；放大之后可以拖动幻灯片。预览上方工具栏中的 **Reset view**，或悬浮工具栏中的缩放级别，可把幻灯片恢复到适配位置。

在终端无法渲染该演示文稿的情况下，浏览器会改为绘制每张幻灯片的近似效果，预览会提示其结果可能与下载的文件不同。这种近似渲染可绘制单系列的柱状图、折线图、饼图和圆环图，包括负值。堆叠图、组合图以及其他图表类型会显示 **Chart preview unavailable**。当精确渲染很重要时，请在对应的应用程序中打开该文件。

### Markdown
可写的 Markdown 文件会在**富文本编辑器**中打开：你直接编辑格式化后的文本，**保存**会把它写回 Markdown。数学公式、提示框和 Mermaid 图表都会渲染出来；点击其中一个即可编辑其源码。你粘贴或拖入编辑器的图片会上传到终端中该 Markdown 文件所在的文件夹，并以相对路径链接。**Source** 切换到代码编辑器查看原始 Markdown，**Editor** 再切回来。

只读的 Markdown 文件会显示**渲染预览**，使用与聊天回复相同的渲染器，因此数学公式、脚注、高亮代码块、提示框和 Mermaid 图表都能正常显示。混入 Markdown 中的 HTML 块会与之一起渲染，因此 `<details>` 区块和 `<div align="center">` 之类的包装会显示其格式化后的 Markdown 内容。指向终端上其他文件的链接会在浏览器中打开该文件。

两种模式下，相对路径的图片都从终端加载。

![渲染后的 Markdown，含标题、表格和代码块](/images/open-terminal-preview-markdown.png)

### 文档中的批注 {#comments-in-documents}
Word、Excel、PowerPoint 和 PDF 的预览会显示文件中存储的批注及其回复，并锚定在它们在文档中的位置。悬停在标记上可以阅读该讨论串，在触摸屏上则可以点按。没有合适预览位置的批注会汇集在角落的计数器后面。如果无法读取批注，预览会提示 **"Could not read comments. Download the original file to review them."**

### 图片 {#images}
图片以合适的大小内联显示。

![显示图片预览的文件浏览器](/images/open-terminal-file-browser-home.png)

### 3D 模型 {#3d-models}
`.glb`、`.gltf`、`.stl`、`.obj` 和 `.ply` 文件会在 3D 查看器中打开。拖动可旋转，滚动可缩放；**Reset view** 可把模型恢复到取景范围内。贴图和材质文件从相对于模型的路径加载。

### HTML

HTML 文件在**沙箱化**的 iframe 中渲染。脚本和下载可以正常工作，但该页面会被赋予自己独有的源，因此它无法读取 cookie 或 `localStorage`，回指 Open WebUI 的同源请求也会失败。

这种隔离正是要点所在：被预览的文件是不可信内容，把你的源交给它就等于让它以你的身份行事。需要同源行为的页面会悄无声息地失败而不是报错——预览看起来坏掉但文件其实没问题时，这通常就是原因。

如果你理解其中的风险并且确实需要，可以在每个用户的 **Settings > Interface > iframe Sandbox Allow Same Origin** 开关中授予该权限。它**默认关闭**，并且适用于每一个内嵌 iframe，而不只是这个预览。完整的取舍参见 [Rich UI](/features/extensibility/plugin/development/rich-ui#sandbox-and-security)。

---

## 上传文件 {#uploading-files}

**拖放**文件或整个文件夹到文件浏览器上即可上传。文件夹会保持原有结构：其中每个子文件夹都会在终端上重新创建。工具栏和右键菜单中的 **Upload Folder** 通过选择器完成同样的事。这就是你与 AI 共享数据的方式：拖入电子表格、PDF、图片，或任何你希望 AI 处理的文件。

![浏览器中列出的文件及其名称和大小](/images/open-terminal-file-browser-documents.png)

:::tip 上传到任意文件夹
先导航到你想要的文件夹，然后再拖放。文件会上传到你当前正在浏览的目录。
:::

标记为 **Read-only** 的文件夹中上传功能是关闭的，往其上拖放文件不会有任何效果。

### 从聊天输入框 {#from-the-chat-input}

在聊天输入框中附加的文件通常会送到 Open WebUI，在那里提取其文本供模型阅读。管理员可以改为把它们指向终端，方法是把连接的 **Chat Uploads** 设置为 `Filesystem`。这样附件会落在文件浏览器当前打开的文件夹中，并像其他任何内容一样出现在这里。模型用终端自带的工具打开它们。参见 [Chat Uploads](/features/open-terminal/setup/connecting#chat-uploads)。

### 把终端文件附加到消息 {#attaching-terminal-files-to-a-message}

把文件从文件浏览器拖到消息输入框上，即可把它们附加到你的下一条消息。选中多个文件时会一起附加。在触摸屏上，请长按文件后再拖动。文件会留在终端上，模型获得它们的路径，与 **Chat Uploads** 设置为 `Filesystem` 时相同。这需要 [Allow File Upload](/features/authentication-access/rbac/permissions#3-chat-permissions) 权限，并且一条消息中的所有终端文件必须来自同一个终端。

---

## 比较两个文件 {#comparing-two-files}

用复选框或 `Ctrl`-点击选中两个文件，然后选择 **Compare**。你也可以在某个文件的菜单中选择 **Select for Compare**，再在另一个文件中选择 **Compare with Selected**。两者会并排显示，并标出差异。

文本文件会在只读的对比视图中打开：用箭头逐步浏览改动，**Swap sides** 可切换哪个文件在左侧，**Refresh** 会重新读取两个文件。**Comparison options** 菜单（**...**）提供 **Ignore whitespace**、**Ignore emphasis markers**（跳过那些只是新增或删除 `*` 和 `_` 的改动）以及 **Only show changes**（折叠大段未变动的行）。改动的行按其匹配文本对齐。该视图可处理每个最大 2 MiB 的 UTF-8 文本文件。

文档（PDF、Word、Excel、PowerPoint、OpenDocument 和 RTF 文件）按从中提取出的**文本**进行比较，因此 Word 文件与 PDF 之间的比较，或者昨天的工作表与今天的工作表之间的比较，都同样适用。

:::info 需要较新的 Open Terminal
文档比较在终端服务器上运行。没有该功能的终端会让浏览器提示 **"File comparison is not available on this terminal. Update Open Terminal to use Compare."** 参见[更新](./setup/updating.mdx)。
:::

## 下载文件 {#downloading-files}

点击任意文件上的**下载按钮**即可将其保存到你的电脑。这是获取结果的方式：AI 生成图表、创建电子表格、处理图片或撰写报告后，直接下载即可。

### 聊天消息中显示的文件 {#files-shown-in-the-chat-message}

AI 也可以直接把文件放进它的回复里，而不是让你自己在浏览器中去找。要求它在聊天中显示该文件，消息就会带上一个小卡片，包含文件名、内容预览，以及下载或在文件浏览器中打开它的按钮。

预览支持浏览器支持的相同格式，因此电子表格以表格呈现，图片以图片呈现，PDF 以页面呈现。卡片每次打开时都会使用你自己的权限从终端读取该文件，因此不会有任何内容被复制出终端，也不会存在指向它的公开链接。由此可见，卡片只在其来源终端处于连接且选中状态时可用，否则它会报告该终端不可用。

长文档可以从最关键的部分打开。对于 PDF、Word 文档或幻灯片演示文稿，AI 可以指明它所说的页码或幻灯片，预览会直接打开到那里，而不是从头开始。询问某个答案出自哪一页，你拿到的文档就已经滚动到该处，从而省去在一百页中翻找回复所引用段落的时间。文件在浏览器中打开而非在消息中打开时，同样如此。

![AI 引用了一处电缆额定值并把手册打开到第 132 页](/images/open-terminal-display-file-manual-page.png)

这里 AI 检索了一份 150 页的手册，引用了它找到的规格说明，并把 PDF 打开到第 132 页，让这段引用能在上下文中被读到。

当你不知道该看哪个文件时也一样。询问哪份文档涵盖了某个主题，会先搜索文件夹，然后把匹配到的文档打开到正确的位置。

![AI 定位到正确的文档并打开到相关页面](/images/open-terminal-display-file-report-page.png)

![以卡片形式显示在助手消息中的 CSV 和生成的图表](/images/open-terminal-inline-file-card.png)

演示文稿的呈现方式相同，带有幻灯片栏、页面控制和缩放，因此无需离开对话即可翻阅整套幻灯片。

![在聊天消息中内联渲染的演示文稿](/images/open-terminal-display-file-deck-inline.png)

卡片标题是一个开关，当预览占据了太多回复空间时可以折叠到只剩文件名，图片和文档预览还带有缩放控件和调整大小的手柄。

默认情况下由 AI 决定，除非它明确要求使用卡片，否则它显示的文件会在文件浏览器中打开。**Settings > Interface > Terminal File Display** 决定在 AI 未指定时你得到哪一种：保持 **Sidebar** 则在浏览器中打开，设为 **Inline** 则让文件出现在消息里。

![在聊天旁以文件查看器打开的 Word 报告](/images/open-terminal-display-file-report-viewer.png)

---

## 编辑文件 {#editing-files}

文本和代码文件会直接在代码编辑器中打开：输入你的修改，然后点击 **保存** 或按 `Ctrl+S`（macOS 上为 `Cmd+S`）。这对于快速修正是很方便的：修改某个配置值、纠正一个错别字，或微调 AI 生成的内容。像 HTML、JSON 或 CSV 这样自带预览的文件，会以 **Source** 打开同一个编辑器。[Markdown](#markdown) 和 [Excel](#excel-workbooks-xlsx-xls) 文件则在各自的预览中编辑。

编辑器会在你输入时提示文件中已经出现过的词语；按 `Tab` 接受其中一个。在 Git 仓库中，与上一次提交相比，新增行的行号旁会带绿色标记，修改行的行号旁会带琥珀色标记。

![在文件浏览器中直接编辑文件](/images/open-terminal-preview-code.png)

如果你带着未保存的编辑离开某个文件，例如打开了另一个文件或文件夹，系统会先请你 **保存** 或 **丢弃更改**。

---

## 就选中内容提问 {#asking-about-a-selection}

在打开的文件中选中文字，旁边会出现一个 **Ask or edit…** 输入框。输入问题或指令后按 `Enter`。该请求会带着附加的文件和被引用的选中文本一起进入聊天，若有页码或工作表也会一并带上。模型在同一个终端上处理该文件，因此它可以就该文件回答问题或修改文件。

一次最多可以选中 16 KiB 的文本。如果文件有未保存的编辑，系统会先请你 **保存并发送**。在回复仍在生成时发送的请求会进入聊天的队列，并在该回复结束后发出。

---

## 创建与删除 {#creating-and-deleting}

你可以直接在文件浏览器中新建文件或文件夹，也可以删除不再需要的内容。文件夹的菜单中还有 **New File** 和 **New Folder**。

![预览了图片的 Files 标签页](/images/open-terminal-file-browser-home.png)

---

## 只读的文件与文件夹 {#read-only-files-and-folders}

有些文件和文件夹无法更改。文件浏览器会把它们标记为 **Read-only**，并把会失败的操作置灰，这样你是在尝试之前就知道，而不是尝试之后。

不可写的文件夹会在顶部面包屑旁标记为 **Read-only**。在其中时 **New File**、**New Folder** 和 **Upload** 都会置灰，往其上拖放文件不会有任何效果，里面的任何东西都无法重命名或删除。

不可更改的单个文件或文件夹会在其名称旁标记为 **Read-only**。其菜单中的 **Rename** 和 **Delete** 会被置灰，它无法被拖入其他文件夹，其预览也无法编辑。如果一次选中多个项目，只要其中有任意一个是只读的，**Delete** 就会保持置灰。

只读只限制修改，别的都不影响。你仍然可以照常浏览、预览和下载这些文件。

---

## 工作目录 {#working-directory}

选中某个终端后，消息输入框中紧挨着它的 **Working Directory** 按钮（文件夹图标）用于选择该聊天工作的文件夹。除非正在生成回复（临时聊天中同样如此），你可以随时更改它。使用 Per chat 终端时，该按钮会在聊天保存之后才出现，而临时聊天只提供其他终端。菜单中有一个搜索框、用于终端自身默认值的 **No folder**、你的 **Recently Used** 文件夹，以及 **Open folder**——后者会打开一个对话框用于浏览终端。在该对话框中，**Use this directory** 会选中你所在的文件夹。

**Recently Used** 列出你最近在该终端上使用过的八个文件夹。它们以文件形式存储在终端上，位于其主目录下的 `.open-webui/users/<user id>/folders`，因此会跟随你到其他浏览器。任何能读取该主目录的人都能看到它们。

### 克隆仓库 {#cloning-a-repository}

当终端支持 Git 时，**Open folder** 对话框以及[文件夹设置](/features/chat-conversations/chat-features/conversation-organization#default-terminal-and-working-directory)中的文件夹选择器都会提供 **Clone repository**。输入一个 HTTP(S) 或 SSH 仓库 URL，它会被克隆到当前所在文件夹内一个以仓库命名的新文件夹中，而该新文件夹随即成为选中的文件夹。克隆会在终端上执行 `git clone`，因此终端需要具备 Git、能访问远端网络，并且私有仓库所需的凭据已在终端上配置好。Git 不会提示输入密码，而 SSH 主机必须已经存在于终端的 known hosts 中。

---

## Git

当文件浏览器中打开的文件夹位于某个 Git 仓库内时，Files 标签页底部会出现一个 **Git** 面板。它需要开启工具服务器，并且需要一个支持 Git 的 Open Terminal。点击它即可展开。

- **Changes**：统一或分栏的差异视图，以及 **Hide whitespace**。可以暂存、取消暂存或丢弃文件，带摘要和说明进行提交，以及 **Undo last commit**。
  **Discard changes** 对已暂存、未暂存和新增文件都有效。它会在确认后丢弃某个文件的全部更改，并删除不在上一次提交中的文件。
- **History**：以往的提交及其差异。
- **Pull requests**：对于终端支持的 GitHub 仓库，可以列出、搜索、创建、编辑、评论、批准、请求更改、合并、关闭、重新打开、检出以及标记为就绪。

分支菜单用于切换、创建、重命名和删除分支，以及管理工作树。同步按钮会按分支所需执行发布、拉取、推送或获取。暂存、推送、拉取和获取都会显示进度。拖动文件列表旁的分隔线可以调整其大小。有改动的文件会在文件浏览器工具栏中获得 **Show diff**。

文件列表同样会标记改动。有改动的文件按其状态着色，并显示新增和删除了多少行。有改动的二进制文件会显示一个状态字母，例如 `M`（已修改）或 `U`（未跟踪）。内部有改动的文件夹会带一个彩色圆点。把指针停在标记上可以查看状态以及这些改动是否已暂存。

---

## 实用提示 {#good-to-know}

:::tip 文件会自动更新
当 AI 创建或修改文件时，文件浏览器会自动刷新，无需手动重新加载。
:::

:::tip 记住你的位置
切换聊天时，Files 标签页会打开到该聊天的工作文件夹。选择另一个终端，则会把 Files 标签页移动到该终端的工作文件夹。
:::

:::tip 实时更新
在能报告实时事件的终端服务器上，Git 面板和[浏览器标签页](./use-cases/web-development.md#the-browser-tab)的 **Ports** 列表会实时更新。否则 Git 面板会在展开时刷新，而 **Ports** 列表上有一个 **Refresh** 按钮。
:::

:::tip 终端就在下方
**Files** 标签页底部是[终端面板](./terminal-pane.md)，AI 运行的每条命令各占一个标签页。
:::

:::tip 多个终端
如果你连接了多个终端，在下拉菜单中切换它们，文件浏览器会更新以展示对应终端的文件。
:::

:::info 为每个对话提供独立文件的终端
管理员可以把一个编排终端设置为给每个对话分配各自独立的工作区，因此你在一个聊天中看到的文件与在另一个聊天中看到的并不相同。这类终端要求对话已经存在：文件浏览器会在你发送第一条消息之后出现，而临时聊天中根本不会提供该终端。参见 [Terminal Contexts](/features/open-terminal/terminals/orchestration/contexts)。
:::

## 更多玩法 {#more-things-to-try}

- **[分析文档与数据 →](./use-cases/file-analysis.md)** —— 拖入电子表格或 PDF，向 AI 提问
- **[从聊天运行代码 →](./use-cases/code-execution.md)** —— AI 创建的文件可以直接在这里看到
- **[构建并预览网站 →](./use-cases/web-development.md)** —— AI 创建的文件会出现在文件浏览器中
