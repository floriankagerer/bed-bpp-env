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
  \file main.cc

  \brief Main function for palletViewer 
  \code CVS Status:
  $Author: tomrkramer $
  $Revision: 1.16 $
  $Date: 2011/02/14 16:21:49 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/

#include <stdio.h>
#include "view.h"    // for glut functions
#include "palletViewer.h"

/********************************************************************/

#define charSize 100

/********************************************************************/

/* usageMessage

Returned Value: none

Called By: main

This prints a message about how to use palletViewer.

*/

void usageMessage(char * command)
{
  fprintf(stderr, "usage: %s -o <order> -p <packlist> "
	  "[-b <asBuilt>] [-s <scoring>] [-t <tolerance>]\n",
	  command);
  fprintf(stderr, "order, packlist, scoring, and asBuilt are file names\n");
  fprintf(stderr, "tolerance is a number of millimeters\n");
  fprintf(stderr, "Example 1: %s -o order.xml -p pack1.xml\n",
	  command);
  fprintf(stderr, "Example 2: %s -o order1.xml -p pack1.xml "
	  "-p built1.xml -s score1.xml -t 0.5\n", command);
  exit(1);
}

/********************************************************************/

/* main

Returned Value: int

This is the main function for the palletViewer. It reads the arguments,
calls PalletViewer::init, and prints information about how to use
palletViewer. Then it enters the glutMainLoop, which handles all the
user interaction and draws the display.

The tolerance (in millimeters) is applied in determining three kinds of
errors: overlap, overhang, and intersection. It is also applied in
finding overlaps. The default tolerance is zero.

If any argument is bad, an error or usage message is printed and
palletViewer exits.

This uses scoreAsPlannedConfig1.xml as the default scoring configuration
file if no file is given using the -s option.

*/

int main(
 int argc,
 char * argv[])
{
  char orderFile[charSize] = "";
  char packlistFile[charSize] = "";
  char asBuiltFile[charSize] = "";
  char scoringFile[charSize] = "";
  int i;
  double tolerance = 0;
  
  if(argc < 5)
    usageMessage(argv[0]);
  for (i = 1; (int)i < argc; i+=2)
    {
      if(strcmp(argv[i], "-o") == 0)
	{
	  if (argc < (i+2))
	    usageMessage(argv[0]);
	  strncpy(orderFile, argv[i+1], charSize);
	}
      else if (strcmp(argv[i], "-p") == 0)
	{
	  if (argc < (i+2))
	    usageMessage(argv[0]);
	  strncpy(packlistFile, argv[i+1], charSize);
	}
      else if (strcmp(argv[i], "-b") == 0)
	{
	  if (argc < (i+2))
	    usageMessage(argv[0]);
	  strncpy(asBuiltFile, argv[i+1], charSize);
	}
      else if (strcmp(argv[i], "-s") == 0)
	{
	  if (argc < (i+2))
	    usageMessage(argv[0]);
	  strncpy(scoringFile, argv[i+1], charSize);
	}
      else if (strcmp(argv[i], "-t") == 0)
	{
	  if (argc < (i+2))
	    usageMessage(argv[0]);
	  if ((sscanf(argv[i+1], "%lf", &tolerance) != 1) || (tolerance < 0.0))
	    {
	      fprintf(stderr, "bad tolerance value %s\n", argv[i+1]);
	      fprintf(stderr, "Exiting\n");
	      exit(1);
	    }
	}
    }
  if (scoringFile[0] == 0)
    strncpy(scoringFile, "scoreAsPlannedConfig1.xml", charSize);
  PalletViewer::init(orderFile, packlistFile,
		     asBuiltFile, scoringFile, tolerance);
  printf("Press r to toggle left mouse button "
	 "between translating and rotating\n");
  printf("Hold down left mouse button and move mouse "
	 "to translate or rotate pallet\n");
  printf("Hold down middle mouse button and move mouse to rotate pallet\n");
  printf("Hold down right mouse button and move mouse up/dn to zoom pallet\n");
  printf("Press h to return to the default view\n");
  printf("Press g to add the next box to the stack\n");
  printf("Press f to remove the last box from the stack\n");
  printf("Press t to save the current image in a ppm file\n");
  printf("Press z or q to exit\n");
  glInit(argc, argv, "Pallet Viewer");
  glutMainLoop();
  
  return 0;
}

/********************************************************************/
