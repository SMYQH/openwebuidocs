```bash
python -m pip install open-webui
open-webui serve
```

Open WebUI 运行在 [http://localhost:8080](http://localhost:8080)。设置 `DATA_DIR` 可以指定数据存放位置，例如 `DATA_DIR=~/.open-webui open-webui serve`。使用 `--host` 和 `--port` 可以更改绑定地址，例如 `open-webui serve --port 3000`。

该命令会用一个密钥对会话签名，它会把密钥写入启动目录下的 `.webui_secret_key`。请在环境变量中设置 `WEBUI_SECRET_KEY`，或始终从同一个目录启动；换用新的密钥会让所有人退出登录。

**提示找不到命令？** 请激活你安装时所用的环境；`open-webui` 命令位于该环境的 `bin` 目录下（Windows 上为 `Scripts`）。

**需要尚未发布的修复？** PyPI 只提供已发布的版本。可以保留现有安装，另用独立的数据卷运行 Docker 的 `:dev` 镜像，或按[开发 Open WebUI](/getting-started/advanced-topics/development)中的说明从 `dev` 分支运行。从本地检出的源码或 Git URL 安装时，会触发构建钩子，需要 Node.js 和 npm 来构建前端；使用 PyPI 的 wheel 则不需要。


## 卸载 {#uninstall}

1. **卸载包：**
    ```bash
    pip uninstall open-webui
    ```

2. **删除数据（可选，会删除所有数据）：** 删除你设置为 `DATA_DIR` 的目录。如果没有设置，数据位于环境内的 `site-packages/open_webui/data`，而 `pip uninstall` 会保留它，因为它是在运行时创建的。
    ```bash
    rm -rf ~/.open-webui
    ```
