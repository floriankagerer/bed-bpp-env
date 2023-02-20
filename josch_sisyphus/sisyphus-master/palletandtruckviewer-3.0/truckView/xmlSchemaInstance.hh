/*********************************************************************/

#ifndef XMLSCHEMAINSTANCE_HH
#define XMLSCHEMAINSTANCE_HH

#include <stdio.h>

/*********************************************************************/

class AttributePair;
class XmlInstanceBase;
class XmlVersion;

/*********************************************************************/

class AttributePair
{
public:
  AttributePair();
  AttributePair(
    char * nameIn,
    char * valIn);
  ~AttributePair();

  char * name;
  char * val;
};

/*********************************************************************/

class XmlSchemaInstanceBase
{
public:
  XmlSchemaInstanceBase();
  virtual ~XmlSchemaInstanceBase();
  virtual void printSelf(FILE * outFile) = 0;
  static void doSpaces(int change, FILE * outFile);
};

/*********************************************************************/

class SchemaLocation :
  public XmlSchemaInstanceBase
{
public:
  SchemaLocation();
  SchemaLocation(
    char * prefixIn,
    char * locationIn);
  ~SchemaLocation();
  void printSelf(FILE * outFile);

  char * prefix;
  char * location;
};

/*********************************************************************/

class XmlVersion :
  public XmlSchemaInstanceBase
{
public:
  XmlVersion();
  XmlVersion(bool hasEncodingIn);
  ~XmlVersion();
  void printSelf(FILE * outFile);

  bool hasEncoding;
};

/*********************************************************************/

#endif // XMLSCHEMAINSTANCE_HH
