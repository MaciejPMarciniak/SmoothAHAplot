from pathlib import Path
from typing import Callable

import pandas as pd
from loguru import logger
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from aha import aha
from aha.utils import data_mapping
from aha_widget import table_model


class Widget(QWidget):
    """Class holding the central widget of the application."""

    def __init__(
        self,
        data: pd.DataFrame,
        case_id: str | pd.Index,
        plot_type: str = "Strain",
    ) -> None:
        QWidget.__init__(self)
        self._data = data
        self.case_id = case_id
        self.plot_type = plot_type

        logger.debug(self.parent())

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        self.size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Other layouts
        self.left_layout = QVBoxLayout()
        self.table_view = QTableView()
        self.button_grid = QGridLayout()

        # Table model
        self.table_model = table_model.CustomTableModel(data, case_id=self.case_id)
        self.table_view.setModel(self.table_model)

        # Table headers and settings
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)
        self.table_view.verticalHeader().hide()

        # Current case
        self.case_label = QLabel()
        self.case_label.setFont(QFont("Calibri", 16))
        self.case_label.setText(f"Case:\n'{self.case_id}'")

        # AHA Plot
        self.aha_plot = QWidget()
        self.layout = QVBoxLayout(self.aha_plot)
        self.aha_plot_canvas = FigureCanvas(self.get_plot())
        self.layout.addWidget(self.aha_plot_canvas)
        self.layout.addWidget(NavigationToolbar(self.aha_plot_canvas, self))

        # Next button
        self.next_button = QPushButton(">", self)
        self.next_button.clicked.connect(lambda: self.update_case_id(self._next))

        # Previous button
        self.previous_button = QPushButton("<", self)
        self.previous_button.clicked.connect(lambda: self.update_case_id(self._previous))

        # Save button
        self.save_button = QPushButton("Save all", self)
        self.save_button.clicked.connect(self.save_all_plots)

        # Quit button
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(QApplication.instance().quit)

        # Table and buttons layout
        self.size.setVerticalStretch(1)
        self.case_label.setSizePolicy(self.size)
        self.left_layout.addWidget(self.case_label)
        self.size.setVerticalStretch(4)
        self.size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(self.size)
        self.left_layout.addWidget(self.table_view)

        # Button layout
        self.button_grid.addWidget(self.previous_button, 0, 0)
        self.button_grid.addWidget(self.next_button, 0, 1)
        self.button_grid.addWidget(self.save_button, 1, 0)
        self.button_grid.addWidget(self.quit_button, 1, 1)

        self.left_layout.addLayout(self.button_grid)

        self.main_layout.addLayout(self.left_layout)

        # Plot
        self.size.setHorizontalStretch(4)
        self.aha_plot.setSizePolicy(self.size)
        self.main_layout.addWidget(self.aha_plot)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)

    def update_view(self) -> None:
        """Updates the table, case label and the plot."""
        # Update table
        self.table_model = table_model.CustomTableModel(self._data, case_id=self.case_id)
        self.table_view.setModel(self.table_model)

        # Re-generate the plot with new data
        # Remove the old canvas and toolbar from the layout
        self._remove_old_canvas()

        # Add the new canvas and toolbar to the layout
        new_canvas = FigureCanvas(self.get_plot())
        self.layout.addWidget(new_canvas)
        self.layout.addWidget(NavigationToolbar(new_canvas, self))

        # Update the aha_plot_canvas attribute to point to the new canvas
        self.aha_plot_canvas = new_canvas

    def _remove_old_canvas(self) -> None:
        for i in reversed(range(self.layout.count())):
            layout_item = self.layout.takeAt(i)
            if layout_item:
                widget = layout_item.widget()
                if widget:
                    widget.deleteLater()

    def get_plot(self) -> plt.Figure:
        case_data = data_mapping.case_to_dict(self._data, self.case_id)
        logger.debug(f"\nReading data: \nCase ID: {self.case_id} \n{case_data}")
        plot = aha.AHA(case_data, plot_type=self.plot_type)

        return plot.bullseye_smooth(True)

    @staticmethod
    def _next(case_index: int, n_cases: int) -> int:
        return case_index + 1 if case_index != n_cases - 1 else 0

    @staticmethod
    def _previous(case_index: int, n_cases: int) -> int:
        return case_index - 1 if case_index != 0 else n_cases - 1

    def update_case_label(self) -> None:
        self.case_label.setText(f"Case:\n'{self.case_id}'")
        logger.debug(f"{self.case_id=}")

    @Slot(object)
    def update_case_id(self, direction: Callable) -> None:
        current_case_index = self._data.index.get_loc(self.case_id)
        new_index = direction(case_index=current_case_index, n_cases=len(self._data))
        self.case_id = self._data.index[new_index]

        self.update_case_label()
        self.update_view()

    @Slot()
    def save_all_plots(self) -> None:
        for case in self._data.index:
            path = Path().resolve() / "data" / "export"
            logger.info(f"Saving images to {path}")
            case_data = data_mapping.case_to_dict(self._data, case)
            plot = aha.AHA(case_data, plot_type=self.plot_type)
            plot.bullseye_smooth(True)
            plt.savefig(path / f"{case}_{self.plot_type}.png")
