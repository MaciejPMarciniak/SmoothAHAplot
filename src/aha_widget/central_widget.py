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
    QMainWindow,
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
        plot_type: str,
        parent: None | QMainWindow,
    ) -> None:
        QWidget.__init__(self, parent=parent)
        self.parent().statusBar().showMessage("Loading AHA data")
        self._data = data
        self.case_id = case_id
        self.plot_type = plot_type

        self.table_model: table_model.CustomTableModel

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        self.size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Other layouts
        self.left_layout = QVBoxLayout()
        self.table_view = QTableView()
        self.button_grid = QGridLayout()

        self._create_buttons()
        self._create_table()
        self._create_current_case_label()

        # AHA Plot
        self.aha_plot = QWidget()
        self.layout = QVBoxLayout(self.aha_plot)
        self.aha_plot_canvas = FigureCanvas(self.get_plot())
        self.layout.addWidget(self.aha_plot_canvas)
        self.layout.addWidget(NavigationToolbar(self.aha_plot_canvas, self))

        # Table and buttons layout
        self.size.setVerticalStretch(1)
        self.case_label.setSizePolicy(self.size)
        self.left_layout.addWidget(self.case_label)
        self.size.setVerticalStretch(4)
        self.size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(self.size)
        self.left_layout.addWidget(self.table_view)

        self.left_layout.addLayout(self.button_grid)

        self.main_layout.addLayout(self.left_layout)

        # Plot
        self.size.setHorizontalStretch(4)
        self.aha_plot.setSizePolicy(self.size)
        self.main_layout.addWidget(self.aha_plot)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)
        self.parent().statusBar().showMessage("Data loaded and plotted")

    def _create_buttons(self) -> None:
        """Create the layout and signals from buttons"""

        # Next button
        next_button = QPushButton(">", self)
        next_button.clicked.connect(lambda: self.update_case_id(self._next))

        # Previous button
        previous_button = QPushButton("<", self)
        previous_button.clicked.connect(lambda: self.update_case_id(self._previous))

        # Save button
        save_button = QPushButton("Save all", self)
        save_button.clicked.connect(self.save_all_plots)

        # Quit button
        quit_button = QPushButton("Quit", self)
        quit_button.clicked.connect(QApplication.instance().quit)

        # Button layout
        self.button_grid.addWidget(previous_button, 0, 0)
        self.button_grid.addWidget(next_button, 0, 1)
        self.button_grid.addWidget(save_button, 1, 0)
        self.button_grid.addWidget(quit_button, 1, 1)

    def _create_table(self) -> None:
        """Create the table and set its properties"""

        # Table model
        self._update_table()

        # Table settings
        self.table_view.verticalHeader().hide()
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setStretchLastSection(True)

    def _update_table(self) -> None:
        self._set_table_model()
        self.table_view.setModel(self.table_model)

    def _set_table_model(self) -> None:
        self.table_model = table_model.CustomTableModel(self._data, case_id=self.case_id)

    def _create_current_case_label(self) -> None:
        self.case_label = QLabel()
        self.case_label.setFont(QFont("Calibri", 16))
        self.case_label.setText(f"Case:\n'{self.case_id}'")

    def update_view(self) -> None:
        """Updates the table, case label and the plot."""
        # Update table

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

    def set_status_bar(self, message: str) -> None:
        self.parent().statusBar().showMessage(message)

    @Slot(object)
    def update_case_id(self, direction: Callable) -> None:
        current_case_index = self._data.index.get_loc(self.case_id)
        new_index = direction(case_index=current_case_index, n_cases=len(self._data))
        self.case_id = self._data.index[new_index]
        self.parent().statusBar().showMessage(f"Plotting case {self.case_id}")
        self.update_case_label()
        self.update_view()
        self.parent().statusBar().showMessage("Data loaded and plotted")

    @Slot()
    def save_all_plots(self) -> None:
        for case in self._data.index:
            path = Path().resolve() / "data" / "export"
            logger.info(f"Saving images to {path}")
            case_data = data_mapping.case_to_dict(self._data, case)
            plot = aha.AHA(case_data, plot_type=self.plot_type)
            plot.bullseye_smooth(True)
            plt.savefig(path / f"{case}_{self.plot_type}.png")
