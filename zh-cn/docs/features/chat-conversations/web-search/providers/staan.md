---
sidebar_position: 28
title: "Staan"
---

:::warning

本教程是社区贡献内容，Open WebUI 团队并不提供支持。它仅用于演示如何针对你的具体用例定制 Open WebUI。想参与贡献？请查看贡献教程。

:::

:::tip

如需查看所有与 Web 搜索相关的环境变量完整列表（包括并发设置、结果数量等），请参阅[环境变量配置文档](/reference/env-configuration#web-search)。

:::

# Staan Web 搜索集成 {#staan-web-search-integration}

[Staan](https://staan.ai/) 是一个数据留在欧盟境内的 Web 搜索 API；当你的部署必须在该边界内完成处理时，这就是选择它而非其他托管搜索 API 的理由。

## 配置步骤 {#configuration-steps}

1. 在 [staan.ai](https://staan.ai/) 注册并创建一个 API key。
2. 在 Open WebUI 中打开 **Settings > Admin > Web Search**。
3. 打开 **Web Search**，并把 **Web Search Engine** 选为 **Staan**。
4. 把该密钥粘贴到 **Staan API Key**。
5. 按下 **Save**。

同样的设置也可以通过环境变量提供：

```bash
ENABLE_WEB_SEARCH=true
WEB_SEARCH_ENGINE=staan
STAAN_API_KEY=your-staan-api-key
```

## 市场区域 {#market}

**Staan Market**（`STAAN_MARKET`，默认 `en-us`）决定结果来自哪个地区与哪种语言，以"语言-国家"配对的形式书写。请把它设为你所服务的受众，例如 `de-de` 表示来自德国的德语结果。

## 结果中的页面内容 {#page-content-in-the-results}

**Staan Max Snippets**（`STAAN_MAX_SNIPPETS`）决定 Open WebUI 会拿回每个页面的多少内容。

取值为 `0`（默认）时，Staan 只返回普通的搜索结果：一个标题、一个 URL 以及它已有的摘要。取值大于 `0` 时，Staan 会抓取每个结果页面，把其中的段落与查询比对打分，并返回至多相应数量的片段。Open WebUI 会把它们拼接到该结果的摘要上，因此模型读到的是页面中相关的部分，而不是一行概括。

当答案需要页面内部的具体细节时可以调高它，但请记住，请求页面内容意味着每次搜索都要做更多工作，因此更高的取值会消耗更多时间，在按量计费的方案下还会花费更多金钱。

## 域名过滤 {#domain-filtering}

**Domain Filter List**（域名过滤列表）对 Staan 的作用与对 Tavily 和 Exa 相同：域名被过滤掉的结果在返回之后会被丢弃。
