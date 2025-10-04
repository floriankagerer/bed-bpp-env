"""
This module gathers the KPIs in a single class.
"""

import environment
import numpy as np
import statistics


class KPIs:
    """
    Collects the KPIs in a single class.

    Attributes.
    -----------
    __DataSources: dict
        Contains the targetspace and the order that is evaluated.
    __Values: dict
        'The values of the defined KPIs.
    """

    def __init__(self) -> None:
        self.__DataSources = {}
        """Contains the targetspace and the order that is evaluated."""

        self.__Values = {
            "unpalletized_items": None,
            "maximum_palletizing_height/mm": None,
            "vol_items/cm^3": None,
            "packing_stability": {"support_area": {"current": None, "min": None, "mean": None, "stdev": None}},
            "volume_utilization": None,
        }
        """The values of the defined KPIs."""

    def __str__(self) -> str:
        return str(self.__Values)

    def update(self) -> dict:
        targetSpace = self.__DataSources.get("target")
        currentOrder = self.__DataSources.get("order")

        palHeightMap = targetSpace.getHeights()

        placedItems = targetSpace.getPlacedItems()
        percentageSupportingAreas = [item.getPercentageDirectSupportSurface() for item in placedItems]

        itemVolumeOnPallet = sum([item.getVolume() / 1000.0 for item in placedItems])

        self.__Values["unpalletized_items"] = len(currentOrder["order"]["item_sequence"]) - len(placedItems)
        self.__Values["maximum_palletizing_height/mm"] = np.amax(palHeightMap)
        self.__Values["vol_items/cm^3"] = itemVolumeOnPallet
        self.__Values["packing_stability"] = {
            "support_area": {
                "current": percentageSupportingAreas[-1],
                "min": min(percentageSupportingAreas),
                "mean": statistics.fmean(percentageSupportingAreas),
                "stdev": statistics.stdev(percentageSupportingAreas) if len(percentageSupportingAreas) > 1 else 0,
            }
        }
        targetBaseArea = palHeightMap.shape[0] * palHeightMap.shape[1]
        volumeCircumscribedCuboidCM3 = (1e-3) * targetBaseArea * np.amax(palHeightMap)
        self.__Values["volume_utilization"] = self.__Values["vol_items/cm^3"] / volumeCircumscribedCuboidCM3

        return self.__Values.copy()

    def getPrettyStr(self) -> str:
        kpisString = ""
        for key, val in self.__Values.items():
            if isinstance(val, dict):
                kpisString += f"{key}\n"
                for k1, v1 in val.items():
                    if isinstance(v1, dict):
                        kpisString += f"    {k1}\n"
                        for k2, v2 in v1.items():
                            kpisString += f"        {k2}: {round(v2, 6)}\n"
                    else:
                        kpisString += f"    {k1}: {v1}\n"

            else:
                kpisString += f"{key}: {round(val, 6)}\n"

        return kpisString

    def reset(self, targetspace: "environment.Space3D", order: dict) -> None:
        self.__DataSources["target"] = targetspace
        self.__DataSources["order"] = order

    def getVolumeUtilization(self) -> float:
        return self.__Values["volume_utilization"]

    def getMeanSupportArea(self) -> float:
        return self.__Values["packing_stability"]["support_area"]["mean"]

    def getMaxHeightOnTarget(self) -> int:
        return self.__Values["maximum_palletizing_height/mm"]
