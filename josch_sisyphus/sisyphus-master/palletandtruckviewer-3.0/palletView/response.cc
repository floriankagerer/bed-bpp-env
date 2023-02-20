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
  \file response.cc

  \brief Parses mixed pallet plan and calculates metrics.
  \code CVS Status:
  $Author: tomrkramer $
  $Revision: 1.15 $
  $Date: 2011/02/16 13:39:45 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/



#include "packlist.h"
#include "xml_parser.h"
#include "response.h"
#include <vector>
#include <math.h>
#include <stdlib.h>
#include <fstream>

typedef unsigned int uint;

/********************************************************************/

AreaData::AreaData() {};

/********************************************************************/

/* AreaData::AreaData

This constructor initializes:
 - pack to packIn
 - area to areaIn
 - pressure to -1.0 to indicate that it is not yet set.

*/

AreaData::AreaData(
 Package * packIn,
 double areaIn)
{
  pack = packIn;
  area = areaIn;
  pressure = -1.0;
}

/********************************************************************/

AreaData::~AreaData() {};

/********************************************************************/

Dimensions::Dimensions() {}

/********************************************************************/

Dimensions::~Dimensions() {}

/********************************************************************/

/* Dimensions::parseDimensions

Returned Value: none

Called By: PackPallet::parsePackPallet

This parses an XML data file text string that describes the dimensions
of a pallet.

*/

void Dimensions::parseDimensions( /* ARGUMENTS       */
 std::string text)                /* string to parse */
{
  length = atoi(xml_parse_tag(text, "Length").c_str());
  width = atoi(xml_parse_tag(text, "Width").c_str());
  max_load_height = atoi(xml_parse_tag(text, "MaxLoadHeight").c_str());
  max_load_weight = atoi(xml_parse_tag(text, "MaxLoadWeight").c_str());
}

/********************************************************************/

Overhang::Overhang() {}

/********************************************************************/

Overhang::~Overhang() {}

/********************************************************************/

/* Overhang::parseOverhang

Returned Value: none

Called By: PackPallet::parsePackPallet

*/

void Overhang::parseOverhang( /* ARGUMENTS       */
 std::string text)            /* string to parse */
{
  length = atoi(xml_parse_tag(text, "Length").c_str());
  width = atoi(xml_parse_tag(text, "Width").c_str());
}

/********************************************************************/

Package::Package() {};

/********************************************************************/

Package::~Package() {};

/********************************************************************/

/* Package::findBoundaries

Returned Value: none

Called By: Package::parsePackage

This assumes the box is oriented so that its edges are parallel to the
X, Y, and Z axes (which is how all packages are assumed to placed).

This sets minX, minY, and minZ of a Package to the point on the box
with minimum x, y, and z.  It sets maxX, maxY, and maxZ to the point
on the box with maximum x, y, and z. It sets the area of the Package
to the area of the face of the box that is pointing up.

The place position is in the middle of the face of the box that points up.

All values are in millimeters.

*/

void Package::findBoundaries() /* NO ARGUMENTS */
{
  double xDist;
  double yDist;
  double zDist;

  if ((orientation == 1) || (orientation == 3) ||
      (orientation == 13) || (orientation == 15))
    {
      xDist = (double)article.length;
      yDist = (double)article.width;
      zDist = (double)article.height;
    }
  else if ((orientation == 2) || (orientation == 4) ||
	   (orientation == 14) || (orientation == 16))
    {
      xDist = (double)article.width;
      yDist = (double)article.length;
      zDist  = (double)article.height;
    }
  else if ((orientation == 5) || (orientation == 7) ||
	   (orientation == 17) || (orientation == 19))
    {
      xDist = (double)article.length;
      yDist = (double)article.height;
      zDist  = (double)article.width;
    }
  else if ((orientation == 6) || (orientation == 8) ||
	   (orientation == 18) || (orientation == 20))
    {
      xDist = (double)article.height;
      yDist = (double)article.length;
      zDist  = (double)article.width;
    }
  else if ((orientation == 9) || (orientation == 11) ||
	   (orientation == 21) || (orientation == 23))
    {
      xDist = (double)article.height;
      yDist = (double)article.width;
      zDist  = (double)article.length;
    }
  else if ((orientation == 10) || (orientation == 12) ||
	   (orientation == 22) || (orientation == 24))
    {
      xDist = (double)article.width;
      yDist = (double)article.height;
      zDist  = (double)article.length;
    }
  else
    {
      fprintf(stderr, "orientation value %d out of range, exiting\n",
	      orientation);
      exit(1);
    }
  area = xDist * yDist;
  minX = (double)place_position.x - (xDist / 2.0);
  maxX = (double)place_position.x + (xDist / 2.0);
  minY = (double)place_position.y - (yDist / 2.0);
  maxY = (double)place_position.y + (yDist / 2.0);
  minZ = (double)place_position.z - zDist;
  maxZ = (double)place_position.z;
}

