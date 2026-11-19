---
sidebar_position: 900
title: "参与文档贡献"
---

# 文档贡献指南 {#contributing-to-documentation}

:::warning

本教程由社区贡献，不属于 Open WebUI 团队官方支持范围。内容仅用于演示如何根据你的特定场景自定义 Open WebUI。想参与贡献？请查看贡献教程。

:::

感谢你对 Open WebUI 文档教程贡献的兴趣。请按照以下步骤完成环境准备并提交你的教程。

## 贡献步骤 {#contributing-steps}

1. **Fork `open-webui/docs` GitHub 仓库**

   - 在 GitHub 打开 [Open WebUI Docs Repository](https://github.com/open-webui/docs)。
   - 点击右上角 **Fork** 按钮，在你的 GitHub 账号下创建副本。

2. **启用 GitHub Actions**

   - 在你 Fork 的仓库中进入 **Actions** 标签页。
   - 若页面提示未启用，请按页面指引开启 GitHub Actions。

3. **启用 GitHub Pages**

   - 在你 Fork 的仓库进入 **Settings** > **Pages**。
   - 在 **Build and deployment** > **Source** 下，选择 **GitHub Actions**。工作流会构建并发布站点，无需选择分支或文件夹。

4. **配置 GitHub 环境变量**

   - 在你 Fork 的仓库进入 **Settings** > **Secrets and variables** > **Actions** > **Variables**。
   - 添加以下环境变量：
     - `BASE_URL` 设置为 `/docs`（或你为 Fork 站点选择的 base URL）。
     - `SITE_URL` 设置为 `https://<your-github-username>.github.io/`。

   这些变量要在按下一节修改工作流和配置后才会生效。上游的 `gh-pages.yml` 构建步骤未设置 `env`，而 `docusaurus.config.ts` 中的 `url` 和 `baseUrl` 都是硬编码值。

### 📝 更新 GitHub Pages 工作流与配置文件 {#updating-the-github-pages-workflow-and-config-file}

如果你需要按自定义部署方式调整设置，可按以下步骤处理：

a. **更新 `.github/workflows/gh-pages.yml`**

- 如有需要，在构建步骤中加入 `BASE_URL` 与 `SITE_URL` 环境变量：

     ```yaml
       - name: Build
         env:
           BASE_URL: ${{ vars.BASE_URL }}
           SITE_URL: ${{ vars.SITE_URL }}
         run: npm run build
     ```

b. **修改 `docusaurus.config.ts` 以使用环境变量**

- 更新 `docusaurus.config.ts`，改为读取这些环境变量，并保留本地或直连部署的默认值：

     ```typescript
     const config: Config = {
       title: "Open WebUI",
       tagline: "On a mission to build the best AI interface",
       favicon: "images/favicon.png",
       url: process.env.SITE_URL || "https://docs.openwebui.com",
       baseUrl: process.env.BASE_URL || "/",
       ...
     };
     ```

- 这样可确保 Fork 仓库和自定义部署场景下的行为一致。

5. **运行 Deploy site to Pages 工作流**

   - 打开 **Actions** ，然后选择 **Deploy site to Pages** 工作流（`gh-pages.yml`）。
   - 视你的配置而定，可手动触发，也可能自动运行。

6. **访问你的 Fork 站点**

   - 访问 `https://<your-github-username>.github.io/<BASE_URL>` 查看你的文档副本。

7. **编写你的变更**

   - 在你 Fork 的仓库中进入对应目录（如 `docs/tutorials/`）。
   - 新建教程 Markdown 文件，或编辑现有教程。
   - 确保你的教程包含“非官方支持”警告横幅。

8. **提交 Pull Request**

   - 教程准备完成后，将变更提交到你的 Fork 仓库。
   - 前往原始 `open-webui/docs` 仓库。
   - 点击 **New Pull Request**，选择你的 Fork 和分支作为来源。
   - 为 PR 填写清晰的标题与说明。
   - 提交 Pull Request 等待审核。

## 重要说明 {#important}

社区贡献教程必须包含以下内容：

```txt

:::warning

This tutorial is a community contribution and is not supported by the Open WebUI team. It serves only as a demonstration on how to customize Open WebUI for your specific use case. Want to contribute? Check out the contributing tutorial.

:::

```

---

:::tip

如何在本地测试 Docusaurus
你可以使用以下命令在本地测试 Docusaurus 站点：

```bash
npm install   # Install dependencies
npm run build # Build the site for production
```

这样可以在部署前尽早发现问题。

:::

---
