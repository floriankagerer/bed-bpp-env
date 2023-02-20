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
  \file truckViewer.cc

  \brief Displays truck and metrics.
  \code CVS Status:
  $Author: dr_steveb $
  $Revision: 1.2 $
  $Date: 2011/03/21 13:22:34 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/

#include <stdio.h>      // for printf, etc.
#include <string.h>     // for strcmp
#include <stdlib.h>     // for exit
#include <math.h>       // for fabs
#include "view.h"       // for draw_string, gl functions, glut functions
#include "truckViewer.h"
#include "TruckLoadingJobClasses.hh"
#include "TruckLoadingPlanClasses.hh"

#define MINIMUM_OVERLAP .4 // the minimum pallet overlap to avoid an error
#define STR_LENGTH 200
#define max(x,y) (((y) > (x)) ? (y) : (x))

/********************************************************************/

// TruckViewer static variables

col *               TruckViewer::colors;    // array of available box colors
int                 TruckViewer::countAsPlanned = 0;// num as-planned displayed
TruckLoadingJobType * TruckViewer::job;     // the job order
double              TruckViewer::maxOkXHang = 0; // largest OK hang in X dir
double              TruckViewer::maxOkYHang = 0; // largest OK hang in Y dir
int                 TruckViewer::missingOrdered;  // ordered, not in plan
int                 TruckViewer::numberPallets; // number of pallets in plan
double              TruckViewer::originX; //plan trk orig X, unscald view coords
double              TruckViewer::originY; //plan trk orig Y, unscald view coords
std::vector<LoadPalletType *> TruckViewer::pallets;  // pallets in plan
TruckLoadingPlanType * TruckViewer::plan;   // the as-planned truck
float               TruckViewer::scale;     // scale to use
float               TruckViewer::spacing;   // grid line spacing in meters
double              TruckViewer::tolerance; // tolerance for overhangs, etc.
double              TruckViewer::truckHeight; // height of truck back load area
double              TruckViewer::truckLength; // total length of truck load area
double              TruckViewer::truckWidth; // max width of truck loading area
PalletForTruckType  TruckViewer::unknownPallet; //unknown pallet

/********************************************************************/

extern TruckLoadingPlanFile * TruckLoadingPlanTree;
extern TruckLoadingJobFile * TruckLoadingJobTree;
extern FILE * yyin;
extern int yyparse();
extern FILE * yyplin;
extern int yyplparse();

/********************************************************************/

/* TruckViewer::checkJob

Returned Value: none

Called By:  TruckViewer::init

This checks that there are no duplicate PalletIds among the 
PalletForTruckTypes in the job. If any are found, this prints an
error message and exits (since the job is impossible).

This also sets the wasLoaded attribute of each PalletForTruckType
to false and counts the total number of pallets in the job, which
is stored in the numberPallets attribute of the TruckViewer/

*/

void TruckViewer::checkJob() /* NO ARGUMENTS */
{
  std::list<PalletSetType *>::iterator iter;
  std::list<PalletForTruckType *>::iterator ator;
  std::list<char *> ids;
  std::list<char *>::iterator ider;
  PalletSetType * set;
  int val;

  numberPallets = 0;
  for (iter = job->PalletSet->begin(); iter != job->PalletSet->end(); iter++)
    { // go through PalletSets
      set = *iter;
      for (ator = set->Pallet->begin(); ator != set->Pallet->end(); ator++)
	{ // go through pallet set
	  (*ator)->wasLoaded = false;
	  numberPallets++;
	  for (ider = ids.begin(); ider != ids.end(); ider++)
	    { // go through jobList and insert palletId in alphabetical order
	      val = strcmp((*ator)->PalletId, *ider);
	      if (val == 0)
		{ // duplicate pallet in job, so quit
		  fprintf(stderr, "Duplicate PalletId %s in job. Exiting\n",
			  *ider);
		  exit(1);
		}
	      if (val <= 0)
		{
		  ids.insert(ider, (*ator)->PalletId);
		  break;
		}
	    }
	  if (ider == ids.end())
	    {
	      ids.push_back((*ator)->PalletId);
	    }
	}
    }
}


/********************************************************************/

/* TruckViewer::checkPlan

Returned Value: none

Called By:  TruckViewer::init

In addition to the attributes of specified by the XML schema, a planned
pallet (LoadPalletType) has the following types of attributes that are
used by the truckViewer:
 - a pointer to the pallet in the job (PalletForTruckType) with the same id
   (or a pointer to the unknownPallet if there is no pallet in the job
   with the same id, or a pallet with the same id has already been loaded)
 - its color
 - its extent in X, Y, and Z in truck coordinates
 - error information for itself
 - error information for the entire stack up to and including itself.

Parsing the plan automatically puts values in attributes specified by
the XML schema. This function checks the plan against the job and
inserts values for a lot of the other attributes into each planned
pallet, as described below.

Go through the plan list. For each planned pallet, pal, find the job
pallet with the same id as pal.

1. If there is a job pallet with the same id as pal:

1A. Set the unorderedError of pal to false.

1B. If the wasLoaded attribute of the job pallet is true:
1Bi.  Set the reloadedError of pal to true.
1Bii. Increase the totalReloadedErrors by 1.
1Biii. Set the jobPallet of pal to the unknownPallet.
1Biv. Set the color of pal to dark gray.

1C. Otherwise (if the wasLoaded attribute of the job pallet is false):
1Ci. Set the reloadedError of pal to false.
1Cii. Set the wasLoaded of the job pallet to true.
1Ciii. Set the jobPallet of pal to point to the job pallet
1Civ. Increase the total weight of the stack by the weight of the job pallet.
1Cv. Set the color of the plan pallet to the next available color and
     add 1 to the index of available colors.

2. If there is no job pallet with the  same id as pal:

2A. Set the unorderedError of pal to true.
2B. Increase totalUnorderedErrors by 1.
2C. Set the job pallet of pal to the unknownPallet.
2D. Set the color of pal to dark gray.

3. Set the stackReloadedErrors of pal to totalReloadedErrors.

4. Set the stackUnorderedErrors of pal to totalUnorderedErrors.

5. Set the stackWeightError of pal to 1 if the stackWeight is more than
   the allowed weight on the truck and to 0 otherwise.

6. Set minX, minY, maxX, maxY, and maxZ for pal. These are values in
   truck coordinates.

7. Add pal at the end of the pallets vector of the truckViewer. A
   vector is needed so that a particular LoadPalletType can be selected
   by indexing.

8. Look at all the job pallets. For each of them that has its wasLoaded
   still set to false, add one to missingOrdered.

*/

