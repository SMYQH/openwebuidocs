---
sidebar_position: 27
title: "OpenSERP"
---

:::tip

如需查看所有与 Web 搜索相关的环境变量完整列表（包括并发设置、结果数量等），请参阅[环境变量配置文档](/reference/env-configuration#web-search)。

:::

:::tip 故障排查

Web 搜索遇到问题？请查阅 [Web 搜索故障排查指南](/troubleshooting/web-search)，了解代理配置、连接超时、内容为空等常见问题的解决办法。

:::

[OpenSERP](https://github.com/karust/openserp) 是一个自托管的抓取器，可以返回多个主流搜索引擎的结果。与 [SearXNG](./searxng.md) 和 [YaCy](./yacy.md) 一样，它运行在你自己的基础设施上，**不需要 API key**，因此 Open WebUI 所需的唯一设置就是一个可达的基础 URL。

Open WebUI 会调用它的 `/mega/search` 端点，该端点同时查询 Google、Bing、Yandex、Baidu、DuckDuckGo 和 Ecosia，并返回合并后的结果。

## 1. 运行 OpenSERP {#1-run-openserp}

```bash
docker run -d --name openserp -p 7000:7000 karust/openserp serve -a 0.0.0.0 -p 7000
```

检查它是否能正常响应：

```bash
curl "http://localhost:7000/mega/search?text=open+webui&limit=3"
```

如果 Open WebUI 本身运行在 Docker 中，`localhost` 指向的是 Open WebUI 容器而不是你的宿主机。请改用 `http://host.docker.internal:7000`，或者把两个容器放到同一个 Docker 网络上并使用服务名。

## 2. 让 Open WebUI 指向它 {#2-point-open-webui-at-it}

1. 前往 **Settings > Admin > Web Search**。
2. 启用 **Web Search**。
3. 将 **Web Search Engine** 设为 `openserp`。
4. 将 **OpenSERP URL** 设为你自己的实例，例如 `http://localhost:7000`。只有在选中 `openserp` 后该字段才会出现。
5. 保存。

基础 URL 也可以通过 [`OPENSERP_BASE_URL`](/reference/env-configuration#openserp_base_url) 设置，其默认值为 `http://localhost:7000`。结尾带斜杠也没关系，它会在发起请求前被去掉。

## 3. 使用它 {#3-use-it}

打开一个新的聊天，从消息输入框的 **+** 菜单中开启 **Web Search**，然后发送一条查询。

:::warning 抓取式搜索引擎可能受到速率限制

OpenSERP 的工作方式是抓取搜索引擎的结果页面，而不是调用官方 API。这些引擎可能会限流、弹出 CAPTCHA，或在高负载时封禁发起请求的地址，在 Open WebUI 中表现为搜索失败。这是它获取结果的方式本身所带来的特性，而不是配置错误，也是"不需要 API key"这一优点的代价。

:::
