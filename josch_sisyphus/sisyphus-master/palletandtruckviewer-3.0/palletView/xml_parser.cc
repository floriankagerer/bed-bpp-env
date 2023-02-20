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
  \file xml_parser.cc

  \brief Parses XML files. Parses XML within given tags.
  \code CVS Status:
  $Author: tomrkramer $
  $Revision: 1.5 $
  $Date: 2011/03/18 14:02:05 $
  \endcode

  \author Stephen Balakirsky
  \date March 23, 2010
*/

#ifdef WIN32
#define snprintf sprintf_s
#endif

#include "xml_parser.h"
#include <fstream>
#include <stdlib.h>
#include <string.h>

/********************************************************************/

// Find file size

unsigned int xml_parser_get_buffer_length(
 const char * filename)
{
  std::ifstream is;
  unsigned int ret;

  is.open(filename);
  if(!is.is_open())
    return 0;
  is.seekg(0, std::ios::end);
  ret = (unsigned int)is.tellg();
  is.close();
  return ret;
}

/********************************************************************/

/* xml_parse_tag

Returned Value: std::string
  Suppose the tag text is foo. This returns the part of the text argument
  between the first occurrence of <foo> and the first occurrence after
  that of </foo>, if both occur. Otherwise, it returns an empty string.

Called By:

This is a bit kludgy in that it is not allowing any white space, except that
there may be a space immediately after "<foo", and in this case it accepts
any additional characters ending with > as the tag. For example, it will
accept <foo bar> as being the same thing as <foo>.

*/

std::string xml_parse_tag(
 std::string text,
 const char * tag)
{
  std::string ret("");
  int i_tag = strlen(tag);
  char* start = (char*) malloc(sizeof(tag) + 25);
  char* end = (char*) malloc(sizeof(tag) + 25);
  snprintf(start, sizeof(tag) + 25, "<%s>", tag);
  snprintf(end, sizeof(tag) + 25, "</%s>", tag);
  int i_start = text.find(start);
  int i_end = text.find(end);
  i_tag = strlen(start);
  if(i_start < 0)
    {
      memset(start, '\0', sizeof(start));
      snprintf(start, sizeof(tag) + 25, "<%s ", tag);
      i_start = text.find(start);
      if(i_start > -1)
	{
	  std::string tmp = text.substr(i_start, i_end-i_start);
	  i_tag = tmp.find(">")+1;
	}
    }
  if((i_start > -1) && (i_end > -1) && (i_end > i_start))
    {
      i_start += i_tag;
      ret = text.substr(i_start, i_end-i_start);
    }
  return ret;
}

/********************************************************************/

// Find the position of the first start tag in the XML file

int xml_find_tag_start(
 std::string text,
 const char* tag)
  {
    char* start = (char*) malloc(sizeof(tag) + 25);
    snprintf(start, sizeof(tag) + 25, "<%s>", tag);
    int i_start = text.find(start);
    if(i_start < 0)
      {
	memset(start, '\0', sizeof(start));
	snprintf(start, sizeof(tag) + 25, "<%s ", tag);
	i_start = text.find(start);
      }
    return i_start;
}

/********************************************************************/

// Find the position of the first end tag in the XML file

int xml_find_tag_end(
 std::string text,
 const char* tag)
{
  char* end = (char*) malloc(sizeof(tag) + 25);
  snprintf(end, sizeof(tag) + 25, "</%s>", tag);
  int i_end = text.find(end)+strlen(end);
  return i_end;
}

/********************************************************************/

/* xml_parse_remove_first_tag

Returned Value: int
  If any data delimited by the given tag is found in the text, this
  returns 1. Otherwise, it returns 0.

Called By: 
  AsBuilt::parseXml (in asBuilt.cc)
  PackList::parse (in response.cc)
  PackPallet::parse (in response.cc)

This removes the first occurrence in text of XML data delimited by tag,
if there is any such occurrence.

*/

int xml_parse_remove_first_tag( /* ARGUMENTS                              */
 std::string * text,            /* string possibly containing tagged text */
 const char * tag)              /* tag to search for                      */
{
  int startIndex = 0;
  int endIndex = 0;

  startIndex = xml_find_tag_start(*text, tag);
  endIndex = xml_find_tag_end(*text, tag);
  if((startIndex > -1) && (endIndex > -1) && (endIndex > startIndex))
    {
      (*text).erase(startIndex, (endIndex - startIndex));
      return 1;
    }
  return 0;
}

/********************************************************************/

