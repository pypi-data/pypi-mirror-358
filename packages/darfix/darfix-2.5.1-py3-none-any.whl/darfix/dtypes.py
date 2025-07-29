from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

import numpy

from darfix.core.dataset import ImageDataset

AxisAndValueIndices = Tuple[List[int], List[int]]


@dataclass
class Dataset:
    """Darfix dataset with indices and background"""

    dataset: ImageDataset  # Darfix dataset object that holds the image stack
    indices: Optional[numpy.ndarray] = (
        None  # Image stack indices to be taking into account. Usually set by the 'partition data' task
    )
    bg_indices: Optional[numpy.ndarray] = (
        None  # Dark image stack indices to be taking into account. Usually set by the 'partition data' task
    )
    bg_dataset: Optional[ImageDataset] = (
        None  # Darfix dataset object that holds the dark image stack
    )


class DatasetTypeError(TypeError):
    def __init__(self, wrong_dataset: Any):
        """Error raised when a dataset has not the expected Dataset type"""
        super().__init__(
            f"Dataset is expected to be an instance of {Dataset}. Got {type(wrong_dataset)}."
        )
