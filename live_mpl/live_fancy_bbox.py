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

"""This module implements the LiveFancyBBox concrete LiveBase child class."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from matplotlib.patches import FancyBboxPatch, BoxStyle
from matplotlib.transforms import Affine2D
from matplotlib.artist import Artist
from dataclasses import InitVar, dataclass, field

import numpy as np

from .live_base import LiveBase
from .exceptions import InconsistentArrayShape, ArrayNot1D

_T = np.ndarray

# Make Initvars work in documentation
InitVar.__call__ = lambda *args: None


@dataclass
class LiveFancyBBox(LiveBase):
    """
    .. _FancyBBoxPatch: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.FancyBboxPatch.html # noqa: E501

    This class implements an interactive fancybbox patch based on a matplotlib
    `FancyBBoxPatch`_ object.

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
    Angle of the fancybbox in degrees measured counter-clockwise from the
    positive y-axis.
    """

    width: float
    """Width of the rectangle in axis units."""
    height: float
    """Height of the rectangle in axis units."""

    boxstyle: InitVar[str | BoxStyle] = BoxStyle("Round", pad=0.1)
    """
    Style of the FancyBBoxPatch.

    .. _BoxStyle: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.BoxStyle.html#matplotlib.patches.BoxStyle # noqa: E501

    See matplotlib's `BoxStyle`_ for more details.

    """

    plot_kwargs: InitVar[dict] = None
    """
    Optional keyword arguments passed directly to matplotlib's FancyBBoxPatch
    constructor.

    See matplotlib's `FancyBBoxPatch`_ for more information about possible arguments.

    """

    _x: _T = field(init=False, repr=False)
    """Post-processed x-axis position of the bottom left corner of the rectangle."""
    _y: _T = field(init=False, repr=False)
    """Post-processed y-axis position of the bottom left corner of the rectangle."""
    _theta: _T = field(init=False, repr=False)
    """Post-processed angle of the rectangle."""
    _patch: FancyBboxPatch = field(init=False, repr=False)
    """FancyBBoxPatch artist rendering the actual patch."""

    def __post_init__(
        self,
        x_center: np.ndarray,
        y_center: np.ndarray,
        angle_deg: np.ndarray,
        boxstyle: str | BoxStyle,
        plot_kwargs: dict,
    ) -> None:
        self._validate_data(x_center, y_center, angle_deg)
        self._x = x_center - (self.width / 2.0)
        self._y = y_center - (self.height / 2.0)
        self._theta = angle_deg

        if plot_kwargs is None:
            plot_kwargs = {}

        self._patch = FancyBboxPatch(
            xy=(self._x[0], self._y[0]),
            width=self.width,
            height=self.height,
            boxstyle=boxstyle,
            animated=True,
            **plot_kwargs,
        )

        self.ax.add_patch(self._patch)
        self.update_axis_limits()

    @property
    def len_data(self) -> int:
        return self._x.size

    @property
    def artists(self) -> list[Artist]:
        return [self._patch]

    def _update_artists(self, x: float, y: float, theta: float) -> None:
        self._patch.set_x(x)
        self._patch.set_y(y)

        x_rot = x + (self.width / 2.0)
        y_rot = y + (self.height / 2.0)
        transform = Affine2D().rotate_deg_around(x_rot, y_rot, theta)

        self._patch.set_transform(transform + self.ax.transData)

    def _get_plot_data(self) -> tuple[_T, ...]:
        x_pos = self._x[self.current_idx]
        y_pos = self._y[self.current_idx]
        angle = self._theta[self.current_idx]
        return x_pos, y_pos, angle

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        # TODO find a better way of calculating this. For now just return axis.
        xl, xr = self.ax.get_xlim()
        yb, yt = self.ax.get_ylim()
        return xl, xr, yb, yt

    def _validate_data(self, x_center: _T, y_center: _T, angle: _T):
        if not x_center.shape == y_center.shape:
            raise InconsistentArrayShape(x_shape=x_center.shape, y_shape=y_center.shape)
        if not x_center.shape == angle.shape:
            raise InconsistentArrayShape(x_shape=x_center.shape, y_shape=angle.shape)
        if not x_center.ndim == 1:
            raise ArrayNot1D(ndim=x_center.ndim)
