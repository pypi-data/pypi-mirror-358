from typing import Mapping

import numpy
from ewokscore import Task

from darfix import dtypes
from darfix.core.dataset import extract_metadata_values
from darfix.core.dimension import POSITIONER_METADATA
from darfix.core.dimension import AcquisitionDims


class DimensionDefinition(
    Task,
    input_names=[
        "dataset",
    ],
    optional_input_names=["dims", "tolerance", "metadata_type"],
    output_names=["dataset"],
):
    DEFAULT_TOLERANCE = 1e-9
    """
    Fit dimension of given dataset.
    If dims are provided then will use them. else will call 'find_dimensions' with the provided tolerance or the default one and with the
    provided metadata_type or the default one
    """

    def run(self):
        if not isinstance(self.inputs.dataset, dtypes.Dataset):
            raise TypeError(
                f"'dataset' input should be an instance of {dtypes.Dataset}. Got {type(self.inputs.dataset)}"
            )

        dataset = self.inputs.dataset.dataset
        if not isinstance(dataset, dtypes.ImageDataset):
            raise TypeError(
                f"self.inputs.dataset is expected to be an instance of {dtypes.ImageDataset}. Get {type(dataset)}"
            )

        # compute dims if not provided
        raw_dims = self.get_input_value("dims", None)
        if raw_dims is None:
            metadata_type = self.get_input_value("metadata_type", POSITIONER_METADATA)
            dims = self.find_dimensions(
                dataset=dataset,
                metadata_type=metadata_type,
                tolerance=self.get_input_value("tolerance", self.DEFAULT_TOLERANCE),
            )
        else:
            if not isinstance(raw_dims, dict):
                raise TypeError(f"dims should be a dictionary. Got {raw_dims}.")
            dims = {int(raw_axis): dim for raw_axis, dim in raw_dims.items()}

        if not isinstance(dims, Mapping):
            raise TypeError(
                f"self.inputs.dims is expected to be an instance of {Mapping}. Get {type(dims)}"
            )

        dataset.clear_dims()
        if len(dataset.data.metadata) > 0:
            for axis, dim in dims.items():
                assert type(axis) is int
                dataset.add_dim(axis=axis, dim=dim)
            try:
                dataset = dataset.reshape_data()
            except ValueError:
                for axis, dimension in dataset.dims.items():
                    values = dataset.get_dimensions_values()[dimension.name]
                    dimension.set_unique_values(numpy.unique(values))
                dataset = dataset.reshape_data()
            else:
                ndim = dataset.dims.ndim
                for axis, dimension in dataset.dims.items():
                    if dataset.dims.ndim > 1:
                        not_axis = ndim - axis - 1
                        metadata = numpy.swapaxes(
                            dataset.data.metadata, ndim - 1, not_axis
                        )
                        for axis in range(ndim - 1):
                            metadata = metadata[0]
                    else:
                        metadata = dataset.data.metadata

                    values = extract_metadata_values(
                        metadata,
                        dimension.kind,
                        dimension.name,
                        missing_value="0",
                        take_previous_when_missing=False,
                    )
                    dimension.set_unique_values(values)
                dataset = dataset.reshape_data()
        self.outputs.dataset = dtypes.Dataset(
            dataset=dataset,
            indices=self.inputs.dataset.indices,
            bg_indices=self.inputs.dataset.bg_indices,
            bg_dataset=self.inputs.dataset.bg_dataset,
        )

    @staticmethod
    def find_dimensions(
        dataset: dtypes.ImageDataset, tolerance: float, metadata_type
    ) -> AcquisitionDims:
        # FIXME: the find dimension is done within the dataset and `Dataset.find_dimensions` is already
        # setting those dimensions. The two should be decoupled.
        dataset.find_dimensions(
            kind=metadata_type,
            tolerance=tolerance,
        )
        return dataset.dims
