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

"""This module implements the Tab class."""
__author__ = "John Talbot"
__contact__ = "jtalbot.me@gmail.com"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from dataclasses import InitVar, dataclass, field
from typing import Any, List

import gi
from matplotlib.axes import Axes
from matplotlib.backends import backend_gtk3, backend_gtk3agg
from matplotlib.figure import Figure

from .live_base import LiveBase

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402 - import must be under previous line


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

    def _update_all(self, idx: int):
        """
        Update all registered live with new index.

        Parameters
        ----------
        idx:
            New data index

        """
        for plot in self._plots:
            plot._update_plot(idx)

        self._set_idx_msg(idx)

    def _redraw_artists(self):
        """Redraw all plot artists."""
        for plot in self._plots:
            plot._redraw_artists()

    def update_all_axis_limits(self):
        """Calls the update axis method on all registered plots."""
        for plot in self._plots:
            plot.update_axis_limits()

    def _set_idx_msg(self, idx: int):
        self._idx_label.set_markup(f"<small>{idx}</small>")
        self._idx_label.set_label(f"Index = {idx}")

    def __post_init__(self, suptitle: str):
        self._page = Gtk.VBox()
        self._figure = Figure(tight_layout=True)
        self._canvas = backend_gtk3agg.FigureCanvasGTK3Agg(self._figure)
        self._page.pack_start(self._canvas, True, True, 0)

        self._bottom_box = Gtk.Box()
        self._page.pack_start(self._bottom_box, False, False, 0)

        self._toolbar = backend_gtk3.NavigationToolbar2GTK3(canvas=self._canvas)
        self._idx_label = Gtk.Label()
        self._idx_label.set_justify(Gtk.Justification.RIGHT)

        self._bottom_box.pack_start(self._toolbar, False, False, 0)
        self._bottom_box.pack_start(self._idx_label, False, False, 0)
        self._figure.suptitle(suptitle)
