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

"""This module implements the LiveVLine concrete LiveBase child class."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import InitVar, dataclass, field

import numpy as np
from matplotlib.artist import Artist
from matplotlib.lines import Line2D

from .exceptions import ArrayNot1D
from .live_base import LiveBase

_DEFAULT_KWARGS = {"color": "black"}


@dataclass
class LiveVLine(LiveBase):
    """
    .. _Line2D: https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html # noqa: E501

    This class implements an interactive vertical line extending across
    the full axis based on a matplotlib `Line2D`_ object.

    Raises
    ------
    ArrayNot1D
        If `x_data` has greater than one dimension.

    """

    x_data: InitVar[np.ndarray]
    """1-Dimensional x-axis data to plot."""

    plot_kwargs: InitVar[dict] = None
    """
    Optional keyword arguments passed directly to matplotlib plot function.

    .. _axvline: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.axvline.html#matplotlib.axes.Axes.axvline.html # noqa: E501

    See matplotlib's `axvline`_ for more information about possible arguments.

    """

    _x: np.ndarray = field(init=False, repr=False)
    """Post-processed x-data."""

    _line: Line2D = field(init=False, repr=False)
    """Line artist rendering the actual plot."""

    @property
    def len_data(self):
        return self._x.size

    @property
    def artists(self) -> list[Artist]:
        return [self._line]

    def _update_artists(self, plot_x: np.ndarray):
        self._line.set_xdata(plot_x)

    def _get_plot_data(self) -> tuple[np.ndarray, ...]:
        return (self._x[self.current_idx],)

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        xl, xr = self.ax.get_xlim()
        yb, yt = self.ax.get_ylim()
        return xl, xr, yb, yt

    def __post_init__(self, x_data: np.ndarray, plot_kwargs: dict):
        x_data = x_data.squeeze()
        if not x_data.ndim == 1:
            raise ArrayNot1D(ndim=x_data.ndim)

        self._x = x_data

        full_plot_kwargs = _DEFAULT_KWARGS
        if plot_kwargs:
            full_plot_kwargs |= plot_kwargs

        self._line = self.ax.axvline(
            *self._get_plot_data(), animated=True, **full_plot_kwargs
        )