void TruckViewer::checkPlan() /* NO ARGUMENTS */
{
  std::list<PalletForTruckType *>::iterator ator;
  std::list<PalletSetType *>::iterator iter;
  std::list<LoadPalletType *>::iterator piter;
  PalletSetType * set;
  LoadPalletType * pal;
  static col greyColor = {0.2f, 0.2f, 0.2f};
  int colorIndex = 0;
  int totalReloadedErrors = 0;
  int totalUnorderedErrors = 0;
  double totalWeight = 0;

  for (piter = plan->LoadPallet->begin();
       piter != plan->LoadPallet->end(); piter++)
    { // go through planList
      pal = *piter;
      for (iter = job->PalletSet->begin(); iter != job->PalletSet->end();iter++)
	{ // go through PalletSets
	  set = *iter;
	  for (ator = set->Pallet->begin(); ator != set->Pallet->end(); ator++)
	    { // go through the set
	      if (strcmp(pal->PalletId, (*ator)->PalletId) == 0)
		{ // found job pallet with same id as plan pallet
		  pal->unorderedError = false;
		  if ((*ator)->wasLoaded)
		    { // job pallet with given PalletId has already been loaded
		      pal->reloadedError = true;
		      totalReloadedErrors++;
		      pal->jobPallet = &unknownPallet;
		      pal->color[0] = greyColor.r;
		      pal->color[1] = greyColor.g;
		      pal->color[2] = greyColor.b;
		    }
		  else
		    {
		      pal->reloadedError = false;
		      (*ator)->wasLoaded = true;
		      pal->jobPallet = (*ator);
		      totalWeight += *(pal->jobPallet->Weight->val);
		      pal->stackWeight = totalWeight;
		      pal->color[0] = colors[colorIndex].r;
		      pal->color[1] = colors[colorIndex].g;
		      pal->color[2] = colors[colorIndex].b;
		      colorIndex++;
		    }
		  break;
		}
	    }
	  if (ator != set->Pallet->end()) // found job pallet
	    break;
	}
      if (iter == job->PalletSet->end())
	{ // did not find a job pallet matching plan pallet
	  pal->unorderedError = true;
	  totalUnorderedErrors++;
	  pal->jobPallet = &unknownPallet;
	  pal->color[0] = greyColor.r;
	  pal->color[1] = greyColor.g;
	  pal->color[2] = greyColor.b;
	}
      pal->stackReloadedErrors = totalReloadedErrors;
      pal->stackUnorderedErrors = totalUnorderedErrors;
      pal->stackWeightError = 
	((pal->stackWeight > *(job->EmptyTruck->MaximumLoadWeight->val)) ? 1:0);
      pal->minX = *(pal->Xcoordinate->val);
      pal->minY = *(pal->Ycoordinate->val);
      pal->maxZ = *(pal->jobPallet->Height->val);
      if (strcmp(pal->Orientation->val, "LengthY"))
	{
	  pal->maxX = (pal->minX + *(pal->jobPallet->Length->val));
	  pal->maxY = (pal->minY + *(pal->jobPallet->Width->val));
	}
      else
	{
	  pal->maxX = (pal->minX + *(pal->jobPallet->Width->val));
	  pal->maxY = (pal->minY + *(pal->jobPallet->Length->val));
	}
      pallets.push_back(pal);
    }
  // now check for job pallets not loaded
  missingOrdered = 0;
  for (iter = job->PalletSet->begin(); iter != job->PalletSet->end();iter++)
    { // go through PalletSets 
      set = *iter;
      for (ator = set->Pallet->begin(); ator != set->Pallet->end(); ator++)
	{ // go through the set
	  if ((*ator)->wasLoaded == false)
	    missingOrdered++;
	}
    }
}

/********************************************************************/

/* TruckViewer::drawString

Returned Value: none

Called By:
  TruckViewer::printAsPlannedPalletText
  TruckViewer::printAsPlannedText
  TruckViewer::printAsPlannedStackText

This prints one line of text starting at the given (x,y) location (in
currently active screen coordinates). The text is printed left to right
in the normal fashion for the English language.

The font argument is actually a symbol such as GLUT_BITMAP_HELVETICA_10.

*/

void TruckViewer::drawString( /* ARGUMENTS                   */
 float x,                     /* X location of start of text */
 float y,                     /* Y location of start of text */
 void * font,                 /* the font to use             */
 char * string)               /* the text to print           */
{
  char * c;

  glRasterPos2f(x, y);
  for (c = string; *c != '\0'; c++)
    {
      glutBitmapCharacter(font, *c);
    }
}

/********************************************************************/

/* TruckViewer::findIntersections

Returned Value: none

Called By: TruckViewer::init

This finds the intersections of each pallet with pallets previously
put on the truck. The index numbers of the intersecting pallets are
added to the inters list of a pallet being tested.

This also finds the intersections of each pallet with the wheel wells.
For each intersection with a wheel well, a zero is added to the inters
list of a pallet being tested.

This also sets the stackInters of each pallet; that is the total number
of intersections found in the up to and including the pallet.

In order for two boxes (pallets or wheel wells) not to intersect, in
at least one of the two XY directions, the minimum of one box must be
greater than the maximum of the other (adjusted by the tolerance).

This also sets the extents of each wheel well in the data for the wheel
well. They are used in insertWheelWell.

*/

