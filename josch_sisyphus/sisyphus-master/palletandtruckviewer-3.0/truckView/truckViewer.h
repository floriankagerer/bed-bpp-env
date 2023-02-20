/*

The TruckViewer class is used to encapsulate (as static class variables)
variables that would otherwise be global. Making the functions static
helps avoid name conflicts and makes it unnecessary to have an instance
of a TruckViewer.

See truckViewer.cc for documentation of what the functions do and what
the variables are for. Since the variables are static, they are
initialized in that file.

*/

#ifndef TRUCKVIEWER_HH
#define TRUCKVIEWER

#include <stdlib.h>
#include <vector>
#include <map>
#include "TruckLoadingJobClasses.hh"
#include "TruckLoadingPlanClasses.hh"

struct siz {int order, pack; };
struct col {float r, g, b; };

class TruckViewer
{
 public:
  static void checkJob();
  static void checkPlan();
  static void drawString(float x, float y, void * font, char * string);
  static void findIntersections(double tolerance);
  static void findOverhangs(double tolerance);
  static void findTotalErrors();
  static void init(char * jobFile, char * planFile, double toleranceIn);
  static void insertBox(col boxColor, double minX, double minY, double minZ,
			double maxX, double maxY, double maxZ, bool solid);
  static void insertDoors(double originX, double originY,
			  std::list<DoorType *> * doors);
  static void insertTruckOutline(double minX, double maxX,
				 double minY, double maxY, double height);
  static void insertWheelWells(col boxColor, double originX, double originY, 
			       std::list<WheelWellType *> * WheelWells);
  static void makeColors(int howMany);
  static void printAsPlannedPalletText(LoadPalletType * pal, float * wy);
  static void printAsPlannedText(int height);
  static void printAsPlannedStackText(LoadPalletType * pal, float * wy);
  static void readJob(char * jobFileName);
  static void readPlan(char * planFileName);
  static void recalculate(int change);
  static void redraw();
  static void usageMessage(char * command);
 private:
  static col *               colors;  // the colors to use
  static int                 countAsPlanned; // num as-planned packages loaded
  static TruckLoadingJobType * job;   // the job order
  static double              maxOkXHang; // largest OK overhang in X direction
  static double              maxOkYHang; // largest OK overhang in Y direction
  static int                 missingOrdered; // number of job pallets missing
  static int                 numberPallets;  // number of pallets in job
  static double              originX; // plan truck orig X, unscaled view coords
  static double              originY; // plan truck orig Y, unscaled view coords
  static std::vector<LoadPalletType *> pallets; // pallets in plan
  static TruckLoadingPlanType * plan; // the as-planned truck
  static float               scale;   // scale to use to convert mm to picture
  static float               spacing; // grid line spacing in meters
  static double              tolerance; // tolerance for overhangs, etc.
  static double              truckHeight; // height of truck back loading area
  static double              truckLength; // total length of truck loading area
  static double              truckWidth; // max width of truck loading area
  static PalletForTruckType  unknownPallet; //unknown pallet
};

#endif //TRUCKVIEWER_HH
