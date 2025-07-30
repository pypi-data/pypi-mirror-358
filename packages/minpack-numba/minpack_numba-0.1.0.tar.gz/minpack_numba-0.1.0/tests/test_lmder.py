"""Python implementation of the tests from the minpack c-api test suite."""

from numba import carray, cfunc, njit
from numpy import array, empty, finfo, float64, int32, ones, sqrt
from numpy.linalg import norm
from numpy.testing import assert_allclose, assert_equal

from minpack_numba import chkder, lmder, lmder1, lmder1_, lmder_, lmder_sig
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
M = int32(15)
N = int32(3)
LWA = 5 * N + M
X0 = ones(N)
FJAC = empty((M, N))
LDFJAC = M
IPVT = empty(N, dtype=int32)
WA = empty(LWA)
DIAG = ones(N)


def _check_results(x, fvec, info, tol=TOL):  # noqa: ANN202
    assert_equal(info, 1)
    assert_allclose(x, REFERENCE, atol=100 * tol)
    assert_allclose(norm(fvec), 0.9063596e-1, tol)


@cfunc(lmder_sig)
def trial_lmder_fcn(m, n, x, fvec, fjac, ldfjac, iflag, udata):  # noqa: ANN201, D103, PLR0913
    y = UDATA
    if iflag[0] == 1:
        for i in range(m):
            tmp1 = i + 1
            tmp2 = 16 - i - 1
            tmp3 = tmp2 if i >= 8 else tmp1

            fvec[i] = y[i] - (x[0] + tmp1 / (x[1] * tmp2 + x[2] * tmp3))
    elif iflag[0] == 2:
        for i in range(m):
            tmp1 = i + 1
            tmp2 = 16 - i - 1
            tmp3 = tmp2 if i >= 8 else tmp1
            tmp4 = pow(x[1] * tmp2 + x[2] * tmp3, 2)
            fjac[i] = -1.0
            fjac[i + ldfjac] = tmp1 * tmp2 / tmp4
            fjac[i + 2 * ldfjac] = tmp1 * tmp3 / tmp4


@cfunc(lmder_sig)
def trial_lmder_fcn_udata(m, n, x, fvec, fjac, ldfjac, iflag, udata):  # noqa: ANN201, D103, PLR0913
    y = carray(udata, (15,), dtype=float64)
    if iflag[0] == 1:
        for i in range(m):
            tmp1 = i + 1
            tmp2 = 16 - i - 1
            tmp3 = tmp2 if i >= 8 else tmp1

            fvec[i] = y[i] - (x[0] + tmp1 / (x[1] * tmp2 + x[2] * tmp3))
    elif iflag[0] == 2:
        for i in range(m):
            tmp1 = i + 1
            tmp2 = 16 - i - 1
            tmp3 = tmp2 if i >= 8 else tmp1
            tmp4 = pow(x[1] * tmp2 + x[2] * tmp3, 2)
            fjac[i] = -1.0
            fjac[i + ldfjac] = tmp1 * tmp2 / tmp4
            fjac[i + 2 * ldfjac] = tmp1 * tmp3 / tmp4


@njit
def driver_trial_lmder_fcn(udata, m, n, x, fvec, fjac, ldfjac, iflag):  # noqa: ANN201, D103, PLR0913
    args = m, n, x.ctypes, fvec.ctypes, fjac.ctypes, ldfjac, iflag.ctypes, udata.ctypes
    return trial_lmder_fcn(*args)


@njit
def driver_trial_lmder_fcn_udata(udata, m, n, x, fvec, fjac, ldfjac, iflag):  # noqa: ANN201, D103, PLR0913
    args = m, n, x.ctypes, fvec.ctypes, fjac.ctypes, ldfjac, iflag.ctypes, udata.ctypes
    return trial_lmder_fcn_udata(*args)


@njit
def driver_lmder1_(address, udata=None):
    x = X0.copy()
    fvec = empty(M)
    fjac = empty((M, N))
    ipvt = empty(N, dtype=int32)
    wa = empty(LWA)
    infoptr = ptr_from_val(int32(0))
    args = address, M, N, x, fvec, fjac, LDFJAC, TOL, infoptr, ipvt, wa, LWA, udata
    _, _, _, _, _ = lmder1_(*args)
    return x, fvec, val_from_ptr(infoptr)


