#!/bin/env python3
# encoding: utf-8
import os, re, vim, sys, copy
import codecs

# Resolve vlogAuto python lib path from this file's location (allow override via env)
_LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
vpath = os.environ.get("VLOGAUTO_PATH", _LOCAL_DIR)
if vpath not in sys.path:
    sys.path.insert(0, vpath)

# Also keep the shared CAD path as a fallback so shared modules can still be found
_SHARED = "/app/common/cad/scripts/vlogAuto"
if os.path.isdir(_SHARED) and _SHARED not in sys.path:
    sys.path.append(_SHARED)

from vlogProcLib import *

re_vim_inst_arg = re.compile(r"^\s*(?P<mname>\w+)(\+(?P<pfix>\w+)){0,1}(\+(?P<num>\w+)){0,1}(\+(?P<sfix>\w+)){0,1}\s*$", re.I)



# Function 'proc_auto_empty_module' # {{{
def proc_auto_empty_module(lines, curFile, fName=None):
    modObj = ModuleInfo(curFile, lines)
    # get port info.
    modObj.initial_port()

    modObj.gen_empty_module(fName, style='full') # or stype=simple

# Function 'proc_auto_empty_module' # }}}

# Function 'proc_auto_port_format' # {{{
def proc_auto_port_format(lines, curFile):
    obj = ModuleInfo(curFile, lines)
    obj.reformat_ports(lines)
# Function 'proc_auto_port_format' # }}}

# Function 'proc_auto_port_define' # {{{
def proc_auto_port_define(lines, curFile, curLine, curBuff):
    i = 0
    bufLines = curBuff.split("\n")
    for line in bufLines:
        if re_comment.search(line):
            continue
        obj = re_port_connect.search(line)
        if obj:
            port  = obj.group('wire')
            width = "%-24s"%(obj.group('width') if obj.group('width') else '')
            io    = obj.group('io').upper()
            inout = 'output ' if io == 'O' else 'input  ' if io == 'I' else 'inout  '
            lines.append("%s%s%s;"%(inout, width, port), curLine+i)
            i    += 1
# Function 'proc_auto_port_define' # }}}

# Function 'proc_auto_arg' # {{{
def proc_auto_arg(lines, curFile):
    modObj = ModuleInfo(curFile, lines)
    modObj.initial_port()
    modObj.update_args()
# Function 'proc_auto_arg' # }}}

# Function 'proc_auto_define' # {{{
def proc_auto_define(lines, curFile):
    modObj = ModuleInfo(curFile, lines)

    # get path info.
    # modObj.initial_path()
    # get port info.
    modObj.initial_port()
    if modObj.mLocate['adef'] == -1:
        print("No '/*autodefine*/' found!")
        return False
    # get module instance info.
    #modObj.initial_instance(detail=True)
    modObj.initial_instance()
    # get wire info.
    modObj.initial_wire()

    #modObj.print_location()

    modObj.update_defines(v2001=True)

    return True
# Function 'proc_auto_define' # }}}

# Function 'iproc_match_name' # {{{
def iproc_match_name(name, listNames):
    """
    True : 'name' in 'listNames' or 'listNames' == [all]
    False: Others
    """

    return name in listNames or 'all' in listNames
# Function 'iproc_match_name' # }}}

# Function 'iproc_parsing_instance_args' # {{{
def iproc_parsing_instance_args(args, fpLog):
    """
    moduleName[+prefix][+num][+sufix] => moduleName, prefix, num, sufix
    """

    num = 0
    mname = prefix = sufix = ''
    obj = re_vim_inst_arg.search(args)
    if obj:
        mname, prefix, num, suffix = (obj.group('mname'), obj.group('pfix'), obj.group('num'), obj.group('sfix'))
        suffix = "" if suffix is None else "_%s"%suffix
        if num is None:
            num = 0
        elif num.isdigit() is False:
            suffix = "_%s"%num
            num = 0
        else:
            num = int(num)
        if prefix is None:
            prefix = ''
        elif prefix.isdigit():
            num    = int(prefix)
            prefix = ''
        elif num == 0 and suffix == '':
            suffix = "_%s"%prefix
            prefix = ''
        else:
            prefix = "%s_"%prefix
    else: #obj is None
        xprint(fpLog, "Invalid argument [%s], <Ignored>!"%(args))

    if mname != '' and num == 0:
        num = 1

    return mname, prefix, num, suffix
