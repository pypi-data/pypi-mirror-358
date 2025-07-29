from __future__ import annotations

import numpy as np
from numba import guvectorize

from dspeed.utils import numba_defaults_kwargs as nb_kwargs


@guvectorize([
    "void(float32[:], float32[:], float32[:], float32[:], float32[:])",
    "void(float64[:], float64[:], float64[:], float64[:], float64[:])",
], "(n),(),()->(),()", **nb_kwargs)
def db_pz_frac(
    wf_tail: np.ndarray,
    tau1: np.ndarray,
    tau2: np.ndarray,
    frac_out: float,
    A_out: float
) -> None:
    frac_out[0] = np.nan
    A_out[0] = np.nan

    if np.isnan(wf_tail).any() or np.isnan(tau1) or np.isnan(tau2):
        return

    N = wf_tail.shape[0]
    if N < 2:
        return

    # build normal-equations sums
    S00 = 0.0  # sum e1^2
    S01 = 0.0  # sum e1*e2
    S11 = 0.0  # sum e2^2
    Sy0 = 0.0  # sum e1 * y
    Sy1 = 0.0  # sum e2 * y

    for k in range(N):
        # basis functions at sample k
        e1 = np.exp(-k / tau1[0])
        e2 = np.exp(-k / tau2[0])
        y  = wf_tail[k]

        S00 += e1 * e1
        S01 += e1 * e2
        S11 += e2 * e2

        Sy0 += e1 * y
        Sy1 += e2 * y

    # solve [ [S00, S01], [S01, S11] ] [c1; c2] = [Sy0; Sy1]
    det = S00 * S11 - S01 * S01
    # avoid singular
    if abs(det) < 1e-12:
        return

    # Cramer's rule
    c1 = ( Sy0 * S11 - S01 * Sy1 ) / det
    c2 = ( S00 * Sy1 - S01 * Sy0 ) / det

    A = c1 + c2
    # avoid divide-by-zero
    if A == 0.0:
        return

    f = c2 / A

    frac_out[0] = f
    A_out[0] = A
