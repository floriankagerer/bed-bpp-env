
/***********************************************************************/

/* includes */
#include <math.h>
#include <GL/glut.h>
#include "mouse.hh"

/***********************************************************************/

enum msTrackingValue {MS_OFF, MS_ROTATE, MS_TRANSLATE, MS_ZOOM};

/* globals */
static GLfloat         msAngle = 0.0;
static GLfloat         msAxis[3];
static GLuint          msHeight;
static GLfloat         msLastPosition[3];
static GLfloat         msLastX = 0.0;
static GLfloat         msLastY = 0.0;
static GLfloat         msTotalX = 0.0;
static GLfloat         msTotalY = 0.0;
static msTrackingValue msTrackingFlag = MS_OFF;
static GLfloat         msRotMatrix[4][4];
static GLuint          msWidth;
static GLfloat         msZoomSize = 0.25;

extern int rotate;

/***********************************************************************/

/* functions in mouse.hh
void msInit();
void msMotion(int x, int y);
void msMouse(int button, int state, int x, int y);
void msMove(int isOrtho);
void msReshape(int extent, int isOrtho);
*/
/* local functions */
static void msPointToVector(int x, int y, int width, int height, float v[3]);
static void msStartMotion(int x, int y, int button);
static void msStopMotion();

/***********************************************************************/

/* msInit

Called by: motion callback (in some other code file)

*/

void msInit() /* NO ARGUMENTS */
{
  /* set the rotation and translation to zero */
  msAngle = 0.0;
  msTotalX = 0.0;
  msTotalY = 0.0;
  
  /* set msRotMatrix to an identity matrix */
  glPushMatrix();
  glLoadIdentity();
  glGetFloatv(GL_MODELVIEW_MATRIX, (GLfloat *)msRotMatrix);
  glPopMatrix();

  /* set msZoomSize to the default of 0.25 */
  msZoomSize = 0.25;
}

/***********************************************************************/

/* msMotion

Called by: motion callback (in some other code file)

If the trackingFlag is MS_ROTATE, this updates msAngle and msAxis, which
will be used to set msRotMatrix in msMove.

If the trackingFlag is MS_TRANSLATE, this updates msTotalX and msTotalY,
which will be used for translation in msMove. The screen coordinates have
Y positive going downward (normal for screens), so msTotalY changes by -dy.

*/

void msMotion( /* ARGUMENTS                     */
 int x,        /* screen X coordinate           */
 int y,        /* screen Y coordinate           */
 int isOrtho)  /* 1=orthographic, 0=perspective */
{
  GLfloat currentPosition[3];
  GLfloat dx;
  GLfloat dy;
  GLfloat dz;
  GLfloat zoomFactor;
  
  if (msTrackingFlag == MS_OFF)
    return;
  
  else if (msTrackingFlag == MS_ROTATE)
    {
      msPointToVector(x, y, msWidth, msHeight, currentPosition);
      
      /* calculate the angle to rotate by (directly proportional to the
	 length of the mouse movement */
      dx = currentPosition[0] - msLastPosition[0];
      dy = currentPosition[1] - msLastPosition[1];
      dz = currentPosition[2] - msLastPosition[2];
      msAngle = GLfloat(90.0 * sqrt(dx * dx + dy * dy + dz * dz));
      
      /* calculate the axis of rotation (cross product) */
      msAxis[0] = msLastPosition[1] * currentPosition[2] - 
	msLastPosition[2] * currentPosition[1];
      msAxis[1] = msLastPosition[2] * currentPosition[0] - 
	msLastPosition[0] * currentPosition[2];
      msAxis[2] = msLastPosition[0] * currentPosition[1] - 
	msLastPosition[1] * currentPosition[0];
      
      /* reset for next time */
      msLastPosition[0] = currentPosition[0];
      msLastPosition[1] = currentPosition[1];
      msLastPosition[2] = currentPosition[2];
      
      /* remember to draw new position */
      glutPostRedisplay();
    }
  else if (msTrackingFlag == MS_TRANSLATE)
    {
      dx = (((x - msLastX) * msZoomSize * 4) / msWidth);
      dy = (((y - msLastY) * msZoomSize * 4) / msWidth);
      msTotalX += dx;
      msTotalY -= dy;
      if (msTotalX > 1.5)
	msTotalX = 1.5;
      else if (msTotalX < -1.5)
	msTotalX = -1.5;
      if (msTotalY > 1.5)
	msTotalY = 1.5;
      else if (msTotalY < -1.5)
	msTotalY = -1.5;

 
      /* reset for next time */
      msLastX = (GLfloat)x;
      msLastY = (GLfloat)y;
      
      /* remember to draw new position */
      glutPostRedisplay();
    }
  else if (msTrackingFlag == MS_ZOOM)
    {
      dy = (y - msLastY);
      zoomFactor = (GLfloat)((dy < 0) ? 1.01 : (dy > 0) ? 0.99 : 1.0);
      msZoomSize *= zoomFactor;
      if (msZoomSize < 0.01)
	msZoomSize = (GLfloat)0.01;
      else if (msZoomSize > 2.0)
	msZoomSize = 2.0;

      /* reset for next time */
      msLastY = (GLfloat)y;

      /* remember to draw new position */
      glutPostRedisplay();
     }
}

/***********************************************************************/

/* msMouse

Called By: mouse callback (in some other code file)

*/

void msMouse( /* ARGUMENTS                       */
 int button,  /* mouse button that changed state */
 int state,   /* up or down                      */
 int x,       /* screen X coordinate             */
 int y)       /* screen Y coordinate             */
{
  if (state == GLUT_DOWN)
    msStartMotion(x, y, button);
  else if (state == GLUT_UP)
    msStopMotion();
}

