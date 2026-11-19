---
sidebar_position: 10
title: "Continue.dev"
---

# 将 Continue.dev VS Code 扩展与 Open WebUI 集成 {#integrating-continuedev-vs-code-extension-with-open-webui}

:::warning
本教程由社区贡献，Open WebUI 团队不予支持。它仅作为演示，说明如何根据您的具体场景自定义 Open WebUI。想参与贡献？请查看[贡献教程](/contributing)。
:::

## 下载扩展 {#download-extension}

您可以在 [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=Continue.continue) 下载 VS Code 扩展，或在 VS Code 的 `EXTENSION:MARKETPLACE` 中搜索 `continue` 直接安装。
安装完成后，您可以通过 VS Code 侧边栏中的 `continue` 选项卡访问该应用程序。

**VS Code 侧边栏图标：**

![continue.dev VS Code 图标](/images/tutorials/continue-dev/continue_dev_vscode_icon.png)

---

## 设置 {#setup}

点击主聊天输入框右侧的助手选择器，将鼠标悬停在 `Local Assistant` 上，然后点击设置图标（⚙️）。
这将在编辑器中打开 `config.yaml` 文件。在这里您可以更改 `Local Assistant` 的设置。

![continue.dev 聊天输入框](/images/tutorials/continue-dev/continue_dev_extension_input_field.png)

:::info

目前 `ollama` 提供商不支持身份验证，因此我们无法在 Open WebUI 中使用此提供商。
不过，Ollama 和 Open WebUI 都兼容 OpenAI API 规范。详情见 [Ollama 关于 OpenAI 兼容性的博客文章](https://ollama.com/blog/openai-compatibility)。
可以将 continue.dev 配置为使用 openai 提供商，从而使用 Open WebUI 的身份验证令牌。

:::

### 配置示例 {#example-config}

以下是本地 Open WebUI 设置的配置示例。

```yaml
name: Local Assistant
version: 1.0.0
schema: v1
models:
  - name: Qwen3.6
    provider: openai
    model: qwen3.6:27b
    env:
      useLegacyCompletionsEndpoint: false
    apiBase: http://localhost:3000/api
    apiKey: YOUR_OPEN_WEBUI_API_KEY
    roles:
      - chat
      - edit
context:
  - provider: code
  - provider: docs
  - provider: diff
  - provider: terminal
  - provider: problems
  - provider: folder
  - provider: codebase

```

---

### 其他配置设置 {#miscellaneous-configuration-settings}

这些值是扩展正常运行所必需的。更多信息请参见[官方配置指南](https://docs.continue.dev/reference)。

```yaml
name: Local Assistant
version: 1.0.0
schema: v1
```

context 部分为模型提供了额外信息。更多信息请参阅 [官方配置指南](https://docs.continue.dev/reference#context) 以及 [上下文提供程序指南](https://docs.continue.dev/customize/model-providers/overview)。

```yaml
context:
  - provider: code
  - provider: docs
  - provider: diff
  - provider: terminal
  - provider: problems
  - provider: folder
  - provider: codebase
```

---

### 模型列表 {#models}

models 部分用于指定您要添加的所有模型。更多信息请参见[官方模型指南](https://docs.continue.dev/reference#models)。

```yaml
models:
  - ...
```

---

### 名称 {#name}

设置您要使用的模型名称，该名称将显示在扩展的聊天输入框中。

```yaml
name: Qwen3.6
```

![continue.dev 聊天输入框](/images/tutorials/continue-dev/continue_dev_extension_input_field.png)

---

### 提供商 {#provider}

指定与 API 通信的方式，本例中为 Open WebUI 提供的 OpenAI API 端点。

```yaml
provider: openai
```

---

### 模型名称 {#model}

这里填模型在 Open WebUI 中的实际名称。在管理界面打开 `Settings` > `Models`，点击要使用的 LLM。
实际名称显示在用户自定义的名称下方。

```yaml
model: qwen3.6:27b
```

---

### 旧版 completions 端点 {#legacy-completions-endpoint}

Open WebUI 不需要此设置，更多信息请参见[原始指南](https://platform.openai.com/docs/guides/completions)。

```yaml
env:
  useLegacyCompletionsEndpoint: false
```

---

### 配置 APIBase {#apibase}

这一步很关键：将 continue.dev 扩展的请求指向 Open WebUI 实例的基础 API 端点。
对于远程实例，使用实际域名（例如 `https://example.com/api`）；对于本地实例，使用本地地址（例如 `http://localhost:3000/api`）。
有关 URL 的更多信息，请参见[端点指南](/reference/api-endpoints)。

```yaml
apiBase: http://localhost:3000/api
```

---

### API 密钥 {#api-key}

要向 Open WebUI 实例进行身份验证，您需要生成一个 API 密钥。
请按照 [API 端点指南](/reference/api-endpoints)中的说明创建密钥。

```yaml
apiKey: YOUR_OPEN_WEBUI_API_KEY
```

---

### 角色 {#roles}

角色将允许您的模型在扩展中用于特定任务。初始可以选择 `chat` 和 `edit`。
有关角色的更多信息，请参见[官方角色指南](https://docs.continue.dev/customize/model-roles/intro)。

```yaml
roles:
  - chat
  - edit
```

设置现已完成，您可以通过聊天输入框与您的模型交互。有关 continue.dev 插件的功能和使用的更多信息，请参见[官方文档](https://docs.continue.dev/getting-started/overview)。
