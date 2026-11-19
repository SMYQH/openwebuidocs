---
sidebar_position: 2
title: "使用 Docker 部署 Kokoro-FastAPI"
---

:::warning

本教程由社区贡献，Open WebUI 团队不提供支持。它仅演示如何针对你的使用场景自定义 Open WebUI。想投稿？请查看教程投稿指南。

:::

## 什么是 `Kokoro-FastAPI`？ {#what-is-kokoro-fastapi}

[Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) 是 [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) 文本转语音模型的容器化 FastAPI 封装，遵循 OpenAI API 规范，能快速生成语音。

## 主要特性 {#key-features}

- 提供兼容 OpenAI Speech 的语音生成端点，支持在一次请求中组合多种语音
- 支持 NVIDIA GPU 加速或 CPU ONNX 推理
- 支持流式输出与可变分块
- 支持多种音频格式（`.mp3`、`.wav`、`.opus`、`.flac`、`.aac`、`.pcm`）
- 集成 Web 界面，默认位于 localhost:8880/web（仓库还提供单独的 Gradio 容器）
- 提供用于转换和生成音素的端点

## 语音 {#voices}

- af
- af_bella
- af_irulan
- af_nicole
- af_sarah
- af_sky
- am_adam
- am_michael
- am_gurney
- bf_emma
- bf_isabella
- bm_george
- bm_lewis

## 语言 {#languages}

- en_us
- en_uk

## 前置要求 {#requirements}

- 系统已安装 Docker
- Open WebUI 正在运行
- 若使用 GPU：需要支持 CUDA 12.3 的 NVIDIA GPU
- 若仅 CPU：无特殊要求

## ⚡️ 快速开始 {#quick-start}

### 你可以选择 GPU 或 CPU 版本 {#you-can-choose-between-gpu-or-cpu-versions}

### GPU 版本（需要支持 CUDA 12.8 的 NVIDIA GPU） {#gpu-version-requires-nvidia-gpu-with-cuda-128}

使用 docker run：

```bash
docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu
```

也可使用 Docker Compose：创建 `docker-compose.yml` 文件并运行 `docker compose up`。例如：

```yaml
name: kokoro
services:
    kokoro-fastapi-gpu:
        ports:
            - 8880:8880
        image: ghcr.io/remsky/kokoro-fastapi-gpu:v0.2.1
        restart: always
        deploy:
            resources:
                reservations:
                    devices:
                        - driver: nvidia
                          count: all
                          capabilities:
                              - gpu
```

:::info

你可能需要先安装并配置 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

:::

### CPU 版本（ONNX 优化推理） {#cpu-version-onnx-optimized-inference}

使用 docker run：

```bash
docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu
```

使用 docker compose：

```yaml
name: kokoro
services:
    kokoro-fastapi-cpu:
        ports:
            - 8880:8880
        image: ghcr.io/remsky/kokoro-fastapi-cpu
        restart: always
```

## 配置 Open WebUI 使用 `Kokoro-FastAPI` {#setting-up-open-webui-to-use-kokoro-fastapi}

按照以下步骤让 Open WebUI 使用 Kokoro-FastAPI：

- 转到 `设置` -> `音频`（管理员区域）
- 将 TTS 设置为：
- - 文本转语音引擎：OpenAI
  - API 基础 URL：`http://localhost:8880/v1` # 也可能需要用 `host.docker.internal` 代替 `localhost`
  - API 密钥：`not-needed`
  - TTS 语音：`af_bella` # 为兼容现有 OAI 语音，也接受其映射值
  - TTS 模型：`kokoro`

:::info

默认 API 密钥字符串是 `not-needed`。如果你不需要额外安全控制，可以保持不变。

:::

## 构建 Docker 容器 {#building-the-docker-container}

```bash
git clone https://github.com/remsky/Kokoro-FastAPI.git
cd Kokoro-FastAPI
cd docker/cpu # or docker/gpu
docker compose up --build
```

**就是这么简单！**

如需了解构建 Docker 容器、修改端口等更多信息，请参阅 [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) 仓库。

## 故障排查 {#troubleshooting}

### 未检测到 NVIDIA GPU {#nvidia-gpu-not-detected}

如果 GPU 版本没有用上你的 GPU：

1. **安装 NVIDIA Container Toolkit：**
   ```bash
   # Ubuntu/Debian
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

2. **验证 GPU 可访问：**
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.2.0-base nvidia-smi
   ```

### 从 Open WebUI 连接失败 {#connection-issues-from-open-webui}

如果 Open WebUI 无法访问 Kokoro，这通常是一个 Docker 网络问题。请根据你的部署情况选择对应方式：

**方案 1 — Docker Desktop（Windows/Mac）：**

使用 `host.docker.internal` 代替 `localhost`：http://host.docker.internal:8880/v1

**方案 2 — Docker Compose（同一网络）：**

直接使用服务名：http://kokoro-fastapi-gpu:8880/v1

**方案 3 — Docker 网络（Linux 推荐）：**

如果 `host.docker.internal` 不可用，可创建一个共享的 Docker 网络：

```bash
# Create a Docker network
docker network create local-llm

# Connect both containers to the network
docker network connect local-llm open-webui
docker network connect local-llm kokoro-fastapi

# Restart both containers
docker restart open-webui kokoro-fastapi
```

随后将基础 API 端点的 URL 设为 `http://kokoro-fastapi:8880/v1`

- 确认服务正在运行：`curl http://localhost:8880/health`
