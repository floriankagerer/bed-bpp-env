/*
  DISCLAIMER:
  This software was produced by the National Institute of Standards
  and Technology (NIST), an agency of the U.S. government, and by statute is
  not subject to copyright in the United States.  Recipients of this software
  assume all responsibility associated with its operation, modification,
  maintenance, and subsequent redistribution.

  See NIST Administration Manual 4.09.07 b and Appendix I. 
*/

/*!
  \file view.cc

  \brief Graphics functions for palletViewer. Uses OpenGL.
  \code CVS Status:
  $Author: dr_steveb $
  $Revision: 1.2 $
  $Date: 2011/03/21 13:22:34 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/

/*

This includes the glInit function and the functions that are called
by callbacks in the glMainLoop.

All motions of the display are performed using the mouse.

No time delays are used because they are not needed. Unless the user is
interacting with the display using the keyboard or mouse, this just sits
there and uses no processing time.

*/

#include <stdlib.h>      // exit
#include <stdio.h>       // printf, etc.
#include "view.h"        // glInit
#include "truckViewer.h" // TruckViewer::recalculate, TruckViewer::redraw
#include "mouse.hh"          

#define IMAGE_SIZE 4000000
#define max(x,y) (((y) > (x)) ? (y) : (x))

static void buildDisplayList(void);
static void displayAsPlannedMetricsWindow(void);
static void displayPictureWindow(void);
void glInit(int argc, char* argv[], const char * winName);
static void keyboard(unsigned char key, int x, int y);
static void makeGrid(void);
static void motion(int x, int y);
static void mouse(int button, int state, int x, int y);
static void reshapeAsPlannedMetricsWindow(int width, int height);
static void reshapePictureWindow(int width, int height);
static int windowDump(void);

/********************************************************************/

static int asPlannedMetricsHeight = 585; // height of as-planned metrics window
static int asPlannedMetricsWidth = 275;  // width of as-planned metrics window
static int asPlannedMetricsWindow = 0;   // id of as-planned metrics window
static int dump = 0;                     // whether to dump image
static int pictureExtent = 600;          // width and height of picture window
static int pictureWindow = 0;            // id of picture window
static GLuint stackList = 0;    // display list for grid, pallet, and boxes

int rotate = 0;         // whether mouse button 1 rotates, used by mouse.cc

/********************************************************************/

/* buildDisplayList

Returned Value: none

Called By:
  glInit
  keyboard

This makes the display list named stackList that includes the background
grid, the pallet, the stack of boxes as planned.

*/

static void buildDisplayList(void) /* NO ARGUMENTS */
{
  // destroy any previous lists
  if (stackList)
    glDeleteLists(stackList, 1);
  // generate a display list
  stackList = glGenLists(1);
  glNewList(stackList, GL_COMPILE);
  makeGrid();
  TruckViewer::redraw();
  glEndList();
}
  
/***********************************************************************/

/* displayAsPlannedMetricsWindow

Returned Value: none

Called By: glInit (as glutDisplayFunc for asPlannedMetricsWindow)

This draws the asPlannedMetricsWindow.

*/

static void displayAsPlannedMetricsWindow(void) /* NO ARGUMENTS */
{
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  TruckViewer::printAsPlannedText(asPlannedMetricsHeight);
  glutSwapBuffers();
}

/***********************************************************************/

/* displayPictureWindow

Returned Value: none

Called By: glInit (as glutDisplayFunc for pictureWindow)

This draws the display. If dump is non-zero, it also dumps a ppm image
and sets dump to zero.

*/

static void displayPictureWindow(void) /* NO ARGUMENTS */
{
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glPushMatrix();
  msMove(0);
  glColor3f(1.0, 1.0, 1.0);
  glCallList(stackList);
  glPopMatrix();
  if (dump)
    {
      windowDump();
      dump = 0;
    }
  glutSwapBuffers();
}

/***********************************************************************/

