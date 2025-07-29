from __future__ import annotations

import logging
from typing import Any
from typing import Sequence

import numpy
from silx.io import fabioh5

_logger = logging.getLogger(__file__)

DEFAULT_METADATA = fabioh5.FabioReader.DEFAULT

COUNTER_METADATA = fabioh5.FabioReader.COUNTER

POSITIONER_METADATA = fabioh5.FabioReader.POSITIONER

_METADATA_TYPES: dict[str, int] = {
    "positioner": POSITIONER_METADATA,
    "default": DEFAULT_METADATA,
    "counter": COUNTER_METADATA,
}

_METADATA_TYPES_I: dict[int, str] = {}
"""used to retrieve the metadata name (str) for the silx.io.fabioh5 id"""
for key, value in _METADATA_TYPES.items():
    assert value not in _METADATA_TYPES_I
    _METADATA_TYPES_I[value] = key


class AcquisitionDims(dict):
    """
    Define the view of the data which has to be made
    """

    def add_dim(self, axis: int, dim: Dimension | dict):
        if isinstance(dim, dict):
            dim = Dimension.from_dict(dim)
        if not isinstance(dim, Dimension):
            raise TypeError(f"dim is expected to be a {Dimension}. Get {type(dim)}")
        self[axis] = dim

    def remove_dim(self, axis: int):
        if axis in self:
            del self[axis]

    @property
    def ndim(self) -> int:
        return len(self)

    def get(self, axis: int, default=None) -> Dimension | None:
        """
        Get Dimension at certain axis.

        :param int axis: axis of the dimension.
        :return: the requested dimension if exists.
        """
        assert type(axis) is int
        return super().get(axis, default)

    def get_names(self) -> list[str]:
        """
        Get list with all the names of the dimensions.

        :return: array_like of strings
        """

        return [dim.name for dim in self.values()]

    @property
    def shape(self) -> tuple[int, ...]:
        """
        Shape order is reversed from the axis so the data is correctly reshaped
        so that the dimensions which motors move first are at the last axis of the
        data. This is done to mantain the axes order as they are used to in the beamlines.

        :return: shape of the currently defined dims
        """
        shape = []
        for iDim in reversed(range(self.ndim)):
            if iDim not in self:
                shape.append(1)
            else:
                shape.append(self[iDim].size or -1)
        return tuple(shape)

    def set_size(self, axis: int, size: int):
        """
        Recreated new dimension with new size and same name and kind.

        :param int axis: axis of the dimension
        :param int size: new size for the dimension
        """
        if axis not in self:
            _logger.error(
                f"axis {axis} is not defined yet, cannot define a size for it"
            )
        else:
            self[axis] = Dimension(
                name=self[axis].name, kind=self[axis].kind, size=size
            )


class Dimension:
    """
    Define a dimension used during the dataset

    :param Union[int,str] kind: metadata type in fabioh5 mapping
    :param str name: name of the dimension (should fit the fabioh5 mapping
                     for now)
    :param Union[int,None] size: length of the dimension.
    """

    def __init__(
        self,
        kind: str | int,
        name: str,
        size: int | None = None,
        _range=None,
        tolerance: float = 1e-09,
        unique_values: Sequence[float] | None = None,
    ):
        if isinstance(kind, str):
            assert kind in _METADATA_TYPES
            self.__kind = _METADATA_TYPES[kind]
        else:
            self.__kind = kind
        self.__name = name
        self._size = size
        self._tolerance = tolerance
        self._range = _range
        self.__unique_values = list(unique_values) if unique_values else []

    @property
    def kind(self):
        return self.__kind

    def set_kind(self, kind: int):
        self.__kind = kind

    @property
    def name(self) -> str:
        return self.__name

    def set_name(self, name: str):
        self.__name = name

    @property
    def size(self) -> int | None:
        return self._size

    def set_size(self, size: int):
        self._size = size

    @property
    def range(self):
        return self._range

    def set_range(self, _range):
        self._range = _range

    @property
    def tolerance(self) -> float:
        return self._tolerance

    def set_tolerance(self, tolerance: float):
        assert isinstance(tolerance, float), "Tolerance has to be float number"
        self._tolerance = tolerance

    @property
    def unique_values(self) -> list[float]:
        return self.__unique_values

    def _find_unique_values(self, values: Sequence[float]) -> list[float]:
        """
        Function that compares the values passed as parameter and returns only the unique
        ones given the dimension's tolerance.

        :param array_like values: list of values to compare.
        """
        unique_values = []
        import math

        for val in values:
            if not unique_values:
                unique_values.append(val)
            else:
                unique = True
                for unique_value in unique_values:
                    if math.isclose(unique_value, val, rel_tol=self.tolerance):
                        unique = False
                        break
                if unique:
                    unique_values.append(val)
        return unique_values

    def set_unique_values(self, values: Sequence[float]):
        """
        Sets the unique values of the dimension. If the size of the dimension is fixed,
        it automatically sets the first size values, else it finds the unique values.

        :param array_like values: list of values.
        """
        if self.range:
            v0, v1, step = self.range
            if not step:
                if not self.size:
                    self.__unique_values = self._values_with_step(
                        self._find_unique_values(values)
                    )
                else:
                    step = (v1 - v0) / (self.size - 1)
                    self.__unique_values = [
                        s for s in numpy.linspace(v0, v1, self.size)
                    ]
            else:
                if not self.size:
                    size = int(numpy.round((v1 - v0) / step)) + 1
                else:
                    size = self.size
                self.__unique_values = [s for s in numpy.linspace(v0, v1, size)]
            self.set_range([v0, v1, step])
        elif self.size:
            self.__unique_values = self._values_with_step(values[: self.size])
        else:
            self.__unique_values = self._values_with_step(
                self._find_unique_values(values)
            )
        self.set_size(len(self.__unique_values))

    def _values_with_step(self, values: Sequence[float]) -> list[float]:
        try:
            v0, v1 = min(values), max(values)
            step = (v1 - v0) / (len(values) - 1)
            self.set_range([v0, v1, step])
            return [s for s in numpy.linspace(v0, v1, len(values))]
        except (ValueError, IndexError):
            return list(values)

    def __str__(self):
        return " ".join((str(self.kind), str(self.name), "size:", str(self.size)))

    def to_dict(self) -> dict[str, Any]:
        """Translate the current Dimension to a dictionary"""
        return {
            "name": self.name,
            "kind": self.kind,
            "size": self.size,
            "range": self.range,
            "tolerance": self.tolerance,
            "unique_values": self.unique_values,
        }

    @staticmethod
    def from_dict(_dict: dict):
        """

        :param dict _dict: dict defining the dimension. Should contains the
                           following keys: name, kind, size.
                           Unique values are not stored into it because it
                           depends on the metadata and should be obtained from a
                           fit / set_dims
        :return: Dimension corresponding to the dict given
        :rtype: :class:`Dimension`
        """
        assert type(_dict) is dict
        missing_keys = []
        for _key in ("name", "kind", "size", "tolerance"):
            if _key not in _dict:
                missing_keys.append(missing_keys)
        if len(missing_keys) > 0:
            raise ValueError(
                f"There are some missing keys ({missing_keys}), unable to create a valid dim object"
            )
        else:
            _range = _dict["range"] if "range" in _dict else None
            _unique_values = (
                _dict["unique_values"] if "unique_values" in _dict else None
            )
            return Dimension(
                name=_dict["name"],
                kind=_dict["kind"],
                size=_dict["size"],
                _range=_range,
                tolerance=_dict["tolerance"],
                unique_values=_unique_values,
            )
