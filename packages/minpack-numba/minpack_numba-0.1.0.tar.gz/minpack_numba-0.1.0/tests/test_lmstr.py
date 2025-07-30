"""Python implementations of the tests from the minpack c-api test suite."""

from numba import carray, cfunc, njit
from numpy import array, empty, finfo, float64, int32, ones, sqrt
from numpy.linalg import norm
from numpy.testing import assert_allclose, assert_equal

from minpack_numba import lmstr, lmstr1, lmstr1_, lmstr_, lmstr_sig
from minpack_numba.utils import ptr_from_val, val_from_ptr

# ruff: noqa: ANN001, ARG001, PLR2004

UDATA = array([10.0, 1.0])
REFERENCE = array([1.0, 1.0])
TOL = sqrt(finfo(float64).eps)

M = 2
N = 2
X0 = array([-1.2, 1.0])
FJAC = empty((M, N))
LDFJAC = M
IPVT = empty(N, dtype=int32)
LWA = M * N + 5 * N + M
WA = empty(LWA)
DIAG = ones(N)


def _check_result(x, fvec, info, nfev=None, njev=None, tol=TOL) -> None:  # noqa: PLR0913
    assert_equal(info, 4)
    if nfev is not None:
        assert_equal(nfev, 21)
    if njev is not None:
        assert_equal(njev, 16)
    assert_allclose(x, REFERENCE, atol=100 * tol)
    assert_allclose(norm(fvec), 0.0, atol=tol)


@cfunc(lmstr_sig)
def trial_lmstr_fcn(m, n, x, fvec, fjrow, iflag, udata):  # noqa: ANN201, D103, PLR0913
    if iflag[0] == 1:
        fvec[0] = 10.0 * (x[1] - x[0] ** 2)
        fvec[1] = 1.0 - x[0]
    elif iflag[0] == 2:
        fjrow[0] = -20.0 * x[0]
        fjrow[1] = 10.0
    else:
        fjrow[0] = -1.0
        fjrow[1] = 0.0


@cfunc(lmstr_sig)
def trial_lmstr_fcn_udata(m, n, x, fvec, fjrow, iflag, udata):  # noqa: ANN201, D103, PLR0913
    y = carray(udata, (2,), dtype=float64)
    if iflag[0] == 1:
        fvec[0] = y[0] * (x[1] - x[0] ** 2)
        fvec[1] = y[1] - x[0]
    elif iflag[0] == 2:
        fjrow[0] = -2.0 * y[0] * x[0]
        fjrow[1] = y[0]
    else:
        fjrow[0] = -1.0
        fjrow[1] = 0.0


@njit
def driver_lmstr1_(address, udata=None):  # noqa: ANN201, D103
    x = X0.copy()
    fvec = empty(M)
    fjac = empty((M, N))
    ipvt = empty(N, dtype=int32)
    wa = empty(LWA)
    infoptr = ptr_from_val(int32(0))

    args = address, M, N, x, fvec, fjac, LDFJAC, TOL, infoptr, ipvt, wa, LWA, udata

    _, _, _, _, _ = lmstr1_(*args)

    return x, fvec, val_from_ptr(infoptr)


@njit
def driver_lmstr_(address, udata=None):  # noqa: ANN201, D103
    x = X0.copy()

    fvec = empty(M)
    fjac = empty((M, N))
    diag = DIAG.copy()
    qtf = empty(N)
    wa1 = empty(N)
    wa2 = empty(N)
    wa3 = empty(N)
    wa4 = empty(M)
    ipvt = empty(N, dtype=int32)
    infoptr = ptr_from_val(int32(0))
    nfevptr = ptr_from_val(int32(0))
    njevptr = ptr_from_val(int32(0))

    args = address, M, N, x, fvec, fjac, LDFJAC, TOL, TOL, 0.0, 2000, diag, 1, 100.0, 0
    args2 = infoptr, nfevptr, njevptr, ipvt, qtf, wa1, wa2, wa3, wa4, udata

    _, _, _, _, _, _, _, _ = lmstr_(*args, *args2)

    return x, fvec, val_from_ptr(nfevptr), val_from_ptr(njevptr), val_from_ptr(infoptr)


def test_lmstr1() -> None:
    """Python implementation of teh minpack c-api lmstr1 test."""
    x, fvec, _, _, info = lmstr1(trial_lmstr_fcn.address, M, X0, TOL)
    _check_result(x, fvec, info)


def test_lmstr1_() -> None:
    """Python implementation of the minpack c-api lmstr1 test."""
    x, fvec, info = driver_lmstr1_(trial_lmstr_fcn.address)
    _check_result(x, fvec, info)


def test_lmstr() -> None:
    """Python implementation of the minpack c-api lmstr test."""
    args = trial_lmstr_fcn.address, M, X0, TOL, TOL, 0.0, 2000, DIAG, 1, 100.0, 0
    x, fvec, _, _, _, nfev, njev, info = lmstr(*args)
    _check_result(x, fvec, info, nfev, njev)


def test_lmstr_() -> None:
    """Python implementation of the minpack c-api lmstr test."""
    x, fvec, nfev, njev, info = driver_lmstr_(trial_lmstr_fcn.address)
    _check_result(x, fvec, info, nfev, njev)


def test_udata_lmstr1() -> None:
    """Python implementation of a modified minpack c-api lmstr1 test."""
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, _, _, info = lmstr1(trial_lmstr_fcn_udata.address, M, X0, TOL, i)
        _check_result(x, fvec, info)


def test_udata_lmstr1_() -> None:
    """Python implementation of a modified minpack c-api lmstr1 test."""
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, info = driver_lmstr1_(trial_lmstr_fcn_udata.address, i)
        _check_result(x, fvec, info)


def test_udata_lmstr() -> None:
    """Python implementation of a modified minpack c-api lmstr test."""
    args = trial_lmstr_fcn_udata.address, M, X0, TOL, TOL, 0.0, 2000, DIAG, 1, 100.0, 0
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, _, _, _, nfev, njev, info = lmstr(*args, i)
        _check_result(x, fvec, info, nfev, njev)


def test_udata_lmstr_() -> None:
    """Python implementation of the minpack c-api lmstr test."""
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, nfev, njev, info = driver_lmstr_(trial_lmstr_fcn_udata.address, i)
        _check_result(x, fvec, info, nfev, njev)