/********************************************************************/

/* Package::findOverhangs

Returned Value: none

Called By: PackPallet::findOverhangs

This calculates the four overhangs for this box (xPlusOver, etc.) and
the four maximum overhangs for the stack on the pallet up to and
including this box.  If the overhang for this box in any direction is
greater than the current stack overhang, the current stack overhang is
reset.

This also determines if the overhangs of this box exceed the allowed
overhangs and adds 1 to errors for each error it finds. Then it sets
the stackOverhangErrors of this box.

Before this is called, errors, minX, minY, maxX, and maxY must already
have been set.

All four of xPlusOver, yPlusOver, xMinusOver, and yMinusOver are positive
if there is overhang and negative if there is underhang.

All lengths are in millimeters.

An overhang must exceed the allowed overhang plus the tolerance in order
to be considered in error.

*/

void Package::findOverhangs( /* ARGUMENTS                                    */
 double palletLength,        /* length of X side of pallet                   */
 double palletWidth,         /* length of Y side of pallet                   */
 double maxOkXHang,          /* largest allowed X overhang                   */
 double maxOkYHang,          /* largest allowed Y overhang                   */
 int * errors,               /* total number of overhang errors, maybe updatd*/
 double * xPlusMax,          /* previous max +X overhang, maybe updated here */
 double * xMinusMax,         /* previous max -X overhang, maybe updated here */
 double * yPlusMax,          /* previous max +Y overhang, maybe updated here */
 double * yMinusMax,         /* previous max -Y overhang, maybe updated here */
 double tolerance)           /* tolerance                                    */
{
  overhangErrorX = 0;
  overhangErrorY = 0;
  xPlusOver = (maxX - palletLength);
  yPlusOver = (maxY -  palletWidth);
  xMinusOver = -minX;
  yMinusOver = -minY;
  if (xPlusOver > *xPlusMax)
    *xPlusMax = xPlusOver;
  if (yPlusOver > *yPlusMax)
    *yPlusMax = yPlusOver;
  if (xMinusOver > *xMinusMax)
    *xMinusMax = xMinusOver;
  if (yMinusOver > *yMinusMax)
    *yMinusMax = yMinusOver;
  stackXPlusOver = *xPlusMax;
  stackYPlusOver = *yPlusMax;
  stackXMinusOver = *xMinusMax;
  stackYMinusOver = *yMinusMax;
  if (xPlusOver > (maxOkXHang + tolerance))
    {
      (*errors)++;
      overhangErrorX++;
    }
  if (xMinusOver > (maxOkXHang + tolerance))
    {
      (*errors)++;
      overhangErrorX++;
    }
  if (yPlusOver > (maxOkYHang + tolerance))
    {
      (*errors)++;
      overhangErrorY++;
    }
  if (yMinusOver > (maxOkYHang + tolerance))
    {
      (*errors)++;
      overhangErrorY++;
    }
  stackOverhangErrors = *errors;
}

/********************************************************************/

/* Package::findOverlapBox

Returned Value: double
  This returns the area of the part of the bottom of the box in this
  package that is over the box in package pack, in square millimeters.

Called By: PackPallet::findOverlaps

This should be called only if the bottom of the box in this package is
at the same height as the top of the box in package pack. The function is
not checking that.

The part of the box in this package in contact with the box in package
pack is a rectangle if there is any contact. This finds the length and
width of that rectangle.

*/

double Package::findOverlapBox( /* ARGUMENTS                         */
 Package * pack)                /* a package that might support this */
{
  double xDist;  // length parallel to X axis
  double yDist;  // length parallel to Y axis

  if ((minX >= pack->maxX) || (maxX < pack->minX) ||
      (minY >= pack->maxY) || (maxY < pack->minY))
    return 0;
  xDist = maxX - minX;
  yDist = maxY - minY;
  if (minX < pack->minX)
    xDist = (xDist - (pack->minX - minX));
  if (minY < pack->minY)
    yDist = (yDist - (pack->minY - minY));
  if (maxX > pack->maxX)
    xDist = (xDist - (maxX - pack->maxX));
  if (maxY > pack->maxY)
    yDist = (yDist - (maxY - pack->maxY));
  return (xDist * yDist);
}

/********************************************************************/

