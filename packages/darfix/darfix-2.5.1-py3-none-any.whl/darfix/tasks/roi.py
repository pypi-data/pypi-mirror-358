from __future__ import annotations

import logging

import numpy
from ewokscore import Task

from darfix.core.dataset import ImageDataset
from darfix.dtypes import Dataset

logger = logging.getLogger(__file__)


class RoiSelection(
    Task,
    input_names=["dataset"],
    optional_input_names=["roi_origin", "roi_size"],
    output_names=["dataset"],
):
    def run(self):
        input_dataset: Dataset = self.inputs.dataset
        dataset: ImageDataset = input_dataset.dataset
        bg_dataset: ImageDataset | None = input_dataset.bg_dataset

        origin: numpy.ndarray = numpy.flip(self.get_input_value("roi_origin", []))
        size: numpy.ndarray = numpy.flip(self.get_input_value("roi_size", []))

        if len(origin) == 0 or len(size) == 0:
            logger.warning(
                f"Cannot apply a ROI if origin ({origin}) or size ({size}) is empty. Dataset is unchanged."
            )
        else:
            dataset = dataset.apply_roi(origin=origin, size=size)
            if bg_dataset:
                bg_dataset = bg_dataset.apply_roi(origin=origin, size=size)
        self.outputs.dataset = Dataset(
            dataset=dataset,
            indices=input_dataset.indices,
            bg_indices=input_dataset.bg_indices,
            bg_dataset=bg_dataset,
        )
