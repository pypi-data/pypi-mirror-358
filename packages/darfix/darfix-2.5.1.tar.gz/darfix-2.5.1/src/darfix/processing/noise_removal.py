import logging
import tempfile
import timeit

import h5py
import numpy as np
from silx.resources import ExternalResources

from darfix.core.data import Data
from darfix.core.data import DataUrl
from darfix.core.dataset import ImageDataset
from darfix.core.imageOperations import Method
from darfix.core.imageOperations import background_subtraction

_logger = logging.getLogger(__file__)


def apply_background_subtraction(
    output_dir: str, running_data: Data, method="median", chunks=True
):
    """
    Applies background subtraction to the data and saves the new data
    into disk.

    :param background: Data to be used as background. If None, data with indices `indices` is used.
        If Dataset, data of the dataset is used. If array, use data with indices in the array.
    :type background: Union[None, array_like, Dataset]
    :param method: Method to use to compute the background.
    :type method: Method
    :param indices: Indices of the images to apply background subtraction.
        If None, the background subtraction is applied to all the data.
    :type indices: Union[None, array_like]
    :param int step: Distance between images to be used when computing the median.
        Parameter used only when flag in_memory is False and method is `Method.median`.
        If `step` is not None, all images with distance of `step`, starting at 0,
        will be loaded into memory for computing the median, if the data loading throws
        a MemoryError, the median computation is tried with `step += 1`.
    :param chunk_shape: Shape of the chunk image to use per iteration.
        Parameter used only when flag in_memory is False and method is `Method.median`.
    :type chunk_shape: array_like
    :returns: dataset with data of same size as `self.data` but with the
        modified images. The urls of the modified images are replaced with
        the new urls.
    :rtype: Dataset
    """

    method = Method.from_value(method)

    data_filename = tempfile.mktemp(dir=output_dir, prefix="data_", suffix=".h5")

    with running_data.open_as_chuncked_hdf5(data_filename, True) as data_h5:
        for data_chuck in data_h5.iter_chunks():
            data_h5[data_chuck] = background_subtraction(
                data_h5[data_chuck], data_h5[data_chuck], method
            )
    return data_filename


def apply_dark_subtraction(
    output_dir: str,
    running_data: Data,
    dark_data: Data,
    method="median",
    chunks=True,
):
    method = Method.from_value(method)

    data_filename = tempfile.mktemp(dir=output_dir, prefix="data_", suffix=".h5")
    dark_filename = tempfile.mktemp(dir=output_dir, prefix="dark_", suffix=".h5")

    with running_data.open_as_chuncked_hdf5(data_filename, chunks) as data_h5:
        with dark_data.open_as_chuncked_hdf5(dark_filename, chunks) as dark_h5:
            for data_chuck, dark_chunck in zip(
                data_h5.iter_chunks(), dark_h5.iter_chunks()
            ):
                data_chuck[:] = background_subtraction(data_chuck, dark_chunck, method)
    return data_filename


def test2():
    dataset = ImageDataset(
        "result",
        in_memory=False,
        isH5=True,
        first_filename="silx:///home/ruyer/Downloads/input.h5?/2.1/measurement/my_detector",
        metadata_url=DataUrl(
            scheme="silx",
            file_path="/home/ruyer/Downloads/input.h5",
            data_path="/2.1/instrument/positioners",
            data_slice=None,
        ),
    )

    apply_background_subtraction("test", dataset.get_data())


test2()


def test1():
    dataset = ImageDataset(
        "result",
        in_memory=False,
        isH5=True,
        first_filename="silx:///home/ruyer/Downloads/input.h5?/2.1/measurement/my_detector",
        metadata_url=DataUrl(
            scheme="silx",
            file_path="/home/ruyer/Downloads/input.h5",
            data_path="/2.1/instrument/positioners",
            data_slice=None,
        ),
    )

    dataset.apply_background_subtraction()
