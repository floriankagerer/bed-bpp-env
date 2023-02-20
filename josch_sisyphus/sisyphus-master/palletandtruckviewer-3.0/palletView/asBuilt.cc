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
  \file asBuilt.cc

  \brief Read and stores as-built information for a mixed pallet.
  \code CVS Status:
  $Author: dr_steveb $
  $Revision: 1.10 $
  $Date: 2011/02/23 16:26:25 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/

/********************************************************************/

#ifdef MOASTSTATIC
#include "asBuilt.h"
#else
#include "asBuilt.h"
#endif
#include "response.h"
#include <stdlib.h>
#include <sstream>
#include <fstream>
#include <string>

/********************************************************************/

/* AsBuilt::findFileErrors

Returned Value: none

Called By: PalletViewer::init (in palletViewer.cc)

This:
1. goes through the as-planned packages and sets the built flag in each
   as-planned package to 0.
2. goes through the as-built packages and checks whether the sequence
   number of each package, is larger than that of the previous package.
   If an as-built package is found whose sequence number is not larger
   than that of the previous package, the sequenceError of the package
   is set to 1 and sequenceErrors is increased by 1. Otherwise,
   the sequenceError of the package is set to 0. In any case, the
   stackSequenceErrors of the package is set to sequenceErrors.
3. goes through the as-built packages a second time and checks whether
   each package, pack, has the same sequence number as another as-built
   package earlier in the packages. If so, since that amounts to putting
   the same package in two different places, duplicateError of pack is
   set to 1, and duplicateErrors is increased by 1. If not, duplicateError
   of pack is set to 0. In either case, stackDuplicateErrors of pack is
   set to duplicateErrors.
4. goes through the as-built packages a third time, and for each one that
   has duplicateError set to 0, calls findFileErrors. That function will
   set the built flag of the corresponding as-planned package to 1 if
   there is any corresponding as-planned package.
5. goes through the as-planned packages and sets missingPlanned to the
   number of as-planned packages that have their built flag set to 0.

*/

void AsBuilt::findFileErrors( /* ARGUMENTS                                  */
 PackPallet * pal,            /* as-planned pallet                          */
 int * missingPlanned)        /* number of planned packages not on as-built */
{
  int i;                   // index for as-planned packages or as-built packages
  int j;                   // another index for BuiltPackages
  int sequenceErrors = 0;  // number of sequence errors
  int duplicateErrors = 0; // number of duplicate sequence errors
  int extraErrors = 0;     // number of extra box errors
  int idErrors = 0;        // number of box id errors
  unsigned int lastSequence = 0;

  for (i = 0; i < (int)pal->packages.size(); i++)
    {
      pal->packages[i].built = 0;
    }
  for (i = 0; i < (int)packages.size(); i++)
    {
      if (packages[i].sequence <= lastSequence)
	{
	  packages[i].sequenceError = 1;
	  sequenceErrors++;
	}
      else
	packages[i].sequenceError = 0;
      packages[i].stackSequenceErrors = sequenceErrors;
      lastSequence = packages[i].sequence;
    }
  for (i = 0; i < (int)packages.size(); i++)
    {
      for (j = 0; j < i; j++)
	{
	  if (packages[i].sequence == packages[j].sequence)
	    break;
	}
      if (j == i) // no duplicate
	packages[i].duplicateError = 0;
      else  // duplicate
	{
	  packages[i].duplicateError = 1;
	  duplicateErrors++;
	}
      packages[i].stackDuplicateErrors = duplicateErrors;
    }
  for (i = 0; i < (int)packages.size(); i++)
    {
      if (!packages[i].duplicateError)
	packages[i].findFileErrors(pal, &extraErrors, &idErrors);
    }
  for (i = 0; i < (int)pal->packages.size(); i++)
    {
      if (!pal->packages[i].built)
	(*missingPlanned)++;
    }
}

/********************************************************************/

