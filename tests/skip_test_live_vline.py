""" test_live_vline

This module implements unit testing for the live_plot module

"""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"


import numpy as np
import pytest
from live_mpl import live_vline
from pytest import approx

from tests.conftest import StubPlotAxis


@pytest.fixture()
def plot():
    x_data = np.arange(10)
    y_data = np.array([0, 10])

    test_ax = StubPlotAxis(x_lim=(0, 10), y_lim=(0, 10))

    return live_vline.LiveVLine(x_data=x_data, y_data=y_data, plot_axis=test_ax)


def test_incorrect_x_data_size():
    x_data = np.row_stack((np.arange(10), np.arange(10)))
    y_data = np.array([0, 10])

    test_ax = StubPlotAxis(x_lim=(0, 10), y_lim=(0, 10))

    with pytest.raises(ValueError):
        live_vline.LiveVLine(x_data=x_data, y_data=y_data, plot_axis=test_ax)


def test_incorrect_y_data_size():
    x_data = np.arange(10)
    y_data = np.array([0, 10, 11])

    test_ax = StubPlotAxis(x_lim=(0, 10), y_lim=(0, 10))

    with pytest.raises(ValueError):
        live_vline.LiveVLine(x_data=x_data, y_data=y_data, plot_axis=test_ax)


def test_x_data_transformed_correct(plot):
    expect_x = np.row_stack((np.arange(10), np.arange(10)))

    assert plot._xdata == approx(expect_x)


def test_gets_correct_data(plot):
    expect_x = np.array([3, 3])
    expect_y = plot._ydata

    plot._idx = 3
    test_x, test_y = plot.get_new_plot_data()

    assert test_x == approx(expect_x)
    assert test_y == approx(expect_y)
