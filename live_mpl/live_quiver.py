# Copyright 2022 John Talbot
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

"""This module implements the LiveLine concrete LiveBase child class."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import InitVar, dataclass, field
from typing import Any

import numpy as np
from matplotlib.artist import Artist
from matplotlib.quiver import Quiver

from .live_base import LiveBase

_T = np.ndarray

_DEFAULT_KWARGS = (("angles", "xy"), ("width", 0.0015))


@dataclass
class LiveQuiver(LiveBase):
    """
    .. _Line2D: https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html # noqa: E501

    This class implements an interactive line plot based on a matplotlib
    `Line2D`_ object.

    Raises
    ------
    InconsistentArrayShape
        If `x_data` and `y_data` do not have the same shape
    InvalidIterationAxis
        If `iter_axis` is invalid for the provided data

    """

    x_data: np.ndarray
    y_data: np.ndarray
    u_data: np.ndarray
    v_data: np.ndarray

    plot_kwargs: InitVar[dict[str, Any]] = None
    """
    Optional keyword arguments passed directly to matplotlib plot function.

    .. _plot: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html#matplotlib.axes.Axes.plot # noqa: E501

    See matplotlib's `plot`_ for more information about possible arguments.

    """

    _quiver: Quiver = field(init=False, repr=False)
    """Line artist rendering the actual plot."""

    @property
    def len_data(self):
        return self.x_data.shape[0]

    @property
    def artists(self) -> list[Artist]:
        return [self._quiver]

    def _update_artists(self, plot_x: _T, plot_y: _T, plot_u: _T, plot_v: _T):
        self._quiver.set_offsets(np.column_stack((plot_x, plot_y)))
        self._quiver.set_UVC(plot_u, plot_v)

    def _get_plot_data(self) -> tuple[_T, ...]:
        plot_x = self.x_data[self.current_idx, :]
        plot_y = self.y_data[self.current_idx, :]
        plot_u = self.u_data[self.current_idx, :]
        plot_v = self.v_data[self.current_idx, :]
        return plot_x, plot_y, plot_u, plot_v

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        return (
            np.min(self.x_data + self.u_data),
            np.max(self.x_data + self.u_data),
            np.min(self.y_data + self.v_data),
            np.max(self.y_data + self.v_data),
        )

    def __post_init__(self, plot_kwargs: dict[str, Any] = None):
        full_kwargs = {key: val for key, val in _DEFAULT_KWARGS}
        if plot_kwargs:
            full_kwargs |= plot_kwargs

        _, _, u, v = self._get_plot_data()
        zero_offsets = np.zeros(u.shape)
        self._quiver = self.ax.quiver(
            zero_offsets, zero_offsets, u, v, animated=True, **full_kwargs
        )