void TruckViewer::findIntersections( /* ARGUMENTS                          */
 double tolerance)                   /* tolerance for allowed intersection */
{
  int i;                 // counter for pallets stacked on a truck
  int j;                 // counter for previously placed pallets
  LoadPalletType * pal;  // pallet being tested
  int totalInters = 0;   // total number of intersections found
  std::list<WheelWellType *> * wells;
  WheelWellType * well;
  std::list<WheelWellType *>::iterator iter;

  originX = (-1 * truckLength);
  originY = (-1 * truckWidth);
  wells = job->EmptyTruck->BackArea->WheelWell;
  for (i = 0; i < (int)pallets.size(); i++)
    {
      pal = pallets[i];
      for (j = 0; j < i; j++)
	{
	  if ((pallets[j]->minX >= (pal->maxX - tolerance)) ||
	      (pallets[j]->maxX <= (pal->minX + tolerance)) ||
	      (pallets[j]->minY >= (pal->maxY - tolerance)) ||
	      (pallets[j]->maxY <= (pal->minY + tolerance)));
	  else
	    pal->inters.push_back(j+1);
	}
      for (iter = wells->begin(); iter != wells->end(); iter++)
	{
	  well = *iter;
	  well->minX = *(well->Xcoordinate->val);
	  well->minY = *(well->Ycoordinate->val);
	  well->maxX = (well->minX + *(well->Length->val));
	  well->maxY = (well->minY + *(well->Width->val));
	  well->maxZ = *(well->Height->val);
	  if ((well->minX >= (pal->maxX - tolerance)) ||
	      (well->maxX <= (pal->minX + tolerance)) ||
	      (well->minY >= (pal->maxY - tolerance)) ||
	      (well->maxY <= (pal->minY + tolerance)));
	  else
	    pal->inters.push_back(0);
	}
      totalInters += pal->inters.size();
      pal->stackIntersections = totalInters;
    }
}

/********************************************************************/

/* TruckViewer::findOverhangs

Returned Value: none

Called By: TruckViewer::init

This finds the pallet overhangs for each pallet in the +X, -X, +Y, and
-Y directions and records them in the data for the pallet. It also finds
the largest overhangs for the stack in those four directions.

The initial values of the four stack overhangs are set to the
overhangs of the first pallet. Each time around the loop, those
values are updated.

This also keeps track of the total number of overhang errors for the stack.

All lengths are in meters.

*/

void TruckViewer::findOverhangs( /* ARGUMENTS                     */
 double tolerance)               /* tolerance for overhang errors */
{
  LoadPalletType * pal;  // the pallet being processed
  double xPlusMax = 0;   // largest overhang of all pallets in +X direction
  double xMinusMax = 0;  // largest overhang of all pallets in -X direction
  double yPlusMax = 0;   // largest overhang of all pallets in +Y direction
  double yMinusMax = 0;  // largest overhang of all pallets in -Y direction
  int i;                 // counter for pallets
  int totalOverhangErrors = 0;

  if (pallets.size() == 0)
    {
      fprintf(stderr, "There are no pallets in the plan. Exiting\n");
      exit(1);
    }
  pal = pallets[0];
  xPlusMax = (pal->maxX - truckLength);
  xMinusMax = -pal->minX;
  yPlusMax = (pal->maxY - truckWidth);
  yMinusMax = -pal->minY;
  for (i = 0; i < (int)pallets.size(); i++)
    {
      pal = pallets[i];
      pal->overhangErrorX = false;
      pal->overhangErrorY = false;
      pal->xPlusOver = (pal->maxX - truckLength);
      pal->yPlusOver = (pal->maxY - truckWidth);
      pal->xMinusOver = -pal->minX;
      pal->yMinusOver = -pal->minY;
      if (pal->xPlusOver > xPlusMax)
	xPlusMax = pal->xPlusOver;
      if (pal->yPlusOver > yPlusMax)
	yPlusMax = pal->yPlusOver;
      if (pal->xMinusOver > xMinusMax)
	xMinusMax = pal->xMinusOver;
      if (pal->yMinusOver > yMinusMax)
	yMinusMax = pal->yMinusOver;
      pal->stackXPlusOver = xPlusMax;
      pal->stackYPlusOver = yPlusMax;
      pal->stackXMinusOver = xMinusMax;
      pal->stackYMinusOver = yMinusMax;
      if (pal->xPlusOver > (maxOkXHang + tolerance))
	{
	  totalOverhangErrors++;
	  pal->overhangErrorX = true;
	}
      if (pal->xMinusOver > (maxOkXHang + tolerance))
	{
	  totalOverhangErrors++;
	  pal->overhangErrorX = true;
	}
      if (pal->yPlusOver > (maxOkYHang + tolerance))
	{
	  totalOverhangErrors++;
	  pal->overhangErrorY = true;
	}
      if (pal->yMinusOver > (maxOkYHang + tolerance))
	{
	  totalOverhangErrors++;
	  pal->overhangErrorY = true;
	}
      pal->stackOverhangErrors = totalOverhangErrors;
    }
}

/********************************************************************/

/* TruckViewer::findTotalErrors

Returned Value: none

Called By: TruckViewer::init

This finds the stackTotalErrors for each pallet. The number of ordered
pallets not on the stack (missingOrdered) is not included. All other
errors are included.

The total number of errors including the missingOrdered errors is displayed
only when the stack is complete. When the stack is incomplete, the total
number of errors dispayed is the value of stackTotalErrors for the current
pallet.

*/

void TruckViewer::findTotalErrors() /* NO ARGUMENTS */
{
  LoadPalletType * pal;  // the pallet being processed
  int i;                 // counter for pallets
  for (i = 0; i < (int)pallets.size(); i++)
    {
      pal = pallets[i];
      pal->stackTotalErrors = (pal->stackIntersections +
			       pal->stackOverhangErrors +
			       pal->stackReloadedErrors +
			       pal->stackUnorderedErrors +
			       pal->stackWeightError);
    }
}

/********************************************************************/

/* TruckViewer::init

Returned Value: none

Called By: main (in main.cc)

This initializes the truckViewer. Specifically, it does the following.

1. Set the size and weight of the unknownPallet. The weight is zero.

2. Set the tolerance of the truckViewer to the tolerance given in the
   arguments. The tolerance (in meters) is applied in determining
   overhang errors and intersection errors.

3. Read the job file and call checkJob to check the job and initialize
   wasLoaded for each job pallet to false.

4. Make the colors.

5. Read the plan file and call checkPlan; it performs a lot of checks
   and adds a lot of data for each plan pallet. Most of the metrics
   are calculated in checkPlan. That way, the data is calculated only
   once and simply retrieved as the stack is loaded in order or
   unloaded in reverse order.

6. Set the truckLength and truckWidth. 

7. Set the scale. The scale is calculated by having the larger of the
   length and width of the truck being used fit exactly into 9 grid
   squares, which is 0.45 units in picture space. That way, the
   as-planned trucks fit into the picture without going beyond the
   grid.

8. Call findIntersections to find intersections (and add some data).
   Every intersection is an error.

9. Call findOverhangs to find overhangs and overhang errors.

10. Call findTotalErrors to find total errors.

*/

