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

"""This module implements the LiveImage concrete LiveBase child class."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import InitVar, dataclass, field
from pathlib import Path

import numpy as np
from matplotlib.artist import Artist
from matplotlib.image import AxesImage
from matplotlib.transforms import Affine2D
from PIL import Image

from .exceptions import ArrayNot1D, InconsistentArrayShape
from .live_base import LiveBase

_T = np.ndarray


@dataclass
class LiveImage(LiveBase):
    """
    .. _AxesImage: https://matplotlib.org/stable/api/image_api.html # noqa: E501

    This class implements an interactive image based on a matplotlib
    `AxesImage`_ object.

    Raises
    ------
    InconsistentArrayShape
        If `x_data` and `y_data` do not have the same shape.
    ArrayNot1D
        If `x_data` or `y_data` has more than one dimension.

    """

    x_center: InitVar[_T]
    """1-Dimensional x-axis position of image center."""
    y_center: InitVar[_T]
    """1-Dimensional y-axis position of image center."""
    angle_deg: InitVar[_T]
    """
    Angle of the image in degrees measured counter-clockwise from the
    positive y-axis.
    """

    image_extent: list[float, float, float, float]
    """
    Extent of image in axis units.

    This sets the size of the image.
    """

    image_path: InitVar[Path]
    """Path to image."""

    animated: bool = True
    """Whether plot should be animated or not."""

    plot_kwargs: InitVar[dict] = None
    """
    Optional keyword arguments passed directly to matplotlib's AxesImage
    contstructor.

    See matplotlib's `AxesImage`_ for more information about possible arguments.

    """

    _x: _T = field(init=False, repr=False)
    """Post-processed x-axis position of the bottom left corner of the rectangle."""
    _y: _T = field(init=False, repr=False)
    """Post-processed y-axis position of the bottom left corner of the rectangle."""
    _theta: _T = field(init=False, repr=False)
    """Post-processed angle of the rectangle."""
    _image: AxesImage = field(init=False, repr=False)
    """Image artist rendering the actual patch."""

    def __post_init__(
        self,
        x_center: _T,
        y_center: _T,
        angle_deg: _T,
        image_path: Path,
        plot_kwargs: dict,
    ):
        self._validate_data(x_center, y_center, angle_deg)
        self._x = x_center
        self._y = y_center
        self._theta = angle_deg

        if plot_kwargs is None:
            plot_kwargs = {}

        self._image = AxesImage(
            self.ax, extent=self.image_extent, animated=self.animated, **plot_kwargs
        )
        self._image.set_data(Image.open(image_path))

    @property
    def artists(self) -> list[Artist]:
        return [self._image]

    def _update_artists(self, idx: int, x: float, y: float, theta: float):
        transform = Affine2D().rotate_deg(theta).translate(x, y)
        self._image.set_transform(transform + self.ax.transData)

    def _get_plot_data(self, idx: int) -> tuple[_T, ...]:
        x_pos = self._x[idx]
        y_pos = self._y[idx]
        angle = self._theta[idx]
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
