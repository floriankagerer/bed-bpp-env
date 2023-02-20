EXTRA_DIST = \
ax_pthread.m4 \
ax_check_gl.m4 \
ax_check_glu.m4 \
ax_check_glut.m4 \
acinclude.m4 \
Makefile.am \
configure.ac \
autogen.sh \
SampleData/InterfaceSpecificationForMixedPalletizing.01.pdf \
SampleData/Food001_1AsBuilt.log \
SampleData/Food001_1Order.xml \
SampleData/Food001_1Packlist.xml \
SampleData/scoreAsPlannedConfig1.xml \
SampleData/truckLoadingPlan1.xml \
SampleData/truckLoadingJob1.xml \
Schema/*

lib_LTLIBRARIES = libpallet.la
libpallet_la_SOURCES = \
palletView/libpallet.cc \
palletView/palletViewer.h \
palletView/palletViewer.cc \
palletView/xml_parser.cc \
palletView/response.cc \
palletView/packlist.cc \
palletView/asBuilt.cc \
palletView/scoreAsPlannedClasses.cc \
palletView/scoreAsPlannedClasses.hh \
palletView/scoreAsPlannedLex.cc     \
palletView/scoreAsPlannedYACC.cc    \
palletView/scoreAsPlannedYACC.hh    \
palletView/asBuilt.h \
palletView/packlist.h \
palletView/response.h \
palletView/xml_parser.h 

noinst_PROGRAMS = truckViewer

truckViewer_SOURCES =                                      \
truckView/mouse.cc                       \
truckView/mouse.hh                       \
truckView/PalletizingDataTypesClasses.cc \
truckView/PalletizingDataTypesClasses.hh \
truckView/TruckLoadingJobClasses.cc      \
truckView/TruckLoadingJobClasses.hh      \
truckView/TruckLoadingJobLex.cc          \
truckView/TruckLoadingJobYACC.cc         \
truckView/TruckLoadingJobYACC.hh         \
truckView/TruckLoadingPlanClasses.cc     \
truckView/TruckLoadingPlanClasses.hh     \
truckView/TruckLoadingPlanLex.cc         \
truckView/TruckLoadingPlanYACC.cc        \
truckView/TruckLoadingPlanYACC.hh        \
truckView/truckViewer.cc                 \
truckView/truckViewer.h                  \
truckView/view.cc                        \
truckView/view.h                         \
truckView/xmlSchemaInstance.cc           \
truckView/xmlSchemaInstance.hh

truckViewer_CXXFLAGS = @X_CFLAGS@ @GL_CFLAGS@ @GLU_CFLAGS@ @GLUT_CFLAGS@
truckViewer_LDADD = $(bin_LIBS) @GLUT_LIBS@ @GLU_LIBS@ @GL_LIBS@ @X_EXTRA_LIBS@ @X_PRE_LIBS@ @X_LIBS@ -lX11 -lglut
