#!/bin/env python3
# encoding: gbk
import re, os, sys, copy
import logging
import codecs


gIgnorePortListFile = '.port.ignore'
gRegType = ['reg', 'trireg', 'integer', 'time', 'real', 'event', 'genvar']
gNetType = ['supply0', 'supply1', 'tri',  'triand', 'trior', 'tri0', 'tri1', 'wire', 'wand', 'wor']
gKeyWord = ['always', 'and', 'assign', 'automatic', 'begin', 'buf', 'bufif0', 'bufif1', 'case', 'casex', 'casez', 'cell', 'cmos', 'config', 'deassign', 'default', 'defparam', 'design', 'disable', 'edge', 'else', 'end', 'endcase', 'endconfig', 'endfunction', 'endgenerate', 'endmodule', 'endprimitive', 'endspecify', 'endtable', 'endtask', 'event', 'for', 'force', 'forever', 'fork', 'function', 'generate', 'genvar', 'highz0', 'highz1', 'if', 'ifnone', 'incdir', 'include', 'initial', 'inout', 'input', 'instance', 'integer', 'join', 'large', 'liblist', 'library', 'localparam', 'macromodule', 'medium', 'module', 'nand', 'negedge', 'nmos', 'nor', 'noshowcancelled', 'not', 'notif0', 'notif1', 'or', 'output', 'parameter', 'pmos', 'posedge', 'primitive', 'pull0', 'pull1', 'pulldown', 'pullup', 'pulsestyle_onevent', 'pulsestyle_ondetect', 'rcmos', 'real', 'realtime', 'reg', 'release', 'repeat', 'rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1', 'scalared', 'showcancelled', 'signed', 'small', 'specify', 'specparam', 'strong0', 'strong1', 'supply0', 'supply1', 'table', 'task', 'time', 'tran', 'tranif0', 'tranif1', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'unsigned', 'use', 'vectored', 'wait', 'wand', 'weak0', 'weak1', 'while', 'wire', 'wor', 'xnor', 'xor', '`define', '`ifdef', '`else', '`endif', '`undefine']
gBusKeyWord = { \
'rom'  : {'rom_clk':'clk','rom_cen':'cen','rom_addr':'addr', 'rom_rdata':'rdata'},
'ram'  : {'ram_clk':'clk','ram_cen':'cen','ram_wen':'wen','ram_addr':'addr', 'ram_wdata':'wdata', 'ram_rdata':'rdata'},
'ram2' : {'ram_wclk':'wclk', 'ram_wcen':'wcen', 'ram_waddr':'waddr', 'ram_wdata':'wdata',
          'ram_rclk':'rclk', 'ram_rcen':'rcen', 'ram_raddr':'raddr', 'ram_rdata':'rdata'},
'apb'  : {'pclk':'pclk', 'presetn':'presetn', 'paddr':'paddr', 'pprot':'pprot', 'psel':'psel', 'penable':'penable', 'pwrite':'pwrite', 'pwdata':'pwdata', 'pstrb':'pstrb', 'pready':'pready', 'prdata':'prdata', 'pslverr':'pslverr'},
'ahb'  : {'hclk':'hclk', 'hresetn':'hresetn', 'haddr':'haddr', 'htrans':'htrans', 'hwrite':'hwrite', 'hsize':'hsize', 'hburst':'hburst', 'hprot':'hprot', 'hwdata':'hwdata', 'hsel':'hsel', 'hrdata':'hrdata', 'hready':'hready', 'hreadyin':'hreadyin', 'hreadyout':'hreadyout', 'hresp':'hresp', 'hbusreq':'hbusreq', 'hlock':'hlock', 'hgrant':'hgrant', 'hmaster':'hmaster', 'hmasterlock':'hmasterlock', 'hsplit':'hsplit'},
'atb'  : {'atclk':'atclk', 'atclken':'atclken', 'atresetn':'atresetn', 'atbytes':'atbytes', 'atdata':'atdata', 'atid':'atid', 'atready':'atready', 'atvalid':'atvalid', 'afvalid':'afvalid', 'afready':'afready', 'syncreq':'syncreq'},
#AXI-Stream
'axis' : {'tvalid':'tvalid', 'tready':'tready', 'tdata':'tdata', 'tstrb':'tstrb', 'tkeep':'tkeep', 'tlast':'tlast', 'tid':'tid', 'tdest':'tdest', 'tuser':'tuser'},
'axi'  : {'aclk':'aclk', 'aresetn':'aresetn', 'awid':'awid', 'awaddr':'awaddr', 'awlen':'awlen', 'awsize':'awsize', 'awburst':'awburst', 'awlock':'awlock', 'awcache':'awcache', 'awprot':'awprot', 'awqos':'awqos', 'awregion':'awregion', 'awuser':'awuser', 'awvalid':'awvalid', 'awready':'awready', 'wid':'wid', 'wdata':'wdata', 'wstrb':'wstrb', 'wlast':'wlast', 'wuser':'wuser', 'wvalid':'wvalid', 'wready':'wready', 'bid':'bid', 'bresp':'bresp', 'buser':'buser', 'bvalid':'bvalid', 'bready':'bready',
'arid':'arid', 'araddr':'araddr', 'arlen':'arlen', 'arsize':'arsize', 'arburst':'arburst', 'arlock':'arlock', 'arcache':'arcache', 'arprot':'arprot', 'arqos':'arqos', 'arregion':'arregion', 'aruser':'aruser', 'arvalid':'arvalid', 'arready':'arready', 'rid':'rid', 'rdata':'rdata', 'rresp':'rresp', 'rlast':'rlast', 'ruser':'ruser', 'rvalid':'rvalid', 'rready':'rready',
'csysreq':'csysreq', 'csysack':'csysack', 'cactive':'cactive'}}

str_autoports_end    = "//Auto add ports end"
str_autoports_begin  = "//Auto add ports begin"
str_delports_end     = "//Auto delete ports end"
str_delports_begin   = "//Auto delete ports begin"

str_addports_end    = "// End of add ports for"
str_addports_begin  = "// Begin of add ports for"
str_autodefs_end    = "// End of automatic define"

re_cfg_fmt          = re.compile(r"//\s*\$(?P<label>(?P<type>\w+?)_\w+)(:(?P<elem>\w+)){0,1}")
re_cfg_pfix         = re.compile(r"^(?P<pfixa>(?P<pfixs>[^_]+)(_[^_]+){0,1})")
re_macro_def_fmt    = re.compile(r"`(?P<type>ifdef\b|ifndef\b|elsif\b|else\b|endif\b)(\s+(?P<str>\S+)){0,1}")
re_macro_def        = re.compile(r"^\s*`(?P<def>ifdef\b|ifndef\b|elsif\b|else\b|endif\b)")
re_comment          = re.compile(r"^\s*//")
re_line_comment     = re.compile(r"//.*")
re_inst_bound       = re.compile(r"\)\s*//")
re_blank_line       = re.compile(r"^\s*$")

re_curly            = re.compile(r"\{[^\{\}]*\}")
re_round            = re.compile(r"\([^\(\)]*\)")
re_square           = re.compile(r"\[[^\[\]]*\]")

re_task             = re.compile(r"\btask\b")
re_function         = re.compile(r"\bfunction\b")
re_generate         = re.compile(r"\bgenerate\b")
re_endtask          = re.compile(r"\bendtask\b")
re_endfunction      = re.compile(r"\bendfunction\b")
re_endgenerate      = re.compile(r"\bendgenerate\b")

re_sys_func         = re.compile(r"\$\w+\s*\(\s+")
re_para             = re.compile(r"(\bparameter\b|\blocalparam\b|\bspecparam\b|\bdefparam\b)\s+")
re_para_match       = re.compile(r"(?P<name>\w+)(?P<equal>\s*=\s*)(?P<value>.*?)(?P<last>\s*$|\s*,\s*\w+\s*=)")
re_para_inst        = re.compile(r"\b(?P<inst>\w+)\s+#\s*\(")
re_port_pfix        = re.compile(r"(?P<dir>\binput\b|\boutput\b|\binout\b)")
re_port_decla_pfix  = re.compile(r"(?P<def>.*?)(?P<args>(?P<dir>\binput\b|\boutput\b|\binout\b).*)")
#no logic: re_port_decla_fmt   = re.compile(r"^\s*(?P<dir>\binput\b|\boutput\b|\binout\b)\s*(?P<type>\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b){0,1}\s*(?P<sign>signed){0,1}\s*(?P<wth>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}(?P<port>.*)")
#no logic: re_port_decla       = re.compile(r"(?P<dir>\binput\b|\boutput\b|\binout\b)\s*(?P<type>\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b){0,1}\s*(?P<sign>signed){0,1}\s*(?P<wth>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}(?P<port>.*)")
re_port_decla_fmt   = re.compile(r"^\s*(?P<dir>\binput\b|\boutput\b|\binout\b)\s*(?P<type>\blogic\b|\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b){0,1}\s*(?P<sign>signed){0,1}\s*(?P<wth>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}(?P<port>.*)")
re_port_decla       = re.compile(r"(?P<dir>\binput\b|\boutput\b|\binout\b)\s*(?P<type>\blogic\b|\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b){0,1}\s*(?P<sign>signed){0,1}\s*(?P<wth>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}(?P<port>.*)")

re_port_connect     = re.compile(r"\.(?P<port>\w+)\s*\(\s*(?P<wire>\w+)\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}\s*\)(\s*,?\s*//\s*(?P<io>IO|I|O))?", re.I)
#no logic: re_type_pfix        = re.compile(r"\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b")
re_type_pfix        = re.compile(r"\blogic\b|\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b")
##re_type_decla       = re.compile(r"^\s*([,;]\s*)?(?P<type>\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b)\s*(\([^\)]+\)){0,1}\s*(vectored|scalared){0,1}\s*(signed){0,1}\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}\s*(#\s*[-\.:\w]+|#\([^\)]+\)){0,1}(?P<last>.*)")
###re_type_decla       = re.compile(r"^\s*([,;]\s*)?(?P<type>\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b)\s*(\([^\)]+\)){0,1}\s*(vectored|scalared){0,1}\s*(signed){0,1}\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^\]]+)){0,1}\]){0,1}\s*(#\s*[-\.:\w]+|#\([^\)]+\)){0,1}(?P<last>.*)")
#no logic: re_type_decla       = re.compile(r"(^\s*([,;]\s*)?|\s+)(?P<type>\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b)\s*(\([^\)]+\)){0,1}\s*(vectored|scalared){0,1}\s*(signed){0,1}\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^\]]+)){0,1}\]){0,1}\s*(#\s*[-\.:\w]+|#\([^\)]+\)){0,1}(?P<last>.*)")
re_type_decla       = re.compile(r"(^\s*([,;]\s*)?|\s+)(?P<type>\blogic\b|\breg\b|\btrireg\b|\binteger\b|\btime\b|\brealtime\b|\breal\b|\bevent\b|\bgenvar\b|\bsupply\b[01]|\btri\b|\btriand\b|\btrior\b|\btri\b[01]|\bwire\b|\bwand\b|\bwor\b)\s*(\([^\)]+\)){0,1}\s*(vectored|scalared){0,1}\s*(signed){0,1}\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^\]]+)){0,1}\]){0,1}\s*(#\s*[-\.:\w]+|#\([^\)]+\)){0,1}(?P<last>.*)")
re_assign           = re.compile(r"(\bassign\b)\s*(\([^\)]+\)){0,1}\s*(#\s*[-\.:\w]*|#\([^\)]*\)){0,1}\s+(?P<wire>\w+)\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}\s*=(?P<expr>[^=].*)")
##re_assign           = re.compile(r"(\bassign\b)\s*(\([^\)]+\)){0,1}\s*(#\s*[-\.:\w]+|#\([^\)]+\)){0,1}\s*(?P<wire>\w+)\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}\s*=(?P<expr>[^=].*)")
re_proc_pfix        = re.compile(r"\balways\b|\binitial\b")
##re_reg_assign       = re.compile(r"(^\s*|:\s*)(?P<reg>\w+)\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}\s*(<=|=)(?P<expr>[^=].*)")
re_reg_assign       = re.compile(r"(^\s*|\s+)(?P<reg>\w+)\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}\s*(<=|=)(?P<expr>[^=].*)")

re_redunction       = re.compile(r"(^|[^\w\s])\s*(\^|\^\~|\~\^|\&|\~\&|\||\~\|)\s*\w+")
re_conditional      = re.compile(r"(\([^\)]+\)|\b\w+\b)\s*\?")

#re_signal           = re.compile("(\w+)\s*(\[([^:\]]+)(:([^:\]]+)){0,1}\]){0,1}")
re_signal           = re.compile("(?P<wire>\w+)(\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}")
re_constant         = re.compile("(^|[^\w])(?P<size>\d*)'(?P<data>b[01]+|o[0-7]+|d[0-9]+|h[0-9a-f]+)", re.I)

re_option_v         = re.compile(r"^\s*-[vV]\s+(?P<file>\S+)\.(?P<pfix>\S+)")
re_option_y         = re.compile(r"^\s*-[yY]\s+(?P<path>\S+)")
re_option_f         = re.compile(r"^\s*-[fF]\s+(?P<file>\S+)")
re_option_inc       = re.compile(r"^\s*\+incdir\+(?P<path>\S+)")
re_option_file      = re.compile(r"^\s*(?P<file>\S+)\.(?P<pfix>\S+)")

re_inst_fmt         = re.compile(r"(?P<mod>\w+)\s+(#|\([^\)]+\)){0,1}\s*(?P<inst>\w+)\s*(\[[^\]]+\]){0,1}\s*\((?P<post>.*)")
re_connect          = re.compile(r"\bcon\s+(?P<finst>\w+)\.(?P<flab>\w+)(:(?P<sfix>\w+)){0,1}(:(?P<fwidth>\[(?P<fmsb>[^:\]]+)(:(?P<flsb>[^\]]+)){0,1}\])){0,1}\s+(?P<tinst>\w+)\.(?P<tlab>\w+)(:(?P<twidth>\[(?P<tmsb>[^:\]]+)(:(?P<tlsb>[^\]]+)){0,1}\])){0,1}")
re_addsocket        = re.compile(r"\baddsocket\s*(?P<module>\w+)\.(?P<label>\w+)(\s+(?P<socket>\w+))?")
re_element          = re.compile(r"(?P<name>\w+)\s*(?P<width>\[(?P<msb>[^\]]+?)(:(?P<lsb>[^:\]]+)){0,1}\]){0,1}\s+(?P<pname>\w+)")
re_endsocket        = re.compile(r"\bendaddsocket\b")

re_autoarg_end      = re.compile(r"\)\s*;")
re_autoarg_begin    = re.compile(r"/\*\s*autoarg\s*\*/", re.I)
re_autodefine       = re.compile(r"/\*\s*autodef(?:ine)?\s*\*/", re.I)
re_autowire_end     = re.compile(r"^\s*//\s*end\s*of\s*automatic\s*define\b", re.I)
re_autoport_end     = re.compile(r"^\s*//\s*end\s*of\s*add\s*ports\s+for\s+\[(?P<inst>\w+)\]", re.I)
re_autoport_begin   = re.compile(r"^\s*//\s*begin\s*of\s*add\s*ports\s+for\s+\[(?P<inst>\w+)\]", re.I)
re_autoarg          = re.compile(r"/\*\s*autoarg\s*\*/(\s*\)\s*;)?", re.I)
re_autoinst         = re.compile(r"/\*\s*autoinst\s*\*/(\s*\)\s*;)?", re.I)
re_autoinst_key     = re.compile(r"/\*\s*autoinst\s*\*/", re.I)

#***********************************************************
# Class 'lDict' # Start{{{
class lDict(dict):
    def __init__(self):
        dict.__init__(self)
        self.lkeys = []

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if key not in self.lkeys:
            self.lkeys.append(key)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.lkeys.remove(key)

    def pop(self, key):
        dict.pop(self, key)
        self.lkeys.remove(key)

    def copy(self):
        dictTmp = lDict()
        for k in self.lkeys:
            try:
                dictTmp[k] = self[k].copy()
            except AttributeError as e:
                dictTmp[k] = self[k]
        return dictTmp
# Class 'lDict' # End}}}
#***********************************************************

#####***********************************************************
##### Function 'logConfig' # Start{{{
##### ColoredFormatter for Linux
####class coloredFormatter(logging.Formatter):
####    def format(self, record):
####        LOG_COLORS = {'DEBUG'   : '\033[1;32;40m[DEBUG]\033[0m',
####                      'INFO'    : '\033[1;36;40m[INFO]\033[0m',
####                      'WARNING' : '\033[1;35;40m[WARNING]\033[0m',
####                      'ERROR'   : '\033[1;37;41m[ERROR]\033[0m',
####                      'CRITICAL': '\033[1;31;40m[CRITICAL]\033[0m'}
####        #LOG_COLORS = {'DEBUG'   : colorama.Fore.GREEN+'[DEBUG]'+colorama.Style.RESET_ALL,
####        #              'INFO'    : colorama.Fore.CYAN+'[INFO]'+colorama.Style.RESET_ALL,
####        #              'WARNING' : colorama.Style.BRIGHT+colorama.Fore.MAGENTA+'[WARNING]'+colorama.Style.RESET_ALL,
####        #              'ERROR'   : colorama.Style.BRIGHT+colorama.Back.RED+colorama.Fore.WHITE+'[ERROR]'+colorama.Style.RESET_ALL,
####        #              'CRITICAL': colorama.Style.BRIGHT+colorama.Back.RED+colorama.Fore.WHITE+'[CRITICAL]'+colorama.Style.RESET_ALL}
####        level_name = record.levelname
####        msg = logging.Formatter.format(self, record)
####        return msg.replace(level_name, LOG_COLORS.get(level_name, level_name))
####
####def logConfig(logfile, level=logging.INFO):
####    # Create Logger
####    objLog = logging.getLogger("VlogDebug")
####
####    # Set Global Logging Level
####    # Logging Levels: CRITICAL(50), ERROR(40), WARN/WARNING(30), INFO(20), DEBUG(10), NOTSET(0)
####    objLog.setLevel(level)
####
####    # Add Logging Handler
####    dateFmt = "%a, %d %b %Y %H:%M:%S"
####    #~~Create logging formatter
####    logFmt = logging.Formatter("%(filename)s[line:%(lineno)d]:\n\t%(levelname)s: %(message)s")
####    #For Linux: logFmt = coloredFormatter("%(filename)s[line:%(lineno)d]:\n\t%(levelname)s: %(message)s")
####    #logFmt = coloredFormatter("%(filename)s[line:%(lineno)d]:\n\t%(levelname)s: %(message)s")
####    #logFmt = logging.Formatter("%(levelname)s: %(message)s")
####    logFmt.datefmt = dateFmt
####    #~~Create console display formatter
####    #dspFmt = logging.Formatter("%(filename)s[line:%(lineno)d]:\n\t%(levelname)s: %(message)s")
####    #For Linux: dspFmt = coloredFormatter("%(filename)s[line:%(lineno)d]:\n\t%(levelname)s: %(message)s")
####    #dspFmt = coloredFormatter("%(filename)s[line:%(lineno)d]:\n\t%(levelname)s: %(message)s")
####    dspFmt = coloredFormatter("%(filename)s[line:%(lineno)d]: %(levelname)s: %(message)s")
####    #dspFmt = logging.Formatter("%(levelname)s: %(message)s")
####    dspFmt.datefmt = dateFmt
####
####    #~~Create file hander with logs even debug messages
####    logFH = logging.FileHandler(logfile, mode='w')
####    logFH.setLevel(level)
####    #~~Create console hander with a higher log level
####    logCH = logging.StreamHandler()
####    logCH.setLevel(level)
####
####    #~~Add formatters to log handlers
####    logCH.setFormatter(dspFmt)
####    logFH.setFormatter(logFmt)
####    #~~Add the handlers to logger
####    objLog.addHandler(logCH)
####    objLog.addHandler(logFH)
####
####    return objLog
##### Function 'logConfig' # End}}}
#####***********************************************************
####
####gLog = logConfig("vlogDebug.log", logging.DEBUG)
####
# Function 'xprint' # {{{
def xprint(fpLog, msg):
    print(msg)
    if fpLog is not None:
        fpLog.write(msg+"\n")
    else:
        if   msg.startswith("Error:"):
            logging.error(msg)
        elif msg.startswith("Warning:"):
            logging.warning(msg)
        elif msg.startswith("Info:"):
            logging.info(msg)
        elif msg.startswith("Fatal:"):
            logging.critical(msg)
        else:
            logging.debug(msg)

# Function 'xprint' # }}}

