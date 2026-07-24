---
title: 离线安装
sidebar_position: 4
---

# 离线安装

Open WebUI Computer 一旦安装完成，无需互联网访问即可运行。Python wheel 包含了构建的前端资源，Docker 镜像是自包含的，因此在运行时不会获取任何内容。

## 在有网络的机器上构建制品

```bash
# Python 方式：下载 wheelhouse
pip download --dest wheelhouse 'cptr[all]'

# Docker 方式：保存镜像
docker pull ghcr.io/open-webui/computer:latest
docker save ghcr.io/open-webui/computer:latest -o cptr-image.tar
```

在与离线主机平台和 Python 版本匹配的机器上下载 wheelhouse，以便 pip 选择兼容的 wheel。

## 在离线主机上安装

从 wheelhouse 安装：

```bash
python -m venv .venv
. .venv/bin/activate
pip install --no-index --find-links ./wheelhouse 'cptr[all]'
cptr run --host 0.0.0.0
```

或者加载并运行 Docker 镜像：

```bash
docker load -i cptr-image.tar
docker run --rm -it \
  --network=none \
  -p 8000:8000 \
  -v cptr-data:/data \
  -v "$PWD:/workspace" \
  -w /workspace \
  ghcr.io/open-webui/computer:latest
```

如果 pip 仍然尝试联系索引，请检查 `--no-index` 和 `--find-links ./wheelhouse` 是否都存在。

## 哪些仍然需要网络

文件、编辑器、终端、git（本地操作）和工作区都可以完全离线工作。任何需要与外部服务通信的功能则不行：

- 托管的模型 API（OpenAI、Anthropic 和其他云提供商）
- 网络搜索提供商
- Git 远程（从互联网 `push`、`pull`、`clone`）
- 消息平台（Telegram、Discord、Slack、WhatsApp、Signal）
