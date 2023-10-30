from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow

from aha_io import read_data
from aha_widget import central_widget, empty_widget


class MainWindow(QMainWindow):
    """Class holding the main window of the application."""

    def __init__(self) -> None:
        QMainWindow.__init__(self)
        self.setWindowTitle("Smooth AHA plot")
        self.plot_widget: central_widget.Widget

        widget = empty_widget.Widget()
        self.setCentralWidget(widget)

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Data file input
        data_file_action = QAction("Data file", self)
        data_file_action.setShortcut(QKeySequence.Open)
        data_file_action.triggered.connect(self.open_data_file)
        self.file_menu.addAction(data_file_action)

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

    def build_widget(self, filename: Path) -> None:
        data = read_data.read_data(filename)
        case_id = data.index[0]
        plot_type = filename.stem.split("_")[0]

        self.plot_widget = central_widget.Widget(
            data=data, case_id=case_id, plot_type=plot_type, parent=self
        )
        self.plot_widget.setParent(self)
        self.setCentralWidget(self.plot_widget)

    @Slot()
    def open_data_file(self) -> None:
        data_folder = Path().resolve() / "data"

        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", str(data_folder), "CSV Files (*.csv)"
        )
        self.build_widget(Path(filename))
