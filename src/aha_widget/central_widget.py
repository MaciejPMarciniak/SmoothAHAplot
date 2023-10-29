import pandas as pd
from loguru import logger
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QSizePolicy, QTableView, QWidget

from aha import aha
from aha.utils import data_mapping
from aha_widget.table_model import CustomTableModel


class Widget(QWidget):
    """Class holding the central widget of the application."""

    def __init__(self, data: pd.DataFrame) -> None:
        QWidget.__init__(self)

        # Getting the Model
        self.model = CustomTableModel(data)

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # QTableView Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)
        self.table_view.verticalHeader().hide()

        # AHA Plot
        self.aha_plot = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.aha_plot)
        logger.debug(data_mapping.case_to_dict(data, "Cid1"))
        strain_plot = aha.AHA(data_mapping.case_to_dict(data, "Cid1"), "Strain")
        fig = strain_plot.bullseye_smooth(True)
        static_canvas = FigureCanvas(fig)
        self.layout.addWidget(static_canvas)
        self.layout.addWidget(NavigationToolbar(static_canvas, self))

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        ## Right Layout
        size.setHorizontalStretch(4)
        self.aha_plot.setSizePolicy(size)
        self.main_layout.addWidget(self.aha_plot)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)
