---
sidebar_position: 3
title: "Chatterbox TTS —— 声音克隆"
---

# Chatterbox TTS —— 声音克隆 {#chatterbox-tts-voice-cloning}

:::warning

本教程来自社区贡献，并非 Open WebUI 官方支持内容。它仅作为演示，说明如何按你的具体场景自定义 Open WebUI。欢迎贡献更多内容，可查看 contributing 教程。

:::

## 什么是 `Chatterbox TTS API`？ {#what-is-chatterbox-tts-api}

[Chatterbox TTS API](https://github.com/travisvn/chatterbox-tts-api) 是一个 API 封装层，支持声音克隆与文本转语音，可直接替代 OpenAI Speech API 端点。

[![Resemble AI 语音样本链接](https://img.shields.io/badge/listen-demo_samples-blue)](https://resemble-ai.github.io/chatterbox_demopage/)

## 主要特性 {#key-features}

- 零样本声音克隆 —— 只需约 10 秒语音样本
- [表现优于 ElevenLabs](https://podonos.com/resembleai/chatterbox)
- 输出带水印，便于负责任地使用声音克隆
- 0.5B Llama backbone
- 自定义 Voice Library 管理
- 支持流式输出，生成更快
- 具备高级内存管理与自动清理
- 可选前端界面，便于管理和使用

### 硬件建议 {#hardware-recommendations}

- 内存：至少 4GB，推荐 8GB+
- GPU：CUDA（Nvidia）或 Apple M 系列（MPS）
- CPU：也能运行，但更慢 —— 生产环境推荐使用 GPU

:::info

Chatterbox 可能会占用较多内存，其硬件要求也可能高于你熟悉的其他本地 TTS 方案。如果你的机器难以满足要求，可以考虑 [OpenAI Edge TTS](/features/chat-conversations/audio/text-to-speech/openai-edge-tts-integration) 或 [Kokoro-FastAPI](/features/chat-conversations/audio/text-to-speech/Kokoro-FastAPI-integration) 作为替代方案。

:::

## ⚡️ 快速开始 {#quick-start}

### 🐍 使用 Python {#using-python}

#### 方案 A：使用 uv（推荐 —— 更快、依赖处理更好） {#option-a-using-uv-recommended-faster--better-dependencies}

```bash

# Clone the repository
git clone https://github.com/travisvn/chatterbox-tts-api
cd chatterbox-tts-api

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv (automatically creates venv)
uv sync

# Copy and customize environment variables
cp .env.example .env

# Start the API with FastAPI
uv run uvicorn app.main:app --host 0.0.0.0 --port 4123

# Or use the main script
uv run main.py
```

> 💡 **为什么选 uv？** 用户普遍反馈它对 `chatterbox-tts` 兼容性更好、安装速度提升 25-40%，并且依赖解析更稳定。[查看迁移指南 →](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/UV_MIGRATION.md)

#### 方案 B：使用 pip（传统方式） {#option-b-using-pip-traditional}

```bash

# Clone the repository
git clone https://github.com/travisvn/chatterbox-tts-api
cd chatterbox-tts-api

# Setup environment — using Python 3.11
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and customize environment variables
cp .env.example .env

# Add your voice sample (or use the provided one)

# cp your-voice.mp3 voice-sample.mp3

# Start the API with FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 4123

# Or use the main script
python main.py
```

> 遇到问题？请查看 [故障排查部分](https://github.com/travisvn/chatterbox-tts-api?tab=readme-ov-file#common-issues)

### 🐳 Docker（推荐） {#docker-recommended}

```bash

# Clone and start with Docker Compose
git clone https://github.com/travisvn/chatterbox-tts-api
cd chatterbox-tts-api

# Use Docker-optimized environment variables
cp .env.example.docker .env  # Docker-specific paths, ready to use

# Or: cp .env.example .env    # Local development paths, needs customization

# Choose your deployment method:

# API Only (default)
docker compose -f docker/docker-compose.yml up -d             # Standard (pip-based)
docker compose -f docker/docker-compose.uv.yml up -d          # uv-optimized (faster builds)
docker compose -f docker/docker-compose.gpu.yml up -d         # Standard + GPU
docker compose -f docker/docker-compose.uv.gpu.yml up -d      # uv + GPU (recommended for GPU users)
docker compose -f docker/docker-compose.cpu.yml up -d         # CPU-only

# API + Frontend (add --profile frontend to any of the above)
docker compose -f docker/docker-compose.yml --profile frontend up -d             # Standard + Frontend
docker compose -f docker/docker-compose.gpu.yml --profile frontend up -d         # GPU + Frontend
docker compose -f docker/docker-compose.uv.gpu.yml --profile frontend up -d      # uv + GPU + Frontend

# Watch the logs as it initializes (the first use of TTS takes the longest)
docker logs chatterbox-tts-api -f

# Test the API
curl -X POST http://localhost:4123/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello from Chatterbox TTS!"}' \
  --output test.wav
```

<!-- markdownlint-disable-next-line MD033 -->
<details>
<!-- markdownlint-disable-next-line MD033 -->
<summary>**🚀 使用前端界面运行**</summary>

该项目包含一个可选的 React Web UI。你可以通过 Docker Compose profile 方便地选择是否启用前端：

### 使用 Docker Compose Profiles {#with-docker-compose-profiles}

```bash

# API only (default behavior)
docker compose -f docker/docker-compose.yml up -d

# API + Frontend + Web UI (with --profile frontend)
docker compose -f docker/docker-compose.yml --profile frontend up -d

# Or use the convenient helper script for fullstack:
python start.py fullstack

# Same pattern works with all deployment variants:
docker compose -f docker/docker-compose.gpu.yml --profile frontend up -d    # GPU + Frontend
docker compose -f docker/docker-compose.uv.yml --profile frontend up -d     # uv + Frontend
docker compose -f docker/docker-compose.cpu.yml --profile frontend up -d    # CPU + Frontend
```

### 本地开发 {#local-development}

本地开发时，你可以分别运行 API 和前端：

```bash

# Start the API first (follow earlier instructions)

# Then run the frontend:
cd frontend && npm install && npm run dev
```

> **注意：** 如果遇到依赖问题，可尝试使用 `npm install --force` 代替普通 `npm install`。

根据 Vite 输出的链接打开 Web UI 即可。

### 生产构建 {#build-for-production}

为生产部署构建前端：

```bash
cd frontend && npm install && npm run build
```

> **注意：** 如果构建因依赖冲突失败，也可以尝试 `npm install --force`。

构建完成后可直接通过本地文件系统中的 `/dist/index.html` 访问。

### 端口说明 {#port-configuration}

- **仅 API**：通过 `http://localhost:4123` 访问
- **带前端**：Web UI 位于 `http://localhost:4321`，API 请求通过反向代理转发

因此，当使用 `--profile frontend` 运行时，Web 界面位于 `http://localhost:4321`，而 API 则在代理后端运行。

</details>

## 配置 Open WebUI 使用 `Chatterbox TTS API` {#setting-up-open-webui-to-use-chatterbox-tts-api}

我们建议你先带前端界面运行，这样可以先上传想克隆的声音文件，再去配置 Open WebUI。如果已按上文正确启动，可访问 `http://localhost:4321` 打开前端。

让 Open WebUI 使用 Chatterbox TTS API 的步骤如下：

- 转到 `设置` -> `音频`（管理员区域）
- 将 TTS 设置为：
- - 文本转语音引擎：OpenAI
  - API 基础 URL：`http://localhost:4123/v1` # 也可尝试 `http://host.docker.internal:4123/v1`
  - API 密钥：`none`
  - TTS 模型：`tts-1` 或 `tts-1-hd`
  - TTS 语音：你克隆出来的语音名称（也可使用前端中定义的别名）
  - 响应切分：`Paragraphs`

:::info

默认 API 密钥为字符串 `none`（无需真实 API 密钥）

:::

![Open WebUI 音频管理员设置截图，展示此项目所需的正确端点](https://lm17s1uz51.ufs.sh/f/EsgO8cDHBTOUjUe3QjHytHQ0xqn2CishmXgGfeJ4o983TUMO)

## 如果觉得这个项目有帮助，请为 [GitHub 仓库](https://github.com/travisvn/chatterbox-tts-api) 点个 ⭐️ {#please-star-the-repo-on-github-to-support-development}

## 需要帮助？ {#need-help}

Chatterbox 初次启动时可能比较折腾，如果某种安装方式不顺利，你可以尝试切换到其他安装路径。

如需了解更多 `chatterbox-tts-api` 信息，请访问其 [GitHub 仓库](https://github.com/travisvn/chatterbox-tts-api)。

- 📖 **文档**：参见 [API 文档](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/API_README.md) 和 [Docker 指南](https://github.com/travisvn/chatterbox-tts-api/blob/main/docs/DOCKER_README.md)

## 故障排查 {#troubleshooting}

### 内存要求 {#memory-requirements}

Chatterbox 的内存要求高于其他 TTS 方案：
- **最低：** 4GB RAM
- **推荐：** 8GB+ RAM
- **GPU：** 推荐使用 NVIDIA CUDA 或 Apple M 系列（MPS）

如果你有内存问题，可考虑改用更轻量的方案，例如 [OpenAI Edge TTS](/features/chat-conversations/audio/text-to-speech/openai-edge-tts-integration) 或 [Kokoro-FastAPI](/features/chat-conversations/audio/text-to-speech/Kokoro-FastAPI-integration)。

### Docker 网络 {#docker-networking}

如果 Open WebUI 无法连接 Chatterbox：

- **Docker Desktop：** 使用 `http://host.docker.internal:4123/v1`
- **Docker Compose：** 使用 `http://chatterbox-tts-api:4123/v1`
- **Linux：** 使用宿主机 IP 地址

### 首次启动 {#first-time-startup}

第一次 TTS 请求通常会更慢，因为模型需要先加载。可使用以下命令查看日志：

```bash
docker logs chatterbox-tts-api -f
```

更多排查建议请参阅 [音频故障排查指南](/troubleshooting/audio)。
