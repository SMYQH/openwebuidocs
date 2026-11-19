# Podman Quadlet（systemd） {#podman-quadlets-systemd}

Podman Quadlet 允许你把容器作为原生 systemd 服务进行管理。这是在使用 systemd 的 Linux 发行版（如 Fedora、RHEL、Ubuntu 等）上运行生产容器的推荐方式。

## 🛠️ 配置 {#setup}

1. **创建配置目录：**
   如果是 rootless 用户部署：
   ```bash
   mkdir -p ~/.config/containers/systemd/
   ```

2. **创建容器文件：**
   新建 `~/.config/containers/systemd/open-webui.container`，内容如下：

   ``` ini title="open-webui.container"
   [Unit]
   Description=Open WebUI Container
   After=network-online.target

   [Container]
   Image=ghcr.io/open-webui/open-webui:main
   ContainerName=open-webui
   PublishPort=3000:8080
   Volume=open-webui:/app/backend/data
   Environment=WEBUI_SECRET_KEY=your-secret-key
   
   # Networking: Pasta is used by default in Podman 5+
   # If you need to access host services (like Ollama on the host):
   AddHost=host.containers.internal:host-gateway
   Environment=OLLAMA_BASE_URL=http://host.containers.internal:11434

   [Service]
   Restart=always

   [Install]
   WantedBy=default.target
   ```

3. **重新加载 systemd 并启动服务：**
   ```bash
   systemctl --user daemon-reload
   systemctl --user start open-webui
   ```

4. **设置开机自启：**
   ```bash
   systemctl --user enable open-webui
   ```

## 📊 管理 {#management}

- **查看状态：**
  ```bash
  systemctl --user status open-webui
  ```

- **查看日志：**
  ```bash
  journalctl --user -u open-webui -f
  ```

- **停止服务：**
  ```bash
  systemctl --user stop open-webui
  ```

:::tip 更新
更新镜像时，只需拉取新版本（`podman pull ghcr.io/open-webui/open-webui:main`），然后重启服务（`systemctl --user restart open-webui`）。
:::
