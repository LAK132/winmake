@echo off
SetLocal EnableDelayedExpansion

set mode=%1
set target=%2

if not "%mode%"=="debug" if not "%mode%"=="release" if not "%mode%"=="clean" (
    echo unknown mode "%mode%"
    goto usage
)
if not "%target%"=="x86" if not "%target%"=="x64" (
    echo unknown target "%target%"
    goto usage
)

call makelist.bat %target%

if "%mode%"=="clean" goto clean

:compile
echo Compiling in %mode% mode for %target%
title Compiler

REM some windows functions are pedantic about \
set OUTDIR=!OUTDIR!\%mode%\%target%
set LIBDIR=!LIBDIR!\%target%
set OUT=%OUTDIR%\%APP%

if not exist %OUTDIR% mkdir %OUTDIR%

set _LIBS=
for %%L in (%LIBS%) do (
    set _LIBS=!_LIBS! %LIBDIR%/%%L
)

if "%mode%"=="debug" goto debug
if "%mode%"=="release" goto release

:usage
echo compile exe: "make [debug/release] [x86/x64]"
echo compile dll: "make lib [debug/release] [x86/x64]"
echo clean: "make clean"
goto :eof

:clean
set target=%2
if not "%target%"=="x86" if not "%target%"=="x64" (
    echo unknown target "%target%"
    goto usage
)
call makelist.bat %target%

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
        set allobj=!allobj! %BINDIR%/%%O.obj
        set inc=
        for %%I in (!%%P_INC!) do (set inc=!inc! /I%%I)
        call cl -std:%CPPVER% %COMPOPT% /Fo:%BINDIR%/%%O.obj /c !%%P_SRC!/%%O !inc!
    )
)
call link %LINKOPT% /out:%OUT% %allobj% %_LIBS%
if not "%LIBDIR%"=="\%target%" for /f %%F in ('dir /b %LIBDIR%') do (
    if "%%~xF"==".dll" echo f | xcopy /y %LIBDIR%\%%F %OUTDIR%\%%F
)
goto :eof