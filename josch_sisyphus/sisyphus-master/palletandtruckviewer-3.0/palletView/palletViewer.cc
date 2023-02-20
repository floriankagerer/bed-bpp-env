/*
  DISCLAIMER:
  This software was produced by the National Institute of Standards
  and Technology (NIST), an agency of the U.S. government, and by statute is
  not subject to copyright in the United States.  Recipients of this software
  assume all responsibility associated with its operation, modification,
  maintenance, and subsequent redistribution.

  See NIST Administration Manual 4.09.07 b and Appendix I. 
*/

/*!
  \file palletViewer.cc

  \brief Displays pallet and metrics.
  \code CVS Status:
  $Author: dr_steveb $
  $Revision: 1.18 $
  $Date: 2011/02/23 16:26:25 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/

#include <stdio.h>
#include <vector>
#include <fstream>
#include <stdlib.h>
#include <map>
#include <time.h>
#include <math.h>
//#include "view.h"    // for draw_string, gl functions, glut functions
#include "xml_parser.h"
#include "packlist.h"
#include "response.h"
#include "asBuilt.h"
#include "palletViewer.h"
#include "scoreAsPlannedClasses.hh"

#define MINIMUM_OVERLAP .4 // the minimum pallet overlap to avoid an error
#define STR_LENGTH 200
#define max(x,y) (((y) > (x)) ? (y) : (x))

/********************************************************************/

// PalletViewer static variables

AsBuilt             PalletViewer::asBuilt;  // model of stack as built
std::map <int, col> PalletViewer::color;    // map from box id to a color
col *               PalletViewer::colors;   // array of available box colors
unsigned int        PalletViewer::countAsBuilt = 0;// num as-built displayed
unsigned int        PalletViewer::countAsPlanned = 0;// num as-planned displayed
PackPallet          PalletViewer::cpallet;  // model of pallet in packlist file
std::map <unsigned int, siz> PalletViewer::items; // map from ID to numbers
PackList            PalletViewer::list;     // model of entire packlist file
int                 PalletViewer::missingOrdered;  // ordered, not on packlist
int                 PalletViewer::missingPlanned;  // planned, not on asBuilt
float               PalletViewer::scale;    // scale to use to convert mm
double              PalletViewer::score;    // overall score
char                PalletViewer::scoringFile[200];//name of scoring config file
float               PalletViewer::spacing;  // grid line spacing in meters
double              PalletViewer::tolerance; // tolerance for overhangs, etc.

/********************************************************************/

extern ScoreAsPlannedFile * tree;
extern FILE * yyin;
extern int yyparse();

/********************************************************************/

/* PalletViewer::checkAsBuiltItems

Returned Value: none

Called By:  PalletViewer::init

This checks the as-built pallet against the packlist (cpallet).


*/

void checkAsBuiltItems()
{

}

/********************************************************************/

/* PalletViewer::checkPlannedItems 

Returned Value: none

Called By:  PalletViewer::init

This checks the first pallet in the packlist (cpallet) against the
order. It is assumes the entire order is on one pallet.

If there are any packages in the packlist that are not in the
order (either an id not in the order at all, or too many of a given
id), errors are recorded and the interlopers or extras are assigned
a dark gray color.

If there are any Articles in the order for which there are not enough in
the packlist, that is recorded.

The mechanism for doing the work is to build a map (items) from ids to
pairs of numbers, where the first number is how many times an item with
that id is ordered, and the second number is how many packages with that
id are in the packlist. Every id that appears in either the order
or the packlist has an entry in the items map once it is built.

There may be several different order lines and several different packages
in the packlist with the same Article.

*/

void PalletViewer::checkPlannedItems( /* ARGUMENTS                   */
 Order * order)                       /* order file to check against */
{
  unsigned int i;
  Package * pack;      // package being tested
  OrderLine * orderLine;
  struct siz sizes;
  unsigned int id;
  std::map<unsigned int, siz>::iterator iter;
  int orderErrors = 0;
  static col greyColor = {0.2f, 0.2f, 0.2f};

  for (i = 0; i < order->n_orderline(); i++)
    { // record order data in the items map
      orderLine = &(order->orderline[i]);
      id = orderLine->article.id;
      iter = items.find(id);
      if (iter == items.end())
	{
	  sizes.order = orderLine->n_barcode();
	  sizes.pack = 0;
	  items.insert(std::pair<unsigned int, siz>(id, sizes));
	}
      else
	{
	  iter->second.order += orderLine->n_barcode();
	}
    }
  for (i = 0; i < cpallet.packages.size(); i++)
    { // record packlist data in the items map
      pack = &(cpallet.packages[i]);
      id = pack->article.id;
      iter = items.find(id);
      if (iter == items.end())
	{ // no items with this id were ordered or previously packlisted
	  sizes.order = 0;
	  sizes.pack = 1;
	  items.insert(std::pair<unsigned int, siz>(id, sizes));
	  pack->orderError = 1;
	  pack->color = greyColor;
	  orderErrors++;
	}
      else
	{ // an item with this id was either ordered or previously packlisted
	  (iter->second.pack)++ ;
	  if (iter->second.pack > iter->second.order)
	    { // too many packages of this type are on the stack
	      pack->orderError = 1;
	      pack->color = greyColor;
	      orderErrors++;
	    }
	  else
	    { // packlisted package was ordered, not too many, everything OK
	      pack->orderError = 0;
	      pack->color = color[id];
	    }
	}
      pack->stackOrderErrors = orderErrors;
    }
  missingOrdered = 0;
  for (iter = items.begin(); iter != items.end(); iter++)
    { // add up the total number of ordered items not in the packlist
      if (iter->second.order > iter->second.pack)
	missingOrdered += (iter->second.order - iter->second.pack);
    }
}

/********************************************************************/

/* drawString

Returned Value: none

Called By:
  PalletViewer::printAsBuiltPackageText
  PalletViewer::printAsBuiltText
  PalletViewer::printAsBuiltStackText
  PalletViewer::printAsPlannedText
  PalletViewer::printAsPlannedPackageText
  PalletViewer::printAsPlannedStackText

This prints one line of text starting at the given (x,y) location (in
currently active screen coordinates). The text is printed left to right
in the normal fashion for the English language.

The font argument is actually a symbol such as GLUT_BITMAP_HELVETICA_10.

*/

/*
void PalletViewer::drawString( *//* ARGUMENTS                   *//*
 float x,                      *//* X location of start of text *//*
 float y,                      *//* Y location of start of text *//*
 void * font,                  *//* the font to use             *//*
 char* string)                 *//* the text to print           *//*
{
  char * c;

  glRasterPos2f(x, y);
  for (c = string; *c != '\0'; c++)
    {
      glutBitmapCharacter(font, *c);
    }
}
*/

