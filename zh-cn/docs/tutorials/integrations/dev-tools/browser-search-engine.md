---
sidebar_position: 50
title: "浏览器搜索引擎"
---

# 浏览器搜索引擎集成 {#browser-search-engine-integration}

:::warning

本教程由社区贡献，不属于 Open WebUI 团队官方支持范围。内容仅用于演示如何根据你的特定场景自定义 Open WebUI。想参与贡献？请查看贡献教程。

:::

Open WebUI 支持直接集成到浏览器。本教程将指导你把 Open WebUI 配置为自定义搜索引擎，让你可以直接在地址栏中发起查询。

## 将 Open WebUI 配置为搜索引擎 {#setting-up-open-webui-as-a-search-engine}

### 前置条件 {#prerequisites}

开始前请确认：

- 你已安装 Chrome 或其他受支持浏览器。
- 你的 Open WebUI 实例可以通过浏览器访问一个稳定的 URL。
- 如果你要使用 Firefox 的一键选项，`WEBUI_URL` 环境变量必须设置为该 URL，可通过 Docker 环境变量或 `.env` 文件配置，参见[环境变量指南](/reference/env-configuration)。

### 第 1 步：设置 WEBUI_URL 环境变量（仅 Firefox） {#step-1-set-the-webui\_url-environment-variable-firefox-only}

下面的 Chrome 配置不需要 `WEBUI_URL`：浏览器会自行打开 `<your-open-webui-url>/?q=%s`。Firefox 的一键选项会读取 Open WebUI 的 `/opensearch.xml`，并用 `WEBUI_URL`（**Admin Panel > Settings > General** 中的 **WebUI URL** 字段）构建搜索 URL，因此请把它设置为你访问 Open WebUI 使用的地址。

#### 使用 Docker 环境变量 {#using-docker-environment-variables}

如果你通过 Docker 运行 Open WebUI，可在 `docker run` 命令中设置该环境变量：

```bash
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  -e WEBUI_URL="https://<your-open-webui-url>" \
  ghcr.io/open-webui/open-webui:main
```

你也可以把该变量写入 `.env` 文件：

```plaintext
WEBUI_URL=https://<your-open-webui-url>
```

### 第 2 步：将 Open WebUI 添加为自定义搜索引擎 {#step-2-add-open-webui-as-a-custom-search-engine}

### 在 Chrome 中配置 {#for-chrome}

1. 打开 Chrome 并进入**设置**。
2. 在侧栏选择**搜索引擎**，点击**管理搜索引擎**。
3. 点击**添加**新建搜索引擎。
4. 按如下填写：
    - **搜索引擎**：Open WebUI Search
    - **关键词**：webui（或你喜欢的任意关键词）
    - **URL（用 %s 代替查询内容）**：

      ```txt
      https://<your-open-webui-url>/?q=%s
      ```

5. 点击**添加**保存配置。

### 在 Firefox 中配置 {#for-firefox}

1. 在 Firefox 中打开 Open WebUI。
2. 点击地址栏展开搜索区域。
3. 点击展开后底部绿色圆圈中的加号图标，将 Open WebUI 搜索添加到浏览器搜索引擎列表。

或使用以下方式：

1. 在 Firefox 中打开 Open WebUI。
2. 右键地址栏。
3. 在菜单中选择“添加 Open WebUI”（或类似选项）。

### 可选：指定模型 {#optional-using-specific-models}

如果你希望搜索时使用指定模型，可将模型 ID 加入 URL：

```txt
https://<your-open-webui-url>/?models=<model_id>&q=%s
```

:::note

**说明：** 模型 ID 需要进行 URL 编码。空格、斜杠等特殊字符都要编码（例如 `my model` 需写成 `my%20model`）。

:::

## 使用示例 {#example-usage}

配置完成后，你可以直接在地址栏发起搜索。输入你设置的关键词，再加查询内容：

```txt
webui your search query
```

浏览器会打开 Open WebUI，并将查询内容填入消息输入框。按 Enter 发送。

## 故障排查 {#troubleshooting}

如果遇到问题，请检查：

- 确认浏览器搜索引擎设置中的 URL 指向一个正在运行的 Open WebUI 实例。
- 对于 Firefox 的一键选项，确认 `WEBUI_URL` 已设置为你访问 Open WebUI 使用的地址。
- 再次核对浏览器中的搜索引擎 URL 格式是否填写正确。
- 确认网络连接正常，且 Open WebUI 服务正在运行。
