###########################################################
## COMPANY Tools and python3 packages ENV
setenv COMPANY "JOINSILICON"
set CAD_TOOL_CSHRC = /app/common/cad/env/cad.cshrc
if (-f $CAD_TOOL_CSHRC) then
    echo "source $CAD_TOOL_CSHRC"
    source $CAD_TOOL_CSHRC
endif
unset CAD_TOOL_CSHRC

# python3 packages ENV
if ($?PYTHONPATH) then
else
    setenv PYTHONPATH ""
endif
setenv PYTHONPATH "/app/common/cad/lib/python3/site-packages/:${PYTHONPATH}"
setenv PYTHONPATH "/app/common/cad/lib/python3/inhouse-packages/:${PYTHONPATH}"
###########################################################

###########################################################
## Claude Code & Agent Hub
source /app/tools/claudecode/claude.csh
source /app/common/cad/dv/agent_hub/install.csh
###########################################################

###########################################################
## Path Setting
## check PATH and LD_LIBRARY_PATH 
if ($?PATH == 0) then
    setenv PATH ""
endif
if ($?LD_LIBRARY_PATH == 0) then
    setenv LD_LIBRARY_PATH ""
endif
if ($?MODULEPATH == 0) then
    setenv MODULEPATH ""
endif

# 通用库路径
setenv LD_LIBRARY_PATH /usr/lib:$LD_LIBRARY_PATH

# user's bin/lib
setenv PATH             "/home2/usrhome/zengjie/.local/bin:${PATH}"
setenv LD_LIBRARY_PATH  "/home2/usrhome/zengjie/.local/lib:${LD_LIBRARY_PATH}"
###########################################################

###########################################################
## Tools Version (module)
setenv SHARE_HOME          "/wx_data/share/"
setenv USER_MODULES_HOME   "/usrhome/zengjie/.local/modules/modulefiles/tools"
setenv MODULEPATH          "$USER_MODULES_HOME/:/app/tools/modules/modulefiles/synopsys:$MODULEPATH"
setenv APP_HOME            "/app"
setenv DW_HOME             "/app/eda/synopsys/dc"

# 默认加载
module load vim/9.0

# 按需加载（取消注释启用）
#module load spyglass/S-2021.09
#module load systemc/2.3.3
#module load gcc/11.2
###########################################################

###########################################################
## Workspace Variables & Navigation
set workpath = /projects/listen_01/workshop/soc/zengjie/Listen_01/FE/sc_model/
set share    = $SHARE_HOME/soc/zengjie/
set exchange = /exchange/to_nj_rdlinux/jie.zeng/
set spyfiles = /app/common/cad/flow/spyglass/

## Workspace Navigation
alias cdp        'cd \!*; setprompt'
alias go_wasp    'cdp /projects/wasp02/workshop/SOC/zengjie/wasp_NTO/'
alias go_3dram   'cdp /projects/3d_dram_ctrl/workshop/zengjie/3D_DRAM_CTRL/'
alias go_listen  'cdp /projects/listen_01/workshop/soc/zengjie/Listen_01/FE/sc_model/'
alias go_tianchi 'cdp /projects/tianchi/workshop/DE/zengjie/'
alias go_qinghaihu 'cdp /projects/qinghaihu_v01//workshop/tc_de/zengjie/'
alias go_hyper   'cdp /projects/hyper03/workshop/zengjie/'
alias go_semi    'cdp /projects/semi_f1/workshop/SOC/zengjie/'
###########################################################

###########################################################
## Git & SVN Aliases
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
alias grsh       'git reset --hard HEAD~1'    # 彻底丢弃上次提交改动
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
alias svrevertall 'svn revert -R .'           #撤销当前目录全部本地修改
alias svclean    'svn status | grep "^\?" | awk "{print \$2}" | xargs rm -rf' #删除svn未纳入版本的临时文件

###########################################################

###########################################################
## User Custom Aliases
# ---- 日常文件操作 ----
alias g     'gvim'
alias cpf   'cp -rf'
alias rm    'rm -i'
alias mv    'mv -i'
alias h     'history'
alias rl    'readlink -f'
alias fgrep 'find \!:1 -type f -exec grep -H \!:2 {} \;'

# ---- LSF 作业 ----
alias bi  'bsub -Is'
alias biw 'bsub -Is -q wasp_de'

# ---- 桌面/系统 ----
alias pic-open  'xdg-open'
alias panel-res 'xfce4-panel --restart'
alias gui-res   'pkill -u $USER xfwm4 ; xfwm4 &'
alias cpu-disp  'ps -eo user,pcpu,args --sort=-pcpu | head -n 21'
alias set-date  'unsetenv date;setenv date `date +%Y%m%d`'
alias draw-io   'bsub -Is -q gui /app/tools/draw.io/drawio-22.1.21 --no-sandbox &'

###########################################################

###########################################################
## Terminal Setting
# ---- 颜色定义 ----
set orange  = "%{\e[38;5;208m%}" # orange
set black   = "%{\e[1;30m%}"     # black
set red     = "%{\e[1;31m%}"     # red
set green   = "%{\e[1;32m%}"     # green
set yellow  = "%{\e[1;33m%}"     # yellow
set blue    = "%{\e[1;34m%}"     # blue
set puple   = "%{\e[1;35m%}"     # puple
set cyan    = "%{\e[1;36m%}"     # cyan
set white   = "%{\e[1;0m%}"      # white

# ---- prompt 格式 ----
#set prompt = "┌─ ($green%nⓐ %m$white}) [$cyan`pwd`$white] \n└>> "
set prompt_format = "┌─ [$orange%h$white] $blue%P $green%n@%m$white $cyan%/$white \n└>> "
alias setprompt 'set prompt = "$prompt_format"'

# ---- cd 系列联动刷新 prompt ----
alias cd "cd \!*; setprompt"
alias .. 'cd ..; setprompt'

# ---- direnv 自动加载（tcsh hook，保持最后） ----
alias precmd 'eval `/home2/usrhome/zengjie/.local/bin/direnv export tcsh`'
# 当目录改变时，通知 GNOME Terminal 当前路径
alias cwdcmd 'printf "\033]7;file://%s%s\007" "`hostname`" "$PWD"'
set ignorecase

# ---- 应用 prompt ----
setprompt
###########################################################