/********************************************************************/

/* findAsPlannedScore

Returned Value: none

Called By: init

This finds the score for a pallet using data from the as-planned file
and the scoring configuration read from the scoring configuration file.

It uses the following seven data factors to compute the score.

Factor Name               Factor Value
-----------               ------------
rightStuff                rightStuffValue (local variable computed here)
overhang                  maxHang (local variable computed here)
volumeDensity             density (local variable computed here)
overlapFraction           stackOverlapFraction of the last package
connectionsBelow          stackAverageConnects of the last package
cogInverseRelativeHeight  relHeight (local variable computed here)
cogRelativeOffset         relOffset (local variable computed here)

Each factor is designated as additive or multiplicative. A factor
value Vi between 0 and 1 is found for each additive factor and a
factor value Ui between 0 and 1 is found for each multiplicative
factor. Each additive factor is assigned a non-negative weight Wi. An
additive score Sa is produced by multiplying each additive value by
its weight, adding the products together, and dividing by the sum of the
weights. If there are no additive factors or their weights are all
zero, Sa = 1.

Sa = (((V1 x W1) + (V2 x W2) ... + (Vn x Wn)) / (W1 + W2 + ... + Wn))

The value of Sa will be between 0 and 1 since all the components of the
equation are positive and the largest the numerator can be is the size
of the denominator.

Then the total score S is found by finding the product of Sa, 100, and
all the multiplicative factors.

S = (100 x Sa x U1 x U2 ... x Um)

In the code below "score" serves for both Sa and S.

Each Vi or Ui factor may be converted to a value between 0 and 1 by
a value function before being used as described above. See documentation
of the valuate function.

The density is the stackDensity of the last package. If that is more
than 1, it is set to 1.

The rightStuffValue is [the total number of packages in the as-built stack
minus the total number of errors] divided by [the number of packages in
the order]. If that is less than zero, it is set to zero.

The maxHang value is the largest overhang off the side of the pallet
in meters.

The relHeight is [half the height of a box that has the same volume as
the total volume of boxes on the stack and has a base that is the pallet
extended by any overhang] divided by [the height of the center of gravity].
If that is more than 1, it is set to 1.

The relOffset is [1] minus [the larger of the relative offsets in the X
and Y directions of the center of gravity]. If that is less than zero
(which is very unlikely), it is set to zero.

This checks to that at least one weight is non-zero and prints an error
message and exits if that is not the case.

*/

void PalletViewer::findAsPlannedScore() /* NO ARGUMENTS */
{
  double density;              // volume density of stack
  Package * pack;              // package being tested
  double rightStuffValue;      // value to be input to rightStuff
  double maxHang;              // largest of four overhangs
  double relOffset;            // 1 - largest COG relative offset absolute value
  double relHeight;            // (half virtual box height) / (COG height)
  scoreAsPlannedType * scorer; // scoring method
  int weight;                  // the weight of a factor
  unsigned totalWeight = 0;    // sum of weights for additive factors
  valueFunctionType * fun;     // a value function
  bool weightOk = false;       // set to true if any weight is positive

  score = 0;
  scorer = tree->ScoreAsPlanned;
  pack = &(cpallet.packages[cpallet.packages.size() - 1]);
  density = pack->stackDensity;
  if (density > 1)
    density = 1;
  rightStuffValue = (((int)cpallet.packages.size() - pack->stackTotalErrors) /
		     (double)(cpallet.packages.size() + missingOrdered));
  if (rightStuffValue < 0.0)
    rightStuffValue = 0.0;
  maxHang = max(max(pack->stackXMinusOver, pack->stackXPlusOver),
		max(pack->stackYMinusOver, pack->stackYPlusOver));
  maxHang /= 1000.0; // convert to meters
  relOffset = (1 - max(fabs(pack->cogRelX), fabs(pack->cogRelY)));
  if (relOffset < 0.0)
    relOffset = 0.0;
  relHeight = ((density * pack->stackHeight) / (2 * pack->cogZ));
  if (relHeight > 1.0)
    relHeight = 1.0;

  weight = *(scorer->rightStuff->weight);
  if (weight)
    {
      weightOk = true;
      if (*(scorer->rightStuff->isAdditive))
	{
	  totalWeight += weight;
	  if ((fun = scorer->rightStuff->valueFunction))
	    score += (weight * valuate(fun, rightStuffValue));
	  else
	    score += (weight * rightStuffValue);
	}
    }
  weight = *(scorer->overhang->weight);
  if (weight)
    {
      weightOk = true;
      if (*(scorer->overhang->isAdditive))
	{
	  totalWeight += weight;
	  fun = scorer->overhang->valueFunction;
	  score += (weight * valuate(fun, maxHang));
	}
    }
  weight = *(scorer->volumeDensity->weight);
  if (weight)
    {
      weightOk = true;
      if (*(scorer->volumeDensity->isAdditive))
	{
	  totalWeight += weight;
      	  if ((fun = scorer->volumeDensity->valueFunction))
	    score += (weight * valuate(fun, density));
	  else
	    score += (weight * density);
	}
    }
  weight = *(scorer->overlapFraction->weight);
  if (weight)
    {
      weightOk = true;
      if (*(scorer->overlapFraction->isAdditive))
	{
	  totalWeight += weight;
      	  if ((fun = scorer->overlapFraction->valueFunction))
	    score += (weight * valuate(fun, pack->stackOverlapFraction));
	  else
	    score += (weight * pack->stackOverlapFraction);
	}
    }
  weight = *(scorer->connectionsBelow->weight);
  if (weight)
    {
      weightOk = true;
      if (*(scorer->connectionsBelow->isAdditive))
	{
	  totalWeight += weight;
	  fun = scorer->connectionsBelow->valueFunction;
	  score += (weight * valuate(fun, pack->stackAverageConnects));
	}
    }
  weight = *(scorer->cogInverseRelativeHeight->weight);
  if (weight)
    {
      weightOk = true;
      if ((*(scorer->cogInverseRelativeHeight->isAdditive)))
	{
	  totalWeight += weight;
	  if ((fun = scorer->cogInverseRelativeHeight->valueFunction))
	    score += (weight * valuate(fun, relHeight));
	  else
	    score += (weight * relHeight);
	}
    }
  weight = *(scorer->cogRelativeOffset->weight);
  if (weight)
    {
      weightOk = true;
      if ((*(scorer->cogRelativeOffset->isAdditive)))
	{
	  totalWeight += weight;
	  if ((fun = scorer->cogRelativeOffset->valueFunction))
	    score += (weight * valuate(fun, relOffset));
	  else
	    score += (weight * relOffset);
	}
    }

  if (weightOk == false)
    {
      fprintf(stderr, "At least one scoring weight must be positive\n");
      exit(1);
    }
  if (totalWeight)
    score /= totalWeight;
  else
    score = 1.0;
  score *= 100.0;
  if ((*(scorer->rightStuff->weight)) &&
      (!(*(scorer->rightStuff->isAdditive))))
    {
      if ((fun = scorer->rightStuff->valueFunction))
	score *= valuate(fun, rightStuffValue);
      else
	score *= rightStuffValue;
    }
  if ((*(scorer->overhang->weight)) &&
      (!(*(scorer->overhang->isAdditive))))
    {
      fun = scorer->overhang->valueFunction;
      score *= valuate(fun, maxHang);
    }
  if ((*(scorer->volumeDensity->weight)) &&
      (!(*(scorer->volumeDensity->isAdditive))))
    {
      if ((fun = scorer->volumeDensity->valueFunction))
	score *= valuate(fun, density);
      else
	score *= density;
    }
  if ((*(scorer->overlapFraction->weight)) &&
      (!(*(scorer->overlapFraction->isAdditive))))
    {
      if ((fun = scorer->overlapFraction->valueFunction))
	score *= valuate(fun, pack->stackOverlapFraction);
      else
	score *= pack->stackOverlapFraction;
    }
  if ((*(scorer->connectionsBelow->weight)) &&
      (!(*(scorer->connectionsBelow->isAdditive))))
    {
      fun = scorer->connectionsBelow->valueFunction;
      score *= valuate(fun, pack->stackAverageConnects);
    }
  if ((*(scorer->cogInverseRelativeHeight->weight)) &&
      (!(*(scorer->cogInverseRelativeHeight->isAdditive))))
    {
      if ((fun = scorer->cogInverseRelativeHeight->valueFunction))
	score *= valuate(fun, relHeight);
      else
	score *= relHeight;
    }
  if ((*(scorer->cogRelativeOffset->weight)) &&
      (!(*(scorer->cogRelativeOffset->isAdditive))))
    {
      if ((fun = scorer->cogRelativeOffset->valueFunction))
	score *= valuate(fun, relOffset);
      else
	score *= relOffset;
    }
}

