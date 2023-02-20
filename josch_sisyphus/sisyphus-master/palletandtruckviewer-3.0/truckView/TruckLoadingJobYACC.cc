/* A Bison parser, made by GNU Bison 2.3.  */

/* Skeleton implementation for Bison's Yacc-like parsers in C

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

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output.  */
#define YYBISON 1

/* Bison version.  */
#define YYBISON_VERSION "2.3"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Using locations.  */
#define YYLSP_NEEDED 0



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




/* Copy the first part of user declarations.  */



#include <stdio.h>             // for stderr
#include <string.h>            // for strcat
#include <stdlib.h>            // for malloc, free
#include "TruckLoadingJobClasses.hh"   // for TruckLoadingJob classes

#define YYERROR_VERBOSE
#define YYDEBUG 1

TruckLoadingJobFile * TruckLoadingJobTree; // the parse tree

extern int yylex();
int readData = 0;
int readDataList = 0;

int yyerror(const char * s);



/* Enabling traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif

/* Enabling verbose error messages.  */
#ifdef YYERROR_VERBOSE
# undef YYERROR_VERBOSE
# define YYERROR_VERBOSE 1
#else
# define YYERROR_VERBOSE 0
#endif

/* Enabling the token table.  */
#ifndef YYTOKEN_TABLE
# define YYTOKEN_TABLE 0
#endif

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
/* Line 187 of yacc.c.  */

	YYSTYPE;
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif



/* Copy the second part of user declarations.  */


/* Line 216 of yacc.c.  */


#ifdef short
# undef short
#endif

#ifdef YYTYPE_UINT8
typedef YYTYPE_UINT8 yytype_uint8;
#else
typedef unsigned char yytype_uint8;
#endif

#ifdef YYTYPE_INT8
typedef YYTYPE_INT8 yytype_int8;
#elif (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
typedef signed char yytype_int8;
#else
typedef short int yytype_int8;
#endif

#ifdef YYTYPE_UINT16
typedef YYTYPE_UINT16 yytype_uint16;
#else
typedef unsigned short int yytype_uint16;
#endif

#ifdef YYTYPE_INT16
typedef YYTYPE_INT16 yytype_int16;
#else
typedef short int yytype_int16;
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif ! defined YYSIZE_T && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned int
# endif
#endif

#define YYSIZE_MAXIMUM ((YYSIZE_T) -1)

#ifndef YY_
# if YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(msgid) dgettext ("bison-runtime", msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(msgid) msgid
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YYUSE(e) ((void) (e))
#else
# define YYUSE(e) /* empty */
#endif

/* Identity function, used to suppress warnings about constant conditions.  */
#ifndef lint
# define YYID(n) (n)
#else
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static int
YYID (int i)
#else
static int
YYID (i)
    int i;
#endif
{
  return i;
}
#endif

