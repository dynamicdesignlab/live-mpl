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

"""This script creates a LiveComet plot."""
__author__ = "John Talbot"
__contact__ = "jtalbot.me@gmail.com"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

import numpy as np
import matplotlib.pyplot as plt

from live_mpl import LiveComet, Tab, Window, animate


def main():
    # Create data
    x_data = np.linspace(0, 100, 100)
    y_data = np.linspace(0, 100, 100)

    fig, ax = plt.subplots()

    # Create a single axis on tab
 
    ax.plot(x_data, y_data)  # You can create classic matplotlib plots on this axis

    head_kwargs = {'marker': None}
    tail_kwargs = {'linewidth': 5, 'color': 'red', 'alpha': 0.5}
    # Create a live comet plot
    plot = LiveComet(ax=ax, x_data=x_data, y_data=y_data, head_kwargs=head_kwargs, tail_kwargs=tail_kwargs)

    animate.animate(
        save_path="animation.mp4",
        fig=fig,
        plots=[plot],
        time_step_s=0.1,
    )



if __name__ == "__main__":
    main()
