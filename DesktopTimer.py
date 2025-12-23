import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import time
import threading
import ctypes  # 用于调用 Windows API
import pystray
from PIL import Image
import sys, os

def resource_path(relative_path):
    """获取打包后资源的正确路径"""
    if hasattr(sys, '_MEIPASS'):  # 如果是 PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
class DesktopTimer:
    def __init__(self):
        # 使用ThemedTk替代Tk，并应用arc主题
        self.root = ThemedTk(theme="arc")
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.setup_drag()
        self.setup_tray()
        # Center the window on startup
        self.center_window()
        
        self.timer_thread = None
        self.is_running = False
        self.is_paused = False
        
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("桌面计时器")
        self.root.geometry("200x120")
        self.root.attributes("-topmost", True)  # 保持在最顶层
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_window)

        # 设置窗口图标（仅在 Windows 上生效）
        try:
            self.root.iconbitmap(resource_path('favicon.ico'))  # 使用同目录下的 icon.ico
        except Exception as e:
            print(f"图标加载失败: {e}")
        
        # 模式状态
        self.mini_mode = False
        
    def setup_variables(self):
        """初始化变量"""
        self.total_seconds = 0
        self.remaining_seconds = 0
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 时间设置框架
        self.time_frame = ttk.Frame(main_frame)
        self.time_frame.pack(fill='x', pady=2)
        
        # 小时滚轮
        ttk.Label(self.time_frame, text="时:", font=('Arial', 8)).pack(side='left')
        self.hours_var = tk.StringVar(value="0")
        vcmd_hours = (self.root.register(self.validate_hours), '%P')
        self.hours_spinbox = ttk.Spinbox(self.time_frame, from_=0, to=23, textvariable=self.hours_var, 
                                         width=3, font=('Arial', 8), wrap=True, command=self.update_time_from_spinbox,
                                         validate='key', validatecommand=vcmd_hours)
        self.hours_spinbox.pack(side='left', padx=1, fill='x', expand=True)
        self.hours_var.trace('w', lambda *args: self.update_time_from_spinbox())
        
        # 分钟滚轮
        ttk.Label(self.time_frame, text="分:", font=('Arial', 8)).pack(side='left', padx=(5, 0))
        self.minutes_var = tk.StringVar(value="5")
        vcmd_minutes = (self.root.register(self.validate_minutes_seconds), '%P')
        self.minutes_spinbox = ttk.Spinbox(self.time_frame, from_=0, to=59, textvariable=self.minutes_var, 
                                           width=3, font=('Arial', 8), wrap=True, command=self.update_time_from_spinbox,
                                           validate='key', validatecommand=vcmd_minutes)
        self.minutes_spinbox.pack(side='left', padx=1, fill='x', expand=True)
        self.minutes_var.trace('w', lambda *args: self.update_time_from_spinbox())
        
        # 秒钟滚轮
        ttk.Label(self.time_frame, text="秒:", font=('Arial', 8)).pack(side='left', padx=(4, 0))
        self.seconds_var = tk.StringVar(value="0")
        vcmd_seconds = (self.root.register(self.validate_minutes_seconds), '%P')
        self.seconds_spinbox = ttk.Spinbox(self.time_frame, from_=0, to=59, textvariable=self.seconds_var, 
                                           width=3, font=('Arial', 8), wrap=True, command=self.update_time_from_spinbox,
                                           validate='key', validatecommand=vcmd_seconds)  
        self.seconds_spinbox.pack(side='left', padx=1, fill='x', expand=True)
        self.seconds_var.trace('w', lambda *args: self.update_time_from_spinbox())
        
        # 显示时间标签
        self.time_label = ttk.Label(main_frame, text="05:00", 
                                font=('Arial', 20, 'bold'), 
                                foreground='#27AE60',
                                anchor='center')
        self.time_label.pack(pady=5, fill='both', expand=True)
        
        # 按钮框架
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.pack(fill='x', pady=2)
        
        # 控制按钮 - 使用ttk.Button以支持主题
        self.start_btn = ttk.Button(self.button_frame, text="开始", width=3, command=self.start_timer,
                                style='Accent.TButton')
        self.start_btn.pack(side='left', padx=5, fill='x', expand=True)
        
        self.pause_btn = ttk.Button(self.button_frame, text="暂停", width=3, command=self.pause_timer)
        self.pause_btn.pack(side='left', padx=5, fill='x', expand=True)
        
        self.reset_btn = ttk.Button(self.button_frame, text="重置", width=3, command=self.reset_timer,
                                style='Danger.TButton')
        self.reset_btn.pack(side='left', padx=5, fill='x', expand=True)
        
    def show_window(self, icon=None, item=None):
        """显示主窗口"""
        print("显示主窗口")
        self.root.after(0, self._show_window_impl)
        
    def _show_window_impl(self):
        """显示窗口的实际实现"""
        try:
            self.switch_to_full_mode()
            self.root.deiconify()  # 显示窗口
            self.root.lift()       # 提升窗口
            self.root.focus_force() # 强制获取焦点
            self.is_hidden = False
            print("窗口已显示")
        except Exception as e:
            print(f"显示窗口时出错: {e}")
        
    def tray_start_timer(self, icon=None, item=None):
        """从托盘开始计时"""
        self.root.after(0, self.start_timer)
        
    def tray_reset_timer(self, icon=None, item=None):
        """从托盘重置计时"""
        self.root.after(0, self.reset_timer)
        

    def quit_app(self, icon=None, item=None):
        """退出应用程序"""
        print("退出应用程序")
        self.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()


    def setup_drag(self):
        """设置窗口拖拽功能"""
        self.start_x = 0
        self.start_y = 0

        def start_drag(event):
            # 检查是否点击的是分钟、秒或小时滚轮，如果是则不执行拖动
            widget = event.widget
            if widget in (self.hours_spinbox, self.minutes_spinbox, self.seconds_spinbox):
                return
            self.start_x = event.x
            self.start_y = event.y

        def drag_window(event):
            # 检查是否点击的是分钟、秒或小时滚轮，如果是则不执行拖动
            widget = event.widget
            if widget in (self.hours_spinbox, self.minutes_spinbox, self.seconds_spinbox):
                return
            x = self.root.winfo_x() + (event.x - self.start_x)
            y = self.root.winfo_y() + (event.y - self.start_y)
            self.root.geometry(f"+{x}+{y}")

        # 绑定拖拽事件到整个窗口
        self.root.bind('<Button-1>', start_drag)
        self.root.bind('<B1-Motion>', drag_window)
        self.time_label.bind('<Button-1>', start_drag)
        self.time_label.bind('<B1-Motion>', drag_window)

        # 双击时间标签切换模式
        self.time_label.bind('<Double-Button-1>', self.toggle_mode)
        
    def validate_hours(self, value):
        """验证小时输入"""
        if value == "":
            return True
        try:
            val = int(value)
            return 0 <= val <= 23
        except ValueError:
            return False

    def validate_minutes_seconds(self, value):
        """验证分钟和秒钟输入"""
        if value == "":
            return True
        try:
            val = int(value)
            return 0 <= val <= 59
        except ValueError:
            return False
        
    def start_timer(self):
        """开始计时"""
        if not self.is_running and not self.is_paused:
            # 获取设置的时间
            try:
                hours = int(self.hours_var.get() or 0)  # 加入小时
                minutes = int(self.minutes_var.get() or 0)
                seconds = int(self.seconds_var.get() or 0)
                self.total_seconds = hours * 3600 + minutes * 60 + seconds  # 计算总秒数
                self.remaining_seconds = self.total_seconds
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字！")
                return
                
            if self.total_seconds <= 0:
                messagebox.showerror("错误", "请设置大于0的时间！")
                return
        
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_btn.config(text="运行中", state='disabled')
            self.pause_btn.config(state='normal')
            
            # 切换到迷你模式
            self.switch_to_mini_mode()
            
            # 在新线程中运行计时器
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()

    def pause_timer(self):
        """暂停/恢复计时"""
        if self.is_running:
            if self.is_paused:
                self.is_paused = False
                self.pause_btn.config(text="暂停")
                self.start_btn.config(text="运行中", state='disabled')
            else:
                self.is_paused = True
                self.pause_btn.config(text="继续")
                self.start_btn.config(text="开始", state='normal')
    
    def reset_timer(self):
        """重置计时器"""
        self.is_running = False
        self.is_paused = False
        self.start_btn.config(text="开始", state='normal')
        self.pause_btn.config(text="暂停", state='normal')
        
        # 切换回完整模式
        self.switch_to_full_mode()
        
        # 重置显示
        try:
            hours = int(self.hours_var.get() or 0)
            minutes = int(self.minutes_var.get() or 0)
            seconds = int(self.seconds_var.get() or 0)
            self.update_display(hours * 60 * 60 + minutes * 60 + seconds)
        except ValueError:
            self.update_display(0)
    
    def position_bottom_right(self):
        """窗口位置在右下角"""
        self.root.update_idletasks()  # 更新窗口大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # 右下角位置（考虑到任务栏高度约40px）
        x = screen_width - window_width - 10  # 任务栏10px边距
        y = screen_height - window_height - 50  # 任务栏50px边距
        
        self.root.geometry(f"+{x}+{y}")
    # 调整窗口大小和位置以适应迷你模式
    def switch_to_mini_mode(self):
        """切换到迷你模式（仅显示时间标签，无其他控件，圆角窗口）"""
        if not self.mini_mode:
            self.mini_mode = True
            # 隐藏设置框架和按钮框架
            self.time_frame.pack_forget()
            self.button_frame.pack_forget()
            # 调整窗口大小，根据是否显示小时来决定
            hours = int(self.hours_var.get() or 0)
            if hours:
                self.root.geometry("100x40")  # 显示小时时的窗口尺寸
            else:
                self.root.geometry("70x40")  # 不显示小时时的窗口尺寸

            self.time_label.config(font=('Arial', 16, 'bold'), foreground='#27AE60')
            # 先更新一次显示，避免切换时出现闪烁
            self.root.update_idletasks()
            self.time_label.pack(expand=True, fill='both')  # 居中显示时间标签
            self.root.overrideredirect(True)  # 移除窗口边框
            self.root.wm_attributes("-alpha", 0.8) # 设置透明度
            # 设置圆角窗口
            self.set_rounded_corners(20)
            # 设置右下角位置
            self.root.after(10, self.position_bottom_right) 

    # 调整窗口大小和位置以适应完整模式
    def switch_to_full_mode(self):
        """切换到完整模式（恢复所有控件，取消圆角）"""
        if self.mini_mode:
            self.mini_mode = False
            # 恢复设置框架和按钮框架
            self.time_frame.pack(fill='x', pady=2, before=self.time_label)
            self.button_frame.pack(fill='x', pady=2)
            # 恢复窗口大小和边框
            self.root.geometry("200x120")
            self.time_label.config(font=('Arial', 20, 'bold'), foreground='#27AE60')
            self.root.overrideredirect(False)  # 恢复窗口边框

            # 取消圆角窗口
            self.set_rounded_corners(0)
            # 取消透明度
            self.root.wm_attributes("-alpha", 1.0) 
            # 完整mode时居中显示
            self.root.after(10, self.center_window)

    def set_rounded_corners(self, radius):
        """设置窗口圆角（仅适用于 Windows 10 及以上）"""
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())  # 获取窗口句柄
        DWM_WINDOW_CORNER_PREFERENCE = 2  # 圆角偏好
        DWMWA_WINDOW_CORNER_PREFERENCE = 33  # 圆角属性
        preference = ctypes.c_int(DWM_WINDOW_CORNER_PREFERENCE if radius > 0 else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(preference), ctypes.sizeof(preference)
        )

    def toggle_mode(self, event=None):
        """切换显示模式（双击时间标签触发）"""
        if self.mini_mode:
            self.switch_to_full_mode()
        else:
            self.switch_to_mini_mode()
    
    def run_timer(self):
        """运行计时器主循环"""
        while self.is_running and self.remaining_seconds > 0:
            if not self.is_paused:
                self.root.after(0, lambda: self.update_display(self.remaining_seconds))
                time.sleep(1)
                self.remaining_seconds -= 1
            else:
                time.sleep(0.1)  # 暂停时短暂休眠
        
        if self.is_running:  # 如果是正常结束（而不是被重置）
            self.root.after(0, self.timer_finished)
    
    def update_display(self, seconds):
        """更新时间显示"""
        hours = seconds // 3600  # 计算小时
        minutes = (seconds % 3600) // 60  # 计算分钟
        secs = seconds % 60  # 计算秒
        # 小时为0时不显示小时（主界面和迷你模式保持一致）
        if hours:
            time_text = f"{hours:02d}:{minutes:02d}:{secs:02d}"  # 显示小时:分钟:秒
        else:
            time_text = f"{minutes:02d}:{secs:02d}"  # 小时为0时不显示小时
        self.time_label.config(text=time_text)
        
        # 根据剩余时间改变颜色
        if seconds <= 10:
            self.time_label.config(foreground='#E74C3C')  # 红色
        elif seconds <= 60:
            self.time_label.config(foreground='#F39C12')  # 橙色
        else:
            self.time_label.config(foreground='#27AE60')  # 绿色

        if self.mini_mode:
            # 当处于迷你模式且显示格式从有小时/无小时切换时，调整宽度并保持右下角对齐
            desired_width = 100 if hours else 70
            current_width = self.root.winfo_width()
            if current_width != desired_width:
                # 改变尺寸后延迟重新定位，确保窗口大小已生效
                self.root.geometry(f"{desired_width}x40")
                self.root.after(10, self.position_bottom_right)
    
    def timer_finished(self):
        """计时结束处理"""
        self.is_running = False
        self.is_paused = False
        self.time_label.config(text="00:00", foreground='#E74C3C')
        
        # 切换回完整模式以显示按钮
        self.switch_to_full_mode()
        
        self.start_btn.config(text="开始", state='normal')
        self.pause_btn.config(text="暂停", state='normal')
        
        # 显示提醒
        messagebox.showinfo("时间到！", "倒计时结束！")
        
        # 闪烁效果
        self.flash_window()

    def center_window(self):
        """将窗口移动到屏幕中央"""
        self.root.update_idletasks()  # 更新窗口信息
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"+{x}+{y}")

    def flash_window(self):
        """窗口闪烁提醒"""
        for i in range(6):
            if i % 2 == 0:
                self.time_label.configure(foreground='#E74C3C')  # 闪烁时改变文字颜色
            else:
                self.time_label.configure(foreground='#27AE60')  # 恢复正常颜色
            self.root.update()
            time.sleep(0.5)
    
    def update_time_from_spinbox(self):
        """根据滚轮的值实时更新时间显示"""
        try:
            hours = int(self.hours_var.get() or 0)  # 加入小时
            minutes = int(self.minutes_var.get() or 0)
            seconds = int(self.seconds_var.get() or 0)
            total_seconds = hours * 3600 + minutes * 60 + seconds  # 计算总秒数
            self.update_display(total_seconds)
        except ValueError:
            pass  # 如果输入无效，忽略更新

    def setup_tray(self):
        """设置系统托盘"""
        try:
            
            # 创建托盘菜单
            menu = pystray.Menu(
                pystray.MenuItem("显示主窗口", self.show_window, default=True),
                pystray.MenuItem("开始计时", self.tray_start_timer),
                pystray.MenuItem("重置计时", self.tray_reset_timer),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("退出", self.quit_app)
            )
            
            # 创建托盘图标对象
            self.tray_icon = pystray.Icon("DesktopTimer", Image.open(resource_path('favicon.ico')), "桌面计时器", menu)
            
        except Exception as e:
            print(f"创建托盘时出错: {e}")
            self.tray_icon = None
        
    def hide_to_tray(self):
        """隐藏窗口到系统托盘"""
        self.root.withdraw()  # 隐藏窗口
        self.is_hidden = True

    def on_close_window(self):
        """处理点击 X 按钮的事件，变成迷你模式"""
        self.switch_to_mini_mode()

    def run_tray(self):
        """运行系统托盘"""
        if self.tray_icon:
            try:
                print("开始运行托盘图标")
                self.tray_icon.run()
            except Exception as e:
                print(f"运行托盘图标时出错: {e}")

    def run(self):
        """启动程序"""
        if not hasattr(self, 'tray_running') or not self.tray_running:
            # 在新线程中启动托盘图标
            self.tray_running = True
            tray_thread = threading.Thread(target=self.run_tray, daemon=True)
            tray_thread.start()

        self.root.mainloop()

if __name__ == "__main__":
    timer = DesktopTimer()
    timer.run()