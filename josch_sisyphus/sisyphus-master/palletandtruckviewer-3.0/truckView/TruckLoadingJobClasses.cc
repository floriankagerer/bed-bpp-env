/*********************************************************************/

#include <stdio.h>             // for printf, etc.
#include <string.h>            // for strdup
#include <stdlib.h>            // for exit
#include <list>
#include "xmlSchemaInstance.hh"
#include "TruckLoadingJobClasses.hh"

#define INDENT 2

/*********************************************************************/
/*********************************************************************/

/* class TruckLoadingJobFile

*/

TruckLoadingJobFile::TruckLoadingJobFile() {}

TruckLoadingJobFile::TruckLoadingJobFile(
  XmlVersion * versionIn,
  TruckLoadingJobType * TruckLoadingJobIn)
{
  version = versionIn;
  TruckLoadingJob = TruckLoadingJobIn;
}

TruckLoadingJobFile::~TruckLoadingJobFile() {}

void TruckLoadingJobFile::printSelf(FILE * outFile)
{
  version->printSelf(outFile);
  fprintf(outFile, "<TruckLoadingJob\n");
  TruckLoadingJob->printSelf(outFile);
  fprintf(outFile, "</TruckLoadingJob>\n");
}

/*********************************************************************/

/* class BackAreaType

*/

BackAreaType::BackAreaType() {}

BackAreaType::BackAreaType(
 PalletDistanceType * LengthIn,
 PalletDistanceType * WidthIn,
 std::list<DoorType *> * DoorIn,
 std::list<WheelWellType *> * WheelWellIn)
{
  Length = LengthIn;
  Width = WidthIn;
  Door = DoorIn;
  WheelWell = WheelWellIn;
}

BackAreaType::~BackAreaType() {}

void BackAreaType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<Length>");
  Length->printSelf(outFile);
  fprintf(outFile, "</Length>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Width>");
  Width->printSelf(outFile);
  fprintf(outFile, "</Width>\n");
  {
    std::list<DoorType *>::iterator iter;
    for (iter = Door->begin(); iter != Door->end(); iter++)
      {
        doSpaces(0, outFile);
        fprintf(outFile, "<Door");
        (*iter)->printSelf(outFile);
        doSpaces(0, outFile);
        fprintf(outFile, "</Door>\n");
      }
  }
  {
    std::list<WheelWellType *>::iterator iter;
    for (iter = WheelWell->begin(); iter != WheelWell->end(); iter++)
      {
        doSpaces(0, outFile);
        fprintf(outFile, "<WheelWell");
        (*iter)->printSelf(outFile);
        doSpaces(0, outFile);
        fprintf(outFile, "</WheelWell>\n");
      }
  }
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class DoorType

*/

DoorType::DoorType() {}

DoorType::DoorType(
 char * DoorIdIn,
 PalletCoordinateType * XcoordinateIn,
 PalletCoordinateType * YcoordinateIn,
 PalletDistanceType * WidthIn,
 PalletDistanceType * HeightIn)
{
  DoorId = DoorIdIn;
  Xcoordinate = XcoordinateIn;
  Ycoordinate = YcoordinateIn;
  Width = WidthIn;
  Height = HeightIn;
}

DoorType::~DoorType() {}

void DoorType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<DoorId>%s</DoorId>\n", DoorId);
  doSpaces(0, outFile);
  fprintf(outFile, "<Xcoordinate>");
  Xcoordinate->printSelf(outFile);
  fprintf(outFile, "</Xcoordinate>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Ycoordinate>");
  Ycoordinate->printSelf(outFile);
  fprintf(outFile, "</Ycoordinate>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Width>");
  Width->printSelf(outFile);
  fprintf(outFile, "</Width>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Height>");
  Height->printSelf(outFile);
  fprintf(outFile, "</Height>\n");
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class EmptyTruckType

*/

EmptyTruckType::EmptyTruckType() {}

EmptyTruckType::EmptyTruckType(
 char * TypeIdIn,
 char * DescriptionIn,
 PalletWeightType * MaximumLoadWeightIn,
 PalletDistanceType * BackAreaHeightIn,
 BackAreaType * BackAreaIn,
 FrontAreaType * FrontAreaIn)
{
  TypeId = TypeIdIn;
  Description = DescriptionIn;
  MaximumLoadWeight = MaximumLoadWeightIn;
  BackAreaHeight = BackAreaHeightIn;
  BackArea = BackAreaIn;
  FrontArea = FrontAreaIn;
}

EmptyTruckType::~EmptyTruckType() {}

void EmptyTruckType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<TypeId>%s</TypeId>\n", TypeId);
  doSpaces(0, outFile);
  fprintf(outFile, "<Description>%s</Description>\n", Description);
  doSpaces(0, outFile);
  fprintf(outFile, "<MaximumLoadWeight>");
  MaximumLoadWeight->printSelf(outFile);
  fprintf(outFile, "</MaximumLoadWeight>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<BackAreaHeight>");
  BackAreaHeight->printSelf(outFile);
  fprintf(outFile, "</BackAreaHeight>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<BackArea");
  BackArea->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</BackArea>\n");
  if (FrontArea)
    {
      doSpaces(0, outFile);
      fprintf(outFile, "<FrontArea");
      FrontArea->printSelf(outFile);
      doSpaces(0, outFile);
      fprintf(outFile, "</FrontArea>\n");
    }
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class FrontAreaType