# Function 'iproc_parsing_instance_args' # }}}

# Function 'proc_auto_instance' # {{{
def proc_auto_instance(lines, curFile, listXnames, instMode=0):
    """
    instMode = 0:     For 'AII',  'listXnames' should be list of instance name
    instMode = 2:     For 'AIIA', 'listXnames' should be list of instance name, will add port definition automatically
    instMode = 3:     For 'INST', 'listXnames' should be list of moduleName[+prefix][+number][+suffix]
                      Example: INST spi+xxx+3+yyy will be instanced 3 spi:
                        spi u_xxx_spi_yyy_0 (/*AUTOINST*/
                              ... ...
                            );
                        spi u_xxx_spi_yyy_1 (/*AUTOINST*/
                              ... ...
                            );
                        spi u_xxx_spi_yyy_2 (/*AUTOINST*/
                              ... ...
                            );
    instMode = 4:     For 'AIIU', 'listXnames' should be list of instance name, will add updated instance connection wires to port definition automaticlly
    instMode = 9:     For 'AIIdbg',  'listXnames' should be list of instance name, debug mode
    instMode = others:For 'AIM',  'listXnames' should be list of module name
    """

    cfg    = True
    detail = True
    debug  = False
    silent = 1
    if instMode == 9:
        debug    = True
        silent   = 0
        instMode = 0

    fpLog = None
    if silent == 0:
        try:
            #fpLog = open("AI.log", 'w')
            fpLog = codecs.open("AI.log", 'w', encoding='gbk', errors='ignore')
        except IOError as e:
            print("Error: cannot open file to write: AI.log (%s)"%e)

    modObj = ModuleInfo(curFile, lines)
    modObj.initial_path(debug, fpLog)
    modObj.initial_port(cfg, silent, fpLog)
    modObj.initial_instance(detail, cfg, silent, fpLog)

    if instMode == 3:
        addiDict = lDict()
        for arg in listXnames:
            mname, prefix, num, suffix = iproc_parsing_instance_args(arg, fpLog)
            iname = "u_%s%s%s"%(prefix, mname, suffix)
            if num == 1 and iname not in modObj.mInst and iname not in addiDict:
                addiDict[iname] = mname
            else:
                #idx = 0
                #while num > 0:
                for idx in range(num):
                    inamex = "%s_%d"%(iname, idx)
                    #if inamex not in modObj.mInst and iname not in addiDict: ???
                    if inamex not in modObj.mInst and inamex not in addiDict:
                        addiDict[inamex] = mname
        instMode = 0 # Change 'instMode' to instance list mode '0'
        listXnames = addiDict.lkeys
        modObj.add_instance(addiDict, silent=silent, fpLog=fpLog)

    for iname in modObj.mInst.lkeys:
        mname = modObj.mInst[iname]['module']
        cname = iname if instMode in [0, 2, 4] else mname
        if modObj.mInst[iname]['auto'] is False or iproc_match_name(cname, listXnames) is False:
            continue
        modObj.update_instance(iname, cfg=cfg, silent=silent, fpLog=fpLog)

    modObj.update_instance_wires(silent, fpLog)
    if (cfg or instMode in [2, 4]) and modObj.mLocate['adef'] > 0:
        for iname in modObj.mInst.lkeys:
            mname = modObj.mInst[iname]['module']
            cname = iname if instMode in [0, 2, 4] else mname
            if modObj.mInst[iname]['auto'] is False or iproc_match_name(cname, listXnames) is False:
                continue
            modObj.update_instance_ports(iname, instMode, cfg=cfg, add=True, silent=silent, fpLog=fpLog)

    if fpLog:
        fpLog.close()

    return True
