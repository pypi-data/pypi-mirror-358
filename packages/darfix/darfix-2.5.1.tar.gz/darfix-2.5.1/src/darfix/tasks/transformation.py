from __future__ import annotations

from ewokscore import Task

from ..dtypes import Dataset
from ..pixel_sizes import PixelSize


class TransformationMatrixComputation(
    Task,
    input_names=["dataset"],
    optional_input_names=[
        "magnification",
        "pixelSize",
        "kind",
        "rotate",
        "orientation",
    ],
    output_names=["dataset"],
):
    """Computes transformation matrix and attach it to the dataset"""

    def run(self):
        input_dataset: Dataset = self.inputs.dataset
        if not isinstance(input_dataset, Dataset):
            raise TypeError(
                f"Dataset is expected to be an instance of {Dataset}. Got {type(input_dataset)} instead."
            )
        dataset = input_dataset.dataset

        if not dataset.dims.ndim:
            return input_dataset

        kind: str = self.get_input_value("kind", None)

        if kind:
            assert dataset.dims.ndim == 1, "Kind RSM can only be used for 1D datasets."

            pixelSize: str = self.get_input_value("pixelSize", None)
            rotate: bool = self.get_input_value("rotate", None)

            dataset.compute_transformation(
                PixelSize[pixelSize].value, kind="rsm", rotate=rotate
            )
        else:
            magnification: float = self.get_input_value("magnification", None)
            orientation: int = self.get_input_value("orientation", None)

            if orientation == -1 or orientation is None:
                dataset.compute_transformation(magnification)
            else:
                dataset.compute_transformation(
                    magnification, topography_orientation=orientation
                )

        self.outputs.dataset = Dataset(
            dataset=dataset,
            indices=input_dataset.indices,
            bg_indices=input_dataset.bg_indices,
            bg_dataset=input_dataset.bg_dataset,
        )