/* Package::findOverlapPallet

Returned Value: bool
  This returns the area of the part of the bottom of the box that
  is over the pallet, in square millimeters.

Called By: PackPallet::findOverlaps

This should be called only if the bottom of the box in this package is
at the top of the pallet. The function is not checking that.

The face of the box pointing down will not be on the top of the pallet
if the box is completely off the pallet.

The part of the box on the pallet is a rectangle if any part of the
box is on the pallet. This finds the length and width of that rectangle
and sets *palArea to the area of the rectangle.

*/

void Package::findOverlapPallet( /* ARGUMENTS                           */
 unsigned int length,            /* length of pallet in millimeters     */
 unsigned int width,             /* width of pallet in millimeters      */
 double * palArea)               /* area of box on the pallet, set here */
{
  double xDist; // extent in X direction of the part of the box on the pallet
  double yDist; // extent in Y direction of the part of the box on the pallet

  if ((minX >= length) || (maxX <= 0) || (minY >= width)  || (maxY <= 0))
    {
      *palArea = 0;
    }
  else
    {
      xDist = maxX - minX;
      yDist = maxY - minY;
      if (minX < 0)
	xDist = (xDist + minX);
      if (minY < 0)
	yDist = (yDist + minY);
      if (maxX > length)
	xDist = (xDist - (maxX - length));
      if (maxY > width)
	yDist = (yDist - (maxY - width));
      *palArea = (xDist * yDist);
    }
}

/********************************************************************/

/* Package::parsePackage

Returned Value: Package
  This returns a Package parsed from the packageString.

Called By: PackPallet::parsePackPallet

*/

void Package::parsePackage( /* ARGUMENTS                   */
 std::string packageString) /* string describing a package */
{
  pack_sequence = atoi(xml_parse_tag(packageString, "PackSequence").c_str());
  incoming_sequence =
    atoi(xml_parse_tag(packageString, "IncomingSequence").c_str());
  orderlineno = atoi(xml_parse_tag(packageString, "OrderLineNo").c_str());
  parent_layer = atoi(xml_parse_tag(packageString, "ParentLayer").c_str());
  article.parse(xml_parse_tag(packageString, "Article"));
  barcode.parse(xml_parse_tag(packageString, "Barcode"));
  place_position.parsePoint(xml_parse_tag(packageString, "PlacePosition"));
  orientation = atoi(xml_parse_tag(packageString, "Orientation").c_str());
  approach_point_1.parsePoint(xml_parse_tag(packageString, "ApproachPoint1"));
  approach_point_2.parsePoint(xml_parse_tag(packageString, "ApproachPoint2"));
  approach_point_3.parsePoint(xml_parse_tag(packageString, "ApproachPoint3"));
  stack_height_before =
    atoi(xml_parse_tag(packageString, "StackHeightBefore").c_str());
  findBoundaries();
}

/********************************************************************/

/* Package::updateCog

Returned Value: none

Called By: PackPallet::findCogs

For the package, this finds:
 cogRelX
 cogRelY
 cogZ
 stackWeight
 stackHeight

This also updates:
 momentX
 momentY
 momentZ
 stackWeightIn
 stackWeightErrors
 stackHeightIn
 stackHeightErrors

The place position is in the middle of the top of the box. We are
assuming the COG of a box is at its center, so the Z value of the
COG of the box is half the height below the place position.

*/

void Package::updateCog( /* ARGUMENTS                                         */
 double * momentX,       /* total X moment around pallet center, updated here */
 double * momentY,       /* total Y moment around pallet center, updated here */
 double * momentZ,       /* total Z moment around pallet center, updated here */
 double halfLength,      /* half the length of the pallet                     */
 double halfWidth,       /* half the width of the pallet                      */
 double * stackWeightIn, /* total weight of stack, updated here               */
 double * stackHeightIn, /* total height of stack, maybe updated here         */
 double maxWeight,       /* maximum load weight allowed on pallet             */
 double maxHeight)       /* maximum stack height allowed (above pallet top)   */
{
  double weight;
  double height;

  height = (place_position.z / 1000.0); //Z location of top of box in meters
  if (height > *stackHeightIn)
    *stackHeightIn = height;
  stackHeight = *stackHeightIn;
  stackHeightErrors = ((stackHeight > maxHeight) ? 1 : 0);
  height -= (article.height / 2000.0); // Z location of COG of box in meters
  weight = (article.weight / 1000.0);
  *momentX += (((place_position.x / 1000.0) - halfLength) * weight);
  *momentY += (((place_position.y / 1000.0) - halfWidth) * weight);
  *momentZ += (height * weight);
  *stackWeightIn += weight;
  stackWeight = *stackWeightIn;
  stackWeightErrors = ((stackWeight > maxWeight) ? 1 : 0);
  cogRelX = (*momentX / (stackWeight * halfLength));
  cogRelY = (*momentY / (stackWeight * halfWidth));
  cogZ = (*momentZ / stackWeight);
}