# Function 'x2int' # {{{
def x2int(x, fpLog=None):
    """
    To decimal integer number
    4'b10   --> 2
    4'd10   --> 10
    4'o10   --> 8
    5'h10   --> 16
    """
    if x.isdigit():
        return int(x)

    x_size = ''
    x_data = 0
    x_base = 10
    obj = re_constant.search(x)
    if obj is not None:
        x_size, x_data = (obj.group('size'), obj.group('data'))
        if   x_data.startswith('b'):
            x_base = 2
        elif x_data.startswith('o'):
            x_base = 8
        elif x_data.startswith('h'):
            x_base = 16
        else:
            x_base = 10
        x_data = x_data[1:]
    else:
        xprint(fpLog, "Error: Invalid Verilog numeric string: %s"%x)
        return None

    return int(x_data, base=x_base) if x_size == '' else int(x_data, base=x_base)%2**int(x_size)
# Function 'x2int' # }}}

# Function 'get_parameter' # {{{
def get_parameter(curStr, preStr, dParam, fpLog=None):
    """
    dParam : {
              paramString : paramValue
             }
    """
    preStr += ' '+curStr
    semicolonIdx = preStr.find(';')
    while semicolonIdx > -1:
        procStr = preStr[:semicolonIdx]
        preStr  = preStr[semicolonIdx+1:]

        obj = re_para.search(procStr)
        if obj:
            orgStr = procStr
            objParam = re_para_match.search( re_para.sub('', procStr) )
            while objParam:
                if objParam.group('name') in dParam:
                    xprint(fpLog, "Error: Parameter '%s' is already defined! <%s>"%(objParam.group('name'), orgStr))
                else:
                    dParam[objParam.group('name')] = objParam.group('value').strip()
                objParam = re_para_match.search( objParam.group('last') )
        semicolonIdx = preStr.find(';')
    return preStr
# Function 'get_parameter' # }}}


# Function 'get_ignore_ports' # {{{
def get_ignore_ports(curStrs, fName, silent=1, fpLog=None):
    """
    lIgnorePorts = [ignorePort0, ignorePort1, ...]
    """
    lIgnorePorts = []
    # Ignore port described as:
    # input  [msb:lsb] in1,  in2,  in3;
    # output [msb:lsb] out1, out2, out3;
    for idx, curStr in enumerate(curStrs):
        orgStr = curStr
        # Remove comments
        if re_comment.search(curStr):
            continue
        elif re_blank_line.search(curStr):
            continue
        curStr = curStr[:curStr.find(';')]

        # Port declaration searching
        obj = re_port_decla.search(curStr)
        if obj:
            portStr = obj.group('port')
            for port in portStr.split(','):
                port = port.strip()
                if len(port) == 0:
                    continue
                if re.search("^\w+$", port):
                    lIgnorePorts.append(port)
                else:
                    xprint(fpLog, "Error: Invalid port [%s] declaration in line[%d] if [%s], <%s>"%(port, idx, fName, orgStr))
        else:
            xprint(fpLog, "Error: Unkown port declaration format in line[%d] if [%s], <%s>"%(idx, fName, orgStr))

    return lIgnorePorts
# Function 'get_ignore_ports' # }}}

# Function 'get_module_ports' # {{{
def get_module_ports(curStrs, mName=None, mFile='', dMacro={}, dCfg={}, silent=1, fpLog=None):
    '''
    Verilog module port parsing:
    dPorts : {
              'plen' : maxPortLen
              'wlen' : maxWireSignalLen
              'llen' : maxWireLabelLen
              'blen' : maxBitWidthLen
              'list' : [portname, ...]
              'dict' : {
                        portname : {
                                    'inout' : input/output/inout
                                    'type'  : wire/reg/...
                                    'width' : [msb:lsb]
                                    'msb'   : msb
                                    'lsb'   : lsb
                                    'name'  : portName
                                    'ignore': True/False
                                    'macro' : { #lDict
                                               MACRO : True/False
                                              }
                                  }
                       }
              'auto' : { instName : {'start':idxStartInList, 'end':idxEndInList}}
             }
    '''
    dPorts = {'plen' : 0,
              'wlen' : 0,
              'llen' : 0,
              'blen' : 5,
              'auto' : {},
              'list' : [],
              'dict' : {}}
    macroCnt  = 0
    macroElse = 0
    curMacros = lDict()
    portInMacro = False
    modArgs  = ''
    modFlag  = 0
    modName  = None
    dInfoLoc = {'eport' : -1,
                'smod'  : -1,
                'emod'  : -1,
                'swire' : -1,
                'ewire' : -1,
                'sarg'  : -1,
                'earg'  : -1,
                'adef'  : -1,
                'ploc'  : {}}
    inComment  = inModule = False
    inFunction = inTask   = False
    inGenerate = inPara   = False

    dParam = lDict()
    preStr   = ''
    portType = 95
    autoPort = None
    findMod  = False
    for idx, curStr in enumerate(curStrs):
        # Get comments location
        if dInfoLoc['sarg'] == -1:
            if re_autoarg_begin.search(curStr):
                dInfoLoc['sarg'] = idx
                if re_autoarg_end.search( re_line_comment.sub('', curStr) ):
                    dInfoLoc['earg'] = idx
        if inModule and dInfoLoc['adef'] == -1:
            obj = re_autoport_begin.search(curStr)
            if obj:
                autoPort = obj.group('inst')
                dPorts['auto'][obj.group('inst')] = {'begin':len(dPorts['list'])}
                dInfoLoc['ploc'][obj.group('inst')] = {'begin':idx}
                continue
            obj = re_autoport_end.search(curStr)
            if obj and obj.group('inst') in dInfoLoc['ploc']:
                autoPort = None
                dPorts['auto'][obj.group('inst')]['end']  = len(dPorts['list'])
                dInfoLoc['ploc'][obj.group('inst')]['end'] = idx
                continue
        #if inModule and dInfoLoc['swire'] == -1: ????
            if re_autodefine.search(curStr):
                dInfoLoc['adef']  = idx
                dInfoLoc['swire'] = idx
                continue
        if inModule and dInfoLoc['ewire'] == -1 and dInfoLoc['adef'] > 0:
            if re_autowire_end.search(curStr):
                dInfoLoc['ewire'] = idx
                continue
        # Filter comments
        preInPara = inPara
        curStr, inComment, inPara, inTask, inFunction, inGenerate, offset, postComment = proc_comment( \
        curStr, inComment, inPara, inTask, inFunction, inGenerate, '')
        curStr = curStr.strip()

        if dInfoLoc['earg'] == -1 and dInfoLoc['sarg'] > -1:
            if re_autoarg_end.search(curStr):
                dInfoLoc['earg'] = idx

        if inTask or inFunction or inGenerate:
            continue

        # ~~ Get Parameters {
        preParamStr = ''
        if inModule:
            preParamStr = get_parameter(curStr, preParamStr, dParam, fpLog)
        # ~~ Get Parameters }

        # `ifdef, `ifndef, `else, `endif
        obj = re_macro_def_fmt.search(curStr)
        while(obj):
            defTyp = obj.group('type')
            defStr = obj.group('str')
            if defTyp == 'ifdef':
                if defStr in curMacros:
                    if curMacros[defStr] is True:
                        xprint(fpLog, "Error: Condition '`ifdef %s' always TRUE (%s is already defined at this branch, will result in incorrect macro define extrct error!) at line [%d] of file [%s], <%s>"%(defStr, defStr, idx+1, mFile, curStr))
                    else:
                        xprint(fpLog, "Error: Condition '`ifdef %s' always FALSE (%s is not defined at this branch, will result in incorrect macro define extrct error!) at line [%d] of file [%s], <%s>"%(defStr, defStr, idx+1, mFile, curStr))
                else:
                    macroCnt += 1
                    curMacros[defStr] = True
            elif defTyp == 'ifndef':
                if defStr in curMacros:
                    if curMacros[defStr] is True:
                        xprint(fpLog, "Error: Condition '`ifndef %s' always FALSE (%s is already defined at this branch, will result incorrect macro define extract error!) at line [%d] of file [%s], <%s>"%(defStr, defStr, idx+1, mFile, curStr))
                    else:
                        xprint(fpLog, "Error: Condition '`ifndef %s' always TRUE (%s is not defined at this branch, will result incorrect macro define extract error!) at line [%d] of file [%s], <%s>"%(defStr, defStr, idx+1, mFile, curStr))
                else:
                    macroCnt += 1
                    curMacros[defStr] = False
            elif defTyp == 'elsif':
                if len(curMacros.lkeys) == 0:
                    xprint(fpLog, "Error: '`elsif' should be used after '`ifdef' or '`ifndef' at line[%d] of file[%s], <%s>"%(idx+1, mFile, curStr))
                else:
                    if defStr in curMacros:
                        if curMacros[defStr] is True:
                            xprint(fpLog, "Error: Condition '`elsif %s' always TRUE (%s is already defined at this branch, will result incorrect macro define extract error!) at line [%d] of file [%s], <%s>"%(defStr, defStr, idx+1, mFile, curStr))
                        else:
                            xprint(fpLog, "Error: Condition '`elsif %s' always FALSE (%s is not defined at this branch, will result incorrect macro define extract error!) at line [%d] of file [%s], <%s>"%(defStr, defStr, idx+1, mFile, curStr))
                    else:
                        macroCnt  += 1
                        macroElse += 1
                        curMacros[curMacros.lkeys[-1]] = not curMacros[curMacros.lkeys[-1]]
                        curMacros[defStr] = True
            elif defTyp == 'else': # ???
                if len(curMacros.lkeys) > 0:
                    curMacros[curMacros.lkeys[-1]] = not curMacros[curMacros.lkeys[-1]]
                else:
                    xprint(fpLog, "Error: '`else' should be used after '`ifdef' or '`ifndef' at line[%d] of file[%s], <%s>"%(idx+1, mFile, curStr))
            else: #defTyp == 'endif'
                macroCnt -= 1
                if portInMacro and macroCnt == 0:
                    portInMacro = False
                    dInfoLoc['eport'] = idx
                if macroElse > 0:
                    macroCnt  -= 1
                    macroElse -= 1
                    del curMacros[curMacros.lkeys[-1]]
                if len(curMacros.lkeys) > 0:
                    del curMacros[curMacros.lkeys[-1]]
                else:
                    xprint(fpLog, "Error: '`endif' is more than defined Macros!")

            curStr = re_macro_def_fmt.sub('', curStr, 1)
            # Port extract begin: `ifdef XXXX input [3:0] in0; `endif
            obj = re_port_pfix.search(curStr)
            while obj:
                #ioNxt = -1
                ioCur = curStr.find(obj.group('dir'))
                ioLen = len(obj.group('dir'))
                ioDef = curStr[ioCur:]

                obj = re_port_pfix.search(curStr[ioCur+ioLen:])
                if obj:
                    #ioNxt  = ioCur + ioLen + curStr[ioCur+ioLen:].find(obj.group('dir'))
                    #ioDef  = curStr[ioCur:ioNxt]
                    #curStr = curStr[ioNxt:]
                    obj = re_port_decla_pfix.search(curStr[ioCur+ioLen:])
                    ioDef  = curStr[ioCur:ioCur+ioLen]+obj.group('def')
                    curStr = obj.group('args')

                ioComaIdx = ioDef.find(';')
                if ioComaIdx > 0:
                    ioDef = ioDef[:ioComaIdx]
                    if obj is None:
                        curStr = curStr[ioCur+ioComaIdx+1:]

                objPortDecla = re_port_decla.search(ioDef)
                if objPortDecla:
                    dInfoLoc['eport'], portInMacro = get_port_list(ioDef, dInfoLoc['eport'], portInMacro, idx-1, macroCnt, autoPort, objPortDecla, curMacros, modName, postComment, dCfg, dPorts, silent, fpLog=fpLog)
            # Port extract end: `ifdef XXXX input [3:0] in0; `endif
            obj = re_macro_def_fmt.search(curStr)

        if inModule is False:
            obj = re.search(r"\bmodule\s+(?P<mname>\w+)", curStr)
            if obj:
                modName = obj.group('mname')
            else:
                obj = re.search(r"\bmodule\b\s+`(?P<mmacro>\S+)", curStr)
                if obj:
                    if obj.group('mmacro') in dMacro:
                        modName = dMacro[obj.group('mmacro')]['value']
                    else:
                        xprint(fpLog, "Error: Macro '`%s' is not defined! <%s>"%(obj.group('mmacro'), curStr))
            if modName is not None and (mName is None or modName == mName):
                preStr   = curStr
                modFlag  = 1
                findMod  = True
                inModule = True
                dInfoLoc['smod'] = idx
        elif modFlag == 1:
            preStr += ' ' + curStr
            argsEnd = preStr.find(';')
            if argsEnd > -1:
                modArgs = preStr[:argsEnd+1]
                preStr  = preStr[argsEnd+1:]
                if re_port_pfix.search(modArgs):
                    modFlag  = 2
                    portType = 2001
                    modArgs  = re.sub("\)\s*;\s*$", '', modArgs)
                else:
                    modFlag = -1
        elif modFlag == 2:
            preStr += ' ' + curStr
            obj = re_port_pfix.search(modArgs)
            while obj:
                ioCur = modArgs.find(obj.group('dir'))
                ioLen = len(obj.group('dir'))
                #ioDef = modArgs[modArgs:]
                ioDef = modArgs[ioCur:]

                obj = re_port_pfix.search(modArgs[ioCur+ioLen:])
                if obj:
                    obj = re_port_decla_pfix.search(modArgs[ioCur+ioLen:])
                    ioDef   = modArgs[ioCur:ioCur+ioLen]+obj.group('def')
                    modArgs = obj.group('args')

                objPortDecla = re_port_decla.search(ioDef)
                if objPortDecla:
                    dInfoLoc['eport'], portInMacro = get_port_list(ioDef, dInfoLoc['eport'], portInMacro, idx-1, macroCnt, autoPort, objPortDecla, curMacros, modName, postComment, dCfg, dPorts, silent, fpLog=fpLog)
            modFlag = -1
        else:
            if re.search(r"\bendmodule\b", curStr):
                preStr = ''
                dInfoLoc['emod'] = idx
                inModule = False
                break
            preStr += ' ' + curStr
            semiIdx = preStr.find(';')
            while semiIdx > -1:
                procLine = preStr[:semiIdx]
                preStr   = preStr[semiIdx+1:]

                objPortDecla = re_port_decla.search(procLine)
                if objPortDecla:
                    dInfoLoc['eport'], portInMacro = get_port_list(procLine, dInfoLoc['eport'], portInMacro, idx-1, macroCnt, autoPort, objPortDecla, curMacros, modName, postComment, dCfg, dPorts, silent, fpLog=fpLog)
                semiIdx = preStr.find(';')
            else:
                obj = re_port_pfix.search(preStr)
                preStr = '' if obj is None else preStr

    if mName is not None and findMod is False:
        xprint(fpLog, "Warning: Cannot find module[%s] in file[%s]!"%(mName, mFile))

    return (dInfoLoc, modName, dPorts, dParam, portType)
# Function 'get_module_ports' # }}}

# Function 'get_port_list' # {{{
def get_port_list(curStr, pLoc, inMacro, idx, macroCnt, autoPort, objPortDecla, curMacros, mName, postComment, dCfg, dPorts, silent=1, fpLog=None):
    if macroCnt > 0:
        inMacro = True
    mTmpName = 'outside'
    cfgLabel = cfgType = cfgElem = None
    objCfg = re_cfg_fmt.search(postComment)
    if objCfg:
        cfgLabel, cfgType, cfgElem = (objCfg.group('label'), objCfg.group('type'), objCfg.group('elem'))
        if 'sufix'  not in dCfg:
            dCfg['sufix'] = {}
        if 'socket'  not in dCfg:
            dCfg['socket'] = {}
        if 'connect' not in dCfg:
            dCfg['connect'] = {}

    pAttrDir   = objPortDecla.group('dir')
    pAttrType  = objPortDecla.group('type')
    pAttrWidth = objPortDecla.group('wth')  if objPortDecla.group('wth') is None else re.sub("\s+", '', objPortDecla.group('wth'))
    pAttrMsb   = objPortDecla.group('msb')  if objPortDecla.group('msb') is None else re.sub("\s+", '', objPortDecla.group('msb'))
    pAttrLsb   = pAttrMsb                   if objPortDecla.group('lsb') is None else re.sub("\s+", '', objPortDecla.group('lsb'))

    if pAttrDir and pAttrType and pAttrDir != 'output' and pAttrDir != 'any' and pAttrType in gRegType:
        xprint(fpLog, "Error: Signal type '%s' used as '%s' port! (%s)"%(pAttrType, pAttrDir, curStr))

    orgStr = curStr
    curStr = objPortDecla.group('port')
    for port in curStr.split(','):
        port = port.strip()
        if len(port) == 0:
            continue
        #print("DEBUG>> mName[%s] -> port[%s]: curStr[%s] --> orgStr[%s]"%(mName, port, curStr, orgStr))
        if re.search("^\w+$", port):
            pLoc = idx
            if port in dPorts['dict']:
                xprint(fpLog, "Error: Port '%s' is already defined! (module[%s]: %s)"%(port, mName, orgStr))
            else:
                dPorts['dict'][port] = {}
                dPorts['dict'][port]['isnew'] = {}
                dPorts['dict'][port]['name' ] = port
                dPorts['dict'][port]['inout'] = pAttrDir
                dPorts['dict'][port]['type' ] = pAttrType
                dPorts['dict'][port]['auto' ] = autoPort
                dPorts['dict'][port]['width'] = pAttrWidth
                dPorts['dict'][port]['msb'  ] = pAttrMsb
                dPorts['dict'][port]['lsb'  ] = pAttrLsb
                dPorts['dict'][port]['macro'] = curMacros.copy()
                dPorts['list'].append(port)

                dPorts['plen'] = max(dPorts['plen'], len(port))
                dPorts['wlen'] = max(dPorts['wlen'], len(port))
                if dPorts['dict'][port]['width']:
                    dPorts['blen'] = max(dPorts['blen'], len(     dPorts['dict'][port]['width']))
                    dPorts['llen'] = max(dPorts['llen'], len(port+dPorts['dict'][port]['width']))
                else:
                    dPorts['llen'] = max(dPorts['llen'], len(port))
                
                # Socket config. info.
                if objCfg:
                    if cfgElem is None:
                        if cfgType in gBusKeyWord:
                            obj = re_cfg_pfix.search(port)
                            if obj:
                                pfixAll, pfixSub = (obj.group('pfixa'), obj.group('pfixs'))
                                if   pfixSub in gBusKeyWord[cfgType]:
                                    cfgElem = gBusKeyWord[cfgElem][pfixSub]
                                elif pfixAll in gBusKeyWord[cfgType]:
                                    cfgElem = gBusKeyWord[cfgElem][pfixAll]
                    if cfgElem is None:
                        if silent == 0:
                            xprint(fpLog, "Warning: <module[%s]> Invalid port socket description <SocketLabel[%s], Port[%s]>"%(mName, cfgLabel, port))
                        continue

                    if mTmpName not in dCfg['socket']:
                        dCfg['socket'][mTmpName] = {}
                    if cfgLabel not in dCfg['socket'][mTmpName]:
                        dCfg['socket'][mTmpName][cfgLabel] = {'type':None, 'p2e':{}, 'e2p':{}}
                    if cfgElem not in dCfg['socket'][mTmpName][cfgLabel]['e2p']:
                        dCfg['socket'][mTmpName][cfgLabel]['e2p'][port]    = {'ename':cfgElem, 'width':None, 'msb':None, 'lsb':None}
                        dCfg['socket'][mTmpName][cfgLabel]['e2p'][cfgElem] = {'pname':port,    'width':None, 'msb':None, 'lsb':None}
                        if silent == 0:
                            xprint(fpLog, "Info: <module[%s]>Find socket description[%s.%s] to port[%s]"%(mName, cfgLabel, cfgElem, port))
                    else:
                        if silent == 0:
                            xprint(fpLog, "Warning: <module[%s]>Element[%s] of SocketLabel[%s] is already defined to port[%s]! <Ignore Port[%s]>"%(mName, cfgElem, cfgLabel, dCfg['socket'][mTmpName][cfgLabel]['e2p'][cfgElem]['pname'], port))
        else:
            if silent == 0:
                xprint(fpLog, "Error: Invalid port[%s] declaration in [%s]"%(port, orgStr))

    return(pLoc, inMacro)
# Function 'get_port_list' # }}}

