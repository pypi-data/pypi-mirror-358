from __future__ import annotations

import logging
from functools import partial
from typing import Optional

import numpy
from silx.gui import qt

from darfix import dtypes
from darfix.core.dimension import _METADATA_TYPES
from darfix.core.dimension import _METADATA_TYPES_I
from darfix.core.dimension import DEFAULT_METADATA
from darfix.core.dimension import Dimension
from darfix.tasks.dimensiondefinition import DimensionDefinition

_logger = logging.getLogger(__file__)


class DimensionMapping(qt.QWidget):
    """
    Widget used to define the number of dimension and with which values they are
    mapped
    """

    _V_HEADERS = ["Axis", "Kind", "Name", "Size", "Range", "Tolerance", "", ""]

    sigDimsChanged = qt.Signal()
    """
    Emit when the dimension definition changed. Either if a dimension has been added / removed
    or if one of the parameter (tolerance, size...) has been changed.
    """

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        self._table = qt.QTableWidget(parent=self)
        self._table.setColumnCount(len(self._V_HEADERS))
        self._table.setHorizontalHeaderLabels(self._V_HEADERS)
        header = self._table.horizontalHeader()
        header.setMinimumSectionSize(50)
        if qt.qVersion() < "5.0":
            setResizeMode = header.setResizeMode
        else:
            setResizeMode = header.setSectionResizeMode
        for iColumn in range(len(self._V_HEADERS)):
            if iColumn in (1, 2):
                setResizeMode(iColumn, qt.QHeaderView.Stretch)
            else:
                setResizeMode(iColumn, qt.QHeaderView.ResizeToContents)
        self._table.verticalHeader().hide()
        self._dims = {}

        self.layout().addWidget(self._table, 0, 0, 6, 10)
        self._addButton = qt.QPushButton("Add", parent=self)
        self.layout().addWidget(self._addButton, 6, 6, 1, 1)

        # connect Signal/SLOT
        self._addButton.pressed.connect(self.addDim)

    def clear(self):
        widgets = list(self._dims.values())
        for widget in widgets:
            self.removeDim(widget)

    @property
    def ndim(self):
        return len(self._dims)

    @property
    def dims(self):
        return self._dims

    def addDim(self, axis=None, dim=None):
        """

        :param axis: which axis is defining this dimension
        :param `Dimension` dim: definition of the dimension to add
        """
        if axis is None:
            axis = self._getNextFreeAxis()
        row = self._table.rowCount()
        self._table.setRowCount(row + 1)
        widget = _DimensionItem(parent=self, table=self._table, row=row)
        widget.removed.connect(self.removeDim)
        if dim is not None:
            widget.setDim(dim)
        widget.axis = axis
        self._dims[row] = widget
        self.sigDimsChanged.emit()
        widget.dimValueChanged.connect(self.sigDimsChanged)
        return widget

    def removeDim(self, row):
        """
        Remove dimension.

        :param Union[int,`_DimensionItem`]: row or item to remove
        """
        if isinstance(row, _DimensionItem):
            iRow = row._row
        else:
            iRow = row
        # remove the widget
        self._table.removeRow(iRow)
        self._dims[iRow].removed.disconnect(self.removeDim)
        self._dims[iRow].dimValueChanged.disconnect(self.sigDimsChanged)
        self._dims[iRow].setAttribute(qt.Qt.WA_DeleteOnClose)
        self._dims[iRow].close()
        del self._dims[iRow]
        # reorder existing widgets
        ini_rows = sorted(list(self._dims.keys()))
        for row in ini_rows:
            if row <= iRow:
                continue
            widget = self._dims[row]
            new_row = row - 1
            assert new_row >= 0
            widget.embedInTable(table=self._table, row=new_row)
            widget.axis = self._getNextFreeAxis()
            self._dims[new_row] = widget
            del self._dims[row]
        self.sigDimsChanged.emit()

    def getDim(self, iRow: int):
        """return the instance of _DimensionItem for the iRow"""
        return self._dims.get(iRow, None)

    def _getNextFreeAxis(self):
        """
        :return int: next unused axis
        """
        res = 0
        usedAxis = []
        [usedAxis.append(_dim.axis) for _dim in self._dims.values()]
        while res in usedAxis:
            res = res + 1
        return res


