import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtWidgets import QVBoxLayout, QWidget

from aha import aha
from aha.utils import data_mapping


class PlotWidget(QWidget):
    """Class holding methods for creating and updating the AHA plot."""

    def __init__(
        self,
        data: pd.DataFrame,
        case_id: str | pd.Index,
        plot_type: str,
        parent: QWidget | None = ...,
    ) -> None:
        super().__init__(parent=parent)
        self._data = data
        self.case_id = case_id
        self.plot_type = plot_type

        self.plot_view = QWidget()
        self.layout = QVBoxLayout(self.plot_view)

        self._plot()

    def create_plot(self) -> None:
        self._plot()

    def update_plot(
        self, data: pd.DataFrame | None, case_id: str | pd.Index, plot_type: str
    ) -> None:
        self._data = data
        self.case_id = case_id
        self.plot_type = plot_type
        self._update_plot()

    def _plot(self) -> None:
        plot_view_canvas = FigureCanvas(self._get_plot())
        self.layout.addWidget(plot_view_canvas)
        self.layout.addWidget(NavigationToolbar(plot_view_canvas, self))

    def _get_plot(self) -> plt.Figure:
        case_data = data_mapping.case_to_dict(self._data, self.case_id)
        logger.debug(f"\nReading data: \nCase ID: {self.case_id} \n{case_data}")
        plot = aha.AHA(case_data, plot_type=self.plot_type)

        return plot.bullseye_smooth(True)

    def _update_plot(self) -> None:
        """Updates the plot according to the new case_id"""
        self._remove_old_canvas()
        self._plot()

    def _remove_old_canvas(self) -> None:
        for i in reversed(range(self.layout.count())):
            layout_item = self.layout.takeAt(i)
            if layout_item:
                widget = layout_item.widget()
                if widget:
                    widget.deleteLater()
