from __future__ import annotations

from typing import Sequence

from ewokscore import Task

from darfix.core.shiftcorrection import apply_shift
from darfix.dtypes import Dataset


class ShiftCorrection(
    Task,
    input_names=["dataset"],
    optional_input_names=["shift", "dimension"],
    output_names=["dataset"],
):
    def run(self):
        dataset: Dataset = self.inputs.dataset
        shift: Sequence[float] = self.get_input_value("shift", None)
        dimension: int | None = self.get_input_value("dimension", None)

        if shift is None:
            self.outputs.dataset = dataset
            return

        new_image_dataset = apply_shift(dataset, shift, dimension)

        self.outputs.dataset = Dataset(
            dataset=new_image_dataset,
            indices=dataset.indices,
            bg_indices=dataset.bg_indices,
            bg_dataset=dataset.bg_dataset,
        )
