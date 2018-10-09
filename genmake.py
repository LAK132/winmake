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
if "%1"=="clean" (
    for /f "delims=" %%A in ('cscript /nologo /e:jscript "%~f0" %1') do (
        set BINDIR=%%A
    )
    if not exist !BINDIR! goto :eof
    pushd !BINDIR!
    del /f /q /s *.obj >NUL
    popd
    goto :eof
)
for /f "delims=" %%A in ('cscript /nologo /e:jscript "%~f0" %*') do (
    call %%A
)
if not "%LIBDIR%"=="\%target%" for /f %%F in ('dir /b %LIBDIR%') do (
    if "%%~xF"==".dll" echo f | xcopy /y %LIBDIR%\%%F %OUTDIR%\%%F
)
goto :eof
*/
String.prototype.trim = function() { return this.replace(/^\s+|\s+$/g, ""); };
String.prototype.toArgs = function() { return this.split(/\s+/g) || []; };
var fs = new ActiveXObject("Scripting.FileSystemObject");
var fileCompare = function(file1, file2) {
    var date1 = 0;
    if (fs.FileExists(file1)) {
        date1 = Date.parse(fs.GetFile(file1).DateLastModified);
    }
    if (fs.FileExists(file2)) {
        return date1 - Date.parse(fs.GetFile(file2).DateLastModified);
    }
    return -1;
};
var f = fs.GetFile("Makefile");
var ts = f.OpenAsTextStream(1, 0);
var regex = /\s*=\s*/gi
var make = {};
var line = ts.ReadLine();
while (line.indexOf("# BUILD SCRIPT") == -1) {
    var longline = line.indexOf("\\");
    while(longline != -1) {
        line = line.substring(0,longline).trim()+" "+(ts.ReadLine().trim());
        longline = line.indexOf("\\");
    }
    line = line.replace(regex, "=");
    var bat = line.indexOf("#bat");
    var comment = line.indexOf("#");
    if (bat != -1)  line = line.substring(bat+4);
    else if (comment != -1) line = line.substring(0, comment);
    var eq = line.indexOf("=");
    if (eq != -1) {
        make[line.substring(0, eq).trim()] = line.substring(eq+1).trim();
    }
    line = ts.ReadLine();
}
var mode = WSH.Arguments(0);
if (mode == "clean") {
    WSH.Echo(make["BINDIR"]);
} else if ((mode == "debug" || mode == "release") && (WSH.Arguments(1) == "x86" || WSH.Arguments(1) == "x64")) {
    var target = WSH.Arguments(1);
    if (mode == "debug") {
        make["COMPOPT"] = make["COMPOPT"]+" "+make["DBGCOMPOPT"];
        make["LINKOPT"] = make["LINKOPT"]+" "+make["DBGLINKOPT"];
    } else {
        make["COMPOPT"] = make["COMPOPT"]+" "+make["RELCOMPOPT"];
        make["LINKOPT"] = make["LINKOPT"]+" "+make["RELLINKOPT"];
    }
    var multi = false;
    var incremental = false;
    if (WSH.Arguments.Length > 2) {
        multi = multi || (WSH.Arguments(2) == "multi");
        incremental = incremental || (WSH.Arguments(2) == "incremental");
    }
    if (WSH.Arguments.Length > 3) {
        multi = multi || (WSH.Arguments(3) == "multi");
        incremental = incremental || (WSH.Arguments(3) == "incremental");
    }
    make["OUTDIR"] = make["OUTDIR"]+"\\"+mode+"\\"+target;
    make["LIBDIR"] = make["LIBDIR"]+"\\"+target;
    make["OUT"] = make["OUTDIR"]+"\\"+make["APP"];
    make["LIBS"] = make["LIBS"].toArgs();
    make["_LIBS"] = "";
    for (var lib in make["LIBS"]) {
        if (make["LIBS"][lib]) {
            make["LIBS"][lib] = make["LIBDIR"]+"\\"+make["LIBS"][lib];
            make["_LIBS"] = make["_LIBS"]+" "+make["LIBS"][lib];
        }
    }
    make["SOURCES"] = make["SOURCES"].toArgs();
    var sources = {};
    for (var _src in make["SOURCES"]) {
        var src = make["SOURCES"][_src];
        sources[src] = {
            "SRC": make[src+"_SRC"] || ".",
            "OBJ": (make[src+"_OBJ"] || "").toArgs(),
            "HDR": (make[src+"_HDR"] || "").toArgs(),
            "DEP": (make[src+"_DEP"] || "").toArgs(),
            "INC": (make[src+"_INC"] || "").toArgs()
        };
    }
    for (var _src in sources) {
        var src = sources[_src];
        src["DEPS"] = [];
        // Add source files to deps
        for (var _obj in src["OBJ"]) {
            var obj = src["OBJ"][_obj];
            if (obj) src["DEPS"].push(src["SRC"]+"\\"+obj);
        }
        // Add headers to deps
        for (var _hdr in src["HDR"]) {
            var hdr = src["HDR"][_hdr];
            if (hdr) src["DEPS"].push(src["SRC"]+"\\"+hdr);
        }
        for (var _dep in src["DEP"]) {
            var dep = sources[src["DEP"][_dep]];
            if (dep) {
                // Add dep objs to deps
                for (var _depobj in dep["OBJ"]) {
                    var depobj = dep["OBJ"][_depobj];
                    if (depobj) src["DEPS"].push(dep["SRC"]+"\\"+depobj);
                }
                // Add dep headers to deps
                for (var _dephdr in dep["HDR"]) {
                    var dephdr = dep["HDR"][_dephdr];
                    if (dephdr) src["DEPS"].push(dep["SRC"]+"\\"+dephdr);
                }
            }
        }
    }
    var all_obj = "";
    WSH.Echo(make["CXX"]+" "+target);
    var compile = "call cl -std:"+make["CPPVER"]+" "+make["COMPOPT"]+" /c";
    for (var _src in sources) {
        var src = sources[_src];
        var inp_src = "";
        var inc = "";
        var bin_dir = make["BINDIR"]+"\\"+mode+"\\"+target+"\\"+_src;
        WSH.Echo("cmd /c if not exist "+bin_dir+" mkdir "+bin_dir);
        for (var _obj in src["OBJ"]) {
            var obj = src["OBJ"][_obj];
            if (obj) {
                var objOut = bin_dir+"\\"+obj.substring(0, obj.lastIndexOf("."))+".obj";
                var add_src = !incremental;
                if (incremental) {
                    for (var _dep in src["DEPS"]) {
                        var dep = src["DEPS"][_dep];
                        if (fileCompare(objOut, dep) < 0) add_src = true;
                        if (add_src) break;
                    }
                }
                if (add_src) inp_src = inp_src+" "+src["SRC"]+"\\"+obj;
                all_obj = all_obj+" "+objOut;
            }
        }
        for (var _inc in src["INC"]) {
            inc = inc+" /I"+src["INC"][_inc];
        }
        for (var _dep in src["DEP"]) {
            if (sources[src["DEP"][_dep]]) inc = inc+" /I"+sources[src["DEP"][_dep]]["SRC"];
        }
        if (inp_src != "") {
            if (multi) {
                WSH.Echo(compile+" /MP "+inp_src+" "+inc+" /Fo:"+bin_dir+"\\");
            } else {
                WSH.Echo(compile+" "+inp_src+" "+inc+" /Fo:"+bin_dir+"\\");
            }
        }
    }
    WSH.Echo("cmd /c if not exist "+make["OUTDIR"]+" mkdir "+make["OUTDIR"]);
    WSH.Echo("link "+make["LINKOPT"]+" /out:"+make["OUT"]+" "+all_obj+" "+make["_LIBS"]);
    WSH.Echo("set LIBDIR="+make["LIBDIR"]);
    WSH.Echo("set OUTDIR="+make["OUTDIR"]);
    WSH.Echo("set target="+target);
} else {
    WSH.Echo("cmd /c echo compile: \"make [debug/release] [x86/x64] [ /multi/incremental/multi incremental]\"");
    WSH.Echo("cmd /c echo clean: \"make clean\"");
}""")

def SetVar(key, value=None):
    return key+' = '+('' if value == None else value+'\n')
def SetVarMulti(key, value=None):
    if is_windows:
        return key+' = \t\t#bat '+key+' = '+value+'\n'
    else:
        return key+' = '+value+'\t\t#bat '+key+' = \n'

makeNewFile = False
while True:
    res = inp('Create new Makefile? (Will overwrite existing file) [y/n]: ')
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

    lib_dir = inp('Library directory (optional): ')
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

    with open('Makefile', 'w+') as fyle:
        fyle.seek(0)
        fyle.write(SetVarMulti('CXX', compiler)+'\n')
        fyle.write(SetVar('CPPVER', cpp_ver)+'\n')
        fyle.write(SetVarMulti('APP', app_name)+'\n')
        fyle.write(SetVar('OUTDIR', out_dir))
        fyle.write(SetVar('BINDIR', bin_dir)+'\n')
        fyle.write(SetVar('LIBDIR', lib_dir))
        fyle.write(SetVarMulti('LIBS', libs)+'\n')
        fyle.write(SetVarMulti('COMPOPT', comp_opt))
        fyle.write(SetVarMulti('LINKOPT', link_opt)+'\n')
        fyle.write(SetVarMulti('DBGCOMPOPT', dbg_comp_opt))
        fyle.write(SetVarMulti('DBGLINKOPT', dbg_link_opt)+'\n')
        fyle.write(SetVarMulti('RELCOMPOPT', rel_comp_opt))
        fyle.write(SetVarMulti('RELLINKOPT', rel_link_opt)+'\n')
        fyle.write(SetVar('SOURCES'))
        dirs = list()
        targets = list()
        dirs.append(os.path.curdir)
        while True:
            dirName = dirs.pop()
            dirList = [os.path.join(dirName, f) for f in os.listdir(dirName)]
            subdirList = [d for d in dirList if os.path.isdir(d)]
            fileList = [f for f in os.listdir(dirName) if os.path.isfile(os.path.join(dirName, f)) and (f.endswith('.cpp') or f.endswith('.cxx') or f.endswith('.c') or f.endswith('.hpp') or f.endswith('.hxx') or f.endswith('.h'))]
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
            fyle.write(SetVar(targname+'_HDR'))
            for f in [f for f in os.listdir(target) if f.endswith('.hpp') or f.endswith('.hxx') or f.endswith('.h')]:
                fyle.write(f+' ')
            fyle.write('\n')
            fyle.write(SetVar(targname+'_DEP', inp('Source "'+target+'" dependency sources: ')))
            fyle.write(SetVarMulti(targname+'_INC', inp('Source "'+target+'" include directories (optional): ')+'\n'))
        fyle.write(r"""# BUILD SCRIPT
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
$(foreach src,$(SOURCES),$(eval $(call COMPILE_TEMPLATE,$(src),$($(src)_SRC),$(foreach header,$($(src)_HDR),$($(src)_SRC)/$(header)) $(foreach dep,$($(src)_DEP),$(foreach depobj,$($(dep)_OBJ),$($(dep)_SRC)/$(depobj)) $(foreach dephdr,$($(dep)_HDR),$($(dep)_SRC)/$(dephdr))),$(foreach inc,$($(src)_INC),-I$(inc)) $(foreach dep,$($(src)_DEP),-I$($(dep)_SRC)))))""")
        fyle.truncate()