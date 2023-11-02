from pathlib import Path
from typing import Callable

import pandas as pd
from loguru import logger
from matplotlib import pyplot as plt
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from aha import aha
from aha.utils import data_mapping
from aha_widget import plot_widget, table_view


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
        self._data = data
        self.case_id = case_id
        self.plot_type = plot_type

        # QWidget Layout
        self.main_layout = QHBoxLayout()

        # Other layouts
        self.left_layout = QVBoxLayout()
        self.table_view = table_view.TableView(data=self._data, case_id=self.case_id, parent=self)
        self.plot_widget = plot_widget.PlotWidget(
            data=self._data, case_id=self.case_id, plot_type=self.plot_type, parent=self
        )
        self.button_grid = QGridLayout()

        self._create_buttons()
        self._create_current_case_label()
        self._set_layouts()

    def _create_buttons(self) -> None:
        """Create the layout and signals from buttons"""

        # Next button
        next_button = QPushButton(">", self)
        next_button.clicked.connect(lambda: self.update(self._next))

        # Previous button
        previous_button = QPushButton("<", self)
        previous_button.clicked.connect(lambda: self.update(self._previous))

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

    def _create_current_case_label(self) -> None:
        self.case_label = QLabel()
        self.case_label.setFont(QFont("Calibri", 16))
        self.case_label.setText(f"Case:\n'{self.case_id}'")

    def _set_layouts(self) -> None:
        """Sets the sizes of the layouts in the central widget."""
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Table and buttons layout
        size.setVerticalStretch(1)
        self.case_label.setSizePolicy(size)
        self.left_layout.addWidget(self.case_label)

        size.setVerticalStretch(4)
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.left_layout.addWidget(self.table_view)
        self.left_layout.addLayout(self.button_grid)
        self.main_layout.addLayout(self.left_layout)

        # Plot layout
        size.setHorizontalStretch(4)
        self.plot_widget.setSizePolicy(size)
        self.main_layout.addWidget(self.plot_widget.plot_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)

    @staticmethod
    def _next(case_index: int, n_cases: int) -> int:
        return case_index + 1 if case_index != n_cases - 1 else 0

    @staticmethod
    def _previous(case_index: int, n_cases: int) -> int:
        return case_index - 1 if case_index != 0 else n_cases - 1

    @Slot(object)
    def update(self, direction: Callable) -> None:
        self._update_case_id(direction=direction)
        self._update_case_label()
        self._update_table()
        self._update_plot()

    def _update_case_id(self, direction: Callable) -> None:
        current_case_index = self._data.index.get_loc(self.case_id)
        new_index = direction(case_index=current_case_index, n_cases=len(self._data))
        self.case_id = self._data.index[new_index]
        logger.debug(f"{self.case_id=}")

    def _update_case_label(self) -> None:
        self.case_label.setText(f"Case:\n'{self.case_id}'")

    def _update_table(self) -> None:
        self.table_view.update_table(self.case_id)

    def _update_plot(self) -> None:
        self.plot_widget.update_plot(
            data=self._data, case_id=self.case_id, plot_type=self.plot_type
        )

    @Slot()
    def save_all_plots(self) -> None:
        for case in self._data.index:
            path = Path().resolve() / "data" / "export"
            logger.info(f"Saving images to {path}")
            case_data = data_mapping.case_to_dict(self._data, case)
            plot = aha.AHA(case_data, plot_type=self.plot_type)
            plot.bullseye_smooth(True)
            plt.savefig(path / f"{case}_{self.plot_type}.png")
            plt.close()
