""" test_live_stackbar

This module implements unit testing for the live_stackbar module

"""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"


import itertools

import numpy as np
import pytest
from live_mpl import live_stackbar
from pytest import approx

from tests.conftest import StubPlotAxis

NUM_STACKS = 3
NUM_BARS = 5
NUM_EPOCH = 4


@pytest.fixture()
def plot_data():
    x_data = np.arange(NUM_BARS)
    labels = [f"{num}" for num in range(NUM_BARS)]
    y_arr = np.tile(np.arange(NUM_EPOCH).reshape((NUM_EPOCH, 1)), (1, NUM_BARS))
    y_data = [y_arr for _ in range(NUM_STACKS)]
    return x_data, y_data, labels


@pytest.fixture()
def plot(plot_data):
    x_data, y_data, labels = plot_data
    test_ax = StubPlotAxis(x_lim=(0, 10), y_lim=(0, 10))

    return live_stackbar.LiveStackBar(
        x_data=None, y_data=y_data, labels=labels, traverse_rows=True, plot_axis=test_ax
    )


def test_num_bars(plot):
    assert plot.num_bars == NUM_BARS


def test_num_epochs(plot):
    assert plot.num_epochs == NUM_EPOCH


def test_x_incorrect_size():
    x_data = np.arange(NUM_BARS)
    labels = [f"{num}" for num in range(NUM_BARS)]
    y_arr = np.zeros((NUM_EPOCH, NUM_BARS + 1))
    y_data = [y_arr for _ in range(NUM_BARS)]

    y_data.append(y_arr)

    test_ax = None

    with pytest.raises(ValueError):
        live_stackbar.LiveStackBar(
            x_data=x_data,
            y_data=y_data,
            labels=labels,
            traverse_rows=True,
            plot_axis=test_ax,
        )


def test_y_not_same_size():
    x_data = np.arange(NUM_BARS)
    labels = [f"{num}" for num in range(NUM_BARS)]
    y_arr_good = np.zeros((NUM_EPOCH, NUM_BARS))
    y_arr_bad = np.zeros((NUM_EPOCH, NUM_BARS + 1))

    y_data = [y_arr_good for _ in range(NUM_BARS)]

    y_data.append(y_arr_bad)

    test_ax = None

    with pytest.raises(ValueError):
        live_stackbar.LiveStackBar(
            x_data=x_data,
            y_data=y_data,
            labels=labels,
            traverse_rows=True,
            plot_axis=test_ax,
        )


def test_get_correct_data(plot_data, plot):
    x_data, y_data, _ = plot_data
    x_res, y_res = plot.get_new_plot_data()

    assert x_res == approx(x_data)

    for test_item, expect_item in itertools.zip_longest(y_res, y_data):
        assert test_item == approx(expect_item[0, :])


def test_get_correct_data_axis_1(plot_data):
    _, y_data, labels = plot_data
    test_ax = StubPlotAxis(x_lim=(0, 10), y_lim=(0, 10))

    test_plot = live_stackbar.LiveStackBar(
        x_data=None,
        y_data=y_data,
        labels=labels,
        traverse_rows=False,
        plot_axis=test_ax,
    )
    x_res, y_res = test_plot.get_new_plot_data()

    assert x_res == approx(np.arange(NUM_EPOCH))

    for test_item, expect_item in itertools.zip_longest(y_res, y_data):
        assert test_item == approx(expect_item[:, 0])


def test_calc_heights(plot):
    for idx in range(NUM_EPOCH):
        assert plot.heights[idx] == idx * 3