/* glInit

Returned Value: none

Called By: main (in main.cc)

This:
1. initializes openGL

2. initializes the as-planned metrics window and registers the callback
   functions for it

3. if there is an as-built file, initializes the as-built metrics window
   and registers the callback functions for it

4. initializes the graphics window and registers the callback functions
   for it

5. initializes mouse parameters

6. builds the original display list.

*/

void glInit(           /* ARGUMENTS                              */
 int argc,             /* number of arguments to the executable  */
 char* argv[],         /* array of executable name and arguments */
 const char * winName) /* name for graphics window               */
{

	glutInit(&argc, argv);
  glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);

  glutInitWindowPosition(2, 0);
  glutInitWindowSize(asPlannedMetricsWidth, asPlannedMetricsHeight);
  asPlannedMetricsWindow = glutCreateWindow("As Planned Metrics");
  glutReshapeFunc(reshapeAsPlannedMetricsWindow);
  glutDisplayFunc(displayAsPlannedMetricsWindow);
  glutInitWindowPosition(asPlannedMetricsWidth + 8, 0);
  glutInitWindowSize(pictureExtent, pictureExtent);
  pictureWindow = glutCreateWindow(winName);
  glShadeModel(GL_SMOOTH);
  glHint(GL_LINE_SMOOTH_HINT, GL_NICEST);
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glEnable(GL_DEPTH_TEST);
  glEnable(GL_LINE_SMOOTH);
  glEnable(GL_COLOR_MATERIAL);
  glDisable(GL_LIGHTING);
  glutDisplayFunc(displayPictureWindow);
  glutReshapeFunc(reshapePictureWindow);
  glutKeyboardFunc(keyboard);
  glutMouseFunc(mouse);
  glutMotionFunc(motion);

  msInit();
  buildDisplayList();
  glClearColor(0.0, 0.0, 0.0, 0.0);
  glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
}

/********************************************************************/

/* keyboard

Returned Value: none

Called By: glInit (as glutKeyboardFunc)

If g is pressed and there are more boxes to display, another box is shown.
If f is pressed and any boxes are displayed, one is removed.
If h or H is pressed, the view is returned to its original position.
If r is pressed, using mouse button 1 to rotate instead of translate is toggled
If t or T is pressed the current image is dumped to a ppm file.
if z, Z, q, or Q is pressed, palletViewer exits.

*/

static void keyboard(
 unsigned char key,
 int x,
 int y)
{
  switch (key)
    {
    case 'Q':
    case 'q':
    case 'Z':
    case 'z':
      exit(0);
      break;
    case 'h':
    case 'H':
      msInit();
      break;
    case 't':
    case 'T':
      dump = 1;
      break;
    case 'f':
      TruckViewer::recalculate(-1);
      buildDisplayList();
      glutPostRedisplay();
      glutSetWindow(asPlannedMetricsWindow);
      glutPostRedisplay();
      glutSetWindow(pictureWindow);
      break;
    case 'g':
      TruckViewer::recalculate(1);
      buildDisplayList();
      glutPostRedisplay();
      glutSetWindow(asPlannedMetricsWindow);
      glutPostRedisplay();
      glutSetWindow(pictureWindow);
      break;
    case 'r' :
      rotate = ((rotate == 0) ? 1 : 0);
      break;
    }
  glutPostRedisplay();
}

/********************************************************************/

/* makeGrid

Returned Value: none

Called By: buildDisplayList

This makes a square grid of light grey lines on the XY plane
The grid is 1 by 1 in view space. There are 21 lines in X and
Y directions, separated by 0.05.

*/

static void makeGrid(void) /* NO ARGUMENTS */
{
  static GLfloat t;
  static GLfloat k = (GLfloat)0.5;
  static GLfloat c = (GLfloat)0.05;

  glColor3f((GLfloat)0.4, (GLfloat)0.4, (GLfloat)0.4);
  glBegin(GL_LINES);
  for (t = -k; t <= (k + 0.01); t += c)
    {
      glVertex3f(t, k, 0.0);
      glVertex3f(t, -k, 0.0);
      glVertex3f(k, t, 0.0);
      glVertex3f(-k, t, 0.0);
    }
  glEnd();
}

