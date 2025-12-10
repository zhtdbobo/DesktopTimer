# DesktopTimer
轻量级桌面倒计时工具

## 介绍

一个基于Python和Tkinter的轻量级桌面倒计时工具，具有以下特点：

- 直观的图形界面，支持小时、分钟、秒设置
- 可拖拽的窗口设计，支持双击时间区域切换显示模式
- 运行时自动切换到迷你模式，显示在屏幕右下角（圆角、透明效果）
- 点击关闭按钮（X）可切换到迷你模式（不退出程序）
- 系统托盘集成，可通过托盘菜单快速操作
- 倒计时结束时弹窗提醒并伴有闪烁效果
- 支持开始、暂停、继续和重置功能
- 时间色彩提醒：剩余 ≤10 秒红色、≤60 秒橙色、否则绿色
- 主界面和迷你模式时间显示同步（小时为 0 时不显示）
- 适用于Windows系统的桌面时间管理工具

## 功能说明

### 主界面（完整模式）
- 设置小时、分钟、秒
- 三个控制按钮：开始、暂停、重置
- 实时显示当前设置的时间

### 迷你模式（小窗模式）
- 仅显示时间倒计时
- 圆角、80% 透明度设计
- 自动位于屏幕右下角
- 点击时间区域可切换回完整模式

### 时间显示规则
- **有小时时**：显示 `HH:MM:SS` 格式
- **无小时时**：显示 `MM:SS` 格式（更简洁）
- 规则适用于主界面和迷你模式

### 系统托盘
- 右键菜单支持：显示主窗口、开始计时、重置计时、退出

## 界面
<img width="302" height="228" alt="image" src="https://github.com/user-attachments/assets/a6f59f2f-8087-40ab-b5f5-9f4ad70d7de9" />


<img width="70" height="40" alt="image" src="https://github.com/user-attachments/assets/abb93fac-aefe-4cf2-9ce9-090a8c4c4a51" />

## 打包

### 使用 PyInstaller 打包

```bash
# 基础打包命令（包含图标和数据文件）
pyinstaller -F -w -i favicon.ico -n "DesktopTimer" DesktopTimer.py --add-data "favicon.ico;."
```

### 使用预配置的 spec 文件

```bash
pyinstaller DesktopTimer.spec
```

## 依赖

- tkinter（Python 内置）
- ttkthemes（主题支持）
- pillow（图像处理）
- pystray（系统托盘）

### 安装依赖

```bash
pip install ttkthemes pillow pystray
```

## 使用说明

1. 在主界面设置倒计时时间
2. 点击"开始"按钮开始计时
3. 运行时会自动切换到迷你模式（右下角）
4. 可随时点击时间区域切换回主界面
5. 点击"暂停"可暂停/继续计时
6. 点击"重置"回到初始状态
7. 关闭窗口（X 按钮）会切换到迷你模式，托盘菜单可退出程序
