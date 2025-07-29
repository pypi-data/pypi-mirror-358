from __future__ import annotations

from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from ewoksorange.gui.orange_imports import Input
from ewoksorange.gui.orange_imports import Output
from silx.gui.colors import Colormap

from darfix import dtypes
from darfix.core.noiseremoval import NoiseRemovalOperation
from darfix.gui.noiseremoval.noiseRemovalWidget import NoiseRemovalDialog
from darfix.tasks.noiseremoval import NoiseRemoval


class NoiseRemovalWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=NoiseRemoval):
    name = "noise removal"
    description = "A widget to perform various noise removal operations"
    icon = "icons/noise_removal.png"
    want_main_area = True
    want_control_area = False

    _ewoks_inputs_to_hide_from_orange = ("operations",)

    # Inputs
    class Inputs:
        colormap = Input("colormap", Colormap)

    # Outputs
    class Outputs:
        colormap = Output("colormap", Colormap)

    def __init__(self):
        super().__init__()

        self._widget = NoiseRemovalDialog(parent=self)
        self.mainArea.layout().addWidget(self._widget)
        self._widget.mainWindow.sigLaunchOperation.connect(
            self._execute_noise_removal_operation
        )
        self._current_operation: NoiseRemovalOperation | None = None
        self._widget.okSignal.connect(self.propagate_downstream)
        self._widget.abortSignal.connect(self.abort)

    def _setCurrentOperation(self, operation: NoiseRemovalOperation | None):
        self._current_operation = operation
        self._widget.setIsComputing(bool(operation))

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
        self._widget.mainWindow.setStackViewColormap(colormap)

    def _execute_noise_removal_operation(
        self, operation: NoiseRemovalOperation
    ) -> None:
        # Apply operations one after the other: take the previous output as input
        # Note:: the history is being kept by '_widget'
        output_dataset = self._widget.getOutputDataset()

        self.set_dynamic_input("dataset", output_dataset)
        self.set_dynamic_input("operations", [operation])

        self._setCurrentOperation(operation)
        self.execute_ewoks_task_without_propagation()

    def task_output_changed(self):
        self._setCurrentOperation(None)
        new_dataset: dtypes.Dataset | None = self.get_task_output_value("dataset", None)
        if new_dataset is None:
            return
        self._widget.setOutputDataset(new_dataset)
        self.Outputs.colormap.send(self._widget.mainWindow.getStackViewColormap())

    def propagate_downstream(self, succeeded: bool | None = None):
        # Save operation history in default inputs
        self.set_default_input("operations", self._widget.getOperationHistory())
        super().propagate_downstream(succeeded)
        self.close()

    def abort(self):
        self._widget.mainWindow.abortOperation(self._current_operation)
        self._setCurrentOperation(None)
