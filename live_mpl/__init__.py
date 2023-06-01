""" live_mpl

This package implements an interactive plotting framework
built on GTK and matplotlib.

"""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"

from .window import Window
from .tab import Tab
from .live_comet import LiveComet
from .live_fancy_bbox import LiveFancyBBox
from .live_image import LiveImage
from .live_line import LiveLine
from .live_base import LiveBase
from .live_rectangle import LiveRectangle
from .live_stackbar import LiveStackBar
from .live_streamlines import LiveStreamlines
from .live_vehicle import create_live_vehicle, LiveVehicleConfig
from .live_vline import LiveVLine
