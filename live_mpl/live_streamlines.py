""" live_phase_portrait

This module implements the LivePhasePort concrete class and associated functions.
Use this module to create interactive phase portrait plots.

"""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2023"
__date__ = "2023/04/09"
__license__ = "MIT"

from dataclasses import dataclass, field
from typing import Any
from pathlib import Path
from matplotlib.artist import Artist

import pickle
import functools
from multiprocessing import Pool
from matplotlib import axis
from collections import deque
import warnings
import numpy as np
from matplotlib.patches import FancyArrowPatch
from matplotlib.collections import LineCollection
from rich import progress

from .live_base import LiveBase
from . import streamplot

ProgBar = progress.Progress(
    progress.TextColumn("[cyan]Calculating Streamplots..."),
    progress.BarColumn(),
    progress.MofNCompleteColumn(),
    progress.TimeElapsedColumn(),
)


def pool_func(
    axes: axis, x_data: np.ndarray, y_data: np.ndarray, plot_args: dict[str, Any], args
) -> tuple[LineCollection, list[FancyArrowPatch]]:
    u_data, v_data, color_data = args
    return streamplot.calc_streamplot(
        axes=axes, x=x_data, y=y_data, u=u_data, v=v_data, color=color_data, **plot_args
    )


@dataclass
class LiveStreamlines(LiveBase):
    """LiveLine

    This is a concrete implementation for a live line plot. This class
    will render interactive line plots given iterables of data.

    """

    _current_lines: LineCollection = field(init=False, repr=False)
    _current_arrows: list[FancyArrowPatch] = field(
        init=False, repr=False, default_factory=list
    )
    _streamlines: list[LineCollection] = field(default_factory=list, repr=False)
    _streamarrows: list[list[FancyArrowPatch]] = field(default_factory=list, repr=False)

    @property
    def artist(self) -> Artist:
        return None

    def __post_init__(self) -> None:
        super().__post_init__()

    def calc_streamlines(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        u_data: np.ndarray,
        v_data: np.ndarray,
        color_data: np.ndarray,
        plot_args: dict[str, Any] = None,
        num_workers: int = 4,
    ) -> None:
        self.set_axis_limits(x_data=x_data, y_data=y_data)
        num_epochs = u_data.shape[-1]

        ulist = [u_data[..., idx] for idx in range(num_epochs)]
        vlist = [v_data[..., idx] for idx in range(num_epochs)]
        clist = [color_data[..., idx] for idx in range(num_epochs)]

        arg_iter = zip(ulist, vlist, clist)
        func = functools.partial(pool_func, self.plot_axis, x_data, y_data, plot_args)
        results = deque()

        with ProgBar as prog:
            with Pool(processes=num_workers) as pool:
                for item in prog.track(pool.imap(func, arg_iter), total=num_epochs):
                    results.append(item)

        self._streamlines = [line for (line, _) in results]
        self._streamarrows = [arrow for (_, arrow) in results]

    def redraw_plot(self, lines: LineCollection, arrows: list[FancyArrowPatch]) -> None:
        if lines is None:
            return

        try:
            self._current_lines.remove()
        except AttributeError:
            pass

        for item in self.plot_axis.get_children():
            if isinstance(item, FancyArrowPatch):
                item.remove()

        transform = self.plot_axis.transData

        lines.set_transform(transform)
        self.plot_axis.add_collection(lines)

        for item in arrows:
            item.set_transform(transform)
            self.plot_axis.add_patch(item)

        self._current_lines = lines

    def redraw_artist(self) -> None:
        pass

    def get_new_plot_data(self) -> tuple[LineCollection, list[FancyArrowPatch]]:
        if not self._streamlines:
            warnings.warn(
                (
                    'User must call either the "calc_streamplots" or '
                    '"load_from_pickle" function before plot will be visible',
                )
            )
            return None, None

        return self._streamlines[self.current_idx], self._streamarrows[self.current_idx]

    def asdict(self) -> dict[str, Any]:
        return {"streamlines": self._streamlines, "streamarrows": self._streamarrows}

    def pickle(self, pickle_path: Path) -> None:
        with open(pickle_path, "wb") as file:
            pickle.dump(self.asdict(), file)

    def load_from_pickle(self, pickle_path: Path) -> None:
        with open(pickle_path, "rb") as file:
            stream_dict = pickle.load(file)

        self._streamlines = stream_dict["streamlines"]
        self._streamarrows = stream_dict["streamarrows"]

    @property
    def len_data(self) -> None:
        return len(self._streamlines)

    def set_axis_limits(self, x_data: np.ndarray, y_data: np.ndarray) -> None:
        """Update Axis Limits

        This method will scale the axes larger as needed to fit
        the data to be plotted. This sets the axis limits to bound the maximum
        and minimum values throughout the data.

        """
        xmin, xmax = np.min(x_data), np.max(x_data)
        self.plot_axis.set_xlim(xmin=xmin, xmax=xmax)

        ymin, ymax = np.min(y_data), np.max(y_data)
        self.plot_axis.set_ylim(ymin=ymin, ymax=ymax)
