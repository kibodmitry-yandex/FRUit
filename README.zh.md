[English](README.md) · [Русский](README.ru.md) · [中文](README.zh.md)

# FRUit — 文件夹恢复工具

**F**older **R**estore **U**tility（for **E**xplorer navigation）—— 一款
Windows 11 工具：保存资源管理器的窗口与标签页，并在需要时把它们恢复回来。

每次重启后都要重新打开十几个文件夹？更糟的是 `explorer.exe` 崩溃之后？
Windows 自带的恢复并不可靠，崩溃后往往失效。FRUit 会记住布局并恢复它：
按分组、按单个窗口，或全部恢复。

## 功能

- **窗口与标签页快照**（通过 `IShellWindows`），每个标签页按唯一地址保存。
- **窗口几何与状态**（位置、大小、最大化/普通）通过
  `GetWindowPlacement` / `SetWindowPos` 恢复。
- **托盘图标**（带香蕉的文件夹）：已保存的标签组（🗂，按首个标签命名）与
  单个窗口（🗀）。每个条目有子菜单 —— 组成（灰色、只读）、*恢复*、
  *✕ 删除*，另有 *全部恢复*。
- **不产生重复**：相同的标签集合不会保存两次；若布局已经打开，只会把该窗口
  带到前台，而不会重新打开。
- **全局热键**：`Ctrl+Alt+S` 制作快照，`Ctrl+Alt+R` 全部恢复。
- **静默托盘**：不弹出控制台窗口；错误写入 `logs\fruit.log`（超过 1 MB 自动
  轮转）。
- **精简 `FRUit.exe` 启动器**：用自己的环境运行当前 Python 代码，改代码后无需
  重新编译。
- **命令行命名快照**：把布局保存为工作/家庭等方案。

## 安装

要求：Windows 11，并且联网（用于安装 Python 和 pip）。

**最简单的方式：**

1. 下载仓库 ZIP 压缩包（*Code → Download ZIP*）或克隆仓库：
   `git clone https://github.com/kibodmitry-yandex/FRUit.git`
2. 双击 **`install.bat`**：它会查找 Python 3.9+（没有则通过 winget 静默
   安装），创建 `.venv` 并安装依赖。
3. 运行 **`FRUit.exe`** —— 托盘中出现图标。

手动安装：

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`FRUit.exe` 使用仓库自带的 `.venv`，请勿移动该文件夹。

## 使用

### 托盘（主要模式）

双击 `FRUit.exe` —— 系统托盘出现“带香蕉的文件夹”图标（不弹出控制台）。
右键 → 菜单：

```
制作快照                           ← 保存当前窗口/标签（不重复）
全部恢复                           ← 打开列表中的全部
────────────────────────────────────🗂 Projects (5 个标签)  ┐ 分组组成（灰色、只读）：
        • src • docs              │ 也就是“恢复”将打开的内容；
        • tests • media           ┘ 单个窗口则显示完整路径
        ────────────────────────
        恢复
        ✕ 删除🗀 Downloads
        • C:\Users\me\Downloads
        ────────────────────────
        恢复
        ✕ 删除
────────────────────────────────────数据文件夹
退出
```

> 说明：实际菜单目前为俄语，对照如下。

| 菜单原文 | 含义 |
|---|---|
| Сделать снапшот | 制作快照 |
| Восстановить все | 全部恢复 |
| Восстановить | 恢复 |
| ✕ Удалить | ✕ 删除 |
| Папка данных | 数据文件夹 |
| Выход | 退出 |

点击布局行会打开子菜单：Windows 的菜单一行只有一个点击区域，因此
*恢复* 位于子菜单内。已打开的布局不会重复创建 —— 窗口会被带到前台，
几何与当前标签保持不变。

全局热键：`Ctrl+Alt+S` 快照，`Ctrl+Alt+R` 全部恢复。
已保存布局位于 `%LOCALAPPDATA%\FRUit\groups.json`。

### 命令行（命名快照）

```bat
FRUit.exe save work                      :: 把当前布局保存为 work
FRUit.exe list                           :: 列出快照
FRUit.exe restore work                   :: 恢复（标签页会合并进窗口）
FRUit.exe restore work --no-tabs         :: 更稳妥：每个文件夹单独开窗
FRUit.exe restore latest                 :: 恢复最新快照
FRUit.exe delete work                    :: 删除快照
```

数据：默认在 `%LOCALAPPDATA%\FRUit`（`snapshots\*.json` 为命名快照，
`groups.json` 为托盘列表），可用环境变量 `FRUIT_DATA` 改位置。
`FRUIT_HOME` 是另一回事：存放 `fruit` **包**的目录，供启动器使用。

## 工作原理

- 通过 `IShellWindows` 枚举窗口与标签页（按窗口句柄分组）。
- 第一个标签通过 `explorer.exe` 打开；其余标签通过 UI 自动化 Invoke
  “新建标签”按钮添加，并用 `IWebBrowser2.Navigate` 导航到地址。
- 若无法添加标签，则以**独立窗口**打开该文件夹（回退方案）—— 任何文件夹
  都不会丢失。
- 窗口几何：`GetWindowPlacement` / `SetWindowPos`。

Windows 11 的资源管理器标签页基于 XAML/WinUI 实现，**没有公开的官方 API**
（参见 [Microsoft Learn](https://learn.microsoft.com/en-us/answers/questions/5852400/)），
因此使用 UI 自动化并带回退方案。

## 限制

- **标签页通过 UI 自动化创建。** 若按钮或导航不可用，则以独立窗口恢复：
  结果接近，但保证完整。
- **菜单项没有图标**（Win32/pystray 限制），分组与窗口用字符 🗂 / 🗀 区分。
- **一行菜单只有一个点击区域**：点击条目会打开其子菜单，所以 *恢复* 放在
  子菜单里，而不是行本身。
- **虚拟文件夹**（此电脑、快速访问、回收站）没有文件路径，会跳过并提示；
  只处理 `CabinetWClass` 窗口。
- 文件夹名中的 **`&`** 在菜单文本中会显示为两个（Win32 助记键规则）。

## 开发

- `launcher\` —— 精简 exe 源码（`FruitLauncher.cs`）、`build_launcher.bat`
  （用系统 `csc.exe` 编译）和图标生成器 `make_icon.py`。
- `tools\` —— 开发与测试脚本，不属于发布内容。
- 图标：`launcher\logo.png` → `python launcher\make_icon.py` 重新生成
  `fruit.ico` / `fruit.png`（16…256 px 各尺寸）。没有该 PNG 时图标由
  Pillow 代码绘制，一切照常。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
