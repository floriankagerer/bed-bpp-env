/*********************************************************************/

#include <stdio.h>             // for printf, etc.
#include <string.h>            // for strdup
#include <stdlib.h>            // for exit
#include <list>
#include "xmlSchemaInstance.hh"
#include "TruckLoadingPlanClasses.hh"

#define INDENT 2

/*********************************************************************/
/*********************************************************************/

/* class TruckLoadingPlanFile

*/

TruckLoadingPlanFile::TruckLoadingPlanFile() {}

TruckLoadingPlanFile::TruckLoadingPlanFile(
  XmlVersion * versionIn,
  TruckLoadingPlanType * TruckLoadingPlanIn)
{
  version = versionIn;
  TruckLoadingPlan = TruckLoadingPlanIn;
}

TruckLoadingPlanFile::~TruckLoadingPlanFile() {}

void TruckLoadingPlanFile::printSelf(FILE * outFile)
{
  version->printSelf(outFile);
  fprintf(outFile, "<TruckLoadingPlan\n");
  TruckLoadingPlan->printSelf(outFile);
  fprintf(outFile, "</TruckLoadingPlan>\n");
}

/*********************************************************************/

/* class LoadPalletType

*/

LoadPalletType::LoadPalletType() {}

LoadPalletType::LoadPalletType(
 char * PalletIdIn,
 PalletCoordinateType * XcoordinateIn,
 PalletCoordinateType * YcoordinateIn,
 PalletOrientType * OrientationIn,
 char * DoorIn)
{
  PalletId = PalletIdIn;
  Xcoordinate = XcoordinateIn;
  Ycoordinate = YcoordinateIn;
  Orientation = OrientationIn;
  Door = DoorIn;
}

LoadPalletType::~LoadPalletType() {}

void LoadPalletType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<PalletId>%s</PalletId>\n", PalletId);
  doSpaces(0, outFile);
  fprintf(outFile, "<Xcoordinate>");
  Xcoordinate->printSelf(outFile);
  fprintf(outFile, "</Xcoordinate>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Ycoordinate>");
  Ycoordinate->printSelf(outFile);
  fprintf(outFile, "</Ycoordinate>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Orientation>");
  Orientation->printSelf(outFile);
  fprintf(outFile, "</Orientation>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Door>%s</Door>\n", Door);
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class PalletOrientType

*/

PalletOrientType::PalletOrientType() {}

PalletOrientType::PalletOrientType(
 char * valIn)
{
  val = valIn;
  bad = checkVal();
}

PalletOrientType::~PalletOrientType() {}

void PalletOrientType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%s", val);
}

bool PalletOrientType::checkVal()
{
  return (strcmp(val, "LengthX") &&
          strcmp(val, "LengthY"));
}

/*********************************************************************/

/* class TruckLoadingPlanType

*/

TruckLoadingPlanType::TruckLoadingPlanType() {}

TruckLoadingPlanType::TruckLoadingPlanType(
 SchemaLocation * locationIn,
 char * JobIdIn,
 std::list<LoadPalletType *> * LoadPalletIn)
{
  location = locationIn;
  JobId = JobIdIn;
  LoadPallet = LoadPalletIn;
}

TruckLoadingPlanType::~TruckLoadingPlanType() {}

void TruckLoadingPlanType::printSelf(FILE * outFile)
{
  fprintf(outFile, "  xmlns=\"urn:Palletizing\"\n");
  fprintf(outFile,
          "  xmlns:plt=\"http://www.w3.org/2001/XMLSchema-instance\"\n");
  location->printSelf(outFile);
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<JobId>%s</JobId>\n", JobId);
  {
    std::list<LoadPalletType *>::iterator iter;
    for (iter = LoadPallet->begin(); iter != LoadPallet->end(); iter++)
      {
        doSpaces(0, outFile);
        fprintf(outFile, "<LoadPallet");
        (*iter)->printSelf(outFile);
        doSpaces(0, outFile);
        fprintf(outFile, "</LoadPallet>\n");
      }
  }
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

