from ewokscore import Task

from darfix import dtypes
from darfix.core.data_selection import load_process_data


class EDFDataSelection(
    Task,
    input_names=[],
    optional_input_names=[
        "filenames",
        "root_dir",
        "in_memory",
        "dark_filename",
        "copy_files",
        "title",
        "raw_filename",
    ],
    output_names=["dataset"],
):
    """Loads data from a set of EDF files in a darfix Dataset"""

    def run(self):
        in_memory = self.get_input_value("in_memory", True)
        copy_files = self.get_input_value("copy_files", True)
        dark_filename = self.get_input_value("dark_filename", None)
        root_dir = self.get_input_value("root_dir", None)
        title = self.get_input_value("title", "")

        filenames = self.get_input_value("filenames", None)
        if filenames is None:
            filenames = self.get_input_value("raw_filename", None)
            if filenames is None:
                raise ValueError(
                    "Either 'filenames' or 'raw_filename' should be provided"
                )

        dataset, indices, bg_indices, bg_dataset = load_process_data(
            filenames=filenames,
            root_dir=root_dir,
            dark_filename=dark_filename,
            in_memory=in_memory,
            copy_files=copy_files,
            title=title,
            isH5=False,
        )
        self.outputs.dataset = dtypes.Dataset(
            dataset=dataset,
            indices=indices,
            bg_indices=bg_indices,
            bg_dataset=bg_dataset,
        )
