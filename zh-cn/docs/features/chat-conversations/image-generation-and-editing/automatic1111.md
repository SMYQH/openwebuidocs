---
sidebar_position: 2
title: "AUTOMATIC1111"
---

:::warning
本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎贡献更多内容，可查看 contributing 教程。
:::

Open WebUI 支持通过 **AUTOMATIC1111** [API](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API) 进行图像生成。以下是快速开始步骤：

### 初始设置 {#initial-setup}

1. 确保你已安装 [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)。
2. 使用额外的标志启动 AUTOMATIC1111 以启用 API 访问：

```python
/webui.sh --api --listen
```

### 配置 Open WebUI 连接 AUTOMATIC1111 {#setting-up-open-webui-with-automatic1111}

1. 在 Open WebUI 中前往**设置** > **图像**（管理员区域），开启**图像生成**并添加连接。
2. 将**连接类型**设为 **AUTOMATIC1111**。
3. 在 **URL** 中填入可访问 AUTOMATIC1111 API 的地址：

```txt
http://<your_automatic1111_address>:7860/
```

如果 Open WebUI 在 Docker 中运行，且 AUTOMATIC1111 在同一台宿主机上运行，请使用 `http://host.docker.internal:7860/`。

4. 如果 AUTOMATIC1111 需要身份验证，请选择 **Basic** 验证类型并输入 `username:password`。
5. 将 **Model IDs** 留空可使用已加载的 checkpoint，也可添加 checkpoint 名称供选择。选择其他已列出的模型会切换服务器已加载的 checkpoint，影响该服务器上的所有用户。
6. 可选：打开**高级**，添加 `{"cfg_scale": 7, "sampler_name": "Euler a"}` 等额外参数。
7. 设置**访问控制**并点击**保存**。未授予访问权限时，只有管理员能使用该连接。

AUTOMATIC1111 连接支持图像生成。如需编辑，请添加 ComfyUI 或兼容 OpenAI 的连接。
