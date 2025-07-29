from __future__ import annotations

from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from ewoksorange.gui.orange_imports import Input
from ewoksorange.gui.orange_imports import Output
from silx.gui.colors import Colormap

from darfix import dtypes
from darfix.gui.rockingCurvesWidget import RockingCurvesWidget
from darfix.tasks.rocking_curves import RockingCurves


class RockingCurvesWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=RockingCurves):
    name = "rocking curves"
    icon = "icons/curves.png"
    want_main_area = True
    want_control_area = False

    _ewoks_inputs_to_hide_from_orange = ("int_thresh", "method", "output_filename")

    # Inputs
    class Inputs:
        colormap = Input("colormap", Colormap)

    class Outputs:
        colormap = Output("colormap", Colormap)

    def __init__(self):
        super().__init__()

        self._widget = RockingCurvesWidget(parent=self)
        self._widget.sigFitClicked.connect(self._launch_fit)
        self.mainArea.layout().addWidget(self._widget)
        int_thresh = self.get_task_input_value("int_thresh", None)
        method = self.get_task_input_value("method", None)
        if int_thresh is not None:
            self._widget.intThresh = int_thresh
        if method is not None:
            self._widget._fitMethod.setCurrentText(method)

    def handleNewSignals(self) -> None:
        dataset = self.get_task_input_value("dataset")
        self.setDataset(dataset, pop_up=True)

        # Do not call super().handleNewSignals() to prevent propagation

    def setDataset(self, dataset: dtypes.Dataset | None, pop_up=True):
        if dataset is None:
            return
        self._widget.setDataset(dataset)
        if pop_up:
            self.open()

    @Inputs.colormap
    def setColormap(self, colormap):
        self._widget.setStackViewColormap(colormap)

    def get_task_inputs(self):
        task_inputs = super().get_task_inputs()

        # Saving is handled by the widget
        task_inputs["output_filename"] = None

        return task_inputs

    def task_output_changed(self) -> None:
        self._widget.onFitFinished()
        dataset = self.get_task_output_value("dataset", None)
        maps = self.get_task_output_value("maps", None)
        if dataset is not None and maps is not None:
            if not isinstance(dataset, dtypes.Dataset):
                raise dtypes.DatasetTypeError(dataset)
            self._widget.updateDataset(dataset.dataset, maps)
        self.Outputs.colormap.send(self._widget.getStackViewColormap())

    def _launch_fit(self):
        self.set_default_input("int_thresh", self._widget.intThresh)
        self.set_default_input("method", self._widget._fitMethod.currentText())
        self.execute_ewoks_task()
