import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import sys
from datetime import datetime, timedelta
import winreg

class CalendarPicker(tk.Toplevel):
    def __init__(self, parent, initial_date=None, on_select=None):
        super().__init__(parent)
        self.parent = parent
        self.on_select = on_select
        
        # 设置窗口属性
        self.title("日期选择")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # 初始化日期
        if initial_date:
            try:
                self.current_date = datetime.strptime(initial_date, "%Y-%m-%d")
            except ValueError:
                self.current_date = datetime.now()
        else:
            self.current_date = datetime.now()
        
        # 保存当前显示的月份和年份
        self.display_year = self.current_date.year
        self.display_month = self.current_date.month
        
        # 创建UI
        self.create_widgets()
        
        # 应用主题
        self.apply_theme()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题栏（月份和年份）
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 上一个月按钮
        self.prev_month_btn = ttk.Button(title_frame, text="◀", command=self.prev_month, width=3)
        self.prev_month_btn.pack(side=tk.LEFT, padx=5)
        
        # 月份和年份显示
        self.title_label = ttk.Label(title_frame, text="", font=("Segoe UI", 12, "bold"))
        self.title_label.pack(side=tk.LEFT, expand=True)
        
        # 下一个月按钮
        self.next_month_btn = ttk.Button(title_frame, text="▶", command=self.next_month, width=3)
        self.next_month_btn.pack(side=tk.RIGHT, padx=5)
        
        # 星期标题
        days = ["日", "一", "二", "三", "四", "五", "六"]
        days_frame = ttk.Frame(main_frame)
        days_frame.pack(fill=tk.X)
        
        for day in days:
            ttk.Label(days_frame, text=day, width=4, anchor=tk.CENTER).pack(side=tk.LEFT, expand=True)
        
        # 日期网格
        self.days_frame = ttk.Frame(main_frame)
        self.days_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建日期按钮网格
        self.create_days_grid()
        
        # 今天按钮
        today_frame = ttk.Frame(main_frame)
        today_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(today_frame, text="今天", command=self.select_today).pack(side=tk.RIGHT)
    
    def create_days_grid(self):
        # 清空现有日期按钮
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        
        # 更新标题
        self.title_label.config(text=f"{self.display_month}月 {self.display_year}")
        
        # 获取当月第一天是星期几
        first_day = datetime(self.display_year, self.display_month, 1)
        start_weekday = first_day.weekday()  # 0=周一, 6=周日
        
        # 调整为周日开始
        start_weekday = (start_weekday + 1) % 7
        
        # 获取当月天数
        if self.display_month == 12:
            next_month = 1
            next_year = self.display_year + 1
        else:
            next_month = self.display_month + 1
            next_year = self.display_year
        
        days_in_month = (datetime(next_year, next_month, 1) - timedelta(days=1)).day
        
        # 计算需要显示的总天数（包括上个月和下个月的部分日期）
        total_days = start_weekday + days_in_month
        rows = (total_days + 6) // 7
        
        # 获取上个月的天数
        if self.display_month == 1:
            prev_month = 12
            prev_year = self.display_year - 1
        else:
            prev_month = self.display_month - 1
            prev_year = self.display_year
        
        days_in_prev_month = (datetime(self.display_year, self.display_month, 1) - timedelta(days=1)).day
        
        # 创建日期按钮
        day_num = 1 - start_weekday
        
        for row in range(rows):
            for col in range(7):
                if day_num < 1:
                    # 上个月的日期
                    prev_day = days_in_prev_month + day_num
                    btn = ttk.Button(self.days_frame, text=str(prev_day), width=4, state=tk.DISABLED, style="DisabledDate.TButton")
                elif day_num > days_in_month:
                    # 下个月的日期
                    next_day = day_num - days_in_month
                    btn = ttk.Button(self.days_frame, text=str(next_day), width=4, state=tk.DISABLED, style="DisabledDate.TButton")
                else:
                    # 当月的日期
                    btn = ttk.Button(self.days_frame, text=str(day_num), width=4, style="Date.TButton")
                    btn.config(command=lambda d=day_num: self.select_date(d))
                    
                    # 高亮今天
                    today = datetime.now()
                    if self.display_year == today.year and self.display_month == today.month and day_num == today.day:
                        btn.config(style="TodayDate.TButton")
                    
                    # 高亮当前选中的日期
                    if self.display_year == self.current_date.year and self.display_month == self.current_date.month and day_num == self.current_date.day:
                        btn.config(style="SelectedDate.TButton")
                
                btn.grid(row=row, column=col, padx=2, pady=2, sticky=tk.NSEW)
                day_num += 1
    
    def prev_month(self):
        if self.display_month == 1:
            self.display_month = 12
            self.display_year -= 1
        else:
            self.display_month -= 1
        self.create_days_grid()
    
    def next_month(self):
        if self.display_month == 12:
            self.display_month = 1
            self.display_year += 1
        else:
            self.display_month += 1
        self.create_days_grid()
    
    def select_date(self, day):
        selected_date = datetime(self.display_year, self.display_month, day)
        if self.on_select:
            self.on_select(selected_date.strftime("%Y-%m-%d"))
        self.destroy()
    
    def select_today(self):
        today = datetime.now()
        if self.on_select:
            self.on_select(today.strftime("%Y-%m-%d"))
        self.destroy()
    
    def apply_theme(self):
        # 创建样式
        style = ttk.Style()
        
        # 获取父窗口的主题
        is_dark_mode = False
        if hasattr(self.parent, 'is_dark_mode'):
            is_dark_mode = self.parent.is_dark_mode
        
        # 根据主题设置不同的样式
        if is_dark_mode:
            # 暗色主题
            style.configure("Date.TButton", padding=5, background="#2d2d30", foreground="#ffffff")
            style.map("Date.TButton", background=[("active", "#404040")])
            
            # 选中日期样式
            style.configure("SelectedDate.TButton", background="#5ba0e5", foreground="white")
            style.map("SelectedDate.TButton", background=[("active", "#4a90e2")])
            
            # 今天日期样式
            style.configure("TodayDate.TButton", background="#2ecc71", foreground="white")
            style.map("TodayDate.TButton", background=[("active", "#27ae60")])
            
            # 禁用日期样式
            style.configure("DisabledDate.TButton", foreground="#666666", background="#2d2d30")
            
            # 窗口背景
            self.configure(bg="#1e1e1e")
        else:
            # 亮色主题
            # 日期按钮样式
            style.configure("Date.TButton", padding=5, background="#ffffff", foreground="#333333")
            style.map("Date.TButton", background=[("active", "#e0e0e0")])
            
            # 选中日期样式
            style.configure("SelectedDate.TButton", background="#4a90e2", foreground="white")
            style.map("SelectedDate.TButton", background=[("active", "#357abd")])
            
            # 今天日期样式
            style.configure("TodayDate.TButton", background="#2ecc71", foreground="white")
            style.map("TodayDate.TButton", background=[("active", "#27ae60")])
            
            # 禁用日期样式
            style.configure("DisabledDate.TButton", foreground="#9e9e9e", background="#ffffff")
            
            # 窗口背景
            self.configure(bg="#f5f5f5")

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo List")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # 使用系统默认的标题栏，以便正常使用最小化功能
        # 移除 overrideredirect(True) 标志，因为它会导致 iconify() 方法失效
        
        # 窗口调整大小相关变量
        self.resize_mode = False
        self.resize_edge = None
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_width = 0
        self.resize_start_height = 0
        
        # 允许窗口调整大小
        self.root.bind("<Motion>", self.on_motion)
        # 只有在点击窗口边缘时才触发调整大小
        self.root.bind("<Button-1>", self.start_resize, add="+")
        self.root.bind("<B1-Motion>", self.resize_window, add="+")
        self.root.bind("<ButtonRelease-1>", self.stop_resize)
        
        # 窗口拖动相关变量
        self.drag_x = 0
        self.drag_y = 0
        
        # 窗口拖动事件绑定
        self.root.bind("<Button-1>", self.start_drag, add="+")
        self.root.bind("<B1-Motion>", self.drag_window, add="+")
        
        # 设置数据文件路径到用户主目录
        self.setup_data_file()
        
        # 加载任务数据
        self.tasks = self.load_tasks()
        
        # 主题相关
        self.is_dark_mode = False
        self.load_theme_preference()
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # 定义颜色方案
        self.define_color_schemes()
        
        # 应用当前主题
        self.apply_theme()
        
        # 创建UI
        self.create_widgets()
        
        # 更新任务列表
        self.update_task_list()
        
        # 窗口置顶
        self.root.wm_attributes("-topmost", True)
    
    def setup_data_file(self):
        """设置数据文件路径并确保目录存在"""
        # 获取用户主目录
        user_home = os.path.expanduser("~")
        
        # 创建数据目录
        self.data_dir = os.path.join(user_home, ".todo")
        
        # 确保目录存在
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建数据目录: {e}")
                self.root.quit()
        
        # 设置数据文件路径
        self.data_file = os.path.join(self.data_dir, "todos.json")
        # 设置主题偏好文件路径
        self.theme_file = os.path.join(self.data_dir, "theme.json")
    
    def load_theme_preference(self):
        """加载用户的主题偏好设置"""
        try:
            if os.path.exists(self.theme_file):
                with open(self.theme_file, "r", encoding="utf-8") as f:
                    theme_data = json.load(f)
                    self.is_dark_mode = theme_data.get("dark_mode", False)
        except Exception as e:
            print(f"加载主题偏好失败: {e}")
            self.is_dark_mode = False
    
    def save_theme_preference(self):
        """保存用户的主题偏好设置"""
        try:
            with open(self.theme_file, "w", encoding="utf-8") as f:
                json.dump({"dark_mode": self.is_dark_mode}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存主题偏好失败: {e}")
    
    def define_color_schemes(self):
        """定义亮色和暗色主题的颜色方案"""
        # 亮色主题
        self.light_theme = {
            "primary_color": "#4a90e2",
            "secondary_color": "#50e3c2",
            "danger_color": "#e74c3c",
            "warning_color": "#f39c12",
            "success_color": "#2ecc71",
            "background_color": "#f5f5f5",
            "card_color": "#ffffff",
            "text_color": "#333333",
            "text_light": "#666666",
            "border_color": "#e0e0e0",
            "scrollbar_bg": "#e0e0e0",
            "scrollbar_trough": "#f0f0f0"
        }
        
        # 暗色主题
        self.dark_theme = {
            "primary_color": "#5ba0e5",
            "secondary_color": "#50e3c2",
            "danger_color": "#e74c3c",
            "warning_color": "#f39c12",
            "success_color": "#2ecc71",
            "background_color": "#1e1e1e",
            "card_color": "#2d2d30",
            "text_color": "#cccccc",
            "text_light": "#999999",
            "border_color": "#444444",
            "scrollbar_bg": "#444444",
            "scrollbar_trough": "#333333"
        }
        
        # 当前主题颜色
        self.current_theme = self.light_theme.copy()
    
    def apply_theme(self):
        """应用当前主题的颜色方案"""
        # 获取当前主题的颜色
        colors = self.dark_theme if self.is_dark_mode else self.light_theme
        self.current_theme = colors.copy()
        
        # 应用窗口背景色
        self.root.configure(bg=colors["background_color"])
        
        # 配置全局样式
        # 标题栏样式
        self.style.configure("Title.TFrame", background=colors["card_color"], relief="flat")
        self.style.configure("Title.TLabel", background=colors["card_color"], foreground=colors["primary_color"], font=("Segoe UI", 18, "bold"))
        
        # 按钮样式
        self.style.configure("Close.TButton", background=colors["card_color"], foreground=colors["text_light"], borderwidth=0, font=("Segoe UI", 12))
        self.style.map("Close.TButton", background=[("active", colors["danger_color"]), ("hover", "#ff6b6b")], foreground=[("active", "white"), ("hover", "white")])
        
        self.style.configure("Add.TButton", background=colors["primary_color"], foreground="white", borderwidth=0, font=("Segoe UI", 11, "bold"), padding=10)
        self.style.map("Add.TButton", background=[("active", "#357abd"), ("hover", "#5aa0e5")])
        
        self.style.configure("Edit.TButton", background=colors["secondary_color"], foreground="white", borderwidth=0, font=("Segoe UI", 11), padding=8)
        self.style.map("Edit.TButton", background=[("active", "#3bc1a0"), ("hover", "#62e6c3")])
        
        self.style.configure("Delete.TButton", background=colors["danger_color"], foreground="white", borderwidth=0, font=("Segoe UI", 11), padding=8)
        self.style.map("Delete.TButton", background=[("active", "#c0392b"), ("hover", "#ea6153")])
        
        self.style.configure("ToggleStatus.TButton", background=colors["warning_color"], foreground="white", borderwidth=0, font=("Segoe UI", 11), padding=8)
        self.style.map("ToggleStatus.TButton", background=[("active", "#d35400"), ("hover", "#f5b041")])
        
        # 输入区域样式
        self.style.configure("Input.TLabelframe", background=colors["background_color"], foreground=colors["primary_color"], font=("Segoe UI", 12, "bold"), relief="flat")
        self.style.configure("Input.TLabelframe.Label", background=colors["background_color"], foreground=colors["primary_color"], font=("Segoe UI", 12, "bold"))
        
        # 列表区域样式
        self.style.configure("List.TLabelframe", background=colors["background_color"], foreground=colors["primary_color"], font=("Segoe UI", 12, "bold"), relief="flat")
        self.style.configure("List.TLabelframe.Label", background=colors["background_color"], foreground=colors["primary_color"], font=("Segoe UI", 12, "bold"))
        
        # 标签样式
        self.style.configure("Label.TLabel", background=colors["card_color"], foreground=colors["text_color"], font=("Segoe UI", 11))
        
        # 输入框样式
        self.style.configure("Entry.TEntry", background=colors["card_color"], foreground=colors["text_color"], font=("Segoe UI", 11), padding=8, relief="solid", bordercolor=colors["border_color"])
        self.style.map("Entry.TEntry", bordercolor=[("focus", colors["primary_color"]), ("hover", colors["border_color"])], relief=[("focus", "solid"), ("hover", "solid")])
        
        # 树状图样式
        self.style.configure("TaskTree.Treeview", background=colors["card_color"], foreground=colors["text_color"], font=("Segoe UI", 10), rowheight=25)
        self.style.configure("TaskTree.Treeview.Heading", background=colors["primary_color"], foreground="white", font=("Segoe UI", 11, "bold"), padding=10)
        self.style.map("TaskTree.Treeview.Heading", background=[("active", "#357abd")])
        self.style.configure("TaskTree.Treeview.Cell", background=colors["card_color"], foreground=colors["text_color"])
        
        # 滚动条样式
        self.style.configure("TScrollbar", background=colors["scrollbar_bg"], troughcolor=colors["scrollbar_trough"], bordercolor=colors["border_color"])
        self.style.map("TScrollbar", background=[("active", colors["primary_color"]), ("hover", colors["primary_color"])])
        
        # Pin按钮样式
        self.style.configure("Pin.TFrame", background=colors["background_color"])
        self.style.configure("Toggle.TCheckbutton", background=colors["card_color"], foreground=colors["text_color"], font=("Segoe UI", 12))
        
        # 操作区域样式
        self.style.configure("Action.TFrame", background=colors["background_color"])
        
        # 更新任务列表显示（重新应用标签样式）
        if hasattr(self, 'task_tree'):
            self.task_tree.tag_configure("completed", foreground=colors["text_light"])
            self.task_tree.tag_configure("pending", foreground=colors["text_color"])
            self.update_task_list()
    
    def setup_window_style(self):
        """设置窗口样式，包括圆角和阴影效果"""
        # 由于tkinter限制，我们使用背景色和布局来模拟圆角效果
        # 通过设置卡片式布局和边框颜色来增强视觉层次感
        
        # 设置窗口透明度（模拟阴影效果）
        # self.root.wm_attributes("-alpha", 0.95)
        
        # 我们将通过卡片式设计来实现现代化外观
        # 在create_widgets中已经实现了卡片式布局
    
    def create_widgets(self):
        # 固定/取消固定按钮和主题切换按钮
        pin_frame = ttk.Frame(self.root, style="Pin.TFrame")
        pin_frame.pack(fill=tk.X, padx=15, pady=5)
        
        # 主题切换按钮
        self.theme_var = tk.BooleanVar(value=self.is_dark_mode)
        theme_btn = ttk.Checkbutton(pin_frame, text="🌙 暗色模式", variable=self.theme_var, 
                                 command=self.toggle_theme, style="Toggle.TCheckbutton")
        theme_btn.pack(side=tk.RIGHT, padx=5)
        
        # 固定/取消固定按钮
        self.pin_var = tk.BooleanVar(value=True)
        pin_btn = ttk.Checkbutton(pin_frame, text="📌 固定窗口", variable=self.pin_var, 
                                 command=self.toggle_pin, style="Toggle.TCheckbutton")
        pin_btn.pack(side=tk.RIGHT, padx=5)
        
        # 任务输入区域
        input_frame = ttk.LabelFrame(self.root, text="添加新任务", style="Input.TLabelframe")
        input_frame.pack(fill=tk.X, padx=15, pady=5)
        
        # 任务描述输入
        ttk.Label(input_frame, text="任务:", style="Label.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.task_entry = ttk.Entry(input_frame, style="Entry.TEntry", font=("Segoe UI", 11))
        self.task_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # 截止日期输入
        ttk.Label(input_frame, text="截止日期:", style="Label.TLabel").pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        # 日期输入框和日历按钮
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.date_entry = ttk.Entry(date_frame, style="Entry.TEntry", font=("Segoe UI", 11))
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 日历按钮
        self.calendar_btn = ttk.Button(date_frame, text="📅", command=self.show_calendar, width=3)
        self.calendar_btn.pack(side=tk.RIGHT)
        
        # 添加任务按钮
        add_btn = ttk.Button(input_frame, text="添加任务", command=self.add_task, style="Add.TButton")
        add_btn.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # 任务列表区域
        list_frame = ttk.LabelFrame(self.root, text="任务列表", style="List.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # 任务列表
        columns = ("id", "task", "due_date", "status", "edit", "delete")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="TaskTree.Treeview")
        
        # 设置列宽
        self.task_tree.column("id", width=40, anchor=tk.CENTER)
        self.task_tree.column("task", width=200, anchor=tk.W)
        self.task_tree.column("due_date", width=100, anchor=tk.CENTER)
        self.task_tree.column("status", width=60, anchor=tk.CENTER)
        self.task_tree.column("edit", width=50, anchor=tk.CENTER)
        self.task_tree.column("delete", width=50, anchor=tk.CENTER)
        
        # 设置列标题
        self.task_tree.heading("id", text="#", anchor=tk.CENTER)
        self.task_tree.heading("task", text="任务", anchor=tk.W)
        self.task_tree.heading("due_date", text="截止日期", anchor=tk.CENTER)
        self.task_tree.heading("status", text="状态", anchor=tk.CENTER)
        self.task_tree.heading("edit", text="编辑", anchor=tk.CENTER)
        self.task_tree.heading("delete", text="删除", anchor=tk.CENTER)
        
        # 添加点击事件处理
        self.task_tree.bind("<Button-1>", self.on_tree_click)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscroll=scrollbar.set)
        
        # 布局
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # 任务操作按钮
        action_frame = ttk.Frame(self.root, style="Action.TFrame")
        action_frame.pack(fill=tk.X, padx=15, pady=15)
        
        edit_btn = ttk.Button(action_frame, text="编辑任务", command=self.edit_task, style="Edit.TButton")
        edit_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        delete_btn = ttk.Button(action_frame, text="删除任务", command=self.delete_task, style="Delete.TButton")
        delete_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        toggle_btn = ttk.Button(action_frame, text="切换状态", command=self.toggle_task_status, style="ToggleStatus.TButton")
        toggle_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 添加删除已完成任务按钮
        delete_completed_btn = ttk.Button(action_frame, text="删除已完成任务", command=self.delete_completed_tasks, style="Delete.TButton")
        delete_completed_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    def start_drag(self, event):
        # 只有在非调整大小模式下才记录拖动起始位置
        if not self.resize_mode:
            self.drag_x = event.x
            self.drag_y = event.y
    
    def drag_window(self, event):
        # 只有在非调整大小模式下才允许拖动窗口
        if not self.resize_mode:
            x = self.root.winfo_x() + (event.x - self.drag_x)
            y = self.root.winfo_y() + (event.y - self.drag_y)
            self.root.geometry(f"+{x}+{y}")
    
    def on_motion(self, event):
        """处理鼠标移动事件，改变光标样式"""
        if not self.resize_mode:
            cursor = self.get_cursor(event)
            self.root.config(cursor=cursor)
    
    def get_cursor(self, event):
        """根据鼠标位置返回相应的光标样式"""
        # 窗口边缘检测的阈值
        edge_threshold = 10
        
        # 获取窗口尺寸和位置
        x = event.x
        width = self.root.winfo_width()
        
        # 只检测左右边缘，不检测上下边缘
        on_left = x < edge_threshold
        on_right = x > width - edge_threshold
        
        # 根据边缘位置返回相应的光标
        if on_left or on_right:
            return "size_we"
        else:
            return "arrow"
    
    def start_resize(self, event):
        """处理调整大小的开始事件"""
        # 窗口边缘检测的阈值
        edge_threshold = 10
        
        # 获取窗口尺寸和位置
        x = event.x
        width = self.root.winfo_width()
        
        # 只检测左右边缘，不检测上下边缘
        on_left = x < edge_threshold
        on_right = x > width - edge_threshold
        
        # 确定调整大小的边缘
        if on_left or on_right:
            self.resize_mode = True
            self.resize_start_x = event.x_root
            self.resize_start_y = event.y_root
            self.resize_start_width = width
            self.resize_start_height = self.root.winfo_height()
            
            # 记录调整大小的边缘
            if on_left:
                self.resize_edge = "w"
            elif on_right:
                self.resize_edge = "e"
        else:
            # 如果不是点击窗口边缘，则不触发调整大小
            self.resize_mode = False
            self.resize_edge = None
    
    def resize_window(self, event):
        """处理调整大小的拖拽事件"""
        if self.resize_mode:
            # 计算鼠标移动的距离
            delta_x = event.x_root - self.resize_start_x
            
            # 获取当前窗口位置和尺寸
            win_x = self.root.winfo_x()
            screen_width = self.root.winfo_screenwidth()
            
            # 初始化新的窗口尺寸和位置
            new_width = self.resize_start_width
            new_height = self.resize_start_height
            new_x = win_x
            
            # 只处理左右调整
            if self.resize_edge == "w":
                # 计算新宽度和新位置
                new_width = max(300, self.resize_start_width - delta_x)
                new_x = win_x + delta_x
                
                # 确保窗口不会移出屏幕左侧
                new_x = max(0, new_x)
            elif self.resize_edge == "e":
                # 计算新宽度
                new_width = max(300, self.resize_start_width + delta_x)
                
                # 确保窗口不会移出屏幕右侧
                max_width = screen_width - win_x
                new_width = min(max_width, new_width)
            
            # 确保窗口始终可见
            new_width = max(300, new_width)
            
            # 设置新的窗口尺寸和位置，保持高度不变
            self.root.geometry(f"{new_width}x{new_height}+{new_x}+{self.root.winfo_y()}")
    
    def stop_resize(self, event):
        """处理调整大小的结束事件"""
        self.resize_mode = False
        self.resize_edge = None
        self.root.config(cursor="arrow")
    
    def toggle_theme(self):
        """切换亮色/暗色主题"""
        self.is_dark_mode = not self.is_dark_mode
        self.theme_var.set(self.is_dark_mode)
        self.apply_theme()
        self.save_theme_preference()
    
    def show_calendar(self):
        """显示日历选择器"""
        # 获取当前输入框中的日期
        current_date = self.date_entry.get().strip()
        
        # 创建日历选择器
        calendar = CalendarPicker(self.root, current_date, self.on_date_selected)
        
        # 确保日历选择器显示在正确的位置
        calendar.geometry(f"+{self.root.winfo_rootx() + 50}+{self.root.winfo_rooty() + 200}")
    
    def on_date_selected(self, date):
        """处理日期选择事件"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date)
    
    def toggle_pin(self):
        self.root.wm_attributes("-topmost", self.pin_var.get())
    
    def minimize_window(self):
        """最小化窗口"""
        self.root.iconify()
    
    def load_tasks(self):
        """加载任务数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except PermissionError:
                messagebox.showerror("加载失败", "无法加载任务数据：没有读取权限。请检查文件权限设置。")
                return []
            except json.JSONDecodeError:
                messagebox.showerror("加载失败", "无法加载任务数据：文件格式错误。数据可能已损坏。")
                return []
            except IOError as e:
                messagebox.showerror("加载失败", f"无法加载任务数据：{str(e)}")
                return []
            except Exception as e:
                messagebox.showerror("加载失败", f"加载任务数据时发生未知错误：{str(e)}")
                return []
        return []
    
    def save_tasks(self):
        """保存任务数据"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except PermissionError:
            messagebox.showerror("保存失败", "无法保存任务数据：没有写入权限。请检查文件权限设置。")
        except IOError as e:
            messagebox.showerror("保存失败", f"无法保存任务数据：{str(e)}")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存任务数据时发生未知错误：{str(e)}")
    
    def add_task(self):
        """添加新任务"""
        task = self.task_entry.get().strip()
        due_date = self.date_entry.get().strip()
        
        # 验证任务描述
        if not task:
            messagebox.showwarning("添加失败", "请输入任务描述！任务不能为空。")
            self.task_entry.focus()
            return
        
        # 验证日期格式
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("添加失败", "日期格式错误！请使用YYYY-MM-DD格式（例如：2023-12-31）。")
                self.date_entry.focus()
                return
        
        # 生成任务ID
        task_id = max([t["id"] for t in self.tasks], default=0) + 1
        
        # 创建新任务
        new_task = {
            "id": task_id,
            "task": task,
            "due_date": due_date,
            "completed": False
        }
        
        # 添加到任务列表
        self.tasks.append(new_task)
        self.save_tasks()
        self.update_task_list()
        
        # 清空输入框
        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        
        # 显示成功提示
        messagebox.showinfo("添加成功", f"任务 '{task}' 已成功添加！")
    
    def update_task_list(self):
        """更新任务列表显示"""
        # 清空现有列表
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # 获取当前主题颜色
        colors = self.dark_theme if self.is_dark_mode else self.light_theme
        
        # 定义标签样式
        self.task_tree.tag_configure("completed", foreground=colors["text_light"])
        self.task_tree.tag_configure("pending", foreground=colors["text_color"])
        
        # 添加任务到列表
        for task in self.tasks:
            status = "✓" if task["completed"] else "✗"
            
            # 根据完成状态设置标签
            tags = ("completed",) if task["completed"] else ("pending",)
            
            # 为完成的任务添加删除线效果（通过修改文本显示）
            task_text = task["task"]
            if task["completed"]:
                # 在tkinter Treeview中，我们使用特殊字符模拟删除线效果
                # 实际的删除线需要更复杂的实现，这里使用灰色文字表示已完成
                pass
            
            self.task_tree.insert("", tk.END, values=(
                task["id"],
                task_text,
                task["due_date"] if task["due_date"] else "无",
                status,
                "✏️",
                "🗑️"
            ), tags=tags)
    
    def on_tree_click(self, event):
        """处理任务列表点击事件"""
        # 获取点击的行和列
        region = self.task_tree.identify_region(event.x, event.y)
        if region == "cell":
            # 获取行和列
            row_id = self.task_tree.identify_row(event.y)
            column = self.task_tree.identify_column(event.x)
            
            # 获取任务ID
            if row_id:
                task_id = int(self.task_tree.item(row_id, "values")[0])
                
                # 处理点击事件
                if column == "#4":  # status column
                    # 切换任务状态
                    self.toggle_task_status_by_id(task_id)
                elif column == "#5":  # edit column
                    self.edit_task_by_id(task_id)
                elif column == "#6":  # delete column
                    self.delete_task_by_id(task_id)
    
    def edit_task(self, task=None):
        """编辑任务，支持回退修改"""
        # 如果没有传递任务对象，则从选中项获取
        if task is None:
            selected_item = self.task_tree.selection()
            if not selected_item:
                messagebox.showwarning("警告", "请先选择一个任务！")
                return
            
            # 获取选中任务的ID
            item = selected_item[0]
            task_id = int(self.task_tree.item(item, "values")[0])
            
            # 查找任务
            task = next((t for t in self.tasks if t["id"] == task_id), None)
            if not task:
                return
        
        # 保存任务的原始状态，以便回退
        original_task = task.copy()
        
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑任务")
        edit_window.geometry("400x250")  # 增大初始高度，确保能显示所有内容
        edit_window.resizable(True, True)  # 允许调整窗口大小
        edit_window.transient(self.root)
        
        # 窗口拖动相关变量
        edit_window.dragging = False
        edit_window.drag_x = 0
        edit_window.drag_y = 0
        
        # 添加窗口拖动功能
        def edit_start_drag(event):
            # 开始拖动
            edit_window.dragging = True
            edit_window.drag_x = event.x
            edit_window.drag_y = event.y
        
        def edit_drag_window(event):
            # 只有在拖动状态下才允许移动窗口
            if edit_window.dragging:
                x = edit_window.winfo_x() + (event.x - edit_window.drag_x)
                y = edit_window.winfo_y() + (event.y - edit_window.drag_y)
                edit_window.geometry(f"+{x}+{y}")
        
        def edit_stop_drag(event):
            # 结束拖动
            edit_window.dragging = False
        
        # 绑定拖动事件
        edit_window.bind("<Button-1>", edit_start_drag, add="+")
        edit_window.bind("<B1-Motion>", edit_drag_window, add="+")
        edit_window.bind("<ButtonRelease-1>", edit_stop_drag, add="+")
        
        # 设置窗口样式，根据当前主题设置背景色
        colors = self.dark_theme if self.is_dark_mode else self.light_theme
        edit_window.configure(bg=colors["background_color"])
        
        # 创建编辑表单
        form_frame = ttk.Frame(edit_window, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 任务描述
        ttk.Label(form_frame, text="任务描述:", style="Label.TLabel").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        task_entry = ttk.Entry(form_frame, width=40, style="Entry.TEntry", font=("Segoe UI", 11))
        task_entry.insert(0, task["task"])
        task_entry.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        
        # 截止日期
        ttk.Label(form_frame, text="截止日期 (YYYY-MM-DD):", style="Label.TLabel").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        date_entry = ttk.Entry(form_frame, width=40, style="Entry.TEntry", font=("Segoe UI", 11))
        date_entry.insert(0, task["due_date"])
        date_entry.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(0, 20))
        
        # 保存按钮
        def save_changes():
            new_task = task_entry.get().strip()
            new_date = date_entry.get().strip()
            
            # 验证任务描述
            if not new_task:
                messagebox.showwarning("编辑失败", "请输入任务描述！任务不能为空。")
                return
            
            # 验证日期格式
            if new_date:
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("编辑失败", "日期格式错误！请使用YYYY-MM-DD格式（例如：2023-12-31）。")
                    return
            
            # 更新任务
            task["task"] = new_task
            task["due_date"] = new_date
            
            self.save_tasks()
            self.update_task_list()
            
            edit_window.destroy()
            messagebox.showinfo("编辑成功", f"任务 '{new_task}' 已成功更新！")
        
        # 取消按钮
        def cancel_edit():
            # 回退到原始状态
            task.update(original_task)
            edit_window.destroy()
        
        # 按钮框架
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW)
        
        # 保存按钮
        save_btn = ttk.Button(button_frame, text="保存", command=save_changes, style="Add.TButton")
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=cancel_edit, style="Edit.TButton")
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # 配置网格列权重，使列能够随窗口大小调整
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        form_frame.rowconfigure(4, weight=1)  # 让按钮框架能够随窗口大小调整
        
        # 设置焦点
        task_entry.focus()
        
        # 绑定回车键保存
        edit_window.bind("<Return>", lambda event: save_changes())
        # 绑定ESC键取消
        edit_window.bind("<Escape>", lambda event: cancel_edit())
        
        # 使用wait_window确保模态行为，但允许主窗口拖动
        self.root.wait_window(edit_window)
    
    def delete_task(self):
        """删除选中的任务"""
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个任务！")
            return
        
        # 获取选中任务的ID
        item = selected_item[0]
        task_id = int(self.task_tree.item(item, "values")[0])
        
        # 确认删除
        if messagebox.askyesno("确认删除", "确定要删除这个任务吗？"):
            # 删除任务
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            self.save_tasks()
            self.update_task_list()
    
    def toggle_task_status(self):
        """切换任务完成状态"""
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个任务！")
            return
        
        # 获取选中任务的ID
        item = selected_item[0]
        task_id = int(self.task_tree.item(item, "values")[0])
        
        # 调用根据ID切换状态的方法
        self.toggle_task_status_by_id(task_id)
    
    def toggle_task_status_by_id(self, task_id):
        """根据ID切换任务完成状态"""
        # 查找任务
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if task:
            # 切换状态
            task["completed"] = not task["completed"]
            self.save_tasks()
            self.update_task_list()
    
    def delete_completed_tasks(self):
        """删除所有已完成的任务"""
        # 统计已完成的任务数量
        completed_tasks = [task for task in self.tasks if task["completed"]]
        if not completed_tasks:
            messagebox.showinfo("提示", "没有已完成的任务可以删除！")
            return
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除所有已完成的任务吗？共 {len(completed_tasks)} 个任务。"):
            # 删除已完成的任务
            self.tasks = [task for task in self.tasks if not task["completed"]]
            self.save_tasks()
            self.update_task_list()
            messagebox.showinfo("删除成功", f"已成功删除 {len(completed_tasks)} 个已完成的任务！")
    
    def delete_task_by_id(self, task_id):
        """根据ID删除任务"""
        # 查找任务
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除任务 '{task['task']}' 吗？"):
            # 删除任务
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            self.save_tasks()
            self.update_task_list()
            messagebox.showinfo("删除成功", f"任务 '{task['task']}' 已成功删除！")
    
    def edit_task_by_id(self, task_id):
        """根据ID编辑任务"""
        # 查找任务
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        
        # 调用编辑任务方法
        self.edit_task(task)



if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    
    # 创建应用
    app = TodoApp(root)
    
    # 运行主循环
    root.mainloop()