# Function 'proc_auto_instance' # }}}

# Function 'proc_auto_drc_check' # {{{
def proc_auto_drc_check(lines, curFile):
    fpLog = None
    logName = 'DRC.log'
    try:
        #fpLog = open(logName, 'w')
        fpLog = codecs.open(logName, 'w', encoding='gbk', errors='ignore')
    except IOError as e:
        print("Error: cannot open file to write: %s (%s)"%(logName, e))

    modObj = ModuleInfo(curFile, lines)
    # get search path info
    modObj.initial_path(fpLog)
    # get port info.
    modObj.initial_port(fpLog)
    # get module instance info
    modObj.initial_instance(detail=True, fpLog=fpLog)
    # get wire info.
    modObj.initial_wire(detail=True, fpLog=fpLog)

    for wname, wdict in modObj.mWires['iwire'].items():
        obj = re.search("^\w+$", wname)
        if obj is None or wname.isdigit() or wdict['inout'] is None:
            continue

        if wname in modObj.mPorts['dict']:  # ~~ port direction check: conflict or undriven
            if wdict['inout'] in ['output', 'inout'] and modObj.mPorts['dict'][wname]['inout'] == 'input':
                hasDup, bitDup = width_check(wdict, modObj.mPorts['dict'][wname])
                if hasDup:
                    xprint(fpLog, "Error: Direction of input '%s%s' port conflicted with module instance connection!"%(wname, bitDup))
            elif wdict['inout'] == 'input' and modObj.mPorts['dict'][wname]['inout'] == 'output' and \
                 wname not in modObj.mWires['regs'] and wname not in modObj.mWires['wires']:
                xprint(fpLog, "Warning: [%s] maybe UNDRIVEN signal!"%(wname))
        elif wdict['inout'] in ['output', 'inout'] and wname in modObj.mWires['wires']:
            hasDup, bitDup = width_check(wdict, modObj.mWires['wires'][wname])
            if hasDup:
                xprint(fpLog, "Error: MULTI-DRIVE signal: '%s%s' --> conflicted with direction of module instance connection"%(wname, bitDup))
        elif wdict['inout'] in ['output', 'inout'] and wname in modObj.mWires['regs']:
            hasDup, bitDup = width_check(wdict, modObj.mWires['regs'][wname])
            if hasDup:
                xprint(fpLog, "Error: MULTI-DRIVE signal: '%s%s' --> conflicted with direction of module instance connection"%(wname, bitDup))
        elif wdict['inout'] in ['output', 'inout'] and wname in modObj.mWires['defs'] and modObj.mWires['defs'][wname]['type'] in gRegType:
            xprint(fpLog, "Error: reg type signal: '%s' conflicted with direction of module instance connection"%(wname))

        if wdict['inout'] == 'input' and wname not in modObj.mWires['regs'] and wname not in modObj.mPorts['dict'] and wname not in modObj.mWires['wires']:
            xprint(fpLog, "Warning: [%s] maybe UNDRIVEN signal!"%(wname))

    # Check signals used before referenced
    for wname, wdict in modObj.mWires['wires'].items():
        if wname not in modObj.mWires['defs']:
            xprint(fpLog, 'Error: Signal [%s] used before referenced!'%(wname))
    for rname, rdict in modObj.mWires['regs'].items():
        if rname not in modObj.mWires['defs']:
            xprint(fpLog, 'Error: Signal [%s] used before referenced!'%(rname))

    xprint(fpLog, "Check done, please check %s for detail info."%(logName))

    if fpLog:
        fpLog.close()
# Function 'proc_auto_drc_check' # }}}