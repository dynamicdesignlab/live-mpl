"""This module implements the Tab class."""

import enum
from dataclasses import InitVar, dataclass, field
from typing import Any, List

import gi
from matplotlib.axes import Axes
from matplotlib.backends import backend_gtk3, backend_gtk3agg
from matplotlib.figure import Figure

from .live_base import LiveBase

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402 - import must be under previous line


class CallbackActionsEnum(enum.Enum):
    """Enumeration of possible actions to take on a Tab."""

    INCREMENT = enum.auto()
    DECREMENT = enum.auto()
    END = enum.auto()
    BEGIN = enum.auto()
    REDRAW = enum.auto()


class _NavigationToolbarNoCoordinates(backend_gtk3.NavigationToolbar2GTK3):
    """Custom toolbar without the normal coordinate readout of the default toolbar."""

    def set_message(self, s):
        pass


@dataclass
class Tab:
    """
    .. _Axes: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes # noqa E501

    This class implements an GTK notebook tab on which to create matplotlib
    `Axes`_ for both classic and interactive plots.

    Note
    ----
        For the Tab to work properly, it must be registered to an existing
        :class:`~live_mpl.window.Window` instance using the
        :meth:`~live_mpl.window.Window.register_tab` method.

    See Also
    --------
    :class:`~live_mpl.window.Window`

    """

    tab_name: str
    """Name of tab."""

    suptitle: InitVar[str] = None
    """Supertitle to use for all subplots."""

    _figure: Figure = field(init=False, repr=False, default=None)
    """Matplotlib figure to draw axes on."""
    _canvas: backend_gtk3agg.FigureCanvasGTK3Agg = field(
        init=False, repr=False, default=None
    )
    """Matplotlib canvas to render images onto."""

    _bg: Any = field(init=False, repr=False, default=None)
    """Matplotlib canvas to render images onto."""

    _plots: List[LiveBase] = field(init=False, repr=False, default_factory=list)
    """List of LiveBase plots this tab controls."""

    @property
    def figure(self) -> Figure:
        return self._figure

    def add_subplot(self, *args, **kwargs) -> Axes:
        """
        Create matplotlib axis on this tab.

        .. _add_subplot: https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure.add_subplot # noqa E501

        This follows the arguments of the matplotlib `add_subplot`_ function.

        Returns
        -------
            Axis handle

        """
        ax = self._figure.add_subplot(*args, **kwargs)
        # ax.callbacks.connect("xlim_changed", self.save_bg)
        # ax.callbacks.connect("ylim_changed", self.save_bg)
        return ax

    def register_plot(self, plot: LiveBase):
        """
        Add the given LiveBase plot to the Tab and register it to be updated by
        the Tab. This is a necessary step in making the plot interactive.

        Parameters
        ----------
        plot:
            Plot to make interactive

        """
        self._plots.append(plot)

    def _save_bg(self):
        """Save this tab's background so it can be restored later for blitting."""
        self._canvas.draw()
        self._bg = self._canvas.copy_from_bbox(self._figure.bbox)

    def _draw_bg(self):
        """Draw this tab's saved background."""
        self._canvas.restore_region(self._bg)

    def _blit(self):
        """Blit this tab's plots."""
        self._canvas.blit(self._figure.bbox)
        self._canvas.flush_events()

    def _increment_all(self, step: int):
        """
        Increment all registered live plots by step.

        Parameters
        ----------
        step:
            Amount to increase plot data indices

        """
        for plot in self._plots:
            plot._increment(step)
            plot._update_plot()

    def _decrement_all(self, step: int):
        """
        Decrement all registered live plots by step.

        Parameters
        ----------
        step:
            Amount to decrease plot data indices

        """
        for plot in self._plots:
            plot._decrement(step)
            plot._update_plot()

    def _jump_all_to_end(self):
        """Jump all plots to their last data item."""
        for plot in self._plots:
            plot._jump_to_end()
            plot._update_plot()

    def _jump_all_to_beginning(self):
        """Jump all plots to their firse data item."""
        for plot in self._plots:
            plot._jump_to_beginning()
            plot._update_plot()

    def _redraw_artists(self):
        """Redraw all plot artists."""
        for plot in self._plots:
            plot._redraw_artists()

    def update_all_axis_limits(self):
        """Calls the update axis method on all registered plots."""
        for plot in self._plots:
            plot.update_axis_limits()

    def _take_action(self, action: CallbackActionsEnum, step: int = None):
        """
        Given an action and params, take that action on all plots

        Parameters
        ----------
        action: CallbackActionsEnum
            Action to take on all plots
        step:
            Amount to increase or decreas plot data index

        """
        if action == CallbackActionsEnum.INCREMENT:
            self._increment_all(step)
        elif action == CallbackActionsEnum.DECREMENT:
            self._decrement_all(step)
        elif action == CallbackActionsEnum.END:
            self._jump_all_to_end()
        elif action == CallbackActionsEnum.BEGIN:
            self._jump_all_to_beginning()
        elif action == CallbackActionsEnum.REDRAW:
            self._redraw_artists()
        else:
            raise NotImplementedError

    def __post_init__(self, suptitle: str):
        self._page = Gtk.VBox()
        self._figure = Figure(tight_layout=True)
        self._canvas = backend_gtk3agg.FigureCanvasGTK3Agg(self._figure)
        self._page.pack_start(self._canvas, True, True, 0)

        self._bottom_box = Gtk.Box()
        self._page.pack_start(self._bottom_box, False, False, 0)

        # toolbar = _NavigationToolbarNoCoordinates(self._canvas, self._page)
        toolbar = _NavigationToolbarNoCoordinates(self._canvas)

        self._init_figure(toolbar, suptitle)

    def _init_figure(self, toolbar: backend_gtk3.NavigationToolbar2GTK3, suptitle: str):
        """
        Initialize figure with custom toolbar

        Parameters
        ----------
        toolbar:
            Toolbar to use with figure.

        """
        toolbar.update()
        self._bottom_box.pack_start(toolbar, False, False, 0)
        self._figure.suptitle(suptitle)