/* AsBuilt::findPositionErrors

Returned Value: none

Called By: PalletViewer::init (in palletViewer.cc)

This finds the position error for each package that does not have
a duplicate sequence number and corresponds to a package in the
packlist. It also finds three statistics for the set of such packages.

*/

void AsBuilt::findPositionErrors( /* ARGUMENTS         */
 PackPallet * pal)                /* as-planned pallet */
{
  unsigned int i;                 // index for packages
  unsigned int k;                 // number of packages to use
  double maxPositionError = 0;    // current maximum position error
  double totalPositionError = 0;  // current total position error
  double totalErrorSquared = 0;   // current total of squares of position error
  double positionErrorVariance=0; // current position error variance

  for (i = 0, k = 0; i < packages.size(); i++)
    {
      if ((!packages[i].duplicateError) && (!packages[i].extraError))
	{
	  k++;
	  packages[i].findPositionErrors(pal, k, &maxPositionError,
					 &totalPositionError,
					 &totalErrorSquared,
					 &positionErrorVariance);
	}
      else
	{
	  packages[i].positionError = -1.0;
	  packages[i].stackMaxPositionError = maxPositionError;
	  packages[i].stackPositionErrorMean =
	    (k ? (totalPositionError / k) : 0.0);
	  packages[i].stackPositionErrorVariance = positionErrorVariance;
	}
    }
}

/********************************************************************/

/* AsBuilt::parseLog

Returned Value: none

Called By: AsBuilt::readAsBuilt

This parses an as-built log file and builds the vector of packages
in the AsBuilt being built. Each line of the as-built log file has
information describing one package.

*/

void AsBuilt::parseLog(  /* ARGUMENTS                       */
 std::ifstream &ifs)     /* as-built log file to read from  */
{
  char line[255];
  BuiltPackage pack;
  
  ifs.getline(line, 255);
  while (ifs.getline(line,255))
    {
      pack.parseLogLine(line);
      packages.push_back(pack);
    }
  printf("AsBuilt Read.\n");
}

/********************************************************************/

/* AsBuilt::parseXml

Returned Value: none

Called By: AsBuilt::readAsBuilt

This parses an XML data file corresponding to the AsBuilt.xsd XML
schema as follows. Every named string is a std::string.

1. Read the entire file into the buffer.
2. Convert the buffer into the asBuiltXmlString.
3. Put the substring of the asBuiltXmlString delimited by the LoadedPallet
   tag into the palletString.
4. Put the substring of the palletString delimited by the PalletIndex tag
   into the palletString and read the number from the palletString into the
   palletNumber of the AsBuilt being built.
5. Repeatedly:
   a. Read the first substring of the palletString delimited by
      a PackagePlacement tag into the packageString.
   b. Call parseXmlPackage to parse the packageString, and add the
      parsed package to the packages vector of the AsBuilt being built.
   c. Delete the substring that was just parsed from the palletString.

*/

void AsBuilt::parseXml( /* ARGUMENTS                            */
 std::ifstream & ifs,   /* as-built XML file to read from       */
 int bufferLength)      /* length of buffer needed to read file */
{
  std::string asBuiltXmlString;
  char * buffer;
  std::string palletString;
  std::string packageString;
  unsigned int palletNumber;
  BuiltPackage pack;
  
  packages.clear();
  buffer = (char*)malloc(bufferLength + 1);
  ifs.read(buffer, bufferLength);
  asBuiltXmlString = buffer;
  palletString = xml_parse_tag(asBuiltXmlString, "LoadedPallet");
  if (palletString.size() == 0)
    {
      fprintf(stderr, "cannot find LoadedPallet in as-built XML\n");
      exit(1);
    }
  palletNumber = atoi(xml_parse_tag(palletString, "PalletIndex").c_str());
  while (1)
    {
      packageString = xml_parse_tag(palletString, "PackagePlacement");
      if (packageString.size() == 0)
	break;
      pack.parseXmlPackage(packageString, palletNumber);
      packages.push_back(pack);
      xml_parse_remove_first_tag(&palletString, "PackagePlacement");
    }
  printf("AsBuilt Read.\n");
  free(buffer);
}

