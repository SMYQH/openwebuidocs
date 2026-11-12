:::info Python 版本兼容性
Open WebUI 支持 **Python 3.11 和 3.12**。**不支持 Python 3.13**：部分依赖还没有兼容 3.13 的发行版，因此在 3.13 上安装会失败或在运行时崩溃。

- **生产环境**请使用 **Docker 镜像**或 **最新的 Python 3.12**。Docker 镜像在 Debian 13 上运行 Python 3.12。
- **Python 3.11** 用 pip 安装同样可用。
:::

:::tip 没有 NVIDIA GPU？
在 Linux x86_64 上，从 PyPI 安装 `open-webui` 会拉入默认的 PyTorch 构建，它会连同机器上的任何 GPU 一起带上 NVIDIA CUDA 库。在没有 NVIDIA GPU 的机器上，请先在同一个环境里安装 PyTorch 的 CPU 构建版，Open WebUI 的安装就会把它们排除在外：

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

使用 uv 时，把同样的命令写成 `uv pip install`。若要在 AMD 显卡上获得加速，请改为安装 [PyTorch 安装页面](https://pytorch.org/get-started/locally/)提供的 ROCm 构建版。
:::