#if ! defined yyoverflow || YYERROR_VERBOSE

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#     ifndef _STDLIB_H
#      define _STDLIB_H 1
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's `empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (YYID (0))
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined _STDLIB_H \
       && ! ((defined YYMALLOC || defined malloc) \
	     && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef _STDLIB_H
#    define _STDLIB_H 1
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* ! defined yyoverflow || YYERROR_VERBOSE */


#if (! defined yyoverflow \
     && (! defined __cplusplus \
	 || (defined YYSTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  yytype_int16 yyss;
  YYSTYPE yyvs;
  };

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (sizeof (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (sizeof (yytype_int16) + sizeof (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

/* Copy COUNT objects from FROM to TO.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(To, From, Count) \
      __builtin_memcpy (To, From, (Count) * sizeof (*(From)))
#  else
#   define YYCOPY(To, From, Count)		\
      do					\
	{					\
	  YYSIZE_T yyi;				\
	  for (yyi = 0; yyi < (Count); yyi++)	\
	    (To)[yyi] = (From)[yyi];		\
	}					\
      while (YYID (0))
#  endif
# endif

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack)					\
    do									\
      {									\
	YYSIZE_T yynewbytes;						\
	YYCOPY (&yyptr->Stack, Stack, yysize);				\
	Stack = &yyptr->Stack;						\
	yynewbytes = yystacksize * sizeof (*Stack) + YYSTACK_GAP_MAXIMUM; \
	yyptr += yynewbytes / sizeof (*yyptr);				\
      }									\
    while (YYID (0))

#endif

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  5
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   121

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  68
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  56
/* YYNRULES -- Number of rules.  */
#define YYNRULES  63
/* YYNRULES -- Number of states.  */
#define YYNSTATES  166

/* YYTRANSLATE(YYLEX) -- Bison symbol number corresponding to YYLEX.  */
#define YYUNDEFTOK  2
#define YYMAXUTOK   322

#define YYTRANSLATE(YYX)						\
  ((unsigned int) (YYX) <= YYMAXUTOK ? yytranslate[YYX] : YYUNDEFTOK)

/* YYTRANSLATE[YYLEX] -- Bison symbol number corresponding to YYLEX.  */
static const yytype_uint8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    22,    23,    24,
      25,    26,    27,    28,    29,    30,    31,    32,    33,    34,
      35,    36,    37,    38,    39,    40,    41,    42,    43,    44,
      45,    46,    47,    48,    49,    50,    51,    52,    53,    54,
      55,    56,    57,    58,    59,    60,    61,    62,    63,    64,
      65,    66,    67
};

#if YYDEBUG
/* YYPRHS[YYN] -- Index of the first RHS symbol of rule number YYN in
   YYRHS.  */
static const yytype_uint8 yyprhs[] =
{
       0,     0,     3,     6,     9,    11,    13,    18,    25,    26,
      32,    38,    42,    43,    49,    50,    56,    63,    67,    69,
      72,    80,    84,    89,    90,    94,    95,   101,   102,   108,
     109,   115,   116,   122,   123,   129,   136,   137,   143,   147,
     151,   153,   156,   160,   162,   165,   166,   167,   173,   181,
     185,   186,   192,   193,   199,   206,   210,   211,   214,   215,
     221,   222,   228,   229
};

/* YYRHS -- A `-1'-separated list of the rules' RHS.  */
static const yytype_int8 yyrhs[] =
{
      69,     0,    -1,    73,   110,    -1,     8,    10,    -1,     4,
      -1,     4,    -1,     9,    13,    10,     7,    -1,     9,    13,
      10,     5,    10,     7,    -1,    -1,    15,     6,    75,    71,
      14,    -1,     6,    95,   118,    84,   117,    -1,    17,    76,
      16,    -1,    -1,    19,     6,    79,    72,    18,    -1,    -1,
      21,     6,    81,    72,    20,    -1,     6,    80,   120,   122,
     118,    91,    -1,    23,    82,    22,    -1,    83,    -1,    84,
      83,    -1,     6,   111,    78,    97,    74,    77,    88,    -1,
      27,    85,    26,    -1,     6,    95,   118,    89,    -1,    -1,
      29,    87,    28,    -1,    -1,    31,     6,    90,    71,    30,
      -1,    -1,    33,     6,    92,    71,    32,    -1,    -1,    37,
       6,    94,    72,    36,    -1,    -1,    39,     6,    96,    71,
      38,    -1,    -1,    41,     6,    98,    71,    40,    -1,     6,
     100,   113,    95,   118,    91,    -1,    -1,    43,     6,   101,
      72,    42,    -1,     6,   106,   107,    -1,    45,   102,    44,
      -1,   103,    -1,   104,   103,    -1,    47,    99,    46,    -1,
     105,    -1,   106,   105,    -1,    -1,    -1,    49,     6,   108,
      72,    48,    -1,    12,    11,    70,     6,    93,   104,    86,
      -1,    53,   109,    52,    -1,    -1,    55,     6,   112,    72,
      54,    -1,    -1,    59,     6,   114,    71,    58,    -1,     6,
     120,   122,    95,   118,    91,    -1,    61,   115,    60,    -1,
      -1,   117,   116,    -1,    -1,    63,     6,   119,    71,    62,
      -1,    -1,    65,     6,   121,    71,    64,    -1,    -1,    67,
       6,   123,    71,    66,    -1
};

/* YYRLINE[YYN] -- source line where rule number YYN was defined.  */
static const yytype_uint16 yyrline[] =
{
       0,   176,   176,   183,   195,   215,   230,   235,   246,   246,
     255,   261,   266,   266,   271,   271,   276,   283,   288,   291,
     307,   315,   320,   327,   328,   333,   333,   342,   342,   360,
     360,   365,   365,   373,   373,   382,   389,   389,   394,   399,
     404,   407,   413,   418,   421,   428,   429,   429,   444,   450,
     455,   455,   475,   475,   483,   490,   496,   497,   503,   503,
     511,   511,   519,   519
};
#endif

#if YYDEBUG || YYERROR_VERBOSE || YYTOKEN_TABLE
/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "$end", "error", "$undefined", "BAD", "DATASTRING", "ENCODING",
  "ENDITEM", "ENDVERSION", "SCHEMALOCATION", "STARTVERSION",
  "TERMINALSTRING", "XMLNSPREFIX", "XMLNSTARGET", "XMLVERSION",
  "BACKAREAHEIGHTEND", "BACKAREAHEIGHTSTART", "BACKAREAEND",
  "BACKAREASTART", "DESCRIPTIONEND", "DESCRIPTIONSTART", "DOORIDEND",
  "DOORIDSTART", "DOOREND", "DOORSTART", "DOUBLEITEMEND",
  "DOUBLEITEMSTART", "EMPTYTRUCKEND", "EMPTYTRUCKSTART", "FRONTAREAEND",
  "FRONTAREASTART", "HEIGHTABOVEBACKEND", "HEIGHTABOVEBACKSTART",
  "HEIGHTEND", "HEIGHTSTART", "INTITEMEND", "INTITEMSTART", "JOBIDEND",
  "JOBIDSTART", "LENGTHEND", "LENGTHSTART", "MAXIMUMLOADWEIGHTEND",
  "MAXIMUMLOADWEIGHTSTART", "PALLETIDEND", "PALLETIDSTART", "PALLETSETEND",
  "PALLETSETSTART", "PALLETEND", "PALLETSTART", "SETINFOEND",
  "SETINFOSTART", "STRINGITEMEND", "STRINGITEMSTART", "TRUCKLOADINGJOBEND",
  "TRUCKLOADINGJOBSTART", "TYPEIDEND", "TYPEIDSTART", "VALUEEND",
  "VALUESTART", "WEIGHTEND", "WEIGHTSTART", "WHEELWELLEND",
  "WHEELWELLSTART", "WIDTHEND", "WIDTHSTART", "XCOORDINATEEND",
  "XCOORDINATESTART", "YCOORDINATEEND", "YCOORDINATESTART", "$accept",
  "y_TruckLoadingJobFile", "y_SchemaLocation", "y_double", "y_string",
  "y_XmlVersion", "y_BackAreaHeight_PalletDistanceType", "@1",
  "y_BackAreaType", "y_BackArea_BackAreaType", "y_Description_string",
  "@2", "y_DoorId_string", "@3", "y_DoorType", "y_Door_DoorType_u",
  "y_Door_DoorType_uList", "y_EmptyTruckType",
  "y_EmptyTruck_EmptyTruckType", "y_FrontAreaType",
  "y_FrontArea_FrontAreaType_0", "y_HeightAboveBack_PalletDistanceType",
  "@4", "y_Height_PalletDistanceType", "@5", "y_JobId_string", "@6",
  "y_Length_PalletDistanceType", "@7",
  "y_MaximumLoadWeight_PalletWeightType", "@8", "y_PalletForTruckType",
  "y_PalletId_string", "@9", "y_PalletSetType",
  "y_PalletSet_PalletSetType_u", "y_PalletSet_PalletSetType_uList",
  "y_Pallet_PalletForTruckType_u", "y_Pallet_PalletForTruckType_uList",
  "y_SetInfo_string_0", "@10", "y_TruckLoadingJobType",
  "y_TruckLoadingJob_TruckLoadingJobType", "y_TypeId_string", "@11",
  "y_Weight_PalletWeightType", "@15", "y_WheelWellType",
  "y_WheelWell_WheelWellType_0_u", "y_WheelWell_WheelWellType_0_uList",
  "y_Width_PalletDistanceType", "@16",
  "y_Xcoordinate_PalletCoordinateType", "@17",
  "y_Ycoordinate_PalletCoordinateType", "@18", 0
};
#endif

# ifdef YYPRINT
/* YYTOKNUM[YYLEX-NUM] -- Internal token number corresponding to
   token YYLEX-NUM.  */
static const yytype_uint16 yytoknum[] =
{
       0,   256,   257,   258,   259,   260,   261,   262,   263,   264,
     265,   266,   267,   268,   269,   270,   271,   272,   273,   274,
     275,   276,   277,   278,   279,   280,   281,   282,   283,   284,
     285,   286,   287,   288,   289,   290,   291,   292,   293,   294,
     295,   296,   297,   298,   299,   300,   301,   302,   303,   304,
     305,   306,   307,   308,   309,   310,   311,   312,   313,   314,
     315,   316,   317,   318,   319,   320,   321,   322
};
# endif

/* YYR1[YYN] -- Symbol number of symbol that rule YYN derives.  */
static const yytype_uint8 yyr1[] =
{
       0,    68,    69,    70,    71,    72,    73,    73,    75,    74,
      76,    77,    79,    78,    81,    80,    82,    83,    84,    84,
      85,    86,    87,    88,    88,    90,    89,    92,    91,    94,
      93,    96,    95,    98,    97,    99,   101,   100,   102,   103,
     104,   104,   105,   106,   106,   107,   108,   107,   109,   110,
     112,   111,   114,   113,   115,   116,   117,   117,   119,   118,
     121,   120,   123,   122
};

/* YYR2[YYN] -- Number of symbols composing right hand side of rule YYN.  */
static const yytype_uint8 yyr2[] =
{
       0,     2,     2,     2,     1,     1,     4,     6,     0,     5,
       5,     3,     0,     5,     0,     5,     6,     3,     1,     2,
       7,     3,     4,     0,     3,     0,     5,     0,     5,     0,
       5,     0,     5,     0,     5,     6,     0,     5,     3,     3,
       1,     2,     3,     1,     2,     0,     0,     5,     7,     3,
       0,     5,     0,     5,     6,     3,     0,     2,     0,     5,
       0,     5,     0,     5
};

/* YYDEFACT[STATE-NAME] -- Default rule to reduce with in state
   STATE-NUM when YYTABLE doesn't specify something else to do.  Zero
   means the default is an error.  */
static const yytype_uint8 yydefact[] =
{
       0,     0,     0,     0,     0,     1,     0,     2,     0,     0,
       0,     0,     6,     0,    49,     0,     0,     0,     7,     3,
       0,     0,     0,    29,     0,    40,     0,     0,     0,     0,
       0,    48,    41,     5,     0,     0,    43,    45,    39,     0,
       0,    30,     0,     0,     0,    44,    38,     0,     0,    21,
       0,     0,    42,    46,    50,     0,     0,    36,     0,     0,
       0,     0,    12,     0,     0,     0,    52,     0,     0,     0,
       0,     0,    33,     0,     0,     0,     0,    31,     0,     0,
      47,    51,     0,     0,     8,     0,    23,    37,     4,     0,
       0,    58,     0,    35,    13,     0,     0,     0,     0,     0,
      20,    53,     0,     0,    27,    34,     0,     0,    11,     0,
       0,    32,     0,     0,     9,     0,     0,    24,    59,     0,
       0,    18,    56,     0,    28,     0,     0,    19,    10,     0,
      22,     0,     0,    17,     0,    57,    25,    14,     0,     0,
       0,     0,     0,     0,    60,     0,     0,     0,    55,     0,
       0,     0,    62,     0,     0,    26,    15,     0,     0,    16,
       0,    61,     0,     0,    63,    54
};

/* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int16 yydefgoto[] =
{
      -1,     2,    17,    89,    34,     3,    74,    96,    98,    86,
      56,    71,   132,   143,   126,   121,   122,    40,    31,   110,
     100,   130,   142,    93,   113,    22,    27,    68,    90,    64,
      83,    43,    51,    65,    29,    25,    26,    36,    37,    46,
      60,    10,     7,    48,    61,    59,    76,   141,   135,   128,
      79,   103,   139,   151,   146,   158
};

/* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
   STATE-NUM.  */
#define YYPACT_NINF -150
static const yytype_int16 yypact[] =
{
       4,     7,    16,   -32,    13,  -150,    12,  -150,     3,    15,
     -25,    18,  -150,    21,  -150,    23,    24,    25,  -150,  -150,
      -4,    29,    -9,  -150,    31,  -150,   -20,    34,    -8,    -3,
      37,  -150,  -150,  -150,     8,    39,  -150,   -30,  -150,   -15,
      20,  -150,     5,     1,    43,  -150,  -150,    44,    32,  -150,
      46,    -6,  -150,  -150,  -150,    48,    14,  -150,    51,    19,
      34,    34,  -150,    53,    45,    34,  -150,    56,     2,    26,
      10,    34,  -150,    60,    50,    27,    64,  -150,    65,    40,
    -150,  -150,    54,    64,  -150,    69,    47,  -150,  -150,    22,
      64,  -150,    72,  -150,  -150,    41,    64,    19,    63,    76,
    -150,  -150,    49,    64,  -150,  -150,    70,     2,  -150,    19,
      57,  -150,    28,    64,  -150,    66,     2,  -150,  -150,    59,
      80,  -150,    66,    61,  -150,    67,    71,  -150,    33,    89,
    -150,    90,    35,  -150,    91,  -150,  -150,  -150,    92,    36,
      35,    42,    64,    34,  -150,    93,     2,    36,  -150,    74,
      81,    64,  -150,    40,    19,  -150,  -150,    52,    64,  -150,
       2,  -150,    55,    40,  -150,  -150
};

/* YYPGOTO[NTERM-NUM].  */
static const yytype_int16 yypgoto[] =
{
    -150,  -150,  -150,   -81,   -60,  -150,  -150,  -150,  -150,  -150,
    -150,  -150,  -150,  -150,  -150,   -17,  -150,  -150,  -150,  -150,
    -150,  -150,  -150,  -149,  -150,  -150,  -150,   -91,  -150,  -150,
    -150,  -150,  -150,  -150,  -150,    82,  -150,    73,  -150,  -150,
    -150,  -150,  -150,  -150,  -150,  -150,  -150,  -150,  -150,  -150,
    -104,  -150,   -34,  -150,   -40,  -150
};

/* YYTABLE[YYPACT[STATE-NUM]].  What to do in state STATE-NUM.  If
   positive, shift that token.  If negative, reduce the rule which
   number is the opposite.  If zero, do what YYDEFACT says.
   If YYTABLE_NINF, syntax error.  */
#define YYTABLE_NINF -1
static const yytype_uint8 yytable[] =
{
      69,    70,    95,   115,   159,    75,   107,    30,    11,   102,
      12,    82,   123,     1,   165,   106,     5,    35,   116,    44,
       4,     6,   112,     8,     9,    24,    13,    14,    15,    16,
      18,    20,   119,    21,    19,    23,    24,    28,    33,    35,
      47,    38,   153,    39,    41,    42,    49,    52,    50,    53,
      54,    55,    57,    58,    62,    63,   163,    66,    67,    72,
      73,   149,    77,   160,    81,    78,    84,    85,    88,    87,
     157,    91,    94,    92,    80,    97,    99,   162,   104,   108,
     101,   105,   109,   150,   114,   117,   125,   111,   131,   120,
     118,   124,   129,   133,   134,   136,   137,   140,   144,   152,
     138,   156,   148,   145,   155,   127,   147,   154,    32,     0,
      45,     0,     0,     0,     0,     0,   161,     0,     0,     0,
       0,   164
};

static const yytype_int16 yycheck[] =
{
      60,    61,    83,   107,   153,    65,    97,    27,     5,    90,
       7,    71,   116,     9,   163,    96,     0,    47,   109,    49,
      13,    53,   103,    10,    12,    45,    11,    52,    10,     8,
       7,     6,   113,    37,    10,     6,    45,     6,     4,    47,
      55,    44,   146,     6,    36,     6,    26,    46,    43,     6,
       6,    19,     6,    59,     6,    41,   160,     6,    39,     6,
      15,   142,     6,   154,    54,    63,     6,    17,     4,    42,
     151,     6,    18,    33,    48,     6,    29,   158,     6,    16,
      58,    40,     6,   143,    14,    28,     6,    38,    21,    23,
      62,    32,    31,    22,    61,     6,     6,     6,     6,     6,
      65,    20,    60,    67,    30,   122,   140,   147,    26,    -1,
      37,    -1,    -1,    -1,    -1,    -1,    64,    -1,    -1,    -1,
      -1,    66
};

/* YYSTOS[STATE-NUM] -- The (internal number of the) accessing
   symbol of state STATE-NUM.  */
static const yytype_uint8 yystos[] =
{
       0,     9,    69,    73,    13,     0,    53,   110,    10,    12,
     109,     5,     7,    11,    52,    10,     8,    70,     7,    10,
       6,    37,    93,     6,    45,   103,   104,    94,     6,   102,
      27,    86,   103,     4,    72,    47,   105,   106,    44,     6,
      85,    36,     6,    99,    49,   105,   107,    55,   111,    26,
      43,   100,    46,     6,     6,    19,    78,     6,    59,   113,
     108,   112,     6,    41,    97,   101,     6,    39,    95,    72,
      72,    79,     6,    15,    74,    72,   114,     6,    63,   118,
      48,    54,    72,    98,     6,    17,    77,    42,     4,    71,
      96,     6,    33,    91,    18,    71,    75,     6,    76,    29,
      88,    58,    71,   119,     6,    40,    71,    95,    16,     6,
      87,    38,    71,    92,    14,   118,    95,    28,    62,    71,
      23,    83,    84,   118,    32,     6,    82,    83,   117,    31,
      89,    21,    80,    22,    61,   116,     6,     6,    65,   120,
       6,   115,    90,    81,     6,    67,   122,   120,    60,    71,
      72,   121,     6,   118,   122,    30,    20,    71,   123,    91,
      95,    64,    71,   118,    66,    91
};

#define yyerrok		(yyerrstatus = 0)
#define yyclearin	(yychar = YYEMPTY)
#define YYEMPTY		(-2)
#define YYEOF		0

#define YYACCEPT	goto yyacceptlab
#define YYABORT		goto yyabortlab
#define YYERROR		goto yyerrorlab


/* Like YYERROR except do call yyerror.  This remains here temporarily
   to ease the transition to the new meaning of YYERROR, for GCC.
   Once GCC version 2 has supplanted version 1, this can go.  */

#define YYFAIL		goto yyerrlab

#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)					\
do								\
  if (yychar == YYEMPTY && yylen == 1)				\
    {								\
      yychar = (Token);						\
      yylval = (Value);						\
      yytoken = YYTRANSLATE (yychar);				\
      YYPOPSTACK (1);						\
      goto yybackup;						\
    }								\
  else								\
    {								\
      yyerror (YY_("syntax error: cannot back up")); \
      YYERROR;							\
    }								\
while (YYID (0))


#define YYTERROR	1
#define YYERRCODE	256


/* YYLLOC_DEFAULT -- Set CURRENT to span from RHS[1] to RHS[N].
   If N is 0, then set CURRENT to the empty location which ends
   the previous symbol: RHS[0] (always defined).  */

#define YYRHSLOC(Rhs, K) ((Rhs)[K])
#ifndef YYLLOC_DEFAULT
# define YYLLOC_DEFAULT(Current, Rhs, N)				\
    do									\
      if (YYID (N))                                                    \
	{								\
	  (Current).first_line   = YYRHSLOC (Rhs, 1).first_line;	\
	  (Current).first_column = YYRHSLOC (Rhs, 1).first_column;	\
	  (Current).last_line    = YYRHSLOC (Rhs, N).last_line;		\
	  (Current).last_column  = YYRHSLOC (Rhs, N).last_column;	\
	}								\
      else								\
	{								\
	  (Current).first_line   = (Current).last_line   =		\
	    YYRHSLOC (Rhs, 0).last_line;				\
	  (Current).first_column = (Current).last_column =		\
	    YYRHSLOC (Rhs, 0).last_column;				\
	}								\
    while (YYID (0))
#endif


/* YY_LOCATION_PRINT -- Print the location on the stream.
   This macro was not mandated originally: define only if we know
   we won't break user code: when these are the locations we know.  */

#ifndef YY_LOCATION_PRINT
# if YYLTYPE_IS_TRIVIAL
#  define YY_LOCATION_PRINT(File, Loc)			\
     fprintf (File, "%d.%d-%d.%d",			\
	      (Loc).first_line, (Loc).first_column,	\
	      (Loc).last_line,  (Loc).last_column)
# else
#  define YY_LOCATION_PRINT(File, Loc) ((void) 0)
# endif
#endif


/* YYLEX -- calling `yylex' with the right arguments.  */

#ifdef YYLEX_PARAM
# define YYLEX yylex (YYLEX_PARAM)
#else
# define YYLEX yylex ()
#endif

/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)			\
do {						\
  if (yydebug)					\
    YYFPRINTF Args;				\
} while (YYID (0))

# define YY_SYMBOL_PRINT(Title, Type, Value, Location)			  \
do {									  \
  if (yydebug)								  \
    {									  \
      YYFPRINTF (stderr, "%s ", Title);					  \
      yy_symbol_print (stderr,						  \
		  Type, Value); \
      YYFPRINTF (stderr, "\n");						  \
    }									  \
} while (YYID (0))


/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

/*ARGSUSED*/
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yy_symbol_value_print (FILE *yyoutput, int yytype, YYSTYPE const * const yyvaluep)
#else
static void
yy_symbol_value_print (yyoutput, yytype, yyvaluep)
    FILE *yyoutput;
    int yytype;
    YYSTYPE const * const yyvaluep;
#endif
{
  if (!yyvaluep)
    return;
# ifdef YYPRINT
  if (yytype < YYNTOKENS)
    YYPRINT (yyoutput, yytoknum[yytype], *yyvaluep);
# else
  YYUSE (yyoutput);
# endif
  switch (yytype)
    {
      default:
	break;
    }
}


/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yy_symbol_print (FILE *yyoutput, int yytype, YYSTYPE const * const yyvaluep)
#else
static void
yy_symbol_print (yyoutput, yytype, yyvaluep)
    FILE *yyoutput;
    int yytype;
    YYSTYPE const * const yyvaluep;
#endif
{
  if (yytype < YYNTOKENS)
    YYFPRINTF (yyoutput, "token %s (", yytname[yytype]);
  else
    YYFPRINTF (yyoutput, "nterm %s (", yytname[yytype]);

  yy_symbol_value_print (yyoutput, yytype, yyvaluep);
  YYFPRINTF (yyoutput, ")");
}

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yy_stack_print (yytype_int16 *bottom, yytype_int16 *top)
#else
static void
yy_stack_print (bottom, top)
    yytype_int16 *bottom;
    yytype_int16 *top;
#endif
{
  YYFPRINTF (stderr, "Stack now");
  for (; bottom <= top; ++bottom)
    YYFPRINTF (stderr, " %d", *bottom);
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)				\
do {								\
  if (yydebug)							\
    yy_stack_print ((Bottom), (Top));				\
} while (YYID (0))


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yy_reduce_print (YYSTYPE *yyvsp, int yyrule)
#else
static void
yy_reduce_print (yyvsp, yyrule)
    YYSTYPE *yyvsp;
    int yyrule;
#endif
{
  int yynrhs = yyr2[yyrule];
  int yyi;
  unsigned long int yylno = yyrline[yyrule];
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %lu):\n",
	     yyrule - 1, yylno);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      fprintf (stderr, "   $%d = ", yyi + 1);
      yy_symbol_print (stderr, yyrhs[yyprhs[yyrule] + yyi],
		       &(yyvsp[(yyi + 1) - (yynrhs)])
		       		       );
      fprintf (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)		\
do {					\
  if (yydebug)				\
    yy_reduce_print (yyvsp, Rule); \
} while (YYID (0))

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args)
# define YY_SYMBOL_PRINT(Title, Type, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef	YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif



#if YYERROR_VERBOSE

# ifndef yystrlen
#  if defined __GLIBC__ && defined _STRING_H
#   define yystrlen strlen
#  else
/* Return the length of YYSTR.  */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static YYSIZE_T
yystrlen (const char *yystr)
#else
static YYSIZE_T
yystrlen (yystr)
    const char *yystr;
#endif
{
  YYSIZE_T yylen;
  for (yylen = 0; yystr[yylen]; yylen++)
    continue;
  return yylen;
}
#  endif
# endif

# ifndef yystpcpy
#  if defined __GLIBC__ && defined _STRING_H && defined _GNU_SOURCE
#   define yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static char *
yystpcpy (char *yydest, const char *yysrc)
#else
static char *
yystpcpy (yydest, yysrc)
    char *yydest;
    const char *yysrc;
#endif
{
  char *yyd = yydest;
  const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
#  endif
# endif

# ifndef yytnamerr
/* Copy to YYRES the contents of YYSTR after stripping away unnecessary
   quotes and backslashes, so that it's suitable for yyerror.  The
   heuristic is that double-quoting is unnecessary unless the string
   contains an apostrophe, a comma, or backslash (other than
   backslash-backslash).  YYSTR is taken from yytname.  If YYRES is
   null, do not copy; instead, return the length of what the result
   would have been.  */
static YYSIZE_T
yytnamerr (char *yyres, const char *yystr)
{
  if (*yystr == '"')
    {
      YYSIZE_T yyn = 0;
      char const *yyp = yystr;

      for (;;)
	switch (*++yyp)
	  {
	  case '\'':
	  case ',':
	    goto do_not_strip_quotes;

	  case '\\':
	    if (*++yyp != '\\')
	      goto do_not_strip_quotes;
	    /* Fall through.  */
	  default:
	    if (yyres)
	      yyres[yyn] = *yyp;
	    yyn++;
	    break;

	  case '"':
	    if (yyres)
	      yyres[yyn] = '\0';
	    return yyn;
	  }
    do_not_strip_quotes: ;
    }

  if (! yyres)
    return yystrlen (yystr);

  return yystpcpy (yyres, yystr) - yyres;
}
# endif

/* Copy into YYRESULT an error message about the unexpected token
   YYCHAR while in state YYSTATE.  Return the number of bytes copied,
   including the terminating null byte.  If YYRESULT is null, do not
   copy anything; just return the number of bytes that would be
   copied.  As a special case, return 0 if an ordinary "syntax error"
   message will do.  Return YYSIZE_MAXIMUM if overflow occurs during
   size calculation.  */
static YYSIZE_T
yysyntax_error (char *yyresult, int yystate, int yychar)
{
  int yyn = yypact[yystate];

  if (! (YYPACT_NINF < yyn && yyn <= YYLAST))
    return 0;
  else
    {
      int yytype = YYTRANSLATE (yychar);
      YYSIZE_T yysize0 = yytnamerr (0, yytname[yytype]);
      YYSIZE_T yysize = yysize0;
      YYSIZE_T yysize1;
      int yysize_overflow = 0;
      enum { YYERROR_VERBOSE_ARGS_MAXIMUM = 5 };
      char const *yyarg[YYERROR_VERBOSE_ARGS_MAXIMUM];
      int yyx;

# if 0
      /* This is so xgettext sees the translatable formats that are
	 constructed on the fly.  */
      YY_("syntax error, unexpected %s");
      YY_("syntax error, unexpected %s, expecting %s");
      YY_("syntax error, unexpected %s, expecting %s or %s");
      YY_("syntax error, unexpected %s, expecting %s or %s or %s");
      YY_("syntax error, unexpected %s, expecting %s or %s or %s or %s");
# endif
      char *yyfmt;
      char const *yyf;
      static char const yyunexpected[] = "syntax error, unexpected %s";
      static char const yyexpecting[] = ", expecting %s";
      static char const yyor[] = " or %s";
      char yyformat[sizeof yyunexpected
		    + sizeof yyexpecting - 1
		    + ((YYERROR_VERBOSE_ARGS_MAXIMUM - 2)
		       * (sizeof yyor - 1))];
      char const *yyprefix = yyexpecting;

      /* Start YYX at -YYN if negative to avoid negative indexes in
	 YYCHECK.  */
      int yyxbegin = yyn < 0 ? -yyn : 0;

      /* Stay within bounds of both yycheck and yytname.  */
      int yychecklim = YYLAST - yyn + 1;
      int yyxend = yychecklim < YYNTOKENS ? yychecklim : YYNTOKENS;
      int yycount = 1;

      yyarg[0] = yytname[yytype];
      yyfmt = yystpcpy (yyformat, yyunexpected);

      for (yyx = yyxbegin; yyx < yyxend; ++yyx)
	if (yycheck[yyx + yyn] == yyx && yyx != YYTERROR)
	  {
	    if (yycount == YYERROR_VERBOSE_ARGS_MAXIMUM)
	      {
		yycount = 1;
		yysize = yysize0;
		yyformat[sizeof yyunexpected - 1] = '\0';
		break;
	      }
	    yyarg[yycount++] = yytname[yyx];
	    yysize1 = yysize + yytnamerr (0, yytname[yyx]);
	    yysize_overflow |= (yysize1 < yysize);
	    yysize = yysize1;
	    yyfmt = yystpcpy (yyfmt, yyprefix);
	    yyprefix = yyor;
	  }

      yyf = YY_(yyformat);
      yysize1 = yysize + yystrlen (yyf);
      yysize_overflow |= (yysize1 < yysize);
      yysize = yysize1;

      if (yysize_overflow)
	return YYSIZE_MAXIMUM;

      if (yyresult)
	{
	  /* Avoid sprintf, as that infringes on the user's name space.
	     Don't have undefined behavior even if the translation
	     produced a string with the wrong number of "%s"s.  */
	  char *yyp = yyresult;
	  int yyi = 0;
	  while ((*yyp = *yyf) != '\0')
	    {
	      if (*yyp == '%' && yyf[1] == 's' && yyi < yycount)
		{
		  yyp += yytnamerr (yyp, yyarg[yyi++]);
		  yyf += 2;
		}
	      else
		{
		  yyp++;
		  yyf++;
		}
	    }
	}
      return yysize;
    }
}
#endif /* YYERROR_VERBOSE */


/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

/*ARGSUSED*/
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
yydestruct (const char *yymsg, int yytype, YYSTYPE *yyvaluep)
#else
static void
yydestruct (yymsg, yytype, yyvaluep)
    const char *yymsg;
    int yytype;
    YYSTYPE *yyvaluep;
#endif
{
  YYUSE (yyvaluep);

  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yytype, yyvaluep, yylocationp);

  switch (yytype)
    {

      default:
	break;
    }
}


/* Prevent warnings from -Wmissing-prototypes.  */

#ifdef YYPARSE_PARAM
#if defined __STDC__ || defined __cplusplus
int yyparse (void *YYPARSE_PARAM);
#else
int yyparse ();
#endif
#else /* ! YYPARSE_PARAM */
#if defined __STDC__ || defined __cplusplus
int yyparse (void);
#else
int yyparse ();
#endif
#endif /* ! YYPARSE_PARAM */



/* The look-ahead symbol.  */
int yychar;

/* The semantic value of the look-ahead symbol.  */
YYSTYPE yylval;

/* Number of syntax errors so far.  */
int yynerrs;



/*----------.
| yyparse.  |
`----------*/

#ifdef YYPARSE_PARAM
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
int
yyparse (void *YYPARSE_PARAM)
#else
int
yyparse (YYPARSE_PARAM)
    void *YYPARSE_PARAM;
#endif
#else /* ! YYPARSE_PARAM */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
int
yyparse (void)
#else
int
yyparse ()

#endif
#endif
{
  
  int yystate;
  int yyn;
  int yyresult;
  /* Number of tokens to shift before error messages enabled.  */
  int yyerrstatus;
  /* Look-ahead token as an internal (translated) token number.  */
  int yytoken = 0;
#if YYERROR_VERBOSE
  /* Buffer for error messages, and its allocated size.  */
  char yymsgbuf[128];
  char *yymsg = yymsgbuf;
  YYSIZE_T yymsg_alloc = sizeof yymsgbuf;
#endif

  /* Three stacks and their tools:
     `yyss': related to states,
     `yyvs': related to semantic values,
     `yyls': related to locations.

     Refer to the stacks thru separate pointers, to allow yyoverflow
     to reallocate them elsewhere.  */

  /* The state stack.  */
  yytype_int16 yyssa[YYINITDEPTH];
  yytype_int16 *yyss = yyssa;
  yytype_int16 *yyssp;

  /* The semantic value stack.  */
  YYSTYPE yyvsa[YYINITDEPTH];
  YYSTYPE *yyvs = yyvsa;
  YYSTYPE *yyvsp;



#define YYPOPSTACK(N)   (yyvsp -= (N), yyssp -= (N))

  YYSIZE_T yystacksize = YYINITDEPTH;

  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;


  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int yylen = 0;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yystate = 0;
  yyerrstatus = 0;
  yynerrs = 0;
  yychar = YYEMPTY;		/* Cause a token to be read.  */

  /* Initialize stack pointers.
     Waste one element of value and location stack
     so that they stay on the same level as the state stack.
     The wasted elements are never initialized.  */

  yyssp = yyss;
  yyvsp = yyvs;

  goto yysetstate;

/*------------------------------------------------------------.
| yynewstate -- Push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
 yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  yyssp++;

 yysetstate:
  *yyssp = yystate;

  if (yyss + yystacksize - 1 <= yyssp)
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYSIZE_T yysize = yyssp - yyss + 1;

#ifdef yyoverflow
      {
	/* Give user a chance to reallocate the stack.  Use copies of
	   these so that the &'s don't force the real ones into
	   memory.  */
	YYSTYPE *yyvs1 = yyvs;
	yytype_int16 *yyss1 = yyss;


	/* Each stack pointer address is followed by the size of the
	   data in use in that stack, in bytes.  This used to be a
	   conditional around just the two extra args, but that might
	   be undefined if yyoverflow is a macro.  */
	yyoverflow (YY_("memory exhausted"),
		    &yyss1, yysize * sizeof (*yyssp),
		    &yyvs1, yysize * sizeof (*yyvsp),

		    &yystacksize);

	yyss = yyss1;
	yyvs = yyvs1;
      }
#else /* no yyoverflow */
# ifndef YYSTACK_RELOCATE
      goto yyexhaustedlab;
# else
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
	goto yyexhaustedlab;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
	yystacksize = YYMAXDEPTH;

      {
	yytype_int16 *yyss1 = yyss;
	union yyalloc *yyptr =
	  (union yyalloc *) YYSTACK_ALLOC (YYSTACK_BYTES (yystacksize));
	if (! yyptr)
	  goto yyexhaustedlab;
	YYSTACK_RELOCATE (yyss);
	YYSTACK_RELOCATE (yyvs);

#  undef YYSTACK_RELOCATE
	if (yyss1 != yyssa)
	  YYSTACK_FREE (yyss1);
      }
# endif
#endif /* no yyoverflow */

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;


      YYDPRINTF ((stderr, "Stack size increased to %lu\n",
		  (unsigned long int) yystacksize));

      if (yyss + yystacksize - 1 <= yyssp)
	YYABORT;
    }

  YYDPRINTF ((stderr, "Entering state %d\n", yystate));

  goto yybackup;

