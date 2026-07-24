---
title: Windows
sidebar_position: 3
---

# Windows

在 PowerShell 中：

```powershell
py -m pip install cptr
cptr run
```

你的浏览器会打开 `http://localhost:8000`。如果安装后 `cptr` 无法识别，说明 Python 的 Scripts 目录不在 PATH 上。添加后重新打开 PowerShell，或者在虚拟环境中安装并从那里运行 `cptr`。

## 终端因缺少 VCRUNTIME140.dll 而失败

如果打开终端报告缺少 `VCRUNTIME140.dll` 或 Universal CRT DLL，请安装 Microsoft 的 [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)，然后重启 `cptr`。

## 应该使用哪个账户运行

Open WebUI Computer 以启动它的 Windows 账户的权限运行；该账户的权限决定了文件浏览器和终端可以访问的范围。使用你的普通账户；不要仅仅为了让文件夹更容易访问而以管理员身份运行。

## 保持运行

要让 Open WebUI Computer 自动启动并在注销后继续运行，请参见[保持运行](/ecosystem/computer/phone-and-remote/keep-it-running)。
