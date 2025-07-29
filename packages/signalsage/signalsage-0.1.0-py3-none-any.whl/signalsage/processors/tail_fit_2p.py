from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares
from numba import guvectorize

def _model(t, a, f, tau1, tau2):
    return a * ((1 - f) * np.exp(-t/tau1) + f * np.exp(-t/tau2))

def _residuals(params, x, y):
    return y - _model(x, *params)

@guvectorize([
    "void(float32[:], float32[:], float32[:], float32[:], float32[:])",
    "void(float64[:], float64[:], float64[:], float64[:], float64[:])",
], "(n)->(),(),(),()", forceobj=True)
def tail_fit_2p(
    wf_in: np.ndarray,
    tau1_out: float,
    tau2_out: float,
    f_out: float,
    A_out: float
) -> None:
    tau1_out[0] = np.nan
    tau2_out[0]   = np.nan
    f_out[0]   = np.nan
    A_out[0]   = np.nan

    t = 2075 + np.arange(len(wf_in))
    p0=[wf_in[0], 0.018, 4750, 200]
    res = least_squares(_residuals, p0, args=(t, wf_in),
                    method='lm')
    if not res.success:
        return

    A_out[0], f_out[0], tau1_out[0], tau2_out[0]  = res.x