/********************************************************************/

/* AsBuilt::readAsBuilt

Returned Value: AsBuilt
  This builds an AsBuilt from an as-built file.

Called By: PalletViewer::init (in palletViewer.cc)

If the filename has a .log suffix, this calls parseLog to parse the
file. If the filename has a .xml suffix, this calls parseLXml to parse the
file. If the filename has neither suffix, this prints an error message
and exits.

*/

void AsBuilt::readAsBuilt( /* ARGUMENTS              */
 const char * filename)    /* name of as-built file  */
{
  std::ifstream ifs(filename);
  int bufferLength;
  int n;
  
  if(!ifs.is_open())
    {
      fprintf(stderr, "%s file not found.\nExiting.\n", filename);
      exit(1);
    }
  
  n = (strlen(filename) - 4);
  if (strncmp(filename+n, ".log", 4) == 0)
    {
      parseLog(ifs);
    }
  else if (strncmp(filename+n, ".xml", 4) == 0)
    {
      bufferLength = xml_parser_get_buffer_length(filename);
      parseXml(ifs, bufferLength);
    }
  else
    {
      fprintf(stderr, "as-built file name must end in .xml or .log\n");
      exit(1);
    }
}

/********************************************************************/

/* BuiltPackage::findFileErrors

Returned Value: none

Called By: AsBuilt::findFileErrors

This first checks that a package, pack, with same sequence number as this
BuiltPackage exists on the pallet.

If not, this sets extraError to 1, increases extraErrors by 1, sets idError
to 0, and constructs a dummy article for this BuiltPackage. The dummy
article is given a grey color.

If so, this sets extraError to 0, sets the article in this
BuiltPackage to the article in pack, sets the color of this
BuiltPackage to the color of pack, and sets the built flag of pack to
1. Then it checks whether the id of this BuiltPackage is the same as
the id of pack. If so, this sets idError to 0 and sets the color of
the as-built package to the color of the as-planned package.  If not,
this sets idError to 1, increases idErrors by 1, changes the id of
this BuiltPackage to the id of pack, and sets the color to gray.

In any case, this sets stackExtraErrors to *extraErrors and sets
stackIdErrors to *idErrors.

It is a bit hard to know how to deal with an as-built package that
has a sequence number that matches an as-planned sequence number
but has an id number that does not match. This is counted as an
id error in the as-built metrics. That's not a problem. But what
should the graphics window show? If the id number is an id number
of one of the as-planned packages, should a package that size be
shown, or should a package the size of the correct one for that
sequence number be shown? Here, a package the size of the correct
one is shown. A graphical indication of an error is provided by
changing the color to gray.

*/

void BuiltPackage::findFileErrors( /* ARGUMENTS                           */
 PackPallet * pal,    /* as-planned pallet                                */
 int * extraErrors,   /* extra box errors for stack, may be reset here    */
 int * idErrors)      /* incorrect id errors for stack, may be reset here */
{
  Package * pack;
  static col greyColor = {0.2f, 0.2f, 0.2f};
  unsigned int i;
  
  for (i = 0; i < pal->packages.size(); i++)
    {
      if (sequence == pal->packages[i].pack_sequence)
	break;
    }
  if (i == pal->packages.size())
    { // corresponding as-planned package not found
      extraError = 1;
      (*extraErrors)++ ;
      idError = 0;
      article.length = 100;
      article.width = 100;
      article.height = 100;
      color = greyColor;
    }
  else
    { // corresponding as-planned package found
      extraError = 0;
      pack = &(pal->packages[i]);
      pack->built = 1;
      article = pack->article;
      if (id == article.id)
	{
	  idError = 0;
	  color = pack->color;
	}
      else
	{ // as-built package has wrong id, so fix it
 	  idError = 1;
	  (*idErrors)++ ;
	  id = article.id;
	  color = greyColor;
	}
    }
  stackExtraErrors = *extraErrors;
  stackIdErrors = *idErrors;
}

/********************************************************************/