# Function 'get_instance' # {{{
def get_instance(curStr, auto=True, fpLog=None):
    """
    case0: (A #() u_A [3:0] ...): A #(p0, p2, .P(px), ..) u_A [3:0] ( [.a (ax), .b(bx), ...] );
    case1: (A     u_A       ...): A                       u_A       ( [.a (ax), .b(bx), ...] );
    case2: (A  () u_A       ...): A (strength)            u_A       ( [.a (ax), .b(bx), ...] );
    """
    orgStr = curStr
    if re.search("#\s*\(", curStr):
        curStr = re.sub("#\s*\(", '#(', curStr)
        idx = curStr.find("#(")
        if idx > -1:
            procStr = curStr[idx+2:]
            curStr  = curStr[:idx]
            num = 1
            while num > 0 and idx > -1:
                idx = procStr.find(')')
                if idx > -1:
                    num += procStr[:idx].count('(') -1
                    procStr = procStr[idx+1:]
            curStr += procStr

    modName  = None
    instName = None
    postPart = orgStr
    obj = re_inst_fmt.search(curStr)
    if obj:
        if obj.group('mod') not in gKeyWord and obj.group('inst') not in gKeyWord:
            modName, instName, postPart = (obj.group('mod'), obj.group('inst'), obj.group('post'))
    elif auto is True:
        xprint(fpLog, "Warning: Un-supported module instance format: %s"%(orgStr))

    return(modName, instName, postPart)
# Function 'get_instance' # }}}

# Function 'get_connected_ports' # {{{
def get_connected_ports(curStrs, dPorts={}, dParam={}, fpLog=None):
    """
    dInstPorts:{
                'plen' :portMaxLen
                'llen' :wireLabelMaxLen
                'wlen' :wireSignalMaxLen
                'blen' :bitWidthMaxLen
                'port' :{portName:{'comment':Comments
                                   'line'   : Line
                                   'msb'    : msb
                                   'lsb'    : lsb
                                   'width'  : [msb:lsb]
                                   'inout'  : input/output/inout
                                   'llist'  : [wire0, wire1, ...]
                                   'wdict'  : {wName:{'width':[msb:lsb]
                                                      'msb'  :msb
                                                      'lsb'  :lsb
                                                      'used' :[]
                                                      'inout':input/output/inout
                                                     }
                                              }
                                  }
                        }
                'false':[portComment0, portComment1, ...]
               }
    """
    inComment = False
    inFunction = inTask = False
    inGenerate = inPara = False
    dInstPorts = {'plen':0, 'llen':0, 'wlen':0, 'blen':5, 'port':{}, 'false':[]}

    maxLlen = maxWlen = 0
    preStr = ''
    for curStr in curStrs:
        orgStr = curStr.strip()
        curStr, inComment, inPara, inTask, inFunction, inGenerate, offset, postComment = proc_comment( \
        curStr, inComment, inPara, inTask, inFunction, inGenerate, '')

        maxLlen, maxWlen, portList, wireList, preStr = get_port_connection(maxLlen, maxWlen, preStr+' '+curStr, dPorts, postComment, dParam, fpLog=fpLog)
        for idx, port in enumerate(portList):
            wireDict = wireList[idx]
            if wireDict:
                dInstPorts['plen'] = max(dInstPorts['plen'], len(port))
                dInstPorts['llen'] = max(dInstPorts['llen'], maxLlen)
                dInstPorts['wlen'] = max(dInstPorts['wlen'], maxWlen)
                if wireDict['width'] is not None:
                    dInstPorts['blen'] = max(dInstPorts['blen'], len(wireDict['width']))
                if port in dInstPorts['port']:
                    xprint(fpLog, "Warning: Duplicated port reference [%s] in module instance! (%s)"%(port, curStr))
                else:
                    dInstPorts['port'][port] = {}
                    if port in dPorts or len(dPorts) == 0:
                        dInstPorts['port'][port]['line'] = curStr
                        dInstPorts['port'][port]['comment'] = postComment
                        dInstPorts['port'][port].update(wireDict)
                    else:
                        dInstPorts['false'].append("        //"+orgStr)
        if re_autoarg_end.search(curStr):
            break
    return dInstPorts
# Function 'get_connected_ports' # }}}

# Function 'get_port_connection' # {{{
def get_port_connection(maxLlen, maxWlen, curStr, dPorts, comment, dParam, fpLog=None):
    """
    wireDict:{'msb'  :msb,
              'lsb'  :lsb,
              'width':[msb:lsb]
              'inout':input/output/inout
              'llist':['label0', label1, ...]
              'wdict':{ #lDict
                       wName:{'width':[msb,lsb]
                              'msb'  : msb
                              'lsb'  : lsb
                              'used' : []
                              'inout':input/output/inout
                             }
                      }
             }
    """
    # .A ( a )
    # .A ( a ) ,
    # .A ( a ),  .B ( b ),
    # .A ( a ));
    # .A ( {{(3+1){a[0]}}, a[2:0]} ),
    # .A ( {{(3+1){a[0]}},
    #       a[2:0], c,
    #       a[3:2]} ),
    portList = []
    wireList = []
    dotCnt = curStr.count('.')
    if dotCnt == 0:
        return maxLlen, maxWlen, portList, wireList, ''
    else:
        while dotCnt > 0:
            wireDict = {}
            orgStr   = curStr
            procStr  = curStr[curStr.find('.'):]

            # Change '.A (a), .B(b),' to '.A(a),' and '.B(b),'
            if dotCnt > 1:
                dot2rd  = procStr[1:].find('.')
                curStr  = procStr[dot2rd:]
                procStr = procStr[:dot2rd]

            # Change '.A (a)); xxx ' to 'A (a)'
            procStr = re.sub('\)\s*;.*', '', procStr)

            leftParOfst  = procStr.find('(')
            rightParOfst = -1
            if re.search("\)\s*,|\)\s*$", procStr):
                rightParOfst = procStr.rfind(')')

            if leftParOfst < 1 or rightParOfst < 1: #~~Case: .A (a)...
                dotCnt = 0
            else:
                if rightParOfst < leftParOfst:
                    xprint(fpLog, "Error: Invalid instance port connection: %s"%(orgStr))
                    return maxLlen, maxWlen, portList, wireList, ''

                wireDict['inout'] = None
                obj = re.search(r"//\s*(?P<inout>IO|I|O)\b", comment, re.I)
                if obj:
                    if obj.group('inout').upper() == 'I':
                        wireDict['inout'] = 'input'
                    elif obj.group('inout').upper() == 'O':
                        wireDict['inout'] = 'output'
                    else:
                        wireDict['inout'] = 'inout'

                obj = re_port_connect.search(procStr)
                if obj:
                    pName = obj.group('port')
                    wName = obj.group('wire')
                    wireDict['width'] = obj.group('width')
                    wireDict['msb'  ] = obj.group('msb')
                    wireDict['lsb'  ] = obj.group('lsb')
                    wireDict['llist'] = []
                    wireDict['wdict'] = lDict()
                    if wireDict['msb'] is not None:
                        wireDict['msb'] = re.sub("\s+", "", wireDict['msb'])
                    if wireDict['lsb'] is not None:
                        wireDict['lsb'] = re.sub("\s+", "", wireDict['lsb'])
                    else:
                        wireDict['lsb'] = wireDict['msb']

                    if pName in dPorts:
                        wireDict['inout'] = dPorts[pName]['inout']
                        #if wireDict['width'] is None:
                        if wireDict['width'] is None and dPorts[pName]['msb'] is not None and dPorts[pName]['msb'].isdigit() and dPorts[pName]['lsb'] is not None and dPorts[pName]['lsb'].isdigit():
                            wireDict['msb' ] = dPorts[pName]['msb' ]
                            wireDict['lsb' ] = dPorts[pName]['lsb' ]
                            wireDict['width'] = dPorts[pName]['width']
                    if wireDict['width'] is not None:
                        wireDict['width'] = re.sub("\s+", "", wireDict['width'])
                        maxLlen = max(maxLlen, len(wName+wireDict['width']))

                    wireDict['llist'].append(wName)
                    maxLlen = max(maxLlen, len(wName))
                    if wName.isdigit() is False:
                        wireDict['wdict'][wName] = {'msb'  : wireDict['msb'],
                                                    'lsb'  : wireDict['lsb'],
                                                    'used' : [],
                                                    'width': wireDict['width'],
                                                    'inout': wireDict['inout']}
                        if wireDict['inout'] != 'input' and wireDict['msb'] is not None and wireDict['msb'].isdigit() and wireDict['lsb'] is not None and wireDict['lsb'].isdigit():
                            wireDict['wdict'][wName]['used'] = list(range(int(wireDict['lsb']), int(wireDict['msb'])+1))
                        maxWlen = max(maxWlen, len(wName))
                else:
                    pName  = procStr[1:leftParOfst].strip()
                    wLabel = procStr[leftParOfst+1:rightParOfst].strip()
                    maxLlen, maxWlen = curly_bracket_parsing(maxLlen, maxWlen, pName, wireDict, wLabel, dParam, fpLog=fpLog)
                    if pName in dPorts:
                        wireDict['inout'] = dPorts[pName]['inout']

                if dotCnt == 1:
                    curStr = ''
                dotCnt = curStr.count('.')
                if pName in portList:
                    xprint(fpLog, "Warning: Port '%s' is duplicated! (%s)"%(pName, procStr))
                else:
                    portList.append(pName)
                    wireList.append(wireDict)

        return(maxLlen, maxWlen, portList, wireList, curStr)
# Function 'get_port_connection' # }}}

# Function 'get_module_info' # {{{
def get_module_info(mName, pathDict, cfg=False, silent=0, fpLog=None):
    modInfo = None
    if mName in pathDict['module']:
        fName = pathDict['module'][mName]
        if os.path.isfile(fName):
            modInfo = ModuleInfo(fName, mname=mName)
            modInfo.initial_port(cfg, silent, fpLog=fpLog)
    else:
        for path in pathDict['path']:
            fName = path+os.path.sep+mName
            if os.path.isfile(fName+'.v'):
                modInfo = ModuleInfo(fName+'.v', mname=mName)
                modInfo.initial_port(cfg, silent, fpLog=fpLog)
                break
            elif os.path.isfile(fName+'.sv'):
                modInfo = ModuleInfo(fName+'.sv', mname=mName)
                modInfo.initial_port(cfg, silent, fpLog=fpLog)
                break
    return modInfo
# Function 'get_module_info' # }}}

# Function 'get_instance_info' # {{{
def get_instance_info(curStrs, module=None, mFile='', dCfg={}, pathDict={}, dParam={}, cfg=False, silent=1, dMacro={}, fpLog=None):
    instDict = lDict()
    imodDict = {}
    dInfoLoc = {'smod'  :-1,
                'emod'  :-1,
                'swire' :-1,
                'ewire' :-1,
                'sarg'  :-1,
                'earg'  :-1,
                'adef'  :-1,
                'ploc'  :{},
                'iloc'  :{}}
    instMname = instIname = moduleName = None

    inParaInst = inInstance = False
    inComment  = inModule   = False
    inFunction = inTask     = False
    inGenerate = inPara     = False

    idupList  = []
    mmissList = []
    prevLines = ['', '', '', '']
    hasModule = False
    for idx, curStr in enumerate(curStrs):
        # Get auto keyword location
        if dInfoLoc['sarg'] == -1:
            if re_autoarg_begin.search(curStr):
                dInfoLoc['sarg'] = idx
                if re_autoarg_end.search( re_line_comment.sub('', curStr) ):
                    dInfoLoc['earg'] = idx
        if inModule and dInfoLoc['adef'] == -1:
            obj = re_autoport_begin.search(curStr)
            if obj:
                dInfoLoc['ploc'][obj.group('inst')] = {'begin':idx}
                continue
            obj = re_autoport_end.search(curStr)
            if obj and obj.group('inst') in dInfoLoc['ploc']:
                dInfoLoc['ploc'][obj.group('inst')]['end'] = idx
                continue
        #if inModule and dInfoLoc['swire'] == -1: ????
            if re_autodefine.search(curStr):
                dInfoLoc['adef']  = idx
                dInfoLoc['swire'] = idx
                continue
        if inModule and dInfoLoc['ewire'] == -1 and dInfoLoc['adef'] > 0:
            if re_autowire_end.search(curStr):
                dInfoLoc['ewire'] = idx
                continue

        # Filter comment
        preInPara = inPara
        curStr, inComment, inPara, inTask, inFunction, inGenerate, offset, postComment = proc_comment( \
        curStr, inComment, inPara, inTask, inFunction, inGenerate, 'autoinst')
        curStr = curStr.strip()

        if dInfoLoc['earg'] == -1 and dInfoLoc['sarg'] > -1:
            if re_autoarg_end.search(curStr):
                dInfoLoc['earg'] = idx

        if inTask or inFunction:   # or inGenerate:
            continue

        if inModule is False:  # Searching start of module
            obj = re.search(r"\bmodule\s+(?P<mname>\w+)", curStr)
            if obj:
                moduleName = obj.group('mname')
            else:
                obj = re.search(r"\bmodule\s+(?P<mname>`\S+)", curStr)
                if obj:
                    if obj.group('mname') in dMacro:
                        moduleName = dMacro[obj.group('mname')]['value']
                    else:
                        xprint(fpLog, "Error: Macro [%s] is not defined! <%s>"%(obj.group('mname'), curStr))
            if moduleName is not None and (module is None or moduleName == module):
                findMod  = True
                inModule = True
                dInfoLoc['smod'] = idx
                prevLines = ['', '', '', curStr]
        else:
            # Break from file parsing by endmodule
            if re.search(r"\bendmodule\b", curStr):
                dInfoLoc['emod'] = idx
                inModule = False
                prevLines = ['', '', '', '']
                break

            if inParaInst:
                 prevLines[-1] += ' ' + curStr
            else:
                 prevLines = prevLines[1:] + [curStr]
                 obj = re_para_inst.search(' '.join(prevLines))
                 if obj and obj.group('inst') not in gKeyWord:
                     inParaInst = True

            if inPara or preInPara:
                continue

            # Extraqct module instance in current module
            inAuto = True  if offset > 0 else False
            instLine = ' '.join(prevLines)
            semiIdx  = instLine.find(';')
            if semiIdx > -1:
                inParaInst = False

            if inInstance is False:
                instMname, instIname, postPart = get_instance(instLine, False, fpLog=fpLog)
                if instMname is None or instIname is None:
                    if semiIdx > -1:
                        prevLines = ['', '', '', instLine[semiIdx+1:]]
                else:
                    inInstance   = True
                    inParaInst   = True
                    instBeginIdx = idx

                    # Module info update
                    if instMname not in imodDict and instMname not in mmissList and len(pathDict) > 0:
                        mTmpInfo = get_module_info(instMname, pathDict, cfg, silent, fpLog=fpLog)
                        if mTmpInfo is not None:
                            imodDict[instMname] = mTmpInfo

                        if instMname not in imodDict:
                            mmissList.append(instMname)
                            xprint(fpLog, "Warning: module [%s] is not found in .v files (Line[%s], instance[%s])"%(instMname, idx, instIname))
                        elif cfg:
                            if 'socket' in imodDict[instMname].cfgInfo:
                                for imname in ('outside', instMname):
                                    if imname in imodDict[instMname].cfgInfo['socket']:
                                        if 'socket' not in dCfg:
                                            dCfg['socket'] = {}
                                        if instMname not in dCfg['socket']:
                                            dCfg['socket'][instMname] = imodDict[instMname].cfgInfo['socket'][imname]
                                        else:
                                            dCfg['socket'][instMname].update(imodDict[instMname].cfgInfo['socket'][imname])
                    # Add instance info.
                    if instIname in instDict:
                        if instIname not in idupList:
                            idupList.append(instIname)
                        #else: ???
                            xprint(fpLog, "Warning: Instance '%s' is defined more than once!"%(instIname))
                    else:
                        instDict[instIname] = {'auto'  :inAuto,
                                               'module':instMname,
                                               'plen'  :0,
                                               'llen'  :0,
                                               'wlen'  :0,
                                               'blen'  :0,
                                               'port'  :{},
                                               'false' :[]}
                    # Inline instance end flag
                    obj = re.search('(.*?)\)\s*;(.*)', postPart)
                    if obj:
                        inInstance = False
                        instEndIdx = idx
                        prePart    = obj.group(1)
                        postPart   = obj.group(2)
                        dInfoLoc['iloc'][instIname] = {'start':instBeginIdx, 'end':instEndIdx}
                        # Get port connection sucn: mname iname (.port (wire), ...);
                        portsDict = {} if instMname not in imodDict else imodDict[instMname].mPorts['dict']
                        conncDict = get_connected_ports([prePart], portsDict, dParam, fpLog=fpLog)
                        instDict[instIname].update(conncDict)
                    prevLines = ['', '', '', postPart]
            else:
                obj = re.search('\)\s*;(.*)', instLine)
                if obj:
                    inInstance = False
                    instEndIdx = idx
                    prevLines = ['', '', '', obj.group(1)]
                    dInfoLoc['iloc'][instIname] = {'start':instBeginIdx, 'end':instEndIdx}

                    portsDict = {} if instMname not in imodDict else imodDict[instMname].mPorts['dict']
                    conncDict = get_connected_ports(curStrs[instBeginIdx:instEndIdx], portsDict, dParam, fpLog=fpLog)
                    instDict[instIname].update(conncDict)

    return (moduleName, dInfoLoc, imodDict, instDict)
# Function 'get_instance_info' # }}}

# Function 'get_instance_wires' # {{{
def get_instance_wires(instDict, dParam={}, silent=0, fpLog=None):
    maxBlen   = 5
    iwireDict = {}

    for iname in instDict.lkeys:
        if 'port' not in instDict[iname]:
            continue
        for pname in instDict[iname]['port']:
            if 'wdict' not in instDict[iname]['port'][pname]:
                continue
            for wname, wdict in instDict[iname]['port'][pname]['wdict'].items():
                if wname in gKeyWord or wname in dParam:
                    continue
                if wname not in iwireDict:
                    iwireDict[wname] = copy.deepcopy(wdict)
                else:
                    if 'inout' in wdict            and wdict['inout']            and wdict['inout']            != 'input' and \
                       'inout' in iwireDict[wname] and iwireDict[wname]['inout'] and iwireDict[wname]['inout'] != 'input':
                        hasDup, bitDup = width_check(iwireDict[wname], wdict, fpLog=fpLog)
                        if hasDup and silent == 0:
                            xprint(fpLog, "Error: Multi-driven '%s%s' (in [%s]): connected to more than one instance's output!"%(wname, bitDup, iname))
                    if 'inout' in wdict:
                        if 'inout' not in iwireDict[wname]:
                            iwireDict[wname]['inout'] = wname
                        elif (wdict['inout'] == 'input'  and iwireDict[wname]['inout'] == 'output') or \
                             (wdict['inout'] == 'output' and iwireDict[wname]['inout'] == 'input' ) :
                            iwireDict[wname]['inout'] = 'inout'
                    iwireDict[wname] = wire_width_merge(iwireDict[wname], wdict, fpLog=fpLog)

                if wdict['width']:
                    maxBlen = max(maxBlen, len(wdict['width']))
    return maxBlen, iwireDict
# Function 'get_instance_wires' # }}}

