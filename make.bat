@if (@a==@b) @end /*
@echo off
SetLocal EnableDelayedExpansion

set mode=%1
set target=%2

if not "%mode%"=="debug" if not "%mode%"=="release" if not "%mode%"=="clean" (
    echo unknown mode "%mode%"
    goto usage
)

if "%mode%"=="clean" (
    call makelist.bat clean
    goto clean
)

call makelist.bat %target%

if not "%target%"=="x86" if not "%target%"=="x64" (
    echo unknown target "%target%"
    goto usage
)

:compile
echo Compiling in %mode% mode for %target%
title Compiler

REM some windows functions are pedantic about \
set OUTDIR=!OUTDIR!\%mode%\%target%
set LIBDIR=!LIBDIR!\%target%
set OUT=%OUTDIR%\%APP%

if not exist %OUTDIR% mkdir %OUTDIR%
if not exist %BINDIR% mkdir %BINDIR%
if not exist %BINDIR%\%mode% mkdir %BINDIR%\%mode%
if not exist %BINDIR%\%mode%\%target% mkdir %BINDIR%\%mode%\%target%

set _LIBS=
for %%L in (%LIBS%) do (
    set _LIBS=!_LIBS! %LIBDIR%/%%L
)

if "%mode%"=="debug" goto debug
if "%mode%"=="release" goto release

:usage
echo compile: "make [debug/release] [x86/x64] [ /multi/incremental/multi incremental]"
echo clean: "make clean"
goto :eof

:clean
if not exist %BINDIR% goto :eof
pushd %BINDIR%
del /f /q /s *.* >NUL
popd
:cleanrd
RD /s /q %BINDIR%
if exist %BINDIR% goto cleanrd
goto :eof

:release
set COMPOPT=!COMPOPT! %RELCOMPOPT%
set LINKOPT=!LINKOPT! %RELLINKOPT%
goto run

:debug
set COMPOPT=!COMPOPT! %DBGCOMPOPT%
set LINKOPT=!LINKOPT! %DBGLINKOPT%
goto run

:run
set INCREMENTAL=0
set MULTI=0
if "%3"=="incremental" set INCREMENTAL=1
if "%4"=="incremental" set INCREMENTAL=1
if "%3"=="multi" set MULTI=1
if "%4"=="multi" set MULTI=1

set allobj=
for %%P in (%SOURCES%) do (
    set inp_src=
    set inc=
    set bin_dir=%BINDIR%\%mode%\%target%\%%P
    if not exist !bin_dir! mkdir !bin_dir!
    for %%O in (!%%P_OBJ!) do (
        if "%INCREMENTAL%"=="1" (
            for /f "delims=" %%A in ('cscript /nologo /e:jscript "%~f0" !bin_dir!\%%~nO.obj !%%P_SRC!\%%O') do (
                if %%A LSS 0 set inp_src=!inp_src! !%%P_SRC!\%%O
            )
        ) else set inp_src=!inp_src! !%%P_SRC!\%%O
        set allobj=!allobj! !bin_dir!\%%~nO.obj
    )
    for %%I in (!%%P_INC!) do (
        set inc=!inc! /I%%I
    )
    if not "!inp_src!"=="" (
        if "%MULTI%"=="1" (
            call cl -std:%CPPVER% %COMPOPT% /MP /Fo:!bin_dir!\ /c !inp_src! !inc!
        ) else (
            call cl -std:%CPPVER% %COMPOPT% /Fo:!bin_dir!\ /c !inp_src! !inc!
        )
    )
)

call link %LINKOPT% /out:%OUT% %allobj% %_LIBS%
if not "%LIBDIR%"=="\%target%" for /f %%F in ('dir /b %LIBDIR%') do (
    if "%%~xF"==".dll" echo f | xcopy /y %LIBDIR%\%%F %OUTDIR%\%%F
)
goto :eof
*/
var fs = new ActiveXObject("Scripting.FileSystemObject");
var date1 = 0;
if(fs.FileExists(WSH.Arguments(0))){
    date1=Date.parse(fs.GetFile(WSH.Arguments(0)).DateLastModified);
}
var date2 = 0;
if(fs.FileExists(WSH.Arguments(1))){
    date2 = Date.parse(fs.GetFile(WSH.Arguments(1)).DateLastModified);
}
WSH.Echo(date1 - date2);