void TruckViewer::init( /* ARGUMENTS                  */
 char * jobFileName,    /* name of job file           */
 char * planFileName,   /* name of plan file          */
 double toleranceIn)    /* in millimeters, see above  */
{
  unknownPallet.Length = new PalletDistanceType(new double(0.2));
  unknownPallet.Width = new PalletDistanceType(new double(0.2));
  unknownPallet.Height = new PalletDistanceType(new double(0.1));
  unknownPallet.Weight = new PalletWeightType(new double(0.0));
  tolerance = toleranceIn;
  readJob(jobFileName);
  printf("job file read\n");
  checkJob();
  makeColors(numberPallets);
  readPlan(planFileName);
  printf("plan file read\n");
  checkPlan();
  truckHeight = *(job->EmptyTruck->BackAreaHeight->val);
  truckLength = *(job->EmptyTruck->BackArea->Length->val);
  if (job->EmptyTruck->FrontArea)
    {
      truckLength += *(job->EmptyTruck->FrontArea->Length->val);
      truckWidth = max(*(job->EmptyTruck->FrontArea->Width->val),
		       *(job->EmptyTruck->BackArea->Width->val));
    }
  else
    truckWidth = *(job->EmptyTruck->BackArea->Width->val);
  scale = 0.450f / (float)max(truckLength, truckWidth);
  spacing = (float)max(truckLength, truckWidth)/9.0f;
  findIntersections(tolerance);
  findOverhangs(tolerance);
  findTotalErrors();
}

/********************************************************************/

/* TruckViewer::insertBox

Returned Value: none

Called By: TruckViewer::redraw

This draws a box at the given position using a method that will work
in a display list. The display area is actually 1 unit wide (to work
well with the camera and openGL) while the area it represents depends
on the size of the truck. The larger of the length and width of the
truck fits in 0.45 picture units.

*/

void TruckViewer::insertBox( /* ARGUMENTS                                  */
 col boxColor,               /* color of box                               */
 double minX,                /* minimum value of X on box in meters        */
 double minY,                /* minimum value of Y on box in meters        */
 double minZ,                /* minimum value of Z on box in meters        */
 double maxX,                /* maximum value of X on box in meters        */
 double maxY,                /* maximum value of Y on box in meters        */
 double maxZ,                /* maximum value of Z on box in meters        */
 bool solid)                 /* true = faces and edges, false = edges only */
{
  static GLubyte allIndices[] = {4,5,6,7, 1,2,6,5, 0,1,5,4,
				 0,3,2,1, 0,4,7,3, 2,3,7,6};
  static GLfloat vertices[] = {0,0,0, 0,0,0, 0,0,0, 0,0,0,
			       0,0,0, 0,0,0, 0,0,0, 0,0,0};
  
  glEnableClientState(GL_VERTEX_ARRAY);
  minX *= scale;
  minY *= scale;
  minZ *= scale;
  maxX *= scale;
  maxY *= scale;
  maxZ *= scale;
  vertices[0]  = (GLfloat)minX;
  vertices[1]  = (GLfloat)minY;
  vertices[2]  = (GLfloat)minZ;
  vertices[3]  = (GLfloat)minX;
  vertices[4]  = (GLfloat)maxY;
  vertices[5]  = (GLfloat)minZ;
  vertices[6]  = (GLfloat)minX;
  vertices[7]  = (GLfloat)maxY;
  vertices[8]  = (GLfloat)maxZ;
  vertices[9]  = (GLfloat)minX;
  vertices[10] = (GLfloat)minY;
  vertices[11] = (GLfloat)maxZ;
  vertices[12] = (GLfloat)maxX;
  vertices[13] = (GLfloat)minY;
  vertices[14] = (GLfloat)minZ;
  vertices[15] = (GLfloat)maxX;
  vertices[16] = (GLfloat)maxY;
  vertices[17] = (GLfloat)minZ;
  vertices[18] = (GLfloat)maxX;
  vertices[19] = (GLfloat)maxY;
  vertices[20] = (GLfloat)maxZ;
  vertices[21] = (GLfloat)maxX;
  vertices[22] = (GLfloat)minY;
  vertices[23] = (GLfloat)maxZ;
  glVertexPointer(3, GL_FLOAT, 0, vertices);
  glColor3f(boxColor.r, boxColor.g, boxColor.b);
  if (solid)
    {
      glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
      glDrawElements(GL_QUADS, 24, GL_UNSIGNED_BYTE, allIndices);
      glColor3f(0.0f, 0.0f, 0.0f);
      glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
      glDrawElements(GL_QUADS, 24, GL_UNSIGNED_BYTE, allIndices);
    }
  else
    {
      glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
      glDrawElements(GL_QUADS, 24, GL_UNSIGNED_BYTE, allIndices);
    }
}

/********************************************************************/

/* TruckViewer::insertDoors

Returned Value: none

Called By: TruckViewer::redraw

This draws the doors on the truck. 

To make it easy to see the places at which the truck may be entered,
for each door, a narrow polygon is placed just outside the loading
area extending the width of the door.  The polygon is at the level of
the floor of the truck loading area and is parallel to the floor.

The outline of the door is also drawn.

The color of the polygon and outline is assigned in the caller and is
currently whitish.

*/

