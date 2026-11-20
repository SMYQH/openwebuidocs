---
sidebar_position: 5
title: "自定义镜像"
---

# 自定义镜像 {#custom-images}

自定义镜像是你自己构建的 Open Terminal 镜像，其中已安装用户需要的工具、语言和文件，因此各实例启动后即可使用。如果启动时安装的软件过多或耗时过长，可构建自定义镜像。

如果只需小幅调整软件包，优先使用 `OPEN_TERMINAL_PACKAGES`、`OPEN_TERMINAL_PIP_PACKAGES` 或 `OPEN_TERMINAL_NPM_PACKAGES`。

如果需要进一步定制，请构建镜像：

```bash
git clone https://github.com/open-webui/open-terminal.git
cd open-terminal
docker build -t ghcr.io/acme/open-terminal:python-ds .
docker push ghcr.io/acme/open-terminal:python-ds
```

然后：

1. 打开终端对话框，展开 **Advanced**。
2. 将 **Image** 设为 `ghcr.io/acme/open-terminal:python-ds`。
3. 保存。

之后启动的实例会使用新镜像。

如果在编排器上设置了 `TERMINALS_ALLOWED_IMAGES`，镜像必须匹配该允许列表。
