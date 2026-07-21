# Open WebUI 文档

[Open WebUI](https://github.com/open-webui/open-webui) 是一款功能丰富的自托管 AI 聊天界面，本仓库是其[文档站点](https://docs.openwebui.com)的**非官方中文翻译版本**。

> **翻译模型**：GPT mini & Luna ；DeepSeek flash & pro ; Minimax......

> **代码模型**：Claude Fable & Opus ; GLM ; DeepSeek pro ; GPT Terra & sol ; Minimax ; Kimi code......

> 🤝 社区被寄予持续驱动此仓库翻译完善的期望，但请勿使用 `Gemini`、`Qwen`、`Doubao` 系列模型贡献。

## 仓库结构

``` Structure
├── en-us/          # 英文源文档 (git 子模块)
├── zh-cn/          # 中文翻译文档
├── STATUS.md       # 翻译进度与版本对照
└── AGENTS.MD       # AI 辅助开发配置
```

翻译状态详见 [STATUS.md](./STATUS.md)。

## 部署方式

[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/SMYQH/openwebuidocs)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/SMYQH/openwebuidocs&root-directory=zh-cn)

> **注意**：
> 点击 Cloudflare 按钮后即可将站点部署到你自己的 `*.workers.dev` 域名，无需手动设置根目录、构建命令或部署命令。
>
> 如需使用自定义域名，请在部署完成后前往 Cloudflare Worker 的 **Settings → Domains & Routes** 绑定域名；同时将 `zh-cn/docusaurus.config.ts` 中的 `url` 改为你的实际站点地址。

### GitHub Pages

通过 GitHub Actions 手动部署：

1. 进入仓库 **操作** → **Deploy to GitHub Pages** → **Run workflow**
2. 填写部署地址（如 `https://myorg.github.io/docs` 或 `https://docs.example.com`），点击运行

Workflow 会自动将用户填写的部署地址解析为 `url` 和 `baseUrl`，替换 `docusaurus.config.ts` 后构建。

### 构建

```bash
cd zh-cn
npm ci           # 安装依赖
npm run build    # 构建静态站点，输出到 zh-cn/build/
npm run serve    # 本地预览构建结果（默认 http://localhost:3000）
```
