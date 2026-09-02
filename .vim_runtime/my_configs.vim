" ============================================================================
" 1. 基础初始化（必须放在最前面）
" ============================================================================
execute pathogen#infect()
set nocompatible              " 禁用 vi 兼容模式
filetype plugin indent on     " 启用文件类型检测、插件和缩进

" ============================================================================
" 2. 界面与编辑基础设置
" ============================================================================
" 显示设置
set number                    " 显示行号
set cursorline                " 高亮当前行
set cursorcolumn              " 高亮当前列
set ruler                     " 显示光标位置
set showcmd                   " 显示命令输入
set showmode                  " 显示当前模式

" 缩进与制表符
set tabstop=4                 " 制表符显示宽度
set softtabstop=4             " 软制表符宽度
set shiftwidth=4              " 自动缩进宽度
set expandtab                 " 空格替代制表符
set autoindent                " 自动缩进
set si                        " 智能缩进（smartindent）

" 搜索优化
set hlsearch                  " 高亮搜索结果
set incsearch                 " 增量搜索
set ignorecase                " 搜索忽略大小写
set smartcase                 " 智能大小写（有大写时区分）

" 其他
set autochdir                 " 自动切换当前目录
set backspace=indent,eol,start  " 退格键行为
set fdm=marker                " 折叠方式（标记）
syntax on                     " 语法高亮
colorscheme peaksea           " 颜色主题
set background=light

" 字体设置
" 仅在 GUI 模式 (gvim) 下执行字体设置
if has('gui_running')
    " 使用 fc-list 检查系统中是否存在 Cousine Nerd Font
    " grep -i 表示忽略大小写，提高匹配成功率
    if system('fc-list | grep -i "Cousine Nerd Font"') !=# ''
        set guifont=Cousine\ Nerd\ Font\ 12
    else
        set guifont=Courier\ 10\ Pitch\ 12
    endif
endif
set guioptions+=T
set guioptions+=r

" ============================================================================
" 3. 文件类型自动命令
" ============================================================================
au BufRead,BufNewFile *.v   set filetype=verilog
au BufRead,BufNewFile *.sv  set filetype=systemverilog
au BufRead,BufNewFile *.svh set filetype=systemverilog

" 定义一个自动命令组，防止重复加载
augroup DisableAutoReadForSpecificExt
    autocmd!
    " 当打开 .log 后缀的文件时，仅对该缓冲区关闭 autoread
    autocmd BufEnter *.log setlocal noautoread
augroup END

" ============================================================================
" 4. 自定义映射
" ============================================================================
" 插入模式：文件名补全
imap <C-f> <C-x><C-f>

" 重新加载 vimrc
nnoremap <silent> <leader>r :source $MYVIMRC<CR>:echo "vimrc reloaded!"<CR>

" ============================================================================
" 5. 字体缩放功能
" ============================================================================
function! IncreaseFontSize()
    let &guifont = substitute(&guifont, '\d\+$', '\=str2nr(submatch(0))+1', '')
    echo "Font size increased: " . &guifont
endfunction

function! DecreaseFontSize()
    let &guifont = substitute(&guifont, '\d\+$', '\=str2nr(submatch(0))-1', '')
    echo "Font size decreased: " . &guifont
endfunction


nmap <M-=> :call IncreaseFontSize()<CR>
nmap <M--> :call DecreaseFontSize()<CR>
command! IncreaseFont call IncreaseFontSize()
command! DecreaseFont call DecreaseFontSize()

" ============================================================================
" 6. 本地插件管理（vim-plug）
" ============================================================================
" 直接把插件根目录设为 plug#begin 的默认路径
"call plug#begin(fnameescape(g:VIM_RUNTIME_PATH . '/my_plugin'))
"
"" 通用插件
"Plug 'vim-easy-align'
"
"" Mark 插件
"Plug 'vim-ingo-library'
"Plug 'vim-mark'
"Plug 'indentLine'
"Plug 'vim-matchup'
""Plug 'verilog_systemverilog.vim'
"
"" Airline 状态栏
"Plug 'vim-airline-0.11'
"Plug 'vim-airline-themes-master'
"
"call plug#end()

