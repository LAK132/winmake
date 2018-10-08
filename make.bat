@if (@a==@b) @end /*
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
}