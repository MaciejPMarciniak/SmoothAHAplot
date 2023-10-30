import sys

from PySide6.QtWidgets import QApplication

from aha_widget import main_window


def main() -> int:
    app = QApplication(sys.argv)
    window = main_window.MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