# Function 'get_module_wires' # {{{
def get_module_wires(curStrs, dInfoLoc, module=None, iwireDict={}, hasPort=False, dPorts={}, dParam={}, silent=1, fpLog=None):
    """
    wireDict:{'blen':maxBitWidthLen
              'defs' :{ ... }
              'regs' :{ ... }
              'wires':{wireName:{'type' :netType
                                 'auto' :False/True
                                 'width':[msb:lsb]
                                 'msb'  :msb
                                 'lsb'  :lsb
                                 'used' :[]
                                 'name' :wireName
                                }
                      }
             }
    """
    moduleName = None
    wireDict = {'blen':5, 'defs':{}, 'regs':{}, 'wires':{}}

    inComment  = inModule = False
    inFunction = inTask   = False
    inGenerate = inPara   = False

    prePart = ''
    findMod = False
    for idx, line in enumerate(curStrs):
        # Remove comments
        preInPara = inPara
        line, inComment, inPara, inTask, inFunction, inGenerate, offset, postComment = proc_comment( \
        line, inComment, inPara, inTask, inFunction, inGenerate, '')
        line = line.strip()

        if inTask or inFunction: # or inGenerate:
            continue

        if inModule is False:  # Searching start of module
            obj = re.search(r"\bmodule\s+(?P<mname>\w+)", line)
            if obj:
                moduleName = obj.group('mname')
            else:
                obj = re.search(r"\bmodule\s+(?P<mname>`\S+)", line)
                if obj:
                    if obj.group('mname') in dMacro:
                        moduleName = dMacro[obj.group('mname')]['value']
                    else:
                        xprint(fpLog, "Error: Macro [%s] is not defined! <%s>"%(obj.group('mname'), line))
            if moduleName is not None and (module is None or moduleName == module):
                findMod  = True
                prePart  = line
                inModule = True
        else:
            if re.search(r"\bendmodule\b", line):
                inModule = False
                prePart  = ''
                break

            if inPara or preInPara:
                continue

            # Skip port-declaration lines (already parsed by initial_port);
            # otherwise `input wire clk` inside `module (...)` is mistaken for a wire decl.
            if idx <= dInfoLoc['eport']:
                continue

            prePart += ' ' + line
            semiIdx  = prePart.find(';')
            while semiIdx > -1:
                procLine = prePart[:semiIdx]
                prePart  = prePart[semiIdx+1:]

                obj = re_type_decla.search(procLine)
                if obj:  # defined signal type
                    netsAttr = {}
                    netsAttr['used' ] = []
                    netsAttr['type' ] = obj.group('type')
                    netsAttr['width'] = obj.group('width')
                    netsAttr['auto' ] = False
                    netsAttr['msb'  ] = obj.group('msb')
                    netsAttr['lsb'  ] = obj.group('lsb')
                    if  netsAttr['msb'] is not None:
                        netsAttr['msb'] = re.sub("\s+", '', netsAttr['msb'])
                    if  netsAttr['lsb'] is not None:
                        netsAttr['lsb'] = re.sub("\s+", '', netsAttr['lsb'])
                    else:
                        netsAttr['lsb'] = netsAttr['msb']
                    if  netsAttr['width'] is not None:
                        netsAttr['width'] = re.sub("\s+", '', netsAttr['width'])
                        wireDict['blen']  = max(wireDict['blen'], len(netsAttr['width']))
                    if dInfoLoc['swire'] < idx and idx < dInfoLoc['ewire']:
                        netsAttr['auto'] = True
                    if  netsAttr['msb'] is not None and netsAttr['msb'].isdigit() and netsAttr['lsb'] is not None and netsAttr['lsb'].isdigit() :
                        netsAttr['used'] = list(range(int(netsAttr['lsb']), int(netsAttr['msb'])+1))

                    orgLine  = procLine
                    procLine = obj.group('last')

                    eqIdx = procLine.find('=')
                    if eqIdx > -1:
                        procLine = procLine[:eqIdx]

                    for net in procLine.split(','):
                        net = re.sub(r"\s*(\w+)(\s*\[.*)?", r"\1", net)
                        net = net.strip()
                        if net in gKeyWord or net in dParam:
                            continue
                        if re.search(r"^\w+$", net):
                            if hasPort is True and net in dPorts:
                                if dPorts[net]['inout'] != 'output' and dPorts[net]['inout'] != 'any' and netsAttr['type'] in gRegType:
                                    if silent == 0:
                                        xprint(fpLog, "Error: Signal[%s] <type[%s]> used as [%s] port! (%s)"%(net, netsAttr['type'], dPorts[net]['inout'], orgLine))
                                elif dPorts[net]['type']:
                                    if silent == 0:
                                        xprint(fpLog, "Error: Signal[%s] <type[%s]> is already defined in port definition<type[%s]>! (%s)"%(net, netsAttr['type'], dPorts[net]['type'], orgLine))
                            netsAttr['name'] = net
                            if net not in wireDict['defs']:
                                wireDict['defs'][net] = netsAttr
                            else:
                                if wireDict['defs'][net]['auto'] is True:
                                    wireDict['defs'][net] = netsAttr
                                if silent == 0:
                                    xprint(fpLog, "Error: [%s]<%s> is already defined (type<%s>): %s"%(net, netsAttr['type'], wireDict['defs'][net]['type'], orgLine))
                        else:
                            if silent == 0:
                                xprint(fpLog, "Error: Invalid type [%s]<%s> declearation: %s"%(net, netsAttr['type'], orgLine))
                else:
                    # remove (xxx) for: if ( a <= b )
                    procLine, num = re_round.subn(' ', procLine)
                    while num > 0:
                        procLine, num = re_round.subn(' ', procLine)

                    obj = re_assign.search(procLine)
                    if obj and obj.group('wire') not in gKeyWord and obj.group('wire') not in dParam: #~~Continious assignment
                        wireName = obj.group('wire')
                        wdict = {}
                        wdict['used' ] = []
                        wdict['auto' ] = False
                        if wireName in wireDict['defs'] and wireDict['defs'][wireName]['auto'] is True:
                            wdict['auto'] = True
                        wdict['type' ] = 'wire'
                        wdict['width'] = obj.group('width')
                        wdict['msb'  ] = obj.group('msb')
                        wdict['lsb'  ] = obj.group('lsb')
                        wdict['name' ] = wireName
                        if  wdict['msb'] is not None:
                            wdict['msb'] = re.sub("\s+", '', wdict['msb'])
                        if  wdict['lsb'] is not None:
                            wdict['lsb'] = re.sub("\s+", '', wdict['lsb'])
                        else:
                            wdict['lsb'] = wdict['msb']
                        if  wdict['width'] is not None:
                            wdict['width'] = re.sub("\s+", '', wdict['width'])
                        else:  # assign expression parsing
                            assignExpr = obj.group('expr')
                            width = get_expression_width(assignExpr, iwireDict, wireDict, fpLog=fpLog)
                            if type(width) is int and width > 1:
                                wdict['msb'  ] = "%d"%(width-1)
                                wdict['lsb'  ] = "%d"%(0)
                                wdict['width'] = "[%d:%d]"%(width-1, 0)

                        if  wdict['msb'] is not None and wdict['msb'].isdigit() and wdict['lsb'] is not None and wdict['lsb'].isdigit():
                            wdict['used'] = list(range(int(wdict['lsb']), int(wdict['msb'])+1))

                        if wireName in wireDict['wires']:
                            hasDup, bitDup = width_check(wdict, wireDict['wires'][wireName], fpLog=fpLog)
                            wdict = wire_width_merge(wdict, wireDict['wires'][wireName], fpLog=fpLog)
                            if hasDup and silent == 0:
                                xprint(fpLog, "Error: Multi-driven '%s%s': assigned more than once <%s>!"%(wireName, bitDup, procLine))
                        elif wireName not in wireDict['defs']:
                            if hasPort and wireName not in dPorts and silent == 0:
                                xprint(fpLog, "Error: Signal '%s' used before referenced <%s>!"%(wireName, procLine))
                        elif wireDict['defs'][wireName]['type'] not in gNetType:
                            if silent == 0:
                                xprint(fpLog, "Error: Signal type mismatch: '%s' defined as '%s' (Should be net type such as 'wire' <%s>!"%(wireName, wireDict['defs'][wireName]['type'], procLine))
## for accurated bitwidth parsing, orginal bitwidth will be replaced
##                        else: #~~Has defined as wire type
##                            wdict = wireDict['defs'][wireName]
##                            #wdict = wire_width_merge(wdict, wireDict['defs'][wireName], fpLog=fpLog)
                        if hasPort is True and wireName in dPorts and dPorts[wireName]['inout'] == 'input':
                            if silent == 0:
                                xprint(fpLog, "Error: Multi-driven '%s': input port has been assigned! (%s)"%(wireName, procLine))

                        wireDict['wires'][wireName] = wdict
                        if  wdict['width'] is not None:
                            wireDict['blen']  = max(wireDict['blen'], len(wdict['width']))
                    else: # Blocking/Non-Blocking assignment for reg
                        #obj = re_reg_assign.search(line)
                        obj = re_reg_assign.search(procLine)
                        if obj and obj.group('reg') not in gKeyWord and obj.group('reg') not in dParam:
                            regName = obj.group('reg')
                            rdict = {}
                            rdict['used' ] = []
                            rdict['auto' ] = False
                            if regName in wireDict['defs'] and wireDict['defs'][regName]['auto'] is True:
                                rdict['auto'] = True
                            rdict['type' ] = 'reg'
                            rdict['width'] = obj.group('width')
                            rdict['msb'  ] = obj.group('msb')
                            rdict['lsb'  ] = obj.group('lsb')
                            rdict['name' ] = regName #TODO
                            if  rdict['msb'] is not None:
                                rdict['msb'] = re.sub("\s+", '', rdict['msb'])
                            if  rdict['lsb'] is not None:
                                rdict['lsb'] = re.sub("\s+", '', rdict['lsb'])
                            else:
                                rdict['lsb'] = rdict['msb']
                            if  rdict['width'] is not None:
                                rdict['width'] = re.sub("\s+", '', rdict['width'])
                            else:  # assign expression parsing
                                assignExpr = obj.group('expr')
                                width = get_expression_width(assignExpr, iwireDict, wireDict, fpLog=fpLog)
                                if type(width) is int and width > 1:
                                    rdict['msb'  ] = "%d"%(width-1)
                                    rdict['lsb'  ] = "%d"%(0)
                                    rdict['width'] = "[%d:%d]"%(width-1, 0)

                            if  rdict['msb'] is not None and rdict['msb'].isdigit() and rdict['lsb'] is not None and rdict['lsb'].isdigit():
                                rdict['used'] = list(range(int(rdict['lsb']), int(rdict['msb'])+1))

                            if regName in wireDict['regs']:
                                hasDup, bitDup = width_check(rdict, wireDict['regs'][regName], fpLog=fpLog)
                                if hasDup is False:
                                    rdict = wire_width_merge(rdict, wireDict['regs'][regName], fpLog=fpLog)
                                else:
                                    rdict = wireDict['regs'][regName]
                            elif regName not in wireDict['regs']:
                                if hasPort is True and silent == 0:
                                    if regName not in dPorts:
                                        xprint(fpLog, "Error: Signal '%s' used before referenced <%s>!"%(regName, procLine))
                                    elif dPorts[regName]['inout'] not in ['output', 'any']:
                                        xprint(fpLog, "Error: Signal '%s' (reg type) used as [%s] port! <%s>!"%(regName, dPorts[regName]['inout'], procLine))
                            elif wireDict['defs'][regName]['type'] not in gRegType:
                                if silent == 0:
                                    xprint(fpLog, "Error: Signal type mismatch: '%s' defined as '%s' (Should be 'reg' <%s>)!"%(regName, wireDict['defs'][regName]['type'], procLine))
## for accurated bitwidth parsing, orginal bitwidth will be replaced
##                            else: #~~Has defined as reg type
##                                rdict = wireDict['defs'][regName]
##                                #rdict = wire_width_merge(rdict, wireDict['defs'][regName], fpLog=fpLog)
                            if hasPort is True and regName in dPorts and dPorts[regName]['inout'] == 'input':
                                if silent == 0:
                                    xprint(fpLog, "Error: Multi-driven '%s': input port has been assigned! (%s)"%(regName, procLine))

                            wireDict['regs'][regName] = rdict
                            if  rdict['width'] is not None:
                                wireDict['blen']  = max(wireDict['blen'], len(rdict['width']))
                semiIdx = prePart.find(';')
            ####else:
            ####    if re_type_pfix.search(prePart) or re_assign.search(prePart) or re_proc_pfix.search(prePart):
            ####        pass
            ####    else:
            ####        prePart = ''
    return moduleName, wireDict
# Function 'get_module_wires' # }}}

# Function 'macro_process_flow' # {{{
def macro_process_flow(objImod, objMod, iname, blankCell, leadJust, mode='inst', dInstPorts={}, dCfg={}, fpLog=None):
    """
    Instanted module port processing:
     autoarg  : mode argv
     autoinst : mode port (input/output port declaration of new module instance)
     autoinst : mode inst (module instance by default)
    """
    lInstLine = []
    leadSteps = 1

    xmode   = mode
    maxPlen = maxLlen = maxWlen = 0
    maxBlen = objImod.mPorts['blen']
    if mode == 'inst':
        maxPlen = max(objImod.mPorts['plen'], objMod.mInst[iname]['plen'])
        #maxLlen = max(objImod.mPorts['llen'], objMod.mInst[iname]['llen'])
        maxLlen = objMod.mInst[iname]['llen']
        if len(dCfg.keys()) > 0:
            wmax = max(maxWlen, dCfg[dCfg.keys()[0]]['wmax'])
            bmax = max(maxBlen, dCfg[dCfg.keys()[0]]['bmax'])
            maxLlen = max(maxLlen, wmax+bmax)
    elif mode in ['iarg', 'oarg', 'xarg']:
        mode = 'argv'
    else:
        maxPlen = max(objImod.mPorts['plen'], objMod.mInst[iname]['plen'])
        maxWlen = max(objImod.mPorts['wlen'], objMod.mInst[iname]['wlen'])
        if len(dCfg.keys()) > 0:
            maxWlen = max(maxWlen, dCfg[dCfg.keys()[0]]['wmax'])

    dInstPorts['plen'] = maxPlen
    dInstPorts['wlen'] = maxWlen
    dInstPorts['blen'] = maxBlen
    dInstPorts['llen'] = maxLlen
    #macros = {'list':[macLev0, macLev1, ...]
    #          'dict':{macLevX:{'time':1/2
    #                           'pole':True/False
    #                          }
    #                 }
    #         }

    realMaxLlen  = 0
    newConnect   = -1
    lineMaxWidth = 70
    validLine    = False
    dMacros      = lDict()
    for p in objImod.mPorts['list']:
        if mode == 'argv':
            if   objImod.mPorts['dict'][p]['inout'] == 'input':
                if xmode != 'iarg':
                    continue
            elif objImod.mPorts['dict'][p]['inout'] == 'output':
                if xmode != 'oarg':
                    continue
            else:
                if xmode != 'xarg':
                    continue
        
        newLines   = []
        dPortMacro = lDict()
        if objImod.mPorts['dict'][p]['macro']: # Get port macro definition
            dPortMacro = copy.deepcopy(objImod.mPorts['dict'][p]['macro'])

        inLine = True
        # Currnet macro alignment with port macro
        # ~~ current macri list deeper than port macro
        #while len(dMacros) > len(dPortMacro) or (len(dMacros) > 0 and dMacros.lkeys != dPortMacro.lkeys[:len(dMacros)]):
        while len(dMacros) > len(dPortMacro):
            steps = len(dMacros)
            if mode not in ['argv', 'inst']:
                steps = steps**leadJust -1
            else:
                steps = steps**leadJust
            inLine = False
            lInstLine.append("%s`endif  //`endif %s"%(blankCell*steps, dMacros.lkeys[-1]))
            dMacros.pop(dMacros.lkeys[-1])
        # ~~ find the same parant point of current macro list and port macro
        while len(dMacros) > 0 and dMacros.lkeys != dPortMacro.lkeys[:len(dMacros)]:
            steps = len(dMacros)
            if mode not in ['argv', 'inst']:
                steps = steps**leadJust -1
            else:
                steps = steps**leadJust
            inLine = False
            lInstLine.append("%s`endif  //`endif %s"%(blankCell*steps, dMacros.lkeys[-1]))
            dMacros.pop(dMacros.lkeys[-1])

        # After alignment, macro pole check
        # ~~ current macro is not empty and macro pole non-eq
        if len(dMacros) > 0 and dMacros[dMacros.lkeys[-1]]['pole'] != dPortMacro[dMacros.lkeys[-1]]:
            curMacro = dMacros.lkeys[-1]
            steps = len(dMacros)-1
            if mode not in ['argv', 'inst'] and steps > 0:
                steps = steps**leadJust - 1
            else:
                steps = steps**leadJust

            inLine = False
            dMacros[curMacro]['pole'] = dPortMacro[curMacro]
            if dMacros[curMacro]['time'] == 1:
                lInstLine.append("%s`else  //`else %s"%(blankCell*steps, curMacro))
                dMacros[curMacro]['time'] = 2
            else: # dMacros[curMacro]['time']
                lInstLine.append("%s`endif  //`endif %s"%(blankCell*steps, curMacro))
                if dMacros[curMacro]['pole']:
                    lInstLine.append("%s`ifdef %s"%(blankCell*steps, curMacro))
                else:
                    lInstLine.append("%s`ifndef %s"%(blankCell*steps, curMacro))
                dMacros[curMacro]['time'] = 1
        # Reach to leaf of port macro if deeper than current macro
        for midx in range(len(dMacros), len(dPortMacro), 1):
            steps = len(dMacros)
            if mode not in ['argv', 'inst'] and steps > 0:
                steps = steps**leadJust - 1
            else:
                steps = steps**leadJust

            inLine = False
            if dPortMacro[dPortMacro.lkeys[midx]]: # Macro: True
                lInstLine.append("%s`ifdef %s" %(blankCell*steps, dPortMacro.lkeys[midx]))
            else: # Macro: False
                lInstLine.append("%s`ifndef %s"%(blankCell*steps, dPortMacro.lkeys[midx]))

            dMacros[dPortMacro.lkeys[midx]] = {'time':1, 'pole':dPortMacro[dPortMacro.lkeys[midx]]}
        # Add port content
        leadSteps = 2+len(dMacros)
        if mode == 'argv':
            #newLines = ["%s%s,"%(blankCell*(leadSteps**leadJust), p)]
            if inLine and len(lInstLine) > 0 and len(lInstLine[-1]+p) < lineMaxWidth:
                lInstLine[-1] += " %s,"%p
            else:
                newLines = ["%s%s,"%(blankCell*(leadSteps**leadJust), p)]
        elif mode == 'inst':
            (newConnect, newLines, realLlen) = add_port_connection(p, newConnect, objImod, objMod, iname, dInstPorts, dCfg, \
                                                                   blankCell, leadSteps**leadJust, maxPlen, maxLlen, fpLog=fpLog)
            realMaxLlen = max(realMaxLlen, realLlen)
        else: #mode == 'port'
            if mode != 'uport' or iname not in objImod.mPorts['dict'][p]['isnew'] or objImod.mPorts['dict'][p]['isnew'][iname]:
                newLines = add_port_declaration(p, objImod, objMod, iname, dInstPorts, dCfg, blankCell, leadSteps**leadJust-1, maxBlen, maxWlen, mode, fpLog=fpLog)

        lInstLine.extend(newLines)
        if validLine is False and len(newLines) > 0:
            validLine = True

    if validLine is False:
        lInstLine = []
    elif len(lInstLine) > 0:
        if mode == 'inst':
            for i in range(len(lInstLine)):
                if ',.' in lInstLine[i]:
                    lInstLine[i] = lInstLine[i].replace(",.", " .")
                    break
        if len(dMacros) == 0:
            pass
            ### Delete the comma of last line
            ##if mode == 'inst':
            ##    comaIdx = lInstLine[-1].rfind(',')
            ##    lInstLine[-1] = lInstLine[-1][:comaIdx]+' '+lInstLine[-1][comaIdx+1:]
        else: 
           # Close the macro define
            while dMacros:
                steps = len(dMacros)
                if mode not in ['argv', 'inst']:
                    steps = steps**leadJust-1
                else:
                    steps = steps**leadJust
                lInstLine.append("%s`endif  //`endif %s"%(blankCell*steps, dMacros.lkeys[-1]))
                dMacros.pop(dMacros.lkeys[-1])
            ### Delete the comma of last line with macro define
            ###            .p     ( w     ), //I
            ###`ifdef A0
            ###            .p01   ( w01   )  //I
            ###  `ifdef A1
            ###           ,.p11   ( w11   ), //I
            ###     `ifdef A2
            ###            .p21   ( w21   ), //I
            ###     `else
            ###            .p21   ( w21   ), //I
            ###     `endif
            ###            .p22   ( w22   )  //I
            ###  `else
            ###           ,.p10   ( w10   )  //I
            ###     `ifdef A3
            ###           ,.p31   ({w31,
            ###                     w32,
            ###                     w33}  )  //I
            ###     `endif
            ###     `ifdef A2
            ###           ,.p21   ( w21   )  //I
            ###     `endif
            ###   `endif
            ###`endif
            ###);
            ##if mode == 'inst':
            ##    maxIdx = -1
            ##    # ~~ searching back to delete last comma in macro block
            ##    depth = 0
            ##    pole  = [0]
            ##    bound = [[1,1]]
            ##    for idx in range(-1, -1*len(lInstLine)-1, -1):
            ##        # Filter comments
            ##        if re_comment.search(lInstLine[idx]):
            ##            continue
            ##        # Check `ifdef, `ifndef, `else, `endif depth and boundary
            ##        obj = re_macro_def.search(lInstLine[idx])
            ##        if obj is None:
            ##            if bound[depth][pole[depth]] == 1:
            ##                # ~~ delete line's comma at boundary
            ##                comaIdx = lInstLine[idx].rfind('),')
            ##                if comaIdx >= 0:
            ##                    lInstLine[idx] = lInstLine[idx][:comaIdx+1]+' '+lInstLine[idx][comaIdx+2:]
            ##                bound[depth][pole[depth]] = 0
            ##            # complete if macro define depth is 0
            ##            if depth == 0:
            ##                maxIdx = idx
            ##                break
            ##        elif obj.group('def') == 'endif':
            ##            pole.append(0)
            ##            bound.append([bound[depth][pole[depth]], bound[depth][pole[depth]]])
            ##            depth += 1
            ##        elif obj.group('def') == 'else':
            ##            pole[depth] = pole[depth] ^ 1
            ##        elif obj.group('def') == 'ifdef' or obj.group('def') == 'ifndef':
            ##            pole.pop()
            ##            bound.pop()
            ##            depth -= 1
            ##    # ~~ Search forward to add comma at the beginning of macro block
            ##    addComa = 1
            ##    for idx in range(maxIdx+1, 0, 1):
            ##        # Filter comments
            ##        if re_comment.search(lInstLine[idx]):
            ##            continue
            ##        if addComa == 1:
            ##            # ~~ add coma into the begin of line at boundary
            ##            comaIdx = lInstLine[idx].find(' .')
            ##            if comaIdx >= 0:
            ##                lInstLine[idx] = lInstLine[idx][:comaIdx]+','+lInstLine[idx][comaIdx+1:]
            ##                addComa = 0
            ##        if re_inst_bound.search(lInstLine[idx]):
            ##            addComa = 1
        # Add the end comment
        if mode == 'inst' and newConnect == 1:
            newConnect = 0
            lInstLine.append("    %s%s"%(blankCell, str_autoports_begin))

    return(lInstLine, realMaxLlen)
