"""
This module contains the class `PalletizingEnvironmentVisualization`, which is inherited from `visualization.Visualization`, that can be used for creating a visualization and images of the different states of palletization.
"""

import logging
import os

import cv2
import vtk

from bed_bpp_env.environment.lc import LC
from bed_bpp_env.visualization import COLOR_DATABASE
from bed_bpp_env.visualization.visualization import Visualization

logger = logging.getLogger(__name__)

WALL_HEIGHT = 2020
"""The height of the stacking wall that is added to the scene and after setting the zoom of the camera removed immediately."""


class PalletizingEnvironmentVisualization(Visualization):
    """
    This class visualizes the palletization of items. Items can be added to the visualization with the method `addLoadCarrier(item)`. The item must be an instance of `LC`.

    In order to show the visualization, call `PalletizingEnvironmentVisualization.displayVisualization()`.

    Parameters.
    -----------
    visID: str (default="0")
        The ID of the object. Typically, the order id is given.
    windowname: str
        The title of the displayed visualization window.
    target: str
        The target of the palletization, i.e., either `"rollcontainer"` or `"euro-pallet"`.

    Attributes.
    -----------
    __Actors: dict
        Contains all actors, i.e., all elements that are visualized in the scene.
    __DBItemColors: dict
        Contains the colors for each item for the requested palletizing environment visualization.
    __ObjectCounter: int
        Holds the amount of open instances of this class.
    __VisID: str
        ID that represents this object.

    Note.
    -----
    The interactive mode is not working.
    """

    ObjectCounter = 0
    """This integer counts how many instances of this class are opened."""

    def __init__(
        self, visID="0", windowname="Visualization | BED-BPP Environment", target: str = "euro-pallet", algo=""
    ) -> None:
        PalletizingEnvironmentVisualization.ObjectCounter += 1
        self.__ObjectCounter = PalletizingEnvironmentVisualization.ObjectCounter
        """Holds the amount of opened visualization windows."""
        self.__VisID = visID
        """An ID that represents this object."""

        # set the properties for the super class
        windowposition = (950 * self.__ObjectCounter, 0)
        super(PalletizingEnvironmentVisualization, self).__init__(self.__VisID, windowname)
        super().setWindowPosition(windowposition)
        super().setFilenameForImage(f"palenvvis.png")

        self.__Actors = {"text": {}, "lcs": []}
        """Contains all actors, i.e., all elements that are visualized in the scene. Possible keys are `text` and `lcs`."""

        self.__DBItemColors = COLOR_DATABASE.get(self.__VisID)
        """The available database for the item colors of a given order."""

        self.__initScene(target)
        if not (algo == ""):
            self.__addAlgorithmToVisualization(algo)

    def __del__(self) -> None:
        """Decreases the object counter and destroys the window that corresponds to this object."""
        PalletizingEnvironmentVisualization.ObjectCounter -= 1
        try:
            self.closeVisualizationWindow()
            fnameImage = super().getFilenameOfImage()
            os.remove(fnameImage)
        except:
            pass

    def closeVisualizationWindow(self) -> None:
        """Closes the visualization window."""
        cv2.destroyWindow(super().getWindowname())

    def addLoadCarrier(self, item: LC) -> None:
        """Adds the given item to the renderer of the visualization."""
        # create the item actor for the visualization
        actor = vtk.vtkActor()
        lccolor = self.__DBItemColors.get(item.sku, "NOT_IN_DB")
        actor.GetProperty().SetColor(self.Colors.GetColor3d(lccolor))
        actor.SetMapper(super().getMapper())
        size = list(item.dimensions)
        actor.SetScale(size)
        targetPosition = item.position.copy()
        actor.SetPosition([targetPosition["x"], targetPosition["y"], targetPosition["z"]])
        actor.GetProperty().EdgeVisibilityOn()

        # add item to renderer
        super().addActorToRenderer(actor)
        self.__Actors["lcs"].append(actor)

    def removeAllLCs(self) -> None:
        """Removes all load carriers that were added to the visualization."""
        for lcActor in self.__Actors["lcs"]:
            super().removeActorFromRenderer(lcActor)

        self.makeScreenshot(fname=None)

    def __addEPAL(self) -> None:
        """Adds a euro-pallet to the renderer."""
        # name of the color of the pallet
        palletColor = "burlywood"

        palletComponents = []
        # sizes of top components wide, top narrow, fillet (=steg), cuboid, bottom
        palCompSizes = [[1200, 150, 20], [1200, 120, 20], [150, 800, 15], [135, 115, 89], [1200, 115, 20]]
        # define the positions and measurements of the components
        offsetY = 400
        posTopCompW = [[0, offsetY + -400, -20], [0, offsetY + -75, -20], [0, offsetY + 250, -20]]
        posTopCompN = [[0, offsetY + -222.5, -20], [0, offsetY + 102.5, -20]]
        posFillet = [[0, offsetY + -400, -35], [525, offsetY + -400, -35], [1050, offsetY + -400, -35]]
        posCuboid = [
            [0, offsetY + -400, -109],
            [532.5, offsetY + -400, -109],
            [1065, offsetY + -400, -109],
            [0, offsetY + -57.5, -109],
            [532.5, offsetY + -57.5, -109],
            [1065, offsetY + -57.5, -109],
            [0, offsetY + 285, -109],
            [532.5, offsetY + 285, -109],
            [1065, offsetY + 285, -109],
        ]
        posBottom = [[0, offsetY + -400, -124], [0, offsetY + -57.5, -124], [0, offsetY + 285, -124]]
        # list of all positions of the components
        palCompPositions = [posTopCompW, posTopCompN, posFillet, posCuboid, posBottom]
        # counter variable
        count = 0
        # iterate over all components of pallet
        mapper = super().getMapper()
        for i in range(len(palCompPositions)):
            for j in range(len(palCompPositions[i])):
                # create an actor object
                palletComponents.append(vtk.vtkActor())
                palletComponents[count].GetProperty().SetColor(self.Colors.GetColor3d(palletColor))
                palletComponents[count].SetMapper(mapper)
                palletComponents[count].SetScale(palCompSizes[i])
                palletComponents[count].SetPosition(palCompPositions[i][j])
                palletComponents[count].GetProperty().EdgeVisibilityOn()
                count += 1
        # add components to renderer
        for i in range(len(palletComponents)):
            # add actor to the renderer
            super().addActorToRenderer(palletComponents[i])

    def __addRollcontainer(self) -> None:
        """Adds a rollcontainer to the renderer."""
        rcColor = "silver"
        rcComponents = []

        # sizes of base area struts x,      base area struts y,  left wall,      right wall
        rcComponentsSizes = [[800, 25, 20], [25, 700, 20], [20, 700, WALL_HEIGHT], [20, 700, WALL_HEIGHT]]

        # define the positions and measurements of the components
        posBaseStrutX = [[0, 112.5 * i, -20] for i in range(7)]
        posBaseStrutY = [[(25 + 600 / 7) * i, 0, -20] for i in range(8)]
        posLeftWall = [[-20, 0, -20]]
        posRightWall = [[800, 0, -20]]

        # list of all positions of the components
        rcCompPositions = [posBaseStrutX, posBaseStrutY, posLeftWall, posRightWall]
        rcCompOpacities = [1, 1, 1, 0.3]
        # counter variable
        count = 0
        mapper = super().getMapper()
        for i in range(len(rcCompPositions)):
            for j in range(len(rcCompPositions[i])):
                # create an actor object
                rcComponents.append(vtk.vtkActor())
                rcComponents[count].GetProperty().SetColor(self.Colors.GetColor3d(rcColor))
                rcComponents[count].SetMapper(mapper)
                # set the size of the rcComponents
                rcComponents[count].SetScale(rcComponentsSizes[i])
                rcComponents[count].SetPosition(rcCompPositions[i][j])
                rcComponents[count].GetProperty().EdgeVisibilityOn()
                rcComponents[count].GetProperty().SetOpacity(rcCompOpacities[i])
                count += 1

        # add components to renderer
        for i in range(len(rcComponents)):
            super().addActorToRenderer(rcComponents[i])

    def __addCuboid(self, dimension: tuple) -> None:
        """Adds a cuboid scene to the renderer."""
        targetColor = "azure"

        targetComponents = []
        # sizes of base area , vertical strip,  left wall,      right wall
        BOTTOM_HEIGHT = 20
        targetComponentsSizes = [
            [10 + dimension[0], 10 + dimension[1], BOTTOM_HEIGHT],
            [5, 5, dimension[2] + BOTTOM_HEIGHT],
            [dimension[0] + 10, 5, 5],
            [5, dimension[1] + 10, 5],
        ]

        # define the positions and measurements of the components
        posBaseArea = [[-5, -5, -20]]
        posVerticalStrip = [
            [-5, -5, -20],
            [dimension[0] + 5, -5, -20],
            [-5, dimension[1] + 5, -20],
            [dimension[0] + 5, dimension[1] + 5, -20],
        ]
        posXHorizontalStrip = [[-5, -5, dimension[2]], [-5, dimension[1], dimension[2]]]
        posYHorizontalStrip = [[-5, -5, dimension[2]], [dimension[0], -5, dimension[2]]]

        # list of all positions of the components
        rcCompPositions = [posBaseArea, posVerticalStrip, posXHorizontalStrip, posYHorizontalStrip]
        rcCompOpacities = [1, 0.3, 0.3, 0.3]
        # counter variable
        count = 0
        mapper = super().getMapper()
        for i in range(len(rcCompPositions)):
            for j in range(len(rcCompPositions[i])):
                # create an actor object
                targetComponents.append(vtk.vtkActor())
                targetComponents[count].GetProperty().SetColor(self.Colors.GetColor3d(targetColor))
                targetComponents[count].SetMapper(mapper)
                # set the size of the rcComponents
                targetComponents[count].SetScale(targetComponentsSizes[i])
                targetComponents[count].SetPosition(rcCompPositions[i][j])
                targetComponents[count].GetProperty().EdgeVisibilityOn()
                targetComponents[count].GetProperty().SetOpacity(rcCompOpacities[i])
                count += 1

        # add components to renderer
        for i in range(len(targetComponents)):
            super().addActorToRenderer(targetComponents[i])

    def addText(self, orderkey: str) -> None:
        """Adds the order key to the visualization window."""
        fontsize = 35

        # create a text actor
        self.__Actors["text"]["palID"] = vtk.vtkTextActor()
        txt = self.__Actors["text"]["palID"]
        txt.SetInput(f"Order {orderkey}")
        txtprop = txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.SetFontSize(fontsize)
        txtprop.SetColor(0, 0, 0)
        txt.SetDisplayPosition(0, fontsize)

        # assign actor to the renderer
        super().addActorToRenderer(txt)

    def __addAlgorithmToVisualization(self, algo: str) -> None:
        """Adds the name of the algorithm to the visualization window."""
        fontsize = 25

        # create a text actor
        self.__Actors["text"]["algo"] = vtk.vtkTextActor()
        txt = self.__Actors["text"]["algo"]
        txt.SetInput(algo)
        txtprop = txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.SetFontSize(fontsize)
        txtprop.SetColor(0, 0, 0)
        windowsize = self.getWindowsize()
        txt.SetDisplayPosition(2 * fontsize, windowsize[1] - 2 * fontsize)

        # assign actor to the renderer
        super().addActorToRenderer(txt)

    def __initScene(self, target: str):
        """Initializes the scene of the visualization."""
        if target == "rollcontainer":
            self.__addRollcontainer()
        elif target == "euro-pallet":
            self.__addEPAL()
        else:
            # check whether cuboid scene is possible
            try:
                sizes = target.split(",")
                dimension = tuple([int(size) for size in sizes])
                self.__addCuboid(dimension)
            except:
                raise ValueError(f"wrong target given: {target}")

        self.__addStackingWall()

        self.addText(self.__VisID)

        self.updateCameraView(rotate=False)
        self.__rmActor("stacking_wall")
        self.updateVisualization()

    def __addStackingWall(self) -> None:
        """Adds a stacking wall to the scene."""
        nameForActor = "stacking_wall"
        if not (nameForActor in self.__Actors.keys()):
            self.__Actors[nameForActor] = []

        stackingWallColor = "burlywood"

        posWalls = [[0, 0, 0], [0, 800, 0]]
        sizeWalls = [[10, 800, WALL_HEIGHT], [1200, 10, WALL_HEIGHT]]

        mapper = super().getMapper()
        for i in range(len(posWalls)):
            self.__Actors[nameForActor].append(vtk.vtkActor())
            self.__Actors[nameForActor][i].GetProperty().SetColor(self.Colors.GetColor3d(stackingWallColor))  # (RGB)
            self.__Actors[nameForActor][i].SetMapper(mapper)
            self.__Actors[nameForActor][i].SetScale(sizeWalls[i])
            self.__Actors[nameForActor][i].SetPosition(posWalls[i])

        for wallActor in self.__Actors[nameForActor]:
            super().addActorToRenderer(wallActor)

    def __rmActor(self, which: str) -> None:
        """Removes all actors that belong to the parameter `which`."""
        for actor in self.__Actors[which]:
            super().removeActorFromRenderer(actor)