/********************************************************************/


/* PalletViewer::init

Returned Value: none

Called By: main (in main.cc)

This initializes the palletViewer by reading the files, calculating
metrics, making the colors, and inserting the colors in the color map.

For all of the metrics, data for the stack up to and including package
N is calculated and stored in the package N data. That way, the data
is calculated only once and simply retrieved as the stack is loaded in
order or unloaded in reverse order.

The scale to use is calculated by having the larger of the length
and width of the pallet being used fit exactly into 9 grid squares,
which is 0.45 units in picture space. That way, the as-planned and
as-built pallets both fit into the picture without going beyond
the grid.

The tolerance (in millimeters) is applied in determining three kinds of
errors: overlap, overhang, and intersection. It is also applied in
finding overlaps.

*/

void PalletViewer::init( /* ARGUMENTS                          */
 char * orderFile,       /* name of order file                 */
 char * packlistFile,    /* name of packlist file              */
 char * asBuiltFile,     /* name of as-built file              */
 char * scoringFileIn,   /* name of scoring configuration file */
 double toleranceIn)     /* in millimeters, see above          */
{
  Order order;
  unsigned int i;

  tolerance = toleranceIn;
  strncpy(scoringFile, scoringFileIn, 100);
  order = readOrder(orderFile);
  makeColors(order.n_orderline());
  for (i = 0; i < order.n_orderline(); i++)
    {
      color.insert(std::pair<int, col>
		   (order.orderline[i].article.id, colors[i]));
    }
  list = PackList::read_response(packlistFile);
  yyin = fopen(scoringFile, "r");
  if (yyin == 0)
    {
      fprintf(stderr, "unable to open file %s for reading\n", scoringFile);
      exit(1);
    }
  yyparse();
  fclose(yyin);
  printf("Scoring File Read.\n");
  if (asBuiltFile[0])
    asBuilt.readAsBuilt(asBuiltFile);
  cpallet = list.packedPallets[0];
  checkPlannedItems(&order);
  scale = 0.450f / max(cpallet.dimensions.length, cpallet.dimensions.width);
  spacing = max(cpallet.dimensions.length, cpallet.dimensions.width)/9000.0f;
  cpallet.findSequenceErrors();
  cpallet.findOverlaps(tolerance, MINIMUM_OVERLAP);
  cpallet.findCogs();
  cpallet.findIntersections(tolerance);
  cpallet.findOverhangs(tolerance);
  cpallet.findPressures();
  cpallet.findPressureMetrics();
  cpallet.findVolumes();
  cpallet.findTotalErrors();
  findAsPlannedScore();

  if (asBuiltFile[0])
    {
      missingPlanned = 0;
      asBuilt.findFileErrors(&cpallet, &missingPlanned);
      asBuilt.findPositionErrors(&cpallet);
    }
  
}

double PalletViewer::evaluate( /* ARGUMENTS                          */
 char * orderFile,       /* name of order file                 */
 char * packlistFile,    /* name of packlist file              */
 char * scoringFileIn)   /* name of scoring configuration file */
{
  Order order;
  unsigned int i;

  tolerance = 0;
  strncpy(scoringFile, scoringFileIn, 100);
  order = readOrder(orderFile);
  makeColors(order.n_orderline());
  for (i = 0; i < order.n_orderline(); i++)
    {
      color.insert(std::pair<int, col>
		   (order.orderline[i].article.id, colors[i]));
    }
  list = PackList::read_response(packlistFile);
  yyin = fopen(scoringFile, "r");
  if (yyin == 0)
    {
      fprintf(stderr, "unable to open file %s for reading\n", scoringFile);
      exit(1);
    }
  yyparse();
  fclose(yyin);
  cpallet = list.packedPallets[0];
  checkPlannedItems(&order);
  scale = 0.450f / max(cpallet.dimensions.length, cpallet.dimensions.width);
  spacing = max(cpallet.dimensions.length, cpallet.dimensions.width)/9000.0f;
  cpallet.findSequenceErrors();
  cpallet.findOverlaps(tolerance, MINIMUM_OVERLAP);
  cpallet.findCogs();
  cpallet.findIntersections(tolerance);
  cpallet.findOverhangs(tolerance);
  cpallet.findPressures();
  cpallet.findPressureMetrics();
  cpallet.findVolumes();
  cpallet.findTotalErrors();
  findAsPlannedScore();

  for (i = 0; i < cpallet.packages.size(); i++) {
      recalculate(1);
      if (countAsPlanned == cpallet.packages.size())
          return score;
  }
}

