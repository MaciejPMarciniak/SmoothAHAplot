import sys

import click
from PySide6.QtWidgets import QApplication

from aha_io import read_data
from aha_widget import central_widget, main_window


@click.command()
@click.option("--filename", "-f", help="Name of the file with segment data.")
def main(filename: str = "") -> int:
    data = read_data.read_data(filename)

    app = QApplication(sys.argv)
    widget = central_widget.Widget(data)
    window = main_window.MainWindow(widget)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
