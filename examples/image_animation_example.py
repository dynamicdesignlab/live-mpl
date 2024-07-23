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

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from live_mpl import LiveBase, LiveImage, animate
from pathlib import Path

NUM_FRAMES = 100
IMAGE_PATH = Path(__file__).parent.joinpath("noun-cool-penguin-57269.png")


def create_sample_data() -> dict[str, np.ndarray]:
    """
    Create data describing the vehicle's position in space

    Returns
    -------
        Dictionary of vehicle position data

    """
    theta_rad = np.linspace(0, 2 * np.pi, NUM_FRAMES)
    x_data = 2.0 * np.cos(theta_rad)
    y_data = 2.0 * np.sin(theta_rad)

    return {
        "theta_rad": theta_rad,
        "x_data": x_data,
        "y_data": y_data
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
    return [LiveImage(
        ax=ax,
        x_center=data["x_data"],
        y_center=data["y_data"],
        angle_deg=np.degrees(data["theta_rad"]),
        image_path=IMAGE_PATH,
        image_extent=[-1.0, 1.0, -1.5, 1.5],
    )]

def main():
    data = create_sample_data()

    # In this case we use a normal matplotlib figure and axis rather
    # than a Window and Tab object.
    fig, ax = plt.subplots()

    ax.plot(data["x_data"], data["y_data"], "k--")  # Plot static path of vehicle
    plots = create_plots(ax=ax, data=data)  # Create interactive plots

    # Some plot customization
    ax.set(xlabel="X Position", ylabel="Y Position", title="Animated Image")
    ax.grid(True)
    ax.axis("equal")

    # Animate the vehicle into a movie
    animate.animate(
        save_path="animation.mp4",
        fig=fig,
        plots=plots,
        num_frames=NUM_FRAMES,
        time_step_s=0.1,
    )


if __name__ == "__main__":
    main()