# Function 'macro_process_flow' # }}}

# Function 'add_port_declaration' # {{{
def add_port_declaration(port, objImod, objMod, iname, dInstPorts, dCfg, blankCell, leadSteps, maxBlen, maxWlen, mode, fpLog=None):
    newWidth = ''
    newLines = []
    wireList = [port]

    portAttr = objImod.mPorts['dict'][port]
    dIports  = objMod.mInst[iname]
    dMports  = objMod.mPorts
    dIwires  = objMod.mWires['iwire']

    if 'port' in dIports and port in dIports['port']:
        for iwire in dIports['port'][port]['wdict'].lkeys:
            #print("dInstPorts: ", dInstPorts)
            #print("dIwires   : ", dIwires)
            if iwire in dInstPorts or iwire not in dIwires:
                continue
            if iwire in dMports and (mode in ['aport', 'uport'] or (dMports[iwire]['auto'] is not None and dMports[iwire]['auto'] != iname)):
                continue
            if mode in ['port', 'aport', 'uport'] or (port in dCfg and dCfg[port]['port'] is True):
                if dIwires[iwire]['width'] is not None:
                    newWidth = dIwires[iwire]['width']
                wireIio = 'input' if dIwires[iwire]['inout'] == 'input' else 'output'
                newLines.append("%s%s %s %s ;"%(blankCell*leadSteps, wireIio.ljust(6), newWidth.ljust(maxBlen), iwire.ljust(maxWlen)))
                # ~~ update port info.
                dInstPorts[iwire] = dIwires[iwire]
                dInstPorts[iwire]['type'] = None
                dInstPorts[iwire]['auto'] = iname
                dInstPorts[iwire]['name'] = iwire
                dInstPorts[iwire]['macro'] = portAttr['macro']

    return newLines
# Function 'add_port_declaration' # }}}

# Function 'add_port_connection' # {{{
def add_port_connection(port, newConnect, objImod, objMod, iname, dInstPorts, dCfg, blankCell, leadSteps, maxPlen, maxLlen, fpLog=None):
    comment    = ''
    newComment = ''
    newLines   = []
    xBlen      = min(dInstPorts['blen'], 20)
    curConnect = newConnect
    blankLead  = blankCell*leadSteps
    blankComm  = blankLead
    if len(blankComm) > 1:
        blankComm = blankComm[1:-1]

    portAttr = objImod.mPorts['dict'][port]
    dIports  = objMod.mInst[iname]

    if portAttr['inout'] == 'input':
        newComment = "%s//I  %s %s"%(blankCell, (portAttr['width'] if portAttr['width'] else "").ljust(xBlen), iname)
    elif portAttr['inout'] == 'output':
        newComment = "%s//O  %s %s"%(blankCell, (portAttr['width'] if portAttr['width'] else "").ljust(xBlen), iname)
    else:
        newComment = "%s//IO %s %s"%(blankCell, (portAttr['width'] if portAttr['width'] else "").ljust(xBlen), iname)

    ignorePort = False
    ignoreFile = os.path.splitext(objImod.mFile)[0]+gIgnorePortListFile
    if 'ignore' in portAttr:
        ignorePort = portAttr['ignore']

    if iname not in objImod.mPorts['dict'][port]['isnew']:
        objImod.mPorts['dict'][port]['isnew'][iname] = True
    objImod.mPorts['dict'][port]['isnew'][iname] = False if port in dIports['port'] else True
    if port in dIports['port']:
        if newConnect == 1:
            curConnect = 0
            newLines.append("    %s%s"%(blankCell, str_autoports_end))
    elif newConnect != 1:
        curConnect = 1
        newLines.append("    %s%s"%(blankCell, str_autoports_begin))

    realLlen = 0
    iWlen, iLlen = (len(port), 0)
    if ignorePort is False:
        # dInstPorts for update instance connection wire info
        dInstPorts['port'][port] = {'inout':portAttr['inout'],
                                    'width':portAttr['width'],
                                    'msb'  :portAttr['msb'  ],
                                    'lsb'  :portAttr['lsb'  ],
                                    'llist':[port],
                                    'wdict':lDict()}
        dInstPorts['port'][port]['wdict'][port] = {'msb'   :portAttr['msb'],
                                                   'lsb'   :portAttr['lsb'],
                                                   'used'  :[],
                                                   'width' :portAttr['width'],
                                                   'inout' :portAttr['inout']}

        if portAttr['msb'] is not None and portAttr['msb'].isdigit() and portAttr['lsb'] is not None and portAttr['lsb'].isdigit():
            dInstPorts['port'][port]['wdict'][port]['used'] = list(range(int(portAttr['msb']), int(portAttr['lsb'])+1))

        newLabel = [port]
        if portAttr['width']:
            newLabel = [port+portAttr['width']]
            dInstPorts['blen'] = max(dInstPorts['blen'], len(portAttr['width']))
        dInstPorts['plen'] = max(dInstPorts['plen'], len(port))

        if (port in dCfg and len(dCfg['port']['name']) > 0) or port in dIports['port']:
            llist = []
            comment = ''
            msb = lsb = None
            if port in dIports['port']:
                msb    = str(dIports['port'][port]['msb'])
                lsb    = str(dIports['port'][port]['lsb'])
                llist  = dIports['port'][port]['llist']
                comment= dIports['port'][port]['comment']
            if len(llist) < 2 and port in dCfg and len(dCfg[port]['name']) > 0:
                llist = [dCfg[port]['name']]
                if dCfg[port]['msb'] is not None:
                    msb = str(dCfg[port]['msb'])
                    lsb = str(dCfg[port]['lsb'])

            vldComment = re.sub('^\s*//\s*[ioIO]+\s*?(.* %s)?\s*'%iname, '', comment)
            if len(llist) > 0: #~~for '.A ( ... )
                if len(llist) > 1 or llist[0].find('{') >= 0: # ~~ for '.A( {w0, w1, ...} )'
                    pass
                    #newLines.append("    %s//,.%s ( %s )%s"%(blankComm, port.ljust(maxPlen), newLines[0].ljust(maxLlen), newComment+' **')
                elif portAttr['msb'] is None and portAttr['lsb'] is None: # ~~ port has no [H:L]
                    widthEq = True
                    if msb is None and lsb is None:
                        obj = re.search("^\s*(\d+)?'[bohdBOHD]", llist[-1]) # ~~ for ".A (1'b1)", ".A ('b1)"
                        if obj:
                            wireWidth = obj.group(1)
                            if wireWidth and int(wireWidth) != 1:
                                widthEq = False
                    elif msb is None or lsb is None or msb != lsb:
                        widthEq = False
                    if widthEq is False:
                        newLines.append("    %s//,.%s ( %s )%s"%(blankComm, port.ljust(maxPlen), newLabel[0].ljust(maxLlen), newComment+' **'))
                        realLlen = max(realLlen, len(newLabel[0]))
                elif portAttr['msb'] is not None and portAttr['lsb'] is not None: # ~~ port [H:L]
                    widthEq = True
                    if msb is not None and lsb is not None:
                        if portAttr['msb'].isdigit() and portAttr['lsb'].isdigit() and msb.isdigit() and lsb.isdigit():
                            if int(msb)-int(lsb)+1 != int(portAttr['msb'])-int(portAttr['lsb'])+1:
                                widthEq = False
                    elif msb is None and lsb is None and portAttr['msb'] != portAttr['lsb'] and portAttr['msb'].isdigit() and portAttr['lsb'].isdigit():
                        portWidth = int(portAttr['msb'])-int(portAttr['lsb'])+1
                        wireWidth = None
                        obj = re.search("^\s*(\d+)?'[bohdBOHD]", llist[-1])
                        if obj: # ~~ for ".A (4'b0)" or ".A(.'h0)"
                            wireWidth = obj.group(1)
                        if wireWidth is not None and portWidth != int(wireWidth):
                            widthEq = False

                    if widthEq is False:
                        newLines.append("    %s//,.%s ( %s )%s"%(blankComm, port.ljust(maxPlen), newLabel[0].ljust(maxLlen), newComment+' **'))
                        realLlen = max(realLlen, len(newLabel[0]))
                elif (msb is not None and portAttr['msb'] is None) or (msb is None and portAttr['msb'] is not None) or \
                     (lsb is not None and portAttr['lsb'] is None) or (lsb is None and portAttr['lsb'] is not None) : # ~~ wire is [msb/x:x/lsb] port is [x/H:L/x]
                    newLines.append("    %s//,.%s ( %s )%s"%(blankComm, port.ljust(maxPlen), newLabel[0].ljust(maxLlen), newComment+' **'))
                    realLlen = max(realLlen, len(newLabel[0]))
                if len(llist) < 2 and port in dCfg and len(dCfg[port]['name']) > 0:
                    iWlen = len(dCfg[port]['name'])
                    dInstPorts['port'][port]['wdict'][dCfg[port]['name']] = {'inout':portAttr['inout']}
                    if dCfg[port]['width']:
                        newLabel = [dCfg[port]['name']+dCfg[port]['width']]
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['msb'  ] = dCfg[port]['msb']
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['lsb'  ] = dCfg[port]['lsb']
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['width'] = dCfg[port]['width']
                    elif portAttr['width']:
                        newLabel = [dCfg[port]['name']+portAttr['width']]
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['msb'  ] = portAttr['msb']
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['lsb'  ] = portAttr['lsb']
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['width'] = portAttr['width']
                    else:
                        newLabel = [dCfg[port]['name']]
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['msb'  ] = None
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['lsb'  ] = None
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['width'] = None
                    xmsb = dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['msb']
                    xlsb = dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['lsb']
                    if xmsb and xmsb.isdigit() and xlsb and xlsb.isdigit():
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['used'] = list(range(int(xlsb), int(xmsb)+1))
                    else:
                        dInstPorts['port'][port]['wdict'][dCfg[port]['name']]['used'] = []
                elif dIports['port'][port]['width'] is not None and re.search("^\w+$", llist[-1]):
                    iWlen = 0
                    for iwname in dIports['port'][port]['wdict']:
                        iWlen = max(iWlen, len(iwname))
                    newLabel = [llist[-1]+dIports['port'][port]['width']]
                    dInstPorts['port'][port]['wdict'] = dIports['port'][port]['wdict']
                    for iwire in dInstPorts['port'][port]['wdict']:
                        dInstPorts['port'][port]['wdict'][iwire]['inout'] = portAttr['inout']
                else:
                    iWlen = 0
                    for iwname in dIports['port'][port]['wdict']:
                        iWlen = max(iWlen, len(iwname))
                    newLabel = llist
                    dInstPorts['port'][port]['wdict'] = dIports['port'][port]['wdict']
                    for iwire in dInstPorts['port'][port]['wdict']:
                        dInstPorts['port'][port]['wdict'][iwire]['inout'] = portAttr['inout']
                newComment += blankCell+vldComment
            else: # ~~ for '.A (   )'
                # newLines.append("    %s//,.%s ( %s )%s"%(blankComm, port.ljust(maxPlen), newLabel[0].ljust(maxLlen), newComment+' **'))
                newComment += blankCell+vldComment
                newLabel = ['']
                # dInstPorts['port'][port] = {'llist':[], 'wdict':lDict()}

    instLine = ''
    if ignorePort is True:
        newComment = newComment+blankCell+'Set Ignore in '+ignoreFile
        instLine   = "    %s//,.%s ( %s )%s"%(blankComm, port.ljust(maxPlen), "*Ignored Port*".ljust(maxLlen), newComment)
        newLines.append(instLine)
    elif len(newLabel) > 1:
        iLlen = len(newLabel[0])
        newLines.append("    %s,.%s ({%s"%(blankLead, port.ljust(maxPlen), (newLabel[0]+',').ljust(maxLlen)))
        realLlen = max(realLlen, len(newLabel[0]))
        newLabel.pop(0)
        while len(newLabel) > 1:
            iLlen = max(iLlen, len(newLabel[0]))
            newLines.append("    %s %s   %s"%(blankLead, ' '.ljust(maxPlen), (newLabel[0]+',').ljust(maxLlen)))
            realLlen = max(realLlen, len(newLabel[0]))
            newLabel.pop(0)
        iLlen = max(iLlen, len(newLabel[0]))
        instLine = "    %s %s   %s})%s"%(blankLead, ' '.ljust(maxPlen), newLabel[0].ljust(maxLlen), newComment)
        realLlen = max(realLlen, len(newLabel[0]))
        newLines.append(instLine)
    else:
        iLlen = max(iLlen, len(newLabel[0]))
        instLine = "    %s,.%s ( %s )%s"%(blankLead, port.ljust(maxPlen), newLabel[0].ljust(maxLlen), newComment)
        realLlen = max(realLlen, len(newLabel[0]))
        newLines.append(instLine)

    if ignorePort is False:
        dInstPorts['llen'] = max(dInstPorts['llen'], iLlen)
        dInstPorts['wlen'] = max(dInstPorts['wlen'], iWlen)
        dInstPorts['port'][port]['llist']   = newLabel
        dInstPorts['port'][port]['line']    = instLine
        dInstPorts['port'][port]['comment'] = newComment

    return curConnect, newLines, realLlen
# Function 'add_port_connection' # }}}

# Function 'get_expression_width' # {{{
def get_expression_width(expr, iwireDict={}, wireDict={}, fpLog=None):
    width = None

    #---------------------------------------
    # Only for: a = b; or a = 4'b0;
    if re.search("^\s*(\w+(\[[^\]]+\]){0,1}|\d?'(b[01]+|o[0-7]+|d[0-9]+|h[0-9a-f]+))\s*$", expr, re.I):
        return width
    #---------------------------------------

    # Resolve conditional expr: 'a ? b : c' or '(...) ? b : c' to 'b : c'
    expr = re_conditional.sub(' ', expr)
    # Resolve reduction expr: ^a, ^~a, ~^a, &a, ~&a, |a, ~|a
    expr = re_redunction.sub('\1', expr)

    # Get width of constant sub as: 3'b0
    obj = re_constant.search(expr)
    while obj:
        if obj.group(1).strip() != '': ## obj.group('size') != '': ???
            if width is None:
                width = int(obj.group('size'))
            else:
                width = max(width, int(obj.group('size')))
        expr = re_constant.sub(' ', expr, 1)
        obj = re_constant.search(expr)

    # Get width of signal as: a[1:0]
    obj = re_signal.search(expr)
    while obj:
        signal, msb, lsb = (obj.group('wire'), obj.group('msb'), obj.group('lsb'))
        if msb is None and lsb is None:
            if signal in iwireDict:
                msb, lsb = (iwireDict[signal]['msb'], iwireDict[signal]['lsb'])
            elif 'defs'  in wireDict and signal in wireDict['defs']:
                msb, lsb = (wireDict['defs'][signal]['msb'], wireDict['defs'][signal]['lsb'])
            elif 'regs'  in wireDict and signal in wireDict['regs']:
                msb, lsb = (wireDict['regs'][signal]['msb'], wireDict['regs'][signal]['lsb'])
            elif 'wires' in wireDict and signal in wireDict['wires']:
                msb, lsb = (wireDict['wires'][signal]['msb'], wireDict['wires'][signal]['lsb'])
        elif msb is not None and msb.isdigit() and lsb is not None and lsb.isdigit():
            if width is None:
                width = int(msb)-int(lsb)+1
            else:
                width = max(width, int(msb)-int(lsb)+1)

        expr = re_signal.sub(' ', expr, 1)
        obj = re_signal.search(expr)

    return width
# Function 'get_expression_width' # }}}

# Function 'curly_bracket_parsing' # {{{
def curly_bracket_parsing(maxLlen, maxWlen, pName, wireDict, wLabel, dParam, fpLog=None):
    """
    '{{(3+1){a[0]}}, b, 1'b0, c}' parsing:
    'wlist':['a', 'b', 'c']
    'llist':['{{(3+1){a[0]}}', 'b', "1'b0", 'c']
    """
    wireDict['msb'  ] = None
    wireDict['lsb'  ] = None
    wireDict['width'] = None
    wireDict['llist'] = []
    wireDict['wdict'] = lDict()
    if wLabel.count('{') == 0 or wLabel.count('{') != wLabel.count('}'):
        if len(wLabel) > 0:
            wireDict['llist'].append(wLabel)
            maxLlen = max(maxLlen, len(wLabel))
            obj = re.search("(?P<width>\d+)'[bohdBOHD]", wLabel)
            if obj:
                width = int(obj.group('width'))
                if width > 1:
                    wireDict['msb']   = "%d"%(width-1)
                    wireDict['lsb']   = 0
                    wireDict['width'] = "[%s:0]"%(wireDict['msb'])
                if wireDict['inout'] is not None and wireDict['inout'] == 'output':
                    xprint(fpLog, "Error: Instantiated output [%s] connected to constant <%s>!"%(pName, wLabel))
        return maxLlen, maxWlen
    oLabel = nLabel = wLabel = re.sub('\s+', '', wLabel)

    # Get wList = ['{{(3+1){a[0]}}', 'b', "1'b0", 'c']
    wLabel = wLabel[wLabel.find('{')+1:wLabel.rfind('}')]
    commaIdx = wLabel.find(',')
    while commaIdx > 0:
        if wLabel[:commaIdx].count('{') != wLabel[:commaIdx].count('}'):
            commaIdx += 1 + wLabel[commaIdx+1:].find(',')
        else:
            wireDict['llist'].append(wLabel[:commaIdx])
            maxLlen = max(maxLlen, len(wLabel[:commaIdx]))
            wLabel  = wLabel[commaIdx+1:]
            commaIdx = wLabel.find(',')
    if '{' in wLabel:
        wLabel = "{%s}"%(wLabel)

    if len(wLabel) > 0:
        wireDict['llist'].append(wLabel)
        maxLlen = max(maxLlen, len(wLabel))

    # Remove x(xx)
    nLabel, num = re_round.subn(' ', nLabel)
    while num > 0:
        nLabel, num = re_round.subn(' ', nLabel)

    # Remove x'bx
    #nLabel, num = re.subn("{[`\w\d]+{[`\w\d]+'[bohdBOHD][`\w\d]+}}", ' ', nLabel)
    nLabel, num = re.subn("[`\w\d]+'[bohdBOHD][`\w\d]+", ' ', nLabel)
    if num > 0 and wireDict['inout'] is not None and wireDict['inout'] == 'output':
        xprint(fpLog, "Error: Instantiated output [%s] connected to constant <%s>!"%(pName, oLabel))

    # Parsing {xxx}
    labList = re_curly.findall(nLabel)
    while labList:
        for label in labList:
            obj = re_signal.search(label)
            while obj:
                wire, msb, lsb = (obj.group('wire'), obj.group('msb'), obj.group('lsb'))
                if wire.isdigit() is False and wire not in gKeyWord and wire not in dParam:
                    lsb   = msb  if lsb is None else lsb
                    width = None if msb is None else '[%s:%s]'%(msb, lsb)
                    wdict = {'width':width,
                             'msb'  :msb,
                             'lsb'  :lsb,
                             'used' :[],
                             'inout':wireDict['inout']}
                    if msb is not None and msb.isdigit() and lsb.isdigit():
                        wdict['used'] = list(range(int(lsb), int(msb)+1))
                    if wire not in wireDict['wdict']:
                        wireDict['wdict'][wire] = wdict
                        maxWlen = max(maxWlen, len(wire))
                    else:
                        wireDict['wdict'][wire] = wire_width_merge(wdict, wireDict['wdict'][wire], fpLog=fpLog)
                label = re_signal.sub(' ', label, 1)
                obj   = re_signal.search(label)
        nLabel = re_curly.sub(' ', nLabel)
        labList = re_curly.findall(nLabel)
    wireDict['msb'  ] = None
    wireDict['lsb'  ] = None
    wireDict['width'] = None
    return maxLlen, maxWlen
