# fa-tui

一个`frida`的终端 TUI 工具，用于选择 `frida-ps -Uai` 输出的进程和本地目录中的 JS 文件，并以 spawn 或 attach 模式执行 Frida 注入命令。

> ⚠️ **注意**  
> 本工具设计用于 Android 设备的 Frida Hook，依赖 `frida` 和 `frida-ps` 命令正确连接 Android 设备（如通过 USB 或 TCP 连接的设备）。

## ✨ 功能特点

- 实时列出 `frida-ps -Uai` 获取的 Android 设备进程列表
- 自动扫描当前目录下的 JS 脚本文件
- 支持切换 `spawn` / `attach` 模式（默认 `spawn`，按 `M` 切换）
- 支持鼠标和键盘操作选择进程和脚本，回车自动执行注入命令

## 📦 安装方式


```bash
pip install fa-tui
````

## 🚀 使用方法

在终端中运行：

```bash
fa-tui
```

交互界面将展示：
* 左侧：`frida-ps -Uai` 输出的 Android 进程列表
* 右侧：当前目录中的 JS 文件列表
* 底部：当前注入模式，按 `M` 键可切换 `spawn` 和 `attach` 模式
* 按 Ctrl+Q 可随时退出程序

选中 JS 文件和目标进程后，按下 `Enter` 键，将会自动执行：

```bash
frida -U -f 包名 -l 脚本.js   # spawn 模式
# 或
frida -U -n 包名 -l 脚本.js   # attach 模式
```

## 🔧 依赖项

* Python 3.8+

* 已安装并配置 `frida` 命令行工具（`frida` 与 `frida-ps`）

* Android 设备连接且可用 `frida-ps -Uai` 正确列出进程

* [Textual](https://github.com/Textualize/textual)
