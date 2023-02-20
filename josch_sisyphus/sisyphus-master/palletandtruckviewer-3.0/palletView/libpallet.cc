#include "palletViewer.h"

extern "C"
{
  double evaluate(char* orderFile, char* packlistFile, char* scoringFile)
  {
    return PalletViewer::evaluate(orderFile, packlistFile, scoringFile);
  }
}
