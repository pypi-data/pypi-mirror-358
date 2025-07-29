from __future__ import annotations

import multiprocessing
from functools import partial
from multiprocessing import Pool
from numbers import Number
from typing import Any
from typing import Generator
from typing import List
from typing import Literal
from typing import Tuple
from typing import Union

import numpy
import tqdm
from scipy.optimize import curve_fit
from silx.utils.enum import Enum as _Enum

import darfix

from ..io.utils import create_nxdata_dict
from .data import Data

Indices = Union[range, numpy.ndarray]

FitMethod = Literal["trf", "lm", "dogbox"]

DataLike = Union[Data, numpy.ndarray]


class Maps(_Enum):
    """
    Different maps that can be shown after fitting the data
    """

    AMPLITUDE = "Amplitude"
    FWHM = "FWHM"
    PEAK = "Peak position"
    BACKGROUND = "Background"
    RESIDUALS = "Residuals"


class Maps_2D(_Enum):
    """
    Different maps that can be shown after fitting the data
    """

    AMPLITUDE = "Amplitude"
    PEAK_X = "Peak position first motor"
    PEAK_Y = "Peak position second motor"
    FWHM_X = "FWHM first motor"
    FWHM_Y = "FWHM second motor"
    BACKGROUND = "Background"
    CORRELATION = "Correlation"
    RESIDUALS = "Residuals"


MAPS_FIT_INDICES = {
    Maps.AMPLITUDE: 0,
    Maps.PEAK: 1,
    Maps.FWHM: 2,
    Maps.BACKGROUND: 3,
}


MAPS_2D_FIT_INDICES = {
    Maps_2D.PEAK_X: 0,
    Maps_2D.PEAK_Y: 1,
    Maps_2D.FWHM_X: 2,
    Maps_2D.FWHM_Y: 3,
    Maps_2D.AMPLITUDE: 4,
    Maps_2D.CORRELATION: 5,
    Maps_2D.BACKGROUND: 6,
}


def _gaussian(x, a, b, c, d):
    """
    Function to calculate the Gaussian with constants a, b, and c

    :param float x: Value to evaluate
    :param float a: height of the curve's peak
    :param float b: position of the center of the peak
    :param float c: standard deviation
    :param float d: lowest value of the curve (value of the limits)

    :returns: result of the function on x
    :rtype: float
    """
    return d + a * numpy.exp(-numpy.power(x - b, 2) / (2 * numpy.power(c, 2)))


def _multi_gaussian(M, x0, y0, xalpha, yalpha, A, C, bg):
    """
    Bivariate case of the multigaussian PDF + background
    """
    x, y = M
    return bg + A * numpy.exp(
        -0.5
        / (1 - C**2)
        * (
            ((x - x0) / xalpha) ** 2
            + ((y - y0) / yalpha) ** 2
            - 2 * C * (x - x0) * (y - y0) / xalpha / yalpha
        )
    )


def generator(
    data: DataLike, moments: numpy.ndarray | None = None, indices=None
) -> (
    Generator[Tuple[float, None], None, None]
    | Generator[Tuple[float, float], None, None]
):
    """
    Generator that returns the rocking curve for every pixel

    :param ndarray data: data to analyse
    :param moments: array of same shape as data with the moments values per pixel and image, optional
    :type moments: Union[None, ndarray]
    """
    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            if indices is None:
                new_data = data[:, i, j]
            else:
                new_data = numpy.zeros(data.shape[0])
                new_data[indices] = data[indices, i, j]
            if moments is not None:
                yield new_data, moments[:, i, j]
            yield new_data, None


# TODO: NOT USED ?
def generator_2d(data, moments=None):
    """
    Generator that returns the rocking curve for every pixel

    :param ndarray data: data to analyse
    :param moments: array of same shape as data with the moments values per pixel and image, optional
    :type moments: Union[None, ndarray]


    """
    for i in range(data.shape[2]):
        for j in range(data.shape[3]):
            yield data[:, :, i, j], None


