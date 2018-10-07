CXX = g++				#bat CXX = vcvarsall.bat
CPPVER = c++11

APP = app				#bat APP = app.exe
OUTDIR = out
BINDIR = bin
LIBDIR = lib
LIBS = dl pthread		#bat LIBS =

SOURCES=target1 target2 target3

target1_SRC=../external_folder
target1_OBJ=external_cpp.cpp
target1_HDR=external_header.h or_even_a_picture.png
target1_DEP=
target1_INC=../external_folder/include ../external_folder/include/asdfghjkl

target2_SRC=src/some/other/folders
target2_OBJ=asdasda.cpp qwerty.cpp
target1_HDR=external_header.h or_even_a_picture.png
target1_DEP=target1
target2_INC=include include/qwerty

target3_SRC=src
target3_OBJ=main.cpp other_main.cpp another.cpp
target1_HDR=main.h
target3_DEP=target1 target2 # don't need to _INC a folder if it is the source of one of the dependencies
target3_INC=include			#bat target3_INC = include different/include/for/windows

# BUILD SCRIPT

ALL_OBJ = $(foreach src,$(SOURCES),$(foreach obj,$($(src)_OBJ),$(src)$(obj).o))
ALL_HDR = $(foreach src,$(SOURCES),$(foreach header,$($(src)_HDR),$($(src)_SRC)/$(header)))

.PHONY: all
all: release

debug: $(BINDIR) $(OUTDIR) $(foreach obj,$(ALL_OBJ),$(BINDIR)/dbg$(obj))
	$(CXX) -std=$(CPPVER) $(foreach obj,$(ALL_OBJ),$(BINDIR)/dbg$(obj)) $(foreach libdir,$(LIBDIR),-L$(libdir)) $(foreach lib,$(LIBS),-l$(lib)) $(COMPOPT) $(LINKOPT) $(DBGLINKOPT) -o $(OUTDIR)/$(APP)

release: $(BINDIR) $(OUTDIR) $(foreach obj,$(ALL_OBJ),$(BINDIR)/rel$(obj))
	$(CXX) -std=$(CPPVER) $(foreach obj,$(ALL_OBJ),$(BINDIR)/rel$(obj)) $(foreach libdir,$(LIBDIR),-L$(libdir)) $(foreach lib,$(LIBS),-l$(lib)) $(COMPOPT) $(LINKOPT) $(RELLINKOPT) -o $(OUTDIR)/$(APP)

clean: $(BINDIR)
	cd $(BINDIR) && rm -f *.o

$(OUTDIR):
	if [ ! -d $@ ]; then mkdir $@; fi
$(BINDIR):
	if [ ! -d $@ ]; then mkdir $@; fi

define COMPILE_TEMPLATE =
$(BINDIR)/dbg$(1)%.o: $(2)/% $(3)
	$(CXX) -std=$(CPPVER) -c $(4) $(COMPOPT) $(DBGCOMPOPT) -o $$@ $$<
$(BINDIR)/rel$(1)%.o: $(2)/% $(3)
	$(CXX) -std=$(CPPVER) -c $(4) $(COMPOPT) $(RELCOMPOPT) -o $$@ $$<
endef

$(foreach src,$(SOURCES),$(eval $(call COMPILE_TEMPLATE,$(src),$($(src)_SRC),$(foreach header,$($(src)_HDR),$($(src)_SRC)/$(header)) $(foreach dep,$($(src)_DEP),$(foreach depobj,$($(dep)_OBJ),$($(dep)_SRC)/$(depobj)) $(foreach dephdr,$($(dep)_HDR),$($(dep)_SRC)/$(dephdr))),$(foreach inc,$($(src)_INC),-I$(inc)) $(foreach dep,$($(src)_DEP),-I$($(dep)_SRC)))))