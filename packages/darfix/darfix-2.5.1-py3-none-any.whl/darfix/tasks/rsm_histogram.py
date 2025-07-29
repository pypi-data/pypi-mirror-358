from __future__ import annotations

from ewokscore import Task

from ..dtypes import Dataset
from ..math import Vector3D
from ..pixel_sizes import PixelSize


class RSMHistogram(
    Task,
    input_names=["dataset", "Q", "a", "map_range", "detector"],
    optional_input_names=[
        "units",
        "n",
        "map_shape",
        "energy",
    ],
    output_names=["hist_values", "hist_edges"],
):
    """Computes Reciprocal Space Map histogram."""

    def run(self):
        input_dataset = self.inputs.dataset
        if not isinstance(input_dataset, Dataset):
            raise TypeError(
                f"dataset is expected to be an instance of Dataset. Got {type(input_dataset)}."
            )
        dataset = input_dataset.dataset

        units: str | None = self.get_input_value("units", None)
        n: Vector3D | None = self.get_input_value("n", None)
        map_shape: Vector3D | None = self.get_input_value("map_shape", None)
        energy: float | None = self.get_input_value("energy", None)

        values, edges = dataset.compute_rsm(
            Q=self.inputs.Q,
            a=self.inputs.a,
            map_range=self.inputs.map_range,
            pixel_size=PixelSize[self.inputs.detector].value,
            units=units.lower() if units else None,
            n=n,
            map_shape=map_shape,
            energy=energy,
        )

        self.outputs.hist_values = values
        self.outputs.hist_edges = edges
