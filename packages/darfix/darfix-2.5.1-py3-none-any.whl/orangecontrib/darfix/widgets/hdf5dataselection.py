from functools import partial

from ewokscore.missing_data import is_missing_data
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from ewoksorange.gui.parameterform import block_signals
from silx.gui import qt

from darfix.gui.data_selection.hdf5 import (
    HDF5DatasetSelectionTabWidget as _HDF5DatasetSelectionTabWidget,
)
from darfix.gui.data_selection.hdf5 import HDF5DatasetSelectionWindow
from darfix.tasks.hdf5_data_selection import HDF5DataSelection


class HDF5DataSelectionWidgetOW(
    OWEwoksWidgetOneThread,
    ewokstaskclass=HDF5DataSelection,
):
    """
    Widget to select dataset stored as HDF5
    """

    name = "HDF5 data selection"
    icon = "icons/upload_hdf5.svg"
    want_main_area = True
    want_control_area = False

    priority = 1

    _ewoks_inputs_to_hide_from_orange = (
        "raw_detector_data_path",
        "raw_metadata_path",
        "dark_detector_data_path",
        "workflow_title",
        "in_memory",
        "treated_data_dir",
    )

    def __init__(self):
        super().__init__()

        self._window = HDF5DatasetSelectionWindow()
        self._window.setWindowFlags(qt.Qt.Widget)
        self.__hdf5DatasetSelectionTabWidget = self._window._mainWidget
        assert isinstance(
            self.__hdf5DatasetSelectionTabWidget, _HDF5DatasetSelectionTabWidget
        )
        types = qt.QDialogButtonBox.Ok
        _buttons = qt.QDialogButtonBox(parent=self)
        _buttons.setStandardButtons(types)

        self.mainArea.layout().addWidget(self._window)
        self.mainArea.layout().addWidget(_buttons)

        _buttons.accepted.connect(self.execute_ewoks_task)
        _buttons.accepted.connect(self.accept)

        # set up
        self._load_settings()

        # connect signal / slot
        self.__hdf5DatasetSelectionTabWidget.sigRawDataInfosChanged.connect(
            self._rawInfosChanged
        )
        self.__hdf5DatasetSelectionTabWidget.sigDarkDataInfosChanged.connect(
            self._darkInfosChanged
        )
        self.__hdf5DatasetSelectionTabWidget.sigTreatedDirInfoChanged.connect(
            self._treatedDirInfosChanged
        )
        self.task_executor.finished.connect(
            self.information,
        )
        self.task_executor.started.connect(
            partial(self.information, "Downloading dataset")
        )

    def _load_settings(self):
        """Load workflow settings"""
        # raw data
        raw_input_file = self.get_task_input_value("raw_input_file")
        if not is_missing_data(raw_input_file):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setRawDataInputFile(raw_input_file)
        in_memory = self.get_task_input_value("in_memory")
        if not is_missing_data(in_memory):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setInMemory(in_memory=in_memory)
        workflow_title = self.get_task_input_value("workflow_title")
        if not is_missing_data(workflow_title):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setWorkflowTitle(
                    title=workflow_title
                )
        raw_detector_data_path = self.get_task_input_value("raw_detector_data_path")
        if not is_missing_data(raw_detector_data_path):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setRawDataDetectorPattern(
                    pattern=raw_detector_data_path
                )
        raw_positioners_data_path = self.get_task_input_value("raw_metadata_path")
        if not is_missing_data(raw_positioners_data_path):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setRawDataMetadataPattern(
                    pattern=raw_positioners_data_path
                )
        # dark / background
        dark_input_file = self.get_task_input_value("dark_input_file")
        if not is_missing_data(dark_input_file):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setBackgroundInputFile(
                    dark_input_file
                )
        dark_detector_data_path = self.get_task_input_value("dark_detector_data_path")
        if not is_missing_data(dark_detector_data_path):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setBackgroundDetectorPattern(
                    pattern=dark_detector_data_path
                )

        treated_data_dir = self.get_task_input_value("treated_data_dir")
        if not is_missing_data(treated_data_dir):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setTreatedDir(treated_data_dir)

    def handleNewSignals(self) -> None:
        # update the input file in case they are provided by another widget (like the hdf5 scan concatenation)
        raw_input_file = self.get_task_input_value("raw_input_file", None)
        if raw_input_file != self.__hdf5DatasetSelectionTabWidget.getRawDataInputFile():
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setRawDataInputFile(raw_input_file)

        bg_input_file = self.get_task_input_value("dark_input_file", None)
        if (
            bg_input_file
            != self.__hdf5DatasetSelectionTabWidget.getBackgroundInputFile()
        ):
            with block_signals(self._window):
                self.__hdf5DatasetSelectionTabWidget.setBackgroundInputFile(
                    bg_input_file
                )
        return super().handleNewSignals()

    def _rawInfosChanged(self, *args, **kwargs):
        self.set_default_input(
            "raw_input_file", self.__hdf5DatasetSelectionTabWidget.getRawDataInputFile()
        )
        self.set_default_input(
            "raw_detector_data_path",
            self.__hdf5DatasetSelectionTabWidget.getRawDataDetectorPattern(),
        )
        self.set_default_input(
            "raw_metadata_path",
            self.__hdf5DatasetSelectionTabWidget.getRawDataMetadataPattern(),
        )
        self.set_default_input(
            "workflow_title",
            self.__hdf5DatasetSelectionTabWidget.getWorkflowTitle(),
        )
        self.set_default_input(
            "in_memory",
            self.__hdf5DatasetSelectionTabWidget.isInMemory(),
        )

    def _darkInfosChanged(self, *args, **kwargs):
        self.set_default_input(
            "dark_input_file",
            self.__hdf5DatasetSelectionTabWidget.getBackgroundInputFile(),
        )
        self.set_default_input(
            "dark_detector_data_path",
            self.__hdf5DatasetSelectionTabWidget.getBackgroundDetectorPattern(),
        )

    def _treatedDirInfosChanged(self, *args, **kwargs):
        self.set_default_input(
            "treated_data_dir",
            self.__hdf5DatasetSelectionTabWidget.getTreatedDataDir(),
        )