# Function 'curly_bracket_parsing' # }}}

# Function 'wire_width_merge' # {{{
def wire_width_merge(mdict, sdict, fpLog=None):
    """
    mdict <= sdict:
    1. Select the one as 'width' attribute if only one has attribute
    2. Find the Hmax and Lmin as new 'width' attribute
    """
    if   mdict['width'] is not None and sdict['width'] is None:
        return mdict
    elif mdict['width'] is None and sdict['width'] is not None:
        return copy.deepcopy(sdict)
    else:
        xdict = mdict
        if 'used' in xdict and 'used' in sdict:
            for bit in sdict['used']:
                if bit not in xdict['used']:
                    xdict['used'].append(bit)
            xdict['used'].sort()

        try:
            hm = int(xdict['msb'])
        except:
            hm = None
        try:
            hs = int(sdict['msb'])
        except:
            hs = None
        try:
            lm = int(xdict['lsb'])
        except:
            lm = None
        try:
            ls = int(sdict['lsb'])
        except:
            ls = None

        msb = None if hm is None or hs is None else max(hm, hs)
        lsb = None if lm is None or ls is None else min(lm, ls)
            
        if msb is not None:
            xdict['msb'] = msb
        if lsb is not None:
            xdict['lsb'] = lsb
        if msb is None and lsb is None:
            pass
        elif lsb is None:
            lsb = xdict['lsb']
            xdict['width'] = "[%d:%s]"%(msb, lsb)
        elif msb is None:
            msb = xdict['msb']
            xdict['width'] = "[%s:%d]"%(msb, lsb)
        else:
            xdict['width'] = "[%d:%d]"%(msb, lsb)

        if 'inout' in sdict and sdict['inout'] == 'any':
            xdict['inout'] = 'any'

        return xdict
# Function 'wire_width_merge' # }}}

# Function 'width_check' # {{{
def width_check(dict0, dict1, fpLog=None):
    bitDup = ''
    hasDup = False
    if 'used' in dict0 and 'used' in dict1:
        bdupList = []
        for bit in dict1['used']:
            if bit in dict0['used']:
                bdupList.append(bit)

        if len(bdupList) > 0:
            hasDup = True
            bdupList.sort()
            minBit = offBit = bdupList[0]
            for i in range(len(bdupList)):
                if i+offBit == bdupList[i]:
                    continue
                if minBit == bdupList[i-1]:
                    bitDup += '[%d], '%minBit
                else:
                    bitDup += '[%d:%d], '%(bdupList[i-1], minBit)
                minBit = bdupList[i]
                offBit = bdupList[i] - i
            if minBit == bdupList[i-1]:
                bitDup += '[%d], '%minBit
            else:
                bitDup += '[%d:%d], '%(bdupList[i-1], minBit)
    elif dict0['msb'] is not None and (type(dict0['msb']) == int or dict0['msb'].isdigit()) and \
         dict0['lsb'] is not None and (type(dict0['lsb']) == int or dict0['lsb'].isdigit()) and \
         dict1['msb'] is not None and (type(dict1['msb']) == int or dict1['msb'].isdigit()) and \
         dict1['lsb'] is not None and (type(dict1['lsb']) == int or dict1['lsb'].isdigit()) :
        datH0 = int(dict0['msb'])
        datL0 = int(dict0['lsb'])
        datH1 = int(dict1['msb'])
        datL0 = int(dict1['lsb'])
        if   datH0 == datL0 and datH1 == datL1:
            return hasDup, bitDup
        elif datH0 == datL0 and (datH0 > datH1 or datL0 < datL1):
            return hasDup, bitDup
        elif datH1 == datL1 and (datH1 > datH0 or datL1 < datL0):
            return hasDup, bitDup

        msbMin = min(datH0, datH1)
        lsbMax = max(datL0, datL1)
        if msbMin > lsbMax:
            hasDup = True
            bitDup = "[%d:%d]"%(msbMin, lsbMax)
        elif msbMin == lsbMax:
            hasDup = True
            bitDup = "[%d]"%(msbMin)

    return hasDup, bitDup
# Function 'width_check' # }}}

# Function 'proc_comment' # {{{
def proc_comment(curStr, inComment, inPara, inTask, inFunction, inGenerate, keyWord, fpLog=None):
    postComment = ''
    if inComment:
        if '*/' in curStr:
            inComment = False
            curStr = curStr[curStr.index('*/')+2:]
        else:
            return ('', True, inPara, inTask, inFunction, inGenerate, -1, '')
    if '//' in curStr:
        comIdx = curStr.index('//')
        if '/*' not in curStr or comIdx < curStr.index('/*'):
            postComment = curStr[comIdx:]
            curStr      = curStr[:comIdx]
    offset = -1
    while '/*' in curStr:
        if '*/' in curStr:
            offset = curStr.find("/*%s*/"%keyWord.lower())
            if offset < 0:
                offset = curStr.find("/*%s*/"%keyWord.upper())
            curStr = curStr[:curStr.index('/*')]+curStr[curStr.index('*/')+2:]
            if '//' in curStr:
                comIdx = curStr.index('//')
                if '/*' not in curStr or comIdx < curStr.index('/*'):
                    postComment = curStr[comIdx:]
                    curStr      = curStr[:comIdx]
        else:
            inComment = True
            curStr = curStr[:curStr.index('/*')]
            break

    inPara     = True  if re_para.search(curStr)     and curStr.find(';') == -1 else inPara
    inTask     = True  if re_task.search(curStr)     else inTask
    inFunction = True  if re_function.search(curStr) else inFunction
    inGenerate = True  if re_generate.search(curStr) else inGenerate

    inPara     = False if inPara     and curStr.find(';') > -1         else inPara
    inTask     = False if inTask     and re_endtask.search(curStr)     else inTask
    inFunction = False if inFunction and re_endfunction.search(curStr) else inFunction
    inGenerate = False if inGenerate and re_endgenerate.search(curStr) else inGenerate

    return (curStr, inComment, inPara, inTask, inFunction, inGenerate, offset, postComment)
# Function 'proc_comment' # }}}

# Function 'search_file_path' # {{{
def search_file_path(curStrs, baseDir, debug=False, fpLog=None):
    """
    Print invalid options if debug is True
    """
    searchDict = {'path':[], 'module':lDict()}
    invalidOpt = []
    for line in curStrs:
        if not line.lstrip().startswith('//'):
            continue
        line = line.replace("'", '"')
        if 'verilog-library-files:' in line:
        #if 'verilog-inst-file:' in line:
            idxBegin = line.find('"')
            idxEnd   = line.find('"', idxBegin+1)
            while idxBegin > -1 and idxEnd > -1:
                invalidOpt.extend( parsing_file_option(searchDict, baseDir, line[idxBegin+1:idxEnd], True, fpLog=fpLog) )
                line = line[idxEnd+1:]
                idxBegin = line.find('"')
                idxEnd   = line.find('"', idxBegin+1)
        elif 'verilog-library-directories:' in line:
            idxBegin = line.find('"')
            idxEnd   = line.find('"', idxBegin+1)
            while idxBegin > -1 and idxEnd > -1:
                curDir = os.path.expandvars(line[idxBegin+1:idxEnd])
                if os.path.isabs(curDir) is False:
                    curDir = os.path.abspath(baseDir+os.path.sep+curDir)
                searchDict['path'].append(curDir)
                line = line[idxEnd+1:]
                idxBegin = line.find('"')
                idxEnd   = line.find('"', idxBegin+1)
    if debug:
        for opt in invalidOpt:
            xprint(fpLog, "Info: Invalid Option: "+opt)
        xprint(fpLog, "Info: \nValid option of path:")
        for p   in searchDict['path']:
            xprint(fpLog, "Info:     "+p)
        xprint(fpLog, "Info: \nValid option of file:")
        for m   in searchDict['module'].lkeys:
            xprint(fpLog, "Info:     "+searchDict['module'][m])
        xprint(fpLog, "Info: ")

    return searchDict
# Function 'search_file_path' # }}}

# Function 'parsing_file_option' # {{{
def parsing_file_option(searchDict, baseDir, option, priority, fpLog=None):
    """
    Parsing file options:
        1. dir/dirc/filename.x
        2. +incdir+idir/idirc
        3. -v dir/dirc/filename.x
        4. -y dir/dirc
        5. -f dir/dir/filelist
    Invalid options will be returned
    """
    invalidOpt = []
    option = option.strip()
    vObj = re_option_v.search(option)
    fObj = yObj = vObj
    if not vObj:
        yObj = re_option_y.search(option)
    if not vObj and not yObj:
        fObj = re_option_f.search(option)
    if not vObj and not yObj and not fObj:
        yObj = re_option_inc.search(option)
    if not vObj and not yObj and not fObj:
        vObj = re_option_file.search(option)

    if vObj:
        files, pfix = (vObj.group('file'), vObj.group('pfix'))
        fName = os.path.expandvars( "%s.%s"%(files, pfix) )
        if os.path.isabs(fName) is False:
            fName = os.path.abspath(baseDir+os.path.sep+fName)

        if priority:
            if os.path.isfile(fName):
                try:
                    #fp = open(fName, "r")
                    fp = codecs.open(fName, "r", encoding='gbk', errors='ignore')
                    inComment  = inPara = False
                    inFunction = inTask = inGenerate = False
                    for line in fp:
                        line, inComment, inPara, inTask, inFunction, inGenerate, offset, postComment = proc_comment( \
                        line, inComment, inPara, inTask, inFunction, inGenerate, '')
                        objm = re.search("^\s*module\s+(?P<module>`S+|\w+)", line)
                        if objm:
                            module = objm.group('module')
                            if module not in searchDict['module']:
                                searchDict['module'][module] = fName
                    fp.close()
                except IOError as e:
                    xprint(fpLog, "Error: Cannot open file: "+e)
            else:
                xprint(fpLog, "Error: Invalid file: %s"%fName)
        else:
            mName = os.path.splitext(os.path.basename(files))[0]
            if mName not in searchDict['module']:
                searchDict['module'][mName] = fName
    elif yObj:
        fdir = yObj.group('path')
        if fdir not in searchDict['path']:
            fdir = os.path.expandvars(fdir)
            if os.path.isabs(fdir) is False:
                fdir = os.path.abspath(baseDir+os.path.sep+fdir)
            searchDict['path'].append(fdir)
    elif fObj:
        flist = os.path.expandvars(fObj.group('file'))
        if os.path.isabs(flist) is False:
            fdir = os.path.abspath(baseDir+os.path.sep+flist)

        projDir = os.environ.get("ENV_DIR")
        tmpBaseDir = baseDir
        if projDir is not None:
            tmpBaseDir = projDir+os.path.sep+'work'+os.path.sep+'tmp'
        else:
            xprint(fpLog, "Warning: Env. variable '$ENV_DIR' is unset, root of relative path in [%s] will be be set to [%s]!"%(flist, baseDir))
        iOpt = parsing_file_list(searchDict, tmpBaseDir, os.path.expandvars(flist), fpLog=fpLog)
        if len(iOpt) > 0:
            invalidOpt.extend(iOpt)
    elif option.isspace() or option.startswith('//') or option.startswith('/*'):
        pass
    else:
        invalidOpt = [option]

    return invalidOpt
# Function 'parsing_file_option' # }}}

# Function 'parsing_file_list' # {{{
def parsing_file_list(searchDict, baseDir, flist, fpLog=None):
    """
    Parsing filelist, and return invalid options
    """
    invalidOpt = ["******Begin of invalid options in filelist: %s"%flist]
    try:
        #fp = open(flist, 'r')
        fp = codecs.open(flist, 'r', encoding='gbk', errors='ignore')
        for line in fp:
            invOpt = parsing_file_option(searchDict, baseDir, line, False, fpLog=fpLog)
            invalidOpt.extend(invOpt)
        fp.close()
    except IOError as e:
        xprint(fpLog, "Warning: Cannot open filelist file: %s"%e)

    invalidOpt = ["******  End of invalid options in filelist: %s"%flist]

    return invalidOpt
# Function 'parsing_file_list' # }}}

# Function 'get_port_config' # {{{
def get_port_config(modObj, iname, silent=1, fpLog=None):
    mname = None
    dPortCfg  = {}
    if iname in modObj.mInst:
        mname = modObj.mInst[iname]['module']
    else:
        if silent == 0:
            xprint(fpLog, "Info: Cannot find module info for instance '%s'"%iname)
        return dPortCfg

    hasPort = False
    wmax = bmax = 0
    lFlab = []
    lTlab = []
    dictCfg = modObj.cfgInfo
    if 'connect' in dictCfg and 'socket' in dictCfg and 'sufix' in dictCfg:
        if 'to' in dictCfg['connect'] and iname in dictCfg['connect']['to']:
            lTlab = dictCfg['connect']['to'][iname].keys()
            if mname in modObj.mMod:
                for pname in lTlab:
                    if pname not in modObj.mMod.mPorts:
                        continue
                    fpname = dictCfg['connect']['to'][iname][pname]['lab']
                    finame = dictCfg['connect']['to'][iname][pname]['inst']

                    toPort = False
                    if finame == 'outside':
                        toPort  = True
                        hasPort = True
                    elif finame in modObj.mInst:
                        fmname = modObj.mInst[finame]['module']
                        if fmname in modObj.mMod and fpname not in modObj[fmname].mPorts:
                            xprint(fpLog, "Warning: Port [%s.%s] is not defined in module[%s] for [%s.%s]!"%(finame, fpname, fmname, iname, pname))
                            continue
                    else:
                        xprint(fpLog, "Warning: Instance[%s] is not instantated in module[%s] for [%s.%s]"%(finame, iname, pname, modObj.mName))
                        continue
                    sufix = ''
                    width = msb = lsb = None
                    if dictCfg['sufix']['from'][finame][fpname]:
                        msb   = dictCfg['sufix']['from'][finame][fpname]['msb'  ]
                        lsb   = dictCfg['sufix']['from'][finame][fpname]['lsb'  ]
                        width = dictCfg['sufix']['from'][finame][fpname]['width']
                        sufix = dictCfg['sufix']['from'][finame][fpname]['sufix']

                    wmax = max(wmax, len(fpname+sufix))
                    if width is not None:
                        bmax = max(bmax, len(width))
                    dPortCfg[pname] = {'port' :toPort,
                                       'name' :fpname+sufix,
                                       'width':width,
                                       'msb'  :msb,
                                       'lsb'  :lsb}
        if 'from' in dictCfg['connect'] and iname in dictCfg['connect']['from']:
            lFlab = dictCfg['connect']['from'][iname].keys()
            if mname in modObj.mMod:
                for pname in lFlab:
                    if pname not in modObj.mMod[mname].mPorts:
                        continue
                    toPort = False
                    if 'outside' in dictCfg['connect']['from'][iname][pname]:
                        toPort  = True
                        hasPort = True

                    sufix = ''
                    width = msb = lsb = None
                    if dictCfg['sufix']['from'][iname][pname] is not None:
                        msb   = dictCfg['sufix']['from'][iname][pname]['msb'  ]
                        lsb   = dictCfg['sufix']['from'][iname][pname]['lsb'  ]
                        width = dictCfg['sufix']['from'][iname][pname]['width']
                        sufix = dictCfg['sufix']['from'][iname][pname]['sufix']

                    wmax = max(wmax, len(pname+sufix))
                    if width is not None:
                        bmax = max(bmax, len(width))
                    dPortCfg[pname] = {'port' :toPort,
                                       'name' :fpname+sufix,
                                       'width':width,
                                       'msb'  :msb,
                                       'lsb'  :lsb}

                    for tiname in dictCfg['connect']['from'][iname][pname]:
                        for tlab in dictCfg['connect']['from'][iname][pname][tiname]:
                            if tiname == 'outside':
                                if tlab not in modObj.mPorts:
                                    xprint(fpLog, "Warning: Port [%s.%s] is not defined in module[%s] for [%s.%s]!"%(tiname, tlab, modObj.mName, iname, pname))
                            elif tiname in modObj.mInst:
                                tmname = modObj.mInst[tiname]['module']
                                if tmname in modObj.mMod and tlab not in modObj.mMod[tmname].mPorts:
                                    xprint(fpLog, "Warning: Port [%s.%s] is not defined in module[%s] for [%s.%s]!"%(tiname, tlab, tmname, iname, pname))
                            else:
                                xprint(fpLog, "Warning: Instance[%s] is not instantated in module[%s] for [%s.%s]"%(tiname, iname, pname, modObj.mName))
        if mname not in dictCfg['socket'] or (len(lFlab) == 0 and len(lTlab) == 0):
            if silent == 0:
                xprint(fpLog, "Info: No config for module[%s] -> instance[%s]..."%(mname, iname))
            for pname in dPortCfg:
                dPortCfg[pname]['wmax'] = wmax
                dPortCfg[pname]['bmax'] = bmax
                dPortCfg[pname]['has_port'] = hasPort
            return dPortCfg
    else:
        if silent == 0:
            xprint(fpLog, "Info: No config information...")
        return dPortCfg

    for label, ldict in dictCfg['socket'][mname].items():
        if label in lFlab:
            sufix = ''
            if dictCfg['sufix']['from'][iname][label] is not None:
                sufix = dictCfg['sufix']['from'][iname][label]['sufix']

            toPort = False
            if 'outside' in dictCfg['connect']['from'][iname][label]:
                toPort  = True
                hasPort = True
            
            tmpList = []
            for pname in ldict['p2e']:
                if pname in dPortCfg:
                    tmpList.append(pname)
                    if silent == 0:
                        xprint(fpLog, "Warning: Port[%s.%s] is already connected to [%s], <Ignored [%s.%s %s -> %s]>"%( \
                        mname, pname, dPortCfg[pname]['name'], iname, label, ldict['p2e'][pname]['ename'], pname))
                    continue
                wmax = max(wmax, len(pname+sufix))
                if ldict['p2e'][pname]['width'] is not None:
                    bmax = max(bmax, len(ldict['p2e'][pname]['width']))
            
                dPortCfg[pname] = {'port' :toPort,
                                   'name' :pname+sufix,
                                   'width':ldict['p2e'][pname]['width'],
                                   'msb'  :ldict['p2e'][pname]['msb'],
                                   'lsb'  :ldict['p2e'][pname]['lsb']}

            for tiname in dictCfg['connect']['from'][iname][label]:
                if tiname not in modObj.mInst and tiname != 'outside':
                    xprint(fpLog, "Warning: Instance[%s] described in [%s.cfg] for [%s.%s] is not instantiated..."%(finame, modObj.mName, iname, label))
                    continue
                for tlab in dictCfg['connect']['from'][iname][label][tiname]:
                    tmname = None
                    if tiname == 'outside':
                        tmname = 'outside'
                    else:
                        tmname = modObj.mInst[tiname]['module']

                    if tmname in dictCfg['socket']:
                        if tlab in dictCfg['socket'][tmname]:
                            for pname in ldict['p2e']:
                                if pname in tmpList:
                                    continue
                                pename = ldict['p2e'][pname]['ename']
                                if silent == 0 and pename not in dictCfg['socket'][tmname][tlab]['e2p']:
                                    xprint(fpLog, "Warning: [%s] is not defined in socket[%s] of module[%s] for [%s.%s]"%(pename, tlab, tmname, iname, label))
                        else:
                            xprint(fpLog, "Warning: Socket[%s] in module[%s is not defined for [%s.%s]"%(tlab, tmname, iname, label))
                    else:
                        xprint(fpLog, "Warning: Socket of module[%s is not defined for [%s.%s]"%(tmname, iname, label))
        elif label in lTlab:
            flab   = dictCfg['connect']['to'][iname][label]['lab']
            finame = dictCfg['connect']['to'][iname][label]['inst']
            if dictCfg['sufix']['from'][finame][flab] is not None:
                sufix = dictCfg['sufix']['from'][finame][flab]['sufix']

            if finame in modObj.mInst or finame == 'outside':
                fmname = None
                toPort = False
                if finame == 'outside':
                    toPort  = True
                    hasPort = True
                    fmname  = 'outside'
                else:
                    fmname = modObj.mInst[finame]['module']

                if fmname in dictCfg['socket']:
                    if flab in dictCfg['socket'][fmname]:
                        for pname in ldict['p2e']:
                            if pname in dPortCfg:
                                if silent == 0:
                                    xprint(fpLog, "Warning: Port[%s.%s] is already connected to [%s], <Ignored [%s.%s %s -> %s]>"%( \
                                        mname, pname, dPortCfg[pname]['name'], iname, label, ldict['p2e'][pname]['ename'], pname))
                                continue
                            pename = ldict['p2e'][pname]['ename']
                            if pename in dictCfg['socket'][fmname][flab]['e2p']:
                                fpname = dictCfg['socket'][fmname][flab]['e2p'][pename]['pname']
                                wmax = max(wmax, len(ldict['p2e'][pname]['width']))
                                if ldict['p2e'][pname]['width'] is not None:
                                    bmax = max(bmax, len(ldict['p2e'][pname]['width']))
                                dPortCfg[pname] = {'port' :toPort,
                                                   'name' :pname+sufix,
                                                   'width':ldict['p2e'][pname]['width'],
                                                   'msb'  :ldict['p2e'][pname]['msb'],
                                                   'lsb'  :ldict['p2e'][pname]['lsb']}
                            else:
                                dPortCfg[pname] = {'port' :toPort,
                                                   'name' :'',
                                                   'width':None,
                                                   'msb'  :None,
                                                   'lsb'  :None}
                                if silent == 0:
                                    xprint(fpLog, "Warning: [%s] is not defined in socket[%s] of module[%s] for [%s.%s]"%(pename, flab, fmname, iname, label))
                    else:
                        xprint(fpLog, "Warning: Socket[%s] in module[%s] is not defined for [%s.%s]"%(flab, fmname, iname, label))
                else:
                    xprint(fpLog, "Warning: Socket of module[%s] is not defined for [%s.%s]"%(fmname, iname, label))
            else:
                xprint(fpLog, "Warning: Instance[%s] described in [%s.cfg] for [%s.%s] is not instantiated..."%(finame, modObj.mName, iname, label))

    for pname in dPortCfg:
        dPortCfg[pname]['wmax'] = wmax
        dPortCfg[pname]['bmax'] = bmax
        dPortCfg[pname]['has_port'] = hasPort
    return dPortCfg