/********************************************************************/

PackList::PackList() {}

/********************************************************************/

PackList::~PackList() {}

/********************************************************************/

/* PackList::parsePackList

Returned Value: none

Called By: PackList::read_response

This parses the packlistString to build "this" PackList.

*/

void PackList::parsePackList( /* ARGUMENTS                    */
 std::string packListString)  /* string describing a PackList */
{
  std::string palletString;
  PackPallet packPallet;

  packedPallets.clear();
  order_id = atoi(xml_parse_tag(packListString, "OrderID").c_str());
  while(1)
    {
      palletString = xml_parse_tag(packListString, "PackPallet");
      if(strlen(palletString.c_str()) == 0)
	break;
      packPallet.parsePackPallet(palletString);
      packedPallets.push_back(packPallet);
      xml_parse_remove_first_tag(&packListString, "PackPallet");
    }
}

/********************************************************************/

/* PackList::read_response (static)

Returned Value: PackList

Called By: PalletViewer::init (in palletViewer.cc)

This:
1. opens the packlist file,
2. reads the entire file into the buffer
3. converts the buffer into the packlistString, which is a std::string,
4. parses the packlistString into a PackList,
5. returns the PackList.

*/

PackList PackList::read_response( /* ARGUMENTS            */
 const char * filename)           /* name of file to read */
{
  std::ifstream ifs(filename);
  int bufferLength;
  std::string packlistString;
  PackList list;
  char * buffer;

  if(!ifs.is_open())
    {
      fprintf(stderr, "%s file not found.\n Exiting.\n", filename);
      exit(1);
    }
  
  bufferLength = xml_parser_get_buffer_length(filename);
  buffer = (char*) malloc (bufferLength + 1);
  ifs.read(buffer, bufferLength);
  packlistString = buffer;
  list.parsePackList(xml_parse_tag(packlistString, "PackList"));
  free(buffer);
  return list;
}

/********************************************************************/

PackPallet::PackPallet() {}

/********************************************************************/

PackPallet::~PackPallet() {}

/********************************************************************/

/* PackPallet::findCogs

Returned Value: none

Called By: PalletViewer::init

This calls updateCog for each package so that each package has the
center of gravity (COG) for the stack including all packages up to and
including that package.  Package:updateCog also updates several other
data items for each package and the stack. See documentation of
package:updateCog

The relative coordinates represent the fraction of half the length
or width of the pallet that the COG is off center. When the COG
is at the center, the relative coordinate is 0.0. When the COG is
at the edge of the pallet, the relative coordinate is 1.0 or -1.0.

*/

void PackPallet::findCogs() /* NO ARGUMENTS */
{
  double momentX = 0;     // total X moment around the center, Kg*m
  double momentY = 0;     // total Y moment around the center, Kg*m
  double momentZ = 0;     // total Z moment around the center, Kg*m
  unsigned int i;         // index for packages
  double halfLength;      // half the length of the pallet, m
  double halfWidth;       // half the width of the pallet, m
  double stackWeight = 0; // weight of stack, Kg
  double stackHeight = 0; // height of stack, m

  halfLength = (dimensions.length / 2000.0);
  halfWidth =  (dimensions.width / 2000.0);
  for (i = 0; i < packages.size(); i++)
    {
      packages[i].updateCog(&momentX, &momentY, &momentZ, halfLength,
			    halfWidth, &stackWeight, &stackHeight,
			    (dimensions.max_load_weight / 1000.0),
			    (dimensions.max_load_height / 1000.0));
    }
}

/********************************************************************/

/* PackPallet::findIntersections

Returned Value: none

Called By: PalletViewer::init

This finds the intersections of each box with the pallet and
with boxes previously put on the stack. The sequence numbers of the
intersecting boxes are added to the inters list of a box being tested.
If a box intersects the pallet, 0 is put on the inters list.

This also sets the stackInters of each box.

In order for two boxes not to intersect, in at least one of the
three XYZ directions, the minimum of one box must be greater than
the maximum of the other.

*/

