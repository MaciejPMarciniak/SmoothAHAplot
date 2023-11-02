import pandas as pd
from PySide6.QtWidgets import QHeaderView, QTableView, QWidget

from aha_widget import table_model


class TableView(QTableView):
    """Class holding methods for creating and updating the data table."""

    def __init__(
        self,
        data: pd.DataFrame | None = None,
        case_id: str | pd.Index | None = None,
        parent: QWidget | None = ...,
    ) -> None:
        super().__init__(parent=parent)
        self._data = data
        self.case_id = case_id

        self.table_model: table_model.CustomTableModel

        ## Create the table and set its properties
        # Table model
        self._update_table()

        # Table settings
        self.verticalHeader().hide()
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

    def update_table(self, new_case_id: str | pd.Index) -> None:
        self.case_id = new_case_id
        self._update_table()

    def _update_table(self) -> None:
        self._set_table_model()
        self.setModel(self.table_model)

    def _set_table_model(self) -> None:
        self.table_model = table_model.CustomTableModel(self._data, case_id=self.case_id)