class DimensionWidget(DimensionMapping):
    """
    Widget to define dimensions and try to fit those with dataset
    """

    sigClear = qt.Signal()
    """Emit when the dimension has been cleared by the user"""
    sigToleranceChanged = qt.Signal(object)
    """Emit when the tolerance is changed. object will be None if tolerance is undefined. Else it will be a float"""
    sigMetadataTypeChanged = qt.Signal(int)
    """
    Emit when the metadata type changed. Possible values are:
    * 0: DEFAULT_METADATA
    * 1: COUNTER_METADATA
    * 2: POSITIONER_METADATA
    """
    sigFit = qt.Signal()
    """Emit when user want to fit the dimension"""
    sigDimsChanged = qt.Signal()
    """Emit when the set of dimension has changed"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dataset = None

        metadataTypeLabel = qt.QLabel("Metadata type: ")
        toleranceLabel = qt.QLabel("Tolerance: ")
        self._metadataTypeCB = qt.QComboBox()
        for metaType in _METADATA_TYPES:
            self._metadataTypeCB.addItem(metaType)
        self._toleranceLE = qt.QLineEdit(str(DimensionDefinition.DEFAULT_TOLERANCE))
        self._toleranceLE.setToolTip(
            "Tolerance for which the values in the dimensions will be considered unique"
        )
        validator = qt.QDoubleValidator()
        validator.setBottom(0)
        self._toleranceLE.setValidator(validator)
        self._autoDetect = qt.QPushButton("Find dimensions", parent=self)
        self._autoDetect.setToolTip(
            "Automatically find all dimensions that "
            "change through the dataset. \n"
            "It is considered that a dimension changes "
            "if the number of unique values is greater "
            "than one.\nThe metadata type is needed to "
            "choose which values to compare, and the "
            "threshold to know when two values are "
            "considered to be different.\nThe threshold"
            " is only used in values that are numbers."
        )
        self._fitButton = qt.QPushButton("Fit", parent=self)
        self._fitButton.setToolTip("Try to reshape data into given dimensions")
        self._clearButton = qt.QPushButton("Clear", parent=self)

        self.layout().addWidget(metadataTypeLabel, 6, 0, 1, 1)
        self.layout().addWidget(self._metadataTypeCB, 6, 1, 1, 1)
        self.layout().addWidget(toleranceLabel, 6, 2, 1, 1)
        self.layout().addWidget(self._toleranceLE, 6, 3, 1, 1)
        self.layout().addWidget(self._clearButton)
        self.layout().addWidget(self._fitButton)
        self.layout().addWidget(self._autoDetect, 6, 4, 1, 1)

        # connect Signal/SLOT
        self._fitButton.pressed.connect(self.fit)
        self._clearButton.pressed.connect(self.clear)
        self._autoDetect.pressed.connect(self._find_dimensions)
        self._metadataTypeCB.currentIndexChanged.connect(self._metadataTypeChanged)
        self._toleranceLE.editingFinished.connect(self._toleranceHasChanged)

    def _metadataTypeChanged(self):
        self.sigMetadataTypeChanged.emit(self.getMetadataType())

    def getMetadataType(self) -> int:
        metadata_type = self._metadataTypeCB.currentText()
        return _METADATA_TYPES[metadata_type]

    def setMetadataType(self, metadata_type: str | int):
        # convert metadata_type from int to str
        def convert_from_str_to_int(value):
            for name, value in _METADATA_TYPES.items():
                if value == metadata_type:
                    return name
            raise ValueError(f"invalid metadata type value ({value})")

        if isinstance(metadata_type, int):
            metadata_type = convert_from_str_to_int(value=metadata_type)

        item_idx = self._metadataTypeCB.findText(metadata_type)
        if item_idx > 0:
            self._metadataTypeCB.setCurrentIndex(item_idx)
        else:
            raise ValueError(f"unable to handle metadata_type '{metadata_type}'")

    def _toleranceHasChanged(self):
        self.sigToleranceChanged.emit(self.getTolerance())

    def getTolerance(self) -> Optional[float]:
        tolerance = self._toleranceLE.text()
        if tolerance == "":
            return None
        else:
            try:
                tolerance = self.locale().toFloat(tolerance)[0]
            except Exception:
                _logger.info(f"unable to cast tolerance {tolerance} to a float.")
                return None
            else:
                return tolerance

    def setTolerance(self, tolerance: None | float | str):
        if tolerance is None:
            return
        else:
            self._toleranceLE.setText(str(tolerance))

    def clear(self):
        super().clear()
        self.sigClear.emit()

    def setDataset(self, dataset: dtypes.Dataset):
        """

        :param dataset: the dataset for which we want to define the
                           dimensions.
        :type dataset: `Dataset`
        """
        if not isinstance(dataset, dtypes.Dataset):
            raise dtypes.DatasetTypeError(dataset)
        self._dataset = dataset.dataset
        if dataset.dataset.nframes > 0:
            for widget in self._dims.values():
                widget._setMetadata(self._dataset.get_data().metadata[0])

    def _find_dimensions(self):
        """
        Automatically find all dimensions that change through the dataset.
        It is considered that a dimension changes if the number of unique values
        is greater than one. The metadata type is needed to choose which values
        to compare, and the threshold to know when two values are considered to
        be different. The threshold is only used in values that are numbers.
        """
        print("tolerance is", self.getTolerance())
        self._dataset.find_dimensions(
            kind=self.getMetadataType(), tolerance=self.getTolerance()
        )
        super().clear()
        for axis, dim in self._dataset.dims.items():
            assert isinstance(
                dim, Dimension
            ), f"dim should be an instance of {Dimension}. Get {type(dim)}"
            print(f"when set dim {axis} get range", dim.range)
            self.addDim(axis=axis, dim=dim)

    def fit(self):
        """
        Fit dimensions into the data.

        :returns: return status of the fit and fail reason, if any
        :rtype: Union[bool,str,None]
        """
        self.sigFit.emit()

    def setDims(self, dims):
        """

        :param dict dims: axis as key and `Dimension` as value.
        """
        self.clear()
        if not isinstance(dims, dict):
            raise TypeError(f"dims should be a dict. Get {type(dims)}")

        for axis, dim in dims.items():
            assert type(axis) is int
            assert isinstance(dim, Dimension)
            self.addDim(axis=axis, dim=dim)
            if self._dataset is not None:
                if len(self._dataset.get_data().metadata) > 0:
                    if not dim.unique_values:
                        values = self._dataset.get_metadata_values(dim.kind, dim.name)
                        dim.set_unique_values(values)
                self._dataset.add_dim(axis=axis, dim=dim)

    def addDim(self, axis=None, dim=None):
        """

        :param axis: which axis is defining this dimension
        :param `Dimension` dim: definition of the dimension to add
        """
        widget = super().addDim(axis, dim)
        if self._dataset is not None and len(self._dataset.data.metadata) > 0:
            widget._setMetadata(self._dataset.get_data().metadata[0])

        return widget


class _DimensionItem(Dimension, qt.QWidget):
    """Widget use to define a dimension"""

    removed = qt.Signal(qt.QObject)
    """Signal emitted when the Item should be removed"""

    dimValueChanged = qt.Signal()
    """Signal emitted when the dimension definition is changed"""

    axisChanged = qt.Signal(int, int)
    """Signal emitted when the axis value is changed: id (row), new_value_value
    """

    class _SizeWidget(qt.QWidget):
        valueChanged = qt.Signal(int)
        """Signal emitted when the value of the Spin box change but decorelated
        with the active state
        """

        def __init__(self, parent):
            qt.QWidget.__init__(self, parent)
            self.setLayout(qt.QVBoxLayout())
            self._sizeSP = qt.QSpinBox(parent=self)
            """_sizeSP will be used to define the size. Will be editable if the
            size editable (so if dimension is set from a relative parameter)
            """
            self._sizeSP.setMaximum(99999)
            self.layout().addWidget(self._sizeSP)

            self.layout().setContentsMargins(0, 0, 0, 0)
            self._active = False
            self._sizeSP.hide()
            # expose API
            self.setMinimum = self._sizeSP.setMinimum

            # connect Signal/SLOT
            self._sizeSP.valueChanged.connect(self._valueHasChanged)

        @property
        def value(self):
            return self._sizeSP.value()

        def setValue(self, size, editable=True):
            """

            :param int or None size: the size of the dimension. If None, not
                                     define yet
            :param editable: the size will be editable if given by the use (so)
                             if is relative.
            """
            if size is None:
                self._sizeSP.hide()
                self._sizeLabel.hide()
            else:
                assert type(size) is int
                self._sizeSP.show()
                self._sizeSP.setMaximum(max(99, 2 * size))
                self._sizeSP.setValue(size)
                self.setEnabled(editable)

        def setEnabled(self, editable):
            self._sizeSP.setEnabled(editable)

        def toggle(self, checked):
            self._active = checked
            if checked:
                self._sizeSP.show()
            else:
                self._sizeSP.hide()

        def _valueHasChanged(self, value):
            self.valueChanged.emit(value)

    class _RangeWidget(qt.QWidget):
        def __init__(self, parent):
            qt.QWidget.__init__(self, parent)
            self.setLayout(qt.QHBoxLayout())
            self._minLE = qt.QLineEdit(parent=self)
            self._minLE.setPlaceholderText("Start")
            self._maxLE = qt.QLineEdit(parent=self)
            self._maxLE.setPlaceholderText("Stop")
            self._stepLE = qt.QLineEdit(parent=self)
            self._stepLE.setPlaceholderText("Step")
            self._minLE.setValidator(qt.QDoubleValidator())
            self._maxLE.setValidator(qt.QDoubleValidator())
            validator = qt.QDoubleValidator()
            validator.setBottom(0)
            self._stepLE.setValidator(validator)
            self.layout().addWidget(self._minLE)
            self.layout().addWidget(self._maxLE)
            self.layout().addWidget(self._stepLE)

            self.layout().setContentsMargins(0, 0, 0, 0)

        @property
        def value(self):
            if self._minLE.text() != "" and self._maxLE.text():
                step = float(self._stepLE.text()) if self._stepLE.text() != "" else 0
                return [float(self._minLE.text()), float(self._maxLE.text()), step]
            else:
                return None

        def setValue(self, _range):
            """

            :param int or None _range
            """
            assert type(_range) is list
            self._minLE.setText(str(numpy.round(_range[0], 5)))
            self._maxLE.setText(str(numpy.round(_range[1], 5)))
            self._stepLE.setText(str(numpy.round(_range[2], 5)))
            self._minLE.setCursorPosition(0)
            self._maxLE.setCursorPosition(0)
            self._stepLE.setCursorPosition(0)

    def __init__(self, parent, table, row):
        """

        :param QTableWidget table: if has to be embed in a table the
                                           parent table
        :param int row: row position in the QTableWidget. Also used as ID
        """
        qt.QWidget.__init__(self, parent)
        Dimension.__init__(self, kind=DEFAULT_METADATA, name="")

        self.__metadata = None

        # axis
        self._axis = qt.QSpinBox(parent=self)
        self._axis.setMinimum(0)
        # kind
        self._kindCB = qt.QComboBox(parent=self)
        self._kindCB.setMinimumWidth(100)
        for _kindName in _METADATA_TYPES:
            self._kindCB.addItem(_kindName)
        # name
        self._namesCB = qt.QComboBox(parent=self)
        self._namesCB.setMinimumWidth(100)
        # size
        self._sizeWidget = self._SizeWidget(parent=self)
        self._sizeWidget.setMinimum(0)
        self._setSize(0)
        # range
        self._rangeWidget = self._RangeWidget(parent=self)
        self._rangeWidget.setMinimumWidth(100)
        self._rangeWidget.setMaximumWidth(200)
        # tolerance
        self._toleranceLE = qt.QLineEdit(parent=self)
        self._toleranceLE.setMaximumWidth(80)
        validator = qt.QDoubleValidator()
        validator.setBottom(0)
        self._toleranceLE.setValidator(validator)
        self._setTolerance(1e-9)
        # rm button
        style = qt.QApplication.style()
        icon = style.standardIcon(qt.QStyle.SP_BrowserStop)
        self._rmButton = qt.QPushButton(icon=icon, parent=self)
        icon = style.standardIcon(qt.QStyle.SP_FileDialogContentsView)
        self._infoButton = qt.QPushButton(icon=icon, parent=self)
        self._infoButton.hide()

        # connect Signal/slot
        self._rmButton.pressed.connect(self.remove)
        self._axis.valueChanged.connect(self._axisHasChanged)
        self._kindCB.currentIndexChanged.connect(self._dimHasChanged)
        self._sizeWidget.valueChanged.connect(self._dimHasChanged)
        self._namesCB.currentIndexChanged.connect(self._dimHasChanged)
        self._kindCB.currentIndexChanged.connect(self._updateNames)
        self._infoButton.pressed.connect(self.showUniqueNames)

        _callback = partial(self._sizeWidget.setValue, 0)
        self._toleranceLE.editingFinished.connect(_callback)

        # update values from `Dim` class
        self._kindCB.currentTextChanged.connect(self.set_kind)
        self._namesCB.currentTextChanged.connect(self.set_name)
        self._sizeWidget.valueChanged.connect(self.set_size)

        self.embedInTable(table=table, row=row)
        self.__row = row

    def _axisHasChanged(self, value):
        self.axisChanged.emit(self._row, value)

    def _dimHasChanged(self, *args, **kwargs):
        self.dimValueChanged.emit()

    def remove(self):
        self.removed.emit(self)

    def showUniqueNames(self):
        title = "%s - %s" % (_METADATA_TYPES_I[self.kind], self.name)
        if len(self.unique_values):
            total_range = max(self.unique_values) - min(self.unique_values)
            unique_values = ", ".join([str(val) for val in self.unique_values])
            msg = f"Unique values: [{unique_values}]\nTotal range: {total_range}"
            qt.QMessageBox.information(self, title, msg)
        else:
            qt.QMessageBox.information(self, title, "No values were found, try fitting")

    def setUniqueValues(self, values):
        super().set_unique_values(values)
        if values is None:
            self._infoButton.hide()
        else:
            self._infoButton.show()

    def setDim(self, dim):
        assert isinstance(dim, Dimension)
        _kind = _METADATA_TYPES_I[dim.kind]
        idx = self._kindCB.findText(_kind)
        assert idx >= 0
        self._kindCB.setCurrentIndex(idx)
        idx = self._namesCB.findText(dim.name)
        if idx >= 0:
            self._namesCB.setCurrentIndex(idx)
        else:
            self._namesCB.addItem(dim.name)
        if dim.size is not None:
            self._sizeWidget.setValue(dim.size)
        if dim.range is not None:
            self._rangeWidget.setValue(dim.range)
        self._setTolerance(str(dim.tolerance))
        self.setUniqueValues(dim.unique_values)

    @property
    def _row(self):
        return self.__row

    @property
    def axis(self):
        return self._axis.value()

    @axis.setter
    def axis(self, axis):
        assert type(axis) is int
        self._axis.setValue(axis)

    @property
    def kind(self):
        assert self._kindCB.currentText() in _METADATA_TYPES
        return _METADATA_TYPES[self._kindCB.currentText()]

    @property
    def dim(self):
        return Dimension(
            name=self.name,
            kind=self.kind,
            size=self.size,
            _range=self.range,
            tolerance=self.getTolerance(),
        )

    @property
    def size(self):
        return self._sizeWidget.value

    @property
    def range(self):
        return self._rangeWidget.value

    @property
    def name(self):
        return self._namesCB.currentText()

    @property
    def tolerance(self):
        return self.locale().toFloat(self._toleranceLE.text())[0]

    def _setSize(self, size):
        Dimension.set_size(self, size)
        self._sizeWidget.setValue(size=size)

    def _setRange(self, _range):
        Dimension.set_range(self, _range)
        self._rangeWidget.setValue(_range)

    def setNames(self, names):
        self._namesCB.clear()
        for name in sorted(list(names)):
            self._namesCB.addItem(name)

    def _setTolerance(self, tolerance):
        self._toleranceLE.setText(str(tolerance))

    def embedInTable(self, table, row):
        self.__row = row
        for column, widget in enumerate(
            (
                self._axis,
                self._kindCB,
                self._namesCB,
                self._sizeWidget,
                self._rangeWidget,
                self._toleranceLE,
                self._infoButton,
                self._rmButton,
            )
        ):
            table.setCellWidget(row, column, widget)

    def _updateNames(self, *args, **kwargs):
        """Update names for the current kind"""
        if self.__metadata is not None:
            _lastActiveName = self.name
            self.setNames(self.__metadata.get_keys(self.kind))
            idx = self._namesCB.findText(_lastActiveName)
            if idx >= 0:
                self._namesCB.setCurrentIndex(idx)

    def _setMetadata(self, metadata):
        self.__metadata = metadata
        self._updateNames()
