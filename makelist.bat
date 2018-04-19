REM Make sure this points to vcvarsall.bat in your version of Visual Studio
REM You could replace this with a shortcut or another batch file
call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat" %1

REM Compiler output (OUTDIR/[release/debug]/[x86/x64]/APP)
set OUTDIR=out
set APP=app.exe

REM Binary files temp location
set BINDIR=bin

REM Lib files location
REM dll files found in an x86 or x64 folder in LIBDIR will be copied into the folder with APP
set LIBDIR=lib
REM Libs to include (will be prepended with LIBDIR/)
set LIBS=lib1.lib lib2.lib

REM Source targets
REM Note: the naming scheme here is important, the names in the SOURCES list will be appended with _SRC, _OBJ and _INC to get the source directory, C/C++ files and include directories respectively
REM target -> target_SRC, target_OBJ, target_INC
REM Note: _SRC should only have a single folder, _OBJ and _INC are space separated lists of files/folders
set SOURCES=target1 target2 target3

set target1_SRC=../external_folder
set target1_OBJ=external_cpp.cpp
set target1_INC=../external_folder/include ../external_folder/include/asdfghjkl

set target2_SRC=src/some/other/folders
set target2_OBJ=gl3w.c imgui_impl_sdl_gl3.cpp
set target2_INC=include include/qwerty

set target3_SRC=src
set target3_OBJ=main.cpp other_main.cpp another.cpp
set target3_INC=include ../external_folder