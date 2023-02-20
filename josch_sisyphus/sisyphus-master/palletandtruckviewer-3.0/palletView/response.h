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
  \file response.h

  \brief Class structure to parse planned mixed pallet and hold metrics.
  \code CVS Status:
  $Author: tomrkramer $
  $Revision: 1.14 $
  $Date: 2011/02/14 16:09:57 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/

/*
Uses XML data files corresponding to XML schemas:
Article.xsd
Error.xsd
OffLineMessage.xsd
OffLineResponse.xsd
PalletInit.xsd
Point.xsd
Restrictions.xsd

The parsing functions here cannot be made efficient because two classes
(Packlist and PackPallet) use vectors of class instances, and there
is no way to build them without copying large structures. It would be
more efficient to make the elements of the vectors be pointers to
class instances. That would require changing a lot of code.

*/

#ifndef RESPONSE_HH
#define RESPONSE_HH

#include "packlist.h"
#include <math.h>
#include <list>

class AreaData;
class Dimensions;
class Overhang;
class Package;
class PackList;
class PackPallet;
class Point;
class SecurityMargins;
struct col {float r, g, b; };

/********************************************************************/

/* Dimensions

This is data for a pallet. The length goes in the X-direction of the
coordinate system of the pallet, the width in the Y-direction.

"PalletDimensions" would be a better name for this class.

The max_load_weight is an assigned property of the pallet, presumably
less than the load-bearing capacity of the pallet and possibly much
less. It is not the maximum allowed weight of a loaded pallet (which
would include the weight of the pallet); that is probably more
important, but it is a different thing.

The max_load_height is an also an assigned property of the pallet. It is
probably much less important than the maximum allowed height of the
loaded pallet (which would include the height of the pallet), but
that is a different thing.

*/

class Dimensions {
 public:
  Dimensions();
  ~Dimensions();
  void parseDimensions(std::string text);

  unsigned int length;           // length in millimeters
  unsigned int width;            // width in millimeters
  unsigned int height;           // height in millimeters (new)
  unsigned int weight;           // weight of the empty pallet in grams (new)
  unsigned int max_load_weight;  // maximum weight of load in grams
  unsigned int max_load_height;  // maximum height of load in millimeters
};

/********************************************************************/

/* Overhang

This is data for a pallet. The length goes in the X-direction of the
coordinate system of the pallet, the width in the Y-direction.

"MaxOverhang" would be a better name for this class

*/

class Overhang
{
 public:
  Overhang();
  ~Overhang();
  void parseOverhang(std::string text);

  unsigned int length; // maximum allowed overhang in X direction in millimeters
  unsigned int width;  // maximum allowed overhang in X direction in millimeters
};

/********************************************************************/

/* Point

A Point is defined by its X, Y, and Z coordinates, which are given
in millimeters in the coordinate system of the pallet. Z is constrained
to be non-negative, so only Points above the pallet can be represented.

*/

class Point {
 public:
  Point();
  ~Point();
  void parsePoint(std::string text);

  int x;
  int y;
  unsigned int z;
};

/********************************************************************/

