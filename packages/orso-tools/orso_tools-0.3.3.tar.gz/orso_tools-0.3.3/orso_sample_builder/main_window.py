import warnings

from traceback import format_exc

import yaml

from numpy import linspace
from orsopy.fileio import model_language as ml
from PySide6.QtCore import QObject, QRunnable, QSize, QThreadPool, Signal, Slot
from PySide6.QtWidgets import QErrorMessage, QFileDialog, QInputDialog, QMainWindow, QToolButton
from refnx.util import xray_energy

from orso_sample_builder.ui_main_window import Ui_MainWindow

DEFAULT_MODEL = """stack: vacuum | Fe 100 | Si
"""

try:
    import refnx
except ImportError:
    refnx = None


class WorkerSignals(QObject):
    resolved = Signal()
    finished = Signal()
    exception = Signal(str, str)


class SimulationWorker(QRunnable):
    """Thread to analyze a sample model in the background, can take a while to find e.g. materials."""

    def __init__(self, sample_model: ml.SampleModel, xray_energy=None):
        super(SimulationWorker, self).__init__()
        self.sample_model = sample_model
        if xray_energy is None:
            self.x = linspace(1e-10, 0.3, 300)
        else:
            self.x = linspace(1e-10, 0.5, 300)
        self.xray_energy = xray_energy
        self.ysim = None
        self.z = None
        self.SLDsim = None
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        # make a local copy not to modify the header information
        sample_model = ml.SampleModel.from_dict(self.sample_model.to_dict())

        with warnings.catch_warnings(action="error"):
            try:
                layers = sample_model.resolve_to_layers()
            except Exception as e:
                self.show_message("Could not resolve model to layers:", f"{format_exc()}")
                return
        self.signals.resolved.emit()

        if refnx is None:
            # refnx is not available, only resolve model
            return

        from refnx.reflect import SLD, ReflectModel, Structure

        if self.xray_energy is None:
            structure = Structure()
            for lj in layers:
                try:
                    m = SLD(lj.material.get_sld() * 1e6)
                except Exception as e:
                    self.show_message(f"Could not resolve material for layer {lj}:", f"{e}")
                    return
                structure |= m(lj.thickness.as_unit("angstrom"), lj.roughness.as_unit("angstrom"))
            model = ReflectModel(structure, bkg=0.0)
        else:
            structure = Structure()
            for lj in layers:
                try:
                    m = SLD(lj.material.get_sld(xray_energy=self.xray_energy / 1000.0) * 1e6)
                except Exception as e:
                    self.show_message(f"Could not resolve material for layer {lj}:", f"{e}")
                    return
                structure |= m(lj.thickness.as_unit("angstrom"), lj.roughness.as_unit("angstrom"))
            model = ReflectModel(structure, bkg=0.0)

        self.ysim = model(self.x)
        self.z, self.SLDsim = structure.sld_profile()

        self.signals.finished.emit()

    def show_message(self, message, traceback=None):
        self.signals.exception.emit(message, traceback)


