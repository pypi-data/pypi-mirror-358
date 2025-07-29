from ewokscore import Task

from darfix import dtypes


class DataPartition(
    Task,
    input_names=[
        "dataset",
    ],
    optional_input_names=["bins", "filter_bottom_bin_idx", "filter_top_bin_idx"],
    output_names=["dataset"],
):
    """
    Filter frames with low intensity.
    """

    def run(self):
        dataset = self.inputs.dataset
        if not isinstance(dataset, dtypes.Dataset):
            raise TypeError(
                f"dataset is expected to be an instance of {dtypes.Dataset}. Got {type(dataset)}"
            )

        darfix_dataset = dataset.dataset

        indices, bg_indices = darfix_dataset.partition_by_intensity(
            bins=self.get_input_value("bins", None),
            bottom_bin=self.get_input_value("filter_bottom_bin_idx", None),
            top_bin=self.get_input_value("filter_top_bin_idx", None),
        )
        self.outputs.dataset = dtypes.Dataset(
            dataset=darfix_dataset,
            indices=indices,
            bg_indices=bg_indices,
            bg_dataset=dataset.bg_dataset,
        )