/********************************************************************/

/* PalletViewer::insertBox

Returned Value: none

Called By: PalletViewer::redraw

This draws a box at the given position using a method that will work
in a display list. The display area is actually 1 unit wide (to work
well with the camera and openGL) while the area it represents depends
on the size of the pallet. The larger of the length and width of the
pallet fits in 0.45 picture units.

The location point of a box is in the middle of the top of the box.

*/

/*
void PalletViewer::insertBox( *//* ARGUMENTS                                  *//*
 col boxColor,                *//* color of box                               *//*
 double minX,                 *//* minimum value of X on box in millimeters   *//*
 double minY,                 *//* minimum value of Y on box in millimeters   *//*
 double minZ,                 *//* minimum value of Z on box in millimeters   *//*
 double maxX,                 *//* maximum value of X on box in millimeters   *//*
 double maxY,                 *//* maximum value of Y on box in millimeters   *//*
 double maxZ,                 *//* maximum value of Z on box in millimeters   *//*
 bool solid)                  *//* true = faces and edges, false = edges only *//*
{
  static GLubyte allIndices[] = {4,5,6,7, 1,2,6,5, 0,1,5,4,
				 0,3,2,1, 0,4,7,3, 2,3,7,6};
  static GLfloat vertices[] = {0,0,0, 0,0,0, 0,0,0, 0,0,0,
			       0,0,0, 0,0,0, 0,0,0, 0,0,0};
  
  glEnableClientState(GL_VERTEX_ARRAY);
  minX *= scale;
  minY *= scale;
  minZ *= scale;
  maxX *= scale;
  maxY *= scale;
  maxZ *= scale;
  vertices[0]  = (GLfloat)minX;
  vertices[1]  = (GLfloat)minY;
  vertices[2]  = (GLfloat)minZ;
  vertices[3]  = (GLfloat)minX;
  vertices[4]  = (GLfloat)maxY;
  vertices[5]  = (GLfloat)minZ;
  vertices[6]  = (GLfloat)minX;
  vertices[7]  = (GLfloat)maxY;
  vertices[8]  = (GLfloat)maxZ;
  vertices[9]  = (GLfloat)minX;
  vertices[10] = (GLfloat)minY;
  vertices[11] = (GLfloat)maxZ;
  vertices[12] = (GLfloat)maxX;
  vertices[13] = (GLfloat)minY;
  vertices[14] = (GLfloat)minZ;
  vertices[15] = (GLfloat)maxX;
  vertices[16] = (GLfloat)maxY;
  vertices[17] = (GLfloat)minZ;
  vertices[18] = (GLfloat)maxX;
  vertices[19] = (GLfloat)maxY;
  vertices[20] = (GLfloat)maxZ;
  vertices[21] = (GLfloat)maxX;
  vertices[22] = (GLfloat)minY;
  vertices[23] = (GLfloat)maxZ;
  glVertexPointer(3, GL_FLOAT, 0, vertices);
  glColor3f(boxColor.r, boxColor.g, boxColor.b);
  if (solid)
    {
      glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
      glDrawElements(GL_QUADS, 24, GL_UNSIGNED_BYTE, allIndices);
      glColor3f(0.0f, 0.0f, 0.0f);
      glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
      glDrawElements(GL_QUADS, 24, GL_UNSIGNED_BYTE, allIndices);
    }
  else
    {
      glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
      glDrawElements(GL_QUADS, 24, GL_UNSIGNED_BYTE, allIndices);
    }
}
*/

/********************************************************************/

/* palletViewer::makeColors

Returned Value: none

Called By: PalletViewer::init

This makes an array of howMany colors by picking points in the RGB cube.
The points gradually become dense in the cube. Colors that are dim
(i.e. the sum of the components is less than 0.4) are not used. Greyish
colors (near the diagonal from (0,0,0) to (1,1,1) are not used.
Colors that are adjacent in the array are generally far apart in the
cube. The first N colors generated for any value of howMany are the same
as the first N colors for any other value of howMany (as long as N is
smaller than both).

Each time around the outer loop, all points generated so far are used
to generate up to 6 new points by adding "jump" to the values of
R, G, B, RG, GB, and RB. Newly generated points outside the cube are
not used, and dim colors are not used. Adding jump to all of RGB is not
used in order to stay away from the central diagonal. At the end of
the outer loop, the jump size is cut in half.

The first color this makes is black in order to seed the outer loop.
In order uphold the "no dim colors" rule, this makes one extra color
and sets colors to point to the second element of the array.

Multiple inner loops are used rather than a single inner loop in order
to keep adjacent colors in the array far apart in the RGB cube.

*/

void PalletViewer::makeColors( /* ARGUMENTS             */
 int howMany)                  /* size of array to make */
{
  int n;      // total number of colors at end of last go-around
  float jump; // how far to move
  int m;      // index to fill in
  int i;      // index for 0 to n
  col * cols; // another handle on the array

  if (howMany < 1)
    { // quit if howMany is zero or negative
      fprintf(stderr, "Number of orders = %d, exiting\n", howMany);
      exit(1);
    }
  howMany++;
  cols = new col[howMany];
  colors = (cols + 1);
  cols[0].r = 0.0;
  cols[0].g = 0.0;
  cols[0].b = 0.0;
  n = 1;
  m = n;

  for (jump = 1.0; m < howMany; n = (m - 1), jump = (jump / 2))
    {
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].r + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + jump) > 0.4))
	    {
	      cols[m].r = (cols[i].r + jump);
	      cols[m].g = cols[i].g;
	      cols[m].b = cols[i].b;
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].g + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + jump) > 0.4))
	    {
	      cols[m].r = cols[i].r;
	      cols[m].g = (cols[i].g + jump);
	      cols[m].b = cols[i].b;
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].b + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + jump) > 0.4))
	    {
	      cols[m].r = cols[i].r;
	      cols[m].g = cols[i].g;
	      cols[m].b = (cols[i].b + jump);
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].r + jump) <= 1.0) &&
	      ((cols[i].g + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + (2 * jump)) > 0.4))
	    {
	      cols[m].r = (cols[i].r + jump);
	      cols[m].g = (cols[i].g + jump);
	      cols[m].b = cols[i].b;
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].g + jump) <= 1.0) &&
	      ((cols[i].b + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + (2 * jump)) > 0.4))
	    {
	      cols[m].r = cols[i].r;
	      cols[m].g = (cols[i].g + jump);
	      cols[m].b = (cols[i].b + jump);
	      if (++m == howMany)
		return;
	    }
	}
      for (i = 0; i < n; i++)
	{
	  if (((cols[i].r + jump) <= 1.0) &&
	      ((cols[i].b + jump) <= 1.0) &&
	      ((cols[i].r + cols[i].g + cols[i].b + (2 * jump)) > 0.4))
	    {
	      cols[m].r = (cols[i].r + jump);
	      cols[m].g = cols[i].g;
	      cols[m].b = (cols[i].b + jump);
	      if (++m == howMany)
		return;
	    }
	}
    } 
}

