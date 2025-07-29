__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "26/04/2021"

import logging

import numpy
import silx
from packaging.version import Version
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.items.roi import RectangleROI
from silx.gui.plot.StackView import StackViewMainWindow
from silx.gui.plot.tools.roi import RegionOfInterestManager

import darfix
from darfix import dtypes
from darfix.core.data import Operation
from darfix.gui.utils.message import missing_dataset_msg

from .operationThread import OperationThread
from .roiLimitsToolbar import RoiLimitsToolBar

_logger = logging.getLogger(__file__)


class ROISelectionWidget(qt.QWidget):
    """
    Widget that allows the user to pick a ROI in any image of the dataset.
    """

    sigComputed = qt.Signal(list, list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._update_dataset = None
        self.indices = None
        self.bg_indices = None
        self.bg_dataset = None
        self._original_dataset = True
        self._dataset = None

        self.setLayout(qt.QVBoxLayout())
        self._sv = StackViewMainWindow()
        _buttons = qt.QDialogButtonBox(parent=self)

        self._okB = _buttons.addButton(_buttons.Ok)
        self._applyB = _buttons.addButton(_buttons.Apply)
        self._abortB = _buttons.addButton(_buttons.Abort)
        self._resetB = _buttons.addButton(_buttons.Reset)
        self._okB.setDefault(False)
        self._abortB.hide()

        self._applyB.clicked.connect(self.applyRoi)
        self._okB.clicked.connect(self.apply)
        self._resetB.clicked.connect(self.resetStack)
        self._abortB.clicked.connect(self.abort)

        self._sv.setColormap(
            Colormap(
                name=darfix.config.DEFAULT_COLORMAP_NAME,
                normalization=darfix.config.DEFAULT_COLORMAP_NORM,
            )
        )
        self.layout().addWidget(self._sv)
        self.layout().addWidget(_buttons)

        if Version(silx.version) < Version("2.0.0"):
            plot = self._sv.getPlot()
        else:
            plot = self._sv.getPlotWidget()

        self._roiManager = RegionOfInterestManager(plot)

        self._appliedRoi = None
        self._userRoi = RectangleROI()
        if Version(silx.version) < Version("2.0.0"):
            self._userRoi.setLabel("ROI")
        else:
            self._userRoi.setText("ROI")
        self._userRoi.setGeometry(origin=(0, 0), size=(10, 10))
        self._userRoi.setEditable(True)
        self._roiManager.addRoi(self._userRoi)

        self._roiToolBar = RoiLimitsToolBar(roiManager=self._roiManager)
        self._sv.addToolBar(qt.Qt.BottomToolBarArea, self._roiToolBar)

    def setDataset(self, dataset: dtypes.Dataset):
        """Saves the dataset and updates the stack with the dataset data."""
        self._dataset = dataset.dataset
        self._update_dataset = dataset.dataset
        self.indices = dataset.indices
        self._original_dataset = True
        if self._dataset.title != "":
            self._sv.setTitleCallback(lambda idx: self._dataset.title)
        self._roiOnNewDataset(self._dataset)
        self.setStack()
        self.bg_indices = dataset.bg_indices
        self.bg_dataset = dataset.bg_dataset

    def _roiOnNewDataset(self, dataset):
        self._appliedRoi = None
        self._userRoi.setVisible(True)
        first_frame_shape = dataset.get_data()[0].shape
        if first_frame_shape != tuple(self._userRoi.getSize()):
            center = first_frame_shape[1] // 2, first_frame_shape[0] // 2
            size = first_frame_shape[1] // 5, first_frame_shape[0] // 5
            self.setRoi(center=center, size=size)

    def setStack(self, dataset=None):
        """
        Sets new data to the stack.
        Mantains the current frame showed in the view.

        :param Dataset dataset: if not None, data set to the stack will be from the given dataset.
        """
        if dataset is None:
            dataset = self._dataset
        nframe = self._sv.getFrameNumber()
        self._sv.setStack(dataset.get_data())
        self._sv.setFrameNumber(nframe)

    def setRoi(self, roi=None, origin=None, size=None, center=None):
        """
        Sets a region of interest of the stack of images.

        :param RectangleROI roi: A region of interest.
        :param Tuple origin: If a roi is not provided, used as an origin for the roi
        :param Tuple size: If a roi is not provided, used as a size for the roi.
        :param Tuple center: If a roi is not provided, used as a center for the roi.
        """
        if roi is not None and (
            size is not None or center is not None or origin is not None
        ):
            _logger.warning(
                "Only using provided roi, the rest of parameters are omitted"
            )

        if roi is not None:
            self._userRoi = roi
        else:
            self._userRoi.setGeometry(origin=origin, size=size, center=center)

    def getRoi(self):
        """
        Returns the roi selected in the stackview.

        :rtype: silx.gui.plot.items.roi.RectangleROI
        """
        return self._userRoi

    def applyRoi(self):
        """
        Function to apply the region of interest at the data of the dataset
        and show the new data in the stack. Dataset data is not yet replaced.
        A new roi is created in the middle of the new stack.
        """
        if self._dataset is None:
            missing_dataset_msg()
            return

        if not self._update_dataset.in_memory:
            self._abortB.show()
        self._applyB.setEnabled(False)
        self._okB.setEnabled(False)
        self._appliedRoi = RectangleROI()
        self._appliedRoi.setGeometry(
            origin=self.getRoi().getOrigin(), size=self.getRoi().getSize()
        )
        self.thread = OperationThread(self, self._update_dataset.apply_roi)
        roi_dir = self._update_dataset.dir if not self._original_dataset else None
        self.thread.setArgs(
            size=numpy.flip(self._appliedRoi.getSize()),
            center=numpy.flip(self._appliedRoi.getCenter()),
            roi_dir=roi_dir,
        )
        self.thread.finished.connect(self._updateData)
        self.thread.start()

    def abort(self):
        self._abortB.setEnabled(False)
        self._update_dataset.stop_operation(Operation.ROI)

    def _updateData(self):
        """
        Updates the stack with the data computed in the thread
        """
        self.thread.finished.disconnect(self._updateData)
        self._abortB.hide()
        self._abortB.setEnabled(True)
        self._applyB.setEnabled(True)
        self._okB.setEnabled(True)
        if self.thread.data:
            self._update_dataset = self.thread.data
            self.thread.func = None
            self.thread.data = None
            self._original_dataset = False
            assert self._update_dataset is not None
            self.setStack(self._update_dataset)
            self._userRoi.setVisible(False)
        else:
            print("\nCorrection aborted")

    def setVisible(self, visible):
        super().setVisible(visible)  # sets okB as default
        self._okB.setDefault(False)

    def apply(self):
        """
        Function that replaces the dataset data with the data shown in the stack of images.
        If the stack has a roi applied, it applies the same roi to the dark frames of the dataset.
        Signal emitted with the roi parameters.
        """
        if self._appliedRoi:
            self.sigComputed.emit(
                self._appliedRoi.getOrigin().tolist(),
                self._appliedRoi.getSize().tolist(),
            )
        else:
            self.sigComputed.emit([], [])

    def getDataset(self) -> dtypes.Dataset:
        if self._appliedRoi:
            bg_dataset = (
                self.bg_dataset.apply_roi(
                    size=numpy.flip(self._appliedRoi.getSize()),
                    center=numpy.flip(self._appliedRoi.getCenter()),
                )
                if self.bg_dataset is not None
                else None
            )
        else:
            bg_dataset = self.bg_dataset
        return dtypes.Dataset(
            dataset=self._update_dataset,
            indices=self.indices,
            bg_indices=self.bg_indices,
            bg_dataset=bg_dataset,
        )

    def getStackViewColormap(self):
        """
        Returns the colormap from the stackView

        :rtype: silx.gui.colors.Colormap
        """
        return self._sv.getColormap()

    def setStackViewColormap(self, colormap):
        """
        Sets the stackView colormap

        :param colormap: Colormap to set
        :type colormap: silx.gui.colors.Colormap
        """
        self._sv.setColormap(colormap)

    def resetStack(self):
        """
        Restores stack with the dataset data.
        """
        self._appliedRoi = None
        self._userRoi.setVisible(True)
        self._update_dataset = self._dataset
        self._original_dataset = True
        self.setStack(self._dataset)

    def clearStack(self):
        """
        Clears stack.
        """
        self._sv.setStack(None)
        self._userRoi.setGeometry(origin=(0, 0), size=(10, 10))
