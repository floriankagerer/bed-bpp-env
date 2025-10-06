"""
This module contains the class `Visualization`, which is the base class of many other visualization classes. It contains essential methods that the different inherited visualization classes need.
"""

import json
import pathlib

import cv2
import vtk

import bed_bpp_env.utils as utils
from bed_bpp_env.visualization import OUTPUTDIRECTORY


class Visualization:
    """
    The base class for different visualization classes.

    Parameters.
    -----------
    visID: str (default = "0")
        An ID that represents the visualization object.
    windowname: str (default = "Visualization")
        The title of the visualization window.

    Attributes.
    -----------
    __Camera: vtk.vtkCamera
        The camera of the renderer.
    __CAMERAVIEW: int
        The defined camera view.
    Colors: vtk.vtkNamedColors
        The colors that can be used in the visualization.
    __DISPLAYTIME: int
        The time in [ms] to display the visualization.
    __DisplayVisualiatzion: bool
        Defines whether the visualization window is displayed
    __Filename: str
        The filename of the visualization window.
    __Images4Video: list
        Contains all images of the palletizing process.
    __Interactive: bool
        Indicates whether the interactive mode should be started. Note: currently not working.
    __MakeVideo: bool
        Indicates whether a video of the visualization should be made.
    __Mapper: vtk.vtkDataSetMapper
        The data mapper of the visualization.
    __OutputFolder: pathlib.Path
        The directory in which the images are stored.
    __Renderer: vtk.vtkRenderer
        The renderer of the visualization.
    __RenderWindow: vtk.vtkRenderWindow
        The render window of the visualization.
    __VisID: str
        An ID that represents the visualization.
    __WINDOWNAME: str
        The name of the visualization window.
    __WINDOWPOSITION: tuple
        The position of the render window.
    __WINDOWSIZE: tuple
        The size of the render window in pixels.

    Note.
    -----
    The interactive mode is not working.
    """

    def __init__(self, visID: str = "0", windowname: str = "Visualization") -> None:
        self.__VisID = visID
        """An ID that represents the visualization."""
        self.__Filename = "vis" + str(self.__VisID).zfill(2) + ".png"
        """The filename of the visualization window."""

        PARSEDARGUMENTS = utils.arguments_parser.parse()
        self.__DisplayVisualiatzion = PARSEDARGUMENTS.get("visualize", True)
        """This bool defines whether the visualization window is displayed."""

        self.__DISPLAYTIME = 50  # 150 or 300
        """The time in [ms] to display the visualization."""

        self.__OutputFolder = OUTPUTDIRECTORY
        """The directory in which the images are stored."""

        self.__Interactive = False
        """Indicates whether the interactive mode should be started. Note: currently not working."""

        self.Colors = vtk.vtkNamedColors()
        """The colors for the visualization."""
        self.Colors.SetColor("BkgColor", [255, 255, 255, 255])
        self.Colors.SetColor("NOT_IN_DB", "#ffffff")
        self.__loadOwnColors()

        self.__Camera = vtk.vtkCamera()
        """The camera of the renderer."""
        self.__CAMERAVIEW = 0
        """The defined camera view."""
        self.__Mapper = vtk.vtkDataSetMapper()
        """The data mapper of the visualization."""
        self.__Renderer = vtk.vtkRenderer()
        """The renderer of the visualization."""

        self.__WINDOWNAME = windowname
        """The name of the visualization window."""
        self.__WINDOWPOSITION = (0, 0)
        """The position of the render window."""
        self.__WINDOWSIZE = (900, 900)
        """The size of the render window in pixels."""
        self.__RenderWindow = vtk.vtkRenderWindow()
        """The render window of the visualization."""

        self.__MakeVideo = True
        """Indicates whether a video of the visualization should be made."""
        self.__Images4Video = []
        """Contains all images of the palletizing process."""

        self.__initMapper()
        self.__initRenderer()
        self.__initRenderWindow()

    def __loadOwnColors(self) -> None:
        """Loads own colors from `visualization/colors/colors.json`."""
        filePath = pathlib.Path(__file__).resolve()
        colorFile = filePath.parent.joinpath("colors/colors.json")
        with open(colorFile) as file:
            OWNCOLORS = json.load(file, parse_int=False)

        for colorName, hexValue in OWNCOLORS.items():
            self.Colors.SetColor(colorName, hexValue)

    def setCameraView(self, view: int = 0, rotate: bool = True) -> None:
        """
        Sets the camera view of the renderer.

        Parameters.
        -----------
        view: int (default = 0)
            Defines the view of the camera. `0: overview from side; 1: roboter view`
        rotate: bool (default = True)
            Indicates whether the view is rotated.
        """
        # settings are [camera position, focal point, roll (=rotation)]
        cameraSettings = [[(1500, -1000, 1800), (600, 400, 900), -55], [(600, -1000, 1800), (600, 400, 900), 0]]

        self.__Camera.SetPosition(cameraSettings[view][0])
        self.__Camera.SetFocalPoint(cameraSettings[view][1])
        self.__Renderer.SetActiveCamera(self.__Camera)

        if rotate:
            self.__Renderer.GetActiveCamera().Roll(cameraSettings[view][2])

        # automatically set up the camera based on the visible actors
        self.__Renderer.ResetCamera()
        # zoom (zoom in: value > 1; zoom out: 0 < value < 1)
        self.__Renderer.GetActiveCamera().Zoom(0.8)

    def updateVisualization(self) -> None:
        """Updates the visualization and makes a screenshot of the current scene."""
        # check whether the mode is set to interactive
        if not self.__Interactive:
            self.__RenderWindow.SetOffScreenRendering(1)
        else:
            # set an interactor for interactive mode
            renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            renderWindowInteractor.SetRenderWindow(self.__RenderWindow)

        self.__RenderWindow.Render()
        self.makeScreenshot()

        if self.__Interactive:
            renderWindowInteractor.Start()

    def makeScreenshot(self, force=False, fname=None) -> None:
        """
        Method that takes a screenshot of the current view and writes it to a file.

        Parameters.
        -----------
        force: bool (default = False)
            Forces to make a screenshot. If False, then a screenshot is only taken when visualization is enabled.
        fname: str (default = None)
            Defines the filename of the screenshot. If `fname` is `None`, then the filename that is stored in the filename attribute is taken, otherwise, the file is stored in the specified output folder with the given filename.
        """
        if self.__DisplayVisualiatzion or force:
            if fname is None:
                filename = self.__Filename
            else:
                filename = pathlib.Path.joinpath(self.__OutputFolder, fname)

            w2if = vtk.vtkWindowToImageFilter()
            w2if.SetInput(self.__RenderWindow)
            w2if.Update()

            # write the image
            writer = vtk.vtkPNGWriter()
            writer.SetFileName(filename.as_posix())
            writer.SetInputConnection(w2if.GetOutputPort())
            writer.Write()

    def displayVisualization(self) -> None:
        """Displays the pallet and load carriers for the specified display time."""
        winX, winY = self.__WINDOWPOSITION
        if self.__DisplayVisualiatzion:
            img = cv2.imread(self.__Filename.as_posix())
            self.__addImage4Video(img)

            cv2.namedWindow(self.__WINDOWNAME)
            cv2.moveWindow(self.__WINDOWNAME, winX, winY)
            cv2.imshow(self.__WINDOWNAME, img)

            cv2.waitKey(self.__DISPLAYTIME)

    def __addImage4Video(self, image: cv2.Mat) -> None:
        """
        Adds the given image to list of images for the video.

        Parameters.
        -----------
        image: cv2.Mat
            The image which is appended to the list of images for the video.
        """
        if self.__MakeVideo is True:
            self.__Images4Video.append(image)

    def getImages4Video(self) -> list:
        """
        Returns a list of images of the palletizing process.

        Returns.
        --------
        images: list
            A list of images, of the type `cv2.Mat`, which are combined in a video.
        """
        return self.__Images4Video

    def __initRenderWindow(self) -> None:
        """Initializes the render window. Sets the window name, the size and the position of the window."""
        self.__RenderWindow.SetWindowName("Visualization")

        self.__RenderWindow.SetSize(self.__WINDOWSIZE)
        self.__RenderWindow.SetPosition(900, 0)

        self.__RenderWindow.AddRenderer(self.__Renderer)

    def __initMapper(self) -> None:
        """Initializes the mapper of the visualization."""
        # get unit hexahedron (1,1,1) = Cube
        [points, hexahedron] = self.__getHexahedron()

        hexs = vtk.vtkCellArray()
        hexs.InsertNextCell(hexahedron)

        uGrid = vtk.vtkUnstructuredGrid()
        uGrid.SetPoints(points)
        uGrid.InsertNextCell(hexahedron.GetCellType(), hexahedron.GetPointIds())

        self.__Mapper.SetInputData(uGrid)

    def __initRenderer(self) -> None:
        """Initializes the renderer of the visualization, i.e., the background color and the camera view is set."""
        self.__Renderer.SetBackground(self.Colors.GetColor3d("BkgColor"))
        self.setCameraView()

    def updateCameraView(self, rotate: bool) -> None:
        """Has to be called in a child class when new objects are added to the scene."""
        self.setCameraView(self.__CAMERAVIEW, rotate=rotate)

    def __getHexahedron(self):
        """
        Creates a heaxahedron object which is the basis for a load carrier.

        Returns.
        --------
        points, hexahedron:
            A list of points and the hexahedron object.
        """
        # For the hexahedron. Setup the coordinates of eight points.
        # The two faces must be in counter clockwise order as viewed from the
        # outside.
        pointCoordinates = []
        pointCoordinates.append([0.0, 0.0, 0.0])  # Face 1
        pointCoordinates.append([1.0, 0.0, 0.0])
        pointCoordinates.append([1.0, 1.0, 0.0])
        pointCoordinates.append([0.0, 1.0, 0.0])
        pointCoordinates.append([0.0, 0.0, 1.0])  # Face 2
        pointCoordinates.append([1.0, 0.0, 1.0])
        pointCoordinates.append([1.0, 1.0, 1.0])
        pointCoordinates.append([0.0, 1.0, 1.0])

        # create hexahedron from points
        points = vtk.vtkPoints()
        hexahedron = vtk.vtkHexahedron()
        for i, point in enumerate(pointCoordinates):
            points.InsertNextPoint(point)
            hexahedron.GetPointIds().SetId(i, i)

        return [points, hexahedron]

    # region For Childclasses

    def addActorToRenderer(self, actor) -> None:
        """Adds the given VTK actor to the renderer."""
        self.__Renderer.AddActor(actor)

    def removeActorFromRenderer(self, actor) -> None:
        """Removes the given VTK actor from the renderer."""
        self.__Renderer.RemoveActor(actor)

    def getMapper(self):
        """Returns the VTK mapper of the visualization."""
        return self.__Mapper

    def getRenderer(self):
        """Returns the VTK renderer of the visualization."""
        return self.__Renderer

    def getWindowname(self) -> str:
        """Returns the window name."""
        return self.__WINDOWNAME

    def getWindowsize(self) -> tuple:
        """Returns the window size."""
        return self.__WINDOWSIZE

    def setFilenameForImage(self, fname: str) -> None:
        """Sets the filename for the visualization image."""
        self.__Filename = pathlib.Path.joinpath(self.__OutputFolder, fname)

    def getFilenameOfImage(self):
        """Returns the filename of the visualization image."""
        return self.__Filename

    def setWindowPosition(self, coordinates: tuple) -> None:
        """Sets the position of the render window. The coordinates are given as `(pos_x, pos_y)`."""
        self.__WINDOWPOSITION = coordinates

    def getLocationOfImage(self) -> pathlib.Path:
        """Returns the location of the visualization image."""
        return pathlib.Path.joinpath(self.__OutputFolder, self.__Filename)

    def saveStoredImages(self) -> None:
        """Saves all images that are stored in this object as `item{number}.png`."""
        for i, image in enumerate(self.__Images4Video):
            filename = pathlib.Path.joinpath(self.__OutputFolder, f"item{i + 1}.png")
            # create a writer
            cv2.imwrite(filename.as_posix(), image)

    def setDisplayTime(self, value: int) -> None:
        """The display time in milliseconds."""
        if value > 0:
            self.__DISPLAYTIME = int(value)

    # endregion For Child classes