class MainWindow(QMainWindow):
    current_model: ml.SampleModel

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.threadpool = QThreadPool()

        self.init_editor()
        self.activateWindow()

    def init_editor(self):
        doc = self.ui.model_editor.document()
        font = doc.defaultFont()
        font.setFamily("Courier New")
        doc.setDefaultFont(font)
        for chld in self.ui.editor_toolbar.children():
            if isinstance(chld, QToolButton):
                chld.pressed.connect(self.insert_class)
        from orsopy.fileio import model_language as ml

        try:
            for subcls in ml.SubStackType.__subclasses__():
                if subcls is ml.SubStack:
                    continue
                self.ui.complex_selector.addItem(subcls.__name__)
        except AttributeError:
            # feature not yet part of official orsopy release
            self.ui.complex_selector.hide()
        else:
            self.ui.complex_selector.currentIndexChanged.connect(self.insert_complex)

        # doc.setPlainText(DEFAULT_MODEL)
        doc.setPlainText("")
        self.current_model = ml.SampleModel(stack="vacuum | Fe 100 | Si")
        self.ui.model_editor.insert_class("SampleModel", **self.current_model.to_dict())

    def show_error(self, message, traceback=None):
        dia = QErrorMessage(parent=self)
        output = f"<h2>{message}</h2>"
        if traceback:
            output += f"<pre>{traceback}</pre>"
        dia.showMessage(output)
        dia.resize(QSize(600, 400))
        dia.setWindowTitle("Error: Sample Builder")
        dia.exec()

    def update_model(self):
        """
        Use the text in the editor to update the model. If an error occurs the editor
        shows a red background and the model stays unchanged.
        """
        sample_yaml = self.ui.model_editor.toPlainText()
        try:
            sample_dict = yaml.safe_load(sample_yaml)
        except Exception as e:
            self.ui.model_editor.setStyleSheet("background-color: #ffaaaa;")
            self.show_error("Issue in YAML code:", f"{e}")
            return
        else:
            self.ui.model_editor.setStyleSheet("background-color: #ffffff;")
            if "data_source" in sample_dict:
                sample_dict = sample_dict["data_source"]
            if "sample" in sample_dict:
                sample_dict = sample_dict["sample"]
            if "model" in sample_dict:
                sample_dict = sample_dict["model"]

        self.ui.model_viewer.preparing_sample()

        with warnings.catch_warnings(action="error"):
            try:
                sample_model = ml.SampleModel.from_dict(sample_dict)
            except Exception as e:
                self.show_error("Issue in SampleModel definition:", f"{format_exc()}")
                return
            else:
                self.current_model = sample_model
                # regenerate the model yaml
                self.ui.model_editor.setPlainText(self.current_model.to_yaml())

        if self.ui.radiation_xray.isChecked():
            xray_energy = self.ui.radiation_energy.value()
        else:
            xray_energy = None
        self._worker = SimulationWorker(self.current_model, xray_energy=xray_energy)
        self._worker.signals.resolved.connect(self.show_model)
        self._worker.signals.finished.connect(self.plot_model)
        self._worker.signals.exception.connect(self.show_error)
        self.threadpool.start(self._worker)

    def plot_model(self):
        self.ui.graph_refl.axes.clear()
        self.ui.graph_refl.axes.semilogy(self._worker.x, self._worker.ysim)
        self.ui.graph_refl.axes.set_xlabel("Q / Å$^{-1}$")
        self.ui.graph_refl.axes.set_ylabel("Reflectivity")
        self.ui.graph_refl.fig.draw_idle()
        self.ui.graph_sld.axes.clear()
        self.ui.graph_sld.axes.plot(self._worker.SLDsim, -self._worker.z)
        self.ui.graph_sld.axes.set_xlabel("SLD / 10$^{-6}$ Å$^{-2}$")
        self.ui.graph_sld.axes.set_ylabel("z-depth / Å")
        self.ui.graph_sld.fig.draw_idle()

    def show_model(self):
        self.ui.model_viewer.show_sample_model(self._worker.sample_model)

    def insert_class(self):
        self.ui.model_editor.insert_class(self.sender().text())

    def insert_complex(self, idx):
        if idx == 0:
            return
        self.ui.complex_selector.setCurrentIndex(0)
        self.ui.model_editor.insert_class(self.ui.complex_selector.itemText(idx))

    def load_model(self):
        sfile, sfilter = QFileDialog.getOpenFileName(self, filter="Sample Model YAML (*.yml *.yaml);;ORSO File (*.ort)")
        if not sfile:
            return
        if sfilter == "Sample Model YAML (*.yml *.yaml)":
            self.ui.model_editor.setPlainText(open(sfile, "r").read())
        else:
            from orsopy.fileio import load_orso

            datasets = load_orso(sfile)
            index = 0
            if len(datasets) > 1:
                dataset_names = [di.info.data_set for di in datasets]
                item, ok = QInputDialog.getItem(self, "Choose Dataset", "dataset", dataset_names, editable=False)
                if not ok:
                    return
                index = dataset_names.index(item)
            self.ui.model_editor.setPlainText(datasets[index].info.data_source.sample.model.to_yaml())
        self.update_model()

    def save_model(self):
        sfile, sfilter = QFileDialog.getSaveFileName(self, filter="Sample Model YAML (*.yml *.yaml);;ORSO File (*.ort)")
        if not sfile:
            return
        self.update_model()
        if sfilter == "Sample Model YAML (*.yml *.yaml)":
            text = self.ui.model_editor.toPlainText()
            open(sfile, "w").write(text)
        else:
            from orsopy.fileio import load_orso, save_orso

            datasets = load_orso(sfile)
            index = 0
            if len(datasets) > 1:
                dataset_names = [di.info.data_set for di in datasets]
                item, ok = QInputDialog.getItem(self, "Choose Dataset", "dataset", dataset_names, editable=False)
                if not ok:
                    return
                index = dataset_names.index(item)
            datasets[index].info.data_source.sample.model = self.current_model
            save_orso(datasets, sfile)

    def model_help(self):
        pass
