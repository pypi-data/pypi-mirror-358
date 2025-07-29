from ewokscore import Task

from darfix import dtypes


class ZSum(
    Task,
    input_names=["dataset"],
    optional_input_names=["indices", "dimension"],
    output_names=["zsum"],
):

    def run(self):
        dataset = self.inputs.dataset
        if isinstance(dataset, dtypes.Dataset):
            dataset = dataset.dataset
        if not isinstance(dataset, dtypes.ImageDataset):
            raise TypeError(
                f"dataset is expected to be an instance of {dtypes.ImageDataset}. But get {type(dataset)}"
            )

        indices = self.get_input_value("indices", None)
        dimension = self.get_input_value("dimension", None)
        self.outputs.zsum = dataset.zsum(
            indices=indices,
            dimension=dimension,
        )