/********************************************************************/

/* PalletViewer::printAsBuiltPackageText

Returned Value: none

Called By: PalletViewer::printAsBuiltText

This prints the top section of the as-built metrics window, which
gives metrics for the most recently loaded package.


*/

/*
void PalletViewer::printAsBuiltPackageText( *//* ARGUMENTS                  *//*
 BuiltPackage * pack,              *//* Package to print from               *//*
 float * wy)                       *//* Y-value on screen at which to print *//*
{
  char str[STR_LENGTH];  // string to print in
  float yy;

  yy = *wy;
  snprintf(str, STR_LENGTH, "CURRENT AS-BUILT PACKAGE METRICS");
  drawString(20.0f, (yy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  if (pack->duplicateError)
    {
      snprintf(str, STR_LENGTH, "Duplicate sequence number, ignoring package");
      drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
      *wy = yy;
      return;
    }
  snprintf(str, STR_LENGTH, "Package sequence number: #%d", pack->sequence);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "%s",
	   (pack->sequenceError ? "Sequence error!" : "No Sequence error"));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "%s", 
	   (pack->extraError ? "Extra error!" : "No extra error"));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "%s",
	   (pack->duplicateError ? "Duplicate error!" : "No duplicate error"));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "%s",
	   (pack->idError ? "Id error!" : "No id error"));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  if (pack->duplicateError || pack->extraError)
    snprintf(str, STR_LENGTH, "Position error: not applicable");
  else
    snprintf(str, STR_LENGTH, "Position error: %.4f meters",
	     pack->positionError);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  *wy = yy;
}
*/

/********************************************************************/

/* PalletViewer::printAsBuiltText

Returned Value: none

Called By: displayAsBuiltMetricsWindow (in view.cc)

This prints the as-built metrics that have been calculated by
PalletViewer::init. The text is printed in the as-built metrics
window. The size and position of the text do not change if the size of
the metrics window is changed. Instead, if the window is made larger
there is more blank space, and if the window is made smaller, some of
the text is no longer visible. The text is anchored at the upper left
corner of the metrics window.

*/

/*
void PalletViewer::printAsBuiltText( *//* ARGUMENTS                 *//*
 int height)                         *//* side of screen, in pixels *//*
{
  char str[STR_LENGTH];   // string to print in
  BuiltPackage * pack;    // package to get data from
  float wy;               // Y value of line being printed

  glColor3f(1.0f, 1.0f, 1.0f);
  wy = (float)height;

  if (countAsBuilt > 0)
    {
      pack = &(asBuilt.packages[countAsBuilt - 1]);
      printAsBuiltPackageText(pack, &wy);
      printAsBuiltStackText(pack, &wy);
    }
  snprintf(str, STR_LENGTH, "SETTINGS");
  drawString(20.0f, (wy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Grid spacing: %.4f meters", spacing);
  drawString(20.0f, (wy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Tolerance: %.4f millimeters", tolerance);
  drawString(20.0f, (wy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
}
*/

/********************************************************************/

/* PalletViewer::printAsBuiltStackText

Returned Value: none

Called By: PalletViewer::printAsBuiltText

This prints the middle section of the as-built metrics window, which
gives metrics for the entire stack, up to and including the most recently
loaded package.

*/

/*
void PalletViewer::printAsBuiltStackText( *//* ARGUMENTS                    *//*
 BuiltPackage * pack,              *//* Package to print from               *//*
 float * wy)                       *//* Y-value on screen at which to print *//*
{
  char str[STR_LENGTH];  // string to print in
  float yy;
  int totalErrors;

  yy = *wy;
  if (countAsBuilt == asBuilt.packages.size())
    snprintf(str, STR_LENGTH, "FINISHED AS-BUILT STACK METRICS");
  else
    snprintf(str, STR_LENGTH, "CURRENT AS-BUILT STACK METRICS");
  drawString(20.0f, (yy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Sequence errors: %d", pack->stackSequenceErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Duplicate errors: %d", pack->stackDuplicateErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Extra errors: %d", pack->stackExtraErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Id errors: %d", pack->stackIdErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Position error maximum: %.4f",
	   pack->stackMaxPositionError);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Position error mean: %.4f meters",
	   pack->stackPositionErrorMean);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Position error variance: %.4f",
	   pack->stackPositionErrorVariance);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  totalErrors = (pack->stackSequenceErrors +
		 pack->stackDuplicateErrors +
		 pack->stackExtraErrors +
		 pack->stackIdErrors);
  if (countAsBuilt == asBuilt.packages.size())
    {
      snprintf(str, STR_LENGTH, "Planned packages missing errors: %d",
	       missingPlanned);
      drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
      totalErrors += missingPlanned;
    }
  snprintf(str, STR_LENGTH, "Total non-position errors: %d", totalErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  *wy = yy;
}
*/

/********************************************************************/

/* PalletViewer::printAsPlannedPackageText

Returned Value: none

Called By:  PalletViewer::printAsPlannedText

This prints the top section of the as-planned metrics window, which
gives metrics for the most recently loaded package.

*/

