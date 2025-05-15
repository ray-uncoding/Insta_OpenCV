# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """啟動主 UI，連線由 UI 控制"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
