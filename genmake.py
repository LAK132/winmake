from sys import platform
import os, sys

is_windows = platform == 'win32'

if is_windows and not os.path.isfile('make.bat'):
    with open('make.bat', 'w+') as fyle:
        fyle.write(
'@if (@a==@b) @end /*\n\
@echo off\n\
SetLocal EnableDelayedExpansion\n\n\
set mode=%1\n\
set target=%2\n\n\
if not "%mode%"=="debug" if not "%mode%"=="release" if not "%mode%"=="clean" (\n\
    echo unknown mode "%mode%"\n\
    goto usage\n\
)\n\n\
call makelist.bat %target%\n\n\
if "%mode%"=="clean" goto clean\n\n\
if not "%target%"=="x86" if not "%target%"=="x64" (\n\
    echo unknown target "%target%"\n\
    goto usage\n\
)\n\n\
:compile\n\
echo Compiling in %mode% mode for %target%\n\
title Compiler\n\n\
REM some windows functions are pedantic about \\\n\
set OUTDIR=!OUTDIR!\\%mode%\\%target%\n\
set LIBDIR=!LIBDIR!\\%target%\n\
set OUT=%OUTDIR%\\%APP%\n\n\
if not exist %OUTDIR% mkdir %OUTDIR%\n\n\
set _LIBS=\n\
for %%L in (%LIBS%) do (\n\
    set _LIBS=!_LIBS! %LIBDIR%/%%L\n\
)\n\n\
if "%mode%"=="debug" goto debug\n\
if "%mode%"=="release" goto release\n\n\
:usage\n\
echo compile: "make [debug/release] [x86/x64]"\n\
echo clean: "make clean"\n\
goto :eof\n\n\
:clean\n\
for /f %%F in (\'dir /b %BINDIR%\') do (\n\
    if "%%~xF"==".obj" del %BINDIR%\\%%F\n\
)\n\
goto :eof\n\n\
:release\n\
set COMPOPT=!COMPOPT! %RELCOMPOPT%\n\
set LINKOPT=!LINKOPT! %RELLINKOPT%\n\
goto run\n\n\
:debug\n\
set COMPOPT=!COMPOPT! %DBGCOMPOPT%\n\
set LINKOPT=!LINKOPT! %DBGLINKOPT%\n\
goto run\n\n\
:run\n\
set allobj=\n\
for %%P in (%SOURCES%) do (\n\
    for %%O in (!%%P_OBJ!) do (\n\
        set out_obj=%BINDIR%/%%O%mode%%target%.obj\n\
        set inp_src=!%%P_SRC!/%%O\n\
        set allobj=!allobj! !out_obj!\n\n\
        set diff="0"\n\
        for /f "delims=" %%A in (\'cscript /nologo /e:jscript "%~f0" !out_obj! !inp_src!\') do (\n\
            set diff=%%A\n\
        )\n\n\
        if !diff! LSS 0 (\n\
            set inc=\n\
            for %%I in (!%%P_INC!) do (set inc=!inc! /I%%I)\n\
            call cl -std:%CPPVER% %COMPOPT% /Fo:!out_obj! /c !inp_src! !inc!\n\
        )\n\
    )\n\
)\n\n\
call link %LINKOPT% /out:%OUT% %allobj% %_LIBS%\n\
if not "%LIBDIR%"=="\\%target%" for /f %%F in (\'dir /b %LIBDIR%\') do (\n\
    if "%%~xF"==".dll" echo f | xcopy /y %LIBDIR%\\%%F %OUTDIR%\\%%F\n\
)\n\
goto :eof\n\n\
*/ var fs=new ActiveXObject("Scripting.FileSystemObject");var date1=0;if(fs.FileExists(WSH.Arguments(0))){date1=Date.parse(fs.GetFile(WSH.Arguments(0)).DateLastModified);}var date2=0;if(fs.FileExists(WSH.Arguments(1))){date2=Date.parse(fs.GetFile(WSH.Arguments(1)).DateLastModified);}WSH.Echo(date1-date2);')

def SetVar(key, value=None):
    if is_windows:
        return 'set '+key+'='+('' if value == None else value+'\n')
    else:
        return key+' = '+('' if value == None else value+'\n')

