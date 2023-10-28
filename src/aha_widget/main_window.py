from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow

from aha_widget import central_widget


class MainWindow(QMainWindow):
    """Class holding the main window of the application."""

    def __init__(self, widget: central_widget.Widget) -> None:
        QMainWindow.__init__(self)
        self.setWindowTitle("Smooth AHA plot")
        self.setCentralWidget(widget)

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")

        # Window dimensions
        geometry = self.screen().availableGeometry()
        self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)
