---
sidebar_position: 10
title: "开发 Open WebUI"
---

# 开发 Open WebUI {#developing-open-webui}

:::danger 在 `dev` 上工作，永远不要在 `main` 上工作
`dev` 是预发布分支，所有改动都会先落到那里。每一次修复、每一个功能都进入 `dev` 并留在 `dev`，因此今天修复的 bug 今天就在 `dev` 上，下一次发布时才会进入 `main`。`main` 只是发布当天从 `dev` 拍下的一份快照，也就是说从 `main` 构建出来的代码已经落后了。

刚用 `git clone` 克隆仓库时，当前分支是 `main`。开始操作前先切换分支：

```bash
git clone https://github.com/open-webui/open-webui.git
cd open-webui
git checkout dev
```

Pull Request 同样是针对 `dev` 提出的。针对 `main` 提出的 PR 必须重做。
:::

**从源码运行 Open WebUI，用于开发与测试。**

本指南介绍如何搭建本地开发环境，让前端（SvelteKit）和后端（Python/FastAPI）并行运行。你需要两个终端会话，各负责一端。

:::tip 不需要完整开发环境？
改为运行 `:dev` 预发布镜像即可。它是同一份代码，随着改动落地每晚重新构建，你不需要自己构建任何东西：

```bash
docker run -d -p 3001:8080 --add-host=host.docker.internal:host-gateway -v open-webui-dev:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui-dev --restart always ghcr.io/open-webui/open-webui:dev
```

测试它并反馈你发现的问题，是成本最低的帮忙方式，也正是让发布变好的关键。详情参见[使用 dev 分支](/getting-started/quick-start#using-the-dev-branch)，并注意它使用独立的卷。
:::

---

## 前置要求 {#prerequisites}

| 要求 | 版本 |
|-------------|---------|
| **Python** | 3.11 或 3.12（见下方说明；暂不支持 3.13） |
| **Node.js** | 22.10+ |
| **Git** | 任意较新版本 |

:::info Python 版本兼容性
Open WebUI 支持 **Python 3.11 与 3.12**。**暂不支持 3.13** —— 我们的部分依赖还需要发布兼容 3.13 的版本，在此之前，在 3.13 上安装会失败或在运行时出错。

- **生产环境**请使用 [Docker 镜像](/getting-started/quick-start) 或 **最新的 Python 3.12**。Docker 镜像在 Debian 13 上运行 Python 3.12。
- **3.11 也可用于**开发及通过 pip 安装。
:::

:::warning 将开发数据与生产数据分开
不要在开发环境与生产环境之间共享数据库或数据目录。开发构建可能包含向后不兼容的数据库迁移。
:::

---

## 1. 克隆仓库 {#1-clone-the-repository}

```bash
git clone https://github.com/open-webui/open-webui.git
cd open-webui
git checkout dev
```

`git checkout dev` 是关键的一步。不切换分支，构建的就是最近一次发布的版本，而不是当前开发代码。

---

## 2. 前端环境配置 {#2-frontend-setup}

在你的**第一个终端**中，于项目根目录执行：

```bash
cp -RPp .env.example .env
npm install
npm run build
npm run dev
```

`npm run build` 会先编译前端并尽早发现构建期错误；它以 12 GB 的 Node.js 堆上限运行 Vite。随后 `npm run dev` 会在 [http://localhost:5173](http://localhost:5173) 启动开发服务器。在后端启动之前，它会显示等待画面。

:::tip
如果 `npm install` 因兼容性警告失败，可尝试运行 `npm install --force`。
:::

---

## 3. 后端环境配置 {#3-backend-setup}

在你的**第二个终端**中执行：

```bash
cd backend
```

创建并激活虚拟环境（Conda 或 venv）：

```bash
# Option A: Conda
conda create --name open-webui python=3.12
conda activate open-webui

# Option B: venv
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

安装依赖并启动服务：

```bash
pip install -r requirements.txt -U
sh dev.sh
```

后端会在 [http://localhost:8080](http://localhost:8080) 启动，API 文档可在 [http://localhost:8080/docs](http://localhost:8080/docs) 查看。

刷新前端页面 [http://localhost:5173](http://localhost:5173)，你应该就能看到完整应用了。

---

## 从其他设备测试 {#testing-from-another-device}

如果你想在手机或同一网络中的另一台电脑上访问开发实例：

1. 找到你机器的局域网 IP（例如 `192.168.1.42`）
2. 在 `backend/dev.sh` 的 CORS 配置中允许该源：

```bash
export CORS_ALLOW_ORIGIN="http://localhost:5173;http://localhost:8080;http://192.168.1.42:5173"
```

3. 重启后端，然后访问 `http://192.168.1.42:5173`

---

## 故障排查 {#troubleshooting}

### “FATAL ERROR: Reached Heap Limit” {#fatal-error-reached-heap-limit}

Node.js 内存不足了。`npm run build` 本身已设置了 12 GB 的堆上限。对于 `npm run dev` 和其他前端命令，请在运行前先增大堆内存：

```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run dev
```

请确认系统至少有 4 GB 可用内存。

### 端口冲突 {#port-conflicts}

如果端口 `5173` 或 `8080` 已被占用，请先找出冲突进程：

```bash
# macOS/Linux
lsof -i :5173

# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess
```

结束对应进程，或在 `vite.config.js`（前端）或 `dev.sh`（后端）中修改端口。

### 图标未加载（CORS） {#icons-not-loading-cors}

如果静态资源加载失败，请在 `backend/dev.sh` 中配置 `CORS_ALLOW_ORIGIN`，使其包含你的前端 URL。详情参见 [CORS 配置](/reference/env-configuration#cors_allow_origin)。

### 热重载不工作 {#hot-reload-not-working}

1. 确认两个开发服务器都已启动且没有报错
2. 强制刷新浏览器（Ctrl+Shift+R / Cmd+Shift+R）
3. 重新安装前端依赖：`rm -rf node_modules && npm install`
4. 后端改动可能需要手动重启 `sh dev.sh`

---

## 贡献流程 {#contributing-workflow}

1. 在开始写代码前，先到 [GitHub Discussions](https://github.com/open-webui/open-webui/discussions/new/choose) **发起讨论**
2. 从 `dev` 分支**创建你自己的分支**。不要直接向 `dev` 提交

```bash
git checkout dev
git pull origin dev
git checkout -b my-feature-branch
```

3. **保持分支同步**，定期从 `dev` 合并更新
4. 以清晰的标题和描述向 `dev` 分支**提交拉取请求（pull request）**

详细规范见[贡献指南](/contributing)。
