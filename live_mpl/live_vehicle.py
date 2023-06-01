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

"""This module implements functions to create a live vehicle plot."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from matplotlib.patches import Rectangle
from enum import Enum
from dataclasses import dataclass
import functools

import numpy as np

from .live_image import LiveImage
from .live_fancy_bbox import LiveFancyBBox
from .live_base import LiveBase
from .exceptions import InconsistentArrayShape, ArrayNot1D
from matplotlib.axes import Axes
from pathlib import Path

_T = np.ndarray


@dataclass
class LiveVehicleConfig:
    """Configuration class controlling the appearance of the vehicle."""

    veh_width: float = 2.0
    """Width of the vehicle in axis units."""
    veh_height: float = 4.5
    """Height of the vehicle in axis units."""
    veh_color: str = "blue"
    """Color of the vehicle."""
    veh_alpha: float = 0.7
    """Transparency of the vehicle."""

    tire_width: float = 0.2
    """Width of the tires in axis units."""
    tire_height: float = 1.125
    """Height of the tires in axis units."""
    tire_color: str = "black"
    """Color of the tires."""
    tire_alpha: float = 0.7
    """Transparency of the tires."""

    image_path: Path = None
    """If supplied, this will place the specified image in the center of the vehicle."""


class _TireEnum(Enum):
    FL = (0.5, -0.5, 0.5, -0.8)
    FR = (0.5, -0.5, -0.5, 0.8)
    RL = (-0.5, 0.5, 0.5, -0.8)
    RR = (-0.5, 0.5, -0.5, 0.8)

    def get_body_position(self, config: LiveVehicleConfig) -> tuple[float, float]:
        a, b, c, d = self.value
        body_x = a * config.veh_height + b * config.tire_height
        body_y = c * config.veh_width + d * config.tire_width
        return body_x, body_y


def create_live_vehicle(
    ax: Axes,
    x_center: _T,
    y_center: _T,
    angle_deg: _T,
    steering_deg: _T,
    config: LiveVehicleConfig = None,
) -> list[LiveBase]:
    """
    Create a live vehicle plot by building several fancybbox plots around a vehicle's
    position data.

    Parameters
    ----------
    ax:
        Matplotlib axis to plot on
    x_data:
        1-Dimensional x-axis position of vehicle center.
    y_data:
        1-Dimensional y-axis position of vehicle center.
    angle_deg:
        Angle of the vehicle in degrees measured counter-clockwise from the
        positive y-axis.
    steering_deg:
        Angle of the front wheel in degrees measured counter-clockwise from the
        direction the vehicle is pointing.
    config:
        Configuration class controlling vehicle appearance


    """
    if config is None:
        config = LiveVehicleConfig()

    _validate_data(x_center, y_center, angle_deg, steering_deg)

    plots = []

    plots.append(_create_vehicle_body(ax, x_center, y_center, angle_deg, config))

    partial_tire = functools.partial(
        _create_tire, ax, x_center, y_center, angle_deg, config
    )
    plots += [partial_tire(steering_deg, tire) for tire in _TireEnum]

    if config.image_path is not None:
        plots.append(_create_image(ax, x_center, y_center, angle_deg, config))

    return plots


def _create_vehicle_body(
    ax: Axes,
    east_m: _T,
    north_m: _T,
    psi_deg: _T,
    config: LiveVehicleConfig,
) -> LiveFancyBBox:
    return LiveFancyBBox(
        ax=ax,
        x_center=east_m,
        y_center=north_m,
        angle_deg=psi_deg,
        width=config.veh_width,
        height=config.veh_height,
        plot_kwargs={
            "facecolor": config.veh_color,
            "edgecolor": "black",
            "alpha": config.veh_alpha,
            "zorder": 2.0,
            "label": "Vehicle",
        },
    )


def _create_image(
    ax: Axes,
    east_m: _T,
    north_m: _T,
    psi_rad: _T,
    config: LiveVehicleConfig,
) -> LiveImage:
    image_extent = [
        -config.veh_width / 4,
        config.veh_width / 4,
        -config.veh_height / 4,
        config.veh_height / 4,
    ]

    return LiveImage(
        ax=ax,
        x_data=east_m,
        y_data=north_m,
        theta_rad=psi_rad,
        image_extent=image_extent,
        image_path=config.image_path,
        plot_kwargs={"zorder": 3.0},
    )


def _create_tire(
    ax: Axes,
    east_m: _T,
    north_m: _T,
    psi_deg: _T,
    config: LiveVehicleConfig,
    delta_deg: _T,
    tire: _TireEnum,
) -> tuple[Rectangle, ...]:
    psi_rad = np.radians(psi_deg)

    tire_angle_deg = psi_deg
    if tire == _TireEnum.FL or tire == _TireEnum.FR:
        tire_angle_deg = _calc_tire_angle(psi_deg=psi_deg, delta_deg=delta_deg)

    tire_x, tire_y = tire.get_body_position(config)
    body_east, body_north = _body_to_global_position(
        x_m=tire_x, y_m=tire_y, psi_rad=psi_rad
    )
    tire_east = body_east + east_m
    tire_north = body_north + north_m

    return LiveFancyBBox(
        ax=ax,
        x_center=tire_east,
        y_center=tire_north,
        angle_deg=tire_angle_deg,
        width=config.tire_width,
        height=config.tire_height,
        plot_kwargs={
            "facecolor": config.tire_color,
            "edgecolor": "black",
            "alpha": config.tire_alpha,
            "zorder": 2.0,
        },
    )


def _calc_tire_angle(psi_deg: _T, delta_deg: _T) -> _T:
    return psi_deg + delta_deg


def _body_to_global_position(x_m: float, y_m: float, psi_rad: _T) -> tuple[_T, _T]:
    rot_array = _enu_to_xyu_rotation(psi_rad)
    pos_xy = np.array([[x_m], [y_m]])
    pos_en = (pos_xy.T @ rot_array).squeeze()
    return pos_en[0, ...], pos_en[1, ...]


def _enu_to_xyu_rotation(psi_rad: _T) -> _T:
    return np.array(
        [[-np.sin(psi_rad), -np.cos(psi_rad)], [np.cos(psi_rad), -np.sin(psi_rad)]]
    )


def _validate_data(x: _T, y: _T, angle: _T, steering: _T):
    if not x.shape == y.shape:
        raise InconsistentArrayShape(x_shape=x.shape, y_shape=y.shape)
    if not x.shape == angle.shape:
        raise InconsistentArrayShape(x_shape=x.shape, y_shape=angle.shape)
    if not x.shape == steering.shape:
        raise InconsistentArrayShape(x_shape=x.shape, y_shape=steering.shape)
    if not x.ndim == 1:
        raise ArrayNot1D(ndim=x.ndim)
