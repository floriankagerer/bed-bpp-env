/* A Bison parser, made by GNU Bison 2.3.  */

/* Skeleton interface for Bison's Yacc-like parsers in C

   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006
   Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor,
   Boston, MA 02110-1301, USA.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     BAD = 258,
     DATASTRING = 259,
     ENCODING = 260,
     ENDITEM = 261,
     ENDVERSION = 262,
     SCHEMALOCATION = 263,
     STARTVERSION = 264,
     TERMINALSTRING = 265,
     XMLNSPREFIX = 266,
     XMLNSTARGET = 267,
     XMLVERSION = 268,
     DESCRIPTIONEND = 269,
     DESCRIPTIONSTART = 270,
     DOOREND = 271,
     DOORSTART = 272,
     DOUBLEITEMEND = 273,
     DOUBLEITEMSTART = 274,
     INTITEMEND = 275,
     INTITEMSTART = 276,
     JOBIDEND = 277,
     JOBIDSTART = 278,
     LOADPALLETEND = 279,
     LOADPALLETSTART = 280,
     ORIENTATIONEND = 281,
     ORIENTATIONSTART = 282,
     PALLETIDEND = 283,
     PALLETIDSTART = 284,
     STRINGITEMEND = 285,
     STRINGITEMSTART = 286,
     TRUCKLOADINGPLANEND = 287,
     TRUCKLOADINGPLANSTART = 288,
     VALUEEND = 289,
     VALUESTART = 290,
     XCOORDINATEEND = 291,
     XCOORDINATESTART = 292,
     YCOORDINATEEND = 293,
     YCOORDINATESTART = 294
   };
#endif
/* Tokens.  */
#define BAD 258
#define DATASTRING 259
#define ENCODING 260
#define ENDITEM 261
#define ENDVERSION 262
#define SCHEMALOCATION 263
#define STARTVERSION 264
#define TERMINALSTRING 265
#define XMLNSPREFIX 266
#define XMLNSTARGET 267
#define XMLVERSION 268
#define DESCRIPTIONEND 269
#define DESCRIPTIONSTART 270
#define DOOREND 271
#define DOORSTART 272
#define DOUBLEITEMEND 273
#define DOUBLEITEMSTART 274
#define INTITEMEND 275
#define INTITEMSTART 276
#define JOBIDEND 277
#define JOBIDSTART 278
#define LOADPALLETEND 279
#define LOADPALLETSTART 280
#define ORIENTATIONEND 281
#define ORIENTATIONSTART 282
#define PALLETIDEND 283
#define PALLETIDSTART 284
#define STRINGITEMEND 285
#define STRINGITEMSTART 286
#define TRUCKLOADINGPLANEND 287
#define TRUCKLOADINGPLANSTART 288
#define VALUEEND 289
#define VALUESTART 290
#define XCOORDINATEEND 291
#define XCOORDINATESTART 292
#define YCOORDINATEEND 293
#define YCOORDINATESTART 294




#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef union YYSTYPE

{
  SchemaLocation *                    SchemaLocationVal;
  XmlVersion *                        XmlVersionVal;
  double *                            dVal;
  int *                               iVal;
  char *                              sVal;

  TruckLoadingPlanFile *              TruckLoadingPlanFileVal;

  DoubleItemType *                    DoubleItemTypeVal;
  IntItemType *                       IntItemTypeVal;
  std::list<LoadPalletType *> *       LoadPalletTypeListVal;
  LoadPalletType *                    LoadPalletTypeVal;
  PalletCoordinateType *              PalletCoordinateTypeVal;
  PalletOrientType *                  PalletOrientTypeVal;
  StringItemType *                    StringItemTypeVal;
  TruckLoadingPlanType *              TruckLoadingPlanTypeVal;
}
/* Line 1489 of yacc.c.  */

	YYSTYPE;
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif

extern YYSTYPE yypllval;