/********************************************************************/

/* motion

Returned Value: none

Called By: glInit (as glutMotionFunc)

This changes the display when a mouse button is held down and the
mouse is moved over the display.

If the left button is held down:
a. If the "rotate" variable is non-zero, the left button does what
the middle button does (see next paragraph)
b. If the "rotate" variable is zero and the mouse is moved, the grid and
box stacks move with the cursor.

If the middle button is held down and the mouse is moved, the grid and
box stacks rotate around an axis perpendicular to the direction of cursor
motion.

If the right button is held down and the mouse is moved, the grid and
box stacks zoom away when the cursor moves up. They zoom in when the cursor
moves down. Sideways motion of the cursor does nothing. This is zooming,
not moving the point of view, so the eye never goes through boxes.

*/

static void motion( /* ARGUMENTS                                  */
 int x,             /* X location of cursor in screen coordinates */
 int y)             /* Y location of cursor in screen coordinates */
{
  msMotion(x, y, 0);
  glutPostRedisplay();
}

/***********************************************************************/

/* mouse

Returned Value: none

Called By: glInit (as glutMouseFunc)

See documentation of the motion function.

*/

static void mouse(  /* ARGUMENTS                                  */
 int button,        /* the mouse button that went up or down      */
 int state,         /* up or down                                 */
 int x,             /* X location of cursor in screen coordinates */
 int y)             /* Y location of cursor in screen coordinates */
{
  msMouse(button, state, x, y);
  glutPostRedisplay();
}

/***********************************************************************/

/* reshapeAsPlannedMetricsWindow

Returned Value: none

Called By: glInit (as glutReshapeFunc for the asPlannedMetricsWindow)

This reshapes the asPlannedMetricsWindow.

*/

static void reshapeAsPlannedMetricsWindow( /* ARGUMENTS                */
 int width,                                /* window width, in pixels  */
 int height)                               /* window height, in pixels */
{
  glViewport(0, 0, (GLsizei)width, (GLsizei)height);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  gluOrtho2D(0.0, (GLdouble)width, 0.0, (GLdouble)height);
  asPlannedMetricsHeight = height;
  asPlannedMetricsWidth = width;
}

/***********************************************************************/

/* reshapePictureWindow

Returned Value: none

Called By: glInit (as glutReshapeFunc for pictureWindow)

This reshapes the picture window. The aspect ratio of the window may
change, but the aspect ratio of the picture in the window will stay
the same.

*/

static void reshapePictureWindow( /* ARGUMENTS                */
 int width,                       /* window width, in pixels  */
 int height)                      /* window height, in pixels */
{
  pictureExtent = ((width < height) ? width : height);
  msReshape(pictureExtent, 0);
  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity();
  glTranslatef(0.0, 0.0, -2.0);
}

/***********************************************************************/

