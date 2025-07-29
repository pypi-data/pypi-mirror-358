import os

import h5py
import numpy
from silx.io.url import DataUrl

import darfix.resources.tests
from darfix.core.dataset import ImageDataset
from darfix.core.dimension import POSITIONER_METADATA
from darfix.core.dimension import Dimension
from darfix.dtypes import Dataset


def test_add_one_dimension(in_memory_dataset, on_disk_dataset):
    """Tests the correct add of a dimension"""

    dimension = Dimension(POSITIONER_METADATA, "test", 20)
    # In memory
    in_memory_dataset.add_dim(0, dimension)
    saved_dimension = in_memory_dataset.dims.get(0)
    assert saved_dimension.name == "test"
    assert saved_dimension.kind == POSITIONER_METADATA
    assert saved_dimension.size == 20

    # On disk
    on_disk_dataset.add_dim(0, dimension)
    saved_dimension = on_disk_dataset.dims.get(0)
    assert saved_dimension.name == "test"
    assert saved_dimension.kind == POSITIONER_METADATA
    assert saved_dimension.size == 20


def test_add_several_dimensions(in_memory_dataset, on_disk_dataset):
    """Tests the correct add of several dimensions"""

    dimension1 = Dimension(POSITIONER_METADATA, "test1", 20)
    dimension2 = Dimension(POSITIONER_METADATA, "test2", 30)
    dimension3 = Dimension(POSITIONER_METADATA, "test3", 40)

    # In memory
    in_memory_dataset.add_dim(0, dimension1)
    in_memory_dataset.add_dim(1, dimension2)
    in_memory_dataset.add_dim(2, dimension3)
    assert in_memory_dataset.dims.ndim == 3

    # On disk
    on_disk_dataset.add_dim(0, dimension1)
    on_disk_dataset.add_dim(1, dimension2)
    on_disk_dataset.add_dim(2, dimension3)
    assert on_disk_dataset.dims.ndim == 3


def test_remove_dimension(in_memory_dataset, on_disk_dataset):
    """Tests the correct removal of a dimension"""

    dimension = Dimension(POSITIONER_METADATA, "test", 20)

    # In memory
    in_memory_dataset.add_dim(0, dimension)
    in_memory_dataset.remove_dim(0)
    assert in_memory_dataset.dims.ndim == 0

    # On disk
    on_disk_dataset.add_dim(0, dimension)
    on_disk_dataset.remove_dim(0)
    assert on_disk_dataset.dims.ndim == 0


def test_remove_dimensions(in_memory_dataset, on_disk_dataset):
    """Tests the correct removal of several dimensions"""

    dimension1 = Dimension(POSITIONER_METADATA, "test1", 20)
    dimension2 = Dimension(POSITIONER_METADATA, "test2", 30)
    dimension3 = Dimension(POSITIONER_METADATA, "test3", 40)

    # In memory
    in_memory_dataset.add_dim(0, dimension1)
    in_memory_dataset.add_dim(1, dimension2)
    in_memory_dataset.add_dim(2, dimension3)
    in_memory_dataset.remove_dim(0)
    in_memory_dataset.remove_dim(2)
    assert in_memory_dataset.dims.ndim == 1
    assert in_memory_dataset.dims.get(1).name == "test2"

    # On disk
    on_disk_dataset.add_dim(0, dimension1)
    on_disk_dataset.add_dim(1, dimension2)
    on_disk_dataset.add_dim(2, dimension3)
    on_disk_dataset.remove_dim(0)
    on_disk_dataset.remove_dim(2)
    assert on_disk_dataset.dims.ndim == 1
    assert on_disk_dataset.dims.get(1).name == "test2"


def test_find_dimensions(in_memory_dataset, on_disk_dataset):
    """Tests the correct finding of the dimensions"""

    # In memory
    in_memory_dataset.find_dimensions(POSITIONER_METADATA)
    assert in_memory_dataset.dims.ndim == 3
    assert in_memory_dataset.dims.get(0).name == "m"
    assert in_memory_dataset.dims.get(1).name == "z"
    assert in_memory_dataset.dims.get(2).name == "obpitch"

    # On disk
    on_disk_dataset.find_dimensions(POSITIONER_METADATA)
    assert on_disk_dataset.dims.ndim == 3
    assert on_disk_dataset.dims.get(0).name == "m"
    assert on_disk_dataset.dims.get(1).name == "z"
    assert on_disk_dataset.dims.get(2).name == "obpitch"


def test_clear_dimensions(in_memory_dataset, on_disk_dataset):
    """Tests the clear dimensions function"""

    # In memory
    in_memory_dataset.find_dimensions(POSITIONER_METADATA)
    in_memory_dataset.clear_dims()
    assert in_memory_dataset.dims.ndim == 0

    # On disk
    on_disk_dataset.find_dimensions(POSITIONER_METADATA)
    on_disk_dataset.clear_dims()
    assert on_disk_dataset.dims.ndim == 0