@njit
def driver_lmder_(address, udata=None):  # noqa: ANN201, D103
    infoptr = ptr_from_val(int32(0))
    nfevptr = ptr_from_val(int32(0))
    njevptr = ptr_from_val(int32(0))
    x = X0.copy()
    fvec = empty(M)
    diag = DIAG.copy()
    fjac = empty((M, N))
    qtf = empty(N)
    wa1 = empty(N)
    wa2 = empty(N)
    wa3 = empty(N)
    wa4 = empty(M)
    ipvt = empty(N, dtype=int32)

    args = address, M, N, x, fvec, fjac, LDFJAC, TOL, TOL, 0.0, 2000, diag, 1, 100.0, 0
    args2 = infoptr, nfevptr, njevptr, ipvt, qtf, wa1, wa2, wa3, wa4, udata

    _, _, _, _, _, _, _, info = lmder_(*args, *args2)
    return x, fvec, info


def test_lmder1() -> None:
    """Python implementation of a modified minpack c-api lmder1 test."""
    xp = empty(N)
    fvec = empty(M)
    fvecp = empty(M)
    err = empty(M)

    _udata = array(0, dtype=float64)
    chkder(M, N, X0, fvec, FJAC, M, xp, fvecp, 1, err)
    driver_trial_lmder_fcn(_udata, M, N, X0, fvec, FJAC, M, array(1, dtype=int32))
    driver_trial_lmder_fcn(_udata, M, N, X0, fvec, FJAC, M, array(2, dtype=int32))
    driver_trial_lmder_fcn(_udata, M, N, xp, fvecp, FJAC, M, array(1, dtype=int32))
    chkder(M, N, X0, fvec, FJAC, M, xp, fvecp, 2, err)

    assert_allclose(err, 1.0, atol=TOL)

    x, fvec, _, _, info = lmder1(trial_lmder_fcn.address, M, X0, TOL)
    _check_results(x, fvec, info)


def test_lmder1_() -> None:
    """Python implementation a modified minpack c-api lmder1 test."""
    x, fvec, info = driver_lmder1_(trial_lmder_fcn.address)
    _check_results(x, fvec, info)


# @pytest.mark.skip(reason="Not implemented")
def test_lmder() -> None:
    """Python implementation a modified minpack c-api lmder test."""
    args = trial_lmder_fcn.address, M, X0, TOL, TOL, 0.0, 2000, DIAG, 1, 100.0, 0
    x, fvec, _, _, _, _, _, info = lmder(*args)
    _check_results(x, fvec, info)


# @pytest.mark.skip(reason="Not implemented")
def test_lmder_() -> None:
    """Python implementation a modified minpack c-api lmder test."""
    x, fvec, info = driver_lmder_(trial_lmder_fcn.address)
    _check_results(x, fvec, info)


def test_udata_lmder1() -> None:
    """Python implementation of the minpack c-api lmder1 test."""
    xp = empty(N)
    fvec = empty(M)
    fvecp = empty(M)
    err = empty(M)

    chkder(M, N, X0, fvec, FJAC, M, xp, fvecp, 1, err)
    driver_trial_lmder_fcn_udata(UDATA, M, N, X0, fvec, FJAC, M, array(1, dtype=int32))
    driver_trial_lmder_fcn_udata(UDATA, M, N, X0, fvec, FJAC, M, array(2, dtype=int32))
    driver_trial_lmder_fcn_udata(UDATA, M, N, xp, fvecp, FJAC, M, array(1, dtype=int32))
    chkder(M, N, X0, fvec, FJAC, M, xp, fvecp, 2, err)

    assert_allclose(err, 1.0, atol=TOL)

    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, _, _, info = lmder1(trial_lmder_fcn_udata.address, M, X0, TOL, i)
        _check_results(x, fvec, info)


def test_udata_lmder1_() -> None:
    """Python implementation of the minpack c-api lmder1 test."""
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, info = driver_lmder1_(trial_lmder_fcn_udata.address, i)
        _check_results(x, fvec, info)


def test_udata_lmder() -> None:
    """Python implementation of the minpack c-api lmder1 test."""
    args = trial_lmder_fcn_udata.address, M, X0, TOL, TOL, 0.0, 2000, DIAG, 1, 100.0, 0
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, _, _, _, _, _, info = lmder(*args, i)
        _check_results(x, fvec, info)


def test_udata_lmder_() -> None:
    """Python implementation of the minpack c-api lmder test."""
    for i in (UDATA, UDATA.ctypes.data):
        x, fvec, info = driver_lmder_(trial_lmder_fcn.address, i)
        _check_results(x, fvec, info)
