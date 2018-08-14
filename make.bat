@if (@a==@b) @end /*
@echo off
SetLocal EnableDelayedExpansion

set mode=%1
set target=%2

if not "%mode%"=="debug" if not "%mode%"=="release" if not "%mode%"=="clean" (
    echo unknown mode "%mode%"
    goto usage
)

call makelist.bat %target%

if "%mode%"=="clean" goto clean

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

set _LIBS=
for %%L in (%LIBS%) do (
    set _LIBS=!_LIBS! %LIBDIR%/%%L
)

if "%mode%"=="debug" goto debug
if "%mode%"=="release" goto release

:usage
echo compile: "make [debug/release] [x86/x64]"
echo clean: "make clean"
goto :eof

:clean
for /f %%F in ('dir /b %BINDIR%') do (
    if "%%~xF"==".obj" del %BINDIR%\%%F
)
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
set allobj=
for %%P in (%SOURCES%) do (
    for %%O in (!%%P_OBJ!) do (
        set out_obj=%BINDIR%/%%O%mode%%target%.obj
        set inp_src=!%%P_SRC!/%%O
        set allobj=!allobj! !out_obj!

        set diff="0"
        for /f "delims=" %%A in ('cscript /nologo /e:jscript "%~f0" !out_obj! !inp_src!') do (
            set diff=%%A
        )

        if !diff! LSS 0 (
            set inc=
            for %%I in (!%%P_INC!) do (set inc=!inc! /I%%I)
            call cl -std:%CPPVER% %COMPOPT% /Fo:!out_obj! /c !inp_src! !inc!
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