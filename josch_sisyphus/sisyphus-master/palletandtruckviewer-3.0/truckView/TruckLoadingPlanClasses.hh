/*********************************************************************/

#ifndef TRUCKLOADINGPLAN_HH
#define TRUCKLOADINGPLAN_HH
#include <stdio.h>
#include <list>
#include "xmlSchemaInstance.hh"
#include "PalletizingDataTypesClasses.hh"
// additional includes
#include "TruckLoadingJobClasses.hh"

/*********************************************************************/

class TruckLoadingPlanFile;
class BoxOrientType;
class CustomItemsType;
class CustomItemsTypeListHolder;
class DoubleItemType;
class IntItemType;
class LoadPalletType;
class PalletAngleType;
class PalletCoordinateType;
class PalletDistanceType;
class PalletOrientType;
class PalletOverhangType;
class PalletPressureType;
class PalletWeightType;
class StringItemType;
class TruckLoadingPlanType;

/*********************************************************************/
/*********************************************************************/

class TruckLoadingPlanFile :
  public XmlSchemaInstanceBase
{
public:
  TruckLoadingPlanFile();
  TruckLoadingPlanFile(
    XmlVersion * versionIn,
    TruckLoadingPlanType * TruckLoadingPlanIn);
  ~TruckLoadingPlanFile();
  void printSelf(FILE * outFile);

  XmlVersion * version;
  TruckLoadingPlanType * TruckLoadingPlan;
};

/*********************************************************************/

class LoadPalletType :
  public XmlSchemaInstanceBase
{
public:
  LoadPalletType();
  LoadPalletType(
    char * PalletIdIn,
    PalletCoordinateType * XcoordinateIn,
    PalletCoordinateType * YcoordinateIn,
    PalletOrientType * OrientationIn,
    char * DoorIn);
  ~LoadPalletType();
  void printSelf(FILE * outFile);

  char * PalletId;
  PalletCoordinateType * Xcoordinate;
  PalletCoordinateType * Ycoordinate;
  PalletOrientType * Orientation;
  char * Door;
  // additional attributes
  float color[3];           // rgb
  std::list<int> inters;    // indexes of pallets intersecting this pallet
  PalletForTruckType * jobPallet; // the pallet from the job with the same id
  double maxX;              // maximum X value of pallet in truck coordinates
  double maxY;              // maximum Y value of pallet in truck coordinates
  double maxZ;              // maximum Z value of pallet in truck coordinates
  double minX;              // minimum X value of pallet in truck coordinates
  double minY;              // minimum Y value of pallet in truck coordinates
  bool overhangErrorX;      // true=overhang error in X direction, false=not
  bool overhangErrorY;      // true=overhang error in Y direction, false=not
  bool reloadedError;       // true=pallet with this id already loaded
  int stackIntersections;   // total pallet intersections thru this pallet
  double stackLoadWeight;   // in kilograms
  int stackOverhangErrors;  // total number of overhang errors thru this pallet
  int stackReloadedErrors;  // total number of reloaded errors thru this pallet
  int stackTotalErrors;     // total number of errors thru this pallet
  int stackUnorderedErrors; // total num of unordered pallets thru this pallet
  double stackWeight;       // stack weight thru this pallet, kg
  int stackWeightError;     // 0 or 1=stack weight thru this pallet over limit
  double stackXMinusOver;   // stack -X overhang of truck thru this pallet, m
  double stackXPlusOver;    // stack +X overhang of truck thru this pallet, m
  double stackYMinusOver;   // stack -Y overhang of truck thru this pallet, m
  double stackYPlusOver;    // stack +Y overhang of truck thru this pallet, m
  bool unorderedError;      // true=no pallet with this id in job, false=not
  double xMinusOver;        // pallet overhang of truck in -X direction, m
  double xPlusOver;         // pallet overhang of truck in +X direction, mm
  double yMinusOver;        // pallet overhang of truck in -Y direction, mm
  double yPlusOver;         // pallet overhang of truck in +Y direction, mm  
};

/*********************************************************************/

class PalletOrientType :
  public XmlSchemaInstanceBase
{
public:
  PalletOrientType();
  PalletOrientType(
    char * valIn);
  ~PalletOrientType();
  void printSelf(FILE * outFile);
  bool checkVal();

  char * val;
  bool bad;
};

/*********************************************************************/

class TruckLoadingPlanType :
  public XmlSchemaInstanceBase
{
public:
  TruckLoadingPlanType();
  TruckLoadingPlanType(
    SchemaLocation * locationIn,
    char * JobIdIn,
    std::list<LoadPalletType *> * LoadPalletIn);
  ~TruckLoadingPlanType();
  void printSelf(FILE * outFile);

  SchemaLocation * location;
  char * JobId;
  std::list<LoadPalletType *> * LoadPallet;
};

/*********************************************************************/

#endif // TRUCKLOADINGPLAN_HH
