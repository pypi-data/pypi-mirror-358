from __future__ import annotations

import sys
import os

"""Convenience functions for reading images."""

from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING

import fabio
import numpy as np

if TYPE_CHECKING:

    from os import PathLike

    from numpy.typing import NDArray

    StrPath = str | PathLike[str]

__all__ = ("load_stack",)


def load_data(path: StrPath, *, frame: None = None) -> NDArray:
    """Load an image from a file.

    Parameters
    ----------
    path : StrPath
        Path to the image.
    frame : None, optional
        Passed to fabio.open, by default None

    Returns
    -------
    NDArray
        Image data.

    """
    with fabio.open(path, frame) as f:
        return f.data


def load_stack(  # noqa: PLR0913
    path: StrPath,
    *patterns: str,
    case_sensitive: bool | None = None,
    frame: None = None,
    axis: int | None = None,
    out: NDArray | None = None,
    dtype: None = None,
) -> list[NDArray] | NDArray:
    """Load all images matching the patterns, sorted by path, from a directory.

    Parameters
    ----------
    path : strPath
        Path to the directory containing the images.
    *patterns : str
        Patterns to match the files.
    case_sensitive : bool | None, optional
        Passed to Path(path).glob, by default None
    frame : None, optional
        Passed to fabio.open, by default None
    axis : int | None, optional
        If None, returns a list of NDArrays, otherwise passed to np.stack, by default
        None
    out : NDArray | None, optional
        Passed to np.stack if axis is not None, by default None
    dtype : None, optional
        Passed to np.stack if axis is not None, by default None

    Returns
    -------
    list[NDArray] | NDArray
        If axis is None, returns a list of NDArrays, otherwise returns a single NDArray.

    """
    _path = Path(path)
    file_paths = sorted(
        chain(*[_path.glob(p, case_sensitive=case_sensitive) for p in patterns]),
    )
    images = [fabio.open(i, frame=frame).data for i in file_paths]
    if axis is None:
        return images
    return np.stack(images, axis=axis, out=out, dtype=dtype)



from PyQt6 import QtWidgets  # Should work with PyQt5 / PySide2 / PySide6 as well
import pyqtgraph as pg

# Always start by initializing Qt (only once per application)
app =pg.mkQApp()

plot_widget = pg.PlotWidget()

plot_widget.plot(np.arange(10))
plot_widget.show()


# Start the Qt event loop
app.exec()  # or app.exec_() for PyQt5 / PySide2
