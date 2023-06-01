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

from matplotlib.patches import Rectangle
from matplotlib.artist import Artist
from dataclasses import InitVar, dataclass, field

import numpy as np

from .live_base import LiveBase
from .exceptions import InconsistentArrayShape, ArrayNot1D

_T = np.ndarray


@dataclass
class LiveRectangle(LiveBase):
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
    angle_deg: InitVar[_T]
    """
    Angle of the rectangle in degrees measured counter-clockwise from the
    positive y-axis.
    """

    width: InitVar[float]
    """Width of the rectangle in axis units."""
    height: InitVar[float]
    """Height of the rectangle in axis units."""

    plot_kwargs: InitVar[dict] = None
    """
    Optional keyword arguments passed directly to matplotlib rectangle patch
    constructor.

    See matplotlib's `Rectangle`_ for more information about possible arguments.

    """

    _x: _T = field(init=False, repr=False)
    """Post-processed x-axis position of the bottom left corner of the rectangle."""
    _y: _T = field(init=False, repr=False)
    """Post-processed y-axis position of the bottom left corner of the rectangle."""
    _theta: _T = field(init=False, repr=False)
    """Post-processed angle of the rectangle."""
    _patch: Rectangle = field(init=False, repr=False)
    """Rectangle artist rendering the actual patch."""

    @property
    def len_data(self) -> int:
        return self._x.size

    @property
    def artists(self) -> list[Artist]:
        return [self._patch]

    def _update_artists(self, x: float, y: float, theta: float) -> None:
        self._patch.set_xy(xy=(x, y))
        self._patch.set_angle(angle=theta)

    def _get_plot_data(self) -> tuple[_T]:
        x_pos = self._x[self.current_idx]
        y_pos = self._y[self.current_idx]
        angle = self._theta[self.current_idx]
        return x_pos, y_pos, angle

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        x_list = [x for x, _ in self._patch.get_corners()]
        y_list = [y for _, y in self._patch.get_corners()]
        return np.min(x_list), np.max(x_list), np.min(y_list), np.max(y_list)

    def _validate_data(self, x_center: _T, y_center: _T, angle: _T):
        if not x_center.shape == y_center.shape:
            raise InconsistentArrayShape(x_shape=x_center.shape, y_shape=y_center.shape)
        if not x_center.shape == angle.shape:
            raise InconsistentArrayShape(x_shape=x_center.shape, y_shape=angle.shape)
        if not x_center.ndim == 1:
            raise ArrayNot1D(ndim=x_center.ndim)

    def __post_init__(
        self,
        x_center: _T,
        y_center: _T,
        angle_deg: _T,
        width: float,
        height: float,
        plot_kwargs: dict,
    ) -> None:
        self._validate_data(x_center, y_center, angle_deg)
        self._x = x_center - (width / 2)
        self._y = y_center - (height / 2)
        self._theta = angle_deg

        if plot_kwargs is None:
            plot_kwargs = {}

        x, y, theta = self._get_plot_data()
        self._patch = Rectangle(
            xy=(x, y),
            angle=theta,
            width=width,
            height=height,
            rotation_point="center",
            animated=True,
            **plot_kwargs,
        )

        self.ax.add_patch(self._patch)
        self.update_axis_limits()
