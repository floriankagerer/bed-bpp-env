"""
This module contains a packing plan evaluator class.
"""

import ast
import logging
import shutil
from typing import Literal

import pandas as pd

from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.order import Order
from bed_bpp_env.environment.cuboid import Cuboid
from bed_bpp_env.environment.space_3d import Space3D
from bed_bpp_env.evaluation import EVALOUTPUTDIR, FILE_KPI_DEFINITION, KPI_DEFINITION
from bed_bpp_env.evaluation.kpis import KPIs

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
    __EvaluationKPIs: list
        The values of the KPIs for each order that are stored in a file.
    __KPIs: KPIs
        tbd
    _order: dict
          The order for which the currently investigated packing plan was created.'
    __OrderID: str
        The ID of the order for which the currently investigated packing plan was created.
    __PackingPlan: list
        The packing plan that is currently investigated. It is a list of actions.
    __TargetSpace: Space3D
        The target that represents the rebuilt packing plan.
    """

    def __init__(self) -> None:
        self.__EvaluationKPIs = []
        """The values of the KPIs for each order that are stored in a file."""
        self.__OrderID = ""
        """The ID of the order for which the currently investigated packing plan was created."""
        self._order = {}
        """The order for which the currently investigated packing plan was created."""
        self.__PackingPlan = []
        """The packing plan that is currently investigated. It is a list of actions."""
        self.__KPIs = KPIs()
        """An instance of this class is responsible for the calculation of the KPIs. It is coupled with the target space."""
        self.__TargetSpace = Space3D()
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
            stabilityInformation = file.readlines()

        # the last line from the file should be the correct
        for line in reversed(stabilityInformation):
            orderInLine, value = line.split(":", maxsplit=1)

            if orderInLine == self.__OrderID:
                # found correct line
                valueDict = ast.literal_eval(value)
                if valueDict.get("max_z-movements/m") > STABILITY_Z_THRESHOLD:
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
        return self.__KPIs.getMeanSupportArea()

    def evalVolumeUtilization(self) -> float:
        """
        This method evaluates how many times the volume of the items is needed on the target caused by the pile of a packing plan.

        The value of this KPI is in [1, \infty).

        Returns.
        --------
        volUtilization: float
            How many times the volume of the items is needed on the target caused by the pile of a packing plan.
        """
        return self.__KPIs.getVolumeUtilization()

    def evalMaxHeightOnTarget(self) -> float:
        """
        This method evaluates the height of a pile. It returns the biggest height in meters.

        The value of this KPI is in [0, \infty).

        Returns.
        --------
        maxHeightInM: float
            The hightest point of a pile in meter.
        """
        return self.__KPIs.getMaxHeightOnTarget() / 1000.0

    def evalUnpalletizedOrderRatio(self) -> float:
        """
        This method evaluates the ratio of the number of unpalletized items with the number of items in an order. This KPI can be understand as how many percent of an order are not palletized.

        Returns.
        --------
        unpalletizedOrderRatio: float
            Indicates the ratio of an order that is not palletized.
        """
        nItemsInOrder = len(self._order["item_sequence"])
        nUnpalItems = nItemsInOrder - len(self.__PackingPlan)

        return float(nUnpalItems / nItemsInOrder)

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
        maxHeightInMM = self.__TargetSpace.getMaximumHeightBelowHeightLevel(evalheightlevel)
        return round(maxHeightInMM / 1000.0, 3)

    def evalScoreOrderPalletizingRatio(self, evalheightlevel: int = EVALUATION_HEIGHT) -> float:
        """
        This method calculates the ratio of number of palletized items with the number of items in an order with respect to the stability of the pile.

        Parameters.
        -----------
        evalheightlevel: int
            The height level in millimeters.

        Returns.
        --------
        palletizingRatioScore: float
            For stable piles this is the value of the palletizing order ratio, else it is 0.
        """
        evalHeightLevel = evalheightlevel

        isStable = self.evalStability()
        itemsInOrder = len(self._order["item_sequence"])
        unpalletizedItems = self.__TargetSpace.getItemsAboveHeightLevel(evalHeightLevel)
        itemsOnPallet = len(self.__TargetSpace.getPlacedItems())

        palletizationRatio = (itemsOnPallet - unpalletizedItems) / itemsInOrder
        palletizingRatioScore = isStable * palletizationRatio

        return palletizingRatioScore

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
        nStablePalletizedItems: float
            For stable piles this is the value of the palletizing order ratio, else it is 0.
        """
        isStable = self.evalStability()
        unpalletizedItems = self.__TargetSpace.getItemsAboveHeightLevel(evalheightlevel)
        nItemsOnPalletBelowThreshold = len(self.__TargetSpace.getPlacedItems()) - unpalletizedItems

        nStablePalletizedItems = isStable * nItemsOnPalletBelowThreshold
        return nStablePalletizedItems

    def evalInterlockingRatio(self) -> float:
        """
        This method evaluates the interlocking ratio of the packing plan. Items that are considered for this KPI are not directly placed at the target.

        Returns.
        --------
        interlockingRatio: float
            The interlocking ratio of the packing plan.
        """
        placedItems = self.__TargetSpace.getPlacedItems()
        rInterlEnumerator = 0
        rInterlDenominator = 0

        for item in placedItems:
            itemsBelowItem = item.getItemsBelow()
            nItemsBelow = len(itemsBelowItem)

            if not (nItemsBelow == 0):
                # item is not directly placed on target
                rInterlDenominator += 1

                # check whether item contributes to enumerator
                if nItemsBelow > 1:
                    rInterlEnumerator += 1
                elif nItemsBelow == 1:
                    if not (item.getOrientation() == placedItems[0].getOrientation()):
                        rInterlEnumerator += 1

        logger.debug(f"r_interl = {rInterlEnumerator} / {rInterlDenominator}")

        rInterl = pd.NA if rInterlDenominator == 0 else float(rInterlEnumerator / rInterlDenominator)
        return rInterl

    def evaluate(self, orderid: str, order: dict, packingplan: list) -> dict:
        """
        This method evaluates the packing plan for a given order.

        Parameters.
        -----------
        orderid: str
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
        self.__OrderID = orderid

        order_data = {"id": orderid}
        order_data.update(order)

        self._order = Order.from_dict(order_data)
        self.__PackingPlan = packingplan

        logger.info(f"evaluate order {orderid}")

        # rebuild target space
        target = self._order.properties.target
        if target == "euro-pallet":
            target_size = (1200, 800)
        elif target == "rollcontainer":
            target_size = (800, 700)
        else:
            raise ValueError(f"target {target} unknown")
        self.__TargetSpace.reset(target_size)

        self.__KPIs.reset(self.__TargetSpace, self._order)

        for action in self.__PackingPlan:
            item = Item.from_dict(action["item"])
            cuboid = Cuboid(item)
            cuboid.setOrientation(action["orientation"])
            flbCoordinates = [int(coord) for coord in action["flb_coordinates"]]
            self.__TargetSpace.addItem(cuboid, action["orientation"], flbCoordinates)
            self.__KPIs.update()

        # obtain the values of the KPIs
        KPIs = {"order_id": self.__OrderID}
        for kpiDict in KPI_DEFINITION.values():
            try:
                kpiMethod = getattr(self, kpiDict.get("method"))
                if "eval_score" in kpiDict.get("name"):
                    KPIs[kpiDict.get("name")] = kpiMethod()
                else:
                    KPIs[f"kpi_{kpiDict.get('num')}"] = kpiMethod()
            except:
                msg = "method missing"
                logger.warning(msg)
                KPIs[f"kpi_{kpiDict.get('num')}"] = msg

        self.__EvaluationKPIs.append(KPIs)
        return KPIs

    def writeToFile(self, totalamountitems: int = 1) -> None:
        """Writes the stored values of the KPIs to a file with name `"evaluation.xlsx"`."""
        dfOrderwiseEval = pd.DataFrame(data=self.__EvaluationKPIs)

        # get the column names in the dataframe
        stabilityColName = f"kpi_{KPI_DEFINITION['stability'].get('num')}"

        # calculate overview KPIs
        overviewDict = {
            "stable": dfOrderwiseEval[stabilityColName].value_counts(normalize=True).get(1),
            "unstable": dfOrderwiseEval[stabilityColName].value_counts(normalize=True).get(0),
            "avg_eval_score_pal_ratio": dfOrderwiseEval["eval_score_pal_ratio"].mean(),
            "avg_target_height/m": dfOrderwiseEval["eval_score_height"].mean(),
            "n_stable_palletized_items": dfOrderwiseEval["eval_score_absolute_n_stable_pal_items"].sum(),
            "rating_algorithm": dfOrderwiseEval["eval_score_absolute_n_stable_pal_items"].sum() / totalamountitems,
        }
        logger.info(f"SCORE OF ALGORITHM = {round(overviewDict['rating_algorithm'], 6)}")
        overviewDF = pd.DataFrame.from_dict(overviewDict, orient="index")

        srcFile = FILE_KPI_DEFINITION
        shutil.copy(srcFile, EVALOUTPUTDIR.joinpath(srcFile.name))

        with pd.ExcelWriter(EVALOUTPUTDIR.joinpath("evaluation.xlsx"), mode="w") as writer:
            overviewDF.to_excel(writer, sheet_name="overview", index=True)
            dfOrderwiseEval.to_excel(writer, sheet_name="orderwise", index=False)
