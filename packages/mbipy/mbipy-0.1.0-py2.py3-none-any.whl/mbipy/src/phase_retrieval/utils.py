"""Utility functions for phase retrieval."""

from __future__ import annotations

__all__ = ("PhaseRetrievalResult", "assert_odd", "swv")

import importlib
from typing import TYPE_CHECKING, NamedTuple

from numpy.lib.array_utils import normalize_axis_tuple

from mbipy.src.utils import (
    array_namespace,
    is_cupy_namespace,
    is_numpy_namespace,
    is_torch_namespace,
)

if TYPE_CHECKING:  # pragma: no cover
    from numpy import floating
    from numpy.typing import NDArray


class PhaseRetrievalResult(NamedTuple):
    # TODO(nin17): docstring
    """Result of phase retrieval.

    Parameters
    ----------
    NamedTuple : PhaseRetrievalResult
        transmission : NDArray[floating] | None = None


        phase : NDArray[floating] | None = None


        phase_gy : NDArray[floating] | None = None


        phase_gx : NDArray[floating] | None = None


        dark : NDArray[floating] | None = None


        dark_yy : NDArray[floating] | None = None


        dark_xx : NDArray[floating] | None = None


        dark_yx : NDArray[floating] | None = None


    """

    transmission: NDArray[floating] | None = None
    phase: NDArray[floating] | None = None
    phase_gy: NDArray[floating] | None = None
    phase_gx: NDArray[floating] | None = None
    dark: NDArray[floating] | None = None
    dark_yy: NDArray[floating] | None = None
    dark_xx: NDArray[floating] | None = None
    dark_yx: NDArray[floating] | None = None


def assert_odd(*args: int) -> None:
    """Check if all arguments are odd integers.

    Parameters
    ----------
    args : int
        The dimensions to check.


    Raises
    ------
    ValueError
        If any of the dimensions are not odd integers.
    """
    if not all(i % 2 == 1 for i in args):
        msg = "All search and template dimensions must be odd."
        raise ValueError(msg)


def swv(
    x: NDArray,
    window_shape: int | tuple[int, ...], # !!! only tuples
    axis: int | tuple[int, ...] | None = None, # !!! only tuples
) -> NDArray:
    """Sliding window view of an array.

    Parameters
    ----------
    x : NDArray
        Array to create the sliding window view from.
    window_shape : int | tuple[int, ...]
        Size of the sliding window over each axis.
    axis : int | tuple[int, ...] | None, optional
        Axis or axes along which the sliding window view is applied, by default None

    Returns
    -------
    NDArray
        Sliding window view of the input array.

    Raises
    ------
    NotImplementedError
        If the array namespace is not supported.
        Supported namespaces are: numpy, cupy, torch.
    """
    xp = array_namespace(x)
    if is_numpy_namespace(xp):
        _swv = importlib.import_module("numpy.lib.stride_tricks").sliding_window_view
    elif is_cupy_namespace(xp):
        _swv = importlib.import_module("cupy.lib.stride_tricks").sliding_window_view
    elif is_torch_namespace(xp):
        axis = normalize_axis_tuple(axis, x.ndim)
        for w, a in zip(window_shape, axis):
            x = x.unfold(a, w, 1)
        return x
    else:
        msg = "sliding window view not supported for this namespace"
        raise NotImplementedError(msg)
    return _swv(x, window_shape, axis=axis)
