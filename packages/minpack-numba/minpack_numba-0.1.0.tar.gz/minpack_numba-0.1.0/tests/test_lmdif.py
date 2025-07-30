"""Python implementations of the tests from the minpack c-api test suite."""

from numba import carray, cfunc, njit
from numpy import array, empty, finfo, float64, int32, ones, sqrt
from numpy.linalg import norm
from numpy.testing import assert_allclose, assert_equal

from minpack_numba import lmdif, lmdif1, lmdif1_, lmdif_, lmdif_sig
from minpack_numba.utils import ptr_from_val, val_from_ptr

# ruff: noqa: ANN001, ARG001, PLR2004

UDATA = array(
    [
        1.4e-1,
        1.8e-1,
        2.2e-1,
        2.5e-1,
        2.9e-1,
        3.2e-1,
        3.5e-1,
        3.9e-1,
        3.7e-1,
        5.8e-1,
        7.3e-1,
        9.6e-1,
        1.34e0,
        2.1e0,
        4.39e0,
    ],
)
REFERENCE = array([0.8241058e-1, 0.1133037e1, 0.2343695e1])
TOL = sqrt(finfo(float64).eps)

M = 15
N = 3
LDFJAC = M
X0 = ones(N)
DIAG = ones(N)
IWA = empty(N, dtype=int32)
LWA = M * N + 5 * N + M
WA = empty(LWA)


def _check_results(x, fvec, info, tol=TOL):  # noqa: ANN202
    assert_equal(info, 1)
    assert_allclose(x, REFERENCE, atol=100 * tol)
    assert_allclose(norm(fvec), 0.9063596e-1, atol=tol)


@cfunc(lmdif_sig)
def trial_lmdif_fcn(m, n, x, fvec, iflag, udata):  # noqa: ANN201, D103, PLR0913
    y = UDATA

    if iflag[0] == 0:
        return

    for i in range(m):
        tmp1 = i + 1
        tmp2 = 16 - i - 1
        tmp3 = tmp2 if i >= 8 else tmp1

        fvec[i] = y[i] - (x[0] + tmp1 / (x[1] * tmp2 + x[2] * tmp3))

    return


@cfunc(lmdif_sig)
def trial_lmdif_fcn_udata(m, n, x, fvec, iflag, udata):  # noqa: ANN201, D103, PLR0913
    y = carray(udata, (15,), dtype=float64)

    if iflag[0] == 0:
        return

    for i in range(m):
        tmp1 = i + 1
        tmp2 = 16 - i - 1
        tmp3 = tmp2 if i >= 8 else tmp1

        fvec[i] = y[i] - (x[0] + tmp1 / (x[1] * tmp2 + x[2] * tmp3))

    return


@njit
def driver_lmdif1_(address, udata=None):  # noqa: ANN201, D103
    x = X0.copy()
    fvec = empty(M)
    infoptr = ptr_from_val(int32(0))
    wa = empty(LWA)
    iwa = empty(N, dtype=int32)
    _, _, _ = lmdif1_(address, M, N, x, fvec, TOL, infoptr, iwa, wa, LWA, udata)
    return x, fvec, val_from_ptr(infoptr)


@njit
def driver_lmdif_(address, udata=None):  # noqa: ANN201, D103
    x = X0.copy()
    diag = DIAG.copy()
    fvec = empty(M)
    infoptr = ptr_from_val(int32(0))
    nfevptr = ptr_from_val(int32(0))
    fjac = empty((M, N))
    qtf = empty(N)
    wa1 = empty(N)
    wa2 = empty(N)
    wa3 = empty(N)
    wa4 = empty(M)
    ipvt = empty(N, dtype=int32)

    args = address, M, N, x, fvec, TOL, TOL, 0.0, 2000, 0.0, diag, 1, 100.0, 0
    args2 = infoptr, nfevptr, fjac, LDFJAC, ipvt, qtf, wa1, wa2, wa3, wa4, udata
    _, _, _, _, _, _, info = lmdif_(*args, *args2)

    return x, fvec, info


def test_lmdif1() -> None:
    """Python implementation of the minpack c-api lmdif1 test."""
    x, fvec, info = lmdif1(trial_lmdif_fcn.address, M, X0, TOL)
    _check_results(x, fvec, info)


def test_lmdif1_() -> None:
    """Python implementation of the minpack c-api lmdif1 test."""
    x, fvec, info = driver_lmdif1_(trial_lmdif_fcn.address)
    _check_results(x, fvec, info)


def test_lmdif() -> None:
    """Python implementation of the minpack c-api lmdif test."""
    args = trial_lmdif_fcn.address, M, X0, TOL, TOL, 0.0, 2000, 0.0, DIAG, 1, 100.0, 0
    x, fvec, _, _, _, _, info = lmdif(*args)
    _check_results(x, fvec, info)


def test_lmdif_() -> None:
    """Python implementation of the minpack c-api lmdif test."""
    x, fvec, info = driver_lmdif_(trial_lmdif_fcn.address)
    _check_results(x, fvec, info)


def test_udata_lmdif1() -> None:
    """Python implementation of the minpack c-api lmdif1 test."""
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, info = lmdif1(trial_lmdif_fcn_udata.address, M, X0, TOL, i)
        _check_results(x, fvec, info)


def test_udata_lmdif1_() -> None:
    """Python implementation of the minpack c-api lmdif1 test."""
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, info = driver_lmdif1_(trial_lmdif_fcn_udata.address, i)
        _check_results(x, fvec, info)


def test_udata_lmdif() -> None:
    """Python implementation of the minpack c-api lmdif1 test."""
    address = trial_lmdif_fcn_udata.address
    args = address, M, X0, TOL, TOL, 0.0, 2000, 0.0, DIAG, 1, 100.0, 0
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, _, _, _, _, info = lmdif(*args, i)
        _check_results(x, fvec, info)


def test_udata_lmdif_() -> None:
    """Python implementation of the minpack c-api lmdif test."""
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, info = driver_lmdif_(trial_lmdif_fcn_udata.address, i)
        _check_results(x, fvec, info)
