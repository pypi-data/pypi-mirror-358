from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares
from numba import guvectorize

def _model(t, a, tau, c):
    return a * np.exp(-t/tau) + c

def _residuals(params, x, y):
    return y - _model(x, *params)

@guvectorize([
    "void(float32[:], float32[:], float32[:], float32[:])",
    "void(float64[:], float64[:], float64[:], float64[:])",
], "(n)->(),(),()", forceobj=True)
def tail_fit(
    wf_in: np.ndarray,
    tau_out: float,
    A_out: float,
    C_out: float,
) -> None:
    tau_out[0] = np.nan
    A_out[0]   = np.nan
    C_out[0]   = np.nan

    t = 2050 + np.arange(len(wf_in))
    p0=[np.mean(wf_in)*1000, 200, np.mean(wf_in)]
    res = least_squares(_residuals, p0, args=(t, wf_in),
                    method='lm')
    if not res.success:
        return

    A_out[0], tau_out[0], C_out[0] = res.x