/*
void PalletViewer::printAsPlannedPackageText( *//* ARGUMENTS                  *//*
 Package * pack,                     *//* Package to print                    *//*
 float * wy)                         *//* Y-value on screen at which to print *//*
{
  char str[STR_LENGTH];                // string to print in
  std::list<int>::iterator iter;       // iterator for intersections list
  std::list<AreaData*>::iterator ator; // iterator for ups and downs lists
  int k;                               // counter for str
  int n;                               // counter for loading errors
  float yy;                              // surrogate for wy

  yy = *wy;
  snprintf(str, STR_LENGTH, "CURRENT AS-PLANNED PACKAGE METRICS");
  drawString(20.0f, (yy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Package sequence number: #%d%s",
	   pack->pack_sequence, (pack->sequenceError ? " error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);

  snprintf(str, STR_LENGTH, "SKU id number: #%d%s", pack->article.id,
	   (pack->orderError ? " error! not ordered" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  
  k = snprintf(str, STR_LENGTH, "Connected below to: %d",
	       (int)pack->downs.size());
  if (pack->downs.size() > 0)
    {
      for (ator = pack->downs.begin(); ator != pack->downs.end(); ator++)
	k += snprintf(str + k, STR_LENGTH - k, " #%d",
		      (*ator)->pack->pack_sequence);
    }
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  
  snprintf(str, STR_LENGTH, "Overlap fraction: %.4lf%s", pack->overlapFraction,
	   ((pack->overlapFraction < MINIMUM_OVERLAP) ? " error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  
  snprintf(str, STR_LENGTH,
	   "X hangs: +X %.1lf mm %s, -X %.1lf mm %s%s",
	   fabs(pack->xPlusOver), 
	   ((pack->xPlusOver < 0) ? "under" : "over"),
	   fabs(pack->xMinusOver),
	   ((pack->xMinusOver < 0) ? "under" : "over"),
	   (pack->overhangErrorX ? " error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH,
	   "Y hangs: +Y %.1lf mm %s, -Y %.1lf mm %s%s",
	   fabs(pack->yPlusOver), 
	   ((pack->yPlusOver < 0) ? "under" : "over"),
	   fabs(pack->yMinusOver),
	   ((pack->yMinusOver < 0) ? "under" : "over"),
	   (pack->overhangErrorY ? " error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  if (pack->ups.size() == 0)
    snprintf(str, STR_LENGTH, "Maximum pressure on top: 0");
  else
    {
      k = snprintf(str, STR_LENGTH,
		   "Maximum pressure on top: %.2lf Kg/m*m #%d",
		   pack->maxBoxPressure, pack->maxBoxSeqNo);
      if ((pack->article.robustness.maxPressureOnTop >= 0.0) &&
	  (pack->maxBoxPressure >
	   (1000.0 * pack->article.robustness.maxPressureOnTop)))
	snprintf(str + k, STR_LENGTH - k, " error!");
    }
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  
  k = snprintf(str, STR_LENGTH, "Intersection errors: %d",
	       (int)pack->inters.size());
  if (pack->inters.size() > 0)
    {
      for (iter = pack->inters.begin(); iter != pack->inters.end(); ++iter)
	{
	  if (*iter == 0)
	    k += snprintf(str + k, STR_LENGTH - k, " P");
	  else
	    k += snprintf(str + k, STR_LENGTH - k, " #%d", *iter);
	}
    }
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  
  k = snprintf(str, STR_LENGTH, "Loading order errors: %d",
	       pack->loadingErrors);
  if (pack->loadingErrors > 0)
    { // errors are at end of downs list
      for (n = pack->downs.size(), ator = pack->downs.begin();
	   n > pack->loadingErrors; n--, ++ator); // skip the beginning
      for ( ; ator != pack->downs.end(); ++ator)
	k += snprintf(str + k, STR_LENGTH - k, " #%d",
		      (*ator)->pack->pack_sequence);
    }
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  *wy = yy;
}
*/

/***********************************************************************/

/* PalletViewer::printAsPlannedText

Returned Value: none

Called By: displayAsPlannedMetricsWindow (in view.cc)

This prints the as-planned metrics that have been calculated by
PalletViewer::init.  The text is printed in the as-planned metrics
window. The size and position of the text do not change if the size of
the metrics window is changed. Instead, if the window is made larger
there is more blank space, and if the window is made smaller, some of
the text is no longer visible. The text is anchored at the upper left
corner of the metrics window.

*/

/*
void PalletViewer::printAsPlannedText( *//* ARGUMENTS                 *//*
 int height)                           *//* side of screen, in pixels *//*
{
  char str[STR_LENGTH];   // string to print in
  Package * pack;         // package to get data from
  float wy;               // Y value of line being printed

  glColor3f(1.0f, 1.0f, 1.0f);
  wy = (float)height;

  if (countAsPlanned > 0)
    {
      pack = &(cpallet.packages[countAsPlanned - 1]);
      printAsPlannedPackageText(pack, &wy);
      printAsPlannedStackText(pack, & wy);
    }
  snprintf(str, STR_LENGTH, "SETTINGS");
  drawString(20.0f, (wy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Grid spacing: %.4f meters", spacing);
  drawString(20.0f, (wy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Tolerance: %.4f millimeters", tolerance);
  drawString(20.0f, (wy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Scoring file: %s ", scoringFile);
  drawString(20.0f, (wy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
}
*/

/********************************************************************/

/* PalletViewer::printAsPlannedStackText

Returned Value: none

Called By: PalletViewer::printAsPlannedText

This prints the middle section of the as-planned metrics window, which
gives metrics for the entire stack, up to and including the most recently
loaded package. Two items (the number of ordered packages that are missing and
the score for the pallet) are printed only after all as-planned packages
have been loaded.

The "yy -= 20.0f" and "yy -= 15.0f" items give the amount of vertical
space before the next line is printed.

*/

