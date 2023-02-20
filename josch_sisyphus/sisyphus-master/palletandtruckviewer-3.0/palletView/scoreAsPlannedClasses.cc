/*********************************************************************/

#include <stdio.h>             // for printf, etc.
#include <string.h>            // for strdup
#include <stdlib.h>            // for exit
#include <list>
#include "scoreAsPlannedClasses.hh"
#include "scoreAsPlannedYACC.hh"

#define INDENT 2

/*********************************************************************/

/* class ScoreAsPlannedBase

*/

ScoreAsPlannedBase::ScoreAsPlannedBase() {}

ScoreAsPlannedBase::~ScoreAsPlannedBase() {}

void ScoreAsPlannedBase::doSpaces(int change, FILE * outFile)
{
  static int spaces = 0;
  static int n;

  if (change)
    spaces += change;
  else
    {
      for (n = 0; n < spaces; n++)
        fputc(' ', outFile);
    }
}

/*********************************************************************/

/* class ScoreAsPlannedFile

*/

ScoreAsPlannedFile::ScoreAsPlannedFile() {}

ScoreAsPlannedFile::ScoreAsPlannedFile(
  XmlVersion * versionIn,
  scoreAsPlannedType * ScoreAsPlannedIn)
{
  version = versionIn;
  ScoreAsPlanned = ScoreAsPlannedIn;
}

ScoreAsPlannedFile::~ScoreAsPlannedFile() {}

void ScoreAsPlannedFile::printSelf(FILE * outFile)
{
  version->printSelf(outFile);
  fprintf(outFile, "<scoreAsPlanned\n");
  ScoreAsPlanned->printSelf(outFile);
  fprintf(outFile, "</scoreAsPlanned>\n");
}

/*********************************************************************/

/* class UrnLocation

*/

UrnLocation::UrnLocation() {}

UrnLocation::UrnLocation(
  char * locationIn)
{
  location = locationIn;
}

UrnLocation::~UrnLocation() {}

void UrnLocation::printSelf(FILE * outFile)
{
  fprintf(outFile, "  xsi:schemaLocation=\"%s\"", location);
}

/*********************************************************************/

/* class XmlVersion

*/

XmlVersion::XmlVersion() {}

XmlVersion::XmlVersion(bool hasEncodingIn)
{
  hasEncoding = hasEncodingIn;
}

XmlVersion::~XmlVersion() {}

void XmlVersion::printSelf(FILE * outFile)
{
  if (hasEncoding)
    fprintf(outFile, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
  else
    fprintf(outFile, "<?xml version=\"1.0\"?>\n");
}

/*********************************************************************/
/*********************************************************************/

/* class AttributePair

*/

AttributePair::AttributePair() {}

AttributePair::AttributePair(
 int nameIn,
 char * valIn)
{
  name = nameIn;
  val = valIn;
}

AttributePair::~AttributePair() {}

/*********************************************************************/
/*********************************************************************/

/* class factorType

*/

factorType::factorType() {}

factorType::factorType(
 bool * isAdditiveIn,
 unsigned int * weightIn)
{
  isAdditive = isAdditiveIn;
  weight = weightIn;
}

factorType::~factorType() {}

void factorType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<isAdditive>%s</isAdditive>\n",
          ((*isAdditive == true) ? "true" : "false"));
  doSpaces(0, outFile);
  fprintf(outFile, "<weight>%u</weight>\n", *weight);
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class factorValueOpt

*/

factorValueOpt::factorValueOpt() {}

factorValueOpt::factorValueOpt(
 bool * isAdditiveIn,
 unsigned int * weightIn,
 valueFunctionType * valueFunctionIn) :
  factorType(isAdditiveIn, weightIn)
{
  valueFunction = valueFunctionIn;
  printTypp = false;
}

factorValueOpt::~factorValueOpt() {}

void factorValueOpt::printSelf(FILE * outFile)
{
  if (printTypp)
    fprintf(outFile, " xsi:type=\"factorValueOpt\"");
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<isAdditive>%s</isAdditive>\n",
          ((*isAdditive == true) ? "true" : "false"));
  doSpaces(0, outFile);
  fprintf(outFile, "<weight>%u</weight>\n", *weight);
  if (valueFunction)
    {
      doSpaces(0, outFile);
      fprintf(outFile, "<valueFunction");
      valueFunction->printSelf(outFile);
      doSpaces(0, outFile);
      fprintf(outFile, "</valueFunction>\n");
    }
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class factorValueReq

*/

factorValueReq::factorValueReq() {}

factorValueReq::factorValueReq(
 bool * isAdditiveIn,
 unsigned int * weightIn,
 valueFunctionType * valueFunctionIn) :
  factorType(isAdditiveIn, weightIn)
{
  valueFunction = valueFunctionIn;
  printTypp = false;
}

