import importlib.metadata
__version__ = importlib.metadata.version("signalsage")

from .processors.integrate import integrate
from .processors.t_pickup import t_pickup
from .processors.time_point_thresh import time_point_thresh

__all__ = [
    "integrate",
    "t_pickup",
    "time_point_thresh"
]
