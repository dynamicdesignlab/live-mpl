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

"""
This script creates a simple LiveLine plot as a first example of how to use the
live_mpl framework.
"""
__author__ = "John Talbot"
__contact__ = "jtalbot.me@gmail.com"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

import numpy as np

from live_mpl import LiveLine, Tab, Window

LEN_DATA = 100

def main():
    # Create data
    x_data = np.linspace(0, 100, LEN_DATA)
    y_data = np.linspace(0, 100, LEN_DATA)

    win = Window(len_data=LEN_DATA, title="Example Plot")
    tab = Tab("First Tab")
    win.register_tab(tab)  # Each tab must be registered to it's parent window

    # Create a single axis on tab
    ax = tab.add_subplot(
        1, 1, 1, ylabel="YAxis Label", xlabel="XAxis Label", title="Example Plot"
    )
    ax.plot(x_data, y_data)  # You can create classic matplotlib plots on this axis

    # Create a live line plot (In this case a single marker)
    breakpoint()
    plot = LiveLine(ax=ax, x_data=x_data, y_data=y_data, iter_axis=0)

    tab.register_plot(plot)  # Each live plot must be registered to it's parent tab

    win.loop()  # This method must be called at the end of the script


if __name__ == "__main__":
    main()
