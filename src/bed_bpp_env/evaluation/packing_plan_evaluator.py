"""
This module contains a packing plan evaluator class.
"""

import ast
import logging
import shutil
from typing import Literal

import pandas as pd

from bed_bpp_env.data_model.order import Order
from bed_bpp_env.data_model.packing_plan import PackingPlan
from bed_bpp_env.environment.cuboid import Cuboid
from bed_bpp_env.environment.space_3d import Space3D
from bed_bpp_env.evaluation import EVALOUTPUTDIR
from bed_bpp_env.evaluation.kpis import FILE_KPI_DEFINITION, KPI_DEFINITION, KPIs

logger = logging.getLogger(__name__)

EVALUATION_HEIGHT = 1000 * KPI_DEFINITION["eval_score_pal_ratio"].get("threshold")
"""The threshold of the height for which items count as unpalletized in the score evaluation in millimeters."""
STABILITY_Z_THRESHOLD = KPI_DEFINITION["stability"].get("threshold")
"""Indicates at which value of the z-movements in meters of any item the target counts as unstable."""


class PackingPlanEvaluator:
    """
    An instance of this class evaluates a packing plan. It is designed that for a complete output file of a solver, every order is evaluated and finally, the means of the KPIs are calculated. The used evaluation criteria are defined in `kpi_definition.yaml` and the results are stored in the evaluation output folder with the name `evaluation.xlsx`.

    Attributes.
    -----------
    _evaluation_kpis: list
        The values of the KPIs for each order that are stored in a file.
    _kpis: KPIs
        tbd
    _order: dict
          The order for which the currently investigated packing plan was created.'
    _order_id: str
        The ID of the order for which the currently investigated packing plan was created.
    _packing_plan: list
        The packing plan that is currently investigated. It is a list of actions.
    _target_space: Space3D
        The target that represents the rebuilt packing plan.
    """

    def __init__(self) -> None:
        self._evaluation_kpis = []
        """The values of the KPIs for each order that are stored in a file."""
        self._order_id = ""
        """The ID of the order for which the currently investigated packing plan was created."""
        self._order = {}
        """The order for which the currently investigated packing plan was created."""
        self._packing_plan = []
        """The packing plan that is currently investigated. It is a list of actions."""
        self._kpis = KPIs()
        """An instance of this class is responsible for the calculation of the KPIs. It is coupled with the target space."""
        self._target_space = Space3D()
        """The target that represents the rebuilt packing plan."""

    def evalStability(self) -> Literal[0, 1]:
        """
        This method evaluates the results of the Blender rigid body simulation and decides whether a packing plan prodcues a stable outcome.

        It is checked whether the maximum movement of an item in z-direction is bigger than a given threshold in the stability file that is produced by the rigid body simulation.

        Returns.
        --------
        Either `1` for stable piles or `0` for unstable.
        """
        VAL_STABLE, VAL_UNSTABLE = 1, 0

        with open(EVALOUTPUTDIR.joinpath("stability.txt")) as file:
            stability_information = file.readlines()

        # the last line from the file should be the correct
        for line in reversed(stability_information):
            order_in_line, value = line.split(":", maxsplit=1)

            if order_in_line == self._order_id:
                # found correct line
                value_dict = ast.literal_eval(value)
                if value_dict.get("max_z-movements/m") > STABILITY_Z_THRESHOLD:
                    return VAL_UNSTABLE
                else:
                    return VAL_STABLE

        raise ValueError("order ids do not match")

    def evalSupportArea(self) -> float:
        """
        This method evaluates the support areas of all items in a packing plan.

        The value of this KPI is in [0, 1).

        Returns.
        --------
        meanSupportArea: float
            The mean of the support areas of all items in a packing plan.
        """
        return self._kpis.getMeanSupportArea()

    def evalVolumeUtilization(self) -> float:
        """
        This method evaluates how many times the volume of the items is needed on the target caused by the pile of a packing plan.

        The value of this KPI is in [1, \infty).

        Returns.
        --------
        volUtilization: float
            How many times the volume of the items is needed on the target caused by the pile of a packing plan.
        """
        return self._kpis.getVolumeUtilization()

    def evalMaxHeightOnTarget(self) -> float:
        """
        This method evaluates the height of a pile. It returns the biggest height in meters.

        The value of this KPI is in [0, \infty).

        Returns.
        --------
        maxHeightInM: float
            The hightest point of a pile in meter.
        """
        return self._kpis.getMaxHeightOnTarget() / 1000.0

    def evalUnpalletizedOrderRatio(self) -> float:
        """
        This method evaluates the ratio of the number of unpalletized items with the number of items in an order. This KPI can be understand as how many percent of an order are not palletized.

        Returns.
        --------
        unpalletizedOrderRatio: float
            Indicates the ratio of an order that is not palletized.
        """
        n_items_in_order = len(self._order.item_sequence)
        n_items_unpalletized = n_items_in_order - len(self._packing_plan)

        return float(n_items_unpalletized / n_items_in_order)

    def evalScorePalletizingHeight(self, evalheightlevel: int = EVALUATION_HEIGHT) -> float:
        """
        This method returns the height of the highest pile of a given packing plan, where all items that are not completely below the parameter `evalheightlevel` are removed.

        Parameters.
        -----------
        evalheightlevel:int
            The height level in millimeters.

        Returns.
        --------
        maxHeightInM: float
            The value of the highest pile in meters.
        """
        max_height_in_mm = self._target_space.getMaximumHeightBelowHeightLevel(evalheightlevel)
        return round(max_height_in_mm / 1000.0, 3)

    def evalScoreOrderPalletizingRatio(self, evalheightlevel: int = EVALUATION_HEIGHT) -> float:
        """
        This method calculates the ratio of number of palletized items with the number of items in an order with respect to the stability of the pile.

        Parameters.
        -----------
        evalheightlevel: int
            The height level in millimeters.

        Returns.
        --------
        palletizing_ratio_score: float
            For stable piles this is the value of the palletizing order ratio, else it is 0.
        """
        evaluation_height_level = evalheightlevel

        is_stable = self.evalStability()
        n_items_in_order = len(self._order.item_sequence)
        number_items_above_eval_height_levelon_pallet = self._target_space.getItemsAboveHeightLevel(
            evaluation_height_level
        )
        number_items_on_pallet = len(self._target_space.getPlacedItems())

        palletizing_ratio = (number_items_on_pallet - number_items_above_eval_height_levelon_pallet) / n_items_in_order
        palletizing_ratio_score = is_stable * palletizing_ratio

        return palletizing_ratio_score

    def evalScoreAbsoluteNStablePalletizedItems(self, evalheightlevel: int = EVALUATION_HEIGHT) -> int:
        """
        This method counts the total number of items that were palletized in a stable manner below the given height level.

        If the built pile was unstable, this method returns `0`.

        Parameters.
        -----------
        evalheightlevel: int
            The height level in millimeters.

        Returns.
        --------
        number_stable_palletized_items: float
            For stable piles this is the value of the palletizing order ratio, else it is 0.
        """
        is_stable = self.evalStability()
        number_items_above_eval_height_level = self._target_space.getItemsAboveHeightLevel(evalheightlevel)
        number_items_below_eval_height_level = (
            len(self._target_space.getPlacedItems()) - number_items_above_eval_height_level
        )

        number_stable_palletized_items = is_stable * number_items_below_eval_height_level
        return number_stable_palletized_items

    def evalInterlockingRatio(self) -> float:
        """
        This method evaluates the interlocking ratio of the packing plan. Items that are considered for this KPI are not directly placed at the target.

        Returns.
        --------
        interlockingRatio: float
            The interlocking ratio of the packing plan.
        """
        placed_items = self._target_space.getPlacedItems()
        interlocking_ratio_enumerator = 0
        interlocking_ratio_denominator = 0

        for item in placed_items:
            items_below_item = item.items_below
            number_items_below_item = len(items_below_item)

            if not (number_items_below_item == 0):
                # item is not directly placed on target
                interlocking_ratio_denominator += 1

                # check whether item contributes to enumerator
                if number_items_below_item > 1:
                    interlocking_ratio_enumerator += 1
                elif number_items_below_item == 1:
                    if item.orientation != placed_items[0].orientation:
                        interlocking_ratio_enumerator += 1

        logger.debug(f"r_interl = {interlocking_ratio_enumerator} / {interlocking_ratio_denominator}")

        interlocking_ratio = (
            pd.NA
            if interlocking_ratio_denominator == 0
            else float(interlocking_ratio_enumerator / interlocking_ratio_denominator)
        )
        return interlocking_ratio

    def evaluate(self, packing_plan: PackingPlan, order: dict) -> dict:
        """
        This method evaluates the packing plan for a given order.

        Parameters.
        -----------
        order_id: str
            The id of the order which packing plan is evaluated.
        order: dict
            The order of the packing plan.
        packingplan: list
            The result of an algorithm for an order.

        Returns.
        --------
        KPIs: dict
            The values of the KPIs of the currently investigated packing plan.

        Examples.
        ---------
        >>> KPIs
        {
            'order_id': '00100001',
            'kpi_1': 0.0,
            'kpi_2': 1.277017760536967,
            'kpi_3': 3.97,
            'kpi_4': 0.8335259392910519,
            'kpi_5': 1,
            'kpi_6': 1,
            'eval_score_pal_ratio': 0.7272727272727273,
            'eval_score_height': 1.849,
            'eval_score_absolute_n_stable_pal_items': 32
        }
        """
        order_id = packing_plan.id
        self._order_id = order_id

        order_data = {"id": order_id}
        order_data.update(order)

        self._order = Order.from_dict(order_data)
        self._packing_plan = packing_plan.actions

        logger.info(f"evaluate order {order_id}")

        # rebuild target space
        target = self._order.properties.target
        if target == "euro-pallet":
            target_size = (1200, 800)
        elif target == "rollcontainer":
            target_size = (800, 700)
        else:
            raise ValueError(f"target {target} unknown")
        self._target_space.reset(target_size)

        self._kpis.reset(self._target_space, self._order)

        for action in self._packing_plan:
            cuboid = Cuboid(action.item)
            cuboid.set_orientation(action.orientation)
            self._target_space.addItem(cuboid, action.orientation, action.flb_coordinates.xyz)
            self._kpis.update()

        # obtain the values of the KPIs
        kpis_dict = {"order_id": self._order_id}
        for kpi_def_dict in KPI_DEFINITION.values():
            logger.info(kpi_def_dict)
            try:
                kpi_method = getattr(self, kpi_def_dict.get("method"))
                if "eval_score" in kpi_def_dict.get("name"):
                    kpis_dict[kpi_def_dict.get("name")] = kpi_method()
                else:
                    kpis_dict[f"kpi_{kpi_def_dict.get('num')}"] = kpi_method()
            except Exception as e:
                msg = "method missing"
                logger.warning(msg)
                logger.exception(e)
                kpis_dict[f"kpi_{kpi_def_dict.get('num')}"] = msg

        self._evaluation_kpis.append(kpis_dict)
        return kpis_dict

    def writeToFile(self, totalamountitems: int = 1) -> None:
        """Writes the stored values of the KPIs to a file with name `"evaluation.xlsx"`."""
        df_orderwise_evaluation = pd.DataFrame(data=self._evaluation_kpis)

        # get the column names in the dataframe
        stability_col_name = f"kpi_{KPI_DEFINITION['stability'].get('num')}"

        # calculate overview KPIs
        overview_dict = {
            "stable": df_orderwise_evaluation[stability_col_name].value_counts(normalize=True).get(1),
            "unstable": df_orderwise_evaluation[stability_col_name].value_counts(normalize=True).get(0),
            "avg_eval_score_pal_ratio": df_orderwise_evaluation["eval_score_pal_ratio"].mean(),
            "avg_target_height/m": df_orderwise_evaluation["eval_score_height"].mean(),
            "n_stable_palletized_items": df_orderwise_evaluation["eval_score_absolute_n_stable_pal_items"].sum(),
            "rating_algorithm": df_orderwise_evaluation["eval_score_absolute_n_stable_pal_items"].sum()
            / totalamountitems,
        }
        logger.info(f"SCORE OF ALGORITHM = {round(overview_dict['rating_algorithm'], 6)}")
        overview_df = pd.DataFrame.from_dict(overview_dict, orient="index")

        kpi_definition_file = FILE_KPI_DEFINITION
        if not EVALOUTPUTDIR.exists():
            EVALOUTPUTDIR.mkdir(exist_ok=True)
        shutil.copy(kpi_definition_file, EVALOUTPUTDIR.joinpath(kpi_definition_file.name))

        with pd.ExcelWriter(EVALOUTPUTDIR.joinpath("evaluation.xlsx"), mode="w") as writer:
            overview_df.to_excel(writer, sheet_name="overview", index=True)
            df_orderwise_evaluation.to_excel(writer, sheet_name="orderwise", index=False)