def test_find_dimension_silicon_111_reflection(tmp_path, resource_files):
    """
    Test 'find_dimension' with a bunch of motor position over a real use cases that used to bring troubles.
    """
    silicon_111_reflection_file = resource_files(darfix.resources.tests).joinpath(
        os.path.join("dimensions_definition", "silicon_111_reflection.h5")
    )

    raw_motor_values = {}
    with h5py.File(silicon_111_reflection_file, mode="r") as h5f:
        raw_motor_values["chi"] = h5f["positioners/chi"][()]
        raw_motor_values["mu"] = h5f["positioners/mu"][()]

    data_folder = tmp_path / "test_fitting"
    data_folder.mkdir()
    data_file_url = DataUrl(
        file_path=os.path.join(str(data_folder), "data.h5"),
        data_path="data",
        scheme="silx",
    )
    number_of_points = 1891
    with h5py.File(data_file_url.file_path(), mode="w") as h5f:
        h5f["data"] = numpy.random.random(number_of_points)

    dataset = Dataset(
        dataset=ImageDataset(
            first_filename=data_file_url.path(),
            metadata_url=DataUrl(
                file_path=str(silicon_111_reflection_file),
                data_path="positioners",
                scheme="silx",
            ).path(),
            isH5=True,
            _dir=None,
            in_memory=False,
        )
    )
    image_dataset = dataset.dataset

    # with a tolerance of 10e-9 we won't find 1081 steps over 2 dimensions
    assert len(image_dataset.dims) == 0
    image_dataset.find_dimensions(kind=None, tolerance=1e-9)
    assert len(image_dataset.dims) == 2
    assert (
        numpy.prod([val.size for val in image_dataset.dims.values()]) > number_of_points
    )

    image_dataset.clear_dims()
    image_dataset.find_dimensions(kind=None, tolerance=1e-5)
    assert (
        numpy.prod([val.size for val in image_dataset.dims.values()])
        == number_of_points
    )
    for dim in image_dataset.dims.values():
        numpy.testing.assert_almost_equal(
            dim.range[0], min(raw_motor_values[dim.name]), decimal=3
        )
        numpy.testing.assert_almost_equal(
            dim.range[1], max(raw_motor_values[dim.name]), decimal=3
        )


def test_find_dimension_NiTi_1PD_002_g411_420MPa_mosalayers_2x(
    tmp_path, resource_files
):
    """
    Test 'find_dimension' with a bunch of motor position over a real use cases that used to bring troubles.
    """
    dataset_file = resource_files(darfix.resources.tests).joinpath(
        os.path.join(
            "dimensions_definition", "NiTi_1PD_002_g411_420MPa_mosalayers_2x.h5"
        )
    )

    raw_motor_values = {}
    with h5py.File(dataset_file, mode="r") as h5f:
        raw_motor_values["chi"] = h5f["positioners/chi"][()]
        raw_motor_values["diffry"] = h5f["positioners/diffry"][()]
        raw_motor_values["difftz"] = h5f["positioners/difftz"][()]

    data_folder = tmp_path / "test_fitting"
    data_folder.mkdir()
    data_file_url = DataUrl(
        file_path=os.path.join(str(data_folder), "data.h5"),
        data_path="data",
        scheme="silx",
    )
    number_of_points = 31500
    with h5py.File(data_file_url.file_path(), mode="w") as h5f:
        h5f["data"] = numpy.random.random(number_of_points)

    dataset = Dataset(
        dataset=ImageDataset(
            first_filename=data_file_url.path(),
            metadata_url=DataUrl(
                file_path=str(dataset_file),
                data_path="positioners",
                scheme="silx",
            ).path(),
            isH5=True,
            _dir=None,
            in_memory=False,
        )
    )
    image_dataset = dataset.dataset

    def check_dimensions_bounds(dims: dict):
        """Make sure find_dimension is correctly fitting motor bounds"""
        for dim in dims.values():
            numpy.testing.assert_almost_equal(
                dim.range[0], min(raw_motor_values[dim.name]), decimal=3
            )
            numpy.testing.assert_almost_equal(
                dim.range[1], max(raw_motor_values[dim.name]), decimal=3
            )

    # with a tolerance of 10e-9 we won't find 1081 steps over 2 dimensions
    assert len(image_dataset.dims) == 0
    image_dataset.find_dimensions(kind=None, tolerance=1e-5)
    assert len(image_dataset.dims) == 3
    check_dimensions_bounds(dims=image_dataset.dims)
    assert (
        numpy.prod([val.size for val in image_dataset.dims.values()]) > number_of_points
    )

    image_dataset.clear_dims()
    image_dataset.find_dimensions(kind=None, tolerance=1e-4)
    assert len(image_dataset.dims) == 3
    check_dimensions_bounds(dims=image_dataset.dims)
    assert (
        numpy.prod([val.size for val in image_dataset.dims.values()])
        == number_of_points
    )
