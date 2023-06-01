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

"""This module implements custom exceptions used across live_mpl modules."""
__author__ = "John Talbot"
__contact__ = "john.talbot@stanford.edu"
__copyright__ = "Copyright 2022"
__date__ = "2022/05/07"
__license__ = "MIT"


class InconsistentArrayShape(Exception):
    """
    Exception raised when input arrays are not the same shape.

    Attributes
    ----------
    x_shape: tuple[int,...]
        The shape of x
    y_shape: tuple[int,...]
        The shape of y

    """

    def __init__(self, x_shape: tuple[int, ...], y_shape: tuple[int, ...]):
        self.x_shape = x_shape
        self.y_shape = y_shape
        self.message = (
            f"Shape of x {self.x_shape} is not consistent "
            f"with the shape of y {self.y_shape}"
        )
        super().__init__(self.message)


class InvalidIterationAxis(Exception):
    """
    Exception raised when the provided iteration axis is invalid for the provided data.

    Attributes
    ----------
    iter_axis: int
        The iteration axis
    num_dims: int
        The number of data dimensions

    """

    def __init__(self, iter_axis: int, num_dims: int):
        self.num_dims = num_dims
        self.iter_axis = iter_axis
        self.message = (
            f"Iteration axis {self.iter_axis} is not valid "
            f"for data with dimension {self.num_dims}"
        )
        super().__init__(self.message)


class ArrayNot1D(Exception):
    """
    Exception raised when input arrays is not 1 dimensional.

    Attributes
    ----------
    ndim: int
        The number of dimensions of the given data array

    """

    def __init__(self, ndim: int):
        self.ndim = ndim
        self.message = f"Expected a 1D array, but got an array with {self.ndim}"
        super().__init__(self.message)
