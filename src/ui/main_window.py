"""
主窗口 GUI
使用 PyQt6 构建应用界面
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QPushButton, QListWidget, QLabel, QListWidgetItem,
    QMessageBox, QTabWidget, QProgressBar, QMenu, QInputDialog,
    QDialog, QDateTimeEdit, QDialogButtonBox, QDateEdit, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QDate, QSettings
from PyQt6.QtGui import QFont, QAction
from datetime import datetime, timedelta
import asyncio
from qasync import asyncSlot

from src.database import DatabaseManager
from src.services import LLMService
from src.models import FragMind, TodoItem
from src.ui.styles import MAIN_WINDOW_STYLE, DIALOG_STYLE, ABOUT_DIALOG_STYLE


class SettingsDialog(QDialog):
    """设置对话框 - API 配置"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API 配置")
        self.setFixedSize(450, 220)
        
        # 统一白色背景风格
        self.setStyleSheet(DIALOG_STYLE)
        
        self.settings = QSettings("FragMind", "AppConfig")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        # 标题/说明
        label = QLabel("DeepSeek API Key")
        layout.addWidget(label)
        
        # 输入框
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password) # 隐藏输入内容
        self.api_key_input.setPlaceholderText("sk-...")
        
        # 加载已有设置
        current_key = self.settings.value("api_key", "")
        self.api_key_input.setText(current_key)
        layout.addWidget(self.api_key_input)
        
        layout.addStretch()
        
        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("background-color: #e0e0e0; color: #333333;")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
    def save_settings(self):
        key = self.api_key_input.text().strip()
        self.settings.setValue("api_key", key)
        self.accept()


class PromptSettingsDialog(QDialog):
    """设置对话框 - Prompt 配置"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义 Prompt")
        self.setFixedSize(500, 400)
        
        # 统一白色背景风格
        self.setStyleSheet(DIALOG_STYLE)
        
        self.settings = QSettings("FragMind", "AppConfig")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        # --- 自定义 Prompt ---
        label_prompt = QLabel("自定义日记总结提示词")
        label_prompt.setToolTip("在此输入您希望 AI 在生成日记总结时遵循的额外指令，例如：'使用幽默的语气' 或 '使用鲁迅的风格'。")
        layout.addWidget(label_prompt)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("例如：'使用幽默的语气' 或 '使用鲁迅的风格'。...")
        self.prompt_input.setText(self.settings.value("summary_prompt", ""))
        layout.addWidget(self.prompt_input)
        
        layout.addStretch()
        
        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("background-color: #e0e0e0; color: #333333;") # 取消按钮用灰色
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
    def save_settings(self):
        prompt = self.prompt_input.toPlainText().strip()
        self.settings.setValue("summary_prompt", prompt)
        self.accept()


class AboutDialog(QDialog):
    """关于对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedSize(400, 220)
        self.setStyleSheet(ABOUT_DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("FragMind")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #007AFF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 信息
        info = QLabel("碎片化思维整理与日记生成工具\nv0.1.0\nMail:Joyu.gbc@outlook.com")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        layout.addStretch()
        
        # 确认按钮
        btn = QPushButton("确定")
        btn.setFixedWidth(100)
        btn.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)


