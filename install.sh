#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"

link() {
    local src="$1" dst="$2"
    mkdir -p "$(dirname "$dst")"

    if [ -L "$dst" ]; then
        rm "$dst"
    elif [ -e "$dst" ]; then
        echo "  backing up $dst -> ${dst}.bak"
        mv "$dst" "${dst}.bak"
    fi

    ln -s "$src" "$dst"
    echo "  $dst -> $src"
}

echo "Installing dotfiles from $DOTFILES"
echo

# Shell
echo "==> zsh"
link "$DOTFILES/zsh/.zshrc" "$HOME/.zshrc"

# Git
echo "==> git"
link "$DOTFILES/git/.gitconfig" "$HOME/.gitconfig"

# SSH
echo "==> ssh"
link "$DOTFILES/ssh/config" "$HOME/.ssh/config"

# Vim
echo "==> vim"
link "$DOTFILES/vim/.vimrc" "$HOME/.vimrc"
link "$DOTFILES/vim/autoload" "$HOME/.vim/autoload"
link "$DOTFILES/vim/colors" "$HOME/.vim/colors"

# Claude Code
echo "==> claude"
link "$DOTFILES/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
link "$DOTFILES/claude/settings.json" "$HOME/.claude/settings.json"
link "$DOTFILES/claude/keybindings.json" "$HOME/.claude/keybindings.json"
link "$DOTFILES/claude/agents/blockhead-ops.md" "$HOME/.claude/agents/blockhead-ops.md"
link "$DOTFILES/claude/agents/buildbot.md" "$HOME/.claude/agents/buildbot.md"

# OpenCode
echo "==> opencode"
link "$DOTFILES/opencode/opencode.json" "$HOME/.config/opencode/opencode.json"

echo
echo "Done. Secrets go in ~/.zshrc.local (not tracked by git)."
