import numpy as np
from live_mpl import LiveStackBar, Tab, Window


def main():
    ascend_vec = np.arange(9).reshape((-1, 1))
    ascend_mat = np.tile(ascend_vec, (1, 10))
    descend_mat = 8 - ascend_mat
    two_mat = 2.0 * np.ones(ascend_mat.shape)

    data = np.stack((ascend_mat, two_mat, descend_mat), axis=2)
    data_list = [ascend_mat, two_mat, descend_mat]

    win = Window("Test")
    tab = Tab("Stackbar Plots")
    win.register_tab(tab)

    ax1 = tab.add_subplot(2, 1, 1, title="3D Array")
    plt1 = LiveStackBar(ax=ax1, y_data=data, labels=["Ascend", "Two", "Descend"])
    ax1.grid(True)
    ax1.legend()
    tab.register_plot(plt1)

    ax2 = tab.add_subplot(2, 1, 2, title="List")
    plt2 = LiveStackBar(ax=ax2, y_data=data_list, labels=["Ascend", "Two", "Descend"])
    ax2.grid(True)
    tab.register_plot(plt2)

    win.loop()


if __name__ == "__main__":
    main()
