/*********************************************************************/

#ifndef SCOREASPLANNED_HH
#define SCOREASPLANNED_HH
#include <stdio.h>
#include <list>

/*********************************************************************/

class ScoreAsPlannedBase;
class ScoreAsPlannedFile;
class UrnLocation;
class XmlVersion;

class AttributeValuePair;

class factorType;
class factorValueOpt;
class factorValueReq;
class nonNegativeReal;
class scoreAsPlannedType;
class taperSideType;
class valueFunctionType;

/*********************************************************************/

class ScoreAsPlannedBase
{
public:
  ScoreAsPlannedBase();
  virtual ~ScoreAsPlannedBase();
  virtual void printSelf(FILE * outFile) = 0;
  static void doSpaces(int change, FILE * outFile);
};

/*********************************************************************/

class ScoreAsPlannedFile :
  public ScoreAsPlannedBase
{
public:
  ScoreAsPlannedFile();
  ScoreAsPlannedFile(
    XmlVersion * versionIn,
    scoreAsPlannedType * ScoreAsPlannedIn);
  ~ScoreAsPlannedFile();
  void printSelf(FILE * outFile);

  XmlVersion * version;
  scoreAsPlannedType * ScoreAsPlanned;
};

/*********************************************************************/

class UrnLocation :
  public ScoreAsPlannedBase
{
public:
  UrnLocation();
  UrnLocation(
    char * locationIn);
  ~UrnLocation();
  void printSelf(FILE * outFile);

  char * location;
};

/*********************************************************************/

class XmlVersion :
  public ScoreAsPlannedBase
{
public:
  XmlVersion();
  XmlVersion(bool hasEncodingIn);
  ~XmlVersion();
  void printSelf(FILE * outFile);

  bool hasEncoding;
};

/*********************************************************************/
/*********************************************************************/

class AttributePair
{
public:
  AttributePair();
  AttributePair(
    int nameIn,
    char * valIn);
  ~AttributePair();

  int name;
  char * val;
};

/*********************************************************************/
/*********************************************************************/

class factorType :
  public ScoreAsPlannedBase
{
public:
  factorType();
  factorType(
    bool * isAdditiveIn,
    unsigned int * weightIn);
  ~factorType();
  void printSelf(FILE * outFile);

  bool * isAdditive;
  unsigned int * weight;
};

/*********************************************************************/

class factorValueOpt :
  public factorType
{
public:
  factorValueOpt();
  factorValueOpt(
    bool * isAdditiveIn,
    unsigned int * weightIn,
    valueFunctionType * valueFunctionIn);
  ~factorValueOpt();
  void printSelf(FILE * outFile);

  valueFunctionType * valueFunction;

  bool printTypp;
};

/*********************************************************************/

class factorValueReq :
  public factorType
{
public:
  factorValueReq();
  factorValueReq(
    bool * isAdditiveIn,
    unsigned int * weightIn,
    valueFunctionType * valueFunctionIn);
  ~factorValueReq();
  void printSelf(FILE * outFile);

  valueFunctionType * valueFunction;

  bool printTypp;
};

/*********************************************************************/

class nonNegativeReal :
  public ScoreAsPlannedBase
{
public:
  nonNegativeReal();
  nonNegativeReal(
    double * valIn);
  ~nonNegativeReal();
  void printSelf(FILE * outFile);
  bool checkVal();

  double * val;
  bool bad;
};

/*********************************************************************/

class scoreAsPlannedType :
  public ScoreAsPlannedBase
{
public:
  scoreAsPlannedType();
  scoreAsPlannedType(
    UrnLocation * locationIn,
    factorValueOpt * rightStuffIn,
    factorValueReq * overhangIn,
    factorValueOpt * volumeDensityIn,
    factorValueOpt * overlapFractionIn,
    factorValueReq * connectionsBelowIn,
    factorValueOpt * cogInverseRelativeHeightIn,
    factorValueOpt * cogRelativeOffsetIn);
  ~scoreAsPlannedType();
  void printSelf(FILE * outFile);

  UrnLocation * location;
  factorValueOpt * rightStuff;
  factorValueReq * overhang;
  factorValueOpt * volumeDensity;
  factorValueOpt * overlapFraction;
  factorValueReq * connectionsBelow;
  factorValueOpt * cogInverseRelativeHeight;
  factorValueOpt * cogRelativeOffset;
};

/*********************************************************************/

class taperSideType :
  public ScoreAsPlannedBase
{
public:
  taperSideType();
  taperSideType(
    char * valIn);
  ~taperSideType();
  void printSelf(FILE * outFile);
  bool checkVal();

  char * val;
  bool bad;
};

/*********************************************************************/

class valueFunctionType :
  public ScoreAsPlannedBase
{
public:
  valueFunctionType();
  valueFunctionType(
    double * bestValueIn,
    nonNegativeReal * widthIn,
    nonNegativeReal * taperIn,
    taperSideType * taperSideIn);
  ~valueFunctionType();
  void printSelf(FILE * outFile);

  double * bestValue;
  nonNegativeReal * width;
  nonNegativeReal * taper;
  taperSideType * taperSide;
};

/*********************************************************************/

#endif // SCOREASPLANNED_HH