/* BuiltPackage::findPositionErrors

Returned Value: none

Called By: AsBuilt::findPositionErrors

This sets the stackPositionErrorMean and the stackPositionErrorVariance.
It also resets the totalPositionError and the totalErrorSquared.

The variance is average of the squares of the differences of individual
values from the mean.

The variance is also equal to the average of the squares minus the
square of the mean. That is used here.

The location point of the as-planned pack is in the middle of the top
of the box, while the location point of this as-built is in the middle
of the box. The Z value of the middle of the as-planned pack is halfway
between its maxZ and minZ.

*/

void BuiltPackage::findPositionErrors( /*  ARGUMENTS                         */
 PackPallet * pal,               /* the as-planned PackPallet                */
 int numberPackages,             /* number of packages on stack              */
 double * maxPositionError,      /* current maximum position error           */
 double * totalPositionError,    /* total of position errors for stack       */
 double * totalErrorSquared,     /* total of squared position errors 4 stack */
 double * positionErrorVariance) /* position error variance for stack        */
{
  Package * pack;
  double dx;
  double dy;
  double dz;
  double errorSquared;

  pack = &(pal->packages[sequence - 1]);
  dx = ((pack->place_position.x / 1000.0) - x);
  dy = ((pack->place_position.y / 1000.0) - y);
  dz = (((pack->maxZ + pack->minZ) / 2000.0) - z);
  errorSquared = ((dx * dx) + (dy * dy) + (dz * dz));
  positionError = sqrt(errorSquared);
  if (positionError > *maxPositionError)
    *maxPositionError = positionError;
  stackMaxPositionError = *maxPositionError;
  *totalPositionError += positionError;
  *totalErrorSquared += errorSquared;
  stackPositionErrorMean = (*totalPositionError / numberPackages);
  *positionErrorVariance = 
    ((*totalErrorSquared  / numberPackages) -
     (stackPositionErrorMean * stackPositionErrorMean));
  stackPositionErrorVariance = *positionErrorVariance;
}

/********************************************************************/

/* BuiltPackage::findSubstring (static)

Returned Value: string
  This returns a substring S of the text string. S starts at the
  character after the one whose index is end. S ends at the first
  comma found in the text string. The end argument is reset to be
  the index of the comma.

Called By: BuiltPackage::parseLogLine

*/

std::string BuiltPackage::findSubstring( /* ARGUMENTS                     */
 const std::string & text, /* string containing substring                 */
 size_t & index)           /* index of character before start, reset here */
{
  std::string searchString(",");
  size_t start = index+1;
  index = text.find(searchString, start);
  if (index == std::string::npos)
    {
      fprintf(stderr, "AsBuilt::findSubstring: unable to find comma in %s\n",
	      text.c_str());
      fprintf(stderr, "Exiting.\n");
      exit(1);
    }
  return text.substr(start, (index - start));
}

/********************************************************************/

/* BuiltPackage::parseDouble (static)

Returned Value: double
  This returns a double whose value is read from the text string.

Called By:  BuiltPackage::parseLogLine

When this is called, index should be the index in the text string of the
character before the start of the double to be read from the string.
The double is expected to be followed by a comma. This constructs a
substring starting with the character after the one indicated by index
and ending with the character before the comma and converts some or all of
the substring into a double.

This resets index to indicate the position in the text string of the comma.

This is not checking that the characters in the substring can represent
a double. It will return zero if not.

This is also not checking that there are no spurious characters between
the end of the double and the comma. For example, if "foo12.5bar,f" is the
string being parsed, and index is set correctly (to 2), this will return
a double whose value is 12.5. It will also reset index to 10.

*/

double BuiltPackage::parseDouble( /* ARGUMENTS                              */
 const std::string & text,        /* string containing number               */
 size_t & index)                  /* index of char before start, reset here */
{
  std::string searchString(",");
  size_t start = index+1;
  index = text.find(searchString, start);
  if( index == std::string::npos )
    {
      fprintf(stderr, "AsBuilt::parseDouble: unable to find comma in %s\n",
	      text.c_str());
      fprintf(stderr, "Exiting.\n");
      exit(1);
    }
  return atof(text.substr(start, index-start).c_str());
}

