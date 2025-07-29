from __future__ import annotations

import logging

import numpy
from ewoksorange.gui.parameterform import block_signals
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D
from silx.gui.plot import StackView
from silx.image.marchingsquares import find_contours
from silx.io.dictdump import dicttonx

import darfix

from .. import dtypes
from ..core.dataset import Operation
from ..core.rocking_curves import MAPS_2D_FIT_INDICES
from ..core.rocking_curves import MAPS_FIT_INDICES
from ..core.rocking_curves import Maps
from ..core.rocking_curves import Maps_2D
from ..core.rocking_curves import fit_2d_rocking_curve
from ..core.rocking_curves import fit_rocking_curve
from ..core.rocking_curves import generate_rocking_curves_nxdict
from .utils.message import missing_dataset_msg

_logger = logging.getLogger(__file__)


class RockingCurvesWidget(qt.QMainWindow):
    """
    Widget to apply fit to a set of images and plot the amplitude, fwhm, peak position, background and residuals maps.
    """

    sigFitClicked = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self.dataset = None
        self.indices = None
        self._update_dataset = None
        self._residuals_cache = None
        self.maps = None

        widget = qt.QWidget(parent=self)
        layout = qt.QGridLayout()

        self._sv = StackView(parent=self, position=True)
        self._sv.setColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME))
        self._plot = Plot2D(parent=self)
        self._plot.setDefaultColormap(Colormap(name="cividis", normalization="linear"))
        self._plot.setGraphTitle("Rocking curves")
        self._plot.setGraphXLabel("Degrees")
        intLabel = qt.QLabel("Intensity threshold:")
        self._intThresh = "15"
        self._intThreshLE = qt.QLineEdit(self._intThresh)
        self._intThreshLE.setValidator(qt.QDoubleValidator())
        self._computeFit = qt.QPushButton("Fit data")
        self._computeFit.clicked.connect(self._grainPlot)
        self._fitMethodLabel = qt.QLabel("method")
        self._fitMethod = qt.QComboBox()
        self._fitMethod.addItems(("trf", "dogbox", "lm"))
        self._fitMethod.setItemData(
            self._fitMethod.findText("trf"),
            "Bounded - Trust Region Reflective algorithm, particularly suitable for large sparse problems with bounds. Generally robust method.",
        )
        self._fitMethod.setItemData(
            self._fitMethod.findText("dogbox"),
            "Bounded - dogleg algorithm with rectangular trust regions, typical use case is small problems with bounds. Not recommended for problems with rank-deficient Jacobian",
        )
        self._fitMethod.setItemData(
            self._fitMethod.findText("lm"),
            "Unbounded Levenberg-Marquardt algorithm as implemented in MINPACK. Doesn’t handle bounds and sparse Jacobians. Usually the most efficient method for small unconstrained problems.",
        )

        self._fitMethod.setCurrentText("lm")

        self._abortFit = qt.QPushButton("Abort")
        self._abortFit.clicked.connect(self.__abort)
        spacer1 = qt.QWidget(parent=self)
        spacer1.setLayout(qt.QVBoxLayout())
        spacer1.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self._motorValuesCheckbox = qt.QCheckBox("Use motor values")
        self._motorValuesCheckbox.setChecked(True)
        self._motorValuesCheckbox.stateChanged.connect(self._checkboxStateChanged)
        self._centerDataCheckbox = qt.QCheckBox("Center angle values")
        self._centerDataCheckbox.setEnabled(False)
        self._centerDataCheckbox.stateChanged.connect(self._checkboxStateChanged)
        self._parametersLabel = qt.QLabel("")
        self._plotMaps = Plot2D(self)
        self._plotMaps.setDefaultColormap(
            Colormap(name="cividis", normalization="linear")
        )
        self._plotMaps.hide()
        self._methodCB = qt.QComboBox(self)
        self._methodCB.hide()
        self._exportButton = qt.QPushButton("Export maps")
        self._exportButton.hide()
        self._exportButton.clicked.connect(self.exportMaps)

        layout.addWidget(self._sv, 0, 0, 1, 2)
        layout.addWidget(self._plot, 0, 2, 1, 3)
        layout.addWidget(self._parametersLabel, 1, 2, 1, 2)
        layout.addWidget(self._motorValuesCheckbox, 2, 2, 1, 1)
        layout.addWidget(self._centerDataCheckbox, 2, 3, 1, 1)
        layout.addWidget(intLabel, 3, 0, 1, 1)
        layout.addWidget(self._intThreshLE, 3, 1, 1, 1)
        layout.addWidget(self._computeFit, 3, 2, 1, 1)
        layout.addWidget(self._fitMethodLabel, 3, 3, 1, 1)
        layout.addWidget(self._fitMethod, 3, 4, 1, 1)
        layout.addWidget(self._abortFit, 3, 2, 1, 2)
        layout.addWidget(self._methodCB, 4, 0, 1, 4)
        layout.addWidget(self._plotMaps, 5, 0, 1, 4)
        layout.addWidget(self._exportButton, 6, 0, 1, 5)
        self._abortFit.hide()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # connect signal / slot
        self._methodCB.currentTextChanged.connect(self.__methodChanged)

    @staticmethod
    def get_item_text(item: Maps | Maps_2D, dataset: dtypes.ImageDataset) -> str:
        """
        Return the name to set for QCombobox text and user data
        """
        if item in (Maps_2D.FWHM_X, Maps_2D.PEAK_X):
            return f"{item.value} - ({dataset.dims.get(0).name})"
        elif item in (Maps_2D.FWHM_Y, Maps_2D.PEAK_Y):
            return f"{item.value} - ({dataset.dims.get(1).name})"
        else:
            return item.value

    def __methodChanged(self, *args, **kwargs):
        """callback when '_methodCB' text has changed"""
        if self.dataset is None:
            return
        elif self.dataset.dims.ndim == 2:
            self._update2DPlot(self._methodCB.currentData())
        else:
            self._updatePlot(self._methodCB.currentData())

    def setDataset(self, dataset: dtypes.Dataset):

        self.dataset = dataset.dataset
        self.indices = dataset.indices
        self._update_dataset = dataset.dataset
        self._residuals_cache = None
        self.setStack()
        self._methodCB.clear()
        with block_signals(self._methodCB):

            if self.dataset.dims.ndim == 2:
                for item in Maps_2D:
                    self._methodCB.addItem(
                        self.get_item_text(item, dataset=dataset.dataset), item
                    )
            else:
                for item in Maps:
                    self._methodCB.addItem(
                        self.get_item_text(item, dataset=dataset.dataset), item
                    )

        self._sv.getPlotWidget().sigPlotSignal.connect(self._mouseSignal)
        self._sv.sigFrameChanged.connect(self._addPoint)

        if self.dataset.title != "":
            self._sv.setTitleCallback(lambda idx: self.dataset.title)

    def setStack(self, dataset=None):
        """
        Sets new data to the stack.
        Mantains the current frame showed in the view.

        :param Dataset dataset: if not None, data set to the stack will be from the given dataset.
        """
        if dataset is None:
            dataset = self.dataset
        nframe = self._sv.getFrameNumber()
        if self.indices is None:
            self._sv.setStack(dataset.get_data() if dataset is not None else None)
        else:
            self._sv.setStack(
                dataset.get_data(self.indices) if dataset is not None else None
            )
        self._sv.setFrameNumber(nframe)

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

    def _mouseSignal(self, info):
        """
        Method called when a signal from the stack is called
        """
        if info["event"] == "mouseClicked":
            # In case the user has clicked on a pixel in the stack
            data = self.dataset.get_data(self.indices)
            px = info["x"]
            py = info["y"]
            # Show vertical and horizontal lines for clicked pixel
            self._sv.getPlotWidget().addCurve(
                (px, px), (0, data.shape[1]), legend="x", color="r"
            )
            self._sv.getPlotWidget().addCurve(
                (0, data.shape[2]), (py, py), legend="y", color="r"
            )
            self.plotRockingCurves(px, py)

    def _addPoint(self, i=None):
        """
        Slot to add curve for frame number in rocking curves plot.

        :param int i: frame number
        """
        xc = self._sv.getPlotWidget().getCurve("x")
        if xc:
            px = xc.getXData()[0]
            py = self._sv.getPlotWidget().getCurve("y").getYData()[0]
            self.plotRockingCurves(px, py)

    def _computeContours(self, image, origin=None, scale=None):
        polygons = []
        levels = []
        for i in numpy.linspace(numpy.min(image), numpy.max(image), 10):
            polygons.append(find_contours(image, i))
            levels.append(i)
        # xdim = self.dataset.dims.get(1)
        # ydim = self.dataset.dims.get(0)
        for ipolygon, polygon in enumerate(polygons):
            # iso contours
            for icontour, contour in enumerate(polygon):
                if len(contour) == 0:
                    continue
                # isClosed = numpy.allclose(contour[0], contour[-1])
                x = contour[:, 1]
                y = contour[:, 0]
                if scale is not None:
                    x *= scale[0]
                    y *= scale[1]
                    x += origin[0] + scale[0] / 2
                    y += origin[1] + scale[1] / 2
                legend = "poly{}.{}".format(icontour, ipolygon)
                self._plot.addCurve(
                    x=x,
                    y=y,
                    linestyle="-",
                    linewidth=2.0,
                    legend=legend,
                    resetzoom=False,
                    color="w",
                )

    def plotRockingCurves(self, px, py):
        """
        Plot rocking curves of data and fitted data at pixel (px, py).

        :param Data data: stack of images to plot
        :param px: x pixel
        :param py: y pixel
        """
        # Get rocking curves from data
        self._plot.clear()
        try:
            data = self.dataset.get_data(self.indices)
            if self.dataset.in_memory:
                y = data[:, int(py), int(px)]
            else:
                y = numpy.array([image[int(py), int(px)] for image in data])
        except IndexError:
            _logger.warning("Index out of bounds")
            return
        if self.dataset.dims.ndim == 2:
            image = numpy.zeros(self.dataset.nframes)
            image[self.indices] = y
            xdim = self.dataset.dims.get(1)
            ydim = self.dataset.dims.get(0)
            self._plot.remove(kind="curve")
            frameNumber = self._sv.getFrameNumber()
            x = [
                self.dataset.get_metadata_values(kind=ydim.kind, key=ydim.name),
                self.dataset.get_metadata_values(kind=xdim.kind, key=xdim.name),
            ]
            dotx = int(frameNumber / ydim.size)
            doty = frameNumber % ydim.size
            xscale = xdim.range[2]
            yscale = ydim.range[2]
            if self._motorValuesCheckbox.isChecked():
                origin = [xdim.range[0], ydim.range[0]]
                dotx = xdim.unique_values[dotx]
                doty = ydim.unique_values[doty]
            else:
                origin = (0.0, 0.0)
                if self._centerDataCheckbox.isChecked():
                    dotx -= int(xdim.size / 2)
                    doty -= int(ydim.size / 2)
                    origin = (
                        -xscale * int(xdim.size / 2),
                        -yscale * int(ydim.size / 2),
                    )
                dotx *= xscale
                doty *= yscale
            try:
                y_gauss, pars = fit_2d_rocking_curve(
                    (image, None), values=x, shape=(ydim.size, xdim.size)
                )
                if numpy.array_equal(y_gauss, image):
                    raise RuntimeError
                y_gauss = numpy.reshape(y_gauss, (xdim.size, ydim.size)).T
                self._computeContours(y_gauss, origin, (xscale, yscale))
                self._parametersLabel.setText(
                    "PEAK_X:{:.3f} PEAK_Y:{:.3f} FWHM_X:{:.3f} FWHM_Y:{:.3f} AMP:{:.3f} CORR:{:.3f} BG:{:.3f}".format(
                        *pars
                    )
                )
            except (TypeError, RuntimeError):
                y_gauss = y
                _logger.warning("Cannot fit")

            y = numpy.reshape(image, (xdim.size, ydim.size)).T
            self._plot.addImage(
                y,
                xlabel=xdim.name,
                ylabel=ydim.name,
                origin=origin,
                scale=(xscale, yscale),
            )
            self._plot.addCurve([dotx], [doty], symbol="o", legend="dot_o", color="b")
            self.x, self.x_gauss, self.y, self.y_gauss = x, x, y, y_gauss
        else:
            if self.dataset.dims.ndim == 0:
                x = numpy.arange(data.shape[0])
            else:
                dim = self.dataset.dims.get(0)
                if self._motorValuesCheckbox.isChecked():
                    x = numpy.array(
                        self.dataset.get_metadata_values(
                            kind=dim.kind, key=dim.name, indices=self.indices
                        )
                    )
                else:
                    scale = dim.range[2]
                    x = numpy.arange(data.shape[0]) * scale
                    if self._centerDataCheckbox.isChecked():
                        x -= int(dim.size / 2)

            if self._centerDataCheckbox.isChecked():
                middle = (float(x[-1]) - float(x[0])) / 2
                # x = numpy.linspace(-middle, middle, len(x))
                x -= float(x[0]) + middle
            # Show rocking curves and fitted curve into plot
            self._plot.clear()
            self._plot.addCurve(x, y, legend="data", color="b")
            i = self._sv.getFrameNumber()
            try:
                y_gauss, pars = fit_rocking_curve(
                    (numpy.array(y), None), values=x, num_points=1000
                )
                self._parametersLabel.setText(
                    "AMP:{:.3f} PEAK:{:.3f} FWHM:{:.3f} BG:{:.3f}".format(*pars)
                )
            except TypeError:
                y_gauss = y
                _logger.warning("Cannot fit")

            # Add curves (points) for stackview frame number
            self.x_gauss = numpy.linspace(x[0], x[-1], len(y_gauss))
            self._plot.addCurve(self.x_gauss, y_gauss, legend="fit", color="r")
            self._plot.addCurve([x[i]], [y[i]], symbol="o", legend="dot_o", color="b")
            i_gauss = i * int((len(y_gauss) - 1) / (len(x) - 1))
            self._plot.addCurve(
                [self.x_gauss[i_gauss]],
                [y_gauss[i_gauss]],
                symbol="o",
                legend="dot_fit",
                color="r",
            )
            self.x, self.y, self.y_gauss = x, y, y_gauss

    def _grainPlot(self):
        """
        Method called when button for computing fit is clicked
        """
        if self.dataset is None:
            missing_dataset_msg()
            return

        self._computeFit.hide()
        self._intThresh = self._intThreshLE.text()
        self.sigFitClicked.emit()
        # TODO: Abort button is not working
        # self._abortFit.show()

    def getResiduals(self) -> numpy.ndarray | None:
        if self.dataset is None:
            missing_dataset_msg()
            return

        if self._residuals_cache is not None:
            return self._residuals_cache

        self._residuals_cache = numpy.sqrt(
            numpy.subtract(
                self._update_dataset.zsum(self.indices), self.dataset.zsum(self.indices)
            )
            ** 2
        )
        return self._residuals_cache

    def _updatePlot(self, method):
        """
        Updates the plots with the chosen method
        """
        if method is None:
            return
        method = Maps(method)
        title = self.dataset.title
        if title != "":
            title += " - "
        maps_idx = MAPS_FIT_INDICES[method]
        if method == Maps.AMPLITUDE:
            self._plotMaps.setGraphTitle(title + Maps.AMPLITUDE.value)
            self._addImage(self.maps[maps_idx])
        elif method == Maps.FWHM:
            self._plotMaps.setGraphTitle(title + Maps.FWHM.value)
            self._addImage(self.maps[maps_idx])
        elif method == Maps.PEAK:
            com = self.maps[maps_idx]
            com[numpy.isnan(com)] = min(com[~numpy.isnan(com)])
            self._plotMaps.setGraphTitle(title + Maps.PEAK.value)
            self._addImage(com)
        elif method == Maps.BACKGROUND:
            self._plotMaps.setGraphTitle(title + Maps.BACKGROUND.value)
            self._addImage(self.maps[maps_idx])
        elif method == Maps.RESIDUALS:
            self._plotMaps.setGraphTitle(title + Maps.RESIDUALS.value)
            self._addImage(self.getResiduals())
        else:
            raise ValueError(f"Invalid map method ({method})")

    def _update2DPlot(self, method):
        """
        Updates the plots with the chosen method
        """
        method = Maps_2D(method)
        title = self.dataset.title
        if title != "":
            title += " - "
        maps_idx = MAPS_2D_FIT_INDICES.get(method, None)
        if method == Maps_2D.PEAK_X:
            com = self.maps[maps_idx]
            com[numpy.isnan(com)] = min(com[~numpy.isnan(com)])
            self._plotMaps.setGraphTitle(title + Maps_2D.PEAK_X.value)
            self._addImage(com)
        elif method == Maps_2D.PEAK_Y:
            com = self.maps[maps_idx]
            com[numpy.isnan(com)] = min(com[~numpy.isnan(com)])
            self._plotMaps.setGraphTitle(title + Maps_2D.PEAK_Y.value)
            self._addImage(com)
        elif method == Maps_2D.FWHM_X:
            self._plotMaps.setGraphTitle(title + Maps_2D.FWHM_X.value)
            self._addImage(self.maps[maps_idx])
        elif method == Maps_2D.FWHM_Y:
            self._plotMaps.setGraphTitle(title + Maps_2D.FWHM_Y.value)
            self._addImage(self.maps[maps_idx])
        elif method == Maps_2D.AMPLITUDE:
            self._plotMaps.setGraphTitle(title + Maps_2D.AMPLITUDE.value)
            self._addImage(self.maps[maps_idx])
        elif method == Maps_2D.CORRELATION:
            self._plotMaps.setGraphTitle(title + Maps_2D.CORRELATION.value)
            self._addImage(self.maps[maps_idx])
        elif method == Maps_2D.BACKGROUND:
            self._plotMaps.setGraphTitle(title + Maps_2D.BACKGROUND.value)
            self._addImage(self.maps[maps_idx])
        elif method == Maps_2D.RESIDUALS:
            self._plotMaps.setGraphTitle(title + Maps_2D.RESIDUALS.value)
            self._addImage(self.getResiduals())
        else:
            raise ValueError(f"Invalid map method ({method})")

    def __abort(self):
        self.abortClicked.emit()
        self._abortFit.setEnabled(False)
        self.dataset.stop_operation(Operation.FIT)

    def onFitFinished(self):
        self._abortFit.hide()
        self._computeFit.show()

    def updateDataset(self, dataset: dtypes.ImageDataset, maps: numpy.ndarray):
        self._update_dataset, self.maps = dataset, maps
        assert self._update_dataset is not None
        if self.dataset.dims.ndim == 2:
            self._update2DPlot(self._methodCB.currentData())
        else:
            self._updatePlot(self._methodCB.currentData())
        self._plotMaps.show()
        self._methodCB.show()
        self._exportButton.show()

    def _wholeStack(self):
        self.setStack(self.dataset)
        self._addPoint()

    def _checkboxStateChanged(self):
        """
        Update widgets linked to the checkbox state
        """
        self._centerDataCheckbox.setEnabled(not self._motorValuesCheckbox.isChecked())
        xc = self._sv.getPlotWidget().getCurve("x")
        if xc:
            px = xc.getXData()[0]
            py = self._sv.getPlotWidget().getCurve("y").getYData()[0]
            self.plotRockingCurves(px, py)
        if Maps(self._methodCB.currentData()) == Maps.PEAK:
            self._updatePlot(Maps.PEAK)

    @property
    def intThresh(self):
        return self._intThresh

    @intThresh.setter
    def intThresh(self, intThresh: str):
        self._intThresh = intThresh
        self._intThreshLE.setText(intThresh)

    def exportMaps(self):
        """
        Creates dictionary with maps information and exports it to a nexus file
        """
        if self.dataset is None or self.maps is None:
            missing_dataset_msg()
            return

        fileDialog = qt.QFileDialog()

        fileDialog.setFileMode(fileDialog.AnyFile)
        fileDialog.setAcceptMode(fileDialog.AcceptSave)
        fileDialog.setOption(fileDialog.DontUseNativeDialog)
        fileDialog.setDefaultSuffix(".h5")
        if fileDialog.exec():
            nxdict = generate_rocking_curves_nxdict(
                dataset=self.dataset,
                maps=self.maps,
                residuals=self.getResiduals(),
            )
            dicttonx(nxdict, fileDialog.selectedFiles()[0])

    def _addImage(self, image):
        if self.dataset.transformation is None:
            self._plotMaps.addImage(image, xlabel="pixels", ylabel="pixels")
            return
        if self.dataset.transformation.rotate:
            image = numpy.rot90(image, 3)
        self._plotMaps.addImage(
            image,
            origin=self.dataset.transformation.origin,
            scale=self.dataset.transformation.scale,
            xlabel=self.dataset.transformation.label,
            ylabel=self.dataset.transformation.label,
        )
