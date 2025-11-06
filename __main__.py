"""
Main application entry point for OBP Yeah U Know Me
"""

import sys
from PyQt6 import QtWidgets
from main_window import MainWindow


def main():
    """Application entry point"""
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
