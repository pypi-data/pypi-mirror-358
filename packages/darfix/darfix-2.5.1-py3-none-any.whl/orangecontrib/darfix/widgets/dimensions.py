from __future__ import annotations

from typing import Optional

from ewokscore.missing_data import MISSING_DATA
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from ewoksorange.gui.parameterform import block_signals
from silx.gui import qt

from darfix import dtypes
from darfix.core.dimension import Dimension
from darfix.gui.dimensionsWidget import DimensionWidget
from darfix.gui.dimensionsWidget import _DimensionItem
from darfix.tasks.dimensiondefinition import DimensionDefinition


class DimensionWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=DimensionDefinition):
    """
    Widget used to define the calibration of the experimentation (select motor
    positions...)
    """

    name = "dimension definition"
    id = "orange.widgets.darfix.dimensiondefinition"
    description = "Define the dimension followed during the acquisition"
    icon = "icons/param_dims.svg"

    _ewoks_inputs_to_hide_from_orange = ("dims", "tolerance", "metadata_type")

    priority = 4
    keywords = ["dataset", "calibration", "motor", "angle", "geometry"]
    want_main_area = False

    def __init__(self):
        super().__init__()
        self._widget = DimensionWidget(parent=self)
        self.controlArea.layout().addWidget(self._widget)

        # buttons
        types = qt.QDialogButtonBox.Ok
        self.buttons = qt.QDialogButtonBox(parent=self)
        self.buttons.setStandardButtons(types)
        self.controlArea.layout().addWidget(self.buttons)

        self.buttons.accepted.connect(self.validate)
        self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled(False)

        # connect Signal/SLOT
        self._widget.sigFit.connect(self.execute_ewoks_task_without_propagation)
        self._widget.sigToleranceChanged.connect(self._toleranceHasChanged)
        self._widget.sigDimsChanged.connect(self._dimsChanged)
        self._widget.sigMetadataTypeChanged.connect(self._metadataTypeChanged)

        # set up
        tolerance = self.get_task_input_value("tolerance", MISSING_DATA)
        if tolerance is not MISSING_DATA:
            with block_signals(self._widget):
                self._widget.setTolerance(tolerance)

        dims = self.get_task_input_value("dims", MISSING_DATA)
        if dims is not MISSING_DATA:
            with block_signals(self._widget):
                # dims values are Dimension provided as dict (to save settings in a readable manner).
                # So when loading them we must convert them back to Dimension
                dims = convert_dim_from_dict_to_Dimension(dims)
                self._widget.setDims(dims)

        metadata_type = self.get_task_input_value("metadata_type", MISSING_DATA)
        if metadata_type is not MISSING_DATA:
            with block_signals(self._widget):
                self._widget.setMetadataType(metadata_type)

    def setDataset(self, dataset: Optional[dtypes.Dataset], pop_up: bool = False):
        """
        Input signal to set the dataset.
        """
        if dataset is None:
            return
        self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled(False)
        try:
            self._widget.setDataset(dataset)
        except ValueError as e:
            qt.QMessageBox.warning(self, "Fail to setup dimension definition", str(e))
        else:
            # note: set_dynamic_input instead of set_static_input to make sure the dataset
            # will not be saved as orange Settings in the .ows file
            self.set_dynamic_input("dataset", dataset)
            if pop_up:
                self.open()

    def validate(self):
        """
        Tries to fit the dimensions into the dataset.
        """
        self.propagate_downstream()
        self.accept()

    # expose API
    def setDims(self, dims):
        self._widget.setDims(dims=dims)

    def task_output_changed(self) -> None:
        dataset = self.get_task_output_value("dataset", MISSING_DATA)
        if dataset in (MISSING_DATA, None):
            darfix_dataset = None
        else:
            if not isinstance(dataset, dtypes.Dataset):
                raise dtypes.DatasetTypeError(dataset)
            self.buttons.button(qt.QDialogButtonBox.Ok).setEnabled(True)
            darfix_dataset = dataset.dataset
        self._provideFitFeedback(
            success=self.task_succeeded,
            error=self.task_exception,
            dataset=darfix_dataset,
        )

        return super().task_output_changed()

    def _provideFitFeedback(self, success: bool, error: str, dataset):
        msg = qt.QMessageBox()
        if success:
            icon = qt.QMessageBox.Information
            dim_names = ", ".join(dataset.dims.get_names())
            text = f"Dimensions {dim_names} could be fit"
            window_title = "Fit succeeded!"
        else:
            icon = qt.QMessageBox.Warning
            text = f"Error: {error}"
            window_title = "Fit failed!"
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle(window_title)
        msg.setStandardButtons(qt.QMessageBox.Ok)
        msg.exec()

    def handleNewSignals(self) -> None:
        """
        Today the DimensionWidgetOW is not processing automatically a dataset when it receives it.
        It wait the user to press optionally 'find dimension', then 'fit' and 'ok' to validate the task
        """
        dataset = self.get_task_input_value("dataset", MISSING_DATA)
        if dataset not in (MISSING_DATA, None):
            self.setDataset(dataset=dataset, pop_up=True)
        # return super().handleNewSignals() do not call to make sure the processing is not triggered

    # settings call back
    def _toleranceHasChanged(self, new_tolerance: Optional[float]):
        self.set_default_input("tolerance", new_tolerance)

    def _dimsChanged(self):
        dims = self._widget.dims
        pickable_dims = make_dims_picklable(dims)
        self.set_default_input("dims", pickable_dims)

    def _metadataTypeChanged(self, metadata_type: int):
        assert isinstance(metadata_type, int)
        self.set_default_input("metadata_type", metadata_type)


def make_dims_picklable(dims: dict):
    if not isinstance(dims, dict):
        raise TypeError("dims should be an instance of dict")
    # convert AcquisitionDims to dict if necessary
    return {key: make_dim_picklable(value) for key, value in dims.items()}


def make_dim_picklable(dim: _DimensionItem | Dimension) -> dict:
    """
    FIXME
    When using the GUI some element of dims can be instances of `_DimensionItem` instead of `Dimension`. The first one is not pickeable.
    But to store settings element must be picklable.
    Most likely it would have been better to modify `_DimensionItem` and make it return directly a pickable instance of `Dimension`.
    But current refactoring (for darfix 2.0) is already too large.
    """
    if isinstance(dim, _DimensionItem):
        return Dimension(
            kind=dim.kind,
            name=dim.name,
            size=dim.size,
            _range=dim._range,
            tolerance=dim.tolerance,
            unique_values=dim.unique_values,
        ).to_dict()
    elif isinstance(dim, Dimension):
        return dim.to_dict()
    else:
        raise NotImplementedError(f"use case not handled. Dim is {type(dim)}")


def convert_dim_from_dict_to_Dimension(dims: dict) -> dict:
    return {key: Dimension.from_dict(value) for key, value in dims.items()}
