from __future__ import annotations

import numpy as np
from numba import guvectorize

from dspeed.utils import numba_defaults_kwargs as nb_kwargs


@guvectorize(
    [
        "void(float32[:], float32[:])",
        "void(float64[:], float64[:])",
    ],
    "(n)->()",
    **nb_kwargs,
)
def t_pickup(wf_in: np.ndarray, t_out: float) -> None:
    """Pick the first non-nan entry in wf_in"""
    t_out[0] = np.nan

    for i in range(0, len(wf_in), 1):
        if not np.isnan(wf_in[i]):
            t_out[0] = wf_in[i]
            return