void PackPallet::findIntersections( /* ARGUMENTS                          */
 double tolerance)                  /* tolerance for allowed intersection */
{
  unsigned int i;      // counter for packages stacked on a pallet
  unsigned int j;      // counter for previously placed packages
  Package * pack;      // package being tested
  int totalInters = 0; // total number of intersections found

  for (i = 0; i < packages.size(); i++)
    {
      pack = &(packages[i]);
      if (pack->minZ < -tolerance)
	pack->inters.push_back(0);
      for (j = 0; j < i; j++)
	{
	  if ((packages[j].minX >= (pack->maxX - tolerance)) ||
	      (packages[j].maxX <= (pack->minX + tolerance)) ||
	      (packages[j].minY >= (pack->maxY - tolerance)) ||
	      (packages[j].maxY <= (pack->minY + tolerance)) ||
	      (packages[j].minZ >= (pack->maxZ - tolerance)) ||
	      (packages[j].maxZ <= (pack->minZ + tolerance)));
	  else
	    pack->inters.push_back((int)(packages[j].pack_sequence));
	}
      totalInters += pack->inters.size();
      pack->stackInters = totalInters;
    }
}

/********************************************************************/

/* PackPallet::findOverhangs

Returned Value: none

Called By: PalletViewer::init

This finds the pallet overhangs for each package in the +X, -X, +Y, and
-Y directions and records them in the data for the package. It also finds
the largest overhangs for the stack in those four directions.

The initial values of the four stack overhangs are set to the overhangs
of the first package. Each call to package::findOverhangs may update those
values.

This also keeps track of the total number of overhang errors for the stack.

All lengths are in millimeters.

*/

void PackPallet::findOverhangs( /* ARGUMENTS                     */
 double tolerance)              /* tolerance for overhang errors */
{
  double length;         // length of pallet
  double width;          // width of pallet
  double xPlusMax = 0;   // largest overhang of all packages in +X direction
  double xMinusMax = 0;  // largest overhang of all packages in -X direction
  double yPlusMax = 0;   // largest overhang of all packages in +Y direction
  double yMinusMax = 0;  // largest overhang of all packages in -Y direction
  int errors = 0;        // total number of overhang errors for stack so far
  unsigned int i;        // counter for packages

  length = (double)dimensions.length;
  width =  (double)dimensions.width;
  xPlusMax = (packages[0].maxX - length);
  xMinusMax = -packages[0].minX;
  yPlusMax = (packages[0].maxY - width);
  yMinusMax = -packages[0].minY;
  for (i = 0; i < packages.size(); i++)
    {
      packages[i].findOverhangs(length, width,
				overhangs.length, overhangs.width, &errors,
				&xPlusMax, &xMinusMax, &yPlusMax, &yMinusMax,
				tolerance);
    }
}

/********************************************************************/

/* PackPallet::findOverlaps

Returned Value: none

Called By: PalletViewer::init

This goes through all the packages on the pallet. For each package,
packI, it does the following:

A. If the bottom of packI is at the same level as the top of the pallet:
 - packI->findOverlapPallet is called to find packI's overlap with the pallet.
 - if packI overlaps the pallet, totalConnections is increased by 1.

B. Otherwise, the function goes through all the packages and calls
   findOverlapBox for each one, packJ, whose top is at the same level as
   the bottom of packI. If packI sits on top of packJ:
 - A pointer to an AreaData is pushed onto the ups list of packJ.
   The AreaData consists of packI, areaJ, and an unset pressure (-1.0).
 - A pointer to an AreaData is pushed onto the downs list of packI.
   The AreaData consists of packJ, areaJ, and an unset pressure (-1.0).
 - The contact area (areaJ) is added to the total bottom contact area
   of packI.
 - If packJ is loaded after packI, 1 is added to the loadingErrors of
   packI and to the totalLoadingErrors.

   After all packJs have been checked, totalConnections is increased by
   the number of boxes on which packI rests.

C. Then it:
 - sets stackLoadingErrors of packI to the current totalLoadingErrors.
 - sets the overlapFraction of packI.
 - if the overlapFraction of packI is less than minOverlapForError,
   adds 1 to totalOverlapErrors.
 - sets the stackOverlapErrors of packI to the current totalOverlapErrors.
 - adds the overlap fraction of packI to the totalOverlap.
 - sets the stackOverlapFraction of packI.
 - sets the stackAverageConnects of packI.

This is using the tolerance in determining if the bottom of one box is
on top of the pallet or at the same height at the top of another box.

When this is finished running, the ups and downs lists of each package
are complete, but all pressures in the elements of those lists are set
to -1.0

The overlap fraction of a box is the fraction of the area of the bottom
of the box that is in contact with the pallet or with other boxes.

The stackOverlapFraction includes (1) the boxes that are directly on
the pallet, for which overlap with the pallet is calculated and (2)
the boxes that are on other boxes, for which the overlap with other
boxes is calculated.

The stackAverageConnects includes (1) the boxes that are directly on
the pallet, for which the number of connections is 1, and (2) the
boxes that are on other boxes, for which the number of such other
boxes is counted.

The way the computation is being done, the first layer of a stack always
has a stackAverageConnects value of 1, and the more layers there are, the
larger the the stackAverageConnects tends to get.

An alternate method of calculating stackAverageConnects might be to
disregard boxes directly on the pallet. This would eliminate the effect
described in the preceding paragraph.

*/

