"""_summary_"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from numpy import bool_
from numpy.lib.array_utils import normalize_axis_index

from mbipy.src.phase_retrieval.implicit.utils import is_not_invertible, laplace32
from mbipy.src.phase_retrieval.utils import PhaseRetrievalResult, swv
from mbipy.src.utils import Pytree, array_namespace, idiv, static_field

if TYPE_CHECKING:
    from types import ModuleType

    from numpy import floating
    from numpy.typing import ArrayLike, DTypeLike, NDArray

    from mbipy.src.orthogonal_transforms import OrthogonalTransform

__all__ = ("Lcs", "LcsDDf", "LcsDf", "lcs", "lcs_ddf", "lcs_df")

MIN_NDIM = 3

# TODO(nin17): template_window, weights

# !!! gradient not in array api standard
# !!! .squeeze() not in array api standard


def _lcs_matrices(reference: NDArray[floating]) -> NDArray[floating]:
    xp = array_namespace(reference)
    if not reference.ndim >= MIN_NDIM:
        msg = f"reference must have at least {MIN_NDIM} dimensions. {reference.ndim=}."
        raise ValueError(msg)
    gy, gx = xp.gradient(reference, axis=(-3, -2))
    return xp.stack((reference, -gy, -gx), axis=-1)


def _lcs_df_matrices(reference: NDArray) -> NDArray:
    xp = array_namespace(reference)
    if not reference.ndim >= MIN_NDIM:
        msg = f"reference must have at least {MIN_NDIM} dimensions. {reference.ndim=}."
        raise ValueError(msg)
    gy, gx = xp.gradient(reference, axis=(-3, -2))
    laplacian = laplace32(reference)
    return xp.stack((reference, -gy, -gx, laplacian), axis=-1)


def _lcs_ddf_matrices(reference: NDArray) -> NDArray:
    xp = array_namespace(reference)
    if not reference.ndim >= MIN_NDIM:
        msg = f"reference must have at least {MIN_NDIM} dimensions. {reference.ndim=}."
        raise ValueError(msg)
    gy, gx = xp.gradient(reference, axis=(-3, -2))
    gyy, gyx = xp.gradient(gy, axis=(-3, -2))
    gxy, gxx = xp.gradient(gx, axis=(-3, -2))
    # Ignore gxy as np.allclose(gxy, gyx) == True
    return xp.stack((reference, -gy, -gx, gyy, gxx, gyx), axis=-1)


def _lcs_vectors(sample: NDArray) -> NDArray:
    if not sample.ndim >= MIN_NDIM:
        msg = f"sample must have at least {MIN_NDIM} dimensions. {sample.ndim=}."
        raise ValueError(msg)
    return sample


def _process_alpha(
    alpha: ArrayLike,
    n: int,
    m_ndim: int,
    xp: ModuleType,
    dtype: DTypeLike,
) -> NDArray[floating]:
    # TODO(nin17): fix this logic for shapes - doesn't seem correct
    alpha = xp.asarray(alpha, dtype=dtype) if isinstance(alpha, (int, float)) else alpha
    shape = alpha.shape + (1,) * (m_ndim - alpha.ndim - 1)
    return xp.reshape(alpha, shape) * xp.eye(n, dtype=dtype)


def _solve(
    matrices: NDArray[floating],
    vectors: NDArray[floating],
    alpha: NDArray[floating],
) -> NDArray[floating]:
    # !!! vecmat conjugate vector matrix product
    xp = array_namespace(matrices, vectors, alpha)
    # !!! xp.conj returns copy for real arrays
    if xp.isdtype(matrices.dtype, "real floating"):
        mtconj = matrices.mT
    elif xp.isdtype(matrices.dtype, "complex floating"):
        mtconj = xp.conj(matrices.mT)
    else:
        # TODO(nin17): error message
        raise ValueError
    # ??? convert to real here to work with rfft and *= sqrt(2.0)
    # ??? how to do this with svd
    ata = xp.real((mtconj @ matrices) + alpha)
    atb = xp.real(mtconj @ vectors)
    return xp.linalg.solve(ata, atb)


def _process_search_window(search_window: tuple[int, int]) -> tuple[int, int]:
    m, n = search_window
    return (m - 1) // 2, (n - 1) // 2


def _process_slices(slices, sw):
    if slices is None:
        slices = slice(0, sw[0], 1), slice(0, sw[1], 1)
    elif isinstance(slices, slice):
        slices = slices, slices
    s0, s1 = slices

    s0_start = normalize_axis_index(0 if s0.start is None else s0.start, sw[0])
    s1_start = normalize_axis_index(0 if s0.start is None else s0.start, sw[1])
    s0_step = 1 if s0.step is None else s0.step
    s1_step = 1 if s1.step is None else s1.step

    return slice(s0_start, s0.stop, s0_step), slice(s1_start, s1.stop, s1_step)


def _min_residuals(
    matrices: NDArray,
    vectors: NDArray,
    result: NDArray,
    search_window: tuple[int, int],
    sliced_window: tuple[int, int],
    slices: tuple[slice, slice],
) -> NDArray:
    xp = array_namespace(matrices, vectors, result)
    m, n = _process_search_window(search_window)
    s0, s1 = slices

    result_reshape = xp.reshape(result, (-1, *result.shape[-2:]), copy=False)
    s = result_reshape.shape[0]
    residuals = matrices @ result - vectors
    ssr = xp.real(xp.vecdot(residuals, residuals, axis=-2))  # !!! does conj for complex
    argmin = xp.argmin(ssr, axis=-1)
    result_minimum = result_reshape[xp.arange(s), :, xp.reshape(argmin, -1, copy=False)]
    result_minimum = xp.reshape(result_minimum, result.shape[:-1], copy=False)
    minima = xp.unravel_index(argmin, sliced_window)  # !!! not in array api

    # TODO(nin17): check this
    # TODO(nin17): slices !!!
    result_minimum[..., 1] += s0.step * minima[0] + (s0.start - m)
    result_minimum[..., 2] += s1.step * minima[1] + (s1.start - n)
    return result_minimum


def _solve_window(
    matrices: NDArray[floating],
    vectors: NDArray[floating],
    alpha: NDArray[floating],
    search_window: tuple[int, int],
    slices: tuple[slice, slice] | None,
) -> NDArray:
    xp = array_namespace(matrices, vectors, alpha)
    m, n = _process_search_window(search_window)
    slices = _process_slices(slices, search_window)
    _matrices = matrices[..., m:-m, n:-n, :, :]
    _vectors = swv(vectors, search_window, axis=(-3, -2))[..., *slices]
    sliced_w = _vectors.shape[-2:]
    _vectors = xp.reshape(_vectors, (*_vectors.shape[:-2], -1))  # !!! creates a copy
    result = _solve(_matrices, _vectors, alpha)

    return _min_residuals(_matrices, _vectors, result, search_window, sliced_w, slices)


def _lcs(
    sample: NDArray,
    reference: NDArray,
    weak_absorption: bool | None,
    alpha: ArrayLike,
    search_window: int | tuple[int, int] | None,
    slices: tuple[slice, slice] | None,
    transform: OrthogonalTransform | None = None,
) -> NDArray:
    xp = array_namespace(reference, sample)
    dtype = xp.result_type(reference, sample)
    if transform is not None:
        reference = transform(reference)
        sample = transform(sample)
    matrices = _lcs_matrices(reference)
    vectors = _lcs_vectors(sample)
    alpha_eye = _process_alpha(alpha, 3, matrices.ndim, xp, dtype)

    if search_window:
        result = _solve_window(matrices, vectors, alpha_eye, search_window, slices)
    else:
        result = xp.squeeze(_solve(matrices, vectors[..., None], alpha_eye), -1)
    result = xp.real(result)

    if not weak_absorption:
        result = idiv(result, (..., slice(1, None)), result[..., :1])
    return PhaseRetrievalResult(
        transmission=result[..., 0],
        phase_gy=result[..., 1],
        phase_gx=result[..., 2],
    )


def lcs(
    sample: NDArray,
    reference: NDArray,
    weak_absorption: bool | None = None,
    alpha: ArrayLike = 0.0,
    search_window: int | tuple[int, int] | None = None,
    slices: tuple[slice, slice] | None = None,
    transform: OrthogonalTransform | None = None,
) -> PhaseRetrievalResult:
    return _lcs(
        sample,
        reference,
        weak_absorption,
        alpha,
        search_window,
        slices,
        transform,
    )


def _lcs_df(
    sample,
    reference,
    weak_absorption,
    alpha,
    search_window,
    slices,
    transform,
):
    xp = array_namespace(reference, sample)
    dtype = xp.result_type(reference, sample)
    if transform is not None:
        reference = transform(reference)
        sample = transform(sample)
    matrices = _lcs_df_matrices(reference)
    vectors = _lcs_vectors(sample)
    alpha_eye = _process_alpha(alpha, 4, matrices.ndim, xp, dtype)
    if search_window:
        result = _solve_window(matrices, vectors, alpha_eye, search_window, slices)
    else:
        result = xp.squeeze(_solve(matrices, vectors[..., None], alpha_eye), -1)
    result = xp.real(result)

    if not weak_absorption:
        result = idiv(result, (..., slice(1, None)), result[..., :1])
    return PhaseRetrievalResult(
        transmission=result[..., 0],
        phase_gy=result[..., 1],
        phase_gx=result[..., 2],
        dark=result[..., 3],
    )


def lcs_df(
    sample: NDArray[floating],
    reference: NDArray,
    weak_absorption: bool | None = None,
    alpha: ArrayLike = 0.0,
    search_window: int | tuple[int, int] | None = None,
    slices: tuple[slice, slice] | None = None,
    transform: OrthogonalTransform | None = None,
) -> PhaseRetrievalResult:
    return _lcs_df(
        sample,
        reference,
        weak_absorption,
        alpha,
        search_window,
        slices,
        transform,
    )


def _lcs_ddf(
    sample,
    reference,
    weak_absorption,
    alpha,
    search_window,
    slices,
    transform,
):
    xp = array_namespace(reference, sample)
    dtype = xp.result_type(reference, sample)
    if transform is not None:
        reference = transform(reference)
        sample = transform(sample)
    matrices = _lcs_ddf_matrices(reference)
    vectors = _lcs_vectors(sample)
    alpha_eye = _process_alpha(alpha, 6, matrices.ndim, xp, dtype)
    if search_window:
        result = _solve_window(matrices, vectors, alpha_eye, search_window, slices)
    else:
        result = xp.squeeze(_solve(matrices, vectors[..., None], alpha_eye), -1)
    result = xp.real(result)

    if not weak_absorption:
        result = idiv(result, (..., slice(1, None)), result[..., :1])
    return PhaseRetrievalResult(
        transmission=result[..., 0],
        phase_gy=result[..., 1],
        phase_gx=result[..., 2],
        dark_yy=result[..., 3],
        dark_xx=result[..., 4],
        dark_yx=result[..., 5],
    )


def lcs_ddf(
    sample: NDArray,
    reference: NDArray,
    weak_absorption: bool | None = None,
    alpha: ArrayLike = 0.0,
    search_window: int | tuple[int, int] | None = None,
    slices: tuple[slice, slice] | None = None,
    transform: OrthogonalTransform | None = None,
) -> PhaseRetrievalResult:
    return _lcs_ddf(
        sample,
        reference,
        weak_absorption,
        alpha,
        search_window,
        slices,
        transform,
    )


class _BaseLcs(Pytree, mutable=True):

    _xp = static_field()

    def __init__(
        self,
        reference: NDArray,
        alpha: ArrayLike,
        rcond: ArrayLike,
        xp: ModuleType | None,
        matrices_func: Callable[[NDArray], NDArray],
    ) -> None:
        _xp = array_namespace(reference)
        xp = xp or _xp
        self._xp = xp

        self.reference = reference
        matrices = matrices_func(reference)
        self._matrices = matrices

        _alpha = xp.asarray(alpha, dtype=reference.dtype)
        self._alpha = xp.reshape(
            _alpha,
            _alpha.shape + (1,) * (matrices.ndim - _alpha.ndim - 1),
        )

        shape_max = float(max(matrices.shape[-2:]))
        rcond_min = xp.asarray(xp.finfo(reference.dtype).eps * shape_max)
        _rcond = xp.maximum(xp.asarray(rcond, dtype=reference.dtype), rcond_min)
        self._rcond = xp.reshape(
            _rcond,
            _rcond.shape + (1,) * (matrices.ndim - _rcond.ndim - 1),
        )

        self._pinv = None

    def __call__(
        self,
        sample: NDArray,
        weak_absorption: bool = False,
        search_window: int | tuple[int, int] | None = None,
        slices: tuple[slice, slice] | None = None,
    ) -> NDArray:  # TODO(nin17): PhaseRetrievalResult
        # TODO(nin17): implement implicit tracking
        xp = array_namespace(self._matrices, sample)
        if self.pinv is None:
            self._compute_svd()

        vectors = _lcs_vectors(sample)

        if search_window is not None:
            m, n = _process_search_window(search_window)
            slices = _process_slices(slices, search_window)
            pinv = self.pinv[..., m:-m, n:-n, :, :]
            matrices = self._matrices[..., m:-m, n:-n, :, :]
            _vectors = swv(vectors, search_window, axis=(-3, -2))[..., *slices]
            sliced_window = _vectors.shape[-2:]
            # ??? do @ with einsum and then reshape to avoid copy
            _result2 = xp.reshape(
                xp.einsum("...ij, ...jkl", pinv, _vectors),
                (*_vectors.shape[:-3], -1, xp.prod(_vectors.shape[-2:])),
                copy=False,
            )
            _vectors = xp.reshape(_vectors, (*_vectors.shape[:-2], -1))  # !!! copy
            # _result = pinv @ _vectors
            # print(_result.shape, result2.shape)
            result = _min_residuals(
                matrices,
                _vectors,
                _result2,
                search_window,
                sliced_window,
                slices,
            )
        else:
            # ??? matmul or vecdot here
            # result = xp.real(xp.vecdot(self.pinv, vectors[..., None, :]))
            result = xp.squeeze(self.pinv @ vectors[..., None], -1)
        result = xp.real(result)

        if not weak_absorption:
            result = idiv(result, (..., slice(1, None)), result[..., :1])
        return result

    @property
    def alpha(self) -> NDArray:
        return self._alpha

    @alpha.setter
    def alpha(self, value: ArrayLike) -> None:
        xp = self._xp
        value = xp.asarray(value, dtype=self.reference.dtype)
        shape = value.shape + (1,) * (self._matrices.ndim - value.ndim - 1)
        self._alpha = xp.reshape(value, shape)
        self._compute_tikhonov_alpha()
        self._compute_tikhonov()
        self._compute_pinv()

    @property
    def rcond(self) -> NDArray:
        return self._rcond

    @rcond.setter
    def rcond(self, value: ArrayLike) -> None:
        xp = self._xp
        value = xp.asarray(value, dtype=self.reference.dtype)
        shape = value.shape + (1,) * (self._matrices.ndim - value.ndim - 1)
        self._rcond = xp.reshape(value, shape)
        self._s_max_rcond = self._s_max * self.rcond
        self._compute_tikhonov_rcond()
        self._compute_tikhonov()
        self._compute_pinv()

    @property
    def xp(self) -> ModuleType:
        return self._xp

    @xp.setter
    def xp(self, value: ModuleType) -> None:
        # Convert all necessary arrays to new xp
        # ??? possibly only convert pinv as that is only one strictly required
        # ??? others can be converted as required
        self._xp = value
        self.pinv = value.asarray(self.pinv)
        self._rcond = value.asarray(self._rcond)
        self._alpha = value.asarray(self._alpha)
        self._s = value.asarray(self._s)
        self._s2 = value.asarray(self._s2)
        self._s_max = value.asarray(self._s_max)
        self._s_max_rcond = value.asarray(self._s_max_rcond)
        self._tikhonov = value.asarray(self._tikhonov)
        self._tikhonov_alpha = value.asarray(self._tikhonov_alpha)
        self._tikhonov_rcond = value.asarray(self._tikhonov_rcond)
        self._vht = value.asarray(self._vht)
        self._vht_tikhonov = value.asarray(self._vht_tikhonov)
        self._ut = value.asarray(self._ut)

    @property
    def pinv(self) -> NDArray:
        return self._pinv

    @property
    def matrices(self) -> NDArray:
        return self._matrices

    def is_not_invertible(
        self,
        alpha: ArrayLike = 0.0,
        rtol: ArrayLike | None = None,
    ) -> NDArray[bool_]:
        alpha = _process_alpha(
            alpha,
            self.matrices.shape[-1],
            self.matrices.ndim,
            self.xp,
            self.matrices.dtype,
        )
        mtm = self.matrices.mT @ self.matrices  # ??? xp.conj()
        return is_not_invertible(mtm + alpha, rtol)

    def _compute_svd(self) -> None:
        u, s, vh = self.xp.linalg.svd(self.matrices, full_matrices=False)
        self._u = u
        self._s = s
        self._s2 = s**2
        self._vh = vh
        s_max = self.xp.max(s, axis=-1, keepdims=True)
        self._s_max = s_max
        self._s_max_rcond = s_max * self._rcond

        if self.xp.isdtype(self.matrices.dtype, "complex floating"):
            vht = self.xp.conj(vh.mT)
            ut = self.xp.conj(u.mT)
        elif self.xp.isdtype(self.matrices.dtype, "real floating"):
            vht = vh.mT
            ut = u.mT

        self._vht = vht
        self._ut = ut

        self._compute_tikhonov_alpha()
        self._compute_tikhonov_rcond()
        self._compute_tikhonov()
        self._compute_pinv()

    def _compute_tikhonov_alpha(self) -> None:
        # Call when alpha changes
        self._tikhonov_alpha = self._s / (self._s2 + self.alpha)

    def _compute_tikhonov_rcond(self) -> None:
        # Call when rcond changes
        self._tikhonov_rcond = self._s < self._s_max_rcond

    def _compute_tikhonov(self) -> None:
        # Call when alpha or rcond changes
        # After _compute_tikhonov_alpha or _compute_tikhonov_rcond
        self._tikhonov = self.xp.where(self._tikhonov_rcond, 0.0, self._tikhonov_alpha)
        self._vht_tikhonov = self._vht * self._tikhonov[..., None, :]

    def _compute_pinv(self) -> None:
        # Pseudo-inverse with Tikhonov regularization
        self._pinv = self._vht_tikhonov @ self._ut


class Lcs(_BaseLcs, mutable=True):
    def __init__(
        self,
        reference: NDArray,
        alpha: ArrayLike = 0.0,
        rcond: ArrayLike = 0.0,
        *,
        xp: ModuleType | None = None,
    ) -> None:
        super().__init__(reference, alpha, rcond, xp, _lcs_matrices)

    def __call__(
        self,
        sample: NDArray,
        weak_absorption: bool = False,
        search_window: int | tuple[int, int] | None = None,
        slices: tuple[slice, slice] | None = None,
    ) -> NDArray:
        result = super().__call__(sample, weak_absorption, search_window, slices)
        return PhaseRetrievalResult(
            transmission=result[..., 0],
            phase_gy=result[..., 1],
            phase_gx=result[..., 2],
        )


class LcsDf(_BaseLcs, mutable=True):
    def __init__(
        self,
        reference: NDArray,
        alpha: ArrayLike = 0.0,
        rcond: ArrayLike = 0.0,
        *,
        xp: ModuleType | None = None,
    ) -> None:
        super().__init__(reference, alpha, rcond, xp, _lcs_df_matrices)

    def __call__(
        self,
        sample: NDArray,
        weak_absorption: bool = False,
        search_window: int | tuple[int, int] | None = None,
        slices: tuple[slice, slice] | None = None,
    ) -> NDArray:
        result = super().__call__(sample, weak_absorption, search_window, slices)
        return PhaseRetrievalResult(
            transmission=result[..., 0],
            phase_gy=result[..., 1],
            phase_gx=result[..., 2],
            dark=result[..., 3],
        )


class LcsDDf(_BaseLcs, mutable=True):
    def __init__(
        self,
        reference: NDArray,
        alpha: ArrayLike = 0.0,
        rcond: ArrayLike = 0.0,
        *,
        xp: ModuleType | None = None,
    ) -> None:
        super().__init__(reference, alpha, rcond, xp, _lcs_ddf_matrices)

    def __call__(
        self,
        sample: NDArray,
        weak_absorption: bool = False,
        search_window: int | tuple[int, int] | None = None,
        slices: tuple[slice, slice] | None = None,
    ) -> NDArray:
        result = super().__call__(sample, weak_absorption, search_window, slices)
        return PhaseRetrievalResult(
            transmission=result[..., 0],
            phase_gy=result[..., 1],
            phase_gx=result[..., 2],
            dark_yy=result[..., 3],
            dark_xx=result[..., 4],
            dark_yx=result[..., 5],
        )