void TruckViewer::insertDoors(  /* ARGUMENTS                    */
 double originX,                /* X coordinate of truck origin */
 double originY,                /* Y coordinate of truck origin */
 std::list<DoorType *> * doors) /* list of doors                */
{
  static double minX;
  static double minY;
  static double maxX;
  static double maxY;
  static double maxZ;
  std::list<DoorType *>::iterator iter;

  glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
  for (iter = doors->begin(); iter != doors->end(); iter++)
    {
      maxZ = *((*iter)->Height->val);
      if (*((*iter)->Xcoordinate->val) == 0.0)
	{
	  minX = (originX - 0.05);
	  maxX = originX;
	  minY = (originY + *((*iter)->Ycoordinate->val));
	  maxY = (minY + *((*iter)->Width->val));
	  glBegin(GL_LINE_STRIP);
	  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * minY), 0.0f);
	  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * minY),
		     (GLfloat)(scale * maxZ));
	  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * maxY),
		     (GLfloat)(scale * maxZ));
	  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * maxY), 0.0f);
	  glEnd();
	}
      else if (*((*iter)->Ycoordinate->val) == 0.0)
	{
	  minX = (originX + *((*iter)->Xcoordinate->val));
	  maxX = (minX + *((*iter)->Width->val));
	  minY = (originY - 0.05);
	  maxY = originY;
	  glBegin(GL_LINE_STRIP);
	  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * maxY), 0.0f);
	  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * maxY),
		     (GLfloat)(scale * maxZ));
	  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * maxY),
		     (GLfloat)(scale * maxZ));
	  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * maxY), 0.0f);
	  glEnd();
	}
      else
	{
	  minX = (originX + *((*iter)->Xcoordinate->val));
	  maxX = (minX + *((*iter)->Width->val));
	  minY = (originY + *((*iter)->Ycoordinate->val));
	  maxY = (minY + 0.05);
	  glBegin(GL_LINE_STRIP);
	  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * minY), 0.0f);
	  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * minY),
		     (GLfloat)(scale * maxZ));
	  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * minY),
		     (GLfloat)(scale * maxZ));
	  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * minY), 0.0f);
	  glEnd();

	}
      glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
      glBegin(GL_POLYGON);
      glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * minY), 0.0f);
      glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * minY), 0.0f);
      glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * maxY), 0.0f);
      glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * maxY), 0.0f);
      glEnd();
    }
}

/********************************************************************/

/* TruckViewer::insertTruckOutline

Returned Value: none

Called By: TruckViewer::redraw

This draws lines showing the outline of upper part of the truck
loading area. The color is assigned in the caller and is currently
whitish.

Lines are used so that the height of the truck is visible but the
pallets on the truck are also visible.

*/

void TruckViewer::insertTruckOutline( /* ARGUMENTS                    */
 double minX,                         /* X value of right rear corner */
 double maxX,                         /* X value of let front corner  */
 double minY,                         /* Y value of right rear corner */
 double maxY,                         /* Y value of left front corner */
 double height)                       /* height of truck              */
{
  glBegin(GL_LINE_STRIP);
  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * minY), 0.0f);
  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * minY),
	     (GLfloat)(scale * height));
  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * minY),
	     (GLfloat)(scale * height));
  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * minY), 0.0f);
  glEnd();
  glBegin(GL_LINE_STRIP);
  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * maxY), 0.0f);
  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * maxY),
	     (GLfloat)(scale * height));
  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * maxY),
	     (GLfloat)(scale * height));
  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * maxY), 0.0f);
  glEnd();
  glBegin(GL_LINES);
  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * minY),
	     (GLfloat)(scale * height));
  glVertex3f((GLfloat)(scale * minX), (GLfloat)(scale * maxY),
	     (GLfloat)(scale * height));
  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * minY),
	     (GLfloat)(scale * height));
  glVertex3f((GLfloat)(scale * maxX), (GLfloat)(scale * maxY),
	     (GLfloat)(scale * height));
  glEnd();
}

/********************************************************************/

/* TruckViewer::insertWheelWells

Returned Value: none

Called By: TruckViewer::redraw

The wheel wells are shown as axis-aligned boxes on the floor of
the truck loading area. The color is assigned by the caller and is
currently light gray.

*/

void TruckViewer::insertWheelWells(       /* ARGUMENTS                    */
 col color,                               /* color to use                 */
 double originX,                          /* X coordinate of truck origin */
 double originY,                          /* Y coordinate of truck origin */
 std::list<WheelWellType *> * WheelWells) /* list of wheel wells          */
{
  std::list<WheelWellType *>::iterator iter;
  WheelWellType * well;

  for (iter = WheelWells->begin(); iter != WheelWells->end(); iter++)
    {
      well = *iter;
      insertBox(color, (originX + well->minX), (originY + well->minY), 0.0,
		(originX + well->maxX), (originY + well->maxY), well->maxZ,
		true);
    }
}

/********************************************************************/

/* TruckViewer::makeColors

Returned Value: none

Called By: TruckViewer::init

This makes an array of howMany colors by picking points in the RGB cube.
The points gradually become dense in the cube. Colors that are dim
(i.e. the sum of the components is less than 0.4) are not used. Greyish
colors (near the diagonal from (0,0,0) to (1,1,1)) are not used.
Colors that are adjacent in the array are generally far apart in the
cube. The first N colors generated for any value of howMany are the same
as the first N colors for any other value of howMany (as long as N is
smaller than both).

Each time around the outer loop, all points generated so far are used
to generate up to 6 new points by adding "jump" to the values of
R, G, B, RG, GB, and RB. Newly generated points outside the cube are
not used, and dim colors are not used. Adding jump to all of RGB is not
used in order to stay away from the central diagonal. At the end of
the outer loop, the jump size is cut in half.

The first color this makes is black in order to seed the outer loop.
In order uphold the "no dim colors" rule, this makes one extra color
and sets colors to point to the second element of the array.

Multiple inner loops are used rather than a single inner loop in order
to keep adjacent colors in the array far apart in the RGB cube.

*/

