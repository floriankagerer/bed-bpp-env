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
     BACKAREAHEIGHTEND = 269,
     BACKAREAHEIGHTSTART = 270,
     BACKAREAEND = 271,
     BACKAREASTART = 272,
     DESCRIPTIONEND = 273,
     DESCRIPTIONSTART = 274,
     DOORIDEND = 275,
     DOORIDSTART = 276,
     DOOREND = 277,
     DOORSTART = 278,
     DOUBLEITEMEND = 279,
     DOUBLEITEMSTART = 280,
     EMPTYTRUCKEND = 281,
     EMPTYTRUCKSTART = 282,
     FRONTAREAEND = 283,
     FRONTAREASTART = 284,
     HEIGHTABOVEBACKEND = 285,
     HEIGHTABOVEBACKSTART = 286,
     HEIGHTEND = 287,
     HEIGHTSTART = 288,
     INTITEMEND = 289,
     INTITEMSTART = 290,
     JOBIDEND = 291,
     JOBIDSTART = 292,
     LENGTHEND = 293,
     LENGTHSTART = 294,
     MAXIMUMLOADWEIGHTEND = 295,
     MAXIMUMLOADWEIGHTSTART = 296,
     PALLETIDEND = 297,
     PALLETIDSTART = 298,
     PALLETSETEND = 299,
     PALLETSETSTART = 300,
     PALLETEND = 301,
     PALLETSTART = 302,
     SETINFOEND = 303,
     SETINFOSTART = 304,
     STRINGITEMEND = 305,
     STRINGITEMSTART = 306,
     TRUCKLOADINGJOBEND = 307,
     TRUCKLOADINGJOBSTART = 308,
     TYPEIDEND = 309,
     TYPEIDSTART = 310,
     VALUEEND = 311,
     VALUESTART = 312,
     WEIGHTEND = 313,
     WEIGHTSTART = 314,
     WHEELWELLEND = 315,
     WHEELWELLSTART = 316,
     WIDTHEND = 317,
     WIDTHSTART = 318,
     XCOORDINATEEND = 319,
     XCOORDINATESTART = 320,
     YCOORDINATEEND = 321,
     YCOORDINATESTART = 322
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
#define BACKAREAHEIGHTEND 269
#define BACKAREAHEIGHTSTART 270
#define BACKAREAEND 271
#define BACKAREASTART 272
#define DESCRIPTIONEND 273
#define DESCRIPTIONSTART 274
#define DOORIDEND 275
#define DOORIDSTART 276
#define DOOREND 277
#define DOORSTART 278
#define DOUBLEITEMEND 279
#define DOUBLEITEMSTART 280
#define EMPTYTRUCKEND 281
#define EMPTYTRUCKSTART 282
#define FRONTAREAEND 283
#define FRONTAREASTART 284
#define HEIGHTABOVEBACKEND 285
#define HEIGHTABOVEBACKSTART 286
#define HEIGHTEND 287
#define HEIGHTSTART 288
#define INTITEMEND 289
#define INTITEMSTART 290
#define JOBIDEND 291
#define JOBIDSTART 292
#define LENGTHEND 293
#define LENGTHSTART 294
#define MAXIMUMLOADWEIGHTEND 295
#define MAXIMUMLOADWEIGHTSTART 296
#define PALLETIDEND 297
#define PALLETIDSTART 298
#define PALLETSETEND 299
#define PALLETSETSTART 300
#define PALLETEND 301
#define PALLETSTART 302
#define SETINFOEND 303
#define SETINFOSTART 304
#define STRINGITEMEND 305
#define STRINGITEMSTART 306
#define TRUCKLOADINGJOBEND 307
#define TRUCKLOADINGJOBSTART 308
#define TYPEIDEND 309
#define TYPEIDSTART 310
#define VALUEEND 311
#define VALUESTART 312
#define WEIGHTEND 313
#define WEIGHTSTART 314
#define WHEELWELLEND 315
#define WHEELWELLSTART 316
#define WIDTHEND 317
#define WIDTHSTART 318
#define XCOORDINATEEND 319
#define XCOORDINATESTART 320
#define YCOORDINATEEND 321
#define YCOORDINATESTART 322




#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef union YYSTYPE

{
  SchemaLocation *                    SchemaLocationVal;
  XmlVersion *                        XmlVersionVal;
  double *                            dVal;
  int *                               iVal;
  char *                              sVal;

  TruckLoadingJobFile *               TruckLoadingJobFileVal;

  BackAreaType *                      BackAreaTypeVal;
  std::list<DoorType *> *             DoorTypeListVal;
  DoorType *                          DoorTypeVal;
  DoubleItemType *                    DoubleItemTypeVal;
  EmptyTruckType *                    EmptyTruckTypeVal;
  FrontAreaType *                     FrontAreaTypeVal;
  IntItemType *                       IntItemTypeVal;
  PalletCoordinateType *              PalletCoordinateTypeVal;
  PalletDistanceType *                PalletDistanceTypeVal;
  std::list<PalletForTruckType *> *   PalletForTruckTypeListVal;
  PalletForTruckType *                PalletForTruckTypeVal;
  std::list<PalletSetType *> *        PalletSetTypeListVal;
  PalletSetType *                     PalletSetTypeVal;
  PalletWeightType *                  PalletWeightTypeVal;
  StringItemType *                    StringItemTypeVal;
  TruckLoadingJobType *               TruckLoadingJobTypeVal;
  std::list<WheelWellType *> *        WheelWellTypeListVal;
  WheelWellType *                     WheelWellTypeVal;
}
/* Line 1489 of yacc.c.  */

	YYSTYPE;
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif

extern YYSTYPE yylval;

