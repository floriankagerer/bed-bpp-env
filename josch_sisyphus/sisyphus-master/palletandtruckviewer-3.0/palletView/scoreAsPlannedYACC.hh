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
     STARTVERSION = 263,
     TERMINALSTRING = 264,
     URNLOCATION = 265,
     XMLVERSION = 266,
     BESTVALUEEND = 267,
     BESTVALUESTART = 268,
     COGINVERSERELATIVEHEIGHTEND = 269,
     COGINVERSERELATIVEHEIGHTSTART = 270,
     COGRELATIVEOFFSETEND = 271,
     COGRELATIVEOFFSETSTART = 272,
     CONNECTIONSBELOWEND = 273,
     CONNECTIONSBELOWSTART = 274,
     ISADDITIVEEND = 275,
     ISADDITIVESTART = 276,
     OVERHANGEND = 277,
     OVERHANGSTART = 278,
     OVERLAPFRACTIONEND = 279,
     OVERLAPFRACTIONSTART = 280,
     RIGHTSTUFFEND = 281,
     RIGHTSTUFFSTART = 282,
     SCOREASPLANNEDEND = 283,
     SCOREASPLANNEDSTART = 284,
     TAPERSIDEEND = 285,
     TAPERSIDESTART = 286,
     TAPEREND = 287,
     TAPERSTART = 288,
     VALUEFUNCTIONEND = 289,
     VALUEFUNCTIONSTART = 290,
     VOLUMEDENSITYEND = 291,
     VOLUMEDENSITYSTART = 292,
     WEIGHTEND = 293,
     WEIGHTSTART = 294,
     WIDTHEND = 295,
     WIDTHSTART = 296,
     FACTORVALUEOPTDECL = 297,
     FACTORVALUEREQDECL = 298,
     PALLETIZINGURN = 299,
     PALLETIZINGXSI = 300
   };
#endif
/* Tokens.  */
#define BAD 258
#define DATASTRING 259
#define ENCODING 260
#define ENDITEM 261
#define ENDVERSION 262
#define STARTVERSION 263
#define TERMINALSTRING 264
#define URNLOCATION 265
#define XMLVERSION 266
#define BESTVALUEEND 267
#define BESTVALUESTART 268
#define COGINVERSERELATIVEHEIGHTEND 269
#define COGINVERSERELATIVEHEIGHTSTART 270
#define COGRELATIVEOFFSETEND 271
#define COGRELATIVEOFFSETSTART 272
#define CONNECTIONSBELOWEND 273
#define CONNECTIONSBELOWSTART 274
#define ISADDITIVEEND 275
#define ISADDITIVESTART 276
#define OVERHANGEND 277
#define OVERHANGSTART 278
#define OVERLAPFRACTIONEND 279
#define OVERLAPFRACTIONSTART 280
#define RIGHTSTUFFEND 281
#define RIGHTSTUFFSTART 282
#define SCOREASPLANNEDEND 283
#define SCOREASPLANNEDSTART 284
#define TAPERSIDEEND 285
#define TAPERSIDESTART 286
#define TAPEREND 287
#define TAPERSTART 288
#define VALUEFUNCTIONEND 289
#define VALUEFUNCTIONSTART 290
#define VOLUMEDENSITYEND 291
#define VOLUMEDENSITYSTART 292
#define WEIGHTEND 293
#define WEIGHTSTART 294
#define WIDTHEND 295
#define WIDTHSTART 296
#define FACTORVALUEOPTDECL 297
#define FACTORVALUEREQDECL 298
#define PALLETIZINGURN 299
#define PALLETIZINGXSI 300




#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef union YYSTYPE

{
  UrnLocation *                       UrnLocationVal;
  XmlVersion *                        XmlVersionVal;
  bool *                              bVal;
  double *                            dVal;
  int *                               iVal;
  char *                              sVal;
  unsigned int *                      uVal;

  ScoreAsPlannedFile *                scoreAsPlannedFileVal;

  factorValueOpt *                    FactorValueOptVal;
  factorValueReq *                    FactorValueReqVal;
  nonNegativeReal *                   NonNegativeRealVal;
  scoreAsPlannedType *                ScoreAsPlannedTypeVal;
  taperSideType *                     TaperSideTypeVal;
  valueFunctionType *                 ValueFunctionTypeVal;
}
/* Line 1489 of yacc.c.  */

	YYSTYPE;
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif

extern YYSTYPE yylval;