def fit_rocking_curve(
    y_values: Tuple[numpy.ndarray, numpy.ndarray | None],
    values: list | numpy.ndarray | None = None,
    num_points: int | None = None,
    int_thresh: Number | None = None,
    method: FitMethod | None = None,
) -> Tuple[numpy.ndarray, numpy.ndarray | list]:
    """
    Fit rocking curve.

    :param y_values: the first element is the dependent data and the second element are
        the moments to use as starting values for the fit
    :param values: The independent variable where the data is measured, optional
    :param num_points: Number of points to evaluate the data on, optional
    :param nt_thresh: Intensity threshold. If not None, only the rocking curves with
        higher ptp (range of values) are fitted, others are assumed to be noise and not important
        data. This parameter is used to accelerate the fit. Optional.

    :returns: If curve was fitted, the fitted curve, else item[0]
    """
    if method is None:
        method = "trf"
    y, moments = y_values
    y = numpy.asanyarray(y)
    x = numpy.asanyarray(values) if values is not None else numpy.arange(len(y))
    ptp_y = numpy.ptp(y)
    if int_thresh is not None and ptp_y < int_thresh:
        return y, [0, x[0], 0, min(y)]
    if moments is not None:
        p0 = [ptp_y, moments[0], moments[1], min(y)]
    else:
        _sum = sum(y)
        if _sum > 0:
            mean = sum(x * y) / sum(y)
            sigma = numpy.sqrt(sum(y * (x - mean) ** 2) / sum(y))
        else:
            mean, sigma = numpy.nan, numpy.nan
        p0 = [ptp_y, mean, sigma, min(y)]
    if numpy.isnan(mean) or numpy.isnan(sigma):
        return y, p0
    if numpy.isclose(p0[2], 0):
        return y, p0
    if num_points is None:
        num_points = len(y)
    epsilon = 1e-2
    bounds = numpy.array(
        [
            [min(ptp_y, min(y)) - epsilon, min(x) - epsilon, 0, -numpy.inf],
            [max(max(y), ptp_y) + epsilon, max(x) + epsilon, numpy.inf, numpy.inf],
        ]
    )

    p0 = numpy.array(p0)
    p0[p0 < bounds[0]] = bounds[0][p0 < bounds[0]]
    p0[p0 > bounds[1]] = bounds[1][p0 > bounds[1]]
    try:
        pars, cov = curve_fit(
            f=_gaussian, xdata=x, ydata=y, p0=p0, bounds=bounds, method=method
        )
        y_gauss = _gaussian(numpy.linspace(x[0], x[-1], num_points), *pars)
        y_gauss[numpy.isnan(y_gauss)] = 0
        y_gauss[y_gauss < 0] = 0
        pars[2] *= darfix.config.FWHM_VAL
        return y_gauss, pars
    except RuntimeError:
        p0[2] *= darfix.config.FWHM_VAL
        return y, p0
    except ValueError:
        p0[2] *= darfix.config.FWHM_VAL
        return y, p0


def fit_2d_rocking_curve(
    y_values: Tuple[numpy.ndarray, numpy.ndarray | None],
    values: list | numpy.ndarray,
    shape: Tuple[int, ...],
    int_thresh: Number | None = None,
    method: FitMethod | None = None,
) -> Tuple[numpy.ndarray, numpy.ndarray | list]:
    if method is None:
        method = "trf"
    assert method in ("trf", "lm", "dogbox")
    y, moments = y_values
    y = numpy.asanyarray(y)
    ptp_y = numpy.ptp(y)
    values = numpy.asanyarray(values)
    _sum = sum(y)
    if numpy.isclose(_sum, 0, rtol=1e-03):
        return y, [numpy.nan, numpy.nan, numpy.nan, numpy.nan, ptp_y, 0, 0]
    x0 = sum(values[0] * y) / _sum
    y0 = sum(values[1] * y) / _sum
    xalpha = numpy.sqrt(sum(y * (values[0] - x0) ** 2) / _sum)
    yalpha = numpy.sqrt(sum(y * (values[1] - y0) ** 2) / _sum)
    if (int_thresh is not None and ptp_y < int_thresh) or xalpha == 0 or yalpha == 0:
        return y, [x0, y0, xalpha, yalpha, ptp_y, 0, 0]
    X, Y = numpy.meshgrid(
        values[0, : shape[0]], values[1].reshape(numpy.flip(shape))[:, 0]
    )
    xdata = numpy.vstack((X.ravel(), Y.ravel()))
    epsilon = 1e-3
    if method in ("trf", "dogbox"):
        bounds = (
            [
                min(values[0]) - epsilon,
                min(values[1]) - epsilon,
                -numpy.inf,
                -numpy.inf,
                min(ptp_y, min(y)) - epsilon,
                -1,
                -numpy.inf,
            ],
            [
                max(values[0]) + epsilon,
                max(values[1]) + epsilon,
                numpy.inf,
                numpy.inf,
                max(ptp_y, max(y)) + epsilon,
                1,
                numpy.inf,
            ],
        )
    else:
        bounds = (-numpy.inf, numpy.inf)

    try:
        pars, cov = curve_fit(
            f=_multi_gaussian,
            xdata=xdata,
            ydata=y,
            p0=[x0, y0, xalpha, yalpha, ptp_y, 0, 0],
            bounds=bounds,
            method=method,
        )
        y_gauss = _multi_gaussian([X, Y], *pars)
        pars[2] *= darfix.config.FWHM_VAL
        pars[3] *= darfix.config.FWHM_VAL
        return y_gauss.ravel(), pars
    except RuntimeError:
        return y, [
            x0,
            y0,
            darfix.config.FWHM_VAL * xalpha,
            darfix.config.FWHM_VAL * yalpha,
            ptp_y,
            0,
            0,
        ]


