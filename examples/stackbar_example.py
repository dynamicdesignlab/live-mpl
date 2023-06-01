import numpy as np
from matplotlib import cm

from live_mpl import live_stackbar, tab, window


def main():
    num_bars = 10
    num_stacks = 5

    # Create data
    y_single_array = np.row_stack(
        (np.ones(num_bars), 2 * np.ones(num_bars), 3 * np.ones(num_bars))
    )
    y_data = [y_single_array for num in range(num_stacks)]

    win = window.Window("Example StackBar Plot")
    tab1 = tab.Tab(tab_name="StackBar")
    win.register_tab(tab1)

    # Create a single plot on tab1
    axis1 = tab1.add_subplot(
        1, 1, 1, ylabel="YAxis Label", xlabel="XAxis Label", title="Example Plot"
    )

    stackplot_colors = cm.tab20(np.linspace(0, 1, num_stacks))

    # Create a live line plot (In this case a single marker)
    plot1 = live_stackbar.LiveStackBar(
        x_data=None,
        y_data=y_data,
        plot_axis=axis1,
        labels=[f"data_{num}" for num in range(num_stacks)],
        colors=stackplot_colors,
    )
    tab1.register_plot(plot1)
    axis1.legend()

    win.loop()


if __name__ == "__main__":
    main()
