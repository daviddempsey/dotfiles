hi clear

if exists("syntax_on")
  syntax reset
endif

exec "source " . expand('<sfile>:p:h') . "/default-light.vim"

let colors_name = "fansi"

" Pass-through background and font color - your terminal profile should
" determine light/dark mode colors for background and font.
hi Normal                    ctermbg=NONE

" In diffs, added lines are green, changed lines are yellow, deleted lines are
" red, and changed text (within a changed line) is bright yellow and bold.
hi DiffAdd        ctermfg=2    ctermbg=NONE
hi DiffChange     ctermfg=3    ctermbg=NONE
hi DiffDelete     ctermfg=1    ctermbg=NONE
hi DiffText       ctermfg=0    ctermbg=11   cterm=bold

" Set a subtle dark background in dark mode and a subtle light background in
" light mode for visually selected text
if &background == "light"
  hi Visual       ctermfg=NONE ctermbg=7    cterm=NONE
else
  hi Visual       ctermfg=NONE ctermbg=0    cterm=NONE
endif

" Highlight search matches in black, with a yellow background
hi Search         ctermfg=0    ctermbg=11

" Dim line numbers, comments, color columns, the status line, splits and sign
" columns.
hi LineNr         ctermfg=8
hi TabLine        ctermfg=NONE ctermbg=NONE cterm=NONE
hi TabLineSel     ctermfg=15   ctermbg=4    cterm=bold
hi TabLineFill    ctermfg=NONE ctermbg=NONE cterm=NONE

" Blue background for wildmenu selected option
hi WildMenu       ctermfg=15   ctermbg=4

" Grey colours for p-menu (autocomplete popover)
hi Pmenu          ctermfg=15   ctermbg=240
hi PmenuSel       ctermfg=15   ctermbg=4
hi PmenuSbar      ctermfg=0    ctermbg=240
hi PmenuThumb                  ctermbg=245

" Blue background for cursor line, for example ctrl-p selected entry
hi CursorLine     ctermfg=15   ctermbg=4 cterm=NONE

" Yellow line number on selected line
hi CursorLineNr   ctermfg=3

" Underline matching parentheses
hi MatchParen     ctermfg=NONE ctermbg=NONE cterm=underline

if &background == "light"
  hi ColorColumn  ctermfg=15   ctermbg=7
  hi Folded       ctermfg=8    ctermbg=7
  hi FoldColumn   ctermfg=8    ctermbg=7
  hi SpellCap     ctermfg=8    ctermbg=7
  hi StatusLine   ctermfg=0    ctermbg=7    cterm=bold
  hi StatusLineNC ctermfg=8    ctermbg=7    cterm=NONE
  hi VertSplit    ctermfg=8    ctermbg=7    cterm=NONE
  hi SignColumn   ctermfg=8    ctermbg=NONE
else
  hi ColorColumn  ctermfg=7    ctermbg=234
  hi Folded       ctermfg=7    ctermbg=8
  hi FoldColumn   ctermfg=7    ctermbg=8
  hi SpellCap     ctermfg=7    ctermbg=8
  hi StatusLine   ctermfg=7    ctermbg=234  cterm=NONE
  hi StatusLineNC ctermfg=7    ctermbg=235  cterm=NONE
  hi VertSplit    ctermfg=235  ctermbg=235  cterm=NONE
  hi SignColumn   ctermfg=15   ctermbg=NONE
endif

" Make syntax errors be highligted in red
hi SpellBad     ctermfg=15     ctermbg=1    cterm=NONE

" Custom code syntax colors
hi Comment      ctermfg=8
hi String       ctermfg=1      ctermbg=NONE cterm=NONE
hi Function     ctermfg=6      ctermbg=NONE cterm=NONE
hi Identifier   ctermfg=3      ctermbg=NONE cterm=NONE
hi Constant     ctermfg=5      ctermbg=NONE cterm=NONE
hi Keyword      ctermfg=3      ctermbg=NONE cterm=NONE
hi NonText      ctermfg=15     ctermbg=NONE cterm=NONE
hi Number       ctermfg=12     ctermbg=NONE cterm=NONE
hi Operator     ctermfg=2      ctermbg=NONE cterm=NONE
hi PreProc      ctermfg=5      ctermbg=NONE cterm=NONE
hi Statement    ctermfg=3      ctermbg=NONE cterm=NONE
hi StorageClass ctermfg=5      ctermbg=NONE cterm=NONE
hi Type         ctermfg=3      ctermbg=NONE cterm=NONE
