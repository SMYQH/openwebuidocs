:::info Python 版本兼容性
Open WebUI 支持 **Python 3.11 和 3.12**。**不支持 Python 3.13**：部分依赖还没有兼容 3.13 的发行版，因此在 3.13 上安装会失败或在运行时崩溃。

- **生产环境**请使用 **Docker 镜像**或 **最新的 Python 3.12**。Docker 镜像在 Debian 13 上运行 Python 3.12。
- **Python 3.11** 用 pip 安装同样可用。
:::

:::tip 没有 NVIDIA GPU？
在 Linux x86_64 上，从 PyPI 安装 `open-webui` 会装入默认的 PyTorch 构建版本。无论机器使用哪种 GPU，这个版本都会附带 NVIDIA CUDA 库。没有 NVIDIA GPU 时，先在同一环境中安装 PyTorch 的 CPU 版本，安装 Open WebUI 时就不会装入这些库：

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

使用 uv 时，请将同一命令的开头改为 `uv pip install`。若要在 AMD GPU 上使用硬件加速，请改为安装 [PyTorch 安装页面](https://pytorch.org/get-started/locally/)提供的 ROCm 版本。
:::
