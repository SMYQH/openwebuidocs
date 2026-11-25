:::info Python 版本兼容性
Open WebUI 支持 **Python 3.11 和 3.12**。**不支持 Python 3.13**：部分依赖还没有兼容 3.13 的发行版，因此在 3.13 上安装会失败或在运行时崩溃。

- **生产环境**请在 **Linux** 上运行 **Docker 镜像**，或使用**最新的 Python 3.12**。Docker 镜像在 Debian 13 上运行 Python 3.12。
- **在 Windows 上**，可以通过 pip、uv 或 Conda 安装供个人使用。生产环境请使用 Linux。
- **Python 3.11** 用 pip 安装同样可用。

如果 pip 报告不支持你的 Python 版本，先激活要安装到的环境，再进行检查：

```bash
python --version
python -m pip --version
```

单独安装 Python 3.12 不会改变现有环境中的解释器。如果版本不符，请使用 Python 3.12 创建新环境，激活该环境，再运行 `python -m pip install open-webui`，以便使用该解释器进行安装。
:::

:::info 系统包
Python 安装不会自带 ffmpeg，而标准 Docker 镜像中包含它。请用操作系统的包管理器安装它，并确保 `ffmpeg` 位于运行 `open-webui serve` 的 shell 的 `PATH` 中。语音转文字用它来转换、压缩和切分音频，文字转语音则用它来转换来自兼容 OpenAI 引擎的非 MP3 回复。缺少它时，服务器日志会显示 `Couldn't find ffmpeg or avconv`，这些步骤也会失败。参见[音频故障排查](/troubleshooting/audio#ffmpeg-missing-on-a-pip-install)。
:::

:::tip 没有 NVIDIA GPU？
在 Linux x86_64 上，从 PyPI 安装 `open-webui` 会装入默认的 PyTorch 构建版本。无论机器使用哪种 GPU，这个版本都会附带 NVIDIA CUDA 库。没有 NVIDIA GPU 时，先在同一环境中安装 PyTorch 的 CPU 版本，安装 Open WebUI 时就不会装入这些库：

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

使用 uv 时，请将同一命令的开头改为 `uv pip install`。若要在 AMD GPU 上使用硬件加速，请改为安装 [PyTorch 安装页面](https://pytorch.org/get-started/locally/)提供的 ROCm 版本。
:::

:::warning 启动目录中的 `.env` 不会被读取
pip、uv 或 Conda 安装会忽略你运行 `open-webui serve` 所在目录中的 `.env` 文件。它只读取 `<env>/lib/python3.12/.env`（Python 3.12 下，Windows 上为 `<env>\Lib\.env`）。请在 shell 或服务单元中导出你的变量，或像下面的示例那样在命令行上设置它们。参见[`.env` 文件被 pip、uv 和 Conda 安装忽略](/reference/env-configuration#env-file-ignored-by-pip-uv-and-conda-installs)，了解如何打印出确切路径。
:::