/* Package

This is really a whole set of data about a box (or something shaped
like a box). Two attributes (article and barcode) together identify
and describe the box. The rest of the attributes are parameters for
placing the box on a stack of boxes on a pallet and for calculating
metrics for the stack.

The first 12 attributes (through stack_height_before) are those given
as elements of the Package element in the XML schema
OffLineResponse.xsd (but the names are reformatted). The remaining
attributes are either metrics for the package or data specific to the
package that is used in calculating metrics. The first 12 attributes
get parsed from the XML file. The rest are calculated.

Many of the values are doubles rather than unsigned ints. This is because
if the length or width of a box is an odd number, half of that is not
an integer.

Point locations for approach points are in the coordinate system of
the pallet. The units are millimeters.

The place_position and the approach points are located in the middle
of the top of the box. They are given in pallet coordinates.

The approach points are to be used as intermediate points in moving
the box.

If the bottom of the box is on the pallet, then overlapFraction is the
fraction of the area of the bottom of the box that is in contact
with the pallet.  Otherwise, the overlapFraction is the fraction of the
area of the bottom of the box that is in contact with another box.

Boxes B1 and B2 are judged to be in contact at the top of B1 and
bottom of B2 if and only if (1) the Z-values of the top of B1 and the
bottom of B2 differ by less than 0.1 millimeter and (2) some part of
the bottom of B2 is above some part of the top of B1.

The following four attributes modeled here are required in the
OffLineResponse.xsd file but do not appear in any of the sample XML
files (the sample files do not conform). Currently, their values are
not used anywhere.
  incoming_sequence
  orderlineno
  parent_layer
  stack_height_before

The data for a Package includes a lot of attributes for the stack made by
this box and all boxes put on the stack before it. The names of such
attributes all start with "stack".

The total errors of various sorts for the stack are recorded here,
but the corresponding errors for the Package itself are not. Those are
recalculated on the fly (which is easy for one Package) when the metrics
are printed.

*/

class Package {
 public:
  Package();
  ~Package();
  
  void findBoundaries();               // finds min and max
  double findOverlapBox(Package * p);  // finds overlap area of this with box p
  void findOverlapPallet(unsigned int length,  // finds overlap with pallet
			 unsigned int width, double * areaI);
  void findOverhangs(double length, double width,
		     double maxOkXHang, double maxOkYHang, int * errors,
		     double * xPlusMax, double * xMinusMax,
		     double * yPlusMax, double * yMinusMax, double tolerance);
                                       // finds overhangs with pallet
  void parsePackage(std::string text); // parse Package from string
  void updateCog(double * momentX, double * momentY, double * momentZ,
		 double halfLength, double halfWidth, double * stackWeightIn,
		 double * stackHeightIn, double MaxWeight, double maxHeight);
                                       // updates COG to include this box
                                     
  unsigned int pack_sequence;       // number of boxes placed earlier, plus 1
  unsigned int incoming_sequence;   // parsed if present, not used
  unsigned int orderlineno;         // parsed if present, not used
  unsigned int parent_layer;        // parsed if present, not used
  Article article;                  // description of box and contents
  Barcode barcode;                  // bar code for specific instance of article
  Point place_position;             // see above
  unsigned int orientation;         // 1 = length parallel to X else parallel Y
  Point approach_point_1;           // first approach point
  Point approach_point_2;           // second approach point
  Point approach_point_3;           // third approach point
  unsigned int stack_height_before; // parsed if present, not used
  
