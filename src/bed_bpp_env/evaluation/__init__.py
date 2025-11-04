"""
The `evaluation` package contains the definition of the KPIs and the methods for our Blender Stability check.

Note that it is neither checked whether the file `kpi_definition.yaml` contains unique keys, nor whether the values of `num` are unique.
"""

from bed_bpp_env.utils import OUTPUTDIRECTORY

EVALOUTPUTDIR = OUTPUTDIRECTORY.joinpath("evaluation/")
EVALOUTPUTDIR.mkdir(exist_ok=True)