class DeselectableListWidget(QListWidget):
    """支持点击空白处取消选中的列表控件"""
    def mousePressEvent(self, event):
        # 获取点击位置的项
        item = self.itemAt(event.pos())
        if not item:
            # 如果点击了空白处，取消选中并清除焦点
            self.clearSelection()
            self.clearFocus()
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.llm_service = LLMService()
        
        # 初始化日期控制
        self.selected_date = QDate.currentDate()
        self.current_date = self.selected_date.toString("yyyy-MM-dd")
        
        self.init_ui()
        self.setup_menubar()
        self.load_today_data()

    def setup_menubar(self):
        """配置菜单栏"""
        menubar = self.menuBar()
        
        # --- 设置菜单 ---
        settings_menu = menubar.addMenu("设置")
        
        # API 配置动作
        api_action = QAction("API 配置...", self)
        api_action.setStatusTip("配置 LLM API 密钥")
        api_action.triggered.connect(self.open_settings_dialog)
        settings_menu.addAction(api_action)
        
        # Prompt 配置动作
        prompt_action = QAction("自定义提示词...", self)
        prompt_action.setStatusTip("配置日记总结的自定义 Prompt")
        prompt_action.triggered.connect(self.open_prompt_settings_dialog)
        settings_menu.addAction(prompt_action)
        
        # --- 帮助菜单 ---
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.open_about_dialog)
        help_menu.addAction(about_action)

    def open_about_dialog(self):
        """打开关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()

    def open_settings_dialog(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.statusbar.showMessage("API 设置已保存", 3000)
            # 重新初始化 LLM Service 以应用新 Key
            self.llm_service = LLMService()

    def open_prompt_settings_dialog(self):
        """打开 Prompt 设置对话框"""
        dialog = PromptSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.statusbar.showMessage("Prompt 设置已保存", 3000)
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("FragMind - 碎片化思维整理与日记生成")
        self.setGeometry(100, 100, 1400, 800)
        
        # 【新增】初始化状态栏变量
        self.statusbar = self.statusBar()
        
        # 设置样式表
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：日记片段输入和列表
        left_panel = self._create_diary_panel()
        
        # 中间：日记总结展示
        middle_panel = self._create_summary_panel()
        
        # 右侧：Todo 列表
        right_panel = self._create_todo_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(middle_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600, 400])
        
        main_layout.addWidget(splitter)
    
    def _create_diary_panel(self):
        """创建日记片段面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- 日期导航栏 ---
        date_nav_layout = QHBoxLayout()
        
        # 标题
        title = QLabel("碎片记录")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        date_nav_layout.addWidget(title)
        
        date_nav_layout.addStretch() # 弹簧
        
        # 前一天按钮
        btn_prev = QPushButton("<")
        btn_prev.setFixedSize(30, 30)
        btn_prev.setToolTip("前一天")
        btn_prev.setStyleSheet("padding: 0px;")
        btn_prev.clicked.connect(lambda: self.change_date(-1))
        
        # 日期选择器
        self.date_edit = QDateEdit()
        self.date_edit.setDate(self.selected_date)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True) 
        self.date_edit.setFixedWidth(120) 
        self.date_edit.setFixedHeight(30)
        self.date_edit.dateChanged.connect(self.on_date_changed)
        
        # 后一天按钮
        btn_next = QPushButton(">")
        btn_next.setFixedSize(30, 30)
        btn_next.setToolTip("后一天")
        btn_next.setStyleSheet("padding: 0px;")
        btn_next.clicked.connect(lambda: self.change_date(1))
        
        # 回到今天按钮
        btn_today = QPushButton("今天")
        btn_today.setFixedSize(50, 30)
        btn_today.setStyleSheet("padding: 0px;")
        btn_today.clicked.connect(self.go_to_today)
        
        date_nav_layout.addWidget(btn_prev)
        date_nav_layout.addWidget(self.date_edit)
        date_nav_layout.addWidget(btn_next)
        date_nav_layout.addWidget(btn_today)
        
        layout.addLayout(date_nav_layout)
        
        # 输入区
        self.quick_input = QTextEdit()
        self.quick_input.setPlaceholderText("想到什么就记下来...")
        self.quick_input.setMinimumHeight(400) 
        layout.addWidget(self.quick_input)
        
        # 保存按钮区域
        btn_layout = QHBoxLayout()
        
        # 按钮 1: 仅保存
        self.btn_save_only = QPushButton("记录")
        self.btn_save_only.setToolTip("仅保存内容，不分析待办事项")
        self.btn_save_only.setFixedHeight(36)
        self.btn_save_only.clicked.connect(lambda: self.save_diary_entry(extract_todo=False))
        
        # 按钮 2: 保存并提取
        self.btn_save_extract = QPushButton("提取待办")
        self.btn_save_extract.setToolTip("不保存内容，尝试从中提取待办事项")
        self.btn_save_extract.setFixedHeight(36)
        self.btn_save_extract.clicked.connect(self.extract_todo_only)
        
        btn_layout.addWidget(self.btn_save_only)
        btn_layout.addWidget(self.btn_save_extract)
        layout.addLayout(btn_layout)
        
        # 今日片段列表
        self.list_label = QLabel(f"片段列表 ({self.current_date})")
        self.list_label.setStyleSheet("margin-top: 10px; font-weight: bold; color: #666;")
        layout.addWidget(self.list_label)
        
        self.entry_list = DeselectableListWidget()
        self.entry_list.setAlternatingRowColors(True)
        self.entry_list.setWordWrap(True)  # 开启自动换行
        self.entry_list.itemDoubleClicked.connect(self.on_entry_double_clicked)
        self.entry_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.entry_list.customContextMenuRequested.connect(self.show_entry_context_menu)
        layout.addWidget(self.entry_list)
        
        # 生成总结按钮
        self.btn_generate_summary = QPushButton("生成今日总结")
        self.btn_generate_summary.setFixedHeight(36)
        self.btn_generate_summary.clicked.connect(self.generate_summary)
        layout.addWidget(self.btn_generate_summary)
        
        return panel
    
    def _create_summary_panel(self):
        """创建日记总结面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title = QLabel("今日日记")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # 总结显示区
        self.summary_display = QTextEdit()
        self.summary_display.setPlaceholderText("在左侧记录碎片化想法，然后点击'生成今日总结'按钮\nAI 会帮你整理成一篇完整的日记")
        self.summary_display.setStyleSheet("font-size: 16px; line-height: 1.6;")
        layout.addWidget(self.summary_display)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.btn_save_summary = QPushButton("保存修改")
        self.btn_save_summary.setFixedHeight(36)
        self.btn_save_summary.clicked.connect(self.save_summary)
        btn_layout.addWidget(self.btn_save_summary)
        layout.addLayout(btn_layout)
        
        return panel
    
    def _create_todo_panel(self):
        """创建 Todo 面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title = QLabel("待办事项")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tab Widget
        self.todo_tabs = QTabWidget()
        
        # 待办列表
        self.todo_list_pending = DeselectableListWidget()
        self.todo_list_pending.setSpacing(5)
        self.todo_list_pending.itemChanged.connect(self.on_todo_item_changed)
        self.todo_list_pending.itemDoubleClicked.connect(self.on_todo_double_clicked)
        self.todo_list_pending.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.todo_list_pending.customContextMenuRequested.connect(lambda pos: self.show_todo_context_menu_from_list(self.todo_list_pending, pos))
        self.todo_tabs.addTab(self.todo_list_pending, "待办")
        
        # 已完成列表
        self.todo_list_completed = DeselectableListWidget()
        self.todo_list_completed.setSpacing(5)
        self.todo_list_completed.itemChanged.connect(self.on_todo_item_changed)
        self.todo_list_completed.itemDoubleClicked.connect(self.on_todo_double_clicked)
        self.todo_list_completed.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.todo_list_completed.customContextMenuRequested.connect(lambda pos: self.show_todo_context_menu_from_list(self.todo_list_completed, pos))
        self.todo_tabs.addTab(self.todo_list_completed, "已完成")
        
        layout.addWidget(self.todo_tabs)
        
        return panel
    
    # ==================== 日期控制 ====================
    
    def change_date(self, days):
        """切换日期"""
        new_date = self.date_edit.date().addDays(days)
        self.date_edit.setDate(new_date)
        
    def go_to_today(self):
        """回到今天"""
        self.date_edit.setDate(QDate.currentDate())
        
    def on_date_changed(self, date):
        """日期改变时的处理"""
        self.selected_date = date
        self.current_date = date.toString("yyyy-MM-dd")
        
        # 更新 UI 状态
        if hasattr(self, 'list_label'):
            self.list_label.setText(f"片段列表 ({self.current_date})")
        
        # 刷新数据
        self.load_diary_entries()
        self.load_summary()

    # ==================== 数据加载 ====================
    
    def load_today_data(self):
        """加载初始数据"""
        self.load_diary_entries()
        self.load_summary()
        self.load_todos()
    
    def load_diary_entries(self):
        """加载当前日期日记片段"""
        self.entry_list.clear()
        entries = self.db.get_frag_minds_by_date(self.current_date)
        
        for entry in entries:
            time_str = entry.created_at.strftime("%H:%M")
            item = QListWidgetItem(f"[{time_str}] {entry.content}")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.entry_list.addItem(item)
    
    def load_summary(self):
        """加载当前日期总结"""
        summary = self.db.get_diary_summary(self.current_date)
        if summary:
            self.summary_display.setText(summary.summary)
        else:
            self.summary_display.clear()
    
    def load_todos(self):
        """加载并显示待办事项"""
        self.is_loading_todos = True
        
        self.todo_list_pending.clear()
        self.todo_list_completed.clear()
        
        todos = self.db.get_all_todos()
        
        pending_todos = []
        completed_todos = []
        
        for todo in todos:
            if todo.completed:
                completed_todos.append(todo)
            else:
                pending_todos.append(todo)
        
        # 1. 按日期归类
        dated_todos = {}  
        no_date_todos = []

        for todo in pending_todos:
            if not todo.due_date:
                no_date_todos.append(todo)
            else:
                # 确保移除时区信息
                d_dt = todo.due_date
                if d_dt.tzinfo is not None:
                    d_dt = d_dt.replace(tzinfo=None)
                
                d_date = d_dt.date()
                if d_date not in dated_todos:
                    dated_todos[d_date] = []
                dated_todos[d_date].append(todo)
        
        # 2. 对日期排序
        sorted_dates = sorted(dated_todos.keys())
        
        # 3. 渲染日期分组
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        for d in sorted_dates:
            todos_in_day = dated_todos[d]
            # 按时间排序 (默认 00:00)
            todos_in_day.sort(key=lambda t: (t.due_date.hour, t.due_date.minute) if t.due_date else (0, 0))
            
            # 添加日期标题
            date_str = f"{d.strftime('%Y-%m-%d')} {weekdays[d.weekday()]}"
            header = QListWidgetItem(f"📅 {date_str}")
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            font = header.font()
            font.setBold(True)
            header.setFont(font)
            header.setBackground(Qt.GlobalColor.lightGray)
            header.setForeground(Qt.GlobalColor.black)
            self.todo_list_pending.addItem(header)
            
            # 添加该日期的事项
            for todo in todos_in_day:
                # 如果有具体时间（非00:00），显示时间
                show_time = False
                if todo.due_date and (todo.due_date.hour != 0 or todo.due_date.minute != 0):
                    show_time = True
                self._add_todo_item(self.todo_list_pending, todo, show_time=show_time)

        # 4. 渲染待定分组
        if no_date_todos:
            header = QListWidgetItem("📅 待定")
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            font = header.font()
            font.setBold(True)
            header.setFont(font)
            header.setBackground(Qt.GlobalColor.lightGray)
            header.setForeground(Qt.GlobalColor.black)
            self.todo_list_pending.addItem(header)
            
            for todo in no_date_todos:
                self._add_todo_item(self.todo_list_pending, todo)
                
        # --- 处理已完成事项 ---
        # 简单按截止时间倒序
        completed_todos.sort(key=lambda t: t.due_date.replace(tzinfo=None) if t.due_date else datetime.max, reverse=True)
        
        for todo in completed_todos:
            self._add_todo_item(self.todo_list_completed, todo)
            
        self.is_loading_todos = False

    def _add_todo_item(self, list_widget, todo, show_time=False):
        """添加单个 Todo 项到列表"""
        display_text = todo.title
        if show_time and todo.due_date:
             display_text = f"[{todo.due_date.strftime('%H:%M')}] {todo.title}"
             
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, todo)
        
        # 设置复选框状态
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked if todo.completed else Qt.CheckState.Unchecked)
        
        # 样式：已完成添加删除线
        if todo.completed:
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
            item.setForeground(Qt.GlobalColor.gray)
        
        # 提示信息
        if todo.due_date:
            item.setToolTip(f"截止: {todo.due_date.strftime('%Y-%m-%d %H:%M')}")
        
        list_widget.addItem(item)

    def on_todo_item_changed(self, item):
        """Todo 列表项状态改变（复选框点击）"""
        if getattr(self, 'is_loading_todos', False):
            return
            
        todo = item.data(Qt.ItemDataRole.UserRole)
        if not todo:
            return
            
        current_checked = (item.checkState() == Qt.CheckState.Checked)
        
        if not hasattr(self, '_todo_timers'):
            self._todo_timers = {}
            
        if current_checked and not todo.completed:
            # 标记为完成：启动 10 秒定时器
            if todo.id in self._todo_timers:
                self._todo_timers[todo.id].stop()
                
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._finalize_todo_completion(todo.id, True))
            timer.start(10000)
            self._todo_timers[todo.id] = timer
            
        elif not current_checked and todo.completed:
            # 已完成列表里的项目被取消勾选：禁止直接还原
            # 强制改回 Checked
            self.is_loading_todos = True # 防止递归
            item.setCheckState(Qt.CheckState.Checked)
            self.is_loading_todos = False
            
        elif not current_checked and not todo.completed:
            # 待办列表里的项目，被勾选后（进入等待期），又被取消勾选
            if todo.id in self._todo_timers:
                self._todo_timers[todo.id].stop()
                del self._todo_timers[todo.id]

    def on_todo_double_clicked(self, item):
        """双击 Todo 项"""
        todo = item.data(Qt.ItemDataRole.UserRole)
        if todo:
            self.edit_todo_item(todo)

    def show_todo_context_menu_from_list(self, list_widget, pos):
        """从列表显示 Todo 右键菜单"""
        item = list_widget.itemAt(pos)
        if not item:
            return
        todo = item.data(Qt.ItemDataRole.UserRole)
        if todo:
            self.show_todo_context_menu(todo, list_widget.mapToGlobal(pos))
    
    # ==================== 事件处理 ====================
    
    @asyncSlot()
    async def save_diary_entry(self, extract_todo=False):
        """
        保存日记片段
        :param extract_todo: 是否执行待办事项提取
        """
        content = self.quick_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "提示", "请输入内容")
            return
        
        entry = FragMind(
            content=content,
            date=self.current_date
        )
        
        entry_id = self.db.add_frag_mind(entry)
        self.quick_input.clear()
        self.load_diary_entries()
        
        # 根据用户选择决定是否触发 Todo 提取
        if extract_todo:
            # 显示一个临时的状态提示
            self.statusbar.showMessage("正在分析待办事项...", 3000)
            asyncio.create_task(self.process_todo_extraction(content))
        else:
            self.statusbar.showMessage("片段已保存", 2000)
    
    @asyncSlot()
    async def extract_todo_only(self):
        """仅提取待办，不保存日记"""
        content = self.quick_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "提示", "请输入内容")
            return
            
        self.statusbar.showMessage("正在分析待办事项...", 3000)
        self.quick_input.clear()
        await self.process_todo_extraction(content)

    @asyncSlot()
    async def generate_summary(self):
        """手动触发日记总结"""
        await self.process_summary_generation()

    async def process_todo_extraction(self, text_to_analyze: str):
        """
        执行 Todo 提取
        :param text_to_analyze: 待分析的文本
        """
        # 显示进度条和状态栏
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        self.statusbar.showMessage("正在分析待办事项...", 0)
        
        try:
            # 准备上下文
            active_todos = self.db.get_active_todos()
            existing_todo_titles = [t.title for t in active_todos]
            
            loop = asyncio.get_running_loop()
            
            # 执行提取
            new_todos = await loop.run_in_executor(
                None, 
                self.llm_service.parse_todo_from_text, 
                text_to_analyze, 
                existing_todo_titles
            )
            
            if new_todos:
                for todo in new_todos:
                    self.db.add_todo_item(todo)
                self.load_todos()
                self.statusbar.showMessage(f"成功提取 {len(new_todos)} 条待办事项", 3000)
            else:
                self.statusbar.showMessage("未发现新的待办事项", 3000)
                
        except Exception as e:
            print(f"Todo extraction failed: {e}")
            self.statusbar.showMessage("待办事项提取失败", 3000)
        finally:
            self.progress_bar.hide()

    async def process_summary_generation(self):
        """
        执行日记总结生成
        """
        # UI 状态更新
        self.btn_generate_summary.setEnabled(False)
        self.btn_generate_summary.setText("正在生成...")
        self.statusbar.showMessage("正在生成今日总结，请稍候...", 0) # 0 表示一直显示直到被覆盖
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        
        try:
            # 准备上下文
            entries = self.db.get_frag_minds_by_date(self.current_date)
            if not entries:
                QMessageBox.warning(self, "提示", "今天还没有任何记录")
                self.statusbar.clearMessage()
                return

            current_summary_obj = self.db.get_diary_summary(self.current_date)
            current_summary_text = current_summary_obj.summary if current_summary_obj else ""
            
            loop = asyncio.get_running_loop()
            
            # 执行生成
            new_summary = await loop.run_in_executor(
                None,
                self.llm_service.summarize_diary_entries,
                entries,
                self.current_date,
                current_summary_text
            )
            
            if new_summary:
                self.summary_display.setText(new_summary)
                # 自动保存一次
                self.save_summary(silent=True)
                self.statusbar.showMessage("今日总结生成完毕", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成总结失败：{str(e)}")
            self.statusbar.showMessage("生成总结失败", 3000)
        finally:
            self.btn_generate_summary.setEnabled(True)
            self.btn_generate_summary.setText("✨ 生成今日总结")
            self.progress_bar.hide()
    
    def save_summary(self, silent=False):
        """保存总结到数据库"""
        summary_text = self.summary_display.toPlainText().strip()
        if not summary_text:
            if not silent:
                QMessageBox.warning(self, "提示", "没有内容可保存")
            return
        
        from src.models import DiarySummary
        entries = self.db.get_frag_minds_by_date(self.current_date)
        
        summary = DiarySummary(
            date=self.current_date,
            summary=summary_text,
            entry_count=len(entries)
        )
        
        self.db.save_diary_summary(summary)
        if not silent:
            QMessageBox.information(self, "成功", "总结已保存")
    
    def on_entry_double_clicked(self, item):
        """双击日记片段进行编辑"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        
        text, ok = QInputDialog.getMultiLineText(
            self, 
            "编辑片段", 
            f"时间: {entry.created_at.strftime('%H:%M')}", 
            text=entry.content
        )
        
        if ok and text.strip():
            # 更新数据库
            self.db.update_frag_mind_content(entry.id, text.strip())
            self.load_diary_entries()

    def show_entry_context_menu(self, position):
        """显示日记片段右键菜单"""
        item = self.entry_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        # 提取为待办
        extract_action = QAction("⚡ 提取为待办", self)
        extract_action.triggered.connect(lambda: self.extract_todo_from_entry(item))
        menu.addAction(extract_action)
        
        menu.addSeparator()
        
        # 删除片段
        delete_action = QAction("🗑️ 删除", self)
        delete_action.triggered.connect(lambda: self.delete_current_entry(item))
        menu.addAction(delete_action)
        
        menu.exec(self.entry_list.mapToGlobal(position))

    def extract_todo_from_entry(self, item):
        """从日记片段提取待办"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        self.statusbar.showMessage("正在分析待办事项...", 3000)
        asyncio.create_task(self.process_todo_extraction(entry.content))

    def delete_current_entry(self, item):
        """删除当前选中的日记片段"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            "确定要删除这个日记片段吗？\n此操作无法撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_frag_mind(entry.id)
            # 从列表中移除
            row = self.entry_list.row(item)
            self.entry_list.takeItem(row)
    
    def _finalize_todo_completion(self, todo_id, completed):
        """延迟执行完成操作"""
        self.db.update_todo_status(todo_id, completed)
        self.load_todos()

    def edit_todo_item(self, todo: TodoItem):
        """编辑 Todo 内容"""
        text, ok = QInputDialog.getText(self, "编辑待办", "内容:", text=todo.title)
        if ok and text:
            self.db.update_todo_info(todo.id, title=text)
            self.load_todos()

    def show_todo_context_menu(self, todo: TodoItem, pos):
        """显示 Todo 右键菜单"""
        menu = QMenu()
        
        if todo.completed:
            # 已完成：显示还原
            action_restore = QAction("↩️ 还原未完成", self)
            action_restore.triggered.connect(lambda: self.restore_todo(todo))
            menu.addAction(action_restore)
        else:
            # 未完成：显示设置截止时间
            action_set_date = QAction("📅 设置截止时间", self)
            action_set_date.triggered.connect(lambda: self.set_todo_date(todo))
            menu.addAction(action_set_date)
        
        menu.addSeparator()
        
        action_delete = QAction("🗑️ 删除", self)
        action_delete.triggered.connect(lambda: self.delete_todo(todo))
        menu.addAction(action_delete)
        
        menu.exec(pos)

    def restore_todo(self, todo: TodoItem):
        """还原待办事项"""
        self.db.update_todo_status(todo.id, False)
        self.load_todos()

    def set_todo_date(self, todo: TodoItem):
        """设置截止时间"""
        dialog = QDialog(self)
        dialog.setWindowTitle("设置截止时间")
        layout = QVBoxLayout(dialog)
        
        dt_edit = QDateTimeEdit(datetime.now())
        if todo.due_date:
            dt_edit.setDateTime(todo.due_date)
        dt_edit.setCalendarPopup(True)
        layout.addWidget(dt_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_date = dt_edit.dateTime().toPyDateTime()
            self.db.update_todo_info(todo.id, due_date=new_date)
            self.load_todos()

    def delete_todo(self, todo: TodoItem):
        """删除 Todo"""
        confirm = QMessageBox.question(self, "确认", f"确定要删除 '{todo.title}' 吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.delete_todo_item(todo.id)
            self.load_todos()