# Function 'get_port_config' # }}}

# Function 'parsing_connect_config' # {{{
def parsing_connect_config(mname, cfgFile, dictCfg={}, silent=1, fpLog=None):
    """
    dictCfg = {'sufix'   : {'to'   : {instName : {socketLabel:{'sufix':sufix
                                                               'width':width
                                                               'msb'  : msb
                                                               'lsb'  : lsb
                                                              }
                                                 }
                                     }
                           {'from' : {instName : {socketLabel:{'sufix':sufix
                                                               'width':width
                                                               'msb'  : msb
                                                               'lsb'  : lsb
                                                              }
                                                 }
                                     }
                           }
               'socket'  : {modName: {socketLabel : {'type'  : socketType
                                                     'p2e'   :{portName:{'ename':socketElement
                                                                         'width':elementWidth
                                                                         'msb'  : msb
                                                                         'lsb'  : lsb
                                                                        }
                                                              }
                                                     'e2p'   :{socketElement:{'pname':portName
                                                                              'width':portWidth
                                                                              'msb'  : msb
                                                                              'lsb'  : lsb
                                                                             }
                                                              }
                                                    }
                                     }
                           }
               'connect' : {'from' : {instName : {socketLabel : { instName : { socketLabel:sufix }
                                                                }
                                                 }
                                     }
                            'to'   : {instName : {socketLabel : {'inst' : instName
                                                                 'lab'  : socketLabel
                                                                }
                                                 }
                                     }

                           }
              }
    """
    fp = None
    try:
        #fp = open(cfgFile, 'r')
        fp = codecs.open(cfgFile, 'r', encoding='gbk', errors='ignore')
    except IOError as e:
        if silent == 0:
            xprint(fpLog, "Warning: Cannot open cfg file [%s]! <%s>"%(cfgFile, e))
    if silent == 0:
        xprint(fpLog, "Info: Parsing cfg file [%s]"%(cfgFile))

    if 'sufix' not in dictCfg:
        dictCfg['sufix'] = {}
    if 'socket' not in dictCfg:
        dictCfg['socket'] = {}
    if 'connect' not in dictCfg:
        dictCfg['connect'] = {}

    module = label = socket = None
    inSocket = False
    for line in fp:
        line = line.strip()
        if line == '' or line.startswith('//'):
            continue

        obj = re_connect.search(line)
        if obj:
            finst, flab = (obj.group('finst'), obj.group('flab'))
            sufix  = '_'+obj.group('sfix') if obj.group('sfix') else ''
            fwidth = obj.group('fwidth')
            fmsb   = obj.group('fmsb')
            flsb   = obj.group('flsb') if obj.group('flsb') else fmsb
            tinst, tlab = (obj.group('tinst'), obj.group('tlab'))
            twidth = obj.group('twidth')
            tmsb   = obj.group('tmsb')
            tlsb   = obj.group('tlsb') if obj.group('tlsb') else tmsb

            if silent == 0:
                xprint(fpLog, "Info: <module[%s]>Find connection: sufix[%s] [%s.%s]->[%s.%s]"%(mname, sufix, finst, flab, tinst, tlab))
            # to instance.label -> from instance.label
            # sufix
            if 'to' not in dictCfg['sufix']:
                dictCfg['sufix']['to'] = {}
            if tinst not in dictCfg['sufix']['to']:
                dictCfg['sufix']['to'][tinst] = {}
            dictCfg['sufix']['to'][tinst][tlab] = {'sufix':sufix, 'width':twidth, 'msb':tmsb, 'lsb':tlsb}
            # connection
            if 'to' not in dictCfg['connect']:
                dictCfg['connect']['to'] = {}
            if tinst not in dictCfg['connect']['to']:
                dictCfg['connect']['to'][tinst] = {}
            if tlab not in dictCfg['connect']['to'][tinst]:
                dictCfg['connect']['to'][tinst][tlab] = {'inst':finst, 'lab':flsb}
            else:
                xprint(fpLog, "Warning: <module[%s]>To [%s.%s] is already connected (from [%s.%s])! <Ignored: %s>"%(mname, tinst, tlab, finst, flab, line))
                continue

            # from instance.label -> to instance.label
            # sufix
            if 'from' not in dictCfg['sufix']:
                dictCfg['sufix']['from'] = {}
            if finst not in dictCfg['sufix']['from']:
                dictCfg['sufix']['from'][finst] = {}
            dictCfg['sufix']['from'][finst][flab] = {'sufix':sufix, 'width':fwidth, 'msb':fmsb, 'lsb':flsb}
            # connection
            if 'from' not in dictCfg['connect']:
                dictCfg['connect']['from'] = {}
            if finst not in dictCfg['connect']['from']:
                dictCfg['connect']['from'][finst] = {}
            if flab not in dictCfg['connect']['from'][finst]:
                dictCfg['connect']['from'][finst][flab] = {}
            if finst not in dictCfg['connect']['from'][finst][flab]:
                dictCfg['connect']['from'][finst][flab][finst] = {}
            if flab not in dictCfg['connect']['from'][finst][flab][finst]:
                dictCfg['connect']['from'][finst][flab][finst][flab] = sufix
            else:
                xprint(fpLog, "Warning: <module[%s]>Connection from [%s.%s] to [%s.%s] is already defined! <Ignored: %s>"%(mname, finst, flab, tinst, tlab, line))
            continue #??

        if inSocket:
            if re_endsocket.search(line):
                inSocket = False
            else:
                obj = re_element.search(line)
                if obj:
                    ename = obj.group('ename')
                    width = obj.group('width')
                    msb   = obj.group('msb'  )
                    lsb   = obj.group('lsb'  ) if obj.group('lsb') is not None else msb
                    pname = obj.group('pname')
                    dictCfg['socket'][module][label]['p2e'][pname] = {'ename':ename,
                                                                      'width':width,
                                                                      'msb'  :msb,
                                                                      'lsb'  :lsb}
                    dictCfg['socket'][module][label]['e2p'][ename] = {'pname':pname,
                                                                      'width':width,
                                                                      'msb'  :msb,
                                                                      'lsb'  :lsb}
                else:
                    xprint(fpLog, "Warning: <module[%s]>Ignored invalid socket element description <%s>"%(mname, line))
        else:
            obj = re_addsocket.search(line)
            if obj:
                module, label, socket = (obj.group('module'), obj.group('label'), obj.group('socket'))
                if silent == 0:
                    xprint(fpLog, "Info: <module[%s]>Find socket [%s.%s %s]"%(mname, module, label, socket))
                if module not in dictCfg['socket']:
                    dictCfg['socket'][module] = {}
                if label not in dictCfg['socket'][module]:
                    inSocket = True
                    dictCfg['socket'][module][label] = {}
                    dictCfg['socket'][module][label]['p2e'] = {}
                    dictCfg['socket'][module][label]['e2p'] = {}
                    dictCfg['socket'][module][label]['type'] = socket
                else:
                    inSocket = False
                    xprint(fpLog, "Warning: <module[%s]> Socket of module[%s]-Label[%s] is already defined (as socket [%s])! <Ignored>"%(mname, module, label, socket))
    fp.close()
    return True
# Function 'parsing_connect_config' # }}}


# Class 'ModuleInfo' # {{{
class ModuleInfo:
    def __init__(self, mfile, lines=[], mname=None, macros={}): #{{
        self.mFile   = mfile
        self.mDir    = os.path.abspath( os.path.expandvars(os.path.dirname(mfile)) )
        self.mLines  = lines
        self.mName   = mname
        self.Macros  = macros

        self.mParas  = lDict()
        self.Paths   = {}
        self.portType= 95
        self.mPorts  = {'dict':{}, 'list':[], 'auto':[]}
        self.mWires  = {'blen':5, 'defs':{}, 'regs':{}, 'wires':{}, 'iwire':{}}
        self.mLocate = {'eport'  :-1,
                        'smod'   :-1,
                        'emod'   :-1,
                        'swire'  :-1,
                        'ewire'  :-1,
                        'sarg'   :-1,
                        'earg'   :-1,
                        'adef'   :-1,
                        'ploc'   :{},
                        'iloc'   :{}}
        self.mInst   = lDict()
        self.mMod    = {}
        self.cfgInfo = {}
    #}}
    def set_name(self, name): #{{
        self.mName = name
    #}}

    def save_module(self, fname=None, lines=[]): #{{
        fn = fname if fname else self.mFile
        ml = lines if lines else self.mLines
        #with open(fn, "w") as fp:
        with codecs.open(fn, "w", encoding='gbk', errors='ignore') as fp:
            for i in ml:
                fp.write( i.rstrip()+'\n' )
            fp.close()
    #}}

    def set_lines(self, lines=[], fpLog=None): #{{
        status = True
        if len(lines) > 0:
            self.mLines = lines
        else:
            fp = None
            try:
                #fp = open(self.mFile, 'r')
                fp = codecs.open(self.mFile, 'r', encoding='gbk', errors='ignore')
            except IOError as e:
                xprint(fpLog, "Error: [%s.%s]Cannot open %s to initilize mLines! <%s>"%(self.__class__, __name__, self.mFile, e))
                status = False
            if fp:
                self.mLines = fp.readlines()
                fp.close()
        return status
    #}}

    def del_all_lines(self): #{{
#        self.mLines = []
        for i in range(len(self.mLines)):
            del self.mLines[0]
    #}}

    def del_lines(self, startIdx, endIdx=None, fpLog=None): #{{
        if endIdx is None:
            endIdx = startIdx+1

        linesLen = len(self.mLines)
        if -1 < startIdx < endIdx and startIdx < linesLen:
            endIdx = linesLen if linesLen < endIdx else endIdx
            for i in range(startIdx, endIdx):
                del self.mLines[startIdx]

            #update location info
            lineDelNum = endIdx - startIdx
            for loc in self.mLocate.keys():
                if loc in ['iloc', 'ploc']:
                    for inst in self.mLocate[loc]:
                        for typ in self.mLocate[loc][inst]:
                            if self.mLocate[loc][inst][typ] >= startIdx:
                                self.mLocate[loc][inst][typ] -= lineDelNum if self.mLocate[loc][inst][typ] >= endIdx else -1
                elif self.mLocate[loc] >= startIdx:
                    self.mLocate[loc] -= lineDelNum if self.mLocate[loc] >= endIdx else -1
            if  self.mLocate['swire'] == -1:
                self.mLocate['swire'] = self.mLocate['adef']
            if  self.mLocate['ewire'] == -1:
                self.mLocate['ewire'] = self.mLocate['swire']
    #}}

    def append_lines(self, lines=[], location=-1, appendMode='append', fpLog=None): #{{
        if location > -1:
            if appendMode != 'append':
                self.mLines = self.mLines[:location]+lines+self.mLines[location:]
            else:
                #self.mLines.append(lines, location)
                for i in range(len(lines)):
                    self.mLines.append(lines[i], location+i)
        else:
            if appendMode != 'append':
                self.mLines.extend(lines)
            else:
                self.mLines.append(lines)
        # update location info.
        lineNum = len(lines)
        for loc in self.mLocate.keys():
            if loc in ['iloc', 'ploc']:
                for inst in self.mLocate[loc]:
                    for typ in self.mLocate[loc][inst]:
                        if  self.mLocate[loc][inst][typ] >= location:
                            self.mLocate[loc][inst][typ] += lineNum
            elif self.mLocate[loc] >= location:
                self.mLocate[loc] += lineNum
    #}}

    def update_location(self, dictLoc={}): #{{
        self.mLocate.update(dictLoc)
        if  self.mLocate['swire'] == -1:
            self.mLocate['swire'] = self.mLocate['adef']
        if  self.mLocate['ewire'] == -1:
            self.mLocate['ewire'] = self.mLocate['swire']
    #}}

    def print_location(self, fpLog=None): #{{
        for loc in self.mLocate.keys():
            if loc in ['iloc', 'ploc']:
                for inst in self.mLocate[loc]:
                    xprint(fpLog, "Info: printLoc: %s.mLocate[%s][%s] = %s"%(self.__class__, loc, inst, self.mLocate[loc][inst]))
            else:
                xprint(fpLog, "Info: printLoc: %s.mLocate[%s] = %s"%(self.__class__, loc, self.mLocate[loc]))
    #}}

    def initial_port(self, cfg=False, silent=1, fpLog=None): #{{
        lines = []
        if len(self.mLines) > 0:
            lines = self.mLines
        else:
            fp = None
            try:
                #fp = open(self.mFile, 'r')
                fp = codecs.open(self.mFile, 'r', encoding='gbk', errors='ignore')
            except IOError as e:
                xprint(fpLog, "Error: [%s.%s]Cannot open %s to initilize mLines! <%s>"%(self.__class__, __name__, self.mFile, e))
            if fp:
                lines = fp.readlines()
                fp.close()
            else:
                return False

        if len(lines) > 0:
            dInfoLoc, self.mName, self.mPorts, self.mParas, self.portType = get_module_ports(lines, self.mName, self.mFile, self.Macros, self.cfgInfo, silent, fpLog=fpLog)

            # get ignore port information
            ignoreFile = os.path.splitext(self.mFile)[0]+gIgnorePortListFile
            if os.path.isfile(ignoreFile):
                fp = None
                try:
                    #fp = open(ignoreFile, 'r')
                    fp = codecs.open(ignoreFile, 'r', encoding='gbk', errors='ignore')
                except IOError as e:
                    xprint(fpLog, "Error: [%s]Cannot open file %s <%s>"%(self.__class__, ignoreFile, e))

                if fp:
                    lines = fp.readlines()
                    fp.close()
                ignorePortList = get_ignore_ports(lines, ignoreFile, silent, fpLog=fpLog)
                for port in self.mPorts['dict']:
                    if port in ignorePortList:
                        self.mPorts['dict'][port]['ignore'] = True
                    else:
                        self.mPorts['dict'][port]['ignore'] = False

            self.update_location(dInfoLoc)
            if cfg:
                self.add_cfg_info(self.mName, silent)
        else:
            xprint(fpLog, "Warning: Current module in file [%s] is empty!"%(self.mFile))

        if self.mName is None:
            xprint(fpLog, "Error: No module defined in '%s'"%(self.mFile))
            return False
        if len(self.mPorts['list']) == 0:
            xprint(fpLog, "Error: No ports have been found in module '%s'"%(self.mName))
            return False

        return True
        #}}

    def initial_wire(self, detail=False, silent=0, fpLog=None): #{{
        lines = []
        if len(self.mLines) > 0:
            lines = self.mLines
        else:
            fp = None
            try:
                #fp = open(self.mFile, 'r')
                fp = codecs.open(self.mFile, 'r', encoding='gbk', errors='ignore')
            except IOError as e:
                xprint(fpLog, "Error: [%s.%s]Cannot open %s to initilize mPorts! <%s>"%(self.__class__, __name__, self.mFile, e))
            if fp:
                lines = fp.readlines()
                fp.close()
            else:
                return False

        maxBlen, self.mWires['iwire'] = get_instance_wires(self.mInst, self.mParas, silent, fpLog=fpLog)
        maxBlen = max(maxBlen, self.mWires['blen'])

        self.mName, wireDict = get_module_wires(lines, self.mLocate, self.mName, self.mWires['iwire'], detail, self.mPorts['dict'], self.mParas, silent, fpLog=fpLog)

        self.mWires.update(wireDict)
        self.mWires['blen'] = max(self.mWires['blen'], maxBlen)

        return True
    #}}

    def initial_instance(self, detail=False, cfg=False, silent=1, fpLog=None): #{{
        lines = []
        if len(self.mLines) > 0:
            lines = self.mLines
        else:
            fp = None
            try:
                #fp = open(self.mFile, 'r')
                fp = codecs.open(self.mFile, 'r', encoding='gbk', errors='ignore')
            except IOError as e:
                xprint(fpLog, "Error: [%s.%s]Cannot open %s to initilize mPorts! <%s>"%(self.__class__, __name__, self.mFile, e))
            if fp:
                lines = fp.readlines()
                fp.close()
            else:
                return False

        pathDict = {}  if detail is False else self.Paths
        self.mName, dInfoLoc, imodDict, self.mInst = get_instance_info(lines, \
        self.mName, self.mFile, self.cfgInfo, pathDict, self.mParas, cfg, silent, self.Macros, fpLog=fpLog)

        self.update_location(dInfoLoc)
        self.mMod.update(imodDict)

        if silent == 0:
            for m in self.mMod:
                xprint(fpLog, "Info: [%s] instanced module[%s] from %s"%(self.mName, m, self.mMod[m].mFile))

        return True
    #}}

    def add_instance(self, addiDict, appendMode='append', silent=1, fpLog=None): #{{
        for iname in addiDict.lkeys:
            if iname in self.mInst:
                xprint(fpLog, "Warning: Add instance name [%s] is already exists, <Ignored>!"%(iname))
                continue

            ilocate = self.mLocate['emod']
            lines = ["%s %s( /*autoinst*/ );"%(addiDict[iname], iname), ""]
            self.append_lines(lines, ilocate, appendMode, fpLog=fpLog)

            mname = addiDict[iname]
            if mname not in self.mMod:
                tmpModInfo = get_module_info(mname, self.Paths, False, silent, fpLog=fpLog)
                if tmpModInfo:
                    self.mMod[mname] = tmpModInfo

            # update module info
            self.mLocate['iloc'][iname] = {'start':ilocate, 'end':ilocate}
            self.mInst[iname] = {'auto'  :True,
                                 'module':mname,
                                 'plen'  :0,
                                 'llen'  :0,
                                 'wlen'  :0,
                                 'blen'  :5,
                                 'port'  :{},
                                 'false' :[]}
    #}}
    def initial_path(self, debug=False, fpLog=None): #{{
        lines = []
        if len(self.mLines) > 0:
            lines = self.mLines
        else:
            fp = None
            try:
                #fp = open(self.mFile, 'r')
                fp = codecs.open(self.mFile, 'r', encoding='gbk', errors='ignore')
            except IOError as e:
                xprint(fpLog, "Error: [%s.%s]Cannot open %s to initilize mPorts! <%s>"%(self.__class__, __name__, self.mFile, e))
            if fp:
                lines = fp.readlines()
                fp.close()
            else:
                return False
        self.Paths = search_file_path(lines, self.mDir, debug, fpLog=fpLog)
        return True
    #}}

    def ext_path(self, module=None): #{{
        if module:
            self.get_module_file(module, True, fpLog=fpLog)
        else:
            for iname in self.mInst.lkeys:
                self.get_module_file(self.mInst[iname]['module'], True, fpLog=fpLog)
    #}}

    def get_module_file(self, mname, ext=False, fpLog=None): #{{
        fname = None
        if 'module' in self.Paths:
            if mname in self.Paths['module'] and (ext or os.path.isfile(self.Paths['module'][mname])):
                fname = self.Paths['module'][mname]
        elif 'path' in self.Paths:
            for path in self.Paths['path']:
                tname = path+os.path.sep+mname
                if os.path.isfile(tname+'.v'):
                    fname = tname+'.v'
                    self.Paths['module'][mname] = fname
                elif os.path.isfile(tname+'.sv'):
                    fname = tname+'.sv'
                    self.Paths['module'][mname] = fname
        else:
             xprint(fpLog, "Warning: No file or searching path specified in module [%s]"%(self.mName))

        return fname
    #}}

    def get_cfg_file(self, mname, ext=False, fpLog=None): #{{
        cfgFile = None
        modFile = self.mFile
        if mname != self.mName:
            modFile = self.get_module_file(mname, ext, fpLog=fpLog)

        if modFile:
            cfgFile = os.path.splitext(modFile)[0]+'.cfg'
        else:
            xprint(fpLog, "Info: No .cfg find for module[%s]"%(mname))

        return cfgFile
    #}}

    def add_cfg_info(self, mname, silent=1, fpLog=None): #{{
        cfgFile = self.get_cfg_file(mname, True, fpLog=fpLog)
        if cfgFile and os.path.isfile(cfgFile):
            if silent == 0:
                xprint(fpLog, "Info: Parsing %s..."%(cfgFile))
            parsing_connect_config(mname, cfgFile, self.cfgInfo, silent, fpLog=fpLog)
        elif silent == 0:
            xprint(fpLog, "Warning: No config file for module[%s]"%(mname))
    #}}

    def del_cfg_info(self): #{{
        self.cfgInfo = {}
    #}}

    def get_cfg_info(self, iname, silent=1, fpLog=None): #{{
        return get_port_config(self, iname, silent, fpLog=fpLog)
    #}}

    def reformat_ports(self, lines=None, silent=1, fpLog=None): #{{
        xlines = lines if lines else self.mLines
        for i in range(len(xlines)):
            obj = re_port_decla_fmt.search(xlines[i])
            if obj:
                xlines[i] = "{:6s} {:24s} {}".format(
                       obj.group('dir'),
                       "{}{}{}".format( "{} ".format(obj.group('type')) if obj.group('type') else "",
                                        "{} ".format(obj.group('sign')) if obj.group('sign') else "",
                                        "{} ".format(obj.group('wth' )) if obj.group('wth' ) else ""),
                       obj.group('port').strip() if obj.group('port') else "")
    #}}

    def update_args(self, appendMode='append', fpLog=None): #{{
        # check port list
        if len(self.mPorts['dict']) == 0:
            xprint(fpLog, "Info: No port declaration is found in module [%s]"%(self.mName))
            return True

        # check /*autoarg*/ location
        if self.mLocate['sarg'] == -1 or self.mLocate['earg'] == -1:
            xprint(fpLog, "Info: No '/*AUTOARG*/ is found in module [%s]"%(self.mName))
            return True
        # format /*autoarg*/ and delete module port args
        self.mLines[self.mLocate['sarg']] = re_autoarg.sub('/*AUTOARG*/', self.mLines[self.mLocate['sarg']])
        self.del_lines(self.mLocate['sarg']+1, self.mLocate['earg']+1, fpLog=fpLog)

        # Generate module port args
        # ~~ inout/output/input args:
        xnewLines = []
        dictXcoms = {'xarg':'Inouts', 'oarg':'Outputs', 'iarg':'Inputs'}
        for arg in ['xarg', 'oarg', 'iarg']:
            newLines, realMaxLlen = macro_process_flow(self, None, None, ' '*4, 0, arg, fpLog=fpLog)
            if len(newLines) > 0:
                newLines.insert(0, "%s//%s"%(' '*4, dictXcoms[arg]))
                if len(xnewLines) > 0:
                    newLines.insert(0, "")
                xnewLines.extend(newLines)
