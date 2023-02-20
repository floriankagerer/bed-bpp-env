/*********************************************************************/

#include <stdio.h>             // for fprintf, etc.
#include "xmlSchemaInstance.hh"

/*********************************************************************/

/* class AttributePair

*/

AttributePair::AttributePair() {}

AttributePair::AttributePair(
 char * nameIn,
 char * valIn)
{
  name = nameIn;
  val = valIn;
}

AttributePair::~AttributePair() {}

/*********************************************************************/

/* class SchemaLocation

*/

SchemaLocation::SchemaLocation() {}

SchemaLocation::SchemaLocation(
  char * prefixIn,
  char * locationIn)
{
  prefix = prefixIn;
  location = locationIn;
}

SchemaLocation::~SchemaLocation() {}

void SchemaLocation::printSelf(FILE * outFile)
{
  fprintf(outFile, "  %s:schemaLocation=\"%s\"", prefix, location);
}

/*********************************************************************/

/* class XmlSchemaInstanceBase

*/

XmlSchemaInstanceBase::XmlSchemaInstanceBase() {}

XmlSchemaInstanceBase::~XmlSchemaInstanceBase() {}

void XmlSchemaInstanceBase::doSpaces(int change, FILE * outFile)
{
  static int spaces = 0;
  static int n;

  if (change)
    spaces += change;
  else
    {
      for (n = 0; n < spaces; n++)
        fputc(' ', outFile);
    }
}

/*********************************************************************/

/* class XmlVersion

*/

XmlVersion::XmlVersion() {}

XmlVersion::XmlVersion(bool hasEncodingIn)
{
  hasEncoding = hasEncodingIn;
}

XmlVersion::~XmlVersion() {}

void XmlVersion::printSelf(FILE * outFile)
{
  if (hasEncoding)
    fprintf(outFile, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
  else
    fprintf(outFile, "<?xml version=\"1.0\"?>\n");
}

/*********************************************************************/