factorValueReq::~factorValueReq() {}

void factorValueReq::printSelf(FILE * outFile)
{
  if (printTypp)
    fprintf(outFile, " xsi:type=\"factorValueReq\"");
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<isAdditive>%s</isAdditive>\n",
          ((*isAdditive == true) ? "true" : "false"));
  doSpaces(0, outFile);
  fprintf(outFile, "<weight>%u</weight>\n", *weight);
  doSpaces(0, outFile);
  fprintf(outFile, "<valueFunction");
  valueFunction->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</valueFunction>\n");
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class nonNegativeReal

*/

nonNegativeReal::nonNegativeReal() {}

nonNegativeReal::nonNegativeReal(
 double * valIn)
{
  val = valIn;
  bad = checkVal();
}

nonNegativeReal::~nonNegativeReal() {}

void nonNegativeReal::printSelf(FILE * outFile)
{
  fprintf(outFile, "%f", *val);
}

bool nonNegativeReal::checkVal()
{
  return ((*val < 0.0));
}

/*********************************************************************/

/* class scoreAsPlannedType

*/

scoreAsPlannedType::scoreAsPlannedType() {}

scoreAsPlannedType::scoreAsPlannedType(
 UrnLocation * locationIn,
 factorValueOpt * rightStuffIn,
 factorValueReq * overhangIn,
 factorValueOpt * volumeDensityIn,
 factorValueOpt * overlapFractionIn,
 factorValueReq * connectionsBelowIn,
 factorValueOpt * cogInverseRelativeHeightIn,
 factorValueOpt * cogRelativeOffsetIn)
{
  location = locationIn;
  rightStuff = rightStuffIn;
  overhang = overhangIn;
  volumeDensity = volumeDensityIn;
  overlapFraction = overlapFractionIn;
  connectionsBelow = connectionsBelowIn;
  cogInverseRelativeHeight = cogInverseRelativeHeightIn;
  cogRelativeOffset = cogRelativeOffsetIn;
}

scoreAsPlannedType::~scoreAsPlannedType() {}

void scoreAsPlannedType::printSelf(FILE * outFile)
{
  fprintf(outFile, "  xmlns=\"urn:Palletizing\"\n");
  fprintf(outFile,
          "  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n");
  location->printSelf(outFile);
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<rightStuff");
  rightStuff->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</rightStuff>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<overhang");
  overhang->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</overhang>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<volumeDensity");
  volumeDensity->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</volumeDensity>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<overlapFraction");
  overlapFraction->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</overlapFraction>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<connectionsBelow");
  connectionsBelow->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</connectionsBelow>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<cogInverseRelativeHeight");
  cogInverseRelativeHeight->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</cogInverseRelativeHeight>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<cogRelativeOffset");
  cogRelativeOffset->printSelf(outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "</cogRelativeOffset>\n");
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

/* class taperSideType

*/

taperSideType::taperSideType() {}

taperSideType::taperSideType(
 char * valIn)
{
  val = valIn;
  bad = checkVal();
}

taperSideType::~taperSideType() {}

void taperSideType::printSelf(FILE * outFile)
{
  fprintf(outFile, "%s", val);
}

bool taperSideType::checkVal()
{
  return (strcmp(val, "plus") &&
          strcmp(val, "minus") &&
          strcmp(val, "both"));
}

/*********************************************************************/

/* class valueFunctionType

*/

valueFunctionType::valueFunctionType() {}

valueFunctionType::valueFunctionType(
 double * bestValueIn,
 nonNegativeReal * widthIn,
 nonNegativeReal * taperIn,
 taperSideType * taperSideIn)
{
  bestValue = bestValueIn;
  width = widthIn;
  taper = taperIn;
  taperSide = taperSideIn;
}

valueFunctionType::~valueFunctionType() {}

void valueFunctionType::printSelf(FILE * outFile)
{
  fprintf(outFile, ">\n");
  doSpaces(+INDENT, outFile);
  doSpaces(0, outFile);
  fprintf(outFile, "<bestValue>%lf</bestValue>\n", *bestValue);
  doSpaces(0, outFile);
  fprintf(outFile, "<width>");
  width->printSelf(outFile);
  fprintf(outFile, "</width>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<taper>");
  taper->printSelf(outFile);
  fprintf(outFile, "</taper>\n");
  doSpaces(0, outFile);
  fprintf(outFile, "<taperSide>");
  taperSide->printSelf(outFile);
  fprintf(outFile, "</taperSide>\n");
  doSpaces(-INDENT, outFile);
}

/*********************************************************************/

