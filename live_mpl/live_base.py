"""

This module implements the LiveBase abstract class.

Users can subclass the LiveBase class and implement the designated abstract
methods to derive new live plotting concrete classes.  Concrete live plotting
classes are a wrapper around a matplotlib artist containing iterable data
allowing the user to scroll through or animated the data.

"""

import abc
from dataclasses import dataclass, field

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

    _idx: int = field(init=False, repr=False, default=0)
    """Current index of iterable data."""

    @property
    @abc.abstractmethod
    def len_data(self) -> int:
        """Length of iterable plot data."""

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
    def _get_plot_data(self) -> tuple[np.ndarray | list[np.ndarray]]:
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

    @property
    def current_idx(self) -> int:
        """Current plot data index."""
        return self._idx

    @property
    def max_idx(self) -> int:
        """Maximum allowed plot data index."""
        if self.len_data < 1:
            return 0

        return self.len_data - 1

    def _increment(self, step: int):
        """
        Increment the data index of this plot by step.

        Parameters
        ----------
        step:
            Amount to increase data index

        """
        self._idx += step

        if self._idx > self.max_idx:
            self._idx = self.max_idx

    def _decrement(self, step: int):
        """
        Decrement the data index of this plot by step.

        Parameters
        ----------
        step:
            Amount to decrease data index

        """
        self._idx -= step

        if self._idx < 0:
            self._idx = 0

    def _jump_to_end(self):
        """Move data index to the end of plotting data."""
        self._idx = self.max_idx

    def _jump_to_beginning(self):
        """Move data index to the beginning of plotting data."""
        self._idx = 0

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

    def _update_plot(self):
        """
        Update plot by fetching new data and piping it to the appropriate
        `update_artist` method.

        """
        self._update_artists(*self._get_plot_data())

    def _animate_step(self, step: int):
        """
        Increment the data index by step and then update the plot.

        This method is used in the animation function to step the plot along as
        it captures each frame.

        Parameters
        ----------
        step:
            Amount to increment data index

        """
        self._increment(step=step)
        self._update_plot()
