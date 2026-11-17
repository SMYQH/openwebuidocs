---
sidebar_position: 1
title: "使用方式"
sidebar_label: "用法"
description: "在对话中启用图像生成、根据提示词创建图像，并在 Open WebUI 中编辑或合成已上传的图片。"
---

在 Open WebUI 对话中，你可以通过提示词生成图像，也可以上传图像并描述你想要的改动。管理员必须先配置好[图像提供商](/features/chat-conversations/image-generation-and-editing)；使用过程中请保持选中你平常的聊天模型。

只有在以下条件全部满足时，聊天中才可以使用图像生成：

- **Settings** > **Images**（管理员区域） 中已启用 **图像生成**。
- 你的角色拥有 **图像生成** 功能权限。管理员始终通过这项检查。
- 模型在 **Workspace** > **Models** > **Edit** 中勾选了 **图像生成** 能力。在旧版模式之外，它的 **内置工具** 能力以及 **图像生成** 内置工具分类也必须保持启用。这些默认都是开启的。
- 该聊天的 **Image** 开关已打开，位于消息输入框的 **+** 菜单中。在模型编辑器中勾选 **默认功能** 下的 **图像生成**，即可让每个新聊天都默认开启。

如果 **+** 菜单中完全没有 **Image**，那么要么是图像生成被全局关闭了，要么是所选模型中有某一个的 **图像生成** 能力未开启，要么是你的角色缺少该权限。引擎自身的 URL 和密钥是另一回事：这两项配错时开关依然会出现，只是生成在运行时失败。

## 使用图像生成 {#using-image-generation}

1. 在消息输入框的 **+** 菜单中打开 **Image**。
2. 输入你的图像生成提示词。
3. 点击 `Send`。

![Image Generation Tutorial](/images/tutorial_image_generation_2.png)

:::warning 继续用你的聊天模型对话
聊天顶部的模型选择器始终停留在你日常使用的聊天模型上。图像模型只需在管理员的图像设置里配置一次，永远不会出现在那里。

把图像模型当作聊天模型是最常见的配置错误。一切看起来都配置妥当，生成却失败或返回无用结果——因为图像模型无法承载对话，而且它并没有按自己预期的方式被要求画图。如果图像生成突然不工作了而设置看起来没问题，先看看模型选择器显示的是什么。

例外情况是：某个聊天模型本身就会创建图像，且它所在的连接的 **API Type** 为 `Responses`，例如通过 OpenRouter 接入的 Gemini 图像模型。它的图像会显示在回复中。
:::

接下来会发生什么取决于 **Function Calling** 模式。它可以在每个聊天中通过 **Model controls** > **Controls** > **Advanced Params** 设置，可以为你自己通过 **设置** > **常规** > **高级参数** 设置，可以在模型编辑器中按模型设置，也可以在管理员模型设置的 **Model Defaults** 下全局设置。上述位置中第一个不是 **Default** 的设置生效；当它们都未设置时则适用 Native。

**Native** 走的是下面描述的工具路径。在 **Legacy** 模式下，只要开关处于开启状态，你发送的每一条消息都会直接进入图像引擎，无论你要求的是什么。当最近的对话中带有图像且 **Image Edit** 已开启时，它会进行编辑而不是新建。在新建路径上，除非你在管理员设置中关闭 **Image Prompt Generation**，否则任务模型会先把你的消息改写为图像提示词。在两种模式下，如果聊天中选中了终端，生成和编辑出的图像也会一并保存到该终端的工作目录，模型因此可以用终端工具继续处理它们。

## 基于原生工具的生成（Agentic） {#native-tool-based-generation-agentic}