void PackPallet::findOverlaps( /* ARGUMENTS                             */
 double tolerance,             /* tolerance for determining same height */
 double minOverlapForError)    /* minimum overlap that is not an error  */
{
  unsigned int i;             // counter 1 for packages stacked on a pallet
  unsigned int j;             // counter 2 for packages stacked on a pallet
  double areaJ;               // area of packages[j] touching packages[i]
  double areaI;               // total area of packI touching pallet or box
  Package * packI;            // pointer to package[i]
  Package * packJ;            // pointer to packages[j]
  int totalOverlapErrors = 0; // total number of overlap errors in file.
  int totalLoadingErrors = 0; // total number of loading order errors in file.
  double totalOverlap = 0.0;  // sum of overlap fractions
  int totalConnections = 0;   // total connections
  
  for (i = 0; i < packages.size(); i++)
    {
      packI = &(packages[i]);
      packI->loadingErrors = 0;
      if ((packI->minZ >= -tolerance) && (packI->minZ <= tolerance))
	{
	  packI->findOverlapPallet(dimensions.length,
				   dimensions.width, &areaI);
	  if (areaI > 0.0)
	    totalConnections += 1;
	}
      else
	{
	  areaI = 0;
	  for (j = 0; j < packages.size(); j++)
	    {
	      packJ = &(packages[j]);
	      if (fabs(packI->minZ - packJ->maxZ) <= tolerance)
		{
		  areaJ = packI->findOverlapBox(packJ);
		  if (areaJ > 0.0)
		    {
		      packI->downs.push_back(new AreaData(packJ, areaJ));
		      packJ->ups.push_back(new AreaData(packI, areaJ));
		      areaI += areaJ;
		      if (j > i)
			{
			  (packI->loadingErrors)++;
			  totalLoadingErrors++;
			}
		    }
		}
	    }
	  totalConnections += packI->downs.size();
	}
      packI->stackLoadingErrors = totalLoadingErrors;
      packI->overlapFraction = (areaI / packI->area);
      if (packI->overlapFraction < minOverlapForError)
	totalOverlapErrors++;
      packI->stackOverlapErrors = totalOverlapErrors;
      totalOverlap += packI->overlapFraction;
      packI->stackOverlapFraction = (double)(totalOverlap / (i+1));
      packI->stackAverageConnects = ((double)totalConnections / (i+1));
    }
}
  
/********************************************************************/

/* PackPallet::findPressureMetrics

Returned Value: none

Called By: PalletViewer::init

This finds the maximum pressure exerted on each box and the sequence
number of the box on top that exerts that pressure. It also records
the total number of pressure errors for the stack through the box.

The units for maxPressureOnTop in robustness are g/mm*mm, while the
other units are Kg/m*m, so a conversion is done for maxPressureOnTop.

*/

void PackPallet::findPressureMetrics() /* NO ARGUMENTS */
{
  int totalPressureErrors = 0;         // total pressure errors
  Package * pack;                      // pointer to packages[i]
  std::list<AreaData*>::iterator iter; // iterator for ups list
  unsigned int i;                      // counter for packages on a pallet

  for (i = 0; i < packages.size(); i++)
    {
      pack = &(packages[i]);
      pack->maxBoxPressure = 0.0;
      for (iter = pack->ups.begin(); iter != pack->ups.end(); ++iter)
	{
	  if ((*iter)->pressure > pack->maxBoxPressure)
	    {
	      pack->maxBoxPressure = (*iter)->pressure;
	      pack->maxBoxSeqNo = (*iter)->pack->pack_sequence;
	    }
	}
      if ((pack->article.robustness.maxPressureOnTop >= 0.0) &&
	  (pack->maxBoxPressure >
	   (1000.0 * pack->article.robustness.maxPressureOnTop)))
	totalPressureErrors++;
      pack->stackPressureErrors = totalPressureErrors;
    }
}

/********************************************************************/

