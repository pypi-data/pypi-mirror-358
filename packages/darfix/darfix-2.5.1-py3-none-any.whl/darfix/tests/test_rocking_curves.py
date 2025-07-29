import numpy

from darfix.core import rocking_curves


def test_generator():
    """Tests the correct creation of a generator without moments"""
    data = numpy.random.random(size=(3, 10, 10))
    g = rocking_curves.generator(data)

    img, moment = next(g)
    assert moment is None
    numpy.testing.assert_array_equal(img, data[:, 0, 0])


def test_generator_with_moments():
    """Tests the correct creation of a generator with moments"""
    data = numpy.random.random(size=(3, 10, 10))
    moments = numpy.ones((3, 10, 10))
    g = rocking_curves.generator(data, moments)

    img, moment = next(g)
    numpy.testing.assert_array_equal(moment, moments[:, 0, 0])
    numpy.testing.assert_array_equal(img, data[:, 0, 0])


def test_fit_rocking_curve():
    """Tests the correct fit of a rocking curve"""

    samples = numpy.random.normal(size=10000) + numpy.random.random(10000)

    y, bins = numpy.histogram(samples, bins=100)

    y_pred, pars = rocking_curves.fit_rocking_curve((y, None))
    rss = numpy.sum((y - y_pred) ** 2)
    tss = numpy.sum((y - y.mean()) ** 2)
    r2 = 1 - rss / tss

    assert r2 > 0.9
    assert len(pars) == 4


def test_fit_data():
    """Tests the new data has same shape as initial data"""
    data = numpy.random.random(size=(3, 10, 10))
    new_data, maps = rocking_curves.fit_data(data)

    assert new_data.shape == data.shape
    assert len(maps) == 4
    assert maps[0].shape == data[0].shape
