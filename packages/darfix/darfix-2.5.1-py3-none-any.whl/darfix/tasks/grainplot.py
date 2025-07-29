import logging
import os

from ewokscore import Task
from silx.io.dictdump import dicttonx

from .. import dtypes
from ..core.dataset import ImageDataset
from ..core.grainplot import OrientationDistImage
from ..core.grainplot import compute_mosaicity
from ..core.grainplot import compute_orientation_dist_data
from ..core.grainplot import generate_grain_maps_nxdict
from ..core.grainplot import get_image_parameters

_logger = logging.getLogger(__file__)


class GrainPlot(
    Task,
    input_names=["dataset"],
    optional_input_names=[
        "filename",
        "dimensions",
        "third_motor",
        "save_maps",
        "orientation_img_origin",
    ],
    output_names=["dataset"],
):
    """Generates and saves maps of Center of Mass, FWHM, Skewness, Kurtosis, Orientation distribution and Mosaicity"""

    def run(self):
        input_dataset: dtypes.Dataset = self.inputs.dataset
        default_filename = os.path.join(input_dataset.dataset._dir, "maps.h5")
        filename: str = self.get_input_value("filename", default_filename)
        dimensions: tuple[int, int] = self.get_input_value("dimensions", (0, 1))
        save_maps: bool = self.get_input_value("save_maps", True)
        third_motor: int | None = self.get_input_value("third_motor", None)
        orientation_img_origin: str | None = self.get_input_value(
            "orientation_img_origin", "dims"
        )

        dataset: ImageDataset = input_dataset.dataset
        moments = dataset.apply_moments()

        # mosaicity and orientation can only be computed for 2D+ datasets
        if dataset.dims.ndim > 1:
            dimension1, dimension2 = dimensions

            mosaicity = compute_mosaicity(
                moments,
                x_dimension=dimension1,
                y_dimension=dimension2,
            )

            orientation_dist_data = compute_orientation_dist_data(
                dataset,
                x_dimension=dimension1,
                y_dimension=dimension2,
                third_motor=third_motor,
            )
            assert orientation_dist_data is not None

            if (
                orientation_img_origin is not None
                and orientation_img_origin != "dims"
                and orientation_img_origin != "center"
            ):
                _logger.warning(
                    f'Unexpected value for orientation_img_origin. Expected dims, center or None, got {orientation_img_origin}. Will use "dims" instead.'
                )
                orientation_img_origin = "dims"

            image_parameters = get_image_parameters(
                dataset,
                x_dimension=dimension1,
                y_dimension=dimension2,
                origin=orientation_img_origin,
            )
            orientation_dist_image = OrientationDistImage(
                xlabel=image_parameters.xlabel,
                ylabel=image_parameters.ylabel,
                scale=image_parameters.scale,
                origin=image_parameters.origin,
                data=orientation_dist_data.data,
                as_rgb=orientation_dist_data.as_rgb,
                contours=dict(),
            )
        else:
            mosaicity = None
            orientation_dist_image = None

        # Save data if asked
        if save_maps:
            nxdict = generate_grain_maps_nxdict(
                dataset, mosaicity, orientation_dist_image
            )
            dicttonx(nxdict, filename)

        self.outputs.dataset = dtypes.Dataset(
            dataset=dataset,
            indices=input_dataset.indices,
            bg_indices=input_dataset.bg_indices,
            bg_dataset=input_dataset.bg_dataset,
        )