  double area;              // area of top or bottom of box, square mm
  int built;                // 1=found corresponding built package, 0=not
  double cogRelX;           // rel X coord of COG of stack thru this box
  double cogRelY;           // rel Y coord of COG of stack thru this box
  double cogZ;              // Z coord of COG of stack thru this box, m
  struct col color;         // color for this box
  std::list<AreaData*> downs; // area data for boxes this box is resting on
  std::list<int> inters;    // seq nos of boxes intersecting this box, pallet=0
  double loadedWeight;      // box weight plus weight of boxes resting on it, Kg
  int loadingErrors;        // loading errors for this box
  double maxBoxPressure;    // maximum pressure on top of box, Kg/m*m
  int maxBoxSeqNo;          // sequence number of box exerting max pressure
  double maxX;              // maximum X value on placed box, mm
  double maxY;              // maximum Y value on placed box, mm
  double maxZ;              // maximum Z value on placed box, mm
  double minX;              // minimum X value on placed box, mm
  double minY;              // minimum Y value on placed box, mm
  double minZ;              // minimum Z value on placed box, mm
  int overhangErrorX;       // 1 or 2 = overhang error in X direction, else 0
  int overhangErrorY;       // 1 or 2 = overhang error in Y direction, else 0
  int orderError;           // 1 if box not ordered, else 0
  double overlapFraction;   // see above, dimensionless
  int sequenceError;        // 1=pack_sequence number is wrong, 0=OK
  double stackAverageConnects; // stack average connections below thru this box
  double stackBoxVolume;    // total volume of stack  thru this box, cubic m
  double stackDensity;      // stackBoxVolume/stackStorageVolume, dimensionless
  double stackHeight;       // height of stack thru this box, m
  int stackHeightErrors;    // 1 if max allowed height of stack exceeded, else 0
  int stackInters;          // total stack intersections thru this box
  int stackLoadingErrors;   // total stack loading errors thru this box
  int stackOrderErrors;     // total stack order errors thru this box
  int stackOverhangErrors;  // total stack overhang errors thru this box
  int stackOverlapErrors;   // total stack overlap errors thru this box
  double stackOverlapFraction; // stack average overlap fraction thru this box
  int stackPressureErrors;  // total stack pressure errors thru this box
  int stackSequenceErrors;  // total stack sequence errors thru this box
  double stackStorageVolume;// stackHeight times virtual box base area, cubic m
  int stackTotalErrors;     // total errors thru this box
  double stackWeight;       // weight of stack thru this box, Kg
  int stackWeightErrors;    // 1 if max load allowed on pallet exceeded, else 0
  double stackXMinusOver;   // stack -X overhang of pallet thru this box, mm
  double stackXPlusOver;    // stack +X overhang of pallet thru this box, mm
  double stackYMinusOver;   // stack -Y overhang of pallet thru this box, mm
  double stackYPlusOver;    // stack +Y overhang of pallet thru this box, mm
  std::list<AreaData*> ups; // area data for boxes resting on this box
  double xMinusOver;        // box overhang of pallet in -X direction, mm
  double xPlusOver;         // box overhang of pallet in +X direction, mm
  double yMinusOver;        // box overhang of pallet in -Y direction, mm
  double yPlusOver;         // box overhang of pallet in +Y direction, mm  
};

/********************************************************************/

/* AreaData

An AreaData is triple consisting of a pointer to a Package, an area in
square meters, and a pressure in Kg per square meter. 

*/

class AreaData {
 public:
  AreaData();
  AreaData(Package * packIn, double areaIn);
  ~AreaData();

  Package * pack;
  double area;
  double pressure;
};

/********************************************************************/

/* PackList

A PackList represents a set of packed pallets.

*/

class PackList {
 public:
  PackList();
  ~PackList();
  void parsePackList(std::string packlistString);
  static PackList read_response(const char * filename);

  unsigned int order_id;
  std::vector<PackPallet> packedPallets;
};

/********************************************************************/

/* SecurityMargins

This is data for a pallet. The length goes in the X-direction of the
coordinate system of the pallet, the width in the Y-direction.

"MinBoxSpacing" would be a better name for this class.

*/

class SecurityMargins
{
 public:
  SecurityMargins();
  ~SecurityMargins();
  void parseSecurityMargins(std::string text);

  unsigned int length; // minimum allowed space between boxes in X direction, mm
  unsigned int width;  // minimum allowed space between boxes in Y direction, mm
  bool exists;         // true=length and width values are meaningful, false=not
};

/********************************************************************/

/* PackPallet

A PackPallet represents a single packed pallet.

findIntersections finds intersections of each box with the pallet and
with boxes previously put on the stack.

*/

class PackPallet {
 public:
  PackPallet();
  ~PackPallet();
  void findCogs();
  void findIntersections(double tolerance);
  void findOverhangs(double tolerance);
  void findOverlaps(double tolerance, double minOverlapForError);
  void findPressures();
  void findPressureMetrics();
  void findSequenceErrors();
  void findTotalErrors();
  void findVolumes();
  void parsePackPallet(std::string packPalletString);

  unsigned int pallet_number;
  unsigned int brutto_weight;
  unsigned int number_of_packages; // parsed from file
  std::string description;
  Dimensions dimensions;
  Overhang overhangs;
  SecurityMargins securityMargins;
  std::vector<Package> packages;
};

/********************************************************************/

#endif // RESPONSE_HH
