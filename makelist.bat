REM Output file name
set APP=app.exe

REM Compiler output (%OUTDIR%\[release/debug]\[x86/x64]\%APP%)
set OUTDIR=out
REM Binary files temp location
set BINDIR=bin
REM Lib files location
set LIBDIR=lib

REM dll files found in an x86 or x64 folder in LIBDIR will be copied into the folder with APP
REM ".\%LIBDIR%\[x64/x86]\%LIB%" -> ".\%LIB%" (for each LIB in %LIBS%)
set LIBS=lib1.lib lib2.dll

REM Source targets
REM Note: the naming scheme here is important, the names in the SOURCES list will be appended with _SRC, _OBJ and _INC to get the source directory, C/C++ files and include directories respectively
REM target -> target_SRC, target_OBJ, target_INC
REM Note: _SRC should only have a single folder, _OBJ and _INC are space separated lists of files/folders
set SOURCES=target1 target2 target3

set target1_SRC=..\external_folder
set target1_OBJ=external_cpp.cpp
set target1_INC=..\external_folder\include ..\external_folder\include\asdfghjkl

set target2_SRC=src\some\other\folders
set target2_OBJ=file.c anotherCppFile.cpp
set target2_INC=include include\qwerty

set target3_SRC=C:\absolute\directory
set target3_OBJ=main.cpp other_main.cpp another.cpp
set target3_INC=include ..\external_folder

REM Version of C++ to be used (-std:%CPPVER%)
set CPPVER=c++latest

REM Command line options for both modes (EXE)
set COMPOPT=/nologo /EHa /MD /bigobj
set LINKOPT=/nologo

REM Command line options for both modes (DLL)
REM set COMPOPT=/nologo /EHa /MD /bigobj
REM set LINKOPT=/nologo /DLL

REM Command line options for release mode
set RELCOMPOPT=/DNDEBUG
set RELLINKOPT=

REM Command line options for debug mode
set DBGCOMPOPT=/Zi
set DBGLINKOPT=/DEBUG

REM Skip vcvarsall.bat if in clean mode
if "%1"=="clean" goto :eof

REM Make sure this points to vcvarsall.bat in your version of Visual Studio
REM You could replace this with a shortcut or another batch file
call vcvarsall.bat %1