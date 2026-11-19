## 使用虚拟环境 {#using-virtual-environments}

使用 `venv` 创建隔离的 Python 环境。

### Venv 步骤 {#venv-steps}

1. **创建虚拟环境：**

   ```bash
   python3 -m venv venv
   ```

2. **激活虚拟环境：**

   - 在 Linux/macOS 上：

     ```bash
     source venv/bin/activate
     ```

   - 在 Windows 上：

     ```bash
     venv\Scripts\activate
     ```

3. **安装 Open WebUI：**

   ```bash
   pip install open-webui
   ```

4. **启动服务：**

   ```bash
   open-webui serve
   ```

:::tip 出现 “open-webui: command not found”？
如果终端提示找不到命令：
1. 请确认虚拟环境已经**激活**（第 2 步）。
2. 如果你想把数据存到指定位置，可使用：`DATA_DIR=./data open-webui serve`
:::

### 卸载 {#uninstall}

1.  **删除虚拟环境：**
    直接删除 `venv` 文件夹即可：
    ```bash
    rm -rf venv
    ```

2.  **删除数据（警告：会删除所有数据）：**
    如果没有设置 `DATA_DIR`，数据目录位于 venv 环境内（`.../site-packages/open_webui/data`），删除 `venv` 文件夹时数据也会一并删除。如果设置了 `DATA_DIR`，则删除该变量所指向的目录：
    ```bash
    rm -rf ~/.open-webui
    ```

---