如果你的模型配置了 **原生函数调用**（参见 [**工具调用指南**](/features/extensibility/plugin/tools#tool-calling-modes-default-vs-native)），它就可以直接把图像生成功能当作工具调用。

### 工作方式： {#how-it-works}

- **要求：**
  - 必须已在 **Settings → Images**（管理员区域） 中全局启用 **图像生成**
  - 模型必须启用了 **图像生成** capability
- **无需聊天内开关**：在 Native Mode 下，只要模型具备 `image_generation` capability，`generate_image` 工具就会自动加入；无需为每个聊天手动打开
- **自然语言调用**：你可以直接告诉模型：*"生成一张赛博风格森林的图像。"*
- **执行方式**：若 **Native Mode** 已启用且模型具备该能力，模型会调用 `generate_image` 工具
- **显示方式**：生成后的图像会直接显示在聊天界面中
- **编辑支持**：同样支持通过 `edit_image` 工具进行 **图像编辑**（修复 / 局部编辑），例如：*"把这张图里的天空改成红色。"*

这种方式允许模型先“推理”提示词，再执行生成，甚至能在复杂请求中一次生成多张图像。

:::tip

你也可以先编辑 LLM 的回复，把真正的图像提示词改成你想发送的消息，然后再用于图像生成，而不必直接使用模型原始回复内容。

:::

:::info
**旧版 “生成图像” 按钮：**
自 Open WebUI v0.7.0 起，原生的 “Generate Image” 按钮（允许直接从消息内容生成图像）已被移除。如果你想恢复该功能，可以使用社区构建的 **[Generate Image Action](https://openwebui.com/posts/3fadc3ca-c955-4c9e-9582-7438f0911b62)**。
:::

## 恢复 “Generate Image” 按钮 {#restoring-the-generate-image-button}

如果你更喜欢“点击任意消息上的按钮，就从该消息内容生成图像”的工作流，可以轻松恢复：

1. 访问 Open WebUI Community 上的 **[Generate Image Action](https://openwebui.com/posts/3fadc3ca-c955-4c9e-9582-7438f0911b62)**
2. 点击 **Get** 将其导入到你的本地实例（或复制代码后粘贴到本地实例中）
3. 导入后，前往 **Admin Panel** > **Functions**，确认 **Generate Image** action 已启用

该 action 会在消息操作栏中加入一个 “生成图像” 图标，让你可以直接根据 LLM 回复生成图像——这在你希望先让助手迭代优化提示词、满意后再执行生成时会很有帮助。

:::info
**要求：** 图像编辑需满足本页顶部列出的相同条件。若要使用 **图像编辑** 或 **图像 + 图像生成**，还需在 **Settings** > **Images**（管理员区域）的 **编辑图像** 部分开启 **图像编辑**，并配置编辑引擎（`Default (Open AI)`、`ComfyUI` 或 `Gemini`）以及支持 inpainting 或 img2img 的模型。
:::

## 图像编辑（Inpainting） {#image-editing-inpainting}

你可以在聊天中直接通过“图像 + 文本提示词”的方式编辑图片。

1. **上传一张图片** 到聊天中
2. **输入提示词** 描述你想要的改动（例如 “把背景改成日落” 或 “加一顶帽子”）
3. 模型会根据你的提示词生成该图片的新版本。

当聊天中选中了管理员添加的 [Open Terminal](/features/open-terminal) 或 [Tether](/ecosystem/tether) 终端时，模型还可以编辑存放在该终端中的任意图像，无论 [Chat Uploads](/features/open-terminal/setup/connecting#chat-uploads) 被设置成什么。它会把这些图像的绝对路径传给 `edit_image`，Open WebUI 则使用你对该终端的访问权限、在聊天所用的同一个工作区中读取它们。每张图像必须是 PNG、JPEG、WebP 或 GIF 格式，且不超过 2500 万像素和 50 MB。

## 图像合成（多图融合） {#image-compositing-multi-image-fusion}

你可以将多张图片无缝融合成一个统一场景——这在专业上通常称为 **图像合成** 或 **多图融合**。你可以把不同来源中的元素（例如一张图中的主体和另一张图中的背景）组合起来，同时协调光照、透视和风格。

1. **上传多张图片** 到聊天中（例如上传一张主体图和一张背景图）
2. **输入提示词** 描述你想要的合成效果（例如 “把这些图片合成一只坐在公园长椅上的猫，并保持光照一致”）
3. 模型会根据你的说明生成一张新的合成图像。
