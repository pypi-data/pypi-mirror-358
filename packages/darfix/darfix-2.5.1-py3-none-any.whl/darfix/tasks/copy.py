import copy

from ewokscore import Task

from darfix import dtypes


class DataCopy(
    Task,
    input_names=["dataset"],
    output_names=["dataset"],
):
    def run(self):
        dataset = self.inputs.dataset
        if not isinstance(dataset, dtypes.Dataset):
            raise dtypes.DatasetTypeError(dataset)
        self.outputs.dataset = dtypes.Dataset(
            dataset=copy.deepcopy(dataset.dataset),
            indices=copy.deepcopy(dataset.indices),
            bg_indices=copy.deepcopy(dataset.bg_indices),
            bg_dataset=copy.deepcopy(dataset.bg_dataset),
        )
