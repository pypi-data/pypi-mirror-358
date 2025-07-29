import os
import string

import h5py
import numpy
from ewokscore import Task

from darfix import dtypes


class WeakBeam(
    Task,
    input_names=["dataset", "nvalue"],
    optional_input_names=["nvalue", "indices", "title"],
    output_names=["dataset"],
):
    """
    Obtain dataset with filtered weak beam and recover its Center of Mass.
    Save file with this COM for further processing.
    """

    def run(self):
        dataset = self.inputs.dataset
        indices = self.get_input_value("indices", None)
        if isinstance(dataset, dtypes.Dataset):
            dataset = dataset.dataset
        if not isinstance(dataset, dtypes.ImageDataset):
            raise TypeError("dataset is expected to be an instance")

        nvalue = self.inputs.nvalue
        wb_dataset = dataset.recover_weak_beam(nvalue, indices=indices)
        com = wb_dataset.apply_moments(indices=indices)[0][0]
        os.makedirs(dataset.dir, exist_ok=True)
        filename = os.path.join(dataset.dir, "weakbeam_{}.hdf5".format(nvalue))

        title = self.get_input_value("title", "")
        # title can be set to None, MISSING_DATA or an empty string. So safer to use the following line
        title = title or self.get_random_title()
        with h5py.File(filename, "a") as _file:
            _file[title] = com

        self.outputs.dataset = dtypes.Dataset(
            dataset=dataset,
            indices=indices,
            bg_indices=self.inputs.dataset.bg_indices,
            bg_dataset=self.inputs.dataset.bg_dataset,
        )

    @staticmethod
    def get_random_title() -> str:
        letters = string.ascii_lowercase
        return "".join(numpy.random.choice(list(letters)) for i in range(6))
