# main.py
import sys
from PyQt5.QtWidgets import QApplication
from src.insta360cam.api import launch_ui

def main():
    """啟動主 UI，連線由 API 控制"""
    launch_ui()

if __name__ == "__main__":
    main()
