from __future__ import annotations

import h5py
from silx.gui import qt

from darfix import dtypes
from darfix.core.datapathfinder import DETECTOR_KEYWORD
from darfix.core.datapathfinder import FIRST_SCAN_KEYWORD
from darfix.core.datapathfinder import LAST_SCAN_KEYWORD
from darfix.gui.configuration.action import AdvancedConfigurationAction
from darfix.gui.configuration.action import RequiredConfigurationAction
from darfix.gui.configuration.level import ConfigurationLevel
from darfix.gui.utils.data_path_selection import DataPathSelection
from darfix.gui.utils.fileselection import FileSelector
from darfix.tasks.hdf5_data_selection import HDF5DataSelection

from .DataSelectionBase import DataSelectionBase


class HDF5DatasetSelectionWindow(qt.QMainWindow):
    """Main window dedicated to define a HDF5 dataset"""

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)
        # define toolbar
        toolbar = qt.QToolBar(self)
        self.addToolBar(qt.Qt.TopToolBarArea, toolbar)

        self.__configurationModesAction = qt.QAction(self)
        self.__configurationModesAction.setCheckable(False)
        menu = qt.QMenu(self)
        self.__configurationModesAction.setMenu(menu)
        toolbar.addAction(self.__configurationModesAction)

        self.__configurationModesGroup = qt.QActionGroup(self)
        self.__configurationModesGroup.setExclusive(True)
        self.__configurationModesGroup.triggered.connect(self._userModeChanged)

        self._requiredConfigAction = RequiredConfigurationAction(toolbar)
        menu.addAction(self._requiredConfigAction)
        self.__configurationModesGroup.addAction(self._requiredConfigAction)
        self._advancedConfigAction = AdvancedConfigurationAction(toolbar)
        menu.addAction(self._advancedConfigAction)
        self.__configurationModesGroup.addAction(self._advancedConfigAction)

        # define main widget
        self._mainWidget = HDF5DatasetSelectionTabWidget(self)
        self.setCentralWidget(self._mainWidget)

        # set up
        self._advancedConfigAction.setChecked(True)
        self._userModeChanged(self._advancedConfigAction)

    def getHDF5DatasetSelectionWidget(self):
        return self._mainWidget

    def _userModeChanged(self, action):
        self.__configurationModesAction.setIcon(action.icon())
        self.__configurationModesAction.setToolTip(action.tooltip())
        if action is self._requiredConfigAction:
            level = ConfigurationLevel.REQUIRED
        elif action is self._advancedConfigAction:
            level = ConfigurationLevel.ADVANCED
        else:
            raise NotImplementedError
        self.setConfigurationLevel(level=level)

    # expose API
    def setConfigurationLevel(self, level: ConfigurationLevel | str):
        self._mainWidget.setConfigurationLevel(level)