/********************************************************************/

/* BuiltPackage::parseFirstNumber (static)

Returned Value: unsigned int
  This returns the first integer found in a string that contains digits.
  e.g.,  parseFirstNumber(string("Box12Box13")) will return 12.

Called By:  BuiltPackage::parseLogLine

*/

unsigned int BuiltPackage::parseFirstNumber( /* ARGUMENTS                */
 const std::string & text )                  /* string containing number */
{
  std::string searchString("0123456789");
  size_t found;

  found = text.find_first_of(searchString);
  if( found == std::string::npos )
    {
      fprintf(stderr, "asBuilt::parseFirstNumber: unable to find digit in %s\n",
	      text.c_str());
      fprintf(stderr, "Exiting.\n");
      exit(1);
    }
  return (unsigned)atoi(text.substr(found).c_str());
}

/********************************************************************/

/* BuiltPackage::parseLogLine

Returned Value: none

Called By:  AsBuilt::parseLog

This parses the BuiltPackage described in the logLine.

The logLine argument is a line of the log file. It consists of items divided
by commas. Here is a sample line from a log file.

MFD_Box0,USARBot.WCCrate11343,Pallet1,0.150,0.105,0.150,0.0,0.0,0.0

The alphabetic characters and period after "Bot" are irrelevant because
they are just skipped over. The important thing in each of the first three
items on the line is the number at the end. The numbers represent:
MFD_Box0             -- 0 is the packlist pack_sequence
USARBot.WCCrate11343 -- 11343 is the SKU id
Pallet1              -- 1 is the pallet number

The findSubstring function finds the substring of logLine starting at the
character after the one whose index is index and ending at the first
comma after that. findSubstring resets index to be the index of the comma.

*/

void BuiltPackage::parseLogLine( /* ARGUMENTS                       */
 std::string logLine)            /* one line of the log file        */
{
  size_t index = -1;  // index for logLine
  std::string str;    // utility string for name ending in number
  
  // add a final ',' on the end to allow easy parsing in findSubstring
  logLine.append(",");
  
  // parse sequence (packlist pack_sequence)
  str = findSubstring(logLine, index);
  sequence = parseFirstNumber(str);
  
  // parse SKU id
  str = findSubstring(logLine, index);
  id = parseFirstNumber(str);
  
  // parse pallet number
  str = findSubstring(logLine, index);
  palletNum = parseFirstNumber(str);
  
  // parse x, y, z
  x = parseDouble(logLine, index);
  y = parseDouble(logLine, index);
  z = parseDouble(logLine, index);
  
  // parse roll, pitch, yaw
  roll = parseDouble(logLine, index);
  pitch = parseDouble(logLine, index);
  yaw = parseDouble(logLine, index);
}

/********************************************************************/

/* BuiltPackage::parseXmlPackage

Returned Value: none
  This parses a BuiltPackage from the packageString.

Called By: AsBuilt::parseXml

*/

void BuiltPackage::parseXmlPackage( /* ARGUMENTS                       */
 std::string packageString,         /* string representing one package */
 unsigned int palletNum)            /* pallet number                   */
{
  palletNum = palletNum;
  sequence = atoi(xml_parse_tag(packageString, "PacklistIndex").c_str());
  id = atoi(xml_parse_tag(packageString, "USARBotWCCrateId").c_str());
  x = atof(xml_parse_tag(packageString, "XCoord").c_str());
  y = atof(xml_parse_tag(packageString, "YCoord").c_str());
  z = atof(xml_parse_tag(packageString, "ZCoord").c_str());
  roll = atof(xml_parse_tag(packageString, "Roll").c_str());
  pitch = atof(xml_parse_tag(packageString, "Pitch").c_str());
  yaw = atof(xml_parse_tag(packageString, "Yaw").c_str());
}

/********************************************************************/
