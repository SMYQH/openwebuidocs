---
sidebar_position: 1
title: "检索增强生成 (RAG)"
---

import ThemedImage from '@theme/ThemedImage';
import useBaseUrl from '@docusaurus/useBaseUrl';

<ThemedImage
  alt="文档：一叠纸张，其中一张被抽出"
  sources={{
    light: useBaseUrl('/images/banners/chat-conversations-documents-light.svg'),
    dark: useBaseUrl('/images/banners/chat-conversations-documents-dark.svg'),
  }}
  style={{ width: '100%', margin: '0.25rem 0 1.75rem' }}
/>

:::warning

如果你正在使用 **Ollama**，请注意它**会根据 GPU 的显存来选择模型的默认上下文长度，在显存小于 24 GiB 的 GPU 上这个值是 4096 个 token**（参见 [Ollama 的上下文长度文档](https://docs.ollama.com/context-length)）。这会严重限制**检索增强生成 (RAG) 的性能**，特别是对于网络搜索，因为检索到的数据可能**根本不会被使用**或仅被部分处理。

:::

检索增强生成 (RAG) 是一种通过结合不同来源的上下文来增强聊天机器人对话能力的技术。它的工作原理是从广泛的来源检索相关信息，如本地和远程文档、网页内容，甚至像 YouTube 视频这样的多媒体来源。然后将检索到的文本与预定义的 RAG 模板结合，并作为用户提示词的前缀，从而提供更丰富且与上下文更相关的响应。

RAG 的主要优势之一是它能够访问并整合来自多种来源的信息，使其成为复杂对话场景的理想解决方案。例如，当用户提出与特定文档或网页相关的问题时，RAG 可以检索该来源的相关信息并将其融入到对话响应中。RAG 还可以检索并整合来自 YouTube 视频等多媒体来源的信息。通过分析这些视频的转录或字幕，RAG 可以提取相关信息并将其整合到对话响应中。

## 本地和远程 RAG 集成 {#local-and-remote-rag-integration}

要在 RAG 中使用本地文档，可在**工作区 > 知识**中将其添加到知识库，或直接上传到聊天。在聊天中查询时，请在查询前输入 `#`，从消息输入框上方的建议列表中选择文档。

![文档与检索设置](/images/admin/admin-documents.png)

:::tip 批量文件管理
需要清理多个已上传的文档或审计您的存储？您现在可以使用位于 **设置 > 数据控制 > 管理文件 (Settings > Data Controls > Manage Files)** 的集中式**[文件管理器](/features/chat-conversations/data-controls/files)**。在那里删除文件将自动清理其相应的 RAG 嵌入数据。
:::

## 外部知识源（外部向量数据库） {#external-knowledge-sources-external-vector-databases}

:::warning 实验性
此功能为实验性，其配置可能在不同版本之间发生变化。
:::

你可以将知识库指向一个你已维护的**外部向量数据库**，而非在 Open WebUI 内部上传和嵌入文档。Open WebUI 在查询时直接访问该数据库，因此你的文档、嵌入向量和索引保留在你自己的存储中，无需重新导入。

支持的提供商：**兼容 OpenAI**（OpenAI 向量存储、Azure OpenAI v1 和 LiteLLM）、**Qdrant**、**Milvus** 和 **pgvector**。对于 Qdrant、Milvus 和 pgvector，Open WebUI 镜像中必须包含对应提供商的 Python 客户端，例如 `qdrant-client` 或 `pymilvus`。支持的 Qdrant 服务端版本见 [Qdrant 设置](/reference/env-configuration#qdrant)。

### 使用兼容 OpenAI 的向量存储 {#using-openai-compatible-vector-stores}

服务器使用创建存储时的嵌入模型执行搜索。输入**端点**（Azure OpenAI 使用 `/openai/v1` URL）及 **API 密钥 / 令牌**，然后点击**验证连接**加载存储列表。一个知识库可使用一个或多个已加载的存储。

如果无需逐个创建知识库，可在添加连接时开启**将存储列为知识库**，以提供该端点下的存储。**存储 ID** 中指定的存储（留空表示全部）会作为只读知识库实时显示在**工作区 > 知识**中。访问权限在连接上设置，对其所有存储生效。关闭此开关时，只有**测试查询**成功返回文档后，才能创建知识库。

### 添加外部知识源 {#adding-an-external-knowledge-source}

下列步骤适用于 Qdrant、Milvus 和 pgvector。在**设置 > 集成 > 外部知识源**（管理员区域）配置：

1. **创建连接**到你的向量数据库：
   - **提供商**（Qdrant / Milvus / pgvector）
   - **端点**（数据库 URL）
   - **API Key / Token**（如果数据库需要认证）
   - **数据库**/**表**/**集合**（取决于提供商）
   - **超时**
2. **映射结果字段**，使 Open WebUI 知道如何读取你的记录。每个设置将存储文档中的字段映射到 Open WebUI 期望的字段：

   | Open WebUI 字段 | 映射设置 | 默认字段 |
   | :--- | :--- | :--- |
   | 文本块 | **内容字段** | `content` |
   | 标题 | **标题字段** | `title` |
   | 来源 | **来源字段** | `source` |
   | URL | **URL 字段** | `url` |
   | 文档 ID | **文档 ID 字段** | `document_id` |
   | 页码 | **页码字段** | `page` |
   | 额外元数据 | **元数据字段** | `metadata` |
   | 相关性评分 | **评分字段** | `score` |

   嵌套字段支持点号路径（例如 `payload.text`）。
3. **测试查询**，使用样本问题。Open WebUI 会针对该源执行实时检索并显示结果。成功测试后才能创建或保存该源。

创建后，外部来源会像其他知识库一样出现在**工作区 > 知识**中，可附加到模型或聊天。对于 Qdrant、Milvus 和 pgvector，聊天时 Open WebUI 使用配置的 RAG 嵌入模型将用户查询转为向量，在外部数据库中执行向量搜索，并把最匹配的结果放入提示词。Open WebUI 不保存文档副本。

启用[检索查询生成](/reference/env-configuration#enable_retrieval_query_generation)后，所有生成的查询会同时运行。它们的结果按排名合并（先取每个查询的第一条结果，再取每个查询的第二条，以此类推），重复项会被丢弃，列表会被裁剪到结果数量。

回答下方的来源按标题列出各项结果。对于 Qdrant、Milvus 和 pgvector，如果结果的**来源字段**包含网址，点击标题或引用中的**内容**链接即可打开该页面。否则标题显示为纯文本。

:::info 嵌入模型必须匹配
对于 Qdrant、Milvus 和 pgvector，Open WebUI 会将查询转为向量，并在数据库中执行向量搜索。因此，外部数据库存储的向量必须由 Open WebUI 所用的**同一个嵌入模型**生成，模型和维度都必须一致。嵌入不匹配时，结果质量很差或毫无意义。
:::

## 用于 RAG 的网络搜索 {#web-search-for-rag}

:::warning
**致 Ollama 用户的上下文长度警告：** 即使经过内容提取，网页通常包含 4,000-8,000 多个 token，包括主要内容、导航元素、页眉、页脚和元数据。如果只有 4096 个可用 token，往往只能获得约一半的页面内容，可能遗漏最相关的信息。即使有 4096 个 token，也往往不足以全面分析网页内容。

**修复方法：** 导航至 **Settings > Models**（管理员区域）中（您的 Ollama 模型的）铅笔图标（**Edit**），打开 **Advanced Params** 并**将上下文长度增加到 8192+（或最好超过 16000）个 token**。此设置特别适用于 Ollama 模型。对于 OpenAI 和其他集成模型，请确保您使用的是具有足够内置上下文长度的模型（例如，拥有 1M token 上下文窗口的 GPT-5.6）。
:::

要引用网页内容，在聊天中先输入 `#`，再输入目标 URL，点击聊天输入框上方显示的格式化 URL。Open WebUI 会尝试获取并解析该 URL 的内容。PDF 等文件链接通过文档提取来读取。如果无法读取该 URL，提示会指出失败的链接。参见[附加链接或 YouTube 视频失败](/troubleshooting/rag#14-attaching-a-link-or-a-youtube-video-fails)。

:::tip

网页通常包含诸如导航和页脚等无关信息。为了获得更好的结果，请链接到该页面的原始或适合阅读的版本。

:::

## RAG 模板自定义 {#rag-template-customization}

从 `Settings` > `Documents`（管理员区域）菜单自定义 RAG 模板。

RAG 模板用于格式化**检索到的上下文**，并会在消息到达模型之前作为前缀附加到你的消息上。请使用 `{{CONTEXT}}` 占位符（或旧版的 `[context]`）来标记检索到的文档上下文插入的位置。没有它，检索到的上下文就无处安放。

:::warning 不要包含查询占位符
你的消息（即查询）**始终会自动追加**在渲染后的模板之后，因此模型已经能看到它一次。模板同样能识别 `{{QUERY}}` / `[query]` 并在那里替换查询，但由于查询随后仍会被追加，写入该占位符会让查询在最终提示词中出现**两次**。请把 `{{QUERY}}` / `[query]` 从模板中去掉：它是检索上下文的包装器，而不是用来安放查询的位置。
:::

## Markdown 标题拆分 {#markdown-header-splitting}

启用后，文档会先按 Markdown 标题（H1-H6）拆分。这能保留文档结构，并尽可能把同一标题下的各小节保留在一起。得到的文本块随后再由标准的字符或 token 切分器进一步处理。

:::tip

使用 **最小块大小目标** 设置（位于 **设置 > 文档**（管理员区域））可以在 Markdown 拆分之后智能合并过小的段落，从而提升检索连贯性并减少数据库中的向量总数。

:::

## 语块化配置 {#chunking-configuration}

Open WebUI 允许您微调文档如何被拆分成块以进行嵌入。这对于获得最佳检索性能至关重要。

- **文本分割器 (Text Splitter)**：决定如何度量语块大小。[`RAG_TEXT_SPLITTER`](/reference/env-configuration#rag_text_splitter) 可取 `character`（默认，RecursiveCharacterTextSplitter）、`token` 或 `token_transformers`。`token` 分割器使用 Tiktoken 计算 token；`token_transformers` 分割器使用由 [`RAG_TOKENIZER_MODEL`](/reference/env-configuration#rag_tokenizer_model) 指定的 HuggingFace 分词器（例如 `bert-base-uncased`）计算，从而让语块边界与你的嵌入模型自身的分词器保持一致。它在 slim 镜像上不可用。
- **Chunk Size (语块大小)**：设置每个语块的最大字符（或 token）数。
- **Chunk Overlap (语块重叠)**：指定相邻语块之间共享多少内容以维持上下文。
- **Chunk Min Size Target (语块最小尺寸目标)**：尽管 [Markdown 标题拆分](#markdown-header-splitting) 在保留结构方面非常出色，但它通常会产生微小且碎片化的语块（例如，独立的副标题、目录条目、单句段落或短列表项），这些语块缺乏足够的语义上下文来进行高质量嵌入。您可以通过设置 **Chunk Min Size Target** 智能合并这些小片段及其相邻片段来解决此问题。

### 为什么使用 Chunk Min Size Target？ {#why-use-a-chunk-min-size-target}

在 markdown 拆分后智能合并较小的章节可提供几个主要优势：

- **提高 RAG 质量**：消除微小、无意义的片段，确保每个检索到的语块都有更好的语义连贯性。
- **减小向量数据库大小**：更少的语块意味着需要存储的向量更少，从而降低存储成本并减少内存使用。
- **加快检索和嵌入速度**：较小的索引搜索速度更快，且较少的语块需要的嵌入 API 调用更少（或更少的本地计算资源）。这在向聊天或知识库上传文件时显着加速了文档处理，因为需要向量化的数据较少。
- **效率和影响**：测试表明，良好配置的阈值（例如，针对 2000 的块大小设置 1000 的阈值）可以使语块数量减少 90% 以上，同时**提高准确性**，加快嵌入速度，并通过维护语义上下文提高整体检索质量。

<details>
<summary>合并算法的工作原理（技术细节）</summary>

对于大多数用户，上述解释已足够：小语块与其邻居合并，可以用更少的向量获得更好的检索结果，并在性能、成本和存储方面带来好处。但如果您好奇确切的逻辑和设计理念，以下是它的内部工作机制。

### 为什么基于标题的拆分需要合并 {#why-header-based-splitting-needs-merging}

Markdown 标题拆分是一种较好的结构化分块方法，因为标题是文档作者放置的明确语义边界。您利用了人类对于一个主题在哪里结束和另一个主题在哪里开始的判断，这通常比可能在段落中间或思想中间切断的固定大小窗口化产生更连贯的块。

然而，真实的文档通常具有结构上的特性：目录、简短的介绍章节、在自己标题下的单句段落或内容极少的深层嵌套副标题。这些会产生造成问题的微小语块：

- 它们缺乏足够的上下文，在被单独检索时用处不大
- 它们会产生嘈杂的检索结果（在有限信号上匹配但没贡献什么有用信息）
- 非常短的文本有时嵌入可靠性较低
- 它们浪费向量存储空间并减慢检索速度
- 许多语块的嵌入时间比具有相同总内容的更少语块的嵌入时间要长
- 更多的嵌入操作意味着更多的 API 调用（成本）或更多的本地计算

合并算法通过在遵守文档结构和大小限制的同时智能地组合过小的块来解决这个问题。

### 算法：单次前向传递 {#the-algorithm-a-single-forward-pass}

合并逻辑特意设计得很简单——对所有语块进行一次单向前向传递：

1. 以第一个语块作为“当前”累加器开始。
2. 对于每个**后续**语块，检查它是否可以被吸收到当前语块中。
3. 如果满足**所有三个条件**，则可以吸收该语块：
   - 当前累加的内容仍低于 `CHUNK_MIN_SIZE_TARGET`
   - 合并不会超过 `CHUNK_SIZE`（最大值）
   - 两个语块属于同一源文档
4. 如果可以吸收，合并它们（使用 `\n\n` 分隔以保留视觉结构），然后继续检查下一个语块。
5. 如果无法吸收，确定当前语块，并以下一个语块作为新的累加器重新开始。
6. 重复，直到处理完所有语块。

**关键点**：大小检查是针对*累加*内容的，而不是单独的块。这意味着多个连续的微小块（如具有许多小条目的目录）将不断折叠在一起，直到合并后的大小达到阈值，或者直到合并下一个语块会超过最大值。

### 设计决策及其重要性 {#design-decisions-and-why-they-matter}

**仅向前合并**：小语块总是向*下一个*语块合并，从不向后。这使得逻辑简单且可预测，并保留了文档中常见的“本节介绍后续内容”的自然关系。向它引入的内容前向合并的一小段介绍语在语义上是合理的。

**为什么不向后合并？** 除了增加代码复杂性之外，向后合并无论如何经常会失败。在任何语块最终确定时，它处于两种状态之一：要么它通过吸收增加达到或超过 `CHUNK_MIN_SIZE_TARGET`（因此它已经“满足”了并且余量有限），要么它无法吸收下一个语块，因为那会超过 `CHUNK_SIZE`（因此它已经碰到了天花板）。无论哪种方式，向后合并尝试通常会在大小检查上失败，这意味着你要为一个很少成功的动作添加分支逻辑和状态跟踪。

**没有跨文档合并**：不同源文件中的块从不合并，即使两者都很小。这保留了清晰的文档边界，以便引用、标明来源和提供检索上下文。

**遵守最大大小**：如果合并两个语块会超过 `CHUNK_SIZE`，则两者保持独立。绝不通过丢弃内容来强制合并。

**元数据继承**：合并后的语块继承合并序列中*第一个*语块的元数据。这与向前合并的语义是一致的——源和标题信息反映了合并部分“开始”的位置，对于检索和引用目的，这通常是正确的选择。

**`\n\n` 分隔符**：当语块合并时，它们通过两个换行符连接，而不是直接连接。这在组合文本中保留了视觉和结构上的分隔，如果您要检查块的话，这对嵌入质量和人类可读性都很重要。

### 边缘情况 {#edge-cases}

**连续的微小语块**：处理得很自然。它们不断积累成一个单一的语块，直到达到阈值或最大尺寸被超过。

**小语块后跟大语块**：如果小语块后跟一个语块大到合并会超过 `CHUNK_SIZE`，那么小语块就会按原样确定下来，仍然不足尺寸。如果不向后合并或内容拆分，这是不可避免的，但在实践中也很罕见。它通常发生在自然的语义边界（密集章节前的简短过渡），并且在边界处将小语块独立保留其实也是正确的。

**文档中的最后一个语块**：如果最后一个语块尺寸不足，由于它没有可以向前合并的内容，它将保持较小尺寸。这同样也是不可避免且通常是可以接受的——文档的结尾是自然的边界。

### 性能特征 {#performance-characteristics}

该算法的复杂度为语块数量的 O(n)——一次遍历，不进行前瞻或回溯。这使得即使对于大型文档集，它也能保持快速。

在某些方面，合并带来的效率提升呈非线性扩展。在 45 个向量而不是 588 个向量中进行检索不只是计算速度加快约 13 倍，您还会获得更清晰的 top-k 结果，因为您已经消除了可能在部分关键字匹配中得分很高但对 LLM 没有有益贡献的近乎空白语块的噪音。质量的提升通常比速度的提升更重要。

合并后保留的每个语块都包含有意义的上下文，而不是干扰嵌入模型和检索排序的零散片段。

</details>

## RAG 嵌入支持 {#rag-embedding-support}

在 **Settings** > **Documents**（管理员区域）中更改 RAG 嵌入模型。嵌入引擎可以是内置的 SentenceTransformers 默认值、Ollama、OpenAI 或 Azure OpenAI。

如果你的嵌入模型文档要求搜索查询使用一个前缀、存储文本使用另一个前缀，请在同一页面的 **Embedding** 部分、**Advanced** 之下分别以 **Query Prefix** 和 **Content Prefix** 填写。它们对应 [`RAG_EMBEDDING_QUERY_PREFIX`](/reference/env-configuration#rag_embedding_query_prefix) 和 [`RAG_EMBEDDING_CONTENT_PREFIX`](/reference/env-configuration#rag_embedding_content_prefix)。请包含模型所期望的尾部空格。Ollama、OpenAI 和 Azure OpenAI 会把前缀加到每段文本的开头，除非 [`RAG_EMBEDDING_PREFIX_FIELD_NAME`](/reference/env-configuration#rag_embedding_prefix_field_name) 把它作为单独的请求字段发送。内置引擎则把它作为 `prompt` 传给 SentenceTransformers。更改 **Content Prefix** 后请为已有文档重建索引，因为改动之前嵌入的文档仍保留旧前缀。

## 初始设置后更改 RAG 设置 {#changing-rag-settings-after-initial-setup}

如果您需要在文件已经建立索引之后更改切块配置（语块大小、重叠）或嵌入模型，理解您需要采取的行动以及这些变更的后果非常重要。

### 更改 Chunk Size 和 Overlap {#changing-chunk-size-and-overlap}

新文档将**自动**使用更新后的语块大小和重叠设置——新上传的文件无需执行任何操作。

知识库中已有的文档会**保留它们原本的切块配置**，直到您执行一次重建索引 (re-index)。对于这些旧块来说，检索仍能正常工作（向量相似性搜索不依赖于语块大小），但如果新旧文档之间语块大小差异很大，您可能会注意到检索质量不一致。

:::tip
如果您仅更改了分块设置而未更改嵌入模型，则不强制要求重新索引——旧文档将继续起作用。然而，为确保所有文档之间的检索质量保持一致，建议运行重新索引。
:::

### 更改嵌入模型 (Embedding Model) {#changing-the-embedding-model}

更改嵌入模型**需要对所有知识库文档进行重新索引**。不同模型产生的嵌入存在于不同的向量空间，互不兼容。不重新建立索引，针对旧嵌入进行检索将产生糟糕甚至荒谬的结果。

更改嵌入模型后，在管理员区域的 **Settings** > **Documents** 中点击 **Reindex**，用新模型重新生成所有知识库文档的嵌入。

### 重建索引会做什么？ {#what-does-re-indexing-do}

重建索引过程对每个知识库执行如下步骤：

1. **删除**该知识库现有的向量集合。
2. 使用当前的内容提取引擎及其设置，从原始上传文件**重新提取**每个文件。
3. 使用当前的语块大小、重叠和文本分割设置，**重新切分**所有文件。
4. 使用当前配置的嵌入模型，**重新生成嵌入**所有块。
5. 同时**重建**知识库中每个文件的逐文件集合，这样单独把某个文件附加到聊天中时，检索到的内容与在它所属的知识库中搜索时相同。

这意味着，一次重建索引能同时应用内容提取、分块设置和嵌入模型变更。

:::note 重建索引会重新解析文件
每个文件都会再次经过内容提取引擎，因此在嵌入之外还要预留内容提取的时间。在知识库文件查看器中编辑过的文本会被新的提取结果替换。音频、图片和视频文件会保留其已存储的文本，原始文件缺失或提取失败的文件同样如此。
:::

:::warning 重新索引不涵盖聊天文件
重新索引操作仅处理属于**知识库**的文件。直接上传到对话中（而未加入任何知识库）的文件拥有单独的逐文件向量集合，这些集合不受重新索引操作的影响。

如果您更改了嵌入模型，那些独立对话文件的嵌入依然使用旧模型，并且它们的检索质量会下降。更新它们的唯一方法就是重新上传文件。
:::

### 总结 {#summary}

| 变更项 | 新文档 | 知识库文档 (未重建索引) | 知识库文档 (重建索引后) | 独立聊天文件 |
|---|---|---|---|---|
| **Chunk Size / Overlap** | ✅ 使用新设置 | ⚠️ 旧块依然可用，但质量可能不一 | ✅ 使用新设置重新切块 | ⚠️ 仍为旧块，需重新上传更新 |
| **Embedding Model** | ✅ 使用新模型 | ❌ 仍为旧嵌入，向量空间不兼容 | ✅ 使用新模型重嵌 | ❌ 仍为旧嵌入，需重新上传更新 |

### 危险区域重置按钮 {#danger-zone-reset-buttons}

**设置** > **Documents**（管理员区域）底部的**危险区域**有两个重置按钮。两者都作用于实例上的每个用户，且都无法撤销。

| 按钮 | 删除什么 | 保留什么 |
|---|---|---|
| **Reset Upload Directory** | 每条文件记录、每个已存储文件（上传目录，或所用的 S3、GCS 或 Azure 存储）以及向量存储 | 知识库（此时不再有文件和向量）和记忆（记忆不再有向量） |
| **Reset Vector Storage/Knowledge** | 向量存储和每个知识库 | 已上传的文件和记忆（它们不再有向量） |

使用默认的 Chroma 向量数据库时，重置向量存储会删除所有集合：知识库、单个文件、缓存的网页搜索结果和用户记忆。记忆保留其文本，因此在同一部分执行 **Reindex Knowledge and Memory Vectors** 即可用当前的嵌入模型重建它们的向量。被 **Reset Vector Storage/Knowledge** 删除的知识库已经不存在，因此没有可重建索引的对象。

## RAG 功能中的引用（Citations） {#citations-in-rag-feature}

RAG 功能允许用户轻松追踪投喂给 LLMs 的文档上下文，并带有用于参考定位的引用信息。这确保了在您的对话中使用外部来源信息的透明度和问责机制。若要让模型引用页码或每个分块随附的其他细节，请设置 [`RAG_SOURCE_METADATA_KEYS`](/reference/env-configuration#rag_source_metadata_keys)。

## 预加载文件与内置工具 {#preload-files-vs-builtin-tools}

Open WebUI 提供两项分别控制文件处理方式的能力。理解它们之间的区别对于正确配置模型很重要。

### 预加载文件能力 {#preload-files-capability}
**预加载文件 (Preload files)** 能力控制 Open WebUI 是否对附件文件执行 RAG（检索增强生成）。在原生函数调用下它默认关闭，在旧版下默认开启。模型编辑器和 **模型默认值** 会显示其生效值。对于不是来自网页界面聊天的 API 请求，除非模型为它保存了某个值，否则它是开启的，因此放在 `files` 字段中的文件和知识可以到达模型。

| 预加载文件 | 行为表现 |
|--------------|----------|
| **启用** | 通过 RAG 处理附加的文件。检索内容并将其注入到对话上下文中。 |
| **禁用** | 文件内容永远不会被提取或注入。在原生或默认函数调用下，模型会看到附加文件的列表，并通过内置 **Files** 工具读取它们（`list_chat_files`、`query_chat_files`、`grep_chat_files`、`view_file`、`display_file`）。这些工具需要 **Files** 内置工具类别、模型的 **File Upload** 能力以及用户的上传权限。 |

**何时禁用预加载文件：**
- **完全绕过 RAG**：当你完全不希望 Open WebUI 处理附加文件时。
- **仅使用[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)**：如果你更倾向于让模型按需检索内容，而不是预先注入。禁用预加载文件也正是[内置 **Files** 工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)可用的前提，模型借此自行列出、搜索和读取聊天附件。
- **调试/测试**：用来隔离问题是否与 RAG 处理相关。

:::warning 禁用预加载文件 = 无预注入内容
禁用预加载文件时，文件内容**不会被自动提取或注入**。Open WebUI 不会把文件转发给模型的原生 API。如果禁用此项，模型获取文件内容的唯一途径就是[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)（如果已启用）——查询知识库或按需检索附加文件（代理式文件处理）。
:::

:::tip 基于单个文件的检索模式
聊天中的单个附件或知识库可通过 **“使用整篇文档（Using Entire Document）”** 开关完全绕过 RAG。无论原生函数调用如何设置，系统都会将文件全文注入每条消息。上传的文件和文本附件如果不超过管理员区域 **Settings** > **Documents** 中设定的**全文阈值（字符数）**，系统会自动包含全文。打开**始终使用全文**可将这条规则应用于所有文档。详情参阅[完整上下文与重点检索](/features/workspace/knowledge#retrieval-modes)。

如果不想逐个选择，请在**设置 > 界面 > 文件**中设置**默认上传模式**。此后每个附件都会默认使用所选模式，之后仍可单独切换。
:::

:::info
只有当模型启用了 **File Upload** 时，预加载文件开关才会出现。
:::

### 内置工具能力 {#builtin-tools-capability}

**[内置工具 (Builtin Tools)](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)** 能力控制模型是否获得原生函数调用工具以实现自动检索：

| 内置工具 | 行为表现 |
|---------------|----------|
| ✅ **启用**（默认） | 除非模型设为旧版函数调用，否则模型会收到 `query_knowledge_bases`、`view_knowledge_file`、`search_chats` 等工具。 |
| ❌ **禁用** | 不注入任何[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)。模型只能依赖预先注入的上下文。 |

**何时禁用[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)：**
- **模型不支持函数调用**：较小或较旧的模型可能无法处理 `tools` 参数。
- **需要可预测的行为**：你只希望模型在给定的有限信息内发挥作用。

### 结合使用两项能力 {#combining-the-two-capabilities}
这些能力独立运作，赋予您精细化的控制权。下表描述的是在设置为默认或原生函数调用的模型上，**在聊天内部**附加的文件和知识库。

在旧版下，[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)设置对这些附件不起作用。无论该设置如何，模型都不会获得任何自主检索工具，因此只有预加载文件决定结果：开启则内容会像传统 RAG 那一行那样预先注入；关闭则像"无文件处理"那一行一样，内容根本不会到达模型。

| 预加载文件 | 内置工具 | 结果 |
|--------------|---------------|--------|
| 启用 | 启用 | **全能代理模式**：注入 RAG 内容 + 模型能自发查询知识库 |
| 启用 | 禁用 | **传统 RAG**：前期注入内容，不支持自动检索工具 |
| 禁用 | 启用 | **纯工具模式**：不预先注入内容。模型按需查询知识库，并且会注入[内置 **Files** 工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)（`list_chat_files`、`query_chat_files`、`grep_chat_files`、`view_file`、`display_file`），让它能读取和搜索聊天自身的附件。在聊天中附加的知识库和笔记会[把知识工具限制在这些内容上](/features/workspace/knowledge#scoped-access-keeps-things-organized)。该组合同时也是[提示缓存的最优配置](/features/chat-conversations/prompt-caching) |
| 禁用 | 禁用 | **无文件处理**：忽略附加文件，没有内容会传递给模型 |

:::warning 附加到模型或文件夹上的知识表现不同
上表涵盖的是在聊天中进行的附加。附加到工作区模型上的知识，以及附加到文件夹上的知识，则遵循函数调用模式：

- **旧版**：知识会排队等待检索并预先注入，与表格描述一致——前提是预加载文件已开启。关闭预加载文件会完全移除检索步骤，因此在旧版下也不会注入任何内容。
- **默认和原生**：无论预加载文件如何设置，都不会注入。知识通过[内置知识工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)提供给模型，由模型自行决定是否检索。

其后果是一种"静默无效"的配置。当预加载文件已开启、[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)被禁用、而函数调用保持默认时，附加到模型或文件夹上的知识永远不会被触及：既没有注入，模型也没有工具去查询它。默认是大多数部署从未改动过的设置，因此很容易在无意中落入这一组合。

以下任一做法都可以解决：

- 在该模型上保持[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)开启。
- 把该模型的函数调用设为旧版。
- 把知识库附加在聊天中，而不是附加到模型或文件夹上。
:::

:::tip 选择正确的配置
- **多数模型**：二者均保持开启（默认设定）以获得完整体验。
- **小型/本地模型**：如果它们不支持函数调用，请关闭[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)。
- **仅按需检索**：如果你希望由模型决定检索内容而非预先提供全部内容，请禁用预加载文件、启用[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)，并把模型设为默认或原生函数调用。这在旧版下不起作用——旧版从不使用按需工具，因此在关闭预加载文件后将完全检索不到任何内容。
:::

## 增强的 RAG Pipeline {#enhanced-rag-pipeline}

我们的 RAG 嵌入功能带有可切换的混合搜索子功能，通过 `BM25` 增强了 RAG，并借由 `CrossEncoder` 实现重排打分，其相关度阈值可以自由配置。这为您的特定用例提供了更精准、更个性化的 RAG 体验。

:::tip 类文件系统的知识库访问（`kb_exec`）
若想获得更强大的代理式体验，可设置 `ENABLE_KB_EXEC=True`。这会让模型获得一个 shell 风格的知识库操作界面（`ls`、`tree`、`grep`、`cat`、`head`/`tail`、按行读取，并支持管道）。相比起一组分散的搜索工具，能力较强的模型通常能更可靠地将其串联起来，因此往往能更准确地定位到目标片段。它要求**原生函数调用**（它是原生模式的[内置工具](/features/extensibility/plugin/tools#built-in-system-tools-nativeagentic-mode)），默认关闭；对于设置为 Legacy 的模型它没有任何效果。我们建议为能力足够的模型开启它。详见[类文件系统的知识库访问](/features/workspace/knowledge#filesystem-style-access-kb_exec)。
:::

## YouTube RAG 流程 {#youtube-rag-pipeline}

通过视频 URL 总结 YouTube 视频的专用 RAG 流程让您能够顺畅地直接和视频转录文本互动。这项创新的特性允许您将视频内容纳入对话，进一步充实了您的聊天体验。

视频以其转录文本的形式附加，因此没有可用转录的视频无法附加，错误信息会指出属于哪种情况：上传者关闭了字幕、视频有年龄限制或不可用、所请求的语言没有转录，或者 YouTube 因请求来源地址而拦截了请求。可通过 [`YOUTUBE_LOADER_LANGUAGE`](/reference/env-configuration#youtube_loader_language) 设置要尝试的语言，并通过**设置 > Web Search > Youtube Proxy URL**（管理员区域）（[`YOUTUBE_LOADER_PROXY_URL`](/reference/env-configuration#youtube_loader_proxy_url)）让被拦截的请求走代理。参见[附加链接或 YouTube 视频失败](/troubleshooting/rag#14-attaching-a-link-or-a-youtube-video-fails)。

## 文档解析 {#document-parsing}
多种不同的解析器能够提取本地及远程文档的内容：内置引擎如 Tika、Docling 和 Mistral OCR，或者在你需要按文件类型路由或自定义逻辑时，通过[外部引擎](/features/chat-conversations/rag/document-extraction/external)运行你自己的服务。完整列表和配置步骤请查阅[文档提取](/features/chat-conversations/rag/document-extraction)。

:::warning 临时聊天限制
当使用**临时聊天 (Temporary Chat)** 时，为了保证数据私密且不在服务器驻留，文档处理受限在**纯前端**环节。由此，基于后端的高级解析功能（服务于如复杂的 DOCX 格式）会被停用，你可能会看到原始数据而不是整理好的解析文字。要获取完备的文档支持，请使用标准会话（Standard Chat）。
:::

### CSV 表格摘要 {#csv-table-summary}

解析后的 CSV 就是它的各行，仅此而已，因此当模型被问及某个表格包含多少条订单时，它只能根据被检索到的那些行来回答。设置 [`ENABLE_RAG_CSV_SUMMARY=true`](/reference/env-configuration#enable_rag_csv_summary)（默认关闭，需要重启）会在每个 `.csv` 文件前面加上一行，写明其行数、数据行数和列名。

`external`、`tika` 和 `docling` 抽取引擎会自行解析 `.csv` 文件，因此不会得到摘要。只有在你开启该设置之后解析的文件才会有摘要，所以请重新建立索引，以便为知识库中已有的 CSV 补上摘要。

## Google Drive 集成 {#google-drive-integration}

当与一个开启了 Google Picker API 以及 Google Drive API 的 Google Cloud 项目共同配置时，此项特性可以让用户直接从聊天界面接入他们的 Drive 文件并上传文档、幻灯片、表格等作为您的对话上下文。这能够在 `Settings` > `Documents`（管理员区域）菜单下启用。使用它必须要设定 [`GOOGLE_DRIVE_API_KEY and GOOGLE_DRIVE_CLIENT_ID`](/reference/env-configuration) 环境变量。

### 详细说明 {#detailed-instructions}

1. 创建一个 OAuth 2.0 客户端，将授权的 JavaScript 来源和重定向 URI 都设为用于访问此实例的 URL（如有端口，也需包含）。
2. 记录下与该 OAuth 客户端绑定的客户端 ID (Client ID)。请完全按照 Google 显示的形式使用它，即 `<project number>-....apps.googleusercontent.com`。选择器会从 Client ID 开头的几位数字读取 Cloud 项目编号。
3. 确保你的项目启用了 Google Drive API 和 Google Picker API 两项服务。
4. 在 OAuth 同意屏幕上，将应用设置为“正式发布 (In production)”；或者保持“测试中 (Testing)”，并把你的用户添加到测试用户列表中。
5. 添加 `https://www.googleapis.com/auth/drive.file` 作用域。Open WebUI 只请求这一个作用域，它授予访问每位用户所选文件的权限。Google 将其归类为非敏感作用域，因此自托管安装无需受限作用域验证或安全评估，用户也不会看到"Google 尚未验证此应用"的警告。
6. 前往 Google Picker API 的控制台，然后点击创建凭据 (create credentials) 按钮。
7. 创建一个 API 密钥，并在应用限制 (Application restrictions) 中勾选网站 (Websites)。随后添入你的 Open-WebUI 实例 URL，内容等同于步骤 1 中的授权 JavaScript 来源和重定向 URI 的地址。
8. 给该 API Key 配置 API 约束限制，使其只准存取 Google Drive API & Google Picker API。
9. 配置环境变量，将 `GOOGLE_DRIVE_CLIENT_ID` 设置为步骤 2 里的 OAuth 客户端的客户端 ID。
10. 将环境变量 `GOOGLE_DRIVE_API_KEY` 设为步骤 7 生成的 API 密钥，而不是步骤 2 的 OAuth 客户端密钥。
11. 建立 `GOOGLE_REDIRECT_URI` 设定为你 Open-WebUI 实例的 URL (包含端口)。
12. 接着，在环境里携带着那三项变量重新启动你的 Open-WebUI。
13. 完成之后，去确保 Google Drive 已经在 `Settings` > `Documents` > `Google Drive`（管理员区域）被开启。

选择器以列表视图打开，因为 `drive.file` 作用域无法访问文件缩略图。
