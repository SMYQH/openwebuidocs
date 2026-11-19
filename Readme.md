# Open WebUI 文档

[Open WebUI](https://github.com/open-webui/open-webui) 是一款功能丰富的自托管 AI 聊天界面，本仓库是其[文档站点](https://docs.openwebui.com)的**非官方中文翻译版本**。

> **翻译模型**：GPT Luna & Terra & Sol (Major) & Astra ; DeepSeek Flash

> **代码模型**：GPT Terra & Sol (Major) & Astra ; Claude Fable & Opus

> 🤝 社区被寄予持续驱动此仓库翻译完善的期望，但请勿使用 `Minimax`、`Doubao` 系列模型贡献。

## 仓库结构

```text
├── .github/workflows/                # 工作流
├── .agents/skills/                   # 共享技能
│   ├── upstream-sync/                # 上游同步与翻译更新
│   ├── translation-checker/          # 基于 Python 的翻译检查
│   └── translation-semantic-review/  # 全量语义审查
├── en-us/                            # 英文源文档（Git 子模块）
├── zh-cn/                            # 中文文档站点
│   └── docs/                         # 简体中文译文
├── .env.example                      # DeepL 密钥配置示例（可选）
├── wrangler.jsonc                    # Cloudflare 部署配置
├── STATUS.md                         # 项目状态
├── Readme.md                         # 项目介绍
└── AGENTS.MD                         # 智能体协作规范
```

翻译状态详见 [STATUS.md](./STATUS.md)。

## 部署方式

通过 GitHub Actions 自动构建并部署到 **Cloudflare Workers**。

### 1. 配置仓库机密

在仓库 **Settings → Secrets and variables → Actions** 中新增以下 Repository secrets：

| 名称 | 说明 | 示例 |
| --- | --- | --- |
| `DOMAIN` | 站点访问地址（用于写入 Docusaurus `url` / `baseUrl`；若主机名属于当前 Account 下 Zone，部署时自动绑定为 Custom Domain） | `https://docs.example.com` |
| `TOKEN` | API Token（需具备 Workers 部署权限，以及 `Zone:Zone:Read` 以便自动检查/绑定自定义域名） | `cfut_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `ID` | Account ID（Dashboard 右侧） | xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |

### 2. 触发部署

- **自动**：推送到 `main`，且变更涉及 `zh-cn/**`、`wrangler.jsonc` 或根目录依赖时触发
- **手动**：仓库 **Actions → Deploy to Cloudflare Workers → Run workflow**

> Workflow 作用

> 1. 用 `DOMAIN` 解析并写入 `zh-cn/docusaurus.config.ts` 的 `url` / `baseUrl`

> 2. 构建中文站点（输出到 `zh-cn/build/`）

> 3. 用 `TOKEN` + `ID` 检查 `DOMAIN` 主机名是否属于当前 Account 的 Zone；若是，则写入 Wrangler Custom Domain 并关闭生产级 `*.workers.dev`（保留 Preview URLs）

> 4. 使用 `TOKEN` + `ID` 通过 Wrangler 部署到 Cloudflare Workers

### 3. 自定义域名

部署时会自动处理，无需在 Dashboard 手动绑定：

1. 从 `DOMAIN` 解析主机名（支持 `https://docs.example.com` 或 `docs.example.com`）
2. 调用 Cloudflare API，在当前 Account 下查找能覆盖该主机名的 Zone
3. **若找到且 Zone 为 active**：向 `wrangler.jsonc` 写入 `routes: [{ pattern: "<hostname>", custom_domain: true }]`，设置 `workers_dev: false`，并保持 `preview_urls: true`
4. **若未找到**（域名不在本 Account、Zone 未激活，或本身是 `*.workers.dev` / `*.pages.dev`）：跳过绑定，保留默认生产级 `workers.dev`，并在日志中给出 warning

> 要求：目标域名必须已作为 Cloudflare Zone 接入同一 Account；`TOKEN` 需能读取 Zone 列表。若主机名上已有冲突的 CNAME 等记录，Custom Domain 绑定可能失败，需先清理冲突 DNS。

### 本地构建

```bash
cd zh-cn
npm ci           # 安装依赖
npm run build    # 构建静态站点，输出到 zh-cn/build/
npm run serve    # 本地预览构建结果（默认 http://localhost:3000）
```

根目录也可一键构建并部署（需本机已登录 Wrangler / 配置好 Cloudflare 凭据）：

```bash
npm run build    # 构建 zh-cn
npm run deploy   # wrangler deploy
```
