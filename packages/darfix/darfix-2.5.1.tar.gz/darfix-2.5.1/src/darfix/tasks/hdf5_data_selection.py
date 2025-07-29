import logging
import os.path

from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from silx.io.url import DataUrl

from .. import dtypes
from ..core.data_selection import load_process_data
from ..core.datapathfinder import DETECTOR_KEYWORD
from ..core.datapathfinder import FIRST_SCAN_KEYWORD
from ..core.datapathfinder import SCAN_KEYWORD
from ..core.datapathfinder import DataPathFinder
from ..core.datapathfinder import get_first_group
from ..core.datapathfinder import get_last_group

_logger = logging.getLogger(__file__)


class HDF5DataSelection(
    Task,
    input_names=["raw_input_file"],
    optional_input_names=[
        "raw_detector_data_path",
        "raw_metadata_path",
        "dark_input_file",
        "dark_detector_data_path",
        "workflow_title",
        "in_memory",
        "treated_data_dir",
    ],
    output_names=[
        "dataset",
    ],
):

    DEFAULT_DETECTOR_DATA_PATH = FIRST_SCAN_KEYWORD + "/measurement/" + DETECTOR_KEYWORD

    DEFAULT_POSITIONERS_DATA_PATH = FIRST_SCAN_KEYWORD + "/instrument/positioners"

    def run(self):
        raw_detector_data_path = self.get_input_value(
            "raw_detector_data_path", self.DEFAULT_DETECTOR_DATA_PATH
        )
        # warning: convention. If the user want to skip loading metadata then he must provide an empty string ''
        raw_metadata_path = self.get_input_value(
            "raw_metadata_path", self.DEFAULT_POSITIONERS_DATA_PATH
        )
        # note on (raw_detector_data_path or "") like conditions: allows raw_detector_data_path to be None and do valid checks.
        dark_detector_data_path = self.get_input_value("dark_detector_data_path", None)
        has_scan_keyword = (
            SCAN_KEYWORD in (raw_detector_data_path or "")
            or SCAN_KEYWORD in (dark_detector_data_path or "")
            or SCAN_KEYWORD in (raw_metadata_path or "")
        )
        if has_scan_keyword:
            raise ValueError(
                f"Only one scan can be loaded at once with HDF5. The {SCAN_KEYWORD} keyword should therefore not be present in data paths."
            )
        if DETECTOR_KEYWORD in (raw_metadata_path or ""):
            raise ValueError(
                f"{DETECTOR_KEYWORD} keyword found in raw_metadata_path: it should only be used detector data paths since  raw_metadata_path is for positioners."
            )

        # solve raw data detector path if needed
        raw_data_det_solver = DataPathFinder(
            file_=self.inputs.raw_input_file,
            pattern=raw_detector_data_path,
        )
        first_scan = get_first_group(self.inputs.raw_input_file)
        last_scan = get_last_group(self.inputs.raw_input_file)
        raw_detector_data_path = raw_data_det_solver.format(
            scan=raw_detector_data_path, first_scan=first_scan, last_scan=last_scan
        )

        dark_input_file = self.get_input_value("dark_input_file", None)
        if dark_input_file is None and dark_detector_data_path is not None:
            raise ValueError(
                "data path provided for background but no file path given."
            )
        assert raw_detector_data_path is not None

        workflow_title = self.get_input_value("workflow_title", "")
        in_memory = self.get_input_value("in_memory", True)
        if dark_input_file:
            dark_detector_data_path = (
                dark_detector_data_path or self.DEFAULT_DETECTOR_DATA_PATH
            )
            # solve bg detector path if needed
            bg_data_det_solver = DataPathFinder(
                file_=dark_input_file, pattern=dark_detector_data_path
            )
            dark_detector_data_path = bg_data_det_solver.format(
                scan=dark_detector_data_path,
                first_scan=first_scan,
                last_scan=last_scan,
            )

            bg_data_url = DataUrl(
                file_path=dark_input_file,
                data_path=dark_detector_data_path,
                scheme="silx",
            )
        else:
            bg_data_url = None
        raw_data_url = DataUrl(
            file_path=self.inputs.raw_input_file,
            data_path=raw_detector_data_path,
            scheme="silx",
        )
        assert raw_detector_data_path is not None
        if raw_metadata_path in ("", None, MISSING_DATA):
            # convention for convenience. If a path is not provided then it will look at the
            # default location. If the user wants to skip loading metadata then they must provide an empty string
            metadata_url = None
        else:
            # solve metadata (positioners) path if needed
            metadata_solver = DataPathFinder(
                file_=self.inputs.raw_input_file, pattern=raw_metadata_path
            )
            raw_metadata_path = metadata_solver.format(
                scan=raw_metadata_path, first_scan=first_scan, last_scan=last_scan
            )
            metadata_url = DataUrl(
                file_path=self.inputs.raw_input_file,
                data_path=raw_metadata_path,
                scheme="silx",
            )

        treated_data_dir = self.get_input_value("treated_data_dir", None)
        # move output folder to 'PROCESSED_DATA' instead of 'RAW_DATA' when possible
        if treated_data_dir is None and "RAW_DATA" in raw_data_url.file_path():
            treated_data_dir = os.path.dirname(raw_data_url.file_path()).replace(
                "RAW_DATA", "PROCESSED_DATA"
            )
            _logger.warning(f"Treated data will be saved in {treated_data_dir}")

        dataset, indices, bg_indices, bg_dataset = load_process_data(
            filenames=raw_data_url.path(),
            root_dir=treated_data_dir,
            dark_filename=bg_data_url,
            in_memory=in_memory,
            copy_files=False,
            title=workflow_title,
            isH5=True,
            metadata_url=metadata_url,
        )

        self.outputs.dataset = dtypes.Dataset(
            dataset=dataset,
            indices=indices,
            bg_indices=bg_indices,
            bg_dataset=bg_dataset,
        )
