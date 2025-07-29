from __future__ import annotations

import numpy as np
from numba import guvectorize

from dspeed.errors import DSPFatal
from dspeed.utils import numba_defaults_kwargs as nb_kwargs

@guvectorize(["void(float32[:], float32, float32, float32[:])",
            "void(float64[:], float64, float64, float64[:])"],
            "(n),(),()->(n)", **nb_kwargs(nopython=True))

def integrate(wf_in: np.ndarray, t0_in: float, tend_in: float, wf_out: np.ndarray) -> None:
    """Integrate the wf_in from t0 to t_end"""
    wf_out[:] = np.nan

    if np.isnan(wf_in).any():
        raise DSPFatal("nan values found in the input waveform in integrate processor")
    
    if t0_in > (len(wf_in) - 1):
        return

    if np.isnan(t0_in):
        return
    else:
        t0 = int(t0_in)

    if np.isnan(tend_in):
        return
        # tend = len(wf_out) - 2
    else:
        tend = int(tend_in)
    
    if tend > len(wf_in):
        tend = len(wf_in)
    if t0 < 0:
        t0 = 0

    wf_out[:t0] = wf_in[t0]
    wf_out[t0:tend] = wf_in[t0:tend]

    for i in range(t0 + 1, tend, 1):
        for j in range(t0, i, 1):
            wf_out[i] += wf_in[j]

    wf_out[tend:] = wf_out[tend-1]
