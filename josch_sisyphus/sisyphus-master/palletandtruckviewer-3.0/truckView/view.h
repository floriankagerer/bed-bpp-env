/*
 * view.h
 *
 *  Created on: Mar 5, 2010
 *      Author: pushkar
 *      Brief: Viewer for opengl (Edit main)
 */

#ifndef VIEW_H_
#define VIEW_H_

#include <GL/glut.h>
#include <GL/gl.h>
#include <GL/glu.h>

#ifdef WIN32
#define snprintf sprintf_s
#define strncpy strncpy_s
#endif

void glInit(int argc, char * argv[], const char * win_name);

#endif /* VIEW_H_ */
