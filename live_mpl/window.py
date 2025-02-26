"""This module implements the Window class."""

import os
import threading
from dataclasses import InitVar, dataclass, field
from typing import List

import gi
import seaborn as sns
from matplotlib import pyplot as plt

from .tab import CallbackActionsEnum, Tab

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402 - import must be under previous line

# plt.style.use("seaborn-deep")
sns.set_style("ticks")
plt.rcParams["axes.grid"] = True
plt.rcParams["savefig.directory"] = os.getcwd()

_SLOW_STEP = 1
_MEDIUM_STEP = 10
_FAST_STEP = 50


@dataclass
class Window(Gtk.Window):
    """
    This class subclasses a GTK window acting as the base for interactive plots.
    The window contains tabs which control the plotting canvas. See the
    :class:`~live_mpl.tab.Tab` class for more information on using tabs, and the
    `examples` folder for different plotting examples.

    Note
    ----
    Be sure to call the `loop` method of this class after setting up
    all desired plots.

    See Also
    --------
    :class:`~live_mpl.tab.Tab`

    """

    title: InitVar[str] = "PythonPlot"
    """Title of the plotting window."""

    slow_step: int = _SLOW_STEP
    """Amount to increment plots during slow step mode."""

    medium_step: int = _MEDIUM_STEP
    """Amount to increment plots during medium step mode."""

    fast_step: int = _FAST_STEP
    """Amount to increment plots during fast step mode."""

    _step: int = field(init=False, repr=False, default=1)
    """Data movement step size."""

    _update_lock: threading.Lock = field(
        init=False, repr=False, default_factory=threading.Lock
    )
    """Lock to debounce updates coming from user interaction."""

    _tabs: List[Tab] = field(init=False, repr=False, default_factory=list)
    """List of tabs belonging to the current window."""

    _bg_stale: bool = field(init=False, repr=False, default=True)
    """Marker that backgrounds are stale and should be redrawn."""

    _current_tab_idx: int = field(init=False, repr=False, default=0)
    """Index of current active tab."""

    _notebook: Gtk.Notebook = field(init=False, repr=False)

    def register_tab(self, tab: Tab):
        """
        Add the given tab to the Window and register it to receive
        callbacks from the Window. This is a necessary step in making
        the Tab visible and interactive.

        Parameters
        ----------
        tab:
            Tab to add to window.

        """
        self._notebook.append_page(tab._page, Gtk.Label(tab.tab_name))
        self._tabs.append(tab)

    @staticmethod
    def enable_latex() -> None:
        plt.rcParams["text.usetex"] = True

    @staticmethod
    def disable_latex() -> None:
        plt.rcParams["text.usetex"] = False

    def loop(self, start_gtk: bool = True):
        """
        Sets the gui mainloop watching for events.

        The `start_gtk` parameter allows the use of multiple windows.
        Either set this true on the last call or call `Gtk.main()` manually
        after setting up the last window.

        Note
        ----
        This method must be called at the end of the plotting script.

        Parameters
        ----------
        start_gtk:
            Start GTK main loop in addition

        """
        self.show_all()
        self._notebook.connect("switch-page", self._tab_change_callback)

        if start_gtk:
            self.start_gtk()

    @staticmethod
    def start_gtk() -> None:
        Gtk.main()

    @property
    def current_tab(self) -> Tab:
        """Return the handle for the current active tab."""
        return self._tabs[self._current_tab_idx]

    def __post_init__(self, title: str = "PythonPlot"):
        super().__init__(title=title)

        self._notebook = Gtk.Notebook()
        self._notebook.set_scrollable(True)
        self.add(self._notebook)

        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self._keyboard_callback)
        self.connect("scroll-event", self._mouse_scroll_callback)
        self.connect("configure-event", self._mark_backgrounds_stale)

    def _tab_change_callback(self, notebook, page, page_num):
        """
        Callback for a tab change in the window.

        This method will save the current tab's background and
        redraw it to get ready for blitting.

        """
        self._current_tab_idx = page_num
        self.current_tab._save_bg()
        self.current_tab._draw_bg()

    def _mark_backgrounds_stale(self, widget, event):
        """Set backgrounds stale flag so that backgrounds will be redrawn."""
        self._bg_stale = True

    def _mouse_scroll_callback(self, widget, event) -> bool:
        """Callback for a mouse scroll event occuring in the window."""
        if event.direction == Gdk.ScrollDirection.UP:
            self._take_action_on_tabs(CallbackActionsEnum.INCREMENT)
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self._take_action_on_tabs(CallbackActionsEnum.DECREMENT)

        # Return true to capture event
        return True

    def _keyboard_callback(self, widget, event) -> bool:
        """Callback for a keyboard press event occuring in the window."""
        if event.keyval == Gdk.KEY_Right:
            self._take_action_on_tabs(CallbackActionsEnum.INCREMENT)
        elif event.keyval == Gdk.KEY_Left:
            self._take_action_on_tabs(CallbackActionsEnum.DECREMENT)
        elif event.keyval == Gdk.KEY_Up:
            self._take_action_on_tabs(CallbackActionsEnum.END)
        elif event.keyval == Gdk.KEY_Down:
            self._take_action_on_tabs(CallbackActionsEnum.BEGIN)
        elif event.keyval == Gdk.KEY_b:
            self._take_action_on_tabs(CallbackActionsEnum.REDRAW)
        elif event.keyval == Gdk.KEY_s:
            self._step = self.slow_step
        elif event.keyval == Gdk.KEY_m:
            self._step = self.medium_step
        elif event.keyval == Gdk.KEY_f:
            self._step = self.fast_step

        # Return true to capture event
        return True

    def _take_action_on_tabs(self, action: CallbackActionsEnum):
        """
        This method takes the given action on all tabs in the window.

        Parameters
        ----------
        action:
            Action to take on all plots

        """
        # If we're still processing the last call, just drop this one
        if self._update_lock.locked():
            return
        self._update_lock.acquire()

        if self._bg_stale:
            self.current_tab._save_bg()
        self.current_tab._draw_bg()

        for tab in self._tabs:
            tab._take_action(action, self._step)

        self.current_tab._take_action(CallbackActionsEnum.REDRAW)

        self.current_tab._blit()
        self._update_lock.release()
