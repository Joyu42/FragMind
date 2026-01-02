"""
FragMind - 基于 AI Agent 的碎片化思维整理与日记生成系统
主入口文件
"""
import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication, QMessageBox

from src.ui import MainWindow


def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常捕获，防止程序直接闪退"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = f"发生未捕获的错误:\n{exc_value}"
    # 打印到控制台以便调试
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    # 弹窗提示用户
    if QApplication.instance():
        QMessageBox.critical(None, "程序错误", error_msg)


def main():
    """应用主函数"""
    # 设置全局异常捕获
    sys.excepthook = handle_exception
    
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("FragMind")
    app.setOrganizationName("FragMind")
    
    # 创建 qasync 循环，将 asyncio 桥接到 PyQt
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 使用 loop.run_forever() 代替 app.exec()
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