/* PackPallet::findPressures

Returned Value: none

Called By: PalletViewer::init

This finds the loadedWeight of each package (which is its weight plus
the force exerted by packages on top). It also finds the ups and downs
of each package. Ups and downs are both AreaDatas, which consist of
(i) a pointer to a package, (ii) the area of the overlap with that package,
and (iii) the pressure for that area.

In the inner loop, a package is processed if (i) it has not already
been processed and (ii) it has no ups or all of its ups have pressures
greater than 0. A package has already been processed if and only if
its loaded weight is greater than 0.

The area is in square millimeters, so it needs to be converted to square
meters for finding pressure in Kg/m*m.

*/

void PackPallet::findPressures() /* NO ARGUMENTS */
{
  bool progress = true; // indicates whether inner loop made progress
  int processed = 0;    // number of packages processed.
  unsigned int i;       // counter for packages stacked on a pallet
  Package * packI;      // pointer to packages[i]
  Package * packJ;      // pointer to another package
  std::list<AreaData*>::iterator iter; // list iterator for packI
  std::list<AreaData*>::iterator ator; // list iterator for packJ
  double totalArea;     // total area of downs of packages[i] in square meters

  for (i = 0; i < packages.size(); i++) // init loadedWeight for all packages
    packages[i].loadedWeight = -1.0;
  while (progress)
    {
      progress = false;
      for (i = 0; i < packages.size(); i++)
	{
	  packI = &(packages[i]);
	  if (packI->loadedWeight > 0)
	    continue;
	  for (iter = packI->ups.begin(); iter != packI->ups.end(); ++iter)
	    if ((*iter)->pressure < 0)
	      break;
	  if (iter != packI->ups.end())
	    continue;
	  progress = true;
	  processed++;
	  totalArea = 0;
	  packI->loadedWeight = (packI->article.weight / 1000.0);
	  for (iter = packI->ups.begin(); iter != packI->ups.end(); ++iter)
	    {
	      packI->loadedWeight +=
		(((*iter)->pressure * (*iter)->area) / 1000000.0);
	    }
	  for (iter = packI->downs.begin(); iter != packI->downs.end(); ++iter)
	    {
	      totalArea += ((*iter)->area / 1000000.0);
	    }
	  for (iter = packI->downs.begin(); iter != packI->downs.end(); ++iter)
	    {
	      (*iter)->pressure = (packI->loadedWeight / totalArea);
	      packJ = (*iter)->pack;
	      for (ator = packJ->ups.begin(); ator != packJ->ups.end(); ++ator)
		{
		  if ((*ator)->pack == packI)
		    {
		      (*ator)->pressure = (*iter)->pressure;
		      break;
		    }
		}
	    }
	}
    }
  if (processed != (int)packages.size())
    {
      fprintf(stderr, "Error in findPressures\n");
    }
}

/********************************************************************/

/* PackPallet::findSequenceErrors

Returned Value: none

Called By: PalletViewer::init

This checks that that the sequence number of the first package on the
as-planned pallet is 1 and that the sequence number of each other package
is one larger than the index of the previous package.

Sequence numbers in error are not corrected here because the as-built file
identifies packages using the sequence numbers in the as-planned file.

If a sequence number is smaller than the previous sequence number, there
may be several duplicate sequence numbers. For example 1 2 3 4 5 2 3 4 5.
Not all duplicates will be detected here. In the example, only the second
occurrence of 2 will be flagged as an error.

*/

void PackPallet::findSequenceErrors() /* NO ARGUMENTS */
{
  unsigned int i;                  // counter for packages stacked on a pallet
  unsigned int sequenceErrors = 0; // total sequence errors for current stack
  Package * pack;                  // pointer to packages[i]
  unsigned int lastNumber = 0;     // sequence number of previous package

  for (i = 0; i < packages.size(); i++)
    {
      pack = &(packages[i]);
      if (pack->pack_sequence != (lastNumber+1))
	{
	  pack->sequenceError = 1;
	  sequenceErrors++;
	}
      else
	pack->sequenceError = 0;
      pack->stackSequenceErrors = sequenceErrors;
      lastNumber = pack->pack_sequence;
    }
}

/********************************************************************/

/* PackPallet::findTotalErrors

Returned Value: none

Called By: PalletViewer::init

This finds and sets the total number of errors for a stack, up to and
including the current package.

*/

void PackPallet::findTotalErrors() /* NO ARGUMENTS */
{
  unsigned int i;         // counter for packages stacked on a pallet
  Package * pack;         // package being tested

  for (i = 0; i < packages.size(); i++)
    {
      pack = &(packages[i]);
      pack->stackTotalErrors = 
	(pack->stackOrderErrors +
	 pack->stackOverhangErrors +
	 pack->stackOverlapErrors +
	 pack->stackInters +
	 pack->stackLoadingErrors +
	 pack->stackPressureErrors +
	 pack->stackSequenceErrors +
	 pack->stackWeightErrors +
	 pack->stackHeightErrors);
    }
}

