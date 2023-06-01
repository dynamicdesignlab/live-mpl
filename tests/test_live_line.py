""" test_live_plot

This module implements unit testing for the live_plot module

"""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"


import numpy as np
import pytest
from live_mpl import LiveLine

from live_mpl.exceptions import InconsistentArrayShape, InvalidIterationAxis


def test_x_y_not_same_shape():
    x_data = np.zeros((5, 6))
    y_data = np.zeros((5, 5))
    with pytest.raises(InconsistentArrayShape):
        LiveLine(ax=None, x_data=x_data, y_data=y_data)


def test_iter_axis_negative():
    x_data = np.zeros((5, 5))
    y_data = np.zeros((5, 5))
    with pytest.raises(InvalidIterationAxis):
        LiveLine(ax=None, x_data=x_data, y_data=y_data, iter_axis=-1)


def test_iter_axis_too_high():
    x_data = np.zeros((5, 5))
    y_data = np.zeros((5, 5))
    with pytest.raises(InvalidIterationAxis):
        LiveLine(ax=None, x_data=x_data, y_data=y_data, iter_axis=2)
