import pytest
from silx.io.url import DataUrl

from ..core.data_selection import load_process_data
from . import utils


@pytest.fixture(scope="session")
def resource_files():
    try:
        from importlib.resources import files
    except ImportError:
        from importlib_resources import files

    return files


@pytest.fixture
def in_memory_dataset(tmpdir):
    return utils.create_3motors_dataset(
        dir=tmpdir,
        in_memory=True,
        backend="edf",
    )


@pytest.fixture
def on_disk_dataset(tmpdir):
    return utils.create_3motors_dataset(
        dir=tmpdir,
        in_memory=False,
        backend="edf",
    )


@pytest.fixture
def input_dataset(tmp_path):
    input_filename = utils.get_external_input_file(str(tmp_path))

    detector_url = DataUrl(
        file_path=input_filename, data_path="/2.1/measurement/my_detector"
    )
    metadata_url = DataUrl(
        file_path=input_filename, data_path="/2.1/instrument/positioners"
    )

    dataset, _, _, _ = load_process_data(
        filenames=detector_url.path(),
        root_dir=tmp_path,
        in_memory=True,
        copy_files=False,
        title="input",
        isH5=True,
        metadata_url=metadata_url,
    )
    return dataset
