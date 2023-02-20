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
  \file packlist.cc
  
  \brief Parser for KUKA packlist XML file. Designed according to packlist XSD.
  \code CVS Status:
  $Author: dr_steveb $
  $Revision: 1.9 $
  $Date: 2011/02/24 16:47:28 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010 

*/

#ifdef MOASTSTATIC
#include "packlist.h"
#include "xml_parser.h"
#else
#include "packlist.h"
#include "xml_parser.h"
#endif
#include <stdlib.h>
#include <fstream>
#ifdef WIN32
#define uint unsigned int
#endif

/********************************************************************/

int Robustness::parse(
 std::string text)
{
  std::string s_maxPressureOnTop = xml_parse_tag(text, "MaxPressureOnTop");
  if(strlen(s_maxPressureOnTop.c_str()) > 0)
    maxPressureOnTop = atof(xml_parse_tag(text, "MaxPressureOnTop").c_str());
  else
    maxPressureOnTop = -1.0;
  return strlen(text.c_str());
}

/********************************************************************/

int Article::parse(
 std::string text)
{
  id = atoi(xml_parse_tag(text, "ID").c_str());
  type = atoi(xml_parse_tag(text, "Type").c_str());
  length = atoi(xml_parse_tag(text, "Length").c_str());
  width = atoi(xml_parse_tag(text, "Width").c_str());
  height = atoi(xml_parse_tag(text, "Height").c_str());
  family = atoi(xml_parse_tag(text, "Family").c_str());
  weight = atoi(xml_parse_tag(text, "Weight").c_str());
  description = xml_parse_tag(text, "Description");
  std::string s_robustness =  xml_parse_tag(text, "Robustness");
  if(strlen(s_robustness.c_str()) > 0)
    robustness.parse(s_robustness);
  else
    robustness.maxPressureOnTop = -1.0;
  return strlen(text.c_str());
}

/********************************************************************/

int Barcode::parse(
 std::string text)
{
  code = text;
  return strlen(text.c_str());
}

/********************************************************************/

int OrderLine::parse(
 std::string text)
{
  orderlineno = atoi(xml_parse_tag(text, "OrderLineNo").c_str());
  std::string s_article = xml_parse_tag(text, "Article");
  article.parse(s_article);
  int ret = 1;
  while(ret)
    {
      std::string s_barcode = xml_parse_tag(text, "Barcode");
      if(strlen(s_barcode.c_str()) > 0)
	{
	  Barcode b;
	  b.parse(s_barcode);
	  barcode.push_back(b);
	}
      ret = xml_parse_remove_first_tag(&text, "Barcode");
    }
  return strlen(text.c_str());
}

/********************************************************************/

int Restrictions::parse(
 std::string text)
{
  if(strcmp(xml_parse_tag(text, "FamilyGrouping").c_str(), "True") == 0)
    familygrouping = true;
  if(strcmp(xml_parse_tag(text, "Ranking").c_str(), "True") == 0)
    ranking = true;
  return strlen(text.c_str());
}

/********************************************************************/

int Order::parse(
 std::string text)
{
  int ret = 1;
  
  id = atoi(xml_parse_tag(text, "ID").c_str());
  description = xml_parse_tag(text, "Description");
  restriction.parse(xml_parse_tag(text, "Restrictions"));
  
  while(ret)
    {
      std::string s_order = xml_parse_tag(text, "OrderLine");
      if(strlen(s_order.c_str()) > 0)
	{
	  OrderLine o;
	  o.parse(s_order);
	  orderline.push_back(o);
	}
      ret = xml_parse_remove_first_tag(&text, "OrderLine");
    }
  
  return (ret && strlen(text.c_str()));
}

/********************************************************************/

int Pallet::parse(
 std::string text)
{
  int ret = 1;
  
  palletnumber = atoi(xml_parse_tag(text, "PalletNumber").c_str());
  description = xml_parse_tag(text, "Description");
  std::string dim_pallet = xml_parse_tag(text, "Dimensions");
  length = atoi(xml_parse_tag(dim_pallet, "Length").c_str());
  width = atoi(xml_parse_tag(dim_pallet, "Width").c_str());
  maxloadheight = atoi(xml_parse_tag(dim_pallet, "MaxLoadHeight").c_str());
  maxloadweight = atoi(xml_parse_tag(dim_pallet, "MaxLoadWeight").c_str());
  std::string overhang_pallet = xml_parse_tag(text, "Overhang");
  overhanglength = atoi(xml_parse_tag(overhang_pallet, "Length").c_str());
  overhangwidth = atoi(xml_parse_tag(overhang_pallet, "Width").c_str());


/*
  printf( "Dimensions: %s\n", xml_parse_tag(text,"Dimensions").c_str());
  printf( "Overhang: %s\n", xml_parse_tag(text, "Overhang").c_str());
 */
  printf( "PalletNumber: %d\n", palletnumber );
  printf( "Description: %s\n", description.c_str() );
  printf( "Length: %d\n", length );
  printf( "Width: %d\n", width );
  printf( "maxLoadHeight: %d\n", maxloadheight );
  printf( "maxloadweight: %d\n", maxloadweight );

  return (ret && strlen(text.c_str()));
}

/********************************************************************/

Order readOrder(
 const char* filename)
{
  std::ifstream ifs(filename);
  if(!ifs.is_open())
    {
      printf("%s File not found.\n Exiting.\n", filename);
      exit(1);
    }
  
  int buf_len = xml_parser_get_buffer_length(filename);
  char* orderlist_buf = (char*) malloc (buf_len + 1);
  ifs.read(orderlist_buf, buf_len);
  std::string orderlist_xml = orderlist_buf;
  
  Order order;
  order.parse(xml_parse_tag(orderlist_xml, "Order"));
  free(orderlist_buf);
  return order;
}

Pallet readPallet(
 const char* filename)
{
  std::ifstream ifs(filename);
  if(!ifs.is_open())
    {
      printf("%s File not found.\n Exiting.\n", filename);
      exit(1);
    }
  
  int buf_len = xml_parser_get_buffer_length(filename);
  char* pallet_buf = (char*) malloc (buf_len + 1);
  ifs.read(pallet_buf, buf_len);
  std::string pallet_xml = pallet_buf;
  
  Pallet pallet;
  pallet.parse(xml_parse_tag(pallet_xml, "Pallets"));
  free(pallet_buf);
  return pallet;
}

/********************************************************************/
