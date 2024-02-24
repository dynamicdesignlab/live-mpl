""" live_phase_portrait

This module implements the LivePhasePort concrete class and associated functions.
Use this module to create interactive phase portrait plots.

"""

__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2023"
__date__ = "2023/04/09"
__license__ = "MIT"

import functools
import pickle
import warnings
from collections import deque
from dataclasses import InitVar, dataclass, field
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrowPatch
from rich import progress
from typing_extensions import Self

from . import streamplot
from .live_base import LiveBase

ProgBar = progress.Progress(
    progress.TextColumn("[cyan]Calculating Streamplots..."),
    progress.BarColumn(),
    progress.MofNCompleteColumn(),
    progress.TimeElapsedColumn(),
)


def pool_func(
    axes: Axes, x_data: np.ndarray, y_data: np.ndarray, plot_args: dict[str, Any], args
) -> tuple[LineCollection, list[FancyArrowPatch]]:
    u_data, v_data, color_data = args
    return streamplot.calc_streamplot(
        axes=axes, x=x_data, y=y_data, u=u_data, v=v_data, color=color_data, **plot_args
    )


def plot_kwargs_factory() -> dict[str, Any]:
    return {"cmap": "viridis", "broken_streamlines": True, "density": 1.8}


@dataclass
class LiveStreamlines(LiveBase):
    """LiveLine

    This is a concrete implementation for a live line plot. This class
    will render interactive line plots given iterables of data.

    """

    x_data: np.ndarray
    y_data: np.ndarray
    u_data: np.ndarray
    v_data: np.ndarray
    color_data: np.ndarray

    bounds: InitVar[tuple[float, float, float, float]] = None
    plot_kwargs: InitVar[dict[str, Any]] = None

    _bounds: tuple[float, float, float, float] = field(init=False, repr=False)
    _current_lines: LineCollection = field(init=False, repr=False)
    _streamlines: list[LineCollection] = field(default_factory=list, repr=False)
    _streamarrows: list[list[FancyArrowPatch]] = field(default_factory=list, repr=False)
    _plot_kwargs: dict[str, Any] = field(
        default_factory=plot_kwargs_factory, repr=False
    )

    @property
    def artists(self) -> list[Artist]:
        return [item for item in self._current_arrows] + [self._current_lines]

    @property
    def _current_arrows(self):
        return [
            item for item in self.ax.get_children() if isinstance(item, FancyArrowPatch)
        ]

    def _get_data_axis_limits(self) -> tuple[float, float, float, float]:
        """Update Axis Limits

        This method will scale the axes larger as needed to fit
        the data to be plotted. This sets the axis limits to bound the maximum
        and minimum values throughout the data.

        """
        return self._bounds

    def _update_artists(self, lines: LineCollection, arrows: list[FancyArrowPatch]):
        if lines is None:
            return

        try:
            self._current_lines.remove()
        except AttributeError:
            pass

        for item in self._current_arrows:
            item.remove()

        transform = self.ax.transData

        lines.set_transform(transform)
        self.ax.add_collection(lines)

        for item in arrows:
            item.set_transform(transform)
            self.ax.add_patch(item)

        self._current_lines = lines

    def _get_plot_data(self, idx: int) -> tuple[LineCollection, list[FancyArrowPatch]]:
        if not self._streamlines:
            warnings.warn(
                (
                    'User must call either the "calc_streamplots" or '
                    '"load_from_pickle" function before plot will be visible',
                )
            )
            return None, None

        return self._streamlines[idx], self._streamarrows[idx]

    def __post_init__(
        self, bounds: tuple[float] = None, plot_kwargs: dict[str, Any] = None
    ):
        if plot_kwargs:
            self._plot_kwargs |= plot_kwargs

        if bounds is None:
            self._bounds = (
                np.min(self.x_data),
                np.max(self.x_data),
                np.min(self.y_data),
                np.max(self.y_data),
            )
        else:
            self._bounds = bounds

        self.update_axis_limits()

    def calc_streamlines(self, num_workers: int = 4):
        num_epochs = self.u_data.shape[-1]

        ulist = [self.u_data[..., idx] for idx in range(num_epochs)]
        vlist = [self.v_data[..., idx] for idx in range(num_epochs)]
        clist = [self.color_data[..., idx] for idx in range(num_epochs)]

        arg_iter = zip(ulist, vlist, clist)
        func = functools.partial(
            pool_func, self.ax, self.x_data, self.y_data, self._plot_kwargs
        )
        results = deque()

        with ProgBar as prog:
            with Pool(processes=num_workers) as pool:
                for item in prog.track(pool.imap(func, arg_iter), total=num_epochs):
                    results.append(item)

        self._streamlines = [line for (line, _) in results]
        self._streamarrows = [arrow for (_, arrow) in results]

    def asdict(self) -> dict[str, Any]:
        return {
            "x_data": self.x_data,
            "y_data": self.y_data,
            "u_data": self.u_data,
            "v_data": self.v_data,
            "color_data": self.color_data,
            "_streamlines": self._streamlines,
            "_streamarrows": self._streamarrows,
        }

    def pickle(self, pickle_path: Path):
        with open(pickle_path, "wb") as file:
            pickle.dump(self.asdict(), file)

    @classmethod
    def load_from_pickle(cls, pickle_path: Path) -> Self:
        with open(pickle_path, "rb") as file:
            stream_dict = pickle.load(file)

        return cls(**stream_dict)