/***********************************************************************/

/* msMove

See documentation of msReshape regarding the factor 2 used here.

*/

void msMove(
 int isOrtho)
{
  GLfloat orthoZoom;

  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  if (isOrtho)
    {
      orthoZoom = (2 * msZoomSize);
      glOrtho(-orthoZoom, orthoZoom, -orthoZoom, orthoZoom, 1.0, 8.0);
    }
  else
    {
      glFrustum(-msZoomSize, msZoomSize, -msZoomSize, msZoomSize, 1.0, 8.0);
    }
  glMatrixMode(GL_MODELVIEW);

  /* put a copy of the current matrix on top of the matrix stack */
  glPushMatrix();
  /* throw away the contents of the matrix on top of the stack and
     replace them with the contents of an identity matrix */
  glLoadIdentity();
  /* multiply the (identity) matrix now on top of the stack by a
     matrix which accomplishes a rotation of msAngle about msAxis */
  glRotatef(msAngle, msAxis[0], msAxis[1], msAxis[2]);
  /* multiply the matrix on top of the stack by the previously saved
     transform */
  glMultMatrixf((GLfloat *)msRotMatrix);
  /* save the matrix on top of the stack in msRotMatrix */
  glGetFloatv(GL_MODELVIEW_MATRIX, (GLfloat *)msRotMatrix);
  /* throw away the matrix on top of the stack */
  glPopMatrix();
  /* multiply the (identity) matrix now on the top of the stack by a
     matrix which accomplishes a translation. */
  glTranslatef(msTotalX, msTotalY, 0);
  /* multiply the matrix on the top of the stack by the new msRotMatrix */
  glMultMatrixf((GLfloat *)msRotMatrix);
}

/***********************************************************************/

/* msPointToVector

Screen coordinates have Y positive going downward, so the calculation
for v[1] is reversed from the calculation for v[0].

*/

static void msPointToVector(
 int x,
 int y,
 int width,
 int height,
 float v[3])
{
  float d;
  float a;

  /* project x, y onto a hemisphere centered within width, height. */
  v[0] = (float)((2.0 * x - width) / width);
  v[1] = (float)((height - 2.0 * y) / height);
  d = sqrt(v[0] * v[0] + v[1] * v[1]);
  v[2] = (float)cos((3.14159265 / 2.0) * ((d < 1.0) ? d : 1.0));
  a = (float)(1.0 / sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]));
  v[0] *= a;
  v[1] *= a;
  v[2] *= a;
}

/***********************************************************************/

/* msReshape

With a fixed viewing window, less of an object is seen is seen in
an orthographic view than in a perspective view. Imagine you are
inside backing away from a window - you see less of what is outside
the farther back you get. What you see in an orthographic view is
what you would see in the window from very far back.

Hence, to see the same amount in an orthographic view as in a perspective
view (when the various distances that affect viewing are unchanged), the
window size must be larger in the orthographic view. The factor 2 used
here is about right when the camera is in the default position
(at the origin looking down the -Z axis), the window is 1 unit down the
-Z axis and is perpendicular to that axis, and the object being viewed is
in a 1-unit cube whose center is on the -Z axis, 2 units down the -Z axis.

If isOrtho is an extern variable, its value does not change here when
it is changed elsewhere. Hence it must be an argument.

*/

void msReshape(
 int extent,
 int isOrtho)
{
  GLfloat orthoZoom;

  msWidth  = extent;
  msHeight = extent;
  glViewport(0, 0, (GLsizei)extent, (GLsizei)extent);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  if (isOrtho)
    {
      orthoZoom = (2 * msZoomSize);
      glOrtho(-orthoZoom, orthoZoom, -orthoZoom, orthoZoom, 1.0, 8.0);
    }
  else
    glFrustum(-msZoomSize, msZoomSize, -msZoomSize, msZoomSize, 1.0, 8.0);
}

/***********************************************************************/

/* msStartMotion

Called by: msMouse

This is called when a mouse button is pushed down. It sets the value
of the msTrackingFlag and, based on the position of the mouse, sets
the values of several parameters used for mouse motion processing.

If the "rotate" global variable (set by the keyboard in view.cc) is
non-zero, the left mouse button rotates the picture. Otherwise, the
left mouse button translates the picture.

*/

static void msStartMotion(
 int x,
 int y,
 int button)
{
  if (button == GLUT_MIDDLE_BUTTON)
    {
      msTrackingFlag = MS_ROTATE;
      msPointToVector(x, y, msWidth, msHeight, msLastPosition);
    }
  else if (button == GLUT_LEFT_BUTTON)
    {
      if (rotate)
	{
	  msTrackingFlag = MS_ROTATE;
	  msPointToVector(x, y, msWidth, msHeight, msLastPosition);
	}
      else
	{
	  msAngle = 0;
	  msTrackingFlag = MS_TRANSLATE;
	  msLastX = (GLfloat)x;
	  msLastY = (GLfloat)y;
	}
    }
  else if (button == GLUT_RIGHT_BUTTON)
    {
      msTrackingFlag = MS_ZOOM;
      msLastY = (GLfloat)y;
    }
}

/***********************************************************************/

/* msStopMotion

Called by: msMouse

This turns off the tracking flag and resets the incremental rotation angle.
It does not change the msTotalX, msTotalY, or msZoomSize.

*/

static void msStopMotion()
{
  msTrackingFlag = MS_OFF;
  msAngle = 0.0;
}

/***********************************************************************/