/*-----------.
| yybackup.  |
`-----------*/
yybackup:

  /* Do appropriate processing given the current state.  Read a
     look-ahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to look-ahead token.  */
  yyn = yypact[yystate];
  if (yyn == YYPACT_NINF)
    goto yydefault;

  /* Not known => get a look-ahead token if don't already have one.  */

  /* YYCHAR is either YYEMPTY or YYEOF or a valid look-ahead symbol.  */
  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token: "));
      yychar = YYLEX;
    }

  if (yychar <= YYEOF)
    {
      yychar = yytoken = YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yyn == 0 || yyn == YYTABLE_NINF)
	goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  if (yyn == YYFINAL)
    YYACCEPT;

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  /* Shift the look-ahead token.  */
  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);

  /* Discard the shifted token unless it is eof.  */
  if (yychar != YYEOF)
    yychar = YYEMPTY;

  yystate = yyn;
  *++yyvsp = yylval;

  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- Do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     `$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
        case 2:

    {(yyval.TruckLoadingJobFileVal) = new TruckLoadingJobFile((yyvsp[(1) - (2)].XmlVersionVal), (yyvsp[(2) - (2)].TruckLoadingJobTypeVal));
	   TruckLoadingJobTree = (yyval.TruckLoadingJobFileVal);
	  ;}
    break;

  case 3:

    {(yyval.SchemaLocationVal) = new SchemaLocation("plt", (yyvsp[(2) - (2)].sVal));
	    if (strncmp("urn:Palletizing ", (yyvsp[(2) - (2)].sVal), 16))
	      {
		fprintf(stderr,
	           "wrong targetNamespace in schema location %s\n", (yyvsp[(2) - (2)].sVal));
		exit(1);
	      }
	  ;}
    break;

  case 4:

    {double * val;
	   val = new double;
	   if (sscanf((yyvsp[(1) - (1)].sVal), "%lf", val) != 1)
	     yyerror("bad value - must be double");
	   (yyval.dVal) = val;
	  ;}
    break;

  case 5:

    {(yyval.sVal) = (yyvsp[(1) - (1)].sVal);;}
    break;

  case 6:

    {(yyval.XmlVersionVal) = new XmlVersion(false);
	   if (strcmp((yyvsp[(3) - (4)].sVal), "1.0"))
	     yyerror("version number must be 1.0");
	  ;}
    break;

  case 7:

    {(yyval.XmlVersionVal) = new XmlVersion(true);
	   if (strcmp((yyvsp[(3) - (6)].sVal), "1.0"))
	     yyerror("version number must be 1.0");
	   else if (strcmp((yyvsp[(5) - (6)].sVal), "UTF-8"))
	     yyerror("encoding must be UTF-8");
	  ;}
    break;

  case 8:

    {readData = 1;;}
    break;

  case 9:

    {(yyval.PalletDistanceTypeVal) = new PalletDistanceType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletDistanceTypeVal)->bad)
	     yyerror("bad BackAreaHeight value");
	  ;}
    break;

  case 10:

    {(yyval.BackAreaTypeVal) = new BackAreaType((yyvsp[(2) - (5)].PalletDistanceTypeVal), (yyvsp[(3) - (5)].PalletDistanceTypeVal), (yyvsp[(4) - (5)].DoorTypeListVal), (yyvsp[(5) - (5)].WheelWellTypeListVal));;}
    break;

  case 11:

    {(yyval.BackAreaTypeVal) = (yyvsp[(2) - (3)].BackAreaTypeVal);;}
    break;

  case 12:

    {readData = 1;;}
    break;

  case 13:

    {(yyval.sVal) = (yyvsp[(4) - (5)].sVal);;}
    break;

  case 14:

    {readData = 1;;}
    break;

  case 15:

    {(yyval.sVal) = (yyvsp[(4) - (5)].sVal);;}
    break;

  case 16:

    {(yyval.DoorTypeVal) = new DoorType((yyvsp[(2) - (6)].sVal), (yyvsp[(3) - (6)].PalletCoordinateTypeVal), (yyvsp[(4) - (6)].PalletCoordinateTypeVal), (yyvsp[(5) - (6)].PalletDistanceTypeVal), (yyvsp[(6) - (6)].PalletDistanceTypeVal));;}
    break;

  case 17:

    {(yyval.DoorTypeVal) = (yyvsp[(2) - (3)].DoorTypeVal);;}
    break;

  case 18:

    {(yyval.DoorTypeListVal) = new std::list<DoorType *>;
	   (yyval.DoorTypeListVal)->push_back((yyvsp[(1) - (1)].DoorTypeVal));;}
    break;

  case 19:

    {(yyval.DoorTypeListVal) = (yyvsp[(1) - (2)].DoorTypeListVal);
	   (yyval.DoorTypeListVal)->push_back((yyvsp[(2) - (2)].DoorTypeVal));;}
    break;

  case 20:

    {(yyval.EmptyTruckTypeVal) = new EmptyTruckType((yyvsp[(2) - (7)].sVal), (yyvsp[(3) - (7)].sVal), (yyvsp[(4) - (7)].PalletWeightTypeVal), (yyvsp[(5) - (7)].PalletDistanceTypeVal), (yyvsp[(6) - (7)].BackAreaTypeVal), (yyvsp[(7) - (7)].FrontAreaTypeVal));;}
    break;

  case 21:

    {(yyval.EmptyTruckTypeVal) = (yyvsp[(2) - (3)].EmptyTruckTypeVal);;}
    break;

  case 22:

    {(yyval.FrontAreaTypeVal) = new FrontAreaType((yyvsp[(2) - (4)].PalletDistanceTypeVal), (yyvsp[(3) - (4)].PalletDistanceTypeVal), (yyvsp[(4) - (4)].PalletDistanceTypeVal));;}
    break;

  case 23:

    {(yyval.FrontAreaTypeVal) = 0;;}
    break;

  case 24:

    {(yyval.FrontAreaTypeVal) = (yyvsp[(2) - (3)].FrontAreaTypeVal);;}
    break;

  case 25:

    {readData = 1;;}
    break;

  case 26:

    {(yyval.PalletDistanceTypeVal) = new PalletDistanceType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletDistanceTypeVal)->bad)
	     yyerror("bad HeightAboveBack value");
	  ;}
    break;

  case 27:

    {readData = 1;;}
    break;

  case 28:

    {(yyval.PalletDistanceTypeVal) = new PalletDistanceType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletDistanceTypeVal)->bad)
	     yyerror("bad Height value");
	  ;}
    break;

  case 29:

    {readData = 1;;}
    break;

  case 30:

    {(yyval.sVal) = (yyvsp[(4) - (5)].sVal);;}
    break;

  case 31:

    {readData = 1;;}
    break;

  case 32:

    {(yyval.PalletDistanceTypeVal) = new PalletDistanceType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletDistanceTypeVal)->bad)
	     yyerror("bad Length value");
	  ;}
    break;

  case 33:

    {readData = 1;;}
    break;

  case 34:

    {(yyval.PalletWeightTypeVal) = new PalletWeightType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletWeightTypeVal)->bad)
	     yyerror("bad MaximumLoadWeight value");
	  ;}
    break;

  case 35:

    {(yyval.PalletForTruckTypeVal) = new PalletForTruckType((yyvsp[(2) - (6)].sVal), (yyvsp[(3) - (6)].PalletWeightTypeVal), (yyvsp[(4) - (6)].PalletDistanceTypeVal), (yyvsp[(5) - (6)].PalletDistanceTypeVal), (yyvsp[(6) - (6)].PalletDistanceTypeVal));;}
    break;

  case 36:

    {readData = 1;;}
    break;

  case 37:

    {(yyval.sVal) = (yyvsp[(4) - (5)].sVal);;}
    break;

  case 38:

    {(yyval.PalletSetTypeVal) = new PalletSetType((yyvsp[(2) - (3)].PalletForTruckTypeListVal), (yyvsp[(3) - (3)].sVal));;}
    break;

  case 39:

    {(yyval.PalletSetTypeVal) = (yyvsp[(2) - (3)].PalletSetTypeVal);;}
    break;

  case 40:

    {(yyval.PalletSetTypeListVal) = new std::list<PalletSetType *>;
	   (yyval.PalletSetTypeListVal)->push_back((yyvsp[(1) - (1)].PalletSetTypeVal));;}
    break;

  case 41:

    {(yyval.PalletSetTypeListVal) = (yyvsp[(1) - (2)].PalletSetTypeListVal);
	   (yyval.PalletSetTypeListVal)->push_back((yyvsp[(2) - (2)].PalletSetTypeVal));;}
    break;

  case 42:

    {(yyval.PalletForTruckTypeVal) = (yyvsp[(2) - (3)].PalletForTruckTypeVal);;}
    break;

  case 43:

    {(yyval.PalletForTruckTypeListVal) = new std::list<PalletForTruckType *>;
	   (yyval.PalletForTruckTypeListVal)->push_back((yyvsp[(1) - (1)].PalletForTruckTypeVal));;}
    break;

  case 44:

    {(yyval.PalletForTruckTypeListVal) = (yyvsp[(1) - (2)].PalletForTruckTypeListVal);
	   (yyval.PalletForTruckTypeListVal)->push_back((yyvsp[(2) - (2)].PalletForTruckTypeVal));;}
    break;

  case 45:

    {(yyval.sVal) = 0;;}
    break;

  case 46:

    {readData = 1;;}
    break;

  case 47:

    {(yyval.sVal) = (yyvsp[(4) - (5)].sVal);;}
    break;

  case 48:

    {(yyval.TruckLoadingJobTypeVal) = new TruckLoadingJobType((yyvsp[(3) - (7)].SchemaLocationVal), (yyvsp[(5) - (7)].sVal), (yyvsp[(6) - (7)].PalletSetTypeListVal), (yyvsp[(7) - (7)].EmptyTruckTypeVal));;}
    break;

  case 49:

    {(yyval.TruckLoadingJobTypeVal) = (yyvsp[(2) - (3)].TruckLoadingJobTypeVal);;}
    break;

  case 50:

    {readData = 1;;}
    break;

  case 51:

    {(yyval.sVal) = (yyvsp[(4) - (5)].sVal);;}
    break;

  case 52:

    {readData = 1;;}
    break;

  case 53:

    {(yyval.PalletWeightTypeVal) = new PalletWeightType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletWeightTypeVal)->bad)
	     yyerror("bad Weight value");
	  ;}
    break;

  case 54:

    {(yyval.WheelWellTypeVal) = new WheelWellType((yyvsp[(2) - (6)].PalletCoordinateTypeVal), (yyvsp[(3) - (6)].PalletCoordinateTypeVal), (yyvsp[(4) - (6)].PalletDistanceTypeVal), (yyvsp[(5) - (6)].PalletDistanceTypeVal), (yyvsp[(6) - (6)].PalletDistanceTypeVal));;}
    break;

  case 55:

    {(yyval.WheelWellTypeVal) = (yyvsp[(2) - (3)].WheelWellTypeVal);;}
    break;

  case 56:

    {(yyval.WheelWellTypeListVal) = new std::list<WheelWellType *>;;}
    break;

  case 57:

    {(yyval.WheelWellTypeListVal) = (yyvsp[(1) - (2)].WheelWellTypeListVal);
	   (yyval.WheelWellTypeListVal)->push_back((yyvsp[(2) - (2)].WheelWellTypeVal));;}
    break;

  case 58:

    {readData = 1;;}
    break;

  case 59:

    {(yyval.PalletDistanceTypeVal) = new PalletDistanceType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletDistanceTypeVal)->bad)
	     yyerror("bad Width value");
	  ;}
    break;

  case 60:

    {readData = 1;;}
    break;

  case 61:

    {(yyval.PalletCoordinateTypeVal) = new PalletCoordinateType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletCoordinateTypeVal)->bad)
	     yyerror("bad Xcoordinate value");
	  ;}
    break;

  case 62:

    {readData = 1;;}
    break;

  case 63:

    {(yyval.PalletCoordinateTypeVal) = new PalletCoordinateType((yyvsp[(4) - (5)].dVal));
	   if ((yyval.PalletCoordinateTypeVal)->bad)
	     yyerror("bad Ycoordinate value");
	  ;}
    break;


/* Line 1267 of yacc.c.  */

      default: break;
    }
  YY_SYMBOL_PRINT ("-> $$ =", yyr1[yyn], &yyval, &yyloc);

  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);

  *++yyvsp = yyval;


  /* Now `shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */

  yyn = yyr1[yyn];

  yystate = yypgoto[yyn - YYNTOKENS] + *yyssp;
  if (0 <= yystate && yystate <= YYLAST && yycheck[yystate] == *yyssp)
    yystate = yytable[yystate];
  else
    yystate = yydefgoto[yyn - YYNTOKENS];

  goto yynewstate;


