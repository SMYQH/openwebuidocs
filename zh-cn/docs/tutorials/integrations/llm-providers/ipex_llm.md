---
sidebar_position: 30
title: "Intel GPU (IPEX-LLM)"
---

:::warning
本教程由社区贡献，Open WebUI 团队不提供支持。它仅演示如何根据你的具体场景自定义 Open WebUI。想参与贡献？请查看[贡献教程](/contributing)。
:::

:::note

本指南已通过[手动安装](/getting-started/)方式搭建的 Open WebUI 进行验证。

:::

## 在 Intel GPU 上使用 IPEX-LLM 进行本地 LLM 设置 {#local-llm-setup-with-ipex-llm-on-intel-gpu}

:::info

[**IPEX-LLM**](https://github.com/intel-analytics/ipex-llm) 是一个 PyTorch 库，可在 Intel CPU 和 GPU 上以极低延迟运行 LLM。它支持配有集成显卡（iGPU）的本地 PC，以及 Arc A 系列、Flex 和 Max 等独立 GPU。

:::

本教程演示如何为 Open WebUI 配置**在 Intel GPU 上运行、由 IPEX-LLM 加速的 Ollama 后端**。即使在只有集成 GPU 的低成本 PC 上，也能流畅使用 Open WebUI。

## 在 Intel GPU 上启动 Ollama 服务 {#start-ollama-serve-on-intel-gpu}

请参阅 IPEX-LLM 官方文档中的[此指南](https://ipex-llm.readthedocs.io/en/latest/doc/LLM/Quickstart/ollama_quickstart.html)，了解如何在 Intel GPU 上安装和运行由 IPEX-LLM 加速的 Ollama 服务。

:::tip

如果您希望从另一台机器访问 Ollama 服务，请在执行 `ollama serve` 命令前确保设置或导出环境变量 `OLLAMA_HOST=0.0.0.0`。

:::

## 配置 Open WebUI {#configure-open-webui}

通过 **Admin Panel > Settings > Connections** 访问 Ollama 设置。默认情况下，**Ollama API** 连接 URL 为 `http://localhost:11434`（在标准 Docker 镜像中为 `http://host.docker.internal:11434`），如下图所示。要验证 Ollama 服务连接状态，点击 Ollama 连接上的 **Configure**（齿轮图标），然后点击 URL 旁边的 **Verify Connection**。如果 WebUI 无法与 Ollama 服务器建立连接，您将看到一条错误消息。

![Open WebUI Ollama 设置失败](https://llm-assets.readthedocs.io/en/latest/_images/open_webui_settings_0.png)

如果连接成功，您将看到提示 `Server connection verified`，如下图所示。

![Open WebUI Ollama 设置成功](https://llm-assets.readthedocs.io/en/latest/_images/open_webui_settings.png)

:::tip

如果您想使用托管在不同 URL 的 Ollama 服务器，请点击 Ollama 连接上的 **Configure**，修改 **URL**，点击 **Verify Connection**，然后点击 **Save**。

:::