##        for idx in reversed(range(len(xnewLines))):
##            comaIdx = xnewLines[idx].rfind(',')
##            if comaIdx > -1:
##                xnewLines[idx] = xnewLines[idx][:comaIdx]+xnewLines[idx][comaIdx+1:]
##                break
        defLevel = 0
        for idx in reversed(range(len(xnewLines))):
            mObj = re_macro_def.search(xnewLines[idx])
            cObj = re_comment.search(xnewLines[idx])
            nObj = re_blank_line.search(xnewLines[idx])
            if cObj or nObj:
                continue
            if mObj:
                if mObj.group('def') == 'endif':
                    defLevel += 1
                elif mObj.group('def') in ['ifdef', 'ifndef']:
                    defLevel -= 1
            else:
                if defLevel > 0:
                    comaIdx = xnewLines[idx].rfind(',')
                    xnewLines[idx] = xnewLines[idx][:4]+','+xnewLines[idx][4:comaIdx]+xnewLines[idx][comaIdx+1:]
                else:
                    comaIdx = xnewLines[idx].rfind(',')
                    xnewLines[idx] = xnewLines[idx][:comaIdx]+xnewLines[idx][comaIdx+1:]
                    break
        xnewLines.append(");")

        # update module port args
        self.append_lines(xnewLines, self.mLocate['sarg']+1, appendMode=appendMode, fpLog=fpLog)
        self.mLocate['earg'] = self.mLocate['earg']+len(xnewLines)
    #}}

    def update_defines(self, appendMode='append', v2001=True, fpLog=None): #{{
        # check /*autodefine*/ location
        if self.mLocate['adef'] == -1:
            xprint(fpLog, "Info: No '/*autodefine*/ is found in module [%s]"%(self.mName))
            return True

        maxBlen   = self.mWires['blen']
        dictRegs  = copy.deepcopy(self.mWires['regs'])
        dictWires = copy.deepcopy(self.mWires['wires'])

        mWiresDefs = self.mWires['defs']
        mPortsDict = self.mPorts['dict']

        # add undeclared input/output signal into wire list
        if v2001 and self.portType != 2001:
            for pname, pdict in mPortsDict.items():
                if pdict['inout'] == 'input':
                    continue
                if pname in mWiresDefs and mWiresDefs[pname]['auto'] is False:
                    continue
                if pdict['type'] is None:
                    dictWires[pname] = pdict
                    if pdict['width']:
                        maxBlen = max(maxBlen, len(pdict['width']))

        # add undeclared module instance signal into wire list
        for wname, wdict in self.mWires['iwire'].items():
            if wname not in mPortsDict and (wname not in mWiresDefs or mWiresDefs[wname]['auto']):
                if wname in dictRegs:
                    dictRegs[wname] = wire_width_merge(dictRegs[wname], wdict)
                elif wname in dictWires:
                    dictWires[wname] = wire_width_merge(dictWires[wname], wdict)
                else:
                    dictWires[wname] = wdict
                if wdict['width']:
                    maxBlen = max(maxBlen, len(wdict['width']))

        # delete current autodefine wire
        self.del_lines(self.mLocate['swire']+1, self.mLocate['ewire']+1)

        # generate wire definition
        maxBlen = maxBlen if maxBlen < 23 else 23
        dictLines = {}
        for wname, wdict in dictWires.items():
            if v2001 and self.portType == 2001 and wname in mPortsDict:
                continue
            if wname in dictRegs or \
              (wname in mPortsDict and mPortsDict[wname]['inout'] in ('input', 'output', 'inout')) or \
              (wname in mWiresDefs and mWiresDefs[wname]['auto']  is False  ) or \
               wname[0].isalpha() is False:
                continue

            if wdict['width']:
                dictLines[wname] = "wire %s %s;"%(wdict['width'].ljust(maxBlen), wname)
            else:
                dictLines[wname] = "wire %s %s;"%(' '.ljust(maxBlen), wname)

        newLines = []
        if len(dictLines) > 0:
            newLines.append("//auto wires{{{")
            for wname in sorted(dictLines.keys()):
                newLines.append(dictLines[wname])
            newLines.append("//}}}")

        # generate reg definition
        dictLines = {}
        for rname, rdict in dictRegs.items():
            if v2001 and self.portType == 2001 and rname in mPortsDict:
                continue
            if (rname in mWiresDefs and mWiresDefs[rname]['auto']  is False  ) or \
                rname[0].isalpha() is False:
                continue

            if rdict['width']:
                dictLines[rname] = "reg  %s %s;"%(rdict['width'].ljust(maxBlen), rname)
            else:
                dictLines[rname] = "reg  %s %s;"%(' '.ljust(maxBlen), rname)

        if len(dictLines) > 0:
            newLines.append("//auto regs{{{")
            for rname in sorted(dictLines.keys()):
                newLines.append(dictLines[rname])
            newLines.append("//}}}")

        if len(newLines) > 0:
            newLines.append(str_autodefs_end)
            self.append_lines(newLines, self.mLocate['swire']+1, appendMode=appendMode, fpLog=fpLog)
            self.mLocate['ewire'] = self.mLocate['ewire']+len(newLines)
    #}}

    def update_instance_wires(self, silent, fpLog=None): #{{
        maxBlen, self.mWires['iwire'] = get_instance_wires(self.mInst, self.mParas, silent, fpLog=fpLog)
        self.mWires['blen'] = max(self.mWires['blen'], maxBlen)
    #}}

    def update_instance(self, iname, cfg=False, silent=1, appendMode='append', fpLog=None): #{{
        if iname not in self.mInst:
            xprint(fpLog, "Warning: Instance[%s] is not found in module[%s], update instance ignored!"%(iname, self.mName))
            return False
        if  self.mInst[iname]['auto'] is False:
            xprint(fpLog, "Warning: Instance[%s] has no '/*AUTOINST*/' attribute, update instance ignored!"%(iname))
            return False
        if  self.mInst[iname]['module'] not in self.mMod:
            xprint(fpLog, "Warning: Module[%s] (instance[%s]) info is not valid, update instance ignored!"%(self.mInst[iname]['module'], iname))
            return False

        if silent == 0:
            xprint(fpLog, "Info: Update instance[%s] of module[%s]..."%(iname, self.mName))

        mname = self.mInst[iname]['module']
        # start to generate module instance lines
        leadJust   = 0
        blankCell  = ' '*4
        instLines  = []
        iportDict  = {'auto'  :True,
                      'module':mname,
                      'plen'  :0,
                      'wlen'  :0,
                      'llen'  :0,
                      'blen'  :5,
                      'port'  :{},
                      'false' :{}}
        # ~~ gen invalid port connection
        if 'false' in self.mInst[iname] and len(self.mInst[iname]['false']) > 0:
            instLines.append("    %s//%s"%(blankCell, str_delports_begin))
            instLines.extend(self.mInst[iname]['false'])
            instLines.append("    %s//%s"%(blankCell, str_delports_end))
            instLines.append("")
        # ~~ gen module instance lines
        dPortCfg = {}
        if cfg:
            dPortCfg = self.get_cfg_info(iname, silent, fpLog=fpLog)
        curMaxLlen = self.mInst[iname]['llen']
        validLine, realMaxLlen = macro_process_flow(self.mMod[mname], self, iname, blankCell, leadJust, 'inst', iportDict, dPortCfg, fpLog=fpLog)
        instLines.extend(validLine)

        # remove existed port connection
        instEnd   = self.mLocate['iloc'][iname]['end']
        instBegin = self.mLocate['iloc'][iname]['start']
        if instBegin == instEnd:
            self.mLines[instBegin] = re_autoinst.sub('/*AUTOINST*/', self.mLines[instBegin])

        # add module instance connection
        if len(instLines) > 0:
            self.del_lines(instBegin+1, instEnd+1, fpLog=fpLog)
            instLines.append(");")
            # ~~ add new instance port connection
            self.append_lines(instLines, instBegin+1, appendMode=appendMode, fpLog=fpLog)
            self.mLocate['iloc'][iname]['end'] = self.mLocate['iloc'][iname]['start']+len(instLines)
        elif instBegin == instEnd:
            self.mLines[instBegin] = re_autoinst_key.sub('/*AUTOINST*/', self.mLines[instBegin])

        # update instance connection info.
        self.mInst[iname] = iportDict

        #if realMaxLlen > curMaxLlen:
        #    self.update_instance(iname, cfg, silent, appendMode, fpLog)

    #}}

    def update_instance_ports(self, iname, portMode, cfg=False, silent=1, appendMode='append', add=True, fpLog=None): #{{
        if self.mLocate['adef'] == -1:
            xprint(fpLog, "Warning: No '/*AUTODEFINE*/' found, update instance ports ignored!")
            return False
        if  iname not in self.mInst:
            xprint(fpLog, "Warning: Instance[%s] is not found in module [%s], update instance ports ignored!"%(iname, self.mName))
            return False
        if  self.mInst[iname]['auto'] is False:
            xprint(fpLog, "Warning: Instance[%s] has no '/*AUTOINST*/' attribute, update instance ports ignored!"%(iname))
            return False
        if  self.mInst[iname]['module'] not in self.mMod:
            xprint(fpLog, "Warning: Module[%s] (instance[%s]) info is not valid, update instance ports ignored!"%(self.mInst[iname]['module'], iname))
            return False

        dPortCfg = {}
        if cfg:
            dPortCfg = self.get_cfg_info(iname, silent, fpLog=fpLog)

        # add new port declaration if needed
        lTmpPortCfgKey = list(dPortCfg.keys())
        if portMode in [2, 4] or (len(lTmpPortCfgKey) > 0 and dPortCfg[lTmpPortCfgKey[0]]['has_port']):
            pass
        else:
            return False

        leadJust  = 0
        blankCell = ' '*4
        portLines = []
        if portMode == 4:       # add instance wire to port declaration (update wire only)
            ptype = 'uport'
        elif portMode == 2:
            if add:             # add instance wire to port declaration
                ptype = 'aport'
            else:               # update instance wire for port declaration
                ptype = 'port'  # will delete original port declaration of current instance
        else:
            if add:             # add instance wire specified by .cfg to port declaration
                ptype = 'aaport'
            else:               # update instance wire specified by .cfg for port declaration
                ptype = 'xport'  # will delete original port declaration of current instance

        iportDict = {'plen' : 0,
                     'wlen' : 0,
                     'llen' : 0,
                     'blen' : 5,
                     'dict' : lDict()}
        # ~~ gen module instance ports
        portLines, realMaxLlen = macro_process_flow(self.mMod[self.mInst[iname]['module']], self, iname, ' '*4, 0, ptype, iportDict, dPortCfg, fpLog=fpLog)
        if len(portLines) > 0:
            hasStart = hasEnd = 0

            #iportStart = iportEnd = self.mLocate['ploc'][iname]['start']
            #if 'ploc' not in self.mLocate:
            #    self.mLocate['ploc'] = {}

            if iname in self.mLocate['ploc']:
                hasStart   = 1
                iportStart = self.mLocate['ploc'][iname]['start']
            else:
                iportStart = self.mLocate['eport']+1

            if iname in self.mLocate['ploc'] and 'end' in self.mLocate['ploc'][iname]:
                hasEnd   = 1
                iportEnd = self.mLocate['ploc'][iname]['end']

            if hasEnd == 0:
                portLines.append(   str_addports_end   + '[%s]'%iname)
            if hasStart == 0:
                portLines.insert(0, str_addports_begin + '[%s]'%iname)

            # ~~ remove existed module instance ports
            if add is False:
                self.del_lines(iportStart+hasStart, iportEnd, fpLog=fpLog)

            # ~~ add new module instance ports
            self.append_lines(portLines, iportStart+1, appendMode=appendMode, fpLog=fpLog)
            if hasStart == 0:
                self.mLocate['ploc'][iname] = {'start':iportStart+1}
            self.mLocate['ploc'][iname]['end'] = self.mLocate['ploc'][iname]['start']+len(portLines)+hasEnd

            # ~~ update port information
            if iname in self.mPorts['auto'] and 'start' in self.mPorts['auto'][iname] and 'end' in self.mPorts['auto'][iname]:
                orgEnd   = self.mPorts['auto'][iname]['end']
                orgStart = self.mPorts['auto'][iname]['start']
                portNum = len(iportDict['dict'])
                orgPortList = self.mPorts['list'][orgStart:orgEnd]
                # -- update mPorts['list']
                if add:
                    self.mPorts['list'] = self.mPorts['list'][:orgStart]+iportDict['dict'].lkeys+self.mPorts['list'][orgEnd:]
                else:
                    portNum -= orgEnd - orgStart
                    self.mPorts['list'] = self.mPorts['list'][:orgStart]+iportDict['dict'].lkeys+self.mPorts['list'][orgEnd:]
                # -- update mPorts['dict']
                if add is False:
                    for orgPort in orgPortList:
                        if orgPort in self.mPorts['dict']:
                        if orgPort in self.mPorts['dict']:
                            del self.self.mPorts['dict'][orgPort]
                # -- Update mPorts['auto']
                for tmpIname in self.mPorts['auto']:
                    for typ in self.mPorts['auto'][tmpIname]:
                        if self.mPorts['auto'][tmpIname][typ] > orgStart:
                            self.mPorts['auto'][tmpIname][typ] = self.mPorts['auto'][tmpIname][typ]+portNum
            else:
                # -- update mPorts['list'] and mPorts['auto']
                self.mPorts['auto'][iname] = {'start':len(self.mPorts['list'])}
                self.mPorts['list'].extend(iportDict['dict'].lkeys)
                self.mPorts['auto'][iname]['end'] = len(self.mPorts['list'])
            # ~~ Update mPorts['dict']
            self.mPorts['dict'].update(iportDict['dict'])
            self.mPorts['plen'] = max(self.mPorts['plen'], iportDict['plen'])
            self.mPorts['wlen'] = max(self.mPorts['wlen'], iportDict['wlen'])
            self.mPorts['llen'] = max(self.mPorts['llen'], iportDict['llen'])
            self.mPorts['blen'] = max(self.mPorts['blen'], iportDict['blen'])
    #}}

    def gen_empty_module(self, fname=None, style='simple', appendMode='append', fpLog=None): #{{
        if self.mLocate['eport'] == -1:
            xprint(fpLog, "Error: No port info, please call 'initial_port()' first!")
            return False
        #self.print_location()
        lBlank   = ["", ""]
        delEnd   = self.mLocate['emod']
        delStart = self.mLocate['eport'] + 1
        if self.mLocate['adef'] != -1:
            delStart = self.mLocate['ewire'] + 1 if self.mLocate['ewire'] != -1 and self.mLocate['ewire'] > self.mLocate['adef'] else self.mLocate['adef'] + 1
            #delStart = self.mLocate['adef'] + 1
        else:
            lBlank   = ["", "/*autodefine*/"] + ["", ""]
            if self.mLocate['ewire'] != -1:
                delStart = self.mLocate['ewire'] + 1
            
        #xprint(fpLog, "delStart: {}  delEnd: {}".format(delStart, delEnd))
        lInPorts  = ["assign unused_ok = &{"]
        lOutPorts = []
        for port in self.mPorts['list']:
            if self.mPorts['dict'][port]['inout'] != 'output':
                lInPorts.append("{:19s} {},".format("", port))
            if self.mPorts['dict'][port]['inout'] != 'input':
                if style == 'simple':
                    lOutPorts.append("assign %*s = 'h0;"%(self.mPorts['plen'], port))
                else:
                    lOutPorts.append("assign %s%s = 'h0;"%(port, self.mPorts['dict'][port]['width'] if self.mPorts['dict'][port]['width'] else ''))

        lInPorts.append( "%19s 1'b0};"%("") )

        if fname is None:
            self.del_lines(delStart, delEnd)
            self.append_lines(lines=lBlank + lOutPorts + ["", ""] + lInPorts + ["", ""], location=delStart, appendMode=appendMode)

            self.initial_wire()
            self.update_defines(v2001=True)
        else:
            ml = self.mLines[:delStart] + lBlank + lOutPorts + ["", ""] + lInPorts + ["", ""] + self.mLines[delEnd:]
            modObj = ModuleInfo(fname, lines=[self.mLines[i] for i in range(len(self.mLines))])
            modObj.initial_port()

            modObj.del_lines(delStart, delEnd)
            modObj.append_lines(lines=lBlank + lOutPorts + ["", ""] + lInPorts + ["", ""], location=delStart, appendMode='extend')

            modObj.initial_wire()
            modObj.update_defines(v2001=True, appendMode='extend')

            # save module file
            modObj.save_module()

        return True
    #}}

# Class 'ModuleInfo' # }}}

if __name__ == '__main__':
    pass
