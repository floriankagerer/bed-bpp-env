/*********************************************************************/

#ifndef PALLETIZINGDATATYPES_HH
#define PALLETIZINGDATATYPES_HH
#include <stdio.h>
#include <list>
#include "xmlSchemaInstance.hh"

/*********************************************************************/

class BoxOrientType;
class CustomItemsType;
class CustomItemsTypeListHolder;
class DoubleItemType;
class IntItemType;
class PalletAngleType;
class PalletCoordinateType;
class PalletDistanceType;
class PalletOverhangType;
class PalletPressureType;
class PalletWeightType;
class StringItemType;

/*********************************************************************/
/*********************************************************************/

class BoxOrientType :
  public XmlSchemaInstanceBase
{
public:
  BoxOrientType();
  BoxOrientType(
    int * valIn);
  ~BoxOrientType();
  void printSelf(FILE * outFile);
  bool checkVal();

  int * val;
  bool bad;
};

/*********************************************************************/

union CustomItemsTypeVal
{
  IntItemType * IntItem;
  DoubleItemType * DoubleItem;
  StringItemType * StringItem;
};

class CustomItemsType :
  public XmlSchemaInstanceBase
{
public:
  enum whichOne {
    IntItemE,
    DoubleItemE,
    StringItemE };
  CustomItemsType();
  CustomItemsType(
    whichOne CustomItemsTypeTypeIn,
    CustomItemsTypeVal CustomItemsTypeValueIn);
  ~CustomItemsType();
  void printSelf(FILE * outFile);

  whichOne CustomItemsTypeType;
  CustomItemsTypeVal CustomItemsTypeValue;
};

class CustomItemsTypeListHolder :
  public XmlSchemaInstanceBase
{
public:
  CustomItemsTypeListHolder();
  CustomItemsTypeListHolder(
    std::list<CustomItemsType *> * theListIn);
  ~CustomItemsTypeListHolder();
  void printSelf(FILE * outFile);

  std::list<CustomItemsType *> * theList;
};

/*********************************************************************/

class DoubleItemType :
  public XmlSchemaInstanceBase
{
public:
  DoubleItemType();
  DoubleItemType(
    char * DescriptionIn,
    double * ValueIn);
  ~DoubleItemType();
  void printSelf(FILE * outFile);

  char * Description;
  double * Value;
};

/*********************************************************************/

class IntItemType :
  public XmlSchemaInstanceBase
{
public:
  IntItemType();
  IntItemType(
    char * DescriptionIn,
    int * ValueIn);
  ~IntItemType();
  void printSelf(FILE * outFile);

  char * Description;
  int * Value;
};

/*********************************************************************/

class PalletAngleType :
  public XmlSchemaInstanceBase
{
public:
  PalletAngleType();
  PalletAngleType(
    double * valIn);
  ~PalletAngleType();
  void printSelf(FILE * outFile);
  bool checkVal();

  double * val;
  bool bad;
};

/*********************************************************************/

class PalletCoordinateType :
  public XmlSchemaInstanceBase
{
public:
  PalletCoordinateType();
  PalletCoordinateType(
    double * valIn);
  ~PalletCoordinateType();
  void printSelf(FILE * outFile);
  bool checkVal();

  double * val;
  bool bad;
};

/*********************************************************************/

class PalletDistanceType :
  public XmlSchemaInstanceBase
{
public:
  PalletDistanceType();
  PalletDistanceType(
    double * valIn);
  ~PalletDistanceType();
  void printSelf(FILE * outFile);
  bool checkVal();

  double * val;
  bool bad;
};

/*********************************************************************/

class PalletOverhangType :
  public XmlSchemaInstanceBase
{
public:
  PalletOverhangType();
  PalletOverhangType(
    double * valIn);
  ~PalletOverhangType();
  void printSelf(FILE * outFile);
  bool checkVal();

  double * val;
  bool bad;
};

/*********************************************************************/

class PalletPressureType :
  public XmlSchemaInstanceBase
{
public:
  PalletPressureType();
  PalletPressureType(
    double * valIn);
  ~PalletPressureType();
  void printSelf(FILE * outFile);
  bool checkVal();

  double * val;
  bool bad;
};

/*********************************************************************/

class PalletWeightType :
  public XmlSchemaInstanceBase
{
public:
  PalletWeightType();
  PalletWeightType(
    double * valIn);
  ~PalletWeightType();
  void printSelf(FILE * outFile);
  bool checkVal();

  double * val;
  bool bad;
};

/*********************************************************************/

class StringItemType :
  public XmlSchemaInstanceBase
{
public:
  StringItemType();
  StringItemType(
    char * DescriptionIn,
    char * ValueIn);
  ~StringItemType();
  void printSelf(FILE * outFile);

  char * Description;
  char * Value;
};

/*********************************************************************/

#endif // PALLETIZINGDATATYPES_HH
