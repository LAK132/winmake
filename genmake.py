from sys import platform
import os, sys

is_windows = platform == 'win32'

inp = input
if not sys.version_info >= (3, 0):
    inp = raw_input

if is_windows and not os.path.isfile('make.bat'):
    with open('make.bat', 'w+') as fyle:
        fyle.write(r"""@if (@a==@b) @end /*
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
WSH.Echo(date1 - date2);""")

def SetVar(key, value=None):
    if is_windows:
        return 'set '+key+'='+('' if value == None else value+'\n')
    else:
        return key+' = '+('' if value == None else value+'\n')

makeNewFile = False
while True:
    res = inp('Create new make{}? (Will overwrite existing file) [y/n]: '.format('list.bat' if is_windows else 'file'))
    if res.startswith('y') or res.startswith('Y'):
        makeNewFile = True
        break
    elif res.startswith('n') or res.startswith('N'):
        makeNewFile = False
        break
    else:
        print('Unknown response "'+res+'"')

if makeNewFile:
    app_name = inp('Output name (ie app{} or lib{}): '.format(
        '.exe' if is_windows else '', 
        '.dll' if is_windows else '.so'
    )) or ('app.exe' if is_windows else 'app')

    out_dir = inp('Output directory: ') or 'out'
    bin_dir = inp('Binaries directory: ') or 'bin'

    lib_dir = inp('Library director{} (optional): '.format('y' if is_windows else 'ies'))
    libs = inp('Libraries (optional): ')

    compiler = ''
    if is_windows:
        compiler = inp('Path to vcvarsall.bat (optional if in PATH): ') or 'vcvarsall.bat'
    else:
        compiler = inp('Compiler (ie g++): ') or 'g++'
    cpp_ver = inp('C++ version (ie c++11{}): '.format(' or c++latest' if is_windows else '')) or ('c++latest' if is_windows else 'c++11')

    comp_opt = inp('Compiler options (optional): ')
    link_opt = inp('Linker options (optional): ')

    dbg_comp_opt = inp('Debug mode compiler options (optional): ')
    dbg_link_opt = inp('Debug mode linker options (optional): ')

    rel_comp_opt = inp('Release mode compiler options (optional): ')
    rel_link_opt = inp('Release mode linker options (optional): ')

    with open('makelist.bat' if is_windows else 'makefile', 'w+') as fyle:
        fyle.seek(0)
        if not is_windows:
            fyle.write(SetVar('CXX', compiler)+'\n')
        fyle.write(SetVar('CPPVER', cpp_ver)+'\n')
        fyle.write(SetVar('APP', app_name)+'\n')
        fyle.write(SetVar('OUTDIR', out_dir))
        fyle.write(SetVar('BINDIR', bin_dir)+'\n')
        fyle.write(SetVar('LIBDIR', lib_dir))
        fyle.write(SetVar('LIBS', libs)+'\n')
        fyle.write(SetVar('COMPOPT', comp_opt))
        fyle.write(SetVar('LINKOPT', link_opt)+'\n')
        fyle.write(SetVar('DBGCOMPOPT', dbg_comp_opt))
        fyle.write(SetVar('DBGLINKOPT', dbg_link_opt)+'\n')
        fyle.write(SetVar('RELCOMPOPT', rel_comp_opt))
        fyle.write(SetVar('RELLINKOPT', rel_link_opt)+'\n')
        fyle.write(SetVar('SOURCES'))
        dirs = list()
        targets = list()
        dirs.append(os.path.curdir)
        while True:
            dirName = dirs.pop()
            dirList = [os.path.join(dirName, f) for f in os.listdir(dirName)]
            subdirList = [d for d in dirList if os.path.isdir(d)]
            fileList = [f for f in os.listdir(dirName) if os.path.isfile(os.path.join(dirName, f)) and (f.endswith('.cpp') or f.endswith('.cxx') or f.endswith('.c'))]
            for subdir in subdirList:
                dirs.append(subdir)
            if len(fileList) > 0:
                includeTarg = False
                target = dirName[2:] if dirName.startswith('.\\') and len(dirName) > 2 else dirName
                while True:
                    res = inp('Include source "'+target+'"? [y/n]: ')
                    if res.startswith('y') or res.startswith('Y'):
                        includeTarg = True
                        break
                    elif res.startswith('n') or res.startswith('N'):
                        break
                    else:
                        print('Unknown response "'+res+'"')
                if includeTarg:
                    targets.append(target)
            if len(dirs) == 0:
                break
        for target in targets:
            fyle.write(target.replace('\\', '_').replace('/', '_').replace('.', '_')+' ')
        fyle.write('\n\n')
        for target in targets:
            targname = target.replace('\\', '_').replace('/', '_').replace('.', '_')
            fyle.write(SetVar(targname+'_SRC', target))
            fyle.write(SetVar(targname+'_OBJ'))
            for f in [f for f in os.listdir(target) if f.endswith('.cpp') or f.endswith('.cxx') or f.endswith('.c')]:
                fyle.write(f+' ')
            fyle.write('\n')
            fyle.write(SetVar(targname+'_INC', inp('Source "'+target+'" include directories (optional): ')+'\n'))
        if is_windows:
            fyle.write('if not "%1"=="x64" if not "%1"=="x86" goto :eof\n\ncall "'+compiler+'" %1')
        else:
            fyle.write(r"""# -------------------
# Start build script:
# -------------------
ALL_OBJ = $(foreach src,$(SOURCES),$(foreach obj,$($(src)_OBJ),$(BINDIR)/$(src)$(obj).o))
.PHONY: debug
debug: $(foreach obj,$(ALL_OBJ),debug-$(obj))
	$(call LINK_TEMPLATE,$(LINKOPT) $(DBGLINKOPT),debug)
release: $(foreach obj,$(ALL_OBJ),release-$(obj))
	$(call LINK_TEMPLATE,$(LINKOPT) $(RELLINKOPT),release)
define LINK_TEMPLATE =
$(CXX) -std=$(CPPVER) -o $(OUTDIR)/$(2)/$(APP) $(ALL_OBJ) $(foreach libdir,$(LIBDIR),-L$(libdir)) $(foreach lib,$(LIBS),-l$(lib)) $(COMPOPT) $(1)
endef
define COMPILE_TEMPLATE =
debug-$(2)$(3).o: $(1)/$(3)
	$(CXX) -std=$(CPPVER) -c -o $(2)$(3).o $(1)/$(3) $(4) $(COMPOPT) $(DBGCOMPOPT)
release-$(2)$(3).o: $(1)/$(3)
	$(CXX) -std=$(CPPVER) -c -o $(2)$(3).o $(1)/$(3) $(4) $(COMPOPT) $(RELCOMPOPT)
endef
$(foreach src,$(SOURCES),$(foreach obj,$($(src)_OBJ),$(eval $(call COMPILE_TEMPLATE,$($(src)_SRC),$(BINDIR)/$(src),$(obj),$(foreach inc,$($(src)_INC),-I$(inc))))))
clean:
	rm -f $(ALL_OBJ)""")
        fyle.truncate()