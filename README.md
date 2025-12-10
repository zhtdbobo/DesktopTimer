# DesktopTimer
轻量级桌面倒计时工具

## 介绍

一个基于Python和Tkinter的轻量级桌面倒计时工具，具有以下特点：

- 直观的图形界面，支持小时、分钟、秒设置
- 可拖拽的窗口设计，支持双击切换显示模式
- 运行时自动切换到迷你模式，显示在屏幕右下角
- 倒计时结束时弹窗提醒并伴有闪烁效果
- 支持开始、暂停、继续和重置功能
- 时间不足时会变色提醒（绿色→橙色→红色）
- 适用于Windows系统的桌面时间管理工具

## 界面
<img width="302" height="228" alt="PixPin_2025-08-28_11-55-37" src="https://github.com/user-attachments/assets/9a96f78c-90ba-44c8-839a-66857581bfe6" />

<img width="105" height="60" alt="PixPin_2025-08-28_11-54-05" src="https://github.com/user-attachments/assets/5b5b35e6-4e09-40cc-ab54-93889e312222" />

## 打包
```bash
pyinstaller DesktopTimer.spec
```