/********************************************************************/

/* PackPallet::findVolumes

Returned Value: none

Called By: PalletViewer::init

This finds and sets the stackStorageVolume, stackBoxVolume, and
stackDensity for each box on the pallet.

The stackStorageVolume is the volume of a virtual box whose height is
the height of the stack (not including the pallet) and whose base
length and width are those of the pallet extended by any overhang
outside the pallet. The stackStorageVolume represents the volume needed to
store the pallet in a warehouse, minus the volume of the pallet itself.

*/

void PackPallet::findVolumes() /* NO ARGUMENTS */
{
  double baseArea;           // area of base of virtual box in square meters
  double baseLength;         // length in millimeters of virtual box base
  double baseWidth;          // width in millimeters of virtual box base
  double totalBoxVolume = 0; // total volume of boxes on stack in cubic meters
  Article * art;             // Article in pack
  unsigned int i;            // counter for packages stacked on a pallet
  Package * pack;            // pointer to packages[i]

  for (i = 0; i < packages.size(); i++)
    {
      pack = &(packages[i]);
      baseLength = (dimensions.length +
		    ((pack->stackXPlusOver > 0) ? pack->stackXPlusOver : 0) +
		    ((pack->stackXMinusOver > 0) ? pack->stackXMinusOver : 0));
      baseWidth = (dimensions.width +
		   ((pack->stackYPlusOver > 0) ? pack->stackYPlusOver : 0) +
		   ((pack->stackYMinusOver > 0) ? pack->stackYMinusOver : 0));
      baseArea = ((baseLength * baseWidth) / 1000000.0);
      pack->stackStorageVolume = (baseArea * pack->stackHeight);
      art = &(pack->article);
      totalBoxVolume += ((art->height / 1000.0) *
			 (art->width / 1000.0) * (art->length / 1000.0));
      pack->stackBoxVolume = totalBoxVolume;
      pack->stackDensity = (pack->stackBoxVolume / pack->stackStorageVolume);
    }
}

/********************************************************************/

/* PackPallet::parsePackPallet

Returned Value: none

Called By: PackList::parsePackList

*/

void PackPallet::parsePackPallet(  /* ARGUMENTS                         */
 std::string packPalletString)     /* string describing a packed pallet */
{
  std::string packageString;
  Package pack;

  packages.clear();
  pallet_number = atoi(xml_parse_tag(packPalletString, "PalletNumber").c_str());
  brutto_weight = atoi(xml_parse_tag(packPalletString, "BruttoWeight").c_str());
  number_of_packages =
    atoi(xml_parse_tag(packPalletString, "NumberOfPackages").c_str());
  description = xml_parse_tag(packPalletString, "Description");
  dimensions.parseDimensions(xml_parse_tag(packPalletString, "Dimensions"));
  overhangs.parseOverhang(xml_parse_tag(packPalletString, "Overhang"));
  while(1)
    {
      packageString = xml_parse_tag(packPalletString, "Package");
      if(strlen(packageString.c_str()) == 0)
	break;
      pack.parsePackage(packageString);
      packages.push_back(pack);
      xml_parse_remove_first_tag(&packPalletString, "Package");
    }
}

/********************************************************************/

Point::Point() {}

/********************************************************************/

Point::~Point() {}

/********************************************************************/

/* Point::parsePoint

Returned Value: none

Called By: Package::parsePackage

*/

void Point::parsePoint( /* ARGUMENTS       */
 std::string text)      /* string to parse */
{
  x = atoi(xml_parse_tag(text, "X").c_str());
  y = atoi(xml_parse_tag(text, "Y").c_str());
  z = atoi(xml_parse_tag(text, "Z").c_str());
}

/********************************************************************/

SecurityMargins::SecurityMargins() {}

/********************************************************************/

SecurityMargins::~SecurityMargins() {}

/********************************************************************/

/* SecurityMargins::parseSecurityMargins

Returned Value: none

Called By: none

Currently, although SecurityMargins are not optional in the XML schema,
they are not included in most data files. Hence, they are treated as
optional in the C++ classes and in parsing. 

*/

void SecurityMargins::parseSecurityMargins( /* ARGUMENTS       */
 std::string text)                          /* string to parse */
{
  if (text.size())
    {
      length = atoi(xml_parse_tag(text, "Length").c_str());
      width = atoi(xml_parse_tag(text, "Width").c_str());
      exists = true;
    }
  else
    exists = false;
}

/********************************************************************/

