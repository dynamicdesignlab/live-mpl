# Live Matplotlib

Live Matplotlib (live_mpl) allows users to easily create interactive plots and animated movies with iterable numeric data.

## Installation

This package depends on PyGObject which in turn depends on some
packages available through `apt`. For more information see [PyGObject-Getting Started](https://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-getting-started).

On `Ubuntu` systems you can run the command to install the necessary packages.
```bash
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0
```

Then use python package manager of your choice to install `live_mpl`.

```bash
pip install git+https://bitbucket.org/dynamicdesign/live_mpl.git
```

## Basic Example

```python
from live_mpl import Window, Tab, LiveLine
import numpy as np


# Create data
x_data = np.linspace(0, 100, 100)
y_data = np.linspace(0, 100, 100)

win = Window("Example Plot")
tab = Tab("First Tab")
win.register_tab(tab)  # Each tab must be registered to it's parent window

# Create a single axis on tab
ax = tab.add_axis(
    1, 1, 1, ylabel="YAxis Label", xlabel="XAxis Label", title="Example Plot"
)
ax.plot(x_data, y_data)  # You can create classic matplotlib plots on this axis

# Create a live line plot (In this case a single marker)
plot = LiveLine(ax=ax, x_data=x_data, y_data=y_data)

tab.register_plot(plot)  # Each live plot must be registered to it's parent tab

win.loop()  # This method must be called at the end of the script
```

See the `examples` directory for more live_mpl examples.

## Documentation
Download the documentation for a given version in the `Downloads` tab on bitbucket. Unzip the file and open `html/index.html` in your web browser of choice.


## License
[MIT](https://choosealicense.com/licenses/mit/)


## Miscellaneous
The cool\_penguin\_icon.png image used in the `image_example.py` script is attributed to:

https://thenounproject.com/term/cool-penguin/57269/, CC BY 3.0 <https://creativecommons.org/licenses/by/3.0>, via Wikimedia Commons