class HDF5DatasetSelectionTabWidget(DataSelectionBase):
    """
    Window to define a HDF5 dataset to be used.
    It contains three tabs: one for the raw data, one for the background and one for the treated data.
    """

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)

        # connect signal / slot
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        assert isinstance(self._darkDataWidget, HDF5DarkDatasetSelectionWidget)
        self._rawDataWidget.sigInputFileChanged.connect(self.sigRawDataInfosChanged)
        self._rawDataWidget._detectorDataPath.sigPatternChanged.connect(
            self.sigRawDataInfosChanged
        )
        self._rawDataWidget._positionerDataPath.sigPatternChanged.connect(
            self.sigRawDataInfosChanged
        )
        self._rawDataWidget.sigKeepDataOnDiskChanged.connect(
            self.sigRawDataInfosChanged
        )
        self._rawDataWidget.sigTitleChanged.connect(self.sigRawDataInfosChanged)

        self._darkDataWidget.sigInputFileChanged.connect(self.sigDarkDataInfosChanged)
        self._darkDataWidget._detectorDataPath.sigPatternChanged.connect(
            self.sigDarkDataInfosChanged
        )
        self._darkDataWidget._positionerDataPath.sigPatternChanged.connect(
            self.sigDarkDataInfosChanged
        )

    def _updateDataset(self, dataset):
        self._dataset = dataset

    def buildRawDataWidget(self):
        widget = HDF5RawDatasetSelectionWidget()
        widget._detectorDataPath.hideExample()
        widget._detectorDataPath.setPlaceholderText("/path/to/detector/dataset")
        widget._positionerDataPath.hideExample()
        widget._positionerDataPath.setPlaceholderText("/path/to/positioners")
        return widget

    def buildDarkDataWidget(self):
        widget = HDF5DarkDatasetSelectionWidget()
        widget._detectorDataPath.hideExample()
        widget._detectorDataPath.setPlaceholderText("/path/to/detector/dataset")
        widget._positionerDataPath.hide()
        return widget

    @property
    def dataset(self):
        return self._dataset

    def getDataset(self) -> dtypes.Dataset:
        return dtypes.Dataset(
            dataset=self._dataset,
            indices=self.indices,
            bg_indices=self.bg_indices,
            bg_dataset=self.bg_dataset,
        )

    def setConfigurationLevel(self, level: ConfigurationLevel):
        self._rawDataWidget.setConfigurationLevel(level)
        self._darkDataWidget.setConfigurationLevel(level)

    def getRawDataInputFile(self) -> str:
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        return self._rawDataWidget.getInputFile()

    def setRawDataInputFile(self, file_path: str):
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        self._rawDataWidget.setInputFile(file_path)

    def getRawDataDetectorPattern(self) -> str:
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        return self._rawDataWidget.getDetectorDataPathSelection().getPattern()

    def setRawDataDetectorPattern(self, pattern: str) -> None:
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        self._rawDataWidget.getDetectorDataPathSelection().setPattern(pattern=pattern)

    def getRawDataMetadataPattern(self) -> str:
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        return self._rawDataWidget.getMetadataPathSelection().getPattern()

    def setRawDataMetadataPattern(self, pattern: str) -> None:
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        return self._rawDataWidget.getMetadataPathSelection().setPattern(
            pattern=pattern
        )

    def getWorkflowTitle(self) -> str:
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        return self._rawDataWidget.getWorkflowTitle()

    def setWorkflowTitle(self, title: str):
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        self._rawDataWidget.setWorkflowTitle(title=title)

    def isInMemory(self) -> bool:
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        return not self._rawDataWidget.isKeepingDataOnDisk()

    def setInMemory(self, in_memory: bool):
        assert isinstance(self._rawDataWidget, HDF5RawDatasetSelectionWidget)
        self._rawDataWidget.setKeepDataOnDisk(not in_memory)

    def getBackgroundInputFile(self) -> str:
        assert isinstance(self._darkDataWidget, HDF5DarkDatasetSelectionWidget)
        return self._darkDataWidget.getInputFile()

    def setBackgroundInputFile(self, file_path):
        assert isinstance(self._darkDataWidget, HDF5DarkDatasetSelectionWidget)
        return self._darkDataWidget.setInputFile(file_path=file_path)

    def getBackgroundDetectorPattern(self) -> str:
        return self._darkDataWidget.getDetectorDataPathSelection().getPattern()

    def setBackgroundDetectorPattern(self, pattern: str) -> None:
        self._darkDataWidget.getDetectorDataPathSelection().setPattern(pattern=pattern)

    def getTreatedDataDir(self) -> str:
        return self._treatedDirData.getDir()


