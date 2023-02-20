/*********************************************************************/

#include <stdio.h>             // for printf, etc.
#include <string.h>            // for strdup
#include <stdlib.h>            // for exit
#include <list>
#include "xmlSchemaInstance.hh"
#include "PalletizingDataTypesClasses.hh"

#define INDENT 2

/*********************************************************************/
/*********************************************************************/

/* class BoxOrientType

*/

BoxOrientType::BoxOrientType() {}

BoxOrientType::BoxOrientType(
 int * valIn)
{
  val = valIn;
  bad = checkVal();
}

BoxOrientType::~BoxOrientType() {}

void BoxOrientType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%d", *val);
}

bool BoxOrientType::checkVal()
{
  return ((*val < 0) ||
          (*val > 24));
}

/*********************************************************************/

/* class CustomItemsType

*/

CustomItemsType::CustomItemsType() {}

CustomItemsType::CustomItemsType(
 whichOne CustomItemsTypeTypeIn,
 CustomItemsTypeVal CustomItemsTypeValueIn)
{
  CustomItemsTypeType = CustomItemsTypeTypeIn;
  CustomItemsTypeValue = CustomItemsTypeValueIn;
}

CustomItemsType::~CustomItemsType() {}

void CustomItemsType::printSelf(FILE * outFile)
{
  if (CustomItemsTypeType == IntItemE)
    {
      doSpaces(0, outFile);
      fprintf(outFile, "<IntItem");
      CustomItemsTypeValue.IntItem->printSelf(outFile);
      doSpaces(0, outFile);
      fprintf(outFile, "</IntItem>\n");
    }
  else if (CustomItemsTypeType == DoubleItemE)
    {
      doSpaces(0, outFile);
      fprintf(outFile, "<DoubleItem");
      CustomItemsTypeValue.DoubleItem->printSelf(outFile);
      doSpaces(0, outFile);
      fprintf(outFile, "</DoubleItem>\n");
    }
  else if (CustomItemsTypeType == StringItemE)
    {
      doSpaces(0, outFile);
      fprintf(outFile, "<StringItem");
      CustomItemsTypeValue.StringItem->printSelf(outFile);
      doSpaces(0, outFile);
      fprintf(outFile, "</StringItem>\n");
    }
}

CustomItemsTypeListHolder::CustomItemsTypeListHolder() {}

CustomItemsTypeListHolder::CustomItemsTypeListHolder(
  std::list<CustomItemsType *> * theListIn)
{
  theList = theListIn;
}

CustomItemsTypeListHolder::~CustomItemsTypeListHolder() {}

void CustomItemsTypeListHolder::printSelf(FILE * outFile)
{
  std::list<CustomItemsType *>::iterator iter;
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  for (iter = theList->begin(); iter != theList->end(); iter++)
    {
      (*iter)->printSelf(outFile);
    }
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class DoubleItemType

*/

DoubleItemType::DoubleItemType() {}

DoubleItemType::DoubleItemType(
 char * DescriptionIn,
 double * ValueIn)
{
  Description = DescriptionIn;
  Value = ValueIn;
}

DoubleItemType::~DoubleItemType() {}

void DoubleItemType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<Description>%s</Description>\n", Description);
  doSpaces(0, outFile);
  fprintf(outFile, "<Value>%f</Value>\n", *Value);
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class IntItemType

*/

IntItemType::IntItemType() {}

IntItemType::IntItemType(
 char * DescriptionIn,
 int * ValueIn)
{
  Description = DescriptionIn;
  Value = ValueIn;
}

IntItemType::~IntItemType() {}

void IntItemType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<Description>%s</Description>\n", Description);
  doSpaces(0, outFile);
  fprintf(outFile, "<Value>%d</Value>\n", *Value);
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class PalletAngleType

*/

PalletAngleType::PalletAngleType() {}

PalletAngleType::PalletAngleType(
 double * valIn)
{
  val = valIn;
  bad = checkVal();
}

PalletAngleType::~PalletAngleType() {}

void PalletAngleType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%f", *val);
}

bool PalletAngleType::checkVal()
{
  return ((*val < -6.2831853) ||
          (*val > +6.2831853));
}

/*********************************************************************/

/* class PalletCoordinateType

*/

PalletCoordinateType::PalletCoordinateType() {}

PalletCoordinateType::PalletCoordinateType(
 double * valIn)
{
  val = valIn;
  bad = checkVal();
}

PalletCoordinateType::~PalletCoordinateType() {}

void PalletCoordinateType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%f", *val);
}

bool PalletCoordinateType::checkVal()
{
  return (false);
}

/*********************************************************************/

/* class PalletDistanceType

*/

PalletDistanceType::PalletDistanceType() {}

PalletDistanceType::PalletDistanceType(
 double * valIn)
{
  val = valIn;
  bad = checkVal();
}

PalletDistanceType::~PalletDistanceType() {}

void PalletDistanceType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%f", *val);
}

bool PalletDistanceType::checkVal()
{
  return ((*val < 0.0));
}

/*********************************************************************/

/* class PalletOverhangType

*/

PalletOverhangType::PalletOverhangType() {}

PalletOverhangType::PalletOverhangType(
 double * valIn)
{
  val = valIn;
  bad = checkVal();
}

PalletOverhangType::~PalletOverhangType() {}

void PalletOverhangType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%f", *val);
}

bool PalletOverhangType::checkVal()
{
  return (false);
}

/*********************************************************************/

/* class PalletPressureType

*/

PalletPressureType::PalletPressureType() {}

PalletPressureType::PalletPressureType(
 double * valIn)
{
  val = valIn;
  bad = checkVal();
}

PalletPressureType::~PalletPressureType() {}

void PalletPressureType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%f", *val);
}

bool PalletPressureType::checkVal()
{
  return ((*val < 0.0));
}

/*********************************************************************/

/* class PalletWeightType

*/

PalletWeightType::PalletWeightType() {}

PalletWeightType::PalletWeightType(
 double * valIn)
{
  val = valIn;
  bad = checkVal();
}

PalletWeightType::~PalletWeightType() {}

void PalletWeightType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%f", *val);
}

bool PalletWeightType::checkVal()
{
  return ((*val < 0.0));
}

/*********************************************************************/

/* class StringItemType

*/

StringItemType::StringItemType() {}

StringItemType::StringItemType(
 char * DescriptionIn,
 char * ValueIn)
{
  Description = DescriptionIn;
  Value = ValueIn;
}

StringItemType::~StringItemType() {}

void StringItemType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<Description>%s</Description>\n", Description);
  doSpaces(0, outFile);
  fprintf(outFile, "<Value>%s</Value>\n", Value);
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

