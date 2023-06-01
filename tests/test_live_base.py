""" test_live_plot

This module implements unit testing for the live_plot module

"""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import dataclass

import numpy as np
import pytest
from matplotlib.artist import Artist

from live_mpl import LiveBase


@dataclass
class LivePlotTest(LiveBase):
    data: np.ndarray

    @property
    def len_data(self) -> int:
        """Length of iterable plot data."""
        return self.data.size

    @property
    def artists(self) -> list[Artist]:
        """Matplotlib artists associated with plot"""
        return []

    def redraw_artist(self) -> None:
        """Redraw plot artist on canvas for blitting."""

    def update_artist(self, *data_args: tuple[np.ndarray]) -> None:
        """
        Method to update artist given new data.

        Parameters
        ----------
        data_args:
            Tuple of data output by `get_plot_data`

        """

    def get_plot_data(self) -> tuple[np.ndarray]:
        """
        Method returning new data to plot.

        Returns
        -------
        new_data:
            Tuple of data expected by `update_artist`
        """

    def get_data_axis_limits(self) -> tuple[float, float, float, float]:
        """
        Return the axis limits for the current data.

        Returns
        -------
        x_lower:
            Lower limit of x-axis
        x_upper:
            Upper limit of x-axis
        y_lower:
            Lower limit of y-axis
        y_upper:
            Upper limit of y-axis

        """


@pytest.fixture()
def plot():
    return LivePlotTest(ax=None, data=np.zeros((100,)))


def test_get_idx(plot: LiveBase):
    assert plot.current_idx == 0


def test_increment_plot_by_one(plot: LiveBase):
    assert plot.current_idx == 0
    plot.increment(1)
    assert plot.current_idx == 1


def test_increment_plot_by_many(plot: LiveBase):
    assert plot.current_idx == 0
    plot.increment(3)
    assert plot.current_idx == 3


def test_increment_plot_clamp(plot: LiveBase):
    plot._idx = plot.len_data - 1
    plot.increment(1)
    assert plot.current_idx == plot.len_data - 1


def test_decrement_plot(plot: LiveBase):
    plot._idx = 3
    plot.decrement(1)
    assert plot.current_idx == 2


def test_decrement_plot_by_many(plot: LiveBase):
    plot._idx = 3
    plot.decrement(3)
    assert plot.current_idx == 0


def test_decrement_plot_clamp(plot: LiveBase):
    plot._idx = 0
    plot.decrement(1)
    assert plot.current_idx == 0


def test_jump_to_end(plot: LiveBase):
    assert plot.current_idx == 0
    plot.jump_to_end()
    assert plot.current_idx == plot.max_idx


def test_jump_to_beginning(plot: LiveBase):
    plot._idx = 10
    plot.jump_to_beginning()
    assert plot.current_idx == 0
