from orsopy import fileio
from orsopy.fileio import model_language
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMainWindow, QStyle, QTreeWidgetItem

from orso_viewer.ui_main_window import Ui_MainWindow

try:
    import refnx
except ImportError:
    refnx = None


class WorkerSignals(QObject):
    resolved = Signal()
    finished = Signal()


class SimulationWorker(QRunnable):
    """Thread to analyze a sample model in the background, can take a while to find e.g. materials."""

    def __init__(self, sample_model: model_language.SampleModel, x, xray_energy=None):
        super(SimulationWorker, self).__init__()
        self.sample_model = sample_model
        self.x = x
        self.xray_energy = xray_energy
        self.ysim = None
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        # make a local copy not to modify the header information
        sample_model = model_language.SampleModel.from_dict(self.sample_model.to_dict())

        layers = sample_model.resolve_to_layers()
        self.signals.resolved.emit()

        if refnx is None:
            # refnx is not available, only resolve model
            return

        from refnx.reflect import SLD, ReflectModel, Structure

        if self.xray_energy is not None:
            structure = Structure()
            for lj in layers:
                m = SLD(lj.material.get_sld() * 1e6)
                structure |= m(lj.thickness.as_unit("angstrom"), lj.roughness.as_unit("angstrom"))
            model = ReflectModel(structure, bkg=0.0)
        else:
            structure = Structure()
            for lj in layers:
                m = SLD(lj.material.get_sld(xray_energy=self.xray_energy) * 1e6)
                structure |= m(lj.thickness.as_unit("angstrom"), lj.roughness.as_unit("angstrom"))
            model = ReflectModel(structure, bkg=0.0)

        self.ysim = model(self.x)

        self.signals.finished.emit()


class MainWindow(QMainWindow):
    datasets: list[fileio.OrsoDataset]

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.datasets = []
        self.threadpool = QThreadPool()

        self.ui.header_tree.setColumnCount(2)
        self.ui.header_tree.setHeaderLabels(["Key", "Type"])

        doc = self.ui.header_data.document()
        font = doc.defaultFont()
        font.setFamily("Courier New")
        doc.setDefaultFont(font)

        self.ui.button_expand.setIcon(self.style().standardIcon(QStyle.SP_TitleBarUnshadeButton))
        self.ui.button_collapse.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    @Slot()
    def open_file(self):
        filename, res = QFileDialog.getOpenFileName(self, caption="Open ORSO File", filter="ORSO Text (*.ort)")
        if res:
            self.read_file(filename)

    def read_file(self, filename):
        self.datasets = fileio.load_orso(filename)

        self.ui.dataset_list.clear()
        self.ui.dataset_list.addItems([str(di.info.data_set) for di in self.datasets])

        self.ui.dataset_list.setCurrentRow(0)

    @Slot(int)
    def dataset_selected(self, index):
        self.plot_dataset(index)
        self.update_header(index)

    def plot_dataset(self, index):
        dataset = self.datasets[index]
        sc = self.ui.data_plot
        sc.axes.clear()
        sc.axes.errorbar(dataset.data[:, 0], dataset.data[:, 1], dataset.data[:, 2], label="data")
        sc.axes.set_yscale("log")
        sc.axes.set_xlabel(dataset.info.columns[0].name + " / " + (dataset.info.columns[0].unit or ""))
        sc.axes.set_ylabel(dataset.info.columns[1].name + " / " + (dataset.info.columns[1].unit or "1"))
        sc.fig.draw_idle()

        try:
            sample_model = dataset.info.data_source.sample.model
        except AttributeError:
            self.ui.sample_viewer.no_sample()
        else:
            self.ui.sample_viewer.preparing_sample()
            self.worker = SimulationWorker(sample_model, dataset.data[:, 0])
            self.worker.signals.resolved.connect(self.show_sample)
            self.worker.signals.finished.connect(self.plot_simulation)
            self.threadpool.start(self.worker)

    @Slot()
    def show_sample(self):
        # the worker already resolved all layers of the model
        self.ui.sample_viewer.show_sample_model(self.worker.sample_model)

    @Slot()
    def plot_simulation(self):
        x = self.worker.x
        ysim = self.worker.ysim
        sc = self.ui.data_plot
        sc.axes.semilogy(x, ysim, label="model")
        sc.axes.legend()
        sc.fig.draw_idle()

    def build_subtree(self, parent, data, obj):
        for key, value in data.items():
            if isinstance(obj, list):
                subobj = obj[key]
                key = str(key)
            else:
                subobj = getattr(obj, key, None)
            if isinstance(subobj, fileio.Header):
                subitem = QTreeWidgetItem([key, subobj.__class__.__name__])
                subitem.setData(0, Qt.ItemDataRole.UserRole, subobj.to_yaml())
                parent.addChild(subitem)
                self.build_subtree(subitem, value, subobj)
            elif isinstance(subobj, list):
                subitem = QTreeWidgetItem([key, "List"])
                subitem.setData(0, Qt.ItemDataRole.UserRole, str(subobj))
                parent.addChild(subitem)
                self.build_subtree(subitem, dict(enumerate(value)), subobj)
            else:
                subitem = QTreeWidgetItem([key, str(subobj)])
                parent.addChild(subitem)

    def update_header(self, index):
        tv = self.ui.header_tree
        dataset: fileio.OrsoDataset = self.datasets[index]
        data = dataset.info.to_dict()
        items = []
        for key, value in data.items():
            obj = getattr(dataset.info, key)
            if isinstance(obj, fileio.Header):
                item = QTreeWidgetItem([key, obj.__class__.__name__])
                item.setData(0, Qt.ItemDataRole.UserRole, obj.to_yaml())
                self.build_subtree(item, value, obj)
            elif isinstance(obj, list):
                item = QTreeWidgetItem([key, "List"])
                item.setData(0, Qt.ItemDataRole.UserRole, str(obj))
                self.build_subtree(item, dict(enumerate(value)), obj)
            else:
                item = QTreeWidgetItem([key, str(obj)])
            items.append(item)

        tv.clear()
        tv.insertTopLevelItems(0, items)

    def show_dataset_item(self, item: QTreeWidgetItem, idx):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data is None:
            self.ui.header_data.setText(item.text(1))
        else:
            self.ui.header_data.setText(data)
