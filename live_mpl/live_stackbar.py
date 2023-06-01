""" live_stackbar

This module implements the LiveStackBar concrete class and associated functions.
Use this module to create interactive stacked bar plots

"""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import InitVar, dataclass, field
from typing import Iterable, Tuple
from matplotlib.artist import Artist

import numpy as np

from .live_base import LiveBase


@dataclass
class LiveStackBar(LiveBase):
    """LiveStackBar

    This is a concrete implementation for a live stacked bar plot. This class
    will render interactive bars.

    """

    x_data: InitVar[np.ndarray]
    """ X-Axis data to plot """
    y_data: InitVar[np.ndarray]
    """ Y-Axis data to plot """

    labels: Iterable[str]
    """ Legend label for plot """

    colors: InitVar[np.ndarray] = field(repr=False, default=None)

    traverse_rows: bool = True
    """ Flag to traverse rows (default True)"""

    _bar_plots: object = field(init=False, repr=False)
    """ Keep account of bar objects here"""

    _xdata: np.ndarray = field(init=False, repr=False)
    _ydata: np.ndarray = field(init=False, repr=False)
    _num_epochs: int = field(init=False, repr=False)
    _num_bars: int = field(init=False, repr=False)

    @property
    def num_bars(self):
        return self._num_bars

    @property
    def num_epochs(self):
        return self._num_epochs

    def __post_init__(
        self, x_data: np.ndarray, y_data: np.ndarray, colors: np.ndarray
    ) -> None:
        if self.traverse_rows:
            y_data_transform = y_data
        else:
            y_data_transform = tuple([item.T for item in y_data])

        self._num_epochs = y_data_transform[0].shape[0]
        self._num_bars = y_data_transform[0].shape[1]

        if x_data is None:
            x_data_transform = np.arange(self.num_bars)
        else:
            x_data_transform = x_data

        self.data_error_checks(x_data_transform, y_data_transform)

        self._xdata = x_data_transform
        self._ydata = y_data_transform
        self.heights = self.calc_heights()

        super().__post_init__()

        x_plot, y_plot = self.get_new_plot_data()

        barplot_list = []
        bottom = np.zeros(self.num_bars)
        for idx, (y_item, label) in enumerate(zip(y_plot, self.labels)):
            if colors is not None:
                bar_color = colors[idx, ...]

                barplot = self.axis.bar(
                    x=x_plot,
                    height=y_item,
                    bottom=bottom,
                    label=label,
                    align="center",
                    animated=True,
                    color=bar_color,
                )

            else:
                barplot = self.axis.bar(
                    x=x_plot,
                    height=y_item,
                    bottom=bottom,
                    label=label,
                    align="center",
                    animated=True,
                )

            bottom += y_item

            barplot_list.append(barplot)

        self._bar_plots = tuple(barplot_list)

    @property
    def artist(self) -> Artist:
        return self._bar_plots[0]

    def calc_heights(self):
        heights = np.zeros(self._ydata[0].shape)

        for y_array in self._ydata:
            heights += y_array

        return np.max(heights, axis=1)

    def redraw_plot(self, plot_x: np.ndarray, plot_y: np.ndarray) -> None:
        bottom = np.zeros(self.num_bars)
        for barplot, y_plot in zip(self._bar_plots, plot_y):
            for idx, rect in enumerate(barplot):
                rect.set_height(y_plot[idx])
                rect.set_y(bottom[idx])
            bottom += y_plot

        self.update_axis_limits()

    def redraw_artist(self) -> None:
        for barplot in self._bar_plots:
            for rect in barplot:
                self.plot_axis.draw_artist(rect)

    def get_new_plot_data(self) -> Tuple[np.ndarray, np.ndarray]:
        plot_y = [item[self.current_idx, ...] for item in self._ydata]
        return self._xdata, tuple(plot_y)

    def data_error_checks(self, x_data: np.ndarray, y_data: Tuple[np.ndarray]):
        """Data error checks

        Performs initial checks on data to verify it can be
        plotted correctly. These are defaults, but this
        method can be overwritten if data needs change.

        """
        y_shape = y_data[0].shape
        for item in y_data:
            if not item.shape == y_shape:
                raise ValueError("Y data is not a consistent shape")

        if x_data is not None:
            if x_data.ndim > 1 or not x_data.size == self.num_bars:
                raise ValueError(
                    "X must be None or a 1 dimensional with same length as the"
                    "non-traversing axis of Y"
                )

    @property
    def len_data(self) -> None:
        return self.num_epochs

    def update_axis_limits(self) -> None:
        yheight = self.heights[self.current_idx]
        self.plot_axis.set_ylim(ymin=0.0, ymax=yheight)
