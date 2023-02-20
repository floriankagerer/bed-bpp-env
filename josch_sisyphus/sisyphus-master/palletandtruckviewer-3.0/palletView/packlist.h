/*
 * Class structure to parse input orders for a mixed pallet.
 * KUKA input file definition for orders is used here.
 *
 * Author: Pushkar Kolhe
*/

#ifndef PACKLIST_H_
#define PACKLIST_H_

#include <vector>
#include <string.h>
#include "xml_parser.h"

/********************************************************************/

class Robustness
{
 public:
  double maxPressureOnTop;

  Robustness() {}
  ~Robustness() {}
  int parse(std::string text);
};

/********************************************************************/

class Article
{
 public:
  unsigned int id;
  std::string description;
  unsigned int type;
  unsigned int length;
  unsigned int width;
  unsigned int height;
  unsigned int weight;
  unsigned int family;
  Robustness robustness;

  Article() {}
  ~Article() {}
  int parse(std::string text);
};

/********************************************************************/

class Barcode
{
 public:
  std::string code;

  Barcode() {}
  ~Barcode() {}
  int parse(std::string text);
};

/********************************************************************/

class OrderLine
{
 public:
  unsigned int orderlineno;
  Article article;
  std::vector<Barcode> barcode;

  OrderLine() {}
  ~OrderLine() {}
  unsigned n_barcode() { return barcode.size(); }
  int parse(std::string text);
};

/********************************************************************/

class Restrictions
{
 public:
  bool familygrouping;
  bool ranking;

  Restrictions()
    {
      familygrouping = false;
      ranking = false;
    }
  ~Restrictions() {}
  int parse(std::string text);
};

/********************************************************************/

class Order
{
 public:
  unsigned int id;
  std::string description;
  Restrictions restriction;
  std::vector <OrderLine> orderline;

  Order() {}
  ~Order() {}
  unsigned int n_orderline() { return orderline.size(); }
  int parse(std::string text);

};

/********************************************************************/

class Pallet
{
 public:
  int palletnumber;
  std::string description;
  int length;
  int width;
  int maxloadheight;
  int maxloadweight;
  int overhanglength;
  int overhangwidth;

  Pallet() {}
  ~Pallet() {}
  int parse(std::string text);
};

/********************************************************************/

class OrderXML
{
 public:
  std::vector<Pallet> pallet;
  unsigned int n_pallet() { return pallet.size(); }
  Order order;

  OrderXML() {}
  ~OrderXML() {}
  int parse(const char* filename, int debug_p = 0, int debug_o = 0);
};

/********************************************************************/

Order readOrder(const char* filename);
Pallet readPallet(const char* filename);

/********************************************************************/

#endif

