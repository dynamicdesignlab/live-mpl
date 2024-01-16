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


""" animate

This module implements functions to easily create an .mp4 movie by animating a
selection of LiveBase plots.

"""
__author__ = "John Talbot"
__contact__ = "jtalbot.me@gmail.com"
__copyright__ = "Copyright 2022"
__date__ = "2023/05/31"
__license__ = "MIT"

from pathlib import Path
from typing import Callable

from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from rich import progress

from .live_base import LiveBase

_ProgBar = progress.Progress(
    progress.TextColumn("[cyan]Generating Animation..."),
    progress.BarColumn(),
    progress.MofNCompleteColumn(),
    progress.TimeElapsedColumn(),
)


def _create_ani_func(plots: list[LiveBase]) -> tuple[Callable, int]:
    """
    Function generator to create animate function used by the matplotlib
    FuncAnimation interface.

    Parameters
    ----------
    plots:
        All LiveBase plots to be animated

    Returns
    -------
        Animation function to use with matplotlib FuncAnimation

        Number of frames to animate

    """

    num_frames = plots[0].len_data

    def take_step(*_):
        for item in plots:
            item._animate_step(1)

        return [artist for item in plots for artist in item.artists]

    return take_step, num_frames


def animate(
    fig: Figure,
    plots: list[LiveBase],
    save_path: Path,
    time_step_s: float,
    show_progress: bool = True,
    **kwargs,
):
    """
    Function to easily create an .mp4 movie from a selection of LiveBase plots.

    This function will increment each of the LiveBase plots given in the plots
    argument, and take a snapshot at each increment.  The entire sequence of
    snapshots is saved to a movie. The figure containing the LiveBase plots can
    also contain classic matplotlib plots which will remain constant over the movie.

    Optionally, this function will display a progressbar detailing the progress
    of the animation.

    Note
    ----
    This function assumes that all LiveBase plots are created from data with the
    same underlying timebase.

    In other words, the data contained in each LiveBase plot must have the same
    number of elements to iterate over, and each given element in a plot's
    dataset must have occured at the same instant as that element in all the
    other plots. Using this function of plots containing data from different
    timebases will lead to a loss of synchronization in the rendered elements,
    and unusable animations.

    Parameters
    ----------
    fig:
        Figure containing the plots to be animated
    plots:
        LiveBase plots to be animated
    save_path:
        Full path where the generated movie will be saved
    time_step_s:
        Duration between frames in the animation [sec]
    show_progress:
        Show a progressbar of the animation status


    """
    time_step_ms = 1_000.0 * time_step_s
    func, num_frames = _create_ani_func(plots)

    anim = FuncAnimation(
        fig,
        func=func,
        frames=num_frames,
        interval=time_step_ms,
        blit=True,
        repeat=True,
    )

    if show_progress:
        with _ProgBar as prog:
            task_id = prog.add_task("animator", total=num_frames)

            def progress_callback(current_frame: int, total_frames: int):
                prog.update(
                    task_id=task_id, total=total_frames, completed=current_frame
                )

            anim.save(str(save_path), progress_callback=progress_callback, **kwargs)
            prog.update(task_id=task_id, total=num_frames, completed=num_frames)
    else:
        anim.save(str(save_path), **kwargs)


def animate_now(
    fig: Figure,
    plots: list[LiveBase],
    time_step_s: float,
):
    """
    Function to easily create an .mp4 movie from a selection of LiveBase plots.

    This function will increment each of the LiveBase plots given in the plots
    argument, and take a snapshot at each increment.  The entire sequence of
    snapshots is saved to a movie. The figure containing the LiveBase plots can
    also contain classic matplotlib plots which will remain constant over the movie.

    Optionally, this function will display a progressbar detailing the progress
    of the animation.

    Note
    ----
    This function assumes that all LiveBase plots are created from data with the
    same underlying timebase.

    In other words, the data contained in each LiveBase plot must have the same
    number of elements to iterate over, and each given element in a plot's
    dataset must have occured at the same instant as that element in all the
    other plots. Using this function of plots containing data from different
    timebases will lead to a loss of synchronization in the rendered elements,
    and unusable animations.

    Parameters
    ----------
    fig:
        Figure containing the plots to be animated
    plots:
        LiveBase plots to be animated
    save_path:
        Full path where the generated movie will be saved
    time_step_s:
        Duration between frames in the animation [sec]
    show_progress:
        Show a progressbar of the animation status


    """
    time_step_ms = 1_000.0 * time_step_s
    func, num_frames = _create_ani_func(plots)
    return FuncAnimation(
        fig,
        func=func,
        frames=num_frames,
        interval=time_step_ms,
        blit=True,
    )
