"""
Classes within this package can be used to obtain actions that can be handed over to the PalletizingEnvironment in gym format.

Each class must have the method `getAction` with parameters `observation:np.ndarray` and `info:dict`!
"""

from heuristics.LowestArea import LowestArea
from heuristics.O3DBP_3_2 import O3DBP_3_2
