from __future__ import annotations

import os.path

from ewokscore import Task
from silx.io.dictdump import dicttonx

from ..core.rocking_curves import compute_residuals
from ..core.rocking_curves import generate_rocking_curves_nxdict
from ..dtypes import Dataset


class RockingCurves(
    Task,
    input_names=["dataset"],
    optional_input_names=["int_thresh", "method", "output_filename"],
    output_names=["dataset", "maps"],
):
    def run(self):
        input_dataset: Dataset = self.inputs.dataset
        int_thresh: float | None = (
            float(self.inputs.int_thresh) if self.inputs.int_thresh else None
        )
        method: str | None = self.get_input_value("method", None)
        default_filename = os.path.join(input_dataset.dataset._dir, "rocking_curves.h5")
        output_filename: str | None = self.get_input_value(
            "output_filename", default_filename
        )

        if output_filename and os.path.isfile(output_filename):
            raise OSError(
                f"""Cannot launch rocking curves fit: saving destination {output_filename} already exists.
                Change the `output_filename` input or set it to None to disable saving."""
            )

        dataset = input_dataset.dataset
        indices = input_dataset.indices
        new_image_dataset, maps = dataset.apply_fit(
            indices=indices, int_thresh=int_thresh, method=method
        )

        if output_filename is not None:
            nxdict = generate_rocking_curves_nxdict(
                new_image_dataset,
                maps,
                residuals=compute_residuals(new_image_dataset, dataset, indices),
            )
            dicttonx(nxdict, output_filename)

        self.outputs.dataset = Dataset(
            dataset=new_image_dataset,
            indices=indices,
            bg_indices=input_dataset.bg_indices,
            bg_dataset=input_dataset.bg_dataset,
        )
        self.outputs.maps = maps
