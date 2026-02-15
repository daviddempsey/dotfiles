# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="minimal"

plugins=(git)

source $ZSH/oh-my-zsh.sh

# Common aliases
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

# NVM Setup (platform-specific paths loaded in .zshrc.local)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

export PAGER="cat"
export PATH="$HOME/.local/bin:$PATH"

# Platform-specific config (symlinked from dotfiles)
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

# Machine-local secrets — not tracked in git
[[ -f ~/.zshrc.secrets ]] && source ~/.zshrc.secrets