*/

FrontAreaType::FrontAreaType() {}

FrontAreaType::FrontAreaType(
 PalletDistanceType * LengthIn,
 PalletDistanceType * WidthIn,
 PalletDistanceType * HeightAboveBackIn)
{
  Length = LengthIn;
  Width = WidthIn;
  HeightAboveBack = HeightAboveBackIn;
}

FrontAreaType::~FrontAreaType() {}

void FrontAreaType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<Length>");
  Length->printSelf(outFile);
  fprintf(outFile, "</Length>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Width>");
  Width->printSelf(outFile);
  fprintf(outFile, "</Width>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<HeightAboveBack>");
  HeightAboveBack->printSelf(outFile);
  fprintf(outFile, "</HeightAboveBack>\n");
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class PalletForTruckType

*/

PalletForTruckType::PalletForTruckType() {}

PalletForTruckType::PalletForTruckType(
 char * PalletIdIn,
 PalletWeightType * WeightIn,
 PalletDistanceType * LengthIn,
 PalletDistanceType * WidthIn,
 PalletDistanceType * HeightIn)
{
  PalletId = PalletIdIn;
  Weight = WeightIn;
  Length = LengthIn;
  Width = WidthIn;
  Height = HeightIn;
}

PalletForTruckType::~PalletForTruckType() {}

void PalletForTruckType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<PalletId>%s</PalletId>\n", PalletId);
  doSpaces(0, outFile);
  fprintf(outFile, "<Weight>");
  Weight->printSelf(outFile);
  fprintf(outFile, "</Weight>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Length>");
  Length->printSelf(outFile);
  fprintf(outFile, "</Length>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Width>");
  Width->printSelf(outFile);
  fprintf(outFile, "</Width>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Height>");
  Height->printSelf(outFile);
  fprintf(outFile, "</Height>\n");
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class PalletSetType

*/

PalletSetType::PalletSetType() {}

PalletSetType::PalletSetType(
 std::list<PalletForTruckType *> * PalletIn,
 char * SetInfoIn)
{
  Pallet = PalletIn;
  SetInfo = SetInfoIn;
}

PalletSetType::~PalletSetType() {}

void PalletSetType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  {
    std::list<PalletForTruckType *>::iterator iter;
    for (iter = Pallet->begin(); iter != Pallet->end(); iter++)
      {
        doSpaces(0, outFile);
        fprintf(outFile, "<Pallet");
        (*iter)->printSelf(outFile);
        doSpaces(0, outFile);
        fprintf(outFile, "</Pallet>\n");
      }
  }
  if (SetInfo)
    {
      doSpaces(0, outFile);
      fprintf(outFile, "<SetInfo>%s</SetInfo>\n", SetInfo);
    }
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class TruckLoadingJobType

*/

TruckLoadingJobType::TruckLoadingJobType() {}

TruckLoadingJobType::TruckLoadingJobType(
 SchemaLocation * locationIn,
 char * JobIdIn,
 std::list<PalletSetType *> * PalletSetIn,
 EmptyTruckType * EmptyTruckIn)
{
  location = locationIn;
  JobId = JobIdIn;
  PalletSet = PalletSetIn;
  EmptyTruck = EmptyTruckIn;
}

TruckLoadingJobType::~TruckLoadingJobType() {}

void TruckLoadingJobType::printSelf(FILE * outFile)
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
    std::list<PalletSetType *>::iterator iter;
    for (iter = PalletSet->begin(); iter != PalletSet->end(); iter++)
      {
        doSpaces(0, outFile);
        fprintf(outFile, "<PalletSet");
        (*iter)->printSelf(outFile);
        doSpaces(0, outFile);
        fprintf(outFile, "</PalletSet>\n");
      }
  }
  doSpaces(0, outFile);
  fprintf(outFile, "<EmptyTruck");
  EmptyTruck->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</EmptyTruck>\n");
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class WheelWellType

*/

WheelWellType::WheelWellType() {}

WheelWellType::WheelWellType(
 PalletCoordinateType * XcoordinateIn,
 PalletCoordinateType * YcoordinateIn,
 PalletDistanceType * LengthIn,
 PalletDistanceType * WidthIn,
 PalletDistanceType * HeightIn)
{
  Xcoordinate = XcoordinateIn;
  Ycoordinate = YcoordinateIn;
  Length = LengthIn;
  Width = WidthIn;
  Height = HeightIn;
}

WheelWellType::~WheelWellType() {}

void WheelWellType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<Xcoordinate>");
  Xcoordinate->printSelf(outFile);
  fprintf(outFile, "</Xcoordinate>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Ycoordinate>");
  Ycoordinate->printSelf(outFile);
  fprintf(outFile, "</Ycoordinate>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Length>");
  Length->printSelf(outFile);
  fprintf(outFile, "</Length>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Width>");
  Width->printSelf(outFile);
  fprintf(outFile, "</Width>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<Height>");
  Height->printSelf(outFile);
  fprintf(outFile, "</Height>\n");
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

