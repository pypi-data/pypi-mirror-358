import os

import h5py
import numpy
import pytest
from ewoksorange.tests.conftest import qtapp  # noqa F401

from darfix.dtypes import Dataset
from darfix.gui.data_selection.hdf5 import HDF5RawDatasetSelectionWidget
from darfix.gui.utils.qsignalspy import QSignalSpy
from orangecontrib.darfix.widgets.hdf5dataselection import HDF5DataSelectionWidgetOW


@pytest.mark.skipif(QSignalSpy is None, reason="Unable to import QSignalSpy")
def test_HDF5DataSelectionWidgetOW(tmp_path, qtapp):  # noqa F811
    """
    test the HDF5ataSelectionWidgetOW
    """
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()

    raw_data_file = os.path.join(raw_data_dir, "raw.hdf5")
    with h5py.File(raw_data_file, mode="w") as h5f:
        h5f["/path/to/data"] = numpy.arange(0, 100 * 100 * 20).reshape(20, 100, 100)

    window = HDF5DataSelectionWidgetOW()
    widget = window._window._mainWidget._rawDataWidget
    assert isinstance(widget, HDF5RawDatasetSelectionWidget)
    widget.setInputFile(raw_data_file)
    expected_inputs = {
        "raw_input_file": raw_data_file,
        "raw_detector_data_path": "{first_scan}/measurement/{detector}",
        "raw_metadata_path": "{first_scan}/instrument/positioners",
        "workflow_title": "",
        "in_memory": True,
    }
    assert window.get_task_input_values() == expected_inputs

    widget.getDetectorDataPathSelection().setPattern("/path/to/data")
    expected_inputs["raw_detector_data_path"] = "/path/to/data"
    assert window.get_task_input_values() == expected_inputs

    # this was one of the API question. What to provide if
    # the user don't want to load metadata (like for dark).
    # We went for an empty string "". Because from the task class
    # point of view the most common would be to use the default pattern.
    expected_inputs["raw_metadata_path"] = ""
    widget.getMetadataPathSelection().setPattern("")
    assert window.get_task_input_values() == expected_inputs

    expected_inputs["workflow_title"] = "my workflow title"
    widget.setWorkflowTitle("my workflow title")
    assert window.get_task_input_values() == expected_inputs

    expected_inputs["in_memory"] = False
    widget.setKeepDataOnDisk(True)
    assert window.get_task_input_values() == expected_inputs

    assert window.task_succeeded is None

    waiter = QSignalSpy(window.task_executor.finished)
    window.execute_ewoks_task()
    # wait for the task_executor to be finished
    waiter.wait(5000)

    dataset = window.get_task_output_value("dataset")
    assert isinstance(dataset, Dataset)
