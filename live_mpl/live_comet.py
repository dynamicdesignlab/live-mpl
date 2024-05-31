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

"""This module implements the LiveComet concrete LiveBase child class."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import InitVar, dataclass, field
from typing import Any

import numpy as np
from matplotlib.artist import Artist
from matplotlib.lines import Line2D

from .exceptions import ArrayNot1D, InconsistentArrayShape
from .live_base import LiveBase

_T = np.ndarray

_DEFAULT_HEAD_KWARGS = {
    "marker": "o",
    "markeredgecolor": "black",
    "markersize": 10,
    "markerfacecolor": "None",
}
_DEFAULT_TAIL_KWARGS = {"linewidth": 2}


@dataclass
class LiveComet(LiveBase):
    """
    .. _Line2D: https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html # noqa: E501

    This class implements an interactive line that extends in length, plotting
    incrementally more elements of the given data arrays. It behaves similarly
    to matlab's comet plot. This plot is based on a matplotlib `Line2D`_ object.

    Raises
    ------
    InconsistentArrayShape
        If `x_data` and `y_data` do not have the same shape
    ArrayNot1D
        If `x_data` or `y_data` has more than one dimension.

    """

    x_data: InitVar[_T]
    """1-Dimensional x-axis data to plot."""
    y_data: InitVar[_T]
    """1-Dimensional y-axis data to plot."""

    animated: bool = True
    """Whether plot should be animated or not."""

    head_kwargs: InitVar[dict] = None
    """
    Optional keyword arguments controlling the appearance of the comet's head.

    .. _plot: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html#matplotlib.axes.Axes.plot # noqa: E501

    By default all head keyword arguments are populated by the
    `~live_mpl.live_comet.default_head_kwargs` factory function. Users may overwrite none, any, or
    all of the arguments specified in that function, and the user's preferences
    will take priority.  See matplotlib's `plot`_ for more information about
    possible arguments.

    """
    tail_kwargs: InitVar[dict] = None
    """
    Optional keyword arguments controlling the appearance of the comet's tail.

    .. _plot: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html#matplotlib.axes.Axes.plot # noqa: E501

    By default all tail keyword arguments are populated by the
    `~live_mpl.live_comet.default_tail_kwargs` factory function. Users may overwrite none, any, or
    all of the arguments specified in that function, and the user's preferences
    will take priority.  See matplotlib's `plot`_ for more information about
    possible arguments.

    """

    _x: _T = field(init=False, repr=False)
    """Post-processed x-data."""
    _y: _T = field(init=False, repr=False)
    """Post-processed y-data."""
    _head: Line2D = field(init=False, repr=False)
    """Line artist rendering the actual plot."""
    _tail: Line2D = field(init=False, repr=False)
    """Line artist rendering the actual plot."""

    @property
    def len_data(self):
        return self._x.size

    @property
    def artists(self) -> list[Artist]:
        return [self._head, self._tail]

    def _update_artists(self, idx: int, head_x: _T, head_y: _T, tail_x: _T, tail_y: _T):
        self._head.set_data(head_x, head_y)
        self._tail.set_data(tail_x, tail_y)

    def _get_plot_data(self, idx: int) -> tuple[_T, ...]:
        head_x = self._x[idx]
        head_y = self._y[idx]
        tail_x = self._x[:idx]
        tail_y = self._y[:idx]
        return head_x, head_y, tail_x, tail_y

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        head_x, head_y, tail_x, tail_y = self._get_plot_data()
        try:
            return np.min(tail_x), np.max(tail_x), np.min(tail_y), np.max(tail_y)
        except ValueError:
            return np.min(head_x), np.max(head_x), np.min(head_y), np.max(head_y)

    @staticmethod
    def _validate_data(x_data: _T, y_data: _T):
        if x_data.ndim > 1:
            raise ArrayNot1D(ndim=x_data.ndim)
        if y_data.ndim > 1:
            raise ArrayNot1D(ndim=y_data.ndim)
        if not x_data.shape == y_data.shape:
            raise InconsistentArrayShape(x_shape=x_data.shape, y_shape=y_data.shape)

    def _create_head(self, head_kwargs: dict[str, Any]) -> Line2D:
        head_x, head_y, _, _ = self._get_plot_data(idx=0)
        head, *_ = self.ax.plot(head_x, head_y, animated=self.animated, **head_kwargs)

        return head

    def _create_tail(self, tail_kwargs: dict[str, Any]) -> Line2D:
        _, _, tail_x, tail_y = self._get_plot_data(idx=0)
        tail, *_ = self.ax.plot(tail_x, tail_y, animated=self.animated, **tail_kwargs)
        return tail

    def __post_init__(
        self, x_data: _T, y_data: _T, head_kwargs: dict, tail_kwargs: dict
    ):
        self._validate_data(x_data, y_data)
        self._x = x_data
        self._y = y_data

        full_head_kwargs = _DEFAULT_HEAD_KWARGS
        if head_kwargs:
            full_head_kwargs |= head_kwargs
        self._head = self._create_head(full_head_kwargs)

        full_tail_kwargs = _DEFAULT_TAIL_KWARGS
        if tail_kwargs:
            full_tail_kwargs |= tail_kwargs
        self._tail = self._create_tail(full_tail_kwargs)

        self.update_axis_limits()