/*------------------------------------.
| yyerrlab -- here on detecting error |
`------------------------------------*/
yyerrlab:
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
#if ! YYERROR_VERBOSE
      yyerror (YY_("syntax error"));
#else
      {
	YYSIZE_T yysize = yysyntax_error (0, yystate, yychar);
	if (yymsg_alloc < yysize && yymsg_alloc < YYSTACK_ALLOC_MAXIMUM)
	  {
	    YYSIZE_T yyalloc = 2 * yysize;
	    if (! (yysize <= yyalloc && yyalloc <= YYSTACK_ALLOC_MAXIMUM))
	      yyalloc = YYSTACK_ALLOC_MAXIMUM;
	    if (yymsg != yymsgbuf)
	      YYSTACK_FREE (yymsg);
	    yymsg = (char *) YYSTACK_ALLOC (yyalloc);
	    if (yymsg)
	      yymsg_alloc = yyalloc;
	    else
	      {
		yymsg = yymsgbuf;
		yymsg_alloc = sizeof yymsgbuf;
	      }
	  }

	if (0 < yysize && yysize <= yymsg_alloc)
	  {
	    (void) yysyntax_error (yymsg, yystate, yychar);
	    yyerror (yymsg);
	  }
	else
	  {
	    yyerror (YY_("syntax error"));
	    if (yysize != 0)
	      goto yyexhaustedlab;
	  }
      }
