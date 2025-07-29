from darfix.core.data import Data
from darfix.core.dataset import ImageDataset
from darfix.core.dimension import POSITIONER_METADATA


def test_apply_2d_fit(in_memory_dataset, on_disk_dataset):
    """Tests the fit with dimensions and indices"""

    # In memory
    data = Data(
        urls=in_memory_dataset.get_data().urls[:10],
        metadata=in_memory_dataset.get_data().metadata[:10],
        in_memory=True,
    )
    dataset = ImageDataset(_dir=in_memory_dataset.dir, data=data)
    dataset.find_dimensions(POSITIONER_METADATA)
    dataset = dataset.reshape_data()
    new_dataset, maps = dataset.apply_fit(indices=[1, 2, 3, 4])
    assert new_dataset.data.urls[0, 0] == dataset.data.urls[0, 0]
    assert new_dataset.data.urls[0, 1] != dataset.data.urls[0, 1]
    assert len(maps) == 7
    assert maps[0].shape == in_memory_dataset.get_data(0).shape

    #  On disk
    data = Data(
        urls=on_disk_dataset.get_data().urls[:10],
        metadata=on_disk_dataset.get_data().metadata[:10],
        in_memory=False,
    )
    dataset = ImageDataset(_dir=on_disk_dataset.dir, data=data)
    dataset.find_dimensions(POSITIONER_METADATA)
    dataset = dataset.reshape_data()
    new_dataset, maps = dataset.apply_fit(indices=[1, 2, 3, 4])

    assert new_dataset.data.urls[0, 0] == dataset.data.urls[0, 0]
    assert new_dataset.data.urls[0, 1] != dataset.data.urls[0, 1]
    assert len(maps) == 7
    assert maps[0].shape == in_memory_dataset.get_data(0).shape
