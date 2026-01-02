"""
UI 样式表定义
"""

MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #f5f5f7;
    }
    QWidget {
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        font-size: 14px;
    }
    QPushButton {
        background-color: #007AFF;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0062CC;
    }
    QPushButton:pressed {
        background-color: #004999;
    }
    QPushButton:disabled {
        background-color: #B0B0B0;
    }
    QTextEdit, QListWidget {
        background-color: white;
        color: #333333;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 8px;
        outline: none;
    }
    QDateEdit {
        background-color: white;
        color: #333333;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
    }
    QListWidget::item:selected {
        background-color: #e6e6e6;
        color: #333333;
        border-radius: 4px;
    }
    QListWidget::item:selected:!active {
        background-color: transparent;
        color: #333333;
    }
    QListWidget::item:hover {
        background-color: #f5f5f5;
        border-radius: 4px;
    }
    QCheckBox {
        color: #333333;
        spacing: 5px;
    }
    QLabel {
        color: #333333;
    }
    QSplitter::handle {
        background-color: #d0d0d0;
        width: 2px;
    }
    QMessageBox {
        background-color: #f5f5f7;
    }
    QMessageBox QLabel {
        color: #333333;
    }
    QTabWidget::pane {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background: white;
    }
    QTabBar::tab {
        background: #f0f0f0;
        color: #333333;
        padding: 8px 12px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background: white;
        border-bottom: 2px solid #007AFF;
        font-weight: bold;
    }
"""

DIALOG_STYLE = """
    QDialog {
        background-color: #f5f5f7;
    }
    QLabel {
        color: #333333;
        font-size: 14px;
        font-weight: bold;
    }
    QLineEdit {
        background-color: white;
        color: #333333;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }
    QPushButton {
        background-color: #007AFF;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: bold;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #0062CC;
    }
    QPushButton:pressed {
        background-color: #004999;
    }
"""

ABOUT_DIALOG_STYLE = """
    QDialog {
        background-color: #f5f5f7;
    }
    QLabel {
        color: #333333;
        font-size: 14px;
    }
    QPushButton {
        background-color: #007AFF;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0062CC;
    }
"""
