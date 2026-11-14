---
sidebar_position: 30
title: "Jupyter Notebook"
---

> [!WARNING]
> 本文档基于当前版本（0.5.16）编写，持续更新中。

# Jupyter Notebook 集成 {#jupyter-notebook-integration}

:::warning
本教程由社区贡献，不受 Open WebUI 团队官方维护或审核。它仅作为演示，说明如何根据你的具体场景自定义 Open WebUI。想参与贡献？请查看贡献教程。
:::

从 v0.5.11 开始，Open-WebUI 发布了一个名为 `代码解释器中的 Jupyter Notebook 支持` 的新功能。该功能允许您将 Open-WebUI 与 Jupyter 集成。此后的几个版本中已对该功能进行了多次改进，请仔细查阅版本发布说明。

本教程将带您了解连接两个服务的基本设置步骤。

- [查看 v0.5.11 发布说明](https://github.com/open-webui/open-webui/releases/tag/v0.5.11)
- [查看 v0.5.15 发布说明](https://github.com/open-webui/open-webui/releases/tag/v0.5.14)

## 什么是 Jupyter Notebooks {#what-are-jupyter-notebooks}

Jupyter Notebook 是一个开源 Web 应用程序，允许用户创建和共享包含实时代码、方程式、可视化图表和叙述性文本的文档。它在数据科学、科学计算和教育领域尤其受欢迎，因为它使用户能够将可执行代码（Python、R 或 Julia 等语言）与解释性文本、图像和交互式可视化图表整合在一个文档中。Jupyter Notebooks 在数据分析和探索方面特别有用，因为它允许用户以小而可管理的代码块执行代码，同时记录思考过程和发现。这种格式使实验、调试代码以及创建全面、可共享的报告变得更加容易，这些报告既能展示分析过程又能呈现结果。

更多信息请访问 Jupyter 官网：[Project Jupyter](https://jupyter.org/)

## 第 0 步：配置摘要 {#step-0-configuration-summary}

以下是本教程将要完成的目标配置。

![代码执行配置](/images/tutorials/jupyter/jupyter-code-execution.png)

# 第 1 步：启动 OUI 和 Jupyter {#step-1-launch-oui-and-jupyter}

为此，我使用 Docker Compose 启动了一个同时包含两个服务以及我的 LLM 的服务栈，但分别运行各个 Docker 容器也应该可行。

```yaml title="docker-compose.yml"
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:latest
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
    extra_hosts:
      - host.docker.internal:host-gateway

  jupyter:
    image: jupyter/minimal-notebook:latest
    container_name: jupyter-notebook
    ports:
      - "8888:8888"
    volumes:
      - jupyter_data:/home/jovyan/work
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=123456

volumes:
  open-webui:
  jupyter_data:
```

`extra_hosts` 这一行让 `host.docker.internal` 在 Linux 上也能解析，下文的 `CODE_EXECUTION_JUPYTER_URL` 正依赖于此；在这个 Compose 项目内部，`http://jupyter:8888` 同样可用。

在保存了 `docker-compose.yml` 文件的目录中运行下面的命令即可启动上述服务栈：

```bash title="运行 Docker Compose"
docker compose up -d
```

现在您应该可以通过以下 URL 访问两个服务：

| 服务 | URL |
| ---------- | ----------------------- |
| Open-WebUI | `http://localhost:3000` |
| Jupyter | `http://localhost:8888` |

访问 Jupyter 服务时，您需要使用上面定义的 `JUPYTER_TOKEN`。本教程使用了示例令牌值 `123456`。

![Jupyter 登录页面要求输入密码或令牌](/images/tutorials/jupyter/jupyter-token.png)

# 第 2 步：为 Jupyter 配置代码执行 {#step-2-configure-code-execution-for-jupyter}

Open-WebUI 和 Jupyter 都运行后，我们需要在 Admin Panel -> Settings -> Code Execution 中配置 Open-WebUI 的代码执行以使用 Jupyter。由于 Open-WebUI 持续发布和改进该功能，建议始终查看 [`configs.py` 文件](https://github.com/open-webui/open-webui/blob/6fedd72e3973e1d13c9daf540350cd822826bf27/backend/open_webui/routers/configs.py#L72)以获取最新配置。截至 v0.5.16，包含以下配置：

| Open-WebUI 环境变量 | 值 |
| ------------------------------------- | -------------------------------- |
| `ENABLE_CODE_INTERPRETER` | True |
| `CODE_EXECUTION_ENGINE` | jupyter |
| `CODE_EXECUTION_JUPYTER_URL` | http://host.docker.internal:8888 |
| `CODE_EXECUTION_JUPYTER_AUTH` | token |
| `CODE_EXECUTION_JUPYTER_AUTH_TOKEN` | 123456 |
| `CODE_EXECUTION_JUPYTER_TIMEOUT` | 60 |
| `CODE_INTERPRETER_ENGINE` | jupyter |
| `CODE_INTERPRETER_JUPYTER_URL` | http://host.docker.internal:8888 |
| `CODE_INTERPRETER_JUPYTER_AUTH` | token |
| `CODE_INTERPRETER_JUPYTER_AUTH_TOKEN` | 123456 |
| `CODE_INTERPRETER_JUPYTER_TIMEOUT` | 60 |

这些都是持久化的管理端设置：环境变量只在针对全新数据库的首次启动时生效；此后以数据库中保存的值为准（在 设置 > 管理 > 代码执行 中修改），除非设置 `ENABLE_PERSISTENT_CONFIG=False`。`CODE_EXECUTION_JUPYTER_AUTH` 只接受 `token` 或 `password` 两种取值；填入其他值则不会发送任何凭据，而密码模式会通过 Jupyter 的 `/login` 表单登录。`CODE_INTERPRETER_JUPYTER_*` 系列变量默认取其 `CODE_EXECUTION_JUPYTER_*` 对应项的值，但 `CODE_INTERPRETER_ENGINE` 并非如此（它默认是 `pyodide`），因此请同时设置这两个引擎变量。

当 Jupyter 成为执行引擎后，默认开启的 [`ENABLE_ORJSON`](/reference/env-configuration#enable_orjson) 能更快地把一次运行的输出送进聊天，在代码打印大量内容或生成图片时尤其明显。请保持它为 `True`；它只在启动时读取一次，修改后需要重启。

## 第 3 步：测试连接 {#step-3-test-the-connection}

首先，让我们确认 Jupyter 目录中的内容。如下图所示，我们只有一个空的 `work` 文件夹。

![代码执行配置](/images/tutorials/jupyter/jupyter-empty.png)

### 创建 CSV {#create-a-csv}

让我们运行第一个提示词。确保已选择 `Code Execution` 按钮。

```txt
Prompt: Create two CSV files using fake data. The first CSV should be created using vanilla python and the second CSV should be created using the pandas library. Name the CSVs data1.csv and data2.csv
```

![代码执行配置](/images/tutorials/jupyter/jupyter-create-csv.png)

我们可以看到 CSV 文件已创建，现在可以在 Jupyter 中访问。

![代码执行配置](/images/tutorials/jupyter/jupyter-view-csv.png)

### 创建可视化图表 {#create-a-visualization}

让我们运行第二个提示词。同样，确保已选择 `Code Execution` 按钮。

```txt
Prompt: Create several visualizations in python using matplotlib and seaborn and save them to jupyter
```

![代码执行配置](/images/tutorials/jupyter/jupyter-create-viz.png)

我们可以看到可视化图表已创建，现在可以在 Jupyter 中访问。

![代码执行配置](/images/tutorials/jupyter/jupyter-view-viz.png)

### 创建 Notebook {#create-a-notebook}

让我们一起运行最后一个提示词。在这个提示词中，我们将仅通过提示词创建一个全新的 notebook。

```txt
Prompt: Write python code to read and write json files and save it to my notebook called notebook.ipynb
```

![代码执行配置](/images/tutorials/jupyter/jupyter-create-notebook.png)

我们可以看到 notebook 已创建，现在可以在 Jupyter 中访问。

![代码执行配置](/images/tutorials/jupyter/jupyter-view-notebook.png)

## 关于工作流的说明 {#note-about-workflow}

在测试此功能时，我注意到有几次 Open-WebUI 不会自动将在 Open-WebUI 中生成的代码或输出保存到我的 Jupyter 实例。为了强制输出我创建的文件/项目，我通常采用以下两步工作流：首先创建所需的代码产物，然后要求它将其保存到我的 Jupyter 实例。

![代码执行配置](/images/tutorials/jupyter/jupyter-workflow.png)

## 您是如何使用此功能的？ {#how-are-you-using-this-feature}

您是否正在使用代码执行功能和/或 Jupyter？如果是，请联系我。我很想了解您如何使用它，以便我可以继续向本教程添加更多使用此功能的精彩示例！