makeNewFile = False
while True:
    res = raw_input('Create new make{}? (Will overwrite existing file) [y/n]: '.format('.bat' if is_windows else 'file'))
    if res.startswith('y') or res.startswith('Y'):
        makeNewFile = True
        break
    elif res.startswith('n') or res.startswith('N'):
        makeNewFile = False
        break
    else:
        print 'Unknown response "'+res+'"'

if makeNewFile:
    app_name = raw_input('Output name (ie app{} or lib{}): '.format(
        '.exe' if is_windows else '', 
        '.dll' if is_windows else '.so'
    )) or ('app.exe' if is_windows else 'app')

    out_dir = raw_input('Output directory: ') or 'out'
    bin_dir = raw_input('Binaries directory: ') or 'bin'

    lib_dir = raw_input('Library director{} (optional): '.format('y' if is_windows else 'ies'))
    libs = raw_input('Libraries (optional): ')

    compiler = ''
    if is_windows:
        compiler = raw_input('Path to vcvarsall.bat (optional if in PATH): ') or 'vcvarsall.bat'
    else:
        compiler = raw_input('Compiler (ie g++): ') or 'g++'
    cpp_ver = raw_input('C++ version (ie c++11{}): '.format(' or c++latest' if is_windows else '')) or ('c++latest' if is_windows else 'c++11')

    comp_opt = raw_input('Compiler options (optional): ')
    link_opt = raw_input('Linker options (optional): ')

    dbg_comp_opt = raw_input('Debug mode compiler options (optional): ')
    dbg_link_opt = raw_input('Debug mode linker options (optional): ')

    rel_comp_opt = raw_input('Release mode compiler options (optional): ')
    rel_link_opt = raw_input('Release mode linker options (optional): ')

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
                    res = raw_input('Include source "'+target+'"? [y/n]: ')
                    if res.startswith('y') or res.startswith('Y'):
                        includeTarg = True
                        break
                    elif res.startswith('n') or res.startswith('N'):
                        break
                    else:
                        print 'Unknown response "'+res+'"'
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
            fyle.write(SetVar(targname+'_INC', raw_input('Source "'+target+'" include directories (optional): ')+'\n'))
        if is_windows:
            fyle.write('if not "%1"=="x64" if not "%1"=="x86" goto :eof\n\ncall "'+compiler+'" %1')
        else:
            fyle.write(
'# -------------------\n\
# Start build script:\n\
# -------------------\n\
ALL_OBJ = $(foreach src,$(SOURCES),$(foreach obj,$($(src)_OBJ),$(BINDIR)/$(obj).o))\n\n\
.PHONY: debug\n\
debug: $(foreach obj,$(ALL_OBJ),debug-$(obj))\n\
    $(call LINK_TEMPLATE,$(DBGLINKOPT))\n\n\
release: $(foreach obj,$(ALL_OBJ),release-$(obj))\n\
    $(call LINK_TEMPLATE,$(RELLINKOPT))\n\n\
define LINK_TEMPLATE =\n\
$(CXX) -std=$(CPPVER) -o $(OUTDIR)/$(APP) $(ALL_OBJ) $(foreach libdir,$(LIBDIR),-L$(libdir)) $(foreach lib,$(LIBS),-l$(lib)) $(COMPOPT) $(1)\n\
endef\n\n\
define COMPILE_TEMPLATE =\n\
debug-$(2)/$(3).o: $(1)/$(3)\n\
    $(CXX) -std=$(CPPVER) -c -o $(2)/$(3).o $(1)/$(3) $(4) $(DBGCOMPOPT)\n\
release-$(2)/$(3).o: $(1)/$(3)\n\
    $(CXX) -std=$(CPPVER) -c -o $(2)/$(3).o $(1)/$(3) $(4) $(RELCOMPOPT)\n\
endef\n\n\
$(foreach src,$(SOURCES),$(foreach obj,$($(src)_OBJ),$(eval $(call COMPILE_TEMPLATE,$($(src)_SRC),$(BINDIR),$(obj),$(foreach inc,$($(src)_INC),-I$(inc))))))\n\n\
clean:\n\
    rm -f $(ALL_OBJ)')
        fyle.truncate()