import os

from PySide6.QtWidgets import QVBoxLayout, QWidget

os.environ["QT_API"] = "PySide6"

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas  # noqa: E402
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402


class MplCanvas(QWidget):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super().__init__(parent=parent)

        layout = QVBoxLayout(self)
        self.fig = FigureCanvas(Figure(figsize=(width, height), dpi=dpi))
        layout.addWidget(self.fig)
        navbar = NavigationToolbar(self.fig, self)
        layout.addWidget(navbar)
        self.fig.figure.set_tight_layout(True)

        self.axes = self.fig.figure.add_subplot(111)