" ============================================================================
" 7. EasyAlign 配置
" ============================================================================
xmap ga <Plug>(EasyAlign)
nmap ga <Plug>(EasyAlign)
vmap gb :EasyAlign<Enter>*<Space>
vmap ge :EasyAlign<Enter>*=
vmap gd :EasyAlign<Enter>-<Space>

" ============================================================================
" 8. vim-mark 配置（Leader 键：\）
" ============================================================================
nmap @         <Plug>MarkSet
vmap <M-m>     <Plug>MarkSet
nmap <M-r>     <Plug>MarkRegex
vmap <M-r>     <Plug>MarkRegex
nmap <M-n>     <Plug>MarkClear
nmap <M-N>     <Plug>MarkConfirmAllClear
nmap <M-/>     <Plug>MarkSearchAnyNext
nmap <M-?>     <Plug>MarkSearchAnyPrev
nmap 1         <Plug>MarkSearchCurrentNext
nmap !         <Plug>MarkSearchCurrentPrev

" ============================================================================
" 9. 文件树配置
" ============================================================================
" 快速切换NERDTree显示/隐藏
nnoremap <F11> :NERDTreeToggle<CR>
nnoremap <F12> :NERDTree<CR>
autocmd FileType nerdtree nmap <buffer> <BS> :NERDTreeUp<CR>

"Show line number.
let g:NERDTreeShowlineNumber=1

"Show hide file.
let g:NERDTreeHidden=0

"Show Node model.
let NERDTreeDirArrows=1

" Start NERDTree when Vim starts with a directory argument.
" 自动行为
autocmd StdinReadPre * let s:std_in=1
autocmd BufEnter * if tabpagenr('$') == 1 && winnr('$') == 1 && exists('b:NERDTree') | quit | endif
autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) && !exists('s:std_in') |
    \ execute 'NERDTree' argv()[0] | wincmd p | enew | execute 'cd '.argv()[0] | endif

" ============================================================================
" 10. Airline 状态栏配置
" ============================================================================
" 等 Vim 启动完成后自动关闭 lightline
autocmd VimEnter * call lightline#disable()
let g:airline_theme = 'molokai'
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#formatter = 'unique_tail'
let g:airline_powerline_fonts = 1

" ============================================================================
" indentLine 配置
" ============================================================================
let g:indentLine_enabled = 1
let g:indentLine_concealcursor = 'inc'
let g:indentLine_conceallevel = 1
let g:indentLine_char_list = ['|', '¦', '┆', '┊']
" listchars Settings
set list
set listchars=lead:˰,trail:˯,tab:→\ 

highlight Whitespace ctermfg=239 guifg=#5C6370
highlight SpecialKey ctermfg=239 guifg=#5C6370
highlight NonText    ctermfg=239 guifg=#5C6370
let g:indentLine_showFirstIndentLevel = 1

" ============================================================================
" matchup 配置
" ============================================================================
let g:matchup_enabled = 1
let g:matchup_matchparen_enabled = 1   " 高亮匹配对

" ============================================================================
" amix vimrc configuration
" ============================================================================
let g:copilot_enabled = 0
" set ctags search path
set tags=tags;
set autochdir

" change comment style to //
autocmd FileType verilog,systemverilog,c,cpp set commentstring=//\ %s
" usage:
"  - gcc to comment out a line
"  - gcap to comment out a paragraph
"  - gcu to uncomment

" Abbreviation for quick comment
iab xmd // Modify <C-r>=strftime("%d/%m/%y %H:%M:%S")<cr><esc>
iab xto // TODO:
iab xsp // ------------------------------------------------------------------------------<esc>
iab xss // -------------------------------------------<esc>

