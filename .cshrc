##########################
# COMPANY Tools
setenv COMPANY "JOINSILICON"
set CAD_TOOL_CSHRC = /app/common/cad/env/cad.cshrc
if (-f $CAD_TOOL_CSHRC) then
    echo "source $CAD_TOOL_CSHRC"
    source $CAD_TOOL_CSHRC
endif
unset CAD_TOOL_CSHRC

setenv LD_LIBRARY_PATH /usr/lib:$LD_LIBRARY_PATH
setenv PATH /app/common/cad/flist/:$PATH

##########################
# Tools version choice
setenv SHARE_HOME  "/wx_data/share/"
#setenv MODULEPATH "/home2/usrhome/zengjie/.local/modules/modulefiles/tools:$MODULEPATH"

setenv USER_MODULES_HOME "/usrhome/zengjie/.local/modules/modulefiles/tools"
setenv MODULEPATH "$USER_MODULES_HOME/:/app/tools/modules/modulefiles/synopsys:$MODULEPATH"
# add linghow's modulelist
setenv APP_HOME "/app"
#setenv MODULEPATH "$APP_HOME/tools/modules/modulefiles/tools:/app/tools/modules/modulefiles/synopsys:$MODULEPATH"

# load default tools
module load vim/9.0

##############################
# User's Workspace
# user's bin/lib
setenv PATH                     "/home2/usrhome/zengjie/.local/bin:${PATH}"
setenv LD_LIBRARY_PATH          "/home2/usrhome/zengjie/.local/lib:${LD_LIBRARY_PATH}"

# user's workpath
alias go_wasp 'cdp /projects/wasp02/workshop/SOC/zengjie/wasp_NTO/'
alias go_3dram 'cdp /projects/3d_dram_ctrl/workshop/zengjie/3D_DRAM_CTRL/'
#/wx_data/share/traffic/zengjie/systemC/
alias go_listen 'cdp /projects/listen_01/workshop/soc/zengjie/Listen_01/FE/sc_model/'
alias go_tianchi 'cdp /projects/tianchi/workshop/DE/zengjie/'
alias go_qinghaihu 'cdp /projects/qinghaihu_v01//workshop/tc_de/zengjie/'

set share = $SHARE_HOME/soc/zengjie/
set exchange = /exchange/to_nj_rdlinux/jie.zeng/
set spyfiles = /app/common/cad/flow/spyglass/

alias cdp "cd \!*; setprompt"

# user's custom cmd
alias g "gvim"
alias cp "cp -i"
alias rm "rm -i"
alias mv "mv -i"
alias h "history"
alias rl "readlink -f"
alias bi "bsub -Is"
alias biw "bsub -Is -q wasp_de"

alias fgrep "find \!:1  -type f -exec grep -H \!:2 {} \;"
alias set-date "setenv date `date +%Y%m%d`"

# other tools
alias pic-open "xdg-open"
alias panel-res "xfce4-panel --restart"
alias gui-res "pkill -u $USER xfwm4 ; xfwm4 &"
alias cpu-disp "ps -eo user,pcpu,args --sort=-pcpu | head -n 21"

### direnv:: autoload .envrc
alias precmd 'eval `/home2/usrhome/linyifan/.local/bin/direnv export tcsh`'

##############################
# Prompt format
set orange  = "%{\e[38;5;208m%}" # orange
set black   = "%{\e[1;30m%}" # black
set red     = "%{\e[1;31m%}" # red
set green   = "%{\e[1;32m%}" # green
set yellow  = "%{\e[1;33m%}" # yellow
set blue    = "%{\e[1;34m%}" # blue
set puple   = "%{\e[1;35m%}" # puple
set cyan    = "%{\e[1;36m%}" # cyan
set white   = "%{\e[1;0m%}" # white
# custom temerial input format
# set prompt = "┌─ ($green%nⓐ %m$white}) [$cyan`pwd`$white] \n└>> "
set prompt_format = "┌─ [$orange%h$white] $blue%P $green%n@%m$white $cyan%/$white \n└>> "
alias setprompt 'set prompt = "$prompt_format"'
alias cd "cd \!*; setprompt"
alias .. 'cd ..; setprompt'
setprompt


