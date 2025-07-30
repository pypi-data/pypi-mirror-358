"""Orthogonal transforms for dimensionality reduction."""

from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from math import sqrt
from typing import TYPE_CHECKING, Literal

from array_api_compat import (
    is_cupy_namespace,
    is_jax_namespace,
    is_numpy_namespace,
    is_torch_namespace,
)

from mbipy.src.config import config as cfg
from mbipy.src.utils import array_namespace, imul

sqrt2 = sqrt(2.0)

if cfg.have_pywt:
    from pywt import Wavelet

if TYPE_CHECKING:
    from typing import Any

    from numpy import number
    from numpy.typing import NDArray


def _copy(v: NDArray[Any], copy: bool | None = None) -> NDArray[Any]:
    xp = array_namespace(v)
    if copy:
        return xp.copy(v)
    return v


class OrthogonalTransform(ABC):
    """Base class for orthogonal transforms."""

    @property
    def cutoff(self) -> int | None:
        """Return the cutoff value."""
        return self._cutoff

    @property
    def copy(self) -> bool | None:
        """Return whether to copy the output array - to make it contiguous."""
        return self._copy

    @abstractmethod
    def _apply_transform(self, v: NDArray[number]) -> NDArray[number]:
        """Apply the orthogonal transform to the input v."""

    def apply_transform(self, v: NDArray[number]) -> NDArray[number]:
        """Apply the orthogonal transform to the input v."""
        return _copy(self._apply_transform(v), copy=self.copy)

    def __call__(self, v: NDArray[number]) -> NDArray[number]:
        """Apply the orthogonal transform to the input v."""
        return self.apply_transform(v)


class DWT(OrthogonalTransform):
    """Discrete Wavelet Transform (DWT) using the specified wavelet."""

    def __init__(
        self,
        cutoff: int | None = None,
        level_cutoff: int | None = None,
        wavelet: str | Wavelet = "db2",
        copy: bool | None = None,
    ) -> None:
        self._cutoff = cutoff
        self._level_cutoff = level_cutoff
        self._wavelet = wavelet if isinstance(wavelet, Wavelet) else Wavelet(wavelet)
        self._mode = "zero"
        self._copy = copy

    @property
    def level_cutoff(self) -> int | None:
        return self._level_cutoff

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def wavelet(self) -> Wavelet:
        return self._wavelet

    def _apply_transform(self, v: NDArray) -> NDArray:
        xp = array_namespace(v)
        if is_numpy_namespace(xp):
            from pywt import wavedec
        elif is_jax_namespace(xp):
            from jaxwt import wavedec
        elif is_torch_namespace(xp):
            from ptwt import wavedec
        else:
            msg = f"Unsupported array namespace: {xp.__name__}"
            raise NotImplementedError(msg)

        _wavedec = wavedec(v, wavelet=self.wavelet, mode=self.mode, axis=-1)[
            : self.level_cutoff
        ]

        div, cutoff = divmod(self.cutoff, v.shape[-1])
        if div not in {-1, 0}:
            msg = f"cutoff: {self.cutoff} outside size of array: {v.shape[-1]}"
            raise ValueError(msg)

        _wav = []
        for i in _wavedec:
            if i.shape[-1] <= cutoff and cutoff - i.shape[-1] > 0:
                _wav.append(i)
            else:
                _wav.append(i[..., :cutoff])
                break
            cutoff -= i.shape[-1]

        return xp.concat(_wav, axis=-1)


class DCT(OrthogonalTransform):
    def __init__(
        self,
        cutoff: int | None = None,
        dct_type: int = 2,
        workers: int | None = None,
        copy: bool | None = None,
    ) -> None:
        self._cutoff = cutoff
        self._dct_type = dct_type
        self._norm = "ortho"
        self._workers = workers
        self._copy = copy

    @property
    def dct_type(self) -> int:
        return self._dct_type

    @property
    def norm(self) -> str:
        return self._norm

    @property
    def workers(self) -> int | None:
        return self._workers

    def _apply_transform(self, v: NDArray) -> NDArray:  # TODO(nin17): use workers
        # TODO(nin17): _apply_dct func for numba overloads.
        xp = array_namespace(v)
        if is_numpy_namespace(xp):
            dct = importlib.import_module("scipy.fft").dct
        elif is_cupy_namespace(xp):
            dct = importlib.import_module("cupyx.scipy.fft").dct
        elif is_jax_namespace(xp):
            dct = importlib.import_module("jax.scipy.fft").dct
        elif is_torch_namespace(xp):
            dct = importlib.import_module("torch_dct").dct
        return dct(v, type=self.dct_type, axis=-1, norm=self.norm)[..., : self.cutoff]


