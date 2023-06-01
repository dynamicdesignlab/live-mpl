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

"""This script creates an animation of a vehicle and LiveComet plot."""
__author__ = "John Talbot"
__contact__ = "jtalbot.me@gmail.com"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from matplotlib.axes import Axes
from matplotlib import pyplot as plt
from live_mpl import LiveBase, create_live_vehicle, LiveLine, animate
import numpy as np

NUM_FRAMES = 100


def create_sample_data() -> dict[str, np.ndarray]:
    """
    Create data describing the vehicle's position in space

    Returns
    -------
        Dictionary of vehicle position data

    """
    psi_rad = np.linspace(0, 2 * np.pi, NUM_FRAMES)
    return {
        "psi_rad": psi_rad,
        "east_m": 15 * np.cos(psi_rad),
        "north_m": 15 * np.sin(psi_rad),
        "delta_rad": np.radians(10 * np.ones(psi_rad.shape)),
    }


def create_plots(ax: Axes, data: dict[str, np.ndarray]) -> list[LiveBase]:
    """
    Create a list of interactive plots for the vehicle.

    Parameters
    ----------
    ax:
        Matplotlib axis
    data:
        Dictionary of vehicle position data

    Returns
    -------
        List of interactive plots

    """
    veh_plots = create_live_vehicle(
        ax,
        east_m=data["east_m"],
        north_m=data["north_m"],
        psi_rad=data["psi_rad"],
        delta_rad=data["delta_rad"],
        animated=True,
    )

    line_plot = LiveLine(
        axis=ax,
        x_data=data["east_m"],
        y_data=data["north_m"],
        data_axis=0,
        plot_kwargs={
            "marker": "^",
            "markerfacecolor": "yellow",
            "markeredgecolor": "black",
        },
    )

    return veh_plots + [line_plot]


def main():
    data = create_sample_data()

    # In this case we use a normal matplotlib figure and axis rather
    # than a Window and Tab object.
    fig, ax = plt.subplots()

    ax.plot(data["east_m"], data["north_m"], "k--")  # Plot static path of vehicle
    plots = create_plots(ax=ax, data=data)  # Create interactive plots

    # Some plot customization
    ax.set(xlabel="East [m]", ylabel="North [m]", title="Animated Vehicle")
    ax.grid(True)
    ax.axis("equal")

    # Animate the vehicle into a movie
    animate.animate(
        save_path="animation.mp4",
        fig=fig,
        plots=plots,
        time_step_s=0.1,
        num_frames=NUM_FRAMES,
    )


if __name__ == "__main__":
    main()
