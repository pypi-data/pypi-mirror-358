"""utility functions for phase retrieval."""

import importlib

import numpy as np

from mbipy.src.utils import array_namespace, is_cupy_namespace, is_numpy_namespace


def correlate1d(x, weights, axis, mode, cval):  # TODO(nin17): correlate1d
    xp = array_namespace(x, weights)
    if is_numpy_namespace(xp):
        _correlate1d = importlib.import_module("scipy.ndimage").correlate1d
    elif is_cupy_namespace(xp):
        _correlate1d = importlib.import_module("cupyx.scipy.ndimage").correlate1d
    else:
        msg = f"correlate1d not supported for {xp.__name__} namespace."
        raise NotImplementedError(msg)
    return _correlate1d(x, weights, axis=axis, mode=mode, cval=cval)

def get_correlate1d(xp):
    """_summary_

    Parameters
    ----------
    xp : _type_
        _description_

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    NotImplementedError
        _description_
    """
    if is_numpy_namespace(xp):
        return importlib.import_module("scipy.ndimage").correlate1d
    if is_cupy_namespace(xp):
        return importlib.import_module("cupyx.scipy.ndimage").correlate1d
    raise NotImplementedError(f"{xp.__name__} not supported")


def find_displacement(array_padded):
    # TODO(nin17): add docstring
    # From create_find_displacement
    xp = array_namespace(array_padded)
    window_shape = tuple(np.asarray(array_padded.shape[-2:]) - 2)
    dy_int, dx_int = xp.unravel_index(
        array_padded[..., 1:-1, 1:-1].reshape(*array_padded.shape[:-2], -1).argmax(-1),
        window_shape,
    )
    ndim = array_padded.ndim - 3
    # TODO(nin17): reshape and do 1d indexing instead
    # TODO nin17: can probably do this with ndarray.take
    preceding = tuple(
        xp.arange(j).reshape((1,) * i + (-1,) + (1,) * (ndim - i))
        for i, j in enumerate(array_padded.shape[:-2])
    )

    dy_int1 = dy_int + 1
    dy_int2 = dy_int + 2

    dx_int1 = dx_int + 1
    dx_int2 = dx_int + 2

    dy = (
        array_padded[preceding + (dy_int2, dx_int1)]
        - array_padded[preceding + (dy_int, dx_int1)]
    ) / 2.0
    dyy = (
        array_padded[preceding + (dy_int2, dx_int1)]
        + array_padded[preceding + (dy_int, dx_int1)]
        - 2.0 * array_padded[preceding + (dy_int1, dx_int1)]
    )
    dx = (
        array_padded[preceding + (dy_int1, dx_int2)]
        - array_padded[preceding + (dy_int1, dx_int)]
    ) / 2.0
    dxx = (
        array_padded[preceding + (dy_int1, dx_int2)]
        + array_padded[preceding + (dy_int1, dx_int)]
        - 2.0 * array_padded[preceding + (dy_int1, dx_int1)]
    )
    dxy = (
        array_padded[preceding + (dy_int2, dx_int2)]
        - array_padded[preceding + (dy_int2, dx_int)]
        - array_padded[preceding + (dy_int, dx_int2)]
        + array_padded[preceding + (dy_int, dx_int)]
    ) / 4.0

    # TODO nin17: sort this out
    denom = dxx * dyy - dxy * dxy
    det = xp.where(denom > xp.finfo(array_padded.dtype).eps, 1.0 / denom, 0.0)

    disp_x = -(dyy * dx - dxy * dy) * det
    disp_y = -(dxx * dy - dxy * dx) * det

    disp_y += dy_int
    disp_x += dx_int

    # TODO nin17: remove this temporary fix
    # ??? nin17: why -2
    disp_y = xp.clip(disp_y, 0.0, array_padded.shape[-2] - 1.0)
    disp_x = xp.clip(disp_x, 0.0, array_padded.shape[-1] - 1.0)

    # ??? nin17: why -2
    disp_y = disp_y - array_padded.shape[-2] // 2 - 1
    disp_x = disp_x - array_padded.shape[-1] // 2 - 1

    return disp_y, disp_x
