from __future__ import annotations

from ewokscore.missing_data import is_missing_data
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from ewoksorange.gui.orange_imports import Input
from ewoksorange.gui.orange_imports import Output
from silx.gui.colors import Colormap

from darfix.dtypes import Dataset
from darfix.gui.roiSelectionWidget import ROISelectionWidget
from darfix.tasks.roi import RoiSelection


class RoiSelectionWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=RoiSelection):
    name = "roi selection"
    icon = "icons/roi.png"
    want_main_area = True
    want_control_area = False

    _ewoks_inputs_to_hide_from_orange = ("roi_origin", "roi_size")

    class Inputs:
        colormap = Input("colormap", Colormap)

    class Outputs:
        colormap = Output("colormap", Colormap)

    def __init__(self):
        super().__init__()

        self._widget = ROISelectionWidget(parent=self)
        self.mainArea.layout().addWidget(self._widget)
        self._widget.sigComputed.connect(self.execute_task)

    def handleNewSignals(self):
        dataset: Dataset = self.get_task_input_value("dataset")

        if is_missing_data(dataset):
            return

        self._widget.setDataset(dataset)
        self.open()
        origin = self.get_default_input_value("roi_origin", [])
        roi_size = self.get_default_input_value("roi_size", [])
        if len(origin) > 0 and len(roi_size) > 0:
            self._widget.setRoi(origin=origin, size=roi_size)

    @Inputs.colormap
    def setColormap(self, colormap):
        self._widget.setStackViewColormap(colormap)

    def execute_task(self, roi_origin, roi_size):
        self.set_default_input("roi_origin", roi_origin)
        self.set_default_input("roi_size", roi_size)
        self.execute_ewoks_task()
        self.accept()

    def task_output_changed(self):
        self.Outputs.colormap.send(self._widget.getStackViewColormap())
