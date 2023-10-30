from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class Widget(QWidget):
    """Class holding the central widget of the application."""

    def __init__(
        self,
    ) -> None:
        QWidget.__init__(self)

        # QWidget Layout
        self.main_layout = QHBoxLayout()

        # Current case
        self.label = QLabel()
        self.label.setFont(QFont("Calibri", 24))
        self.label.setText("Select file to display the AHA data")

        self.main_layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setLayout(self.main_layout)
