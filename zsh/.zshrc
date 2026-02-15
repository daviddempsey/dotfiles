# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="minimal"

plugins=(git)

source $ZSH/oh-my-zsh.sh

# Dotfiles repo setup
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

eval "$(/opt/homebrew/bin/brew shellenv)"
export GPG_TTY=$(tty)

# Auto-start tmux
if command -v tmux &> /dev/null && [ -z "$TMUX" ] && [ -n "$PS1" ] && [[ ! "$TERM" =~ screen ]] && [[ ! "$TERM" =~ tmux ]]; then
    exec tmux new-session -A -s default
fi

# PHP Setup
export PATH="/opt/homebrew/opt/php@8.2/bin:$PATH"
export PATH="/opt/homebrew/opt/php@8.2/sbin:$PATH"

# NVM Setup
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"

# Windsurf
export PATH="/Users/ddempsey/.codeium/windsurf/bin:$PATH"

export PAGER="cat"

# Claude
export PATH="/Users/ddempsey/.local/bin:$PATH"

# Antigravity
export PATH="/Users/ddempsey/.antigravity/antigravity/bin:$PATH"

# Machine-local secrets (API keys, etc.) — not tracked in git
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