class HDF5DatasetSelectionWidget(qt.QWidget):
    """Widget to concatenate a series of scans together"""

    sigInputFileChanged = qt.Signal(str)

    DETECTOR_PATH_ALLOWED_KEYWORDS = (
        DETECTOR_KEYWORD,
        FIRST_SCAN_KEYWORD,
        LAST_SCAN_KEYWORD,
    )

    POSITIONER_PATH_ALLOWED_KEYWORDS = (
        FIRST_SCAN_KEYWORD,
        LAST_SCAN_KEYWORD,
    )

    def __init__(
        self,
        parent: qt.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setLayout(qt.QGridLayout())
        # input file selector
        self._inputFileSelector = FileSelector(label="input file:")
        self.layout().addWidget(self._inputFileSelector, 0, 0, 1, 5)
        self._inputFileSelector.setDialogFileMode(qt.QFileDialog.ExistingFile)
        self._inputFileSelector.setDialogNameFilters(
            ("HDF5 files (*.h5 *.hdf5 *.nx *.nxs *.nexus)",)
        )

        # detector data path
        self._detectorDataPath = DataPathSelection(
            self,
            title="detector-data path",
            completer_display_dataset=True,
            data_path_type=h5py.Dataset,
        )
        self._detectorDataPath.setPattern(
            HDF5DataSelection.DEFAULT_DETECTOR_DATA_PATH,
            store_as_default=True,
        )
        self._detectorDataPath.setAvailableKeywords(self.DETECTOR_PATH_ALLOWED_KEYWORDS)
        self.layout().addWidget(self._detectorDataPath, 1, 0, 1, 5)
        # positioner data path
        self._positionerDataPath = DataPathSelection(
            self,
            title="metadata path (positioners)",
            completer_display_dataset=False,
            data_path_type=h5py.Group,
        )
        self._positionerDataPath.setPattern(
            HDF5DataSelection.DEFAULT_POSITIONERS_DATA_PATH,
            store_as_default=True,
        )
        self._positionerDataPath.setAvailableKeywords(
            self.POSITIONER_PATH_ALLOWED_KEYWORDS
        )
        self.layout().addWidget(self._positionerDataPath, 2, 0, 1, 5)

        # spacer
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 999, 0, 1, 5)

        # connect signal / slot
        self._inputFileSelector.sigFileChanged.connect(self._inputFileChanged)

    def _inputFileChanged(self):
        input_file = self.getInputFile()
        self._detectorDataPath.setInputFile(input_file)
        self._positionerDataPath.setInputFile(input_file)
        self.sigInputFileChanged.emit(input_file)

    def getDetectorDataPathSelection(self) -> DataPathSelection:
        return self._detectorDataPath

    def getMetadataPathSelection(self) -> DataPathSelection | None:
        return self._positionerDataPath

    def setInputFile(self, file_path: str):
        self._inputFileSelector.setFilePath(file_path=file_path)
        self._inputFileChanged()

    def getInputFile(self) -> str | None:
        return self._inputFileSelector.getFilePath()

    def setConfigurationLevel(self, level: ConfigurationLevel | str):
        level = ConfigurationLevel.from_value(level)
        self._positionerDataPath.setVisible(level > ConfigurationLevel.REQUIRED)
        self._detectorDataPath.setVisible(level > ConfigurationLevel.REQUIRED)


class HDF5RawDatasetSelectionWidget(HDF5DatasetSelectionWidget):
    """Same as the 'HDF5DatasetSelectionWidget' but adds an option to keep data on disk and to provide the title"""

    sigKeepDataOnDiskChanged = qt.Signal(bool)
    sigTitleChanged = qt.Signal(str)

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)
        self._keepDataOnDisk = qt.QCheckBox("Keep data on disk")
        self.layout().addWidget(self._keepDataOnDisk, 1, 3, 2, 2)

        self._titleLabel = qt.QLabel("Workflow title")
        self.layout().addWidget(self._titleLabel, 3, 0, 1, 1)
        self._title = qt.QLineEdit("")
        self.layout().addWidget(self._title, 3, 1, 1, 4)

        # redefine layout because we want to display 'title' just after the file path selection
        self.layout().addWidget(self._detectorDataPath, 4, 0, 1, 5)
        self.layout().addWidget(self._positionerDataPath, 5, 0, 1, 5)

        # connect signal / slot
        self._keepDataOnDisk.toggled.connect(self.sigKeepDataOnDiskChanged)
        self._title.editingFinished.connect(self._titleChanged)

    def isKeepingDataOnDisk(self) -> bool:
        return self._keepDataOnDisk.isChecked()

    def setKeepDataOnDisk(self, value: bool):
        self._keepDataOnDisk.setChecked(value)

    def getWorkflowTitle(self) -> str:
        return self._title.text()

    def setWorkflowTitle(self, title: str):
        self._title.setText(title)
        self._titleChanged()

    def _titleChanged(self, *args, **kwargs):
        self.sigTitleChanged.emit(self._title.text())


class HDF5DarkDatasetSelectionWidget(HDF5DatasetSelectionWidget):
    """Same as the 'HDF5DatasetSelectionWidget' but hide metadata selection that is unused for dark"""

    def setConfigurationLevel(self, level: ConfigurationLevel | str):
        # no positioner posible for dark so hide the selection
        super().setConfigurationLevel(level)
        self._positionerDataPath.hide()

    def getMetadataPathSelection(self) -> None:
        return None
