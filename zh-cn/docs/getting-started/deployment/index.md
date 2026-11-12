---
slug: /deployment/
sidebar_position: 0
title: "部署 Open WebUI"
---

# 部署 Open WebUI {#deploying-open-webui}

选择在你的环境中运行 Open WebUI 的方式。可以从单实例开始；当需要多个应用副本时，再使用共享基础设施。

## 选择部署方式 {#choose-a-deployment}

| 部署方式 | 适用场景 | 指南 |
| :--- | :--- | :--- |
| Docker 或 Python | 你希望在自己管理的机器上跑起一个实例。 | [快速开始](/getting-started/quick-start) |
| Kubernetes | 你的团队运维着集群，并希望通过 Helm 部署。 | [Kubernetes 部署](/deployment/kubernetes) |
| AWS ECS / Fargate | 你希望使用由 AWS 托管的容器任务，并配合应用负载均衡器。 | [AWS ECS / Fargate](/deployment/aws-ecs) |
| Azure 容器应用 | 你希望使用与 Azure 网络和服务集成的托管容器。 | [Azure 容器应用](/deployment/azure-container-apps) |
| Google Cloud Run | 你希望使用托管的 Google Cloud 容器，并能接受请求时长和实例生命周期的限制。 | [Google Cloud Run](/deployment/google-cloud-run) |
| 托管容器服务 | 你的组织在托管容器平台上运行应用。 | [容器服务](/enterprise/deployment/container-service) |
| 虚拟机上的 Python | 你在虚拟机上管理应用进程和扩缩容。 | [虚拟机上的 Python / Pip](/enterprise/deployment/python-pip) |

### Docker Swarm

| 指南 | 内容范围 |
| :--- | :--- |
| [Docker Swarm](/deployment/docker-swarm) | 跨节点的 Swarm 栈，支持 GPU 与非 GPU 场景 |

在你自己管理的机器上运行**单个实例**，或使用 Podman、WSL、Docker Desktop 扩展或纯 Python 环境，相关内容见[快速开始选项卡](/getting-started/quick-start)。镜像标签参考（包括 GPU、Ollama 与 slim 变体）见 [Docker 镜像与标签](/getting-started/quick-start#image-variants)。

Kubernetes 指南同时涵盖持久化的单副本安装，以及使用共享 PostgreSQL、Redis 与对象存储的生产配置。

AWS、Azure 与 Google Cloud 指南分别覆盖各平台的网络、密钥、数据库初始化与更新流程。它们使用外部数据库和对象存储，因此替换应用实例不会丢失持久化数据。

## 为生产环境做准备 {#plan-for-production}

在向用户开放之前，请配置认证、持久化、备份与监控。请参考[加固指南](/getting-started/advanced-topics/hardening)、[扩缩容指南](/getting-started/advanced-topics/scaling)和[监控参考](/reference/monitoring)中的相关配置。

模型推理与 Open WebUI 应用分开配置。请使用[连接模型提供方](/getting-started/quick-start/connect-a-provider)接入已有的模型服务器或托管 API。