void TruckViewer::makeColors( /* ARGUMENTS             */
 int howMany)                 /* size of array to make */
{
  int n;      // total number of colors at end of last go-around
  float jump; // how far to move
  int m;      // index to fill in
  int i;      // index for 0 to n
  col * cols; // another handle on the array

  if (howMany < 1)
    { // quit if howMany is zero or negative
      fprintf(stderr, "Number of orders = %d, exiting\n", howMany);
      exit(1);
    }
  howMany++;
  cols = new col[howMany];
  colors = (cols + 1);
  cols[0].r = 0.0;
  cols[0].g = 0.0;
  cols[0].b = 0.0;
  n = 1;
  m = n;

  for (jump = 1.0; m < howMany; n = (m - 1), jump = (jump / 2))
    {
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].r + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + jump) > 0.4))
	    {
	      cols[m].r = (cols[i].r + jump);
	      cols[m].g = cols[i].g;
	      cols[m].b = cols[i].b;
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].g + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + jump) > 0.4))
	    {
	      cols[m].r = cols[i].r;
	      cols[m].g = (cols[i].g + jump);
	      cols[m].b = cols[i].b;
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].b + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + jump) > 0.4))
	    {
	      cols[m].r = cols[i].r;
	      cols[m].g = cols[i].g;
	      cols[m].b = (cols[i].b + jump);
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].r + jump) <= 1.0) &&
	      ((cols[i].g + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + (2 * jump)) > 0.4))
	    {
	      cols[m].r = (cols[i].r + jump);
	      cols[m].g = (cols[i].g + jump);
	      cols[m].b = cols[i].b;
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].g + jump) <= 1.0) &&
	      ((cols[i].b + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + (2 * jump)) > 0.4))
	    {
	      cols[m].r = cols[i].r;
	      cols[m].g = (cols[i].g + jump);
	      cols[m].b = (cols[i].b + jump);
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].r + jump) <= 1.0) &&
	      ((cols[i].b + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + (2 * jump)) > 0.4))
	    {
	      cols[m].r = (cols[i].r + jump);
	      cols[m].g = cols[i].g;
	      cols[m].b = (cols[i].b + jump);
	      if (++m == howMany)
		return;
	    }
	}
    } 
}

/********************************************************************/

/* TruckViewer::printAsPlannedPalletText

Returned Value: none

Called By:  TruckViewer::printAsPlannedText

This prints the top section of the as-planned metrics window, which
gives metrics for the most recently loaded pallet.

The following items are printed.

Pallet index - The 1-based index of the planned pallet in the
   list of planned pallets in the plan data file.

Pallet id - The given pallet id. If a pallet with this id has
   already been loaded, "error! already loaded" is printed after the id.

Pallet weight - The weight of the pallet.

X hangs - The overhangs of the pallet on the +X and -X sides of the truck.
   If the overhang exceeds the allowed overhang, "error!" is also printed.
   All overhang values are positive. If the side of the pallet is
   inside the side of the truck, "under" is printed. If the side of the
   pallet sticks out beyond the side of the truck, "over" is printed.

Y hangs - The overhangs of the pallet on the +Y and -Y sides of the truck.
   If the overhang exceeds the allowed overhang, "error!" is also printed.
   All overhang values are positive. If the side of the pallet is
   inside the side of the truck, "under" is printed. If the side of the
   pallet sticks out beyond the side of the truck, "over" is printed.

Intersection errors - The number of intersection errors for the pallet.
   The index numbers of any other pallets that intersect the pallet are
   printed, and for each wheel well that intersects the pallet, a W is
   printed.

*/

