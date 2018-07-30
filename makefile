CXX = g++

APP = app

OUTDIR = out
BINDIR = bin

LIBDIR = lib libdir2
LIBS = dl pthread

SOURCES=target1 target2 target3

target1_SRC=../external_folder
target1_OBJ=external_cpp.cpp
target1_INC=../external_folder/include ../external_folder/include/asdfghjkl

target2_SRC=src/some/other/folders
target2_OBJ=asdasda.cpp qwerty.cpp
target2_INC=include include/qwerty

target3_SRC=src
target3_OBJ=main.cpp other_main.cpp another.cpp
target3_INC=include ../external_folder

CPPVER = c++11

COMPOPT =
LINKOPT = 

RELLINKOPT = 
RELCOMPOPT =

DBGLINKOPT =
DBGCOMPOPT = -g

ALL_OBJ = $(foreach src,$(SOURCES),$(foreach obj,$($(src)_OBJ),$(BINDIR)/$(obj).o))

.PHONY: debug
debug: $(foreach obj,$(ALL_OBJ),debug-$(obj))
	$(call LINK_TEMPLATE,$(DBGLINKOPT))

release: $(foreach obj,$(ALL_OBJ),release-$(obj))
	$(call LINK_TEMPLATE,$(RELLINKOPT))

define LINK_TEMPLATE =
$(CXX) -std=$(CPPVER) -o $(OUTDIR)/$(APP) $(ALL_OBJ) $(foreach libdir,$(LIBDIR),-L$(libdir)) $(foreach lib,$(LIBS),-l$(lib)) $(COMPOPT) $(1)
endef

define COMPILE_TEMPLATE =
debug-$(2)/$(3).o: $(1)/$(3)
	$(CXX) -std=$(CPPVER) -c -o $(2)/$(3).o $(1)/$(3) $(4) $(DBGCOMPOPT)
release-$(2)/$(3).o: $(1)/$(3)
	$(CXX) -std=$(CPPVER) -c -o $(2)/$(3).o $(1)/$(3) $(4) $(RELCOMPOPT)
endef

$(foreach src,$(SOURCES),$(foreach obj,$($(src)_OBJ),$(eval $(call COMPILE_TEMPLATE,$($(src)_SRC),$(BINDIR),$(obj),$(foreach inc,$($(src)_INC),-I$(inc))))))

clean:
	rm -f $(ALL_OBJ)