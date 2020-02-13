" ======== VIM-PLUG ========

call plug#begin('~/.vim/plugged')

" asynchronous code linting
Plug 'w0rp/ale'

" fuzzy file, buffer, mru, tag, etc finder
Plug 'kien/ctrlp.vim'

" tree-style file explorer
Plug 'scrooloose/nerdtree', { 'on':  'NERDTreeTabsToggle' }

" makes nerdtree work better with tab-based workflow
Plug 'jistr/vim-nerdtree-tabs', { 'on':  'NERDTreeTabsToggle' }

" show git diff in the gutter, stage/revert hunks
Plug 'airblade/vim-gitgutter'

" powerful and lightweight status/tabline
Plug 'itchyny/lightline.vim'

" ALE indicators for lightline
Plug 'maximbaz/lightline-ale'

" improved syntax highlighting
Plug 'sheerun/vim-polyglot'

" colorize color codes
Plug 'lilydjwg/colorizer'

" LSP client
Plug 'neoclide/coc.nvim', {'do': { -> coc#util#install()}}

call plug#end()

" ======== VISUAL ========

" render a column at 80 characters
set colorcolumn=80

" use 256 colors
:set t_Co=256

" set colorscheme to fansi
colorscheme fansi

" ======== EDITING ========

" use 4 spaces to represent tab
:set tabstop=2
:set softtabstop=2
" number of spaces to use for auto indent
:set shiftwidth=2
" copy indent from current line when starting a new line
:set autoindent
" expand tabs to spaces
:set expandtab

" make backspace work like you'd expect in insert mode
:set backspace=indent,eol,start

" use system clipboard as default clipboard
:set clipboard=unnamedplus

" number of lines to keep above and below the cursor
:set scrolloff=5

" show line numbers
:set number

" always show the sign column, e.g. where lint errors are marked
set signcolumn=yes

" highlight search result
:set hlsearch
" ignore search case
:set ignorecase
" unless you use capitals
:set smartcase
" make sarches always appear in centre of page
:nnoremap n nzz
:nnoremap N Nzz
:nnoremap * *zz
:nnoremap # #zz
:nnoremap g* g*zz
:nnoremap g# g#zz
" clear search highlighting with enter
nnoremap <cr> :noh<CR><CR>:<backspace>

" F9 to toggle paste mode
:nnoremap <silent><F9> :set paste!<CR>

" don't automatically comment next line on enter/o if already commenting
autocmd BufNewFile,BufRead * setlocal formatoptions-=cro

" automatically strip trailing whitespace
fun! <SID>StripTrailingWhitespaces()
    let l = line(".")
    let c = col(".")
    %s/\s\+$//e
    call cursor(l, c)
endfun
autocmd BufWritePre * :call <SID>StripTrailingWhitespaces()

" ======== MISCELLANEOUS ========

" force unix fileformat
:set fileformat=unix

" enable mouse selection
:set mouse=a

" increase max number of files you can open as tabs with -p command line option
:set tabpagemax=50

" make swapfiles be kept in a central location to avoid polluting file system
set directory^=$HOME/.vim/swapfiles//

" use undodir for persistent undoing across file closure
set undodir=~/.vim/undodir
set undofile

" visual autocomplete for command menu
:set wildmenu
" make tab completion in wildmenu work like bash
set wildmode=longest:full,full
set wildmenu

" switch tabs with Ctrl left and right
nnoremap <C-right> :tabnext<CR>
nnoremap <C-left> :tabprevious<CR>
" and whilst in insert mode
inoremap <C-right> <Esc>:tabnext<CR>
inoremap <C-left> <Esc>:tabprevious<CR>

" always write to existing file - prevents webpack watch flakiness
:set backupcopy=yes

" ======== GIT GUTTER ========

" allow us to override the color
let g:gitgutter_override_sign_column_highlight = 0

" default is 4 seconds - reduce to 100ms
set updatetime=100

" ======== NERDTREE ========

" set toggle to C-n
map <C-n> :NERDTreeTabsToggle<CR>

" ignore certain files/folders
set wildignore+=*.pyc,node_modules,dist
let NERDTreeRespectWildIgnore=1

" ======== CTRLP ========

" only search for things under the directory that you opened vim from
let g:ctrlp_working_path_mode = ''

" ignore temp files
set wildignore+=*/tmp/*,*.so,*.swp,*.zip,*.pyc

" don't index inside node_modules or dist directories
let g:ctrlp_custom_ignore = '\v[\/](node_modules|dist)$'

" C-b to search open buffers
nmap <C-b> :CtrlPBuffer<CR>

" ======== STATUS/TAB BARS ========

" always show status bar
set laststatus=2
" don't show -- INSERT --, pointless as we have a status bar
set noshowmode

" Initialize lightline config
let g:lightline = {}

" Disable lightline's tab bar
let g:lightline.enable = {'tabline': 0}

" Add lightline-ale components to lightline
let g:lightline.component_expand = {
\  'linter_checking': 'lightline#ale#checking',
\  'linter_warnings': 'lightline#ale#warnings',
\  'linter_errors': 'lightline#ale#errors',
\  'linter_ok': 'lightline#ale#ok'
\ }

" Set colours for the components
let g:lightline.component_type = {
\  'linter_checking': 'left',
\  'linter_warnings': 'warning',
\  'linter_errors': 'error',
\  'linter_ok': 'left'
\ }

" Configure lightline's statusbar
let g:lightline.active = {
\  'left': [[ 'mode', 'paste'], ['readonly', 'relativepath', 'modified']],
\  'right': [
\    ['lineinfo'],
\    ['percent'],
\	   ['linter_checking', 'linter_errors', 'linter_warnings', 'linter_ok']
\  ]
\ }

" ======== COMPLETION ========

" Use tab to trigger completion and tab/shift-tab to navigate results
inoremap <silent><expr> <TAB>
      \ pumvisible() ? "\<C-n>" :
      \ <SID>check_back_space() ? "\<TAB>" :
      \ coc#refresh()
inoremap <expr><S-TAB> pumvisible() ? "\<C-p>" : "\<C-h>"
function! s:check_back_space() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

" Close preview pane once completion is
autocmd InsertLeave,CompleteDone * if pumvisible() == 0 | pclose | endif

" use ctrl-j, ctrl-k for selecting omni completion entries
inoremap <expr> <C-j> pumvisible() ? '<C-n>' : ''
inoremap <expr> <C-k> pumvisible() ? '<C-p>' : ''

" select omni completion entry with enter (always supress newline)
inoremap <expr> <CR> pumvisible() ? "\<C-Y>" : "\<CR>"

" ======== LINTING ========

" specify some specific ale linter sources, rest are using defaults
let g:ale_linters = {
\   'javascript': ['eslint'],
\   'c': ['clang', 'clangtidy', 'clang-format'],
\   'typescript': ['eslint']
\ }
let g:ale_python_flake8_args='--exclude=migrations --ignore=E261 --max-line-length=80'

" Javascript / React improved highlighting/indentation
let g:javascript_plugin_jsdoc = 1
let g:jsx_ext_required = 0

" map error jumping to [e and ]e
nnoremap <silent> <Plug>LocationPrevious    :<C-u>exe 'call <SID>LocationPrevious()'<CR>
nnoremap <silent> <Plug>LocationNext        :<C-u>exe 'call <SID>LocationNext()'<CR>
nmap <silent> [e  <Plug>LocationPrevious
nmap <silent> ]e  <Plug>LocationNext
" make error jumping wrap
function! <SID>LocationPrevious()
    try
        lprev
    catch /^Vim\%((\a\+)\)\=:E553/
        llast
    endtry
endfunction
function! <SID>LocationNext()
    try
        lnext
    catch /^Vim\%((\a\+)\)\=:E553/
        lfirst
    endtry
endfunction
