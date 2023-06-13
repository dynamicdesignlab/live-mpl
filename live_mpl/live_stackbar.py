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
from typing import Iterable, Tuple

import numpy as np
from matplotlib.artist import Artist

from .exceptions import InconsistentArrayShape
from .live_base import LiveBase


@dataclass
class LiveStackBar(LiveBase):
    """
    .. _Rectangle: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html # noqa: E501

    This class implements an interactive stackbar plot based on a matplotlib
    `Rectangle`_ object.

    Raises
    ------
    InconsistentArrayShape
        If `x_data` and `y_data` do not have the same shape.
    ArrayNot1D
        If `x_data` or `y_data` has more than one dimension.

    """

    y_data: list[np.ndarray]
    """
    List of (M, N) arrays to plot as bars.

    Rows of the array are iterated over in the plots. Columns of the array are
    treated as separate columns. The bars are stacked in the order of the arrays
    in the list with the first array on the bottom.
    """

    x_data: list[float] = None
    """
    X-axis values at which to plot each individual bar

    This should contain N values.
    
    """

    labels: InitVar[list[str]] = None
    """Legend labels for each set of bars."""

    colors: InitVar[np.ndarray] = field(repr=False, default=None)

    _bar_plots: object = field(init=False, repr=False)
    """ Keep account of bar objects here"""

    @property
    def len_data(self) -> int:
        return self.y_data[0].shape[0]

    @property
    def num_bars(self) -> int:
        return self.y_data[0].shape[1]

    def __post_init__(self, labels: list[str], colors: np.ndarray):
        if self.x_data is None:
            self.x_data = np.arange(self.num_bars).tolist()

        self._validate_data(labels)
        self.heights = self.calc_heights()

        x_plot, y_plot = self.get_new_plot_data()

        barplot_list = []
        bottom = np.zeros(self.num_bars)
        for idx, (y_item, label) in enumerate(zip(y_plot, self.labels)):
            if colors is not None:
                bar_color = colors[idx, ...]

                barplot = self.axis.bar(
                    x=x_plot,
                    height=y_item,
                    bottom=bottom,
                    label=label,
                    align="center",
                    animated=True,
                    color=bar_color,
                )

            else:
                barplot = self.axis.bar(
                    x=x_plot,
                    height=y_item,
                    bottom=bottom,
                    label=label,
                    align="center",
                    animated=True,
                )

            bottom += y_item

            barplot_list.append(barplot)

        self._bar_plots = tuple(barplot_list)

    def calc_heights(self):
        heights = np.zeros((self.len_data, self.num_bars))

        for y_array in self.y_data:
            heights += y_array

        return np.max(heights, axis=1)

    def redraw_plot(self, plot_x: np.ndarray, plot_y: np.ndarray):
        bottom = np.zeros(self.num_bars)
        for barplot, y_plot in zip(self._bar_plots, plot_y):
            for idx, rect in enumerate(barplot):
                rect.set_height(y_plot[idx])
                rect.set_y(bottom[idx])
            bottom += y_plot

        self.update_axis_limits()

    def redraw_artist(self):
        for barplot in self._bar_plots:
            for rect in barplot:
                self.plot_axis.draw_artist(rect)

    def get_new_plot_data(self) -> Tuple[np.ndarray, np.ndarray]:
        plot_y = [item[self.current_idx, ...] for item in self._ydata]
        return self._xdata, tuple(plot_y)

    def _validate_data(self, labels: list[str]):
        y_shape = self.y_data[0].shape
        for array in self.y_data:
            if not array.shape == y_shape:
                raise InconsistentArrayShape(x_shape=y_shape, y_shape=array.shape)

        if not self.num_bars == len(self.x_data):
            raise ValueError("Differing number of bars in x and y data")

        if not self.num_bars == len(labels):
            raise ValueError("Differing number of bars in and labels")

    def update_axis_limits(self):
        yheight = self.heights[self.current_idx]
        self.plot_axis.set_ylim(ymin=0.0, ymax=yheight)
