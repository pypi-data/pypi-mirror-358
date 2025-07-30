from __future__ import annotations

import warnings

from numba import extending, prange, types
from numpy import empty, float64, identity
from numpy.linalg import solve

from .lcs import _lcs


@extending.overload(_lcs, jit_options={"parallel": True, "fastmath": True})
def _lcs_overload(
    sample,
    reference,
    weak_absorption,
    alpha,
    search_window,
    start,
    stop,
    step,
):
    ndim = 3
    if isinstance(alpha, types.Array):
        msg = "only scalar alpha is implemented."
        raise TypeError(msg)

    if sample.ndim != ndim or reference.ndim != ndim:
        msg = "only 3D sample and reference arrays are implemented."
        raise ValueError(msg)
    if not all(i is types.none for i in (search_window, start, stop, step)):
        msg = "search_window, start, stop, and step are not implemented."
        raise ValueError(msg)

    warnings.warn(
        "Numba implementation is not correct for the edge pixels.",
        stacklevel=2,
    )

    # TODO(nin17): complex conjugate
    def impl(
        sample,
        reference,
        weak_absorption,
        alpha,
        search_window,
        start,
        stop,
        step,
    ):
        if sample.shape != reference.shape:
            msg = "sample and reference must have the same shape."
            raise ValueError(msg)
        z, y, x = reference.shape
        # y, x, z = reference.shape
        matrices = empty((y, x, z, 3), dtype=float64)
        out = empty((y, x, 3), dtype=float64)
        # TODO check this alpha stuff
        # alpha = np.asarray(alpha, dtype=np.float64)
        # alpha = alpha.reshape(alpha.shape + [1 for _ in range(matrices.ndim - alpha.ndim)])
        alpha_identity = alpha * identity(3, dtype=float64)

        # sample = sample.transpose(1, 2, 0).copy()
        sample = sample.transpose(1, 2, 0)
        # TODO nin17: edges
        for j in prange(1, y - 1):
            for k in range(1, x - 1):
                for i in range(z):
                    matrices[j, k, i, 0] = reference[i, j, k]
                    matrices[j, k, i, 1] = (
                        -reference[i, j + 1, k] + reference[i, j - 1, k]
                    ) / 2.0
                    matrices[j, k, i, 2] = (
                        -reference[i, j, k + 1] + reference[i, j, k - 1]
                    ) / 2.0
                    #!!! change to this eventually - ...yxk faster than ...kyx
                    # matrices[j, k, i, 0] = reference[j, k, i]
                    # matrices[j, k, i, 1] = (
                    #     -reference[j + 1, k, i] + reference[j - 1, k, i]
                    # ) / 2.0
                    # matrices[j, k, i, 2] = (
                    #     -reference[j, k + 1, i] + reference[j, k - 1, i]
                    # ) / 2.0
                a = matrices[j, k]
                ata = (a.T @ a) + alpha_identity
                atb = a.T @ sample[j, k]
                result = solve(ata, atb)
                if weak_absorption:
                    out[j, k] = result
                else:
                    out[j, k, 1:] = result[1:] / result[0]
                    out[j, k, 0] = result[0]

        # for j in prange(1, y - 1):
        #     for k in range(1, x - 1):
        #         a = matrices[j, k]
        #         ata = (a.T @ a) + alpha_identity
        #         atb = a.T @ sample[j, k]
        #         out[j, k] = solve(ata, atb)

        # if weak_absorption:
        #     return out

        # for i in prange(1, y - 1):
        #     for j in range(1, x - 1):
        #         out[i, j, 1:] /= out[i, j, 0]

        return out

    return impl


# try:
#     import numba as nb

#     _have_numba = True
# except ImportError:
#     _have_numba = False

# if _have_numba:
#     import numpy as np

# @nb.extending.overload(lcs)
# def overload_lcs(
#     sample,
#     reference,
#     weak_absorption=False,
#     alpha=0.0,
#     search_window=None,
#     start=None,
#     stop=None,
#     step=None,
# ):
#     def lcs_numba(
#         sample,
#         reference,
#         weak_absorption=False,
#         alpha=0.0,
#         search_window=None,
#         start=None,
#         stop=None,
#         step=None,
#     ):
#         assert reference.shape == sample.shape
#         assert reference.ndim == 3
#         x, y, z = reference.shape
#         matrices = np.empty((y, z, x, 3), dtype=np.float64)
#         out = np.empty((y, z, 3), dtype=np.float64)
#         # TODO check this alpha stuff
#         # alpha = np.asarray(alpha, dtype=np.float64)
#         # alpha = alpha.reshape(alpha.shape + [1 for _ in range(matrices.ndim - alpha.ndim)])
#         alpha_identity = alpha * np.identity(3, dtype=np.float64)

#         sample = sample.transpose(1, 2, 0).copy()
#         # TODO nin17: edges
#         for j in nb.prange(1, y - 1):
#             for k in range(1, z - 1):
#                 for i in range(x):
#                     matrices[j, k, i, 0] = reference[i, j, k]
#                     matrices[j, k, i, 1] = (
#                         -reference[i, j + 1, k] + reference[i, j - 1, k]
#                     ) / 2.0
#                     matrices[j, k, i, 2] = (
#                         -reference[i, j, k + 1] + reference[i, j, k - 1]
#                     ) / 2.0

#         for j in nb.prange(1, y - 1):
#             for k in range(1, z - 1):
#                 a = matrices[j, k]
#                 ata = (a.T @ a) + alpha_identity
#                 atb = a.T @ sample[j, k]
#                 out[j, k] = np.linalg.solve(ata, atb)

#         if weak_absorption:
#             return out

#         for i in nb.prange(1, y - 1):
#             for j in range(1, z - 1):
#                 out[i, j, 1:] /= out[i, j, 0]

#         return out

#     return lcs_numba
