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

"""

This module implements the LiveBase abstract class.

Users can subclass the LiveBase class and implement the designated abstract
methods to derive new live plotting concrete classes.  Concrete live plotting
classes are a wrapper around a matplotlib artist containing iterable data
allowing the user to scroll through or animated the data.

"""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

import abc
from dataclasses import dataclass

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes

_AXIS_SCALE_FACTOR = 0.05


@dataclass
class LiveBase(abc.ABC):
    """LiveBase

    Implements the interface definition of live plotting classes.

    Users can subclass the LiveBase class and implement the designated abstract
    methods to derive new live plotting concrete classes.  Concrete live
    plotting classes are a wrapper around a matplotlib artist containing
    iterable data allowing the user to scroll through or animated the data.

    """

    ax: Axes
    """Matplotlib axis to plot on."""

    @property
    @abc.abstractmethod
    def artists(self) -> list[Artist]:
        """Matplotlib artists associated with plot"""

    @abc.abstractmethod
    def _update_artists(self, *data_args: tuple[np.ndarray]):
        """
        Method to update artist given new data.

        :meta public:

        Parameters
        ----------
        data_args:
            Tuple of data output by `get_plot_data`

        """

    @abc.abstractmethod
    def _get_plot_data(self, idx: int) -> tuple[np.ndarray | list[np.ndarray]]:
        """
        Method returning new data to plot.

        :meta public:

        Returns
        -------
        new_data:
            Tuple of data expected by `update_artist`
        """

    @abc.abstractmethod
    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        """
        Return the axis limits for the current data.

        :meta public:

        Returns
        -------
        x_lower:
            Lower limit of x-axis
        x_upper:
            Upper limit of x-axis
        y_lower:
            Lower limit of y-axis
        y_upper:
            Upper limit of y-axis

        """

    def update_axis_limits(self, scale_factor: float = _AXIS_SCALE_FACTOR):
        """
        Set new axis limits given the current state of the plot.

        New axis limits are extended by scale_factor to give some buffer
        along the edges of the plot.

        Parameters
        ----------
        scale_factor:
            Factor to extend axis limits to give some visual buffer

        """
        xl, xr, yb, yt = self._get_data_axis_limits()

        xl_ax, xr_ax = self.ax.get_xlim()
        yb_ax, yt_ax = self.ax.get_ylim()

        if self.ax.xaxis_inverted():
            xl = np.nanmax([xl, xl_ax])
            xr = np.nanmin([xr, xr_ax])
        else:
            xl = np.nanmin([xl, xl_ax])
            xr = np.nanmax([xr, xr_ax])

        if self.ax.yaxis_inverted():
            yb = np.nanmax([yb, yb_ax])
            yt = np.nanmin([yt, yt_ax])
        else:
            yb = np.nanmin([yb, yb_ax])
            yt = np.nanmax([yt, yt_ax])

        self.ax.set_xlim(left=xl, right=xr)
        self.ax.set_ylim(bottom=yb, top=yt)

    def _redraw_artists(self):
        """Redraw plot artist on canvas for blitting."""
        for artist in self.artists:
            self.ax.draw_artist(artist)

    def _update_plot(self, idx: int):
        """
        Update plot by fetching new data and piping it to the appropriate
        `update_artist` method.

        """
        self._update_artists(*self._get_plot_data(idx))

    # def _animate_step(self, step: int):
    #     """
    #     Increment the data index by step and then update the plot.

    #     This method is used in the animation function to step the plot along as
    #     it captures each frame.

    #     Parameters
    #     ----------
    #     step:
    #         Amount to increment data index

    #     """
    #     self._increment(step=step)
    #     self._update_plot()
