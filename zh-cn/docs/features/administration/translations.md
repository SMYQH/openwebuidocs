---
sidebar_position: 14
title: "界面翻译"
---

# 界面翻译 {#translations}

Open WebUI 会把自己的界面翻译成多种语言，但你在其中创建的内容——模型名称、工具描述、横幅文字等——都按你输入的原样保存。翻译功能让你可以为每种语言保存一份对应的文本版本，这样以德语阅读界面的用户会看到德语的模型名称和德语的提示建议，而其他人仍然看到原文。

没有任何内容会被自动翻译。每一个版本都由你亲自撰写，或导入别人准备好的文件。

与此分开的是，管理员可以覆盖 Open WebUI 自身的界面措辞，也就是应用自带的按钮和标签。这正是本页底部的[界面文本](#interface-text)。

---

## 可以翻译什么 {#what-can-be-translated}

| 资源 | 字段 | 位置 |
| :--- | :--- | :--- |
| **模型** | 名称、描述、提示建议、模型控件与选项名称 | Workspace > Models 中的模型编辑器。参见[模型](/features/workspace/models#translations) |
| **Tools** | 名称、描述、valve 标签 | Workspace > Tools 中的工具编辑器 |
| **技能** | 名称、描述 | Workspace > Skills 中的技能编辑器 |
| **Functions** | 名称、描述、valve 标签、各动作标签 | Admin Panel > Functions 中的函数编辑器 |
| **横幅** | 内容（不含标题） | Settings > General（管理员区域） 中 Banners 标题旁 |
| **竞技场模型** | 名称、描述 | Settings > Evaluations（管理员区域） 中的竞技场模型对话框 |
| **默认提示建议** | 建议内容本身 | Settings > Models > Model Defaults（管理员区域） |
| **Open WebUI 自身的界面** | 应用自带的任意字符串 | Settings > General（管理员区域） 中的 UI Translations。参见[界面文本](#interface-text) |

---

## 语言选择器 {#the-language-selector}

每个支持该功能的编辑器都有一个地球图标选择器。它默认停在 **Default**（即原文），选择某种语言后编辑器会切换到该语言：各字段中保存的是译文，原文则作为占位文本显示。切回 **Default** 即可再次编辑原文。

Open WebUI 提供的每一种语言都在列表中，包括英语。**Default** 不是一种语言，它就是原文，普通字段中保存的正是它。选择 `en-US` 会存储一份英语译文，让英语读者看到的是它而不是原文，这通常不是你想要的：除非你确实想为英语单独准备一套措辞，否则请让英语保持在 **Default**。

在资源编辑器中，已经填写了内容的语言会标上 `*`，你可以一眼看出哪些已经翻译过。

在模型编辑器、横幅列表和竞技场对话框中，已翻译的字段旁边有两个小按钮：**Copy default** 会把原文填入作为起点，**Use default** 会清空译文从而重新使用原文。Tool 和技能的名称与描述没有这些按钮，直接在字段中输入即可，清空字段就能回到原文。

![切换到德语的模型编辑器，其中的名称、描述和提示建议都已翻译](/images/features/translations/model-editor-translations.png)

---

## 用户会看到哪个版本 {#which-version-a-user-sees}

Open WebUI 按用户界面的语言依次选择：

1. 完全匹配的语言，例如 `de-DE`
2. 基础语言 `de`，因此一份 `de` 译文可以覆盖 `de-DE` 与 `de-AT`
3. 原文

留空的字段在保存时会被丢弃，因此空译文等同于没有译文，原文会直接显示出来。只翻译重要的内容，其余保持原样。

译文会跟随该资源出现在所有显示它的位置：模型与工具选择器、新建聊天界面、`@`、`$` 和 `/` 菜单、**+** 菜单、模型控件面板、回复下方的操作按钮、侧边栏以及工作区列表。工作区搜索同时匹配译文名称和原文，因此搜其中任意一个都能找到它。

---

## 翻译 valve 标签 {#translating-valve-labels}

Tool 和 Function 带有 [valves](/features/extensibility/plugin/development/valves)，也就是由管理员或用户填写的设置项。这些标签同样可以翻译，其中用户 valve 最为关键，因为普通用户在聊天的 **Model controls > Controls** 下看到的就是它们。

在工具或函数编辑器中选择一种语言，代码编辑器就会被替换成一张翻译表，列出该插件暴露的每一个标签（管理员 valve 与用户 valve 都有）。每一行显示键、原文以及一个填写译文的输入框，并带有一个箭头按钮用于把该行清回原文。

![工具编辑器中的 valve 翻译表，含键、原文和德语译文](/images/features/translations/tool-valve-translations.png)

键的命名遵循其所属 valve 的形状：

| 键 | 标注的内容 |
| :--- | :--- |
| `valves.<field>.title` | 管理员 valve 的标签 |
| `valves.<field>.description` | 它的帮助文本 |
| `valves.<field>.enum.<value>` | 下拉 valve 的一个选项 |
| `user_valves.<field>.` | 用户 valve 的同样三种形状 |
| `actions.<action_id>.name` | Function 暴露的某个动作的标签 |
| `actions.<action_id>.description` | 该动作的提示文字 |

动作键不会自动列出。用 **+** 按钮自行添加即可。

只有标签会改变。valve 名称、存储的值和默认值都不受影响，因此翻译后的插件与未翻译的插件行为完全一致。

### 导入与导出 {#importing-and-exporting}

**Export** 会把当前语言下载为一个由键和文本对组成的 JSON 文件，文件名由插件名和语言名组成，并跳过你留空的内容。**Import** 会重新读取该文件，这是把文件交给翻译者、或把一套译文复制到另一个实例的实用做法。

导入内容在接受前会被校验。每个值都必须是字符串，且原文中的任何 `{{ placeholder }}` 都必须出现在译文中，这样译文就不会悄悄丢掉要被替换进去的值。未通过任一校验的文件会被拒绝，并指出有问题的键，同时不会产生任何改动。

该表还有一个搜索框和一个 **Modified** 过滤器，可只显示你真正翻译过的行——这就是在 valve 众多的插件中找出剩余工作的方法。

---

## 翻译模型控件 {#translating-model-controls}

模型的[控件](/features/workspace/models#model-controls)带有人们在聊天中会读到的名称：控件名称、描述以及每个选项的名称。在模型编辑器中选择一种语言，**Model controls** 行会列出它们，原文作为占位文本显示。**Use default** 会一次性清空该语言的所有控件译文。

译文与模型的其他译文一起存放在 `meta.i18n` 中，每种语言一张映射表，使用下列键：

| 键 | 标注的内容 |
| :--- | :--- |
| `model_controls.<key>.label` | 控件名称 |
| `model_controls.<key>.description` | 它的帮助文本 |
| `model_controls.<key>.options.<value>.label` | 某个选项的名称 |

`<key>` 是控件的 ID，`<value>` 是选项的 ID，与 API 在 `params.model_controls` 下使用的 ID 相同。只有名称会变；每个选项发送的参数在所有语言中保持不变。

---

## 横幅 {#banners}

横幅内容在 **Settings > General**（管理员区域） 中翻译，同样使用 Banners 标题旁的地球图标选择器。每条横幅都会保留其原始内容以及每种语言的一个版本，用户看到的是与其界面语言匹配的那一份。

![正在以德语编辑的横幅，语言选择器位于 Banners 标题旁](/images/features/translations/banner-translations.png)

这取代了以往把多种语言塞进同一条横幅的做法。把它们写成翻译，意味着每位用户读到的都是一条用自己语言写的消息，而不是一堆消息的堆叠。参见[横幅](/features/administration/banners)。

---

## 界面文本 {#interface-text}

以上内容都关于你自己创建的东西。这一节讲的是 Open WebUI 自身的措辞：应用自带的按钮、标签和提示信息。

打开 **Settings > General**（管理员区域） 并找到 **UI Translations**。每一行都是一对内容：左侧是应用实际使用的英文原文，右侧是你希望改为显示的内容。选择器决定右栏属于哪种语言，初始为当前阅读界面所用的语言。

这些覆盖项会合并到 Open WebUI 自带的语言文件之上。你覆盖的生效，未覆盖的保留原有措辞，因此改动一个词并不需要提供一整份目录。

![UI Translations 面板，其中三个界面字符串已被替换](/images/features/translations/ui-translations.png)

在界面上的效果如下：

![显示替换后标签的侧边栏](/images/features/translations/ui-translations-effect.png)

:::warning 语言必须完全匹配
这一部分不像资源翻译那样会回退。存放在 `en-US` 下的覆盖项对使用 `en-GB` 阅读界面的人毫无作用，存放在 `de` 下的对 `de-DE` 也同样如此。请在你的用户实际使用的每一个语言代码下都存放该覆盖项，否则这项改动会悄无声息地不生效。
:::

在这里英语也算一种语言，因此这也是为所有人改名的办法：左侧填 `Knowledge`，右侧填 `Library`，以英语保存，整个界面就都会显示 Library。

**左侧必须与原始字符串完全一致**，包括大小写和标点。它是应用查找时使用的键，差一点就永远匹配不上，结果是什么都不会变。

保存时会强制执行若干规则，违反其中任何一条的保存都会被拒绝，并指出有问题的条目：

- 替换内容必须是文本。留空会被丢弃，这也是移除某个覆盖项的方式。
- 原文中的任何 `{{ placeholder }}` 也必须出现在替换内容中，这样改写后的字符串就不会丢掉要被替换进去的值。
- 同一段原文不能出现在两行中。
- `__proto__`、`prototype` 和 `constructor` 不能作为语言或原文字符串。

某一行上的 **Delete** 只会移除选择器中所选语言的替换内容，其提示文字会标明该语言。其他语言的替换内容会保留，当没有任何替换内容剩下时，这一行就会消失。

你自己的会话会在保存的瞬间更新。其他人则会在他们的浏览器下次加载 Open WebUI 时看到这项变更。

### 通过 API 设置 {#setting-it-through-the-api}

这些覆盖项以 `I18N` 的形式存放在管理配置中，结构是从语言到"原文到替换内容"映射的映射，通过 `POST /api/v1/auths/admin/config` 发送，并可从 `/api/config` 以 `i18n` 读取。那里同样强制执行上述规则。

请求中省略 `I18N` 会保留已存储的内容，因此写入其他管理设置的集成不会意外清空这些覆盖项。发送 `{}` 则会清空它们。

---

## 说明 {#notes}

- 译文与资源本身一起保存，因此导出模型、工具或技能时会一并带出。
- 界面语言未被你翻译过的用户会看到原文，而不会看到空白字段。
- 这里的一切都不会改变模型收到的内容。模型得到的仍然是原始系统提示、原始 valve 值和原始工具规格，因此翻译一段描述不会改变任何行为。