void TruckViewer::printAsPlannedPalletText( /* ARGUMENTS                    */
 LoadPalletType * pal,               /* pallet to print                     */
 float * wy)                         /* Y-value on screen at which to print */
{
  char str[STR_LENGTH];                // string to print in
  std::list<int>::iterator iter;       // iterator for intersections list
  int k;                               // counter for str
  float yy;                            // surrogate for wy
  
  yy = *wy;
  snprintf(str, STR_LENGTH, "CURRENT AS-PLANNED PALLET METRICS");
  drawString(20.0f, (yy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Pallet index: %d", countAsPlanned);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Pallet id: %s%s", pal->PalletId,
	   (pal->reloadedError ? " error! already loaded" :
	    (pal->jobPallet == &unknownPallet) ? " error! not ordered" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Pallet weight: %.3f Kg",
	   *(pal->jobPallet->Weight->val));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH,
	   "X hangs: +X %.4lf m %s, -X %.4lf m %s%s",
	   fabs(pal->xPlusOver), 
	   ((pal->xPlusOver < 0) ? "under" : "over"),
	   fabs(pal->xMinusOver),
	   ((pal->xMinusOver < 0) ? "under" : "over"),
	   (pal->overhangErrorX ? " error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);

  snprintf(str, STR_LENGTH,
	   "Y hangs: +Y %.4lf m %s, -Y %.4lf m %s%s",
	   fabs(pal->yPlusOver), 
	   ((pal->yPlusOver < 0) ? "under" : "over"),
	   fabs(pal->yMinusOver),
	   ((pal->yMinusOver < 0) ? "under" : "over"),
	   (pal->overhangErrorY ? " error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  k = snprintf(str, STR_LENGTH, "Intersection errors: %d",
	       (int)pal->inters.size());
  if (pal->inters.size() > 0)
    {
      for (iter = pal->inters.begin(); iter != pal->inters.end(); ++iter)
	{
	  if (*iter == 0)
	    k += snprintf(str + k, STR_LENGTH - k, " W");
	  else
	    k += snprintf(str + k, STR_LENGTH - k, " #%d", *iter);
	}
    }
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  *wy = yy;
}

/***********************************************************************/

/* TruckViewer::printAsPlannedText

Returned Value: none

Called By: displayAsPlannedMetricsWindow (in view.cc)

This prints the as-planned metrics that have been calculated by
TruckViewer::init.  The text is printed in the as-planned metrics
window. The size and position of the text do not change if the size of
the metrics window is changed. Instead, if the window is made larger
there is more blank space, and if the window is made smaller, some of
the text is no longer visible. The text is anchored at the upper left
corner of the metrics window.

*/

void TruckViewer::printAsPlannedText( /* ARGUMENTS                 */
 int height)                          /* side of screen, in pixels */
{
  char str[STR_LENGTH];   // string to print in
  LoadPalletType * pal;   // pallet to get data from
  float wy;               // Y value of line being printed

  glColor3f(1.0f, 1.0f, 1.0f);
  wy = (float)height;

  if (countAsPlanned > 0)
    {
      pal = pallets[countAsPlanned - 1];
      printAsPlannedPalletText(pal, &wy);
      printAsPlannedStackText(pal, & wy);
    }
  snprintf(str, STR_LENGTH, "SETTINGS");
  drawString(20.0f, (wy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Grid spacing: %.4f meters", spacing);
  drawString(20.0f, (wy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Tolerance: %.4f meters", tolerance);
  drawString(20.0f, (wy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
}

/********************************************************************/

/* TruckViewer::printAsPlannedStackText

Returned Value: none

Called By: TruckViewer::printAsPlannedText

This prints the middle section of the as-planned metrics window, which
gives metrics for the entire stack, up to and including the most
recently loaded package. The number of ordered packages that are
missing is printed only after all as-planned packages have been loaded.

The "yy -= 20.0f" and "yy -= 15.0f" items give the amount of vertical
space before the next line is printed.

The following items are printed.

Packages on stack - The number of packages currently on the stack and the
total number planned.

Stack weight - The total weight of the stack in kilograms. If this exceeds
the allowed weight, " Error!" is printed after the weight.

X hangs - The overhangs of the stack of pallets (up to the current
   pallet) on the +X and -X sides of the truck.  If the overhang
   exceeds the allowed overhang, "error!" is also printed.  All
   overhang values are positive. If the side of the stack is inside
   the side of the truck, "under" is printed. If the side of the
   pallet sticks out beyond the side of the truck, "over" is printed.

Y hangs - The overhangs of the stack of pallets (up to the current
   pallet) on the +Y and -Y sides of the truck.  If the overhang
   exceeds the allowed overhang, "error!" is also printed.  All
   overhang values are positive. If the side of the stack is inside
   the side of the truck, "under" is printed. If the side of the
   pallet sticks out beyond the side of the truck, "over" is printed.

Ordered pallets not on truck errors - The number of pallets in the job
   that are not in the plan. This is printed only when all pallets in
   the plan have been loaded.

Total unordered pallet errors - The number of pallets in the plan that
   are not in the job up to the current pallet.

Total reloaded pallet errors - The number of pallets in the job that are
   loaded more than once in the plan up to the current pallet.

Total overhang errors - The total number of overhang errors for all pallets
   up to the current pallet.

Total intersection errors - The total number of intersection errors
   for all pallets up to the current pallet. Intersections with the
   wheel wells and with previously loaded pallets are included. An
   intersection of two pallets is one error, not two.

Total errors - The sum of the previous four items, plus 1 if there is
   a stack weight error, and plus the "Ordered pallets not on truck errors"
   if all pallets in the plan have been loaded.

*/

void TruckViewer::printAsPlannedStackText( /* ARGUMENTS                     */
 LoadPalletType * pal,               /* pallet to print from                */
 float * wy)                         /* Y-value on screen at which to print */
{
  char str[STR_LENGTH];  // string to print in
  float yy;

  yy = *wy;
  if (countAsPlanned == (int)pallets.size())
    snprintf(str, STR_LENGTH, "FINISHED AS-PLANNED STACK METRICS");
  else
    snprintf(str, STR_LENGTH, "CURRENT AS-PLANNED STACK METRICS");
  drawString(20.0f, (yy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Packages on stack: %d of %d",
	   countAsPlanned, (int)pallets.size());
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Stack weight: %.3f Kg%s",
	   pal->stackWeight, (pal->stackWeightError ? " Error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH,
	   "X hangs: +X %.4lf m %s, -X %.4lf m %s",
	   fabs(pal->stackXPlusOver), 
	   ((pal->stackXPlusOver < 0) ? "under" : "over"),
	   fabs(pal->stackXMinusOver),
	   ((pal->stackXMinusOver < 0) ? "under" : "over"));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH,
	   "Y hangs: +Y %.4lf m %s, -Y %.4lf m %s",
	   fabs(pal->stackYPlusOver), 
	   ((pal->stackYPlusOver < 0) ? "under" : "over"),
	   fabs(pal->stackYMinusOver),
	   ((pal->stackYMinusOver < 0) ? "under" : "over"));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  if (countAsPlanned == (int)pallets.size())
    {
      snprintf(str, STR_LENGTH, "Ordered pallets not on truck errors: %d",
	       missingOrdered);
      drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
    }
  snprintf(str, STR_LENGTH, "Total unordered pallet errors: %d",
	   pal->stackUnorderedErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total reloaded pallet errors: %d",
	   pal->stackReloadedErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total overhang errors: %d",
	   pal->stackOverhangErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total intersection errors: %d",
	   pal->stackIntersections);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total errors: %d",
	   (pal->stackTotalErrors +
	    ((countAsPlanned == (int)pallets.size()) ? missingOrdered : 0)));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  *wy = yy;
}

/***********************************************************************/

/* TruckViewer::readJob

Returned Value: none

Called By: TruckViewer::init

This reads the job file, which must be an XML data file corresponding to
the TruckLoadingJob.xsd XML schema. The data file may include XML comments
but all data elements must match the schema. The yyin and TruckLoadingJobTree
are extern variables. yyparse is an extern function. The "job" attribute
of the TruckViewer class is set to the TruckLoadingJob branch of the
TruckLoadingJobTree.

*/

void TruckViewer::readJob( /* ARGUMENTS        */
 char * jobFileName)       /* name of job file */
{
  yyin = fopen(jobFileName, "r");
  if (yyin == 0)
    {
      fprintf(stderr, "unable to open file %s for reading\n", jobFileName);
      exit(1);
    }
  yyparse();
  fclose(yyin);
  job = TruckLoadingJobTree->TruckLoadingJob;
}

/***********************************************************************/

/* TruckViewer::readPlan

Returned Value: none

Called By: TruckViewer::init

This reads the plan file, which must be an XML data file corresponding to
the TruckLoadingPlan.xsd XML schema. The data file may include XML comments
but all data elements must match the schema. The yyplin and
TruckLoadingPlanTree are extern variables. yyplparse is an extern function.
The "plan" attribute of the TruckViewer class is set to the TruckLoadingPlan
branch of the TruckLoadingPlanTree.
*/

void TruckViewer::readPlan( /* ARGUMENTS         */
 char * planFileName)       /* name of plan file */
{
  yyplin = fopen(planFileName, "r");
  if (yyplin == 0)
    {
      fprintf(stderr, "unable to open file %s for reading\n", planFileName);
      exit(1);
    }
  yyplparse();
  fclose(yyplin);
  plan = TruckLoadingPlanTree->TruckLoadingPlan;
}

/***********************************************************************/

/* TruckViewer::recalculate

Returned Value: none

Called By: keyboard (in view.cc) - change argument will be 1 or -1

This is called if the f or g key is pressed.

1. If countAsPlanned is larger than zero and change is -1, subtract 1
from countAsPlanned.
2. Otherwise, if countAsPlanned is less than the size of the as-planned
stack and change is +1, add 1 to countAsPlanned.

*/

void TruckViewer::recalculate( /* ARGUMENTS */
 int change)                   /* 1, or -1  */
{
  if (((countAsPlanned > 0) && (change == -1)) ||
      ((countAsPlanned < (int)(plan->LoadPallet->size())) && (change == 1)))
    {
      countAsPlanned += change;
    }
}

/********************************************************************/

/* TruckViewer::redraw

Returned Value: none

Called By: buildDisplayList (in view.cc)

This draws the truck as planned.

The origin of a truck is in its lower left corner (when viewing
the XY plane in the usual orientation (+X right, +Y up) from above
(+Z).

The origin of the graphics coordinate system is at the center of the grid.
The grid is one unit by one unit in the graphics coordinate system.
The scale of the grid is adjusted according to the size of the truck,
as given in the job file.

The truck is offset into the third quadrant of the graphics
coordinate system, so that the upper right corner of the truck is at
the origin of the graphics coordinate system.

The loading area of the truck is a large light gray box. The wheel wells
are small light gray boxes on the top of the light gray box. The edges of
the upper part of the truck loading area are shown as whitish lines.
The doors are shown as whitish lines plus a thin white polygon at the
base of the door (to make it easier to see).

The pallets on the truck shown as boxes. If a box is in error, it is small
and dark gray. Otherwise it is the size given in the job and is colored.

*/

void TruckViewer::redraw() /* NO ARGUMENTS   */
{
  static col grayish = {0.5f, 0.5f, 0.5f};
  static col whitish = {0.8f, 0.8f, 0.8f};
  col color;
  LoadPalletType * planPallet;
  PalletForTruckType * jobPallet;
  std::list<LoadPalletType *>::iterator iter;
  int count;

  // draw the truck in the third quadrant with its top on the XY plane
  insertBox(grayish, originX, originY, -0.04, 0.0, 0.0, 0.0, true);
  insertWheelWells(grayish, originX, originY, 
		   job->EmptyTruck->BackArea->WheelWell);
  glColor3f(whitish.r, whitish.g, whitish.b);
  insertTruckOutline(originX, 0.0, originY, 0.0, truckHeight);
  insertDoors(originX, originY, job->EmptyTruck->BackArea->Door);
  for (count = 1, iter=plan->LoadPallet->begin();
       (count <= countAsPlanned) && (iter != plan->LoadPallet->end());
       count++, iter++)
    { // draw box on truck as planned
      planPallet = *iter;
      jobPallet = planPallet->jobPallet;
      color.r = planPallet->color[0];
      color.g = planPallet->color[1];
      color.b = planPallet->color[2];
      insertBox(color, (originX + planPallet->minX),
		(originY + planPallet->minY), 0.0, (originX + planPallet->maxX),
		(originY + planPallet->maxY), planPallet->maxZ, true);
    }
}

/********************************************************************/

/* TruckViewer::usageMessage

Returned Value: none

Called By: main

This prints a message about how to use truckViewer.

*/

void TruckViewer::usageMessage(
 char * command)
{
  fprintf(stderr, "usage: %s -j <job> -p <plan> [-t <tolerance>]\n", command);
  fprintf(stderr, "job and plan are file names\n");
  fprintf(stderr, "tolerance is a number of meters\n");
  fprintf(stderr, "Example 1: %s -j job1.xml -p plan1.xml\n", command);
  fprintf(stderr, "Example 2: %s -j job1.xml -p plan1.xml -t 0.001\n", command);
  exit(1);
}

/********************************************************************/

/* main

Returned Value: int

This is the main function for the truckViewer. It reads the arguments,
calls TruckViewer::init, and prints information about how to use
truckViewer. Then it enters the glutMainLoop, which handles all the
user interaction and draws the display.

The tolerance (in meters) is applied in determining two kinds of
errors: overhang, and intersection. The default tolerance is zero.

If any argument is bad, an error or usage message is printed and
truckViewer exits.

*/

int main(
 int argc,
 char * argv[])
{
  char jobFileName[STR_LENGTH] = "";
  char planFileName[STR_LENGTH] = "";
  int i;
  double tolerance = 0;
  
  if(argc < 5)
    TruckViewer::usageMessage(argv[0]);
  for (i = 1; i < argc; i+=2)
    {
      if(strcmp(argv[i], "-j") == 0)
	{
	  if (argc < (i+2))
	    TruckViewer::usageMessage(argv[0]);
	  strncpy(jobFileName, argv[i+1], STR_LENGTH);
	}
      else if (strcmp(argv[i], "-p") == 0)
	{
	  if (argc < (i+2))
	    TruckViewer::usageMessage(argv[0]);
	  strncpy(planFileName, argv[i+1], STR_LENGTH);
	}
      else if (strcmp(argv[i], "-t") == 0)
	{
	  if (argc < (i+2))
	    TruckViewer::usageMessage(argv[0]);
	  if ((sscanf(argv[i+1], "%lf", &tolerance) != 1) || (tolerance < 0.0))
	    {
	      fprintf(stderr, "bad tolerance value %s\n", argv[i+1]);
	      fprintf(stderr, "Exiting\n");
	      exit(1);
	    }
	}
    }
  TruckViewer::init(jobFileName, planFileName, tolerance);
  printf("Press r to toggle left mouse button "
	 "between translating and rotating\n");
  printf("Hold down left mouse button and move mouse "
	 "to translate or rotate pallet\n");
  printf("Hold down middle mouse button and move mouse to rotate truck\n");
  printf("Hold down right mouse button and move mouse up/dn to zoom truck\n");
  printf("Press h to return to the default view\n");
  printf("Press g to add the next pallet to the truck\n");
  printf("Press f to remove the last pallet from the truck\n");
  printf("Press t to save the current image in a ppm file\n");
  printf("Press z or q to exit\n");
  glInit(argc, argv,  "TruckViewer");
  glutMainLoop();
  
  return 0;
}

/********************************************************************/
