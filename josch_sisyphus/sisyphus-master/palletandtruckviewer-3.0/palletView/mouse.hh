/* mouse.hh and mouse.cc provide for changing view using a 3-button mouse.
 
Usage:

call msInit() before any other ms call
call msMotion() in the motion callback
call msMouse() in the mouse callback
call msMove() in the display callback
call msReshape() in the reshape callback

Typical calls:

#include mouse.hh

void init(void)
{
  msInit();
  . . .
}

void reshape(int width, int height)
{
  int extent;
  extent = ((width < height) ? width : height);
  msReshape(extent, isOrtho);
  . . .
}

void display(void)
{
  glPushMatrix();
  
  msMove(isOrtho);
  . . . draw the scene . . .
	  
  glPopMatrix();
}

void mouse(int button, int state, int x, int y)
{
  msMouse(button, state, x, y);
  . . .
}

void motion(int x, int y)
{
  msMotion(x, y, isOrtho);
  . . .
}

int main(int argc, char** argv)
{
  . . .
  init();
  glutReshapeFunc(reshape);
  glutDisplayFunc(display);
  glutMouseFunc(mouse);
  glutMotionFunc(motion);
  . . .
}

*/

/* externally available functions */
void msInit();
void msMotion(int x, int y, int isOrtho);
void msMouse(int button, int state, int x, int y);
void msMove(int isOrtho);
void msReshape(int extent, int isOrtho);

