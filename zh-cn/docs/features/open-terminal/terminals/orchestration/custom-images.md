---
sidebar_position: 4
title: "自定义镜像"
---

# 自定义镜像

对于小的包变更，优先使用 `OPEN_TERMINAL_PACKAGES`、`OPEN_TERMINAL_PIP_PACKAGES` 或 `OPEN_TERMINAL_NPM_PACKAGES`。

对于更重的自定义，构建一个镜像：

```bash
git clone https://github.com/open-webui/open-terminal.git
cd open-terminal
docker build -t ghcr.io/acme/open-terminal:python-ds .
docker push ghcr.io/acme/open-terminal:python-ds
```

然后：

1. 将策略镜像设置为 `ghcr.io/acme/open-terminal:python-ds`。
2. 在 Open WebUI 中保存策略。
3. 刷新受影响的终端。

新预配的终端将使用新镜像。

如果在编排器上设置了 `TERMINALS_ALLOWED_IMAGES`，镜像必须匹配该允许列表。
