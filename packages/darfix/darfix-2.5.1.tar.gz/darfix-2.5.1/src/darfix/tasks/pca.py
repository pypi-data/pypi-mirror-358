from __future__ import annotations

from ewokscore import Task
from ewokscore.missing_data import is_missing_data

from darfix.dtypes import Dataset


class PCA(
    Task,
    input_names=["dataset"],
    optional_input_names=["num_components", "chunk_size"],
    output_names=["vals", "dataset"],
):
    def run(self):
        dataset = self.inputs.dataset
        if not isinstance(dataset, Dataset):
            raise TypeError(
                f"dataset is expected to be an instance of {Dataset}. Got {type(dataset)} instead"
            )
        num_components = self.get_input_value("num_components")
        chunk_size = self.get_input_value("chunk_size")

        pca_kwargs = {"return_vals": True, "indices": dataset.indices}
        if not is_missing_data(num_components):
            pca_kwargs["num_components"] = num_components

        if not is_missing_data(chunk_size):
            pca_kwargs["chunk_size"] = chunk_size

        vals = dataset.dataset.pca(**pca_kwargs)

        self.outputs.vals = vals
        self.outputs.dataset = Dataset(
            dataset=dataset.dataset,
            indices=dataset.indices,
            bg_dataset=dataset.bg_dataset,
            bg_indices=dataset.bg_indices,
        )
