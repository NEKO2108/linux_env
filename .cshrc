##########################
# COMPANY Tools
setenv COMPANY "JOINSILICON"
set CAD_TOOL_CSHRC = /app/common/cad/env/cad.cshrc
if (-f $CAD_TOOL_CSHRC) then
    echo "source $CAD_TOOL_CSHRC"
    source $CAD_TOOL_CSHRC
endif
unset CAD_TOOL_CSHRC

### check PATH and LD_LIBRARY_PATH 
if ($?PATH == 0) then
    setenv PATH ""
endif
if ($?LD_LIBRARY_PATH == 0) then
    setenv LD_LIBRARY_PATH ""
endif
if ($?MODULEPATH == 0) then
    setenv MODULEPATH ""
endif


setenv LD_LIBRARY_PATH /usr/lib:$LD_LIBRARY_PATH
setenv PATH /app/common/cad/flist/:$PATH

##########################
# Tools version choice
setenv SHARE_HOME  "/wx_data/share/"

setenv APP_HOME "/app"
setenv USER_MODULES_HOME "$HOME/.local/modules/modulefiles/tools"
setenv MODULEPATH "$USER_MODULES_HOME/:$MODULEPATH"

# load default tools
module load vim/9.0

#==================== Git 常用别名 csh/tcsh ====================
alias gs         'git status'
alias gl         'git log --oneline -10'       # 最近10条简洁日志
alias gll        'git log --stat'             # 带变更文件统计
alias gllp       'git log -p'                 # 展示代码diff
alias grf        'git reflog --oneline'       # 本地操作历史，找回reset提交
alias ga         'git add \!*'
alias gaa        'git add .'
alias gc         'git commit '
alias gca        'git commit --amend'         # 修改上一次commit
alias gcan       'git commit --amend --no-edit' # 追加修改不修改注释
alias gp         'git push \!*'
alias gpf        'git push --force-with-lease \!*' #安全强推，优先用这个，不要直接--force
alias gpl        'git pull \!*'
alias gco        'git checkout \!*'
alias gcb        'git checkout -b \!*'        # 创建并切换新分支
alias gb         'git branch'
alias gba        'git branch -a'              # 显示本地+远程全部分支
alias gd         'git diff \!*'
alias gdc        'git diff --cached \!*'      # 对比暂存区diff
alias grs        'git reset \!*'
alias grss       'git reset --soft HEAD~1'    # 撤销上次commit，保留改动到暂存
alias grsh       'git reset --hard HEAD~1'   # ⚠️彻底丢弃上次提交改动
alias grh        'git reset --hard HEAD'      # 丢弃本地所有未提交修改
alias grev       'git revert \!*'
alias gmg        'git merge \!*'
alias gst        'git status'
alias gstash     'git stash'
alias gstashl    'git stash list'
alias gstashp    'git stash pop'
alias gstashd    'git stash drop'
alias gfetch     'git fetch --prune'          #拉取远程，清理已经删除远程分支引用

#==================== SVN 常用别名 csh/tcsh ====================
alias svst       'svn status'
alias svup       'svn update'
alias svci       'svn commit -m "\!*"'
alias svco       'svn checkout \!*'
alias svadd      'svn add \!*'
alias svrm       'svn rm \!*'
alias svmv       'svn mv \!*'
alias svdiff     'svn diff \!*'
alias svlog      'svn log -l 10 \!*'          #最近10条svn日志
alias svinfo     'svn info'
alias svrevert   'svn revert \!*'
alias svrevertall 'svn revert -R .'           #⚠️撤销当前目录全部本地修改
alias svclean    'svn status | grep "^\?" | awk "{print \$2}" | xargs rm -rf' #删除svn未纳入版本的临时文件

#==================== 快捷帮助 ====================
alias ghelp      'echo "gs status; gl log; ga add; gc commit; gp push; gpl pull; grss soft reset~1; grsh hard reset~1; grf reflog"'
alias svhelp     'echo "svst status; svup update; svci commit; svdiff diff; svlog log; svrevertall revert all local changes"'

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
alias set-date "unsetenv date; setenv date `date +%Y%m%d`"

# other tools
alias pic-open "xdg-open"
alias panel-res "xfce4-panel --restart"
alias gui-res "pkill -u $USER xfwm4 ; xfwm4 &"
alias cpu-disp "ps -eo user,pcpu,args --sort=-pcpu | head -n 21"

### direnv:: autoload .envrc
#alias precmd 'eval `/home2/usrhome/linyifan/.local/bin/direnv export tcsh`'

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


