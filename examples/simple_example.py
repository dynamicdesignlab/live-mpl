"""
This script creates a simple LiveLine plot as a first example of how to use the
live_mpl framework.
"""

import numpy as np

from live_mpl import LiveLine, Tab, Window


def main():
    # Create data
    x_data = np.linspace(0, 100, 100)
    y_data = np.linspace(0, 100, 100)

    win = Window("Example Plot")
    tab = Tab("First Tab")
    win.register_tab(tab)  # Each tab must be registered to it's parent window

    # Create a single axis on tab
    ax = tab.add_subplot(
        1, 1, 1, ylabel="YAxis Label", xlabel="XAxis Label", title="Example Plot"
    )
    ax.plot(x_data, y_data)  # You can create classic matplotlib plots on this axis

    # Create a live line plot (In this case a single marker)
    plot = LiveLine(ax=ax, x_data=x_data, y_data=y_data)

    tab.register_plot(plot)  # Each live plot must be registered to it's parent tab

    win.loop()  # This method must be called at the end of the script


if __name__ == "__main__":
    main()
