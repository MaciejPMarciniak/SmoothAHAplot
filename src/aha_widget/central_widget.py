import pandas as pd
from PySide6.QtCharts import QChart, QChartView
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QSizePolicy, QTableView, QWidget

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

        # Creating QChart
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)

        # Creating QChartView
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        ## Right Layout
        size.setHorizontalStretch(4)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)
