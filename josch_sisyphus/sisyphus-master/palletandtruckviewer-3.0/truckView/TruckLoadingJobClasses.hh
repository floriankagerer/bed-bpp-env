/*********************************************************************/

#ifndef TRUCKLOADINGJOB_HH
#define TRUCKLOADINGJOB_HH
#include <stdio.h>
#include <list>
#include "xmlSchemaInstance.hh"
#include "PalletizingDataTypesClasses.hh"

/*********************************************************************/

class TruckLoadingJobFile;
class BackAreaType;
class BoxOrientType;
class CustomItemsType;
class CustomItemsTypeListHolder;
class DoorType;
class DoubleItemType;
class EmptyTruckType;
class FrontAreaType;
class IntItemType;
class PalletAngleType;
class PalletCoordinateType;
class PalletDistanceType;
class PalletForTruckType;
class PalletOverhangType;
class PalletPressureType;
class PalletSetType;
class PalletWeightType;
class StringItemType;
class TruckLoadingJobType;
class WheelWellType;

/*********************************************************************/
/*********************************************************************/

class TruckLoadingJobFile :
  public XmlSchemaInstanceBase
{
public:
  TruckLoadingJobFile();
  TruckLoadingJobFile(
    XmlVersion * versionIn,
    TruckLoadingJobType * TruckLoadingJobIn);
  ~TruckLoadingJobFile();
  void printSelf(FILE * outFile);

  XmlVersion * version;
  TruckLoadingJobType * TruckLoadingJob;
};

/*********************************************************************/

class BackAreaType :
  public XmlSchemaInstanceBase
{
public:
  BackAreaType();
  BackAreaType(
    PalletDistanceType * LengthIn,
    PalletDistanceType * WidthIn,
    std::list<DoorType *> * DoorIn,
    std::list<WheelWellType *> * WheelWellIn);
  ~BackAreaType();
  void printSelf(FILE * outFile);

  PalletDistanceType * Length;
  PalletDistanceType * Width;
  std::list<DoorType *> * Door;
  std::list<WheelWellType *> * WheelWell;
};

/*********************************************************************/

class DoorType :
  public XmlSchemaInstanceBase
{
public:
  DoorType();
  DoorType(
    char * DoorIdIn,
    PalletCoordinateType * XcoordinateIn,
    PalletCoordinateType * YcoordinateIn,
    PalletDistanceType * WidthIn,
    PalletDistanceType * HeightIn);
  ~DoorType();
  void printSelf(FILE * outFile);

  char * DoorId;
  PalletCoordinateType * Xcoordinate;
  PalletCoordinateType * Ycoordinate;
  PalletDistanceType * Width;
  PalletDistanceType * Height;
};

/*********************************************************************/

class EmptyTruckType :
  public XmlSchemaInstanceBase
{
public:
  EmptyTruckType();
  EmptyTruckType(
    char * TypeIdIn,
    char * DescriptionIn,
    PalletWeightType * MaximumLoadWeightIn,
    PalletDistanceType * BackAreaHeightIn,
    BackAreaType * BackAreaIn,
    FrontAreaType * FrontAreaIn);
  ~EmptyTruckType();
  void printSelf(FILE * outFile);

  char * TypeId;
  char * Description;
  PalletWeightType * MaximumLoadWeight;
  PalletDistanceType * BackAreaHeight;
  BackAreaType * BackArea;
  FrontAreaType * FrontArea;
};

/*********************************************************************/

class FrontAreaType :
  public XmlSchemaInstanceBase
{
public:
  FrontAreaType();
  FrontAreaType(
    PalletDistanceType * LengthIn,
    PalletDistanceType * WidthIn,
    PalletDistanceType * HeightAboveBackIn);
  ~FrontAreaType();
  void printSelf(FILE * outFile);

  PalletDistanceType * Length;
  PalletDistanceType * Width;
  PalletDistanceType * HeightAboveBack;
};

/*********************************************************************/

class PalletForTruckType :
  public XmlSchemaInstanceBase
{
public:
  PalletForTruckType();
  PalletForTruckType(
    char * PalletIdIn,
    PalletWeightType * WeightIn,
    PalletDistanceType * LengthIn,
    PalletDistanceType * WidthIn,
    PalletDistanceType * HeightIn);
  ~PalletForTruckType();
  void printSelf(FILE * outFile);

  char * PalletId;
  PalletWeightType * Weight;
  PalletDistanceType * Length;
  PalletDistanceType * Width;
  PalletDistanceType * Height;
  // additional attributes
  bool wasLoaded;
};

/*********************************************************************/

class PalletSetType :
  public XmlSchemaInstanceBase
{
public:
  PalletSetType();
  PalletSetType(
    std::list<PalletForTruckType *> * PalletIn,
    char * SetInfoIn);
  ~PalletSetType();
  void printSelf(FILE * outFile);

  std::list<PalletForTruckType *> * Pallet;
  char * SetInfo;
};

/*********************************************************************/

class TruckLoadingJobType :
  public XmlSchemaInstanceBase
{
public:
  TruckLoadingJobType();
  TruckLoadingJobType(
    SchemaLocation * locationIn,
    char * JobIdIn,
    std::list<PalletSetType *> * PalletSetIn,
    EmptyTruckType * EmptyTruckIn);
  ~TruckLoadingJobType();
  void printSelf(FILE * outFile);

  SchemaLocation * location;
  char * JobId;
  std::list<PalletSetType *> * PalletSet;
  EmptyTruckType * EmptyTruck;
};

/*********************************************************************/

class WheelWellType :
  public XmlSchemaInstanceBase
{
public:
  WheelWellType();
  WheelWellType(
    PalletCoordinateType * XcoordinateIn,
    PalletCoordinateType * YcoordinateIn,
    PalletDistanceType * LengthIn,
    PalletDistanceType * WidthIn,
    PalletDistanceType * HeightIn);
  ~WheelWellType();
  void printSelf(FILE * outFile);

  PalletCoordinateType * Xcoordinate;
  PalletCoordinateType * Ycoordinate;
  PalletDistanceType * Length;
  PalletDistanceType * Width;
  PalletDistanceType * Height;
  // additional attributes
  double maxX;  // maximum X value of wheel well in truck coordinates
  double maxY;  // maximum Y value of wheel well in truck coordinates
  double maxZ;  // maximum Z value of wheel well in truck coordinates
  double minX;  // minimum X value of wheel well in truck coordinates
  double minY;  // minimum Y value of wheel well in truck coordinates
};

/*********************************************************************/

#endif // TRUCKLOADINGJOB_HH