def fit_data(
    data: DataLike,
    moments: numpy.ndarray | None = None,
    values: List[numpy.ndarray] | numpy.ndarray | None = None,
    shape: Any = None,
    indices: Indices | None = None,
    int_thresh: Number = 15,
    method: FitMethod | None = None,
):
    """Fit data in axis 0 of data"""

    g = generator(data, moments)
    cpus = multiprocessing.cpu_count()
    curves, maps = [], []
    with Pool(cpus - 1) as p:
        for curve, pars in tqdm.tqdm(
            p.imap(
                partial(
                    fit_rocking_curve,
                    values=values,
                    int_thresh=int_thresh,
                    method=method,
                ),
                g,
            ),
            total=data.shape[1] * data.shape[2],
        ):
            curves.append(list(curve))
            maps.append(list(pars))

    return numpy.array(curves).T.reshape(data.shape), numpy.array(maps).T.reshape(
        (4, data.shape[-2], data.shape[-1])
    )


def fit_2d_data(
    data: DataLike,
    values: List[numpy.ndarray] | numpy.ndarray,
    shape: Tuple[int, int],
    moments: numpy.ndarray | None = None,
    int_thresh: int = 15,
    indices: Indices | None = None,
    method: FitMethod | None = None,
):
    """Fit data in axis 0 of data"""
    g = generator(data, moments, indices)
    cpus = multiprocessing.cpu_count()
    curves, maps = [], []
    with Pool(cpus - 1) as p:
        for curve, pars in tqdm.tqdm(
            p.imap(
                partial(
                    fit_2d_rocking_curve,
                    values=values,
                    shape=shape,
                    int_thresh=int_thresh,
                    method=method,
                ),
                g,
            ),
            total=data.shape[-2] * data.shape[-1],
        ):
            curves.append(list(curve))
            maps.append(list(pars))

    curves = numpy.array(curves).T
    if indices is not None:
        curves = curves[indices]
    return curves.reshape(data[indices].shape), numpy.array(maps).T.reshape(
        (7, data.shape[-2], data.shape[-1])
    )


def generate_rocking_curves_nxdict(
    dataset,  # ImageDataset. Cannot type due to circular import
    maps: numpy.ndarray,
    residuals: numpy.ndarray | None,
) -> dict:
    entry = "entry"

    nx = {
        entry: {"@NX_class": "NXentry"},
        "@NX_class": "NXroot",
        "@default": entry,
    }

    if dataset.transformation:
        axes = [
            dataset.transformation.yregular,
            dataset.transformation.xregular,
        ]
        axes_names = ["y", "x"]
        axes_long_names = [
            dataset.transformation.label,
            dataset.transformation.label,
        ]
    else:
        axes = None
        axes_names = None
        axes_long_names = None

    if dataset.dims.ndim == 2:
        for _map in Maps_2D:
            signal_name = _map.value
            if _map == Maps_2D.RESIDUALS:
                signal = residuals
            else:
                maps_idx = MAPS_2D_FIT_INDICES[_map]
                signal = maps[maps_idx]
            nx[entry][signal_name] = create_nxdata_dict(
                signal, signal_name, axes, axes_names, axes_long_names
            )
        nx[entry]["@default"] = Maps_2D.AMPLITUDE.value
    else:
        for _map in Maps:
            signal_name = _map.value
            if _map == Maps.RESIDUALS:
                signal = residuals
            else:
                maps_idx = MAPS_FIT_INDICES[_map]
                signal = maps[maps_idx]
            nx[entry][signal_name] = create_nxdata_dict(
                signal, signal_name, axes, axes_names, axes_long_names
            )
        nx[entry]["@default"] = Maps.AMPLITUDE.value

    return nx


def compute_residuals(
    target_dataset,  # ImageDataset. Cannot type due to circular import
    original_dataset,  # ImageDataset. Cannot type due to circular import
    indices: numpy.ndarray | None,
):
    return numpy.sqrt(
        numpy.subtract(target_dataset.zsum(indices), original_dataset.zsum(indices))
        ** 2
    )