/*
void PalletViewer::printAsPlannedStackText( *//* ARGUMENTS                  *//*
 Package * pack,                   *//* Package to print from               *//*
 float * wy)                       *//* Y-value on screen at which to print *//*
{
  char str[STR_LENGTH];  // string to print in
  float yy;

  yy = *wy;
  if (countAsPlanned == cpallet.packages.size())
    snprintf(str, STR_LENGTH, "FINISHED AS-PLANNED STACK METRICS");
  else
    snprintf(str, STR_LENGTH, "CURRENT AS-PLANNED STACK METRICS");
  drawString(20.0f, (yy -= 20.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Packages on stack: %d of %d",
	   countAsPlanned, (int)cpallet.packages.size());
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Stack weight: %.3f Kg%s",
	   pack->stackWeight,
	   (pack->stackWeightErrors ? " Error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Stack height: %.3lf m%s",
	   pack->stackHeight,
	   (pack->stackHeightErrors ? " Error!" : ""));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Volume of boxes: %.4lf cubic m",
	   pack->stackBoxVolume);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Stack storage volume: %.4lf cubic m",
	   pack->stackStorageVolume);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Volume density: %.4f", pack->stackDensity);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Pallet average overlap fraction: %.2f",
	   pack->stackOverlapFraction);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Pallet average connections below: %.2f",
	   pack->stackAverageConnects);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "COG height: %.4f m", pack->cogZ);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "COG relative offsets: X%+.4f Y%+.4f",
	   pack->cogRelX, pack->cogRelY);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH,
	   "X hangs: +X %.1lf mm %s, -X %.1lf mm %s",
	   fabs(pack->stackXPlusOver), 
	   ((pack->stackXPlusOver < 0) ? "under" : "over"),
	   fabs(pack->stackXMinusOver),
	   ((pack->stackXMinusOver < 0) ? "under" : "over"));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH,
	   "Y hangs: +Y %.1lf mm %s, -Y %.1lf mm %s",
	   fabs(pack->stackYPlusOver), 
	   ((pack->stackYPlusOver < 0) ? "under" : "over"),
	   fabs(pack->stackYMinusOver),
	   ((pack->stackYMinusOver < 0) ? "under" : "over"));
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  if (countAsPlanned == cpallet.packages.size())
    {
      snprintf(str, STR_LENGTH, "Ordered packages not on pallet: %d",
	       missingOrdered);
      drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
    }
  snprintf(str, STR_LENGTH, "Total sequence errors: %d",
	   pack->stackSequenceErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total unordered package errors: %d",
	   pack->stackOrderErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total overhang errors: %d",
	   pack->stackOverhangErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total overlap errors: %d",
	   pack->stackOverlapErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total intersection errors: %d",
	   pack->stackInters);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total loading order errors: %d",
	   pack->stackLoadingErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total maximum pressure errors: %d",
	   pack->stackPressureErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  snprintf(str, STR_LENGTH, "Total errors: %d", pack->stackTotalErrors);
  drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
  if (countAsPlanned == cpallet.packages.size())
    {
      snprintf(str, STR_LENGTH, "Score: %.2f", score);
      drawString(20.0f, (yy -= 15.0f), GLUT_BITMAP_HELVETICA_10, str);
    }
  *wy = yy;
}
*/

/***********************************************************************/

/* palletViewer::recalculate

Returned Value: none

Called By: keyboard (in view.cc) - change argument will be 1 or -1

This is called if the f or g key is pressed. It may change the
countAsBuilt and/or the countAsPlanned by the change amount, depending
on the circumstances as described below. Either the as-built stack or
the as-planned stack might have more packages.

A. If countAsPlanned is larger than the number of packages on the as-built
stack:
A1. If countAsPlanned is larger than zero and change is -1, subtract 1
from countAsPlanned.
A2. Otherwise, if countAsPlanned is less than the size of the as-planned
stack and change is +1, add 1 to countAsPlanned.

B. Otherwise, if countAsBuilt is larger than the number of packages on the
as-planned stack:
B1. If countAsBuilt is larger than zero and change is -1, subtract 1
from countAsBuilt.
B2. Otherwise, if countAsBuilt is less than the size of the as-built
stack and change is +1, add 1 to countAsBuilt.

C. Otherwise, 
C1. countAsBuilt should equal countAsPlanned. Check that, and if the check
fails, print an error message and exit.
C2. Otherwise, do as described in A1, A2, B1, and B2.

*/

void PalletViewer::recalculate( /* ARGUMENTS */
 int change)                    /* 1, or -1  */
{
  if (countAsPlanned > asBuilt.packages.size())
    {
      if (((countAsPlanned > 0) && (change == -1)) ||
	  ((countAsPlanned < cpallet.packages.size()) && (change == 1)))
	countAsPlanned += change;
    }
  else if (countAsBuilt > cpallet.packages.size())
    {
      if (((countAsBuilt > 0) && (change == -1)) ||
	  ((countAsBuilt < asBuilt.packages.size()) && (change == 1)))
	countAsBuilt += change;
    }
  else 
    {
      if (countAsPlanned != countAsBuilt)
	{
	  fprintf(stderr, "bug in recalculate\n");
	  exit(1);
	}
      if (((countAsBuilt > 0) && (change == -1)) ||
	  ((countAsBuilt < asBuilt.packages.size()) && (change == 1)))
	countAsBuilt += change;
      if (((countAsPlanned > 0) && (change == -1)) ||
	  ((countAsPlanned < cpallet.packages.size()) && (change == 1)))
	countAsPlanned += change;
    }
}

/********************************************************************/

/* PalletViewer::redraw

Returned Value: none

Called By: buildDisplayList (in view.cc)

This draws the pallet as planned in the packlist. If there is an asBuilt,
it also draws that.

The package numbers this uses are sequential starting with 1 (since
the PackSequence numbers start at 1, not 0). This is assuming the
PackSequence numbers are sequential. Otherwise, the package numbers
displayed will not match the numbers in the packlist.

The origin of a pallet is in its lower left corner (when viewing
the XY plane in the usual orientation (+X right, +Y up) from above
(+Z).

The origin of the graphics coordinate system is at the center of the grid.
Two meters in real space is one unit in the graphics coordinate system.
The grid is one unit by one unit in the graphics coordinate system,
which is 2 meters by 2 meters in real space.

The packlist pallet is offset into the third quadrant of the graphics
coordinate system, so that the upper right corner of the pallet is at
the origin of the graphics coordinate system. 

The asBuilt pallet is offset into the first quadrant, translated 0.1
meters in real space towards +X and +Y so that the origin of the
as-built pallet coordinate system is one grid square up and to the
right of the center of the pallet.

This function is a little strange in that the parameters to insertBox
are assumed to be in millimeters in real space while the parameters
to glTranslated are in graphics space units (which are scaled down
from millimeters by the scale factor or scaled down from meters by
a factor of 1000 times scale. The as-built values are in meters.

The graphics operations (3 rotations, 1 translation) for as-built in
OpenGL are performed in the opposite order from how they appear in the
code. Thus, the order is:
  - insert a box of the correct size with the origin of the box
    coordinate system (which is at the middle of the top of the box)
    at the origin of the graphics coordinate system. In the box coordinate
    system, length is along the X axis, and height is along the Z axis.
  - rotate the box around the X axis of the graphics coordinate system
    by roll
  - rotate the box around the Y axis of the graphics coordinate system
    by pitch
  - rotate the box around the Z axis of the graphics coordinate system
    by yaw
  - translate the box to the correct XYZ location relative to the as-built
    pallet.

The color for each package in the packlist has already been assigned
and stored in the package when this function is called, so the color
is simply retrieved from the package.

The color for each as-built package has also already been assigned, and
is also retrieved from the package.

If there are more as-planned packages than as-built packages, the first
"for" loop just stops drawing as-built packages when all have been drawn.

If there are more as-built packages than as-planned packages, the second
"for" loop draws the extra as-built packages. These are all necessarily
in error, so they will be drawn as small gray boxes.

*/

