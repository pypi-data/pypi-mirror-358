from __future__ import annotations

from ewokscore import Task

from darfix.dtypes import Dataset

from ..core.noiseremoval import NoiseRemovalOperation
from ..core.noiseremoval import apply_noise_removal_operation


class NoiseRemoval(
    Task,
    input_names=["dataset"],
    optional_input_names=["operations"],
    output_names=["dataset"],
):
    def run(self):
        input_dataset: Dataset = self.get_input_value("dataset")
        operations: list[NoiseRemovalOperation] = self.get_input_value("operations", [])

        dataset = input_dataset
        for operation in operations:
            new_darfix_dataset = apply_noise_removal_operation(dataset, operation)
            if new_darfix_dataset is None:
                continue

            dataset = Dataset(
                dataset=new_darfix_dataset,
                indices=input_dataset.indices,
                bg_dataset=input_dataset.bg_dataset,
                bg_indices=input_dataset.bg_indices,
            )

        self.outputs.dataset = dataset
