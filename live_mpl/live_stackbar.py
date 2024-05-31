# Copyright 2022 John Talbot
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""This module implements the LiveStackbar concrete LiveBase child class."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import InitVar, dataclass, field
from itertools import chain
from typing import Tuple

import numpy as np
from matplotlib import cm
from matplotlib.artist import Artist
from matplotlib.container import BarContainer

from .live_base import LiveBase

_T_YIN = np.ndarray | list[np.ndarray]


@dataclass
class LiveStackBar(LiveBase):
    """
    .. _Rectangle: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html # noqa: E501

    This class implements an interactive stackbar plot based on a matplotlib
    `Rectangle`_ object.

    """

    y_data: InitVar[_T_YIN]
    """
    Y-axis values representing individual bars.

    This may be a list of length S holding (T, B) arrays or a single (T, B, S)
    array where T is the number of epochs, C is the number of bars along the
    x-axis, and S is the number of stacked bars or bars along the y-axis.

    If a list is entered, it will be concatenated along axis 2 (depth) to form a
    3-D numpy array.

    """

    _y_data: np.ndarray = field(init=False, default=None)
    """
    X-axis values at which to plot each individual bar.

    This should contain B values. Leaving this value at its default will plot
    each bar at integer values starting with 0.
    """

    x_data: np.ndarray = None
    """
    X-axis values at which to plot each individual bar.

    This should contain B values. Leaving this value at its default will plot
    each bar at integer values starting with 0.
    """

    labels: InitVar[list[str]] = None
    """Legend labels for each set of bars along the y-axis."""

    colors: InitVar[np.ndarray] = field(repr=False, default=None)
    """Color for each set of bars along the y-axis."""

    _bar_cts: list[BarContainer] = field(init=False, repr=False, default_factory=list)
    """List of containers which hold patchs for each rectangle."""

    _max_heights: np.ndarray = field(init=False, repr=False)
    """Maximum y-axis at each epoch."""

    @property
    def len_data(self) -> int:
        return self._y_data.shape[0]

    @property
    def num_cols(self) -> int:
        return self._y_data.shape[1]

    @property
    def num_stacks(self) -> int:
        return self._y_data.shape[2]

    @property
    def artists(self) -> list[Artist]:
        return list(chain(*self._bar_cts))

    def _update_artists(self, idx: int, _: np.ndarray, plot_y: np.ndarray):
        bottoms = np.zeros(self.num_cols)

        for yvals, bar_ct in zip(plot_y.T, self._bar_cts):
            for yval, bottom, patch in zip(yvals, bottoms, bar_ct):
                patch.set_height(yval)
                patch.set_y(bottom)

            bottoms += yval

    def _get_plot_data(self) -> Tuple[np.ndarray, np.ndarray]:
        return self.x_data, self._y_data[self.current_idx, ...]

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        return (
            np.min(self.x_data),
            np.max(self.x_data),
            0.0,
            self._max_heights[self.current_idx],
        )

    def __post_init__(self, y_data: _T_YIN, labels: list[str], colors: np.ndarray):
        if type(y_data) == list:
            self._y_data = np.stack(y_data, axis=-1)
        else:
            self._y_data = y_data

        if self.x_data is None:
            self.x_data = np.arange(self.num_cols)

        self._max_heights = self._calc_max_heights()

        if colors is None:
            colors = cm.tab20(np.linspace(0, 1, self.num_stacks))

        self._bar_cts = self._create_plots(labels=labels, colors=colors)

    def _create_plots(self, labels: list[str], colors: np.ndarray) -> None:
        x_plot, y_plot = self._get_plot_data()

        bar_containers = []
        bottom = np.zeros(self.num_cols)

        for yval, label, color in zip(y_plot.T, labels, colors):
            bar_container = self.ax.bar(
                x=x_plot,
                height=yval,
                bottom=bottom,
                label=label,
                align="center",
                animated=True,
                color=color,
            )

            bottom += yval
            bar_containers.append(bar_container)

        return bar_containers

    def _calc_max_heights(self):
        """Calculate the maximum bar height at each epoch."""
        heights = np.sum(self._y_data, axis=2)
        return np.max(heights, axis=1)
