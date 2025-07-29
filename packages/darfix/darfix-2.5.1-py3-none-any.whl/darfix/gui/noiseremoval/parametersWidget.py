from silx.gui import qt

from darfix.core.imageOperations import Method

_KERNEL_SIZES = (3, 5)


class ParametersWidget(qt.QWidget):
    def __init__(self, parent=None):
        """Widget containing the input parameters for the noise removal operations."""
        super().__init__(parent)
        self._layout = qt.QGridLayout()
        titleFont = qt.QFont()
        titleFont.setBold(True)

        # Background subtraction
        bsLabel = qt.QLabel("Background Subtraction")
        bsLabel.setFont(titleFont)
        self._layout.addWidget(bsLabel, 0, 0, 1, 2)
        self.bsMethodsCB = qt.QComboBox(self)
        for method in Method.values():
            self.bsMethodsCB.addItem(method)
        self.bsBackgroundCB = qt.QComboBox(self)
        self.computeBS = qt.QPushButton("Compute")
        methodLabel = qt.QLabel("Method:")
        bgLabel = qt.QLabel("Background:")
        methodLabel.setMargin(0)
        # Step widget
        # note: step wodget, ChunksWidget and ondist will be displayed if the dataset
        # has been loaded with the `on disk` option in "DataSelectionWidgetOW"
        self.stepWidget = qt.QWidget()
        stepLayout = qt.QHBoxLayout()
        stepLayout.addWidget(qt.QLabel("Step:"))
        self.step = qt.QLineEdit()
        self.step.setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Preferred)
        stepLayout.setContentsMargins(0, 0, 0, 0)
        stepLayout.addWidget(self.step)
        self.stepWidget.setLayout(stepLayout)
        # Chunks widget
        self.chunksWidget = qt.QWidget()
        chunksLayout = qt.QHBoxLayout()
        chunksLabel = qt.QLabel("Chunks:")
        self.verticalChunkSize = qt.QLineEdit()
        self.verticalChunkSize.setValidator(qt.QIntValidator())
        self.horizontalChunkSize = qt.QLineEdit()
        self.horizontalChunkSize.setValidator(qt.QIntValidator())
        chunksLayout.addWidget(chunksLabel)
        chunksLayout.addWidget(self.verticalChunkSize)
        chunksLayout.addWidget(self.horizontalChunkSize)
        chunksLayout.setContentsMargins(0, 0, 0, 0)
        self.chunksWidget.setLayout(chunksLayout)

        self.onDiskCheckbox = qt.QCheckBox("Use chunks to compute median")
        self.onDiskWidget = qt.QWidget()
        onDiskLayout = qt.QVBoxLayout()
        onDiskLayout.addWidget(self.stepWidget)
        onDiskLayout.addWidget(self.chunksWidget)
        onDiskLayout.addWidget(
            self.onDiskCheckbox, alignment=qt.Qt.AlignmentFlag.AlignRight
        )
        self.chunksWidget.hide()
        self.onDiskCheckbox.toggled.connect(self._toggleChunks)
        onDiskLayout.setContentsMargins(0, 0, 0, 0)
        self.onDiskWidget.setLayout(onDiskLayout)

        self._layout.addWidget(methodLabel, 1, 0, 1, 1)
        self._layout.addWidget(bgLabel, 2, 0, 1, 1)
        self._layout.addWidget(self.bsMethodsCB, 1, 1, 1, 1)
        self._layout.addWidget(self.bsBackgroundCB, 2, 1, 1, 1)
        self._layout.addWidget(self.onDiskWidget, 3, 0, 1, 2)
        self._layout.addWidget(self.computeBS, 4, 1, 1, 1)
        self.computeBS.hide()
        self.onDiskWidget.hide()

        # Hot pixel removal
        hpLabel = qt.QLabel("Hot Pixel Removal")
        hpLabel.setFont(titleFont)
        self._layout.addWidget(hpLabel, 0, 2, 1, 2)
        ksizeLabel = qt.QLabel("Kernel size:")
        self._layout.addWidget(ksizeLabel, 1, 2, 1, 1)
        self.hpSizeCB = qt.QComboBox(self)
        for size in _KERNEL_SIZES:
            self.hpSizeCB.addItem(str(size))
        self.computeHP = qt.QPushButton("Compute")
        self._layout.addWidget(self.hpSizeCB, 1, 3, 1, 1)
        self._layout.addWidget(self.computeHP, 4, 3, 1, 1)
        self.computeHP.hide()

        # Threshold removal
        tpLabel = qt.QLabel("Threshold Removal")
        tpLabel.setFont(titleFont)
        self._layout.addWidget(tpLabel, 0, 4, 1, 2)
        bottomLabel = qt.QLabel("Bottom threshold:")
        topLabel = qt.QLabel("Top threshold:")
        self._layout.addWidget(bottomLabel, 1, 4, 1, 1)
        self._layout.addWidget(topLabel, 2, 4, 1, 1)
        self.bottomLE = qt.QLineEdit()
        self.bottomLE.setValidator(qt.QIntValidator())
        self.bottomLE.setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Preferred)
        self.topLE = qt.QLineEdit()
        self.topLE.setValidator(qt.QIntValidator())
        self.topLE.setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Preferred)
        self.computeTP = qt.QPushButton("Compute")
        self._layout.addWidget(self.bottomLE, 1, 5, 1, 1)
        self._layout.addWidget(self.topLE, 2, 5, 1, 1)
        self._layout.addWidget(self.computeTP, 4, 5, 1, 1)
        self.computeTP.hide()

        # Mask removal
        mrLabel = qt.QLabel("Mask Removal")
        mrLabel.setFont(titleFont)
        self._layout.addWidget(mrLabel, 0, 6, 1, 2)
        maskLabel = qt.QLabel("Use mask from toolbox.\n Set values off mask to 0.")
        self.computeMR = qt.QPushButton("Compute")
        self._layout.addWidget(maskLabel, 1, 6, 1, 2)
        self._layout.addWidget(self.computeMR, 4, 7, 1, 1)
        self.computeMR.hide()

        self._layout.setHorizontalSpacing(10)
        self.setLayout(self._layout)
        self.set_default_values()

    def set_default_values(self):
        self.step.setText("1")
        self.verticalChunkSize.setText("100")
        self.horizontalChunkSize.setText("100")
        self.bottomLE.setText("0")
        self.topLE.setText("100")

    def _toggleChunks(self, checked: bool):
        if checked:
            self.chunksWidget.show()
            self.stepWidget.hide()
        else:
            self.chunksWidget.hide()
            self.stepWidget.show()
