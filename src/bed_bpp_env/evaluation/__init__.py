"""
The `evaluation` package contains the definition of the KPIs and the methods for our Blender Stability check.

Note that it is neither checked whether the file `kpi_definition.yaml` contains unique keys, nor whether the values of `num` are unique.
"""

from bed_bpp_env.utils import OUTPUTDIRECTORY
import pathlib
import yaml

EVALOUTPUTDIR = OUTPUTDIRECTORY.joinpath("evaluation/")
EVALOUTPUTDIR.mkdir(exist_ok=True)


FILE_KPI_DEFINITION = pathlib.Path(__file__).parent.resolve().joinpath("kpi_definition.yaml")
with open(FILE_KPI_DEFINITION) as file:
    KPI_DEFINITION = yaml.load(file, Loader=yaml.loader.SafeLoader)