/*
void PalletViewer::redraw()
{
  float radToDeg = 57.29577958f; // for asBuilt
  double offsetX;   // for as-planned, in millimeters
  double offsetY;   // for as-planned, in millimeters
  double asOffsetX; // for asBuilt, in meters
  double asOffsetY; // for asBuilt, in meters
  col boxColor;
  Package * pack;
  BuiltPackage * asBuiltPack;
  Article * art;
  unsigned int i;
  std::map<int, col>::iterator iter;

  // draw the pallet in the third quadrant with its top on the XY plane
  offsetX = (-1.0 * cpallet.dimensions.length);
  offsetY = (-1.0 * cpallet.dimensions.width);
  
  boxColor.r = 0.5f;
  boxColor.g = 0.5f;
  boxColor.b = 0.5f;
  insertBox(boxColor, offsetX, offsetY, -40.0, 0.0, 0.0, 0.0, true);
  if (asBuilt.packages.size())
    {
      asOffsetX = spacing;
      asOffsetY = ((9.0 * spacing) - (cpallet.dimensions.width / 1000.0));
      boxColor.r = 0.3f;
      boxColor.g = 0.3f;
      boxColor.b = 0.3f;
      insertBox(boxColor,
		(double)(spacing * 1000), (asOffsetY * 1000), -40.0,
		(double)((spacing * 1000) + cpallet.dimensions.length),
		((asOffsetY * 1000) + cpallet.dimensions.width),
		0.0, true);
    }
  for (i = 0; i < countAsPlanned; i++)
    {
      // draw box on pallet as planned
      pack = &(cpallet.packages[i]);
      insertBox(pack->color, (offsetX + pack->minX), (offsetY + pack->minY),
		pack->minZ, (offsetX + pack->maxX), (offsetY + pack->maxY),
		pack->maxZ, true);
      // draw box on pallet as built
      if ((i < asBuilt.packages.size()) &&
	  (!asBuilt.packages[i].duplicateError))
	{
	  asBuiltPack = &(asBuilt.packages[i]);
	  art = &(asBuiltPack->article);
	  glPushMatrix();
	  glTranslated((scale * 1000.0f * (asOffsetX + asBuiltPack->x)),
		       (scale * 1000.0f * (asOffsetY + asBuiltPack->y)),
		       (scale * 1000.0f * asBuiltPack->z));
	  glRotated((float)(asBuiltPack->yaw)   * radToDeg, 0.0f, 0.0f, 1.0f);
	  glRotated((float)(asBuiltPack->pitch) * radToDeg, 0.0f, 1.0f, 0.0f);
	  glRotated((float)(asBuiltPack->roll)  * radToDeg, 1.0f, 0.0f, 0.0f);
	  insertBox(asBuiltPack->color,
		    (art->length)/-2.0, (art->width)/-2.0, (art->height)/-2.0, 
		    (art->length)/ 2.0, (art->width)/ 2.0, (art->height)/ 2.0,
		    true);
	  glPopMatrix();
	}
    }
  if (asBuilt.packages.size() > countAsPlanned)
    {
      for ( ; i < countAsBuilt; i++)
	{
	  if (!asBuilt.packages[i].duplicateError)
	    {
	      asBuiltPack = &(asBuilt.packages[i]);
	      art = &(asBuiltPack->article);
	      glPushMatrix();
	      glTranslated((scale * 1000.0f * (asOffsetX + asBuiltPack->x)),
			   (scale * 1000.0f * (asOffsetY + asBuiltPack->y)),
			   (scale * 1000.0f * asBuiltPack->z));
	      glRotated((float)(asBuiltPack->yaw) * radToDeg, 0.0f, 0.0f, 1.0f);
	      glRotated((float)(asBuiltPack->pitch) * radToDeg,0.0f,1.0f, 0.0f);
	      glRotated((float)(asBuiltPack->roll)* radToDeg, 1.0f, 0.0f, 0.0f);
	      insertBox(asBuiltPack->color,
			(art->length)/-2.0, (art->width)/-2.0,
			(art->height)/-2.0, (art->length)/ 2.0,
			(art->width)/ 2.0, (art->height)/ 2.0, true);
	      glPopMatrix();
	    }
	}
    }
}
*/

/********************************************************************/

/* valuate

Returned Value: double
  This returns the result of applying the valueFunction to the val.

Called By: findAsPlannedScore

A value function has one of the following three forms (graphs on a
standard Cartesian plane), depending on the value of taperSide. In all
three, the upper value is 1, and the lower value is zero.

              ____
minus    ____/

         ____
plus         \____

          ___
both ____/   \____


The slope of the slopes in the functions is controlled by the value of
taper in the value function.

For "plus" and "minus", the "best" value is is the X value of the
point at the upper end of the slope. For "both" the "best" value is
the X value of the point in the middle of the mesa.

*/

double PalletViewer::valuate( /* ARGUMENTS                 */
 valueFunctionType * fun,     /* the value function to use */
 double val)                  /* the input X value         */
{
  static double best;
  static double taper;
  static double right;
  static double left;

  best = *(fun->bestValue);
  taper = *(fun->taper->val);
  if (strcmp(fun->taperSide->val, "minus") == 0)
    {
      if (taper == 0.0)
	return ((val >= best) ? 1.0 : 0.0);
      else if (val < (best - taper))
	return 0.0;
      else if (val > best)
	return 1.0;
      else // in between
	return (1.0 - ((best - val) / taper));
    }
  else if (strcmp(fun->taperSide->val, "plus") == 0)
    {
      if (taper == 0.0)
	return ((val <= best) ? 1.0 : 0.0);
      else if (val < best)
	return 1.0;
      else if (val > (best + taper))
	return 0.0;
      else // in between
	return (1.0 - ((val - best) / taper));
    }
  else if (strcmp(fun->taperSide->val, "both") == 0)
    {
      right = (best + (*(fun->width->val) / 2));
      left  = (best - (*(fun->width->val) / 2));
      if (taper == 0.0)
	return ((val < left) ? 0.0 : (val > right) ? 0.0 : 1.0);
      else if (val < (left - taper))
	return 0.0;
      else if (val < left)
	return (1.0 - ((left - val) / taper));
      else if (val < right)
	return 1.0;
      else if (val < (right + taper))
	return (1.0 - ((val - right) / taper));
      else // if (val >= (right + taper))
	return 0.0;
    }
  else
    {
      fprintf(stderr, "bad taperSide %s in a valueFunctionType\n",
	      fun->taperSide->val);
      exit(1);
    }
  return 0.0;
}

/********************************************************************/
