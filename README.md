# winmake

Build scripts with no external software dependencies

`make.bat` compares the built object last-modified-date times with their repective source files to see if they need to be rebuilt (similar to GNU-make), this should result in a compile time speed up for large projects

# Setup

## The Easy Way (genmake)

Simply run `genmake.py`, it will ask you a bunch of questions about the project and build a `make.bat` and `makelist.bat` or `makefile` to match. It will attempt to find `.c`, `.cxx` and `.cpp` files within the project to add to the source lists

```
> python genmake.py
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
Create new make.bat? (Will overwrite existing file) [y/n]: y
Include source "src"? [y/n]: y
Include source "src.bak"? [y/n]: n
Include source "lib"? [y/n]: y
Source "src" include directories (optional): include lib
Source "lib" include directories (optional): include lib ../../external/dependecy
```

## The Hard Way

Copy `make.bat` and `makelist.bat` (and `makefile` for cross-platform projects) into the root directory of your project and edit them manually (instructions below)

## `makelist.bat`

`APP` is the file name for the executable

`OUTDIR` is the directory where the executable will be saved

`BINDIR` is where the unlinked binary blobs will be stored (`make clean` will delete everything in this folder)

`LIBDIR` is the directory where the libs are stored. Note: the libs must be in an `x86` or `x64` folder inside the `LIBDIR` folder

`LIBS` is the list of libs to include at link time

`*_SRC` is the root directroy (where the C/C++ files are) for source `*`.

`*_OBJ` is the list of C/C++ files in `*_SRC` that should be compiled for source `*`.

`*_INC` is a list of include directories for source `*`.

`SOURCES` is the list of sources (the `*` in `*_SRC`, `*_OBJ`, `*_INC`) to compile. This is not a list of C/C++ files.

`CPPVER` is the vertions of C++ to use (c++11, c++latest, etc)

`COMPOPT` is the compiler flags to use

`LINKOPT` is the linker flags to use

`RELCOMPOPT` is the compilers flags to use in only `release` mode

`RELLINKOPT` is the linker flags to use in only `release` mode

`DBGCOMPOPT` is the compiler flags to use in only `debug` mode

`DBGLINKOPT` is the linker flags to use in only `debug` mode

`call vcvarsall.bat %1` should be changed to point to `vcvarsall.bat` in your version of Visual Studio. If `vcvarsall.bat` is in your system PATH variable then you can leave it as is

Example:

```
set APP=app.exe
set OUTDIR=out
set BINDIR=bin
set LIBDIR=lib
set LIBS=lib1.lib lib2.lib

set SOURCES=target1 target2 target3

set target1_SRC=..\external_folder
set target1_OBJ=external_cpp.cpp
set target1_INC=..\external_folder\include ..\external_folder\include\asdfghjkl

set target2_SRC=src\some\other\folders
set target2_OBJ=file.c anotherCppFile.cpp
set target2_INC=include include\qwerty

set target3_SRC=src C:\absolute\directory
set target3_OBJ=main.cpp other_main.cpp another.cpp
set target3_INC=include ..\external_folder

set CPPVER=c++latest

set COMPOPT=/nologo /EHa /MD /MP
set LINKOPT=/nologo

set RELCOMPOPT=/DNDEBUG
set RELLINKOPT=

set DBGCOMPOPT=/Zi
set DBGLINKOPT=/DEBUG

if not "%1"=="x64" if not "%1"=="x86" goto :eof
call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat" %1
```

## `makefile`

The makefile is laid out in a similar way to `makelist.bat`, the only differences are the `CXX` definition at the top (which compiler to use), `LIBDIR` supporting multiple directories and the templates at the bottom (don't change these)

Example:

```
CXX = g++
APP = app
OUTDIR = out
BINDIR = bin
LIBDIR = lib libdir2
LIBS = dl pthread
SOURCES = target1
target1_SRC = ../external_folder
target1_OBJ = external_cpp.cpp
target1_INC = ../external_folder/include ../external_folder/include/asdfghjkl
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
```

# Running

## Windows

To compile an x86 release ``> make release x86``

To compile an x64 release ``> make release x64``

To compile an x86 debug ``> make debug x86``

To compile an x64 debug ``> make debug x64``

To clean out the object folder ``> make clean``

## Linux/etc...

To compile a release ``> make release``

To compile a debug ``> make debug``

To clean out the object folder ``> make clean``
