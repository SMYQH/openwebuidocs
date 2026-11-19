---
sidebar_position: 0
title: "多用户配置"
---

# 为团队配置 Open Terminal {#setting-up-open-terminal-for-a-team}

当你团队中的多人需要通过 Open WebUI 访问终端时，你有两种选择。

| | 单容器 | 每用户独立容器 |
| :--- | :--- | :--- |
| **方式** | 一个容器，容器内独立账户 | 每个用户拥有自己的容器 |
| **隔离** | 在同一个共享容器内划分独立的工作区 | 每个用户拥有一个独立的容器，其中包含其专属的文件、进程和资源。在 Docker 后端，这些容器共享一个网络 |
| **配置** | 一个额外设置 | 额外的编排服务 |
| **适用场景** | 成员之间彼此完全信任的小型团队 | 生产环境、较大团队、不受信任的用户 |
| **包含于** | Open Terminal（免费） | [Terminals](https://github.com/open-webui/terminals)（企业版） |

:::danger 多用户 Open WebUI 部署必读
如果你的 Open WebUI 实例**拥有不止一个用户账户**，并且同一个 terminal-server 连接被多个用户共享，那么你**必须**使用下面两种隔离模式之一。一个未设置 `OPEN_TERMINAL_MULTI_USER=true` 的单 Open Terminal 容器（或没有通过 Terminals 提供的每用户独立容器）会把所有用户放进同一个 shell、同一份文件系统、同一个网络命名空间——这意味着任何用户都能读取、修改或替换其他用户的文件，能以共享用户身份执行命令，还能绑定共享端口。这种配置在多用户 Open WebUI 中并不受支持。

**方式 1 隔离工作区。它不是用户之间的安全边界。** 所有人依然共享同一个内核、同一份进程列表、同一个网络命名空间和一套系统资源，而且在容器内配置每用户账户需要提升的权限，所以试图在容器内获得 root 的用户会成功。只在实例上的所有用户享有相同信任级别的场景中使用此模式。

对于**包含不可信用户**的部署（开放注册、对公网门户、用户之间不互相信任），请使用**方式 2（通过 Terminals 提供的每用户容器）**，在其 Kubernetes 后端上运行并添加 NetworkPolicy，这才是在用户之间建立真正边界的方案。在方式 1 之上叠加 `TERMINAL_PROXY_HEADERS` 会限制代理响应在用户浏览器中的能力，但容器内的任何事情都不会改变。
:::

---

## 方式 1：内置多用户模式 {#option-1-built-in-multi-user-mode}

最简单的方式。添加一个设置，每个人会自动获得独立的工作区。

```bash
docker run -d --name open-terminal -p 8000:8000 \
  -v open-terminal:/home \
  -e OPEN_TERMINAL_MULTI_USER=true \
  -e OPEN_TERMINAL_API_KEY=your-secret-key \
  ghcr.io/open-webui/open-terminal
```

{/* TODO: Screenshot: Docker run command in terminal with the MULTI_USER=true flag highlighted. */}

### 工作原理 {#what-happens}

当有人通过 Open WebUI 使用终端时，Open Terminal 会自动：

1. 根据该用户的 Open WebUI 用户 ID 为其创建个人账户
2. 在 `/home/{user-id}` 设置私有主目录
3. 在其自己的账户下运行所有命令
4. 将每个用户的文件保留在自己的文件夹中

每个用户在文件浏览器中只能看到自己的文件。

{/* TODO: Screenshot: Two views side by side: User A's file browser showing /home/user-a/ with their files, and User B's file browser showing /home/user-b/ with completely different files. */}

### 独立与共享的内容 {#whats-shared-vs-separate}

| | 每用户独立 | 共享 |
| :--- | :--- | :--- |
| 主目录和文件 | 是 | |
| 运行命令 | 是 | |
| 系统软件包 | | 是 |
| CPU 和内存 | | 是 |
| 网络访问 | | 是 |
| 进程列表和命令行 | | 是 |
| 系统状态和容器内的 root 权限 | | 是 |

:::warning 适合小团队，不适合生产环境
此模式给每个人提供独立的工作区，但所有人都运行在同一个容器内。资源压力（内存、CPU）是共享的。网络命名空间是共享的，所以一个用户绑定的端口（例如 `python -m http.server 8080`）可以从该容器上其他任何用户的 shell 访问。端口列表和端口代理的作用域限于拥有该端口的用户，因此端口不会出现在其他用户的文件导航器中，访问它需要从 shell 直接发起请求。进程列表是共享的，所以用户可以看到彼此运行的命令。容器内的 root 权限可以从任何账户访问到，因为首先配置这些账户本身就需要这些权限。

将一个实例上的所有用户视为同样信任，当用户需要彼此保护时使用下方的**方式 2（每用户独立容器）**的 Kubernetes 后端。在上面叠加 [`TERMINAL_PROXY_HEADERS`](/reference/env-configuration#terminal_proxy_headers) 配置可以在浏览器中将代理响应锁定在沙盒 CSP 中，值得做，但不会改变容器内发生的事情。
:::

```mermaid
flowchart LR
    OW["Open WebUI"]

    subgraph container ["Single Open Terminal Container"]
        direction TB
        UA["/home/user-a"]
        UB["/home/user-b"]
        UC["/home/user-c"]
        SH["Shared: CPU, memory,<br/>packages, network"]
    end

    OW --> container

    style OW fill:#4a90d9,color:#fff
    style UA fill:#27ae60,color:#fff
    style UB fill:#27ae60,color:#fff
    style UC fill:#27ae60,color:#fff
    style SH fill:#e67e22,color:#fff
    style container fill:#f0f0f0,stroke:#ccc
```

---

## 方式 2：使用 Terminals 实现每用户独立容器 {#option-2-per-user-containers-with-terminals}

对于较大规模部署或需要真正隔离的场景，[**Terminals**](../terminals/) 为每个用户提供完全独立于其他人的容器。

- **完全隔离** — 每个用户的容器独立运行，拥有各自的文件、进程和资源
- **按需分配** — 容器在用户启动会话时创建，空闲时自动清理
- **资源控制** — 可按用户或按环境设置 CPU、内存和存储限制
- **多环境支持** — 为不同团队提供不同配置（如数据科学、开发等）
- **Kubernetes 支持** — 支持 Docker、Kubernetes 和 k3s
- **按范围限定的工作区** — 通过 [终端上下文](/features/open-terminal/terminals/orchestration/contexts)，可以让每个已保存的聊天或每个自动化拥有自己的工作区，而不是每个用户共用一个
- **Docker 后端上的单一网络** — 所有工作区都位于同一个 Docker 网络中，以便编排器可以按名称访问每个工作区，这也使工作区能够访问其他用户工作区已打开的端口。文件和进程仍然相互隔离。对于互不信任的用户，请使用 Kubernetes 后端并添加 NetworkPolicy

```mermaid
flowchart LR
    OW["Open WebUI"]
    OR["Orchestrator"]
    OW --> OR
    OR --> CA["Container<br/>User A"]
    OR --> CB["Container<br/>User B"]
    OR --> CC["Container<br/>User C"]

    style OW fill:#4a90d9,color:#fff
    style OR fill:#e67e22,color:#fff
    style CA fill:#27ae60,color:#fff
    style CB fill:#27ae60,color:#fff
    style CC fill:#27ae60,color:#fff
```

提供两种部署后端：

- **[Docker 后端](../terminals/#deployment)** — 运行在单个 Docker 宿主机上。适合中小型团队或没有 Kubernetes 的环境。
- **[Kubernetes Operator](../terminals/#deployment)** — 使用基于 CRD 的 Operator 进行生产级部署，通过 Helm chart 与 Open WebUI 一起部署。

:::info 需要企业许可证
Terminals 需要 [Open WebUI 企业许可证](/enterprise)。许可证详情请参阅 [Terminals 仓库](https://github.com/open-webui/terminals)。
:::

## 相关链接 {#related}

- [Terminals 概述 →](../terminals/)
- [Terminals：Docker 后端 →](../terminals/#deployment)
- [Terminals：Kubernetes Operator →](../terminals/#deployment)
- [安全最佳实践 →](./security.md)
- [所有配置选项 →](./configuration.md)
