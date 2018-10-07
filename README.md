# winmake

Build scripts with no external software dependencies

`make.bat` is designed to emulate GNU-make on Windows systems. Because it uses JScript for most of the heavy lifting, it is able to read parameters directly from the `Makefile`

`make.bat` with the `incremental` option compares the built object last-modified-date times with their repective source files to see if they need to be rebuilt, this should result in a compile time speed up for large projects with very few changes. If not using the `incremental` option, `mutli` is recommended (where possible), this option applies the /MP compiler option on MSVC

# Running

## Windows

To compile an x86 release
>``> make release x86``

To compile an x64 release
>``> make release x64``

To compile an x86 debug
>``> make debug x86``

To compile an x64 debug
>``> make debug x64``

To compile an x64 debug incrementally
>``> make debug x64 incremental``

To compile an x64 debug with the multi-thread option (/MP)
>``> make debug x64 multi``

Multi and incremental can be used at the same time (in any order)
>``>make debug x64 multi incremental``

To clean the object folder
>``> make clean``

## Linux/etc...

To compile a release
>``> make release``

To compile a debug
>``> make debug``

To clean out the object folder
>``> make clean``

# Setup

## The Easy Way (genmake)

Simply run `genmake.py`, it will ask you a bunch of questions about the project and build a `make.bat` and `makelist.bat` or `Makefile` to match. It will attempt to find `.c`, `.cxx` and `.cpp` files within the project to add to the source lists

```
> python genmake.py
Create new makelist.bat? (Will overwrite existing file) [y/n]: y
Output name (ie app.exe or lib.dll): app.exe
Output directory: out
Binaries directory: bin
Library directory (optional): lib
Libraries (optional): lib1.lib lib2.dll
Path to vcvarsall.bat (optional if in PATH): vcvarsall.bat
C++ version (ie c++11 or c++latest): c++latest
Compiler options (optional): /nologo /EHa /MD /MP
Linker options (optional): /nologo
Debug mode compiler options (optional): /Zi
Debug mode linker options (optional): /DEBUG
Release mode compiler options (optional): /DNDEBUG
Release mode linker options (optional):
Include source "src"? [y/n]: y
Include source "src.bak"? [y/n]: n
Include source "lib"? [y/n]: y
Source "src" dependency sources: lib
Source "src" include directories (optional): include lib
Source "lib" dependency sources:
Source "lib" include directories (optional): include lib ../../external/dependecy
```

## The Hard Way

Copy `make.bat` and `makelist.bat` (and `Makefile` for cross-platform projects) into the root directory of your project and edit them manually (instructions below)

## `Makefile`

`#bat ...` tells `make.bat` to use the following variable definition. This is how you can define things differently for Windows vs Linux

`APP` is the file name for the executable

`OUTDIR` is the directory where the executable will be saved

`BINDIR` is where the unlinked binary blobs will be stored (`make clean` will delete everything in this folder)

`LIBDIR` is the directory where the libs are stored. Note: the libs must be in an `x86` or `x64` folder inside the `LIBDIR` folder

`LIBS` is the list of libs to include at link time

`*_SRC` is the root directroy (where the C/C++ files are) for source `*`

`*_OBJ` is the list of C/C++ files in `*_SRC` that should be compiled for source `*`

`*_HDR` is the list of non-compiled/header files that should be checked before compiling `*_SRC` in incremental mode

`*_DEP` is the list of other sources (targets) that should be included and checked before compiling `*_SRC` in incremental mode

`*_INC` is a list of include directories for source `*`

`SOURCES` is the list of sources (the `*` in `*_SRC`, `*_OBJ`, `*_INC`) to compile. This is not a list of C/C++ files

`CPPVER` is the vertions of C++ to use (c++11, c++latest, etc)

`COMPOPT` is the compiler flags to use

`LINKOPT` is the linker flags to use

`RELCOMPOPT` is the compilers flags to use in only `release` mode

`RELLINKOPT` is the linker flags to use in only `release` mode

`DBGCOMPOPT` is the compiler flags to use in only `debug` mode

`DBGLINKOPT` is the linker flags to use in only `debug` mode

`CXX` should be your compiler (Linux) or changed to point to `vcvarsall.bat` in your version of Visual Studio (Windows). If `vcvarsall.bat` is in your system PATH variable then you can leave it as `vcvarsall.bat`

`# BUILD SCRIPT` this tells `make.bat` to stop reading the `Makefile`, ignored by GNU-make

Example:

``` Makefile
CXX = /usr/bin/g++-8	#bat CXX = vcvarsall.bat
CPPVER = c++17
APP = app				#bat APP = app.exe
OUTDIR = out
BINDIR = bin
LIBDIR = lib
LIBS =					#bat LIBS = SDL2main.lib SDL2.lib
COMPOPT = -ldl -lSDL2 -pthread -lstdc++fs	#bat COMPOPT = /nologo /EHa /MD /bigobj
LINKOPT =									#bat LINKOPT = /nologo
DBGCOMPOPT =			#bat DBGCOMPOPT = /Zi
DBGLINKOPT =			#bat DBGLINKOPT = /DEBUG
RELCOMPOPT = -DNDEBUG	#bat RELCOMPOPT = /DNDEBUG
RELLINKOPT =			#bat RELLINKOPT =

SOURCES = lib src

lib_SRC = ./lib
lib_OBJ = gl3w.c
lib_HDR = gl3w.h
lib_DEP =
lib_INC = include /usr/include/SDL2			#bat lib_INC = include include/SDL

src_SRC = ./src
src_OBJ = main.cpp draw.cpp update.cpp
src_HDR = main.h draw.h update.h
src_DEP = lib
src_INC = include /usr/include/SDL2			#bat src_INC = include include/SDL

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
```