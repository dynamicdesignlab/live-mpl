"""This module implements the LiveLine concrete LiveBase child class."""

from dataclasses import InitVar, dataclass, field
from typing import Any, Callable

import numpy as np
from matplotlib.artist import Artist
from matplotlib.lines import Line2D

from .exceptions import InconsistentArrayShape, InvalidIterationAxis
from .live_base import LiveBase

_T = np.ndarray

_DEFAULT_KWARGS = (("marker", "*"),)


@dataclass
class LiveLine(LiveBase):
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

    x_data: InitVar[_T]
    """x-axis data to plot."""

    y_data: InitVar[_T]
    """y-axis data to plot."""

    iter_axis: int = 0
    """
    Data axis for plot to traverse.

    This follows the numpy convention, and defaults to row-wise iteration. This
    value is only respected if the numpy data has more than 1 dimension.
    """

    plot_kwargs: InitVar[dict[str, Any]] = None
    """
    Optional keyword arguments passed directly to matplotlib plot function.

    .. _plot: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html#matplotlib.axes.Axes.plot # noqa: E501

    See matplotlib's `plot`_ for more information about possible arguments.

    """

    callback_func: Callable[[Line2D, int], None] = None
    """
    Optional function called when artists are updated

    Arguments
    ---------
    index: int
        Current plot epoch index

    """

    _x: _T = field(init=False, repr=False)
    """Post-processed x-data."""
    _y: _T = field(init=False, repr=False)
    """Post-processed y-data."""
    _line: Line2D = field(init=False, repr=False)
    """Line artist rendering the actual plot."""

    @property
    def len_data(self):
        return self._x.shape[self.iter_axis]

    @property
    def artists(self) -> list[Artist]:
        return [self._line]

    def _update_artists(self, plot_x: _T, plot_y: _T):
        try:
            self.callback_func(self._line, self._idx)
        except TypeError:
            pass

        self._line.set_data(plot_x, plot_y)

    def _get_plot_data(self) -> tuple[_T, ...]:
        plot_x = self._x.take(indices=self.current_idx, axis=self.iter_axis)
        plot_y = self._y.take(indices=self.current_idx, axis=self.iter_axis)
        return plot_x, plot_y

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        return np.min(self._x), np.max(self._x), np.min(self._y), np.max(self._y)

    def _validate_data(self, x_data: _T, y_data: _T):
        if not x_data.shape == y_data.shape:
            raise InconsistentArrayShape(x_shape=x_data.shape, y_shape=y_data.shape)
        if self.iter_axis < 0 or self.iter_axis >= x_data.ndim:
            raise InvalidIterationAxis(iter_axis=self.iter_axis, num_dims=x_data.ndim)

    def __post_init__(self, x_data: _T, y_data: _T, plot_kwargs: dict[str, Any] = None):
        x_data = np.atleast_2d(x_data)
        y_data = np.atleast_2d(y_data)

        if np.atleast_1d(x_data.squeeze()).ndim == 1:
            self.iter_axis = 0

        self._validate_data(x_data, y_data)
        self._x, self._y = x_data, y_data

        full_kwargs = {key: val for key, val in _DEFAULT_KWARGS}
        if plot_kwargs:
            full_kwargs |= plot_kwargs

        self._line, *_ = self.ax.plot(
            *self._get_plot_data(), animated=True, **full_kwargs
        )
