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

"""This module implements the LiveRectangle concrete LiveBase child class."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import InitVar, dataclass, field

import numpy as np
from matplotlib.artist import Artist
from matplotlib.patches import Circle

from .exceptions import ArrayNot1D, InconsistentArrayShape
from .live_base import LiveBase

_T = np.ndarray


@dataclass
class LiveCircle(LiveBase):
    """
    .. _Rectangle: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html # noqa: E501

    This class implements an interactive rectangle patch based on a matplotlib
    `Rectangle`_ object.

    Raises
    ------
    InconsistentArrayShape
        If `x_data` and `y_data` do not have the same shape.
    ArrayNot1D
        If `x_data` or `y_data` has more than one dimension.

    """

    x_center: InitVar[_T]
    """1-Dimensional x-axis position of rectangle center."""
    y_center: InitVar[_T]
    """1-Dimensional y-axis position of rectangle center."""
    radius: InitVar[_T]
    """Radius of the circle in axis units."""

    animated: bool = True
    """Whether plot should be animated or not."""

    plot_kwargs: InitVar[dict] = None
    """
    Optional keyword arguments passed directly to matplotlib rectangle patch
    constructor.

    See matplotlib's `Rectangle`_ for more information about possible arguments.

    """

    _x: _T = field(init=False, repr=False)
    """Post-processed x-axis position of the center of the circle."""
    _y: _T = field(init=False, repr=False)
    """Post-processed y-axis position of the center of the circle."""
    _radius: _T = field(init=False, repr=False)
    """Post-processed radius of the circle."""
    _patch: Circle = field(init=False, repr=False)
    """Rectangle artist rendering the actual patch."""

    @property
    def artists(self) -> list[Artist]:
        return [self._patch]

    def _update_artists(self, idx: int, x: float, y: float, radius: float):
        self._patch.set_center(xy=(x, y))
        self._patch.set_radius(radius=radius)

    def _get_plot_data(self, idx: int) -> tuple[_T]:
        x_pos = self._x[idx]
        y_pos = self._y[idx]
        radius = self._radius[idx]
        return x_pos, y_pos, radius

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        x_list = [x for x, _ in self._patch.get_corners()]
        y_list = [y for _, y in self._patch.get_corners()]
        return np.min(x_list), np.max(x_list), np.min(y_list), np.max(y_list)

    def _validate_data(self, x_center: _T, y_center: _T):
        if not x_center.shape == y_center.shape:
            raise InconsistentArrayShape(x_shape=x_center.shape, y_shape=y_center.shape)
        if not x_center.ndim == 1:
            raise ArrayNot1D(ndim=x_center.ndim)

    def __post_init__(
        self,
        x_center: _T,
        y_center: _T,
        radius: _T | float,
        plot_kwargs: dict,
    ):
        self._validate_data(x_center, y_center)
        self._x = x_center
        self._y = y_center

        if isinstance(radius, np.ndarray):
            self._radius = radius
        else:
            self._radius = radius * np.ones(self._x.shape)

        if plot_kwargs is None:
            plot_kwargs = {}

        x, y, radius = self._get_plot_data(idx=0)
        self._patch = Circle(
            xy=(x, y),
            radius=radius,
            animated=self.animated,
            **plot_kwargs,
        )

        self.ax.add_patch(self._patch)
        self.update_axis_limits()
