#!/usr/bin/env python3

import os, sys

# Resolve vlogAuto python lib path from this file's location (allow override via env)
_LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
vpath = os.environ.get("VLOGAUTO_PATH", _LOCAL_DIR)
if vpath not in sys.path:
    sys.path.insert(0, vpath)

_SHARED = "/app/common/cad/scripts/vlogAuto"
if os.path.isdir(_SHARED) and _SHARED not in sys.path:
    sys.path.append(_SHARED)

from vlogProcLib import *

def get_bk_file_name(fName):

    return fName[:fName.rfind('.')]+'.bk'+fName[fName.rfind('.'):]

# Function 'iproc_match_name' # {{{
def iproc_match_name(name, listNames):
    """
    True : 'name' in 'listNames' or 'listNames' == [all] or 'listNames' == []
    False: Others
    """

    return len(listNames)==0 or name in listNames or 'all' in listNames
# Function 'iproc_match_name' # }}}

def vim_AR(fName):
    modObj = ModuleInfo(fName)
    modObj.set_lines()
    modObj.initial_port()
    modObj.update_args(appendMode='extend')

    os.remove(fName)
    modObj.save_module(fname=fName)
    #with open(fName, "w") as fp:
    #    for i in modObj.mLines:
    #        fp.write( i.rstrip()+'\n' )
    #    fp.close()

def vim_AD(fName):
    modObj = ModuleInfo(fName)
    modObj.set_lines()

    # get port info.
    modObj.initial_port()
    if modObj.mLocate['adef'] == -1:
        print("No '/*autodefine*/' found!")
        return False

    modObj.initial_instance()
    # get wire info.
    modObj.initial_wire()

    modObj.update_defines(appendMode="extend")

    os.remove(fName)
    modObj.save_module(fname=fName)
    #with open(fName, "w") as fp:
    #    for i in modObj.mLines:
    #        i = i.rstrip();
    #        fp.write( i+'\n' )
    #    fp.close()

def vim_AIX(fName, listMnames, module=True):
    modObj = ModuleInfo(fName)
    modObj.set_lines()
    modObj.initial_path()
    modObj.initial_port()
    modObj.initial_instance(detail=True)

    for iname in modObj.mInst.lkeys:
        mname = modObj.mInst[iname]['module']

        cname = mname if module else iname
        if modObj.mInst[iname]['auto'] is False or iproc_match_name(cname, listMnames) is False:
            continue
        modObj.update_instance(iname, appendMode='extend')

    modObj.update_instance_wires( 0 )

    os.remove(fName)
    modObj.save_module(fname=fName)
    #with open(fName, "w") as fp:
    #    for i in modObj.mLines:
    #        fp.write( i.rstrip()+'\n' )
    #    fp.close()

def vim_AIM(fName, listMnames=['all']):

    vim_AIX(fName, listMnames, module=True)

def vim_AII(fName, listMnames=['all']):

    vim_AIX(fName, listMnames, module=False)

def vim_APF(fName):
    modObj = ModuleInfo(fName)
    modObj.set_lines()

    modObj.reformat_ports()

    os.remove(fName)
    modObj.save_module(fname=fName)

def vim_EMPTY(fName, eName=None):
    """
        fName: source RTL file
        eName: file name of generated .empty.v, optional
        Notes: if 'eName' is not specified, the source RTL file 'fName' will be generated as .empty.v!!
    """
    modObj = ModuleInfo(fName)
    modObj.set_lines()

    status = modObj.initial_port()

    if status:
        status = modObj.initial_wire()

    if status:
        if eName:
            # style:
            #   'full'  : assign port_name[$msb:$lsb] = 'h0;
            #   'simple': assign port_name            = 'h0;
            status = modObj.gen_empty_module(eName, style='full')
        else:
            status = modObj.gen_empty_module(fName, style='full')
            if status:
                os.remove(fName)
                modObj.save_module(fname=fName)
    return status

if __name__ == '__main__':

    #********************************************************************************
    # gVim Cmd                 Python Function
    #  :AR                      vim_AR( "xxxx.v" )
    #  :AD                      vim_AD( "xxxx.v" )
    #  :AIM all                 vim_AIM("xxxx.v" )     or vim_AIM("xxxx.v", ['all'])
    #  :AIM $mod1 $mod2  ...    vim_AIM("xxxx.v", [$mod1, $mod2, ...] )
    #  :AII all                 vim_AII("xxxx.v" )     or vim_AII("xxxx.v", ['all'])
    #  :AII $ins1 $ins2  ...    vim_AII("xxxx.v", [$ins1, $ins2, ...] )


    if sys.argv[2] == 'AR':
        vim_AR(sys.argv[1])

    if sys.argv[2] == 'AD':
        vim_AD(sys.argv[1])

    if sys.argv[2] == 'AIM':
        if len(sys.argv) > 3:
            vim_AIM(sys.argv[1], sys.argv[2:])
        else:
            vim_AIM(sys.argv[1], ['all'])    # or: vim_AD(sys.argv[1])