#endif
    }



  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse look-ahead token after an
	 error, discard it.  */

      if (yychar <= YYEOF)
	{
	  /* Return failure if at end of input.  */
	  if (yychar == YYEOF)
	    YYABORT;
	}
      else
	{
	  yydestruct ("Error: discarding",
		      yytoken, &yylval);
	  yychar = YYEMPTY;
	}
    }

  /* Else will try to reuse look-ahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*---------------------------------------------------.
| yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
yyerrorlab:

  /* Pacify compilers like GCC when the user code never invokes
     YYERROR and the label yyerrorlab therefore never appears in user
     code.  */
  if (/*CONSTCOND*/ 0)
     goto yyerrorlab;

  /* Do not reclaim the symbols of the rule which action triggered
     this YYERROR.  */
  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);
  yystate = *yyssp;
  goto yyerrlab1;


/*-------------------------------------------------------------.
| yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;	/* Each real token shifted decrements this.  */

  for (;;)
    {
      yyn = yypact[yystate];
      if (yyn != YYPACT_NINF)
	{
	  yyn += YYTERROR;
	  if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYTERROR)
	    {
	      yyn = yytable[yyn];
	      if (0 < yyn)
		break;
	    }
	}

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
	YYABORT;


      yydestruct ("Error: popping",
		  yystos[yystate], yyvsp);
      YYPOPSTACK (1);
      yystate = *yyssp;
      YY_STACK_PRINT (yyss, yyssp);
    }

  if (yyn == YYFINAL)
    YYACCEPT;

  *++yyvsp = yylval;


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", yystos[yyn], yyvsp, yylsp);

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturn;

/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturn;

#ifndef yyoverflow
/*-------------------------------------------------.
| yyexhaustedlab -- memory exhaustion comes here.  |
`-------------------------------------------------*/
yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  /* Fall through.  */
#endif

yyreturn:
  if (yychar != YYEOF && yychar != YYEMPTY)
     yydestruct ("Cleanup: discarding lookahead",
		 yytoken, &yylval);
  /* Do not reclaim the symbols of the rule which action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (yylen);
  YY_STACK_PRINT (yyss, yyssp);
  while (yyssp != yyss)
    {
      yydestruct ("Cleanup: popping",
		  yystos[*yyssp], yyvsp);
      YYPOPSTACK (1);
    }
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif
#if YYERROR_VERBOSE
  if (yymsg != yymsgbuf)
    YYSTACK_FREE (yymsg);
#endif
  /* Make sure YYID is used.  */
  return YYID (yyresult);
}





/*********************************************************************/

/* yyerror

Returned Value: int (0)

Called By: yyparse

This prints whatever string the parser provides.

*/

int yyerror(      /* ARGUMENTS       */
 const char * s)  /* string to print */
{
  fflush(stdout);
  fprintf(stderr, "\n%s\n", s);
  exit(1);
  return 0;
}

/*********************************************************************/

