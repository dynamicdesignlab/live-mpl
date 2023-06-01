from live_mpl.window import Window
from live_mpl.tab import Tab
from live_mpl.live_image import LiveImage
from pathlib import Path

import numpy as np

IMAGE_PATH = Path(__file__).parent.joinpath("cool_penguin_icon.png")


def main():
    # Create data
    theta_rad = np.linspace(0, 2 * np.pi, 100)
    x_data = 2.0 * np.cos(theta_rad)
    y_data = 2.0 * np.sin(theta_rad)

    win = Window("Example Plot")

    # Create tab and register to window
    tab = Tab("First Tab")
    win.register_tab(tab)

    # Create a single plot on tab
    ax = tab.add_axis(
        1, 1, 1, ylabel="YAxis Label", xlabel="XAxis Label", title="Example Image"
    )

    # Create a live image plot
    im = LiveImage(
        ax=ax,
        x_center=x_data,
        y_center=y_data,
        angle_deg=np.degrees(theta_rad),
        image_path=IMAGE_PATH,
        image_extent=[-1.0, 1.0, -1.5, 1.5],
    )

    # Register plot to tab
    tab.register_plot(im)
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)

    # Call this at the very end to run Gtk's event loop
    win.loop()


if __name__ == "__main__":
    main()
