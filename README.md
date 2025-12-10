# DesktopTimer
轻量级桌面倒计时工具

## 介绍

一个基于Python和Tkinter的轻量级桌面倒计时工具，具有以下特点：

- 直观的图形界面，支持小时、分钟、秒设置
- 可拖拽的窗口设计，支持双击切换显示模式
- 运行时自动切换到迷你模式，显示在屏幕右下角
- 倒计时结束时弹窗提醒并伴有闪烁效果
- 支持开始、暂停、继续和重置功能
- 时间不足时会变色提醒
- 适用于Windows系统的桌面时间管理工具

## 界面
<img width="302" height="228" alt="image" src="https://github.com/user-attachments/assets/a6f59f2f-8087-40ab-b5f5-9f4ad70d7de9" />


<img width="70" height="40" alt="image" src="https://github.com/user-attachments/assets/abb93fac-aefe-4cf2-9ce9-090a8c4c4a51" />

## 打包
```bash
pyinstaller DesktopTimer.spec
```
