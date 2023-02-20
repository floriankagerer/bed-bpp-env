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
  \file asBuilt.h

  \brief Class structure to hold as built information for a mixed pallet.
  \code CVS Status:
  $Author: tomrkramer $
  $Revision: 1.6 $
  $Date: 2010/12/04 15:10:06 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/

/*

The as-built file might be checked against the order file, the packlist
file, or both. The approach taken here is to check only against the
packlist file. 

It will be possible to tell if a box in the as-built stack is not in
the order, however, because the color of an as-built box is taken from
the color of the corresponding box in the packlist file, and that is
dark grey if the box was not in the order.

*/

/***********************************************************************/

#ifndef ASBUILT_HH
#define ASBUILT_HH

#include <vector>
#include <string.h>
#include "packlist.h"
#include "response.h"

/***********************************************************************/

/* class BuiltPackage

The location point of a BuiltPackage is the point in the middle of the
package (it used to be in the middle of the top of the package). The
coordinate system of a package has its origin at the location point,
its X axis pointing along the length of the package, and its Z axis
pointing along the height of the package. The coordinate system of the
package is located in the pallet coordinate system by the
x,y,z,roll,pitch,yaw given here.

The first 10 attributes are set when the as-built file is parsed.
The other attributes are used to hold metrics values and are calculated
when when the find... functions that return void are called.

The attributes whose names start with "stack" hold values for the
stack up to and including this BuiltPackage.

In the case of a package with a duplicateError, it will not be
processed further, since a duplicateError indicates putting the same
package in two different places

*/

class BuiltPackage 
{
 public:
  BuiltPackage() {}
  ~BuiltPackage() {}
  void findFileErrors(PackPallet * pal, int * extraErrors, int * idErrors);
  void findPositionErrors(PackPallet * pal, int numberPackages,
			  double * maxPositionError,
			  double * totalPositionError,
			  double * totalErrorSquared,
			  double * positionErrorVariance);
  static std::string findSubstring(const std::string & data, size_t & index);
  static double parseDouble(const std::string & data, size_t & index);
  static unsigned int parseFirstNumber(const std::string & data);
  void parseLogLine(std::string logLine);
  void parseXmlPackage(std::string packageString, unsigned int palletNum);

  Article article;         // Article data for package
  unsigned int id;         // SKU id number (matches id number in packlist)
  unsigned int palletNum;  // pallet number
  double pitch;            // pitch relative to pallet coords
  double roll;             // roll relative to pallet coords
  unsigned int sequence;   // pack_sequence of package in packlist
  double x;                // pallet X coordinate of location point
  double y;                // pallet Y coordinate of location point
  double yaw;              // yaw relative to pallet coords
  double z;                // pallet Z coordinate of location point

  col color;                     // color of box
  int duplicateError;            // 1=processed box has same sequence number
  int extraError;                // 1=sequence number not in as-planned, 0=OK
  int idError;                   // 1=box has wrong id for sequence, 0=OK
  double positionError;          // distance of location point from planned
  int sequenceError;             // 1=sequence number not larger than last, 0=OK
  int stackDuplicateErrors;      // number of duplicate errors for stack
  int stackExtraErrors;          // number of extra box errors for stack
  int stackIdErrors;             // number of id errors for stack
  double stackMaxPositionError;  // maximum position error for stack
  double stackPositionErrorMean; // average position error for stack
  double stackPositionErrorVariance; // variance of position error for stack
  int stackSequenceErrors;       // number of sequence errors for stack
};

/***********************************************************************/

/* class AsBuilt

*/

class AsBuilt
{
 public:
  AsBuilt() {}
  ~AsBuilt() {}
  void findFileErrors(PackPallet * pal, int * missingPlanned);
  void findPositionErrors(PackPallet * pal);
  void parseLog(std::ifstream & ifs);
  void parseXml(std::ifstream & ifs, int bufferLength);
  void readAsBuilt(const char * filename);

  unsigned int palletID;
  std::string description;
  std::vector <BuiltPackage> packages;
};

/***********************************************************************/

#endif // ASBUILT_HH
