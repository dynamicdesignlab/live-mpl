from matplotlib.figure import Figure


def scale_figure_for_width(fig: Figure, width_in: float) -> None:
    (width, height) = fig.get_size_inches()
    scale = width_in / width
    fig.set_size_inches(w=width * scale, h=height * scale)
    return None


def scale_figure_for_height(fig: Figure, height_in: float) -> None:
    (width, height) = fig.get_size_inches()
    scale = height_in / height
    fig.set_size_inches(w=width * scale, h=height * scale)
    return None