class DST(OrthogonalTransform):
    def __init__(
        self,
        cutoff: int | None = None,
        dst_type: int = 2,
        workers: int | None = None,
        copy: bool | None = None,
    ):
        self._cutoff = cutoff
        self._dst_type = dst_type
        self._norm = "ortho"
        self._workers = workers
        self._copy = copy

    @property
    def dst_type(self) -> int:
        return self._dst_type

    @property
    def norm(self) -> str:
        return self._norm

    @property
    def workers(self) -> int | None:
        return self._workers

    def _apply_transform(self, v: NDArray) -> NDArray:  # TODO(nin17): use workers
        xp = array_namespace(v)
        if is_numpy_namespace(xp):
            dst = importlib.import_module("scipy.fft").dst
        elif is_cupy_namespace(xp):
            dst = importlib.import_module("cupyx.scipy.fft").dst
        elif is_jax_namespace(xp):
            dst = importlib.import_module("jax.scipy.fft").dst
        else:
            msg = f"Unsupported array namespace: {xp.__name__}"
            raise NotImplementedError(msg)

        return dst(v, type=self.dst_type, axis=-1, norm=self.norm)[..., : self.cutoff]


class RFFT(OrthogonalTransform):  # TODO(nin17): multiply [..., 1:] by sqrt(2)
    def __init__(self, cutoff: int | None = None, workers: int | None = None) -> None:
        self._cutoff = cutoff
        self._norm = "ortho"
        self._workers = workers

    def _apply_transform(self, v: NDArray) -> NDArray:
        xp = array_namespace(v)
        kwargs = {"norm": self._norm, "axis": -1}
        if is_numpy_namespace(xp):
            if cfg.use_scipy_fft:
                fft = importlib.import_module("scipy.fft")
                res = fft.rfft(v, **kwargs, workers=self._workers)
        elif is_cupy_namespace(xp) and cfg.use_pyvkfft:
            fft = importlib.import_module("pyvkfft.fft")
            res = fft.rfftn(v, ndim=1, norm=self._norm)

        res = xp.fft.rfft(v, **kwargs)[..., : self.cutoff]

        if res.shape[-1] % 2:
            res = imul(res, (..., slice(1, None)), sqrt2)
        else:
            res = imul(res, (..., slice(1, -1)), sqrt2)

        return res[..., : self.cutoff]


def _svd_flip(v: NDArray[number]) -> NDArray[number]:
    xp = array_namespace(v)
    # TODO(nin17): permalink to this function in scikit-learn
    # Based on SVD flip from scikit-learn
    max_abs_v_rows = xp.argmax(xp.abs(v), axis=-1)
    shift = xp.arange(v.shape[-2])
    indices = max_abs_v_rows + shift * v.shape[-1]
    signs = xp.sign(xp.take(xp.reshape(v, (-1,)), indices, axis=0))
    return imul(v, ..., signs[..., None])


class PCA(OrthogonalTransform):
    def __init__(
        self,
        reference: NDArray[number],
        *,
        mean_correction=True,
        std_correction=True,
        method: Literal["eigh", "qr", "svd"] = "qr",
        cutoff: int | None = None,
        deterministic=None,
    ) -> None:
        xp = array_namespace(reference)

        ref = xp.reshape(reference, (*reference.shape[:-3], -1, reference.shape[-1]))
        if mean_correction:
            ref = ref - xp.mean(ref, axis=-2, keepdims=True)
        if std_correction:
            ref = ref / xp.std(ref, axis=-2, keepdims=True)

        if method not in {"eigh", "qr", "svd"}:
            msg = f"Invalid method: {method}. Choose from 'eigh', 'qr', or 'svd'."
            raise ValueError(msg)

        if method == "eigh":
            cov = ref.mT @ ref / (ref.shape[-2] - 1)
            vh = xp.linalg.eigh(cov).eigenvectors[..., ::-1].mT
        if method == "qr":
            if is_numpy_namespace(xp):
                qr = importlib.import_module("numpy.linalg").qr
                r = qr(ref, mode="r")
            elif is_cupy_namespace(xp):
                qr = importlib.import_module("cupy.linalg").qr
                r = qr(ref, mode="r")
            else:
                r = xp.linalg.qr(ref, mode="reduced").R

            vh = xp.linalg.svd(r, full_matrices=False).Vh
        if method == "svd":
            vh = xp.linalg.svd(ref, full_matrices=False).Vh

        self._vh = _svd_flip(vh) if deterministic else vh
        self._v = self._vh[..., None, :, :].mT
        self._cutoff = cutoff
        self._deterministic = deterministic

    def _apply_transform(self, v: NDArray) -> NDArray:
        return v @ self._v[..., : self.cutoff]
