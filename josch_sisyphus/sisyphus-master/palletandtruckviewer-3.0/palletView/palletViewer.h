/*

The PalletViewer class is used to encapsulate (as static class variables)
variables that would otherwise be global. Making the functions static
helps avoid name conflicts and makes it unnecessary to have an instance
of a PalletViewer.

See palletViewer.cc for documentation of what the functions do and what
the variables are for. Since the variables are static, they are
initialized in that file.

The siz struct is a pair of ints representing the number of
instances of an Article ordered and the number in the packlist,
respectively. The items map is a map from the ID of an article
to the two numbers.

*/

#ifndef PALLETVIEWER_HH
#define PALLETVIEWER

#include <stdlib.h>
#include <vector>
#include <map>
#include "asBuilt.h"
#include "response.h"
#include "scoreAsPlannedClasses.hh"

struct siz {int order, pack; };

class PalletViewer
{
 public:
  static void checkPlannedItems(Order * order);
  static void drawString(float x, float y, void * font, char * string);
  static void findAsPlannedScore();
  static void init(char * orderFile, char * packlistFile, char * asBuiltFile,
		   char * scoringFileIn, double toleranceIn);
  static double evaluate(char * orderFile, char * packlistFile, char * scoringFileIn);
  static void insertBox(col boxColor, double minX, double minY, double minZ,
			double maxX, double maxY, double maxZ, bool solid);
  static void makeColors(int howMany);
  static void printAsBuiltPackageText(BuiltPackage * pack, float * wy);
  static void printAsBuiltText(int height);
  static void printAsBuiltStackText(BuiltPackage * pack, float * wy);
  static void printAsPlannedPackageText(Package * pack, float * wy);
  static void printAsPlannedText(int height);
  static void printAsPlannedStackText(Package * pack, float * wy);
  static void recalculate(int change);
  static void redraw();
  static double valuate(valueFunctionType * fun, double val);
 private:
  static AsBuilt             asBuilt; // the as-built pallet
  static std::map <int, col> color;   // map of color to use for each box type
  static col *               colors;  // the colors to use
  static unsigned int        countAsBuilt;   // num as-built packages loaded
  static unsigned int        countAsPlanned; // num as-planned packages loaded
  static PackPallet          cpallet; // the as-planned pallet
  static std::map <unsigned int, siz> items;   // see above
  static PackList            list;    // the list of as-planned pallets
  static int                 missingOrdered; // number ordered packages missing
  static int                 missingPlanned; // number planned packages missing
  static float               scale;   // scale to use to convert mm to picture
  static double              score; // overall score
  static char                scoringFile[200]; //name of scoring config file
  static float               spacing; // grid line spacing in meters
  static double              tolerance; // tolerance for overhangs, etc.
};

#endif //PALLETVIEWER_HH