/* windowDump

Returned Value: int
If this file is written successfully, this returns 0.
Otherwise, it prints an error message to the terminal and returns 1.

Called By: displayPictureWindow

This writes a ppm file containing an image that combines the
asPlannedMetricsWindow and the pictureWindow.
The asPlannedMetricsWindow is on the left side of the image. The
pictureWindow is on the right.

This gets copies the two windows, combines them, and writes out the
ppm file. Each window is first saved in the tempImage array and then
transferred to the allImage array. 

The indexing for making allImage (the contents of the ppm file) is
complex since (1) glReadPixels writes pixels left to right and
bottom to top, while ppm files are read left to right and top to
bottom, (2) three windows are being combined into one image, and (3)
there are 3 chars for each pixel. The critical variables are:
 i is the index for rows of allImage. For copying a window from tempImage
   into allImage, its value is set initially to the row of allImage into
   which the lowest row of the window is to be copied. Then i is
   decreased by 1 each time around the row loop, to move upwards in
   allImage.
 k is the index for lines of whatever window is being copied into
   allImage. It starts at 0 and is increased by 1 each time around
   the row loop to move upwards in tempImage.
 j is the index for chars on a row.
 start is the char index of place on a line of allImage at which to
   start copying in a line from the tempImage.
 stop is the length in chars of a line of the tempImage.

The default value for GL_PACK_ALIGNMENT is 4 rather than 1. If the
value is not set to 1 and the window width is not divisible by 4, the
dumped image is skewed. The "glPixelStorei(GL_PACK_ALIGNMENT, 1);"
which sets the value to 1 needs to be repeated for each window.

*/
#define fname_size 32
static int windowDump(void) /* NO ARGUMENTS */
{
  FILE * outFile;         // file pointer for dumped image
  static int counter = 0; // counter for dumped images
  char fname[fname_size]; // name of dumped image
  static char allImage[IMAGE_SIZE];  // storage for dumped image
  static char tempImage[IMAGE_SIZE]; // storage for image of one window
  int allWidth;     // entire width of dumped image, in chars
  int allHeight;    // entire height of dumped image, in lines of pixels
  int i;            // index for chars then lines of allImage
  int j;            // index for columns of tempImage and allImage
  int k;            // index for lines of tempImage
  int start;        // starting point on line of allImage
  int stop;         // upper bound of index value
  int imageSize;    // number of chars in image (3 times number of pixels)
  
  allHeight = max(pictureExtent, asPlannedMetricsHeight);
  allWidth = (3 *(pictureExtent + asPlannedMetricsWidth));
  imageSize = (allWidth * allHeight);
  if (imageSize > IMAGE_SIZE)
    {
      fprintf(stderr, "WindowDump - Image too large for window dump\n");
      return 1;
    }

  // handle the as-planned metrics window
  glutSetWindow(asPlannedMetricsWindow);
  glPixelStorei(GL_PACK_ALIGNMENT, 1);
  glReadBuffer(GL_BACK);
  glReadPixels(0, 0, asPlannedMetricsWidth, asPlannedMetricsHeight,
	       GL_RGB, GL_UNSIGNED_BYTE, tempImage);
  stop = (3 * asPlannedMetricsWidth);
  for (i = allHeight; i > asPlannedMetricsHeight; i--)
    { // put black rectangle under the as-planned metrics window if needed
      for (j = 0;  j < stop; j++)
	allImage[(i * allWidth) + j] = 0;
    }
  for (k=0; i >= 0; i--, k++)
    { // copy in the as-planned metrics window
      for (j = 0;  j < stop; j++)
	allImage[(i * allWidth) + j] = tempImage[(k * stop) + j];
    }

  // handle the picture window
  glutSetWindow(pictureWindow);
  glPixelStorei(GL_PACK_ALIGNMENT, 1);
  glReadBuffer(GL_BACK);
  glReadPixels(0, 0, pictureExtent, pictureExtent,
  	       GL_RGB, GL_UNSIGNED_BYTE, tempImage);
  start = (3 * asPlannedMetricsWidth);
  stop = (3 * pictureExtent);
  for (i = allHeight; i > pictureExtent; i--)
    { // put black rectangle under the picture window if needed
      for (j = 0; j < stop; j++)
	allImage[(i * allWidth) + start + j] = 0;
    }
  for (k=0; i >= 0; i--, k++)
    { // copy in the picture window
      for (j = 0; j < stop; j++)
	allImage[(i * allWidth) + start + j] = tempImage[(k * stop) + j];
    }

  glutSetWindow(pictureWindow);
  snprintf(fname, fname_size, "anaglyph_%04d.ppm", counter++);
  if ((outFile = fopen(fname, "w")) == NULL)
    {
      fprintf(stderr, "WindowDump - Failed to open file %s\n", fname);
      return 1;
    }
  fprintf(outFile, "P6\n%d %d\n255\n", (allWidth / 3), allHeight);
  if (fwrite(allImage, imageSize * sizeof(char), 1, outFile) != 1)
    {
      fprintf(stderr, "WindowDump - Failed to write in file %s\n", fname);
      fclose(outFile);
      return 1;
    }
  fclose(outFile);
  return 0;
}

/********************************************************************/

