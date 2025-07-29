from __future__ import annotations

from typing import Sequence

from ewokscore import Task

from ..dtypes import Dataset


class Projection(
    Task,
    input_names=["dataset", "dimension"],
    output_names=["dataset"],
):
    """
    Removes one dimension by projecting (summing) all images in this dimension.

    Details in https://gitlab.esrf.fr/XRD/darfix/-/issues/37
    """

    def run(self):
        dataset = self.inputs.dataset

        if not isinstance(dataset, Dataset):
            raise TypeError(
                f"dataset is expected to be an instance of {Dataset}. Got {type(dataset)}"
            )

        darfix_dataset = dataset.dataset
        indices = dataset.indices
        dimension: Sequence[int] = self.inputs.dimension

        darfix_dataset = darfix_dataset.project_data(
            dimension=dimension, indices=indices
        )

        self.outputs.dataset = Dataset(
            dataset=darfix_dataset,
            indices=indices,
            bg_indices=dataset.bg_indices,
            bg_dataset=dataset.bg_dataset,
        )
