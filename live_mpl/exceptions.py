"""This module implements custom exceptions used across live_mpl modules."""

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
