from typing import Optional

import pandas as pd
from loguru import logger
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor


class NoDataProvided(ValueError):
    """In case the data was not provided to the"""


class CustomTableModel(QAbstractTableModel):
    """Class holding the segment data table model"""

    def __init__(self, data: pd.DataFrame | None = None):
        if data is None:
            raise NoDataProvided("Provide data with segmental values for the table")
        QAbstractTableModel.__init__(self)
        self.load_data(data)
        self.segment_names = data.columns.to_numpy()
        logger.debug(self.segment_names)

    def load_data(self, data: pd.DataFrame, case_id: str = "Cid1") -> None:
        self.segment_values = data.loc[case_id].values

        self.column_count = 2
        self.row_count = len(self.segment_values)
        logger.debug(self.row_count)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Optional[str]:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Segment Name", "Segment Value")[section]
        return f"{section}"

    def rowCount(
        self, parent: QModelIndex = QModelIndex()  # pylint: disable=unused-argument
    ) -> int:
        return self.row_count

    def columnCount(
        self, parent: QModelIndex = QModelIndex()  # pylint: disable=unused-argument
    ) -> int:
        return self.column_count

    def data(self, index: QModelIndex, role: Qt.DisplayRole = Qt.DisplayRole) -> str | None:
        """Controls the data display parameters in the table

        Args:
            index (QModelIndex): Indexes of the table, both rows and columns.
            role (Qt.DisplayRole, optional): The role of the parameter. Defaults to Qt.DisplayRole.

        Returns:
            str | None: Parameter set for controlling table display. Depends on the role.
        """
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            if column == 0:
                segment_name = self.segment_names[row]
                return str(segment_name)
            if column == 1:
                segment_value = self.segment_values[row]
                return str(segment_value)
        if role == Qt.BackgroundRole:
            return QColor(Qt.black)
        if role == Qt.TextAlignmentRole:
            if column == 0:
                return Qt.AlignRight
            if column == 1:
                return Qt.AlignCenter

        return None
